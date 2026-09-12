import os

import pytest


def test_material_window_has_navigation_and_status(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    try:
        from PySide6.QtWidgets import QApplication
        from fh6_radio_clean_v02 import MaterialWindow
    except ImportError:
        pytest.skip("PySide6 unavailable")
    app = QApplication.instance() or QApplication([])
    window = MaterialWindow()
    assert window.navigation.count() == 6
    assert window.pages.count() == 6
    window.set_status("PLAYING")
    assert window.status.text() == "PLAYING"
    window.close()
    app.processEvents()
