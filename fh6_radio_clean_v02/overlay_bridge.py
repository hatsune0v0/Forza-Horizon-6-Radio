"""Generation-gated bridge between asynchronous media providers and UI code."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .overlay import MediaSnapshot, OverlayCoordinator, OverlayStatus


@dataclass(frozen=True)
class SnapshotDelivery:
    generation: int
    snapshot: MediaSnapshot | None


class OverlayBridge:
    def __init__(self, coordinator: OverlayCoordinator | None = None, *, on_status: Callable[[OverlayStatus], None] | None = None) -> None:
        self.coordinator = coordinator or OverlayCoordinator()
        self.on_status = on_status or (lambda status: None)
        self.generation = 0
        self.closed = False

    def start(self, *, enabled: bool = True) -> int:
        self.generation += 1
        self.closed = False
        self._emit(self.coordinator.set_lifecycle(enabled=enabled, service_running=True))
        return self.generation

    def stop(self) -> None:
        self.generation += 1
        self._emit(self.coordinator.set_lifecycle(service_running=False))

    def close(self) -> None:
        if self.closed:
            return
        self.generation += 1
        self.closed = True
        self._emit(self.coordinator.close())

    def deliver(self, delivery: SnapshotDelivery) -> bool:
        if self.closed or delivery.generation != self.generation:
            return False
        self._emit(self.coordinator.consume(delivery.snapshot))
        return True

    def set_focus(self, focused: bool) -> None:
        self._emit(self.coordinator.set_focus(focused))

    def set_scene(self, scene) -> None:
        self._emit(self.coordinator.set_scene(scene))

    def _emit(self, status: OverlayStatus) -> None:
        self.on_status(status)
