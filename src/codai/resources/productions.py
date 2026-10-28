"""``/v1/studio/productions`` — codai Studio brief → finished output (RC-20), one of 8 kinds (``kind``, default
``video``): ``video`` (MP4 render), ``image`` (PNG), ``deck`` (PPTX), ``doc`` (DOCX), ``sheet`` (XLSX), ``carousel``
(ZIP of PNG slides + cover PNG), ``print`` (A4/A5 PDF) and ``audio`` (MP3 jingle or song).

``video``: one model turn storyboards the brief on a built-in video starter, every scene gets an image and a voice-over
line, the result is saved as an editable creative and a draft render is queued; a vision review may fix text once.
Other kinds: one plan turn, generated images or music, an editable creative and the output built by the Studio
builders; the response adds ``kind``, ``output_asset_id`` and ``outputs`` (Studio assets with a ``role``).
``starter``, ``voice``, ``narration`` and ``aspect_ratio`` apply to ``video`` only.

``create`` returns 202 ``{id, status: "running", phase}`` after the output is queued (about a minute), ``retrieve``
advances and reads it, ``wait`` polls until ``succeeded`` / ``failed`` and ``run`` does ``create`` + ``wait``. The
plan and review turns are token-metered; images, music, voice-over and renders are billed at their usual prices;
``budget_micro_usd`` (default 3,000,000 = $3) caps the whole production.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Productions", "PRODUCTION_TERMINAL_STATUSES"]

_BASE = "/v1/studio/productions"
PRODUCTION_TERMINAL_STATUSES = ("succeeded", "failed")


def _idem(key: Optional[str], ext: Optional[RequestExtensions]) -> Optional[Dict[str, Any]]:
    if not key:
        return dict(ext) if ext else None
    merged: Dict[str, Any] = dict(ext or {})
    merged["headers"] = {**dict(merged.get("headers") or {}), "Idempotency-Key": key}
    return merged


class Productions(Resource):
    """Create, read and wait for Studio productions."""

    def create(
        self,
        brief: str,
        language: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        starter: Optional[str] = None,
        voice: Optional[str] = None,
        narration: Optional[bool] = None,
        budget_micro_usd: Optional[int] = None,
        title: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        kind: Optional[str] = None,
        duration_s: Optional[int] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/productions`` — plan + images / music + creative + the output being built
        (``kind``: video | image | deck | doc | sheet | audio | carousel | print, default video)."""
        body: Dict[str, Any] = {"brief": brief}
        for k, v in (
            ("kind", kind),
            ("language", language),
            ("aspect_ratio", aspect_ratio),
            ("duration_s", duration_s),
            ("starter", starter),
            ("voice", voice),
            ("narration", narration),
            ("budget_micro_usd", budget_micro_usd),
            ("title", title),
        ):
            if v is not None:
                body[k] = v
        return (
            self._json(
                _BASE,
                ext=_idem(idempotency_key, ext),
                method="POST",
                body=body,
                no_retry=not idempotency_key,
            )
            or {}
        )

    def retrieve(self, production_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/productions/{id}`` — advances render → review → repair → ready and returns the production.
        Another account's id is a 404."""
        return self._json(f"{_BASE}/{enc(production_id)}", ext=ext) or {}

    def wait(
        self,
        production_id: str,
        interval: float = 5.0,
        timeout: float = 600.0,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Poll :meth:`retrieve` until ``status`` is ``succeeded`` or ``failed`` (a failed production is returned too).
        Raises ``TimeoutError`` after ``timeout`` seconds (default 10 min)."""
        deadline = time.monotonic() + timeout
        while True:
            p = self.retrieve(production_id, ext=ext)
            if p.get("status") in PRODUCTION_TERMINAL_STATUSES:
                return p
            if time.monotonic() + interval > deadline:
                raise TimeoutError(f"codai production {production_id} did not finish within {timeout} s")
            time.sleep(interval)

    def run(
        self,
        brief: str,
        interval: float = 5.0,
        timeout: float = 600.0,
        ext: Optional[RequestExtensions] = None,
        **params: Any,
    ) -> Dict[str, Any]:
        """:meth:`create` then :meth:`wait`. ``params`` are :meth:`create`'s keyword args."""
        p = self.create(brief, ext=ext, **params)
        if p.get("status") in PRODUCTION_TERMINAL_STATUSES:
            return p
        return self.wait(p["id"], interval=interval, timeout=timeout, ext=ext)
