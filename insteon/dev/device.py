import insteon.util as util

from contextlib import contextmanager

class NetworkConfig:
    def __init__(self):
        self.dev_by_name = {}
        self.dev_by_addr = {}
        self.name_by_addr = {}

        self.conduits = {}

    def register_device(self, name, device):
        self.dev_by_name[name] = device
        self.dev_by_addr[device.addr] = device
        self.name_by_addr[device.addr] = name

    # Registers a device as reachable through a modem "conduit"
    def register_conduit(self, addr, modem):
        if addr not in self.conduits:
            self.conduits[addr] = []
        self.conduits[addr].append(modem)

    def conduit_of(self, addr):
        if addr not in self.conduits:
            return None
        else:
            return self.conduits[addr][0]

    def port_of(self, addr):
        if addr not in self.conduits:
            return None
        else:
            # Get the port of the conduit
            return self.conduits[addr][0].port

    # TODO: Make thread safe with locks
    @contextmanager
    def bind(self):
        reg = Device.s_bound_netconf
        Device.s_bound_netconf = self
        yield
        Device.s_bound_netconf = reg

class Device:
    s_bound_conduit = None
    s_bound_netconf = None

    def __init__(self, addr=None):
        self.addr = addr
        self.features = {}

        self._network = None

    @property
    def primary_port(self):
        # For modem-like devices
        if hasattr(self, 'port'):
            return self.port

        if not self._network:
            return None
        return self._network.port_of(self.addr)

    # Can provide a custom conduit/network to register with
    # or can use the currently bound one
    def register(self, name, conduit=None, network=None):
        network = network if network else Device.s_bound_netconf

        if self._network or network:
            if not self._network:
                self._network = network

            conduit = conduit if conduit else Device.s_bound_conduit
            if conduit:
                self._network.register_conduit(self.addr, conduit)

        return self

    def add_feature(self, name, feature):
        setattr(self, name, feature)
        self.features[name] = feature
