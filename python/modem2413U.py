import commands

from device import *
from linkdb import *
from commands import insteon
from threading import Timer
from threading import Condition

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress
from us.pfrommer.insteon.cmd.utils import Utils

def out(msg = ""):
	insteon.out().println(msg)

class DBBuilder(MsgListener):
        condition = Condition()
        keepRunning = True
        timer  = None
        recordDict = {}
        def start(self):
                recordDict = {}
                insteon.addListener(self)
                insteon.writeMsg(Msg.s_makeMessage("GetFirstALLLinkRecord"))

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

        @staticmethod
        def ctrlToStr(ctrl):
                s = "CTRL" if (ctrl & (0x01 << 6)) else "RESP"
                s += "  " if (ctrl & (0x01 << 7)) else " X"
                return s

        def dumpRecord(self, rec):
                addr = rec["addr"].toString()
                dev = getDevByAddr(addr).getName() if getDevByAddr(addr) else addr
                out(format(dev, '20s') + " " + rec["type"] + " group: " + rec["group"] + " data: " + ' '.join(rec["data"]))

        def msgReceived(self, msg):
                if msg.isPureNack():
                        return;
                if msg.getByte("Cmd") == 0x69 or msg.getByte("Cmd") == 0x6a :
                        if msg.getByte("ACK/NACK") == 0x15:
                                self.done()
                elif msg.getByte("Cmd") == 0x57:
                        self.dbMsg(msg)
                        insteon.writeMsg(Msg.s_makeMessage("GetNextALLLinkRecord"))
                else:
                        out("got unexpected msg: " + msg.toString())

        def dbMsg(self, msg):
                recordFlags = msg.getByte("RecordFlags") & 0xff
                #linkType    = "CTRL" if ((recordFlags & (0x1 << 6)) != 0) else "RESP"
                linkType    = recordFlags
                group       = msg.getByte("ALLLinkGroup") & 0xFF
                linkAddr    = msg.getAddress("LinkAddr")
                data        = [msg.getByte("LinkData1"), msg.getByte("LinkData2"), msg.getByte("LinkData3")]
                addRecord(self.recordDict,
                          {"offset" : 0, "addr": linkAddr, "type" : linkType, "group" : group, "data" : data})
        def dumpDB(self):
                dumpDB(self.recordDict)
                                

class modem2413U(Device):
    dbbuilder = None
    def __init__(self, name, addr):
        Device.__init__(self, name, addr)
        self.dbbuilder = DBBuilder()
    def getdb(self):
        self.dbbuilder.start()
        self.dbbuilder.wait()
        self.dbbuilder.dumpDB()
        out("Modem Link DB complete")
