"""Thread-free orchestration boundary for adapters used by the clean rewrite."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Protocol

from .core import Publication, Scene, StateMachine
from .settings import VolumeSettings
from .volume import target_for


class AudioSink(Protocol):
    def set_volume(self, value: float) -> None: ...

    def set_playback(self, intent: str) -> None: ...


class Clock(Protocol):
    def __call__(self) -> float: ...


class ProcessProbe(Protocol):
    def is_running(self) -> bool: ...


@dataclass(frozen=True)
class RuntimeStatus:
    publication: Publication
    audio_available: bool
    diagnostic: str | None = None


class Runtime:
    """Apply declarative state effects while keeping adapters optional."""

    def __init__(self, settings: VolumeSettings | None = None, *, sink: AudioSink | None = None,
                 process: ProcessProbe | None = None, clock: Clock | None = None,
                 on_status: Callable[[RuntimeStatus], None] | None = None) -> None:
        self.settings = settings or VolumeSettings()
        self.sink = sink
        self.process = process
        self.clock = clock or time.monotonic
        self.on_status = on_status
        self.machine = StateMachine()
        self.running = False
        self.last_status = RuntimeStatus(self.machine.tick(now=0.0, fh6_running=False), sink is not None)

    def start(self) -> RuntimeStatus:
        self.running = True
        return self.last_status

    def close(self) -> RuntimeStatus:
        publication = self.machine.stop(now=self.clock())
        self.running = False
        self._apply(publication)
        return self.last_status

    def ingest(self, packet: bytes, *, now: float | None = None, fh6_running: bool | None = None) -> RuntimeStatus:
        current_time = self.clock() if now is None else now
        process_running = self.process.is_running() if fh6_running is None and self.process is not None else bool(fh6_running)
        publication = self.machine.ingest(packet, now=current_time, fh6_running=process_running)
        self._apply(publication)
        return self.last_status

    def tick(self, *, now: float | None = None, fh6_running: bool | None = None) -> RuntimeStatus:
        current_time = self.clock() if now is None else now
        process_running = self.process.is_running() if fh6_running is None and self.process is not None else bool(fh6_running)
        publication = self.machine.tick(now=current_time, fh6_running=process_running)
        self._apply(publication)
        return self.last_status

    def force_sync(self) -> RuntimeStatus:
        publication = self.machine._publication
        self._apply(publication, force=True)
        return self.last_status

    def _apply(self, publication: Publication, *, force: bool = False) -> None:
        diagnostic = None
        if self.sink is None:
            diagnostic = "audio adapter unavailable"
        elif force or publication.effect is not None:
            try:
                self.sink.set_volume(target_for(publication.current_scene, self.settings))
                if publication.effect is not None:
                    self.sink.set_playback(publication.effect.playback_intent)
            except Exception:
                diagnostic = "audio adapter write failed"
        status = RuntimeStatus(publication, self.sink is not None, diagnostic)
        self.last_status = status
        if self.on_status is not None:
            self.on_status(status)
