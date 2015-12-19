package us.pfrommer.insteon.cmd;

import java.io.File;
import java.io.PrintStream;
import java.io.Reader;

import org.python.core.Py;
import org.python.util.PythonInterpreter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.cmd.console.Console;

public class InsteonTerminal {
	private static Logger logger = LoggerFactory.getLogger(InsteonTerminal.class);
	
	private PythonInterpreter m_interpreter = null;
	private Console m_console = null;
	private IOFun m_iofun = null;
	
	public InsteonTerminal() {}
	
	public PythonInterpreter 	getInterpreter() { return m_interpreter; }
	public Console 				getConsole() { return m_console; }
	public IOFun				getIOFun() { return m_iofun; }
	
	public Reader 		in() { return m_iofun.in(); }
	public PrintStream 	out() { return m_iofun.out(); }
	public PrintStream 	err() { return m_iofun.err(); }
	
	//Interpreter functions

	public void init() throws Exception {
		logger.info("Setting up interpreter...");
		
		if (m_interpreter != null) {
			m_interpreter.cleanup();
			m_interpreter = null;
		}
		
		m_interpreter = new PythonInterpreter();
		
		m_interpreter.setOut(out());
		m_interpreter.setIn(in());
		m_interpreter.setErr(err());
		
		File f = new File(".");
		File init = new File(f, "init.py");
		File python = new File(f, "python");
		
		try {
			m_interpreter.exec("import sys");

			//Remove all existing modules so we can reload them
			m_interpreter.exec("sys.modules.clear()");

			m_interpreter.exec("sys.path.append('" + f.getAbsolutePath() + "')");
			m_interpreter.exec("sys.path.append('" + python.getAbsolutePath() + "')");

			//Import commands
			
			m_interpreter.exec("import iofun");			

			//Call the init function to setup the python-console bridge
			m_interpreter.get("iofun").__getattr__("_init_io_fun").__call__(Py.java2py(m_iofun));

			m_interpreter.exec("import console_commands");			

			m_interpreter.exec("from console_commands import *");		

			
			if (init.exists()) {
				//Import init
				m_interpreter.exec("from init import *");
			}

		} catch (Exception e) {
			throw e;
		}
	}
	
	
	public void run(Console c) {
		m_console = c;				
		m_iofun = new IOFun(this, c);

		//Initialize the console
		
		logger.info("Starting terminal");

		out().println("Insteon Terminal");
		
		try {
			init();
			out().println("Terminal ready!");
		} catch (Exception e) {
			out().println("Failed to initialize python interpreter: " + e.getMessage());
			e.printStackTrace(err());
		}

		logger.info("Terminal started");

		
		try{
			while(true) {
				String line = m_console.readLine(">>> ");
				if (line.trim().isEmpty()) continue;
				line = line.trim();
				exec(line);
			}
		} catch(Exception io){
			io.printStackTrace();
		}
	}
	
	public void exec(String line) {
		if (line.equals("help")) {
			out().println("Use help()");
		} else if (line.equals("exit")) {
			out().println("Use exit()");
		} else if (line.equals("quit")) {
			out().println("Use quit()");
		} else if (line.equals("clear")) {
			out().println("Use clear()");
		} else if (line.equals("reset")) {
			out().println("Use reset()");
		} else if (line.equals("?")) {
			//TODO: Fix
			out().println("STUB: This functionality has been temporarily removed");
		} else {
			if (m_interpreter != null) {
				try {
					m_interpreter.exec(line);
				} catch (Exception e) {
					e.printStackTrace(err());
				}
			}
		}
	}
	
	
	//Terminate the current running program
	//TODO: Figure out how to do this
	public void terminate() {
		out().println("terminate() called: no way to terminate a running python program");
	}
}
