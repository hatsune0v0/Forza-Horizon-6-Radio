"""Pure scene volume targets, fade curves, and strict process matching."""

from __future__ import annotations

from dataclasses import dataclass

from .core import Scene
from .settings import VolumeSettings


def curve_value(curve: str, progress: float) -> float:
    p = max(0.0, min(1.0, float(progress)))
    if curve == "linear":
        return p
    if curve == "smoothstep":
        return p * p * (3.0 - 2.0 * p)
    if curve == "ease_in":
        return p * p
    if curve == "ease_out":
        return 1.0 - (1.0 - p) * (1.0 - p)
    if curve == "ease_in_out":
        return 2.0 * p * p if p < 0.5 else 1.0 - ((-2.0 * p + 2.0) ** 2) / 2.0
    raise ValueError("unsupported fade curve")


def target_for(scene: Scene, settings: VolumeSettings) -> float:
    return {
        Scene.PLAYING: settings.free_roam,
        Scene.RACE: settings.race,
        Scene.TRANSITION: settings.transition,
        Scene.PAUSED: settings.paused,
        Scene.STOPPED: 0,
    }[scene] / 100.0


@dataclass
class Fade:
    start: float
    end: float
    started_at: float
    duration: float
    curve: str

    def value_at(self, now: float) -> float:
        if self.duration <= 0:
            return self.end
        return self.start + (self.end - self.start) * curve_value(self.curve, (now - self.started_at) / self.duration)


def normalize_process_name(name: str) -> str:
    return name.strip().casefold()


def matches_process(name: str, configured: tuple[str, ...]) -> bool:
    candidate = normalize_process_name(name)
    return bool(candidate) and any(candidate == normalize_process_name(item) for item in configured)
