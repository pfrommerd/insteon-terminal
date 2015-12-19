package us.pfrommer.insteon.emulator;

import us.pfrommer.insteon.msg.Msg;

public interface ModemListener {
	public void onMsgSent(Msg m);
	public void onMsgReceived(Msg m);
}
