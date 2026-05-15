from collections import namedtuple

CanFrame = namedtuple('CanFrame', ['can_id', 'data', 'dlen'])


class SerialReader:
    """Reads binary CAN frames from UART. Non-blocking."""

    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self._ser = None

    def open(self):
        import serial
        self._ser = serial.Serial(self.port, self.baudrate, timeout=0.01)

    def close(self):
        if self._ser:
            self._ser.close()

    def read_frame(self):
        """Read one CAN frame. Returns CanFrame or None if no data."""
        if self._ser is None:
            return None
        header = self._ser.read(3)
        if len(header) < 3:
            return None

        can_id = (header[0] << 8) | header[1]
        dlen = header[2] & 0x0F
        if dlen > 8:
            dlen = 8

        data = self._ser.read(dlen)
        if len(data) < dlen:
            return None

        # Pad to 8 bytes
        padded = bytearray(8)
        padded[:len(data)] = data
        return CanFrame(can_id=can_id, data=bytes(padded), dlen=dlen)
