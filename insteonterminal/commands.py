from .component import Component
import inspect

class Commands(Component):
    def __init__(self):
        super().__init__('shell_commands')
        self._hooks = []

    async def reload(self, shell):
        await shell.deinit()
        await shell.init()

    def list_components(self, shell):
        for i, c in enumerate(shell.components):
            print('{}: {}'.format(i, c.name))

    def add_shutdown_hook(self, hook):
        self._hooks.append(hook)

    async def init(self, shell):
        shell.set_local('list_components', \
                lambda: self.list_components(shell))
        shell.set_local('add_shutdown_hook', \
                lambda h: self.add_shutdown_hook(h))
        shell.set_local('reload', \
                lambda: self.reload(shell))

    async def dispose(self, shell):
        shell.unset_local('list_components')
        shell.unset_local('reload')
        for h in self._hooks:
            val = h()
            if inspect.iscoroutine(val):
                await val
        self._hooks.clear()
