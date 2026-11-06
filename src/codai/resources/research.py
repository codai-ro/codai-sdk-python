"""``/v1/research`` — asynchronous deep research: codai plans several searches, reads the best pages and writes a
report where every claim cites its source as ``[S1]``..``[Sn]`` (or a JSON ``answer`` with ``output_schema``).

``create`` starts a job (200 when it finished within ``wait_s``, else 202 ``{id, status}``), ``retrieve`` reads it,
``wait`` polls until ``done`` / ``failed`` and ``run`` does ``create`` + ``wait``. Price: $0.20 per job plus its model
tokens (free inside the monthly allowance or a codai agent turn). Polling is free.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Research", "RESEARCH_TERMINAL_STATUSES"]

_BASE = "/v1/research"
RESEARCH_TERMINAL_STATUSES = ("done", "failed")


def _idem(key: Optional[str], ext: Optional[RequestExtensions]) -> Optional[Dict[str, Any]]:
    if not key:
        return dict(ext) if ext else None
    merged: Dict[str, Any] = dict(ext or {})
    merged["headers"] = {**dict(merged.get("headers") or {}), "Idempotency-Key": key}
    return merged


class Research(Resource):
    """Start, read and wait for deep-research jobs."""

    def create(
        self,
        question: str,
        time_budget_s: Optional[int] = None,
        max_sources: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        published_after: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        wait_s: Optional[float] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/research`` — ``{id, status, created_at}`` while ``queued`` / ``running``; with ``wait_s``
        (0..55) the call waits that long and returns the finished job. The same ``idempotency_key`` returns the job
        created earlier instead of starting another one."""
        body: Dict[str, Any] = {"question": question}
        for k, v in (
            ("time_budget_s", time_budget_s),
            ("max_sources", max_sources),
            ("include_domains", include_domains),
            ("published_after", published_after),
            ("output_schema", output_schema),
            ("wait_s", wait_s),
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

    def retrieve(self, job_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/research/{id}`` — ``report`` / ``answer``, ``sources``, ``searches`` and ``pages_read`` once
        ``status`` is ``done``; ``error`` when ``failed``. Another account's id is a 404. Free."""
        return self._json(f"{_BASE}/{enc(job_id)}", ext=ext) or {}

    def wait(
        self,
        job_id: str,
        interval: float = 3.0,
        timeout: float = 360.0,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Poll :meth:`retrieve` every ``interval`` seconds until the job is ``done`` or ``failed`` and return it (a
        ``failed`` job is returned too — check ``status`` / ``error``). Raises ``TimeoutError`` after ``timeout``
        seconds (default 6 min; the longest job budget is 300 s)."""
        deadline = time.monotonic() + timeout
        while True:
            job = self.retrieve(job_id, ext=ext)
            if job.get("status") in RESEARCH_TERMINAL_STATUSES:
                return job
            if time.monotonic() + interval > deadline:
                raise TimeoutError(f"codai research job {job_id} did not finish within {timeout} s")
            time.sleep(interval)

    def run(
        self,
        question: str,
        interval: float = 3.0,
        timeout: float = 360.0,
        ext: Optional[RequestExtensions] = None,
        **params: Any,
    ) -> Dict[str, Any]:
        """:meth:`create` then :meth:`wait` until the job finishes. ``params`` are :meth:`create`'s keyword args."""
        job = self.create(question, ext=ext, **params)
        if job.get("status") in RESEARCH_TERMINAL_STATUSES:
            return job
        return self.wait(job["id"], interval=interval, timeout=timeout, ext=ext)
