
from . import linkdb

from .device import Device
from ..util import Channel

from contextlib import contextmanager

import logbook
logger = logbook.Logger(__name__)

class Modem(Device):
    # Query for the address...
    def __init__(self, port):
        self.port = port

        addr = (0x00, 0x00, 0x00)
        # Query for the modem address
        addr_query = port.defs['GetIMInfo'].create()

        reply_channel = Channel()
        port.write(addr_query, ack_reply_channel=reply_channel)
        if reply_channel.wait(5): # Wait for a reply
            msg = reply_channel.recv()
            addr = msg['IMAddress']

        super().__init__(addr)

        # Add the features
        from .dbmanager import ModemDBManager
        self.add_feature('db', ModemDBManager(port))

    @contextmanager
    def bind(self): # Binds as the default conduit
        cond = Device.s_bound_conduit
        Device.s_bound_conduit = self
        yield
        Device.s_bound_conduit = cond
