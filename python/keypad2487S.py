import commands

from device import Device
from commands import insteon
from threading import Timer

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

class keypad2487S(Device):
    def __init__(self, name, addr):
        Device.__init__(self, name, addr)
