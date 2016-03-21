#-------------------------------------------------------------------------------
#
# Insteon Thermostat 2441TH
#

from thermostat import Thermostat

class Thermostat2441TH(Thermostat):
	"""==============  Insteon Thermostat 2441TH ==============="""
	def __init__(self, name, addr):
		Thermostat.__init__(self, name, addr, 0x1fff)
