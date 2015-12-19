package us.pfrommer.insteon.terminal.console.gui;

import java.awt.Color;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;

import javax.swing.AbstractAction;
import javax.swing.ActionMap;
import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.UIDefaults;
import javax.swing.UIManager;

public class FancyGUI extends JFrame {
	private static final long serialVersionUID = 1L;
	
	private FancyConsoleArea m_console;
	public FancyGUI() {
		//Stop the pane from scrolling on arrow keys
		UIManager.getDefaults().put("ScrollPane.ancestorInputMap",  
		        new UIDefaults.LazyInputMap(new Object[] {}));
		
		final JScrollPane pane = new JScrollPane();
	
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
		
		//m_console = new JConsole(new Font("Courier New", Font.PLAIN, 15));
		m_console = new FancyConsoleArea(new Font(Font.MONOSPACED, Font.PLAIN, 14),
										   Color.BLACK, Color.WHITE, Color.RED);
		
		pane.getViewport().add(m_console);
		
		getContentPane().add(pane); 
		
		addWindowListener(new WindowListener() {
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

		
		setTitle("Insteon Terminal");
		setSize(500, 500);
	}
	
	public FancyConsoleArea getConsole() {
		return m_console;
	}
}
