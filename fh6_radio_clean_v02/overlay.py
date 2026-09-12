"""Pure media overlay gating and first-observation de-duplication."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from .core import Scene

SPOTIFY_WIN32 = "spotify.exe"
SPOTIFY_AUMID = "spotifyab.spotifymusic_zpdnekdrzrea0!spotify"


class PlaybackStatus(str, Enum):
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MediaSnapshot:
    source_id: str
    provider_identity: str
    title: str
    artist: str
    album_title: str | None = None
    track_number: int | None = None
    playback_status: PlaybackStatus = PlaybackStatus.UNKNOWN
    cover_bytes: bytes | None = None
    cover_mime: str | None = None

    def normalized(self) -> "MediaSnapshot | None":
        source = self.source_id.strip().casefold()
        if source not in {SPOTIFY_WIN32, SPOTIFY_AUMID}:
            return None
        title, artist = self.title.strip(), self.artist.strip()
        if not title or not artist or self.playback_status is not PlaybackStatus.PLAYING:
            return None
        number = self.track_number if isinstance(self.track_number, int) and not isinstance(self.track_number, bool) and self.track_number >= 0 else None
        album = self.album_title.strip() if isinstance(self.album_title, str) and self.album_title.strip() else None
        cover = self.cover_bytes if isinstance(self.cover_bytes, bytes) and len(self.cover_bytes) <= 5 * 1024 * 1024 else None
        return MediaSnapshot(source, self.provider_identity, title, artist, album, number, PlaybackStatus.PLAYING, cover, self.cover_mime)

    def key(self) -> tuple[str, str, str, str | None, int | None]:
        normalized = self.normalized()
        if normalized is None:
            raise ValueError("snapshot is not displayable")
        return (normalized.source_id, normalized.title.casefold(), normalized.artist.casefold(), normalized.album_title.casefold() if normalized.album_title else None, normalized.track_number)


@dataclass(frozen=True)
class OverlayStatus:
    visible: bool
    reason: str
    snapshot: MediaSnapshot | None = None


class OverlayCoordinator:
    def __init__(self, *, show: Callable[[MediaSnapshot], None] | None = None, hide: Callable[[], None] | None = None) -> None:
        self.show = show or (lambda snapshot: None)
        self.hide = hide or (lambda: None)
        self.enabled = True
        self.service_running = False
        self.focused = False
        self.scene = Scene.STOPPED
        self._baseline: tuple[str, str, str, str | None, int | None] | None = None
        self.status = OverlayStatus(False, "stopped")

    def set_lifecycle(self, *, enabled: bool | None = None, service_running: bool | None = None) -> OverlayStatus:
        if enabled is not None:
            self.enabled = bool(enabled)
        if service_running is not None:
            self.service_running = bool(service_running)
        if not self.enabled or not self.service_running:
            if not self.service_running:
                self._baseline = None
            return self._hide("disabled" if not self.enabled else "stopped")
        return self.status

    def set_focus(self, focused: bool) -> OverlayStatus:
        self.focused = bool(focused)
        return self.status if self.focused else self._hide("fh6-not-focused")

    def set_scene(self, scene: Scene) -> OverlayStatus:
        self.scene = scene
        return self._hide("scene-blocked") if scene in {Scene.PAUSED, Scene.STOPPED} else self.status

    def consume(self, snapshot: MediaSnapshot | None) -> OverlayStatus:
        normalized = snapshot.normalized() if snapshot is not None else None
        if normalized is None:
            return self._hide("media-unavailable")
        key = normalized.key()
        if self._baseline is None:
            self._baseline = key
            return self._hide("baseline")
        changed = key != self._baseline
        self._baseline = key
        if not changed:
            return self.status
        if not (self.enabled and self.service_running and self.focused and self.scene in {Scene.PLAYING, Scene.RACE, Scene.TRANSITION}):
            return self._hide("gate-blocked")
        self.show(normalized)
        self.status = OverlayStatus(True, "new-track", normalized)
        return self.status

    def close(self) -> OverlayStatus:
        self.enabled = False
        self.service_running = False
        self._baseline = None
        return self._hide("closed")

    def _hide(self, reason: str) -> OverlayStatus:
        self.hide()
        self.status = OverlayStatus(False, reason, None)
        return self.status
