#-------------------------------------------------------------------------------
#
# Insteon smoke bridge
#

import iofun
import message

from device import Device
from switch import Switch
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

class ConfigMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		out("lock:             " + str(tmp & 0x01));
		out("led on/off on tx: " + str((tmp >> 1) & 0x01));
		out("led on/off:       " + str((tmp >> 4) & 0x01));
		out("heartbeat:        " + str((tmp >> 5) & 0x01));
		out("cleanup:          " + str((tmp >> 6) & 0x01));
		return 1

class SmokeBridge(Device):
	"""==============  Insteon SmokeBridge ==============="""
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def ping(self):
		"""ping()
		pings device"""
		self.querier.setMsgHandler(DefaultMsgHandler("ping"))
		self.querier.querysd(0x0F, 0x01);

	def beep(self):
		"""beep()
		make smoke bridge beep"""
		self.querier.setMsgHandler(DefaultMsgHandler("beep"))
		self.querier.querysd(0x30, 0x01);

	def readConfig(self):
		"""readConfig()
		reads configuration byte"""
		self.querier.setMsgHandler(ConfigMsgHandler("config"))
		self.querier.querysd(0x1F, 0x00);

	def programmingLockOn(self):
		"""programmingLockOn()
		locks programming mode"""
		self.querier.setMsgHandler(MsgHandler("got lock on return msg:"))
		self.querier.queryext(0x20,  0x00, [0x0, 0x0, 0x0])

	def programmingLockOff(self):
		"""programmingLockOff()
		unlocks programming mode"""
		self.querier.setMsgHandler(MsgHandler("got lock off return msg:"))
		self.querier.queryext(0x20,  0x01, [0x0, 0x0, 0x0])

	def heartbeatOn(self):
		"""heartbeatOn()
		switch on heartbeats"""
		self.querier.setMsgHandler(MsgHandler("heartbeat on return msg:"))
		self.querier.queryext(0x20,  0x06, [0x0, 0x0, 0x0])

