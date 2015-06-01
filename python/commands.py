from java.lang import System
from threading import Timer
from us.pfrommer.insteon.cmd.hub import HubStream
from us.pfrommer.insteon.cmd.serial import SerialIOStream

from us.pfrommer.insteon.cmd import IOPort

from us.pfrommer.insteon.cmd.utils import Utils

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener

from us.pfrommer.insteon.cmd.msg import InsteonAddress

from us.pfrommer.insteon.cmd.gui import PortTracker

from device import Device
import struct

insteon = None

#sets up the environment with the correct interpreter
#called from the java application
# i.e, sets up insteon variable

def init(interpreter):
	global insteon
	insteon = interpreter

# a buch of helper functions

def err(msg = ""):
	"""
	prints to std err the value of msg and a newline character
	"""
	insteon.err().println(msg)
	
def out(msg = ""):
	insteon.out().println(msg)

def reload():
	insteon.reload()

def help(obj = None):
	if obj is not None :
		if obj.__doc__ is not None :
			out(obj.__doc__.strip())
		else :
			out("No documentation for \"" + obj.__name__ + "\"")
	else :
		out("-------Welcome to Insteon Shell-------")
		out("to get a list of available functions, type '?'")
		out("to get the doc of a function, type help(funcName)")
		out("to quit, type 'quit()'")

def clear():
	insteon.getConsole().clear()
	
def reset():
	insteon.reset()

def quit():
	System.exit(0)

def exit():
	quit()

# gui-related stuff

def trackPort():
	if insteon.isConnected() :
		tracker = PortTracker(insteon.getPort())
	else :
		err("Not connected!")
# insteon-related functions

def connectToHub(adr, port, pollMillis, user, password):
	insteon.setPort(IOPort(HubStream(adr, port, pollMillis, user, password)))

def connectToSerial(dev):
	insteon.setPort(IOPort(SerialIOStream(dev)))

def disconnect():
	insteon.setPort(None)

def writeMsg(msg):
	insteon.writeMsg(msg)
	
def readMsg():
	return insteon.readMsg()


#creates a send standard message Msg
#if group is -1, the address will be used, other wise the group will be used
def createStdMsg(adr, flags, cmd1, cmd2, group):
        msg = Msg.s_makeMessage("SendStandardMessage")
        if group != -1:
                flags |= 0xc0
                adr = InsteonAddress(0x00, 0x00, group & 0xFF)
        msg.setAddress("toAddress", adr)
        msg.setByte("messageFlags", flags)
        msg.setByte("command1", cmd1)
        msg.setByte("command2", cmd2)
        return msg

def createExtendedMsg(adr, cmd1, cmd2, data1, data2, data3, flags = 0x1f):
       	msg = Msg.s_makeMessage("SendExtendedMessage")
	msg.setAddress("toAddress", adr)
	msg.setByte("messageFlags", flags | 0x10)
	msg.setByte("command1", cmd1)
	msg.setByte("command2", cmd2)
	msg.setByte("userData1", data1)
	msg.setByte("userData2", data2)
	msg.setByte("userData3", data3)
	msg.setByte("userData4", 0)
	msg.setByte("userData5", 0)
	msg.setByte("userData6", 0)
	msg.setByte("userData7", 0)
	msg.setByte("userData8", 0)
	msg.setByte("userData9", 0)
	msg.setByte("userData10", 0)
	msg.setByte("userData11", 0)
	msg.setByte("userData12", 0)
	msg.setByte("userData13", 0)
	checksum = (~(cmd1 + cmd2 + data1 + data2) + 1)
	msg.setByte("userData14", checksum)
        return msg

def createExtendedMsg2(adr, cmd1, cmd2, data1, data2, data3, flags = 0x1f):
       	msg = Msg.s_makeMessage("SendExtendedMessage")
	msg.setAddress("toAddress", adr)
	msg.setByte("messageFlags", flags | 0x10)
	msg.setByte("command1",  cmd1)
	msg.setByte("command2",  cmd2)
	msg.setByte("userData1", data1)
	msg.setByte("userData2", data2)
	msg.setByte("userData3", data3)
	msg.setByte("userData4", 0)
	msg.setByte("userData5", 0)
	msg.setByte("userData6", 0)
	msg.setByte("userData7", 0)
	msg.setByte("userData8", 0)
	msg.setByte("userData9", 0)
	msg.setByte("userData10", 0)
	msg.setByte("userData11", 0)
	msg.setByte("userData12", 0)
        crc = calcCRC(msg)
        crcLow   = crc & 0xFF
        crcHigh  = (crc >> 8) & 0xFF
        out("checksum = " + format(crc, 'x') + " = " + format(crcHigh, '02x') + ":" + format(crcLow, '02x'))
	msg.setByte("userData13", int(crcLow & 0xFF))
	msg.setByte("userData14", int(crcHigh & 0xFF))
        return msg

def calcCRC(msg):
        bytes = msg.getBytes("command1", 14);
        crc = int(0);
        for loop in xrange(0, len(bytes)):
                b = bytes[loop] & 0xFF
                #out("orig byte: " + '{0:32b}'.format(b) + " int: " + format(b, 'd') + " = " + format(b, 'x'))
                for bit in xrange(0, 8):
                        fb = b & 0x01
                        fb = fb ^ 0x01 if (crc & 0x8000) else fb
                        fb = fb ^ 0x01 if (crc & 0x4000) else fb
                        fb = fb ^ 0x01 if (crc & 0x1000) else fb
                        fb = fb ^ 0x01 if (crc & 0x0008) else fb
                        crc = ((crc << 1) | fb) & 0xFFFF;
                        b = b >> 1

        out("calc crc for: " + str([format(bytes[x] & 0xFF, ' 02x') for x in xrange(0, len(bytes))]))
        return crc
	
# basic insteon commands

def on(devName, level = 0xFF):
        on(getDevAddress(devName), level)

def on(adr, level = 0xFF):
        writeMsg(createStdMsg(adr, 0x0F, 0x11, level, -1))
	
def off(devName):
        off(getDevAddress(devName))

def off(adr):
        writeMsg(createStdMsg(adr, 0x0F, 0x13, 0, -1))


class Querier(MsgListener):
        addr   = None
        timer  = None
        msgHandler = None
        def __init__(self, addr):
                self.addr = addr
        def setMsgHandler(self, handler):
                self.msgHandler = handler
        def sendMsg(self, msg):
                insteon.addListener(self)
                writeMsg(msg)
                out("sent msg: " + msg.toString())
                self.timer = Timer(5.0, self.giveUp)
                self.timer.start()
                
        def queryext(self, cmd1, cmd2, data1, data2):
                msg = createExtendedMsg(InsteonAddress(self.addr), cmd1, cmd2, data1, data2, 0)
                self.sendMsg(msg);
        def queryext2(self, cmd1, cmd2, data1, data2, data3):
                msg = createExtendedMsg2(InsteonAddress(self.addr), cmd1, cmd2, data1, data2, data3)
                self.sendMsg(msg);
        def queryext3(self, cmd1, cmd2, data1, data2, data3):
                msg = createExtendedMsg(InsteonAddress(self.addr), cmd1, cmd2, data1, data2, data3)
                self.sendMsg(msg);
        def querysd(self, cmd1, cmd2, group = -1):
                msg = createStdMsg(InsteonAddress(self.addr), 0x0f, cmd1, cmd2, group)
                self.sendMsg(msg);
        def giveUp(self):
                out("did not get response, giving up!")
                insteon.removeListener(self)
                self.timer.cancel()
        def done(self):
                insteon.removeListener(self)
                if self.timer:
                        self.timer.cancel()
        def msgReceived(self, msg):
                if msg.isPureNack():
                        out("got pure NACK")
                        return
                if msg.getByte("Cmd") == 0x62:
                        out("query msg acked!")
                        return
                if (self.msgHandler):
                        if self.msgHandler.processMsg(msg):
                                self.done()
                else:
                        out("got reply msg: " + msg.toString())
                        self.done()

