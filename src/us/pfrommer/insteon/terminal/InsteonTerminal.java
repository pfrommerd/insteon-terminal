package us.pfrommer.insteon.terminal;

import java.io.File;
import java.io.PrintStream;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import org.python.core.Py;
import org.python.core.PyFunction;
import org.python.core.PyStringMap;
import org.python.util.PythonInterpreter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.terminal.console.Console;

public class InsteonTerminal {
	private static Logger logger = LoggerFactory.getLogger(InsteonTerminal.class);
	
	private PythonInterpreter m_interpreter = null;
	private Console m_console = null;
	private IOFun m_iofun = null;
	
	public List<String> m_searchPaths = new ArrayList<String>();
	
	public InsteonTerminal() {}
	
	public PythonInterpreter 	getInterpreter() { return m_interpreter; }
	public Console 				getConsole() { return m_console; }
	public IOFun				getIOFun() { return m_iofun; }
	
	public Reader 		in() { return m_iofun.in(); }
	public PrintStream 	out() { return m_iofun.out(); }
	public PrintStream 	err() { return m_iofun.err(); }
	
	//Interpreter functions


	// Locations to search for init.py and any insteonplm-related modules
	public void addModuleSearchPath(String path) {
		m_searchPaths.add(path);
	}
	
	//TODO: Make throw just a python stack trace for python errors
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
		
		File init = new File("init.py");
		
		try {
			m_interpreter.exec("import sys");

			//Remove all existing modules so we can reload them
			m_interpreter.exec("sys.modules.clear()");

			for (String path : m_searchPaths) {
				logger.debug("Appending {} to python module path", path);
				m_interpreter.exec("sys.path.append('" + path + "')");				
			}

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
			out().println("Failed to initialize python interpreter: ");
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
			//Print out a list of all the functions
			out().println("----All available functions---");
			
			List<PyFunction> funcs = new ArrayList<PyFunction>();
			
			PyStringMap dict = (PyStringMap) m_interpreter.getLocals();
			for (Object o : dict.values()) {
				if (o instanceof PyFunction) {
					PyFunction f = (PyFunction) o;
					funcs.add(f);
				}
			}
			//Order them alphabetically
			Collections.sort(funcs, new Comparator<PyFunction>() {
				@Override
				public int compare(PyFunction f1, PyFunction f2) {
					return f1.__name__.compareTo(f2.__name__);
				}
			});
			
			for (PyFunction f : funcs) {
				String doc =  f.__doc__.toString().trim();
				if (doc.equals("None")) doc = "No doc";
				
				out().println(f.__name__ + "() - " + doc);
			}
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
