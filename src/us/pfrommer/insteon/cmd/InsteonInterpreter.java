package us.pfrommer.insteon.cmd;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintStream;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;

import org.python.core.PyFunction;
import org.python.core.PyStringMap;
import org.python.util.PythonInterpreter;

import us.pfrommer.insteon.cmd.msg.InsteonAddress;
import us.pfrommer.insteon.cmd.msg.Msg;
import us.pfrommer.insteon.cmd.msg.MsgListener;
import us.pfrommer.insteon.cmd.utils.Utils;

public class InsteonInterpreter implements PortListener {
	private HashMap<String, InsteonAddress>  m_deviceMap = new HashMap<String, InsteonAddress>();
	private HashMap<InsteonAddress, String> m_addressMap = new HashMap<InsteonAddress, String>();
	
	
	private PythonInterpreter m_interpreter;
	
	private IOPort m_port;
	private Msg m_lastMsg;
	
	private Console m_console;
	
	private HashSet<MsgListener> m_listeners = new HashSet<MsgListener>();
	
	public InsteonInterpreter(Console c) {
		m_console = c;
		init();
	}
	
	public void init() {
		m_interpreter = new PythonInterpreter();

		m_interpreter.setOut(out());
		m_interpreter.setIn(in());
		m_interpreter.setErr(err());
		
		out().println("Insteon Terminal");
		
		m_interpreter.set("insteon", this);
		
		try {
			//Load the built in commands
			loadCommands(InsteonInterpreter.class.getResourceAsStream("/defaultCommands.py"));
			//Load the startup commands
			File startup = new File("init.py");
			if (startup.exists()) {
				loadCommands(startup);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public PythonInterpreter getInterpreter() { return m_interpreter; }
	public Console getConsole() { return m_console; }
	
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
	
	public void setPort(IOPort p) {
		if (m_port != null) {
			m_port.removeListener(this);
			try {
				m_port.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
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
	
	//Device functions
	
	public void setDevice(String name, InsteonAddress adr) {
		m_deviceMap.put(name, adr);
		m_addressMap.put(adr, name);
	}
	public void removeDevice(String name) {
		InsteonAddress adr = m_deviceMap.get(name);
		m_deviceMap.remove(name);
		if (adr != null) m_addressMap.remove(name);
	}
	
	public String getDeviceName(InsteonAddress adr) {
		return m_addressMap.get(adr);
	}
	public InsteonAddress getDeviceAddress(String name) {
		return m_deviceMap.get(name);
	}
	//Interpreter functions
	
	public void exec(String s) {
		m_interpreter.exec(s);
	}
	
	private void dumpFuncs() {
		//Dump all the available functions
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
	}
	
	public void run() {
		try{
			while(true) {
				String line = m_console.readLine(">>> ");
				try {
					if (line.trim().equals("help")) {
						out().println("Use help()");
					} else if (line.trim().equals("exit")) {
						out().println("Use exit()");
					} else if (line.trim().equals("quit")) {
						out().println("Use quit()");
					} else if (line.trim().equals("clear")) {
						out().println("Use clear()");
					} else if (line.trim().equals("reset")) {
						out().println("Use reset()");
					} else if (line.equals("?")) {
						dumpFuncs();
					} else exec(line);
				} catch (Exception e) {
					e.printStackTrace();
				}

			}
		} catch(IOException io){
			io.printStackTrace();
		}
	}
	public void loadCommands(InputStream in) throws IOException {
		String s = Utils.read(in);
		exec(s);
	}
	public void loadCommands(String s) throws IOException {
		loadCommands(new File(s));
	}
	public void loadCommands(File file) throws IOException {
		String s = Utils.readFile(file);
		exec(s);
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
	
	public void writeHex(String hex) {
		hex = hex.replaceAll("\\s+", "");
		//Convert the string to a byte array
	    int len = hex.length();
	    byte[] data = new byte[len / 2];
	    for (int i = 0; i < len; i += 2) {
	        data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
	                             + Character.digit(hex.charAt(i+1), 16));
	    }
	    
	    //write data
	    write(data);
	}
	
	public void write(byte[] bytes) {
		if (m_port == null) {
			err().println("Not connected");
			return;
		}
		m_port.write(bytes);
	}
	
	public void writeMsg(Msg m) {
		if (m_port == null) {
			err().println("Not connected");
			return;
		}
		m_port.write(m);
	}
	
	//Port listener functions
	@Override
	public void bytesReceived(byte[] bytes) {}
	
	@Override
	public void msgReceived(Msg msg) {
		synchronized(m_listeners) {
			for (MsgListener l : m_listeners) l.msgReceived(msg); 
		}
		
		//Notify current blocking readMsg();
		synchronized(this) {
			notifyAll();
			m_lastMsg = msg;
		}
	}
}
