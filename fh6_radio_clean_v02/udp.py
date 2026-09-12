"""Minimal UDP adapter that feeds bytes into the pure runtime."""

from __future__ import annotations

import socket
import threading
from dataclasses import dataclass
from typing import Callable

from .runtime import Runtime


@dataclass(frozen=True)
class UdpAddress:
    host: str = "127.0.0.1"
    port: int = 5300


class UdpService:
    def __init__(self, runtime: Runtime, address: UdpAddress | None = None, *, process_running: Callable[[], bool] | None = None) -> None:
        self.runtime = runtime
        self.address = address or UdpAddress()
        self.process_running = process_running or (lambda: True)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._socket: socket.socket | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.running:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._worker, name="fh6-radio-udp", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self._stop.set()
        sock = self._socket
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass
        thread = self._thread
        if thread is not None:
            thread.join(timeout=max(0.0, timeout))
        self._thread = None

    def _worker(self) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                self._socket = sock
                sock.settimeout(0.2)
                sock.bind((self.address.host, self.address.port))
                while not self._stop.is_set():
                    try:
                        data, _ = sock.recvfrom(4096)
                    except socket.timeout:
                        self.runtime.tick(fh6_running=self.process_running())
                        continue
                    except OSError:
                        break
                    self.runtime.ingest(data, fh6_running=self.process_running())
        except OSError:
            # Binding and adapter failures are represented by the runtime's
            # diagnostics in the host application; the worker must not escape.
            return
        finally:
            self._socket = None
