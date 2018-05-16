from time import time as _time
import queue
import threading
import inspect

class Channel:
    def __init__(self, filter=None, maxqueue=0):
        self._queue = queue.Queue(maxqueue)

        self._counter = 0 # Number of messages queued
        self._counter_lock = threading.Lock()

        self._filter = filter

    @property
    def has_filter(self):
        return self._filter is not None

    @property
    def active(self):
        return not self._queue.empty()

    @property
    def has_activated(self):
        return self.num_sent > 0

    @property
    def num_sent(self):
        with self._counter_lock:
            return self._counter

    def reset_num_sent(self):
        with self._counter_lock:
            self._counter = 0

    def clear(self):
        with self._queue.mutex:
            self._queue.queue.clear()

    def set_queuesize(self, newsize):
        # oops, just for get about the current
        # elements for now
        self._queue = queue.Queue(newsize)

    def set_filter(self, filter):
        self._filter = filter

    def chain_filter(self, filter):
        if self._filter:
            f = self._filter
            def chain(*args):
                return f(*args) and filter(*args)
            self._filter = chain
        else:
            self._filter = filter

    # Waits until there is at least one element in the queue
    # but doesn't take it
    def wait(self, timeout=None):
        with self._queue.not_empty:
            if timeout is None:
                if not self._queue._qsize():
                    self._queue.not_empty.wait()
                return True
            elif timeout > 0:
                endtime = _time() + timeout
                while not self._queue._qsize():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        return False
                    self._queue.not_empty.wait(remaining)
                return True
            elif timeout <= 0:
                # Just return whether there
                # is anything in the queue
                return self._queue._qsize()

    def recv(self, timeout=None):
        try:
            if timeout is None:
                return self._queue.get()
            elif timeout > 0:
                return self._queue.get(True, timeout)
            elif timeout <= 0:
                return self._queue.get(False)
        except queue.Empty:
            return None

    def send(self, *args):
        # Push args tuple onto queue
        # if only a single arg, push the first arg
        arg = args
        if len(arg) == 1:
            arg = args[0]
        elif len(arg) == 0:
            arg = None

        try:
            if not self._filter or self._filter(*args):
                with self._counter_lock:
                    self._counter = self._counter + 1
                    self._queue.put(arg)
        except queue.Full:
            return # Drop...

    def __call__(self, *args):
        self.send(*args)

# Now the resolver
# utility
def resolver(param_name, res):
    # The actual function that gets
    # called on decorate
    def decorate(func):
        # Get the original function signature
        # to find the argument number that
        # we need to bind to
        sig = inspect.signature(func)
        if not param_name in sig.parameters:
            # Help!
            raise ValueError('Binding param not found!')
        param_idx = list(sig.parameters).index(param_name)

        # The actual function that
        # is executed on method invocation
        def exec_func(*args, **kwargs):
            # Check if the argument has been manually supplied
            if param_name in kwargs or len(args) > param_idx:
                return func(*args, **kwargs)

            # A partially-bound function
            # that just needs the operand
            def call_internal(param):
                kwargs[param_name] = param
                return func(*args, **kwargs)

            # Otherwise try to resolve the parameter 
            param = res(args, kwargs)
            if param is not None:
                return call_internal(param)
            else:
                # Return a partially-bound function
                return call_internal

        # return the method that gets called
        return exec_func
    # return the actual decorator
    return decorate

def port_resolver(param_name):
    def resolve_port(args, kwargs):
        if hasattr(args[0], '_modem') and args[0]._modem:
            return args[0]._modem.port
        else:
            return None

    return resolver(param_name, resolve_port)


def modem_resolver(param_name):
    def resolve_modem(args, kwargs):
        if hasattr(args[0], '_modem'):
            return args[0]._modem
        else:
            return None

    return resolver(param_name, resolve_modem)

def registry_resolver(param_name):
    def resolve_registry(args, kwargs):
        if hasattr(args[0], '_registry'):
            return args[0]._registry
        else:
            return None

    return resolver(param_name, resolve_registry)

# Now error and logger-related stuff
