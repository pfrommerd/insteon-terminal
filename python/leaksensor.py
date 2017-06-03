#-------------------------------------------------------------------------------
#
# Base class for all motion sensors
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

class StatusMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l

	def processMsg(self, msg):
		if msg.isExtended():
			LEDBrightness =  msg.getByte("userData3") & 0xFF
			rawflags = msg.getByte("userData6") & 0xFF
			flags = bin(msg.getByte("userData6") & 0xFF)[2:].zfill(8)
			# Bit 0
			if (rawflags & 0b00000001 == 1):
				cleanupreport = "Send Cleanup Report"
			else:
				cleanupreport = "Don't Send Cleanup Report"
			# Bit 1
			if (rawflags & 0b00000010 == 2):
				readjumper = "Don't Read the jumper"
			else:
				readjumper = "Read The Jumper"
			# Bit 2
			if (rawflags & 0b00000100 == 4):
				wetdrygroups = "Send Dry on Group 1 ON/Wet on Group 2 ON"
			else:
				wetdrygroups = "Send both Dry and Wet on Group 1 (On=Dry and Off=Wet)"
			# Bit 3
			if (rawflags & 0b00001000 == 8):
				wetrepeat = "Send Repeated Wet Commands"
			else:
				wetrepeat = "Don't Send Repeated Wet Commands"
			# Bit 4
			if (rawflags & 0b00010000 == 16):
				dryrepeat = "Send Repeated Dry Commands"
			else:
				dryrepeat = "Don't Send Repeated Dry Commands"
			# Bit 5
			if (rawflags & 0b00100000 == 32):
				ledonoff = "LED does not blink on transmission"
			else:
				ledonoff = "LED blinks on transmission"
			# Bit 6
			if (rawflags & 0b01000000 == 64):
				ffgrp = "Link to FF Group"
			else:
				ffgrp = "Don't link to FF Group"
			# Bit 7
			if (rawflags & 0b10000000 == 128):
				plock = "Programming lock on"
			else:
				plock = "Programming lock off"

			iofun.out(self.label + " LED Brightness (if flag set on): " + format(LEDBrightness, 'd'))
			iofun.out(" Configuration Byte (hex): " + format(rawflags,'X'))
			iofun.out(" Configuration Byte (binary): " + format(flags, 'd'))
			iofun.out(" Bit 0: 1 = Send Cleanup Report, 0 = Don't Send Cleanup Report")
			iofun.out(" Bit 1: 1 = Don't Read the Jumper, 0 = Read the Jumper")
			iofun.out(" Bit 2: 1 = Send Dry on Group 1 ON/Wet on Group 2 ON, 0 = Send both Dry and Wet on Group 1 (On=Dry and Off=Wet)")
			iofun.out(" Bit 3: 1 = Send Repeated Wet Commands, 0 = Don't Send Repeated Wet Commands")
			iofun.out(" Bit 4: 1 = Send Repeated Dry Commands, 0 = Don't Send Repeated Dry Commands")
			iofun.out(" Bit 5: 1 = LED does not blink on transmission, 0 = LED blinks on transmission")
			iofun.out(" Bit 6: 1 = Link to FF Group, 0 = Don't link to FF Group")
			iofun.out(" Bit 7: 1 = Programming lock on, 0 = Programming Lock off")
			iofun.out("\nCurrent Config Byte Setting:")
			iofun.out("\n\t" + cleanupreport + "\n\t" + readjumper + "\n\t" + wetdrygroups + "\n\t"+ wetrepeat + "\n\t" + dryrepeat + "\n\t" + ledonoff + "\n\t" + ffgrp + "\n\t" + plock)
			return 1
		else:
			iofun.out(self.label + " unexpected direct message: " + msg.toString())
		return 0
		iofun.out(self.label + " = " + format(tmp, '02d'))
		return 1

class LeakSensor(Device):
	"""==============  Insteon Leak Sensor ===============
	NOTE: 1) The sensor must be awake in order for you to read/write data from/to it.
	      2) Press and hold the set button until the LED begins to blink in order to put it into Link mode.
	         This is the best way to ensure it is awake.
		  3) After you are complete communicating with the sensor, tap the set button 2x until the LED stop blinking.
	      4) Use modem.startWatch() / modem.stopWatch() to see incoming messages
	      """

	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def getStatus(self):
		"""getStatus()
		Reads and diplays all of the device settings as well as current wet/dry status"""
		self.querier.setMsgHandler(StatusMsgHandler("\nLeak Sensor Status & Settings\n"))
		return self.querier.queryext(0x2e, 0x00, [0x00, 0x00, 0x00])

	def setLEDBrightness(self,value):
		"""setLEDBrightness()
		Sets the brightness of the motion LED to the decimal hex value provided. 0 or 0x00=off 255 or 0xFF=Full Bright. (0-255 or 0x00-0xFF)
		"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set LED Brightness\n"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x02, value]);

	def setConfigByte(self,value):
		"""setConfigByte()
		Sets the configuration Byte to the value provided, setting all flags at once. Can be provided in dec, hex or bin (0-255, 0x00-0xFF, or 0b00000000-0b11111111)
		"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Configuraiton Byte\n"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x05, value]);

