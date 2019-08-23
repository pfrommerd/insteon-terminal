# All components must have an init and a dispose functionality
class Component:
    def __init__(self, name):
        self.name = name

    def init(self, shell):
        pass

    def dispose(self, shell):
        pass
