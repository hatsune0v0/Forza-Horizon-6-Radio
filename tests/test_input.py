import sys
import threading
import time

import pytest

from fh6_radio_clean_v02.input import (
    InputController,
    InputDispatcher,
    GamepadEdgeDetector,
    normalize_gamepad_button,
    normalize_hotkey,
    validate_hotkey,
)


def test_hotkey_normalization_and_default():
    assert normalize_hotkey(" alt + ctrl + f9 ") == "Ctrl+Alt+F9"
    assert normalize_hotkey("") == ""
    assert normalize_hotkey(None) == "Ctrl+Alt+F9"


@pytest.mark.parametrize("value", ["Ctrl+Ctrl+F9", "Ctrl+Alt", "Ctrl+NoSuchKey", "F0", "+A"])
def test_hotkey_validation_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        validate_hotkey(value)


def test_gamepad_single_and_combined_buttons_are_canonical():
    assert normalize_gamepad_button("rb+lb") == "LB+RB"
    assert normalize_gamepad_button(" lt + rt ") == "LT+RT"
    assert normalize_gamepad_button("up") == "DPAD_UP"


def test_gamepad_combination_requires_all_members_and_edge_only_once():
    detector = GamepadEdgeDetector("LB+RB")
    assert detector.update({"LB"}) is False
    assert detector.update({"LB", "RB"}) is True
    assert detector.update({"LB", "RB"}) is False
    assert detector.update(set()) is False
    assert detector.update({"RB", "LB"}) is True


def test_dispatcher_is_fifo_and_does_not_run_callback_on_submit():
    seen = []
    dispatcher = InputDispatcher()
    dispatcher.submit(lambda: seen.append("a"), source="keyboard")
    dispatcher.submit(lambda: seen.append("b"), source="gamepad")
    assert seen == []
    assert dispatcher.consume() == 2
    assert seen == ["a", "b"]


def test_dispatcher_stop_invalidates_unconsumed_requests():
    seen = []
    dispatcher = InputDispatcher()
    dispatcher.submit(lambda: seen.append(1), source="keyboard")
    dispatcher.invalidate()
    assert dispatcher.consume() == 0
    assert seen == []


def test_controller_queues_hotkey_and_gamepad_without_direct_callback(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    seen = []
    dispatcher = InputDispatcher()
    controller = InputController(
        keyboard_hotkey="Ctrl+Alt+F9", gamepad_enabled=True, gamepad_button="A", dispatcher=dispatcher
    )
    controller.start()
    controller.handle_hotkey("Ctrl+Alt+F9")
    controller.handle_gamepad_state({"A"})
    controller.handle_gamepad_state({"A"})
    assert seen == []
    assert dispatcher.consume(callback=seen.append) == 2
    assert [item.source for item in dispatcher.last_consumed] == ["keyboard", "gamepad"]
    controller.stop()


def test_controller_dispatcher_rejection_is_safe_and_diagnostic():
    class Rejecting:
        def submit(self, *args, **kwargs):
            raise RuntimeError("closed")

    controller = InputController(dispatcher=Rejecting(), keyboard_hotkey="F8")
    controller.start()
    controller.handle_hotkey("F8")
    assert controller.diagnostics
    controller.stop()


def test_non_windows_native_adapters_degrade_safely(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    controller = InputController(gamepad_enabled=True)
    status = controller.start()
    assert status.gamepad_available is False
    assert any("unavailable" in msg.lower() for msg in controller.diagnostics)
    controller.stop()


def test_controller_stop_does_not_wait_for_blocking_provider():
    class BlockingProvider:
        def read_state(self):
            time.sleep(5)
            return set()

    controller = InputController(gamepad_enabled=True, provider=BlockingProvider())
    controller.start()
    started = time.monotonic()
    controller.stop(timeout=0.01)
    assert time.monotonic() - started < 1
