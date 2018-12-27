from terminal.interpreter import InterpreterSetup
from terminal.shell import Shell,LoadScript
from terminal.console import ConsoleTerminal,ConsoleCommands
from terminal.commands import Commands
from terminal.component import Component

import logbook
import builtins
import appdirs

# These two loggers
# will not be printed by the stream logger
console_logger = logbook.Logger('console')
prompt_logger = logbook.Logger('prompt')

# The logging setup
class LoggingSetup(Component):
    def __init__(self, stdout, stderr):
        super().__init__('logging')
        self._stdout = stdout
        self._stderr = stderr
        self._original_print = builtins.print
        self._stream_handler = logbook.StreamHandler(self._stdout, bubble=True,
                                filter=lambda r,h: r.channel != 'console' and r.channel != 'prompt')

        def format(record, handler):
            if record.level != logbook.INFO:
                return logbook.get_level_name(record.level) + ': ' + record.message
            else:
                return record.message
        self._stream_handler.formatter = format

        self._file_handler = logbook.FileHandler('insteon-terminal.log', bubble=True)

    def init(self, shell):
        def print(*args, **kwargs):
            self._original_print(*args, **kwargs)
            lines = ' '.join(map(str, args)).split('\n')
            for l in lines:
                console_logger.info(l)
        builtins.print = print

        self._file_handler.push_application()
        self._stream_handler.push_application()

    def dispose(self, shell):
        builtins.print = self._original_print

        self._stream_handler.pop_application()
        self._file_handler.pop_application()

def run():
    shell = Shell()
    shell.add_resource_path('.')
    shell.add_resource_path('config')
    shell.add_resource_path(appdirs.user_config_dir('insteon-terminal'))
    shell.add_resource_path('/usr/share/insteon-terminal')

    terminal = ConsoleTerminal()
    terminal.add_prompt_listener(lambda p,v: prompt_logger.info(v))

    shell.add_component(InterpreterSetup())
    shell.add_component(LoggingSetup(terminal.stdout, terminal.stderr))
    shell.add_component(Commands())
    shell.add_component(ConsoleCommands(terminal))
    shell.add_component(LoadScript('sys_init.py'))
    shell.add_component(LoadScript('init.py'))

    terminal.run(shell)

