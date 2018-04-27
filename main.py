from insteonterminal.msg.msg import Msg,Direction,DataType,MsgDef

definition = MsgDef('foobar')
definition.append_field(DataType.BYTE, 'value_1')
