import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import serial
import time
import threading

from insteonterminal.msg.port import *
from insteonterminal.msg.msg import *

import insteonterminal.msg.xmlmsgreader as xmlreader

definitions = xmlreader.read_xml(os.path.join(os.path.dirname(__file__),'../res/msg_definitions.xml'))

conn = serial.Serial('/dev/ttyUSB0', 19200, timeout=0.1, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=8)


port = Port(conn, definitions)
port.add_read_listener(print)
port.add_write_listener(print)

msg = definitions['CancelALLLinking'].create()

time.sleep(0.1)

acked = threading.Event()
port.write(msg,ack_reply_event=acked)
acked.wait()

time.sleep(10)

port.detach()
