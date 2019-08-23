from .interpreter import Interpreter,InterpretError
from .component import Component
import inspect
import logbook
import os

logger = logbook.Logger('console')

# A shell contains resource paths
# processes new input and components to load
class Shell:
    def __init__(self):
        self._interpreter = Interpreter()

        self._resource_paths = []
        self._components = []

        self._buffer = [] # Holds partial code

    # Component-related methods
    @property
    def components(self):
        return self._components

    def add_component(self, comp):
        self._components.append(comp)

    async def init(self):
        for comp in self._components:
            await comp.init(self)

    async def deinit(self):
        for comp in reversed(self._components):
            await comp.dispose(self)

    # Resource-related methods
    def add_resource_path(self, path):
        self._resource_paths.append(path)

    def resolve_resource(self, filename):
        for l in self._resource_paths:
            path = os.path.join(l, filename)
            if os.path.isfile(path):
                return path
        return None
    
    def run_resource(self, filename):
        res = self.resolve_resource(filename)
        if res:
            self._interpreter.exec_file(res)
            return True
        else:
            return False

    async def run_resource_async(self, filename):
        res = self.resolve_resource(filename)
        if res:
            await self._interpreter.exec_file_async(res)
            return True
        else:
            return False

    # Input-related methods
    def set_local(self, name, val):
        self._interpreter.locals[name] = val

    def unset_local(self, name):
        del self._interpreter.locals[name]

    def clear_locals(self):
        self._interpreter.locals.clear()

    async def process_input(self, line, stdout, stdin, stderr):
        self._buffer.append(line)
        try:
            code = self._interpreter.try_compile_async('\n'.join(self._buffer))
        except InterpretError:
            self._buffer.clear()
            raise
        if not code:
            return False
        self._buffer.clear()

        res = await self._interpreter.exec_code_async(code, stdout, stdin, stderr)
        if res:
            print(res, file=stdout)
        return True

class LoadScript(Component):
    def __init__(self, res):
        super().__init__('load {}'.format(res))
        self._res = res

    async def init(self, shell):
        if not await shell.run_resource_async(self._res):
            print('Couldn\'t load script {}'.format(self._res))

    async def dispose(self, shell):
        pass
