"""Unit tests for the AM7P packet parser."""

import struct

from custom_components.am7p.parser import parse_packet


def _build_packet(pm25, pm10, hcho_raw, tvoc_raw, co2, temp_raw, hum_raw) -> bytes:
    """Build a synthetic AM7P datagram: 23 header bytes + 7 big-endian uint16."""
    header = b"\x00" * 23
    body = struct.pack(
        ">HHHHHHH", pm25, pm10, hcho_raw, tvoc_raw, co2, temp_raw, hum_raw
    )
    return header + body


def test_parse_valid_packet():
    data = _build_packet(12, 20, 5, 30, 600, 3500 + 2150, 4500)
    result = parse_packet(data)
    assert result == {
        "pm25": 12,
        "pm10": 20,
        "hcho": 0.05,
        "tvoc": 0.30,
        "co2": 600,
        "temperature": 21.5,
        "humidity": 45.0,
    }


def test_parse_too_short_returns_none():
    assert parse_packet(b"\x00" * 36) is None


def test_parse_exact_minimum_length():
    data = _build_packet(0, 0, 0, 0, 0, 3500, 0)
    result = parse_packet(data)
    assert result is not None
    assert result["temperature"] == 0.0


def test_parse_negative_temperature():
    data = _build_packet(0, 0, 0, 0, 0, 3500 - 500, 0)
    result = parse_packet(data)
    assert result["temperature"] == -5.0
