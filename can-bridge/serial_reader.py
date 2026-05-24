from collections import namedtuple

CanFrame = namedtuple('CanFrame', ['can_id', 'data', 'dlen'])

_SYNC_BYTE = 0xAA


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
        """Read one CAN frame. Returns CanFrame or None if no data.

        Scans for the 0xAA sync byte before parsing so ASCII noise or a
        mid-frame start never permanently corrupts alignment.
        """
        if self._ser is None:
            return None

        # Scan for sync byte — discards any stray bytes (e.g. ASCII startup prints).
        while True:
            b = self._ser.read(1)
            if not b:
                return None
            if b[0] == _SYNC_BYTE:
                break

        header = self._ser.read(3)  # id_hi, id_lo, dlen
        if len(header) < 3:
            return None

        can_id = (header[0] << 8) | header[1]
        if can_id > 0x7FF:
            return None  # not a valid 11-bit standard CAN ID

        dlen = header[2] & 0x0F
        if dlen > 8:
            dlen = 8

        data = self._ser.read(dlen)
        if len(data) < dlen:
            return None

        padded = bytearray(8)
        padded[:len(data)] = data
        return CanFrame(can_id=can_id, data=bytes(padded), dlen=dlen)
