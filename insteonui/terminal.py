import readline
import code
import os
import sys
import threading
import importlib

class Commands:
    _reload_hooks = []
    _unload_hooks = []

    def help():
        print('Welcome to the Insteon Terminal')

    def quit():
        for h in Commands._unload_hooks:
            h()
        Commands._unload_hooks.clear()

        term.unload_modules()
        term.kill_background_threads()

        sys.exit(0)

    def load_config(filename):
        term.load_file(filename)

    def add_unload_hook(hook):
        Commands._unload_hooks.append(hook)

    # Will be run on reload, but not on quit
    def add_reload_hook(hook):
        Commands._reload_hooks.append(hook)

    def reload():
        # Execute and then reset the reload hooks
        for h in Commands._unload_hooks:
            h()
        Commands._unload_hooks.clear()

        term.unload_modules()
        term.kill_background_threads()

        # Now setup again
        for h in Commands._reload_hooks:
            h()
        Commands._reload_hooks.clear()

        term.setup_locals()
        term.load_sys_config()

# The actual shell which does the 
# interpreting
class InsteonShell(code.InteractiveConsole):
    pass

# The terminal also manages
# some state variables
class InsteonTerminal:
    def __init__(self):
        self._shell = InsteonShell()

    def setup_locals(self):
        self._shell.locals.clear()

        for attr in dir(Commands):
            if not attr.startswith('_'):
                # We have a function!
                func = getattr(Commands, attr)
                self._shell.locals[attr] = func

    def load_sys_config(self):
        self.load_file('sys_init.py')

    def load_file(self, filename):
        if os.path.isfile(filename):
            code = ''
            with open(filename, 'r') as f:
                code = f.read()
            # Interpret the code
            compiled = compile(code,filename,'exec')
            self._shell.runcode(compiled)

    def kill_background_threads(self):
        # Kill any background threads that might be running
        for t in threading.enumerate():
            if t != threading.current_thread():
                # Hack this in there, the threads MUST follow this
                # by program design
                t.override_kill = True

    def unload_modules(self):
        modules = list(sys.modules.keys())
        for module in modules:
            if module.startswith('insteon.') and module != 'insteon.terminal':
                del sys.modules[module]

    def interact(self):
        self._shell.interact(banner="Welcome to the Insteon Terminal!", exitmsg='')

if __name__=="__main__":
    term = InsteonTerminal()

    # Happens only once
    term.setup_locals()
    term.load_sys_config()

    term.interact()
