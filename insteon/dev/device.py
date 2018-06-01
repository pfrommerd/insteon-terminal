from ..util import port_resolver

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

        # Prevent circular import
        self._modem = modem if modem else Device.s_default_modem
        self._registry = registry if registry else Device.s_default_registry
        
        self.dbcache = linkdb.LinkDB()

        # Add to registry only if name and addr is set
        if name and addr:
            self._registry.register(self)

    # To be overridden by implementing devices
    @port_resolver('port')
    def update_dbcache(self, targetdb=None, port=None):
        logger.warning('STUB: update_dbcache()')

    @port_resolver('port')
    def flash_dbcache(self, srcdb=None, port=None):
        logger.warning('STUB: flash_dbcache()')
