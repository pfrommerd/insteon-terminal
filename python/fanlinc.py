#-------------------------------------------------------------------------------
#
# Insteon fanlinc
#

import iofun
import message

from dimmer import Dimmer
from querier import Querier
from querier import MsgHandler
from threading import Timer
from linkdb import *
from device import LinkRecordAdder
from dbbuilder import GenericDBBuilder
from linkdb import LightDBRecordFormatter

from us.pfrommer.insteon.msg import Msg
from us.pfrommer.insteon.msg import MsgListener
from us.pfrommer.insteon.msg import InsteonAddress

def out(msg = ""):
	iofun.out(msg)
def outchars(msg = ""):
	iofun.outchars(msg)

class DefaultMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		iofun.out(self.label + " got msg: " + msg.toString())
		return 1

class FanStatusMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
                if (tmp == 0):
                    speed = "off"
                elif (tmp < 0x80):
                    speed = "low"
                elif (tmp < 0xff):
                    speed = "med"
                else:
                    speed = "high"
		iofun.out(self.label + " = " + speed + " ("
                                     + format(tmp, '02x') + ")")
		return 1

class FanLinc(Dimmer):
	"""==============  Insteon FanLinc ==============="""
	def __init__(self, name, addr):
		Dimmer.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def getSpeed(self):
		"""getSpeed()
		get current fan speed"""
		self.querier.setMsgHandler(FanStatusMsgHandler("fan speed"))
		self.querier.querysd(0x19, 0x03)

        def setSpeed(self, speed = "off"):
		"""setSpeed(speed = "off")
		set fan speed (off, low, med, high)"""
                if (speed == "off"):
                    tmp = 0x00
                elif (speed == "low"):
                    tmp = 0x55
                elif (speed == "med"):
                    tmp = 0xaa
                elif (speed == "high"):
                    tmp = 0xff
                else:
                    out("invalid speed")
                    tmp = 0x00
		self.querier.setMsgHandler(DefaultMsgHandler("fan speed"))
		self.querier.queryext(0x11, tmp, [2, 0 ,0])

#
# The fanlinc device has lots of other features, none of it implemented
# yet. This is where *you* come in...
#
