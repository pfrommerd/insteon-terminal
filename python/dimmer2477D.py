#-------------------------------------------------------------------------------
#
# Insteon dimmer 2477D
#

import iofun
from linkdb import *

from querier import Querier
from querier import MsgHandler
from dimmer import Dimmer

from python.mixins.keybeepmixin import KeyBeepMixin

from us.pfrommer.insteon.msg import Msg
from us.pfrommer.insteon.msg import MsgListener
from us.pfrommer.insteon.msg import InsteonAddress

def out(msg = ""):
	iofun.out(msg)

class DefaultMsgHandler(MsgHandler):
	label = None
	def __init__(self, l):
		self.label = l
	def processMsg(self, msg):
		out(self.label + " got msg: " + msg.toString())
		return 1

class Flags1MsgHandler(MsgHandler):
        def __init__(self, name):
                MsgHandler.__init__(self, name)
        def processMsg(self, msg):
                tmp = msg.getByte("command2") & 0xFF
                out(self.name + " = " + format(tmp, '02d'))
                f = ""
                f +=  "Prog Lock ON|"  if (tmp & (0x1 << 0)) else "Prog Lock OFF|"
                f +=  "LED on TX ON|" if (tmp & (0x1 << 1)) else "LED on TX OFF|"
                f +=  "Resume Dim ON|" if (tmp & (0x1 << 2)) else "Resume Dim OFF|"
                #f +=  "Fourth ON|" if (tmp & (0x1 << 3)) else "Fourth OFF|"
                f +=  "LED Backlight OFF|" if (tmp & (0x1 << 4)) else "LED Backlight ON|"
                f +=  "Key Beep ON|" if (tmp & (0x1 << 5)) else "Key Beep OFF|"
                f +=  "RF Disable ON|" if (tmp & (0x1 << 6)) else "RF Disable OFF|"
                f +=  "Powerline Disable ON" if (tmp & (0x1 << 7)) else "Powerline Disable OFF"
                out(self.name + " got flags1: " + f);
                return 1

class Flags2MsgHandler(MsgHandler):
        def __init__(self, name):
                MsgHandler.__init__(self, name)
        def processMsg(self, msg):
                tmp = msg.getByte("command2") & 0xFF
                out(self.name + " = " + format(tmp, '02d'))
                f = ""
                f +=  "TenD ON|"  if (tmp & (0x1 << 0)) else "TenD OFF|"
                f +=  "X10 ON|" if (tmp & (0x1 << 1)) else "X10 OFF|"
                f +=  "Blink On Error ON|" if (tmp & (0x1 << 2)) else "Blink On Error OFF|"
                f +=  "Cleanup Report ON|" if (tmp & (0x1 << 3)) else "Cleanup Report OFF|"
                f +=  "Detach Load ON|" if (tmp & (0x1 << 5)) else "Detach Load OFF|"
                f +=  "SmartHops OFF" if (tmp & (0x1 << 6)) else "SmartHops ON"
                out(self.name + " got flags2: " + f);
                return 1


class Dimmer2477D(Dimmer, KeyBeepMixin):
	"""==============  Insteon SwitchLinc Dimmer 2477D ==============="""
	def __init__(self, name, addr):
		Dimmer.__init__(self, name, addr)

        def getext(self):
                self.querier.setMsgHandler(ExtMsgHandler("getext"))
                self.querier.queryext(0x2e, 0x00, [])

        def readFlags1(self):
                """readFlags1()
                read plock/led/resum/beep etc flags"""
                self.querier.setMsgHandler(Flags1MsgHandler("read flags1"))
                self.querier.querysd(0x1f, 0x00)

        def readFlags2(self):
                """readFlags2()
                read TenD/NX10/blinkOnError etc flags"""
                self.querier.setMsgHandler(Flags2MsgHandler("read flags2"))
                self.querier.querysd(0x1f, 0x05)

        def readCRCErrorCount(self):
                """readCRCErrorCount()
                read CRC error counts"""
                self.querier.setMsgHandler(CountMsgHandler("CRC error count"))
                self.querier.querysd(0x1f, 0x02)

        def readSNFailureCount(self):
                """readSNFailureCount()
                read SN failure counts """
                self.querier.setMsgHandler(CountMsgHandler("S/N failure count"))
                self.querier.querysd(0x1f, 0x03)

        def readDeltaFlag(self):
                """readDeltaFlag()
                read database delta flag """
                self.querier.setMsgHandler(CountMsgHandler("database delta flag"))
                self.querier.querysd(0x1f, 0x01)

        def getLEDStatus(self):
                """getLEDStatus()
                get current led status """
                self.querier.setMsgHandler(LEDStatusMsgHandler("led level"))
                self.querier.querysd(0x19, 0x01)

        def setPLOn(self):
                """setPLOn()
                This enables the Local Programming Lock - No Press and Hold Linking"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Programming Lock ON"))
                return self.querier.queryext(0x20, 0x00, [0x00, 0x00, 0x00]);

        def setPLOff(self):
                """setPLOff()
                This disables the Local Programming Lock - Allows Press and Hold Linking"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Programming Lock OFF"))
                return self.querier.queryext(0x20, 0x01, [0x00, 0x00, 0x00]);

        def setLEDOn(self):
                """setLEDOn()
                This enables the LED blink during transmission"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set LED ON"))
                return self.querier.queryext(0x20, 0x02, [0x00, 0x00, 0x00]);

        def setLEDOff(self):
                """setLEDOff()
                This diables the LED blink during transmission"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set LED OFF"))
                return self.querier.queryext(0x20, 0x03, [0x00, 0x00, 0x00]);

        def setResumeDimOn(self):
                """setResumeDimOn()
                This resumes previous dim level next time turned on"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Resule Dim ON"))
                return self.querier.queryext(0x20, 0x04, [0x00, 0x00, 0x00]);

        def setResumeDimOff(self):
                """setResumeDimOff()
                This ignores previous dim level next time turned on"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Resume Dim Off"))
                return self.querier.queryext(0x20, 0x05, [0x00, 0x00, 0x00]);

        #def setLinkToAllGrpsOn(self):
        #        """setLinkToAllGrpsOn()
        #        This links the HDS to all groups (Group 0xFF)"""
        #        self.querier.setMsgHandler(DefaultMsgHandler("Set Link to FF"))
        #        return self.querier.queryext(0x20, 0x06, [0x00, 0x00, 0x00]);

        #def setLinkToAllGrpsOff(self):
        #        """setLinkToAllGrpsOff()
        #        This removes the link to all groups (0xFF)"""
        #        self.querier.setMsgHandler(DefaultMsgHandler("Set Link to FF off"))
        #        return self.querier.queryext(0x20, 0x07, [0x00, 0x00, 0x00]);

        def setLEDBLOff(self):
                """setLEDBLOff()
                This sets the LED Backlight off"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set LED Backlight OFF"))
                return self.querier.queryext(0x20, 0x08, [0x00, 0x00, 0x00]);

        def setLEDBLOn(self):
                """setLEDBLOn()
                This sets the LED Backlight on"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set LED Backlight ON"))
                return self.querier.queryext(0x20, 0x09, [0x00, 0x00, 0x00]);

        def setRFOff(self):
                """setRFOff()
                This sets Rf Off...as an originator, will still hop messages"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set RF OFF"))
                return self.querier.queryext(0x20, 0x0C, [0x00, 0x00, 0x00]);

        def setRFOn(self):
                """setRFOn()
                This sets Rf on"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set RF ON"))
                return self.querier.queryext(0x20, 0x0D, [0x00, 0x00, 0x00]);

        def setInsteonPLOff(self):
                """setInsteonPLOff()
                This sets Insteon Powerline Communications Off"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Insteon Powerline OFF"))
                return self.querier.queryext(0x20, 0x0E, [0x00, 0x00, 0x00]);

        def setInsteonPLOn(self):
                """setInsteonPLOn()
                This sets Insteon Powerline Communications On....will go back to on every power cycle"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Insteon Powerline ON"))
                return self.querier.queryext(0x20, 0x0F, [0x00, 0x00, 0x00]);

        def setTenDOn(self):
                """setTenDOn()
                This sets TenD On"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set TenD ON"))
                return self.querier.queryext(0x20, 0x10, [0x00, 0x00, 0x00]);

        def setTenDOff(self):
                """setTenDOff()
                This sets TenD Off"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set TenD OFF"))
                return self.querier.queryext(0x20, 0x11, [0x00, 0x00, 0x00]);

        def setX10On(self):
                """setX10On()
                This sets X10 RX/TX On - Uses House Code and Unit Code Set with setX10Address(Housecode, UnitCode)"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set X10 ON"))
                return self.querier.queryext(0x20, 0x12, [0x00, 0x00, 0x00]);

        def setX10Off(self):
                """setX10Off()
                This sets X10 RX/TX Off"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set X10 RX/TX OFF"))
                return self.querier.queryext(0x20, 0x13, [0x00, 0x00, 0x00]);

        def setBlinkOnErrorOff(self):
                """setBlinkOnErrorOff()
                This prevents the dimmer from blinking LED on error"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set blink on error Off\n"))
                return self.querier.queryext(0x20, 0x14, [0x00, 0x00, 0x00]);

        def setBlinkOnErrorOn(self):
                """setBlinkOnErrorOn()
                This allows the dimmer to blink LED on error"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set blink on error On\n"))
                return self.querier.queryext(0x20, 0x15, [0x00, 0x00, 0x00]);

        def setCleanupReportOff(self):
                """setCleanupReportOff()
                This prevents the HDS from sending a cleanup report after changes in status"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Cleanup Report Off\n"))
                return self.querier.queryext(0x20, 0x16, [0x00, 0x00, 0x00]);

        def setCleanupReportOn(self):
                """setCleanupReportOn()
                This allows the HDS to send a cleanup report after changes in status"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Cleanup Report On\n"))
                return self.querier.queryext(0x20, 0x17, [0x00, 0x00, 0x00]);

        def setDetachLoadOff(self):
                """setDetachLoadOff()
                This attaches load from local control."""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Detach Load Off\n"))
                return self.querier.queryext(0x20, 0x1A, [0x00, 0x00, 0x00]);

        def setDetachLoadOn(self):
                """setDetachLoadOn()
                This detached load from local control, paddle still sends commands."""
                self.querier.setMsgHandler(DefaultMsgHandler("Set Detach Load On\n"))
                return self.querier.queryext(0x20, 0x1B, [0x00, 0x00, 0x00]);

        def setSmartHopsOn(self):
                """setSmartHopsOn()
                Starts Hops of last Rx ACK (SmartHops)"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set SmartHops On\n"))
                return self.querier.queryext(0x20, 0x1C, [0x00, 0x00, 0x00]);

        def setSmartHopsOff(self):
                """setSmartHopsOff()
                Start Hops at 1"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set SmartHops Off\n"))
                return self.querier.queryext(0x20, 0x1D, [0x00, 0x00, 0x00]);

        def setLocalOnLevel(self, level):
                """setLocalOnLevel(level)
                This sets brightness level when dimmer is turned on lcoally - Value (0-255)"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set On Level"))
                return self.querier.queryext(0x2E, 0x00, [0x00, 0x06, level]);

        def setX10Address(self, HC, UC):
                """setX10Address(Housecode, UnitCode)
                This sets the X10 house code 1-16 for codes A-P (0x20 or 32 = no HC) and unit code 1-16 (0x20 or 32 = no UC)"""
                self.querier.setMsgHandler(DefaultMsgHandler("Set X10 Address"))
                return self.querier.queryext(0x2E, 0x00, [0x00, 0x04, HC, UC]);
