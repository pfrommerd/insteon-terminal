#-------------------------------------------------------------------------------
#
# Base class for all motion sensors
#
import iofun
import message
from device import Device
from querier import Querier
from querier import MsgHandler
from dbbuilder import LightDBBuilder
from linkdb import LightDBRecordFormatter
from us.pfrommer.insteon.cmd.msg import InsteonAddress

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

class MotionSensor(Device):
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = LightDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def ping(self):
		"""ping()
		pings device"""
		self.querier.setMsgHandler(DefaultMsgHandler("ping"))
		self.querier.querysd(0x0F, 0x01);
 
	def getStatus(self):
		"""getStatus()
		get current light level of device"""
		self.querier.setMsgHandler(StatusMsgHandler("light level"))
		self.querier.querysd(0x19, 0x0)
