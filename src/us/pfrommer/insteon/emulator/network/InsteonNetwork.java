package us.pfrommer.insteon.emulator.network;

import java.util.HashMap;

import us.pfrommer.insteon.msg.InsteonAddress;
import us.pfrommer.insteon.msg.MsgType;

/**
 * The insteon network handles all the message routing
 * @author Daniel Pfrommer
 */
public class InsteonNetwork {
	private HashMap<InsteonAddress, Device> m_devices = new HashMap<InsteonAddress, Device>();

	public InsteonNetwork() {
		
	}
	
	public void addDevice(Device d) {
		m_devices.put(d.getInfo().getAddress(), d);
		d.setNetwork(this);
	}

	public void removeDevice(Device d) {
		m_devices.remove(d.getInfo().getAddress());
		d.setNetwork(null);
	}

	// For message routing
	public Device resolve(InsteonAddress a) {
		return m_devices.get(a);
	}
	
	public void routeStandard(InsteonAddress from, InsteonAddress to, MsgType type, int cmd1, int cmd2) {
		Device d = m_devices.get(to);
		if (d != null) d.onStandardMsg(from, type, cmd1, cmd2);
	}
	
	public void routeExtended(InsteonAddress from, InsteonAddress to, MsgType type, int cmd1, int cmd2, byte[] data) {
		Device d = m_devices.get(to);
		if (d != null) d.onExtendedMsg(from, type, cmd1, cmd2, data);
	}

}
