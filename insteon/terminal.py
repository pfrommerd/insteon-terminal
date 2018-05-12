import readline
import code
import os
import sys
import threading
import importlib

class Commands:
    def help():
        print('Welcome to the Insteon Terminal')

    def quit():
        term.unload_modules()
        term.kill_background_threads()

        sys.exit(0)

    def load_config(filename):
        term.load_file(filename)

    def reload():
        term.unload_modules()
        term.kill_background_threads()
        # Now setup again
        term.setup_locals()
        term.load_sys_config()

class InsteonTerminal:
    def __init__(self):
        self._locals = {}
        self._shell = code.InteractiveConsole(self._locals)

    def setup_locals(self):
        self._locals.clear()

        for attr in dir(Commands):
            if not attr.startswith('_'):
                # We have a function!
                func = getattr(Commands, attr)
                self._locals[attr] = func

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

    term.setup_locals()
    term.load_sys_config()

    term.interact()
