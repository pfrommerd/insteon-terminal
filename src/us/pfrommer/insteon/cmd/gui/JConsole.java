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
import java.awt.Dimension;
import java.awt.Font;
import java.awt.FontMetrics;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PipedInputStream;
import java.io.PipedOutputStream;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Formatter;
import java.util.HashSet;

import javax.swing.JComponent;

import us.pfrommer.insteon.cmd.Console;


/**
	A JFC/Swing based console for the BeanShell desktop.
	This is a descendant of the old AWTConsole.

	Improvements by: Mark Donszelmann <Mark.Donszelmann@cern.ch>
		including Cut & Paste

  	Improvements by: Daniel Leuck
		including Color and Image support, key press bug workaround
*/
public class JConsole extends JComponent
	implements Console, KeyListener {
	private static final long serialVersionUID = 1L;
	
	//A list sorted from most recent to least recent command
	private ArrayList<String> m_history = new ArrayList<String>();
	
	private StringBuilder m_text = new StringBuilder();
	private int m_cursorIndex = 0;
	private int m_historyIndex = -1;
	
	private ConsoleStream m_in = new ConsoleStream();
	private ConsolePrintStream m_out = new ConsolePrintStream();

	private HashSet<JConsoleListener> m_listeners = new HashSet<JConsoleListener>();
	
	private Font m_font;
	
	private Color m_foreground = Color.BLACK;
	private Color m_background = Color.WHITE;
	
	private Dimension m_preferredSize = new Dimension(10, 10);
	private boolean m_cursorVisible = true;
	
	public JConsole(Font f) {
		m_font = f;
		
		addKeyListener(this);
		
		setFocusable(true);
		requestFocus();
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

	@Override
	public void paintComponent(Graphics g) {
		Graphics2D g2d = (Graphics2D) g;
		
		g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,
							 RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
		
		
		//Fill the background
		g2d.setColor(m_background);
		g2d.fillRect(0, 0, getWidth(), getHeight());
		
		//Draw the text
		g2d.setColor(m_foreground);
		
		g2d.setFont(m_font);
		FontMetrics metrics = g2d.getFontMetrics();
		
		String text = m_text.toString();
		String[] lines = text.split("\\r?\\n", -1);
		
		int lineHeight = metrics.getHeight();
		int lineAscent = metrics.getAscent();
		
		int prefWidth = 0;
		int prefHeight = 0;
		
		int x = 3;
		//We need to start at lineHeight
		//as the y is the baseline, not the top of the text
		int y = 0;
		for (int i = 0; i < lines.length; i++) {
			String line = lines[i];
			//Add the lineHeight as the x,y are the baseline
			g2d.drawString(line, x, y + lineAscent);
			
			//Add this line to the preferred height
			prefHeight += lineHeight;
			
			//Update the prefWidth
			prefWidth = Math.max(prefWidth, x + metrics.stringWidth(line));
			
			//newline only if the line had a \n(if it is not the last line
			if (i != lines.length - 1) y += lineHeight;
			else {
				//If it is the last line,
				//we want to draw the currentline after it
				//so set the x to the pos after the last char
				x += metrics.stringWidth(line);
			}
		}
		//Include the last line of text in the preferred width
		prefWidth = Math.max(prefWidth, x + metrics.stringWidth(m_in.getTextBuff()));

		//Draw the current line of text
		//after the end of the last line
		String inputBuf = m_in.getTextBuff();
		
		String before = inputBuf.substring(0, m_cursorIndex);
		char cursorChar = m_cursorIndex < inputBuf.length() ? inputBuf.charAt(m_cursorIndex) : '\0';
		String after =  m_cursorIndex < inputBuf.length() ? inputBuf.substring(m_cursorIndex + 1) : "";
		
		//Draw the part before the cursor
		g2d.drawString(before, x, y + lineAscent);
		x += metrics.stringWidth(before);
		
		//Draw the cursor
		
		//Use an space as the default width if the cursor is not over a character
		int cursorWidth = cursorChar == '\0' ? metrics.stringWidth(" ") : metrics.stringWidth(Character.toString(cursorChar));
		
		if (cursorChar == '\0') x += 1;
		
		if (m_cursorVisible) {
			//Draw a rect covering the char with the foreground color
			g2d.setColor(m_foreground);
			g2d.fillRect(x, y, cursorWidth, lineHeight);
		}

		if (cursorChar != '\0') {
			//Draw the char with the background color
			//only if the cursor is visible
			if (m_cursorVisible) g2d.setColor(m_background);

			g2d.drawString(Character.toString(cursorChar), x, y + lineAscent);

			//Set the drawing color back to normal
			g2d.setColor(m_foreground);
		}
		
		x += cursorWidth;
		
		//Draw the second part
		g2d.drawString(after, x, y + lineAscent);
		x += g2d.getFontMetrics().stringWidth(after);
		
		
		//Update preferred size
		Dimension newSize = new Dimension(prefWidth + 10, prefHeight + 10);
		
		if (!m_preferredSize.equals(newSize)) {
			m_preferredSize = newSize;
			
			//Revalidate to make sure the scrollpane knows the size has changed
			revalidate();

			synchronized(m_listeners) {
				for (JConsoleListener l : m_listeners) l.sizeChanged(m_preferredSize);
			}			
		}
		
	}
	
	@Override
	public void keyTyped(KeyEvent e) {
		//Check to make sure the character is valid before typing it
		if ((e.getKeyChar() < 32 || e.getKeyChar() > 126) && e.getKeyChar() != '\n') return;
		//Type it!
		m_in.characterTyped(e.getKeyChar());
		
		//Don't forget to repaint
		repaint();
	}

	@Override
	public void keyPressed(KeyEvent e) {
		switch(e.getKeyCode()) {
		case KeyEvent.VK_BACK_SPACE: m_in.backspace(); break;
		case KeyEvent.VK_LEFT : m_in.left(); break;
		case KeyEvent.VK_RIGHT : m_in.right(); break;
		case KeyEvent.VK_UP : m_in.up(); break;
		case KeyEvent.VK_DOWN : m_in.down(); break;
		default: break;
		}
		
		repaint();
	}

	@Override
	public void keyReleased(KeyEvent e) {
		
	}

	@Override
	public InputStream in() {
		return m_in;
	}

	@Override
	public PrintStream out() {
		return m_out;
	}

	@Override
	public PrintStream err() {
		return m_out;
	}
	
	@Override
	public void clear() {
		m_text = new StringBuilder();
		repaint();
	}

	@Override
	public void reset() {
		repaint();
		//Will clear the screen
		//and wipe the history
		m_history.clear();
	}
	
	@Override
	public Dimension getPreferredSize() {
		return m_preferredSize;
	}
	

	public class ConsoleStream extends InputStream {
		PipedOutputStream m_output = new PipedOutputStream();
		InputStream m_in;
		
		StringBuilder m_currentLine = new StringBuilder();
		String m_preview;

		public ConsoleStream() {
			try {
				m_in = new PipedInputStream(m_output);
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		
		public void left() {
			if (m_cursorIndex > 0) m_cursorIndex--;
		}
		
		public void right() {
			if (m_cursorIndex < getTextBuff().length()) m_cursorIndex++;
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

			if (m_currentLine.length() != 0) {
				m_currentLine.deleteCharAt(m_cursorIndex - 1);
				m_cursorIndex--;
			}
		}
		
		public void delete() {
			setToPreview();
			
			if (m_currentLine.length() != 0 && m_cursorIndex < m_currentLine.length()) {
				m_currentLine.deleteCharAt(m_cursorIndex);
			}
		}

		public void characterTyped(char c) {
			setToPreview();
			if (c == '\n') {
				//Will send the line to the output
				flushToQueue();
				
				m_out.println(m_currentLine.toString());
				
				m_cursorIndex = 0;
				// Add the line to the last history
				m_history.add(0, getLine());
				m_currentLine = new StringBuilder();
			} else {
				m_currentLine.insert(m_cursorIndex, c);
				m_cursorIndex++;
			}
		}

		public void setCurrentLine(String line) {
			m_currentLine = new StringBuilder();
			m_currentLine.append(line);
			m_cursorIndex = m_currentLine.length();
		}

		public void flushToQueue() {
			PrintWriter writer = new PrintWriter(m_output);
			writer.write(getLine());
			writer.write('\n');
			writer.flush();
			try {
				m_output.flush();
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
			m_preview = line;
			// Put cursor at the end of the line
			m_cursorIndex = line.length();
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

		public int read() throws IOException {
			int read = m_in.read();
			return read;
		}


		// Do nothing
		@Override
		public void close() throws IOException {
		}
	}
	
	public class ConsolePrintStream extends PrintStream {
		private Formatter m_formatter;

		public ConsolePrintStream() {
			//Forget about this, we overwrite all the necessary methods
			super(new OutputStream() {
				@Override
				public void write(int b) throws IOException {
					m_text.append((char) b);
					flush();
				}
				@Override
				public void write(byte[] b, int off, int len) throws IOException {
					m_text.append(new String(b, off, len));
					flush();
				}		
				@Override
				public void flush() {
					repaint();
				}
			});
		}
	}
}


