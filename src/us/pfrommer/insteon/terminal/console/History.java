package us.pfrommer.insteon.terminal.console;


public class History {
	private String[] m_history;
	private int m_count = 0;
	private int m_last = -1;
	
	public History(int size) {
		m_history = new String[size];
	}
	
	public int length() { return m_count; }
	
	//Previous is from 0-histoy.length -1
	//0 is the last thing entered
	// and history.length - 1 is the first thing entered
	public String get(int previous) {
		if (m_last < 0) return null;
		if (previous >= m_count) return null;
				
		int idx = Math.min(m_last, Math.max(0, m_last - previous));
		
		while (idx < 0) {
			idx += m_history.length;
		}
		
		return m_history[idx];
	}
	
	public void add(String s) {
		String l = get(0);
		if (l != null && l.equals(s)) return; //Don't store duplicate entries
		
		int idx = m_last + 1;
		if (idx >= m_history.length) {
			idx -= m_history.length;
		}
		m_history[idx] = s;
		
		m_last = idx;
		
		m_count = Math.max(m_history.length, m_count++);
	}
}
