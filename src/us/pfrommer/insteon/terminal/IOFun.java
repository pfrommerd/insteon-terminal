package us.pfrommer.insteon.terminal;

import java.io.IOException;
import java.io.PrintStream;
import java.io.Reader;
import java.util.Collections;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import us.pfrommer.insteon.emulator.EmulatorStream;
import us.pfrommer.insteon.emulator.ModemEmulator;
import us.pfrommer.insteon.msg.IOPort;
import us.pfrommer.insteon.msg.Msg;
import us.pfrommer.insteon.msg.MsgListener;
import us.pfrommer.insteon.msg.PortListener;
import us.pfrommer.insteon.msg.hub.HubStream;
import us.pfrommer.insteon.msg.hub.LegacyHubStream;
import us.pfrommer.insteon.msg.serial.SerialIOStream;
import us.pfrommer.insteon.terminal.console.Console;

public class IOFun implements PortListener {
	private InsteonTerminal m_terminal = null;
	private Console m_console = null;
	
	private IOPort m_port = null;
	
	private Set<MsgListener> m_msgListeners = 
			Collections.newSetFromMap(new ConcurrentHashMap<MsgListener, Boolean>());

	private Set<PortListener> m_portListeners = 
			Collections.newSetFromMap(new ConcurrentHashMap<PortListener, Boolean>());

	public IOFun(InsteonTerminal terminal, Console console) {
		m_terminal = terminal;
		m_console = console;
	}
	
	public Reader in() { return m_console.in(); }
	public PrintStream out() { return m_console.out(); }
	public PrintStream err() { return m_console.err(); }

	public boolean isConnected() { return m_port != null; }

	
	// IO Functions

	public void reload() {
		out().println("Resetting terminal...");

		try {
			disconnect();
		} catch (Exception e) {
			err().println("Failed to close connection: " + e.getMessage());
		}
		
		//Clear the listeners to prevent python listeners from hanging around
		m_msgListeners.clear();
		m_portListeners.clear();

		try {
			m_terminal.init();
		} catch (Exception e) {
			err().println("Failed to reset terminal");
			e.printStackTrace(err());
		}

		out().println("Terminal reset!");
	}

	public void reset() throws IOException {
		m_console.reset();
		reload();
	}

	public void clear() {
		m_console.clear();
	}


	// Basic connectivity functions

	private void updatePort(IOPort newPort) throws IOException {
		if (m_port != null) disconnect();
		m_port = newPort;
		m_port.addListener(this);
		m_port.open();
	}
	
	public void connectToHub(String address, int port, int pollMillis, String user, String password) throws IOException {
		updatePort(new IOPort(new HubStream(address, port, pollMillis, user, password)));
	}

	public void connectToLegacyHub(String address, int port) throws IOException {
		updatePort(new IOPort(new LegacyHubStream(address, port)));
	}

	public void connectToSerial(String port) throws IOException {
		updatePort(new IOPort(new SerialIOStream(port)));
	}
	
	public ModemEmulator connectToEmulator() throws IOException {
		ModemEmulator m = new ModemEmulator();
		updatePort(new IOPort(new EmulatorStream(m)));
		return m;
	}

	public void disconnect() throws IOException {
		if (m_port != null) {
			m_port.removeListener(this);
			m_port.close();
			m_port = null;
		}
	}
	
	// IO Functions
	
	public void addMsgListener(MsgListener l) {
		m_msgListeners.add(l);
	}
	
	public void removeMsgListener(MsgListener l) {
		m_msgListeners.remove(l);
	}

	public void addPortListener(PortListener l) {
		m_portListeners.add(l);
	}
	
	public void removePortListener(PortListener l) {
		m_portListeners.remove(l);
	}

	public void writeMsg(Msg m) throws IOException {
		if (m_port == null) {
			throw new IOException("Not connected");
		}
		m_port.write(m);
	}
	
	// Port listening functions

	@Override
	public void msgWritten(Msg msg) {
		for (PortListener l : m_portListeners) {
			l.msgWritten(msg);
		}


	}

	@Override
	public void msgReceived(Msg msg) {
		for (PortListener l : m_portListeners) {
			l.msgReceived(msg);
		}

		for (MsgListener l : m_msgListeners) {
			l.msgReceived(msg);
		}
	}
}
