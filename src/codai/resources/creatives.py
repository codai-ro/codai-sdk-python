"""``/v1/studio/creatives`` — codai Studio editable creative documents (ECD) with an append-only version history.

Everything except :meth:`Creatives.render`, :meth:`Creatives.comment` / :meth:`Creatives.variants` (token-metered
``codai`` calls; variants also queue draft renders) and frames beyond the daily free quota is free. ``render`` queues a
``codai-render`` (HTTP 202; poll it with ``client.renders.retrieve(render_id)``) or returns the identical existing
render (HTTP 200, ``cached: True``).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Creatives"]

_BASE = "/v1/studio/creatives"


def _path(creative_id: str, tail: str = "") -> str:
    return f"{_BASE}/{enc(creative_id)}{tail}"


class Creatives(Resource):
    """Create, read, edit (ops), version, lint, preview and render creatives (video, image, deck, doc, sheet)."""

    def list(
        self,
        kind: Optional[str] = None,
        before: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/creatives`` — ``{object: "list", data, next_before}``, most recently updated first."""
        return self._json(_BASE, ext=ext, query={"kind": kind, "before": before, "limit": limit}) or {}

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/creatives`` — ``body`` has ``kind`` (``video`` | ``image`` | ``deck`` | ``doc`` |
        ``sheet``) and optional ``title`` / ``doc`` / ``brand_kit_id`` (applies a brand kit to version 1) /
        ``template`` + ``vars`` (start from one of your templates, ``vars`` = values by var key); without ``doc`` or
        ``template`` you get an empty document for the kind. Returns
        ``{id, kind, title, head_seq, version: {seq, doc_hash}, doc}``."""
        return self._http.request(_BASE, body=body, ext=ext, no_retry=True).json() or {}

    def retrieve(
        self, creative_id: str, seq: Optional[int] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/studio/creatives/{id}`` — the document at the head (or ``seq``) with signed ``assets``."""
        return self._json(_path(creative_id), ext=ext, query={"seq": seq}) or {}

    def outline(self, creative_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET …/outline`` — compact text outline plus formats and vars (cheapest structure for a prompt)."""
        return self._json(_path(creative_id, "/outline"), ext=ext) or {}

    def find(
        self, creative_id: str, query: Union[str, Dict[str, Any]], ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST …/find`` — node ids matching a text substring or ``{text, type, sceneId, assetId, locked}``."""
        return self._http.request(_path(creative_id, "/find"), body={"query": query}, ext=ext).json() or {}

    def subtree(
        self,
        creative_id: str,
        ids: Optional[List[str]] = None,
        scene_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/subtree`` — full JSON of ``ids`` (scene ids return whole scenes) or of one ``scene_id``."""
        body: Dict[str, Any] = {}
        if ids is not None:
            body["ids"] = ids
        if scene_id is not None:
            body["sceneId"] = scene_id
        return self._http.request(_path(creative_id, "/subtree"), body=body, ext=ext).json() or {}

    def edit(
        self,
        creative_id: str,
        base_seq: int,
        ops: List[Dict[str, Any]],
        intent: Optional[str] = None,
        author: Optional[str] = None,
        force: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/ops`` — apply ``ops`` (all or nothing) authored against ``base_seq``. A stale base is rebased when
        the touched targets did not change meanwhile; otherwise ``CodaiError`` 409 ``stale`` (reload and retry).
        Rejected ops raise 400 with ``code`` ``invalid`` / ``not_found`` / ``locked`` / ``duplicate_id``."""
        body: Dict[str, Any] = {"base_seq": base_seq, "ops": ops}
        if intent is not None:
            body["intent"] = intent
        if author is not None:
            body["author"] = author
        if force is not None:
            body["force"] = force
        return self._http.request(_path(creative_id, "/ops"), body=body, ext=ext, no_retry=True).json() or {}

    def versions(
        self,
        creative_id: str,
        before_seq: Optional[int] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET …/versions`` — history, newest first (``next_before_seq`` pages)."""
        return (
            self._json(_path(creative_id, "/versions"), ext=ext, query={"before_seq": before_seq, "limit": limit})
            or {}
        )

    def revert(self, creative_id: str, seq: int, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST …/revert`` — new head whose document is version ``seq``'s (undo / redo)."""
        path = _path(creative_id, "/revert")
        return self._http.request(path, body={"seq": seq}, ext=ext, no_retry=True).json() or {}

    def fork(
        self,
        creative_id: str,
        seq: Optional[int] = None,
        title: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/fork`` — new creative from version ``seq`` (default the head)."""
        body: Dict[str, Any] = {}
        if seq is not None:
            body["seq"] = seq
        if title is not None:
            body["title"] = title
        return self._http.request(_path(creative_id, "/fork"), body=body, ext=ext, no_retry=True).json() or {}

    def delete(self, creative_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/studio/creatives/{id}`` — soft delete."""
        return self._http.request(_path(creative_id), method="DELETE", ext=ext).json() or {}

    def lint(
        self, creative_id: str, ext: Optional[RequestExtensions] = None, locale: Optional[str] = None
    ) -> Dict[str, Any]:
        """``POST …/lint`` — ``{head_seq, issues, fixable}`` (contrast, safe area, empty text, missing assets, brand
        colours, platform safe zones and text floors, alt text, missing captions, reading speed, flashing, missing /
        stale translations); issues carry ``format`` / ``fixable`` / ``locale`` (fix them with :meth:`lint_fix`).
        ``locale`` lints the translated document (adds ``text_overflow_locale``); 404 for an unknown locale."""
        path = _path(creative_id, "/lint")
        if locale is None:
            return self._http.request(path, method="POST", ext=ext).json() or {}
        return self._http.request(path, method="POST", body={"locale": locale}, ext=ext).json() or {}

    def compiled(
        self,
        creative_id: str,
        format: Optional[str] = None,  # noqa: A002 — mirrors the query parameter
        scene: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        locale: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``GET …/compiled`` — preview HTML with signed asset URLs; ``locale`` previews a translation."""
        query = {"format": format, "scene": scene, "locale": locale}
        return self._json(_path(creative_id, "/compiled"), ext=ext, query=query) or {}

    def render(
        self,
        creative_id: str,
        body: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
        locale: Optional[str] = None,
        ai_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``POST …/render`` — queue an MP4 (``codai-render``, HTTP 202, ``{render_id, cached: False, …}``); ``body``
        may have ``format``, ``quality`` (``draft`` | ``final``), ``fps`` and ``title``. Poll ``renders.retrieve``.
        When the same render already exists (same version, format, quality, fps) it is returned at once (HTTP 200,
        ``cached: True``, ``status: "succeeded"``, no new charge). ``locale`` renders a translation. ``ai_label``
        (``none`` | ``corner`` | ``end_card``, EU AI Act art. 50(4)) burns a visible AI label into the video; omitted =
        ``corner`` with TTS narration or AI images, else ``none`` (``none`` with narration: 400 ``ai_label_required``)."""
        path = _path(creative_id, "/render")
        payload: Dict[str, Any] = dict(body or {})
        if locale is not None:
            payload["locale"] = locale
        if ai_label is not None:
            payload["ai_label"] = ai_label
        return self._http.request(path, body=payload, ext=ext, no_retry=True).json() or {}

    def frame(
        self,
        creative_id: str,
        *,
        t_ms: List[int],
        format: Optional[str] = None,  # noqa: A002 — mirrors the body field
        exact: Optional[bool] = None,
        version: Optional[int] = None,
        locale: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/frame`` — PNG still frames at up to 6 times (``t_ms``). ``exact=False`` (default) screenshots
        the compiled HTML; ``exact=True`` cuts them from a draft render of the covering scenes. Waits up to ~90 s:
        ``{object: "studio.creative.frames", status: "succeeded", frames, billed_micro_usd}`` or a running job
        ``{object: "studio.creative.frame_job", status: "running", frame_job_id}`` to poll with :meth:`frame_job`.
        Cached frames are free; 60 frame jobs per UTC day are free, then billed."""
        body: Dict[str, Any] = {"t_ms": list(t_ms)}
        if format is not None:
            body["format"] = format
        if exact is not None:
            body["exact"] = exact
        if version is not None:
            body["version"] = version
        if locale is not None:
            body["locale"] = locale
        path = _path(creative_id, "/frame")
        return self._http.request(path, body=body, ext=ext, no_retry=True).json() or {}

    def comment(
        self,
        creative_id: str,
        *,
        t_ms: int,
        comment: str,
        base_seq: int,
        node_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        apply: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/comments`` — turn a comment pinned on a frame into an edit: one bounded ``codai`` model turn
        proposes ops, applied like :meth:`edit` against ``base_seq``. Returns ``{head_seq, applied_ops, summary,
        version}``; 409 ``stale`` on an overlapping change, 422 ``no_edit`` when the model made no edit,
        ``apply=False`` only proposes the ops. Token-metered like any ``codai`` text call."""
        body: Dict[str, Any] = {"t_ms": t_ms, "comment": comment, "base_seq": base_seq}
        if node_id is not None:
            body["node_id"] = node_id
        if scene_id is not None:
            body["scene_id"] = scene_id
        if apply is not None:
            body["apply"] = apply
        path = _path(creative_id, "/comments")
        return self._http.request(path, body=body, ext=ext, no_retry=True).json() or {}

    def variants(
        self,
        creative_id: str,
        *,
        base_seq: int,
        count: Optional[int] = None,
        focus: Optional[List[str]] = None,
        brief: Optional[str] = None,
        render: Optional[bool] = None,
        format: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/variants`` — A/B variants: one bounded ``codai`` model turn proposes ``count`` (default 3)
        variants changing only ``focus`` (``hook`` | ``title`` | ``cta`` | ``visual`` | ``copy``; default hook,
        title, cta); each becomes a fork at ``base_seq`` with the ops applied plus a queued draft render
        (``render=False`` to skip). Returns ``{group_id, base_seq, variants: [{creative_id, label, rationale,
        applied_ops, head_seq, render_id}]}``; 422 ``no_edit``, 504 ``timeout`` after 90 s. Token-metered."""
        body: Dict[str, Any] = {"base_seq": base_seq}
        if count is not None:
            body["count"] = count
        if focus is not None:
            body["focus"] = focus
        if brief is not None:
            body["brief"] = brief
        if render is not None:
            body["render"] = render
        if format is not None:
            body["format"] = format
        path = _path(creative_id, "/variants")
        return self._http.request(path, body=body, ext=ext, no_retry=True).json() or {}

    def list_variants(self, creative_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET …/variants`` — the latest variant group (``group_id: None`` when none) with ``status``
        (``candidate`` | ``winner`` | ``rejected``) and the stored draft render state."""
        return self._json(_path(creative_id, "/variants"), ext=ext) or {}

    def pick_variant(
        self, creative_id: str, variant_id: str, *, base_seq: int, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST …/variants/{variantId}/pick`` — apply the winner's ops to the original against ``base_seq``
        (rebased like :meth:`edit`, 409 ``stale`` on overlap) and mark the group's statuses. Returns
        ``{head_seq, version, winner, rebased}``."""
        path = _path(creative_id, f"/variants/{enc(variant_id)}/pick")
        return self._http.request(path, body={"base_seq": base_seq}, ext=ext, no_retry=True).json() or {}

    def export_fcpxml(
        self,
        creative_id: str,
        format: Optional[str] = None,
        seq: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET …/export.fcpxml`` — queue an FCPXML export of a video creative (``seq``, default the head;
        ``format``, default the first 1920×1080 / 1080×1920 / 1080×1080 format): a zip with ``project.fcpxml`` +
        per-scene MP4 segments + audio for Final Cut Pro, DaVinci Resolve or Premiere. Returns the queued export; poll
        it with ``client.exports.wait(e["id"])``. Only newly rendered seconds are billed (final render price). 400
        ``unsupported_kind`` / ``unsupported_format`` / ``too_long``."""
        path = _path(creative_id, "/export.fcpxml")
        query = {"format": format, "seq": seq}
        return self._http.request(path, query=query, ext=ext, no_retry=True).json() or {}

    def export_lottie(
        self,
        creative_id: str,
        format: Optional[str] = None,
        formats: Optional[str] = None,
        seq: Optional[int] = None,
        container: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET …/export.lottie`` — export a video creative as a Lottie animation (``seq``, default the head;
        ``format``, default the document's default format, or ``formats="all"``; ``container``: ``"json"``
        (default, Bodymovin JSON with embedded images) or ``"dotlottie"``). Free and synchronous: returns an export
        that is already ``succeeded`` with a signed ``url`` (valid 1 h) and the fidelity report in ``warnings``
        (video, chart, HTML block, table, cell grid and audio nodes are not exported). 400 ``unsupported_kind`` /
        ``invalid_request``, 413 ``too_large`` (over 20 MB)."""
        query = {"format": format, "formats": formats, "seq": seq, "container": container}
        return self._http.request(_path(creative_id, "/export.lottie"), query=query, ext=ext, no_retry=True).json() or {}

    def download_lottie(
        self,
        creative_id: str,
        format: Optional[str] = None,
        formats: Optional[str] = None,
        seq: Optional[int] = None,
        container: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET …/export.lottie?download=1`` — the Lottie file itself (nothing stored): ``application/json`` for one
        Bodymovin JSON, ``application/zip`` for a dotLottie archive or a zip of JSON files (``formats="all"``).
        Returns ``{bytes, filename, content_type}``. Same options and errors as :meth:`export_lottie`. Free."""
        query = {"format": format, "formats": formats, "seq": seq, "container": container, "download": "1"}
        res = self._http.request(_path(creative_id, "/export.lottie"), query=query, ext=ext)
        m = re.search(r'filename="([^"]+)"', res.header("content-disposition") or "", re.I)
        return {
            "bytes": bytes(res.data),
            "filename": m.group(1) if m else None,
            "content_type": res.header("content-type"),
        }

    def from_document(self, document_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/documents/{id}/creative`` — turn one of your Studio documents (deck, doc, sheet) into an
        editable creative: slides become scenes with a ``layout`` and speaker ``notes``, doc pages a ``flow`` group,
        sheets a ``cell_grid``; nodes carry a semantic ``role``. Idempotent: a document that already has a creative
        returns it with ``existing: True`` (HTTP 200; a new one is HTTP 201, ``existing: False``). Returns
        ``{id, kind, title, head_seq, version, doc, document_id, existing}``. Free. 404 unknown document, 409
        ``document_spec_missing``, 400 ``invalid_spec``, 413 ``too_large``."""
        path = f"/v1/studio/documents/{enc(document_id)}/creative"
        return self._http.request(path, method="POST", ext=ext, no_retry=True).json() or {}

    def build(
        self,
        creative_id: str,
        seq: Optional[int] = None,
        preview: Optional[bool] = None,
        filename: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/build`` — build a deck / doc / sheet creative (at ``seq``, default the head) into a PPTX / DOCX /
        XLSX, as a new version of its Studio document. Returns ``{object: "studio.creative_build", creative_id, seq,
        warnings, document}`` where ``document`` is exactly the ``POST /v1/studio/documents`` body. The file is free;
        ``preview=True`` also queues a billed preview (``document["preview"]``). 400 ``not_supported_for_kind`` (video /
        image) or ``invalid_spec``."""
        body: Dict[str, Any] = {}
        if seq is not None:
            body["seq"] = seq
        if preview is not None:
            body["preview"] = preview
        if filename is not None:
            body["filename"] = filename
        return self._http.request(_path(creative_id, "/build"), body=body, ext=ext, no_retry=True).json() or {}

    def save_template(
        self,
        creative_id: str,
        *,
        vars: List[Dict[str, Any]],
        title: Optional[str] = None,
        seq: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/template`` — save the creative (at ``seq``, default the head) as a private template. Each
        ``vars`` entry ``{"node_id", "prop": "text" | "image", "key", "label"?}`` turns a text node's text or an
        image node's asset into a variable whose default is the current value. Returns the template with ``doc``;
        400 ``node_not_found`` / ``invalid_pick`` / ``duplicate_key``. Free."""
        body: Dict[str, Any] = {"vars": vars}
        if title is not None:
            body["title"] = title
        if seq is not None:
            body["seq"] = seq
        return self._http.request(_path(creative_id, "/template"), body=body, ext=ext, no_retry=True).json() or {}

    def restyle(
        self,
        creative_id: str,
        brand_kit_id: Optional[str] = None,
        tokens: Optional[Dict[str, Any]] = None,
        base_seq: Optional[int] = None,
        snap: Optional[bool] = None,
        fonts: Optional[bool] = None,
        force: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/restyle`` — re-apply a brand kit (``brand_kit_id``) or a flat token map (``tokens``) — exactly
        one, else ``ValueError`` — as one new version: literal colours equal to the old brand become token refs,
        ``snap=True`` maps every other colour to the nearest kit colour, ``fonts`` (default true) sets heading / body
        font refs by role, locked nodes are skipped unless ``force``. ``base_seq`` defaults to the head. Returns the
        ``edit`` answer ``{seq, doc_hash, changed, warnings, rebased}``. Free."""
        if (brand_kit_id is None) == (tokens is None):
            raise ValueError("creatives.restyle: pass exactly one of brand_kit_id= or tokens=")
        body: Dict[str, Any] = {}
        for key, value in (
            ("brand_kit_id", brand_kit_id),
            ("tokens", tokens),
            ("base_seq", base_seq),
            ("snap", snap),
            ("fonts", fonts),
            ("force", force),
        ):
            if value is not None:
                body[key] = value
        return self._http.request(_path(creative_id, "/restyle"), body=body, ext=ext, no_retry=True).json() or {}

    def captions(
        self,
        creative_id: str,
        clip_id: Optional[str] = None,
        preset: Optional[str] = None,
        node_id: Optional[str] = None,
        script: Optional[str] = None,
        language: Optional[str] = None,
        retranscribe: Optional[bool] = None,
        base_seq: Optional[int] = None,
        force: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/captions`` — auto-captions: transcribe a voice clip (``clip_id``, default the first voice clip)
        word by word and add or update a captions node (``preset``: ``bold-pill`` (default) | ``clean-outline`` |
        ``karaoke-pop`` | ``minimal``) as one new version. Words are cached on the asset (free next time unless
        ``retranscribe``); ``script`` (default the narration of a codai speech asset) corrects the spelling. Returns
        the ``edit`` answer plus ``{node_id, words, cached, corrected, cost_micro_usd}`` (a fresh transcription is
        billed at the speech-to-text rate). Video only (400 ``unsupported_kind``)."""
        body: Dict[str, Any] = {}
        for key, value in (
            ("clip_id", clip_id),
            ("preset", preset),
            ("node_id", node_id),
            ("script", script),
            ("language", language),
            ("retranscribe", retranscribe),
            ("base_seq", base_seq),
            ("force", force),
        ):
            if value is not None:
                body[key] = value
        return self._http.request(_path(creative_id, "/captions"), body=body, ext=ext, no_retry=True).json() or {}

    def captions_srt(
        self,
        creative_id: str,
        node_id: Optional[str] = None,
        seq: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
        locale: Optional[str] = None,
    ) -> str:
        """``GET …/captions.srt`` — the captions as SubRip text on the document timeline (``locale``: a translation);
        404 without captions. Free."""
        query = {"node_id": node_id, "seq": seq, "locale": locale}
        res = self._http.request(_path(creative_id, "/captions.srt"), ext=ext, query=query)
        return res.data.decode("utf-8")

    def captions_vtt(
        self,
        creative_id: str,
        node_id: Optional[str] = None,
        seq: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
        locale: Optional[str] = None,
    ) -> str:
        """``GET …/captions.vtt`` — the captions as WebVTT text on the document timeline (``locale``: a translation);
        404 without captions. Free."""
        query = {"node_id": node_id, "seq": seq, "locale": locale}
        res = self._http.request(_path(creative_id, "/captions.vtt"), ext=ext, query=query)
        return res.data.decode("utf-8")

    def adapt(
        self,
        creative_id: str,
        platforms: List[str],
        focal: Optional[str] = None,
        base_seq: Optional[int] = None,
        force: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/adapt`` — one format per platform (``tiktok``, ``reels``, ``shorts``, ``feed-square``,
        ``feed-portrait``, ``youtube``) as one new version, text kept inside each platform safe zone and above its
        legible size. ``focal="vision"`` (token-metered) finds the focal point of full-bleed images and fails open;
        ``"none"`` (default) is free. Returns the ``edit`` answer plus ``{formats, focal}``."""
        body: Dict[str, Any] = {"platforms": list(platforms)}
        for key, value in (("focal", focal), ("base_seq", base_seq), ("force", force)):
            if value is not None:
                body[key] = value
        return self._http.request(_path(creative_id, "/adapt"), body=body, ext=ext, no_retry=True).json() or {}

    def lint_fix(
        self,
        creative_id: str,
        codes: Optional[List[str]] = None,
        agent: Optional[bool] = None,
        base_seq: Optional[int] = None,
        force: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/lint/fix`` — deterministic fixes (free) for ``off_brand_color``, ``text_too_small``,
        ``outside_platform_safe_zone`` and ``flashing`` (``codes`` limits them); ``agent=True`` (token-metered)
        gives the rest to one ``codai`` turn. Returns ``{seq, changed, warnings, rebased, fixed, remaining, agent}``;
        nothing to fix keeps the current ``seq`` (no new version)."""
        body: Dict[str, Any] = {}
        for key, value in (("codes", codes), ("agent", agent), ("base_seq", base_seq), ("force", force)):
            if value is not None:
                body[key] = list(value) if key == "codes" else value
        return self._http.request(_path(creative_id, "/lint/fix"), body=body, ext=ext, no_retry=True).json() or {}

    def controls(self, creative_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET …/controls`` — the tweak panel model ``{head_seq, controls: [{key, label, control, value, type,
        locked}]}``. Change values with a ``setVar`` op and controls with a ``setControl`` op (:meth:`edit`). Free."""
        return self._json(_path(creative_id, "/controls"), ext=ext) or {}

    def locales(
        self,
        creative_id: str,
        locale: Optional[str] = None,
        units: Optional[bool] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET …/locales`` — ``{head_seq, source, glossary, total, locales: [{locale, tone, translated, missing,
        stale, voice}]}``; with ``locale`` (and ``units``, default on) also ``units`` (source text, translation,
        ``by``, ``stale``, ``locked``, ``max_chars``) and ``units_total``, paged with ``offset`` / ``limit`` ≤ 500.
        Free."""
        query = {"locale": locale, "units": units, "offset": offset, "limit": limit}
        return self._json(_path(creative_id, "/locales"), ext=ext, query=query) or {}

    def localize(
        self,
        creative_id: str,
        locales: List[str],
        tone: Optional[str] = None,
        glossary: Optional[List[str]] = None,
        only_missing: Optional[bool] = None,
        voice: Optional[bool] = None,
        base_seq: Optional[int] = None,
        force: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/localize`` — translate every text into up to 10 BCP-47 ``locales`` as per-locale overrides (one
        new version, author ``agent``; token-metered ``codai`` turns). ``glossary`` terms and the brand kit name stay
        verbatim, ``tone`` (``formal`` | ``informal``) picks the address, ``only_missing`` (default on) skips fresh
        translations, ``voice=True`` (video, billed) narrates voice clips again. Returns the ``edit`` answer plus
        ``{locales: [{locale, translated, remaining, voice_clips}], cost_micro_usd}``."""
        body: Dict[str, Any] = {"locales": list(locales)}
        for key, value in (
            ("tone", tone),
            ("glossary", glossary),
            ("only_missing", only_missing),
            ("voice", voice),
            ("base_seq", base_seq),
            ("force", force),
        ):
            if value is not None:
                body[key] = list(value) if key == "glossary" else value
        return self._http.request(_path(creative_id, "/localize"), body=body, ext=ext, no_retry=True).json() or {}

    def fork_locale(
        self,
        creative_id: str,
        locale: str,
        title: Optional[str] = None,
        seq: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/locales/{locale}/fork`` — ``locale`` as a new standalone creative (translations applied,
        overrides dropped; default title ``<title> (<locale>)``). Returns the new creative plus ``locale`` and
        ``fork_of`` (HTTP 201). 404 for an unknown locale. Free."""
        body: Dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if seq is not None:
            body["seq"] = seq
        path = _path(creative_id, f"/locales/{enc(locale)}/fork")
        return self._http.request(path, body=body, ext=ext, no_retry=True).json() or {}

    def create_share(
        self,
        creative_id: str,
        kind: str,
        label: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        seq: Optional[int] = None,
        allow_remix: Optional[bool] = None,
        can_approve: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/shares`` — a public link: ``kind="view"`` (read-only preview of ``seq`` or the head;
        ``allow_remix`` default false) or ``kind="review"`` (comments by name, no account; ``can_approve`` lets the
        holder approve). ``token`` and ``url`` are returned only here (HTTP 201). 400 ``unknown_seq``; 409
        ``too_many_shares`` (20 active links). Free."""
        body: Dict[str, Any] = {"kind": kind}
        for key, value in (
            ("label", label),
            ("expires_in_days", expires_in_days),
            ("seq", seq),
            ("allow_remix", allow_remix),
            ("can_approve", can_approve),
        ):
            if value is not None:
                body[key] = value
        return self._http.request(_path(creative_id, "/shares"), body=body, ext=ext, no_retry=True).json() or {}

    def list_shares(self, creative_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET …/shares`` — ``{object: "list", data}``: active links, newest first (``url`` is always ``None``)."""
        return self._json(_path(creative_id, "/shares"), ext=ext) or {}

    def revoke_share(self, creative_id: str, share_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE …/shares/{shareId}`` — the link answers 404 from then on."""
        self._http.request(_path(creative_id, f"/shares/{enc(share_id)}"), method="DELETE", ext=ext)

    def review(self, creative_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET …/review`` — ``{status, head_seq, requested_seq, approved_seq, approved_doc_hash, approved_is_head,
        decided_by, decided_at, decision_note, threads: {open, total}}``. Free."""
        return self._json(_path(creative_id, "/review"), ext=ext) or {}

    def request_review(self, creative_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST …/review`` ``{action: "request"}`` — send the head to review (``in_review``). Free."""
        return self._http.request(_path(creative_id, "/review"), body={"action": "request"}, ext=ext).json() or {}

    def reset_review(self, creative_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST …/review`` ``{action: "reset"}`` — back to ``draft`` (decision cleared, comments kept). Free."""
        return self._http.request(_path(creative_id, "/review"), body={"action": "reset"}, ext=ext).json() or {}

    def review_threads(
        self, creative_id: str, status: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET …/review/threads`` — threads newest first (≤ 200), replies oldest first; ``status`` ``open`` |
        ``resolved`` | ``all``. Free."""
        return self._json(_path(creative_id, "/review/threads"), ext=ext, query={"status": status}) or {}

    def create_review_thread(
        self,
        creative_id: str,
        body: str,
        node_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        t_ms: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST …/review/threads`` — start a thread as the owner, optionally anchored (checked against the head:
        400 ``unknown_node`` / ``unknown_scene``; HTTP 201). 409 ``too_many_comments``. Free."""
        payload: Dict[str, Any] = {"body": body}
        for key, value in (("node_id", node_id), ("scene_id", scene_id), ("t_ms", t_ms)):
            if value is not None:
                payload[key] = value
        path = _path(creative_id, "/review/threads")
        return self._http.request(path, body=payload, ext=ext, no_retry=True).json() or {}

    def reply_review_thread(
        self, creative_id: str, thread_id: str, body: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST …/review/threads/{threadId}/replies`` — reply as the owner (HTTP 201); the whole thread. Free."""
        path = _path(creative_id, f"/review/threads/{enc(thread_id)}/replies")
        return self._http.request(path, body={"body": body}, ext=ext, no_retry=True).json() or {}

    def resolve_review_thread(
        self, creative_id: str, thread_id: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST …/review/threads/{threadId}/resolve`` — resolve a thread. Free."""
        path = _path(creative_id, f"/review/threads/{enc(thread_id)}/resolve")
        return self._http.request(path, method="POST", ext=ext).json() or {}

    def reopen_review_thread(
        self, creative_id: str, thread_id: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST …/review/threads/{threadId}/reopen`` — reopen a resolved thread. Free."""
        path = _path(creative_id, f"/review/threads/{enc(thread_id)}/reopen")
        return self._http.request(path, method="POST", ext=ext).json() or {}

    def delete_review_comment(self, creative_id: str, comment_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE …/review/comments/{commentId}`` — owner moderation (deleting a root hides the thread). Free."""
        self._http.request(_path(creative_id, f"/review/comments/{enc(comment_id)}"), method="DELETE", ext=ext)

    def frame_job(self, creative_id: str, job_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET …/frames/{jobId}`` — poll a frame job: frames when done (``status: "succeeded"``),
        ``status: "running"`` meanwhile; an unknown job raises 404."""
        return self._json(_path(creative_id, f"/frames/{enc(job_id)}"), ext=ext) or {}
