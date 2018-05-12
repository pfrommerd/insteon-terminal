import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import traceback

from insteon.msg.msg import Direction,DataType,MsgDef,MsgStreamDecoder,MsgStreamEncoder

import insteon.msg.xmlmsgreader as xmlreader

definitions = xmlreader.read_xml(os.path.join(os.path.dirname(__file__),'../res/msg_definitions.xml'))

decoder = MsgStreamDecoder(definitions)
encoder = MsgStreamEncoder(definitions)

for d in definitions.values():
    try:
        # Change the direction for the decoder...
        decoder._direction = d.direction
        decoder._reset_filtered_defs()

        msg = d.create()
        serialized = encoder.encode(msg)

        # Now feed the serialized version in byte-by-byte to the decoder
        for i in range(len(serialized) - 1):
            decoder.decode(bytes([serialized[i]]))
        deserialized = decoder.decode(bytes([serialized[-1]]))

        reserialized = encoder.encode(deserialized)
        # Make sure reserialzied = serialized
        if not serialized == reserialized:
            raise ValueError('Mismatching encode/decodes!')
    except Exception as e:
        print(traceback.format_exc())
        print('Failed: {}'.format(d.name))
        print('Serialized: {}'.format(serialized))
        print('Deserialized: {}'.format(deserialized))
        print('Reserialized: {}'.format(reserialized))
        sys.exit(1)

