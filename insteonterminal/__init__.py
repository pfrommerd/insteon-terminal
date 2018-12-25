from terminal.interpreter import InterpreterSetup
from terminal.shell import Shell,LoadScript
from terminal.console import ConsoleTerminal,ConsoleCommands
from terminal.commands import Commands

def run():
    shell = Shell()
    shell.add_resource_path('.')
    shell.add_resource_path('config')
    shell.add_resource_path('/usr/share/insteon-terminal')

    terminal = ConsoleTerminal()

    shell.add_component(InterpreterSetup())
    shell.add_component(Commands())
    shell.add_component(ConsoleCommands(terminal))
    shell.add_component(LoadScript('sys_init.py'))
    shell.add_component(LoadScript('init.py'))

    terminal.run(shell)

