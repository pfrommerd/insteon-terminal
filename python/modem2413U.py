#-------------------------------------------------------------------------------
#
# Insteon Modem 2414U
#
import iofun
import time
import message

from device import *
from linkdb import DB
from querier import Querier
from querier import MsgHandler

from dbbuilder import ModemDBBuilder

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

def out(msg = ""):
	iofun.out(msg)

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
	"""==============  Insteon PowerLinc modem (PLM) ==============="""
	dbbuilder = None
	querier = None
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = ModemDBBuilder(addr, self.db)
	def getdb(self):
		"""getdb()
		download the modem database and print it on the console"""
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.dumpDB()
		out("Modem Link DB complete")
	def startWatch(self):
		"""startWatch()
		modem will print all incoming messages on terminal"""
		self.querier = Querier(InsteonAddress("00.00.00"))
		self.querier.setMsgHandler(MsgDumper("modem"))
		self.querier.startWait(10000)
	def stopWatch(self):
		"""stopWatch()
		stop modem from printing all incoming messages on terminal"""
		if (self.querier):
			self.querier.cancel()
	def getid(self):
		"""getid()
		get modem id data"""
		self.querier = Querier(InsteonAddress("00.00.00"))
		self.querier.setMsgHandler(IMInfoMsgHandler("getid"))
		msg = Msg.s_makeMessage("GetIMInfo")
		self.querier.sendMsg(msg)
	def sendOn(self, group):
		"""sendOn(group)
		sends ALLLink broadcast ON message to group "group" """
		msg = message.createStdMsg(InsteonAddress("00.00.00"), 0x0f,
									0x11, 0xFF, group)
		iofun.writeMsg(msg)
		iofun.out("sent msg: " + msg.toString())
	def sendOff(self, group):
		"""sendOff(group)
		sends ALLLink broadcast OFF message to group "group" """
		msg = message.createStdMsg(InsteonAddress("00.00.00"), 0x0f,
									0x13, 0xFF, group)
		iofun.writeMsg(msg)
		iofun.out("sent msg: " + msg.toString())

	def linkAsController(self, otherDevice, group):
		"""linkAsController(otherDevice, group)
		puts modem in link mode to control device "otherDevice" on group "group" """
		addr = InsteonAddress(otherDevice)
		self.querier = Querier(addr)
		self.querier.setMsgHandler(DefaultMsgHandler("link as controller"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x01)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
	def linkAsResponder(self, otherDevice, group):
		"""linkAsResponder(otherDevice, group)
		puts modem in link mode to respond to device "otherDevice" on group "group" """
		addr = InsteonAddress(otherDevice)
		self.querier = Querier(addr)
		self.querier.setMsgHandler(DefaultMsgHandler("start linking"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x00)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
	def linkAsEither(self, otherDevice, group):
		"""linkAsEither(otherDevice, group)
		puts modem in link mode to link as controller or responder to device "otherDevice" on group "group" """
		addr = InsteonAddress(otherDevice)
		self.querier = Querier(addr)
		self.querier.setMsgHandler(
			DefaultMsgHandler("link/unlink as controller or responder"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x03)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
	def respondToUnlink(self, otherDevice, group):
		"""respondToUnlink(otherDevice, group)
		make modem respond to unlink message from other device"""
		# could not get 0xFF to unlink
		self.linkAsEither(otherDevice, group)
	def unlinkAsController(self, otherDevice, group):
		"""unlinkAsController(otherDevice, group)
		puts modem in unlink mode to unlink as controller from device "otherDevice" on group "group" """
		addr = InsteonAddress(otherDevice)
		self.querier = Querier(addr)
		self.querier.setMsgHandler(DefaultMsgHandler("unlink as controller"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0xFF)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
	def cancelLinking(self):
		"""cancelLinking()
		takes modem out of linking or unlinking mode"""
		self.querier = Querier(InsteonAddress("00.00.00"))
		self.querier.setMsgHandler(DefaultMsgHandler("cancel linking"))
		msg = Msg.s_makeMessage("CancelALLLinking")
		self.querier.sendMsg(msg)
	def addController(self, addr, group):
		"""addController(addr, group):
		adds device with address "addr" to modem link database as controller for group "group" """
		self.__modifyRecord(addr, group, 0x40, 0xa2, [0,0,group], "addResponder")
	def addResponder(self, addr, group):
		"""addResponder(addr, group):
		adds device with address "addr" to modem link database as responder to group "group" """
		self.__modifyRecord(addr, group, 0x41, 0xa2, [0,0,group], "addResponder")
	def addSoftwareResponder(self, addr):
		"""addSoftwareResponder(addr):
		adds device with address "addr" to modem link database as software responder"""
		self.__modifyRecord(addr, 0xef, 0x41, 0xa2, [0,0,0xef],
						  "addSoftwareController")
	def removeResponderOrController(self, addr, group):
		"""removeResponderOrController(addr, group)
		removes device with address "addr" and group "group" from modem link database"""
		self.__deleteFirstRecord(addr, group, "removeResponderOrController")
	def __deleteFirstRecord(self, addr, group, text = "delete record"):
		self.__modifyRecord(addr, group, 0x80, 0x00, [0,0,0], text)
	def modifyFirstOrAdd(self, addr, group, recordFlags, data):
		if (recordFlags & (1 << 6)): # controller
			self.__modifyRecord(addr, group, 0x40, recordFlags,
							  data, "modify first or add")
		else:
			self.__modifyRecord(addr, group, 0x41, recordFlags,
							  data, "modify first or add")
	def modifyFirstControllerOrAdd(self, addr, group, data):
		self.__modifyRecord(addr, group, 0x40, 0xe2, data,
						  "modify first ctrl found or add")
	def modifyFirstResponderOrAdd(self, addr, group, data):
		self.__modifyRecord(addr, group, 0x41, 0xa2, data,
						  "modify first resp found or add")
	def __modifyRecord(self, addr, group, controlCode, recordFlags, data, txt):
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
		"""saveDB(filename)
		save modem database to file "filename" """
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.saveDB(filename)
	def loadDB(self, filename):
		"""loadDB(filename)
		restore modem database from file "filename" """
		self.dbbuilder.loadDB(filename)
		self.dbbuilder.dumpDB()
	def nukeDB(self):
		"""nukeDB()
		delete complete modem database! """
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.nukeDB(self)
	def restoreDB(self, filename):
		"""restoreDB()
		restore modem database from file "filename" """
		self.loadDB(filename)
		self.dbbuilder.restoreDB(self, filename)
