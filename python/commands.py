#-------------------------------------------------------------------------------
#
# methods for accessing the terminal environment (I/O etc)
#

from java.lang import System
from threading import Timer
from us.pfrommer.insteon.cmd.hub import HubStream
from us.pfrommer.insteon.cmd.serial import SerialIOStream

from us.pfrommer.insteon.cmd import IOPort
from us.pfrommer.insteon.cmd.utils import Utils
from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress
from us.pfrommer.insteon.cmd.gui import PortTracker

import struct

insteon = None

# sets up the environment with the correct interpreter
# called from the java application
# i.e, sets up insteon variable

def init(interpreter):
	global insteon
	insteon = interpreter

#
# resets the interpreter
#
def reload():
	insteon.reload()

def err(msg = ""):
	"""
	prints to std err the value of msg and a newline character
	"""
	insteon.err().println(msg)
	
def out(msg = ""):
	insteon.out().println(msg)

def outchars(msg = ""):
	insteon.out().print(msg)

def clear():
	insteon.getConsole().clear()
	
def reset():
	insteon.reset()

def quit():
	System.exit(0)

def exit():
	quit()

def connectToHub(adr, port, pollMillis, user, password):
	insteon.setPort(IOPort(HubStream(adr, port, pollMillis, user, password)))

def connectToSerial(dev):
	insteon.setPort(IOPort(SerialIOStream(dev)))

def disconnect():
	insteon.setPort(None)

def writeMsg(msg):
	insteon.writeMsg(msg)
	
def readMsg():
	return insteon.readMsg()

def addListener(listener):
	insteon.addListener(listener)

def removeListener(listener):
	insteon.removeListener(listener)

#
# start serial port tracker
#

def trackPort():
	if insteon.isConnected() :
		tracker = PortTracker(insteon.getPort())
	else :
		err("Not connected!")

def help(obj = None):
	if obj is not None :
		if obj.__doc__ is not None :
			out(obj.__doc__.strip())
		else :
			out("No documentation for \"" + obj.__name__ + "\"")
	else :
		out("-------Welcome to Insteon Shell-------")
		out("to get a list of available functions, type '?'")
		out("to get the doc of a function, type help(funcName)")
		out("to quit, type 'quit()'")

