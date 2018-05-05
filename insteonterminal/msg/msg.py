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
    INVALID = 0xff

def buffer_get_field(buf, field):
    if field[1] == DataType.BYTE:
        return struct.unpack('c', data[field[0]:field[0]+1])[0]
    elif field[1] == DataType.INT:
        return struct.unpack('i', data[field[0]:field[0]+4])[0]
    elif field[1] == DataType.FLOAT:
        return struct.unpack('f', data[field[0]:field[0]+4])[0]
    elif field[1] == DataType.ADDRESS:
        return (struct.unpack('c', data[field[0]:field[0]+1])[0],
                struct.unpack('c', data[field[0]+1:field[0]+2])[0],
                struct.unpack('c', data[field[0]+2:field[0]+3])[0])
    else:
        return None

def buffer_set_field(buf, field, value):
    if field[1] == DataType.BYTE:
        buf[field[0]] = struct.pack('c',value)
    elif field[1] == DataType.INT:
        buf[field[0]:field[0]+4] = struct.pack('i', value)
    elif field[1] == DataType.FLOAT:
        buf[field[0]:field[0]+4] = struct.pack('f', value)
    elif field[1] == DataType.ADDRESS:
        buf[field[0]] = struct.pack('c', value[0])[0]
        buf[field[0] + 1] = struct.pack('c', value[1])[0]
        buf[field[0] + 2] = struct.pack('c', value[2])[0]

class MsgDef:
    name = ""
    header_length = 0
    length = 0
    # The filter format is (offset, type, name, default_val)
    fields_map = {}
    fields_list = []

    def __init__(self, name=''):
        self.name = name

    def append_field(self, data_type, name, default_value): # Changes the length
        offset = self.length

        field_len = data_type.value
        self.length = self.length + field_len

        # Add to the map
        self.fields_map[name] = (offset, data_type, name, default_value)
        self.fields_list.append( (offset, data_type, name, default_value) )

    def contains_field(self, name):
        return name in self.fields_map

    def get_field(self, name):
        return self.fields_map[name]

    def deserialize(self, buf):
        m = {}
        for f in fields_list:
            val = buffer_get_field(buf, f)
            m[f[2]] = val

    def serialize(self, msg):
        buf = bytearray(self.length)
        for f in fields_list:
            val = msg[f[2]] if f[2] in msg else f[3]
            if val is not None:
                buffer_set_field(buf, f, val)

class MsgStreamEncoder:
    pass

class MsgStreamDecoder:
    buf = bytearray()
    pass

