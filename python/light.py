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

class Light(Device):
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def ping(self):
		"""ping()
		pings device"""
		self.querier.setMsgHandler(DefaultMsgHandler("ping"))
		self.querier.querysd(0x0F, 0x01);
 
	def on(self, level=0xFF):
		"""on(level)
		switch on to given light level"""
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x11, level, -1))

	def rampRateOn(self, level=0xFF, rate = 0x1f):
		"""rampRateOn(level, rate)
		switch on to given light level (0-255) at given rate (0-31)"""
		cmd2 = (level & 0xf0) | ((rate & 0x1f) >> 1);
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x2e, cmd2, -1))

	def rampRateOff(self, rate = 0x1f):
		"""rampRateOff(rate)
		switch off at rate (0-31)"""
		cmd2 = (rate & 0x1f) >> 1
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x2f, cmd2, -1))

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
	

	def setLEDBrightness(self, level):
		"""setLEDBrightness(level)
		set brightness level from 0x11 -> 0x7f"""
		self.querier.setMsgHandler(DefaultMsgHandler("set led brightness"))
		self.querier.queryext(0x2e, 0x00, [0x01, 0x07, level]);
