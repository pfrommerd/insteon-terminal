from .component import Component

class Commands(Component):
    def __init__(self):
        super().__init__('shell_commands')

    def reload(self, shell):
        import threading
        shell.deinit()

        # Stop any running threads that are
        # not the main thread
        for thread in threading.enumerate():
            if thread is not threading.main_thread() and thread.is_alive():
                stop = getattr(thread, 'stop', None)
                if stop:
                    stop()

        shell.init()

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
