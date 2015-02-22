package us.pfrommer.insteon.cmd;

import us.pfrommer.insteon.cmd.msg.Msg;

public interface PortListener {
	public void wroteBytes(byte[] bytes);
	
	public void bytesReceived(byte[] bytes);
	public void msgReceived(Msg msg);
}
