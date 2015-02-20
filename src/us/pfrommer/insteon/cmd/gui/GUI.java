package us.pfrommer.insteon.cmd.gui;

import java.awt.Dimension;
import java.awt.Font;
import java.io.IOException;

import javax.swing.JFrame;
import javax.swing.JScrollBar;
import javax.swing.JScrollPane;
import javax.swing.UIDefaults;
import javax.swing.UIManager;

import us.pfrommer.insteon.cmd.InsteonInterpreter;

public class GUI extends JFrame {
	private static final long serialVersionUID = 1L;
	
	private JConsole m_console;
	public GUI() {
		//Stop the pane from scrolling on arrow keys
		UIManager.getDefaults().put("ScrollPane.ancestorInputMap",  
		        new UIDefaults.LazyInputMap(new Object[] {}));
		
		final JScrollPane pane = new JScrollPane();
		pane.getVerticalScrollBar().setUnitIncrement(16);
		
		m_console = new JConsole(new Font(Font.MONOSPACED, Font.PLAIN, 14));
		
		m_console.addListener(new JConsoleListener() {
			@Override
			public void sizeChanged(Dimension newSize) {
				//Call validate by hand
				//to ensure that the pane
				//gets the update
				//before we scroll down
				pane.validate();

				JScrollBar vertical = pane.getVerticalScrollBar();
				vertical.setValue(vertical.getMaximum());
			}
		});
		
		pane.getViewport().add(m_console);
		
		getContentPane().add(pane); 
		
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		
		setTitle("Insteon Terminal");
		setSize(500, 500);
		setVisible(true);
	}
	
	public void run() {
		InsteonInterpreter i = new InsteonInterpreter(m_console);
		i.run();
	}
	
	public static void main(String[] args) throws IOException {
		GUI gui = new GUI();
		gui.run();
	}
}