#-------------------------------------------------------------------------------
#
# I/O functions
#

import commands

def err(msg = ""):
	"""prints to std err the value of msg and a newline character"""
	commands.insteon.err().println(msg)

def out(msg = ""):
	commands.insteon.out().println(msg)

def outchars(msg = ""):
	commands.insteon.out().print(msg)

def writeMsg(msg):
	commands.insteon.writeMsg(msg)
	
def readMsg():
	return commands.insteon.readMsg()

def addListener(listener):
	commands.insteon.addListener(listener)

def removeListener(listener):
	commands.insteon.removeListener(listener)
