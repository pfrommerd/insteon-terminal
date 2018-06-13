import readline
import code
import os
import sys
import threading
import importlib
import pickle

class Commands:
    _reload_hooks = []
    _unload_hooks = []

    def __init__(self, term):
        self._term = term
        self._reload_hooks = []
        self._unload_hooks = []

    def help(self):
        print('Welcome to the Insteon Terminal')

    def load_config(self, filename):
        self._term.load_file(filename)

    def resolve_resource(self, filename):
        return self._term.resolve_resource(filename)

    def require_resource(self, filename):
        path = self._term.resolve_resource(filename)
        if not path:
            print('Fatal missing resource: ' + filename)
            abort()
            return None
        return path


    def add_unload_hook(self, hook):
        self._unload_hooks.append(hook)

    # Will be run on reload, but not on quit
    def add_reload_hook(self, hook):
        self._reload_hooks.append(hook)

    def reload(self):
        # Execute and then reset the reload hooks
        for h in self._unload_hooks:
            h()
        self._unload_hooks.clear()

        self._term.unload_modules()
        self._term.kill_background_threads()

        # Now setup again
        for h in self._reload_hooks:
            h()
        self._reload_hooks.clear()

        # Make sure the commands are
        # in the locals again
        self._term.setup_commands()
        # Reload the system config
        self._term.load_sys_config()

    def quit(self):
        for h in Commands._unload_hooks:
            h()
        self._unload_hooks.clear()

        self._term.unload_modules()
        self._term.kill_background_threads()

        sys.exit(0)

    def abort(self):
        sys.exit(1)


# The actual shell which does the 
# interpreting
# overloads the raw_input to log that to a file
class InsteonShell(code.InteractiveConsole):
    def write(self, line):
        if hasattr(sys, 'interprethook') and sys.interprethook:
            sys.interprethook(line)

        result = super().write(line)
        return result

# The terminal also manages
# some state variables
class InsteonTerminal:
    def __init__(self):
        self._shell = InsteonShell()
        self._commands = Commands(self)
        self._protected_locals = []

        # Setup the locals
        self.setup_commands()

    def resolve_resource(self, filename):
        locations = [os.curdir, os.path.join(os.curdir, 'config'), os.path.expanduser('~/.config/insteon-terminal'), os.path.join(sys.prefix,'share/insteon-terminal')]

        for l in locations:
            path = os.path.join(l, filename)
            if os.path.isfile(path):
                return path
        return None


    def setup_commands(self):
        self._shell.locals.clear()

        for attr in dir(Commands):
            if not attr.startswith('_'):
                # We have a function!
                func = getattr(self._commands, attr)
                self._shell.locals[attr] = func
    
    def load_sys_config(self):
        confpath = self.resolve_resource('sys_init.py')
        if not confpath:
            print('Could not find system config file!')
            return

        self.load_file(confpath)

    def load_file(self, path):
        if path and os.path.isfile(path):
            code = ''
            with open(path, 'r') as f:
                code = f.read()
            # Interpret the code
            compiled = compile(code,path,'exec')
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
            if module.startswith('insteon.') and module != 'insteonterminal':
                del sys.modules[module]

    def interact(self):
        self._shell.interact(banner="Welcome to the Insteon Terminal!", exitmsg='')

def run():
    import sys

    term = InsteonTerminal()
    term.load_sys_config()

    term.interact()

if __name__ == '__main__':
    run()
