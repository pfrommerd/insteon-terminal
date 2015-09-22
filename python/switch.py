#-------------------------------------------------------------------------------
#
# Base class for all switches
#
import iofun
import message

from us.pfrommer.insteon.cmd.msg import InsteonAddress
from light import Light

class Switch(Light):
	def __init__(self, name, adr):
		Light.__init__(self, name, adr)
