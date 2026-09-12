import struct

from fh6_radio_clean_v02.core import StateMachine


def packet(position=0):
    data = bytearray(324)
    struct.pack_into("<I", data, 0, 1)
    data[314] = position
    return bytes(data)


def test_same_state_and_target_do_not_repeat_effect():
    machine = StateMachine()
    first = machine.ingest(packet(), now=0.0, fh6_running=True)
    second = machine.ingest(packet(), now=0.1, fh6_running=True)

    assert first.effect is not None
    assert second.effect is None


def test_stop_effect_always_declares_safe_zero_volume():
    machine = StateMachine()
    publication = machine.tick(now=0.0, fh6_running=False)

    assert publication.effect.target_volume == 0.0
    assert publication.effect.playback_intent == "STOP"


def test_no_change_publications_do_not_replay_previous_effect():
    machine = StateMachine()
    machine.ingest(packet(), now=0.0, fh6_running=True)
    stale = machine.tick(now=2.0, fh6_running=True)
    again = machine.ingest(b"bad", now=2.1, fh6_running=True)
    assert stale.effect is not None
    assert again.effect is None


def test_current_volume_stays_unknown_until_observed():
    machine = StateMachine()
    publication = machine.ingest(packet(), now=0.0, fh6_running=True)
    assert publication.current_volume is None
    observed = machine.observe_volume(0.42)
    assert observed.current_volume == 0.42
