package us.pfrommer.insteon.cmd;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.io.Reader;
import java.util.Scanner;

public class Terminal implements Console {
	private Scanner m_scanner = new Scanner(System.in);
	
	public Reader in() { return new InputStreamReader(System.in); }
	public PrintStream out() { return System.out; }
	public PrintStream err() { return System.err; }
	
	@Override
	public void clear() {
		
	}
	@Override
	public void reset() {
		
	}
	
	@Override
	public String readLine() throws IOException {
		return m_scanner.nextLine();
	}
	
	@Override
	public String readLine(String prompt) throws IOException {
		System.out.print(prompt);
		return m_scanner.nextLine();
	}
	
	public static void main(String[] args) throws IOException {
		InsteonInterpreter i = new InsteonInterpreter(new Terminal());
		i.run();
	}
}
