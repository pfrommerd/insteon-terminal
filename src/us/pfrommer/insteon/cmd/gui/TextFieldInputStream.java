package us.pfrommer.insteon.cmd.gui;

import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.io.IOException;
import java.io.InputStream;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import javax.swing.JTextField;


public class TextFieldInputStream extends InputStream {
	private BlockingQueue<byte[]> m_queue = new LinkedBlockingQueue<byte[]>();
	private byte[] m_current;
	private int m_pointer;

    public TextFieldInputStream(final JTextField text) {

        text.addKeyListener(new KeyAdapter() {
            @Override
            public void keyReleased(KeyEvent e) {
                if(e.getKeyChar()=='\n'){
                	byte[] b = (text.getText() + '\n').getBytes();
                    m_queue.add(b);
                    text.setText("");
                }
                super.keyReleased(e);
            }
        });
    }

    @Override
    public int read() throws IOException {
    	if (m_current == null || m_current.length <= m_pointer) {
    		try {
				m_current = m_queue.take();
			} catch (InterruptedException e) {}
    		m_pointer = 0;
    	}
    	System.out.println("Reading: " + (char) m_current[m_pointer]);
    	if (m_current[m_pointer] == '\n') System.out.println("New line!");
        return m_current[m_pointer++];
    }
    
    @Override
    public int read(byte[] b, int off, int len) {
		if (m_current == null || m_pointer >= m_current.length) {
			try {
				m_current = m_queue.take();
			} catch (InterruptedException e) {}
			m_pointer = 0;
		}
		int i = 0;
    	for (; i < len && m_pointer < m_current.length; i++, m_pointer++) {
    		b[off + i] = m_current[m_pointer];
    	}
    	return i;
    }
}