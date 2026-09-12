"""Optional Windows pycaw bridge for the strict injected audio target."""

from __future__ import annotations

from typing import Any, Iterable


class PycawSession:
    def __init__(self, session: Any) -> None:
        self._session = session
        process = getattr(session, "Process", None)
        self.process_name = process.name() if process is not None else ""

    def set_volume(self, value: float) -> None:
        self._session._ctl.GetSimpleAudioVolume().SetMasterVolume(float(value), None)


class PycawSessionProvider:
    """Enumerate only sessions exposed by pycaw; no import is attempted at module load."""

    def sessions(self) -> Iterable[PycawSession]:
        try:
            from pycaw.pycaw import AudioUtilities
        except ImportError:
            return ()
        result = []
        for session in AudioUtilities.GetAllSessions():
            try:
                if session.Process is not None and session._ctl.GetSimpleAudioVolume() is not None:
                    result.append(PycawSession(session))
            except Exception:
                continue
        return tuple(result)
