#-------------------------------------------------------------------------------
#
# Insteon Modem 2448A7
#

import iofun
import time
import message

from device import *
from linkdb import DB
from querier import Querier
from querier import MsgHandler

from dbbuilder import ModemDBBuilder

from us.pfrommer.insteon.msg import Msg
from us.pfrommer.insteon.msg import MsgListener
from us.pfrommer.insteon.msg import InsteonAddress

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

class IMConfigMsgHandler(MsgHandler):
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

class DeviceRemover(DBBuilderListener):
	linkAddr = None
	def __init__(self, dev, linkAddr):
		self.dev = dev
		self.linkAddr = InsteonAddress(linkAddr)
	def databaseComplete(self, db):
		iofun.out("database complete, analyzing...")
		if not self.linkAddr:
			iofun.out("address to remove not set, aborting!")
			return
		if not self.dev:
			iofun.out("no valid device set, aborting!")
			return
			
		linkType = 0
		linkType |= (1 << 1) # high water mark
		linkType |= (1 << 5) # unused bit, but seems to be always 1
		searchRec = {"offset" : 0, "addr": self.linkAddr, "type" : linkType,
					 "group" : 0, "data" : [0,0,0]}
		iofun.out("database has " + format(db.getNumberOfRecords(), 'd') + " records");
		records = db.findActiveRecords(searchRec, True, False, False);
		if not records:
			iofun.out("no matching record found, no action taken!")
			return
		iofun.out("found active " + format(len(records), 'd') +  " records.");
		for rec in records:
			self.dev.modifyRecord(rec["addr"], rec["group"],
								  0x80, 0x00, [0,0,0], "remove record")
			time.sleep(5.0)

	def databaseIncomplete(self, db):
		iofun.out("database incomplete, reload() and retry!")


class Modem2448A7(Device):
	"""==============  Insteon PowerLinc modem (PLM) ==============="""
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = ModemDBBuilder(addr, self.db)
	def __modifyModemDB(self, listener):
		self.dbbuilder.setListener(listener)
		# after db download complete, listener will perform action
		iofun.out("getting db, be patient!")
		self.dbbuilder.clear()
		self.dbbuilder.start()

	def getdb(self):
		"""getdb()
		download the modem database and print it on the console"""
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.dumpDB()
		out("Modem Link DB complete")
	def readdb(self):
		"""readdb()
		download the modem database and return it"""
		self.dbbuilder.start()
		self.dbbuilder.wait()
		out("Modem Link DB complete!")
		return self.dbbuilder.getdb()
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
	def getIMConfig(self):
		"""getIMConfig()
		get modem configuration flags byte"""
		self.querier = Querier(InsteonAddress("00.00.00"))
		self.querier.setMsgHandler(IMConfigMsgHandler("getIMConfig"))
		msg = Msg.s_makeMessage("GetIMConfig")
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

	def linkAsController(self, group):
		"""linkAsController(group)
		puts modem in link mode on group "group" """
		self.querier.setMsgHandler(DefaultMsgHandler("link as controller"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x01)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
		
	def linkAsResponder(self, group):
		"""linkAsResponder(group)
		puts modem in link mode on group "group" """
		self.querier.setMsgHandler(DefaultMsgHandler("start linking"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x00)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
		
	def linkAsEither(self, group):
		"""linkAsEither(group)
		puts modem in link mode to link as controller or responder on group "group" """
		self.querier.setMsgHandler(
			DefaultMsgHandler("link/unlink as controller or responder"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0x03)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
		
	def respondToUnlink(self, group):
		"""respondToUnlink(group)
		make modem respond to unlink message"""
		# could not get 0xFF to unlink
		self.linkAsEither(group)

	def unlinkAsController(self, group):
		"""unlinkAsController(group)
		puts modem in unlink mode to unlink as controller on group "group" """
		self.querier.setMsgHandler(DefaultMsgHandler("unlink as controller"))
		msg = Msg.s_makeMessage("StartALLLinking")
		msg.setByte("LinkCode", 0xFF)
		msg.setByte("ALLLinkGroup", group)
		self.querier.sendMsg(msg)
		
	def cancelLinking(self):
		"""cancelLinking()
		takes modem out of linking or unlinking mode"""
		self.querier.setMsgHandler(DefaultMsgHandler("cancel linking"))
		msg = Msg.s_makeMessage("CancelALLLinking")
		self.querier.sendMsg(msg)
		
	def addController(self, addr, group):
		"""addController(addr, group):
		adds device with address "addr" to modem link database as controller for group "group" """
		self.modifyRecord(addr, group, 0x40, 0xa2, [0,0,group], "addController")
		
	def addResponder(self, addr, group, data = None):
		"""addResponder(addr, group[, data]):
		adds device with address "addr" to modem link database as responder to group "group" """
		data = data if data else [00, 00, group];
		self.modifyRecord(addr, group, 0x41, 0xa2, data, "addResponder")
		
	def addSoftwareResponder(self, addr):
		"""addSoftwareResponder(addr):
		adds device with address "addr" to modem link database as software responder"""
		self.modifyRecord(addr, 0xef, 0x41, 0xa2, [0,0,0xef],
						  "addSoftwareController")
		
	def removeResponderOrController(self, addr, group):
		"""removeResponderOrController(addr, group)
		removes device with address "addr" and group "group" from modem link database"""
		self.__deleteFirstRecord(addr, group, "removeResponderOrController")
		
	def removeResponder(self, addr, group):
		"""removeResponder(addr, group)
		could not be implemented for the modem. Use removeResponderOrController() instead!"""
		iofun.out("removeResponder(addr, group) could not be implemented" +
				  " for the modem. Use removeResponderOrController() instead!")
		
	def removeController(self, addr, group):
		"""removeController(addr, group)
		could not be implemented for the modem. Use removeResponderOrController() instead!"""
		iofun.out("removeController(addr, group) could not be implemented" +
				  " for the modem. Use removeResponderOrController() instead!")
		
	def removeDevice(self, addr):
		"""removeDevice(addr):
		removes all links to device with address "addr" from modem database"""
		self.__modifyModemDB(DeviceRemover(self, addr))
		
	def __deleteFirstRecord(self, addr, group, text = "delete record"):
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
		msg = self.__makeModMsg(addr, group, controlCode, recordFlags, data, txt)
		self.querier = Querier(self.address)
		self.querier.setMsgHandler(DefaultMsgHandler(txt))
		self.querier.sendMsg(msg)
		
	def __makeModMsg(self, addr, group, controlCode, recordFlags, data, txt):
		msg = Msg.s_makeMessage("ManageALLLinkRecord");
		msg.setByte("controlCode", controlCode); # mod. first ctrl found or add
		msg.setByte("recordFlags", recordFlags);
		msg.setByte("ALLLinkGroup", group);
		msg.setAddress("linkAddress", InsteonAddress(addr));
		msg.setByte("linkData1", data[0] & 0xFF)
		msg.setByte("linkData2", data[1] & 0xFF)
		msg.setByte("linkData3", data[2] & 0xFF)
		return msg;
	
	def saveDB(self, filename):
		"""saveDB(filename)
		save modem database to file "filename" """
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.saveDB(filename)
		
	def loadDB(self, filename):
		"""loadDB(filename)
		load modem database from file "filename" (note: this will not change the actual modem db) """
		self.dbbuilder.loadDB(filename)
		self.dbbuilder.dumpDB()
		
	def nukeDB(self):
		"""nukeDB()
		delete complete modem database! """
		self.dbbuilder.start()
		self.dbbuilder.wait()
		self.dbbuilder.nukeDB(self)
		
	def restoreDB(self, filename):
		"""restoreDB(filename)
		restore modem database from file "filename" """
		self.loadDB(filename)
		self.dbbuilder.restoreDB(self, filename)

