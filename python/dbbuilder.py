#-------------------------------------------------------------------------------
#
# database builders shared by various devices
#

import iofun
import message

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

from threading import Timer
from threading import Condition


def out(msg = ""):
	iofun.out(msg)
def outchars(msg = ""):
	iofun.outchars(msg)

class DBBuilder(MsgListener):
	addr   = None
	timer  = None
	listener = None
	db     = None
	def __init__(self, addr, db):
		self.addr = addr
		self.db = db
	def setListener(self, l):
		self.listener = l;
	def clear(self):
		self.db.clear()
	def start(self):
		self.db.clear()
		iofun.addListener(self)
		msg = message.createExtendedMsg(InsteonAddress(self.addr), 0x2f, 0, [])
		msg.setByte("userData1", 0);
		msg.setByte("userData2", 0);
		msg.setByte("userData3", 0);
		msg.setByte("userData4", 0);
		msg.setByte("userData5", 0);
		iofun.writeMsg(msg)
		outchars("sent db query msg, incoming records: ")
		self.timer = Timer(20.0, self.giveUp)
		self.timer.start()
	def restartTimer(self):
		if self.timer:
			self.timer.cancel()
		self.timer = Timer(20.0, self.giveUp)
		self.timer.start()
	def giveUp(self):
		out("did not get full database, giving up!")
		iofun.removeListener(self)
		self.timer.cancel()
		if self.listener:
			self.listener.databaseIncomplete(self.db)
		self.listener = None
	def done(self):
		iofun.removeListener(self)
		if self.timer:
			self.timer.cancel()
		out("")
		out("----- database -------")
		self.printdb()
		out("----- end ------------")
		if self.listener:
			self.listener.databaseComplete(self.db)
		self.listener = None
	def printdb(self):
		self.db.dump()

	def msgReceived(self, msg):
		self.restartTimer()
		out("MUST IMPLEMENT msgReceived() method!!!")

class ThermostatDBBuilder(DBBuilder):
	def __init__(self, addr, db):
		self.addr = addr
		self.db = db
	def msgReceived(self, msg):
		self.restartTimer()
		if msg.isPureNack():
			#out("got pure NACK")
			return
		if msg.getByte("Cmd") == 0x62:
			#out("query msg acked!")
			return
		if msg.getByte("Cmd") == 0x50 and msg.getByte("command1") == 0x2F:
			#out("std reply received!")
			return
		elif msg.getByte("Cmd") == 0x51:
			off = (((msg.getByte("userData3") & 0xFF) << 8) |
				   (msg.getByte("userData4") & 0xFF))
			linkType = msg.getByte("userData6") & 0xFF
			group    = msg.getByte("userData7") & 0xFF
			linkAddr = InsteonAddress(msg.getByte("userData8") & 0xFF,
									  msg.getByte("userData9") & 0xFF,
									  msg.getByte("userData10") & 0xFF)
			data     = [msg.getByte("userData11") & 0xFF,
						msg.getByte("userData12") & 0xFF,
						msg.getByte("userData13") & 0xFF]

			if (self.db.hasOffset(off)):
				return
			rec = {"offset" : off, "addr": linkAddr, "type" : linkType,
				   "group" : group, "data" : data}
			self.db.addRecord(rec, False)
			#self.db.dumpRecord(rec, "got record: ");
			outchars(" " + format(self.db.getNumberOfRecords(), 'd'))
			if (linkType & 0x02 == 0): # has end-of-list marker
				self.done()
				return
		else:
			out("got unexpected msg: " + msg.toString())
	

class LightDBBuilder(DBBuilder):
	def __init__(self, addr, db):
		self.addr = addr
		self.db = db
	def msgReceived(self, msg):
		self.restartTimer()
		if msg.isPureNack():
#			out("got pure NACK")
			return
		if msg.getByte("Cmd") == 0x62:
#			out("query msg acked!")
			return
		elif msg.getByte("Cmd") == 0x50:
#			out("got ack of direct!")
			return
		elif msg.getByte("Cmd") == 0x51:
			off   = (msg.getByte("userData3") & 0xFF) << 8 | (msg.getByte("userData4") & 0xFF)
			rb    = msg.getBytes("userData6", 8); # ctrl + group + [data1,data2,data3] + whatever
			ltype = rb[0] & 0xFF
			group = rb[1] & 0xFF
			data  = rb[5:8]
			addr  = InsteonAddress(rb[2] & 0xff, rb[3] & 0xff, rb[4] & 0xff)
			rec   = {"offset" : off, "addr": addr, "type" : ltype,
					 "group" : group, "data" : data}
			self.db.addRecord(rec, False)
			outchars(" " + format(self.db.getNumberOfRecords(), 'd'))
			if (ltype & 0x02 == 0):
				# out("last record: " + msg.toString())
				self.done()
				return
		else:
			out("got unexpected msg: " + msg.toString())


class ModemDBBuilder(DBBuilder):
	condition = Condition()
	keepRunning = True
	def __init__(self, addr, db):
		self.addr = addr
		self.db = db
	def start(self):
		self.db.clear()
		self.keepRunning = True
		iofun.addListener(self)
		iofun.writeMsg(Msg.s_makeMessage("GetFirstALLLinkRecord"))

	def done(self):
		iofun.removeListener(self)
		self.condition.acquire()
		self.keepRunning = False
		self.condition.notify()
		self.condition.release()
		if self.listener:
			self.listener.databaseComplete(self.db)
		self.listener = None

	def wait(self):
		self.condition.acquire()
		while self.keepRunning:
			self.condition.wait()
		self.condition.release()

	def msgReceived(self, msg):
		if msg.isPureNack():
			return;
		if msg.getByte("Cmd") == 0x69 or msg.getByte("Cmd") == 0x6a :
			if msg.getByte("ACK/NACK") == 0x15:
				self.done()
		elif msg.getByte("Cmd") == 0x57:
			self.dbMsg(msg)
			iofun.writeMsg(Msg.s_makeMessage("GetNextALLLinkRecord"))
		else:
			out("got unexpected msg: " + msg.toString())

	def dbMsg(self, msg):
		recordFlags = msg.getByte("RecordFlags") & 0xff
		linkType    = recordFlags
		group       = msg.getByte("ALLLinkGroup") & 0xFF
		linkAddr    = msg.getAddress("LinkAddr")
		data        = [msg.getByte("LinkData1"), msg.getByte("LinkData2"),
					   msg.getByte("LinkData3")]
		self.db.addRecord({"offset" : 0, "addr": linkAddr,
						   "type" : linkType,
						   "group" : group, "data" : data})
	def dumpDB(self):
		self.db.dump()
	def saveDB(self, filename):
		self.db.save(filename)
	def loadDB(self, filename):
		self.db.load(filename);
	def nukeDB(self, modem):
		records = self.db.getRecordsAsArray()
		out("nuking " + format(len(records), 'd') + " records")
		for rec in records:
			modem.deleteFirstRecord(rec["addr"], rec["group"])
			time.sleep(1)
	def restoreDB(self, modem, filename):
		self.loadDB(filename)
		records = self.db.getRecordsAsArray()
		out("restoring " + format(len(records), 'd') + " records")
		for rec in records:
			modem.modifyFirstOrAdd(rec["addr"], rec["group"],
								   rec["type"], rec["data"])
			time.sleep(1)

