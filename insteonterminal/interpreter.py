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

    async def init(self, shell):
        shell.clear_locals()

    async def dispose(self, shell):
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

    def try_compile_async(self, source, filename='<input>', mode='single'):
        if not '\n' in source:
            source = 'async def __ex():\n' + \
                    ' ret = ' + source + '\n' + \
                    ' return (ret, locals())\n'
        else:
            source = 'async def __ex(): ' + ''.join(f'\n {l}' for l in source.split('\n')) + \
                    '\n return (None, locals())\n'
        return self.try_compile(source, filename, mode)

    def exec_file(self, path):
        if path and os.path.isfile(path):
            code = ''
            with open(path, 'r') as f:
                code = f.read()
            # Interpret the code
            compiled = compile(code, filename=path, mode='exec')
            self.exec_code(compiled)

    async def exec_file_async(self, path):
        if path and os.path.isfile(path):
            code = ''
            with open(path, 'r') as f:
                code = f.read()
            code = 'async def __ex(): ' + ''.join(f'\n {l}' for l in code.split('\n')) + \
                        '\n return locals()'
            # Interpret the code
            compiled = compile(code, filename=path, mode='exec')
            if '__ex' in self.locals:
                del self.locals['__ex']
            self.exec_code(compiled)
            func = self.locals['__ex']
            del self.locals['__ex']
            self.locals.update(await func())

    async def exec_code_async(self, compiled_code, stdout=None, stdin=None, stderr=None, locals_=None):
        if locals_ is None:
            locals_ = self.locals
        if '__ex' in locals_:
            del locals_['__ex']

        try:
            self.exec_code(compiled_code, stdout, stdin, stderr, locals_)
            func = locals_['__ex']
            del locals_['__ex']

            ret, new_locals = await func()
            locals_.update(new_locals)
            return ret
        except SystemExit:
            raise
        except InterpretError as e:
            raise e
        except:
            t, v, last_tb = sys.exc_info()
            if getattr(v, 'quiet', False):
                print(v, file=stdout)
            else:
                raise InterpretError((''.join(traceback.format_exception(t, v, last_tb.tb_next))).strip())

    def exec_code(self, compiled_code, stdout=None, stdin=None, stderr=None, locals_=None):
        if locals_ is None:
            locals_ = self.locals
        try:
            return exec(compiled_code, locals_)
        except SystemExit:
            raise
        except InterpretError as e:
            raise e
        except:
            t, v, last_tb = sys.exc_info()
            if getattr(v, 'quiet', False):
                print(v, file=stdout)
            else:
                raise InterpretError((''.join(traceback.format_exception(t, v, last_tb.tb_next))).strip())
