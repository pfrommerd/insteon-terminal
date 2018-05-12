from .device import Device

class Modem(Device):
    def __init__(self, name, port):
        self.port = port

        super().__init__(name, (0x00, 0x00, 0x00), self)
