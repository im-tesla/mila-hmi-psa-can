"""Tests for CAN parser and signal definitions."""

from can_parser import parse_frame, extract_bits, encode_signal


def test_extract_bits_simple():
    data = bytes([0b11010100])
    assert extract_bits(data, 0, 0, 4) == 0b0100
    assert extract_bits(data, 0, 4, 4) == 0b1101


def test_extract_bits_cross_byte():
    data = bytes([0x03, 0x4A, 0, 0, 0, 0, 0, 0])
    assert extract_bits(data, 0, 0, 16) == 842


def test_parse_0x0B6_rpm_speed():
    data = bytes([0x03, 0x4A, 0x00, 0x3E, 0x01, 0x6E, 0x44, 0x80])
    result = parse_frame(0x0B6, data)
    assert result["rpm"] == 842
    assert result["speed"] == 6.2


def test_parse_0x128_gear():
    # gear_position: byte 6, bits 1-3  -> 0b011 = 3 = "D"
    data = bytes([0, 0, 0, 0, 0, 0, 0b00000110, 0])
    result = parse_frame(0x128, data)
    assert result["gear_position"] == "D"


def test_parse_0x0E8_door_open():
    data = bytes([0b00001000, 0, 0, 0, 0, 0, 0, 0])
    result = parse_frame(0x0E8, data)
    assert result["front_left_door_open"] == "open"


def test_parse_0x1A1_popup():
    data = bytes([0x80, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    result = parse_frame(0x1A1, data)
    assert result["show_popup"] == 0x80
    assert result["popup_message"] == 0x01


def test_parse_unknown_id():
    result = parse_frame(0xFFF, bytes(8))
    assert result["_unknown"] is True


def test_encode_signal_single_bit_set():
    data = bytearray(8)
    encode_signal(data, 7, 0, 1, 1)
    assert data[7] == 0x01
    assert extract_bits(bytes(data), 7, 0, 1) == 1


def test_encode_signal_single_bit_clear():
    data = bytearray([0xFF] * 8)
    encode_signal(data, 7, 0, 1, 0)
    assert data[7] == 0xFE
    assert extract_bits(bytes(data), 7, 0, 1) == 0


def test_encode_signal_preserves_adjacent_bits():
    data = bytearray([0xFF] * 8)
    encode_signal(data, 7, 0, 1, 0)
    for i in range(7):
        assert data[i] == 0xFF
    assert data[7] == 0xFE


def test_encode_signal_multi_byte():
    data = bytearray(8)
    encode_signal(data, 0, 0, 16, 842)
    assert extract_bits(bytes(data), 0, 0, 16) == 842


def test_encode_signal_non_zero_bit_offset():
    data = bytearray(8)
    encode_signal(data, 0, 3, 2, 1)
    assert extract_bits(bytes(data), 0, 3, 2) == 1
    assert data[0] & 0xE7 == 0


def test_encode_signal_roundtrip_enum():
    data = bytearray([0x42, 0x5E, 0x12, 0x34, 0x56, 0x00, 0x12, 0x80])
    encode_signal(data, 7, 0, 1, 1)
    assert extract_bits(bytes(data), 7, 0, 1) == 1
    encode_signal(data, 7, 0, 1, 0)
    assert extract_bits(bytes(data), 7, 0, 1) == 0
