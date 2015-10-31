package us.pfrommer.insteon.cmd.gui;

import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.io.IOException;
import java.io.PipedReader;
import java.io.PipedWriter;
import java.io.Reader;
import java.util.Scanner;
import java.util.concurrent.CopyOnWriteArrayList;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.InputMap;
import javax.swing.JTextField;
import javax.swing.KeyStroke;

import us.pfrommer.insteon.cmd.History;

public class InputArea extends JTextField {
	private InputAreaReader m_reader = null;
	private Scanner m_scanner = null;
	
	private History m_history = null;
	
	private String m_currentCache = null;
	
	private int m_selectionIdx = -1;
	
	//If prompting, non-null
	private String m_prompt = null;
	
	private CopyOnWriteArrayList<InputListener> m_listeners = new CopyOnWriteArrayList<InputListener>();
	
	public interface InputListener {
		public void onInput(String input, String text);
	}
	
	public InputArea(Font f, History h) {
		setFont(f);
		m_history = h;
		m_reader = new InputAreaReader();
		
		addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				submit();
			}
		}); 
		
		Action submit = new AbstractAction() {
			private static final long serialVersionUID = 1L;

			@Override
			public void actionPerformed(ActionEvent e) {
				submit();
			}
		};

		Action up = new AbstractAction() {
			private static final long serialVersionUID = 1L;

			@Override
			public void actionPerformed(ActionEvent e) {
				up();
			}
		};
		
		Action down = new AbstractAction() {
			private static final long serialVersionUID = 1L;

			@Override
			public void actionPerformed(ActionEvent e) {
				down();
			}
		};
		
		KeyStroke submitStroke = KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, 0);
		KeyStroke upStroke = KeyStroke.getKeyStroke(KeyEvent.VK_UP, 0);
		KeyStroke downStroke = KeyStroke.getKeyStroke(KeyEvent.VK_DOWN, 0);
		
		InputMap im = getInputMap();
		im.put(submitStroke, submit);
		im.put(upStroke, up);
		im.put(downStroke, down);
		
		
		m_scanner = new Scanner(m_reader);
	}

	
	public String getCurrentInputLine() {
		String text = getText();

		if (m_prompt != null && text.startsWith(m_prompt)) {
			text = text.substring(m_prompt.length());
		}
		return text;
	}
	
	
	public void addInputListener(InputListener l) {
		m_listeners.add(l);
	}

	public Reader getInput() {
		return m_reader;
	}
	
	
	public String readLine() {
		String s = m_scanner.nextLine();
		return s;
	}
	
	public String readLine(String prompt) {
		//Don't show the prompt
		m_prompt = prompt;
		setText(prompt + getText());
		
		setCaretPosition(getText().length());
		
		return readLine();
	}

	public void clear() {
		setText("");
	}
	
	public void up() {	
		int idx = Math.min(m_selectionIdx + 1, m_history.length() - 1);

		
		if (idx == -1) { //We can't go up
			return;
		}

		
		if (m_selectionIdx == -1) {
			m_currentCache = getCurrentInputLine();
		}

		m_selectionIdx = idx;
		
		
		
		String sel = m_history.get(idx);
		
		if (m_prompt != null) {
			sel = m_prompt + sel;
		}
		
		setText(sel);
		
		setCaretPosition(sel.length());
	}
	
	public void down() {
		int idx = Math.max(m_selectionIdx - 1, -1);
		
		if (idx == -1) { // We can't go down
			return;
		}
		
		m_selectionIdx = idx;
		
		String sel = null;
		
		if (m_selectionIdx == 0) {
			sel = m_currentCache;
			m_currentCache = null;
		} else {
			sel = m_history.get(idx);
		}
		
		if (m_prompt != null) {
			sel = m_prompt + sel;
		}
		
		setText(sel);
		
		setCaretPosition(sel.length());
	}

	public void submit() {
		String text = getText();
		
		if (text.length() == 0) return;
		
		String input = text;

		if (m_prompt != null && text.startsWith(m_prompt)) {
			input = text.substring(m_prompt.length());
			m_prompt = null;
		}
		
		for (InputListener l : m_listeners) {
			l.onInput(input, text);
		}
		
		try {
			m_reader.process(input);
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		clear();
	}
	
	private class InputAreaReader extends Reader {
		private PipedWriter m_writer = new PipedWriter();
		private PipedReader m_reader;
		private boolean m_open = false;
		
		public InputAreaReader() {
			try {
				m_reader = new PipedReader(m_writer);
				m_open = true;
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		
		public void process(String text) throws IOException {
			if (m_open)	{
				m_writer.write(text);
				m_writer.write('\n');
			}
			
		}
		
		@Override
		public int read(char[] cbuf, int off, int len) throws IOException {
			return m_reader.read(cbuf, off, len);
		}


		@Override
		public void close() throws IOException {
			m_open = false;
			m_writer.close();
			m_reader.close();			
		}
	}
}
