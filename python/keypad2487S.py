#-------------------------------------------------------------------------------
#
# Insteon keypad 2487S
#

import iofun
import message

from switch import Switch
from querier import Querier
from querier import MsgHandler
from threading import Timer
from linkdb import *

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

def out(msg = ""):
	iofun.out(msg)
def outchars(msg = ""):
	iofun.outchars(msg)

class DefaultMsgHandler(MsgHandler):
	def __init__(self, name):
		MsgHandler.__init__(self, name)
	def processMsg(self, msg):
		out(self.name + " got msg: " + msg.toString())
		return 1


class ExtMsgHandler(MsgHandler):
	def __init__(self, name = "ExtMsgHandler"):
		MsgHandler.__init__(self, name)
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
	def __init__(self, name):
		MsgHandler.__init__(self, name)
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
		out(self.name + " got flags1: " + f);
		return 1

class Flags2MsgHandler(MsgHandler):
	def __init__(self, name):
		MsgHandler.__init__(self, name)
	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		out(self.name + " = " + format(tmp, '02d'))
		f = ""
		f +=  "TenD ON|"  if (tmp & (0x1 << 0)) else "TenD OFF|"
		f +=  "NX10Flag ON|" if (tmp & (0x1 << 1)) else "NX10Flag OFF|"
		f +=  "blinkOnError ON|" if (tmp & (0x1 << 2)) else "blinkOnError OFF|"
		f +=  "CleanupReport ON|" if (tmp & (0x1 << 3)) else "CleanupReport OFF|"
		f +=  "Detach Load ON|" if (tmp & (0x1 << 5)) else "Detach Load OFF|"
		f +=  "Smart Hops ON|" if (tmp & (0x1 << 6)) else "Smart Hops OFF"
		out(self.name + " got flags2: " + f);
		return 1

class CountMsgHandler(MsgHandler):
	def __init__(self, name):
		MsgHandler.__init__(self, name)
	def processMsg(self, msg):
		tmp = msg.getByte("command2") & 0xFF
		out(self.name + " = " + format(tmp, '02d'))
		return 1

class KPRecordFormatter(RecordFormatter):
	def __init__(self):
		pass
	def format(self, rec):
		dumpRecord(rec)


class Keypad2487S(Switch):
	"""==============  Insteon Keypad2487S ==============="""
	querier = None
	def __init__(self, name, addr):
		Switch.__init__(self, name, addr)

	def getext(self):
		self.querier.setMsgHandler(ExtMsgHandler("getext"))
		self.querier.queryext(0x2e, 0x00, [])

	def readFlags1(self):
		"""readFlags1()
		read plock/led/resum/beep etc flags"""
		self.querier.setMsgHandler(Flags1MsgHandler("read flags1"))
		self.querier.querysd(0x1f, 0x01)

	def readFlags2(self):
		"""readFlags2()
		read TenD/NX10/blinkOnError etc flags"""
		self.querier.setMsgHandler(Flags2MsgHandler("read flags2"))
		self.querier.querysd(0x1f, 0x05)

	def readCRCErrorCount(self):
		"""readCRCErrorCount()
		read CRC error counts"""
		self.querier.setMsgHandler(CountMsgHandler("CRC error count"))
		self.querier.querysd(0x1f, 0x02)

	def readSNFailureCount(self):
		"""readSNFailureCount()
		read SN failure counts """
		self.querier.setMsgHandler(CountMsgHandler("S/N failure count"))
		self.querier.querysd(0x1f, 0x03)

	def readDeltaFlag(self):
		"""readDeltaFlag()
		read database delta flag """
		self.querier.setMsgHandler(CountMsgHandler("database delta flag"))
		self.querier.querysd(0x1f, 0x01)

