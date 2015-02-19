package us.pfrommer.insteon.cmd;

import us.pfrommer.insteon.cmd.msg.Msg;

public interface PortListener {
	public void bytesReceived(byte[] bytes);
	public void msgReceived(Msg msg);
}
