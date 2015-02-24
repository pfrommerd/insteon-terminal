from java.lang import System

from us.pfrommer.insteon.cmd.hub import HubStream
from us.pfrommer.insteon.cmd.serial import SerialIOStream

from us.pfrommer.insteon.cmd import IOPort

from us.pfrommer.insteon.cmd.utils import Utils

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener

from us.pfrommer.insteon.cmd.msg import InsteonAddress

from threading import Condition
from threading import Timer

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

devNameMap = {}
devAddressMap = {}

def addDev(dev):
	devNameMap[dev.getName()] = dev
	devAddressMap[dev.getAddress()] = dev;
	
def getDevByName(name):
	return devNameMap[name]

def getDevByAdr(adr):
	return devAddressMap[adr]
	
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

def createExtendedMsg(adr, cmd1, cmd2, flags = 0x1f):
       	msg = Msg.s_makeMessage("SendExtendedMessage")
	msg.setAddress("toAddress", adr)
	msg.setByte("messageFlags", flags | 0x10)
	msg.setByte("command1", cmd1)
	msg.setByte("command2", cmd2)
	checksum = (~(cmd1 + cmd2) + 1)
	msg.setByte("userData14", checksum)
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

class KeypadDBDumper(MsgListener):
        dev   = None
        timer = None
        recordDict = {};
        def __init__(self, d):
                self.dev = d
        def start(self):
                insteon.addListener(self)
                msg = createExtendedMsg(InsteonAddress(self.dev), 0x2f, 0)
                msg.setByte("userData1", 0);
                msg.setByte("userData2", 0);
                msg.setByte("userData3", 0);
                msg.setByte("userData4", 0);
                msg.setByte("userData5", 0);
                writeMsg(msg)
                out("sent query msg ... ")
                self.timer = Timer(20.0, self.giveUp)
                self.timer.start()

        def restartTimer(self):
                if self.timer:
                        self.timer.cancel()
                self.timer = Timer(20.0, self.giveUp)
                self.timer.start()

        def giveUp(self):
                out("did not get full database, giving up!")
                insteon.removeListener(self)
                self.timer.cancel()

        def done(self):
                insteon.removeListener(self)
                if self.timer:
                        self.timer.cancel()
                out("database complete!")
        
                
        def msgReceived(self, msg):
                self.restartTimer()
                if msg.isPureNack():
                        out("got pure NACK")
                        return
                if msg.getByte("Cmd") == 0x62:
                        out("query msg acked!")
                elif msg.getByte("Cmd") == 0x51:
                        dbaddr = (msg.getByte("userData3") & 0xFF) << 8 | (msg.getByte("userData4") & 0xFF)
                        if (self.recordDict.has_key(dbaddr)):
                                out("duplicate record ignored: 0x" + format(dbaddr,'04x'))
                                return
                        rb = msg.getBytes("userData6", 8); # ctrl + group + [data1,data2,data3] + whatever
                        ctrl = rb[0] & 0xFF;
                        if (ctrl & 0x02 == 0):
                                self.done()
                                return
                        rec = ' '.join(format(x & 0xFF, '02x') for x in rb)
                        self.recordDict[dbaddr] = rb
#                        out("linkrecord: addr 0x" + format(dbaddr, '04x') + " record: " + rec)
                        out("linkrecord: addr 0x" + format(dbaddr, '04x') + " ctrl: " + '{0:08b}'.format(rb[0] & 0xFF)
                            + " group: " + format(rb[1] & 0xFF, '02x')
                            + " data: " + ' '.join(format(x & 0xFF, '02x') for x in rb[2:4]))
                else:
                        out("got unexpected msg: " + msg.toString())

def getDB(dev):
	if insteon.isConnected() is not True:
                err("Not connected!");
                return;
        out("getting link database of device " + dev)
        dumper = KeypadDBDumper(dev);
        dumper.start()
