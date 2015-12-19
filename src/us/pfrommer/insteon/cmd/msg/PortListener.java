package us.pfrommer.insteon.cmd.msg;


public interface PortListener extends MsgListener {
	public void msgWritten(Msg msg);
	public void msgReceived(Msg msg);
}
