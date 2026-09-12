"""Schema-5 overlay preference with read-only migration and atomic saves."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = 5


@dataclass(frozen=True)
class OverlaySettings:
    enabled: bool = True


def load_overlay_settings(path: str | os.PathLike[str]) -> tuple[OverlaySettings, str | None]:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("root is not an object")
        value = raw.get("overlay_enabled", True)
        if not isinstance(value, bool):
            return OverlaySettings(), "overlay setting invalid; using enabled default"
        return OverlaySettings(value), None
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return OverlaySettings(), f"overlay configuration unavailable ({type(exc).__name__})"


def save_overlay_settings(path: str | os.PathLike[str], settings: OverlaySettings) -> None:
    if not isinstance(settings.enabled, bool):
        raise ValueError("overlay enabled must be boolean")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": SCHEMA_VERSION, "overlay_enabled": settings.enabled}
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2)
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
