"""codai Studio share links seen from the outside — read, remix and review a creative someone shared with you.

Every method takes the token or the whole link (``https://hub.codai.ro/s/<token>`` or ``…/r/<token>``). The public
routes (``/v1/public/studio/…``) ignore the API key; reviewers are identified only by the ``name`` they type (visible
to the owner and other reviewers). Owners create and revoke links with ``creatives.create_share`` /
``creatives.revoke_share``. Everything is free.
"""

from __future__ import annotations

import re
import urllib.parse
from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Shares", "share_token_from"]

_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{43}$")


def share_token_from(value: str) -> Optional[str]:
    """The share token in ``value``: a raw token, or any ``https://…/s/<token>`` / ``…/r/<token>`` URL (query and
    fragment ignored). Trims; ``None`` for anything else (same rule as the gateway and the apps)."""
    s = (value or "").strip()
    if _TOKEN_RE.match(s):
        return s
    try:
        url = urllib.parse.urlsplit(s)
    except ValueError:
        return None
    if url.scheme not in ("https", "http") or not url.netloc:
        return None
    parts = [p for p in url.path.split("/") if p]
    if len(parts) < 2:
        return None
    kind, token = parts[-2], parts[-1]
    return token if kind in ("s", "r") and _TOKEN_RE.match(token) else None


def _token(token_or_url: str) -> str:
    token = share_token_from(token_or_url)
    if token is None:
        raise ValueError("codai: not a share link or token (expected …/s/<token> or …/r/<token>)")
    return token


def _review(token_or_url: str, tail: str) -> str:
    return f"/v1/public/studio/reviews/{enc(_token(token_or_url))}{tail}"


def _thread(token_or_url: str, thread_id: str, tail: str) -> str:
    return _review(token_or_url, f"/threads/{enc(thread_id)}{tail}")


def _anchor(body: Dict[str, Any], node_id: Optional[str], scene_id: Optional[str], t_ms: Optional[int]) -> None:
    for key, value in (("node_id", node_id), ("scene_id", scene_id), ("t_ms", t_ms)):
        if value is not None:
            body[key] = value


class Shares(Resource):
    """Read, remix and review through share links."""

    def get(
        self,
        token_or_url: str,
        format: Optional[str] = None,  # noqa: A002 — mirrors the query parameter
        locale: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/public/studio/shares/{token}`` — title, kind, version, formats, locales and the compiled preview
        HTML of ``format`` / ``locale`` (``None`` for images); review links add ``review`` and ``threads``. 404 for
        unknown, revoked or expired links. No key needed."""
        path = f"/v1/public/studio/shares/{enc(_token(token_or_url))}"
        return self._json(path, ext=ext, query={"format": format, "locale": locale}) or {}

    def remix(
        self, token_or_url: str, title: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/studio/shares/{token}/remix`` — copy the version a ``view`` link shows into a new creative of
        yours (owner's ready assets copied, foreign brand kit dropped; HTTP 201) with ``remixed_from``. 404 for review
        links or links without remix; 413 ``remix_too_large``. Free."""
        body: Dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        path = f"/v1/studio/shares/{enc(_token(token_or_url))}/remix"
        return self._http.request(path, body=body, ext=ext, no_retry=True).json() or {}

    def comment(
        self,
        token_or_url: str,
        name: str,
        body: str,
        node_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        t_ms: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/public/studio/reviews/{token}/threads`` — start a thread as a reviewer (HTTP 201). 400
        ``invalid_name``; 409 ``too_many_comments``."""
        payload: Dict[str, Any] = {"name": name, "body": body}
        _anchor(payload, node_id, scene_id, t_ms)
        return self._http.request(_review(token_or_url, "/threads"), body=payload, ext=ext, no_retry=True).json() or {}

    def reply(
        self, token_or_url: str, thread_id: str, name: str, body: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST …/threads/{threadId}/replies`` — reply as a reviewer (HTTP 201); returns the whole thread."""
        path = _thread(token_or_url, thread_id, "/replies")
        return self._http.request(path, body={"name": name, "body": body}, ext=ext, no_retry=True).json() or {}

    def resolve(
        self, token_or_url: str, thread_id: str, name: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST …/threads/{threadId}/resolve`` — resolve a thread (``resolved_by`` = ``name``)."""
        return self._http.request(_thread(token_or_url, thread_id, "/resolve"), body={"name": name}, ext=ext).json() or {}

    def reopen(
        self, token_or_url: str, thread_id: str, name: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST …/threads/{threadId}/reopen`` — reopen a resolved thread."""
        return self._http.request(_thread(token_or_url, thread_id, "/reopen"), body={"name": name}, ext=ext).json() or {}

    def decide(
        self,
        token_or_url: str,
        name: str,
        decision: str,
        seq: int,
        note: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/public/studio/reviews/{token}/decision`` — ``decision`` ``approve`` | ``request_changes`` on the
        head ``seq`` (approver links only). 403 ``not_an_approver``, 409 ``review_not_open``, 409 ``stale`` (with
        ``head_seq``). Returns the new review state."""
        payload: Dict[str, Any] = {"name": name, "decision": decision, "seq": seq}
        if note is not None:
            payload["note"] = note
        return self._http.request(_review(token_or_url, "/decision"), body=payload, ext=ext, no_retry=True).json() or {}
