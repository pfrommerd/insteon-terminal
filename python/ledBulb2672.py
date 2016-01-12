#-------------------------------------------------------------------------------
#
# Insteon led bulb 2672-222
#

import iofun
from linkdb import *

from querier import Querier
from querier import MsgHandler
from dimmer import Dimmer

from us.pfrommer.insteon.msg import Msg
from us.pfrommer.insteon.msg import MsgListener
from us.pfrommer.insteon.msg import InsteonAddress

def out(msg = ""):
	iofun.out(msg)

class DefaultMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		out(self.label + " got msg: " + msg.toString())
		return 1

class LEDBulb2672(Dimmer):
	"""==============  Insteon LED Bulb 2672 ==============="""
	def __init__(self, name, addr):
		Dimmer.__init__(self, name, addr)
