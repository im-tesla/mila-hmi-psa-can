"""Generic CAN frame parser using signal definitions.

Uses Motorola (big-endian) byte ordering for multi-byte signals.
"""

from can_definitions import CAN_DEFINITIONS


def extract_bits(data: bytes, byte_offset: int, bit_offset: int, bit_length: int) -> int:
    """Extract a bit field from raw CAN data bytes (Motorola / big-endian).

    In Motorola format the byte at the lowest address holds the most
    significant bits.  Successive bytes hold progressively less significant
    bits.
    """
    value = 0
    bits_remaining = bit_length
    current_byte = byte_offset
    current_bit = bit_offset

    while bits_remaining > 0:
        if current_byte >= len(data):
            break

        bits_from_this_byte = min(8 - current_bit, bits_remaining)
        mask = ((1 << bits_from_this_byte) - 1) << current_bit
        chunk = (data[current_byte] & mask) >> current_bit

        # Earlier bytes are *more* significant (Motorola / big-endian).
        value = (value << bits_from_this_byte) | chunk

        bits_remaining -= bits_from_this_byte
        current_bit = 0
        current_byte += 1

    return value


def parse_frame(can_id: int, data: bytes) -> dict:
    """Parse a CAN frame into named signal values.

    Returns a dict keyed by signal name.  Unknown CAN IDs produce
    ``{"_unknown": True}``.
    """
    if can_id not in CAN_DEFINITIONS:
        return {"_unknown": True}

    result: dict = {}
    for sig in CAN_DEFINITIONS[can_id]:
        name, byte_off, bit_off, bit_len, scale, offset, unit, enum_map = sig

        raw = extract_bits(data, byte_off, bit_off, bit_len)
        scaled = raw * scale + offset

        if enum_map is not None and raw in enum_map:
            result[name] = enum_map[raw]
        elif bit_len == 1 and enum_map is None:
            result[name] = bool(raw)
        elif scale == 1 and offset == 0 and isinstance(scaled, float) and scaled == int(scaled):
            result[name] = int(scaled)
        else:
            result[name] = scaled

    return result
