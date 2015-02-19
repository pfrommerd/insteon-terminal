package us.pfrommer.insteon.cmd;

import java.io.InputStream;
import java.io.PrintStream;

public interface Console {
	public InputStream in();
	public PrintStream out();
	public PrintStream err();
}
