from insteon.msg.port import Port

# Just a formal definition of what
# really is a duck-typable object that
# can be called on a port object
class Operation:
    def __call__(self, modem):
        pass


# operator takes a function whose first
# parameter is a IO port and transforms it into a
# function that calls the original but with the first
# parameter switched to be the correct port in that particular
# context (for now that just means self._modem._port for a device)
def operator(func):
    def operation_exec(*args):
        if len(args) > 1 and isinstance(args[1], Port):
            return func(*args)

        def call_internal(port):
            a = tuple([args[0], port] + list(args[1:]))
            func(*a)

        # Now take the function and bind
        # the correct port
        if hasattr(args[0],'_modem'):
            if args[0]._modem:
                return call_internal(args[0]._modem.port)
            else:
                return call_internal

    return operation_exec
