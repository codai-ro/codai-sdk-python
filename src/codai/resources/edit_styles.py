"""``/v1/studio/edit-styles`` — codai Studio edit styles (SX-44): named cut settings (pacing, captions, zoom, b-roll
density and sources, reframe speed) applied to a finished cut with
``client.productions.restyle_cut(production_id, style)``.

The 6 built-ins (``podcast-clip``, ``talking-head``, ``tutorial``, ``fast-social``, ``cinematic``, ``minimal``) come
with :meth:`EditStyles.list`; you can save up to 50 private styles, share one to the public gallery (codai reviews it
first; only the name, description and settings are shared, with your username), copy gallery styles and report one
that breaks the rules. Everything here is free.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["EditStyles"]

_BASE = "/v1/studio/edit-styles"


def _path(style_id: int, tail: str = "") -> str:
    return f"{_BASE}/{int(style_id)}{tail}"


class EditStyles(Resource):
    """List, save, edit, delete, share, browse, copy, report and moderate edit styles."""

    def list(
        self,
        lang: Optional[str] = None,
        gallery: bool = False,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/edit-styles`` — ``{builtin, styles}`` (built-in names in ``lang``: en | ro) and, with
        ``gallery=True``, the first gallery page under ``gallery``."""
        query: Dict[str, Any] = {}
        if lang is not None:
            query["lang"] = lang
        if gallery:
            query["gallery"] = "1"
        return self._json(_BASE, ext=ext, query=query or None) or {}

    def create(
        self,
        name: str,
        knobs: Dict[str, Any],
        description: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/edit-styles`` — save a private style (``knobs``: ``pacing``, ``captions``, ``zoom``,
        ``broll``, ``reframe``). ``CodaiError`` 409 ``too_many_styles`` at 50."""
        body: Dict[str, Any] = {"name": name, "knobs": knobs}
        if description is not None:
            body["description"] = description
        return self._json(_BASE, ext=ext, method="POST", body=body, no_retry=True) or {}

    def update(
        self,
        style_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        knobs: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PATCH /v1/studio/edit-styles/{id}`` — change one of your styles (at least one field, else
        ``ValueError``). Any edit makes the style private again (it leaves the gallery)."""
        body: Dict[str, Any] = {}
        for k, v in (("name", name), ("description", description), ("knobs", knobs)):
            if v is not None:
                body[k] = v
        if not body:
            raise ValueError("edit_styles.update: nothing to change")
        return self._json(_path(style_id), ext=ext, method="PATCH", body=body, no_retry=True) or {}

    def delete(self, style_id: int, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/studio/edit-styles/{id}`` — delete one of your styles."""
        return self._json(_path(style_id), ext=ext, method="DELETE") or {}

    def submit(self, style_id: int, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/edit-styles/{id}/submit`` — share to the gallery: status ``pending`` until codai reviews
        it. 10 per day (429); 409 ``style_removed`` for a style removed from the gallery."""
        return self._json(_path(style_id, "/submit"), ext=ext, method="POST", no_retry=True) or {}

    def gallery(
        self,
        limit: Optional[int] = None,
        cursor: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/edit-styles/gallery`` — approved styles, newest first (``limit`` 1-48, default 24;
        ``cursor`` = the previous ``next_cursor``)."""
        query: Dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if cursor is not None:
            query["cursor"] = cursor
        return self._json(f"{_BASE}/gallery", ext=ext, query=query or None) or {}

    def copy(self, style_id: int, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/edit-styles/{id}/copy`` — a private copy of a gallery style (``copied_from`` = source)."""
        return self._json(_path(style_id, "/copy"), ext=ext, method="POST", no_retry=True) or {}

    def report(
        self,
        style_id: int,
        reason: str,
        details: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/edit-styles/{id}/report`` — ``reason``: spam | harassment | hate | sexual | violence |
        illegal | ip | other. Returns ``{created, hidden}``; one report per user and style."""
        body: Dict[str, Any] = {"reason": reason}
        if details is not None:
            body["details"] = details
        return self._json(_path(style_id, "/report"), ext=ext, method="POST", body=body, no_retry=True) or {}

    def moderation_queue(self, status: Optional[str] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/edit-styles/moderation`` — super_admin: styles in one status (default ``pending``)."""
        query = {"status": status} if status is not None else None
        return self._json(f"{_BASE}/moderation", ext=ext, query=query) or {}

    def moderate(self, style_id: int, action: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/edit-styles/{id}/moderate`` — super_admin: ``approve`` | ``reject`` | ``remove``."""
        return (
            self._json(_path(style_id, "/moderate"), ext=ext, method="POST", body={"action": action}, no_retry=True)
            or {}
        )
