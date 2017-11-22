package us.pfrommer.insteon.msg.serial;

import com.fazecast.jSerialComm.SerialPort;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import us.pfrommer.insteon.msg.IOStream;

public class SerialIOStream implements IOStream {
	private InputStream		m_in;
	private OutputStream	m_out;
	
	private	SerialPort		m_port		= null;
	private final int		m_speed		= 19200; // baud rate
	private String			m_devName 	= null;
	
	public SerialIOStream(String devName) {
		m_devName = devName;
	}
	
	public boolean isOpen() { return m_in != null && m_out != null; }
	
	public OutputStream out() { return m_out; }
	public InputStream in() { return m_in; }
	
	@Override
	public void open() throws IOException {
		try {
            m_port = SerialPort.getCommPort(m_devName);
            m_port.setComPortParameters(m_speed, 8, SerialPort.ONE_STOP_BIT, SerialPort.NO_PARITY);
            m_port.setComPortTimeouts(SerialPort.TIMEOUT_READ_SEMI_BLOCKING, 0, 0);
            m_port.setFlowControl(SerialPort.FLOW_CONTROL_DISABLED);
            if (m_port.openPort()) {
                m_in = m_port.getInputStream();
                m_out = m_port.getOutputStream();
            } else {
                m_port = null;
                throw new IOException("IO Error, could not open port: " + m_devName);
            }
        } catch(IOException e) {
            throw e;
        } catch (Exception e) {
            throw new IOException(e);
        }
	}

	@Override
	public void close() throws IOException {
		if (m_in != null) m_in.close();
		if (m_out != null) m_out.close();
		if (m_port != null) {
			m_port.closePort();
		}
		m_port = null;
		m_in = null;
		m_out = null;
	}
	
	private class NoFlushOutputStream extends OutputStream {
		private OutputStream m_output;
		
		public NoFlushOutputStream(OutputStream out) {
			m_output = out;
		}
		
		@Override
		public void write(int b) throws IOException {
			m_output.write(b);
		}
		
		@Override
		public void write(byte[] b, int off, int len) throws IOException {
			m_output.write(b, off, len);
		}
		
		@Override
		public void flush() {}
	}
}
