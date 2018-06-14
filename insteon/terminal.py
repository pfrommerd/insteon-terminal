import os
import sys
import traceback

class InsteonCommands:
    def __init__(self, term):
        self._term = term
        self._unload_hooks = []

    def help(self):
        print('Welcome to the Insteon Terminal')

    def load_config(self, filename):
        self._term.interpreter.exec_file(filename)

    def resolve_resource(self, filename):
        return self._term.resolve_resource(filename)

    def add_unload_hook(self, hook):
        self._unload_hooks.append(hook)

    def reload(self):
        # Execute the unload hooks
        for h in self._unload_hooks:
            h()
        self._unload_hooks.clear()

        self._term.deinit()
        self._term.init()

    def quit(self):
        for h in self._unload_hooks:
            h()
        self._unload_hooks.clear()

        self._term.deinit()

        sys.exit(0)

    def abort(self):
        sys.exit(1)


class InterpretError(Exception):
    pass

# The actual interpreter
class Interpreter:
    def __init__(self):
        self.locals = {}

    # Will return none if incomplete
    # Will raise any syntax errors
    def try_compile(self, source, filename='<input>', mode='single'):
        PyCF_DONT_IMPLY_DEDENT = 0x200
        # Handle multiple lines
        for line in source.split("\n"):
            line = line.strip()
            if line and line[0] != '#':
                break              
        else:
            if mode != "eval":
                source = "pass"     
        err = err1 = err2 = None
        code = code1 = code2 = None
        try:
            code = compile(source, filename, mode, PyCF_DONT_IMPLY_DEDENT)
        except SyntaxError as err:
            pass
        try:
            code1 = compile(source + "\n", filename, mode, PyCF_DONT_IMPLY_DEDENT)
        except SyntaxError as e:
            err1 = e
        try:
            code2 = compile(source + "\n\n", filename, mode, PyCF_DONT_IMPLY_DEDENT)
        except SyntaxError as e:
            err2 = e
        if code:
            return code
        if not code1 and repr(err1) == repr(err2):
            try:
                raise err1
            except:
                t, v, tb = sys.exc_info()
                
                try:
                    msg, (dummy_filename, lineno, offset, line) = v.args
                except ValueError:
                    # Not the format we expect; leave it alone
                    pass
                else:
                    # Stuff in the right filename
                    v = SyntaxError(msg, (filename, lineno, offset, line))
                raise InterpretError((''.join(traceback.format_exception_only(t, v))).strip())

    def exec_file(self, path):
        if path and os.path.isfile(path):
            code = ''
            with open(path, 'r') as f:
                code = f.read()
            # Interpret the code
            compiled = compile(code, filename=path, mode='exec')
            self.exec_code(compiled)

    def exec_code(self, compiled_code, stdout=None, stdin=None, stderr=None):
        try:
            return exec(compiled_code, self.locals)
        except SystemExit:
            raise
        except:
            t, v, last_tb = sys.exc_info()

            raise InterpretError((''.join(traceback.format_exception(t, v, last_tb.tb_next))).strip())

# The terminal also manages
# some state variables
class Shell:
    def __init__(self):
        self.interpreter = Interpreter()

        self.resource_paths = []
        self.components = []

        self._buffer = [] # Holds partial code

    def add_comp(self, comp):
        self.components.append(comp)

    def resolve_resource(self, filename):
        for l in self.resource_paths:
            path = os.path.join(l, filename)
            if os.path.isfile(path):
                return path
        return None

    def process_input(self, line, stdout, stdin, stderr):
        self._buffer.append(line)
        try:
            code = self.interpreter.try_compile('\n'.join(self._buffer))
        except InterpretError:
            self._buffer.clear()
            raise
        if not code:
            return None # We need to get more input
        self._buffer.clear()

        return str(self.interpreter.exec_code(code, stdout, stdin, stderr))

    def init(self):
        for comp in self.components:
            if comp[0]:
                comp[0](self) # Call the init function

    def deinit(self):
        for comp in reversed(self.components):
            if comp[1]:
                comp[1](self)

def create_interpreter_reloader():
    def load(term):
        # Clear interpreter locals
        modules = list(sys.modules.keys())
        for module in modules:
            if module.startswith('insteon.') and module != 'insteon.terminal':
                del sys.mdoules[module]
    return (load, None)

def create_print_redirect(printout):
    default_print = __builtins__.print
    def print(*objects, sep='', end='\n', file=printout, flush=False):
        default_print(*objects, sep=sep, end=end, file=file, flush=flush)

    def load(term):
        __builtins__.print = print

    def unload(term):
        __builtins__.print = default_print

    return (load, unload)

def create_commands_injector(obj):
    def load(shell):
        for attr in dir(obj):
            if not attr.startswith('_'):
                func = getattr(obj, attr)
                shell.interpreter.locals[attr] = func
    return (load, None)

def create_sysconfig_loader(filename):
    def load(shell):
        res = shell.resolve_resource(filename)
        if res:
            shell.interpreter.exec_file(res)
        else:
            print('Could not find system config!')

    def unload(shell):
        pass

    return (load, unload)

# Now the actual terminal that will
# have IO streams attached
class ConsoleTerminal:
    def __init__(self):
        import sys
        try:
            import readline
        except ImportError:
            pass

        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.stdin = sys.stdin
    
    def run(self, shell):
        more = False
        while True:
            try:
                prompt = '... ' if more else '>>> '
                try:
                    line = input(prompt) # TODO: Handle if we want to use something else besides stdin
                except EOFError:
                    self.stdout.write('\n')
                    break
                else:
                    try:
                        more = not shell.process_input(line, self.stdout, self.stderr, self.stdin)
                    except InterpretError as e:
                        print(e)

            except KeyboardInterrupt:
                self.write('\nKeyboardInterrupt\n')
                # Clear the input buffer
                shell.interpreter._buffer.clear()
                more = False

def run():
    import sys
    terminal = ConsoleTerminal()

    shell = Shell()
    # Will ensure that modules are reloaded and all locals are cleared
    # on deinit
    shell.add_comp(create_interpreter_reloader())

    # Inject the commands from the insteon commands object
    commands = InsteonCommands(shell)
    shell.add_comp(create_commands_injector(commands))

    # Setup logging anything outputted to the terminal
    # TODO
    
    # Lastly, add a system config loader
    shell.add_comp(create_sysconfig_loader('sys_init.py'))

    # Add default search paths for resources
    shell.resource_paths.extend([os.curdir, os.path.join(os.curdir, 'config')])

    shell.init() # Load system config and the light
    print('Welcome to the Insteon Terminal')
    terminal.run(shell)

if __name__ == '__main__':
    run()
