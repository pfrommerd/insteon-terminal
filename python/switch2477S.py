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
	querier = None
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = LightDBBuilder(addr, self.db)
		self.querier = Querier(addr)

	def getdb(self):
		out("getting db, be patient!")
		self.dbbuilder.clear()
		self.dbbuilder.start()

	def startLinking(self):
		self.querier.setMsgHandler(DefaultMsgHandler("start linking"))
		self.querier.querysd(0x09, 0x03);

	def ping(self):
		self.querier.setMsgHandler(DefaultMsgHandler("ping"))
		self.querier.querysd(0x0F, 0x01);
 
	def idrequest(self):
		self.querier.setMsgHandler(DefaultMsgHandler("id request"))
		self.querier.querysd(0x10, 0x00);

