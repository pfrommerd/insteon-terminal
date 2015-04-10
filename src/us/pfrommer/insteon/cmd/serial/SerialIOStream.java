package us.pfrommer.insteon.cmd.serial;

import gnu.io.CommPort;
import gnu.io.CommPortIdentifier;
import gnu.io.NoSuchPortException;
import gnu.io.PortInUseException;
import gnu.io.SerialPort;
import gnu.io.UnsupportedCommOperationException;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import us.pfrommer.insteon.cmd.IOStream;

public class SerialIOStream implements IOStream {
	private InputStream		m_in;
	private OutputStream	m_out;
	
	private	SerialPort		m_port		= null;
	private	final String	m_appName	= "PLM";
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
			/* by default, RXTX searches only devices /dev/ttyS* and
			 * /dev/ttyUSB*, and will so not find symlinks. The
			 *  setProperty() call below helps 
			 */
			System.setProperty("gnu.io.rxtx.SerialPorts", m_devName);
			CommPortIdentifier ci =
					CommPortIdentifier.getPortIdentifier(m_devName);
			CommPort cp = ci.open(m_appName, 1000);
			if (cp instanceof SerialPort) {
				m_port = (SerialPort)cp;
			} else {
				throw new IllegalStateException("unknown port type");
			}
			m_port.setSerialPortParams(m_speed, SerialPort.DATABITS_8,
					SerialPort.STOPBITS_1, SerialPort.PARITY_NONE);
			m_port.setFlowControlMode(SerialPort.FLOWCONTROL_NONE);
			m_port.disableReceiveFraming();
			m_port.disableReceiveThreshold();
			//m_port.enableReceiveThreshold(1000);
			//Do receive timeout so we can check if the reader has to stop
			m_port.enableReceiveTimeout(1000);
			
			m_in	= m_port.getInputStream();
			m_out	= new NoFlushOutputStream(m_port.getOutputStream());
		} catch (IOException e) {
			throw e;
		} catch (PortInUseException e) {
			throw new IOException(e);
		} catch (UnsupportedCommOperationException e) {
			throw new IOException(e);
		} catch (NoSuchPortException e) {
			throw new IOException(e);
		} catch (IllegalStateException e) {
			throw new IOException(e);
		}
	}

	@Override
	public void close() throws IOException {
		if (m_in != null) m_in.close();
		if (m_out != null) m_out.close();
		if (m_port != null) {
			m_port.close();
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
