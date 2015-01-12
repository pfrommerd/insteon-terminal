package us.pfrommer.insteon.cmd.hub;

import us.pfrommer.insteon.cmd.Command;
import us.pfrommer.insteon.cmd.IOPort;
import us.pfrommer.insteon.cmd.InsteonInterpreter;

public class HubConnectCommand implements Command {
	@Override
	public String getCmd() {
		return "connect_hub";
	}

	@Override
	public String getDesc() {
		return "connect to an insteon hub via the http interface";
	}

	@Override
	public String getUsage() {
		return getCmd() + " <host> <port> <pollrate> [user] [pass]";
	}

	@Override
	public void exec(InsteonInterpreter interpreter, String... args) {
		if (args.length < 3) {
			interpreter.err().println("Usage:" + getUsage());
			return;
		}
		String host = args[0];
		int port = Integer.parseInt(args[1]);
		int pollRate = Integer.parseInt(args[2]);
		String user = null;
		String pass = null;
		if (args.length >= 5) {
			user = args[3];
			pass = args[4];
		}
		interpreter.out().println("connecting to hub...");
		interpreter.setPort(new IOPort(new HubStream(host, port, pollRate, user, pass)));
	}

}
