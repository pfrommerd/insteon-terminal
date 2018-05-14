
""" operator is a decorator that takes a member function and mangles its first
 parameter (the one after self) to be optional based on a type
 and to be resolved by a specified manner if not supplied
 if it cannot be resolved (resolver return null), it returns
 a partially-bound function that can be bound to the type

 operator decorators can also be chained
 (the partially-bound function will also be chained in that case)

 TODO: Partially-bound function chaining isn't working correct
 TODO: Also, make a function that forces a partially-bound function
       to be returned
"""
def operator(func, operand_type, operand_resolver):
    def operation_exec(*args):
        # Check if the argument has been manually supplied
        if len(args) > 1 and isinstance(args[1], operand_type):
            return func(*args)

        # A partially-bound function
        # that just needs the operand
        def call_internal(operand):
            a = tuple([args[0], operand] + list(args[1:]))
            return func(*a)

        # Otherwise try to resolve the operand
        operand = operand_resolver(*args)
        if operand is not None:
            return call_internal(operand)
        else:
            return call_internal

    return operation_exec

# We have to put the imports inside
# as this might be imported in those files
# themselves (such as insteon.dev.Device)
# and we want to avoid a circular import

def port_operator(func):
    from insteon.msg.port import Port
    def resolve_port(*args):
        if hasattr(args[0], '_modem') and args[0]._modem:
            return args[0]._modem.port
        else:
            return None

    return operator(func, Port, resolve_port)


def modem_operator(func):
    from insteon.dev.modem import Modem
    def resolve_modem(*args):
        if hasattr(args[0], '_modem'):
            return args[0]._modem
        else:
            return None

    return operator(func, Modem, resolve_modem)

def registry_operator(func):
    from insteon.dev.Device import DeviceRegistry
    def resolve_registry(*args):
        if hasattr(args[0], '_registry'):
            return args[0]._registry
        else:
            return None

    return operator(func, DeviceRegistry, resolve_registry)
