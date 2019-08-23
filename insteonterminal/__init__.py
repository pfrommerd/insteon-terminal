from .interpreter import InterpreterSetup
from .shell import Shell,LoadScript
from .commands import Commands
from .component import Component

import os
import logbook
import builtins
import appdirs
import asyncio

# These two loggers
# will not be printed by the stream logger
console_logger = logbook.Logger('console')
prompt_logger = logbook.Logger('prompt')

log_dir = appdirs.user_log_dir('insteon-terminal')
config_dir = appdirs.user_config_dir('insteon-terminal')

class SysConfig(Component):
    def __init__(self):
        super().__init__('sys_config')

    async def init(self, shell):
        import insteon.io.xmlmsgreader
        shell.set_local('definitions', insteon.io.xmlmsgreader.read_default_xml())

    async def dipose(self, shell):
        shell.unset_local('definitions')

# The logging setup
class LoggingSetup(Component):
    def __init__(self, stdout, stderr):
        super().__init__('logging')
        self._stdout = stdout
        self._stderr = stderr
        self._original_print = builtins.print

        stream_handler = logbook.StreamHandler(self._stdout, bubble=True,
                                filter=lambda r,h: r.channel != 'console' and r.channel != 'prompt')

        def format(record, handler):
            if record.level != logbook.INFO:
                return logbook.get_level_name(record.level) + ': ' + record.message
            else:
                return record.message
        stream_handler.formatter = format

        self._setup = logbook.NestedSetup([
                logbook.NullHandler(),
                stream_handler,
                logbook.FileHandler(os.path.join(log_dir, 'insteon-terminal.log'), bubble=True),
                logbook.NullHandler(filter=lambda r,h: r.channel.startswith('insteon.io.hub') \
                                                        and r.level == logbook.TRACE),
                logbook.FileHandler(os.path.join(log_dir, 'insteon-trace.log'), bubble=True)
            ])

    async def init(self, shell):
        def print(*args, **kwargs):
            self._original_print(*args, **kwargs)
            lines = ' '.join(map(str, args)).split('\n')
            for l in lines:
                console_logger.info(l)
        builtins.print = print

        self._setup.push_application()

    async def dispose(self, shell):
        builtins.print = self._original_print

        self._setup.pop_application()

def run():
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    from .console import ConsoleTerminal,ConsoleCommands
    terminal = ConsoleTerminal()
    terminal.add_prompt_listener(lambda p,v: prompt_logger.info(v))

    shell = Shell()

    shell.add_resource_path('.')
    shell.add_resource_path(config_dir)

    shell.add_component(InterpreterSetup())
    shell.add_component(LoggingSetup(terminal.stdout, terminal.stderr))

    shell.add_component(Commands())
    shell.add_component(ConsoleCommands(terminal))


    shell.add_component(SysConfig())
    shell.add_component(LoadScript('init.py'))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(terminal.run(shell))
