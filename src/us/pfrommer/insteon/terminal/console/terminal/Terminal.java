package us.pfrommer.insteon.terminal.console.terminal;

import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.io.Reader;
import java.util.Scanner;

import us.pfrommer.insteon.terminal.InsteonTerminal;
import us.pfrommer.insteon.terminal.console.Console;
import us.pfrommer.insteon.terminal.console.ConsoleListener;

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
	public void addConsoleListener(ConsoleListener l) {
		
	}
	@Override
	public void removeConsoleListener(ConsoleListener l) {
		
	}
	
	@Override
	public String readLine(String prompt) throws IOException {
		System.out.print(prompt);
		return m_scanner.nextLine();
	}
}
