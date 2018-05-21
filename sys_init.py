import insteon.msg.xmlmsgreader

definitions = insteon.msg.xmlmsgreader.read_xml('res/msg_definitions.xml')

# Overload the exceptions handler to
# make InsteonErrors pretty-printed
# by default

import sys

def custom_excepthook(type, value, tb):
    import traceback
    
    lines = traceback.format_exception(type, value, tb.tb_next)
    print(lines)
    print(''.join(lines), end='')

sys.excepthook = custom_excepthook

# Don't pollute the namespace
del custom_excepthook 
del sys
    

print('........')
# Now read the user config next
load_config('init.py')
print('........')
