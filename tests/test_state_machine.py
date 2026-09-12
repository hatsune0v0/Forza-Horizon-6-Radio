import struct

from fh6_radio_clean_v02.core import (
    STALE_AFTER_SECONDS,
    Scene,
    StateMachine,
)


def packet(*, race_on=1, position=0):
    data = bytearray(324)
    struct.pack_into("<I", data, 0, race_on)
    data[304:316] = b"ignored-12!!"
    data[314] = position
    return bytes(data)


def test_three_consecutive_nonzero_positions_enter_race():
    machine = StateMachine()
    assert machine.ingest(packet(position=1), now=0.0, fh6_running=True).current_scene is Scene.PLAYING
    assert machine.ingest(packet(position=2), now=0.1, fh6_running=True).current_scene is Scene.PLAYING
    publication = machine.ingest(packet(position=3), now=0.2, fh6_running=True)

    assert publication.current_scene is Scene.RACE
    assert publication.target_volume == 0.80


def test_zero_position_before_race_is_normal_playing():
    publication = StateMachine().ingest(packet(position=0), now=0.0, fh6_running=True)

    assert publication.current_scene is Scene.PLAYING
    assert publication.target_volume == 1.0


def test_three_zero_positions_after_race_leave_to_transition():
    machine = StateMachine()
    for index in range(3):
        machine.ingest(packet(position=index + 1), now=index * 0.1, fh6_running=True)

    for index in range(2):
        assert machine.ingest(packet(position=0), now=1 + index * 0.1, fh6_running=True).current_scene is Scene.RACE
    publication = machine.ingest(packet(position=0), now=1.3, fh6_running=True)

    assert publication.current_scene is Scene.TRANSITION
    assert publication.target_volume == 0.15


def test_race_off_is_immediately_paused():
    machine = StateMachine()
    for index in range(3):
        machine.ingest(packet(position=1), now=index * 0.1, fh6_running=True)

    publication = machine.ingest(packet(race_on=0, position=8), now=1.0, fh6_running=True)
    assert publication.current_scene is Scene.PAUSED
    assert publication.target_volume == 0.0


def test_stale_running_process_is_transition_and_stopped_process_is_zero():
    machine = StateMachine()
    machine.ingest(packet(position=0), now=10.0, fh6_running=True)
    stale = machine.tick(now=10.0 + STALE_AFTER_SECONDS + 0.01, fh6_running=True)
    assert stale.connection_status == "STALE"
    assert stale.current_scene is Scene.TRANSITION
    assert stale.target_volume == 0.15

    stopped = machine.tick(now=20.0, fh6_running=False)
    assert stopped.current_scene is Scene.STOPPED
    assert stopped.target_volume == 0.0


def test_invalid_length_does_not_change_published_state():
    machine = StateMachine()
    first = machine.ingest(packet(position=0), now=0.0, fh6_running=True)
    second = machine.ingest(b"bad", now=0.1, fh6_running=True)
    assert second.connection_status == first.connection_status
    assert second.current_scene == first.current_scene
    assert second.target_volume == first.target_volume
    assert second.effect is None


def test_invalid_length_breaks_consecutive_entry_evidence():
    machine = StateMachine()
    machine.ingest(packet(position=1), now=0.0, fh6_running=True)
    machine.ingest(packet(position=2), now=0.1, fh6_running=True)
    machine.ingest(b"bad", now=0.2, fh6_running=True)

    publication = machine.ingest(packet(position=3), now=0.3, fh6_running=True)
    assert publication.current_scene is Scene.PLAYING


def test_invalid_valid_length_clears_race_confirmation_and_requires_reentry():
    machine = StateMachine()
    for index in range(3):
        machine.ingest(packet(position=1), now=index * 0.1, fh6_running=True)
    malformed = bytearray(324)
    struct.pack_into("<I", malformed, 0, 2)
    machine.ingest(bytes(malformed), now=1.0, fh6_running=True)

    publication = machine.ingest(packet(position=1), now=1.1, fh6_running=True)
    assert publication.current_scene is Scene.PLAYING


def test_priority_process_exit_beats_pause_and_race():
    machine = StateMachine()
    publication = machine.ingest(packet(race_on=0, position=0), now=0.0, fh6_running=False)
    assert publication.current_scene is Scene.STOPPED
    assert publication.target_volume == 0.0


def test_gap_before_packet_clears_evidence_and_requires_three_fresh_samples():
    machine = StateMachine()
    machine.ingest(packet(position=1), now=0.0, fh6_running=True)
    machine.ingest(packet(position=2), now=0.1, fh6_running=True)
    assert machine.ingest(packet(position=3), now=2.0, fh6_running=True).current_scene is Scene.PLAYING
    assert machine.ingest(packet(position=4), now=2.1, fh6_running=True).current_scene is Scene.PLAYING
    assert machine.ingest(packet(position=5), now=2.2, fh6_running=True).current_scene is Scene.RACE


def test_rejects_nonfinite_or_backwards_time_without_mutating_state():
    machine = StateMachine()
    first = machine.ingest(packet(), now=1.0, fh6_running=True)
    import pytest
    for bad in (float("nan"), float("inf"), -float("inf"), 0.5):
        with pytest.raises((TypeError, ValueError)):
            machine.ingest(packet(position=1), now=bad, fh6_running=True)
    assert machine._publication == first


def test_rejects_invalid_stale_timeout_configuration():
    import pytest
    for value in (0, -1, float("nan"), float("inf"), True):
        with pytest.raises((TypeError, ValueError)):
            StateMachine(stale_after=value)


def test_stop_without_timestamp_is_safe_after_clock_advanced():
    machine = StateMachine()
    machine.ingest(packet(position=0), now=12.0, fh6_running=True)

    publication = machine.stop()

    assert publication.current_scene is Scene.STOPPED
    assert publication.target_volume == 0.0
