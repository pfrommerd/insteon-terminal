#-------------------------------------------------------------------------------
#
# class for querying devices
#

import iofun
import message

from java.lang import System
from threading import Timer
from threading import Condition

from us.pfrommer.insteon.msg import Msg
from us.pfrommer.insteon.msg import MsgListener
from us.pfrommer.insteon.msg import InsteonAddress


def out(msg = ""):
	iofun.out(msg)

class MsgHandler:
	name = "MsgHandler"
	def __init__(self, name = "MsgHandler"):
		self.name = name
	def __del__(self):
		# for debugging
		pass
	def processMsg(self, msg):
		out(self.name + ": " + msg.toString())
		return 1
	def gotAck(self):
#        out(self.name + " got ack!")
		return 1
	def gotNoReply(self):
		out(self.name + " got no reply!")
		return 1


class Querier(MsgListener):
	addr   = None
	timer  = None
	msgHandler = None
	condition = Condition()
	gotReply = False
	def __init__(self, addr):
		self.addr = addr
	def setMsgHandler(self, handler):
		self.msgHandler = handler
	def sendMsg(self, msg):
		self.started()
		iofun.addListener(self)
		if self.timer:
			self.timer.cancel()
		self.timer = Timer(5.0, self.giveUp)
		self.timer.start()
		iofun.writeMsg(msg)
		out("sent msg: " + msg.toString())
		# out("started timer!")
		
	def startWait(self, time):
		iofun.addListener(self)
		if self.timer:
			self.timer.cancel()
		self.timer = Timer(time, self.giveUp)
		self.timer.start()

	def waitForReply(self, timeout):
		self.condition.acquire()
		self.condition.wait(timeout)
		gotReply = self.gotReply
		self.condition.release()
		return gotReply

	def cancel(self):
		# out("querier timer canceled")
		iofun.removeListener(self)
		if self.timer:
			self.timer.cancel()
		self.timer = None
		self.complete(False)
	def queryext(self, cmd1, cmd2, data):
		msg = message.createExtendedMsg(InsteonAddress(self.addr),
										 cmd1, cmd2, data)
		self.sendMsg(msg);
		return msg;
	def queryext2(self, cmd1, cmd2, data):
		msg = message.createExtendedMsg2(InsteonAddress(self.addr),
										  cmd1, cmd2, data)
		self.sendMsg(msg);
		return msg;
	def querysd(self, cmd1, cmd2, group = -1):
		msg = message.createStdMsg(InsteonAddress(self.addr), 0x0f,
									cmd1, cmd2, group)
		self.sendMsg(msg);
		return msg;
	def giveUp(self):
		self.msgHandler.gotNoReply()
		#                out("did not get response, giving up!")
		iofun.removeListener(self)
		self.timer.cancel()
		self.complete(False)
	def done(self):
		iofun.removeListener(self)
		if self.timer:
			self.timer.cancel()
		self.complete(True)
	def complete(self, gotReply):
		self.condition.acquire()
		self.gotReply = gotReply
		self.condition.notify()
		self.condition.release()
	def started(self):
		self.condition.acquire()
		self.gotReply = False
		self.condition.release()


	def msgReceived(self, msg):
		if msg.isPureNack():
			# out("got pure NACK")
			return
		if msg.getByte("Cmd") == 0x62:
			if (self.msgHandler):
				self.msgHandler.gotAck()
				return
		if (self.msgHandler):
			if self.msgHandler.processMsg(msg):
				self.done()
		else:
			out("got reply msg: " + msg.toString())
			self.done()

