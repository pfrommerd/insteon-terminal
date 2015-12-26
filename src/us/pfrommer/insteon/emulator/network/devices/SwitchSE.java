package us.pfrommer.insteon.emulator.network.devices;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.emulator.network.Device;
import us.pfrommer.insteon.emulator.network.DeviceInfo;
import us.pfrommer.insteon.emulator.network.StandardHandler;
import us.pfrommer.insteon.msg.InsteonAddress;
import us.pfrommer.insteon.msg.MsgType;

public class SwitchSE extends Device {
	private static final Logger logger = LoggerFactory.getLogger(SwitchSE.class);
	
	private boolean m_state = false;
	
	public SwitchSE(String name, InsteonAddress adr) {
		super(name, new DeviceInfo(adr, 0x00, 0x00, 0x01));
		init();
	}

	public SwitchSE(String name, String adr) {
		this(name, new InsteonAddress(adr));
	}
	
	private void init() {
		addStandardHandler(0x11, new OnHandler());
		addStandardHandler(0x12, new OnHandler());
		addStandardHandler(0x13, new OffHandler());
		addStandardHandler(0x14, new OffHandler());
		
		addStandardHandler(0x019, new StatusRequestHandler());
	}
	
	public class OnHandler implements StandardHandler {
		@Override
		public void handleStandard(InsteonAddress from, MsgType type, int cmd1, int cmd2) {
			m_state = true;
			logger.info("Switch \"{}\" updated to {}", getName(), m_state ? "ON" : "OFF");
			
			sendStandardMsg(from, MsgType.ACK_OF_DIRECT, cmd1, cmd2);
		}
	}

	public class OffHandler implements StandardHandler {
		@Override
		public void handleStandard(InsteonAddress from, MsgType type, int cmd1, int cmd2) {
			m_state = false;
			logger.info("Switch \"{}\" updated to {}", getName(), m_state ? "ON" : "OFF");
			
			sendStandardMsg(from, MsgType.ACK_OF_DIRECT, cmd1, cmd2);
		}
	}
	
	public class StatusRequestHandler implements StandardHandler {
		@Override
		public void handleStandard(InsteonAddress from, MsgType type, int cmd1, int cmd2) {
			logger.info("Switch \"{}\" queried, state is: {}", getName(), m_state ? "ON" : "OFF");
			
			sendStandardMsg(from, MsgType.ACK_OF_DIRECT, 0, m_state ? 0xFF : 0x00);
		}
	}
}
