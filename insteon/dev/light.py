from .device import Device
from .operation import operator

class Light(Device):
    def __init__(self, name, addr, modem=None):
        super().__init__(name, addr, modem)

    @operator
    def set_on(self, port):
        self.send_cmd(port, 0x12, 0xFF)

    @operator
    def set_off(self, port):
        self.send_cmd(port, 0x13, 0x00)
