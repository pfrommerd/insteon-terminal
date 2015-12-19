from java.lang import System

#-------------------------------------------------------------------------------
#
# I/O functions
#
# These represent the basic api for communicating with the console 
#

console = None

def _init_io_fun(insteonConsole):
	global console
	console = insteonConsole

def err(msg = ""):
	"""prints to std err the value of msg and a newline character"""
	console.err().println(msg)

def out(msg = ""):
	"""out("text") prints text to the console""" 
	console.out().println(msg)

def outchars(msg = ""):
	"""out("text") prints text to the console, but without a newline""" 
	console.out().print(msg)

def clear():
	"""clears the console screen"""
	console.clear()

def reload():
	"""reloads the .py files and resets the interpreter"""
	console.reload()
	
def reset():
	"""Resets the interpreter (clear + reload)"""
	console.reset()
	
def exit():
	"""quits the application"""
	System.exit(0)

def quit():
	"""quits the application"""
	exit()
	
# Basic connection functions	

def connectToHub(adr, port, pollMillis, user, password):
	"""connectToHub(adr, port, pollMillis, user, password) connects to a specific non-legacy hub """
	console.connectToHub(adr, port, pollMillis, user, password)
	
def connectToLegacyHub(adr, port):
	"""connectToLegacyHub(adr, port) connects to a specific legacy hub"""
	console.connectToLegacyHub(adr, port)

def connectToSerial(dev):
	"""connectToSerial("/path/to/device") connects to specific serial port"""
	console.connectToSerial(dev)

def disconnect():
	"""disconnects from serial port or hub"""
	console.disconnect()

# Basic Message IO

def writeMsg(msg):
	console.writeMsg(msg)

def addListener(listener):
	"""Adds a MsgListener for incoming messages"""
	console.addMsgListener(listener)

def removeListener(listener):
	"""Removes a MsgListener"""
	console.removeMsgListener(listener)

def addPortListener(listener):
	"""like addListener, but listener is an instance of PortListener and has the msgWritten function"""
	console.addMsgListener(listener)

def removePortListener(listener):
	"""like removeListener, but listener is an instance of PortListener and has the msgWritten function"""
	console.removeMsgListener(listener)
