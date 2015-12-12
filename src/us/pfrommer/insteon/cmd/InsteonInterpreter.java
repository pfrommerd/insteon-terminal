package us.pfrommer.insteon.cmd;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.io.Reader;
import java.util.HashSet;

import org.python.core.Py;
import org.python.util.PythonInterpreter;

import us.pfrommer.insteon.cmd.hub.HubStream;
import us.pfrommer.insteon.cmd.hub.LegacyHubStream;
import us.pfrommer.insteon.cmd.msg.IOPort;
import us.pfrommer.insteon.cmd.msg.Msg;
import us.pfrommer.insteon.cmd.msg.MsgListener;
import us.pfrommer.insteon.cmd.msg.PortListener;
import us.pfrommer.insteon.cmd.serial.SerialIOStream;

public class InsteonInterpreter implements PortListener, ConsoleListener {
	private PythonInterpreter m_interpreter;
	
	private IOPort m_port;
	private Msg m_lastMsg;
	
	private Console m_console;
	
	private HashSet<MsgListener> m_listeners = new HashSet<MsgListener>();

	public InsteonInterpreter(Console c) {
		m_console = c;
		m_console.addConsoleListener(this);
	}
	
	public PythonInterpreter getInterpreter() { return m_interpreter; }
	public Console getConsole() { return m_console; }
	public IOPort getPort() { return m_port; }
	
	public Reader in() { return m_console.in(); }
	public PrintStream out() { return m_console.out(); }
	public PrintStream err() { return m_console.err(); }
	
	public boolean isConnected() { return m_port != null; }
	
	public void addListener(MsgListener l) {
		synchronized(m_listeners) {
			m_listeners.add(l);
		}
	}
	public void removeListener(MsgListener l) {
		synchronized(m_listeners) {
			m_listeners.remove(l);
		}	
	}
	

	//All the shorthand read-write methods
	
	/**
	 * Will block, waiting for the next Msg
	 */
	public Msg readMsg() {
		if (m_port == null) {
			err().println("Not connected");
			return null;
		}
		synchronized(this) {
			try {
				wait();
			} catch (InterruptedException e) {}
			return m_lastMsg;
		}
	}
	
	public void writeMsg(Msg m) throws IOException {
		if (m_port == null) {
			err().println("Not connected");
			return;
		}
		m_port.write(m);
	}
	
	//
	
	public void reload() throws IOException {
		out().println("Resetting interpreter...");
		closePort();
		//Setup a new interpreter for us to use
		init();

		out().println("Interpreter reset!");
	}

	public void reset() throws IOException {
		m_console.reset();
		reload();
	}
	
	public void clear() {
		m_console.clear();
	}
	
	
	// Basic connectivity functions
	
	public void connectToHub(String address, int port, int pollMillis, String user, String password) {
		if (m_port != null) closePort();
		setPort(new IOPort(new HubStream(address, port, pollMillis, user, password)));
	}

	public void connectToLegacyHub(String address, int port) {
		if (m_port != null) closePort();
		setPort(new IOPort(new LegacyHubStream(address, port)));
	}

	public void connectToSerial(String port) {
		if (m_port != null) closePort();
		setPort(new IOPort(new SerialIOStream(port)));
	}
	
	public void disconnect() {
		closePort();
	}
	
	// Internal connectivity functions
	
	private void setPort(IOPort p) {
		closePort();
		m_port = p;
		if (m_port != null) {
			try {
				m_port.open();
			} catch (IOException e) {
				e.printStackTrace();
			}
			m_port.addListener(this);
		}
	}
	
	private void closePort() {
		if (m_port != null) {
			m_port.removeListener(this);
			try {
				m_port.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
			m_port = null;
		}
	}

	
	//Interpreter functions
	
	public void init() {
		if (m_interpreter == null) m_interpreter = new PythonInterpreter();

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
			m_interpreter.get("iofun").__getattr__("_init_io_fun").__call__(Py.java2py(this));

			m_interpreter.exec("import console_commands");			

			m_interpreter.exec("from console_commands import *");		

			
			if (init.exists()) {
				//Import init
				m_interpreter.exec("from init import *");
			}

		} catch (Exception e) {
			e.printStackTrace();
		}
	}


	public void exec(String s) {
		try {
			m_interpreter.exec(s);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	public void run() {
		try{
			out().println("Insteon Terminal");

			init();
			out().println("Python interpreter initialized...");

			
			while(true) {
				String line = m_console.readLine(">>> ");
				if (line.isEmpty()) continue;
				line = line.trim();
				try {
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
						out().println("STUB: This functionality has been temporarily removed");
					} else exec(line);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		} catch(IOException io){
			io.printStackTrace();
		}
	}
	

	
	//Terminate the current running program
	@Override
	public void terminate() {
		out().println("terminate() called: no way to terminate a running python program");
	}
	
	//Port listener functions
	@Override
	public void msgReceived(Msg msg) {
		HashSet<MsgListener> copyOfList;
		synchronized(m_listeners) {
			copyOfList = new HashSet<MsgListener>(m_listeners);
			// iterate through copy of list, since msgReceived() may actually modify the list!
		}
		for (MsgListener l : copyOfList) l.msgReceived(msg); 
		
		//Notify current blocking readMsg();
		synchronized(this) {
			notifyAll();
			m_lastMsg = msg;
		}
	}

	@Override
	public void msgWritten(Msg msg) {}
}
