# ------------------------------------------------------------------------------
#
# helper methods for message creation and manipulation
#
# creates a send standard message Msg
# if group is -1, the address will be used, otherwise the group will be used
#
from us.pfrommer.insteon.cmd.msg import Msg
import commands

def createStdMsg(adr, flags, cmd1, cmd2, group):
	msg = Msg.s_makeMessage("SendStandardMessage")
	if group != -1:
		flags |= 0xc0
		adr = InsteonAddress(0x00, 0x00, group & 0xFF)
	msg.setAddress("toAddress", adr)
	msg.setByte("messageFlags", flags)
	msg.setByte("command1", cmd1)
	msg.setByte("command2", cmd2)
	return msg

def setMsgData(msg, data):
	msg.setByte("userData1", data[0] & 0xFF)
	msg.setByte("userData2", data[1] & 0xFF)
	msg.setByte("userData3", data[2] & 0xFF)
	msg.setByte("userData4", data[3] & 0xFF)
	msg.setByte("userData5", data[4] & 0xFF)
	msg.setByte("userData6", data[5] & 0xFF)
	msg.setByte("userData7", data[6] & 0xFF)
	msg.setByte("userData8", data[7] & 0xFF)
	msg.setByte("userData9", data[8] & 0xFF)
	msg.setByte("userData10", data[9] & 0xFF)
	msg.setByte("userData11", data[10] & 0xFF)
	msg.setByte("userData12", data[11] & 0xFF)
	msg.setByte("userData13", data[12] & 0xFF)
	msg.setByte("userData14", data[13] & 0xFF)

def getMsgData(msg):
	data = [0] * 14;
	data[0] =  msg.getByte("userData1");
	data[1] =  msg.getByte("userData2");
	data[2] =  msg.getByte("userData3");
	data[3] =  msg.getByte("userData4");
	data[4] =  msg.getByte("userData5");
	data[5] =  msg.getByte("userData6");
	data[6] =  msg.getByte("userData7");
	data[7] =  msg.getByte("userData8");
	data[8] =  msg.getByte("userData9");
	data[9] =  msg.getByte("userData10");
	data[10] =  msg.getByte("userData11");
	data[11] =  msg.getByte("userData12");
	data[12] =  msg.getByte("userData13");
	data[13] =  msg.getByte("userData14");
	return data

def populateMsg(msg, adr, cmd1, cmd2, data):
	for n in range(len(data), 14):
		data.append(0x00)
	msg.setAddress("toAddress", adr)
	msg.setByte("command1", cmd1)
	msg.setByte("command2", cmd2)
	setMsgData(msg, data)

def createExtendedMsg(adr, cmd1, cmd2, data, flags = 0x1f):
	msg = Msg.s_makeMessage("SendExtendedMessage")
	populateMsg(msg, adr, cmd1, cmd2, data)
	msg.setByte("messageFlags", flags | 0x10)
	checksum = (~(cmd1 + cmd2 + sum(data)) + 1) & 0xFF
	msg.setByte("userData14", checksum)
	return msg

def createExtendedMsg2(adr, cmd1, cmd2, data, flags = 0x1f):
	msg = Msg.s_makeMessage("SendExtendedMessage")
	populateMsg(msg, adr, cmd1, cmd2, data)
	msg.setByte("messageFlags", flags | 0x10)
	crc = calcCRC(msg)
	crcLow   = crc & 0xFF
	crcHigh  = (crc >> 8) & 0xFF
	msg.setByte("userData13", int(crcHigh & 0xFF))
	msg.setByte("userData14", int(crcLow & 0xFF))
	return msg

def calcCRC(msg):
	bytes = msg.getBytes("command1", 14);
	crc = int(0);
	for loop in xrange(0, len(bytes)):
		b = bytes[loop] & 0xFF
		for bit in xrange(0, 8):
			fb = b & 0x01
			fb = fb ^ 0x01 if (crc & 0x8000) else fb
			fb = fb ^ 0x01 if (crc & 0x4000) else fb
			fb = fb ^ 0x01 if (crc & 0x1000) else fb
			fb = fb ^ 0x01 if (crc & 0x0008) else fb
			crc = ((crc << 1) | fb) & 0xFFFF;
			b = b >> 1
	return crc
