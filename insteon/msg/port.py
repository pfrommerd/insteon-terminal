import threading
import traceback
import queue
import copy

import time

from . import msg as message
from .. import util as util

class WriteRequest:
    def __init__(self, msg, priority=1, prewrite_quiet_time=0, postwrite_quiet_time=0,
            write_channel=None, first_reply_channel=None,
            ack_reply_channel=None, custom_channels=[]):
        self.msg = msg
        self.priority = priority

        self.prewrite_quiet_time = prewrite_quiet_time
        self.postwrite_quiet_time = postwrite_quiet_time

        self.write_channel = write_channel 

        self.first_reply_channel = first_reply_channel

        ack_msg_name = msg['type'] + 'Reply'
        # We must have this channel to know if we have received an ack!
        self.ack_reply_channel = ack_reply_channel if ack_reply_channel else \
                util.Channel(lambda x: x['type'] == ack_msg_name, 1)

        if not self.ack_reply_channel.has_filter or self.ack_reply_channel.has_activated:
            # No filter or if we are reusing a channel
            self.ack_reply_channel.reset_num_sent()
            self.ack_reply_channel.set_filter(lambda x: x['type'] == ack_msg_name)

        self.custom_channels = custom_channels # Will be added with write() call

    def __gt__(self, other):
        return self.priority > other.priority
    def __lt__(self, other):
        return self.priority < other.priority
    def __ge__(self, other):
        return self.priority >= other.priority
    def __le__(self, other):
        return self.priority <= other.priority
    def __eq__(self, other):
        return self.priority == other.priority
    def __nq__(self, other):
        return self.priority != other.priority

# Takes a connection object that has read(), write(), flush(), and close() methods
class Port:
    def __init__(self, conn=None, definitions={}):
        self.defs = definitions

        # Connection and threads
        self._conn = None
        self._reader = None
        self._writer = None

        # A queue containing write requests
        self._write_queue = queue.PriorityQueue()

        # Setup the listeners
        self._read_listeners = []
        self._read_listeners_lock = threading.RLock()

        self._write_listeners = []
        self._write_listeners_lock = threading.RLock()

        def format_msg(m):
            return self.defs[m['type']].format_msg(m)

        # Setup the watchers, for optional use by the user
        # to print out to stdout the traffic through the port
        self._read_watcher = lambda x: print('{}'.format(format_msg(x)))
        self._write_watcher = lambda x: print('{}'.format(format_msg(x)))

        if conn:
            self.attach(conn)

    def __del__(self):
        self.detach()

    def attach(self, conn):
        if self._conn:
            self.detach()

        # Start threads
        self._conn = conn
        self._reader = threading.Thread(target=self._read_thread)
        self._reader.override_kill = False
        self._writer = threading.Thread(target=self._write_thread)
        self._writer.override_kill = False

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


    def notify_on_read(self, handler):
        if not handler:
            return
        with self._read_listeners_lock:
            self._read_listeners.append(handler)

    def unregister_on_read(self, handler):
        if not handler:
            return
        with self._read_listeners_lock:
            self._read_listeners.remove(handler)

    def notify_on_write(self, handler):
        if not handler:
            return
        with self._write_listeners_lock:
            self._write_listeners.append(handler)

    def unregister_on_write(self, handler):
        if not handler:
            return
        with self._write_listeners_lock:
            self._write_listeners.remove(handler)

    # Utility debug functions.....

    def start_watching(self):
        self.notify_on_read(self._read_watcher)
        self.notify_on_write(self._write_watcher)
    
    def stop_watching(self):
        self.unregister_on_read(self._read_watcher)
        self.unregister_on_write(self._write_watcher)

    # Now the actual IO logic

    def write(self, msg, priority=1, prewrite_quiet_time=0, postwrite_quiet_time = 0,
            write_channel=None, first_reply_channel=None,
            ack_reply_channel=None, custom_channels={}):

        self.write_request( WriteRequest(msg, priority,
            prewrite_quiet_time, postwrite_quiet_time,
            write_channel, first_reply_channel,
            ack_reply_channel, custom_channels) )

    def write_request(self, request):
        self._write_queue.put(request)

    def _read_thread(self):
        decoder = message.MsgStreamDecoder(self.defs)
        buf = bytes()
        while self._reader and not threading.current_thread().override_kill:
            try:
                #if len(buf) > 0:
                #    print('reading...')

                buf = self._conn.read(1) # Read a byte
                #if len(buf) < 1:
                #    continue

                # TODO: Logging of raw data!
                #print('read {}'.format(buf))

                # Feed into decoder
                msg = decoder.decode(buf)
                if not msg:
                    continue
            except TypeError as te: # Gets thrown on close() called during read() sometimes
                continue
            except Exception as e:
                print('Error reading!')
                print(traceback.format_exc())
                continue
            
            # Notify listeners
            with self._read_listeners_lock:
                listeners = list(self._read_listeners)
                for l in listeners:
                    l(msg)

    def _write_thread(self):
        encoder = message.MsgStreamEncoder(self.defs)
        while self._writer and not threading.current_thread().override_kill:
            try:
                request = self._write_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            # Wait the pre-write quiet time we want
            # during this time all is quiet (no reading either!)
            if request.prewrite_quiet_time > 0:
                time.sleep(request.prewrite_quiet_time)

            msg = request.msg

            # Writer channels:
            write_channel = request.write_channel

            # Reader channels:
            first_reply_channel = request.first_reply_channel
            ack_reply_channel = request.ack_reply_channel

            any_reply_channel = util.Channel() # For writer control
            nack_reply_channel = util.Channel() # For writer control

            # Setup the filters...
            if first_reply_channel:
                first_reply_channel.set_filter(lambda msg: True) # Let everything in

            # Our channels
            any_reply_channel.set_filter(lambda msg: True) # Let everything in
            nack_reply_channel.set_filter(lambda msg: msg['type'] == 'PureNACK')

            # Including the write channel
            if write_channel:
                write_channel.set_queuesize(1)
                write_channel.set_filter(lambda msg: True)

            # Get the listener lock so we don't miss anything
            # while we write
            with self._read_listeners_lock:
                # Add the channels
                self.notify_on_read(any_reply_channel)
                self.notify_on_read(nack_reply_channel)

                self.notify_on_read(first_reply_channel)
                self.notify_on_read(ack_reply_channel)


                self.notify_on_write(write_channel)

                # Will be removed by hand by the person who
                # queued the write...
                for channel in request.custom_channels:
                    self.notify_on_read(channel)

                for i in range(5): # Maximum of 5 resends...

                    # Now we do the actual writing
                    try: 
                        data = encoder.encode(msg)
                        self._conn.write(data)
                        self._conn.flush()
                    except Exception as e:
                        # TODO: Make logging
                        print('Error writing message!')
                        print(traceback.format_exc())
                        break # Move on to the next message

                    # Notify the listeners of the write
                    with self._write_listeners_lock:
                        listeners = list(self._write_listeners)
                        for l in listeners:
                            l(msg)

                    # Remove the write channel the first time we write
                    if i == 0:
                        self.unregister_on_write(write_channel)

                    # Now we see what comes back by disabling the listener lock
                    self._read_listeners_lock.release()

                    resend = False
                    for mi in range(6): # Look at the next 6 messages or 0.6 second, max
                        if any_reply_channel.wait(0.1): # Wait 100ms for something to arrive
                            # Check if what came was an ack or nack
                            if ack_reply_channel.has_activated:
                                # Woo, we are done, no resend
                                break
                            elif nack_reply_channel.has_activated:
                                # Resend on a nack
                                any_reply_channel.clear()
                                nack_reply_channel.clear()
                                resend = True
                                break
                            else:
                                # Other message type...wait again
                                any_reply_channel.clear()

                    if not ack_reply_channel.has_activated and not resend:
                        # Resend due to no ack!
                        any_reply_channel.clear()
                        nack_reply_channel.clear()
                        resend = True

                    # Re-acquire so the with block doesn't get confused
                    self._read_listeners_lock.acquire() 

                    if not resend:
                        break

                # Remove the listeners
                self.unregister_on_read(first_reply_channel)
                self.unregister_on_read(ack_reply_channel)
                self.unregister_on_read(any_reply_channel)
                self.unregister_on_read(nack_reply_channel)

                # In case this hasn't happened
                self.unregister_on_write(write_channel)
            # Now outside of the lock,
            # post-write quiet time
            if request.postwrite_quiet_time > 0:
                time.sleep(request.postwrite_quiet_time)
