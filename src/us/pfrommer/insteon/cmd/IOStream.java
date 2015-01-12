package us.pfrommer.insteon.cmd;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

public interface IOStream {
	
	public boolean isOpen();
	
	public InputStream in();
	public OutputStream out();
	
	public void open() throws IOException;
	public void close() throws IOException;
}
