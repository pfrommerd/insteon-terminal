package us.pfrommer.insteon.cmd.gui;

import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.JFrame;
import javax.swing.JTextArea;

import us.pfrommer.insteon.cmd.IOPort;
import us.pfrommer.insteon.cmd.PortListener;
import us.pfrommer.insteon.cmd.msg.Msg;
import us.pfrommer.insteon.cmd.utils.Utils;

public class PortTracker extends JFrame  implements PortListener {
	private static final long serialVersionUID = 1L;
	
	private JTextArea m_area;
	
	public PortTracker(final IOPort p) {
		m_area = new JTextArea();
		
		getContentPane().add(m_area);

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
	public void wroteBytes(byte[] bytes) {
		m_area.append("OUT: " + Utils.toHex(bytes, bytes.length, " ") + "\n");
	}

	@Override
	public void bytesReceived(byte[] bytes) {
		m_area.append("IN: " + Utils.toHex(bytes, bytes.length, " ") + "\n");
	}

	@Override
	public void msgReceived(Msg msg) {
		
	}
}
