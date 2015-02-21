from java.lang import System

from us.pfrommer.insteon.cmd.hub import HubStream
from us.pfrommer.insteon.cmd.serial import SerialIOStream

from us.pfrommer.insteon.cmd import IOPort

from us.pfrommer.insteon.cmd.utils import Utils
from us.pfrommer.insteon.cmd.utils.Resource import FileResource

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener

from us.pfrommer.insteon.cmd.msg import InsteonAddress

from threading import Condition

from device import Device

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
	insteon.getConsole().reset()

def quit():
	System.exit(0)

def exit():
	quit()

# device-related functions

def setDev(name, adr):
        insteon.setDevice(name, adr)

def getDevAddress(name):
        return insteon.getDeviceAddress(name)

def getDevName(adr):
        return insteon.getDeviceName(name)

# insteon-related functions

def connectToHub(adr, port, pollMillis, user, password):
	insteon.setPort(IOPort(HubStream(adr, port, pollMillis, user, password)))

def connectToSerial(dev):
	insteon.setPort(IOPort(SerialIOStream(dev)))

def disconnect():
	insteon.setPort(None)

def writeMsg(msg):
	insteon.writeMsg(msg)

def writeHex(hex):
	insteon.writeHex(hex)
	
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
	
# basic insteon commands

def on(devName, level = 0xFF):
        on(getDevAddress(devName), level)

def on(adr, level = 0xFF):
        writeMsg(createStdMsg(adr, 0x0F, 0x11, level, -1))
	
def off(devName):
        off(getDevAddress(devName))

def off(adr):
        writeMsg(createStdMsg(adr, 0x0F, 0x13, 0, -1))

	
class ModemDBDumper(MsgListener):
        condition = Condition()
        keepRunning = True

        def start(self):
                insteon.addListener(self)
                writeMsg(Msg.s_makeMessage("GetFirstALLLinkRecord"))
                
        def done(self):
                insteon.removeListener(self)

                self.condition.acquire()

                self.keepRunning = False

                self.condition.notify()
                self.condition.release()
        def wait(self):

                self.condition.acquire()
                while self.keepRunning:
                        self.condition.wait()
                self.condition.release()

        def dumpEntry(self, msg):
                recordFlags = msg.getByte("RecordFlags") & 0xff
                linkType = "CTRL" if ((recordFlags & (0x1 << 6)) != 0) else "RESP"

                group = Utils.getHexString(msg.getByte("ALLLinkGroup"))
                linkAddr = msg.getAddress("LinkAddr")
                data1 = Utils.getHexString(msg.getByte("LinkData1"))
                data2 = Utils.getHexString(msg.getByte("LinkData2"))
                data3 = Utils.getHexString(msg.getByte("LinkData3"))

                out(linkAddr.toString() + " " + linkType + " group: " + group + " data1: " + data1 + 
                    " data2: " + data2 + " data3: " + data3)

        def msgReceived(self, msg):
                if msg.isPureNack():
                        return;
                if msg.getByte("Cmd") == 0x69 or msg.getByte("Cmd") == 0x6a :
                        if msg.getByte("ACK/NACK") == 0x15:
                                self.done()
                elif msg.getByte("Cmd") == 0x57:
                        self.dumpEntry(msg)
                        writeMsg(Msg.s_makeMessage("GetNextALLLinkRecord"))

def dumpLinkDB():
	if insteon.isConnected() is not True:
                err("Not connected!");
                return;
        out("Starting Modem Link DB");
        dumper = ModemDBDumper()
        dumper.start()
        dumper.wait()
        out("Modem Link DB Done")
