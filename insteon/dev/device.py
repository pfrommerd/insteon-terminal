from .operation import operator

import insteon.util as util

class Device:
    def __init__(self, name=None, addr=None, modem=None):
        self.name = name
        self.addr = addr
        self._modem = modem if modem else Device.s_default_modem


    @operator
    def send_cmd(self, port, cmd1, cmd2):
        msg = port.defs['SendStandardMessage'].create()
        msg['toAddress'] = self.addr
        msg['command1'] = cmd1
        msg['command2'] = cmd2

        # Write the message
        ack_reply = util.Event()
        port.write(msg, ack_reply_event=ack_reply)
        # Wait for the ack
        ack_reply.wait()

    s_default_modem = None
    @staticmethod
    def s_set_default_modem(modem):
        Device.s_default_modem = modem
