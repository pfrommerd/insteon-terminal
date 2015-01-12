package us.pfrommer.insteon.cmd;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

public interface Command {
	public String getCmd();
	public String getDesc();
	public String getUsage();
	
	public void exec(InsteonInterpreter interpreter, String... args);
	
	public static class HelpCommand implements Command {
		@Override
		public String getCmd() {
			return "help";
		}

		@Override
		public String getDesc() {
			return "gets the usage and description info about a command";
		}

		@Override
		public String getUsage() {
			return "help <commandName>";
		}

		@Override
		public void exec(InsteonInterpreter interpreter, String... args) {
			if (args.length < 1) {
				interpreter.out().println("Usage: " + getUsage());
				return;
			}
			String cmd = args[0];
			Command command = interpreter.getCommand(cmd);
			if (command == null) interpreter.out().println("Could not find command: "  + cmd);
			interpreter.out().println("Description: " + (command.getDesc().equals("") ? "No description" : command.getDesc()));
			interpreter.out().println("Usage: " + command.getUsage());
		}
	}
	public static class ListCommands implements Command {
		@Override
		public String getCmd() {
			return "?";
		}

		@Override
		public String getDesc() {
			return "lists all available commands";
		}

		@Override
		public String getUsage() {
			return "?";
		}

		@Override
		public void exec(InsteonInterpreter interpreter, String... args) {
			for (Command c : interpreter.getCommands()) {
				interpreter.out().println(c.getCmd() + " - " + c.getDesc());
			}
		}
	}
	public static class LoadCommand implements Command {
		@Override
		public String getCmd() {
			return "load_cmds";
		}
		@Override
		public String getDesc() {
			return "loads commands from a file";
		}
		@Override
		public String getUsage() {
			return getCmd() + " <absolute_path_to_commands_file>";
		}

		@Override
		public void exec(InsteonInterpreter interpreter, String... args) {
			if (args.length < 1) {
				interpreter.err().println("Usage:"  + getUsage());
				return;
			}
			try {
				String filePath = args[0];
				filePath = filePath.replaceAll("\\~", System.getProperty("user.home"));
				InputStream in = new FileInputStream(new File(filePath));
				interpreter.addCommands(CommandsLoader.s_loadCommands(in));
			} catch (Exception e) { e.printStackTrace(); }
		}
	}
	public static class MacroCommand implements Command {
		private String m_name;
		private String m_desc;
		private String m_usage;
		private List<String> m_lines = new ArrayList<String>();
		
		public MacroCommand(String name, String desc, String usage) {
			m_name = name;
			m_desc = desc;
			m_usage = usage;
		}

		public void addLine(String line) { m_lines.add(line); }
		
		@Override
		public String getCmd() {
			return m_name;
		}
		@Override
		public String getDesc() {
			return m_desc;
		}
		@Override
		public String getUsage() {
			return m_usage;
		}

		@Override
		public void exec(InsteonInterpreter console, String... args) {
			for (String ex : m_lines) {
				for (int i = 0; i < args.length; i++) {
					if (!ex.contains("$" + i))
						throw new IllegalArgumentException("Too many params");
					ex = ex.replaceAll("\\$" + i, args[i]);
				}
				if (ex.contains("$")) {
					console.err().println("Tew few params, usage: " + getUsage());
					return;
				}
				console.exec(ex);
			}
		}
	}
}
