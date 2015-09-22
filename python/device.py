#-------------------------------------------------------------------------------
#
# base class for all devices
#

from us.pfrommer.insteon.cmd.msg import InsteonAddress
from linkdb import DB
from dbbuilder import DBBuilder
from all_devices import *
import iofun
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


class Device:
	name = ""
	address   = InsteonAddress()
	db        = None
	dbbuilder = None
	def __init__(self, name, adr):
		self.name = name
		self.address = adr
		self.db = DB()
		addDev(self)

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
