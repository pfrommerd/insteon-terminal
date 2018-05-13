import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import insteon.util as util

import threading
import time

#c = util.Channel(lambda x: x.startswith('foo'))
c = util.Channel()

def run():
    time.sleep(1)
    c.send('foo')
    time.sleep(2)
    c.send('bar')

t = threading.Thread(target=run)
t.start()

print(c.recv())

print(c.wait(1))
print(c.recv())
