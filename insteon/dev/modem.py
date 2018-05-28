from .device import Device

from . import linkdb as linkdb

from insteon.msg.msg import MsgDef

from ..util import port_resolver, InsteonError
from .. import util as util

import datetime

import logbook
logger = logbook.Logger(__name__)

class Modem(Device):
    def __init__(self, port, name=None, registry=None):
        self.port = port

        addr = (0x00, 0x00, 0x00)
        # Query for the modem address
        addr_query = port.defs['GetIMInfo'].create()

        reply_channel = util.Channel()
        port.write(addr_query, ack_reply_channel=reply_channel)
        if reply_channel.wait(5): # Wait for a reply
            msg = reply_channel.recv()
            addr = msg['IMAddress']

        super().__init__(name, addr, self, registry)


    # Override the update linkdb function
    @port_resolver('port')
    def update_dbcache(self, targetdb=None, port=None):
        reply_channel = util.Channel()
        done_channel = util.Channel(lambda x: (x['type'] == 'GetFirstALLLinkRecordReply' or \
                                              x['type'] == 'GetNextALLLinkRecordReply') and \
                                              x['ACK/NACK'] == 0x15)
        record_channel = util.Channel(lambda x: x['type'] == 'ALLLinkRecordResponse')


        # Now send the first message
        port.write(port.defs['GetFirstALLLinkRecord'].create(), ack_reply_channel=reply_channel,
                        custom_channels=[done_channel, record_channel])

        try:
            raise InsteonError('Test error!')
        except Exception as e:
            raise InsteonError('foo')

        records = []

        offset = 0x00 # Count manually
        while reply_channel.recv(5): # Wait at most 5 seconds for some reply
            if done_channel.has_activated: # If the reply says we are done, exit
                break
            # Wait another 2 seconds for the record
            msg = record_channel.recv(2)
            if not msg:
                logger.warning('No link data received after ack for modem DB query')
                raise InsteonError('No link data after ack for modem DB query')

            # Turn the msg into a record
            rec = {}
            rec['offset'] = offset
            rec['address'] = msg['LinkAddr']
            rec['flags'] = msg['RecordFlags']
            rec['group'] = msg['ALLLinkGroup']
            rec['data'] = [msg['LinkData1'], msg['LinkData2'], msg['LinkData3']]
            records.append(rec)

            # Increment the offset
            offset = offset + 0x08

            # Request the next one
            port.write(port.defs['GetNextALLLinkRecord'].create(),
                        ack_reply_channel=reply_channel)
        else:
            logger.warning('No reply for modem DB query, stopping query...')
            raise OSError('Did not get reply for modem DB query')

        port.unregister_on_read(done_channel)
        port.unregister_on_read(record_channel)

        # If we were successful, update
        if not targetdb:
            targetdb = self.dbcache

        targetdb.update(records)


    @port_resolver('port')
    def flash_dbcache(self, srcdb=None, port=None):
        backfile_name = '{}_{}.linkdb.bk'.format(self.name, datetime.datetime.now().strftime('%b_%d_%Y_%H:%M:%S'))
        print('WARNING: This can nuke your modem database if not done properly!')
        print('This method will save a backup copy of your database to {}'.format(backfile_name))

        if not srcdb:
            srcdb = self.dbcache

        if not srcdb.is_populated:
            # Just to make sure people aren't doing
            # anything too stupid
            raise ValueError('Source database for flashing has not been populated')

        currentdb = linkdb.LinkDB()

        if not self.update_dbcache(targetdb=currentdb, port=port) is True:
            raise ValueError('Failed to get snapshot of current db before re-flashing')
            

        # Save the old db
        currentdb.save(backfile_name)

        current_records = list(linkdb.offsets_stripped(currentdb.records))
        src_records = list(linkdb.offsets_stripped(srcdb.records))

        # Now go through everything in the currentdb 
        # records that is not in the cachedb
        # and delete
        for record in current_records:
            if not record in src_records:
                logger.info('Deleting link record {}'.format(record))
                msg = port.defs['ManageALLLinkRecord'].create()
                msg['controlCode'] = 0x80 # Delete by search
                msg['recordFlags'] = record['flags']
                msg['ALLLinkGroup'] = record['group']
                msg['linkAddress'] = record['address']
                msg['linkData1'] = record['data'][0]
                msg['linkData2'] = record['data'][1]
                msg['linkData2'] = record['data'][2]

                # Send the delete message and wait for a response
                ack_reply = util.Channel()
                port.write(msg, ack_reply_channel=ack_reply)
                reply_msg = ack_reply.recv(2)
                if reply_msg['ACK/NACK'] != 0x06:
                    logger.warning('The modem couldn\'t find the record we wanted to delete!')
                    raise OSError('The modem couldn\'t find the record we wanted to delete!')
                elif not reply_msg:
                    logger.warning('No reply to delete message!')
                    raise OSError('No reply to delete message')

        # Update the current records
        with util.raise_warnings():
            try:
                self.update_dbcache(targetdb-currentdb, port=port)
            except RuntimeWarning:
                warn('Failed to get snapshot of db after removal!', RuntimeWarning)

        current_records = list(linkdb.offsets_stripped(currentdb.records))

        # Now go and ad any we need
        for record in src_records:
            if not record in current_records:
                logger.info('Adding link record {}'.format(record))
                msg = port.defs['ManageALLLinkRecord'].create()
                # Add resp. or controller
                msg['controlCode'] = 0x40 if (record['flags'] & (1 << 6)) else 0x41
                msg['recordFlags'] = record['flags']
                msg['ALLLinkGroup'] = record['group']
                msg['linkAddress'] = record['address']
                msg['linkData1'] = record['data'][0]
                msg['linkData2'] = record['data'][1]
                msg['linkData3'] = record['data'][2]

                ack_reply = util.Channel()
                port.write(msg, ack_reply_channel=ack_reply)
                if not ack_reply.wait(2):
                    logger.warning('No reply on record add!')
                    return False
