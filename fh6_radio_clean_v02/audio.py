"""Strict, injectable audio-session target boundary.

The default implementation is intentionally inert. A Windows backend can
implement ``AudioSessionProvider`` without changing matching or safety rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from .volume import matches_process


class AudioSession(Protocol):
    process_name: str

    def set_volume(self, value: float) -> None: ...


class AudioSessionProvider(Protocol):
    def sessions(self) -> Iterable[AudioSession]: ...


@dataclass(frozen=True)
class AudioWriteReport:
    matched: int
    written: int
    failed: int
    diagnostic: str | None = None


class StrictAudioTarget:
    def __init__(self, provider: AudioSessionProvider | None, process_names: tuple[str, ...] = ("Spotify.exe",)) -> None:
        self.provider = provider
        self.process_names = tuple(name.strip() for name in process_names if isinstance(name, str) and name.strip())

    def write(self, value: float) -> AudioWriteReport:
        if not 0.0 <= value <= 1.0:
            raise ValueError("volume must be within 0..1")
        if self.provider is None:
            return AudioWriteReport(0, 0, 0, "audio session provider unavailable")
        matched = written = failed = 0
        try:
            sessions = self.provider.sessions()
        except Exception:
            return AudioWriteReport(0, 0, 0, "audio session discovery failed")
        for session in sessions:
            if not matches_process(getattr(session, "process_name", ""), self.process_names):
                continue
            matched += 1
            try:
                session.set_volume(value)
            except Exception:
                failed += 1
            else:
                written += 1
        diagnostic = None if matched else "target application not running or has no audio session"
        return AudioWriteReport(matched, written, failed, diagnostic)
