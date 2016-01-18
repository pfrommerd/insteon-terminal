package us.pfrommer.insteon.msg;

import java.io.IOException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.msg.Msg.Direction;
import us.pfrommer.insteon.utils.Utils;
/**
 * This class takes data coming from the serial port and turns it
 * into an message. For that, it has to figure out the length of the 
 * message from the header, and read enough bytes until it hits the
 * message boundary. The code is tricky, partly because the Insteon protocol is.
 * Most of the time the command code (second byte) is enough to determine the length
 * of the incoming message, but sometimes one has to look deeper into the message
 * to determine if it is a standard or extended message (their lengths differ).
 * 
 * @author Bernd Pfrommer
 * @author Daniel Pfrommer
 * @since 1.5.0
 */
public class MsgReader {
	private static final Logger logger = LoggerFactory.getLogger(MsgReader.class);
	// no idea what the max msg length could be, but
	// I doubt it'll ever be larger than 4k
	private final static int	MAX_MSG_LEN = 4096;
	private byte[] 				m_buf = new byte[MAX_MSG_LEN];
	private int					m_end = 0;	// offset of end of buffer

	private Direction			m_direction = Direction.FROM_MODEM;
	
	/**
	 * Constructor
	 */
	public MsgReader() {}

	public MsgReader(Direction d) {
		m_direction = d;
	}

	/**
	 * Adds incoming data to the data buffer. First call addData(), then call processData()
	 * @param data data to be added
	 * @param len length of data to be added
	 */
	public void addData(byte [] data, int off, int len) {
		if (len + m_end > MAX_MSG_LEN) {
			logger.error("warn: truncating excessively long message!");
			len = MAX_MSG_LEN - m_end;
		}
		// append the new data to the one we already have
		System.arraycopy(data, off, m_buf, m_end, len);
		m_end += len;
		// copy the incoming data to the end of the buffer
		logger.trace("read buffer: len {} data: {}", len, Utils.toHex(data, off, len));
	}
	
	/**
	 * Adds incoming data to the data buffer
	 * @param data data to be added
	 * @param len length of data to be added
	 */
	public void addData(byte b) {
		if (1 + m_end > MAX_MSG_LEN) {
			logger.error("warn: truncating excessively long message!");
		} else {
			// append the new data to the one we already have
			m_buf[m_end] = b;

			m_end += 1;

			// copy the incoming data to the end of the buffer
			logger.trace("read buffer: len {} data: {}", 1, Utils.toHex(b));
		}
	}
	
	/**
	 * After data has been added, this method processes it.
	 * processData() needs to be called until it returns null, indicating that no
	 * more messages can be formed from the data buffer.
	 * @return a valid message, or null if the message is not complete
	 * @throws IOException if data was received with unknown command codes
	 */
	public Msg processData() throws IOException {
		logger.trace("processing data: len {} data: {}", m_end, Utils.toHex(m_buf, 0, m_end));
		// handle the case where we get a pure nack
		if (m_end > 0 && m_buf[0] == 0x15) {
			logger.trace("got pure nack!");
			removeFromBuffer(1);
			try {
				Msg m = Msg.s_makeMessage("PureNACK");
				return m;
			} catch (IOException e) {
				return null;
			}
		}
		// drain the buffer until the first byte is 0x02
		if (m_end > 0 && m_buf[0] != 0x02) {
			bail("incoming message does not start with 0x02");
		}
		// Now see if we have enough data for a complete message.
		// If not, we return null, and expect this method to be called again
		// when more data has come in.
		int msgLen = -1;
		boolean isExtended = false;
		if (m_end > 1) {
			// we have some data, but do we have enough to read the entire header? 
			int headerLength = 0;
			switch(m_direction) {
			case FROM_MODEM: headerLength = Msg.s_getReplyHeaderLength(m_buf[1]); break;
			case TO_MODEM: headerLength = Msg.s_getSendHeaderLength(m_buf[1]); break;
			default: logger.error("Unrecognized message direction {}", m_direction);
			}
			
			isExtended = Msg.s_isExtended(m_buf, m_end, headerLength);
			logger.trace("header length expected: {} extended: {}", headerLength, isExtended);
			if (headerLength < 0) {
				removeFromBuffer(1); // get rid of the leading 0x02 so draining works
				bail("got unknown command code " + Utils.toHex(m_buf[1]));
			} else if (headerLength >= 2) {
				if (m_end >= headerLength) {
					// only when the header is complete do we know that isExtended is correct!
					msgLen = 0;
					switch(m_direction) {
					case FROM_MODEM: msgLen = Msg.s_getReplyMessageLength(m_buf[1], isExtended); break;
					case TO_MODEM: msgLen = Msg.s_getSendMessageLength(m_buf[1], isExtended); break;
					default: logger.error("Unrecognized message direction {}", m_direction);
					}
					
					if (msgLen < 0) {
						// Cannot make sense out of the combined command code & isExtended flag.
						removeFromBuffer(1);
						bail("unknown command code/ext flag: " + Utils.toHex(m_buf[1]));
					}
				}
			} else { // should never happen
				logger.error("invalid header length, internal error!");
				msgLen = -1;
			}
		}
		logger.trace("msgLen expected: {}", msgLen);
		Msg msg = null;
		if (msgLen > 0 && m_end >= msgLen) {
			switch(m_direction) {
			case FROM_MODEM: msg = Msg.s_createReplyMessage(m_buf, msgLen, isExtended); break;
			case TO_MODEM: msg = Msg.s_createSendMessage(m_buf, msgLen, isExtended); break;
			default: logger.error("Unrecognized message direction {}", m_direction);
			}
			removeFromBuffer(msgLen);
		}
		logger.trace("keeping buffer len {} data: {}", m_end, Utils.toHex(m_buf, 0, m_end));
		return msg;
	}
	
	private void bail(String txt) throws IOException {
		drainBuffer(); // this will drain until end or it finds the next 0x02
		logger.warn(txt);
		throw new IOException(txt);
	}
	
	private void drainBuffer() {
		while (m_end > 0 && m_buf[0] != 0x02) {
			removeFromBuffer(1);
		}
	}
	
	private void removeFromBuffer(int len) {
		if (len > m_end) len = m_end;
		System.arraycopy(m_buf, len, m_buf, 0, m_end + 1 - len);
		m_end -= len;
	}
}
