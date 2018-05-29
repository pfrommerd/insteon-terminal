class SerialConn:
    FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = 5, 6, 7, 8
    STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = 1, 1.5, 2
    PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'

    def __init__(self, port, baudrate=19200, bytesize=EIGHTBITS, parity=PARITY_NONE,
                    stopbits=STOPBITS_ONE, timeout=0.1,
                    xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False,
                    inter_byte_timeout=None):
        # Find the right serial implementation to use
        import serial
        self._port = serial.Serial(port=port, baudrate=baudrate,
                                    bytesize=bytesize, parity=parity,
                                    stopbits=stopbits, timeout=timeout,
                                    xonxoff=xonxoff, rtscts=rtscts,
                                    write_timeout=write_timeout, dsrdtr=dsrdtr,
                                    inter_byte_timeout=inter_byte_timeout)
    
    def close(self):
        self._port.close()

    def read(self, size=1):
        return self._port.read(size)

    def write(self, data):
        return self._port.write(data)

    def flush(self):
        self._port.flush()
