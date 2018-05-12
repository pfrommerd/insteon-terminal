import threading

class Event(threading.Event):
    def __init__(self):
        super().__init__()
