#-------------------------------------------------------------------------------
#
#   cross-device class to hold and manipulate a link database
#

import json
import re
import iofun

from us.pfrommer.insteon.msg import InsteonAddress

from all_devices import getDevByAddr

debug = False
#
# --------------- bunch of helper functions ------------
#
def out(msg = ""):
	iofun.out(msg)

def dumpRecord(rec, prefix = ""):
	off  = rec["offset"]
	addr = rec["addr"].toString()
	dev = getDevByAddr(addr).getName() if getDevByAddr(addr) else addr
	cr = ctrlToString(rec["type"])
	out(prefix + format(off, '04x') + " " + format(dev, '30s') +
		" " + format(addr, '8s') + " " + cr + " " +
		'{0:08b}'.format(rec["type"]) + 
		" group: " + format(rec["group"], '02x') + " data: " +
		' '.join([format(x & 0xFF, '02x') for x in rec["data"]]))

def ctrlToString(ctrl):
	valid  = (ctrl & (0x01 << 7))
	bracketOpen   = " " if valid else "("
	bracketClose  = " " if valid else ")"
	return (bracketOpen + ("CTRL" if (ctrl & (0x01<<6)) else "RESP")
			+ bracketClose)

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

class RecordFormatter():
	def format(self, rec):
		dumpRecord(rec)
	@staticmethod
	def ctrlToString(rec):
		dumpRecord(rec)

class DefaultRecordFormatter(RecordFormatter):
	def format(self, rec, prefix = ""):
		dumpRecord(rec, prefix)

class LightDBRecordFormatter(RecordFormatter):
	@staticmethod
	def dataToString(data):
		return ("ON LVL: " + format(data[0] & 0xFF, '3d')
				+ " RMPRT: " + format(data[1] & 0xFF, '3d')
				+ " BUTTON: " + format(data[2] & 0xFF, '3d'))
	def format(self, rec, prefix = ""):
		off  = rec["offset"]
		addr = rec["addr"].toString()
		dev = getDevByAddr(addr).getName() if getDevByAddr(addr) else addr
		cr = ctrlToString(rec["type"])
		out(prefix + format(off, '04x') + " " + format(dev, '30s') +
			" " + format(addr, '8s') + " " + cr + " " +
			'{0:08b}'.format(rec["type"]) + 
			" group: " + format(rec["group"], '02x') + " " +
			self.dataToString(rec["data"]))
	
#
# ------ cross-device class to manipulate the link databases ------------------
#

class DB():
	records = {}
	recordFormatter = None
	def __init__(self):
		self.records = {}
		self.recordFormatter = DefaultRecordFormatter()
	def clear(self):
		self.records = {};
	def setRecordFormatter(self, fmt):
		self.recordFormatter = fmt
	def getNumberOfRecords(self):
		return len(getRecordsAsArray(self.records))
	def addRecord(self, rec, allowDuplicates = True):
		off  = rec["offset"]
		addr = rec["addr"]
		ltype = rec["type"]
		group = rec["group"]
		if not self.records.has_key(off):
			self.records[off] = {}
		if not self.records[off].has_key(addr):
			self.records[off][addr] = {}
		if not self.records[off][addr].has_key(ltype):
			self.records[off][addr][ltype] = {}
		if not self.records[off][addr][ltype].has_key(group):
			self.records[off][addr][ltype][group] = []
		if not allowDuplicates:
			self.records[off][addr][ltype][group] = []
		self.records[off][addr][ltype][group].append(rec)
	def hasOffset(self, off):
		return (self.records.has_key(off));
	def dump(self):
		arr = getRecordsAsArray(self.records);
		for r in arr:
			self.recordFormatter.format(r)
	def dumpRecord(self, rec, text):
		self.recordFormatter.format(rec, text)
	def save(self, filename):
		f = open(filename, 'w')
		if not f:
			out("ERROR: cannot open file " + filename)
			return
		arr = getRecordsAsArray(self.records)
		for r in arr:
			saveRecord(f, r)
		f.close()
		out("saved " + format(len(arr), 'd') + " records")
	def load(self, filename):
		r = re.compile('[ \t\n\r:]+')
		with open(filename, 'r') as f:
			for line in f:
				(offset, addr, typ, group, d1, d2, d3, dummy) = r.split(line)
				rec = {"offset" : int(offset, 16),
					   "addr" : InsteonAddress(addr),
					   "type" : int(typ, 16),
					   "group" : int(group, 16),
					   "data" : [int(d1, 16), int(d2, 16), int(d3, 16)]}
				self.addRecord(rec, True)
	def getRecordsAsArray(self):
		return getRecordsAsArray(self.records)
	def recordPresent(self, rec, matchAddress = True, matchGroup = True,
					  matchData = True):
		rec["type"] |= (1 << 7) # set record in use bit
		mask = 0xc2 # mask unused bits, but match all other bits
		return self.findRecord(rec, mask, matchAddress,
							   matchGroup, matchData) != None
	def findAllRecords(self, rec, matchAddress = True,
						 matchGroup = True, matchData = False):
		rec["type"] = (1 << 1) # set high water mark
		mask = 0x02 # must match these two bits
		return self.findRecord(rec, mask, matchAddress, matchGroup, matchData, True)
	def findActiveRecords(self, rec, matchAddress = True,
						  matchGroup = True, matchData = False, matchController = False):
		rec["type"] |= (1 << 7) # set record in use bit
		rec["type"] |= (1 << 1) # set high water mark
		mask = 0x82 # must match these two bits
		mask |= (1<<6) if matchController else 0 # and maybe controller bit
		return self.findRecord(rec, mask, matchAddress, matchGroup, matchData, True)
	def findActiveRecord(self, rec, matchAddress = True,
						 matchGroup = True, matchData = False):
		rec["type"] |= (1 << 7) # set record in use bit
		mask = 0xc2 # mask unused bits, but match all other bits
		return self.findRecord(rec, mask, matchAddress, matchGroup, matchData)
	def findInactiveRecord(self, rec, matchAddress = True,
						   matchGroup = True, matchData = False):
		rec["type"] &= 0x7F # clear record in use bit
		mask = 0x82 # mask unused bits and the controller/responder bit
		return self.findRecord(rec, mask, matchAddress, matchGroup, matchData)
	def findFreeRecord(self, rec, matchAddress = False,
					   matchGroup = False, matchData = False):
		rec["offset"] &= (0x7f) # record free
		mask = 0xc2 # mask unused bits, but match all other bits
		return self.findRecord(rec, mask, matchAddress, matchGroup, matchData)
	def findStopRecordAddresses(self):
		aboveStopAddress = 0
		stopAddress = 0x1fff
		offsets = sorted(self.records, reverse = True)
		if len(offsets) > 0:
			stopAddress = offsets[-1]; # last element
		if (stopAddress < 0x1fff):
			aboveStopAddress = stopAddress + 8
		belowStopAddress = stopAddress - 8
		return aboveStopAddress, stopAddress, belowStopAddress

	def findRecord(self, rec, mask, matchAddress = True, matchGroup = True,
				   matchData = True, returnAll = False):
		recs = [];
		if debug:
			dumpRecord(rec, "testing for:")
			out("MASK: " + '{0:08b}'.format(mask))
			out("number of records: " + format(self.getNumberOfRecords()))
		for off in sorted(self.records, reverse = True):  # loop through offsets
			a = rec["addr"]
			recsByAddr =  {a : self.records[off].get(a, {})} if matchAddress else self.records[off]
			if debug:
				out("offset: " + format(off, '04x') + " has " +
					format(len(recsByAddr), '3d') + " addresses, matchaddr: " +
					(a.toString() if matchAddress else "NO"))
			# loop through all matching addresses at offset
			for addr, allRecsByType in recsByAddr.iteritems():
				if debug:
					out(" address: " + addr.toString())
					out(" # of types: " + format(len(allRecsByType), 'd'))
				# loop through all types at address
				for rt, allRecsByGroup in allRecsByType.iteritems():
					if debug:
						out("  link type: " + '{0:08b}'.format(rt) +
							"  mask:      " + '{0:08b}'.format(mask) +
							"  search:    " + '{0:08b}'.format(rec["type"]))
					if (rt & mask) != (rec["type"] & mask): # mask no match: skip
						if debug:
							out("    link type no match!")
						continue
					recsByGroup =  {rec["group"] : allRecsByGroup.get(rec["group"], [])} if matchGroup else allRecsByGroup;
					# loop through all groups
					if debug:
						out("    found groups " + format(len(recsByGroup), 'd') + ", match groups: " +
							(format(rec["group"], "02x") if matchGroup else "NO"))
					for group, recList in recsByGroup.iteritems():
						if debug:
							out("   group: " + format(group, '02x') + " size: " + format(len(recList), 'd'))
						for tmprec in recList:
							if not matchData:
								if returnAll:
									recs.append(tmprec)
									continue
								else:
									return tmprec
							if (tmprec["data"] == rec["data"]):
								if debug:
									out("data matches: ")
									dumpRecord(tmprec)
								if returnAll:
									recs.append(tmprec)
								else:
									return tmprec
							else:
								if debug:
									out("data does not match: ")
									dumpRecord(tmprec)
								if not returnAll:
									return None
		if returnAll:
			return recs
		return None
