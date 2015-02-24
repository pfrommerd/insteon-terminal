package us.pfrommer.insteon.cmd;

public interface ConsoleListener {
	//For Ctrl-C
	//should terminate the current running command
	public void terminate();
}
