"""``/v1/usage`` + ``/v1/keys`` — the caller's own usage breakdown and API keys (device attribution, tags)."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Usage", "Keys", "USAGE_QUERY_KEYS"]

USAGE_QUERY_KEYS = ("from", "to", "group_by", "key", "device", "app", "platform", "model", "tag")


class Usage(Resource):
    def get(
        self, query: Optional[Mapping[str, Any]] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/usage`` — ``{"from", "to", "group_by", "key", "device", "app", "platform", "model", "tag"}``.

        ``from`` / ``to`` are inclusive ``YYYY-MM-DD`` UTC dates (default: last 30 days; at most 400).
        ``group_by``: ``day`` (default) | ``key`` | ``device`` | ``app`` | ``platform`` | ``model`` | ``client`` | ``tag``.
        Each row's ``cost_micro_usd`` is USD micros as a string — never converted.
        """
        q = query or {}
        unknown = sorted(set(q) - set(USAGE_QUERY_KEYS))
        if unknown:
            raise ValueError(f"usage.get: unknown query keys {unknown}")
        return self._json("/v1/usage", ext=ext, query={k: q.get(k) for k in USAGE_QUERY_KEYS})


class Keys(Resource):
    def list(self, include_revoked: bool = False, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/keys`` — your keys (never the secret); ``current: True`` marks the calling key."""
        return self._json("/v1/keys", ext=ext, query={"include_revoked": "true" if include_revoked else None})

    def set_tags(self, key_id: str, tags: List[str], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/keys/{id}`` — replace the key's tags (≤ 16, each ≤ 32 chars; ``[]`` clears)."""
        return self._json(f"/v1/keys/{enc(key_id)}", ext=ext, method="PATCH", body={"tags": list(tags)})
