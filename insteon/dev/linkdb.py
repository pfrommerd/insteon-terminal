import insteon.io.msg as msg

import datetime
import json

import logbook
logger = logbook.Logger(__name__)

from warnings import warn

class DefaultRecordFormatter:
    def __init__(self, registry=None):
        self._registry = registry

    def __call__(self, rec):
        off = rec['offset']
        addr = msg.format_addr(rec['address'])
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

def offset_stripped(record):
    copy = dict(record)
    if 'offset' in copy:
        del copy['offset']
    return copy

def offsets_stripped(records):
    for rec in records:
        yield offset_stripped(rec)

class LinkDB:
    def __init__(self, records=None, formatter=None):
        from .device import Device

        self.records = records if records else []
        self.last_updated = None # Not yet populated
        self.formatter = formatter if formatter else DefaultRecordFormatter(Device.s_default_registry)

    @property
    def is_populated(self):
        return self.last_updated is not None

    @property
    def end_offset(self):
        last_off = 0x00
        for r in self.records:
            if r['offset'] > last_off:
                last_off = r['offset'] + 0x08
        return last_off

    def print(self, formatter=None):
        formatter = formatter if formatter else self.formatter

        if not self.is_populated:
            logger.warning('LinkDB cache not populated!')
            logger.warning('set_updated() must first be called for proper linkdb initialization (even if there are records in the DB)')
            return

        print(self.last_updated.strftime('Retrieved: %b %d %Y %H:%M:%S'))
        for rec in self.records:
            print(formatter(rec))

    def add_record(self, rec, allow_duplicates=False):
        # Make sure all the fields are nicely formatted
        rec['offset'] = rec['offset'] if 'offset' in rec else self.end_offset
        rec['address'] = rec['address'] if 'address' in rec else (0, 0, 0)
        rec['group'] = rec['group'] if 'group' in rec else 0x00
        rec['flags'] = rec['flags'] if 'flags' in rec else 0x02
        rec['data'] = rec['data'] if 'offset' in rec else [0, 0, 0]

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
            ser['timestamp'] = self.last_updated.strftime('%b %d %Y %H:%M:%S')
        ser['records'] = self.records
        return ser

    def deserialize(self, ser):
        if 'timestamp' in ser:
            self.last_updated = datetime.datetime.strptime(ser['timestamp'],'%b %d %Y %H:%M:%S')
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
