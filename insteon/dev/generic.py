from .device import Device
from ..util import Channel, InsteonError

from ..io.msg import MsgType

""" A generic device represents a device
    on the insteon network, while other devices
    may include things such as modems, which do not live on
    the insteon network
"""
class GenericDevice(Device):
    def __init__(self, name=None, addr=None, modem=None, registry=None):
        super().__init__(name, addr, modem, registry)

    def request_id(self, port=None):
        id_channel = Channel(lambda x: MsgType.from_value(x['messageFlags']) ==
                                        MsgType.BROADCAST and x['command1'] == 0x01)
        self.send_query_sd(0x10,0x00, wait_response=True, extra_channels=[id_channel])

        id_info = id_channel.recv(1)
        if not id_info:
            raise InsteonError('No ID info message received after request sent')
        return (id_info['toAddress'][0],id_info['toAddress'][1],id_info['toAddress'][2],
                    id_info['command2'])

    def request_id_str(self, port=None):
        id_result = self.request_id(port=port)

        if id_result:
            return '0x{:02X}:0x{:02X}[{}|{}]'.format(*id_result)
        else:
            return None
