from insteonterminal.msg.msg import Direction,DataType,MsgDef

import insteonterminal.msg.xmlmsgreader as xmlreader

definitions = xmlreader.read_xml('msg_definitions.xml')
print(definitions)
