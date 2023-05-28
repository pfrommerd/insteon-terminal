"""
DefaultMsgHandler

This handler provides default message handling by sending message to standard out.
"""

import iofun

from python.querier import MsgHandler

def out(msg = ""):
    iofun.out(msg)

class DefaultMsgHandler(MsgHandler):
    label = None
    def __init__(self, l):
            self.label = l
    def processMsg(self, msg):
            out(self.label + " got msg: " + msg.toString())
            return 1
