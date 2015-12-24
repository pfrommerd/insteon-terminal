package us.pfrommer.insteon.emulator.network.modem;

import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.emulator.network.Device;
import us.pfrommer.insteon.emulator.network.DeviceInfo;
import us.pfrommer.insteon.emulator.network.LinkDatabase;
import us.pfrommer.insteon.emulator.network.LinkRecord;
import us.pfrommer.insteon.emulator.network.LinkType;
import us.pfrommer.insteon.msg.InsteonAddress;
import us.pfrommer.insteon.msg.Msg;
import us.pfrommer.insteon.msg.MsgType;

public class ModemSE extends Device {
	private static final Logger logger = LoggerFactory.getLogger(ModemSE.class);	

	private Set<ModemListener> m_listeners = Collections.newSetFromMap(new ConcurrentHashMap<ModemListener, Boolean>());
	
	private ConcurrentHashMap<String, ModemHandler> m_handlers = new ConcurrentHashMap<String, ModemHandler>();

	private HashMap<InsteonAddress, Device> m_devices = new HashMap<InsteonAddress, Device>();
	
	
	public ModemSE() {
		//Make up an address, devcat, subcat, and version
		super("modem", new DeviceInfo(new InsteonAddress("00.00.00"),
								0x00, 0x00, 0x01));
		init();
	}
	
	public ModemSE(DeviceInfo info) {
		super("modem", info);
		init();
	}

	
	
	public void addListener(ModemListener l) {
		m_listeners.add(l);
	}
	
	public void removeListener(ModemListener l) {
		m_listeners.remove(l);
	}
	
	public void addModemHandler(String msg, ModemHandler handler) {
		m_handlers.put(msg, handler);
	}
	
	private void init() {
		//Add the handlers
		addModemHandler("SendStandardMessage", new SendStandardHandler());
		
		addModemHandler("GetIMInfo", new InfoHandler());
		addModemHandler("GetFirstALLLinkRecord", new GetFirstLinkHandler());
		addModemHandler("GetNextALLLinkRecord", new GetNextLinkHandler());
	}
	
	//Send and receive methods
		
	// Modem uses this to send commands to the host
	public void sendToHost(Msg m) {
		logger.trace("Emulated modem sent: {}", m);
		
		for (ModemListener l : m_listeners) {
			l.onMsgSent(m);
		}
	}
	
	// Gets called when a message arrives from the host
	public void receiveFromHost(Msg m) {
		logger.trace("Emulated modem received: {}", m);

		for (ModemListener l : m_listeners) {
			l.onMsgReceived(m);
		}
		
		String msgType = m.getDefinition().getName();
		
		ModemHandler h = m_handlers.get(msgType);
		if (h != null) {
			h.handle(m);
		}
	}

	// Handlers for messages received from the "network"
	
	@Override
	public void onStandardMsg(InsteonAddress sender, MsgType type, int cmd1, int cmd2) {
		try {
			Msg m = Msg.s_makeMessage("StandardMessageReceived");
			m.setAddress("fromAddress", sender);
			m.setAddress("toAddress", getInfo().getAddress());
			m.setByte("messageFlags", (byte)(type.getByteValue() & 0xFF));
			m.setByte("command1", (byte) (cmd1 & 0xFF)); 
			m.setByte("command2", (byte) (cmd2 & 0xFF)); 
			
			sendToHost(m);
		} catch (Exception e) {
			logger.error("Failed to create StandardMessageReceived!", e);
		}
	}

	@Override
	public void onExtendedMsg(InsteonAddress sender, MsgType type, int cmd1, int cmd2, byte[] data) {
		try {
			Msg m = Msg.s_makeMessage("ExtendedMessageReceived");
			m.setAddress("fromAddress", sender);
			m.setAddress("toAddress", getInfo().getAddress());
			m.setByte("messageFlags", (byte)(type.getByteValue() & 0xFF));
			m.setByte("command1", (byte) (cmd1 & 0xFF)); 
			m.setByte("command2", (byte) (cmd2 & 0xFF)); 
			
			if (data.length != 12)  {
				logger.error("Illegal userdata from {}, length is not 12!", sender);
				return;
			}
			
			m.setByte("userData1", data[0]);
			m.setByte("userData2", data[1]);
			m.setByte("userData3", data[2]);
			m.setByte("userData4", data[3]);
			m.setByte("userData5", data[4]);
			m.setByte("userData6", data[5]);
			m.setByte("userData7", data[6]);
			m.setByte("userData8", data[7]);
			m.setByte("userData9", data[8]);
			m.setByte("userData10", data[10]);
			m.setByte("userData11", data[11]);
			m.setByte("userData12", data[12]);
			m.setByte("userData13", data[13]);
			
			sendToHost(m);
		} catch (Exception e) {
			logger.error("Failed to create StandardMessageReceived!", e);
		}
	}
	
	// Now the modem handlers
	// that is, messages received from the host
	
	//
	// Message sending handlers
	//
	
	public class SendStandardHandler implements ModemHandler {
		@Override
		public void handle(Msg m) {
			logger.trace("Handling SendStandard message");

			try {

				Msg reply = Msg.s_makeMessage("SendStandardMessageReply");
				reply.setAddress("toAddress", m.getAddress("toAddress"));
				reply.setByte("messageFlags", m.getByte("messageFlags"));
				reply.setByte("command1", m.getByte("command1"));
				reply.setByte("command2", m.getByte("command2"));
				reply.setByte("ACK/NACK", (byte) 0x06);

				sendToHost(reply);

				MsgType type = MsgType.s_fromValue(m.getByte("messageFlags"));
				
				m_network.routeStandard(getInfo().getAddress(), m.getAddress("toAddress"), type,
										m.getByte("command1") & 0xFF, m.getByte("command2") & 0xFF);
			} catch (Exception e) {
				logger.error("Failed to create SendStandardMessageReply!", e);
			}
		}
	}
	
	
	//
	// Link database handlers
	//
	
	//Handles GetFirstALLLinkRecord 
	public class GetFirstLinkHandler implements ModemHandler {
		public void handle(Msg m) {
			logger.trace("Handling GetFirstLinkRecord message");

			LinkDatabase db = getLinkDB();
			db.resetCounter();
			try {
				Msg reply = Msg.s_makeMessage("GetFirstALLLinkRecordReply");
				reply.setByte("ACK/NACK", (byte) (db.size() > 0 ? 0x06 : 0x15));
				sendToHost(reply);
				
				//Retrieve the first record
				if (db.size() > 0) {
					LinkRecord record = db.get(0);
					
					byte flag = (byte) (0b10000010 & 0xFF);
					if (record.getType() == LinkType.CONTROLLER)
						flag |= 0b01000000;
					
					Msg response = Msg.s_makeMessage("ALLLinkRecordResponse");
					response.setByte("RecordFlags", flag);
					response.setByte("ALLLinkGroup", (byte) (record.getGroup() & 0xFF));
					response.setAddress("LinkAddr", record.getAddress());

					response.setByte("LinkData1", record.getData1());
					response.setByte("LinkData2", record.getData2());
					response.setByte("LinkData3", record.getData3());

					sendToHost(response);
				}
			} catch (Exception e) {
				logger.error("Failed to create GetFirstAllLinkRecord reply!", e);
			}
		}
	}
	
	public class GetNextLinkHandler implements ModemHandler {
		public void handle(Msg m) {
			logger.trace("Handling GetNextLinkRecord message");

			LinkDatabase db = getLinkDB();
			db.incCounter();
			try {
				Msg reply = Msg.s_makeMessage("GetNextALLLinkRecordReply");
				reply.setByte("ACK/NACK", (byte) (db.size() - db.counter() > 0 ? 0x06 : 0x15));
				sendToHost(reply);
				
				//Retrieve the first record
				if (db.size() - db.counter() > 0) {
					LinkRecord record = db.get(0);
					
					byte flag = (byte) (0b10000010 & 0xFF);
					if (record.getType() == LinkType.CONTROLLER)
						flag |= 0b01000000;
					
					Msg response = Msg.s_makeMessage("ALLLinkRecordResponse");
					response.setByte("RecordFlags", flag);
					response.setByte("ALLLinkGroup", (byte) (record.getGroup() & 0xFF));
					response.setAddress("LinkAddr", record.getAddress());

					response.setByte("LinkData1", record.getData1());
					response.setByte("LinkData2", record.getData2());
					response.setByte("LinkData3", record.getData3());

					sendToHost(response);
				}
			} catch (Exception e) {
				logger.error("Failed to create GetNextAllLinkRecord reply!", e);
			}
		}
	}
	
	//
	// 
	//
	
	// Handles GetIMInfo messages
	public class InfoHandler implements ModemHandler {
		public void handle(Msg m) {
			try {
				logger.trace("Handling GetIMInfo message");
				
				DeviceInfo info = getInfo();

				Msg reply = Msg.s_makeMessage("GetIMInfoReply");

				reply.setAddress("IMAddress", info.getAddress());
				reply.setByte("DeviceCategory", info.getDeviceCategory());
				reply.setByte("DeviceSubCategory", info.getSubCategory());
				reply.setByte("FirmwareVersion", info.getFirmwareVersion());
				reply.setByte("ACK/NACK", (byte) 0x06);
				
				sendToHost(reply);
			} catch (Exception e) {
				logger.error("Failed to create GetIMInfoReply message!", e);
			}
		}
	}
}
