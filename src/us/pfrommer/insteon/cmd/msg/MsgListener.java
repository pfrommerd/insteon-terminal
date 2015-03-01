package us.pfrommer.insteon.cmd.msg;

//Like PortListener, but only msgReceived
public interface MsgListener {
	public void msgReceived(Msg msg);
}
