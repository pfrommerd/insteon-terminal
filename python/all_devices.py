#-------------------------------------------------------------------------------
#
# global translation map for all device addresses
#

import iofun

from us.pfrommer.insteon.msg import InsteonAddress

devNameMap = {}
devAddressMap = {}

def addDev(dev):
	devNameMap[dev.getName()] = dev
	addr = InsteonAddress(dev.getAddress()).toString()
	devAddressMap[addr] = dev;

def getDevByName(name):
	return devNameMap.get(name)

def getDevByAddr(addr):
	return devAddressMap.get(addr)

def listDevices():
	for name, dev in devNameMap.iteritems():
		iofun.out(format(name, '30s') + " " + dev.getAddress())
