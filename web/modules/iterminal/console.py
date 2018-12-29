from .interpreter import InterpretError
from .component import Component
import sys

class ConsoleTerminal:
    def __init__(self):
        sys.stdout.write = self.write
        sys.stdout.flush = lambda: None
        sys.stderr.write = self.write
        sys.stderr.flush = lambda: None
        sys.stdin = None # Disable stdin

        self.stdout = sys.stdout
        self.stdin = sys.stdin
        self.stderr = sys.stderr

        self._input_listeners = []

    def add_prompt_listener(self, l):
        self._input_listeners.append(l)

    def clear(self):
        pass

    def write(self, text):
        import js
        js.call('window.console_write', text)

    def run(self, shell):
        # Return ourself so the java script
        # can call on_input and on_ready when it's ready
        self._shell = shell
        shell.init()
        import js

        def _input(prompt, line):
            for l in self._input_listeners:
                l(prompt, line)
            more = False
            try:
                more = not self._shell.process_input(line, sys.stdout, sys.stderr, sys.stdin)
            except InterpretError as e:
                print(e)
            _prompt(more)
        def _prompt(more):
            prompt = '... ' if more else '>>> '
            promise = js.call('window.console_prompt', prompt)
            promise.then(lambda l: _input(prompt, l))
        _prompt(False)

class ConsoleCommands(Component):
    def __init__(self, console):
        self._console = console
        super().__init__('console_commands')

    # The commands
    def clear(self):
        self._console.clear()

    def init(self, shell):
        shell.set_local('clear', self.clear)

    def dispose(self, shell):
        shell.unset_local('clear')
