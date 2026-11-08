"""``/v1/studio/exports`` — codai Studio FCPXML exports: project zips of your video creatives (``project.fcpxml`` +
per-scene MP4 segments + audio) for Final Cut Pro, DaVinci Resolve or Premiere.

Queue one with :meth:`codai.resources.creatives.Creatives.export_fcpxml`, then :meth:`Exports.wait` until the zip is
ready. Only newly rendered seconds are billed (at the final render price); polling is free.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Exports"]

_BASE = "/v1/studio/exports"
_DONE = ("succeeded", "failed")


class Exports(Resource):
    """Read and wait for FCPXML exports."""

    def retrieve(self, export_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/exports/{id}`` — ``{id, status, creative_id, seq, format, fps, filename, url, expires_at,
        bytes, rendered_seconds, cost_micro_usd, warnings, error, created_at}``; ``url`` (signed, valid 1 h) once
        ``status`` is ``succeeded``. Free."""
        return self._json(f"{_BASE}/{enc(export_id)}", ext=ext) or {}

    def wait(
        self,
        export_id: str,
        interval: float = 3.0,
        timeout: float = 900.0,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Poll :meth:`retrieve` every ``interval`` seconds until the export is ``succeeded`` or ``failed`` and return
        it (a ``failed`` export is returned too — check ``status`` / ``error``). Raises ``TimeoutError`` when it is not
        done within ``timeout`` seconds (default 15 min)."""
        deadline = time.monotonic() + timeout
        while True:
            st = self.retrieve(export_id, ext=ext)
            if st.get("status") in _DONE:
                return st
            if time.monotonic() + interval > deadline:
                raise TimeoutError(f"codai export {export_id} did not finish within {timeout} s")
            time.sleep(interval)
