from .. import util as util

import datetime

class DefaultRecordFormatter:
    def __init__(self, registry=None):
        self._registry = registry if registry is not None else Device.s_default_registry

    def __call__(self, rec):
        off = rec['offset']
        addr = util.format_addr(rec['address'])
        dev = self._registry.get_by_addr(rec['address']) \
                if self._registry.get_by_addr(rec['address']) else addr


class LinkDB:
    def __init__(self, records=[]):
        self.records = records
        self.last_updated = None # Not yet populated

    @property
    def is_populated(self):
        return self.last_updated is not None

    def set_updated(self): # Updates the last_updated time
        self.last_updated = datetime.datetime.now()

    def clear(self):
        self.records.clear()

    def add_record(self, rec, allow_duplicates=False):
        if not allow_duplicates and rec in self.records:
            return
        else:
            self.records.append(rec)

    # Returns a filter generator that can be used
    # to search the linkdb
    def filter_records(self, rec_filter, ltype_mask):
        def msg_matches(x):
            return not ('type' in rec_filter and rec_filter['type'] != x['type'] & ltype_mask) and  \
                    all(item in x for item in rec_filter.items() if item[0] != 'type')
            
        return filter(msg_matches, self.records)

    def filter_active_records(self, rec_filter={}, ltype_mask=0x82):
        rec_filter['type'] |= (1 << 7) # record in use bit
        rec_filter['type'] |= (1 << 1) # high water mark

        return self.filter_records(rec_filter, ltype_mask)
