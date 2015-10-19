#-------------------------------------------------------------------------------
#
# Insteon IO linc 2450
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

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

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

class IOLinc2450(Device):
	"""==============  Insteon I/O Linc 2450 ==============="""
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def ping(self):
		"""ping()
		pings device"""
		self.querier.setMsgHandler(DefaultMsgHandler("ping"))
		self.querier.querysd(0x0F, 0x01);

#
# somebody should figure out how this thing works ... why not YOU?
#
