"""Pure decoding of the provisional canonical 324-byte telemetry profile."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Any

PACKET_SIZE = 324
ACTIVITY_OFFSET = 0
RACE_POSITION_OFFSET = 314


class PacketFormatError(ValueError):
    """Raised when a packet cannot satisfy the exact input contract."""

    def __init__(self, message: str, *, kind: str = "field") -> None:
        super().__init__(message)
        self.kind = kind


@dataclass(frozen=True)
class Telemetry:
    is_race_on: bool
    race_position_324: int


def _u8(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255:
        raise PacketFormatError("race position must be an integer U8")
    return value


def validate_race_position(value: Any) -> int:
    """Validate an adapter-supplied race-position value without coercion."""
    return _u8(value)


def decode_packet(data: bytes) -> Telemetry:
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise PacketFormatError("packet must be bytes", kind="length")
    if len(data) != PACKET_SIZE:
        raise PacketFormatError("packet length must be exactly 324 bytes", kind="length")
    raw = bytes(data)
    try:
        race_flag = struct.unpack_from("<I", raw, ACTIVITY_OFFSET)[0]
        position = raw[RACE_POSITION_OFFSET]
    except (struct.error, IndexError) as exc:
        raise PacketFormatError("packet fields are truncated") from exc
    if race_flag not in (0, 1):
        raise PacketFormatError("activity flag must be canonical 0 or 1")
    return Telemetry(bool(race_flag), _u8(position))
