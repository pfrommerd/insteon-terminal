package us.pfrommer.insteon.cmd.console;

import java.io.IOException;
import java.io.PrintStream;
import java.io.Reader;

public interface Console {
	public String readLine() throws IOException;
	public String readLine(String prompt) throws IOException;
	
	public void addConsoleListener(ConsoleListener l);
	public void removeConsoleListener(ConsoleListener l);
	
	public Reader in();
	public PrintStream out();
	public PrintStream err();
	
	public void clear();
	public void reset();
}
