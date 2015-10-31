package us.pfrommer.insteon.cmd.gui;

import java.awt.Color;
import java.awt.Font;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;

import javax.swing.JTextPane;
import javax.swing.text.AttributeSet;
import javax.swing.text.BadLocationException;
import javax.swing.text.DefaultCaret;
import javax.swing.text.SimpleAttributeSet;
import javax.swing.text.StyleConstants;
import javax.swing.text.StyledDocument;

public class OutputArea extends JTextPane {
	private static final long serialVersionUID = 1L;

	public OutputArea(Font f) {
		setFont(f);
		
		 DefaultCaret caret = (DefaultCaret) getCaret();
		 caret.setUpdatePolicy(DefaultCaret.ALWAYS_UPDATE);
	}
	
	public PrintStream createOutput(Color textColor) {
		SimpleAttributeSet attrib = new SimpleAttributeSet();
		StyleConstants.setForeground(attrib, textColor);
		
		return new ConsolePrintStream(attrib);
	}
	
	public void clear() {
		setText("");
	}

	private void append(String s, AttributeSet attr) {
		StyledDocument doc = getStyledDocument();
		try {
			doc.insertString(doc.getLength(), s, attr);
		} catch (BadLocationException e) {
			e.printStackTrace();
		}
	}
	
	public class ConsolePrintStream extends PrintStream {
		public ConsolePrintStream(final AttributeSet attr) {
			super(new OutputStream() {
				@Override
				public void write(int b) throws IOException {
					OutputArea.this.append(Character.toString((char) b), attr);
				}
				@Override
				public void write(byte[] b, int off, int len) throws IOException {
					OutputArea.this.append(new String(b, off, len), attr);
				}
				
				@Override
				public void flush() {}
			});
		}
	}
}
