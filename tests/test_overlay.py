from fh6_radio_clean_v02 import MediaSnapshot, OverlayCoordinator, PlaybackStatus, Scene


def snap(title, source="Spotify.exe"):
    return MediaSnapshot(source, "session-1", title, "Artist", playback_status=PlaybackStatus.PLAYING)


def test_first_observation_is_silent_then_new_track_shows_once():
    shown = []
    coordinator = OverlayCoordinator(show=shown.append)
    coordinator.set_lifecycle(service_running=True)
    coordinator.set_focus(True)
    coordinator.set_scene(Scene.PLAYING)
    assert coordinator.consume(snap("One")).reason == "baseline"
    assert shown == []
    assert coordinator.consume(snap("One")).visible is False
    assert coordinator.consume(snap("Two")).visible is True
    assert [item.title for item in shown] == ["Two"]
    coordinator.consume(snap("Two"))
    assert [item.title for item in shown] == ["Two"]


def test_pause_focus_and_invalid_source_hide_without_replaying_old_track():
    shown = []
    coordinator = OverlayCoordinator(show=shown.append)
    coordinator.set_lifecycle(service_running=True)
    coordinator.set_focus(True)
    coordinator.set_scene(Scene.PLAYING)
    coordinator.consume(snap("One"))
    coordinator.set_scene(Scene.PAUSED)
    assert coordinator.status.visible is False
    coordinator.consume(snap("Two", "Chrome.exe"))
    coordinator.consume(snap("Two"))
    coordinator.set_scene(Scene.PLAYING)
    coordinator.consume(snap("Two"))
    assert shown == []


def test_cover_limit_and_invalid_metadata_are_safe():
    coordinator = OverlayCoordinator()
    coordinator.set_lifecycle(service_running=True)
    coordinator.set_focus(True)
    coordinator.set_scene(Scene.PLAYING)
    huge = MediaSnapshot("Spotify.exe", "session-1", "One", "Artist", cover_bytes=b"x" * (5 * 1024 * 1024 + 1), playback_status=PlaybackStatus.PLAYING)
    assert coordinator.consume(huge).reason == "baseline"
    assert coordinator.consume(MediaSnapshot("Spotify.exe", "session-1", "", "Artist", playback_status=PlaybackStatus.PLAYING)).visible is False
