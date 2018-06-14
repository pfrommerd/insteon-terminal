
class Querier:
    def __init__(self, device):
        self._device = device

    def send_stdmsg(self, cmd1, cmd2, flags=MsgType.DIRECT, port=None):
        port = port if port else self._device

        msg = port.defs['SendStandardMessage'].create()
        msg['toAddress'] = self.addr
        msg['messageFlags'] = flags.value
        msg['command1'] = cmd1
        msg['command2'] = cmd2

        # Write the message
        ack_reply = Channel() 

        port.write(msg, ack_reply_channel=ack_reply)

        return ack_reply

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
