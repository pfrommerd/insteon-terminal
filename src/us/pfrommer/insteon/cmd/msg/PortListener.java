package us.pfrommer.insteon.cmd.msg;


public interface PortListener {
	public void msgWritten(Msg msg);
	public void msgReceived(Msg msg);
}
