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

import iofun
import struct
import types
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
	"""
	Reloads the interpreter. Use this whenever you feel the state got screwed up.
	"""
	insteon.reload()

def err(msg = ""):
	"""prints to std err the value of msg and a newline character"""
	insteon.err().println(msg)
	
def clear():
	"""clears the console screen"""
	insteon.getConsole().clear()
	
def reset():
	"""Resets the interpreter"""
	insteon.reset()

def out(msg = ""):
	"""out("text") prints text to the console""" 
	insteon.out().println(msg)

def quit():
	"""quits the interpreter"""
	System.exit(0)

def exit():
	"""quits the interpreter"""
	quit()

def connectToHub(adr, port, pollMillis, user, password):
	"""connectToHub(adr, port, pollMillis, user, password) connects to specific hub"""
	insteon.setPort(IOPort(HubStream(adr, port, pollMillis, user, password)))

def connectToSerial(dev):
	"""connectToSerial("/path/to/device") connects to specific serial port """
	insteon.setPort(IOPort(SerialIOStream(dev)))

def disconnect():
	"""disconnects from serial port or hub"""
	insteon.setPort(None)

#
# start serial port tracker
#

def trackPort():
	"""start serial port tracker(monitor) that shows all incoming/outgoing bytes"""
	if insteon.isConnected() :
		tracker = PortTracker(insteon.getPort())
	else:
		err("Not connected!")

def help(obj = None):
	"""help(object) prints out help for object, e.g. help(modem)"""
	if obj is not None :
		if obj.__doc__ is None :
			iofun.out("No documentation for \"" +
					  obj.__class__.__name__ + "\"")
			return
		sep='\n'
		if isinstance(obj, (types.MethodType)):
			iofun.out(obj.__doc__)
		elif isinstance(obj, (types.ClassType, types.ObjectType)):
			iofun.out(obj.__doc__)
			docList = [getattr(obj, method).__doc__ for method in dir(obj) if callable(getattr(obj, method)) and getattr(obj, method).__doc__]
			if len(docList) == 0:
				return
			maxMethodLen = max([len(doc.split(sep)[0]) for doc in docList])
			iofun.out("\n".join(["%s %s" %
								 (doc.split(sep)[0].ljust(maxMethodLen + 1),
								  " ".join(doc.split(sep)[1:]).strip())
								 for doc in docList]))
	else:
		out("-------Welcome to the Insteon Terminal-------")
		out("to get a list of available functions, type '?'")
		out("to get help, type help(funcName) or help(objectName)")
		out("for example: help(Modem2413U)")
		out("to quit, type 'quit()'")

