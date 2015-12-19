package us.pfrommer.insteon.emulator;

import java.util.Collections;
import java.util.HashMap;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import us.pfrommer.insteon.emulator.device.DeviceInfo;
import us.pfrommer.insteon.emulator.device.EmulatedDevice;
import us.pfrommer.insteon.emulator.device.LinkDatabase;
import us.pfrommer.insteon.emulator.device.LinkRecord;
import us.pfrommer.insteon.emulator.device.LinkType;
import us.pfrommer.insteon.msg.InsteonAddress;
import us.pfrommer.insteon.msg.Msg;

public class ModemEmulator extends EmulatedDevice {
	private static final Logger logger = LoggerFactory.getLogger(ModemEmulator.class);	

	private Set<ModemListener> m_listeners = Collections.newSetFromMap(new ConcurrentHashMap<ModemListener, Boolean>());
	
	private ConcurrentHashMap<String, ModemHandler> m_handlers = new ConcurrentHashMap<String, ModemHandler>();

	private HashMap<InsteonAddress, EmulatedDevice> m_devices = new HashMap<InsteonAddress, EmulatedDevice>();
	
	
	public ModemEmulator() {
		//Make up an address, devcat, subcat, and version
		super(null, new DeviceInfo(new InsteonAddress("00.00.00"),
								0x00, 0x00, 0x01));
		init();
	}
	
	public ModemEmulator(DeviceInfo info) {
		super(null, info);
		init();
	}

	
	
	public void addListener(ModemListener l) {
		m_listeners.add(l);
	}
	
	public void removeListener(ModemListener l) {
		m_listeners.remove(l);
	}
	
	public void addHandler(String msg, ModemHandler handler) {
		m_handlers.put(msg, handler);
	}
	
	private void init() {
		setRouting(getInfo().getAddress(), this);
		
		//Add the handlers
		addHandler("SendStandardMessage", new SendStandardHandler());
		
		addHandler("GetIMInfo", new InfoHandler());
		addHandler("GetFirstALLLinkRecord", new GetFirstLinkHandler());
		addHandler("GetNextALLLinkRecord", new GetNextLinkHandler());
	}
	
	
	// For message routing
	public EmulatedDevice resolve(InsteonAddress a) {
		return m_devices.get(a);
	}
	
	public void setRouting(InsteonAddress a, EmulatedDevice d) {
		m_devices.put(a, d);
	}
	
	public void route(EmulatedDevice sender, Msg m) {
		InsteonAddress fromAddress = sender.getInfo().getAddress();
		
		String type = m.getDefinition().getName();
		if (type.equals("SendStandardMessage")) {
			try {
				InsteonAddress toAddress = m.getAddress("toAddress");
				
				Msg receive = Msg.s_makeMessage("StandardMessageReceived");
				receive.setAddress("fromAddress", fromAddress);
				receive.setAddress("toAddress", toAddress);
				receive.setByte("messageFlags", m.getByte("messageFlags"));
				receive.setByte("command1", m.getByte("command1"));
				receive.setByte("command2", m.getByte("command2"));
				
				EmulatedDevice d = resolve(toAddress);
				d.receive(receive);
			} catch (Exception e) {
				logger.error("Could not route standard message: ", e);
			}
		} else if (type.equals("SendExtendedMessage")) {
			logger.warn("Routing extended messages not implemented!");
		} else {
			logger.warn("Cannot route messages of type {}", type);
		}
	}
	
	// Override the send and receive methods
	
	public void sendToHost(Msg m) {
		logger.debug("Emulator sent: {}", m);
		
		for (ModemListener l : m_listeners) {
			l.onMsgSent(m);
		}
	}
	
	public void receiveFromHost(Msg m) {
		logger.debug("Emulator received: {}", m);

		for (ModemListener l : m_listeners) {
			l.onMsgReceived(m);
		}
		
		String msgType = m.getDefinition().getName();
		logger.debug("Processing message of type: {}", msgType);
		
		ModemHandler h = m_handlers.get(msgType);
		if (h != null) {
			h.handle(this, m);
		}
	}
	
	// Handling messages from other devices

	public void receive(Msg m) {
		
	}
	
	// Now the handlers
	
	//
	// Message sending handlers
	//
	
	public static class SendStandardHandler implements ModemHandler {
		@Override
		public void handle(ModemEmulator emulator, Msg m) {
			logger.trace("Handling SendStandard message");

			try {

				Msg reply = Msg.s_makeMessage("SendStandardMessageReply");
				reply.setAddress("toAddress", m.getAddress("toAddress"));
				reply.setByte("messageFlags", m.getByte("messageFlags"));
				reply.setByte("command1", m.getByte("command1"));
				reply.setByte("command2", m.getByte("command2"));
				reply.setByte("ACK/NACK", (byte) 0x06);

				emulator.sendToHost(reply);

				emulator.route(emulator, m);
			} catch (Exception e) {
				logger.error("Failed to create SendStandardMessageReply!", e);
			}
		}
	}
	
	
	//
	// Link database handlers
	//
	
	//Handles GetFirstALLLinkRecord 
	public static class GetFirstLinkHandler implements ModemHandler {
		public void handle(ModemEmulator emulator, Msg m) {
			logger.trace("Handling GetFirstLinkRecord message");

			LinkDatabase db = emulator.getLinkDB();
			db.resetCounter();
			try {
				Msg reply = Msg.s_makeMessage("GetFirstALLLinkRecordReply");
				reply.setByte("ACK/NACK", (byte) (db.size() > 0 ? 0x06 : 0x15));
				emulator.sendToHost(reply);
				
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

					emulator.sendToHost(response);
				}
			} catch (Exception e) {
				logger.error("Failed to create GetFirstAllLinkRecord reply!", e);
			}
		}
	}
	
	public static class GetNextLinkHandler implements ModemHandler {
		public void handle(ModemEmulator emulator, Msg m) {
			logger.trace("Handling GetNextLinkRecord message");

			LinkDatabase db = emulator.getLinkDB();
			db.incCounter();
			try {
				Msg reply = Msg.s_makeMessage("GetNextALLLinkRecordReply");
				reply.setByte("ACK/NACK", (byte) (db.size() - db.counter() > 0 ? 0x06 : 0x15));
				emulator.sendToHost(reply);
				
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

					emulator.sendToHost(response);
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
	public static class InfoHandler implements ModemHandler {
		public void handle(ModemEmulator emulator, Msg m) {
			try {
				logger.trace("Handling GetIMInfo message");
				
				DeviceInfo info = emulator.getInfo();

				Msg reply = Msg.s_makeMessage("GetIMInfoReply");

				reply.setAddress("IMAddress", info.getAddress());
				reply.setByte("DeviceCategory", info.getDeviceCategory());
				reply.setByte("DeviceSubCategory", info.getSubCategory());
				reply.setByte("FirmwareVersion", info.getFirmwareVersion());
				reply.setByte("ACK/NACK", (byte) 0x06);
				
				emulator.sendToHost(reply);
			} catch (Exception e) {
				logger.error("Failed to create GetIMInfoReply message!", e);
			}
		}
	}
}
