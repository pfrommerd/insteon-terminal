package us.pfrommer.insteon.cmd;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.math.BigInteger;
import java.util.Collection;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map.Entry;
import java.util.regex.Pattern;

import us.pfrommer.insteon.cmd.Command.HelpCommand;
import us.pfrommer.insteon.cmd.Command.ListCommands;
import us.pfrommer.insteon.cmd.Command.LoadCommand;
import us.pfrommer.insteon.cmd.hub.HubConnectCommand;
import us.pfrommer.insteon.cmd.serial.SerialConnectCommand;

public class InsteonInterpreter implements Runnable, PortListener {
	private IOPort m_port;
	private Console m_console;
	
	private HashMap<String, String> m_variables = new HashMap<String, String>();
	private HashMap<String, Command> m_commands = new LinkedHashMap<String, Command>();
	
	public InsteonInterpreter(Console c) {
		m_console = c;
		
		//Add default commands
		addCommand(new ListCommands());
		addCommand(new HelpCommand());
		addCommand(new LoadCommand());
		addCommand(new HubConnectCommand());
		addCommand(new SerialConnectCommand());
		try {
			InputStream in = InsteonInterpreter.class.getResourceAsStream("/commands.cmds");
			addCommands(CommandsLoader.s_loadCommands(in));
		} catch (Exception e) { e.printStackTrace(); }
		
		out().println("Insteon Command Shell initialized...waiting for commands");
	}
	
	public Collection<Command> getCommands() { return m_commands.values(); }
	public Command getCommand(String cmd) { return m_commands.get(cmd); }
	
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
		
	public InputStream in() { return m_console.in(); }
	public PrintStream out() { return m_console.out(); }
	public PrintStream err() { return m_console.out(); }
	
	public void addCommand(Command cmd) {
		m_commands.put(cmd.getCmd(), cmd);
	}
	public void addCommands(Collection<? extends Command> cmds) {
		for (Command c : cmds) {
			addCommand(c);
		}
	}
	
	public void setVariable(String var, String val) {
		m_variables.put(var, val);
	}
	
	@Override
	public void bytesReceived(byte[] bytes) {
		out().println("IN: " + s_bytesToHex(bytes, 0, bytes.length));
	}
	
	public void write(byte[] msg) {
		if (msg.length > 0) {
			if (m_port != null) {
				out().println("OUT: " + s_bytesToHex(msg, 0, msg.length));
				m_port.write(msg);
			} else out().println("Cannot send bytes because no port set");
		}
	}
	
	public void exec(String line) {
		//If there are no equals signs, substitute variables
		if (line.indexOf('=') < 0) {
			//Substitute variables
			for (Entry<String, String> var : m_variables.entrySet()) {
				line = line.replaceAll(Pattern.quote(var.getKey()), var.getValue());
			}
		}
		
		String[] parts = line.split("\\s+");
		String[] args = new String[parts.length - 1]; 
		System.arraycopy(parts, 1, args, 0, args.length);
		
		String cmd = parts[0];
		if (m_commands.containsKey(cmd)) {
			m_commands.get(cmd).exec(this, args);
		} else if (line.contains("=")) {
			String varName = line.substring(0, line.indexOf('=')).trim();
			if (varName.indexOf(' ') >= 0) {
				err().println("Cannot have space in variable name " + varName);;
				return;
			}
			String val = "";
			if (line.length() > line.indexOf('='))
				val = line.substring(line.indexOf('=') + 1).trim();
			setVariable(varName, val);
			out().println("Setting " + varName + " to " + val);
		} else if (!line.equals("")) {
			write(hexStringToByteArray(line.replaceAll("\\s+", "")));
		}
	}
	
	public void run() {
		try{
			BufferedReader br = new BufferedReader(new InputStreamReader(in()));
	 
			String line;
			while((line = br.readLine()) != null) {
				try {
					exec(line);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		} catch(IOException io){
			io.printStackTrace();
		}
	}
	
	public byte[] hexStringToByteArray(String s) {
		try {
			if (s.equals("")) return new byte[0];
			return new BigInteger(s, 16).toByteArray();
		} catch (NumberFormatException e) {
			err().println("Must be hex input!");
			return new byte[0];
		}
	}
	
	public static String s_bytesToHex(byte[] bytes, int off, int len) {
		StringBuilder b = new StringBuilder();
		for (int i = off; i < len; i++) {
			if (i != 0) b.append(' ');
			b.append(String.format("%02x", bytes[i]));
		}
		return b.toString();
	}
	public static byte[] s_parseInsteonAdr(String adr) {
		byte[] b = new byte[3];
		if (adr.contains(".")) {
			String[] prts = adr.split("\\.");
			b[0] = (byte) Integer.parseInt(prts[0], 16);
			b[1] = (byte) Integer.parseInt(prts[1], 16);
			b[2] = (byte) Integer.parseInt(prts[2], 16);
		} else {
			b[0] = (byte) Integer.parseInt(adr.substring(0, 2), 16);
			b[1] = (byte) Integer.parseInt(adr.substring(2, 4), 16);
			b[2] = (byte) Integer.parseInt(adr.substring(4, 6), 16);
		}
		return b;
	}
}
