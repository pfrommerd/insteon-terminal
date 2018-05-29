import sys
from . import InsteonTerminal

term = InsteonTerminal()

# Happens only once
term.setup_locals()
term.load_sys_config()

term.interact()


