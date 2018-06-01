from .device import Device
from ..util import port_resolver, Channel, InsteonError

from ..io.msg import MsgType

""" A generic device represents a device
    on the insteon network, while other devices
    may include things such as modems, which do not live on
    the insteon network
"""
class GenericDevice(Device):
    def __init__(self, name=None, addr=None, modem=None, registry=None):
        super().__init__(name, addr, modem, registry)

    @port_resolver('port')
    def send_stdmsg(self, cmd1, cmd2, flags=MsgType.DIRECT, port=None):
        msg = port.defs['SendStandardMessage'].create()
        msg['toAddress'] = self.addr
        msg['messageFlags'] = flags.value
        msg['command1'] = cmd1
        msg['command2'] = cmd2

        # Write the message
        ack_reply = Channel() 

        port.write(msg, ack_reply_channel=ack_reply)

        # Wait for the ack for a second before
        # giving up
        return ack_reply

    # Query sd both sends a standard, direct command
    # and will return a channel to the response ack msg
    # (and will wait for the modem ack
    @port_resolver('port')
    def send_query_sd(self, cmd1, cmd2, wait_response=False, extra_channels=[], port=None):
        msg = port.defs['SendStandardMessage'].create()
        msg['toAddress'] = self.addr
        msg['messageFlags'] = MsgType.DIRECT.value
        msg['command1'] = cmd1
        msg['command2'] = cmd2

        direct_ack_channel = Channel(lambda x: MsgType.from_value(x['messageFlags']) ==
                                                MsgType.ACK_OF_DIRECT)
        ack_reply = Channel()

        extras = [direct_ack_channel]
        extras.extend(extra_channels)

        port.write(msg, ack_reply_channel=ack_reply, custom_channels=extras)

        if not ack_reply.wait(1):
            raise InsteonError('No IM reply to send command!')

        if wait_response:
            if not direct_ack_channel.wait(1):
                raise InsteonError('No response to SD query received')

        return direct_ack_channel

    @port_resolver('port')
    def request_id(self, port=None):
        id_channel = Channel(lambda x: MsgType.from_value(x['messageFlags']) ==
                                        MsgType.BROADCAST and x['command1'] == 0x01)
        self.send_query_sd(0x10,0x00, wait_response=True, extra_channels=[id_channel])

        id_info = id_channel.recv(1)
        if not id_info:
            raise InsteonError('No ID info message received after request sent')
        return (id_info['toAddress'][0],id_info['toAddress'][1],id_info['toAddress'][2],
                    id_info['command2'])

    @port_resolver('port')
    def request_id_str(self, port=None):
        id_result = self.request_id(port=port)

        if id_result:
            return '0x{:02X}:0x{:02X}[{}|{}]'.format(*id_result)
        else:
            return None
