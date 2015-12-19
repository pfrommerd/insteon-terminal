package us.pfrommer.insteon.cmd.msg.hub;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import us.pfrommer.insteon.InsteonHub;
import us.pfrommer.insteon.cmd.msg.IOStream;

public class HubStream implements IOStream {
	private InsteonHub m_hub;
	
	private String m_user;
	private String m_pass;
	
	public HubStream(String adr, int port, int pollTime, String user, String pass) {
		m_hub = new InsteonHub(adr, port, pollTime);
		m_user = user;
		m_pass = pass;
	}
	
	public boolean isOpen() {
		return m_hub.isConnected();
	}
	
	@Override
	public InputStream in() {
		return m_hub.getInputStream();
	}

	@Override
	public OutputStream out() {
		return m_hub.getOutputStream();
	}

	@Override
	public void open() throws IOException {
		if (m_user == null || m_pass == null) m_hub.connect();
		else m_hub.connect(m_user, m_pass);
	}

	@Override
	public void close() throws IOException {
		m_hub.disconnect();
	}
}
