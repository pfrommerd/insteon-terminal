from .device import Device
from ..util import port_resolver

class Light(Device):
    def __init__(self, name=None, addr=None, modem=None, registry=None):
        super().__init__(name, addr, modem, registry)

    @port_resolver('port')
    def set_on(self, port=None):
        self.send_cmd(0x12, 0xFF, port=port)

    @port_resolver('port')
    def set_off(self, port=None):
        self.send_cmd(0x13, 0x00, port=port)
