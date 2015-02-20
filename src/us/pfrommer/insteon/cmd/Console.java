package us.pfrommer.insteon.cmd;

import java.io.IOException;
import java.io.PrintStream;
import java.io.Reader;

public interface Console {
	public String readLine() throws IOException;
	public String readLine(String prompt) throws IOException;
	
	public Reader in();
	public PrintStream out();
	public PrintStream err();
	
	public void clear();
	public void reset();
}
