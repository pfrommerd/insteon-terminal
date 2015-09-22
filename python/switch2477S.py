#-------------------------------------------------------------------------------
#
# Insteon switch 2477S
#
import iofun
import message

from device import Device
from querier import Querier
from querier import MsgHandler
from threading import Timer
from switch import Switch
from dbbuilder import LightDBBuilder
from linkdb import LightDBRecordFormatter
from linkdb import *

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

def out(msg = ""):
	iofun.out(msg)

class DefaultMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		out(self.label + " got msg: " + msg.toString())
		return 1

class Switch2477S(Switch):
	"""==============  Insteon SwitchLinc 2477S ==============="""
	querier = None
	def __init__(self, name, addr):
		Switch.__init__(self, name, addr)

	def readOpFlags(self):
		"""readOpFlags()
		read operational flags"""
		self.querier.setMsgHandler(DefaultMsgHandler("read op flags"))
		self.querier.querysd(0x1f, 0x00);

