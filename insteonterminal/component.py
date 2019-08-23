# All components must have an init and a dispose functionality
class Component:
    def __init__(self, name):
        self.name = name

    async def init(self, shell):
        pass

    async def dispose(self, shell):
        pass
