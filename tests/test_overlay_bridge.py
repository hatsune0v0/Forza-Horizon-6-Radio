from fh6_radio_clean_v02 import MediaSnapshot, OverlayBridge, PlaybackStatus, SnapshotDelivery


def test_generation_invalidates_late_snapshot_and_close_is_idempotent():
    shown = []
    bridge = OverlayBridge(on_status=shown.append)
    generation = bridge.start()
    assert bridge.deliver(SnapshotDelivery(generation, MediaSnapshot("Spotify.exe", "s", "One", "Artist", playback_status=PlaybackStatus.PLAYING)))
    bridge.stop()
    assert not bridge.deliver(SnapshotDelivery(generation, None))
    bridge.close()
    bridge.close()
    assert bridge.closed
