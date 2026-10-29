"""``/v1/studio/batches`` — codai Studio batches: one creative per CSV / sheet row, from a template or a creative with
variables.

:meth:`Batches.dry_run` validates the rows for free (mapping, errors, a 3-row preview); :meth:`Batches.create` stores
the batch and runs it in the background; :meth:`Batches.wait` polls :meth:`Batches.get` until it is finished. Creating
a batch is free; rows with a ``locale`` column are translated (token-metered) and ``render=True`` renders every row
(billed like any render).
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Batches"]

_BASE = "/v1/studio/batches"
_DONE = ("completed", "failed", "cancelled")


def _path(batch_id: str, tail: str = "") -> str:
    return f"{_BASE}/{enc(batch_id)}{tail}"


def _body(
    source: Dict[str, Any],
    dry_run: bool,
    csv: Optional[str],
    sheet: Optional[Dict[str, Any]],
    delimiter: Optional[str],
    mapping: Optional[Dict[str, Optional[str]]],
    title: Optional[str],
    render: Optional[bool],
    quality: Optional[str],
    format: Optional[str],  # noqa: A002 — mirrors the body field
    localize: Optional[Dict[str, Any]],
    ai_label: Optional[str] = None,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {"source": dict(source)}
    for key, value in (
        ("csv", csv),
        ("sheet", sheet),
        ("delimiter", delimiter),
        ("mapping", mapping),
        ("title", title),
        ("render", render),
        ("quality", quality),
        ("format", format),
        ("localize", localize),
        ("ai_label", ai_label),
    ):
        if value is not None:
            body[key] = value
    body["dry_run"] = dry_run
    return body


class Batches(Resource):
    """Create, validate, follow, cancel, retry, export and zip batches."""

    def create(
        self,
        source: Dict[str, Any],
        csv: Optional[str] = None,
        sheet: Optional[Dict[str, Any]] = None,
        delimiter: Optional[str] = None,
        mapping: Optional[Dict[str, Optional[str]]] = None,
        title: Optional[str] = None,
        render: Optional[bool] = None,
        quality: Optional[str] = None,
        format: Optional[str] = None,  # noqa: A002 — mirrors the body field
        localize: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
        ai_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/batches`` — ``source`` is ``{"template_id": …}`` or ``{"creative_id": …, "seq": …}``,
        plus exactly one of ``csv`` (text with a header row, ≤ 500 rows) or ``sheet`` (``{"creative_id", "node_id"?}``).
        ``mapping`` maps column → variable (``None`` ignores the column); the reserved columns ``title``, ``locale`` and
        ``format`` set the row's title, translate it and pick its format. Returns ``{batch}`` (HTTP 201); rows with
        errors are stored as ``failed``, 400 ``invalid_rows`` when every row is invalid. ``ai_label`` (``none`` |
        ``corner`` | ``end_card``, EU AI Act art. 50(4)) applies to every row render. Free."""
        body = _body(source, False, csv, sheet, delimiter, mapping, title, render, quality, format, localize, ai_label)
        return self._http.request(_BASE, body=body, ext=ext, no_retry=True).json() or {}

    def dry_run(
        self,
        source: Dict[str, Any],
        csv: Optional[str] = None,
        sheet: Optional[Dict[str, Any]] = None,
        delimiter: Optional[str] = None,
        mapping: Optional[Dict[str, Optional[str]]] = None,
        title: Optional[str] = None,
        render: Optional[bool] = None,
        quality: Optional[str] = None,
        format: Optional[str] = None,  # noqa: A002 — mirrors the body field
        localize: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
        ai_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/batches`` with ``dry_run: true`` — ``{dry_run, columns, unmapped_vars, rows, valid,
        errors, preview, estimate}``; nothing is stored. Free."""
        body = _body(source, True, csv, sheet, delimiter, mapping, title, render, quality, format, localize, ai_label)
        return self._http.request(_BASE, body=body, ext=ext).json() or {}

    def list(
        self, limit: Optional[int] = None, before: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/studio/batches`` — ``{batches, next_before}``, newest first. Free."""
        return self._json(_BASE, ext=ext, query={"limit": limit, "before": before}) or {}

    def get(
        self,
        batch_id: str,
        rows: Optional[bool] = None,
        status: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/batches/{id}`` — ``{batch, rows?}`` (``rows=True`` adds the rows; ``status``, ``offset``,
        ``limit`` ≤ 100). Every poll advances the batch a little. Free."""
        query = {"rows": rows, "status": status, "offset": offset, "limit": limit}
        return self._json(_path(batch_id), ext=ext, query=query) or {}

    def cancel(self, batch_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST …/cancel`` — the batch; rows not started become ``skipped``. 409 ``not_cancellable``. Free."""
        return self._http.request(_path(batch_id, "/cancel"), method="POST", ext=ext, no_retry=True).json() or {}

    def retry(self, batch_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST …/retry`` — queue the failed rows again (≤ 3 attempts each). 409 ``nothing_to_retry``. Free."""
        return self._http.request(_path(batch_id, "/retry"), method="POST", ext=ext, no_retry=True).json() or {}

    def export_csv(self, batch_id: str, ext: Optional[RequestExtensions] = None) -> str:
        """``GET …/export.csv`` — the original rows plus ``creative_id,status,error,render_url`` (formula-safe). Free."""
        return self._http.request(_path(batch_id, "/export.csv"), ext=ext).data.decode("utf-8")

    def zip(self, batch_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST …/zip`` — start building a ZIP of the finished renders (202, ``zip.status: "building"``; unchanged
        when already building or ready). Poll :meth:`get` until ``zip.status`` is ``ready``. 409 ``no_renders``."""
        return self._http.request(_path(batch_id, "/zip"), method="POST", ext=ext, no_retry=True).json() or {}

    def wait(
        self,
        batch_id: str,
        interval: float = 3.0,
        timeout: float = 600.0,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Poll :meth:`get` every ``interval`` seconds until the batch is ``completed``, ``failed`` or ``cancelled``
        and return it. Raises ``TimeoutError`` when it is not done within ``timeout`` seconds (default 10 min)."""
        deadline = time.monotonic() + timeout
        while True:
            batch = (self.get(batch_id, ext=ext) or {}).get("batch") or {}
            if batch.get("status") in _DONE:
                return batch
            if time.monotonic() + interval > deadline:
                raise TimeoutError(f"codai batch {batch_id} did not finish within {timeout} s")
            time.sleep(interval)
