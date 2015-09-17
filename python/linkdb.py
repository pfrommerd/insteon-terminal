#-------------------------------------------------------------------------------
#
#   cross-device class to hold and manipulate a link database
#

import json
import re
from commands import insteon

from all_devices import getDevByAddr

#
# --------------- bunch of helper functions ------------
#
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
	cr = bracketOpen + ("CTRL" if (ctrl & (0x01<<6)) else "RESP") + bracketClose
	out(prefix + format(off, '04x') + " " + format(dev, '30s') +
		" " + format(addr, '8s') + " " + cr + " " +
		'{0:08b}'.format(rec["type"]) + 
		" group: " + format(rec["group"], '02x') + " data: " +
		' '.join([format(x & 0xFF, '02x') for x in rec["data"]]))

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

class DefaultRecordFormatter(RecordFormatter):
	def format(self, rec, prefix = ""):
		dumpRecord(rec, prefix)

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
		return len(self.records)
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
			out("saved " + format(len(arr), 'd') + " records")
			f.close()
	def load(self, d, filename):
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
				   matchData = True):
		#          dumpRecord(rec, "testing for:")
		#          out("MASK: " + '{0:08b}'.format(mask))
		for off in sorted(self.records, reverse = True):  # loop through offsets
			# out("offset: " + format(off, '04x'))
			recsByAddr =  {rec["addr"] : self.records[off].get(rec["addr"], {})} if matchAddress else self.records[off]
			# loop through all matching addresses at offset
			for addr, allRecsByType in recsByAddr.iteritems():
				# out(" address: " + addr.toString())
				# loop through all types at address
				for rt, allRecsByGroup in allRecsByType.iteritems():
					# out("  link type: " + '{0:08b}'.format(rt))
					if (rt & mask) != (rec["type"] & mask): # mask no match: skip
						# out("    link type no match!")
						continue
					recsByGroup =  {rec["group"] : allRecsByGroup.get(rec["group"], [])} if matchGroup else allRecsByGroup;
					# loop through all groups
					for group, recList in recsByGroup.iteritems():
						#  out("   group: " + format(group, '02x') + " size: " + format(len(recList), 'd'))
						for tmprec in recList:
							if not matchData:
								return tmprec
							if (tmprec["data"] == rec["data"]):
								#  out("data matches: ")
								#  dumpRecord(tmprec)
								return tmprec
							else:
								#   out("data does not match: ")
								#dumpRecord(tmprec)
								return None

