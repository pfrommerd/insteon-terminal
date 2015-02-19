package us.pfrommer.insteon.cmd.gui;

import java.awt.BorderLayout;
import java.io.InputStream;
import java.io.PrintStream;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.swing.JTextField;

import us.pfrommer.insteon.cmd.Console;

@SuppressWarnings("serial")
public class JConsole extends JFrame implements Console {
	private JTextArea m_text;
	private JTextField m_field;
	
	private InputStream m_in;
	private PrintStream m_out;
	
	public JConsole() {
		setTitle("Insteon Console");
		JPanel panel = new JPanel(new BorderLayout());
		getContentPane().add(panel, BorderLayout.CENTER);
		
		m_text = new JTextArea();
		m_text.setEditable(false);
		m_field = new JTextField();
		
		panel.add(m_text, BorderLayout.CENTER);
		panel.add(m_field, BorderLayout.SOUTH);
		
		m_in = new TextFieldInputStream(m_field);
		m_out = new PrintStream(new TextAreaOutputStream(m_text));
		
		setSize(500, 500);
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
}
