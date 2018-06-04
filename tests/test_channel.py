import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import insteon.util as util

import threading
import time

def test_channel():
    c = util.Channel()

    def run():
        c.send('foo')
        c.send('bar')

    t = threading.Thread(target=run)
    t.start()

    print(c.recv())
    print(c.recv())

if __name__=="__main__":
    test_channel()
