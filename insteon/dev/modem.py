from .device import Device
from .operation import port_operator

from insteon.msg.msg import MsgDef

from .. import util as util

class Modem(Device):
    def __init__(self, port, name=None, registry=None):
        self.port = port

        addr = (0x00, 0x00, 0x00)
        # Query for the modem address
        addr_query = port.defs['GetIMInfo'].create()

        reply_channel = util.Channel()
        port.write(addr_query, ack_reply_channel=reply_channel)
        if reply_channel.wait(5): # Wait for a reply
            msg = reply_channel.recv()
            addr = msg['IMAddress']

        super().__init__(name, addr, self, registry)

    # Override the update linkdb function
    @port_operator
    def update_linkdb_cache(self, port):
        # Clear the database
        self.linkdb_cache.clear()

        reply_channel = util.Channel()
        done_channel = util.Channel(lambda x: (x['type'] == 'GetFirstALLLinkRecordReply' or \
                                              x['type'] == 'GetNextALLLinkRecordReply') and \
                                              x['ACK/NACK'] == 0x15)
        record_channel = util.Channel(lambda x: x['type'] == 'ALLLinkRecordResponse')


        # Now send the first message
        port.write(port.defs['GetFirstALLLinkRecord'].create(), ack_reply_channel=reply_channel,
                        custom_channels=[done_channel, record_channel])

        success = False
        while reply_channel.recv(5): # Wait at most 5 seconds for some reply
            if done_channel.has_activated: # If the reply says we are done, exit
                success = True
                break
            # Wait another 2 seconds for the record
            msg = record_channel.recv(2)
            if not msg:
                success = False
                break
            # Request the next one
            port.write(port.defs['GetNextALLLinkRecord'].create(),
                        ack_reply_channel=reply_channel)

        port.unregister_on_read(done_channel)
        port.unregister_on_read(record_channel)

        return success
