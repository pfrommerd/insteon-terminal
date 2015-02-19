package us.pfrommer.insteon.cmd.utils;

/**
 * Generic pair class.
 *
 * @author Daniel Pfrommer
 * @since 1.5.0
 */

public class Pair<K, V> {
	private K m_key;
	private V m_value;

	/**
	 * Constructs a new <code>Pair</code> with a given key/value
	 * 
	 * @param key  the key
	 * @param value the value
	 */
	public Pair(K key, V value) {
		setKey(key);
		setValue(value);
	}

	public K getKey() 				{ return m_key; }
	public V getValue() 			{ return m_value; }

	public void setKey(K key) 		{ m_key = key; }
	public void setValue(V value) 	{ m_value = value; }
}