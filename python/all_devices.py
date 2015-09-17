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
