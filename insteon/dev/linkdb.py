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
        dev = self._registry.by_addr[rec['address']].name \
                if self._registry and rec['address'] in self._registry.by_addr else addr
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
    def __init__(self, records=None, formatter=None):
        self.records = records if records else []
        self.timestamp = None # Not valid yet!
        self.formatter = formatter

    def __iter__(self):
        for r in self.records:
            yield r

    @property
    def empty(self):
        return not self.records

    @property
    def valid(self):
        return self.timestamp is not None

    @property
    def end_offset(self):
        last_off = 0x00
        for r in self.records:
            if r['offset'] > last_off:
                last_off = r['offset'] + 0x08
        return last_off

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

    # Sets the timestamp of the device (if ts is None, sets it to the current time)
    def set_timestamp(self, ts=None):
        self.timestamp = ts if ts else datetime.datetime.now()

    def set_invalid(self):
        self.timestamp = None

    # Adds a bunch of records and sets the timestamp (if records has a timestamp property, it uses
    # that, otherwise it just uses the current time)
    def update(self, records):
        self.clear()
        for r in records:
            self.add_record(r)

        if hasattr(records, 'timestamp'):
            self.set_timestamp(records.timestamp)
        else:
            self.set_timestamp()

    def serialize(self):
        ser = {}
        if self.timestamp:
            ser['timestamp'] = self.timestamp.strftime('%b %d %Y %H:%M:%S')
        ser['records'] = self.records
        return ser

    def deserialize(self, ser):
        if 'timestamp' in ser:
            self.timestamp = datetime.datetime.strptime(ser['timestamp'],'%b %d %Y %H:%M:%S')
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

    def print(self, formatter=None):
        formatter = formatter if formatter else self.formatter
        if not formatter:
            logger.warning('No formatter set in call LinkDB.print()!')
            return

        if not self.valid:
            logger.warning('LinkDB cache not valid!')
            logger.warning('set_timestamp() must first be called for proper linkdb initialization (even if there are records in the DB)')
            return

        print(self.timestamp.strftime('Retrieved: %b %d %Y %H:%M:%S'))
        for rec in self.records:
            print(formatter(rec))


    # Returns a filtered "subset" linkDB that 
    # contains only the records that match a certain record
    # filter
    def filter_records(self, rec_filter, flags_mask):
        def msg_matches(x):
            return not ('flags' in rec_filter and rec_filter['flags'] & ltype_mask != x['flags'] & ltype_mask) and  \
                    all(item in x for item in rec_filter.items() if item[0] != 'flags')
        return LinkDB(filter(msg_matches, self.records))

    def filter_active_records(self, rec_filter={}, flags_mask=0x82):
        rec_filter['flags'] |= (1 << 7) # record in use bit
        rec_filter['flags'] |= (1 << 1) # high water mark

        return self.filter_records(rec_filter, flags_mask)
