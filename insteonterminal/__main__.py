import sys
from . import InsteonTerminal

term = InsteonTerminal()
term.load_sys_config()

term.interact()


