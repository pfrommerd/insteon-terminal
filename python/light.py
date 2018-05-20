#-------------------------------------------------------------------------------
#
# Base class for all light type of devices (dimmers, switches ...)
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
		tmp = msg.getByte("command2") & 0xFF
		iofun.out(self.label + " = " + format(tmp, '02d'))
		return 1

class ExtStatusMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		if not msg.isExtended():
			if (msg.getByte("command1") == 0x2E):
				iofun.out(self.label + " got ack: " + msg.toString())
			else:
				iofun.out(self.label + " got unexpected: " + msg.toString())
			return 0 # still need to wait for ext message to come in
		# got an extended message
		iofun.out(self.label + " got " + msg.toString())
		#
		#

		iofun.out(self.label + " on  mask:               " +
				  '{0:08b}'.format(msg.getByte("userData3") & 0xFF))
		iofun.out(self.label + " off mask:               " +
				  '{0:08b}'.format(msg.getByte("userData4") & 0xFF))
		iofun.out(self.label + " non-toggle mask bits:   " +
				  '{0:08b}'.format(msg.getByte("userData10") & 0xFF))
		iofun.out(self.label + " LED status bits:        " +
				  '{0:08b}'.format(msg.getByte("userData11") & 0xFF))
		iofun.out(self.label + " X10 all bit mask:       " +
				  '{0:08b}'.format(msg.getByte("userData12") & 0xFF))
		iofun.out(self.label + " on/off bit mask:        " +
				  '{0:08b}'.format(msg.getByte("userData13") & 0xFF))
		iofun.out(self.label + " trigger group bit mask: " +
				  '{0:08b}'.format(msg.getByte("userData14") & 0xFF))
		iofun.out(self.label + " X10 house code: " +
				  format(msg.getByte("userData5") & 0xFF, '03x'))
		iofun.out(self.label + " X10 unit:       " +
				  format(msg.getByte("userData6") & 0xFF, '03x'))
		iofun.out(self.label + " ramp rate:      " +
				  format(msg.getByte("userData7") & 0xFF, '03d'))
		iofun.out(self.label + " on level:       " +
				  format(msg.getByte("userData8") & 0xFF, '03d'))
		iofun.out(self.label + " LED brightness: " +
				  format(msg.getByte("userData9") & 0xFF, '03d'))

		return 1

class Light(Device):
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def on(self, level=0xFF):
		"""on(level)
		switch on to given light level"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x11, level, -1))

	def setRampRateOn(self, level=0xFF, rate = 0x1f):
		"""setRampRateOn(level, rate)
		set future ramp rate and switch on to level (0-255) at rate (0-31)"""
		cmd2 = (level & 0xf0) | ((rate & 0x1f) >> 1);
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x2e, cmd2, -1))

	def setRampRateOff(self, rate = 0x1f):
		"""setRampRateOff(rate)
		set future ramp rate and switch off at rate (0-31)"""
		cmd2 = (rate & 0x1f) >> 1
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x2f, cmd2, -1))

	def fastOn(self, level):
		"""fastOn(level)
		switch immediately to level"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x12, level, -1))

	def fastOff(self):
		"""fastOff()
		switch off immediately"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x14, 0, -1))

	def instantOn(self, level):
		"""instantOn(level)
		switch on instantly to level"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x21, level, -1))

	def instantOff(self):
		"""instantOff()
		switch off instantly"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x21, 0, -1))

	def off(self):
		"""off()
		switch off"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x13, 0x00, -1))

	def beep(self):
		"""beep()
		make device beep"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x30, 0x00, -1))

	def getStatus(self):
		"""getStatus()
		get current light level of device"""
		self.querier.setMsgHandler(StatusMsgHandler("light level"))
		self.querier.querysd(0x19, 0x0)
	
	def getExtStatus(self):
		"""getExtStatus()
		get extended status of device"""
		self.querier.setMsgHandler(ExtStatusMsgHandler("ext status"))
		self.querier.queryext(0x2e, 0x00, [0, 0, 0]);


	def setLEDBrightness(self, level):
		"""setLEDBrightness(level)
		set brightness level from 0x11 -> 0x7f"""
		self.querier.setMsgHandler(DefaultMsgHandler("set led brightness"))
		self.querier.queryext(0x2e, 0x00, [0x01, 0x07, level]);
