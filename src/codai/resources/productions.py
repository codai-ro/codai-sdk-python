"""``/v1/studio/productions`` — codai Studio brief → finished output (RC-20), one of 8 kinds (``kind``, default
``video``): ``video`` (MP4 render), ``image`` (PNG), ``deck`` (PPTX), ``doc`` (DOCX), ``sheet`` (XLSX), ``carousel``
(ZIP of PNG slides + cover PNG), ``print`` (A4/A5 PDF) and ``audio`` (MP3 jingle or song).

``video``: one model turn storyboards the brief on a built-in video starter, every scene gets an image and a voice-over
line, the result is saved as an editable creative and a draft render is queued; a vision review may fix text once.
Other kinds: one plan turn, generated images or music, an editable creative and the output built by the Studio
builders; the response adds ``kind``, ``output_asset_id`` and ``outputs`` (Studio assets with a ``role``).
``starter``, ``voice``, ``narration`` and ``aspect_ratio`` apply to ``video`` only.

``create`` returns 202 ``{id, status: "running", phase}`` after the output is queued (about a minute), ``retrieve``
advances and reads it, ``wait`` polls until ``succeeded`` / ``failed`` and ``run`` does ``create`` + ``wait``. The
plan and review turns are token-metered; images, music, voice-over and renders are billed at their usual prices;
``budget_micro_usd`` (default 3,000,000 = $3) caps the whole production.

``kind="cut"`` (SX-08, :meth:`Productions.create_cut`): your uploads (``asset_ids``: video, audio, photos) become an
edited video — ingest → music → plan → broll → assemble → render. :meth:`Productions.cut` reads the explain-the-edit
log (decisions with reasons, take clusters, script gaps, stats) and :meth:`Productions.revise_cut` re-assembles a
finished cut with toggled decisions / takes / pacing / captions into a new creative version (free). Ingest of
not-yet-ingested sources is billed on each asset (``ingest_quote_micro_usd``).

:meth:`Productions.restyle_cut` (SX-44) applies an edit style (``client.edit_styles``) to a finished cut: the knobs
are written at once and free; extra b-roll is fetched by a background job (``broll_job``, poll it with
:meth:`Productions.retrieve`), where only generated images are billed, at cost.

:meth:`Productions.cut_variants` (SX-42) proposes alternative edits of a finished cut scored 0-99 on Hook / Flow /
Value / Fit (two token-metered turns; ``judge=False`` = one), :meth:`Productions.retrieve_cut_variants` reads them
again for free and :meth:`Productions.select_cut_variant` applies one as a new version (free).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Union

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Productions", "PRODUCTION_TERMINAL_STATUSES"]

_BASE = "/v1/studio/productions"
PRODUCTION_TERMINAL_STATUSES = ("succeeded", "failed")


def _idem(key: Optional[str], ext: Optional[RequestExtensions]) -> Optional[Dict[str, Any]]:
    if not key:
        return dict(ext) if ext else None
    merged: Dict[str, Any] = dict(ext or {})
    merged["headers"] = {**dict(merged.get("headers") or {}), "Idempotency-Key": key}
    return merged


class Productions(Resource):
    """Create, read and wait for Studio productions."""

    def create(
        self,
        brief: str,
        language: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        starter: Optional[str] = None,
        voice: Optional[str] = None,
        narration: Optional[bool] = None,
        budget_micro_usd: Optional[int] = None,
        title: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        kind: Optional[str] = None,
        duration_s: Optional[int] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/productions`` — plan + images / music + creative + the output being built
        (``kind``: video | image | deck | doc | sheet | audio | carousel | print, default video)."""
        body: Dict[str, Any] = {"brief": brief}
        for k, v in (
            ("kind", kind),
            ("language", language),
            ("aspect_ratio", aspect_ratio),
            ("duration_s", duration_s),
            ("starter", starter),
            ("voice", voice),
            ("narration", narration),
            ("budget_micro_usd", budget_micro_usd),
            ("title", title),
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

    def create_cut(
        self,
        brief: str,
        asset_ids: List[str],
        language: Optional[str] = None,
        formats: Optional[List[str]] = None,
        default_format: Optional[str] = None,
        target_duration_s: Optional[int] = None,
        pacing: Optional[str] = None,
        reframe_preset: Optional[str] = None,
        captions: Union[bool, Dict[str, Any], None] = None,
        music: Optional[Dict[str, Any]] = None,
        broll: Optional[Dict[str, Any]] = None,
        script: Optional[str] = None,
        brand_kit_id: Optional[str] = None,
        budget_micro_usd: Optional[int] = None,
        title: Optional[str] = None,
        multicam: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/productions`` with ``kind: "cut"`` — 1-10 owned video / audio / image assets (≤ 60 min of
        media) become an edited video: ``formats`` ⊆ ``9x16`` / ``1x1`` / ``16x9``, ``pacing`` calm | balanced |
        punchy, ``captions`` a style dict or ``False``, ``music`` ``{"source": none|asset|lyria|music_room, ...}``,
        ``broll`` ``{"own", "stock", "generated": none|images|veo}``. SX-32 ``multicam`` ``{"angles": [...],
        "master_audio"?, "offsets_ms"?, "speaker_angles"?, "wide_angle"?, "split"?}``: several cameras of one recording,
        synced by sound and switched to the active speaker. Returns the ``StudioCutProduction`` (202)."""
        body: Dict[str, Any] = {"kind": "cut", "brief": brief, "asset_ids": list(asset_ids)}
        for k, v in (
            ("language", language),
            ("formats", formats),
            ("default_format", default_format),
            ("target_duration_s", target_duration_s),
            ("pacing", pacing),
            ("reframe_preset", reframe_preset),
            ("captions", captions),
            ("music", music),
            ("broll", broll),
            ("script", script),
            ("brand_kit_id", brand_kit_id),
            ("budget_micro_usd", budget_micro_usd),
            ("title", title),
            ("multicam", multicam),
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

    def cut(self, production_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/productions/{id}/cut`` — decisions (``id``, ``kind``, ``label``, ``reason``, ``enabled``,
        ``at_ms``, ``cluster``), take ``clusters``, ``script_gaps``, ``stats`` and ``overrides`` of a cut. Free;
        ``CodaiError`` 409 ``production_not_ready`` until the cut is assembled."""
        return self._json(f"{_BASE}/{enc(production_id)}/cut", ext=ext) or {}

    def revise_cut(
        self,
        production_id: str,
        disabled: Optional[List[str]] = None,
        takes: Optional[Dict[str, str]] = None,
        pacing: Optional[str] = None,
        captions: Union[bool, Dict[str, Any], None] = None,
        base_seq: Optional[int] = None,
        prompt: Optional[str] = None,
        target_s: Optional[int] = None,
        plan_delta: Optional[Dict[str, Any]] = None,
        default_format: Optional[str] = None,
        broll: Optional[bool] = None,
        angles: Optional[Dict[str, Optional[str]]] = None,
        reset_target: bool = False,
        reset_story: bool = False,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/productions/{id}/cut/revise`` — ``disabled`` decision ids (``"+<id>"`` re-enables,
        cumulative), ``takes`` (cluster id → sentence id), ``pacing``, ``captions`` (``False`` = none). Writes a new
        creative version (a new branch ``cut-<n>`` when you had edited it) and returns ``{creative_id, seq, branch,
        decisions, stats, warnings}``. Free. ``base_seq`` turns a moved branch into 409 ``stale``.

        SX-43: ``prompt`` is the edit request in words (EN or RO): length / energy / captions / b-roll / framing are
        mapped for free, content requests ("only the pricing part") cost one plan-funded model turn; the answer then
        carries ``prompt`` ``{path, understood, explanation, unmet, cost_micro_usd}``. ``target_s`` (15-600),
        ``plan_delta`` ``{keep_only, drop, hook, order}`` with sentence ids, ``default_format``, ``broll`` are free;
        ``reset_target`` / ``reset_story`` send ``null`` to undo the target / every story edit. SX-32 ``angles`` (multicam
        cuts): ``{"angle:3": asset_id | "wide" | "split" | None}`` pins shots (``None`` removes a pin)."""
        body: Dict[str, Any] = {}
        for k, v in (
            ("disabled", disabled),
            ("takes", takes),
            ("pacing", pacing),
            ("captions", captions),
            ("prompt", prompt),
            ("target_s", target_s),
            ("plan_delta", plan_delta),
            ("default_format", default_format),
            ("broll", broll),
            ("angles", angles),
            ("base_seq", base_seq),
        ):
            if v is not None:
                body[k] = v
        if reset_target:
            body["target_s"] = None
        if reset_story:
            body["plan_delta"] = None
        return (
            self._json(f"{_BASE}/{enc(production_id)}/cut/revise", ext=ext, method="POST", body=body, no_retry=True)
            or {}
        )

    def restyle_cut(
        self,
        production_id: str,
        style: Union[str, int],
        fetch_broll: Optional[bool] = None,
        base_seq: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/productions/{id}/cut/restyle`` — ``style`` is a built-in id (``"fast-social"``, ...) or
        the numeric id of one of your styles or a gallery style. Writes a new version at once (free) and returns the
        revise answer plus ``style``, ``broll_slots_needed`` and ``broll_job`` (``None`` when nothing is fetched; else
        a ``StudioRestyleJob`` to poll with :meth:`retrieve`). Only generated b-roll images are billed, at cost.
        ``fetch_broll=False`` applies the knobs only; ``base_seq`` turns a moved branch into 409 ``stale``."""
        body: Dict[str, Any] = {"style": style}
        if fetch_broll is not None:
            body["fetch_broll"] = fetch_broll
        if base_seq is not None:
            body["base_seq"] = base_seq
        return (
            self._json(f"{_BASE}/{enc(production_id)}/cut/restyle", ext=ext, method="POST", body=body, no_retry=True)
            or {}
        )

    def cut_variants(
        self,
        production_id: str,
        n: Optional[int] = None,
        judge: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/productions/{id}/cut/variants`` — ``n`` alternative edits (default 3, max 5; angles
        strongest_hook / story / punchy / topic), each scored 0-99 on ``hook`` / ``flow`` / ``value`` / ``fit`` with
        ``reasons``, ``weakest_axis`` and ``fix_hint``, sorted best first (``variants``), plus the ``current`` cut's
        score. Two token-metered model turns (``judge=False`` skips the judge: measured score only). Stored: read again
        free with :meth:`retrieve_cut_variants`. Apply one with :meth:`select_cut_variant`; raise the weakest axis with
        ``revise_cut(id, prompt=variant["score"]["fix_hint"])``. Scores are predictions, not guarantees."""
        body: Dict[str, Any] = {}
        if n is not None:
            body["n"] = n
        if judge is not None:
            body["judge"] = judge
        return (
            self._json(f"{_BASE}/{enc(production_id)}/cut/variants", ext=ext, method="POST", body=body, no_retry=True)
            or {}
        )

    def retrieve_cut_variants(self, production_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/productions/{id}/cut/variants`` — the stored variants and scores (free; ``CodaiError`` 404
        ``no_variants`` before the first :meth:`cut_variants`). ``stale`` is true when the cut changed since."""
        return self._json(f"{_BASE}/{enc(production_id)}/cut/variants", ext=ext) or {}

    def select_cut_variant(
        self,
        production_id: str,
        variant: str,
        base_seq: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/productions/{id}/cut/select`` — write variant ``"v1"``… as a new version (free); returns
        the :meth:`revise_cut` answer plus ``variant`` and its ``score``. Undo with ``revise_cut(id, reset_story=True)``;
        ``base_seq`` turns a moved branch into 409 ``stale``."""
        body: Dict[str, Any] = {"variant": variant}
        if base_seq is not None:
            body["base_seq"] = base_seq
        return (
            self._json(f"{_BASE}/{enc(production_id)}/cut/select", ext=ext, method="POST", body=body, no_retry=True)
            or {}
        )

    def retrieve(self, production_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/productions/{id}`` — advances render → review → repair → ready and returns the production.
        Another account's id is a 404."""
        return self._json(f"{_BASE}/{enc(production_id)}", ext=ext) or {}

    def wait(
        self,
        production_id: str,
        interval: float = 5.0,
        timeout: float = 600.0,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Poll :meth:`retrieve` until ``status`` is ``succeeded`` or ``failed`` (a failed production is returned too).
        Raises ``TimeoutError`` after ``timeout`` seconds (default 10 min)."""
        deadline = time.monotonic() + timeout
        while True:
            p = self.retrieve(production_id, ext=ext)
            if p.get("status") in PRODUCTION_TERMINAL_STATUSES:
                return p
            if time.monotonic() + interval > deadline:
                raise TimeoutError(f"codai production {production_id} did not finish within {timeout} s")
            time.sleep(interval)

    def run(
        self,
        brief: str,
        interval: float = 5.0,
        timeout: float = 600.0,
        ext: Optional[RequestExtensions] = None,
        **params: Any,
    ) -> Dict[str, Any]:
        """:meth:`create` then :meth:`wait`. ``params`` are :meth:`create`'s keyword args."""
        p = self.create(brief, ext=ext, **params)
        if p.get("status") in PRODUCTION_TERMINAL_STATUSES:
            return p
        return self.wait(p["id"], interval=interval, timeout=timeout, ext=ext)
