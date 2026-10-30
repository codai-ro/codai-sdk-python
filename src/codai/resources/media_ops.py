"""``/v1/studio/media-ops`` — codai Studio media operations on your assets (AR-02): background removal, upscale,
inpaint / outpaint / erase, stem separation, denoise, audio → MIDI, mastering, analysis, ACE-Step music and sound
effects.

``list`` returns the op catalogue (engine, mode, inputs, ``available``, a list quote; free), ``quote`` the exact price
of a request (free), ``run`` executes one op — sync ops answer with a ``media_op.result`` (the stored outputs), async
ops with a ``media_op.job`` (``status: pending``) — ``job`` reads a job (a finished one is settled on read), ``wait``
polls until ``ready`` / ``failed`` and ``run_and_wait`` does ``run`` + ``wait``. The quote is held on the wallet (402
``insufficient_funds``), the measured cost is billed once; every output is AI-marked and carries lineage
(``parent_asset_id``, ``op``, ``op_inputs``). A lane that is not configured answers 503 ``media_ops_unavailable``.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Sequence

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["MediaOps", "MEDIA_JOB_TERMINAL_STATUSES", "is_media_op_job"]

_BASE = "/v1/studio/media-ops"
MEDIA_JOB_TERMINAL_STATUSES = ("ready", "failed")


def is_media_op_job(result: Dict[str, Any]) -> bool:
    """True when a ``run`` answer is an async job (HTTP 202) rather than a sync result."""
    return result.get("object") == "media_op.job"


def _idem(key: Optional[str], ext: Optional[RequestExtensions]) -> Optional[Dict[str, Any]]:
    if not key:
        return dict(ext) if ext else None
    merged: Dict[str, Any] = dict(ext or {})
    merged["headers"] = {**dict(merged.get("headers") or {}), "Idempotency-Key": key}
    return merged


def _body(
    asset_ids: Optional[Sequence[str]], params: Optional[Dict[str, Any]], mask_png_b64: Optional[str] = None
) -> Dict[str, Any]:
    ids: List[str] = list(asset_ids or [])
    body: Dict[str, Any] = {"asset_ids": ids, "params": dict(params or {})}
    if mask_png_b64 is not None:
        body["mask_png_b64"] = mask_png_b64
    return body


class MediaOps(Resource):
    """List, quote, run and wait for Studio media operations."""

    def list(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/media-ops`` — every op with engine, mode, inputs, ``available`` and a list quote (free)."""
        return self._json(_BASE, ext=ext) or {}

    def quote(
        self,
        op: str,
        asset_ids: Optional[Sequence[str]] = None,
        params: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
        mask_png_b64: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/media-ops/{op}/quote`` — exact price of this request; nothing is held or billed.
        ``mask_png_b64`` (inpaint / erase) is validated without storing anything."""
        body = _body(asset_ids, params, mask_png_b64)
        return self._json(f"{_BASE}/{enc(op)}/quote", ext=ext, method="POST", body=body) or {}

    def run(
        self,
        op: str,
        asset_ids: Optional[Sequence[str]] = None,
        params: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        mask_png_b64: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/media-ops/{op}`` — a ``media_op.result`` (sync ops) or a ``media_op.job`` (async ops; poll
        with :meth:`job` / :meth:`wait`). ``asset_ids`` in the order the op expects (mask second). For
        ``image.inpaint`` / ``image.erase`` you may instead send ONE asset id plus ``mask_png_b64`` (a base64 PNG mask
        painted in an editor, white = edit, black = keep, at most 8 MB): the gateway stores it as a free private asset
        and passes it as the second input."""
        return (
            self._json(
                f"{_BASE}/{enc(op)}",
                ext=_idem(idempotency_key, ext),
                method="POST",
                body=_body(asset_ids, params, mask_png_b64),
                no_retry=not idempotency_key,
            )
            or {}
        )

    def job(self, job_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/media-ops/jobs/{id}`` — the job; reading a finished one stores its outputs and bills it once.
        Another account's id is a 404."""
        return self._json(f"{_BASE}/jobs/{enc(job_id)}", ext=ext) or {}

    def wait(
        self,
        job_id: str,
        interval: float = 3.0,
        timeout: float = 1200.0,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Poll :meth:`job` until ``status`` is ``ready`` or ``failed`` (a failed job is returned too — check ``error``).
        Raises ``TimeoutError`` after ``timeout`` seconds (default 20 min, the server-side job timeout)."""
        deadline = time.monotonic() + timeout
        while True:
            j = self.job(job_id, ext=ext)
            if j.get("status") in MEDIA_JOB_TERMINAL_STATUSES:
                return j
            if time.monotonic() + interval > deadline:
                raise TimeoutError(f"codai media job {job_id} did not finish within {timeout} s")
            time.sleep(interval)

    def run_and_wait(
        self,
        op: str,
        asset_ids: Optional[Sequence[str]] = None,
        params: Optional[Dict[str, Any]] = None,
        interval: float = 3.0,
        timeout: float = 1200.0,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        mask_png_b64: Optional[str] = None,
    ) -> Dict[str, Any]:
        """:meth:`run`, then :meth:`wait` when the op answered with a pending job."""
        r = self.run(op, asset_ids, params, idempotency_key=idempotency_key, ext=ext, mask_png_b64=mask_png_b64)
        if is_media_op_job(r) and r.get("status") not in MEDIA_JOB_TERMINAL_STATUSES:
            return self.wait(r["id"], interval=interval, timeout=timeout, ext=ext)
        return r
