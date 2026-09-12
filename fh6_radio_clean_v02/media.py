"""Provider-neutral media metadata and playlist interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(frozen=True)
class Track:
    title: str
    artist: str
    album: str | None = None
    cover_path: str | None = None


class MediaProvider(Protocol):
    def current(self) -> Track | None: ...


class Playlist(Protocol):
    def tracks(self) -> Iterable[Track]: ...


def normalize_track(track: Track | None) -> Track | None:
    if track is None:
        return None
    title = track.title.strip()
    artist = track.artist.strip()
    if not title or not artist:
        return None
    return Track(title, artist, track.album.strip() if isinstance(track.album, str) and track.album.strip() else None, track.cover_path)


def track_key(track: Track | None) -> tuple[str, str] | None:
    normalized = normalize_track(track)
    return None if normalized is None else (normalized.title.casefold(), normalized.artist.casefold())
