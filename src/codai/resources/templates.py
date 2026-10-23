"""``/v1/studio/templates`` — codai Studio templates: private, reusable creative documents with variables, saved from
your own creatives with :meth:`codai.resources.creatives.Creatives.save_template`.

Create a creative from one with ``client.creatives.create({"kind": "video", "template": tpl_id, "vars": {...}})``.
Everything here is free.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Templates"]

_BASE = "/v1/studio/templates"


class Templates(Resource):
    """List, read and delete creative templates."""

    def list(
        self,
        kind: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
        *,
        source: Optional[str] = None,
        locale: Optional[str] = None,
        month: Optional[int] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/templates`` — ``{object: "list", data}`` without ``doc``: your templates (newest first), then
        the 40 built-in starters (``source: "starter"``, ids ``starter:<slug>:<en|ro>``) in ``locale`` (``en`` / ``ro``),
        in-season (``month`` 1-12) first. ``source``: ``own`` | ``starter`` | ``all`` (default). A starter id works
        anywhere a template id does; starters cannot be deleted."""
        query = {"kind": kind, "limit": limit, "source": source, "locale": locale, "month": month}
        return self._json(_BASE, ext=ext, query=query) or {}

    def retrieve(self, template_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/templates/{id}`` — one template with ``vars_schema`` and ``doc``."""
        return self._json(f"{_BASE}/{enc(template_id)}", ext=ext) or {}

    def delete(self, template_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/studio/templates/{id}`` — soft delete (creatives made from it are not affected)."""
        return self._http.request(f"{_BASE}/{enc(template_id)}", method="DELETE", ext=ext).json() or {}
