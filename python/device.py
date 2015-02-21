from us.pfrommer.insteon.cmd.msg import InsteonAddress

class Device:
    def __init__(self, name, adr):
        self.m_name = name
        self.m_address = adr
    
    def getName(self):
        return self.m_name
    
    def getAddress(self):
        return self.m_address