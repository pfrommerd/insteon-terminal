#-------------------------------------------------------------------------------
#
# methods for accessing the terminal environment (I/O etc)
#

from java.lang import System
from threading import Timer
from us.pfrommer.insteon.cmd.hub import HubStream
from us.pfrommer.insteon.cmd.hub import LegacyHubStream
from us.pfrommer.insteon.cmd.serial import SerialIOStream

from us.pfrommer.insteon.cmd.msg import IOPort
from us.pfrommer.insteon.cmd.utils import Utils
from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener
from us.pfrommer.insteon.cmd.msg import InsteonAddress

from org.slf4j import LoggerFactory
from ch.qos.logback.classic import Logger
from ch.qos.logback.classic import Level


import all_devices
import struct
import types

# all io-based stuff

import iofun

def err(msg = ""):
	"""prints to std err the value of msg and a newline character"""
	iofun.err(msg)

def out(msg = ""):
	"""out("text") prints text to the console""" 
	iofun.out(msg)

def outchars(msg = ""):
	"""out("text") prints text to the console, but without a newline""" 
	iofun.outchars(msg)

def clear():
	"""clear() clears the console screen"""
	iofun.clear()

def reload():
	"""reload() reloads the .py files and resets the interpreter"""
	iofun.reload()
	
def reset():
	"""reset() resets the interpreter (clear + reload)"""
	iofun.reset()
	
def exit():
	"""exit() quits the application"""
	iofun.exit()

def quit():
	"""quit() quits the application"""
	iofun.quit()

# Change logging configuration

def setLogLevel(level):
	"""setLogLevel(level) changes the log level to level, where level is a string """
	
	logger = LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME)
	levels = {
				'ERROR': Level.ERROR,
				'WARN': Level.WARN,
				'INFO': Level.INFO,
				'DEBUG': Level.DEBUG,
				'TRACE': Level.TRACE
			  }
	l = levels[level.upper()]
	logger.setLevel(l)
	
	print("Log level set to " + level)

# Basic connection functions	

def connectToHub(adr, port, pollMillis, user, password):
	"""connectToHub(adr, port, pollMillis, user, password) connects to a specific non-legacy hub """
	print("Connecting")

	try:
		iofun.connectToHub(adr, port, pollMillis, user, password)
		
		print("Connected")
	except IOException as e:
		err(e.getMessage())

	
def connectToLegacyHub(adr, port):
	"""connectToLegacyHub(adr, port) connects to a specific legacy hub"""
	print("Connecting")

	try:
		iofun.connectToLegacyHub(adr, port)
		
		print("Connected")
	except IOException as e:
		err(e.getMessage())

def connectToSerial(dev):
	"""connectToSerial("/path/to/device") connects to specific serial port """
	print("Connecting")

	try:
		iofun.connectToSerial(dev)
		
		print("Connected")
	except IOException as e:
		err(e.getMessage())

def disconnect():
	"""disconnects from serial port or hub"""
	iofun.disconnect()

# Basic Message IO

def writeMsg(msg):
	iofun.writeMsg(msg)
	
def addListener(listener):
	iofun.addListener(listener)

def removeListener(listener):
	iofun.removeListener(listener)


#
# a bunch of useful miscellaneous commands
# most of the io commands are defined in iofun
#

def listDevices():
	"""lists all configured devices"""
	all_devices.listDevices()

#
# start serial port tracker
#

def help(obj = None):
	"""help(object) prints out help for object, e.g. help(modem)"""
	if obj is not None :
		sep='\n'
		if isinstance(obj, (types.FunctionType)):
			if obj.__doc__ is None :
				iofun.out("No documentation for \"" +
						obj.__name__ + "\"")
				return

			iofun.out(obj.__doc__)
		elif isinstance(obj, (types.ClassType, types.ObjectType)):
			if obj.__doc__ is None :
				iofun.out("No documentation for \"" +
					  	obj.__class__.__name__ + "\"")
				return
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

