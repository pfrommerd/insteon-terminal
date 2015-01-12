package us.pfrommer.insteon.cmd;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import us.pfrommer.insteon.cmd.Command.MacroCommand;

public class CommandsLoader {
	public static List<Command> s_loadCommands(InputStream in) throws IOException {
		ArrayList<Command> cmds = new ArrayList<Command>();
	
		MacroCommand currentCmd = null;

		BufferedReader reader = new BufferedReader(new InputStreamReader(in));
		String line;
        while ((line = reader.readLine()) != null) {
        	line = line.trim();
        	if (line.contains("#")) {
        		line = line.substring(0, line.indexOf('#'));
        	}
        	if (line.contains(":")) {
        		if (currentCmd != null) cmds.add(currentCmd);
        		int firstColon = line.indexOf(':');
        		
        		int secondColon = line.substring(firstColon + 1).indexOf(':') + firstColon + 1;
        		
        		if (secondColon < 0) System.err.println("Error parsing line: " + line + " must be two colons");
        		String name = line.substring(0, firstColon);
        		String dest = line.substring(Math.min(firstColon + 1, line.length() - 1), secondColon);
        		String usage = line.substring(Math.min(secondColon + 1, line.length() - 1), line.length());
        		
        		currentCmd = new MacroCommand(name, dest, usage);
        	} else if (currentCmd != null) {
        		if (!line.equals("")) currentCmd.addLine(line);
        	} else {
        		if (!line.equals("")) throw new RuntimeException("Unexpected: " + line);
        	}
        }
		if (currentCmd != null) cmds.add(currentCmd);
		
        reader.close();
		
		return cmds;
	}
}
