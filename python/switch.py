#-------------------------------------------------------------------------------
#
# Base class for all switches
#
import iofun
import message

from us.pfrommer.insteon.cmd.msg import InsteonAddress
from device import Device

class Switch(Device):
	def __init__(self, name, adr):
		Device.__init__(self, name, adr)
	def on(self, level=0xFF):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x11, level, -1))
	def off(self):
		iofun.writeMsg(message.createStdMsg(
			InsteonAddress(self.getAddress()), 0x0F, 0x13, 0x00, -1))
