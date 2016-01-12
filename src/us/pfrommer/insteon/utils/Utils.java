package us.pfrommer.insteon.utils;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import us.pfrommer.insteon.msg.DataType;
import us.pfrommer.insteon.msg.InsteonAddress;

/**
 * Various utility functions for e.g. hex string parsing
 * @author Daniel Pfrommer
 * @since 1.5.0
 */

public class Utils {
	public static String readFile(File f) throws IOException {
		return read(new FileInputStream(f));
	}
	public static String read(InputStream in) throws IOException {
		BufferedReader r = new BufferedReader(new InputStreamReader(in));
		StringBuilder b = new StringBuilder();
		
		String line = null;
		while((line = r.readLine()) != null) {
			b.append(line);
			b.append('\n');
		}
		
		return b.toString();
	}
	
	
	public static String toHex(int b) {
		String result =  String.format("%02X", b & 0xFF);
		return result;
	}
	public static String toHex(byte b) {
		String result =  String.format("%02X", b);
		return result;
	}

	public static String toHex(byte[] b) {
		return toHex(b, 0, b.length);
	}
	
	public static String toHex(byte[] b, int off, int len) {
		return toHex(b, off, len, "");
	}

	public static String toHex(byte[] b, int off, int len, String separator) {
		StringBuilder result = new StringBuilder();
		for (int i = 0; i < b.length && i < len; i++) {
			result.append(toHex(b[i]));
			if (i != b.length - 1) result.append(separator);
		}
		return result.toString();
	}
	
	public static int fromHexString(String string) {
		return Integer.parseInt(string, 16);
	}
	
	public static int from0xHexString(String string) {
		String hex = string.substring(2);
		return fromHexString(hex);
	}
	
	public static String toHexByte(byte b) {
		return String.format("0x%02X", b & 0xFF);
	}
	
	public static String toHexByte(int b) {
		return String.format("0x%02X", b);
	}
	
	public static class DataTypeParser {
		public static Object s_parseDataType(DataType type, String val) {
			switch(type) {
			case BYTE: 		return s_parseByte(val);
			case INT:		return s_parseInt(val);
			case FLOAT: 	return s_parseFloat(val);
			case ADDRESS:	return s_parseAddress(val);
			default : throw new IllegalArgumentException("Data Type not implemented in Field Value Parser!");
			}
		}
		
		public static byte s_parseByte(String val) {
			if (val != null && !val.trim().equals("")) {
				return (byte) Utils.from0xHexString(val.trim());
			} else return 0x00;
		}
		public static int s_parseInt(String val) {
			if (val != null && !val.trim().equals("")) {
				return Integer.parseInt(val);
			} else return 0x00;
		}
		public static float s_parseFloat(String val) {
			if (val != null && !val.trim().equals("")) {
				return Float.parseFloat(val.trim());
			} else return 0;
		}
		public static InsteonAddress s_parseAddress(String val) {
			if (val != null && !val.trim().equals("")) {
				return InsteonAddress.s_parseAddress(val.trim());
			} else return new InsteonAddress();
		}
	}
	/**
	 * Exception to indicate various xml parsing errors.
	 */
	@SuppressWarnings("serial")
	public static class ParsingException  extends Exception { 
		public ParsingException(String msg) {
			super(msg);
		}
		public ParsingException(String msg, Throwable cause) {
			super(msg, cause);
		}
	}
}
