from collections import namedtuple

CanFrame = namedtuple('CanFrame', ['can_id', 'data', 'dlen'])


class SerialReader:
    """Reads binary CAN frames from UART. Non-blocking."""

    def __init__(self):
        self._ser = None

    def open(self, port: str, baudrate: int = 115200):
        import serial
        self._ser = serial.Serial(port, baudrate, timeout=0.01)

    def close(self):
        if self._ser:
            try:
                self._ser.close()
            except Exception:
                pass
            self._ser = None

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

        padded = bytearray(8)
        padded[:len(data)] = data
        return CanFrame(can_id=can_id, data=bytes(padded), dlen=dlen)
