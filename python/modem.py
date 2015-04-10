import commands

from commands import insteon

from commands import out
from commands import writeMsg

from device import Device

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener

from threading import Condition

import utils

#we need a special DB dump
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
            recordBytes = msg.getBytes("RecordFlags", 8)
            out(utils.formatLREntry(recordBytes))

        def msgReceived(self, msg):
                if msg.isPureNack():
                        return;
                if msg.getByte("Cmd") == 0x69 or msg.getByte("Cmd") == 0x6a :
                        if msg.getByte("ACK/NACK") == 0x15:
                                self.done()
                elif msg.getByte("Cmd") == 0x57:
                        self.dumpEntry(msg)
                        writeMsg(Msg.s_makeMessage("GetNextALLLinkRecord"))


class Modem(Device, MsgListener):
    def __init__(self, name):
        Device.__init__(self, name, None)
        
        commands.insteon.addListener(self)
        
        #Query for Modem Data
        msg = Msg.s_makeMessage("GetIMInfo")
        commands.writeMsg(msg)
    
    def msgReceived(self, msg):
        if msg.getByte("Cmd") == 0x60 :
            self.m_address = msg.getAddress("IMAddress")
            commands.insteon.removeListener(self)
    
    def dumpDB(self):
        out("Starting Modem Link DB");
        dumper = ModemDBDumper()
        dumper.start()
        dumper.wait()
        out("Modem Link DB Done")
    