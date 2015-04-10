from threading import Timer

from us.pfrommer.insteon.cmd.msg import Msg
from us.pfrommer.insteon.cmd.msg import MsgListener

from us.pfrommer.insteon.cmd.msg import InsteonAddress

devNameMap = {}
devAddressMap = {}

def out(msg = ""):
    from commands import insteon
    insteon.out().println(msg)

def addDev(dev):
	devNameMap[dev.getName()] = dev
        addr = InsteonAddress(dev.getAddress()).toString()
	devAddressMap[addr] = dev;
	
def getDevByName(name):
	return devNameMap.get(name)

def getDevByAddr(addr):
    return devAddressMap.get(addr)
	

class Device:
    m_name = ""
    m_address = InsteonAddress()
    m_dbBuilder = None
    
    def __init__(self, name, adr):
        self.m_name = name
        self.m_address = adr
        addDev(self)

    def getName(self):
        return self.m_name
    
    def getAddress(self):
        return self.m_address
