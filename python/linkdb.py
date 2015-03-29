import commands

from device import *
from commands import insteon


def out(msg = ""):
	insteon.out().println(msg)

def dumpRecord(rec):
        off  = rec["offset"]
        addr = rec["addr"].toString()
        dev = getDevByAddr(addr).getName() if getDevByAddr(addr) else addr
        out(format(off, '04x') + " " + format(dev, '20s') + '{0:08b}'.format(rec["type"]) + 
            " group: " + format(rec["group"], '02x') + " data: " +
            ' '.join([format(x & 0xFF, '02x') for x in rec["data"]]))


def addRecord(d, rec):
        off  = rec["offset"]
        addr = rec["addr"]
        ltype = rec["type"]
        group = rec["group"]
        if not d.has_key(off):
                d[off] = {}
        if not d[off].has_key(addr):
                d[off][addr] = {}
        if not d[off][addr].has_key(ltype):
                d[off][addr][ltype] = {}
        if  not d[off][addr][ltype].has_key(group):
                d[off][addr][ltype][group] = []
        d[off][addr][ltype][group].append(rec)

def dumpDB(d):
        for off in sorted(d):
                for addr in sorted(d[off]):
                        for type in sorted(d[off][addr]):
                                for group in sorted(d[off][addr][type]):
                                        for inst in sorted(d[off][addr][type][group]):
                                                dumpRecord(inst)
