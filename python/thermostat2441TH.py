import commands

from device import Device
from linkdb import *
from commands import insteon
from commands import Querier
from threading import Timer

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

def out(msg = ""):
	insteon.out().println(msg)

class MsgHandler:
        def processMsg(self, msg):
                out("got msg: " + msg.toString())
                return 1

class StatusInfoMsgHandler(MsgHandler):
        label = None
        def __init__(self, l):
                self.label = l
        def processMsg(self, msg):
                out("got msg: " + msg.toString())
                tmp = msg.getByte("command2") & 0xFF
                out(self.label + " = " + format(tmp, '02d'))
                return 1

class ReadSetData1MsgHandler(MsgHandler):
        label = None
        def processMsg(self, msg):
                out("got msg: " + msg.toString())
                tmp = msg.getByte("command1") & 0xFF
                if (tmp != 0x2e):
                        out("unexpected msg!")
                        return 0
                if msg.isExtended():
                        temp = (msg.getByte("userData3") & 0xFF) << 8
                        temp += msg.getByte("userData4") & 0xFF
                        hum  = msg.getByte("userData5") & 0xFF
                        toff = msg.getByte("userData6") & 0xFF
                        hoff = msg.getByte("userData7") & 0xFF
                        smode = msg.getByte("userData8") & 0xFF
                        fmode = msg.getByte("userData9") & 0xFF
                        bsecs = msg.getByte("userData10") & 0xFF
                        hmins = msg.getByte("userData11") & 0xFF
                        sbackpt = msg.getByte("userData12") & 0xFF
                        ackb  = msg.getByte("userData13") & 0xFF
                        fwrev  = msg.getByte("userData14") & 0xFF
                        out("temp [C]:     "   + format(temp * 0.1, 'f'))
                        out("humidity:     "   + format(hum, 'd'))
                        out("temp off:     "   + format(toff, 'd'))
                        out("humidity off: "   + format(hoff, 'd'))
                        out("system mode:  "   + format(smode, 'd'))
                        out("fan mode:     "   + format(fmode, 'd'))
                        out("backlite sec: "   + format(bsecs, 'd'))
                        out("AC hist mins: "   + format(hmins, 'd'))
                        out("energy bk pt: "   + format(sbackpt, 'd'))
                        out("ack byte:     "   + format(ackb, '02x'))
                        out("fw revision:  "   + format(fwrev, '02x'))
                        return 1
                else:
                        out("got ack, waiting for reply!")
                        return 0
                return 1

class ReadSetData1bMsgHandler(MsgHandler):
        label = None
        def processMsg(self, msg):
                out("got msg: " + msg.toString())
                tmp = msg.getByte("command1") & 0xFF
                if (tmp != 0x2e):
                        out("unexpected msg!")
                        return 0
                if msg.isExtended():
                        humlow  = msg.getByte("userData4") & 0xFF
                        humhigh = msg.getByte("userData5") & 0xFF
                        fwv     = msg.getByte("userData6") & 0xFF
                        coolpt  = msg.getByte("userData7") & 0xFF
                        heatpt  = msg.getByte("userData8") & 0xFF
                        rfoff   = msg.getByte("userData9") & 0xFF
                        esspt   = msg.getByte("userData10") & 0xFF
                        exoff   = msg.getByte("userData11") & 0xFF
                        srenab  = msg.getByte("userData12") & 0xFF
                        extpwr  = msg.getByte("userData13") & 0xFF
                        exttmp  = msg.getByte("userData14") & 0xFF

                        out("hum low:      "   + format(humlow, 'd'))
                        out("hum high:     "   + format(humhigh, 'd'))
                        out("fw revision:  "   + format(fwv, '02x'))
                        out("coolpt:       "   + format(coolpt, 'd'))
                        out("heatpt:       "   + format(heatpt, 'd'))
                        out("rf offset:    "   + format(rfoff, 'd'))
                        out("en sv set pt: "   + format(esspt, 'd'))
                        out("ext T off:    "   + format(exoff, 'd'))
                        out("stat rep enb: "   + format(srenab, 'd'))
                        out("ext pwr on:   "   + format(extpwr, 'd'))
                        out("ext tmp opt:  "   + format(exttmp, 'd'))
                        return 1
                else:
                        out("got ack, waiting for reply!")
                        return 0
                return 1

class ReadSetData2MsgHandler(MsgHandler):
        label = None
        def processMsg(self, msg):
                out("got msg: " + msg.toString())
                tmp = msg.getByte("command1") & 0xFF
                if (tmp != 0x2e):
                        out("unexpected msg!")
                        return 0
                if msg.isExtended():
                        d4  = msg.getByte("userData4") & 0xFF
                        d5 = msg.getByte("userData5") & 0xFF
                        d6 = msg.getByte("userData6") & 0xFF
                        d7 = msg.getByte("userData7") & 0xFF
                        d8 = msg.getByte("userData8") & 0xFF
                        d9 = msg.getByte("userData9") & 0xFF
                        d10 = msg.getByte("userData10") & 0xFF
                        d11 = msg.getByte("userData11") & 0xFF
                        d12 = msg.getByte("userData12") & 0xFF

                        out("d4:      "   + format(d4,  'd'))
                        out("d5:      "   + format(d5,  'd'))
                        out("d6:      "   + format(d6,  'd'))
                        out("d7:      "   + format(d7,  'd'))
                        out("d8:      "   + format(d8,  'd'))
                        out("d9:      "   + format(d9,  'd'))
                        out("d10:     "   + format(d10, 'd'))
                        out("d11:     "   + format(d11, 'd'))
                        out("d12:     "   + format(d12, 'd'))
                        return 1
                else:
                        out("got ack, waiting for reply!")
                        return 0
                return 1

class OpFlagsMsgHandler(MsgHandler):
        def processMsg(self, msg):
                out("got msg: " + msg.toString())
                tmp = msg.getByte("command2") & 0xFF
                out(" Plock:      " + format((tmp >> 0) & 0x01, 'd'))
                out(" LED on TX:  " + format((tmp >> 1) & 0x01, 'd'))
                out(" Resume Dim: " + format((tmp >> 2) & 0x01, 'd'))
                out(" LED OFF:    " + format((tmp >> 3) & 0x01, 'd'))
                out(" LoadSense:  " + format((tmp >> 4) & 0x01, 'd'))
                return 1

class EngineVersionMsgHandler(MsgHandler):
        def processMsg(self, msg):
                out("got msg: " + msg.toString())
                tmp = msg.getByte("command2") & 0xFF
                out(" i2CS engine version:  " + format(tmp, '02x'))
                return 1

class IDRequestMsgHandler(MsgHandler):
        def processMsg(self, msg):
                out("got msg: " + msg.toString())
                cmd1 = msg.getByte("command1") & 0xFF
                if cmd1 == 0x10:
                        out("got ack!")
                        return 0
                elif cmd1 == 0x01:
                        out("firmware version: " + msg.getAddress("toAddress").toString())
                        return 1
                return 1

class DBBuilder(MsgListener):
        addr   = None
        timer  = None
        recordDict = {};
        def __init__(self, addr):
                self.addr = addr
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
                dumpDB(self.recordDict) # linkdb class
                out("database complete!")
        @staticmethod
        def ctrlToStr(ctrl):
                s = "CTRL" if (ctrl & (0x01 << 6)) else "RESP"
                s += "  " if (ctrl & (0x01 << 7)) else " X"
                return s

        def msgReceived(self, msg):
                self.restartTimer()
                if msg.isPureNack():
                        out("got pure NACK")
                        return
                if msg.getByte("Cmd") == 0x62:
                        out("query msg acked!")
                        return
                if msg.getByte("Cmd") == 0x50 and msg.getByte("command1") == 0x2F:
                        out("std reply received!")
                        return
                elif msg.getByte("Cmd") == 0x51:
                        off = ((msg.getByte("userData3") & 0xFF) << 8) | ((msg.getByte("userData4") & 0xFF))
#                        out("got: " + msg.toString())
#                        rb = msg.getBytes("userData6", 8); # ctrl + group + [data1,data2,data3] + whatever
#                        rec = ' '.join(format(x & 0xFF, '02x') for x in rb)

                        linkType = msg.getByte("userData6") & 0xFF
                        group    = msg.getByte("userData7") & 0xFF
                        linkAddr = InsteonAddress(msg.getByte("userData8") & 0xFF,
                                                  msg.getByte("userData9") & 0xFF,
                                                  msg.getByte("userData10") & 0xFF)
                        data     = [msg.getByte("userData11") & 0xFF,
                                    msg.getByte("userData12") & 0xFF,
                                    msg.getByte("userData13") & 0xFF]

                        if (self.recordDict.has_key(off)):
#                                out("duplicate record ignored: 0x" + format(off,'04x'))
                                return
                        rec = {"offset" : off, "addr": linkAddr, "type" : linkType,
                                   "group" : group, "data" : data}
                        addRecord(self.recordDict, rec)
                        dumpRecord(rec)
                        if (linkType & 0x02 == 0): # has end-of-list marker
                                self.done()
                                return
#                        out("linkrecord: addr 0x" + format(dbaddr, '04x') + " "
#                            + DBBuilder.ctrlToStr(rb[0] & 0xFF)
#                            + " ctrl: " + '{0:08b}'.format(rb[0] & 0xFF)
#                            + " group: " + format(rb[1] & 0xFF, '02x')
#                            + " dev: " + '.'.join(format(x & 0xFF, '02x') for x in rb[2:5])
#                            + " data: " + ' '.join(format(x & 0xFF, '02x') for x in rb[5:]))
                else:
                        out("got unexpected msg: " + msg.toString())


class thermostat2441TH(Device):
    dbbuilder = None
    querier = None
    def __init__(self, name, addr):
        Device.__init__(self, name, addr)
        self.dbbuilder = DBBuilder(addr)
        self.querier = Querier(addr)

    def ext(self, cmd1, cmd2, data1, data2):
        self.querier.queryext(cmd1, cmd2, data1, data2)
    def ext2(self, cmd1, cmd2, data1, data2, data3):
        self.querier.queryext2(cmd1, cmd2, data1, data2, data3)
    def ext3(self, cmd1, cmd2, data1, data2, data3):
        self.querier.queryext3(cmd1, cmd2, data1, data2, data3)
    def sd(self, cmd1, cmd2):
        self.querier.querysd(cmd1, cmd2)
#
#  test stuff
#
    def getdata12(self, cmd2, data1, data2, data3):
        #checksum computed correctly, but no response!
        self.querier.setMsgHandler(ReadSetData1MsgHandler())
        # cmd1, cmd2, data1, data2
#        self.ext2(0x2e, 0x02, 0x00, 0x0)
        self.ext2(0x2e, cmd2, data1, data2, data3)
#
#   tested and working
#
    def setdb(self, offset, linkAddress, group, isCtrl):
        msg   = Msg.s_makeMessage("SendExtendedMessage")
        laddr = InsteonAddress(linkAddress)
        ctrl  = (1 << 6) if isCtrl else 0  # ctrl = 1, resp = 0
        ctrl |= (1 << 7) # 1 == record is in use
        ctrl |= (1 << 5) # supposedly not used
        ctrl |= (1 << 1) # 1 == not last record
 	msg.setAddress("toAddress", InsteonAddress(self.getAddress()))
        msg.setByte("messageFlags", 0x1f)
	msg.setByte("command1", 0x2f)
	msg.setByte("command2", 0x00)
	msg.setByte("userData1", 0x00) # don't care info
        msg.setByte("userData2", 0x02) # set database
        msg.setByte("userData3", offset >> 8)  # high byte
        msg.setByte("userData4", offset & 0xff) # low byte
        msg.setByte("userData5", 8)  # number of bytes set:  1...8
        msg.setByte("userData6", ctrl)
        msg.setByte("userData7", group)
        msg.setByte("userData8", laddr.getHighByte())
        msg.setByte("userData9", laddr.getMiddleByte())
        msg.setByte("userData10", laddr.getLowByte())
        msg.setByte("userData11", 0x00) # dependent on mode: could be e.g. trigger point
        msg.setByte("userData12", 0x00) # no idea
        msg.setByte("userData13", 0x00) # no idea
        rb = msg.getBytes("command1", 15);
        checksum = (~sum(rb) + 1) & 0xFF
        msg.setByte("userData14", checksum)
        self.querier.setMsgHandler(MsgHandler())
        self.querier.sendMsg(msg);
    def ping(self):
        self.sd(0x0f, 0)
    def getid(self):
        self.querier.setMsgHandler(IDRequestMsgHandler())
        self.querier.querysd(0x10, 0x00)
    def getversion(self):
        self.querier.setMsgHandler(EngineVersionMsgHandler())
        self.querier.querysd(0x0d, 0x00)
    def beep(self):
        msg = commands.createStdMsg(InsteonAddress(self.m_address), 0x0f, 0x30, 0x00, -1);
        commands.writeMsg(msg)
    def gettemp(self):
        self.querier.setMsgHandler(StatusInfoMsgHandler("temperature"))
        self.querier.querysd(0x6a, 0x00)
    def gethumid(self):
        self.querier.setMsgHandler(StatusInfoMsgHandler("humidity"))
        self.querier.querysd(0x6a, 0x60)
    def getsetpoint(self):
        self.querier.setMsgHandler(StatusInfoMsgHandler("setpoint"))
        self.querier.querysd(0x6a, 0x20)
    def readopflags(self):
        self.querier.setMsgHandler(OpFlagsMsgHandler())
        self.querier.querysd(0x1f, 0x00)
    def getdata1(self):
        self.querier.setMsgHandler(ReadSetData1MsgHandler())
        self.ext3(0x2e, 0, 0x00, 0x00, 0x00) # query temperature
    def getdata1b(self):
        self.querier.setMsgHandler(ReadSetData1bMsgHandler())
        self.ext3(0x2e, 0, 0x00, 0x00, 0x01) # query humidity and temperature set points
    def getdatawhatever(self):
        self.querier.setMsgHandler(ReadSetData1bMsgHandler())
        self.ext3(0x2e, 0, 0x00, 0x00, 0x02) # gets something, but not sure what!
    def getdb(self):
        self.dbbuilder.start()
