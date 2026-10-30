"""``/v1/studio/brand-kits`` — codai Studio brand kits: reusable brand tokens (5 colour roles + extras, 2 fonts,
optional radius) stored as a Design Tokens (DTCG 2025.10) document, plus a logo.

:meth:`BrandKits.extract` is token-metered (one bounded ``codai`` model call, from a web page or a logo image);
creating, editing, exporting, listing, reading and deleting are free. Apply a kit when creating a creative
(``client.creatives.create({"kind": "video", "brand_kit_id": kit_id})``), re-apply it to an existing creative with
``client.creatives.restyle(creative_id, brand_kit_id=kit_id)``, or set tokens directly with a ``setBrand`` op.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["BrandKits"]

_BASE = "/v1/studio/brand-kits"


class _Unset:
    def __repr__(self) -> str:
        return "UNSET"


_UNSET: Any = _Unset()


class BrandKits(Resource):
    """Create, edit, export (DTCG), extract, list, read and delete brand kits."""

    def create(
        self,
        name: str,
        *,
        tokens: Optional[Dict[str, Any]] = None,
        dtcg: Optional[Dict[str, Any]] = None,
        logo_asset_id: Optional[str] = None,
        source_url: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/brand-kits`` — save a kit you define: flat ``tokens`` (the 5 colours ``#rrggbb``,
        optional ``headingFont`` / ``bodyFont``) or a DTCG document in ``dtcg`` (import) — exactly one (else
        ``ValueError``). 400 ``invalid_tokens`` (``details.issues``) for an invalid DTCG document, 404 when
        ``logo_asset_id`` is not one of your ready image assets. Free."""
        if (tokens is None) == (dtcg is None):
            raise ValueError("brand_kits.create: pass exactly one of tokens= or dtcg=")
        body: Dict[str, Any] = {"name": name}
        if tokens is not None:
            body["tokens"] = tokens
        if dtcg is not None:
            body["dtcg"] = dtcg
        if logo_asset_id is not None:
            body["logo_asset_id"] = logo_asset_id
        if source_url is not None:
            body["source_url"] = source_url
        return self._http.request(_BASE, body=body, ext=ext, no_retry=True).json() or {}

    def update(
        self,
        kit_id: str,
        *,
        name: Optional[str] = None,
        tokens: Optional[Dict[str, Any]] = None,
        dtcg: Optional[Dict[str, Any]] = None,
        logo_asset_id: Any = _UNSET,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PATCH /v1/studio/brand-kits/{id}`` — ``tokens`` (partial) is merged onto the current kit, ``dtcg``
        replaces the whole document (not both, else ``ValueError``); ``logo_asset_id=None`` removes the logo, leaving
        it out keeps it. At least one field. Creatives keep their tokens until ``creatives.restyle``. Free."""
        if tokens is not None and dtcg is not None:
            raise ValueError("brand_kits.update: pass tokens= or dtcg=, not both")
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if tokens is not None:
            body["tokens"] = tokens
        if dtcg is not None:
            body["dtcg"] = dtcg
        if logo_asset_id is not _UNSET:
            body["logo_asset_id"] = logo_asset_id
        if not body:
            raise ValueError("brand_kits.update: nothing to change")
        return (
            self._http.request(f"{_BASE}/{enc(kit_id)}", method="PATCH", body=body, ext=ext, no_retry=True).json()
            or {}
        )

    def export_dtcg(self, kit_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/brand-kits/{id}/dtcg`` — the kit as a DTCG 2025.10 JSON document
        (``$extensions["ro.codai"]`` = ``{kit_id, name, logo_asset_id}``). Free."""
        return self._json(f"{_BASE}/{enc(kit_id)}/dtcg", ext=ext) or {}

    def extract(
        self,
        url: Optional[str] = None,
        name: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        *,
        logo_asset_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/brand-kits/extract`` — from a public ``https`` page (``url``: palette + fonts, the logo is
        stored as an ``image`` asset) or from one of your logo images (``logo_asset_id``: PNG / JPEG / WebP up to 5 MB,
        one vision turn; it becomes the kit logo). Exactly one of the two (else ``ValueError``). 400 ``url_blocked`` /
        ``unsupported_media``, 422 ``fetch_failed`` / ``extract_failed``, 504 ``timeout`` after 60 s. Token-metered."""
        if (url is None) == (logo_asset_id is None):
            raise ValueError("brand_kits.extract: pass exactly one of url= or logo_asset_id=")
        body: Dict[str, Any] = {"url": url} if url is not None else {"logo_asset_id": logo_asset_id}
        if name is not None:
            body["name"] = name
        return self._http.request(f"{_BASE}/extract", body=body, ext=ext, no_retry=True).json() or {}

    def list(self, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/brand-kits`` — ``{object: "list", data}``, newest first."""
        return self._json(_BASE, ext=ext, query={"limit": limit}) or {}

    def retrieve(self, kit_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/brand-kits/{id}`` — one kit with a signed logo URL (1 h), ``dtcg`` and ``contrast``."""
        return self._json(f"{_BASE}/{enc(kit_id)}", ext=ext) or {}

    def delete(self, kit_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/studio/brand-kits/{id}`` — soft delete (creatives keep their tokens; the logo asset stays)."""
        return self._http.request(f"{_BASE}/{enc(kit_id)}", method="DELETE", ext=ext).json() or {}
