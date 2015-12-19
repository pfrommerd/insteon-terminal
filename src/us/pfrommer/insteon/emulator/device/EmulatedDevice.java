package us.pfrommer.insteon.emulator.device;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.emulator.ModemEmulator;
import us.pfrommer.insteon.msg.InsteonAddress;
import us.pfrommer.insteon.msg.Msg;

public class EmulatedDevice {
	private static final Logger logger = LoggerFactory.getLogger(EmulatedDevice.class);
	
	private DeviceInfo m_info;
	private LinkDatabase m_linkDB;
	
	protected ModemEmulator m_modem;
	
	public EmulatedDevice(ModemEmulator modem, DeviceInfo info) {
		m_modem = modem;
		
		if (m_modem != null) m_modem.setRouting(info.getAddress(), this);
		
		m_info = info;
		m_linkDB = new LinkDatabase();
	}
	
	public DeviceInfo getInfo() { return m_info; }
	
	public LinkDatabase getLinkDB() { return m_linkDB; }
	public void setLinkDB(LinkDatabase db) { m_linkDB = db; }
	
	public void send(Msg m) {
		m_modem.route(this, m);
	}
	
	public void receive(Msg m) {
		String type = m.getDefinition().getName();
		
		if (type.equals("StandardMessageReceived")) {
			try {
				InsteonAddress sender = m.getAddress("fromAddress");
				byte cmd1 = m.getByte("command1");
				byte cmd2 = m.getByte("command2");
				
				onStandardMsg(sender, cmd1 & 0xFF, cmd2 & 0xFF);
			} catch (Exception e) {
				logger.error("Failed to unwrap standard message", e);
			}
		}
	}
	
	public void onStandardMsg(InsteonAddress sender, int cmd1, int cmd2) {}
}
