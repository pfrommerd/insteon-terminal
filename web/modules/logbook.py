# Just some dummy things
class NestedSetup:
    def __init__(self, setup):
        pass

    def push_application(self):
        pass

    def pop_application(self):
        pass

class NullHandler:
    def __init__(self, filter=None):
        pass

class FileHandler:
    def __init__(self, filename, filter=None, bubble=False):
        pass

class StreamHandler:
    def __init__(self, stdout, filter=None, bubble=False):
        pass

class Logger:
    def __init__(self, name):
        self._name = name

    def info(self, *args):
        if self._name != 'console' and self._name != 'prompt':
            print(*args)

    def trace(self, *args):
        if self._name != 'console' and self._name != 'prompt':
            print('WARN: ', *args)

    def debug(self, *args):
        if self._name != 'console' and self._name != 'prompt':
            print('DEBUG: ', *args)

    def warn(self, *args):
        if self._name != 'console' and self._name != 'prompt':
            print('WARN: ', *args)

    def error(self, *args):
        if self._name != 'console' and self._name != 'prompt':
            print('ERROR: ', *args)
