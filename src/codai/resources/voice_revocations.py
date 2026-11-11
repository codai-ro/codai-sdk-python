"""``POST /v1/studio/voice-revocations`` — ask for a voice cloned in codai Studio to be taken down (for people without
a codai account). Public: the route does not require the key; nothing in the request is echoed back. Free."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["VoiceRevocations"]


class VoiceRevocations(Resource):
    """Public takedown tickets for cloned voices."""

    def create(
        self,
        email: str,
        voice_owner_name: str,
        details: str,
        evidence_url: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Store a takedown ticket for manual review (HTTP 202): ``{id, object, status}``. Never retried."""
        body: Dict[str, Any] = {"email": email, "voice_owner_name": voice_owner_name, "details": details}
        if evidence_url is not None:
            body["evidence_url"] = evidence_url
        return self._http.request("/v1/studio/voice-revocations", body=body, ext=ext, no_retry=True).json() or {}
