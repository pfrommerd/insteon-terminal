package us.pfrommer.insteon.cmd.msg.hub;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.net.UnknownHostException;

import us.pfrommer.insteon.cmd.msg.IOStream;

public class LegacyHubStream implements IOStream {
	private Socket m_socket;
	
	private InputStream m_in;
	private OutputStream m_out;
	
	private String m_host;
	private int m_port;
	
	public LegacyHubStream(String host, int port) {
		m_host = host;
		m_port = port;
	}
	
	public boolean isOpen() {
		return m_socket != null;
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
	public void open() throws IOException {
		try {
			m_socket = new Socket(m_host, m_port);
			m_socket.setSoTimeout(1000);
			m_in	 = new NonBlockingStream(m_socket.getInputStream());
			m_out 	 = m_socket.getOutputStream();
		} catch (UnknownHostException e) {
			throw new IOException("Unkown host: " + m_host, e);
		} catch (IOException e) {
			throw new IOException("Failed to open connection to " + m_host, e);
		}
	}

	@Override
	public void close() throws IOException {
		try {
			if (m_socket != null) m_socket.close();
		} catch (IOException e) {
			throw new IOException("Failed to close connection to hub!", e);
		}
	}
	
	public static class NonBlockingStream extends InputStream {
		public InputStream m_in;
		
		public NonBlockingStream(InputStream in) {
			m_in = in;
		}
		
		@Override
		public int read() throws IOException {
			try {
				return m_in.read();
			} catch (SocketTimeoutException e) {
				return -2; 
			}
		}
		
		@Override
		public int read(byte[] b, int off, int len) throws IOException {
			try {
				return m_in.read(b, off, len);
			} catch (SocketTimeoutException e) {
				return 0;
			}
		}
	}
}
