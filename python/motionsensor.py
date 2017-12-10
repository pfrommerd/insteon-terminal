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
			rawmotioncountdown = msg.getByte("userData4") & 0xFF
			motioncountdownsec = (rawmotioncountdown + 1) * 30
			rawlightsensitivity = msg.getByte("userData5") & 0xFF
			rawflags = msg.getByte("userData6") & 0xFF
			flags = bin(msg.getByte("userData6") & 0xFF)[2:].zfill(8)
			light = msg.getByte("userData11") & 0xFF
			battery = msg.getByte("userData12") & 0xFF
			# Bit 0
			if (rawflags & 0b00000001 == 1):
				cleanupreport = "Unknown"
			else:
				cleanupreport = "Unknown"
			# Bit 1
			if (rawflags & 0b00000010 == 2):
				onoffmode = "Send on and after timeout send off"
			else:
				onoffmode = "Only sends on commands"
			# Bit 2
			if (rawflags & 0b00000100 == 4):
				daynightmode = "Send commands at day and night"
			else:
				daynightmode = "Sends comands only when dark is sensed (as set by light/dark threshold)"
			# Bit 3
			if (rawflags & 0b00001000 == 8):
				ledonoff = "LED blinks when motion is detected at brightness set by LED Brightness"
			else:
				ledonoff = "LED does not blink with motion"
			# Bit 4
			if (rawflags & 0b00010000 == 16):
				occmode = "Sends repeated On commands whenever motion is detected"
			else:
				occmode = "Sends only 1 On command until timeout set by Motion Countdown time"
			# Bit 5
			if (rawflags & 0b00100000 == 32):
				unk1 = "Unknown"
			else:
				unk1 = "Unknown"
			# Bit 6
			if (rawflags & 0b01000000 == 64):
				ffgrp = "Unknown"
			else:
				ffgrp = "Unknown"
			# Bit 7
			if (rawflags & 0b10000000 == 128):
				plock = "Unknown"
			else:
				plock = "Unknown"

			iofun.out(self.label + " LED Brightness (if flag set on): " + format(LEDBrightness, 'd'))
			iofun.out(" Light level: " + format(light, 'd') + " Light/Dark threshold: " + format(rawlightsensitivity, 'd'))
			iofun.out(" Battery level: " + format(battery, 'd'))
			iofun.out(" Motion Countdown Set Value: " + format(rawmotioncountdown, 'd'))
			iofun.out(" Motion Countdown Time: " + format(motioncountdownsec, 'd') + "seconds")
			iofun.out(" Configuration Byte (hex): " + format(rawflags,'X'))
			iofun.out(" Configuration Byte (binary): " + format(flags, 'd'))
			iofun.out(" Bit 0: Unknown")
			iofun.out(" Bit 1: 1 = On/Off Mode, 0 = On Only Mode")
			iofun.out(" Bit 2: 1 = Day/Night Mode, 0 = Night Only Mode")
			iofun.out(" Bit 3: 1 = Motion LED on, 0 = Motion LED Off")
			iofun.out(" Bit 4: 1 = Occupancy Mode on, 0 = Occupancy Mode Off")
			iofun.out(" Bit 5: Unknown")
			iofun.out(" Bit 6: Unknown")
			iofun.out(" Bit 7: Unknown")
			iofun.out("\nCurrent Config Byte Setting:")
			iofun.out("\n\t" + cleanupreport + "\n\t" + onoffmode + "\n\t" + daynightmode + "\n\t"+ ledonoff + "\n\t" + occmode + "\n\t" + unk1 + "\n\t" + ffgrp + "\n\t" + plock)
			return 1
		else:
			iofun.out(self.label + " unexpected direct message: " + msg.toString())
		return 0
		iofun.out(self.label + " = " + format(tmp, '02d'))
		return 1

class MotionSensor(Device):
	"""==============  Insteon Motion Sensor ===============
	NOTE: 1) The sensor must be awake in order for you to read/write data from/to it.
	      2) Press and hold the set button until the motion LED begins to blink in order to put it into Link mode.
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
		Reads and diplays all of the device settings as well as current open/closed status"""
		self.querier.setMsgHandler(StatusMsgHandler("\nMotion Detector Status & Settings\n"))
		return self.querier.queryext(0x2E, 0x00, [0x00, 0x00, 0x00])

	def setLEDBrightness(self,value):
		"""setLEDBrightness()
		Sets the brightness of the motion LED to the decimal or hex value provided. 0x00=off 0xFF=Full Bright. (0-255 or 0x00-0xFF)
		"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set LED Brightness\n"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x02, value]);

	def setMotionCountdown(self,value):
		"""setMotionCountdown()
		Sets the motion countdown to the decimal or hex value provided in 30 sec increments. 0x00 = 30 seconds (0-255 or 0x00-0xFF)
		"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Motion Countdown\n"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x03, value]);

	def setLightSense(self,value):
		"""setLightSense()
		Sets the light/dark threshold to decimal or hex value provided. (0-255 or 0x00-0xff)
		"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set light/dark threshold\n"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x04, value]);

	def setConfigByte(self,value):
		"""setConfigByte()
		Sets the configuration Byte to the value provided, setting all flags at once. Can be provided in dec, hex or bin (0-255, 0x00-0xFF, or 0b00000000-0b11111111)
		"""
		self.querier.setMsgHandler(DefaultMsgHandler("Set Configuraiton Byte\n"))
		return self.querier.queryext(0x2E, 0x00, [0x01, 0x05, value]);

