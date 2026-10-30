"""``/v1/studio/music-room`` — codai Studio Music Room (MR-09..MR-17): a team of role agents (producer, composer,
lyricist, arranger, session players, vocal producer, mix and mastering engineers, critic, rights) writes, plays, sings
and mixes a song that sounds played by people, saved as an editable audio creative.

``create`` starts a song (202), ``get`` advances and reads it, ``list`` pages your songs, ``quota`` reports the songs
included this month, ``choose`` answers the open gate (``plan`` / ``demo`` / ``final``) and ``direct`` asks one player
to re-play a part. ``plugins`` / ``plugin`` read the cloud CLAP/VST3 plugin set and ``set_track_plugin`` puts a plugin
chain on one player's track (MR-41). ``wait`` polls until ``succeeded`` / ``failed`` or, with ``until_gate=True``, until the song waits
at a gate. Free within the monthly plan quota; beyond it every step is held on the wallet up to ``budget_micro_usd``
(default 4,000,000 = $4).
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["MusicRoom", "Studio", "MUSIC_ROOM_TERMINAL_STATUSES"]

_BASE = "/v1/studio/music-room"
MUSIC_ROOM_TERMINAL_STATUSES = ("succeeded", "failed")


def _idem(key: Optional[str], ext: Optional[RequestExtensions]) -> Optional[Dict[str, Any]]:
    if not key:
        return dict(ext) if ext else None
    merged: Dict[str, Any] = dict(ext or {})
    merged["headers"] = {**dict(merged.get("headers") or {}), "Idempotency-Key": key}
    return merged


class MusicRoom(Resource):
    """Start, steer and wait for Music Room songs."""

    def create(
        self,
        brief: str,
        language: Optional[str] = None,
        genre: Optional[str] = None,
        duration_seconds: Optional[int] = None,
        vocals: Optional[bool] = None,
        timbre: Optional[str] = None,
        voice_passport_id: Optional[str] = None,
        instruments: Optional[List[str]] = None,
        auto: Optional[bool] = None,
        budget_micro_usd: Optional[int] = None,
        title: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/music-room`` — start a song (the producer plans it, then it waits at the plan gate)."""
        body: Dict[str, Any] = {"brief": brief}
        for k, v in (
            ("language", language),
            ("genre", genre),
            ("duration_seconds", duration_seconds),
            ("vocals", vocals),
            ("timbre", timbre),
            ("voice_passport_id", voice_passport_id),
            ("instruments", instruments),
            ("auto", auto),
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

    def get(self, music_room_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/music-room/{id}`` — advances the workflow and returns the song. Another account's id is a 404."""
        return self._json(f"{_BASE}/{enc(music_room_id)}", ext=ext) or {}

    def list(
        self,
        limit: Optional[int] = None,
        before: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/music-room`` — ``{object: "list", data, has_more}``, newest first; page with ``before``."""
        return self._json(_BASE, ext=ext, query={"limit": limit, "before": before}) or {}

    def quota(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/music-room/quota`` — ``{plan, included, used, remaining, period_end}`` for this month."""
        return self._json(f"{_BASE}/quota", ext=ext) or {}

    def choose(
        self,
        music_room_id: str,
        gate: str,
        variant: Optional[int] = None,
        approve: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/music-room/{id}/choose`` — answer the open gate: ``gate="plan", variant=0..2`` or
        ``gate="demo"`` / ``gate="final"`` (approved). 409 ``not_at_gate`` when the song is not waiting there."""
        body: Dict[str, Any] = {"gate": gate}
        if gate == "plan":
            body["variant"] = 0 if variant is None else variant
        else:
            body["approve"] = True if approve is None else approve
        return self._json(f"{_BASE}/{enc(music_room_id)}/choose", ext=ext, method="POST", body=body) or {}

    def direct(
        self,
        music_room_id: str,
        role: str,
        direction: str,
        section_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/music-room/{id}/direct`` — one player re-plays its part following ``direction`` (≤ 500
        characters) and the demo is re-rendered. Only at the demo or final gate."""
        body: Dict[str, Any] = {"role": role, "direction": direction}
        if section_id is not None:
            body["section_id"] = section_id
        return (
            self._json(
                f"{_BASE}/{enc(music_room_id)}/direct",
                ext=_idem(idempotency_key, ext),
                method="POST",
                body=body,
                no_retry=not idempotency_key,
            )
            or {}
        )

    def plugins(
        self,
        kind: Optional[str] = None,
        q: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/music-room/plugins`` — ``{object: "list", data}``: the cloud plugin set (free/open-source
        CLAP and VST3 instruments and effects that always render in the cloud), filtered by ``kind`` (``instrument`` /
        ``effect``) and a free-text ``q``."""
        return self._json(f"{_BASE}/plugins", ext=ext, query={"kind": kind, "q": q}) or {}

    def plugin(self, format: str, plugin_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/music-room/plugins/{format}/{pluginId}`` — one cloud plugin with its curated params
        (404 ``plugin_not_found`` otherwise)."""
        return self._json(f"{_BASE}/plugins/{enc(format)}/{enc(plugin_id)}", ext=ext) or {}

    def set_track_plugin(
        self,
        music_room_id: str,
        body: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/music-room/{id}/plugin`` — ``{role, plugin, effects?}``: an instrument plugin plus up to 4
        effects of one format on one player's track, or ``plugin: None`` to go back to the instrument. Re-renders at
        the demo or final gate (402 ``budget_exhausted`` when the song budget is short)."""
        return (
            self._json(
                f"{_BASE}/{enc(music_room_id)}/plugin",
                ext=_idem(idempotency_key, ext),
                method="POST",
                body=body,
                no_retry=not idempotency_key,
            )
            or {}
        )

    def export_project(self, music_room_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/music-room/{id}/export?format=dawproject`` — build a ``.dawproject`` (DAWproject 1.0) in
        the background (202, free). Poll ``exports.wait(export["id"])`` until ``succeeded``, then download
        ``url``."""
        return (
            self._json(
                f"{_BASE}/{enc(music_room_id)}/export",
                ext=ext,
                method="POST",
                query={"format": "dawproject"},
            )
            or {}
        )

    def wait(
        self,
        music_room_id: str,
        until_gate: bool = False,
        interval: float = 10.0,
        timeout: float = 1800.0,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Poll :meth:`get` until ``status`` is ``succeeded`` or ``failed`` (a failed song is returned too) or, with
        ``until_gate=True``, until it waits at a gate. Raises ``TimeoutError`` after ``timeout`` seconds (default 30 min)."""
        deadline = time.monotonic() + timeout
        while True:
            r = self.get(music_room_id, ext=ext)
            status = r.get("status")
            if status in MUSIC_ROOM_TERMINAL_STATUSES or (until_gate and status == "waiting"):
                return r
            if time.monotonic() + interval > deadline:
                raise TimeoutError(f"codai music room {music_room_id} did not finish within {timeout} s")
            time.sleep(interval)


class Studio:
    """codai Studio namespace: ``client.studio.music_room``."""

    def __init__(self, http: Any) -> None:
        self.music_room = MusicRoom(http)
