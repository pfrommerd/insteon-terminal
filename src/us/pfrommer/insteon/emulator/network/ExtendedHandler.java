package us.pfrommer.insteon.emulator.network;

import us.pfrommer.insteon.msg.InsteonAddress;
import us.pfrommer.insteon.msg.MsgType;

public interface ExtendedHandler {
	public void handleExtended(InsteonAddress from, MsgType type, int cmd1, int cmd2, byte[] data);
}
