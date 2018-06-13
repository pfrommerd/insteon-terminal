# Setup the logging
import sys

import logbook
import logbook.compat
import warnings

# Setup the "console" logger, which prints to stdout
# things in the 'console' channel or any warnings/errors/critical msgs
# in any other channel

handler = logbook.StreamHandler(sys.stdout)

# Format to print 'WARNING' or 'ERORR' before message
def formatter(record, handler):
    import logbook
    if record.level == logbook.WARNING or \
        record.level == logbook.ERROR or \
        record.level == logbook.CRITICAL:
        return record.level_name + ': ' + record.message
    else:
        return record.message

# Only let through if warning or error or to 'console' logger
# Explicitly don't print whatever the case if the 'noprint' extra
# has been set
def filterer(record, handler):
    import logbook

    if 'noprint' in record.extra and record.extra['noprint']:
        return False

    if record.level == logbook.WARNING or \
        record.level == logbook.ERROR or \
        record.level == logbook.CRITICAL:
        return True
    else:
        return record.channel == 'console'

handler.formatter = formatter
handler.filter = filterer

handler.push_application()

# Redirect warning calls to logbook
import logbook.compat
logbook.compat.redirect_warnings()

import warnings
# Always show warnings for the console
# so that when the user re-runs a command the
# warning shows twice
warnings.simplefilter('always')

# Clean up logging-specific imports
# so we don't pollute the main namespace
del handler
del formatter
del filterer

del logbook
del warnings

# Overload print to make printed statements be logged
# to the "console" logger (which uses stdout, not print())

def print(*objects, sep='', end='\n', file=sys.stdout, flush=False):
    import sys
    import logbook

    if file is not sys.stdout: # Don't print to the console
        __builtins__['print'](*objects, sep=sep, end=end, file=file, flush=flush)

    logger = logbook.Logger('console')
    msg = sep.join(map(str, objects)) + end
    for m in msg.split('\n'):
        if len(m.strip()) > 0:
            logger.info(m)

# We just stash this in sys,
# the interpreter will call it on input
# and on eval result

# This will let us print out user input and any results
# and not just program-generated messages
def custom_interprethook(line):
    import logbook
    logger = logbook.Logger('console')
    def inject_noprint(r):
        r.extra['noprint'] = True
    with logbook.Processor(inject_noprint).applicationbound():
        logger.info(line)

sys.interprethook = custom_interprethook

del custom_interprethook

# Overload the exceptions handler to
# make InsteonErrors pretty-printed
# by default to the console

def custom_excepthook(type, value, tb):
    import traceback
    import inspect
    import insteon.util
    import logbook

    
    if isinstance(value, insteon.util.InsteonError):
        logger = logbook.Logger('console')
        msg = 'Insteon error: {}'
        exc = value
        while exc:
            logger.error(msg.format(str(exc)))
            if exc.__cause__:
                msg = '  Caused by: {}'
                exc = exc.__cause__
            elif exc.__context__:
                msg = '  During: {}'
                exc = exc.__context__
            else:
                exc = None

    exception_module = inspect.getmodulename(traceback.extract_tb(tb.tb_next)[-1][0])

    # Handle syntax error differently
    if isinstance(value, SyntaxError):
        exception_module = inspect.getmodulename(value.filename)

    if not exception_module:
        exception_module = '<console>'

    logger = logbook.Logger(exception_module)

    # If it is an instance of insteon error
    # tell the console handler no to print
    def inject_noprint(r):
        r.extra['noprint'] = isinstance(value, insteon.util.InsteonError)
        # Add a special "(hidden)" before the printout
        # if the full trace is hidden due to being an insteon error
        if r.extra['noprint']:
            r.message = ' (hidden) ' + r.message

    with logbook.Processor(inject_noprint).applicationbound():
        lines = traceback.format_exception(type, value, tb.tb_next)
        for l in lines:
            parts = l.split('\n')
            for p in parts:
                if len(p.strip()) > 0:
                    logger.error(p.rstrip())

sys.excepthook = custom_excepthook

# Don't pollute the namespace
del custom_excepthook 
del sys

# Insteon-related setup

# Now load the msg definitions for the user to use

import insteon.io.xmlmsgreader
definitions = insteon.io.xmlmsgreader.read_default_xml()
# Don't pollute the namespace
del insteon.io.xmlmsgreader

print('........')

# Load the init file (if it exists in the system)
load_config(resolve_resource('init.py'))

print('........')
