from . import linkdb

class DBManager:
    def __init__(self, dev, record_formatter):
        self.cache = linkdb.LinkDB(formatter=record_formatter)
        self._dev = dev

    # Will update/return the target db,
    # create a new database if None
    def update_cache(self, targetdb=None, port=None):
        port = port if port else self._dev.primary_port

        if not targetdb:
            targetdb = self.cache

        # _retrieve() returns a LinkDB() object
        records = self._retrieve(port)
        targetdb.update(records)

        return targetdb

    def flash_cache(self, srcdb=None, port=None):
        port = port if port else self._dev.primary_port

        if not srcdb:
            srcdb = self.cache

        if not srcdb.valid:
            logger.error('The source database provided is not valid in that it has not have \
                            a timestamp and so is not considered "populated" to prevent accidentally \
                            wipping the database')
            raise ValueError('Source database for flashing has not been set as populated (updated)')

        currentdb = linkdb.LinkDB()
        # Make a backup ....
        # Retrieve the current DB into a "currentdb" variable
        self.update_cache(targetdb=currentdb, port=port)

        # Save the currentdb
        backfile_name = '{}.linkdb.bk'.format(datetime.datetime.now().strftime('%b_%d_%Y_%H:%M:%S'))

        logger.warning('Modifying Link Database. This can go catastrophically wrong. A backup of the current database has been written to {}', backfile_name)
        currentdb.save(backfile_name)

        self._write(port, srcdb, currentdb)

    # The actual implementation
    # that returns a database
    # retrieved
    def _retrieve(self, port):
        pass

    # The actual implementation that writes
    # a database given a current database and
    # a source database to write
    def _write(self, port, srcdb, currentdb):
        pass


#
# -----------------------------------------------------------------
# -------- Now specific database managers--------------------------
# -----------------------------------------------------------------
#

class ModemDBManager(DBManager):
    def __init__(self, dev):
        super().__init__(dev, linkdb.DefaultRecordFormatter())

    def _retrieve(self, port):
        reply_channel = Channel()
        done_channel = Channel(lambda x: (x['type'] == 'GetFirstALLLinkRecordReply' or \
                                              x['type'] == 'GetNextALLLinkRecordReply') and \
                                              x['ACK/NACK'] == 0x15)
        record_channel = Channel(lambda x: x['type'] == 'ALLLinkRecordResponse')


        # Now send the first message
        port.write(port.defs['GetFirstALLLinkRecord'].create(), ack_reply_channel=reply_channel,
                        custom_channels=[done_channel, record_channel])
        # Custom channels will be removed on garbage collect due to
        # weak references

        records = []

        offset = 0x00 # Count manually
        while reply_channel.recv(5): # Wait at most 5 seconds for some reply
            if done_channel.has_activated: # If the reply says we are done, exit
                break
            # Wait another 2 seconds for the record
            msg = record_channel.recv(2)
            if not msg:
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
            raise InsteonError('Did not get reply for modem DB query')
        
        db = linkdb.LinkDB()
        db.update(records)

        return db

    def _write(self, port, srcdb, currentdb):
        for record in currentdb:
            filter_rec = dict(record)
            del filter_rec['offset']
            # If we do not find this record (regardless of offset) in the source
            # database, delete it!
            if not srcdb.filter_records(filter_rec).empty:
                logger.debug('Deleting record {}', srcdb.formatter(record))

                msg = port.defs['ManageALLLinkRecord'].create()
                msg['controlCode'] = 0x80 # Delete by search
                msg['recordFlags'] = record['flags']
                msg['ALLLinkGroup'] = record['group']
                msg['linkAddress'] = record['address']
                msg['linkData1'] = record['data'][0]
                msg['linkData2'] = record['data'][1]
                msg['linkData2'] = record['data'][2]

                # Send the delete message and wait for a response
                ack_reply = Channel()
                port.write(msg, ack_reply_channel=ack_reply)
                reply_msg = ack_reply.recv(2)
                if reply_msg['ACK/NACK'] != 0x06:
                    raise InsteonError('The modem couldn\'t find the record we wanted to delete!')
                elif not reply_msg:
                    raise InsteonError('No reply to delete message')

        try:
            currentdb = linkdb.LinkDB()
            self.update_cache(targetdb=currentdb, port=port)
        except InsteonError as e:
            raise InsteonError('Unable to get database after removing records!') from e

        for record in srcdb:
            filter_rec = dict(record)
            del filter_rec['offset']
            if not srcdb.filter_records(filter_rec).empty:
                logger.debug('Adding record {}', srcdb.formatter(record))

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
                    raise InsteonError('No reply on record add!')
