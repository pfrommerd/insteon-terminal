/*****************************************************************************
 *                                                                           *
 *  This file is part of the BeanShell Java Scripting distribution.          *
 *  Documentation and updates may be found at http://www.beanshell.org/      *
 *                                                                           *
 *  Sun Public License Notice:                                               *
 *                                                                           *
 *  The contents of this file are subject to the Sun Public License Version  *
 *  1.0 (the "License"); you may not use this file except in compliance with *
 *  the License. A copy of the License is available at http://www.sun.com    * 
 *                                                                           *
 *  The Original Code is BeanShell. The Initial Developer of the Original    *
 *  Code is Pat Niemeyer. Portions created by Pat Niemeyer are Copyright     *
 *  (C) 2000.  All Rights Reserved.                                          *
 *                                                                           *
 *  GNU Public License Notice:                                               *
 *                                                                           *
 *  Alternatively, the contents of this file may be used under the terms of  *
 *  the GNU Lesser General Public License (the "LGPL"), in which case the    *
 *  provisions of LGPL are applicable instead of those above. If you wish to *
 *  allow use of your version of this file only under the  terms of the LGPL *
 *  and not to allow others to use your version of this file under the SPL,  *
 *  indicate your decision by deleting the provisions above and replace      *
 *  them with the notice and other provisions required by the LGPL.  If you  *
 *  do not delete the provisions above, a recipient may use your version of  *
 *  this file under either the SPL or the LGPL.                              *
 *                                                                           *
 *  Patrick Niemeyer (pat@pat.net)                                           *
 *  Author of Learning Java, O'Reilly & Associates                           *
 *  http://www.pat.net/~pat/                                                 *
 *                                                                           *
 *****************************************************************************/

package	us.pfrommer.insteon.cmd.gui;

import java.awt.Color;
import java.awt.Font;
import java.awt.HeadlessException;
import java.awt.Toolkit;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.UnsupportedFlavorException;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PipedReader;
import java.io.PipedWriter;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Scanner;

import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import javax.swing.JTextPane;
import javax.swing.text.AttributeSet;
import javax.swing.text.BadLocationException;
import javax.swing.text.SimpleAttributeSet;
import javax.swing.text.StyleConstants;
import javax.swing.text.StyledDocument;

import us.pfrommer.insteon.cmd.Console;

public class JConsole extends JTextPane implements Console, KeyListener {
	
	
	private static final long serialVersionUID = 1L;
	
	//A list sorted from most recent to least recent command
	private ArrayList<String> m_history = new ArrayList<String>();
	
	private int m_historyIndex = -1;
	
	private ConsoleStream m_in;
	
	private ConsolePrintStream m_out;
	private ConsolePrintStream m_err;

	private HashSet<JConsoleListener> m_listeners = new HashSet<JConsoleListener>();
	
	private Scanner m_scanner;
	
	private Font m_font;
	
	private Color m_foreground = Color.BLACK;
	private Color m_background = Color.WHITE;
	private Color m_errColor = Color.RED;
	
	private JPopupMenu m_menu = new JPopupMenu();
	
	public JConsole(Font f, Color foreground, Color background, Color err) {
		m_foreground = foreground;
		m_background = background;
		m_errColor = err;
		
		m_in = new ConsoleStream();
		
		//Default attribute set
		m_out = new ConsolePrintStream(null);
		
		SimpleAttributeSet errAttr = new SimpleAttributeSet();
		StyleConstants.setForeground(errAttr, m_errColor);
		
		m_err = new ConsolePrintStream(errAttr);
		
		m_font = f;
		m_scanner = new Scanner(in());
		
		addKeyListener(this);
		
		setFocusable(true);
		requestFocus();
		
		setBackground(m_background);
		setForeground(m_foreground);
		
		m_menu.add(new JMenuItem("Cut")).addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JConsole.this.cut();
			}
		});
		m_menu.add(new JMenuItem("Copy")).addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JConsole.this.copy();
			}
		});
		m_menu.add(new JMenuItem("Paste")).addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				JConsole.this.paste();
			}
		});
		
		addMouseListener(new MouseListener(){
			@Override
			public void mouseClicked(MouseEvent e) {
				if (e.getButton() == MouseEvent.BUTTON3) m_menu.show(JConsole.this, e.getX(), e.getY());
			}
			@Override
			public void mousePressed(MouseEvent e) {}
			@Override
			public void mouseReleased(MouseEvent e) {}
			@Override
			public void mouseEntered(MouseEvent e) {}
			@Override
			public void mouseExited(MouseEvent e) {}
		});
		
		setFont(m_font);
	}
	
	public void addListener(JConsoleListener l) {
		synchronized(m_listeners) {
			m_listeners.add(l);
		}
	}
	
	public void removeListener(JConsoleListener l) {
		synchronized(m_listeners) {
			m_listeners.remove(l);
		}
	}
	
	
	public String getHistory(int ago) {
		if (ago > -1 && ago < m_history.size()) return m_history.get(ago);
		else if (ago >= m_history.size()) return "";
		else return m_in.getLine();
	}
	
	
	public void append(String s, AttributeSet attr) {
		if (m_in.getLine().length() > 0) {
			m_in.removeLine();
		}
		
		StyledDocument doc = getStyledDocument();
		try {
			doc.insertString(doc.getLength(), s, attr);
		} catch (BadLocationException e) {
			e.printStackTrace();
		}
		
		if (m_in.getLine().length() > 0) {
			try {
				doc.insertString(doc.getLength(), m_in.getLine(), attr);
			} catch (BadLocationException e) {
				e.printStackTrace();
			}
		}
		
		m_in.updateCaret();
	}
	
	
	@Override
	public void keyTyped(KeyEvent e) {
		//Check to make sure the character is valid before typing it
		if ((e.getKeyChar() < 32 || e.getKeyChar() > 126) && e.getKeyChar() != '\n') return;
		//Type it!
		m_in.characterTyped(e.getKeyChar());
		
		e.consume();
	}

	@Override
	public void keyPressed(KeyEvent e) {
		switch(e.getKeyCode()) {
		case KeyEvent.VK_BACK_SPACE: m_in.backspace(); break;
		case KeyEvent.VK_DELETE: m_in.delete(); break;
		case KeyEvent.VK_LEFT : m_in.left(); break;
		case KeyEvent.VK_RIGHT : m_in.right(); break;
		case KeyEvent.VK_UP : m_in.up(); break;
		case KeyEvent.VK_DOWN : m_in.down(); break;
		default: break;
		}
		
		e.consume();
	}

	@Override
	public void keyReleased(KeyEvent e) {
		e.consume();
	}

	@Override
	public Reader in() {
		return m_in;
	}

	@Override
	public PrintStream out() {
		return m_out;
	}

	@Override
	public PrintStream err() {
		return m_err;
	}
	
	@Override
	public String readLine() {
		String res = m_scanner.nextLine();
		if (res.trim().length() != 0) m_history.add(0, res);
		return res;
	}
	
	@Override
	public String readLine(String prompt) {
		out().print(prompt);
		String res = m_scanner.nextLine();
		if (res.trim().length() != 0) m_history.add(0, res);
		return res; 
	}
	
	@Override
	public void clear() {
		setText("");
	}

	@Override
	public void reset() {
		clear();
		//Will clear the screen
		//and wipe the history
		m_history.clear();
	}
	
	@Override
	public void cut() {
		super.cut();
	}
	
	@Override
	public void paste() {
		setCaretPosition(getStyledDocument().getLength());
		super.paste();
		//Add the pasted text to the end of the current line of input
		try {
			String text = (String) Toolkit.getDefaultToolkit()
			        		.getSystemClipboard().getData(DataFlavor.stringFlavor);
			m_in.getCurrent().append(text);
		} catch (HeadlessException e) {
			e.printStackTrace();
		} catch (UnsupportedFlavorException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	@Override
    public boolean getScrollableTracksViewportWidth() {
        return getUI().getPreferredSize(this).getWidth() 
            <= getParent().getSize().getWidth();
    }

	public class ConsoleStream extends Reader {
		PipedWriter m_writer = new PipedWriter();
		PipedReader m_reader;
		
		StringBuilder m_currentLine = new StringBuilder();
		String m_preview;
		
		//Cursor index in the last line
		private int m_cursorIndex = 0;
		
		public ConsoleStream() {
			try {
				m_reader = new PipedReader(m_writer);
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		public StringBuilder getCurrent() { return m_currentLine; }
		
		public int getCmdStart() {
			int len = m_preview == null ? m_currentLine.length() : m_preview.length();
			return getStyledDocument().getLength() - len;
		}
		
		//Removes the current command(for, say, viewing history)
		public void removeLine() {
			int len = m_preview == null ? m_currentLine.length() : m_preview.length();
			try {
				getStyledDocument().remove(getCmdStart(), len);
			} catch (BadLocationException e) {
				e.printStackTrace();
			}
		}
		
		public void left() {
			if (m_cursorIndex > 0) m_cursorIndex--;
			
			setCaretPosition(getCmdStart() + m_cursorIndex);
		}
		
		public void right() {
			if (m_cursorIndex < getTextBuff().length()) m_cursorIndex++;

			if (getCaretPosition() < getCmdStart()) setCaretPosition(getCmdStart() + m_cursorIndex);
			if (getCaretPosition() < getStyledDocument().getLength()) setCaretPosition(getCaretPosition() + 1);
		}
		
		public void up() {
			if (m_historyIndex < m_history.size() && m_history.size() > 0)
					previewLine(getHistory(++m_historyIndex));			
		}

		public void down() {
			if (m_historyIndex > -1)
					previewLine(getHistory(--m_historyIndex));
		}
		
		public void backspace() {
			//If we are previewing a line in our history
			//set that line to the current line
			setToPreview();

			if (m_currentLine.length() != 0 && m_cursorIndex > 0) {
				m_currentLine.deleteCharAt(m_cursorIndex - 1);
				
				try {
					getStyledDocument().remove(getCmdStart() + m_cursorIndex - 2, 1);
				} catch (BadLocationException e) {
					e.printStackTrace();
				}
								
				m_cursorIndex--;
				updateCaret();
			}
		}
		
		public void delete() {
			setToPreview();
			
			if (m_currentLine.length() != 0 && m_cursorIndex < m_currentLine.length()) {
				m_currentLine.deleteCharAt(m_cursorIndex);
				
				
				try {
					getStyledDocument().remove(getCmdStart() + m_cursorIndex - 1, 1);
				} catch (BadLocationException e) {
					e.printStackTrace();
				}
				
				updateCaret();
			}
		}

		public void characterTyped(char c) {
			setToPreview();
			if (c == '\n') {
				//Will send the line to the output
				flushToQueue();

				m_cursorIndex = 0;
				//We add the line to history in readLine(), as we only want
				//prompted stuff to be saved in the history
				m_currentLine = new StringBuilder();
			} else {
				m_currentLine.insert(m_cursorIndex, c);
				m_cursorIndex++;
			}
			//Insert the character at the caret position
			try {
				getStyledDocument().insertString(getCmdStart() + m_cursorIndex, Character.toString(c), null);
			} catch (BadLocationException e) {
				e.printStackTrace();
			}
			
			updateCaret();
		}


		
		public void setCurrentLine(String line) {
			m_currentLine = new StringBuilder();
			m_currentLine.append(line);
			m_cursorIndex = m_currentLine.length();
		}

		public void flushToQueue() {
			PrintWriter writer = new PrintWriter(m_writer);
			writer.write(getLine());
			writer.write("\n");
			writer.flush();
			try {
				m_writer.flush();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

		public void setToPreview() {
			if (m_preview != null) {
				m_historyIndex = -1;
				// setCurrentLine() without the cursorIndex set
				m_currentLine = new StringBuilder();
				m_currentLine.append(m_preview);

				m_preview = null;
			}
		}

		public boolean isPreviewing() {
			return m_preview != null;
		}

		public String getPreview() {
			return m_preview;
		}
		
		public void previewLine(String line) {
			removeLine();
			
			try {
				getStyledDocument().insertString(getStyledDocument().getLength(), line, null);
			} catch (BadLocationException e) {
				e.printStackTrace();
			}

			m_preview = line;
			
			// Put cursor at the end of the line
			m_cursorIndex = line.length();
			
			updateCaret();
		}

		public String getLine() {
			return m_currentLine.toString();
		}

		public String getTextBuff() {
			if (isPreviewing())
				return getPreview();
			else
				return getLine();
		}
		
		public void updateCaret() {
			setCaretPosition(getCmdStart() + m_cursorIndex);
		}

		// Do nothing
		@Override
		public void close() throws IOException {
		}

		@Override
		public int read(char[] cbuf, int off, int len) throws IOException {
			return m_reader.read(cbuf, off, len);
		}

	}
	
	public class ConsolePrintStream extends PrintStream {
		public ConsolePrintStream(final AttributeSet attr) {
			super(new OutputStream() {
				@Override
				public void write(int b) throws IOException {
					JConsole.this.append(Character.toString((char) b), attr);
				}
				@Override
				public void write(byte[] b, int off, int len) throws IOException {
					JConsole.this.append(new String(b, off, len), attr);
				}
				
				@Override
				public void flush() {}
			});
		}
	}
}


