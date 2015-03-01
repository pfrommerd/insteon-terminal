from threading import Timer

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener

from us.pfrommer.insteon.cmd.msg import InsteonAddress

import utils

class DBBuilder(MsgListener):
    addr   = None
    timer  = None
    recordDict = {};
    def __init__(self, addr):
        self.addr = addr
    def start(self):
        import commands
        from commands import out
        from commands import insteon        
        
        insteon.addListener(self)
        msg = commands.createExtendedMsg(self.addr, 0x2f, 0)
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
        import commands
        from commands import out
        from commands import insteon        

        out("did not get full database, giving up!")
        insteon.removeListener(self)
        self.timer.cancel()

    def done(self):
        import commands
        from commands import out
        from commands import insteon        
        
        insteon.removeListener(self)
        if self.timer:
                self.timer.cancel()
        out("database complete!")
                
    def msgReceived(self, msg):
        import commands
        from commands import out
        from commands import insteon        

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
                rb = msg.getBytes("userData6", 8); # the LR (everything after byte 3 in All-link record response
                self.recordDict[dbaddr] = rb
                out(utils.formatLREntry(rb))
        else:
            out("got unexpected msg: " + msg.toString())

class Device:
    m_name = ""
    m_address = InsteonAddress()
    m_dbBuilder = None
    
    def __init__(self, name, adr):
        self.m_name = name
        self.m_address = adr
        self.m_dbBuilder = DBBuilder(adr)
    
    def getName(self):
        return self.m_name
    
    def getAddress(self):
        return self.m_address
    
    def dumpDB(self):
        self.m_dbBuilder.start()
    