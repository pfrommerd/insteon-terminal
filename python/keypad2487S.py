#-------------------------------------------------------------------------------
#
# Insteon keypad 2487S
#

import iofun
import message

from device import Device
from querier import Querier
from querier import MsgHandler
from threading import Timer
from linkdb import *
from dbbuilder import LightDBBuilder

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
		out(self.label + " got msg: " + msg.toString())
		return 1

class ExtMsgHandler(MsgHandler):
	def __init__(self, n = "ExtMsgHandler"):
		self.name = n
	def processMsg(self, msg):
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out(self.name + " got unexpected msg: " + msg.toString())
			return 0
		if msg.isExtended():
			out(self.name + " got ext: " + msg.toString())
			return 1
		else:
			out(self.name + " got ack, waiting for ext msg!")
			return 0

class Flags1MsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		f = ""
		f +=  "Plock ON|"  if (tmp & (0x1 << 0)) else "Plock OFF|"
		f +=  "LED on TX ON|" if (tmp & (0x1 << 1)) else "LED on TX OFF|"
		f +=  "Resume Dim bit ON|" if (tmp & (0x1<<2)) else "Resum Dim bit OFF|"
		f +=  "LED OFF|" if (tmp & (0x1 << 4)) else "LED ON|"
		f +=  "KeyBeep ON|" if (tmp & (0x1 << 5)) else "KeyBeep OFF|"
		f +=  "RF Disable ON|" if (tmp & (0x1 << 6)) else "RF Disable OFF|"
		f +=  "Powerline Disable ON|" if (tmp & (0x1<<7)) else "Powerline Disable OFF"
		out(self.label + " got flags1: " + f);
		return 1

class Flags2MsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		out(self.label + " = " + format(tmp, '02d'))
		f = ""
		f +=  "TenD ON|"  if (tmp & (0x1 << 0)) else "TenD OFF|"
		f +=  "NX10Flag ON|" if (tmp & (0x1 << 1)) else "NX10Flag OFF|"
		f +=  "blinkOnError ON|" if (tmp & (0x1 << 2)) else "blinkOnError OFF|"
		f +=  "CleanupReport ON|" if (tmp & (0x1 << 3)) else "CleanupReport OFF|"
		f +=  "Detach Load ON|" if (tmp & (0x1 << 5)) else "Detach Load OFF|"
		f +=  "Smart Hops ON|" if (tmp & (0x1 << 6)) else "Smart Hops OFF"
		out(self.label + " got flags2: " + f);
		return 1

class StatusMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		out(self.label + " = " + format(tmp, '02d'))
		return 1

class CountMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		out(self.label + " = " + format(tmp, '02d'))
		return 1

class KPRecordFormatter(RecordFormatter):
	def __init__(self):
		pass
	def format(self, rec):
		dumpRecord(rec)


class Keypad2487S(Device):
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
		self.querier.querysd(0x0F, 0x01)

	def idrequest(self):
		self.querier.setMsgHandler(DefaultMsgHandler("id request"))
		self.querier.querysd(0x10, 0x00)

	def getext(self):
		self.querier.setMsgHandler(ExtMsgHandler("getext"))
		self.querier.queryext(0x2e, 0x00, [])


	def readFlags1(self):
		self.querier.setMsgHandler(Flags1MsgHandler("read flags1"))
		self.querier.querysd(0x1f, 0x01)

	def readFlags2(self):
		self.querier.setMsgHandler(Flags2MsgHandler("read flags2"))
		self.querier.querysd(0x1f, 0x05)

	def readCRCErrorCount(self):
		self.querier.setMsgHandler(CountMsgHandler("CRC error count"))
		self.querier.querysd(0x1f, 0x02)

	def readSNFailureCount(self):
		self.querier.setMsgHandler(CountMsgHandler("S/N failure count"))
		self.querier.querysd(0x1f, 0x03)

	def readDeltaFlag(self):
		self.querier.setMsgHandler(CountMsgHandler("database delta flag"))
		self.querier.querysd(0x1f, 0x01)

	def on(self, level=0xFF):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x11, level, -1))

	def onFast(self, level=0xFF):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x12, level, -1))

	def off(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x13, 0x00, -1))

	def offFast(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x14, 0x00, -1))

	def incrementalBright(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x15, 0x00, -1))

	def incrementalDim(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x16, 0x00, -1))

	def startManualChangeUp(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x17, 0x01, -1))

	def startManualChangeDown(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x17, 0x00, -1))

	def stopManualChange(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x18, 0x00, -1))

	def getStatus(self):
		self.querier.setMsgHandler(StatusMsgHandler("light level"))
		self.querier.querysd(0x19, 0x0)
	
	def beep(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x30, 0x00, -1))

	def setLEDBrightness(self, level):
		self.querier.setMsgHandler(ExtMsgHandler("set led level"))
		self.querier.queryext(0x2e, 00, [0x01, 0x07, level])

