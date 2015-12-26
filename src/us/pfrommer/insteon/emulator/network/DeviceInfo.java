package us.pfrommer.insteon.emulator.network;

import us.pfrommer.insteon.msg.InsteonAddress;

public class DeviceInfo {
	private InsteonAddress m_address;
	
	private byte m_deviceCategory;
	private byte m_subCategory;
	private byte m_firmwareVersion;
	
	public DeviceInfo(InsteonAddress adr, byte devCat, byte subCat, byte version) {
		m_address = adr;
		m_deviceCategory = devCat;
		m_subCategory = subCat;
		m_firmwareVersion = version;
	}

	public DeviceInfo(InsteonAddress adr, int devCat, int subCat, int version) {
		m_address = adr;
		m_deviceCategory = (byte) (devCat & 0xFF);
		m_subCategory = (byte) (subCat & 0xFF);
		m_firmwareVersion = (byte) (version & 0xFF);
	}

	public InsteonAddress getAddress() { return m_address; }
	public byte getDeviceCategory() { return m_deviceCategory; }
	public byte getSubCategory() { return m_subCategory; }
	public byte getFirmwareVersion() { return m_firmwareVersion; }
}
