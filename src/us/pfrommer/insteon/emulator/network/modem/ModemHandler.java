package us.pfrommer.insteon.emulator.network.modem;

import us.pfrommer.insteon.msg.Msg;

public interface ModemHandler {	
	public void handle(Msg m);
}