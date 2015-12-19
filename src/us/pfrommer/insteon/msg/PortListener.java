package us.pfrommer.insteon.msg;


public interface PortListener extends MsgListener {
	public void msgWritten(Msg msg);
	public void msgReceived(Msg msg);
}
