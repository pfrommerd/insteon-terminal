package us.pfrommer.insteon.emulator;

import us.pfrommer.insteon.msg.Msg;

public interface ModemHandler {	
	public void handle(ModemEmulator emulator, Msg m);
}
