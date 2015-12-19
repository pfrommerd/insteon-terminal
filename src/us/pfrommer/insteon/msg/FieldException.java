package us.pfrommer.insteon.msg;
/**
 * Exception to be thrown if there is an error processing a field, for
 * example type mismatch, out of bounds etc.
 * 
 * @author Daniel Pfrommer
 * @since 1.5.0
 */
@SuppressWarnings("serial")
public class FieldException extends Exception {
	public FieldException() { super(); }
	public FieldException(String m) { super(m); }
	public FieldException(String m, Throwable cause) { super(m, cause); }
	public FieldException(Throwable cause) { super(cause); }
}
