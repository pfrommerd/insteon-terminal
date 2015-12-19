package us.pfrommer.insteon.msg;

import java.io.IOException;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Queue;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class IOPort {
	private static final Logger logger = LoggerFactory.getLogger(IOPort.class);
	
	enum ReplyType {
		GOT_ACK,
		WAITING_FOR_ACK,
		GOT_NACK
	}
	
	private IOStream		m_stream;
	private IOStreamWriter	m_writer;
	private IOStreamReader	m_reader;
	private Thread			m_readThread;
	private Thread			m_writeThread;
	private Queue<Msg>		m_writeQueue = new LinkedList<Msg>();
	private HashSet<PortListener> m_listeners = new HashSet<PortListener>();
	
	private MsgReader 		m_msgReader = new MsgReader();
	private	final int		m_readSize	= 1024; // read buffer size
	
	
	public IOPort(IOStream s) {
		m_stream = s;
	}
	public void removeListener(PortListener l) {
		synchronized(m_listeners) {
			m_listeners.remove(l);
		}		
	}
	public void addListener(PortListener l) {
		synchronized(m_listeners) {
			m_listeners.add(l);
		}
	}
	
	public void open() throws IOException {
		m_writer = new IOStreamWriter();
		m_reader = new IOStreamReader();
		
		if (!m_stream.isOpen()) m_stream.open();
		
		m_readThread	= new Thread(m_reader);
		m_writeThread	= new Thread(m_writer);
		
		m_readThread.start();
		m_writeThread.start();
	}
	
	public void close() throws IOException {
		if (!m_stream.isOpen()) return;
		//Wait for the write queue to be empty
		synchronized(m_writeQueue) {
			m_writeQueue.clear();
		}
		m_writer.stopThread();
		try {
			m_writeThread.join();
		} catch (InterruptedException e) {
			// not sure what to do here
		}
		

		m_reader.stopThread();
		m_readThread.interrupt();
		try {
			m_readThread.join();
		} catch (InterruptedException e) {
			// not sure what to do here
		}

		
		m_reader = null;
		m_writer = null;
		
		if (m_stream.isOpen()) m_stream.close();
	}
	
	public void write(Msg m) throws IOException {
		if (m == null) {
			throw new IOException("trying to write null message!");
		}
		if (m.getData() == null) {
			throw new IOException("trying to write message without data!");
		}
		synchronized (m_writeQueue) {
			m_writeQueue.add(m);
			m_writeQueue.notifyAll();
		}
	}

	public class IOStreamReader implements Runnable {
		private ReplyType	m_reply = ReplyType.GOT_ACK;
		private	Object		m_replyLock = new Object();
		boolean				m_keepRunning = true;
		/**
		 * Helper function for implementing synchronization between reader and writer
		 * @return reference to the RequesReplyLock
		 */
		public	Object getRequestReplyLock() { return m_replyLock; }

		public synchronized void stopThread() {
			m_keepRunning = false;
		}
	
		@Override
		public void run() {
			byte[] buffer = new byte[2 * m_readSize];
			int len = -1;
			try	{
				while (m_keepRunning && (len = m_stream.in().read(buffer, 0, m_readSize)) > -1) {
					m_msgReader.addData(buffer, len);
					processMessages();
				}
			} catch (IOException e)	{
				e.printStackTrace();
			}         
		}
		
		private void processMessages() {
			try {
				// must call processData() until we get a null pointer back
				for (Msg m = m_msgReader.processData(); m != null;
						m = m_msgReader.processData()) {
						logger.debug("Msg received: {}", m);
						toAllListeners(m);
						notifyWriter(m);
				}
			} catch (IOException e) {
				// got bad data from modem,
				// unblock those waiting for ack
				synchronized (getRequestReplyLock()) {
					if (m_reply == ReplyType.WAITING_FOR_ACK) {
						m_reply = ReplyType.GOT_ACK;
						getRequestReplyLock().notify();
					}
				}
			}
		}

		private void notifyWriter(Msg msg) {
			synchronized (getRequestReplyLock()) {
				if (m_reply == ReplyType.WAITING_FOR_ACK) {
					if (!msg.isUnsolicited()) {
						m_reply = (msg.isPureNack() ? ReplyType.GOT_NACK : ReplyType.GOT_ACK);
						getRequestReplyLock().notify();
					} else if (msg.isPureNack()){
						m_reply = ReplyType.GOT_NACK;
						getRequestReplyLock().notify();
					}
				}
			}
		}

		@SuppressWarnings("unchecked")
		private void toAllListeners(Msg msg) {
			// When we deliver the message, the recipient
			// may in turn call removeListener() or addListener(),
			// thereby corrupting the very same collection that we are iterating
			// over. That's why we make a copy of it, and iterate over that.
			HashSet<PortListener> tempList = null;
			synchronized(m_listeners) {
				tempList= (HashSet<PortListener>) m_listeners.clone();
			}
			for (PortListener l : tempList) {
				l.msgReceived(msg); // deliver msg to listener
			}
		}
		
		/**
		 * Blocking wait for ack or nack from modem.
		 * Called by IOStreamWriter for flow control.
		 * @return true if retransmission is necessary
		 */
		public boolean waitForReply() {
			m_reply = ReplyType.WAITING_FOR_ACK;
			while (m_reply == ReplyType.WAITING_FOR_ACK) {
				try {
					getRequestReplyLock().wait();
				} catch (InterruptedException e) {
					// do nothing
				}
			}
			return (m_reply == ReplyType.GOT_NACK);
		}
	}
	/**
	 * Writes messages to the port. Flow control is implemented following Insteon
	 * documents to avoid over running the modem.
	 * 
	 * @author Bernd Pfrommer
	 */
	class IOStreamWriter implements Runnable {
		private static final int WAIT_TIME = 200; // milliseconds
		boolean m_keepRunning = true;
	
		public void stopThread() {
			synchronized (m_writeQueue) {
				m_keepRunning = false;
				m_writeQueue.notifyAll();
				synchronized (m_reader.getRequestReplyLock()) {
					m_reader.getRequestReplyLock().notifyAll();
				}
			}
		}
		@Override
		public void run() {
			while (true) {
				try {
					Msg msg;
					synchronized (m_writeQueue) {
						while (m_writeQueue.isEmpty() && m_keepRunning) {
							m_writeQueue.wait();
						}
						if (!m_keepRunning) return;
						msg = m_writeQueue.poll();
					}
					if (msg.getData() != null) {
						// To debug race conditions during startup (i.e. make the .items
						// file definitions be available *before* the modem link records,
						// slow down the modem traffic with the following statement:
						// Thread.sleep(500);
						synchronized (m_reader.getRequestReplyLock()) {
							m_stream.out().write(msg.getData());
							m_stream.out().flush();
							
							notifyListenersWrite(msg);
							
							while (m_reader.waitForReply() && m_keepRunning) {
								Thread.sleep(WAIT_TIME); // wait before retransmit!
								m_stream.out().write(msg.getData());
							}
						}
					}
					// if rate limited, need to sleep now.
					if (msg.getQuietTime() > 0) {
						Thread.sleep(msg.getQuietTime());
					}
				} catch (InterruptedException e) {
					return;
				} catch (IOException e) {
					try { Thread.sleep(30000);} catch (InterruptedException ie) {	}
				} catch (Exception e) {
				}
			}
		}
		@SuppressWarnings("unchecked")
		private void notifyListenersWrite(Msg msg) {
			logger.debug("Msg written: {}", msg);
			
			// When we deliver the message, the recipient
			// may in turn call removeListener() or addListener(),
			// thereby corrupting the very same collection that we are iterating
			// over. That's why we make a copy of it, and iterate over that.
			HashSet<PortListener> tempList = null;
			synchronized(m_listeners) {
				tempList= (HashSet<PortListener>) m_listeners.clone();
			}
			
			for (PortListener l : tempList) {
				l.msgWritten(msg); // deliver msg to listener
			}
		}
	}
}
