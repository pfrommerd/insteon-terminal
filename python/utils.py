from us.pfrommer.insteon.cmd.utils import Utils
from us.pfrommer.insteon.cmd.msg import InsteonAddress


def formatLREntry(recordBytes):
    recordFlags = recordBytes[0] & 0xff

    group = Utils.toHex(recordBytes[1])

    
    linkType = "CTRL" if ((recordFlags & (0x1 << 6)) != 0) else "RESP"
    
    linkAddr = InsteonAddress(recordBytes[2], recordBytes[3], recordBytes[4])
    
    data1 = Utils.toHex(recordBytes[5])
    data2 = Utils.toHex(recordBytes[6])
    data3 = Utils.toHex(recordBytes[7])

    return linkAddr.toString() + " " + linkType + " group: " + group + " data1: " + data1 + " data2: " + data2 + " data3: " + data3