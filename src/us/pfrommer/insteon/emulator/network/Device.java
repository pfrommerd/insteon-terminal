package us.pfrommer.insteon.emulator.network;

import java.util.HashMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.msg.InsteonAddress;
import us.pfrommer.insteon.msg.MsgType;

public abstract class Device {
	private static final Logger logger = LoggerFactory.getLogger(Device.class);
	
	protected InsteonNetwork m_network = null;
	
	private String m_name = null;
	
	private DeviceInfo m_info = null;
	private LinkDatabase m_linkDB = null;	
	
	private HashMap<Integer, StandardHandler> m_standardHandlers = new HashMap<Integer, StandardHandler>();
	private HashMap<Integer, ExtendedHandler> m_extendedHandlers = new HashMap<Integer, ExtendedHandler>();
	
	public Device(String name, DeviceInfo info) {
		m_name = name;
		m_info = info;
		m_linkDB = new LinkDatabase();
	}
	
	public String getName() { return m_name; }
	public DeviceInfo getInfo() { return m_info; }
	public LinkDatabase getLinkDB() { return m_linkDB; }

	public InsteonNetwork getNetwork() { return m_network; }

	public void setName(String name) { m_name = name; }
	public void setLinkDB(LinkDatabase db) { m_linkDB = db; }
	
	protected void setNetwork(InsteonNetwork n) { m_network = n; }
	
	
	public void addStandardHandler(int cmd1, StandardHandler handler) {
		m_standardHandlers.put(cmd1, handler);
	}
	
	public void addExtendedHandler(int cmd1, ExtendedHandler handler) {
		m_extendedHandlers.put(cmd1, handler);
	}
	
	public void onStandardMsg(InsteonAddress sender, MsgType type, int cmd1, int cmd2) {
		StandardHandler h = m_standardHandlers.get(cmd1);
		
		if (h != null) {
			h.handleStandard(sender, type, cmd1, cmd2);
		}
	}
	
	public void onExtendedMsg(InsteonAddress sender, MsgType type, int cmd1, int cmd2, byte[] data) {
		ExtendedHandler h = m_extendedHandlers.get(cmd1);
		
		if (h != null) {
			h.handleExtended(sender, type, cmd1, cmd2, data);
		}
	}
	
	public void sendStandardMsg(InsteonAddress to, MsgType type, int cmd1, int cmd2) {
		if (m_network != null) m_network.routeStandard(getInfo().getAddress(), to, type, cmd1, cmd2);
		else logger.warn("Cannot send message as device not connected to the network!");
	}

	public void sendExtendedMsg(InsteonAddress to, MsgType type, int cmd1, int cmd2, byte[] data) {
		if (m_network != null) m_network.routeStandard(getInfo().getAddress(), to, type, cmd1, cmd2);
		else logger.warn("Cannot send message as device not connected to the network!");
	}

}
