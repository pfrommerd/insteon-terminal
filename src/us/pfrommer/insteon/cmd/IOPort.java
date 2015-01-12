package us.pfrommer.insteon.cmd;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashSet;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class IOPort {
	private IOStream m_stream;
	
	private ByteWriter m_writer;
	private ByteReader m_reader;
	
	private Thread m_readThread;
	private Thread m_writeThread;
	
	private BlockingQueue<byte[]> m_writeQueue = new LinkedBlockingQueue<byte[]>();
	private HashSet<PortListener> m_listeners = new HashSet<PortListener>();
	
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
		m_writer = new ByteWriter();
		m_reader = new ByteReader();
		
		if (!m_stream.isOpen()) m_stream.open();
		
		m_readThread = new Thread(m_reader);
		m_writeThread = new Thread(m_writer);
		
		m_readThread.start();
		m_writeThread.start();
	}
	
	public void close() throws IOException {
		if (!m_stream.isOpen()) return;
		//Wait for the write queue to be empty
		synchronized(m_writeQueue) {
			while (!m_writeQueue.isEmpty()) {
				try {
					m_writeQueue.wait();
				} catch (InterruptedException e) {
					break;
				} 
			}
		}
		
		
		if (m_readThread != null) m_readThread.interrupt();
		if (m_writeThread != null) m_writeThread.interrupt();
		
		m_reader = null;
		m_writer = null;
		
		if (m_stream.isOpen()) m_stream.close();
	}
	
	public void write(byte[] buf) {
		m_writeQueue.add(buf);
	}
	
	public class ByteWriter implements Runnable {
		@Override
		public void run() {
			while(!Thread.currentThread().isInterrupted()) {
				try {
					byte[] buf = m_writeQueue.take();
					m_stream.out().write(buf);
					m_stream.out().flush();
					synchronized(m_writeQueue) {
						m_writeQueue.notifyAll();
					}
				} catch (InterruptedException e) {
					break;
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}
	
	public class ByteReader implements Runnable {
		@Override
		public void run() {
			try {
				//Start reading
				InputStream is = m_stream.in();
				int len;
				byte[] buffer = new byte[1024];
				while((len = is.read(buffer)) >= 0 && !Thread.currentThread().isInterrupted()) {
					if (len > 0) {
						byte[] bytes = new byte[len];
						System.arraycopy(buffer, 0, bytes, 0, len);
						synchronized(m_listeners) {
							for (PortListener l : m_listeners)
								l.bytesReceived(bytes);
						}
					}
				}
			} catch (IOException e) {
				e.printStackTrace();;
			}
		}
	}
}
