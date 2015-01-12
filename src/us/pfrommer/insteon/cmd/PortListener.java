package us.pfrommer.insteon.cmd;

public interface PortListener {
	public void bytesReceived(byte[] bytes);
}
