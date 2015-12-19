package us.pfrommer.insteon.msg;

//Like PortListener, but only msgReceived
public interface MsgListener {
	public void msgReceived(Msg msg);
}
