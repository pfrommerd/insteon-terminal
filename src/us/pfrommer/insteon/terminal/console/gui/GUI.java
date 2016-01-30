package us.pfrommer.insteon.terminal.console.gui;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.io.IOException;
import java.io.PrintStream;
import java.io.Reader;

import javax.swing.AbstractAction;
import javax.swing.ActionMap;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.UIDefaults;
import javax.swing.UIManager;

import us.pfrommer.insteon.terminal.console.Console;
import us.pfrommer.insteon.terminal.console.ConsoleListener;
import us.pfrommer.insteon.terminal.console.History;
import us.pfrommer.insteon.terminal.console.gui.InputArea.InputListener;

public class GUI implements Console {	
	private JFrame m_frame;
	
	private History m_history = new History(100);
	
	private OutputArea m_output;
	private InputArea m_input;
	
	private PrintStream m_out;
	private PrintStream m_err;
	
	public GUI() {
		JFrame frame = new JFrame();
		
		//Create the areas
		Font f = new Font(Font.MONOSPACED, Font.PLAIN, 14);
		
		m_output = new OutputArea(f);
		m_output.setEditable(false);
		
		m_output.addMouseListener(new MouseListener() {

			@Override
			public void mouseClicked(MouseEvent e) {
				m_input.requestFocus();
			}

			@Override
			public void mousePressed(MouseEvent e) {
			}

			@Override
			public void mouseReleased(MouseEvent e) {}

			@Override
			public void mouseEntered(MouseEvent e) {}

			@Override
			public void mouseExited(MouseEvent e) {}
		});
		
		m_out = m_output.createOutput(Color.BLACK);
		m_err = m_output.createOutput(Color.RED);
		
		m_input = new InputArea(f, m_history);
		m_input.addInputListener(new InputListener() {
			@Override
			public void onInput(String input, String text) {
				m_history.add(input);
				GUI.this.m_out.println(text);
			}
		});
		
		m_input.setBorder(null);
		
		//Now create the scroll stuff, layouts....
		
		//Stop the pane from scrolling on arrow keys
		UIManager.getDefaults().put("ScrollPane.ancestorInputMap",  
		        new UIDefaults.LazyInputMap(new Object[] {}));
		
		
		JPanel main = new JPanel(new BorderLayout()); 
		
		final JScrollPane pane = new JScrollPane();
		
		main.add(pane, BorderLayout.CENTER);
		main.add(m_input, BorderLayout.SOUTH);
	
		//Stop it from using arrow keys again....
		AbstractAction nothing = new AbstractAction() {
			private static final long serialVersionUID = 1L;

			@Override
			public void actionPerformed(ActionEvent e) {
			}
		};

		ActionMap am = pane.getActionMap();
		am.put("unitScrollUp", nothing);
		am.put("unitScrollDown", nothing);
		am.put("unitScrollLeft", nothing);
		am.put("unitScrollRight", nothing);
		
		pane.setBorder(null);
		pane.getVerticalScrollBar().setUnitIncrement(16);
		
		pane.getViewport().add(m_output);
		
		frame.getContentPane().add(main);
		
		frame.addWindowListener(new WindowListener() {
			@Override
			public void windowOpened(WindowEvent e) {}
			@Override
			public void windowClosing(WindowEvent e) {
				//For some reason window closed does not do the trick
				System.exit(0);				
			}
			@Override
			public void windowClosed(WindowEvent e) {
				System.exit(0);
			}
			@Override
			public void windowIconified(WindowEvent e) {}
			@Override
			public void windowDeiconified(WindowEvent e) {}

			@Override
			public void windowActivated(WindowEvent e) {}

			@Override
			public void windowDeactivated(WindowEvent e) {}
		});

		
		frame.setTitle("Insteon Terminal");
		frame.setSize(500, 500);
		
		m_frame = frame;
	}
	
	public void setVisible(boolean visible) {
		m_frame.setVisible(visible);
	}

	@Override
	public String readLine() throws IOException {
		return m_input.readLine();
	}

	@Override
	public String readLine(String prompt) throws IOException {
		return m_input.readLine(prompt);
	}

	@Override
	public void addConsoleListener(ConsoleListener l) {
		
	}

	@Override
	public void removeConsoleListener(ConsoleListener l) {
		
	}

	@Override
	public Reader in() {
		return m_input.getInput();
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
	public void clear() {
		m_output.clear();
		m_input.clear();
	}

	@Override
	public void reset() {
		clear();
	}
}