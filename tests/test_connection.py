import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import serial
import time
import threading

from insteon.msg.port import *
from insteon.msg.msg import *

import insteon.msg.xmlmsgreader as xmlreader

definitions = xmlreader.read_xml(os.path.join(os.path.dirname(__file__),'../res/msg_definitions.xml'))

conn = serial.Serial('/dev/ttyUSB0', 19200, timeout=0.1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=8)


port = Port(conn, definitions)
port.add_read_listener(lambda x: print('Read: {}'.format(x)))
port.add_write_listener(lambda x: print('Wrote: {}'.format(x)))

msg = definitions['CancelALLLinking'].create()

acked = threading.Event()
port.write(msg,ack_reply_event=acked)
acked.wait()
print('Reply: {}'.format(acked.msg))

port.detach()
