package us.pfrommer.insteon.cmd.gui;

import java.awt.Dimension;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.io.IOException;

import javax.swing.AbstractAction;
import javax.swing.ActionMap;
import javax.swing.JFrame;
import javax.swing.JScrollBar;
import javax.swing.JScrollPane;
import javax.swing.UIDefaults;
import javax.swing.UIManager;
import javax.swing.UIManager.LookAndFeelInfo;

import us.pfrommer.insteon.cmd.InsteonInterpreter;

public class GUI extends JFrame {
	private static final long serialVersionUID = 1L;
	
	private JConsole m_console;
	public GUI() {
		//Load the system look and feel
		try {
			for (LookAndFeelInfo info : UIManager.getInstalledLookAndFeels()) {
				if (info.getName().equals("Nimbus")) {
					UIManager.setLookAndFeel(info.getClassName());
					break;
				}
			}
		} catch (Exception e) { e.printStackTrace(); } 
		
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