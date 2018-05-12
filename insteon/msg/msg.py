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


def buffer_get_field(buf, field):
    if field[1] == DataType.BYTE:
        return int.from_bytes(buf[field[0]:field[0]+1], byteorder='big')
    elif field[1] == DataType.INT:
        return int.from_bytes(buf[field[0]:field[0]+4], byteorder='big')
    elif field[1] == DataType.FLOAT:
        return struct.unpack('f', buf[field[0]:field[0]+4])[0]
    elif field[1] == DataType.ADDRESS:
        return (int.from_bytes(buf[field[0]:field[0]+1], byteorder='big'),
                int.from_bytes(buf[field[0]:field[0]+1], byteorder='big'),
                int.from_bytes(buf[field[0]:field[0]+1], byteorder='big'))
    else:
        return None

def buffer_set_field(buf, field, value):
    if field[1] == DataType.BYTE:
        buf[field[0]] = value.to_bytes(1, byteorder='big')[0]
    elif field[1] == DataType.INT:
        buf[field[0]:field[0]+4] = value.to_bytes(4, byteorder='big')
    elif field[1] == DataType.FLOAT:
        buf[field[0]:field[0]+4] = struct.pack('f', value)
    elif field[1] == DataType.ADDRESS:
        buf[field[0]] = value[0].to_bytes(1, byteorder='big')[0]
        buf[field[0] + 1] = value[1].to_bytes(1, byteorder='big')[0]
        buf[field[0] + 2] = value[2].to_bytes(1, byteorder='big')[0]

# A field is composed of (offset, type, name, default_value, filter-for header fields)
class MsgDef:
    def __init__(self, name='', direction=Direction.TO_MODEM):
        self.name = name
        self.header_length = 0
        self.length = 0
        self.direction = direction
        self.fields_list = []
        self.fields_map = {}

    def append_field(self, data_type, name, default_value, filter=None): # Changes the length
        offset = self.length

        field_len = data_type.value
        self.length = self.length + field_len

        # Add to the map
        if name:
            self.fields_map[name] = (offset, data_type, name, default_value, filter)
        self.fields_list.append( (offset, data_type, name, default_value, filter) )

    def contains_field(self, name):
        return name in self.fields_map

    def get_field(self, name):
        return self.fields_map[name]

    def header_matches(self, buf):
        check_len = min(self.header_length, len(buf))
        for f in filter(lambda x: x[0] + x[1].value <= check_len and x[4], self.fields_list):
            # Check the filter
            val = buffer_get_field(buf, f)
            if not f[4](val):
                return False
        return True

    def create(self):
        m = {}
        m['type'] = self.name

        for f in self.fields_list:
            if f[2]:
                m[f[2]] = f[3]

        return m

    def deserialize(self, buf):
        m = {}
        # Add some meta-fields
        m['type'] = self.name

        for f in self.fields_list:
            if f[2]:
                val = buffer_get_field(buf, f)
                m[f[2]] = val
        return m

    def serialize(self, msg):
        # Assume the 'type' field has already been set
        buf = bytearray(self.length)
        for f in self.fields_list:
            val = msg[f[2]] if f[2] is not None and f[2] in msg else f[3]
            if val is not None:
                buffer_set_field(buf, f, val)
        return bytes(buf)

    def format_msg(self, msg):
        s = self.direction.value + '(' + self.name + '):'
        for f in self.fields_list:
            if f[2]:
                val = f[3] if f[3] else (msg[f[2]] if f[2] in msg else None)
                if val:
                    s = s + f[2] + ':' + str(val) + '|'
                else:
                    s = s + f[2] + ':???|'
        return s

    def __str__(self):
        sep = '<' if self.direction == Direction.TO_MODEM else '['
        sep2 = '>' if self.direction == Direction.TO_MODEM else ']'
        s = sep + self.name + sep2 + ':'
        for f in self.fields_list:
            if f[2]:
                if f[3]:
                    s = s + f[2] + ':' + str(f[3]) + '|'
                else:
                    s = s + f[2] + '|'
        return s

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
