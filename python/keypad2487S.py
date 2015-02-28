import commands

from device import Device
from commands import insteon
from threading import Timer

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

def out(msg = ""):
	insteon.out().println(msg)

class DBBuilder(MsgListener):
        addr   = None
        timer  = None
        recordDict = {};
        def __init__(self, addr):
                self.addr = addr
        def start(self):
                insteon.addListener(self)
                msg = commands.createExtendedMsg(InsteonAddress(self.addr), 0x2f, 0)
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
                        out("linkrecord: addr 0x" + format(dbaddr, '04x') + " ctrl: " + '{0:08b}'.format(rb[0] & 0xFF)
                            + " group: " + format(rb[1] & 0xFF, '02x')
                            + " data: " + ' '.join(format(x & 0xFF, '02x') for x in rb[2:4]))
                else:
                        out("got unexpected msg: " + msg.toString())


class keypad2487S(Device):
    dbbuilder = None
    def __init__(self, name, addr):
        Device.__init__(self, name, addr)
        self.dbbuilder = DBBuilder(addr)
    def getdb(self):
        self.dbbuilder.start()
