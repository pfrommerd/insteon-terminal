import threading
import traceback
import queue
import copy

import time

from . import msg as message

# Takes a connection object that has read(), write(), flush(), and close() methods
class Port:
    def __init__(self, conn=None, definitions={}):
        self._definitions = definitions

        self._ack_reply_waiters_lock = threading.RLock()
        self._ack_reply_waiters = {} # A map of message type to waiter events (usually for replies)

        # A queue containing tuples of (priority, msg, write_event, reply_event)
        self._write_queue = queue.PriorityQueue()

        # The current written message for re-enqueuing by the reader thread
        self._written_message = None
        self._written_message_lock = threading.RLock()

        self._conn = None
        self._reader = None
        self._writer = None

        self._read_listeners = []
        self._read_listeners_lock = threading.RLock()

        self._write_listeners = []
        self._write_listeners_lock = threading.RLock()

        if conn:
            self.attach(conn)


    def attach(self, conn):
        if self._conn:
            self.detach()

        # Start threads
        self._conn = conn
        self._reader = threading.Thread(target=self._read_thread)
        self._writer = threading.Thread(target=self._write_thread)

        self._reader.start()
        self._writer.start()

    def detach(self):
        if self._reader:
            r = self._reader
            self._reader = None
            r.join()
        if self._writer:
            w = self._writer
            self._writer = None
            w.join()
        self._conn = None

    def add_read_listener(self, handler):
        with self._read_listeners_lock:
            self._read_listeners.append(handler)

    def remove_read_listener(self, handler):
        with self._read_listeners_lock:
            self._read_listeners.remove(handler)

    def add_write_listener(self, handler):
        with self._write_listeners_lock:
            self._write_listeners.append(handler)

    def remove_write_listener(self, handler):
        with self._write_listeners_lock:
            self._write_listeners.remove(handler)

    def write(self, msg, priority=0, write_event=None, ack_reply_event=None, any_reply_event=None):
        self._write_queue.put( (priority, msg, write_event, ack_reply_event, any_reply_event) )

    def _read_thread(self):
        decoder = message.MsgStreamDecoder(self._definitions)
        while self._reader:
            try:
                buf = self._conn.read(1024) # Read as much as possible
                if len(buf) < 1:
                    continue
                # TODO: Logging of raw data!
                #print(buf)

                # Feed into decoder
                msg = decoder.decode(buf)
                if not msg:
                    continue
            except Exception as e:
                print('Error reading!')
                print(traceback.format_exc())

            # Only notify the reply waiters if this isn't a pure nack
            # if it is a pure nack we need to request a resend and
            # the reply waiters will be notified when the real message comes in
            if msg['type'] == 'PureNACK':
                # TODO: What if nack is processed for previous message
                # just after new message is queued to be written?
                with self._written_message_lock:
                    m = copy.deepcopy(self._written_message[1]) # Deep copy of message dict
                    m['pre_quiet_time'] = 0.1 # Wait 100ms before resending
                    self.write(m, priority=-1, ack_reply_event=self._written_message[2])

                    # Notify the any_reply waiters so the
                    # write thread does the resend

                    # Hack in the msg to the any_reply event
                    self._written_message[4].msg = msg
                    self._written_message[4].set()
            else:
                # Notify the any_reply waiters, so that the
                # write thread can move on to the next message
                with self._written_message_lock:
                    # Hack in the message to the any_reply event
                    self._written_message[4].msg = msg
                    self._written_message[4].set()

                # Notify anyone waiting on the ack reply waiters
                with self._ack_reply_waiters_lock:
                    if msg['type'] in self._ack_reply_waiters:
                        # Hack in the message to the ack_reply event
                        self._ack_reply_waiters[msg['type']].msg = msg
                        self._ack_reply_waiters[msg['type']].set()
            
            # Notify listeners
            listeners = []
            with self._read_listeners_lock:
                listeners = list(self._read_listeners)

            for l in listeners:
                l(msg)

    def _write_thread(self):
        encoder = message.MsgStreamEncoder(self._definitions)
        while self._writer:
            try:
                queue_item = self._write_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # Now we save the queue item as the next-written-one in case the read thread
            # needs to queue a resend on a pure-nack
            with self._written_message_lock:

                msg = queue_item[1]
                write_event = queue_item[2]
                # Put the reply event into the map
                # TODO: Reply type should be a passable parameter (if None no reply is expected)
                ack_reply_type = msg['type'] + 'Reply'
                if ack_reply_type in self._definitions and queue_item[3]:
                    ack_reply_event = queue_item[3]
                    with self._ack_reply_waiters_lock:
                        self._ack_reply_waiters[ack_reply_type] = ack_reply_event

                any_reply_event = queue_item[4] if queue_item[4] else threading.Event()
                queue_item = (queue_item[0], queue_item[1],
                                queue_item[2], queue_item[3],
                                any_reply_event) # We need this definitely to be called by the reader

                # Update to account for any_reply_event
                self._written_message = queue_item

                # Wait the pre-write quiet time we want
                if 'pre_quiet_time' in msg:
                    time.sleep(msg['pre_quiet_time'])

                # Now we do the actual writing
                try: 
                    data = encoder.encode(msg)
                    self._conn.write(data)
                    self._conn.flush()
                except Exception as e:
                    # TODO: Make logging
                    print('Error writing message!')
                    print(traceback.format_exc())

                # Trigger the write event
                if write_event:
                    # Hack in the message into
                    # the write event
                    write_event.msg = msg
                    write_event.set()

                # Notify the listeners of the write
                listeners = []
                with self._write_listeners_lock:
                    listeners = list(self._write_listeners)

                for l in listeners:
                    l(msg)

            # Wait for some reply for at least 1 second
            # before moving on
            any_reply_event.wait(1)

            # Wait the quiet time we want
            if 'post_quiet_time' in msg:
                time.sleep(msg['post_quiet_time'])

