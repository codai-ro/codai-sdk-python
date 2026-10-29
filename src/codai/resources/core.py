"""Core endpoints: embeddings, images, audio, ephemeral tokens, models, health."""

from __future__ import annotations

import base64
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import quote

from .._http import RequestExtensions, frame_json
from ._base import Resource, list_of

__all__ = [
    "Assets",
    "Audio",
    "Documents",
    "Embeddings",
    "EmbeddingsResult",
    "EphemeralToken",
    "Health",
    "Images",
    "ImagesResult",
    "Models",
    "Music",
    "MusicResult",
    "RenderResult",
    "Renders",
    "Sfx",
    "SfxSearchResult",
    "SpeechJsonResult",
    "SpeechResult",
    "SystemOne",
    "Tokens",
    "TranscriptionResult",
    "Verify",
    "VideoResult",
    "Videos",
]


# ---------------------------------------------------------------- embeddings
@dataclass
class EmbeddingsResult:
    embeddings: List[List[float]]
    raw: Dict[str, Any]
    routed_to: Optional[str]
    fallback: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


class Embeddings(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> EmbeddingsResult:
        """``POST /v1/embeddings`` — ``body`` has ``input`` (+ optional ``model``, ``dimensions``)."""
        payload = {**body, "model": body.get("model") or "codai-embed"}
        res = self._http.request("/v1/embeddings", body=payload, ext=ext)
        raw = res.json() or {}
        return EmbeddingsResult(
            embeddings=[list(d.get("embedding") or []) for d in raw.get("data") or []],
            raw=raw,
            routed_to=res.header("x-codai-routed-to"),
            fallback=res.header("x-codai-embed-fallback"),
            headers=res.headers,
        )


# ---------------------------------------------------------------- images
@dataclass
class ImagesResult:
    images: List[bytes]
    """Decoded image bytes, one per generated image (see ``mime_types``). Keep them as returned:
    images from the EU endpoint carry C2PA credentials + SynthID, and re-encoding strips C2PA."""
    raw: Dict[str, Any]
    routed_to: Optional[str]
    cost_micro_usd: Optional[int]
    """Usage-based charge for the request in micro-USD (``x-codai-cost-micro-usd``)."""
    headers: Dict[str, str] = field(default_factory=dict)
    mime_types: List[str] = field(default_factory=list)
    """MIME type of each entry in ``images`` (usually ``image/png``)."""
    data_region: Optional[str] = None
    """Vertex location that processed the request, ``eu`` or ``global`` (``x-codai-data-region``)."""
    assets: List[Dict[str, Any]] = field(default_factory=list)
    """Stored assets with 1 h signed ``url`` (``response_format: "url"`` only; ``images`` is then empty)."""


def is_asset(item: Any) -> bool:
    """True for a ``data`` item that is a stored asset (``AssetDto``) rather than inline base64."""
    return isinstance(item, dict) and "asset_id" in item


# Image generation typically takes 5-30 s (gateway upstream timeout 120 s); never cap below this.
_MIN_IMAGE_TIMEOUT = 150.0


class Images(Resource):
    def generate(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> ImagesResult:
        """``POST /v1/images/generations`` — ``body`` has ``prompt`` (+ optional ``model`` —
        ``codai-image`` (default, gemini-3.1-flash-image, EU), ``codai-image-fast``, ``codai-image-pro`` —
        ``n``, ``size``, ``aspect_ratio``, ``image_size``, ``negative_prompt``, and ``reference_images``:
        ``[{"b64_json": ..., "mime_type": "image/png"}]`` to keep a logo/palette/product consistent; and/or
        ``reference_asset_ids``: your ready Studio image asset ids, e.g. a creative's cast, sent after
        ``reference_images`` and counted against the same per-model limit; a missing or foreign asset is 404).
        ``response_format: "url"`` stores each image as an asset and fills ``assets`` (1 h signed URLs) instead of
        ``images``. Needs a real API key; ephemeral tokens are rejected."""
        return self._post("/v1/images/generations", body, ext)

    def edit(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> ImagesResult:
        """``POST /v1/images/edits`` (JSON body) — ``body`` has ``prompt`` and ``image`` (one
        ``{"b64_json": ..., "mime_type": ...}`` or a list of up to 14), plus the same optional fields as
        :meth:`generate`. ``mask`` is not supported: describe the region to change in ``prompt``."""
        return self._post("/v1/images/edits", body, ext)

    def _post(self, path: str, body: Dict[str, Any], ext: Optional[RequestExtensions]) -> ImagesResult:
        payload = {**body, "model": body.get("model") or "codai-image"}
        client_timeout = self._http.timeout
        timeout = client_timeout if not client_timeout else max(client_timeout, _MIN_IMAGE_TIMEOUT)
        res = self._http.request(path, body=payload, ext=ext, timeout=timeout)
        raw = res.json() or {}
        cost = res.header("x-codai-cost-micro-usd")
        data = raw.get("data") or []
        return ImagesResult(
            images=[base64.b64decode(d.get("b64_json") or "") for d in data if not is_asset(d)],
            raw=raw,
            routed_to=res.header("x-codai-routed-to"),
            cost_micro_usd=int(cost) if cost is not None else None,
            headers=res.headers,
            mime_types=[d.get("mime_type") or "image/png" for d in data],
            data_region=res.header("x-codai-data-region"),
            assets=[d for d in data if is_asset(d)],
        )


# ---------------------------------------------------------------- codai Studio: music + video
@dataclass
class MusicResult:
    clips: List[bytes]
    """Decoded audio bytes (MP3 for Lyria 3, WAV for ``codai-music-legacy``), one per clip (see ``mime_types``)."""
    raw: Dict[str, Any]
    routed_to: Optional[str]
    cost_micro_usd: Optional[int]
    """Charge for the request in micro-USD (``x-codai-cost-micro-usd``)."""
    headers: Dict[str, str] = field(default_factory=dict)
    mime_types: List[str] = field(default_factory=list)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    """Stored assets with 1 h signed ``url`` (``response_format: "url"`` only; ``clips`` is then empty)."""
    tracks: List[Dict[str, Any]] = field(default_factory=list)
    """Per-item ``lyrics``, ``caption``, ``lyrics_match`` and ``warnings`` (Lyria 3), in ``data`` order."""
    warnings: List[str] = field(default_factory=list)
    """All warnings across items, deduplicated (e.g. ``lyrics_mismatch``, ``lyrics_check_unavailable``)."""


# Lyria 3 Pro can take minutes for a long song (gateway upstream timeout 240 s + lyrics check); never cap below this.
_MIN_MUSIC_TIMEOUT = 300.0


class Music(Resource):
    def generate(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> MusicResult:
        """``POST /v1/audio/music``. ``body`` has a ``prompt`` and optional ``model``: ``codai-music`` (default,
        Lyria 3 Clip, 30 s with vocals, $0.04), ``codai-music-pro`` (Lyria 3 Pro, full song up to 184 s, $0.08) or
        ``codai-music-legacy`` (Lyria 2 instrumental WAV, $0.06). Lyria 3 takes ``lyrics``, ``instrumental``,
        ``bpm`` (40-220), ``duration_seconds`` (10-184, pro only) and ``language`` (lyrics hint, e.g. ``ro``);
        non-English lyrics are best effort and come back with ``lyrics_match`` + warning ``lyrics_mismatch``.
        ``negative_prompt``, ``seed`` and ``n`` > 1 are ``codai-music-legacy`` only. ``response_format``
        ``b64_json`` (default) | ``url`` stores each clip as an asset and fills ``assets``. US-only: refused for EU
        data residency."""
        client_timeout = self._http.timeout
        timeout = client_timeout if not client_timeout else max(client_timeout, _MIN_MUSIC_TIMEOUT)
        res = self._http.request("/v1/audio/music", body=body, ext=ext, timeout=timeout)
        raw = res.json() or {}
        cost = res.header("x-codai-cost-micro-usd")
        data = raw.get("data") or []
        tracks = [
            {
                "lyrics": d.get("lyrics"),
                "caption": d.get("caption"),
                "lyrics_match": d.get("lyrics_match"),
                "warnings": list(d.get("warnings") or []),
            }
            for d in data
        ]
        warnings: List[str] = []
        for t in tracks:
            for w in t["warnings"]:
                if w not in warnings:
                    warnings.append(w)
        return MusicResult(
            clips=[base64.b64decode(d.get("b64_json") or "") for d in data if not is_asset(d)],
            raw=raw,
            routed_to=res.header("x-codai-routed-to"),
            cost_micro_usd=int(cost) if cost is not None else None,
            headers=res.headers,
            mime_types=[d.get("mime_type") or "audio/wav" for d in data],
            assets=[d for d in data if is_asset(d)],
            tracks=tracks,
            warnings=warnings,
        )


@dataclass
class VideoResult:
    video: bytes
    """Decoded MP4 bytes."""
    mime_type: str
    id: str
    seconds: Optional[int]
    raw: Dict[str, Any]
    asset: Optional[Dict[str, Any]] = None
    """The stored asset when polled with ``response_format="url"`` (``video`` is then empty)."""


class Videos(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/videos`` — starts a Veo 3.1 Fast job (HTTP 202 ``{id, status: "running", seconds,
        estimated_cost_micro_usd}``). ``body`` has an English ``prompt`` (+ optional ``negative_prompt``,
        ``seconds`` 4|6|8, ``aspect_ratio`` ``16:9``|``9:16``, ``resolution`` ``720p``|``1080p``, ``audio``,
        ``image`` ``{"b64_json", "mime_type"}``, ``seed``, ``reference_asset_ids``: up to 3 ready PNG / JPEG Studio
        image assets of ONE subject the model keeps consistent — not combinable with ``image``, always 8 s). US-only;
        nothing is charged until it succeeds."""
        return self._http.request("/v1/videos", body=body, ext=ext, no_retry=True).json() or {}

    def retrieve(
        self,
        job_id: str,
        ext: Optional[RequestExtensions] = None,
        response_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/videos/{id}`` — ``status`` is ``running``, ``succeeded`` (with ``data[0].b64_json``),
        ``failed`` or ``filtered``. Billed exactly once ($0.10 / s) on the first ``succeeded`` poll, across gateway
        instances. ``response_format="url"`` returns ``data[0]`` as a stored asset with a 1 h signed ``url``."""
        query = {"response_format": response_format} if response_format else None
        return (
            self._http.request(f"/v1/videos/{quote(job_id, safe='')}", method="GET", query=query, ext=ext).json()
            or {}
        )

    def generate(
        self,
        body: Dict[str, Any],
        poll_interval: float = 5.0,
        timeout: float = 300.0,
        ext: Optional[RequestExtensions] = None,
        response_format: Optional[str] = None,
    ) -> VideoResult:
        """Create a job and poll until it succeeds. Raises ``RuntimeError`` on ``failed``/``filtered``
        and ``TimeoutError`` when it does not finish within ``timeout`` seconds. ``response_format="url"``
        returns the stored asset in ``VideoResult.asset`` instead of the MP4 bytes."""
        job = self.create(body, ext=ext)
        job_id = job["id"]
        deadline = time.monotonic() + timeout
        while True:
            st = self.retrieve(job_id, ext=ext, response_format=response_format)
            status = st.get("status")
            if status == "succeeded":
                data = (st.get("data") or [{}])[0]
                if is_asset(data):
                    return VideoResult(
                        video=b"",
                        mime_type=data.get("mime_type") or "video/mp4",
                        id=job_id,
                        seconds=st.get("seconds") or job.get("seconds"),
                        raw=st,
                        asset=data,
                    )
                if not data.get("b64_json"):
                    raise RuntimeError(f"codai video job {job_id} succeeded without video data")
                return VideoResult(
                    video=base64.b64decode(data["b64_json"]),
                    mime_type=data.get("mime_type") or "video/mp4",
                    id=job_id,
                    seconds=st.get("seconds") or job.get("seconds"),
                    raw=st,
                )
            if status in ("failed", "filtered"):
                raise RuntimeError(f"codai video job {status}: {st.get('error') or 'no details'}")
            if time.monotonic() + poll_interval > deadline:
                raise TimeoutError(f"codai video job {job_id} did not finish within {timeout} s")
            time.sleep(poll_interval)


@dataclass
class RenderResult:
    id: str
    asset: Dict[str, Any]
    """The stored MP4 (``kind: "render"``, 1 h signed ``url``; refresh with ``assets.retrieve(id)``)."""
    raw: Dict[str, Any]
    poster_url: Optional[str] = None
    qa: Optional[Dict[str, Any]] = None
    """``{duration_seconds, width, height, lufs, warnings}`` measured on the output."""
    cost_micro_usd: Optional[int] = None


class Renders(Resource):
    """``/v1/studio/renders`` — codai Studio renders (``codai-render``): a HyperFrames HTML composition to MP4, up to
    180 s at 1080p. Studio assets are referenced in the HTML as ``asset:<asset_id>``. ``create_timeline`` renders a
    list of image/video scenes without HTML and ``regenerate_scene`` replaces one scene in a new render."""

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/renders`` — queues a render (HTTP 202 ``{id, object: "studio.render", status: "queued",
        price_micro_usd_per_second, minimum_micro_usd, ...}``). ``body`` has ``html`` (+ optional ``variables``,
        ``aspect_ratio`` ``16:9``|``9:16``|``1:1``, ``quality`` ``final``|``draft``, ``fps`` 24|25|30, ``title``,
        ``ai_label`` ``none``|``corner``|``end_card``). ``ai_label`` (EU AI Act art. 50(4)) burns a visible AI label
        into the video; omitted = ``corner`` with TTS narration or AI images, else ``none`` (``none`` with narration:
        400 ``ai_label_required``); the reply reports the resolved ``ai_label``. Nothing is charged until it succeeds."""
        return self._http.request("/v1/studio/renders", body=body, ext=ext, no_retry=True).json() or {}

    def retrieve(
        self,
        render_id: str,
        ext: Optional[RequestExtensions] = None,
        expand_assets: bool = False,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/renders/{id}`` — ``status`` is ``queued``, ``rendering`` (with ``progress`` 0..1),
        ``succeeded`` (``data[0]`` is the MP4 asset, plus ``qa``, ``poster_url``, ``cost_micro_usd``) or ``failed``
        (``error``). Billed exactly once (final $0.01 / s, min $0.05; draft half) on the first finished poll.
        Timeline renders also carry ``timeline``, ``parent_render_id`` and ``root_render_id``; ``expand_assets=True``
        (``?expand=assets``) signs the scene and narration assets."""
        query = {"expand": "assets" if expand_assets else None}
        return self._json(f"/v1/studio/renders/{quote(render_id, safe='')}", ext=ext, query=query) or {}

    def list(
        self,
        before: Optional[str] = None,
        limit: Optional[int] = None,
        root_render_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/renders`` — renders newest first, without polling and without signed URLs. Returns
        ``{object: "list", data, next_before}``; ``root_render_id`` restricts it to one timeline's version chain."""
        query = {"before": before, "limit": limit, "root_render_id": root_render_id}
        return self._json("/v1/studio/renders", ext=ext, query=query) or {}

    def create_timeline(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/timelines`` — renders ``scenes`` (``{kind: "image"|"video", asset_id, seconds?, fit?,
        video_volume?, prompt?, narration?: {text, voice?, language?}}``, 1-30, <= 180 s) with optional
        ``transition``, ``music_asset_id``/``music_volume`` and ``narration_defaults``. HTTP 202 with ``id``,
        ``root_render_id``, ``narration_cost_micro_usd`` (narration is billed now); poll with ``retrieve``."""
        return self._http.request("/v1/studio/timelines", body=body, ext=ext, no_retry=True).json() or {}

    def regenerate_scene(
        self,
        render_id: str,
        scene_id: str,
        body: Dict[str, Any],
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/renders/{id}/scenes/{scene_id}/regenerate`` — a NEW render with one scene replaced
        (``parent_render_id`` = ``render_id``). ``body`` has ``visual`` (``{asset_id}`` or ``{prompt?, model?,
        seconds?}``), ``narration`` (``{asset_id}``, ``{text?, voice?}`` or ``None`` to remove it) and/or
        ``quality``. HTTP 202 with ``scene_cost_micro_usd``; 409 ``not_a_timeline`` unless the source is a succeeded
        timeline render."""
        path = (
            f"/v1/studio/renders/{quote(render_id, safe='')}/scenes/{quote(scene_id, safe='')}/regenerate"
        )
        return self._http.request(path, body=body, ext=ext, no_retry=True).json() or {}

    def render(
        self,
        body: Dict[str, Any],
        poll_interval: float = 5.0,
        timeout: float = 900.0,
        ext: Optional[RequestExtensions] = None,
    ) -> RenderResult:
        """Queue a render and poll until it succeeds. Raises ``RuntimeError`` on ``failed`` and ``TimeoutError``
        when it does not finish within ``timeout`` seconds."""
        job = self.create(body, ext=ext)
        render_id = job["id"]
        deadline = time.monotonic() + timeout
        while True:
            st = self.retrieve(render_id, ext=ext)
            status = st.get("status")
            if status == "succeeded":
                asset = next((d for d in st.get("data") or [] if is_asset(d)), None)
                if asset is None:
                    raise RuntimeError(f"codai render {render_id} succeeded without an asset")
                cost = st.get("cost_micro_usd")
                return RenderResult(
                    id=render_id,
                    asset=asset,
                    raw=st,
                    poster_url=st.get("poster_url"),
                    qa=st.get("qa"),
                    cost_micro_usd=int(cost) if cost is not None else None,
                )
            if status == "failed":
                raise RuntimeError(f"codai render failed: {st.get('error') or 'no details'}")
            if time.monotonic() + poll_interval > deadline:
                raise TimeoutError(f"codai render {render_id} did not finish within {timeout} s")
            time.sleep(poll_interval)


# ---------------------------------------------------------------- codai Studio: stored assets
class Assets(Resource):
    """``/v1/assets`` — media generated with ``response_format: "url"`` and every finished video job. Owner-scoped
    (a foreign id is 404), kept 90 days; each ``ready`` asset carries a 1 h V4 signed ``url``."""

    def list(
        self,
        kind: Optional[str] = None,
        before: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/assets`` — newest first, ``limit`` <= 100 (default 30); ``kind`` is ``music`` | ``video`` |
        ``image`` | ``speech`` | ``render`` | ``upload`` | ``sfx``. Returns ``{object: "list", data, next_before}``; pass
        ``next_before`` as ``before`` for the next page."""
        query = {"kind": kind, "before": before, "limit": limit}
        return self._json("/v1/assets", ext=ext, query=query) or {}

    def iterate(
        self,
        kind: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Yield every asset across pages."""
        before: Optional[str] = None
        while True:
            page = self.list(kind=kind, before=before, limit=limit, ext=ext)
            yield from list_of(page, "data")
            before = page.get("next_before")
            if not before:
                return

    def retrieve(self, asset_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/assets/{id}`` — one asset with a fresh 1 h signed ``url`` (``None`` while not ``ready``)."""
        return self._json(f"/v1/assets/{quote(asset_id, safe='')}", ext=ext) or {}

    def content_url(self, asset_id: str, ext: Optional[RequestExtensions] = None) -> str:
        """A fresh signed URL of the asset's bytes (valid 1 h; needs no API key). Raises ``RuntimeError`` when the
        asset has no content yet. ``GET /v1/assets/{id}/content`` is the same URL behind an authenticated 302."""
        asset = self.retrieve(asset_id, ext=ext)
        url = asset.get("url")
        if not url:
            raise RuntimeError(f"codai asset {asset_id} has no content yet (status {asset.get('status')})")
        return str(url)

    def content_path(self, asset_id: str) -> str:
        """The authenticated redirect URL ``GET /v1/assets/{id}/content`` (302 to the signed URL)."""
        return self._http.url(f"/v1/assets/{quote(asset_id, safe='')}/content")

    def content(self, asset_id: str, ext: Optional[RequestExtensions] = None, timeout: float = 120.0) -> bytes:
        """Download the asset's bytes from its signed URL (the API key is never sent to storage)."""
        import urllib.request

        with urllib.request.urlopen(self.content_url(asset_id, ext=ext), timeout=timeout) as resp:  # noqa: S310
            return resp.read()

    def delete(self, asset_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/assets/{id}`` -> ``{id, object: "asset", deleted: True}``; issued signed URLs stop working."""
        return self._json(f"/v1/assets/{quote(asset_id, safe='')}", ext=ext, method="DELETE") or {}


# ---------------------------------------------------------------- codai Studio: sound effects
@dataclass
class SfxSearchResult:
    data: List[Dict[str, Any]]
    """``SfxDto`` items: ``sfx_id``, ``name``, ``category``, ``tags``, ``duration_seconds``, ``mime_type``,
    ``license`` (always ``CC0-1.0``), ``source``, ``preview_url``."""
    source: str
    """``library`` or ``library+freesound``."""
    fallback_unavailable: bool
    """True when the Freesound fallback was needed but failed (``x-codai-sfx-fallback: unavailable``)."""
    raw: Dict[str, Any]


class Sfx(Resource):
    """``/v1/studio/sfx`` — the codai Studio sound-effects library (``codai-sfx``): curated CC0 sounds (Kenney packs)
    plus a Freesound CC0-only fallback. Searching and importing are free; an imported sound is a studio asset
    (``kind: "sfx"``) usable as ``asset:<asset_id>`` in ``renders.create``."""

    def search(
        self,
        q: Optional[str] = None,
        category: Optional[str] = None,
        tags: Any = None,
        max_duration: Optional[float] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> SfxSearchResult:
        """``GET /v1/studio/sfx`` — best match first. ``category`` is one of ``impact``, ``whoosh``, ``ui``,
        ``notification``, ``transition``, ``ambience``, ``foley``, ``scifi``, ``cartoon``, ``nature``, ``crowd``,
        ``other``; ``tags`` is a comma-separated string or a list (any match); ``max_duration`` in seconds;
        ``limit`` 1-50 (default 20)."""
        if isinstance(tags, (list, tuple)):
            tags = ",".join(str(t) for t in tags) or None
        query = {"q": q, "category": category, "tags": tags, "max_duration": max_duration, "limit": limit}
        res = self._http.request("/v1/studio/sfx", query=query, ext=ext)
        raw = res.json() or {}
        return SfxSearchResult(
            data=list_of(raw, "data"),
            source=str(raw.get("source") or "library"),
            fallback_unavailable=res.header("x-codai-sfx-fallback") == "unavailable",
            raw=raw,
        )

    def import_(self, sfx_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/sfx/{sfx_id}/import`` — copies the sound into your assets and returns the ``AssetDto``
        (``kind: "sfx"``, ``model: "codai-sfx"``, free). Named ``import_`` because ``import`` is a Python keyword.
        Raises ``CodaiError`` 400 ``license_not_allowed`` for a non-CC0 Freesound sound and 404 for an unknown id."""
        return self._json(f"/v1/studio/sfx/{quote(sfx_id, safe='')}/import", ext=ext, method="POST") or {}


# ---------------------------------------------------------------- codai Studio: documents
class Documents(Resource):
    """``/v1/studio/documents`` — codai Studio documents (``codai-docs``): a deck (PPTX), doc (DOCX) or sheet (XLSX)
    built synchronously from a JSON ``spec`` (free, asset ``kind: "document"``), LibreOffice previews
    (``codai-docs-preview``: tagged PDF + page PNGs + contact sheet, $0.002 / page, min $0.01) and deck -> MP4
    slideshows queued as a ``codai-render`` render. Served in the EU."""

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/documents`` — ``body`` has ``type`` (``deck`` | ``doc`` | ``sheet``) and a ``spec`` that
        matches it (+ optional ``theme`` ``codai-light`` | ``codai-dark`` | ``corporate``, ``title``, ``language``,
        ``filename``, ``based_on`` (next version of one of your documents), ``preview`` (also queue a billed preview)).
        Returns ``{id, object: "studio.document", type, version, warnings, file: AssetDto, preview, ...}``; an invalid
        spec raises ``CodaiError`` 400 ``invalid_spec``."""
        return self._http.request("/v1/studio/documents", body=body, ext=ext, no_retry=True).json() or {}

    def retrieve(self, document_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/documents/{id}`` — the document with a fresh 1 h signed ``file.url``, the stored ``spec``
        (edit it and send it back with ``based_on``) and ``latest_preview_id``."""
        return self._json(f"/v1/studio/documents/{quote(document_id, safe='')}", ext=ext) or {}

    def preview(
        self,
        document_id: str,
        body: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/documents/{id}/previews`` — queues a preview (HTTP 202 ``{id, object: "studio.preview",
        status: "queued", price_micro_usd_per_page, minimum_micro_usd}``). At most 3 active previews per user (429
        ``too_many_previews``); billed once on the first poll that sees the result."""
        path = f"/v1/studio/documents/{quote(document_id, safe='')}/previews"
        return self._http.request(path, body=body or {}, ext=ext, no_retry=True).json() or {}

    def retrieve_preview(self, preview_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/previews/{id}`` — ``status`` is ``queued``, ``rendering``, ``succeeded`` (``pdf`` asset,
        ``pages`` with signed PNG URLs, ``contact_sheet_url``, ``page_count``, ``cost_micro_usd``) or ``failed``
        (``error``)."""
        return self._json(f"/v1/studio/previews/{quote(preview_id, safe='')}", ext=ext) or {}

    def video(
        self,
        document_id: str,
        body: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/documents/{id}/video`` — decks only (400 ``not_a_deck``). ``body`` may have ``quality``
        ``final`` | ``draft``, ``seconds_per_slide`` (2-20), ``transition`` ``fade`` | ``none``, ``music_asset_id`` and
        ``narrate`` ``{model, voice, language, instructions}`` (synthesized and billed now). Returns a queued render
        (HTTP 202, plus ``preview_id``, ``narration_cost_micro_usd``, ``slides``, ``duration_seconds``); poll it with
        ``renders.retrieve`` or use :meth:`video_and_wait`."""
        path = f"/v1/studio/documents/{quote(document_id, safe='')}/video"
        return self._http.request(path, body=body or {}, ext=ext, no_retry=True).json() or {}

    def create_preview_and_wait(
        self,
        document_id: str,
        poll_interval: float = 3.0,
        timeout: float = 300.0,
        body: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Queue a preview and poll until it succeeds; returns the succeeded preview. Raises ``RuntimeError`` on
        ``failed`` and ``TimeoutError`` when it does not finish within ``timeout`` seconds."""
        job = self.preview(document_id, body=body, ext=ext)
        preview_id = job["id"]
        deadline = time.monotonic() + timeout
        while True:
            st = self.retrieve_preview(preview_id, ext=ext)
            status = st.get("status")
            if status == "succeeded":
                return st
            if status == "failed":
                raise RuntimeError(f"codai document preview failed: {st.get('error') or 'no details'}")
            if time.monotonic() + poll_interval > deadline:
                raise TimeoutError(f"codai document preview {preview_id} did not finish within {timeout} s")
            time.sleep(poll_interval)

    def video_and_wait(
        self,
        document_id: str,
        body: Optional[Dict[str, Any]] = None,
        poll_interval: float = 5.0,
        timeout: float = 900.0,
        ext: Optional[RequestExtensions] = None,
    ) -> RenderResult:
        """Queue a deck video and poll ``GET /v1/studio/renders/{id}`` until the MP4 is ready. Raises
        ``RuntimeError`` on ``failed`` (e.g. ``preview_failed``) and ``TimeoutError`` after ``timeout`` seconds."""
        accepted = self.video(document_id, body=body, ext=ext)
        render_id = accepted["id"]
        renders = Renders(self._http)
        deadline = time.monotonic() + timeout
        while True:
            st = renders.retrieve(render_id, ext=ext)
            status = st.get("status")
            if status == "succeeded":
                asset = next((d for d in st.get("data") or [] if is_asset(d)), None)
                if asset is None:
                    raise RuntimeError(f"codai render {render_id} succeeded without an asset")
                cost = st.get("cost_micro_usd")
                return RenderResult(
                    id=render_id,
                    asset=asset,
                    raw=st,
                    poster_url=st.get("poster_url"),
                    qa=st.get("qa"),
                    cost_micro_usd=int(cost) if cost is not None else None,
                )
            if status == "failed":
                raise RuntimeError(f"codai deck video failed: {st.get('error') or 'no details'}")
            if time.monotonic() + poll_interval > deadline:
                raise TimeoutError(f"codai deck video {render_id} did not finish within {timeout} s")
            time.sleep(poll_interval)


# ---------------------------------------------------------------- system one
class SystemOne(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/systemone`` — typed decisions from codai-s1.

        ``body`` = ``{"state": ..., "questions": {id: {"type": "choice"|"score"|"noul", ...}}}``, or
        ``{"items": [{"id", "state"}], "questions": ...}`` for a batch (1-16 items → ``items[]``).
        Optional ``timeout_ms`` (100-5000) and ``fallback`` (``"codai-fast"``). Raises ``CodaiError``
        on 503 ``s1_unavailable``; keep a local fallback — the gateway substitutes a generative model
        only when ``fallback="codai-fast"`` is sent, and then the response has ``fallback_used: True``.
        """
        return self._http.request("/v1/systemone", body=body, ext=ext).json() or {}

    def batch(
        self,
        items: List[Dict[str, Any]],
        questions: Dict[str, Any],
        timeout_ms: Optional[int] = None,
        fallback: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Same ``questions`` about up to 16 ``items`` (``[{"id", "state"}]``); returns ``{"items": [{"id", "answers"}], ...}``."""
        body: Dict[str, Any] = {"items": items, "questions": questions}
        if timeout_ms is not None:
            body["timeout_ms"] = timeout_ms
        if fallback is not None:
            body["fallback"] = fallback
        return self.create(body, ext)


# --------------------------------------------------------------------- audio
@dataclass
class TranscriptionResult:
    text: str
    raw: Dict[str, Any]
    routed_to: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class SpeechResult:
    audio: bytes
    content_type: str
    routed_to: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class SpeechJsonResult:
    audio: bytes
    """Decoded audio bytes (empty with ``store: True`` — use ``asset["url"]``)."""
    words: Optional[List[Dict[str, Any]]]
    """``[{"word", "start", "end"}]`` in seconds; ``None`` when not requested or the timing pass failed."""
    asset: Optional[Dict[str, Any]]
    """Stored studio asset (``store: True``), referenceable as ``asset:<asset_id>`` in renders."""
    duration_seconds: Optional[float]
    cost_micro_usd: Optional[int]
    """Upstream cost of the request in micro-USD."""
    timestamps_unavailable: bool
    """True when the gateway answered ``x-codai-timestamps: unavailable``."""
    raw: Dict[str, Any]
    routed_to: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


def _multipart(fields: Dict[str, str], file_field: str, filename: str, file_bytes: bytes) -> "tuple[bytes, str]":
    boundary = f"----codai{int(time.time() * 1000)}"
    parts: List[bytes] = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    parts.append(
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; '
            f'filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'
        ).encode()
    )
    parts.append(file_bytes)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


class Audio(Resource):
    def transcribe(
        self,
        file: bytes,
        filename: str = "audio.webm",
        model: str = "codai-transcribe",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[float] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> str:
        """Speech-to-text (multipart, max 25 MB, never retried). Returns the transcript."""
        return self.transcribe_detailed(
            file, filename, model, language, prompt, response_format, temperature, ext
        ).text

    def transcribe_detailed(
        self,
        file: bytes,
        filename: str = "audio.webm",
        model: str = "codai-transcribe",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[float] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> TranscriptionResult:
        fields: Dict[str, str] = {"model": model}
        if language:
            fields["language"] = language
        if prompt:
            fields["prompt"] = prompt
        if response_format:
            fields["response_format"] = response_format
        if temperature is not None:
            fields["temperature"] = str(temperature)
        payload, content_type = _multipart(fields, "file", filename, file)
        res = self._http.request(
            "/v1/audio/transcriptions", method="POST", raw_body=payload, content_type=content_type, ext=ext
        )
        raw = res.json() or {}
        text = raw.get("text")
        return TranscriptionResult(
            text=text if isinstance(text, str) else "",
            raw=raw,
            routed_to=res.header("x-codai-routed-to"),
            headers=res.headers,
        )

    def speech(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> bytes:
        """Text-to-speech. ``body`` has ``input`` (+ ``model``, ``voice``, ``response_format``…). Returns audio bytes."""
        return self.speech_detailed(body, ext).audio

    def speech_detailed(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> SpeechResult:
        model = body.get("model") or "codai-tts"
        payload = {**body, "model": model}
        # codai-speech* pick their own default voice (Aoede / Kore); ``alloy`` is an Azure voice name.
        if body.get("voice") or not model.startswith("codai-speech"):
            payload["voice"] = body.get("voice") or "alloy"
        res = self._http.request("/v1/audio/speech", body=payload, ext=ext)
        return SpeechResult(
            audio=res.data,
            content_type=res.header("content-type") or "audio/mpeg",
            routed_to=res.header("x-codai-routed-to"),
            headers=res.headers,
        )

    def speech_json(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> SpeechJsonResult:
        """Text-to-speech with JSON output: per-word timings (``timestamps``, default ``True`` here unless only
        ``store`` is set) and/or a stored studio asset (``store``). Works for every speech model; ``codai-speech``
        (Chirp 3 HD) and ``codai-speech-expressive`` (Gemini TTS, honours ``instructions``) speak Romanian natively
        (``language``, default ``ro-RO``). Defaults to ``codai-speech``."""
        payload = {**body, "model": body.get("model") or "codai-speech"}
        if "timestamps" not in body and not body.get("store"):
            payload["timestamps"] = True
        res = self._http.request("/v1/audio/speech", body=payload, ext=ext)
        raw = res.json() or {}
        cost = raw.get("cost_micro_usd")
        if cost is None:
            cost = res.header("x-codai-cost-micro-usd")
        b64 = raw.get("b64_json")
        words = raw.get("words")
        return SpeechJsonResult(
            audio=base64.b64decode(b64) if b64 else b"",
            words=list(words) if isinstance(words, list) else None,
            asset=raw.get("asset"),
            duration_seconds=raw.get("duration_seconds"),
            cost_micro_usd=int(cost) if cost is not None else None,
            timestamps_unavailable=res.header("x-codai-timestamps") == "unavailable",
            raw=raw,
            routed_to=res.header("x-codai-routed-to"),
            headers=res.headers,
        )

    def speech_stream(
        self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None
    ) -> Iterator[Dict[str, Any]]:
        """``POST /v1/audio/speech/stream`` — Azure neural TTS (``codai-tts-ro``) with lip-sync timing.

        ``body`` has ``input`` (+ ``voice``: ``alina`` (default) | ``emil`` | any Azure voice name,
        ``response_format``: ``pcm`` (default, PCM16 mono 24 kHz) | ``mp3``, ``speed`` 0.5-2.0).
        Yields ``{"type": "start"|"audio"|"viseme"|"word"|"done"|"error", ...}``; ``audio`` events
        also carry ``audio_bytes`` (the decoded ``delta``). Stops after ``done`` / ``error``.
        """
        payload = {**body, "model": body.get("model") or "codai-tts-ro"}
        for frame in self._http.sse("/v1/audio/speech/stream", method="POST", body=payload, ext=ext):
            data = frame_json(frame)
            if not isinstance(data, dict) or not isinstance(data.get("type"), str):
                continue
            if data["type"] == "audio" and isinstance(data.get("delta"), str):
                data["audio_bytes"] = base64.b64decode(data["delta"])
            yield data
            if data["type"] in ("done", "error"):
                return


# -------------------------------------------------------------------- tokens
@dataclass
class EphemeralToken:
    token: str
    expires_at: str
    scope: str
    raw: Dict[str, Any]


class Tokens(Resource):
    def create(
        self, scope: str, ttl_seconds: Optional[int] = None, ext: Optional[RequestExtensions] = None
    ) -> EphemeralToken:
        """``POST /v1/tokens`` — mint a 60–3600 s token bound to ``realtime`` | ``audio`` | ``embeddings``
        | ``live`` (realtime + audio in one token, for a live co-host's STT and TTS)."""
        body: Dict[str, Any] = {"scope": scope}
        if ttl_seconds is not None:
            body["ttl_seconds"] = ttl_seconds
        raw = self._json("/v1/tokens", ext=ext, body=body) or {}
        return EphemeralToken(
            token=str(raw.get("token") or ""),
            expires_at=str(raw.get("expires_at") or ""),
            scope=str(raw.get("scope") or scope),
            raw=raw,
        )


# -------------------------------------------------------------------- models
class Models(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/models`` — every model the calling key may address (``data[]``)."""
        return list_of(self._json("/v1/models", ext=ext), "data")


# -------------------------------------------------------------------- health
class Health(Resource):
    def get(self) -> Dict[str, Any]:
        """``GET /health`` — liveness."""
        return self._http.json("/health", no_retry=True)

    def ready(self) -> Dict[str, Any]:
        """``GET /health/ready`` — readiness; 503 is returned as a body with ``http_status``."""
        res = self._http.request("/health/ready", no_retry=True, accept_status=(503,))
        body = res.json() or {}
        body["http_status"] = res.status
        return body

    def status(self) -> Dict[str, Any]:
        """``GET /status`` — public provider status."""
        return self._http.json("/status", no_retry=True)


# ------------------------------------------------------------------- verify
class Verify(Resource):
    """EXPERIMENTAL, unaudited (HIDE protocol) verification of signed agent outputs.

    Provenance only, never authentication. Both endpoints are unauthenticated.
    """

    def agent_output_key(self) -> Dict[str, Any]:
        """``GET /v1/verify/agent-output/key`` — ``{"enabled": False, ...}`` when signing is off."""
        return self._http.json("/v1/verify/agent-output/key")

    def agent_output(self, payload: Dict[str, Any], signature: Dict[str, Any]) -> Dict[str, Any]:
        """``POST /v1/verify/agent-output`` — ``{"valid", "key_id", "reason"?}``; 503 ``signing_disabled``."""
        return self._http.json(
            "/v1/verify/agent-output",
            method="POST",
            body={"payload": payload, "signature": signature},
            no_retry=True,
        )
