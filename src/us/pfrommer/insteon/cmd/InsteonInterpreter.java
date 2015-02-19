package us.pfrommer.insteon.cmd;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.util.HashMap;
import java.util.HashSet;

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

		out().println("Insteon Terminal");
		
		m_interpreter = new PythonInterpreter();
		
		m_interpreter.setOut(out());
		m_interpreter.setIn(in());
		m_interpreter.setErr(err());
		
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
	
	public InputStream in() { return m_console.in(); }
	public PrintStream out() { return m_console.out(); }
	public PrintStream err() { return m_console.err(); }
	
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
		try {
			m_port.open();
		} catch (IOException e) {
			e.printStackTrace();
		}
		m_port.addListener(this);
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
	
	public void run() {
		try{
			BufferedReader br = new BufferedReader(new InputStreamReader(in()));
			
			out().print(">> ");
			
			String line;
			while((line = br.readLine()) != null) {
				try {
					exec(line);
				} catch (Exception e) {
					e.printStackTrace();
				}
				out().print(">> ");
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
