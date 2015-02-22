package us.pfrommer.insteon.cmd.terminal;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.io.Reader;

import jline.ConsoleReader;
import jline.Terminal;
import us.pfrommer.insteon.cmd.Console;
import us.pfrommer.insteon.cmd.ConsoleListener;
import us.pfrommer.insteon.cmd.InsteonInterpreter;

public class JLineTerminal extends Reader implements Console {
	private ConsoleReader m_reader;
	
	private String m_currentStr;
	private int m_strIdx = 0;
	
	public JLineTerminal() {
		Terminal.setupTerminal();
		try {
			m_reader = new ConsoleReader();
		} catch (IOException e) {
			e.printStackTrace();
		}
		try {
			File historyFile = new File(System.getProperty("user.home"),
					".insteon-terminal/history.txt");
			
			if (!historyFile.exists()) {
				historyFile.getParentFile().mkdirs();
				historyFile.createNewFile();
			}
			
			m_reader.getHistory().setHistoryFile(historyFile);
		} catch(IOException e) {
			e.printStackTrace();
		}
	}
	
	@Override
	public Reader in() {
		return this;
	}

	@Override
	public PrintStream out() {
		return System.out;
	}

	@Override
	public PrintStream err() {
		return System.err;
	}

	@Override
	public String readLine() throws IOException {
		return m_reader.readLine();
	}
	
	@Override
	public String readLine(String prompt) throws IOException {
		return m_reader.readLine(prompt);
	}
	
	@Override
	public void clear() {
		
	}

	@Override
	public void reset() {
		
	}
	
	@Override
	public void addConsoleListener(ConsoleListener l) {
		
	}
	
	@Override
	public void removeConsoleListener(ConsoleListener l) {
		
	}

	@Override
	public int read(char[] cbuf, int off, int len) throws IOException {
		if (m_currentStr == null) {
			m_currentStr = m_reader.readLine();
		}
		for (int i = 0; i < len; i++) {
			if (m_currentStr.length() == m_strIdx) {
				m_strIdx++;
				cbuf[i + off] = '\n';
			} else if (m_strIdx > m_currentStr.length()){
				m_currentStr = null;
				return i;
			} else {
				cbuf[i + off] = m_currentStr.charAt(m_strIdx);
			}
		}
		return len;
	}

	@Override
	public void close() throws IOException {
		
	}
	
	public static void main(String[] args) {
		JLineTerminal t = new JLineTerminal();
		InsteonInterpreter i = new InsteonInterpreter(t);
		i.run();
	}
}
