"""Deterministic state machine with no networking, UI, or audio dependencies."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .parser import PacketFormatError, Telemetry, decode_packet

ENTRY_PACKETS_REQUIRED = 3
EXIT_PACKETS_REQUIRED = 3
STALE_AFTER_SECONDS = 1.0


class Scene(str, Enum):
    PLAYING = "PLAYING"
    RACE = "RACE"
    TRANSITION = "TRANSITION"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


@dataclass(frozen=True)
class Effect:
    target_volume: float
    playback_intent: str
    reason: str


@dataclass(frozen=True)
class Publication:
    connection_status: str
    current_scene: Scene
    current_volume: Optional[float]
    target_volume: float
    playback_status: str
    current_song: Optional[str]
    current_playlist: Optional[str]
    error_info: Optional[str]
    effect: Optional[Effect] = None


class StateMachine:
    def __init__(self, *, stale_after: float = STALE_AFTER_SECONDS) -> None:
        if isinstance(stale_after, bool) or not isinstance(stale_after, (int, float)) or not math.isfinite(stale_after) or stale_after <= 0:
            raise ValueError("stale_after must be finite and positive")
        self._stale_after = stale_after
        self._service_active = True
        self._last_packet_at: Optional[float] = None
        self._last_time: Optional[float] = None
        self._race_confirmed = False
        self._entry_count = 0
        self._exit_count = 0
        self._publication = Publication("DISCONNECTED", Scene.STOPPED, None, 0.0, "UNKNOWN", None, None, None)
        self._last_effect_key: Optional[tuple[Scene, float]] = None

    def stop(self, *, now: float | None = None) -> Publication:
        # A no-argument stop uses the latest accepted timestamp so shutdown
        # remains safe after the clock has advanced.
        stop_time = self._last_time if now is None and self._last_time is not None else (0.0 if now is None else now)
        self._accept_time(stop_time)
        self._service_active = False
        return self._publish("DISCONNECTED", Scene.STOPPED, reason="service stopped")

    def ingest(self, data: bytes, *, now: float, fh6_running: bool) -> Publication:
        self._accept_time(now)
        if not self._service_active:
            return self._without_effect()
        if not fh6_running:
            self._clear_race()
            return self._publish("DISCONNECTED", Scene.STOPPED, reason="FH6 process stopped")
        if self._last_packet_at is not None and now - self._last_packet_at > self._stale_after:
            self._clear_race()
        try:
            packet = decode_packet(data)
        except PacketFormatError as exc:
            if exc.kind == "length":
                self._clear_race()
                return self._without_effect()
            self._clear_race()
            return self._publish("STALE", Scene.TRANSITION, reason="invalid telemetry fields")

        self._last_packet_at = now
        if not packet.is_race_on:
            self._clear_race()
            return self._publish("CONNECTED", Scene.PAUSED, reason="race flag off")
        if packet.race_position_324 > 0:
            self._exit_count = 0
            if not self._race_confirmed:
                self._entry_count += 1
                if self._entry_count >= ENTRY_PACKETS_REQUIRED:
                    self._race_confirmed = True
            scene = Scene.RACE if self._race_confirmed else Scene.PLAYING
            return self._publish("CONNECTED", scene, reason="nonzero race position")

        self._entry_count = 0
        if self._race_confirmed:
            self._exit_count += 1
            if self._exit_count >= EXIT_PACKETS_REQUIRED:
                self._race_confirmed = False
                self._exit_count = 0
                return self._publish("CONNECTED", Scene.TRANSITION, reason="race evidence cleared")
            return self._publish("CONNECTED", Scene.RACE, reason="race evidence held")
        return self._publish("CONNECTED", Scene.PLAYING, reason="normal driving")

    def tick(self, *, now: float, fh6_running: bool) -> Publication:
        self._accept_time(now)
        if not self._service_active:
            return self._without_effect()
        if not fh6_running:
            self._clear_race()
            return self._publish("DISCONNECTED", Scene.STOPPED, reason="FH6 process stopped")
        if self._last_packet_at is None or now - self._last_packet_at > self._stale_after:
            self._clear_race()
            return self._publish("STALE", Scene.TRANSITION, reason="telemetry stale")
        return self._without_effect()

    def observe_volume(self, value: float) -> Publication:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("observed volume must be finite and within 0..1")
        self._publication = Publication(self._publication.connection_status, self._publication.current_scene, float(value), self._publication.target_volume, self._publication.playback_status, self._publication.current_song, self._publication.current_playlist, self._publication.error_info, None)
        return self._publication

    def _accept_time(self, now: float) -> None:
        if isinstance(now, bool) or not isinstance(now, (int, float)) or not math.isfinite(now):
            raise ValueError("time must be finite")
        if self._last_time is not None and now < self._last_time:
            raise ValueError("time must be monotonic")
        self._last_time = float(now)

    def _clear_race(self) -> None:
        self._race_confirmed = False
        self._entry_count = 0
        self._exit_count = 0

    def _publish(self, connection: str, scene: Scene, *, reason: str) -> Publication:
        target = {
            Scene.PLAYING: 1.0,
            Scene.RACE: 0.80,
            Scene.TRANSITION: 0.15,
            Scene.PAUSED: 0.0,
            Scene.STOPPED: 0.0,
        }[scene]
        intent = {
            Scene.PLAYING: "PLAY",
            Scene.RACE: "PLAY",
            Scene.TRANSITION: "PAUSE",
            Scene.PAUSED: "PAUSE",
            Scene.STOPPED: "STOP",
        }[scene]
        key = (scene, target)
        effect = None
        if key != self._last_effect_key:
            effect = Effect(target, intent, reason)
            self._last_effect_key = key
        publication = Publication(connection, scene, self._publication.current_volume, target, "UNKNOWN", None, None, None, effect)
        self._publication = publication
        return publication

    def _without_effect(self) -> Publication:
        if self._publication.effect is None:
            return self._publication
        self._publication = Publication(self._publication.connection_status, self._publication.current_scene, self._publication.current_volume, self._publication.target_volume, self._publication.playback_status, self._publication.current_song, self._publication.current_playlist, self._publication.error_info, None)
        return self._publication
