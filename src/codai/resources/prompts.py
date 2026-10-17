"""Pending prompts: ``/v1/prompts/*`` — ready-to-paste prompts left for a future chat (handoffs, follow-ups)."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from .._http import RequestExtensions, frame_json
from ._base import Resource, enc

__all__ = ["Prompts"]


def _prompt(prompt_id: str, suffix: str = "") -> str:
    return f"/v1/prompts/{enc(prompt_id)}{suffix}"


class Prompts(Resource):
    def list(
        self, status: Optional[str] = None, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/prompts?status=&limit=`` — default ``open``; ``due`` = open and ``not_before`` empty or passed."""
        return self._json("/v1/prompts", ext=ext, query={"status": status, "limit": limit})

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/prompts`` — idempotent on the text (``created: False`` for a duplicate);
        ``goal_key`` supersedes older open prompts with the same key."""
        return self._json("/v1/prompts", ext=ext, method="POST", body=body)

    def get(self, prompt_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/prompts/{id}``."""
        return self._json(_prompt(prompt_id), ext=ext)

    def update(self, prompt_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/prompts/{id}`` — edit, snooze (``not_before``), close (``status: done | dismissed``)."""
        return self._json(_prompt(prompt_id), ext=ext, method="PATCH", body=body)

    def delete(self, prompt_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/prompts/{id}`` — ``{"deleted": 0}`` when the id is missing or not yours."""
        return self._json(_prompt(prompt_id), ext=ext, method="DELETE")

    def launch(
        self, prompt_id: str, device_id: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/prompts/{id}/launch`` — new shared session + ``send`` control on a device (not retried)."""
        return self._json(
            _prompt(prompt_id, "/launch"),
            ext=ext,
            method="POST",
            body={"device_id": device_id} if device_id else {},
            no_retry=True,
        )

    def match(self, prompt_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/prompts/{id}/match`` — ``{"ref", "turn_id"?, "score"?, "sent_at"?, "answered"?, "base_sha"?}``;
        the prompt becomes ``sent`` (or ``answered``); never downgrades ``verified|done|dismissed``."""
        return self._json(_prompt(prompt_id, "/match"), ext=ext, method="POST", body=body)

    def verify(
        self, prompt_id: str, body: Optional[Dict[str, Any]] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/prompts/{id}/verify`` — LLM report over ``transcript`` (or the matched session) and an
        optional ``diff``; verdict ``done`` → ``verified``. 502 when the model call fails (not retried)."""
        return self._json(_prompt(prompt_id, "/verify"), ext=ext, method="POST", body=body or {}, no_retry=True)

    def verify_many(
        self,
        ids: Optional[List[str]] = None,
        all_active: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/prompts/verify`` — transcript-only verification of up to 20 prompts, sequentially."""
        body: Dict[str, Any] = {}
        if ids:
            body["ids"] = ids
        if all_active is not None:
            body["all_active"] = all_active
        return self._json("/v1/prompts/verify", ext=ext, method="POST", body=body, no_retry=True)

    def stream(self, ext: Optional[RequestExtensions] = None) -> Iterator[Dict[str, Any]]:
        """``GET /v1/prompts/stream`` — yields ``{"op", "id", "status", "prompt"?}`` per ``prompt`` event."""
        for frame in self._http.sse("/v1/prompts/stream", ext=ext):
            if frame.event != "prompt":
                continue
            data = frame_json(frame)
            if isinstance(data, dict):
                yield data
