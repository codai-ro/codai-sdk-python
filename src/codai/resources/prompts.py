"""Pending prompts: ``/v1/prompts/*`` — ready-to-paste prompts left for a future chat (handoffs, follow-ups).

Every prompt row also carries the PR-04/07 organise fields: ``tags`` (list), ``priority`` (0..3), ``recurrence``
(``{"every": "day|week|month", "at"?: "HH:MM"}`` or ``{"on": "session_end"}``), ``next_prompt_id``, ``launch``
(``{"agent"?, "model"?, "folder"?}``) and ``is_template``; ``create`` / ``update`` accept them in the body."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Sequence, Union

from .._http import RequestExtensions, frame_json
from ._base import Resource, enc

__all__ = ["Prompts"]


def _prompt(prompt_id: str, suffix: str = "") -> str:
    return f"/v1/prompts/{enc(prompt_id)}{suffix}"


def _filters(
    status: Optional[str],
    limit: Optional[int],
    tag: Optional[Union[str, Sequence[str]]],
    priority_min: Optional[int],
    q: Optional[str],
    templates: Optional[str],
    sort: Optional[str],
    order: Optional[str],
) -> Dict[str, Any]:
    tags = tag if isinstance(tag, str) or tag is None else ",".join(tag)
    return {
        "status": status,
        "limit": limit,
        "tag": tags or None,
        "priority_min": priority_min,
        "q": q,
        "templates": templates,
        "sort": sort,
        "order": order,
    }


class Prompts(Resource):
    def list(
        self,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
        *,
        tag: Optional[Union[str, Sequence[str]]] = None,
        priority_min: Optional[int] = None,
        q: Optional[str] = None,
        templates: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/prompts`` — default ``open``, templates excluded; ``due`` = open and ``not_before`` empty or passed.
        ``tag`` (several = AND), ``priority_min`` 0..3, ``q`` (title / prompt / session title), ``templates``
        ``only|exclude``, ``sort`` ``created|updated|priority|not_before``, ``order`` ``asc|desc``."""
        return self._json(
            "/v1/prompts",
            ext=ext,
            query=_filters(status, limit, tag, priority_min, q, templates, sort, order),
        )

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

    def bulk(
        self,
        ids: List[str],
        action: str,
        *,
        not_before: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/prompts/bulk`` — ``action`` in ``done|dismiss|delete|snooze|tag|untag|priority`` over up to 200
        of your prompts (``snooze`` needs ``not_before``, ``tag``/``untag`` ``tags``, ``priority`` ``priority``)
        → ``{"updated": n}``."""
        body: Dict[str, Any] = {"ids": ids, "action": action}
        if not_before is not None:
            body["not_before"] = not_before
        if tags is not None:
            body["tags"] = tags
        if priority is not None:
            body["priority"] = priority
        return self._json("/v1/prompts/bulk", ext=ext, method="POST", body=body)

    def events(self, prompt_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/prompts/{id}/events`` — ``{"events": [{"kind", "detail", "created_at"}]}``, newest first."""
        return self._json(_prompt(prompt_id, "/events"), ext=ext)

    def instantiate(self, prompt_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/prompts/{id}/instantiate`` — open copy of a template (not retried)."""
        return self._json(_prompt(prompt_id, "/instantiate"), ext=ext, method="POST", no_retry=True)

    def export_prompts(
        self,
        format: str = "csv",
        status: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
        *,
        tag: Optional[Union[str, Sequence[str]]] = None,
        priority_min: Optional[int] = None,
        q: Optional[str] = None,
        templates: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> str:
        """``GET /v1/prompts/export?format=csv|md`` — the list filters apply (``status`` defaults to ``all``);
        returns the CSV (RFC 4180) or Markdown text."""
        query = _filters(status, limit, tag, priority_min, q, templates, sort, order)
        query["format"] = format
        res = self._http.request("/v1/prompts/export", ext=ext, query=query)
        return res.data.decode("utf-8")

    def stream(self, ext: Optional[RequestExtensions] = None) -> Iterator[Dict[str, Any]]:
        """``GET /v1/prompts/stream`` — yields ``{"op", "id", "status", "prompt"?}`` per ``prompt`` event."""
        for frame in self._http.sse("/v1/prompts/stream", ext=ext):
            if frame.event != "prompt":
                continue
            data = frame_json(frame)
            if isinstance(data, dict):
                yield data
