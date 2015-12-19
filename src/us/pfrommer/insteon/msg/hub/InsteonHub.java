package us.pfrommer.insteon.msg.hub;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;

import org.apache.http.HttpResponse;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import us.pfrommer.insteon.utils.ByteArrayIO;

public class InsteonHub implements Runnable {
	private String m_host 						= null;
	private int m_port 							= -1;
	
	private CloseableHttpClient m_client 		= null;
	
	//The index of the last byte we have read in the buffer
	private int m_bufferIdx 			= -1;
	private int m_pollTime 				= 1000;
	
	private HubInputStream m_input 		= null;
	private HubOutputStream m_output 	= null;
	
	private Thread m_pollThread = null;
	
	public InsteonHub(String host, int port, int pollTime) {
		m_host = host;
		m_port = port;
		m_pollTime = pollTime;
	}
	
	public InputStream getInputStream() { return m_input; }
	public OutputStream getOutputStream() { return m_output; }
	
	public String getHost() { return m_host; }
	public int getPort() { return m_port; }

	public boolean isConnected() { return m_client != null; }
	
	public void connect() throws IOException {
		m_client = HttpClients.createSystem();

		m_input = new HubInputStream();
		m_output = new HubOutputStream();
		
		m_pollThread = new Thread(this);
		m_pollThread.start();
	}
	
	public void connect(String username, String password) throws IOException {
		CredentialsProvider credsProvider = new BasicCredentialsProvider();
		credsProvider.setCredentials(new AuthScope(m_host,  m_port), 
									new UsernamePasswordCredentials(username, password));
		
		HttpClientBuilder builder = HttpClients.custom();
		builder.setDefaultCredentialsProvider(credsProvider);
		
		m_client = builder.build();
		
		m_input = new HubInputStream();
		m_output = new HubOutputStream();
		
		clearBuffer();

		m_pollThread = new Thread(this);
		m_pollThread.start();
	}
	
	public void disconnect() throws IOException {
		m_client = null;
		if (m_pollThread != null) m_pollThread.interrupt();
		
		if (m_input != null) m_input.close();
		if (m_output != null) m_output.close();
	}
	
	public synchronized String bufferStatus() throws IOException {
		String result = getURL("/buffstatus.xml");
		result = result.split("<BS>")[1].split("</BS>")[0].trim();
		return result;
	}
	
	public synchronized void clearBuffer() throws IOException {
		getURL("/1?XB=M=1");
		m_bufferIdx = 0;
	}
	
	public synchronized void write(ByteBuffer msg) throws IOException {
		//Poll before we read to ensure we're not missing anything
		poll();
		
		clearBuffer();
		StringBuilder b = new StringBuilder();
		while (msg.remaining() > 0) {
			b.append(String.format("%02x", msg.get()));
		}
		String hexMSG = b.toString();
		getURL("/3?"+ hexMSG + "=I=3");
		//After receiving data, the modem will clear the buffer
		m_bufferIdx = 0;
	}

	public void poll() throws IOException {
		String buffer = bufferStatus();
		String data = buffer.substring(0, buffer.length() - 2);

		//The new idx
		int nIdx = Integer.parseInt(buffer.substring(buffer.length() - 2, buffer.length()), 16);
		
		if (m_bufferIdx == -1) {
			m_bufferIdx = nIdx;
			return;
		}
		
		StringBuilder msg = new StringBuilder();
		if (nIdx < m_bufferIdx) {
			String after = data.substring(m_bufferIdx);
			
			//Do some basic checking
			//if everything after the last index was 0
			//then most likely someone has cleared the buffer
			//note: this will not solve all problems around someone else
			//clearing the buffer!
			
			if (!after.matches("0+")) {
				msg.append(after);
			}
			
			msg.append(data.substring(0, nIdx));
		} else {
			msg.append(data.substring(m_bufferIdx, nIdx));
		}
		if (msg.length() != 0) {
			ByteBuffer buf = ByteBuffer.wrap(s_hexStringToByteArray(msg.toString()));
			m_input.handle(buf);
		}
		m_bufferIdx = nIdx;
	}
	private String getURL(String resource) throws IOException {
		StringBuilder b = new StringBuilder();
		b.append("http://");
		b.append(m_host);
		if (m_port != -1) {
			b.append(":").append(m_port);
		}
		b.append(resource);

		HttpGet get = new HttpGet(b.toString());
		HttpResponse res = m_client.execute(get);
		if (res.getStatusLine().getStatusCode() == 401)
			throw new IOException("Bad authentication...access forbidden");
		return EntityUtils.toString(res.getEntity());
    }
	
	public void run() {
		while(!Thread.currentThread().isInterrupted()) {
			try {
				poll();
			} catch (IOException e) {
				e.printStackTrace();
			}
			try {
				Thread.sleep(m_pollTime);
			} catch (InterruptedException e) {
				break;
			}
		}
	}

	public static byte[] s_hexStringToByteArray(String s) {
	    int len = s.length();
	    byte[] data = new byte[len / 2];
	    for (int i = 0; i < len; i += 2) {
	        data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
	                             + Character.digit(s.charAt(i+1), 16));
	    }
	    return data;
	}
	
	public class HubInputStream extends InputStream {	
		private ByteArrayIO m_buffer = new ByteArrayIO(1024);

		public HubInputStream() {}
		
		public void handle(ByteBuffer buffer) throws IOException {
			//Make sure we cleanup as much space as possible
			m_buffer.compact();
			m_buffer.add(buffer.array());
		}
		
		@Override
		public int read() throws IOException {
			try {
				return m_buffer.get();
			} catch (InterruptedException e) {
				throw new IOException(e);
			}
		}
		public int read(byte[] b, int off, int len) throws IOException {
			try {
				return m_buffer.get(b, off, len);
			} catch (InterruptedException e) {
				return 0;
			}
		}
		@Override
		public void close() throws IOException {}
	}
	public class HubOutputStream extends OutputStream {
		private ByteArrayOutputStream m_out = new ByteArrayOutputStream();
		
		@Override
		public void write(int b) throws IOException {
			m_out.write(b);
		}
		@Override
		public void write(byte[] b, int off, int len) {
			m_out.write(b, off, len);
		}
		@Override
		public void flush() {
			ByteBuffer buffer = ByteBuffer.wrap(m_out.toByteArray());
			
			try {
				InsteonHub.this.write(buffer);
			} catch (IOException e) {
				e.printStackTrace();
			}
			
			m_out.reset();
		}
	}
}
