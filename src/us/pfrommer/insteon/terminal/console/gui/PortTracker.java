package us.pfrommer.insteon.terminal.console.gui;

import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

import us.pfrommer.insteon.msg.IOPort;
import us.pfrommer.insteon.msg.Msg;
import us.pfrommer.insteon.msg.PortListener;
import us.pfrommer.insteon.utils.Utils;

public class PortTracker extends JFrame  implements PortListener {
	private static final long serialVersionUID = 1L;
	
	private JTextArea m_area;
	
	public PortTracker(final IOPort p) {
		m_area = new JTextArea();
		
		JScrollPane pane = new JScrollPane(m_area);
		
		getContentPane().add(pane);

		p.addListener(this);
		
		setTitle("PortTracker");
		setSize(500, 600);
		setVisible(true);

		addWindowListener(new WindowAdapter() {
			boolean m_closed = false;
			
			@Override
			public void windowClosing(WindowEvent e) {
				if (!m_closed) {
					p.removeListener(PortTracker.this);
					m_closed = true;
				}
			}
			@Override
			public void windowClosed(WindowEvent e) {
				if (!m_closed) {
					p.removeListener(PortTracker.this);
					m_closed = true;
				}
			}
		});
	}

	@Override
	public void msgWritten(Msg msg) {
		byte[]  bytes = msg.getData();
		m_area.append("OUT: " + Utils.toHex(bytes, 0, bytes.length, " ") + "\n");
		m_area.setCaretPosition(m_area.getDocument().getLength());
	}

	@Override
	public void msgReceived(Msg msg) {
		byte[] bytes = msg.getData();
		m_area.append("IN: " + Utils.toHex(bytes, 0, bytes.length, " ") + "\n");
		m_area.setCaretPosition(m_area.getDocument().getLength());
	}
}
