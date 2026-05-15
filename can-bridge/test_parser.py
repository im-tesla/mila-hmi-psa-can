"""Tests for CAN parser and signal definitions."""

from can_parser import parse_frame, extract_bits


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
