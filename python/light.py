import commands

from device import Device

class Light(Device):
    def __init__(self, name, adr):
        Device.__init__(self, name, adr)
    
    def on(self, level=0xFF):
        commands.writeMsg(commands.createStdMsg(self.getAddress(), 0x0F, 0x11, level, -1))
    
    def off(self):
        commands.writeMsg(commands.createStdMsg(self.getAddress(), 0x0F, 0x13, 0x00, -1))