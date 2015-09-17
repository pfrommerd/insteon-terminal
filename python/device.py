#-------------------------------------------------------------------------------
#
# base class for all devices
#

from us.pfrommer.insteon.cmd.msg import InsteonAddress
from linkdb import DB
from all_devices import *

class Device:
	name = ""
	address = InsteonAddress()
	db      = None
	def __init__(self, name, adr):
		self.name = name
		self.address = adr
		self.db = DB()
		addDev(self)

	def getName(self):
		return self.name

	def getAddress(self):
		return self.address
