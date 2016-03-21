#-------------------------------------------------------------------------------
#
# Insteon Thermostat 2441V
#

from thermostat import Thermostat


class Thermostat2441V(Thermostat):
	"""==============  Insteon Thermostat 2441V ==============="""
	def __init__(self, name, addr):
		Thermostat.__init__(self, name, addr, 0x0fff)
