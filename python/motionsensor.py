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
			light = msg.getByte("userData11") & 0xFF
			battery = msg.getByte("userData12") & 0xFF
			iofun.out(self.label + " light level: " + format(light, 'd') +
					  " battery level: " + format(battery, 'd')) 
			return 1
		else:
			iofun.out(self.label + " unexpected direct message: " + msg.toString())
		return 0
		iofun.out(self.label + " = " + format(tmp, '02d'))
		return 1

class MotionSensor(Device):
	"""==============  Insteon Motion Sensor ===============
	   NOTE: 1) none of the database management commands works!
	         2) only getStatus() has been tested, and even that one is hit and miss
	         3) use modem.startWatch() / modem.stopWatch() to see incoming messages"""
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def getStatus(self):
		"""getStatus()
		YOU MUST PRESS THE SENSOR BUTTON SHORTLY BEFORE SO IT'S ALIVE. TRY SEVERAL TIMES!"""
		self.querier.setMsgHandler(StatusMsgHandler("status"))
		return self.querier.queryext(0x2e, 0x0, [0,0,0])

