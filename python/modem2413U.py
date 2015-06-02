import commands
import time

from device import *
from linkdb import *
from commands import insteon
from commands import Querier
from threading import Timer
from threading import Condition

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress
from us.pfrommer.insteon.cmd.utils import Utils
# >>> modem.getdb()
# 0000 25.65.D6             25.65.D6 CTRL 11100010 group: 01 data: 02 2a 43
# 0000 1E.F1.E3             1E.F1.E3 CTRL 11100010 group: 01 data: 02 2a 42
# 0000 1E.EF.32             1E.EF.32 CTRL 11100010 group: 01 data: 02 2a 42
# 0000 24.D7.90             24.D7.90 CTRL 11100010 group: 01 data: 02 2a 43
# 0000 23.EE.16             23.EE.16 CTRL 11100010 group: 01 data: 02 2a 43
# 0000 20.AB.26             20.AB.26 RESP 10100010 group: 01 data: 01 20 41
# 0000 20.AB.26             20.AB.26 CTRL 11100010 group: 01 data: 01 20 41
# 0000 27.8C.A3             27.8C.A3 CTRL 11100010 group: 01 data: 10 01 41
# 0000 20.A4.43             20.A4.43 RESP 10100010 group: 01 data: 01 20 41
# 0000 20.A4.43             20.A4.43 CTRL 11100010 group: 01 data: 01 20 41
# 0000 20.AC.99             20.AC.99 RESP 10100010 group: 01 data: 01 20 41
# 0000 20.AC.99             20.AC.99 CTRL 11100010 group: 01 data: 01 20 41
# 0000 kitchen_thermostat   32.F7.2C RESP 10100010 group: 01 data: 00 00 00
# 0000 kitchen_thermostat   32.F7.2C RESP 10100010 group: 02 data: 00 00 00
# 0000 kitchen_thermostat   32.F7.2C RESP 10100010 group: 03 data: 00 00 00
# 0000 kitchen_thermostat   32.F7.2C RESP 10100010 group: 04 data: 00 00 00
# 0000 kitchen_thermostat   32.F7.2C RESP 10100010 group: ef data: 00 00 ef
# 0000 kitchen_thermostat   32.F7.2C CTRL 11100010 group: 00 data: 01 00 00
# 0000 office_keypad        30.0D.9F CTRL 11100010 group: 00 data: 02 2c 41

#modem.modifyFirstOrAdd("25.65.D6", 0x01, 0xe2, [0x02, 0x2a, 0x43])
def out(msg = ""):
	insteon.out().println(msg)


class DefaultMsgHandler:
        label = None
        def __init__(self, l):
                self.label = l
        def processMsg(self, msg):
                out(self.label + " got msg: " + msg.toString())
                return 1

class IMInfoMsgHandler:
        label = None
        def processMsg(self, msg):
                out(" got msg: " + msg.toString())
                return 1

class DBBuilder(MsgListener):
        condition = Condition()
        keepRunning = True
        timer  = None
        recordDict = {}
        def start(self):
                self.keepRunning = True
                self.recordDict = {}
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
                linkType    = recordFlags
                group       = msg.getByte("ALLLinkGroup") & 0xFF
                linkAddr    = msg.getAddress("LinkAddr")
                data        = [msg.getByte("LinkData1"), msg.getByte("LinkData2"),
                               msg.getByte("LinkData3")]
                addRecord(self.recordDict,
                          {"offset" : 0, "addr": linkAddr, "type" : linkType,
                           "group" : group, "data" : data})
        def dumpDB(self):
                dumpDB(self.recordDict) # linkdb class
                                
        def saveDB(self, filename):
                saveDB(self.recordDict, filename)
        def loadDB(self, filename):
                self.recordDict = {}
                loadDB(self.recordDict, filename)
        def nukeDB(self, modem):
                records = getRecordsAsArray(self.recordDict)
                out("nuking " + format(len(records), 'd') + " records")
                for rec in records:
                        modem.deleteFirstRecord(rec["addr"], rec["group"])
                        time.sleep(1)
        def restoreDB(self, modem, filename):
                self.loadDB(filename)
                records = getRecordsAsArray(self.recordDict)
                out("restoring " + format(len(records), 'd') + " records")
                for rec in records:
                        modem.modifyFirstOrAdd(rec["addr"], rec["group"], rec["type"], rec["data"])
                        time.sleep(1)

class modem2413U(Device):
    dbbuilder = None
    querier = None
    def __init__(self, name, addr):
        Device.__init__(self, name, addr)
        self.dbbuilder = DBBuilder()
    def getdb(self):
        self.dbbuilder.start()
        self.dbbuilder.wait()
        self.dbbuilder.dumpDB()
        out("Modem Link DB complete")
    def getid(self):
        self.querier = Querier(InsteonAddress("00.00.00"))
        self.querier.setMsgHandler(IMInfoMsgHandler())
        msg = Msg.s_makeMessage("GetIMInfo")
        self.querier.sendMsg(msg)
    def linkAsController(self, otherDevice, group):
        addr = InsteonAddress(otherDevice)
        self.querier = Querier(addr)
        self.querier.setMsgHandler(DefaultMsgHandler("link as controller"))
        msg = Msg.s_makeMessage("StartALLLinking")
        msg.setByte("LinkCode", 0x01)
        msg.setByte("ALLLinkGroup", group)
        self.querier.sendMsg(msg)
    def linkAsResponder(self, otherDevice, group):
        addr = InsteonAddress(otherDevice)
        self.querier = Querier(addr)
        self.querier.setMsgHandler(DefaultMsgHandler("start linking"))
        msg = Msg.s_makeMessage("StartALLLinking")
        msg.setByte("LinkCode", 0x00)
        msg.setByte("ALLLinkGroup", group)
        self.querier.sendMsg(msg)
    def linkAsEither(self, otherDevice, group):
        addr = InsteonAddress(otherDevice)
        self.querier = Querier(addr)
        self.querier.setMsgHandler(DefaultMsgHandler("link/unlink as controller or responder"))
        msg = Msg.s_makeMessage("StartALLLinking")
        msg.setByte("LinkCode", 0x03)
        msg.setByte("ALLLinkGroup", group)
        self.querier.sendMsg(msg)
    def respondToUnlink(self, otherDevice, group):
        # could not get 0xFF to unlink
        self.linkAsEither(otherDevice, group)
    def unlinkAsController(self, otherDevice, group):
        addr = InsteonAddress(otherDevice)
        self.querier = Querier(addr)
        self.querier.setMsgHandler(DefaultMsgHandler("unlink as controller"))
        msg = Msg.s_makeMessage("StartALLLinking")
        msg.setByte("LinkCode", 0xFF)
        msg.setByte("ALLLinkGroup", group)
        self.querier.sendMsg(msg)
    def cancelLinking(self):
        self.querier = Querier(self.m_address)
        self.querier.setMsgHandler(DefaultMsgHandler("cancel linking"))
        msg = Msg.s_makeMessage("CancelALLLinking")
        self.querier.sendMsg(msg)
    def addSoftwareController(self, addr):
        self.modifyRecord(addr, 0xef, 0x41, 0xa2, [0,0,0xef], "addSoftwareController")
    def deleteSoftwareController(self, addr):
        self.modifyRecord(addr, 0xef, 0x80, 0x00, [0,0,0], "deleteSoftwareController")
    def deleteFirstRecord(self, addr, group):
        self.modifyRecord(addr, group, 0x80, 0x00, [0,0,0], "delete record")
    def modifyFirstOrAdd(self, addr, group, recordFlags, data):
        if (recordFlags & (1 << 6)): # controller
                self.modifyRecord(addr, group, 0x40, recordFlags, data, "modify first or add")
        else:
                self.modifyRecord(addr, group, 0x41, recordFlags, data, "modify first or add")
    def modifyFirstControllerOrAdd(self, addr, group, data):
        self.modifyRecord(addr, group, 0x40, 0xe2, data, "modify first controller found or add")
    def modifyFirstResponderOrAdd(self, addr, group, data):
        self.modifyRecord(addr, group, 0x41, 0xa2, data, "modify first responder found or add")
    def modifyRecord(self, addr, group, controlCode, recordFlags, data, txt):
        msg = Msg.s_makeMessage("ManageALLLinkRecord");
        msg.setByte("controlCode", controlCode); # modify first controller found or add
        msg.setByte("recordFlags", recordFlags);
        msg.setByte("ALLLinkGroup", group);
        msg.setAddress("linkAddress", InsteonAddress(addr));
        msg.setByte("linkData1", data[0] & 0xFF)
        msg.setByte("linkData2", data[1] & 0xFF)
        msg.setByte("linkData3", data[2] & 0xFF)
        self.querier = Querier(self.m_address)
        self.querier.setMsgHandler(DefaultMsgHandler(txt))
        self.querier.sendMsg(msg)
            
    def saveDB(self, filename):
        self.dbbuilder.start()
        self.dbbuilder.wait()
        self.dbbuilder.saveDB(filename)
    def loadDB(self, filename):
        self.dbbuilder.loadDB(filename)
        self.dbbuilder.dumpDB()
    def nukeDB(self):
        self.dbbuilder.start()
        self.dbbuilder.wait()
        self.dbbuilder.nukeDB(self)
    def restoreDB(self, filename):
        self.loadDB(filename)
        self.dbbuilder.restoreDB(self, filename)
    

