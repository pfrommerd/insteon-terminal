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
import javax.swing.text.AttributeSet;
import javax.swing.text.BadLocationException;
import javax.swing.text.Document;
import javax.swing.text.DocumentFilter;
import javax.swing.text.PlainDocument;
import javax.swing.text.SimpleAttributeSet;

import us.pfrommer.insteon.cmd.History;

public class InputArea extends JTextField {
	private static final long serialVersionUID = 1L;
	
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
		
		//Setup the filter so we can't remove the prompt
		PlainDocument doc = (PlainDocument) getDocument();
		doc.setDocumentFilter(new PromptFilter());
		
		
		m_scanner = new Scanner(m_reader);
	}

	
	public String getCurrentInputLine() {
		String text = getText();

		if (m_prompt != null && text.startsWith(m_prompt)) {
			text = text.substring(m_prompt.length());
		}
		return text;
	}
	
	public void setCurrentInputLine(String input) {
		if (m_prompt != null) {
			Document d = getDocument();
			try {
				d.remove(m_prompt.length(), getCurrentInputLine().length());
				d.insertString(m_prompt.length(), input, new SimpleAttributeSet());
			} catch (BadLocationException e) {
				e.printStackTrace();
			}			
		} else setText(input); 

		setCaretPosition(getText().length());
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
		setText(prompt + getText());
		m_prompt = prompt;
		
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
		setCurrentInputLine(sel);
	}
	
	public void down() {
		if (m_selectionIdx == -1) { // We can't go down
			return;
		}


		int idx = Math.max(m_selectionIdx - 1, -1);
		
		m_selectionIdx = idx;
		
		String sel = null;
		
		if (m_selectionIdx == -1) {
			sel = m_currentCache;
			m_currentCache = null;
		} else {
			sel = m_history.get(idx);
		}
		
		setCurrentInputLine(sel);
	}

	public void submit() {
		m_selectionIdx = -1; //If we were previewing, doesn't matter anymore
		
		String text = getText();
		
		if (text.length() == 0) return;
		
		String input = text;

		if (m_prompt != null && text.startsWith(m_prompt)) {
			input = text.substring(m_prompt.length());
			m_prompt = null;
		} else if (m_prompt != null) {
			text = m_prompt + text;
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
	
	//Prevents us from modifying the caret...
	private class PromptFilter extends DocumentFilter {
		   @Override
		   public void insertString(FilterBypass fb, int offset, String string,
		         AttributeSet attr) throws BadLocationException {

			   if (m_prompt != null && offset < m_prompt.length()) {
				   //Do nothing...
			   } else super.insertString(fb, offset, string, attr);
		   }

		   @Override
		   public void replace(FilterBypass fb, int offset, int length, String text,
		         AttributeSet attrs) throws BadLocationException {

			   if (m_prompt != null && offset < m_prompt.length()) {
				   //Do nothing...
			   } else super.replace(fb, offset, length, text, attrs);
		   }

		   @Override
		   public void remove(FilterBypass fb, int offset, int length)
		         throws BadLocationException {
			   if (m_prompt != null && offset < m_prompt.length()) {
				   //Do nothing...
			   } else super.remove(fb, offset, length);
		   }
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
