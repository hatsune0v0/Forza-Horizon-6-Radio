import struct

import pytest

from fh6_radio_clean_v02.parser import (
    PACKET_SIZE,
    RACE_POSITION_OFFSET,
    PacketFormatError,
    decode_packet,
    validate_race_position,
)


def packet(*, race_on=1, position=0):
    data = bytearray(PACKET_SIZE)
    struct.pack_into("<I", data, 0, race_on)
    data[304:316] = b"junk-at-304!"
    data[RACE_POSITION_OFFSET] = position
    return bytes(data)


def test_decodes_exact_packet_fields_at_declared_offsets():
    parsed = decode_packet(packet(race_on=1, position=0))

    assert parsed.is_race_on is True
    assert parsed.race_position_324 == 0
    assert decode_packet(packet(position=7)).race_position_324 == 7


def test_ignores_unrelated_bytes_at_304_308_and_312():
    data = bytearray(packet(position=9))
    data[304:316] = bytes.fromhex("ff ff ff ff 00 00 80 7f 00 00 80 ff")
    data[RACE_POSITION_OFFSET] = 9
    parsed = decode_packet(data)
    assert parsed.is_race_on is True
    assert parsed.race_position_324 == 9


@pytest.mark.parametrize("size", [0, 323, 325])
def test_rejects_any_packet_that_is_not_exactly_324_bytes(size):
    with pytest.raises(PacketFormatError):
        decode_packet(bytes(size))


@pytest.mark.parametrize("value", [True, -1, 256, 1.5, "7", None])
def test_rejects_non_u8_race_position_values(value):
    with pytest.raises(PacketFormatError):
        validate_race_position(value)


@pytest.mark.parametrize("value", [0, 1, 255])
def test_accepts_all_u8_race_position_boundaries(value):
    assert validate_race_position(value) == value
