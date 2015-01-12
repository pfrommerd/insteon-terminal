package us.pfrommer.insteon.cmd.serial;

import us.pfrommer.insteon.cmd.Command;
import us.pfrommer.insteon.cmd.IOPort;
import us.pfrommer.insteon.cmd.InsteonInterpreter;

public class SerialConnectCommand implements Command {
	@Override
	public String getCmd() {
		return "connect_serial";
	}

	@Override
	public String getDesc() {
		return "connects to a insteon plm via a serial port";
	}

	@Override
	public String getUsage() {
		return getCmd() + " <deviceName/path>";
	}

	@Override
	public void exec(InsteonInterpreter interpreter, String... args) {
		if (args.length < 1) {
			interpreter.err().println("Usage " + getUsage());
			return;
		}
		String devName = args[0];
		
		interpreter.out().println("connecting to serial port " + devName);
		interpreter.setPort(new IOPort(new SerialIOStream(devName)));
	}
}
