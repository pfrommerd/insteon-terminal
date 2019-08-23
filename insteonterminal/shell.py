from .interpreter import Interpreter,InterpretError
from .component import Component
import os

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

    def init(self):
        for comp in self._components:
            comp.init(self)

    def deinit(self):
        for comp in reversed(self._components):
            comp.dispose(self)

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

    # Input-related methods
    def set_local(self, name, val):
        self._interpreter.locals[name] = val

    def unset_local(self, name):
        del self._interpreter.locals[name]

    def clear_locals(self):
        self._interpreter.locals.clear()

    def process_input(self, line, stdout, stdin, stderr):
        self._buffer.append(line)
        try:
            code = self._interpreter.try_compile('\n'.join(self._buffer))
        except InterpretError:
            self._buffer.clear()
            raise
        if not code:
            return None # We need to get more input
        self._buffer.clear()

        return str(self._interpreter.exec_code(code, stdout, stdin, stderr))

class LoadScript(Component):
    def __init__(self, res):
        super().__init__('load {}'.format(res))
        self._res = res

    def init(self, shell):
        if not shell.run_resource(self._res):
            print('Couldn\'t load script {}'.format(self._res))

    def dispose(self, shell):
        pass
