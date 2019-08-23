from .component import Component

import os
import sys
import traceback
import imp

class InterpretError(Exception):
    pass

class InterpreterSetup(Component):
    def __init__(self):
        super().__init__('interpreter')
        self._blacklist = ['codecs', 'encodings', '__main__', 'logbook',
                           'io', 'abc', 'site', 'builtins', 'sys']

    def init(self, shell):
        shell.clear_locals()

    def dispose(self, shell):
        shell.clear_locals()
        # Delete all of the modules
        for name in list(sys.modules.keys()):
            if not name.startswith(tuple(self._blacklist)):
                del sys.modules[name]

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
            if getattr(v, 'quiet', False):
                print(v)
            else:
                raise InterpretError((''.join(traceback.format_exception(t, v, last_tb.tb_next))).strip())
