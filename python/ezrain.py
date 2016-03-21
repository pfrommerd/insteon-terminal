#-------------------------------------------------------------------------------
#
# Insteon EZRain V1 #5010A
#

import iofun
import message
import time

from device import Device
from switch import Switch
from querier import Querier
from querier import MsgHandler
from threading import Timer
from linkdb import *
from device import LinkRecordAdder
from dbbuilder import GenericDBBuilder
from linkdb import LightDBRecordFormatter

from us.pfrommer.insteon.msg import Msg
from us.pfrommer.insteon.msg import MsgListener
from us.pfrommer.insteon.msg import InsteonAddress

# EZRAIN Standard Commands
GET_PRODUCT_KEY = 0x03
PING            = 0x0F
VALVE_ON        = 0x40
VALVE_OFF       = 0x41
PROGRAM_ON      = 0x42
PROGRAM_OFF     = 0x43
CONTROL         = 0x44
GET_TIMERS      = 0x45

# CONTROL SUB-COMMANDS
RESET           = 0x00
LOAD_EEPROM     = 0x01
GET_STATUS      = 0x02
DISABLE_CMD     = 0x03
ENABLE_CMD      = 0x04
SKIP_FORWARD    = 0x05
SKIP_BACK       = 0x06
ENABLE_PUMP     = 0x07
DISABLE_PUMP    = 0x08
ENABLE_CHG_MSG  = 0x09
DISABLE_CHG_MSG = 0x0A
LOAD_RAM        = 0x0B

# EZRAIN Extended Commands
SET_TIMERS      = 0x40
GET_RESPONSE    = 0x41

# EZRAIN STATUS WORD MASKS
VALVES_MASK  = 0x07
PROGRAM_MASK = 0x18
RUNNING_MASK = 0x20
PUMP_MASK    = 0x40
ON_MASK      = 0x80

def out(msg = ""):
	iofun.out(msg)
def outchars(msg = ""):
	iofun.outchars(msg)

class DefaultMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		iofun.out(time.strftime("%H:%M:%S") + ": " + self.label + " got msg: " + msg.toString())
		return 1

class EZRainStatusMsgHandler(MsgHandler):
    def __init__(self, n="EZRainStatusMsgHandler"):
        self.name = n
    def processMsg(self, msg):
        out(time.strftime("%H:%M:%S") + ": " + self.name + " got: " + msg.toString())
        status_cmds = [ VALVE_ON, VALVE_OFF, GET_STATUS, CONTROL ]
        cmd1 = msg.getByte("command1") & 0xFF
        if (False == (cmd1 in status_cmds)):
            out(time.strftime("%H:%M:%S") + ": " + self.name + "got unexpected msg!")
            return 0
        else:
             status  = msg.getByte("command2") & 0xFF
             valves  = status & VALVES_MASK
             program = status & PROGRAM_MASK
             running = status & RUNNING_MASK
             pump    = status & PUMP_MASK
             on      = status & ON_MASK
             out("EZRain response status(0x" + format(status, '02x')+")");
             out("\tactive valve             = " + format(valves,  'd'))
             out("\tactive program           = " + format(program, 'd'))
             out("%s%s" % ("\tprogram sequence running = ", (running == RUNNING_MASK)))
             out("%s%s" % ("\tV8 pump control          = ", (pump == PUMP_MASK)))
             out("%s%s" % ("\tactive valve is on       = ", (on == ON_MASK)))
             return 1

class productKeyResponseMsgHandler(MsgHandler):
    def __init__(self, n="ProductKeyResponseMsgHandler"):
        self.name = n
    def processMsg(self,msg):
        out(time.strftime("%H:%M:%S") + ": " + self.name + " got: " + msg.toString())
        if msg.isExtended():
            out("message is extended")
            d4  = msg.getByte("userData4") & 0xFF
            d5 = msg.getByte("userData5") & 0xFF
            d6 = msg.getByte("userData6") & 0xFF
            d7 = msg.getByte("userData7") & 0xFF
            d8 = msg.getByte("userData8") & 0xFF
            d9 = msg.getByte("userData9") & 0xFF
            d10 = msg.getByte("userData10") & 0xFF
            d11 = msg.getByte("userData11") & 0xFF
            d12 = msg.getByte("userData12") & 0xFF
            out("d4:      "   + format(d4,  'd'))
            out("d5:      "   + format(d5,  'd'))
            out("d6:      "   + format(d6,  'd'))
            out("d7:      "   + format(d7,  'd'))
            out("d8:      "   + format(d8,  'd'))
            out("d9:      "   + format(d9,  'd'))
            out("d10:     "   + format(d10, 'd'))
            out("d11:     "   + format(d11, 'd'))
            out("d12:     "   + format(d12, 'd'))
            return 1
        else:
            out("message is not extended")
            return 0

class EZRain(Device):
	"""==============  EZRain  ==============="""
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = GenericDBBuilder(addr, self.db)
		self.db.setRecordFormatter(LightDBRecordFormatter())

	def ping(self):
		"""ping()
		pings device"""
		self.querier.setMsgHandler(DefaultMsgHandler("ping"))
		self.querier.querysd(PING, 0x01)

	def reset(self):
		"""reset()
        reset to factory defaults
        """
		self.querier.setMsgHandler(DefaultMsgHandler("reset"))
		self.querier.querysd(CONTROL, RESET)

	def getPKey(self):
		"""getPKey
		get the EZRain Product Key
        The EZRain is supposed to reply with an extended length Product Key 
        Response message but it does not work. I just get an ACK. 
        According to http://www.madreporite.com/insteon/commands.htm, a Product
        Key Response has cmd1 = 0x03, cmd2 = 0x00 and the data looks like this:
        Extended Data as follows: D1: 0x00, D2-D4: Product Key, 
                                  D5: DevCat, D6: SubCat, D7: Firmware, 
                                  D8-D14: not specified"""
		self.querier.setMsgHandler(productKeyResponseMsgHandler())
		self.querier.querysd(GET_PRODUCT_KEY, 0x00)
#		self.querier.queryext(GET_PRODUCT_KEY, 0x00, [])

	def setValveOn(self,valve):
		"""setValveOn(<valve number>)
        Turns the given valve on and sets it to be the active valve.
        exRain responds with am ACK message with cmd2 containing a status word.
        The status word is decoded as follows:
        bits 0-2: the active valve (0-7)
        bits 3-4: the active program (0-3)
        bit  5:   is program sequence running?
        bit  6:   is V8 configured for pump control
        bit  7:   a valve is ON.
        """
		self.querier.setMsgHandler(EZRainStatusMsgHandler())
		self.querier.querysd(VALVE_ON, valve)

	def setValveOff(self,valve):
		"""setValveOff(<valve number>)
        Turns the given valve off and sets it to be the active valve.
        EZRain responds with an ACK message with cmd2 containing a status word.
        See setValveOn() doc for the meaning of the status word.
        """
		self.querier.setMsgHandler(EZRainStatusMsgHandler())
		self.querier.querysd(VALVE_OFF, valve)

	def skipFwd(self):
		"""skipFwd()
        Turn off active valve and continue with next valve in program.
        """
		self.querier.setMsgHandler(DefaultMsgHandler("skipFwd"))
		self.querier.querysd(CONTROL, SKIP_FORWARD)

	def skipBack(self):
		"""skipBack()
        Turn off active valve and continue with previous valve in program.
        """
		self.querier.setMsgHandler(DefaultMsgHandler("skipBack"))
		self.querier.querysd(CONTROL, SKIP_BACK)

	def getValveStatus(self):
		"""getValveStatus()
        Get the status word.
        EZRain responds with an ACK message with cmd2 containing a status word.
        See setValveOn() doc for the meaning of the status word.
        """
		self.querier.setMsgHandler(EZRainStatusMsgHandler())
		self.querier.querysd(CONTROL, GET_STATUS)

	def enablePump(self):
		"""enablePump()
        configure V8 output for pump control
        This works but the results are not reflected in the status word until
        a valve control messages has been sent. eg all valves off, send enable,
        get status -> pump is off, send valve 1 off, status shows enable is on.
        """
		self.querier.setMsgHandler(DefaultMsgHandler("enablePump"))
		self.querier.querysd(CONTROL, ENABLE_PUMP)

	def disablePump(self):
		"""disablePump()
        configure V8 output for normal V8 control
        This works but the results are not reflected in the status word until
        a valve control messages has been sent. eg all valves off, send enable,
        get status -> pump is off, send valve 1 off, status shows enable is on.
        """
		self.querier.setMsgHandler(DefaultMsgHandler("disablePump"))
		self.querier.querysd(CONTROL, DISABLE_PUMP)

	def enableChangeMsg(self):
		"""enableChangeMsg()
        After this message has been sent, any change in a valve status,
        eg a program starts, will result in a broadcast message containing
        the status word to be sent.
        """
		self.querier.setMsgHandler(DefaultMsgHandler("enableChgMsg"))
		self.querier.querysd(CONTROL, ENABLE_CHG_MSG)

	def disableChangeMsg(self):
		"""disableChangeMsg()
        After this message has been sent, any change in a valve status,
        eg a program starts, will result not in a broadcast message containing
        the status word to be sent.
        """
		self.querier.setMsgHandler(DefaultMsgHandler("enableChgMsg"))
		self.querier.querysd(CONTROL, ENABLE_CHG_MSG)

	def getTimersRequest(self,prog = 0x00):
		"""getTimersRequest(<program number>)
        Get the information about the timers. 
        prog can be 0-3 with 0 being the default.
        EZRain is supposed to respond with an extended message containing the 
        current valve timer bank info.
        Doesn't work. Never get a response
        """
		self.querier.setMsgHandler(productKeyResponseMsgHandler())
		self.querier.querysd(GET_TIMERS, prog)
