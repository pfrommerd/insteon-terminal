from .operation import port_operator

from . import linkdb as linkdb

import insteon.util as util

class DeviceRegistry:
    def __init__(self):
        self.by_name = {}
        self.by_addr = {}

    def register(self, device):
        if device.name:
            self.by_name[device.name] = device
        if device.addr:
            self.by_addr[device.addr] = device

    def get_by_name(self, name):
        if name in self.by_name:
            return self.by_name[name]
        else:
            return None

    def get_by_addr(self, addr):
        if addr in self.by_addr:
            return self.by_addr[addr]
        else:
            return None

class Device:
    s_default_modem = None
    s_default_registry = DeviceRegistry() # A basic default registry

    @staticmethod
    def s_set_default_modem(modem):
        Device.s_default_modem = modem

    @staticmethod
    def s_set_default_registry(registry):
        Device.s_default_registry = registry


    def __init__(self, name=None, addr=None, modem=None, registry=None):
        self.name = name
        self.addr = addr

        self.linkdb_cache = linkdb.LinkDB()

        self._modem = modem if modem else Device.s_default_modem
        self._registry = registry if registry else Device.s_default_registry
        
        # Add to registry
        self._registry.register(self)


    @port_operator
    def send_cmd(self, port, cmd1, cmd2):
        msg = port.defs['SendStandardMessage'].create()
        msg['toAddress'] = self.addr
        msg['command1'] = cmd1
        msg['command2'] = cmd2

        # Write the message
        ack_reply = util.Channel()
        port.write(msg, ack_reply_channel=ack_reply)
        # Wait for the ack for a second before
        # giving up
        ack_reply.wait(1)

    @port_operator
    def update_linkdb_cache(self, port):
        pass

