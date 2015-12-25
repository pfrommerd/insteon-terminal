package us.pfrommer.insteon.emulator.network;

import java.util.ArrayList;
import java.util.Iterator;

public class LinkDatabase implements Iterable<LinkRecord> {
	private ArrayList<LinkRecord> m_records = new ArrayList<LinkRecord>();
	
	private int m_currentCounter = 0; // the next message to be returned
	
	public LinkDatabase() {}
	public int size() { return m_records.size(); }
	
	public int counter() { return m_currentCounter; }
	public void incCounter() { m_currentCounter++; }
	public void resetCounter() { m_currentCounter = 0; }
	
	public ArrayList<LinkRecord> getRecords() { return m_records; }
	
	public void add(LinkRecord r) { m_records.add(r); }
	
	public void remove(LinkRecord r) { m_records.remove(r); }
	public void remove(int idx) { m_records.remove(idx); }
	
	public LinkRecord get(int idx) { return m_records.get(idx); }
	
	public Iterator<LinkRecord> iterator() {
		return m_records.iterator();
	}
}
