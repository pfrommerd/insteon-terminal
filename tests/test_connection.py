import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import serial
import time

from insteon.msg.port import *
from insteon.msg.msg import *

import insteon.util as util
import insteon.msg.xmlmsgreader as xmlreader

definitions = xmlreader.read_xml(os.path.join(os.path.dirname(__file__),'../res/msg_definitions.xml'))

conn = serial.Serial('/dev/ttyUSB0', 19200, timeout=0.1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=8)


port = Port(conn, definitions)
port.notify_on_read(lambda x: print('Read: {}'.format(x)))
port.notify_on_write(lambda x: print('Wrote: {}'.format(x)))

msg = definitions['CancelALLLinking'].create()

acked = util.Channel()
port.write(msg,ack_reply_channel=acked)

reply = acked.recv()
print('Reply: {}'.format(reply))

port.detach()
