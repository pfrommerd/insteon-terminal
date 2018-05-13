from .device import Device
from .operation import port_operator

class Light(Device):
    def __init__(self, name=None, addr=None, modem=None, registry=None):
        super().__init__(name, addr, modem, registry)

    @port_operator
    def set_on(self, port):
        self.send_cmd(port, 0x12, 0xFF)

    @port_operator
    def set_off(self, port):
        self.send_cmd(port, 0x13, 0x00)
