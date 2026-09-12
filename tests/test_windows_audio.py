from fh6_radio_clean_v02 import PycawSessionProvider


def test_pycaw_provider_degrades_when_optional_dependency_missing(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "pycaw", None)
    assert tuple(PycawSessionProvider().sessions()) == ()
