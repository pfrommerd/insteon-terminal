import commands

from device import Device
from commands import insteon
from threading import Timer
from threading import Condition

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress
from us.pfrommer.insteon.cmd.utils import Utils

def out(msg = ""):
	insteon.out().println(msg)

class ModemDBDumper(MsgListener):
        condition = Condition()
        keepRunning = True

        def start(self):
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

        def dumpEntry(self, msg):
                recordFlags = msg.getByte("RecordFlags") & 0xff
                linkType = "CTRL" if ((recordFlags & (0x1 << 6)) != 0) else "RESP"

                group = Utils.toHex(msg.getByte("ALLLinkGroup"))
                linkAddr = msg.getAddress("LinkAddr")
                data1 = Utils.toHex(msg.getByte("LinkData1"))
                data2 = Utils.toHex(msg.getByte("LinkData2"))
                data3 = Utils.toHex(msg.getByte("LinkData3"))

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
                        insteon.writeMsg(Msg.s_makeMessage("GetNextALLLinkRecord"))

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

        def dumpEntry(self, msg):
                recordFlags = msg.getByte("RecordFlags") & 0xff
                linkType = "CTRL" if ((recordFlags & (0x1 << 6)) != 0) else "RESP"

                group = Utils.toHex(msg.getByte("ALLLinkGroup"))
                linkAddr = msg.getAddress("LinkAddr")
                data1 = Utils.toHex(msg.getByte("LinkData1"))
                data2 = Utils.toHex(msg.getByte("LinkData2"))
                data3 = Utils.toHex(msg.getByte("LinkData3"))

                out(linkAddr.toString() + " " + linkType + " group: " + group + " data1: " + data1 + 
                    " data2: " + data2 + " data3: " + data3)

        def dumpRecord(self, rec):
#                out(rec["addr"] + " " + rec["type"] + " " + rec["group"] + " " + ' '.join(rec["data"]))
                out(rec["addr"].toString() + " " + rec["type"] + " " + rec["group"])

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
                linkType = "CTRL" if ((recordFlags & (0x1 << 6)) != 0) else "RESP"
                group = Utils.toHex(msg.getByte("ALLLinkGroup"))
                linkAddr = msg.getAddress("LinkAddr")
                data = [Utils.toHex(msg.getByte("LinkData1")), Utils.toHex(msg.getByte("LinkData2")),
                        Utils.toHex(msg.getByte("LinkData3"))]
                if not self.recordDict.has_key(linkAddr):
                        self.recordDict[linkAddr] = {}
                if not self.recordDict[linkAddr].has_key(linkType):
                        self.recordDict[linkAddr][linkType] = {}
                if  not self.recordDict[linkAddr][linkType].has_key(group):
                        self.recordDict[linkAddr][linkType][group] = []

                self.recordDict[linkAddr][linkType][group].append({"addr": linkAddr,
                                                                   "type" : linkType,
                                                                   "group" : group,
                                                                   "data" : data})
        def dumpDB(self):
                for addr in sorted(self.recordDict):
                        for type in sorted(self.recordDict[addr]):
                                for group in sorted(self.recordDict[addr][type]):
                                        for inst in self.recordDict[addr][type][group]:
                                                self.dumpRecord(inst)
                                

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
