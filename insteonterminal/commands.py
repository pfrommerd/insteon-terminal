from .component import Component

class Commands(Component):
    def __init__(self):
        super().__init__('shell_commands')

    async def reload(self, shell):
        await shell.deinit()
        await shell.init()

    def list_components(self, shell):
        for i, c in enumerate(shell.components):
            print('{}: {}'.format(i, c.name))

    async def init(self, shell):
        shell.set_local('list_components', \
                lambda: self.list_components(shell))
        shell.set_local('reload', \
                lambda: self.reload(shell))

    async def dispose(self, shell):
        shell.unset_local('list_components')
        shell.unset_local('reload')
