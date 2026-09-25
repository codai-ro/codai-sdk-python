"""Event triggers and the inbox: ``/v1/triggers/*``, ``/v1/hooks/{id}`` and ``/v1/notifications/*``."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Notifications", "Triggers", "sign_hook"]


def _trigger(trigger_id: str, suffix: str = "") -> str:
    return f"/v1/triggers/{enc(trigger_id)}{suffix}"


def sign_hook(secret: str, raw_body: str, timestamp: Optional[int] = None) -> str:
    """``X-Codai-Signature`` value: ``t=<unix>,v1=HMAC_SHA256(secret, "<t>.<body>")`` (hex)."""
    t = int(time.time()) if timestamp is None else int(timestamp)
    mac = hmac.new(secret.encode("utf-8"), f"{t}.{raw_body}".encode("utf-8"), hashlib.sha256).hexdigest()
    return f"t={t},v1={mac}"


class Triggers(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/triggers`` — never includes the signing secret."""
        return self._json("/v1/triggers", ext=ext)

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/triggers`` — the response carries the signing ``secret`` ONCE."""
        return self._json("/v1/triggers", ext=ext, method="POST", body=body)

    def update(self, trigger_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/triggers/{id}`` — name / enabled / policy."""
        return self._json(_trigger(trigger_id), ext=ext, method="PATCH", body=body)

    def delete(self, trigger_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/triggers/{id}`` — its hook URL stops working immediately."""
        return self._json(_trigger(trigger_id), ext=ext, method="DELETE")

    def rotate_secret(self, trigger_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/triggers/{id}/rotate-secret`` — new secret, shown once."""
        return self._json(_trigger(trigger_id, "/rotate-secret"), ext=ext, method="POST", body={})

    def set_secret(self, trigger_id: str, secret: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PUT /v1/triggers/{id}/secret`` — store a secret issued by the source (e.g. a Sentry client secret)."""
        return self._json(
            _trigger(trigger_id, "/secret"), ext=ext, method="PUT", body={"secret": secret}, no_retry=True
        )

    def test(
        self, trigger_id: str, body: Optional[Dict[str, Any]] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/triggers/{id}/test`` — manual fire through the full pipeline; returns the decision + reason."""
        return self._json(_trigger(trigger_id, "/test"), ext=ext, method="POST", body=body or {})

    def events(
        self, trigger_id: str, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/triggers/{id}/events?limit=`` — recent deliveries with decisions."""
        return self._json(_trigger(trigger_id, "/events"), ext=ext, query={"limit": limit})

    def fire_hook(
        self,
        trigger_id: str,
        secret: str,
        event: Dict[str, Any],
        delivery_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/hooks/{id}`` — send an event to a ``generic`` / ``form`` trigger.

        Signs the body (``X-Codai-Signature: t=<unix>,v1=HMAC_SHA256(secret, "<t>.<body>")``);
        ``delivery_id`` makes retries idempotent. The signature is the auth.
        """
        raw = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
        headers: Dict[str, str] = dict((ext or {}).get("headers") or {})
        headers["Content-Type"] = "application/json"
        headers["x-codai-signature"] = sign_hook(secret, raw)
        if delivery_id:
            headers["x-codai-delivery"] = delivery_id
        merged: Dict[str, Any] = {**dict(ext or {}), "headers": headers}
        return self._json(
            f"/v1/hooks/{enc(trigger_id)}",
            ext=merged,
            method="POST",
            raw_body=raw.encode("utf-8"),
            content_type="application/json",
        )


class Notifications(Resource):
    def list(
        self, unread: bool = False, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/notifications?unread=1&limit=`` — newest first."""
        return self._json("/v1/notifications", ext=ext, query={"unread": "1" if unread else None, "limit": limit})

    def mark_read(self, ids: Optional[List[int]] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/notifications/read`` — ``ids`` omitted = every unread one."""
        return self._json(
            "/v1/notifications/read", ext=ext, method="POST", body={"ids": ids} if ids is not None else {}
        )
