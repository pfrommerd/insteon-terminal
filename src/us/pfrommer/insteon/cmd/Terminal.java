package us.pfrommer.insteon.cmd;

import java.io.IOException;
import java.io.InputStream;
import java.io.PrintStream;

public class Terminal implements Console {
	public InputStream in() { return System.in; }
	public PrintStream out() { return System.out; }
	public PrintStream err() { return System.err; }
	
	public static void main(String[] args) throws IOException {
		InsteonInterpreter i = new InsteonInterpreter(new Terminal());
		i.run();
	}
}
