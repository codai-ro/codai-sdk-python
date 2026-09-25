"""Platform endpoints: tools, tasks, devices, hosts, orgs, account, receipt, feedback, phone models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Union

from .._http import HttpClient, RequestExtensions, frame_json
from ._base import Resource, enc, list_of

__all__ = [
    "Account",
    "Devices",
    "Feedback",
    "Hosts",
    "OrgMembers",
    "Orgs",
    "PhoneModels",
    "Receipts",
    "Tasks",
    "Tools",
]


def _iso(value: Union[str, datetime, None]) -> Optional[str]:
    return value.isoformat() if isinstance(value, datetime) else value


# --------------------------------------------------------------------- tools
class Tools(Resource):
    def search(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/tools/search`` — verified web search."""
        return self._json("/v1/tools/search", ext=ext, body=body)

    def fetch(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/tools/fetch`` — fetch + extract a public page."""
        return self._json("/v1/tools/fetch", ext=ext, body=body)


# --------------------------------------------------------------------- tasks
class Tasks(Resource):
    def list(
        self,
        outcome: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/tasks`` — ``{"tasks": [...], "next_cursor": ...}``, newest first."""
        return self._json("/v1/tasks", ext=ext, query={"outcome": outcome, "limit": limit, "cursor": cursor})

    def pending(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/tasks/pending`` — tasks awaiting your confirmation."""
        return list_of(self._json("/v1/tasks/pending", ext=ext), "tasks")

    def stats(
        self, since: Union[str, datetime, None] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/tasks/stats?since=``"""
        return self._json("/v1/tasks/stats", ext=ext, query={"since": _iso(since)})

    def get(self, id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/tasks/{id}``"""
        return self._json(f"/v1/tasks/{enc(id)}", ext=ext)

    def confirm(self, id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/tasks/{id}/confirm`` — ``{"outcome": "confirmed"|"fail", ...}``."""
        return self._json(f"/v1/tasks/{enc(id)}/confirm", ext=ext, body=body)


# ------------------------------------------------------------------- devices
class Devices(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/devices``"""
        return list_of(self._json("/v1/devices", ext=ext), "devices")

    def update(self, id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/devices/{id}`` — rename / change platform."""
        return self._json(f"/v1/devices/{enc(id)}", ext=ext, method="PATCH", body=body)

    def delete(self, id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/devices/{id}``"""
        return self._json(f"/v1/devices/{enc(id)}", ext=ext, method="DELETE")

    def dispatch_inbox(self, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/devices/me/dispatch`` — pending dispatches for the calling device."""
        return self._json("/v1/devices/me/dispatch", ext=ext, query={"limit": limit})


# --------------------------------------------------------------------- hosts
class Hosts(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/hosts`` — online hosts of the calling user."""
        return list_of(self._json("/v1/hosts", ext=ext), "hosts")

    def exec(
        self,
        device_id: str,
        op: str,
        args: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
        label: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/hosts/{deviceId}/exec`` — relay one operation to a host and wait for the result."""
        body: Dict[str, Any] = {"op": op, "args": args or {}}
        if timeout_ms is not None:
            body["timeout_ms"] = timeout_ms
        if label is not None:
            body["label"] = label
        return self._json(
            f"/v1/hosts/{enc(device_id)}/exec",
            ext=ext,
            body=body,
            timeout=((timeout_ms if timeout_ms is not None else 60_000) + 10_000) / 1000,
            no_retry=True,
        )

    def post_result(self, req_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/hosts/exec/{reqId}/result`` — host side: deliver the result of a relayed exec."""
        return self._json(f"/v1/hosts/exec/{enc(req_id)}/result", ext=ext, body=body)

    def stream(
        self,
        os: Optional[str] = None,
        hostname: Optional[str] = None,
        roots: Optional[List[str]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Iterator[Dict[str, Any]]:
        """``GET /v1/hosts/stream`` — host side: yields ``{"event": "hello"|"ping"|"exec", "data": {...}}``."""
        query = {"os": os, "hostname": hostname, "roots": ",".join(roots) if roots else None}
        for frame in self._http.sse("/v1/hosts/stream", ext=ext, query=query):
            data = frame_json(frame)
            if not isinstance(data, dict):
                continue
            yield {"event": frame.event, "data": data}


# ---------------------------------------------------------------------- orgs
class OrgMembers(Resource):
    def list(self, org_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/orgs/{id}/members``"""
        return list_of(self._json(f"/v1/orgs/{enc(org_id)}/members", ext=ext), "members")

    def add(self, org_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/orgs/{id}/members`` — ``{"user_id": ..., "role": ...}``."""
        return self._json(f"/v1/orgs/{enc(org_id)}/members", ext=ext, body=body)

    def remove(self, org_id: str, user_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/orgs/{id}/members/{userId}``"""
        return self._json(f"/v1/orgs/{enc(org_id)}/members/{enc(user_id)}", ext=ext, method="DELETE")


class Orgs(Resource):
    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)
        self.members = OrgMembers(http)

    def create(self, name: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/orgs``"""
        return self._json("/v1/orgs", ext=ext, body={"name": name})

    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/orgs``"""
        return list_of(self._json("/v1/orgs", ext=ext), "orgs")


# ------------------------------------------------------------------- account
class Account(Resource):
    def get(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/account`` — the full account card."""
        return self._json("/v1/account", ext=ext)

    def update(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/account`` — consents, username, referral."""
        return self._json("/v1/account", ext=ext, method="PATCH", body=body)


class Receipts(Resource):
    def get(
        self,
        session_id: Optional[str] = None,
        since: Union[str, datetime, None] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/receipt`` — spend receipt (``session_id`` wins over ``since``; default last 24 h)."""
        return self._json("/v1/receipt", ext=ext, query={"session_id": session_id, "since": _iso(since)})


class Feedback(Resource):
    def submit(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/feedback`` — exactly one of ``event_id`` / ``session_id`` / ``client_request_id``."""
        return self._json("/v1/feedback", ext=ext, body=body) or {}


class PhoneModels(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/phone/models`` — on-device model catalog with signed URLs."""
        return list_of(self._json("/v1/phone/models", ext=ext), "models")
