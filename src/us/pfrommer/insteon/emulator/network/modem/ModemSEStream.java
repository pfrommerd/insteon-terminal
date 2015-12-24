package us.pfrommer.insteon.emulator.network.modem;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import us.pfrommer.insteon.msg.IOStream;
import us.pfrommer.insteon.msg.Msg;
import us.pfrommer.insteon.msg.Msg.Direction;
import us.pfrommer.insteon.msg.MsgReader;
import us.pfrommer.insteon.utils.ByteArrayIO;

public class ModemSEStream implements IOStream, ModemListener {
	private ModemSE m_modem;
	
	//Input and out are switched
	
	// out is for writing to the modem
	// in is for reading from the modem
	private ModemOutputStream m_out = new ModemOutputStream();
	private ModemInputStream m_in = new ModemInputStream();
	
	public ModemSEStream(ModemSE m) {
		m_modem = m;
		m.addListener(this);
	}
	
	@Override
	public boolean isOpen() {
		return m_modem != null;
	}

	@Override
	public InputStream in() {
		return m_in;
	}

	@Override
	public OutputStream out() {
		return m_out;
	}

	@Override
	public void open() throws IOException {}

	@Override
	public void close() throws IOException {
		m_modem.removeListener(this);
		m_modem = null;
	}

	@Override
	public void onMsgSent(Msg m) {
		m_in.onMsg(m);
	}

	@Override
	public void onMsgReceived(Msg m) {}
	
	public class ModemOutputStream extends OutputStream {
		private MsgReader m_reader = new MsgReader(Direction.TO_MODEM);
		
		@Override
		public void write(byte[] b, int off, int len) throws IOException {
			m_reader.addData(b, off, len);
			processMessages();
		}
		
		@Override
		public void write(int b) throws IOException {
			m_reader.addData((byte) (b & 0xFF));
			processMessages();
		}
		
		public void processMessages() throws IOException {
			for (Msg m = m_reader.processData(); m != null;
					 m = m_reader.processData()) {
				m_modem.receiveFromHost(m);
			}
		}
	}
	
	public class ModemInputStream extends InputStream {
		private ByteArrayIO m_buffer = new ByteArrayIO();
		
		public void onMsg(Msg m) {
			m_buffer.add(m.getData());
		}
		
		public int read(byte[] b, int off, int len) {
			try {
				int ret = m_buffer.get(b, off, len);
				m_buffer.compact();
				return ret;
			} catch (InterruptedException e) {
				return 0;
			}
		}
		
		@Override
		public int read() throws IOException {
			try {
				return m_buffer.get();
			} catch (InterruptedException e) {
				return -1;
			}
		}
	}

}
