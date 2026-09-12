"""Platform-neutral keyboard/gamepad input boundary for the clean v0.2 slice.

The module deliberately knows nothing about Qt, UDP, audio, or the game. Native
adapters are optional and failures are represented as status/diagnostic data.
"""

from __future__ import annotations

import queue
import sys
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping

DEFAULT_HOTKEY = "Ctrl+Alt+F9"

_MODIFIERS = {"CTRL": "Ctrl", "CONTROL": "Ctrl", "ALT": "Alt", "SHIFT": "Shift", "WIN": "Win", "META": "Win"}
_MODIFIER_ORDER = ("Ctrl", "Alt", "Shift", "Win")
_KEY_ALIASES = {
    "ESC": "Esc", "ESCAPE": "Esc", "RETURN": "Enter", "DEL": "Delete",
    "PGUP": "PageUp", "PGDOWN": "PageDown", "SPACEBAR": "Space",
    "SPACE": "Space", "BKSP": "Backspace", "BACKSPACE": "Backspace",
    "LEFT": "Left", "RIGHT": "Right", "UP": "Up", "DOWN": "Down",
}
_SPECIAL_KEYS = {"Enter", "Esc", "Space", "Tab", "Backspace", "Delete", "Insert", "Home", "End", "PageUp", "PageDown", "Left", "Right", "Up", "Down", "PrintScreen", "Pause"}

_GAMEPAD_ALIASES = {
    "UP": "DPAD_UP", "DOWN": "DPAD_DOWN", "LEFT": "DPAD_LEFT", "RIGHT": "DPAD_RIGHT",
    "DPADUP": "DPAD_UP", "DPADDOWN": "DPAD_DOWN", "DPADLEFT": "DPAD_LEFT", "DPADRIGHT": "DPAD_RIGHT",
    "LSTICK": "LS", "RSTICK": "RS", "LEFTSTICK": "LS", "RIGHTSTICK": "RS",
}
_GAMEPAD_ALLOWED = {"DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT", "START", "BACK", "LS", "RS", "LB", "RB", "A", "B", "X", "Y", "LT", "RT"}


def normalize_hotkey(value: str | None) -> str:
    """Return canonical PortableText-like hotkey text.

    ``None`` selects the default; an empty/whitespace string explicitly disables
    the hotkey. Invalid values raise ``ValueError`` with a user-readable reason.
    """
    if value is None:
        return DEFAULT_HOTKEY
    if not isinstance(value, str):
        raise ValueError("hotkey must be a string")
    text = value.strip()
    if not text:
        return ""
    parts = [part.strip() for part in text.split("+")]
    if any(not part for part in parts):
        raise ValueError("hotkey contains an empty key")
    modifiers: list[str] = []
    primary: str | None = None
    for raw in parts:
        upper = raw.upper()
        if upper in _MODIFIERS:
            modifier = _MODIFIERS[upper]
            if modifier in modifiers:
                raise ValueError(f"duplicate modifier: {modifier}")
            modifiers.append(modifier)
            continue
        if primary is not None:
            raise ValueError("hotkey must contain exactly one primary key")
        key = _KEY_ALIASES.get(upper)
        if key is None:
            if len(raw) == 1 and raw.isalpha():
                key = raw.upper()
            elif len(raw) == 1 and raw.isdigit():
                key = raw
            elif upper.startswith("F") and upper[1:].isdigit() and 1 <= int(upper[1:]) <= 24:
                key = upper
            elif raw[:1].isupper() and raw in _SPECIAL_KEYS:
                key = raw
            else:
                raise ValueError(f"unknown key name: {raw}")
        primary = key
    if primary is None:
        raise ValueError("hotkey is missing a primary key")
    ordered = [name for name in _MODIFIER_ORDER if name in modifiers]
    return "+".join((*ordered, primary))


def validate_hotkey(value: str | None) -> str:
    return normalize_hotkey(value)


def normalize_gamepad_button(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("gamepad button is required")
    names: list[str] = []
    for raw in value.split("+"):
        token = raw.strip().upper().replace("-", "").replace(" ", "")
        token = _GAMEPAD_ALIASES.get(token, token)
        if token not in _GAMEPAD_ALLOWED:
            raise ValueError(f"unsupported gamepad button: {raw.strip()}")
        if token in names:
            raise ValueError(f"duplicate gamepad button: {token}")
        names.append(token)
    # Stable display order makes equivalent combinations round-trip identically.
    order = {name: index for index, name in enumerate(("DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT", "START", "BACK", "LS", "RS", "LB", "RB", "A", "B", "X", "Y", "LT", "RT"))}
    return "+".join(sorted(names, key=order.__getitem__))


class GamepadEdgeDetector:
    def __init__(self, button: str = "START", trigger_threshold: float = 0.5):
        self.button = normalize_gamepad_button(button)
        self._members = frozenset(self.button.split("+"))
        self.trigger_threshold = trigger_threshold
        self._previous = False

    def update(self, state: Iterable[str] | Mapping[str, Any] | None) -> bool:
        pressed = _pressed_buttons(state, self.trigger_threshold)
        current = self._members.issubset(pressed)
        edge = current and not self._previous
        self._previous = current
        return edge

    def absorb(self, state: Iterable[str] | Mapping[str, Any] | None) -> None:
        self._previous = self._members.issubset(_pressed_buttons(state, self.trigger_threshold))


def _pressed_buttons(state: Iterable[str] | Mapping[str, Any] | None, threshold: float) -> set[str]:
    if state is None:
        return set()
    if isinstance(state, Mapping):
        result: set[str] = set()
        for key, value in state.items():
            name = _GAMEPAD_ALIASES.get(str(key).upper().replace("-", "").replace(" ", ""), str(key).upper())
            if name in {"LT", "RT"}:
                if isinstance(value, (int, float)) and value >= threshold:
                    result.add(name)
            elif bool(value):
                result.add(name)
        return result
    return {_GAMEPAD_ALIASES.get(str(item).upper().replace("-", "").replace(" ", ""), str(item).upper()) for item in state}


@dataclass(frozen=True)
class InputEvent:
    source: str
    action: str = "toggle_service"


class InputDispatcher:
    """Thread-safe FIFO. Producers only enqueue; ``consume`` runs callbacks."""
    def __init__(self):
        self._queue: queue.Queue[tuple[InputEvent, Callable[[], Any]]] = queue.Queue()
        self._active = True
        self._lock = threading.Lock()
        self.last_consumed: list[InputEvent] = []

    def submit(self, callback: Callable[[], Any], *, source: str = "unknown", action: str = "toggle_service") -> bool:
        with self._lock:
            if not self._active:
                raise RuntimeError("dispatcher is stopped")
            self._queue.put((InputEvent(source, action), callback))
        return True

    def consume(self, callback: Callable[[InputEvent], Any] | None = None, limit: int | None = None) -> int:
        count = 0
        consumed: list[InputEvent] = []
        while limit is None or count < limit:
            try:
                event, action = self._queue.get_nowait()
            except queue.Empty:
                break
            consumed.append(event)
            if callback is None:
                action()
            else:
                callback(event)
            count += 1
        self.last_consumed = consumed
        return count

    def invalidate(self) -> None:
        with self._lock:
            self._active = False
            while True:
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break

    def activate(self) -> None:
        with self._lock:
            self._active = True


@dataclass(frozen=True)
class InputStatus:
    gamepad_available: bool = False
    hotkey_registered: bool = False


class WindowsHotkeyRegistrar:
    """Small injectable wrapper; native registration is best-effort only."""
    def __init__(self, register_fn: Callable[[str], bool] | None = None, unregister_fn: Callable[[], bool] | None = None):
        self._register_fn, self._unregister_fn = register_fn, unregister_fn
        self.registered = False
        self.hotkey = ""

    def register(self, hotkey: str) -> bool:
        if not hotkey:
            return False
        try:
            ok = self._register_fn(hotkey) if self._register_fn else sys.platform.startswith("win")
        except Exception:
            ok = False
        self.registered = bool(ok)
        if ok:
            self.hotkey = hotkey
        return self.registered

    def unregister(self) -> bool:
        try:
            ok = self._unregister_fn() if self._unregister_fn else True
        except Exception:
            ok = False
        if ok:
            self.registered = False
            self.hotkey = ""
        return bool(ok)


class InputController:
    def __init__(self, keyboard_hotkey: str | None = None, gamepad_enabled: bool = False, gamepad_button: str = "START", dispatcher: InputDispatcher | Any | None = None, toggle_service: Callable[[], Any] | None = None, registrar: WindowsHotkeyRegistrar | None = None, provider: Any | None = None):
        self.keyboard_hotkey = normalize_hotkey(keyboard_hotkey)
        self.gamepad_enabled = bool(gamepad_enabled)
        self.gamepad_button = normalize_gamepad_button(gamepad_button)
        self.dispatcher = dispatcher or InputDispatcher()
        self.toggle_service = toggle_service
        self.registrar = registrar or WindowsHotkeyRegistrar()
        self.provider = provider
        self.detector = GamepadEdgeDetector(self.gamepad_button)
        self.diagnostics: list[str] = []
        self.status = InputStatus()
        self._running = False
        self._stop = threading.Event()
        self._worker: threading.Thread | None = None

    def start(self) -> InputStatus:
        if self._running:
            return self.status
        try:
            self.dispatcher.activate()
        except AttributeError:
            pass
        self._running = True
        hotkey_registered = False
        if self.keyboard_hotkey:
            hotkey_registered = self.registrar.register(self.keyboard_hotkey)
            if not hotkey_registered:
                self.diagnostics.append(f"global hotkey unavailable: {self.keyboard_hotkey}")
        gamepad_available = False
        if self.gamepad_enabled:
            if not sys.platform.startswith("win"):
                self.diagnostics.append("gamepad unavailable on this platform")
            elif self.provider is None:
                self.diagnostics.append("gamepad unavailable: no XInput provider")
            else:
                gamepad_available = True
                self._stop.clear()
                self._worker = threading.Thread(target=self._poll, name="input-gamepad", daemon=True)
                self._worker.start()
        self.status = InputStatus(gamepad_available, hotkey_registered)
        return self.status

    def stop(self, timeout: float = 0.25) -> None:
        if not self._running:
            return
        self._running = False
        self._stop.set()
        try:
            self.dispatcher.invalidate()
        except Exception:
            pass
        self.registrar.unregister()
        worker = self._worker
        if worker and worker is not threading.current_thread():
            worker.join(timeout=max(0.0, timeout))
        self._worker = worker if worker and worker.is_alive() else None

    def handle_hotkey(self, hotkey: str) -> bool:
        try:
            if not self._running or not self.keyboard_hotkey or normalize_hotkey(hotkey) != self.keyboard_hotkey:
                return False
        except ValueError:
            return False
        return self._enqueue("keyboard")

    def handle_gamepad_state(self, state: Iterable[str] | Mapping[str, Any] | None) -> bool:
        if not self._running or not self.gamepad_enabled:
            return False
        if self.detector.update(state):
            return self._enqueue("gamepad")
        return False

    def _enqueue(self, source: str) -> bool:
        callback = self.toggle_service or (lambda: None)
        try:
            return bool(self.dispatcher.submit(callback, source=source))
        except Exception as exc:
            self.diagnostics.append(f"input dispatch rejected ({source}): {exc}")
            return False

    def _poll(self) -> None:
        while not self._stop.is_set():
            try:
                state = self.provider.read_state()
                self.handle_gamepad_state(state)
            except Exception as exc:
                self.diagnostics.append(f"gamepad read error: {type(exc).__name__}")
                return
            self._stop.wait(0.05)
