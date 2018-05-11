from insteonterminal.msg.msg import Direction,DataType,MsgDef

import insteonterminal.msg.xmlmsgreader as xmlreader

definitions = xmlreader.read_xml('msg_definitions.xml')
set_cat = definitions['SetHostDeviceCategory']
print(set_cat)
