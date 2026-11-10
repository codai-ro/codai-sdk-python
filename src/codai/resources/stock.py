"""``/v1/studio/stock`` — royalty-free stock b-roll for codai Studio (SX-08): Pexels first, Pixabay as the fallback
(each only when the gateway has its key; Pixabay AI-generated items are filtered out). Searching and importing are
free (600 searches and 200 new imports per user per day).

Licence: Pexels License / Pixabay Content License — use inside a new work (commercial included), never redistribute
the raw files, never build a competing stock service, bulk-copy or train models on them. Show every item's ``credit``
(e.g. "Video by Jane Doe on Pexels", linked to ``page_url``) wherever you display it, and keep the imported asset's
``credit`` visible wherever you publish the work. ``preview_url`` / ``files[].url`` are for temporary display only.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["Stock"]


class Stock(Resource):
    """Search stock video / photos and import one as a studio asset (with its licence and credit)."""

    def search(
        self,
        q: str,
        kind: Optional[str] = None,
        orientation: Optional[str] = None,
        locale: Optional[str] = None,
        min_duration: Optional[float] = None,
        max_duration: Optional[float] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/stock/search`` — ``kind`` video | photo (default video), ``orientation`` landscape |
        portrait | square, ``locale`` en | ro, durations in seconds, ``limit`` 1-30 (default 15). Returns ``{object,
        data: [StudioStockItem], providers_tried, warnings, attribution}``. ``CodaiError`` 503 ``stock_unavailable``
        when no provider is configured, 429 ``stock_rate_limited`` when every provider is rate limited."""
        query = {
            "q": q,
            "kind": kind,
            "orientation": orientation,
            "locale": locale,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "limit": limit,
        }
        return self._http.request("/v1/studio/stock/search", query=query, ext=ext).json() or {}

    def import_(
        self,
        provider: str,
        id: str,
        kind: str,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/stock/import`` — copies one item (the variant closest to ``target_width`` ×
        ``target_height``, default 1920×1080) into your assets with its licence recorded; usable only inside your
        creatives. Returns ``{asset_id, credit, provider, provider_asset_id, licence, licence_url, source_page_url}``;
        idempotent per item. Named ``import_`` because ``import`` is a Python keyword."""
        body: Dict[str, Any] = {"provider": provider, "id": id, "kind": kind}
        if target_width is not None:
            body["target_width"] = target_width
        if target_height is not None:
            body["target_height"] = target_height
        return self._json("/v1/studio/stock/import", ext=ext, method="POST", body=body) or {}
