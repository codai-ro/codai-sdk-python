"""Platform endpoints: tools, tasks, devices, hosts, orgs, account, settings, themes, receipt, feedback, phone models."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Union

from .._http import CodaiError, HttpClient, RequestExtensions, frame_json
from ._base import Resource, enc, list_of

__all__ = [
    "Account",
    "Devices",
    "Feedback",
    "Hosts",
    "OrgMembers",
    "Orgs",
    "OsGate",
    "PhoneModels",
    "Receipts",
    "Settings",
    "settings_conflict_current",
    "Tasks",
    "Themes",
    "Tools",
]


def _iso(value: Union[str, datetime, None]) -> Optional[str]:
    return value.isoformat() if isinstance(value, datetime) else value


_IPHONE_TOOL_RE = re.compile(r"^[a-z_]{1,64}$")


# --------------------------------------------------------------------- tools
class Tools(Resource):
    def search(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/tools/search`` — verified web search. Filters: ``include_domains`` / ``exclude_domains``,
        ``freshness`` (day/week/month/year) or ``published_after`` / ``published_before`` (undated pages are dropped),
        ``content_chars`` for a verified excerpt per result. Each result has ``published_at`` (``None`` when unknown,
        never the crawl date) and ``crawled_at``. Metered: $3 / 1k fast, $8 / 1k deep (1,000 free per month, free
        inside a codai agent turn)."""
        return self._json("/v1/tools/search", ext=ext, body=body)

    def fetch(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/tools/fetch`` — fetch + extract a public page (``max_chars`` default 8000, max 40000;
        $0.50 / 1k)."""
        return self._json("/v1/tools/fetch", ext=ext, body=body)

    def ground(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/tools/ground`` — find a described UI element on an inline ``data:image`` screenshot."""
        return self._json("/v1/tools/ground", ext=ext, body=body)


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

    def plugins(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/devices/plugins`` — MR-40: installed CLAP/VST3 plugins per device."""
        return self._json("/v1/devices/plugins", ext=ext) or {}

    def set_plugins(self, id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PUT /v1/devices/{id}/plugins`` — MR-40: replace a device's plugin inventory (``{scanned_at, plugins}``)."""
        return self._json(f"/v1/devices/{enc(id)}/plugins", ext=ext, method="PUT", body=body)

    def revoke_self_key(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/keys/self/revoke`` — the API key this client uses revokes itself (sign out)."""
        return self._json("/v1/keys/self/revoke", ext=ext, method="POST")

    def dispatch_inbox(self, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/devices/me/dispatch`` — pending dispatches for the calling device."""
        return self._json("/v1/devices/me/dispatch", ext=ext, query={"limit": limit})


# --------------------------------------------------------------------- hosts
class Hosts(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/hosts`` — online hosts of the calling user (each with ``caps`` and ``environment_id``)."""
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

    def iphone(
        self,
        device_id: str,
        tool: str,
        args: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
        label: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/hosts/{deviceId}/exec`` with op ``iphone`` — run one codai iPhone bridge tool (``screen``,
        ``tap``, ``swipe``, ``type``, ``open_app``, … — the ``codai-iphone`` MCP names without ``iphone_``) on an
        online host with cap ``iphone``. ``result`` is ``{"data": ..., "image": "data:image/jpeg;base64,…"?}``.
        Sensitive tools are refused by the bridge when called remotely."""
        if not _IPHONE_TOOL_RE.match(tool):
            raise ValueError("hosts.iphone: tool must match ^[a-z_]{1,64}$")
        payload: Dict[str, Any] = {"tool": tool}
        if args is not None:
            payload["args"] = args
        return self.exec(device_id, "iphone", payload, timeout_ms=timeout_ms, label=label, ext=ext)

    def post_result(self, req_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/hosts/exec/{reqId}/result`` — host side: deliver the result of a relayed exec."""
        return self._json(f"/v1/hosts/exec/{enc(req_id)}/result", ext=ext, body=body)

    def stream(
        self,
        os: Optional[str] = None,
        hostname: Optional[str] = None,
        roots: Optional[List[str]] = None,
        caps: Optional[List[str]] = None,
        environment_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Iterator[Dict[str, Any]]:
        """``GET /v1/hosts/stream`` — host side: yields ``{"event": "hello"|"ping"|"exec", "data": {...}}``.
        ``caps`` (≤ 16, e.g. ``["iphone", "video"]``) and ``environment_id`` (the environment serving this host's
        ``video`` / ``pty`` streams) are sent as ``caps=`` / ``env=``."""
        query = {
            "os": os,
            "hostname": hostname,
            "roots": ",".join(roots) if roots else None,
            "caps": ",".join(caps) if caps else None,
            "env": environment_id,
        }
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

    def delete(self, confirm_email: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/account`` — schedule the erasure of the account after the 7-day grace period.
        ``confirm_email`` must equal the account e-mail (case-insensitive); full keys only. Every API key (this one
        included) is revoked at once; signing in at ``cancel_url`` within the grace cancels it. Idempotent: an
        already-queued request returns its original ``scheduled_for``."""
        return self._json("/v1/account", ext=ext, method="DELETE", body={"confirm_email": confirm_email})


class Settings(Resource):
    """Account-level settings shared by every device of the account (per user, not per key)."""

    def get(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/settings`` — full settings with defaults; ``version`` 0 / ``updatedAt`` None until the first write."""
        return self._json("/v1/settings", ext=ext)

    def update(
        self,
        partial: Dict[str, Any],
        version: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PATCH /v1/settings`` — deep-merge ``partial`` (e.g. ``{"transcripts": {"waveform": "bars"}}`` or
        ``{"appearance": {"accent": "teal", "mode": "dark", "skin": "focus"}}``; ``appearance`` is the look & feel
        synced to desktop, phone and hub, typed as ``codai._types.AppearanceSettings``).

        With ``version`` the write is conditional: a stale version raises ``CodaiError`` with status 409 and code
        ``version_conflict``; the current state is in ``err.body["current"]`` (see :func:`settings_conflict_current`).
        Unknown keys / invalid values raise a 400 ``CodaiError``."""
        body: Dict[str, Any] = {"settings": partial}
        if version is not None:
            body["version"] = version
        return self._json("/v1/settings", ext=ext, method="PATCH", body=body)


def settings_conflict_current(err: BaseException) -> Optional[Dict[str, Any]]:
    """The ``current`` state of a 409 ``version_conflict`` raised by ``settings.update``, else None."""
    if not isinstance(err, CodaiError) or err.status != 409 or err.code != "version_conflict":
        return None
    body = err.body if isinstance(err.body, dict) else {}
    current = body.get("current")
    return current if isinstance(current, dict) else None


class Themes(Resource):
    """Public curated colour theme catalogue (licensed third-party themes with provenance)."""

    def list(self, etag: Optional[str] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/themes`` — ``{"version", "etag", "themes": [...]}`` (``codai._types.ThemesCatalog``). With
        ``etag`` (the last answer's ``etag``) it sends ``If-None-Match``; when unchanged the gateway answers 304 and
        this returns ``{"notModified": True}``."""
        call_ext: Dict[str, Any] = dict(ext or {})
        if etag:
            call_ext["headers"] = {**dict(call_ext.get("headers") or {}), "If-None-Match": etag}
        res = self._http.request("/v1/themes", ext=call_ext or None, accept_status=(304,))  # type: ignore[arg-type]
        if res.status == 304:
            return {"notModified": True}
        return res.json()


class OsGate(Resource):
    """OS protection gate (spec ``packages/agent-core/spec/os-gate.json``): org override policy + override audit."""

    def policy(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/policy`` — ``{"os_gate": {"allow_override": bool}}`` folded over every org of the caller (any org
        forbidding wins). Cache it (``max-age=300``) and keep the last value offline; a 503 ``policy_unavailable``
        ``CodaiError`` means "keep the cached value"."""
        return self._json("/v1/policy", ext=ext)

    def record_event(
        self,
        action: str,
        checks: List[str],
        surface: str,
        app_version: str,
        at: Union[str, datetime],
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/os-gate/events`` — audit an override ``"granted"`` / ``"revoked"`` for ``checks`` (spec check ids,
        1..16) on ``surface`` (``desktop``, ``headless``, ``codaid``, ``phone``, ``mobile_agent``, ``wear``, ``vscode``).
        Returns ``{"ok": True}`` (202). The body is strict: unknown check ids raise a 400 ``CodaiError``."""
        body: Dict[str, Any] = {
            "action": action,
            "checks": list(checks),
            "surface": surface,
            "app_version": app_version,
            "at": _iso(at),
        }
        return self._json("/v1/os-gate/events", ext=ext, body=body)


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
