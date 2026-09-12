import json

import pytest

from fh6_radio_clean_v02 import Fade, Scene, VolumeSettings, curve_value, load_settings, matches_process, save_settings, target_for


def test_defaults_and_scene_targets():
    settings = VolumeSettings()
    assert (settings.free_roam, settings.race, settings.transition, settings.paused, settings.stopped) == (100, 80, 15, 0, 0)
    assert target_for(Scene.PLAYING, settings) == 1.0
    assert target_for(Scene.RACE, settings) == 0.8
    assert target_for(Scene.STOPPED, settings) == 0.0


def test_schema_two_fields_migrate_without_writing_source(tmp_path):
    source = tmp_path / "state-machine.v2.json"
    source.write_text(json.dumps({"schema_version": 2, "normal_volume": 72, "duck_volume": 11}), encoding="utf-8")
    before = source.read_bytes()
    settings, warning = load_settings(source)
    assert warning is None and settings.free_roam == 72 and settings.transition == 11
    assert source.read_bytes() == before
    out = tmp_path / "state-machine.v3.json"
    save_settings(out, settings)
    assert json.loads(out.read_text(encoding="utf-8"))["schema_version"] == 3


def test_corrupt_settings_fall_back(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")
    settings, warning = load_settings(path)
    assert settings == VolumeSettings() and warning is not None


def test_curves_are_bounded_and_monotonic():
    for curve in ("linear", "smoothstep", "ease_in", "ease_out", "ease_in_out"):
        values = [curve_value(curve, i / 10) for i in range(11)]
        assert values[0] == 0 and values[-1] == 1 and values == sorted(values)
        assert all(0 <= value <= 1 for value in values)


def test_fade_reaches_end_and_zero_duration_is_immediate():
    assert Fade(0.2, 0.8, 10.0, 2.0, "linear").value_at(11.0) == pytest.approx(0.5)
    assert Fade(0.2, 0.8, 10.0, 0.0, "linear").value_at(10.0) == 0.8


def test_process_matching_is_exact_and_case_insensitive():
    configured = (" Spotify.exe ",)
    assert matches_process("spotify.exe", configured)
    assert not matches_process("spotifyhelper.exe", configured)
    assert not matches_process("Chrome.exe", configured)
