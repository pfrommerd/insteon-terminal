from .. import util as util


import datetime
import json

class DefaultRecordFormatter:
    def __init__(self, registry=None):
        self._registry = registry

    def __call__(self, rec):
        off = rec['offset']
        addr = util.format_addr(rec['address'])
        dev = self._registry.get_by_addr(rec['address']).name \
                if self._registry and self._registry.get_by_addr(rec['address']) else addr
        group = rec['group']
        flags = rec['flags']

        # Convert the type flags to a string
        valid = (flags & (1 << 7))
        ltype = 'CTRL' if (flags & (1 << 6)) else 'RESP'
        ctrl = ' ' + ltype + ' ' if valid else '(' + ltype + ')'

        data_str = ' '.join([format(x & 0xff, '02x') for x in rec['data']])

        return '{:04x} {:30s} {:8s} {} {:08b} group: {:02x} data: {}'.format(
                off,   dev,  addr, ctrl, flags,     group,       data_str)


class LinkDB:
    def __init__(self, records=[]):
        self.records = records
        self.last_updated = None # Not yet populated

    @property
    def is_populated(self):
        return self.last_updated is not None


    def add_record(self, rec, allow_duplicates=False):
        if not allow_duplicates and rec in self.records:
            return
        else:
            self.records.append(rec)

    def clear(self):
        self.records.clear()

    def set_updated(self): # Updates the last_updated time
        self.last_updated = datetime.datetime.now()

    def update(self, records):
        self.clear()
        for r in records:
            self.add_record(r)
        self.set_updated()

    def serialize(self):
        ser = {}
        if self.last_updated:
            ser['timestamp'] = self.last_updated.strftime('%b %d %Y %I:%M%p')
        ser['records'] = self.records
        return ser

    def deserialize(self, ser):
        if 'timestamp' in ser:
            self.last_updated = datetime.datetime.strptime(ser['timestamp'],'%b %d %Y %I:%M%p')
        if 'records' in ser:
            for r in ser['records']:
                # Change the address type back to a tuple
                r['address'] = (r['address'][0], r['address'][1], r['address'][2])

                self.add_record(r)

    def save(self, filename):
        with open(filename, 'w') as out:
            json.dump(self.serialize(), out)

    def load(self, filename):
        with open(filename, 'r') as i:
            ser = json.load(i)
            self.deserialize(ser)

    # Returns a filter generator that can be used
    # to search the linkdb
    def filter_records(self, rec_filter, flags_mask):
        def msg_matches(x):
            return not ('flags' in rec_filter and rec_filter['flags'] & ltype_mask != x['flags'] & ltype_mask) and  \
                    all(item in x for item in rec_filter.items() if item[0] != 'flags')
            
        return filter(msg_matches, self.records)

    def filter_active_records(self, rec_filter={}, flags_mask=0x82):
        rec_filter['flags'] |= (1 << 7) # record in use bit
        rec_filter['flags'] |= (1 << 1) # high water mark

        return self.filter_records(rec_filter, flags_mask)
