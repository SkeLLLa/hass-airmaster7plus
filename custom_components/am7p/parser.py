"""AM7P UDP packet parser. Pure, no HA deps."""

from __future__ import annotations

import struct

# Payload begins at byte offset 23; 7 big-endian uint16 measurements follow.
_OFFSET = 23
_FIELDS = 7
_MIN_LEN = _OFFSET + _FIELDS * 2


def parse_packet(data: bytes) -> dict | None:
    """Parse a raw AM7P UDP datagram into a measurement dict, or None if invalid."""
    if len(data) < _MIN_LEN:
        return None
    x = struct.unpack_from(">HHHHHHH", data[_OFFSET:])
    return {
        "pm25": x[0],
        "pm10": x[1],
        "hcho": x[2] / 100,
        "tvoc": x[3] / 100,
        "co2": x[4],
        "temperature": (x[5] - 3500) / 100,
        "humidity": x[6] / 100,
    }
