import json

from fh6_radio_clean_v02 import OverlaySettings, load_overlay_settings, save_overlay_settings


def test_overlay_setting_defaults_and_atomic_save(tmp_path):
    source = tmp_path / "state-machine.v4.json"
    source.write_text(json.dumps({"schema_version": 4, "overlay_enabled": False}), encoding="utf-8")
    before = source.read_bytes()
    settings, warning = load_overlay_settings(source)
    assert settings == OverlaySettings(False) and warning is None
    assert source.read_bytes() == before
    target = tmp_path / "state-machine.v5.json"
    save_overlay_settings(target, settings)
    assert json.loads(target.read_text(encoding="utf-8")) == {"schema_version": 5, "overlay_enabled": False}


def test_invalid_overlay_value_falls_back_with_warning(tmp_path):
    path = tmp_path / "state-machine.v5.json"
    path.write_text(json.dumps({"overlay_enabled": "yes"}), encoding="utf-8")
    settings, warning = load_overlay_settings(path)
    assert settings == OverlaySettings() and warning
