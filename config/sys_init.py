# Now load the msg definitions for the user to use

import insteon.io.xmlmsgreader
definitions = insteon.io.xmlmsgreader.read_default_xml()

# Don't pollute the namespace
del insteon.io.xmlmsgreader

print('........')

# Load the init file (if it exists in the system)
load_config(resolve_resource('init.py'))

print('........')
