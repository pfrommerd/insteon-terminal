import commands

from device import Device
from commands import insteon
from commands import Querier
from threading import Timer
from switch import Switch
from linkdb import *

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

def out(msg = ""):
	insteon.out().println(msg)

class DefaultMsgHandler:
        label = None
        def __init__(self, l):
                self.label = l
        def processMsg(self, msg):
                out(self.label + " got msg: " + msg.toString())
                return 1

class ClearDatabase:
        dbbuilder = None
        def do(self, dbb):
                self.dbbuilder = dbb
                

class DBBuilder(MsgListener):
        addr   = None
        timer  = None
        completeAction = None
        db = {};
        def __init__(self, addr):
                self.addr = addr
        def clear(self):
                db = {};
        def setCompleteAction(self, action):
                self.completeAction = action
        def start(self):
                insteon.addListener(self)
                msg = commands.createExtendedMsg(InsteonAddress(self.addr), 0x2f, 0, 0, 0, 0)
                msg.setByte("userData1", 0);
                msg.setByte("userData2", 0);
                msg.setByte("userData3", 0);
                msg.setByte("userData4", 0);
                msg.setByte("userData5", 0);
                commands.writeMsg(msg)
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
                dumpDB(self.db)
                out("database complete!")
                if not self.completeAction == None:
                        self.completeAction.do(self)

                
        def msgReceived(self, msg):
                self.restartTimer()
                if msg.isPureNack():
                        out("got pure NACK")
                        return
                if msg.getByte("Cmd") == 0x62:
                        out("query msg acked!")
                elif msg.getByte("Cmd") == 0x51:
                        off   = (msg.getByte("userData3") & 0xFF) << 8 | (msg.getByte("userData4") & 0xFF)
                        rb    = msg.getBytes("userData6", 8); # ctrl + group + [data1,data2,data3] + whatever
                        ltype = rb[0] & 0xFF
                        group = rb[1] & 0xFF
                        data  = rb[5:8]
                        addr  = InsteonAddress(rb[2] & 0xff, rb[3] & 0xff, rb[4] & 0xff)
                        rec   = {"offset" : off, "addr": addr, "type" : ltype,
                                 "group" : group, "data" : data}
                        addRecord(self.db, rec, False)
                        if (ltype & 0x02 == 0):
#                                out("last record: " + msg.toString())
                                self.done()
                                return
#                        dumpRecord(rec)
                else:
                        out("got unexpected msg: " + msg.toString())


class switch2477S(Switch):
    def __init__(self, name, addr):
        Device.__init__(self, name, addr)
        self.dbbuilder = DBBuilder(addr)
        self.querier = Querier(addr)

    def getdb(self):
        out("getting db, be patient!")
        self.dbbuilder.clear()
        self.dbbuilder.start()

    def startLinking(self):
        self.querier.setMsgHandler(DefaultMsgHandler("start linking"))
        self.querier.querysd(0x09, 0x03);

    def ping(self):
        self.querier.setMsgHandler(DefaultMsgHandler("ping"))
        self.querier.querysd(0x0F, 0x01);
 
    def idrequest(self):
        self.querier.setMsgHandler(DefaultMsgHandler("id request"))
        self.querier.querysd(0x10, 0x00);

