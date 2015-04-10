package us.pfrommer.insteon.cmd;

import us.pfrommer.insteon.cmd.msg.Msg;

public interface PortListener {
	public void msgWritten(Msg msg);
	public void msgReceived(Msg msg);
}
