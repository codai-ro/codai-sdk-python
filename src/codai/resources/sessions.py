"""``/v1/sessions/*`` — shared-sessions protocol v2 (events, controls, lease,
dispatch, SSE stream) plus per-session shares. Every call needs the
``x-codai-device`` header: set ``Codai(device="<uuid>")`` or pass ``ext={"device": ...}``."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from .._http import HttpClient, RequestExtensions, frame_json
from ._base import Resource, enc, list_of

__all__ = ["Sessions", "SessionEvents", "SessionControls", "SessionLease", "SessionShares"]


class SessionLease(Resource):
    def acquire(
        self, session_id: str, body: Optional[Dict[str, Any]] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/sessions/{id}/lease`` — CAS claim; ``{"force": True}`` takes over a live lease."""
        return self._json(f"/v1/sessions/{enc(session_id)}/lease", ext=ext, method="POST", body=body or {})

    def renew(self, session_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PUT /v1/sessions/{id}/lease`` — heartbeat every 10 s (TTL 30 s)."""
        return self._json(f"/v1/sessions/{enc(session_id)}/lease", ext=ext, method="PUT")

    def release(self, session_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/sessions/{id}/lease``"""
        return self._json(f"/v1/sessions/{enc(session_id)}/lease", ext=ext, method="DELETE")


class SessionEvents(Resource):
    def list(
        self,
        session_id: str,
        after: Optional[int] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/sessions/{id}/events?after=&limit=``"""
        return self._json(f"/v1/sessions/{enc(session_id)}/events", ext=ext, query={"after": after, "limit": limit})

    def append(self, session_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/sessions/{id}/events`` — executor only (needs the live lease)."""
        return self._json(f"/v1/sessions/{enc(session_id)}/events", ext=ext, body=body)


class SessionControls(Resource):
    def list(
        self,
        session_id: str,
        applied: Optional[bool] = None,
        target: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> List[Dict[str, Any]]:
        """``GET /v1/sessions/{id}/controls?applied=&target=``"""
        raw = self._json(
            f"/v1/sessions/{enc(session_id)}/controls", ext=ext, query={"applied": applied, "target": target}
        )
        return list_of(raw, "controls")

    def submit(self, session_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/sessions/{id}/control`` — send a control to the executor (editor+)."""
        return self._json(f"/v1/sessions/{enc(session_id)}/control", ext=ext, body=body)

    def mark_applied(
        self, session_id: str, control_id: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/sessions/{id}/control/{cid}/applied`` — executor only."""
        return self._json(
            f"/v1/sessions/{enc(session_id)}/control/{enc(control_id)}/applied", ext=ext, method="POST"
        )


class SessionShares(Resource):
    def list(self, session_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/sessions/{id}/shares`` — owner only."""
        return list_of(self._json(f"/v1/sessions/{enc(session_id)}/shares", ext=ext), "shares")

    def create(self, session_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/sessions/{id}/shares`` — ``token`` is returned once for link shares."""
        return self._json(f"/v1/sessions/{enc(session_id)}/shares", ext=ext, body=body)

    def delete(self, session_id: str, share_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/sessions/{id}/shares/{shareId}``"""
        return self._json(f"/v1/sessions/{enc(session_id)}/shares/{enc(share_id)}", ext=ext, method="DELETE")

    def shared_with_me(
        self, archived: Optional[bool] = None, ext: Optional[RequestExtensions] = None
    ) -> List[Dict[str, Any]]:
        """``GET /v1/sessions/shared-with-me``"""
        raw = self._json("/v1/sessions/shared-with-me", ext=ext, query={"archived": "1" if archived else None})
        return list_of(raw, "sessions")


class Sessions(Resource):
    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)
        self.events = SessionEvents(http)
        self.controls = SessionControls(http)
        self.lease = SessionLease(http)
        self.shares = SessionShares(http)

    def create(self, body: Optional[Dict[str, Any]] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/sessions`` — idempotent on ``session_key``; result carries ``created`` (201 vs 200)."""
        res = self._http.request("/v1/sessions", body=body or {}, ext=ext)
        session = res.json() or {}
        session["created"] = res.status == 201
        return session

    def list(
        self,
        limit: Optional[int] = None,
        archived: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> List[Dict[str, Any]]:
        """``GET /v1/sessions?limit=&archived=`` — own sessions first, then shared."""
        raw = self._json("/v1/sessions", ext=ext, query={"limit": limit, "archived": "1" if archived else None, "v": "2"})
        return list_of(raw, "sessions")

    def get(self, session_id: str, share: Optional[str] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/sessions/{id}`` — detail with members, lease and presence."""
        return self._json(f"/v1/sessions/{enc(session_id)}", ext=ext, query={"share": share, "v": "2"})

    def update(self, session_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/sessions/{id}`` — rename / archive (owner)."""
        return self._json(f"/v1/sessions/{enc(session_id)}", ext=ext, method="PATCH", body=body)

    def delete(self, session_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/sessions/{id}`` — irreversible (owner)."""
        return self._json(f"/v1/sessions/{enc(session_id)}", ext=ext, method="DELETE")

    def dispatch(self, session_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/sessions/{id}/dispatch`` — queue a ``send`` for one device and wake it over FCM."""
        return self._json(f"/v1/sessions/{enc(session_id)}/dispatch", ext=ext, body=body)

    def stream(
        self,
        session_id: str,
        after: Optional[int] = None,
        share: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Iterator[Dict[str, Any]]:
        """``GET /v1/sessions/{id}/stream?after=`` — yields ``{"event": "event"|"control"|"lease"|"presence", "data": {...}}``;
        ``: ping`` heartbeats are skipped. The server closes after 30 min; reconnect with ``after`` = highest ``seq``."""
        for frame in self._http.sse(
            f"/v1/sessions/{enc(session_id)}/stream", ext=ext, query={"after": after, "share": share}
        ):
            data = frame_json(frame)
            if not isinstance(data, dict):
                continue
            yield {"event": frame.event, "data": data}
