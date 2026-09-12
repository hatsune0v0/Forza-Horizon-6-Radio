"""Small, isolated configuration model for the independent v0.2 rewrite."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 3


@dataclass(frozen=True)
class VolumeSettings:
    free_roam: int = 100
    race: int = 80
    transition: int = 15
    paused: int = 0
    stopped: int = 0
    fade_duration_ms: int = 500
    fade_curve: str = "smoothstep"
    target_process_names: tuple[str, ...] = ("Spotify.exe",)

    def __post_init__(self) -> None:
        for name in ("free_roam", "race", "transition", "paused", "stopped"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
                raise ValueError(f"{name} must be an integer from 0 to 100")
        if isinstance(self.fade_duration_ms, bool) or not isinstance(self.fade_duration_ms, int) or not 0 <= self.fade_duration_ms <= 10000:
            raise ValueError("fade_duration_ms must be an integer from 0 to 10000")
        if self.fade_curve not in {"linear", "smoothstep", "ease_in", "ease_out", "ease_in_out"}:
            raise ValueError("unsupported fade_curve")
        names = tuple(n.strip() for n in self.target_process_names if isinstance(n, str) and n.strip())
        object.__setattr__(self, "target_process_names", names)


def _int_value(raw: dict[str, Any], key: str, fallback: int) -> int:
    value = raw.get(key, fallback)
    return max(0, min(100, value)) if isinstance(value, int) and not isinstance(value, bool) else fallback


def _from_mapping(raw: dict[str, Any]) -> VolumeSettings:
    names = raw.get("target_process_names", ["Spotify.exe"])
    if not isinstance(names, list):
        names = ["Spotify.exe"]
    return VolumeSettings(
        free_roam=_int_value(raw, "free_roam_volume", _int_value(raw, "normal_volume", 100)),
        race=_int_value(raw, "race_volume", 80),
        transition=_int_value(raw, "transition_volume", _int_value(raw, "duck_volume", 15)),
        paused=_int_value(raw, "paused_volume", 0),
        stopped=_int_value(raw, "stopped_volume", 0),
        fade_duration_ms=raw.get("fade_duration_ms", 500) if isinstance(raw.get("fade_duration_ms", 500), int) and not isinstance(raw.get("fade_duration_ms", 500), bool) else 500,
        fade_curve=raw.get("fade_curve", "smoothstep") if isinstance(raw.get("fade_curve", "smoothstep"), str) else "smoothstep",
        target_process_names=tuple(names),
    )


def load_settings(path: str | os.PathLike[str]) -> tuple[VolumeSettings, str | None]:
    target = Path(path)
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("root is not an object")
        return _from_mapping(raw), None
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return VolumeSettings(), f"configuration unavailable ({type(exc).__name__})"


def save_settings(path: str | os.PathLike[str], settings: VolumeSettings) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": SCHEMA_VERSION, **asdict(settings)}
    payload["target_process_names"] = list(settings.target_process_names)
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
