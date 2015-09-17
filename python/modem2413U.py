#-------------------------------------------------------------------------------
#
# Insteon Modem 2414U
#
import commands
import time

from device import *
from linkdb import DB
from querier import Querier
from querier import MsgHandler

from dbbuilder import ModemDBBuilder

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

def out(msg = ""):
	commands.out(msg)

class DefaultMsgHandler(MsgHandler):
	def __init__(self, name):
		self.name = name
	def processMsg(self, msg):
		out(self.name + " got msg: " + msg.toString())
		return 1

class IMInfoMsgHandler(MsgHandler):
	def __init__(self, name):
		self.name = name
	def processMsg(self, msg):
		out(self.name + " got msg: " + msg.toString())
		return 1

class MsgDumper(MsgHandler):
	def __init__(self, name):
		self.name = name
	def processMsg(self, msg):
		out(self.name + " got msg: " + msg.toString())
		return 0 # return 0 to keep it running!

class Modem2413U(Device):
	dbbuilder = None
	querier = None
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = ModemDBBuilder(addr, self.db)
	def getdb(self):
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.dumpDB()
		out("Modem Link DB complete")
	def startWatch(self):
		self.querier = Querier(InsteonAddress("00.00.00"))
		self.querier.setMsgHandler(MsgDumper("modem"))
		self.querier.startWait(10000)
	def stopWatch(self):
		if (self.querier):
			self.querier.cancel()
	def getid(self):
		self.querier = Querier(InsteonAddress("00.00.00"))
		self.querier.setMsgHandler(IMInfoMsgHandler())
		msg = Msg.s_makeMessage("GetIMInfo")
		self.querier.sendMsg(msg)
	def linkAsController(self, otherDevice, group):
		addr = InsteonAddress(otherDevice)
		self.querier = Querier(addr)
		self.querier.setMsgHandler(DefaultMsgHandler("link as controller"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x01)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
	def linkAsResponder(self, otherDevice, group):
		addr = InsteonAddress(otherDevice)
		self.querier = Querier(addr)
		self.querier.setMsgHandler(DefaultMsgHandler("start linking"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x00)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
	def linkAsEither(self, otherDevice, group):
		addr = InsteonAddress(otherDevice)
		self.querier = Querier(addr)
		self.querier.setMsgHandler(
			DefaultMsgHandler("link/unlink as controller or responder"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x03)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
	def respondToUnlink(self, otherDevice, group):
		# could not get 0xFF to unlink
		self.linkAsEither(otherDevice, group)
	def unlinkAsController(self, otherDevice, group):
		addr = InsteonAddress(otherDevice)
		self.querier = Querier(addr)
		self.querier.setMsgHandler(DefaultMsgHandler("unlink as controller"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0xFF)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
	def cancelLinking(self):
		self.querier = Querier(InsteonAddress("00.00.00"))
		self.querier.setMsgHandler(DefaultMsgHandler("cancel linking"))
		msg = Msg.s_makeMessage("CancelALLLinking")
		self.querier.sendMsg(msg)
	def addResponder(self, addr, group):
		self.modifyRecord(addr, group, 0x41, 0xa2, [0,0,group], "addResponder")
	def addSoftwareResponder(self, addr):
		self.modifyRecord(addr, 0xef, 0x41, 0xa2, [0,0,0xef],
						  "addSoftwareController")
	def removeResponderOrController(self, addr, group):
		self.deleteFirstRecord(addr, group, "removeResponderOrController")
	def deleteFirstRecord(self, addr, group, text = "delete record"):
		self.modifyRecord(addr, group, 0x80, 0x00, [0,0,0], text)
	def modifyFirstOrAdd(self, addr, group, recordFlags, data):
		if (recordFlags & (1 << 6)): # controller
			self.modifyRecord(addr, group, 0x40, recordFlags,
							  data, "modify first or add")
		else:
			self.modifyRecord(addr, group, 0x41, recordFlags,
							  data, "modify first or add")
	def modifyFirstControllerOrAdd(self, addr, group, data):
		self.modifyRecord(addr, group, 0x40, 0xe2, data,
						  "modify first ctrl found or add")
	def modifyFirstResponderOrAdd(self, addr, group, data):
		self.modifyRecord(addr, group, 0x41, 0xa2, data,
						  "modify first resp found or add")
	def modifyRecord(self, addr, group, controlCode, recordFlags, data, txt):
		msg = Msg.s_makeMessage("ManageALLLinkRecord");
		msg.setByte("controlCode", controlCode); # mod. first ctrl found or add
		msg.setByte("recordFlags", recordFlags);
		msg.setByte("ALLLinkGroup", group);
		msg.setAddress("linkAddress", InsteonAddress(addr));
		msg.setByte("linkData1", data[0] & 0xFF)
		msg.setByte("linkData2", data[1] & 0xFF)
		msg.setByte("linkData3", data[2] & 0xFF)
		self.querier = Querier(self.address)
		self.querier.setMsgHandler(DefaultMsgHandler(txt))
		self.querier.sendMsg(msg)
	def saveDB(self, filename):
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.saveDB(filename)
	def loadDB(self, filename):
		self.dbbuilder.loadDB(filename)
		self.dbbuilder.dumpDB()
	def nukeDB(self):
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.nukeDB(self)
	def restoreDB(self, filename):
		self.loadDB(filename)
		self.dbbuilder.restoreDB(self, filename)
