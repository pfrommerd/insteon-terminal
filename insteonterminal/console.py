from .interpreter import InterpretError
from .component import Component

import aioconsole

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
        self._input_listeners = []

    def add_prompt_listener(self, l):
        self._input_listeners.append(l)

    async def prompt(self, prompt=''):
        i = await aioconsole.ainput(prompt)
        for l in self._input_listeners:
            l(prompt, i)
        return i

    def clear(self):
        import os
        os.system('clear')
    
    async def run(self, shell):
        try:
            await shell.init()
        except InterpretError as e:
            print(e)
            return

        more = False
        while True:
            try:
                prompt = '... ' if more else '>>> '
                try:
                    line = await self.prompt(prompt) # TODO: Handle if we want to use something else besides stdin
                except EOFError:
                    self.stdout.write('\n')
                    break
                else:
                    try:
                        more = not await shell.process_input(line, self.stdout, self.stderr, self.stdin)
                    except InterpretError as e:
                        print(e)

            except KeyboardInterrupt:
                self.stdout.write('\nKeyboardInterrupt\n')
                # Clear the input buffer
                shell._buffer.clear()
                more = False

class ConsoleCommands(Component):
    def __init__(self, console):
        self._console = console
        super().__init__('console_commands')

    # The commands
    def clear(self):
        self._console.clear()

    async def init(self, shell):
        shell.set_local('clear', self.clear)

    async def dispose(self, shell):
        shell.unset_local('clear')
