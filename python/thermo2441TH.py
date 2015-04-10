import commands

from device import Device

class Thermo2441TH(Device):
    def __init__(self, name, adr):
        Device.__init__(self, name, adr)