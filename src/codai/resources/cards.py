"""``/v1/cards/*`` — server-side data for typed cards (``@codai/cards``).

Every JSON method returns ``{"block": ..., "provenance": ...}`` where ``block`` is already a valid card block (weather,
places, map, metric, table or links); :meth:`Cards.static_map` returns PNG bytes. Weather and FX are free. Places,
geocode and static maps are Google calls billed to your usage at Google's list price (Places text/nearby $0.032,
geocoding $0.005, static map $0.002) and limited per user per UTC day (200 Places, 500 maps); ``unfurl`` is free but
limited to 500 fetches per day (cache hits do not count). Maps methods raise a 503 ``CodaiError`` with code
``maps_not_configured`` when the gateway has no maps key — fall back to text.

:meth:`Cards.render` turns a ``chart`` or ``qr`` block into a PNG or SVG on the gateway (free, 2000 per day) for
surfaces that cannot draw cards; Mermaid / math blocks raise a 422 ``CodaiError`` with code ``render_unsupported``.

:meth:`Cards.route` is Google Routes travel time (billed: $0.010 traffic-aware driving, $0.005 walk/bike/transit;
maps limit). :meth:`Cards.track` follows a parcel (Sameday live; FAN Courier, Cargus, DPD only when the gateway has
their contract) and :meth:`Cards.efactura` lists your fiscal documents issued through Brivio with their ANAF e-Factura
status; both free.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Union

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["Cards", "CardsRendered", "CardsStaticMap"]


@dataclass
class CardsStaticMap:
    """A rendered static map."""

    data: bytes
    """PNG bytes."""
    content_type: str
    attribution: Optional[str]
    """``x-codai-attribution`` (``Google Maps``)."""


@dataclass
class CardsRendered:
    """A card block rendered by the gateway."""

    data: bytes
    """PNG or SVG bytes."""
    content_type: str
    """``image/png`` or ``image/svg+xml``."""
    width: Optional[int]
    """Output width in pixels (``x-codai-render-size``)."""
    height: Optional[int]


def _csv(value: Union[str, Iterable[str], None]) -> Optional[str]:
    if value is None or isinstance(value, str):
        return value or None
    return ",".join(str(v) for v in value) or None


class Cards(Resource):
    """Typed card data: ``weather``, ``places``, ``geocode``, ``static_map``, ``fx``, ``route``, ``track``,
    ``efactura``, ``unfurl``, ``product``, ``render``."""

    def weather(
        self, lat: float, lng: float, name: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/cards/weather`` — ``weather`` block from MET Norway (cached 30-60 min per 0.01°, free)."""
        return self._json("/v1/cards/weather", ext=ext, query={"lat": lat, "lng": lng, "name": name}) or {}

    def places(
        self,
        q: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        radius: Optional[int] = None,
        type: Union[str, Iterable[str], None] = None,  # noqa: A002 — mirrors the query parameter
        limit: Optional[int] = None,
        lang: Optional[str] = None,
        region: Optional[str] = None,
        open_now: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/cards/places`` — ``places`` block from Google Places: Text Search with ``q`` (biased to
        ``lat``/``lng``/``radius``), Nearby Search without it (``type`` = up to 5 Google place types). Billed per call;
        ``block`` is None when nothing matched."""
        query = {
            "q": q,
            "lat": lat,
            "lng": lng,
            "radius": radius,
            "type": _csv(type),
            "limit": limit,
            "lang": lang,
            "region": region,
            "open_now": open_now,
        }
        return self._json("/v1/cards/places", ext=ext, query=query) or {}

    def geocode(
        self,
        address: str,
        lang: Optional[str] = None,
        region: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/cards/geocode`` — ``map`` block (up to 5 markers) plus raw ``results`` (Google Geocoding, billed)."""
        query = {"address": address, "lang": lang, "region": region}
        return self._json("/v1/cards/geocode", ext=ext, query=query) or {}

    def static_map(
        self,
        center: Optional[str] = None,
        markers: Optional[str] = None,
        zoom: Optional[int] = None,
        w: Optional[int] = None,
        h: Optional[int] = None,
        maptype: Optional[str] = None,
        lang: Optional[str] = None,
        path: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> CardsStaticMap:
        """``GET /v1/cards/static-map`` — PNG from Google Maps Static proxied through the gateway (no maps key on the
        client). Needs ``center`` (``"lat,lng"``) or ``markers`` (``lat,lng[,L]`` joined by ``|``); at most 640x400
        points. Billed per call."""
        query = {
            "center": center,
            "markers": markers,
            "zoom": zoom,
            "w": w,
            "h": h,
            "maptype": maptype,
            "lang": lang,
            "path": path,
        }
        res = self._http.request("/v1/cards/static-map", query=query, ext=ext)
        return CardsStaticMap(
            data=res.data,
            content_type=res.header("content-type") or "image/png",
            attribution=res.header("x-codai-attribution"),
        )

    def fx(
        self,
        source: Optional[str] = None,
        from_: Optional[str] = None,
        to: Optional[str] = None,
        amount: Optional[float] = None,
        quote: Optional[str] = None,
        symbols: Union[str, Iterable[str], None] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/cards/fx`` — BNR (default) or ECB reference rates: a ``metric`` block with ``from_`` + ``to``,
        otherwise a ``table`` block against ``quote``, optionally limited to ``symbols``. Free. ``from_`` has a trailing
        underscore because ``from`` is a Python keyword."""
        query = {
            "source": source,
            "from": from_,
            "to": to,
            "amount": amount,
            "quote": quote,
            "symbols": _csv(symbols),
        }
        return self._json("/v1/cards/fx", ext=ext, query=query) or {}

    def route(
        self,
        from_: Optional[str] = None,
        to: Optional[str] = None,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        mode: Optional[str] = None,
        depart_at: Optional[str] = None,
        lang: Optional[str] = None,
        region: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/cards/route`` — travel time from Google Routes: ``route`` (mode, durationS, staticDurationS,
        distanceM, polyline) and a ``map`` block. ``origin``/``destination`` as ``"lat,lng"`` or ``from_``/``to`` as
        addresses; ``mode`` drive (traffic-aware, default), walk, bicycle, transit, two_wheeler. Billed per call."""
        query = {
            "from": from_,
            "to": to,
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "depart_at": depart_at,
            "lang": lang,
            "region": region,
        }
        return self._json("/v1/cards/route", ext=ext, query=query) or {}

    def track(
        self, awb: str, carrier: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/cards/track`` — parcel history as a ``timeline`` block plus ``result`` (carrier, configured,
        found, delivered, events, trackingUrl). ``carrier`` (sameday | fan | cargus | dpd) is guessed from the AWB
        when omitted; carriers without gateway credentials answer ``configured: False``. Free."""
        return self._json("/v1/cards/track", ext=ext, query={"awb": awb, "carrier": carrier}) or {}

    def efactura(self, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/cards/efactura`` — your fiscal documents issued through Brivio with their ANAF e-Factura status
        (``documents`` + a ``table`` block, None when there are none). Free."""
        return self._json("/v1/cards/efactura", ext=ext, query={"limit": limit}) or {}

    def unfurl(self, url: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/cards/unfurl`` — ``links`` block (variant ``preview``) for a public https page; SSRF-guarded,
        cached 24 h. Private targets raise 400 ``unfurl_blocked``, non-https pages 422 ``unfurl_not_https``."""
        return self._json("/v1/cards/unfurl", ext=ext, method="POST", body={"url": url}) or {}

    def product(
        self, url: str, lang: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/cards/product`` — ``products`` block with one item from a public https product page's schema.org
        ``Product`` JSON-LD (or OpenGraph product tags): name, image, price + currency (lowest offer), old price,
        rating (0-5), reviews, seller, availability badge in ``lang`` (``en`` default, or ``ro``). Only what the page
        states; never sponsored. SSRF-guarded like ``unfurl``, cached 6 h. No product data raises 422
        ``product_not_found``."""
        body: Dict[str, Any] = {"url": url}
        if lang is not None:
            body["lang"] = lang
        return self._json("/v1/cards/product", ext=ext, method="POST", body=body) or {}

    def render(
        self,
        block: Dict[str, Any],
        format: Optional[str] = None,  # noqa: A002 — mirrors the body field
        width: Optional[int] = None,
        height: Optional[int] = None,
        theme: Optional[str] = None,
        scale: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> CardsRendered:
        """``POST /v1/cards/render`` — renders a ``chart`` or ``qr`` block to ``format`` (``"png"`` default or
        ``"svg"``) at ``width`` x ``height`` CSS px (64-1200, defaults 480 x 300; QR is square) times ``scale``
        (1-3, PNG only). Other block types (Mermaid ``diagram``, ``math``, ...) raise 422 ``render_unsupported``.
        Free; 2000 renders per day."""
        body: Dict[str, Any] = {"block": block}
        for k, v in (("format", format), ("width", width), ("height", height), ("theme", theme), ("scale", scale)):
            if v is not None:
                body[k] = v
        res = self._http.request("/v1/cards/render", method="POST", body=body, ext=ext)
        size = re.match(r"^(\d+)x(\d+)$", res.header("x-codai-render-size") or "")
        return CardsRendered(
            data=res.data,
            content_type=res.header("content-type") or "image/png",
            width=int(size.group(1)) if size else None,
            height=int(size.group(2)) if size else None,
        )
