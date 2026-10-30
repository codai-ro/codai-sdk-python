"""``/v1/memory`` — your persistent memory (same store as the MCP memory tools)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Memory", "MEMORY_TIERS"]

MEMORY_TIERS = ("semantic", "episodic", "procedural", "graph")


class Memory(Resource):
    def list(
        self,
        tier: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/memory`` — ``{"memories": [...], "total"}``, newest first.

        ``limit`` 1–100 (default 20); ``tier`` one of ``semantic`` | ``episodic`` | ``procedural`` | ``graph``.
        Listing does not embed anything and is not metered.
        """
        return self._json("/v1/memory", ext=ext, query={"tier": tier, "limit": limit, "offset": offset})

    def search(self, q: str, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/memory/search`` — ``{"memories": [{id, tier, content, relevance}]}``, most relevant first.

        ``limit`` 1–10 (default 5). Embeds the query once (metered as ``memory:search``).
        """
        return self._json("/v1/memory/search", ext=ext, query={"q": q, "limit": limit})

    def create(
        self, content: str, importance: Optional[float] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/memory`` — store one semantic memory; returns ``{"id"}``.

        ``content`` ≤ 4000 chars, ``importance`` 0–1 (server default 0.6). Embeds once (``memory:create``).
        """
        body: Dict[str, Any] = {"content": content}
        if importance is not None:
            body["importance"] = importance
        return self._json("/v1/memory", ext=ext, method="POST", body=body)

    def delete(self, memory_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/memory/{id}`` — ``{"deleted": True}``; 404 when the id is unknown or not yours."""
        return self._json(f"/v1/memory/{enc(memory_id)}", ext=ext, method="DELETE")

    def delete_all(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/memory?confirm=all`` — erase EVERY memory of your account (all tiers). Irreversible.

        Returns ``{"deleted": {tier: n}, "total": n}``. Allowed on every plan.
        """
        return self._json("/v1/memory", ext=ext, method="DELETE", query={"confirm": "all"})
