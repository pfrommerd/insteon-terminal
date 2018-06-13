from .device import Device

class Light(Device):
    def __init__(self, addr):
        super().__init__(addr)

    def set_on(self, port=None):
        self.send_stdmsg(0x12, 0xFF, port=port)

    def set_off(self, port=None):
        self.send_stdmsg(0x13, 0x00, port=port)
