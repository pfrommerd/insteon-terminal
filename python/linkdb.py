import commands
import json
import re

from device import *
from commands import insteon


def out(msg = ""):
	insteon.out().println(msg)

def dumpRecord(rec, prefix = ""):
        off  = rec["offset"]
        addr = rec["addr"].toString()
        dev = getDevByAddr(addr).getName() if getDevByAddr(addr) else addr
        ctrl = rec["type"]
        valid  = (ctrl & (0x01 << 7))
        bracketOpen   = " " if valid else "("
        bracketClose  = " " if valid else ")"
        cr = bracketOpen + ("CTRL" if (ctrl & (0x01 << 6)) else "RESP") + bracketClose
        out(prefix + format(off, '04x') + " " + format(dev, '20s') +
            " " + format(addr, '8s') + " " + cr + " " +
            '{0:08b}'.format(rec["type"]) + 
            " group: " + format(rec["group"], '02x') + " data: " +
            ' '.join([format(x & 0xFF, '02x') for x in rec["data"]]))


def addRecord(d, rec, allowDuplicates = True):
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
        if not d[off][addr][ltype].has_key(group):
                d[off][addr][ltype][group] = []
        if not allowDuplicates:
                d[off][addr][ltype][group] = []
        d[off][addr][ltype][group].append(rec)

def dumpDB(d):
        arr = getRecordsAsArray(d);
        for r in arr:
                dumpRecord(r)

def saveRecord(f, rec):
        d = rec["data"]
        f.write("%04x %8s %02x %02x %02x %02x %02x\n" %
                (rec["offset"], rec["addr"].toString(), rec["type"], rec["group"],
                 d[0] & 0xFF, d[1] & 0xFF, d[2] & 0xFF))

def getRecordsAsArray(d):
        arr = [];
        for off in sorted(d, reverse = True):
                for addr in sorted(d[off]):
                        for type in sorted(d[off][addr]):
                                for group in sorted(d[off][addr][type]):
                                        for inst in sorted(d[off][addr][type][group]):
                                                arr.append(inst)
        return arr;


def saveDB(d, filename):
        f = open(filename, 'w')
        if not f:
                out("ERROR: cannot open file " + filename)
                return
        arr = getRecordsAsArray(d)
        for r in arr:
                saveRecord(f, r)
        out("saved " + format(len(arr), 'd') + " records")
        f.close()

def loadDB(d, filename):
        r = re.compile('[ \t\n\r:]+')
        with open(filename, 'r') as f:
                for line in f:
                        (offset, addr, typ, group, d1, d2, d3, dummy) = r.split(line)
                        rec = {"offset" : int(offset, 16),
                               "addr" : InsteonAddress(addr),
                               "type" : int(typ, 16),
                               "group" : int(group, 16),
                               "data" : [int(d1, 16), int(d2, 16), int(d3, 16)]}
                        addRecord(d, rec, True)
