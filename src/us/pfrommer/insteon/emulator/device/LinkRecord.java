package us.pfrommer.insteon.emulator.device;

import us.pfrommer.insteon.msg.InsteonAddress;

public class LinkRecord {
	private LinkType m_type;

	private InsteonAddress m_address;

	private byte m_group;
	
	private byte m_data1;
	private byte m_data2;
	private byte m_data3;
	
	public LinkRecord() {}

	public LinkType getType() 			{ return m_type; }
	public InsteonAddress getAddress() 	{ return m_address; }
	public int getGroup() 				{ return m_group; }

	public byte getData1() 				{ return m_data1; }
	public byte getData2()				{ return m_data2; }
	public byte getData3() 				{ return m_data3; }

	public void setType(LinkType type) { m_type = type; }
	public void setAddress(InsteonAddress address) { m_address = address; }
	public void setGroup(int group) { m_group = (byte) (group & 0xFF); }

	public void setData1(byte data1) { m_data1 = data1; }
	public void setData2(byte data2) { m_data2 = data2; }
	public void setData3(byte data3) { m_data3 = data3; }
}
