package us.pfrommer.insteon.emulator.device;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.emulator.ModemEmulator;
import us.pfrommer.insteon.msg.InsteonAddress;

public class Switch2477SEmulator extends EmulatedDevice {
	private static final Logger logger = LoggerFactory.getLogger(Switch2477SEmulator.class);
	
	public Switch2477SEmulator(ModemEmulator modem, InsteonAddress adr) {
		super(modem, new DeviceInfo(adr, 0x00, 0x00, 0x01));
	}

	public Switch2477SEmulator(ModemEmulator modem, String adr) {
		this(modem, new InsteonAddress(adr));
	}

	@Override
	public void onStandardMsg(InsteonAddress sender, int cmd1, int cmd2) {
		logger.info("Light received: {} {}", cmd1, cmd2);
		
		
	}
}
