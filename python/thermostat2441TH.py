#-------------------------------------------------------------------------------
#
# Insteon Thermostat 2441TH
#

from threading import Timer
from us.pfrommer.insteon.msg import Msg
from us.pfrommer.insteon.msg import MsgListener
from us.pfrommer.insteon.msg import InsteonAddress

from device import Device
from linkdb import DB
from querier import Querier
from querier import MsgHandler
from dbbuilder import ThermostatDBBuilder

import iofun
import message


#
# various helper functions used by the message handlers
#

def out(msg = ""):
	iofun.out(msg)

def getTime(msg):
	hour    = msg.getByte("userData3")
	minute  = msg.getByte("userData4")
	seconds = msg.getByte("userData5")
	return (format(hour, '02d') + ":" + format(minute, '02d') +
			":" + format(seconds, '02d'))

def printSched(text, d1, d2, d3):
	out(text + " time: " + timeToText(d1) +
		" cool: " + format(d2, 'd') +
		" heat: " + format(d3, 'd'))

def printScheduleMsg(msg):
	printSched("wake  ", msg.getByte("userData1"),
			   msg.getByte("userData2"), msg.getByte("userData3"));
	printSched("leave ", msg.getByte("userData4"),
			   msg.getByte("userData5"), msg.getByte("userData6"));
	printSched("return", msg.getByte("userData7"),
			   msg.getByte("userData8"), msg.getByte("userData9"));
	printSched("sleep ", msg.getByte("userData10"),
			   msg.getByte("userData11"), msg.getByte("userData12"));

def timeToText(time):
	h, m  = [int((time * 15) /60), (time * 15) % 60]
	return format(h, '02d') + ":" + format(m, '02d')

def printOpFlags(flags):
	out(" link lock:   " + format((flags >> 0) & 0x01, 'd'))
	out(" button beep: " + format((flags >> 1) & 0x01, 'd'))
	out(" button lock: " + format((flags >> 2) & 0x01, 'd'))
	out(" temp format: " + ("C" if (flags & 0x08) else "F"))
	out(" time format: " + ("24h" if (flags & 0x10) else "12h"))
	out(" status LED:  " + format((flags >> 6) & 0x01, 'd'))
#
# ---------------------- message handlers ---------------------------------
#

class StatusInfoMsgHandler(MsgHandler):
	factor = 1.0
	def __init__(self, n = "StatusInfoMsgHandler", f = 1.0):
		self.name = n
		self.factor = f
	def processMsg(self, msg):
		out(self.name + " got msg: " + msg.toString())
		tmp = msg.getByte("command2") & 0xFF
		out(self.name + " = " + format(tmp * self.factor, 'f'))
		return 1

class ReadData1MsgHandler(MsgHandler):
	def __init__(self, n = "ReadData1MsgHandler"):
		self.name = n
	def processMsg(self, msg):
		out(self.name + " got msg: " + msg.toString())
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out(self.name + " got unexpected msg!")
			return 0
		if msg.isExtended():
			temp    = msg.getByte("userData4") & 0xFF
			hum     = msg.getByte("userData5") & 0xFF
			toff    = msg.getByte("userData6") & 0xFF
			hoff    = msg.getByte("userData7") & 0xFF
			smode   = msg.getByte("userData8") & 0xFF
			fmode   = msg.getByte("userData9") & 0xFF
			bsecs   = msg.getByte("userData10") & 0xFF
			hmins   = msg.getByte("userData11") & 0xFF
			sbackpt = msg.getByte("userData12") & 0xFF
			flags   = msg.getByte("userData13") & 0xFF
			temp   |= (msg.getByte("userData14") & 0xFF) << 8
			out("temp [C]:     "   + format(temp * 0.1, 'f'))
			out("humidity:     "   + format(hum, 'd'))
			out("temp off:     "   + format(toff, 'd'))
			out("humidity off: "   + format(hoff, 'd'))
			out("system mode:  "   + format(smode, 'd'))
			out("fan mode:     "   + format(fmode, 'd'))
			out("backlite sec: "   + format(bsecs, 'd'))
			out("AC hist mins: "   + format(hmins, 'd'))
			out("energy bk pt: "   + format(sbackpt, 'd'))
			out("op flags:     "   + format(flags, '02x'))
			printOpFlags(flags)
			return 1
		else:
			out(self.name + " got ack, waiting for ext msg!")
			return 0

				
class ReadData1bMsgHandler(MsgHandler):
	def __init__(self, n = "ReadData1bMsgHandler"):
		self.name = n
	def processMsg(self, msg):
		out(self.name + " got: " + msg.toString())
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out("unexpected msg!")
			return 0
		if msg.isExtended():
			humhigh = msg.getByte("userData4") & 0xFF
			humlow  = msg.getByte("userData5") & 0xFF
			fwv     = msg.getByte("userData6") & 0xFF
			coolpt  = msg.getByte("userData7") & 0xFF
			heatpt  = msg.getByte("userData8") & 0xFF
			rfoff   = msg.getByte("userData9") & 0xFF
			esspt   = msg.getByte("userData10") & 0xFF
			stage1  = msg.getByte("userData11") & 0xFF
			srenab  = msg.getByte("userData12") & 0xFF
			extpwr  = msg.getByte("userData13") & 0xFF
			exttmp  = msg.getByte("userData14") & 0xFF

			out("stage 1 mins: "   + format(stage1, 'd'))
			out("hum low:      "   + format(humlow, 'd'))
			out("hum high:     "   + format(humhigh, 'd'))
			out("fw revision:  "   + format(fwv, '02x'))
			out("coolpt:       "   + format(coolpt, 'd'))
			out("heatpt:       "   + format(heatpt, 'd'))
			out("rf offset:    "   + format(rfoff, 'd'))
			out("en sv set pt: "   + format(esspt, 'd'))
			out("stat rep enb: "   + format(srenab, 'd'))
			out("ext pwr on:   "   + format(extpwr, 'd'))
			out("ext tmp opt:  "   + format(exttmp, 'd'))
			return 1
		else:
			out(self.name + " got ack, waiting for ext msg!")
			return 0
				
class DumpDataMsgHandler(MsgHandler):
	def __init__(self, n = "DumpDataMsgHandler"):
		self.name = n
	def processMsg(self, msg):
		out(self.name + " got: " + msg.toString())
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out(self.name + " got unexpected msg!")
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
			out(self.name + " got ack, waiting for ext msg!")
			return 0


class ReadData2MsgHandler(MsgHandler):
	def __init__(self, n = "ReadData2MsgHandler"):
		self.name = n
	def processMsg(self, msg):
		out(self.name + " got msg: " + msg.toString())
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out("unexpected msg!")
			return 0
		if msg.isExtended():
			out("time:         " + getTime(msg))
			mode   = msg.getByte("userData6") & 0xFF
			coolpt = msg.getByte("userData7") & 0xFF
			hum    = msg.getByte("userData8") & 0xFF
			temp   = msg.getByte("userData10") & 0xFF
			temp  |= (msg.getByte("userData9") & 0xFF) << 8
			stat   = msg.getByte("userData11") & 0xFF
			heatpt = msg.getByte("userData12") & 0xFF
			out("temp [C]:     "   + format(temp * 0.1, 'f'))
			out("humidity:     "   + format(hum, 'd'))
			out("sysmode:      "   + format((mode & 0xF0) >> 4, '02x'))
			out("fanmode:      "   + format((mode & 0x0F) >> 0, '02x'))
			out("cool pt:      "   + format(coolpt, 'd'))
			out("heat pt:      "   + format(heatpt, 'd'))
			out("status:       "   + format(stat, '02x'))
			return 1
		else:
			out(self.name + " got ack, waiting for ext msg!")
			return 0

class ScheduleMsgHandler(MsgHandler):
	def __init__(self, n = "ScheduleMsgHandler"):
		self.name = n
	def processMsg(self, msg):
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out(self.name + " got unexpected msg: " + msg.toString())
			return 0
		if msg.isExtended():
			out(self.name + " got schedule: ")
			printScheduleMsg(msg)
			return 1
		else:
			out(self.name + " got ack, waiting for ext msg!")
			return 0

class SetScheduleMsgHandler(MsgHandler):
	day = 0
	period = 0 #wake, leave, return, sleep
	time = 0
	cool = 100
	heat = 0
	thermostat = None
	def __init__(self, thermostat, day, period, time, cool, heat):
		self.name = "SetScheduleMsgHandler"
		self.thermostat = thermostat
		self.day    = day
		self.period = period
		self.time   = SetScheduleMsgHandler.textToTime(time)
		self.cool   = cool
		self.heat   = heat
	def processMsg(self, msg):
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out(self.name + " got unexpected msg: " + msg.toString())
			return 0
		if msg.isExtended():
			out(self.name + " existing schedule:")
			printScheduleMsg(msg)
			idx  = 3 * self.period;
			data = message.getMsgData(msg)
			data = [(data[k] & 0xFF) for k in range(len(data))]
			data[idx]     = self.time & 0xFF
			data[idx + 1] = self.cool & 0xFF
			data[idx + 2] = self.heat & 0xFF
			nmsg = message.createExtendedMsg2(
				InsteonAddress(self.thermostat.address),
				0x2e, (0x03 + self.day) & 0xFF, data)
			out(self.name + " new schedule:")
			printScheduleMsg(nmsg)
			iofun.writeMsg(nmsg)
			out(self.name + " sent new schedule: " + nmsg.toString())
			return 1
		else:
			out(self.name + " got ack, waiting for ext msg!")
			return 0
	@staticmethod
	def textToTime(text):
		h, m  = text.split(':')
		return int(h) * 4 + int(int(m)/15)

class SetOperatingFlagsMsgHandler(MsgHandler):
	mask = 0
	bits = 0
	thermostat = None
	def __init__(self, th, mask, bits):
		self.name = "SetOperatingFlagsMsgHandler";
		self.thermostat = th
		self.mask = mask
		self.bits = bits
	def processMsg(self, msg):
		out(self.name + " got: " + msg.toString())
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out(self.name + " got unexpected msg!")
			return 0
		if msg.isExtended():
			flags = msg.getByte("userData13") & 0xFF
			out("got flags " + format(flags, '02x') + ", changing them")
			flags = (flags & ~self.mask) | self.bits
			self.thermostat.ext(0x2e, 0x00, [0x00, 0x04, 0x00, flags])
			return 1
		else:
			out(self.name + " got ack, waiting for ext msg!")
			return 0

class OpFlagsSDMsgHandler(MsgHandler):
	def __init__(self, n = "OpFlagsSDMsgHandler"):
		self.name = n
	def processMsg(self, msg):
		out("got opflags msg: " + msg.toString())
		tmp = msg.getByte("command2") & 0xFF
		out(" Prg. lock:  " + format((tmp >> 0) & 0x01, 'd'))
		out(" LED on TX:  " + format((tmp >> 1) & 0x01, 'd'))
		out(" Resume Dim: " + format((tmp >> 2) & 0x01, 'd'))
		out(" LED OFF:    " + format((tmp >> 3) & 0x01, 'd'))
		out(" LoadSense:  " + format((tmp >> 4) & 0x01, 'd'))
		return 1

class OpFlagsExtMsgHandler(MsgHandler):
	def __init__(self):
		self.name = "OpFlagsExtMsgHandler";
	def processMsg(self, msg):
		out(self.name + " got: " + msg.toString())
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out(self.name + " got unexpected msg!")
			return 0
		if msg.isExtended():
			flags = msg.getByte("userData13") & 0xFF
			printOpFlags(flags)
			return 1
		else:
			out(self.name + " got ack, waiting for ext msg!")
			return 0

class EnableStatusReportsMsgHandler(MsgHandler):
	def __init__(self, n = "EnableStatusReportsMsgHandler"):
		self.name = n
	def processMsg(self, msg):
		out("esrp got msg: " + msg.toString())
		tmp = msg.getByte("command1") & 0xFF
		if (tmp != 0x2e):
			out("esrp unexpected msg!")
			return 0
		if msg.isExtended():
			out("esrp got extended reply!");
			return 1
		else:
			out(self.name + " got ack!")
			return 1

class EngineVersionMsgHandler(MsgHandler):
	def __init__(self, n = "EngineVersionMsgHandler"):
		self.name = n
	def processMsg(self, msg):
		out(self.name + " got: " + msg.toString())
		tmp = msg.getByte("command2") & 0xFF
		out(" i2CS engine version:  " + format(tmp, '02x'))
		return 1

class FirmwareVersionMsgHandler(MsgHandler):
	def __init__(self, n = "FirmwareVersionMsgHandler"):
		self.name = n
	def processMsg(self, msg):
		out(self.name + " got: " + msg.toString())
		cmd1 = msg.getByte("command1") & 0xFF
		if cmd1 == 0x10:
			out(self.name + " got ack!")
			return 0
		elif cmd1 == 0x01:
			out("firmware version: " + msg.getAddress("toAddress").toString())
			return 1

class Thermostat2441TH(Device):
	"""==============  Insteon Thermostat 2441TH ==============="""
	def __init__(self, name, addr):
		Device.__init__(self, name, addr)
		self.dbbuilder = ThermostatDBBuilder(addr, self.db)
#
#   helper functions 
#
	def ext(self, cmd1, cmd2, data):
		return self.querier.queryext(cmd1, cmd2, data)
	def ext2(self, cmd1, cmd2, data):
		return self.querier.queryext2(cmd1, cmd2, data)

	def sendext2(self, cmd1, cmd2, data):
		msg = message.createExtendedMsg2(InsteonAddress(self.address),
										  cmd1, cmd2, data)
		self.__sendMsg(msg);
		return msg;

	def __sendMsg(self, msg):
		iofun.writeMsg(msg)
		out("sent msg: " + msg.toString())

	def __sd(self, cmd1, cmd2):
		return self.querier.querysd(cmd1, cmd2)

	def __bcast(self, group, cmd1, cmd2):
		msg = Msg.s_makeMessage("SendStandardMessage")
		flags = 0xcf
		adr = InsteonAddress(0x00, 0x00, group & 0xFF)
		msg.setAddress("toAddress", adr)
		msg.setByte("messageFlags", flags)
		msg.setByte("command1", cmd1)
		msg.setByte("command2", cmd2)
		iofun.writeMsg(msg)

	def __setOperatingFlags(self, mask, bits):
		self.querier.setMsgHandler(SetOperatingFlagsMsgHandler(self, mask,bits))
		# Send query message that will yield the current flags.
		# Upon receipt of answer, the handler will set the flags
		self.ext(0x2e, 0, [0x00, 0x00, 0x00]) # send query

	def __setMode(self, mode):
		self.querier.setMsgHandler(MsgHandler("got mode set return msg"))
		self.ext(0x6b,  mode, [0x0, 0x0, 0x0])

		
#
#   misc simple commands
#
	def ping(self):
		"""ping()
		pings the device"""
		self.querier.setMsgHandler(MsgHandler("ping"))
		self.__sd(0x0f, 0)
	def beep(self):
		"""beep()
		sends beep command to the device"""
		msg = message.createStdMsg(
			InsteonAddress(self.address), 0x0f, 0x30, 0x00, -1);
		iofun.writeMsg(msg)
	def sendOn(self): #  send ON bcast on group #1 (see if thermostat responds)
		"""sendOn()
		sends on command to the device"""
		self.__bcast(0x01, 0x11, 0x00)
	def sendOff(self): # send OFF bcast on group #1
		"""sendOff()
		sends off command to the device"""
		self.__bcast(0x01, 0x13, 0x00)

#
#   methods for querying the device
#
	def getFirmwareVersion(self):
		"""getFirmwareVersion()
		queries device for firmware version"""
		self.querier.setMsgHandler(FirmwareVersionMsgHandler())
		self.__sd(0x10, 0x00)
	def getEngineVersion(self):
		"""getEngineVersion()
		queries device for engine version"""
		self.querier.setMsgHandler(EngineVersionMsgHandler())
		self.__sd(0x0d, 0x00)
	def getTemperature(self):
		"""getTemperature()
		queries temperature"""
		self.querier.setMsgHandler(StatusInfoMsgHandler("temperature", 0.5))
		self.__sd(0x6a, 0x00)
	def getHumidity(self):
		"""getHumidity()
		queries humidity"""
		self.querier.setMsgHandler(StatusInfoMsgHandler("humidity"))
		self.__sd(0x6a, 0x60)
	def getSetPoint(self):
		"""getSetPoint()
		queries temperature set point"""
		self.querier.setMsgHandler(StatusInfoMsgHandler("setpoint", 0.5))
		self.__sd(0x6a, 0x20)
	def getOpFlagsSD(self):
		"""getOpFlagsSD()
		gets operational flags via sd message"""
		self.querier.setMsgHandler(OpFlagsSDMsgHandler())
		self.__sd(0x1f, 0x00)
	def getOpFlagsExt(self):
		"""getOpFlagsExt()
		gets operational flags via ext message"""
		self.querier.setMsgHandler(OpFlagsExtMsgHandler())
		self.ext(0x2e, 0, [0x00, 0x00, 0x00])
	def getSchedule(self, day):
		"""getSchedule(day)
		gets schedule for day (0=Sunday, 6=Saturday)"""
		self.querier.setMsgHandler(ScheduleMsgHandler())
		self.ext2(0x2e, 0x0A + 2 * day, [0x00])
	def getData1(self):
		"""getData1()
		performs data1 query"""
		self.querier.setMsgHandler(ReadData1MsgHandler())
		self.ext(0x2e, 0, [0x00, 0x00, 0x00])
	def getData1b(self): # only documented in the 2441ZTH notes!
		"""getData1b()
		performs data1b query"""
		self.querier.setMsgHandler(ReadData1bMsgHandler())
		self.ext(0x2e, 0, [0x00, 0x00, 0x01])
	def getData2(self):
		"""getData2()
		performs data2 query"""
		self.querier.setMsgHandler(ReadData2MsgHandler())
		self.ext2(0x2e, 0x02, [00, 0x00, 0x00])
#
#   methods to change settings
#
	def enableStatusReports(self):
		"""enableStatusReports()
		enables status reports being sent to group #0xef"""
		self.querier.setMsgHandler(EnableStatusReportsMsgHandler())
		self.ext(0x2e, 0, [0x00, 0x08, 0x00])
	def linkingLockOn(self):
		"""linkingLockOn()
		sets linking lock on"""
		self.__setOperatingFlags(0x01 << 0, 0x01 << 0)
	def linkingLockOff(self):
		"""linkingLockOff()
		sets linking lock off"""
		self.__setOperatingFlags(0x01 << 0, 0x00 << 0)
	def buttonBeepOn(self):
		"""buttonBeepOn()
		sets button beep on"""
		self.__setOperatingFlags(0x01 << 1, 0x01 << 1)
	def buttonBeepOff(self):
		"""buttonBeepOff()
		sets button beep off"""
		self.__setOperatingFlags(0x01 << 1, 0x00 << 1)
	def buttonLockOn(self):
		"""buttonLockOn()
		sets button lock on"""
		self.__setOperatingFlags(0x01 << 2, 0x01 << 2)
	def buttonLockOff(self):
		"""buttonLockOff()
		sets button lock off"""
		self.__setOperatingFlags(0x01 << 2, 0x00 << 2)
	def useFahrenheit(self):
		"""useFahrenheit()
		set temperature display in fahrenheit"""
		self.__setOperatingFlags(0x01 << 3, 0x00 << 3)
	def useCelsius(self):
		"""useCelsius()
		set temperature display in celsius"""
		self.__setOperatingFlags(0x01 << 3, 0x01 << 3)
	def use24hFormat(self):
		"""use24hFormat()
		set time format 24h"""
		self.__setOperatingFlags(0x01 << 4, 0x01 << 4)
	def use12hFormat(self):
		"""use12hFormat()
		set time format 12h"""
		self.__setOperatingFlags(0x01 << 4, 0x00 << 4)
	def statusLEDOn(self):
		"""statusLEDOn()
		switch status LED on when heating/cooling"""
		self.__setOperatingFlags(0x01 << 6, 0x01 << 6)
	def statusLEDOff(self):
		"""statusLEDOff()
		don't switch status LED on when heating/cooling"""
		self.__setOperatingFlags(0x01 << 6, 0x00 << 6)
	def setTemperatureOffset(self, offset):
		"""setTemperatureOffset(offset)
		set temperature offset(for calibration, use with care!)"""
		self.querier.setMsgHandler(MsgHandler("set temp offset return msg:"))
		self.ext(0x2e, 0, [0x01, 0x02, offset])
	def setHumidityOffset(self, offset):
		"""setHumidityOffset(offset)
		set humidity offset(for calibration, use with care!)"""
		self.querier.setMsgHandler(MsgHandler("set humidity offset return msg:"))
		self.ext(0x2e, 0, [0x01, 0x03, offset])
	def setBacklightSeconds(self, time):
		"""setBacklightSeconds(time)
		set backlight time in seconds"""
		self.querier.setMsgHandler(MsgHandler("set backlight secs return msg:"))
		self.ext(0x2e, 0, [0x01, 0x05, time])
	def setStage1Minutes(self, time):
		"""setStage1Minutes(time)
		set number of minutes to try stage 1 before going into stage2"""
		self.querier.setMsgHandler(MsgHandler("set stage 1 mins return msg:"))
		self.ext(0x2e, 0, [0x01, 0x0A, time])
	def setACHysteresis(self, mins):
		"""setACHysteresis(minutes)
		set A/C hysteresis (in minutes)"""
		self.querier.setMsgHandler(MsgHandler("set a/c hysteresis return msg:"))
		self.ext(0x2e, 0, [0x01, 0x06, mins])
	def setTime(self, day, hour, min, sec):
		"""setTime(day, hour, min, sec)
		sets clock time (day = 0(Sunday) .. 6 (Saturday)) """
		self.querier.setMsgHandler(MsgHandler("set time return msg:"))
		self.ext2(0x2e, 0x02, [0x02, day, hour, min,  0,  sec])
	def setSchedule(self, day, period, time, cool, heat):
		"""setSchedule(day, period, time, cool, heat)
		sets schedule params: day = 0(Sunday) .. 6 (Saturday), period = (0=wake, 1=leave, 2=return, 3=sleep), time = (e.g.) "06:30", cool/heat = temperatures"""
		self.querier.setMsgHandler(
			SetScheduleMsgHandler(self, day, period, time, cool, heat))
		# query will trigger the handler to send command
		self.ext2(0x2e, 0x0A + 2 * day, [0x00])
	def setCoolPoint(self, temp):
		"""setCoolPoint(temp)
		sets cooling temperature"""
		self.querier.setMsgHandler(MsgHandler("set cool point"))
		self.ext(0x6c,  temp * 2, [0x0, 0x0, 0x0])
	def setHeatPoint(self, temp):
		"""setHeatPoint(temp)
		sets heating temperature"""
		self.querier.setMsgHandler(MsgHandler("set heat point"))
		self.ext(0x6d,  temp * 2, [0x0, 0x0, 0x0])
	def setHumidityHighPoint(self, point):
		"""setHumidityHighPoint(point)
		sets high point for dehumidification"""
		self.querier.setMsgHandler(MsgHandler("set humidity high pt"))
		self.ext(0x2e, 0, [0x01, 0x0b, point])
	def setHumidityLowPoint(self, point):
		"""setHumidityLowPoint(point)
		sets low point for humidification"""
		self.querier.setMsgHandler(MsgHandler("set humidity low pt"))
		self.ext(0x2e, 0, [0x01, 0x0c, point])
#
#   commands to switch the mode
#
	def setToHeat(self):
		"""setToHeat()
		set system mode to HEAT"""
		self.__setMode(0x04)
	def setToCool(self):
		"""setToCool()
		set system mode to COOL"""
		self.__setMode(0x05)
	def setToAuto(self):
		"""setToAuto()
		set system mode to AUTO (manual)"""
		self.__setMode(0x06)
	def setAllOff(self):
		"""setAllOff()
		set system mode to OFF"""
		self.__setMode(0x09)
	def setToProgram(self):
		"""setToProgram()
		set system mode to AUTO (program)"""
		self.__setMode(0x0A)
	def setFanOn(self):
		"""setFanOn()
		set fan mode to ALWAYS ON"""
		self.__setMode(0x07)
	def setFanAuto(self):
		"""setFanAuto()
		set fan mode to AUTO"""
		self.__setMode(0x08)
#
#   link database management
#
	def addSoftwareController(self, addr):
		"""addSoftwareController(addr)
		add device with "addr" as software controller"""
		self.addController(addr, 0xef, [0x03, 0x1f, 0xef])
	def removeSoftwareController(self, addr):
		"""removeSoftwareController(addr)
		remove device with "addr" as software controller"""
		self.addController(addr, 0xef, [0x03, 0x1f, 0xef])
		self.removeController(addr, 0xef)
#
#  stuff that should work but doesn't. Maybe just for the battery operated ZTH?
#
	def stayAwake(self): # stay awake for 4mins
		self.querier.setMsgHandler(MsgHandler("got stay awake return msg:"))
		self.ext(0x20,  0x06, [0x0, 0x0, 0x0])
	def goToSleep(self): # go to sleep after 3 seconds
		self.querier.setMsgHandler(MsgHandler("got go to sleep msg:"))
		self.ext(0x20,  0x07, [0x0, 0x0, 0x0])

