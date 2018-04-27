from enum import Enum
import struct

class Direction(Enum):
    TO_MODEM = 'to_modem'
    FROM_MODEM = 'from_modem'
    INVALID = 'invalid'

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

class MsgDef:
    name = ""
    fields_map = {}
    fields_list = []
    length = 0
    header_length = 0

    def __init__(self, name=''):
        self.name = name

    def append_field(self, data_type, name):
        offset = self.length

        field_len = data_type.value
        self.length = self.length + field_len

        # Add to the map
        self.fields_map[name] = (offset, data_type, name)
        self.fields_list.append( (offset, data_type, name) )

    def contains_field(self, name):
        return name in self.fields_map

    def get_field(self, name):
        return self.fields_map[name]

class Msg:
    data = bytearray()
    direction = Direction.TO_MODEM
    definition = MsgDef()
    quiet_time = 0 # The time of no-IO that this message requires

    # Msg can either be a definition or a msg to copy from
    def __init__(self, msg, direction=Direction.TO_MODEM): 
        if isinstance(msg, Msg):
            # Copy constructor
            self.data[:] = msg.data
            self.direction = msg.direction
            self.definition = msg.definition
            self.quiet_time = msg.quiet_time
        elif isinstance(msg, MsgDef):
            self.definition = msg
            self.direction = direction
            self.data = bytearray(msg.length)

    @property
    def command_code(self):
        return -1 if len(data) < 2 else data[1]

    def get_field(self, field):
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

    def set_field(self, field, value):
        if field[1] == DataType.BYTE:
            self.data[field[0]] = struct.pack('c',value)
        elif field[1] == DataType.INT:
            self.data[field[0]:field[0]+4] = struct.pack('i', value)
        elif field[1] == DataType.FLOAT:
            self.data[field[0]:field[0]+4] = struct.pack('f', value)
        elif field[1] == DataType.ADDRESS:
            self.data[field[0]] = struct.pack('c', value[0])[0]
            self.data[field[0] + 1] = struct.pack('c', value[1])[0]
            self.data[field[0] + 2] = struct.pack('c', value[2])[0]

    def get(self, field_name):
        if field in self.definition.fields_map:
            return self.get_field(self.definitions.fields_map[field])
        else:
            return None

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        s = 'OUT:' if self.direction == Direction.TO_MODEM else 'IN:'
        for f in self.definition.fields_list:
            if f.name == 'messageFlags':
                s = s + f[2] + ':' + self.get(f.name)
            else:
                s = s + f[2] + ':' + self.get(f.name)
            s = s + '|'
