#-------------------------------------------------------------------------------
#
# base class for all devices
#

from us.pfrommer.insteon.cmd.msg import InsteonAddress
from us.pfrommer.insteon.cmd.msg import Msg

from linkdb import DB
from dbbuilder import DBBuilder
from all_devices import *
import iofun
import time
from querier import Querier
from querier import MsgHandler


class IdMsgHandler(MsgHandler):
	def __init__(self, name):
		MsgHandler.__init__(self, name)
	def processMsg(self, msg):
		tmp = msg.getByte("command1") & 0xFF
		if msg.isAckOfDirect():
			iofun.out(self.name + " got ack!")
			return 0
		if  msg.isBroadcast() and tmp == 0x01:
			iofun.out(self.name + " got info: " + msg.toString())
			addr = msg.getAddress("toAddress");
			devCat, subCat, fwv = [addr.getHighByte(),
								   addr.getMiddleByte(), addr.getLowByte()]
			hwv = msg.getByte("command2") & 0xFF;
			iofun.out(self.name + " dev cat: " + format(devCat, '02x') +
				" subcat: " + format(subCat, '02x') +
				" firmware: " + format(fwv, '02x') +
				" hardware: " + format(hwv, '02x'))
			return 1
		return 0


class DBBuilderListener:
	dev = None
	def databaseComplete(self, db):
		iofun.out("databaseComplete() not implemented!")
	def databaseIncomplete(self, db):
		iofun.out("databaseIncomplete() not implemented!")

class LastRecordRemover(DBBuilderListener):
	def __init__(self, dev):
		self.dev = dev
	def databaseComplete(self, db):
		iofun.out("database complete, removing last record")
		above, stopaddr, below = db.findStopRecordAddresses()
		if (above == 0):
			iofun.out("db already empty!")
		else:
			self.dev.setRecord(above, InsteonAddress("00.00.00"),
									  0x00, 0x00, [0, 0, 0])
	def databaseIncomplete(self, db):
		iofun.out("database incomplete, reload() and retry!")

class LinkRecordRemover(DBBuilderListener):
	group = None
	data  = [0x03, 0x1f, 0xef]
	isController = True
	linkAddr = None
	def __init__(self, dev, linkAddr, g, isContr):
		self.dev = dev
		self.linkAddr = InsteonAddress(linkAddr)
		self.group = g;
		self.isController = isContr
	def databaseComplete(self, db):
		iofun.out("database complete, analyzing...")
		if not self.group:
			iofun.out("group to remove not set, aborting!")
			return
		if not self.linkAddr:
			iofun.out("address to remove not set, aborting!")
			return
		linkType = (1 << 6) if self.isController else 0
		linkType |= (1 << 1) # high water mark
		linkType |= (1 << 5) # unused bit, but seems to be always 1
		# linkType |= (1 << 7) # valid record
		searchRec = {"offset" : 0, "addr": self.linkAddr, "type" : linkType,
					 "group" : self.group, "data" : self.data}
		rec = db.findActiveRecord(searchRec);
		if not rec:
			iofun.out("no matching found record, no action taken!")
			return
		iofun.out("erasing active record at offset: " + format(rec["offset"], '04x'))
		self.dev.setRecord(rec["offset"], rec["addr"], rec["group"],
						   rec["type"] & 0x3f, rec["data"]);
	def databaseIncomplete(self, db):
		iofun.out("database incomplete, reload() and retry!")


class AddressReplacer(DBBuilderListener):
	oldAddr = None
	newAddr = None
	dev = None
	def __init__(self, dev, oldAddr, newAddr):
		self.dev = dev
		self.oldAddr = oldAddr
		self.newAddr = newAddr
	def databaseComplete(self, db):
		iofun.out("database complete, replacing...")
	def databaseIncomplete(self, db):
		iofun.out("database incomplete, retrying!")
		self.dev.dbbuilder.setListener(self)
		self.dev.getdb()

class LinkRecordAdder(DBBuilderListener):
	group = None
	data  = [0x03, 0x1f, 0xef]
	isController = True
	linkAddr = None
	isController = True
	def __init__(self, dev, linkAddr, g, d, isContr):
		self.dev = dev
		self.linkAddr = InsteonAddress(linkAddr)
		self.group = g
		self.data = d
		self.isController = isContr
	def addEmptyRecordAtEnd(self, db):
		above, stopaddr, below = db.findStopRecordAddresses()
		self.dev.setRecord(below, InsteonAddress("00.00.00"),
							 0x00, 0x00, [0, 0, 0])
		return stopaddr
	def databaseComplete(self, db):
		iofun.out("database complete, analyzing...")
		linkType = (1 << 6) if self.isController else 0
		linkType |= (1 << 1) # set high water mark
		linkType |= (1 << 5) # unused bit, but seems to be always 1
		linkType |= (1 << 7) # valid record
		searchRec = {"offset" : 0, "addr": self.linkAddr, "type" : linkType,
					 "group" : self.group, "data" : self.data}
		rec = db.findActiveRecord(searchRec)
		if rec:
			db.dumpRecord(rec, "found active record:");
			iofun.out("already linked, no action taken!")
			return
		searchRec["type"] = linkType;
		# match all but data
		rec = db.findInactiveRecord(searchRec, True, True, False)
		if not rec:
			# match address
			rec = db.findInactiveRecord(searchRec, True, False, False)
		if not rec:
			# match any unused record
			rec = db.findInactiveRecord(searchRec, False, False, False)
		if rec:
			db.dumpRecord(rec, "reusing inactive record:")
			self.dev.setRecord(rec["offset"], self.linkAddr,
								 self.group, linkType, self.data)
			iofun.out("link record added!")
		else:
			iofun.out("no unused records, adding one at the end!")
			newOffset = self.addEmptyRecordAtEnd(db)
			iofun.out("now setting the new record!")
			self.dev.setRecord(newOffset, self.linkAddr, self.group,
								 linkType, self.data)
	def databaseIncomplete(self, db):
		iofun.out("database incomplete, reload() and retry!")


class OnLevelModifier(DBBuilderListener):
	group = None
	data  = [0x03, 0x1f, 0xef]
	isController = True
	linkAddr = None
	isController = True
	def __init__(self, dev, linkAddr, g, level, ramprate, button, isContr):
		self.dev = dev
		self.linkAddr = InsteonAddress(linkAddr)
		self.group = g
		self.data = [level, ramprate, button]
		self.isController = isContr
	def addEmptyRecordAtEnd(self, db):
		above, stopaddr, below = db.findStopRecordAddresses()
		self.dev.setRecord(below, InsteonAddress("00.00.00"),
							 0x00, 0x00, [0, 0, 0])
		return stopaddr
	def databaseComplete(self, db):
		iofun.out("database complete, analyzing...")
		linkType = (1 << 6) if self.isController else 0
		linkType |= (1 << 1) # set high water mark
		linkType |= (1 << 5) # unused bit, but seems to be always 1
		linkType |= (1 << 7) # valid record
		searchRec = {"offset" : 0, "addr": self.linkAddr, "type" : linkType,
					 "group" : self.group, "data" : self.data}
		rec = db.findActiveRecord(searchRec)
		if rec:
			db.dumpRecord(rec, "found active record:");
			self.dev.setRecord(rec["offset"], rec["addr"], rec["group"],
								 rec["type"], self.data)
		else:
			iofun.out("no matching record found, check your data!")
			return
	def databaseIncomplete(self, db):
		iofun.out("database incomplete, reload() and retry!")

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
		searchRec = {"offset" : 0, "addr": self.linkAddr, "type" : linkType,
					 "group" : 0, "data" : [0,0,0]}
		records = db.findActiveRecords(searchRec, True, False, False);
		if not records:
			iofun.out("no matching record found, no action taken!")
			return
		iofun.out("found active records: ");
		for rec in records:
			db.dumpRecord(rec, "removing record: ")
			self.dev.setRecord(rec["offset"], rec["addr"], rec["group"],
							   rec["type"] & 0x3f, rec["data"]);
			time.sleep(5.0)

	def databaseIncomplete(self, db):
		iofun.out("database incomplete, reload() and retry!")


class LastNRecordRemover(DBBuilderListener):
	linkAddr = None
	numRecords = -1 # -1 means delete all records
	def __init__(self, dev, numRecords = -1):
		self.dev = dev
		self.numRecords = numRecords
	def databaseComplete(self, db):
		iofun.out("database complete, analyzing...")
		if not self.dev:
			iofun.out("no valid device set, aborting!")
			return
		linkType = 0
		searchRec = {"offset" : 0, "addr": InsteonAddress("00.00.00"),
					 "type" : linkType, "group" : 0, "data" : [0,0,0]}
		records = db.findAllRecords(searchRec, False, False, False)
		if not records:
			iofun.out("no matching record found, no action taken!")
			return
		iofun.out("found active records: ")
		i = 0
		for rec in reversed(records):
			if self.numRecords > 0 and i > self.numRecords: break
			db.dumpRecord(rec, " removing record:")
			self.dev.setRecord(rec["offset"], InsteonAddress("00.00.00"), 0,
								   0, [0, 0, 0]);
			time.sleep(5.0)
			i = i + 1

	def databaseIncomplete(self, db):
		iofun.out("database incomplete, reload() and retry!")


class Device:
	name = ""
	address   = InsteonAddress()
	db        = None
	dbbuilder = None
	querier   = None
	def __init__(self, name, addr):
		self.name = name
		self.address = addr
		self.db = DB()
		self.querier = Querier(addr)
		addDev(self)

	def modifyDB(self, listener):
		self.dbbuilder.setListener(listener)
		# after db download complete, listener will perform action
		self.getdb()

	def setRecord(self, offset, laddr, group, linkType, data):
		msg = self.makeMsg(offset, laddr, group, linkType,data)
		self.querier.setMsgHandler(MsgHandler("got set record"))
		self.querier.sendMsg(msg)

	def makeMsg(self, offset, laddr, group, linkType, data):
		msg   = Msg.s_makeMessage("SendExtendedMessage")
		msg.setAddress("toAddress", InsteonAddress(self.getAddress()))
		msg.setByte("messageFlags", 0x1f)
		msg.setByte("command1", 0x2f)
		msg.setByte("command2", 0x00)
		msg.setByte("userData1", 0x00) # don't care info
		msg.setByte("userData2", 0x02) # set database
		msg.setByte("userData3", offset >> 8)  # high byte
		msg.setByte("userData4", offset & 0xff) # low byte
		msg.setByte("userData5", 8)  # number of bytes set:  1...8
		msg.setByte("userData6", linkType)
		msg.setByte("userData7", group)
		msg.setByte("userData8", laddr.getHighByte())
		msg.setByte("userData9", laddr.getMiddleByte())
		msg.setByte("userData10", laddr.getLowByte())
		# depends on mode: could be e.g. trigger point
		msg.setByte("userData11", data[0])
		msg.setByte("userData12", data[1]) # unused?
		msg.setByte("userData13", data[2]) # unused?
		rb = msg.getBytes("command1", 15);
		checksum = (~sum(rb) + 1) & 0xFF
		msg.setByte("userData14", checksum)
		return msg

	def getName(self):
		return self.name

	def getAddress(self):
		return self.address

	def getdb(self):
		"""getdb()
		download the device database and print it on the console"""
		iofun.out("getting db, be patient!")
		self.dbbuilder.clear()
		self.dbbuilder.start()

	def printdb(self):
		"""printdb()
		print the downloaded link database to the console"""
		self.dbbuilder.printdb()

	def getId(self):
		"""getId()
		get category, subcategory, firmware, hardware version"""
		self.querier.setMsgHandler(IdMsgHandler("id"))
		self.querier.querysd(0x10, 0x00)


#
#   link database management
#
	def addController(self, addr, group, data = None):
		"""addController(addr, group, data)
		add device with "addr" as controller for group "group", with link data "data" """
		data = data if data else [00, 00, group];
		self.modifyDB(LinkRecordAdder(self, addr, group, data, True))
	def removeController(self, addr, group):
		"""removeController(addr, group)
		remove device with "addr" as controller for group "group", with link data "data" """
		self.modifyDB(LinkRecordRemover(self, addr, group, True))
	def addResponder(self, addr, group, data = None):
		"""addResponder(addr, group, data)
		add device with "addr" as responder for group "group", with link data "data" """
		data = data if data else [00, 00, group];
		self.modifyDB(LinkRecordAdder(self, addr, group, data, False))
	def removeResponder(self, addr, group):
		"""removeResponder(addr, group)
		remove device with "addr" as responder for group "group" """
		self.modifyDB(LinkRecordRemover(self, addr, group, False))
	def removeDevice(self, addr):
		"""removeDevice(addr):
		removes all links to device with address "addr" from device database"""
		self.modifyDB(DeviceRemover(self, addr))
	def replaceDevice(self, oldAddr, newAddr):
		"""replaceDevice(oldAddr, newAddr):
		replaces all linkdb occurrences of oldAddr with newAddr """
		self.dbbuilder.setListener(AddressReplacer(self, oldAddr, newAddr))
		# after db download is complete, listener will perform action
		self.getdb()
	def removeLastRecord(self):
		"""removeLastRecord()
		removes the last device in the link database"""
		self.modifyDB(LastRecordRemover(self))
	def nukeDB(self):
		"""nukeDB()
		really WIPES OUT all records in the device's database!"""
		self.modifyDB(LastNRecordRemover(self, -1))
	def setOnLevelResponder(self, addr, group, level, ramprate = 28, button = 1):
		"""setOnLevelResponder(addr, group, level, ramprate = 28, button = 1)
		sets (on level, ramp rate, button) for controller with "addr" and group "group" """
		self.modifyDB(OnLevelModifier(self, addr, group, level, ramprate, button, False))
