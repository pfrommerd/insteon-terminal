from enum import Enum
import struct

class Direction(Enum):
    TO_MODEM = 'TO_MODEM'
    FROM_MODEM = 'FROM_MODEM'
    INVALID = 'INVALID'

class DataType(Enum):
    BYTE = 1
    INT = 4
    FLOAT = 4
    ADDRESS = 3
    INVALID = 0

class MsgType(Enum):
    BROADCAST = 0x80
    DIRECT = 0x00
    ACK_OF_DIRECT = 0x20
    NACK_OF_DIRECT = 0xa0
    ALL_LINK_BROADCAST = 0xc0
    ALL_LINK_CLEANUP = 0x40
    ALL_LINK_CLEANUP_ACK = 0x60
    ALL_LINK_CLEANUP_NACK = 0xe0

    def from_value(val):
        if not val:
            return None
        return MsgType(val & 0xe0)

    def from_msg(msg):
        if not 'messageFlags' in msg:
            return None

        return MsgType.from_value(msg['messageFlags'])

class AckType(Enum):
    ACK = 0x06
    NACK = 0x15

    def from_value(val):
        if not (val == 0x06 or val == 0x15):
            return None
        return AckType(val)

    def from_msg(msg):
        if not 'ACK/NACK' in msg:
            return None
        return AckType(msg['ACK/NACK'])

class Field:
    def __init__(self, offset, type, name=None, default_value=None, filter=None):
        self.offset = offset
        self.type = type
        self.name = name
        self.default_value = default_value
        self.filter = filter

    def get(self, buf):
        o = self.offset
        if self.type == DataType.BYTE:
            return int.from_bytes(buf[o:o+1], byteorder='big')
        elif self.type == DataType.INT:
            return int.from_bytes(buf[o:o+4], byteorder='big')
        elif self.type == DataType.FLOAT:
            return struct.unpack('f', buf[o:o+4])[0]
        elif self.type == DataType.ADDRESS:
            return (int.from_bytes(buf[o:o+1], byteorder='big'),
                    int.from_bytes(buf[o+1:o+2], byteorder='big'),
                    int.from_bytes(buf[o+2:o+3], byteorder='big'))
        else:
            return None

    def set(self, buf, val):
        o = self.offset
        if self.type == DataType.BYTE:
            buf[o] = val.to_bytes(1, byteorder='big')[0]
        elif self.type == DataType.INT:
            buf[o:o+4] = val.to_bytes(4, byteorder='big')
        elif self.type == DataType.FLOAT:
            buf[o:o+4] = struct.pack('f', val)
        elif self.type == DataType.ADDRESS:
            buf[o:o+1] = val[0].to_bytes(1, byteorder='big')
            buf[o+1:o+2] = val[1].to_bytes(1, byteorder='big')
            buf[o+2:o+3] = val[2].to_bytes(1, byteorder='big')

    def get_msg(self, d):
        if self.name in d:
            return d[self.name]
        else:
            return self.default_value

    def set_msg(self, msg, val):
        msg[self.name] = val

    def format(self, msg={}):
        val = self.default_value

        if msg and self.name and self.name in msg:
            val = msg[self.name]

        if val is not None:
            valstr = str(val)
            if self.type == DataType.ADDRESS:
                valstr = format_addr(val)
            elif self.type == DataType.BYTE:
                valstr = '0x{:02x}'.format(val)
        else:
            valstr = '???'

        return self.name + ':' + valstr

# Some generic address-related
# utilities
def parse_addr(addr):
    parts = addr.split('\\.')
    return (int(parts[0],16), int(parts[1],16), int(parts[2],16))

def format_addr(addr):
    return format(addr[0], 'x') + '.' + format(addr[1], 'x') + '.' + format(addr[2], 'x')


# A field is composed of (offset, type, name, default_value, filter-for header fields)
class MsgDef:
    def __init__(self, name='', direction=Direction.TO_MODEM):
        self.name = name
        self.header_length = 0
        self.length = 0
        self.direction = direction
        self.fields_list = []
        self.fields_map = {}

    def append_field(self, data_type, name=None, default_value=None, filter=None): # Changes the length
        offset = self.length

        field_len = data_type.value
        self.length = self.length + field_len # Extend the length

        field = Field(offset, data_type, name, default_value, filter)
        # Add to the map
        if name:
            self.fields_map[name] = field
        self.fields_list.append(field)

    def contains_field(self, name):
        return name in self.fields_map

    def get_field(self, name):
        return self.fields_map[name]

    def header_matches(self, buf):
        check_len = min(self.header_length, len(buf))
        for f in filter(lambda x: x.offset + x.type.value <= check_len and x.filter, self.fields_list):
            # Check the filter
            val = f.get(buf)
            if not (f.filter)(val):
                return False
        return True

    def create(self):
        m = {}
        m['type'] = self.name

        for f in self.fields_list:
            if f.name:
                m[f.name] = f.default_value
        return m

    def deserialize(self, buf):
        m = {}
        # Add some meta-fields
        m['type'] = self.name

        for f in self.fields_list:
            if f.name:
                val = f.get(buf)
                m[f.name] = val
        return m

    def serialize(self, msg):
        # Assume the 'type' field has already been set
        buf = bytearray(self.length)
        for f in self.fields_list:
            val = msg[f.name] if f.name is not None and f.name in msg else f.default_value
            if val is not None:
                f.set(buf, val)
        return bytes(buf)

    def format_msg(self, msg):
        sep = ('<','>') if self.direction == Direction.TO_MODEM else ('[',']')
        fields_str = '|'.join(map(lambda x: x.format(msg),
            filter(lambda x: x.name is not None, self.fields_list)))
        return sep[0] + self.name + sep[1] + ':' + fields_str

    def __str__(self):
        sep = ('<','>') if self.direction == Direction.TO_MODEM else ('[',']')
        fields_str = '|'.join(map(lambda x: x.format(),
            filter(lambda x: x.name is not None, self.fields_list)))
        return sep[0] + self.name + sep[1] + ':' + fields_str

class MsgStreamEncoder:
    def __init__(self, defs = {}):
        self._defs_map = defs

    def encode(self, msg):
        # Get the type
        if not 'type' in msg:
            raise ValueError('No type in message dict!')

        msg_type = msg['type']

        if not (msg_type in self._defs_map):
            raise ValueError('Message type unknown: ' + msg_type)

        d = self._defs_map[msg_type]
        return d.serialize(msg)


class MsgStreamDecoder:
    def __init__(self, defs = {}, direction=Direction.FROM_MODEM):
        self._buf = bytearray()
        self._direction = direction

        self._all_defs = defs.values()
        self._reset_filtered_defs()

    def _reset_filtered_defs(self):
        self._filtered_defs = list(filter(lambda d: d.direction == self._direction, self._all_defs))

    def decode(self, buf):
        if len(self._filtered_defs) < 1:
            self._reset_filtered_defs()

        self._buf += buf

        while True:
            # A one-byte message isn't currently allowed!
            if len(self._buf) < 2:
                break
            
            # If we haven't yet determined the message, filter
            if len(self._filtered_defs) > 1: 
                self._filtered_defs = list(filter(lambda d: d.header_matches(self._buf),self._filtered_defs))
            # Now check to see if we are done or are totally lost
            if len(self._filtered_defs) == 1 and self._filtered_defs[0].length <= len(self._buf): # Done with message!
                d = self._filtered_defs[0]
                # Pop off the required length and convert to immutable bytes
                msg_buf = bytes(self._buf[:d.length])
                self._buf = self._buf[d.length:]

                # Reset filtered defs
                self._reset_filtered_defs()

                return d.deserialize(msg_buf)
            elif len(self._filtered_defs) < 1:
                # Flush a single byte and reset the filter
                self._buf = self._buf[1:]

                self._reset_filtered_defs()
                continue
            # We can't determine anything yet
            break
        return None
