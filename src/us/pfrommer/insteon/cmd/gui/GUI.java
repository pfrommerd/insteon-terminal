package us.pfrommer.insteon.cmd.gui;

import java.io.IOException;

import us.pfrommer.insteon.cmd.InsteonInterpreter;

public class GUI {
	public static void main(String[] args) throws IOException {
		JConsole console = new JConsole();
		console.setDefaultCloseOperation(JConsole.EXIT_ON_CLOSE);
		
		System.setIn(console.in());
		System.setErr(console.out());
		System.setOut(console.out());
		
		console.setVisible(true);
		InsteonInterpreter i = new InsteonInterpreter(console);
		i.run();
	}
}