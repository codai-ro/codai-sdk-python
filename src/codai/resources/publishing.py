"""``/v1/studio/connections`` + ``/v1/studio/publish`` — codai Studio direct publishing (SX-30).

Connect a YouTube channel (Google OAuth with PKCE) and upload a finished video render with the fields the person
approved. Privacy and made-for-kids are never defaulted. Free. Until codai enables publishing,
:meth:`Publishing.list_connections` reports ``enabled: False`` and connect / draft / publish answer 404 ``not_found``.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import quote

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["Publishing"]


def _q(value: str) -> str:
    return quote(str(value), safe="")


class Publishing(Resource):
    """Connections (list / start / exchange / delete) and publications (draft / create / retrieve / cancel)."""

    def list_connections(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/connections`` — ``{enabled, data}``; ``enabled`` is false while publishing is off."""
        return self._json("/v1/studio/connections", ext=ext) or {}

    def start_connection(self, platform: str = "youtube", ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/connections/{platform}/start`` — ``authorize_url``, ``state``, ``code_verifier``
        (send the last two to :meth:`exchange_connection` within 10 minutes)."""
        return self._json(f"/v1/studio/connections/{_q(platform)}/start", ext=ext, method="POST", body={}, no_retry=True) or {}

    def exchange_connection(
        self,
        code: str,
        state: str,
        code_verifier: str,
        platform: str = "youtube",
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/connections/{platform}/exchange`` — finish the flow with the code from the redirect."""
        body = {"code": code, "state": state, "code_verifier": code_verifier}
        return (
            self._json(f"/v1/studio/connections/{_q(platform)}/exchange", ext=ext, method="POST", body=body, no_retry=True)
            or {}
        )

    def delete_connection(self, connection_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/studio/connections/{id}`` — revoke at Google, delete tokens, cancel queued uploads."""
        return self._json(f"/v1/studio/connections/{_q(connection_id)}", ext=ext, method="DELETE") or {}

    def draft(
        self,
        render_id: str,
        title: str,
        description: Optional[str] = None,
        hashtags: Optional[List[str]] = None,
        language: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/publish/draft`` — pre-filled fields + AI disclosure; nothing is uploaded."""
        body: Dict[str, Any] = {"render_id": render_id, "title": title}
        if description is not None:
            body["description"] = description
        if hashtags is not None:
            body["hashtags"] = hashtags
        if language is not None:
            body["language"] = language
        return self._json("/v1/studio/publish/draft", ext=ext, method="POST", body=body) or {}

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/publish`` (202) — ``render_id``, ``connection_id``, ``title``, ``privacy``,
        ``made_for_kids``, ``contains_synthetic_media`` required; retried only with ``client_request_id``."""
        no_retry = not body.get("client_request_id")
        return self._json("/v1/studio/publish", ext=ext, method="POST", body=body, no_retry=no_retry) or {}

    def retrieve(self, publication_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/studio/publish/{id}`` — phase, progress, link, error."""
        return self._json(f"/v1/studio/publish/{_q(publication_id)}", ext=ext) or {}

    def cancel(self, publication_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/studio/publish/{id}/cancel`` — only before the upload starts."""
        return (
            self._json(f"/v1/studio/publish/{_q(publication_id)}/cancel", ext=ext, method="POST", body={}, no_retry=True)
            or {}
        )
