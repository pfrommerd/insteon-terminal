import insteon.msg.xmlmsgreader

definitions = insteon.msg.xmlmsgreader.read_xml('res/msg_definitions.xml')
print('........')
# Now read the user config next
load_config('init.py')
print('........')
