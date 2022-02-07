#-------------------------------------------------------------------------------
#
# Base class for all door sensors
#
import iofun
import message
from device import Device
from querier import Querier
from querier import MsgHandler
from dbbuilder import GenericDBBuilder
from linkdb import LightDBRecordFormatter
from us.pfrommer.insteon.msg import InsteonAddress

class DefaultMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		iofun.out(self.label + " got msg: " + msg.toString())
		return 1

# class StatusMsgHandler(MsgHandler):
#         label = None
#         def __init__(self, l):
#                 self.label = l
#         def processMsg(self, msg):
# 		if (msg.getByte("command2") == 0xFF):
# 			iofun.out(" Status: Open")
# 		elif (msg.getByte("command2") == 0x00):
# 			iofun.out(" Status: Closed")
#                 return 1

class StatusMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l

	def processMsg(self, msg):
		if msg.isExtended():
			rawflags = msg.getByte("userData3") & 0xFF
			flags = bin(msg.getByte("userData3") & 0xFF)[2:].zfill(8)
			batterylevel = msg.getByte("userData4") & 0xFF
			rawopenclosed = msg.getByte("userData5") & 0xFF
			if (rawopenclosed == 0):
				openclosed = "Open"
			elif (rawopenclosed == 255):
				openclosed = "Closed"
			else:
				openclosed = "Error reading status"
			rawheartbeatint = msg.getByte("userData6") & 0xFF ## heartbeat interval = this value * 5minutes.  0x00 = 24 hours (default)
			if (rawheartbeatint == 0):
				heartbeatint = 24*60
			else:
				heartbeatint = rawheartbeatint * 5
			lowbatterythreshold = msg.getByte("userData7") & 0xFF

			
			# Bit 0
			if (rawflags & 0b00000001 == 1):
				cleanupreport = "Send Cleanup Report"
			else:
				cleanupreport = "Don't Send Cleanup Report"
			# Bit 1
			if (rawflags & 0b00000010 == 2):
				twogroups = "Send Open on Group 1 ON and Closed on Group 2 ON"
			else:
				twogroups = "Send both Open and Closed on Group 1 (On=Open and Off=Closed)"
			# Bit 2
			if (rawflags & 0b00000100 == 4):
				openrepeat = "Send Repeated Open Commands (Every 5 mins for 50 mins)"
			else:
				openrepeat = "Don't Send Repeated Open Commands"
			# Bit 3
			if (rawflags & 0b00001000 == 8):
				closedrepeat = "Send Repeated Closed Commands (Every 5 mins for 50 mins)"
			else:
				closedrepeat = "Don't Send Repeated Closed Commands"
			# Bit 4
			if (rawflags & 0b00010000 == 16):
				ffgrp = "Link to FF Group"
			else:
				ffgrp = "Don't link to FF Group"
			# Bit 5
			if (rawflags & 0b00100000 == 32):
				ledonoff = "LED does not blink on transmission"
			else:
				ledonoff = "LED blinks on transmission"
			# Bit 6
			if (rawflags & 0b01000000 == 64):
				noeffect = "No Effect"
			else:
				noeffect = "No Effect"
			# Bit 7
			if (rawflags & 0b10000000 == 128):
				plock = "Programming lock on"
			else:
				plock = "Programming lock off"

			iofun.out(self.label + " Battery level: " + format(batterylevel, 'd') + " Low Battery threshold: " + format(lowbatterythreshold, 'd'))
			iofun.out(" Sensor Status: " + format(openclosed, 'd'))
			iofun.out(" Heartbeat Set Value: " + format(rawheartbeatint , 'd'))
			iofun.out(" Heartbeat Time: " + format(heartbeatint, 'd') + " minutes")
			iofun.out(" Configuration Byte (hex): " + format(rawflags,'X'))
			iofun.out(" Configuration Byte (binary): " + format(flags, 'd'))
			iofun.out(" Bit 0: 1 = Send Cleanup Report, 0 = Don't Send Cleanup Report")
			iofun.out(" Bit 1: 1 = Send Open on Group 1 ON / Closed on Group 2 ON, 0 = Send both Open and Closed on Group 1 (On=Open and Off=Closed)")
			iofun.out(" Bit 2: 1 = Send Repeated Open Commands, 0 = Don't Send Repeated Open Commands")
			iofun.out(" Bit 3: 1 = Send Repeated Closed Commands, 0 = Don't Send Repeated Closed Commands")
			iofun.out(" Bit 4: 1 = Link to FF Group, 0 = Don't link to FF Group")
			iofun.out(" Bit 5: 1 = LED does not blink on transmission, 0 = LED blinks on transmission")
			iofun.out(" Bit 6: No Effect")
			iofun.out(" Bit 7: 1 = Programming lock on, 0 = Programming Lock off")
			iofun.out("\nCurrent Config Byte Setting:")
			iofun.out("\n\t" + cleanupreport + "\n\t" + twogroups + "\n\t" + openrepeat + "\n\t"+ closedrepeat + "\n\t" + ffgrp + "\n\t" + ledonoff + "\n\t" + noeffect + "\n\t" + plock)
			return 1
		else:
			iofun.out(self.label + " unexpected direct message: " + msg.toString())
		return 0
		iofun.out(self.label + " = " + format(tmp, '02d'))
		return 1

class BatMsgHandler(MsgHandler):
        label = None
        def __init__(self, l):
                self.label = l
        def processMsg(self, msg):
                battery = msg.getByte("command2") & 0xFF
		iofun.out(" battery level: " + format(battery, 'd'))
                return 1

class HiddenDoorSensor(Device):
	"""==============  Insteon Hidden Door Sensor ===============
	NOTE: 1) The sensor must be awake in order for you to read/write data from/to it
	      2) Press and hold the link button to put it into Link mode.  This is the best way to ensure it is awake
	      3) Use modem.startWatch() / modem.stopWatch() to see incoming messages
	      """

	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

#	def getStatus(self):
#		"""getStatus()"""
#		self.querier.setMsgHandler(DefaultMsgHandler("status"))
#		return self.querier.queryext(0x19, 0x00, [0,0,0])

	def getStatus(self):
		"""getStatus()
		Reads and diplays all of the device settings as well as current open/closed position"""
		self.querier.setMsgHandler(StatusMsgHandler("\nHidden Door Sensor Status and Settings\n"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x00, 0x00])	

	def getBatLevel(self):
		"""getBatLevel()
		Reports battary level as a decimal number [61=~1.75v 54=~1.6 51=~1.5 40=~1.25]"""
		self.querier.setMsgHandler(BatMsgHandler("Get Bat Level"))
		return self.querier.queryext(0x19, 0x01, [0,0,0])

	def getFlags(self):
		"""getFlags()
		Reads and displays operating flags"""
		iofun.writeMsg(message.createStdMsg(InsteonAddress(self.getAddress()), 0x0F, 0x1F, 0x00, -1))

	def getDDBCount(self):
		"""getDDBCount()
		Data Base Delta flag gets incremented with any change in the Database """
		iofun.writeMsg(message.createStdMsg(InsteonAddress(self.getAddress()), 0x0F, 0x1F, 0x01, -1))

	def setPLOn(self):
		"""setPLOn()
		This enables the Local Programming Lock - No Press and Hold Linking"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Programming Lock ON"))
		return self.querier.queryext(0x20, 0x00, [0x00, 0x00, 0x00]);

	def setPLOff(self):
		"""setPLOff()
		This disables the Local Programming Lock - Allows Press and Hold Linking"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Programming Lock OFF"))
		return self.querier.queryext(0x20, 0x01, [0x00, 0x00, 0x00]);

	def setLEDOff(self):
		"""setLEDOff()
		This disables the LED blink during transmission"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set LED OFF"))
		return self.querier.queryext(0x20, 0x02, [0x00, 0x00, 0x00]);

	def setLEDOn(self):
		"""setLEDOn()
		This enables the LED blink during transmission"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set LED ON"))
		return self.querier.queryext(0x20, 0x03, [0x00, 0x00, 0x00]);

	def setTwoGroupsOn(self):
		"""setTwoGroupsOn()
		This makes the HDS send an ON to group 1 for Open and an ON to group 2 for closed."""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Two Groups ON"))
		return self.querier.queryext(0x20, 0x04, [0x00, 0x00, 0x00]);

	def setTwoGroupsOff(self):
		"""setTwoGroupsOff()
		this makes the HDS send an ON to group 1 for open and an OFF to group 1 for closed"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Two Groups Off"))
		return self.querier.queryext(0x20, 0x05, [0x00, 0x00, 0x00]);	

	def setLinkToAllGrpsOn(self):
		"""setLinkToAllGrpsOn()
		This links the HDS to all groups (Group 0xFF)"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Link to FF"))
		return self.querier.queryext(0x20, 0x06, [0x00, 0x00, 0x00]);

	def setLinkToAllGrpsOff(self):
		"""setLinkToAllGrpsOff()
		This removes the link to all groups (0xFF)"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Link to FF off"))
		return self.querier.queryext(0x20, 0x07, [0x00, 0x00, 0x00]);

	def setCloseRepeatOn(self):
		"""setCloseRepeatOn()
		This sets the HDS to send repeat closed commands every 5 mins for 50 mins"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Close Repeat ON"))
		return self.querier.queryext(0x20, 0x08, [0x00, 0x00, 0x00]);

	def setCloseRepeatOff(self):
		"""setCloseRepeatOff()
		This stops the HDS from sending repeat closed commands every 5 mins for 50 mins"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Close Repeat OFF"))
		return self.querier.queryext(0x20, 0x09, [0x00, 0x00, 0x00]);

	def setOpenRepeatOn(self):
		"""setOpenRepeatOn()
		This sets the HDS to send repeat open commands every 5 mins for 50 mins"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Open Repeat ON"))
		return self.querier.queryext(0x20, 0x0A, [0x00, 0x00, 0x00]);

	def setOpenRepeatOff(self):
		"""setOpenRepeatOff()
		This stops the HDS from sending repeat open commands every 5 mins for 50 mins"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Open Repeat OFF"))
		return self.querier.queryext(0x20, 0x0B, [0x00, 0x00, 0x00]);

	def setCleanupReportOff(self):
		"""setCleanupReportOff()
		This prevents the HDS from sending a cleanup report after changes in status"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Cleanup Report Off\n"))
		return self.querier.queryext(0x20, 0x16, [0x00, 0x00, 0x00]);

	def setCleanupReportOn(self):
		"""setCleanupReportOn()
		This allows the HDS to send a cleanup report after changes in status"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Cleanup Report On\n"))
		return self.querier.queryext(0x20, 0x17, [0x00, 0x00, 0x00]);

	def setHBInterval(self, level):
		"""setHBInterval(level)
		This sets the heartbeat interval in 5 minute increments.  Value (0-255) x 5mins (0 = 24 hours)"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Heartbeat Interval"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x02, level]);

	def setLowBatLevel(self, level):
		"""setLowBatLevel(level)
		This sets point where the HDS sends an ON command to Group 3 to indicate low battery. Value (0-255)"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Heartbeat Interval"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x03, level]);

