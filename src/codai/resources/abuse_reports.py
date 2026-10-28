"""``POST /v1/studio/abuse-reports`` — report illegal or abusive content seen on a codai Studio share (``/s/<token>``)
or review (``/r/<token>``) link (DSA art. 16 notice). Public: the route does not require the key; an unknown link still
answers 202 (no enumeration). Free."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["AbuseReports"]


class AbuseReports(Resource):
    """Public abuse reports about codai Studio share / review links."""

    def create(
        self,
        share_token: str,
        surface: str,
        category: str,
        explanation: str,
        reporter_name: str,
        reporter_email: str,
        good_faith: bool = True,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Store an abuse report for manual review (HTTP 202): ``{id, object, status}``. Never retried.

        ``surface`` is ``"share"`` or ``"review"``; ``category`` one of ``voice_without_consent``, ``impersonation``,
        ``fraud``, ``election``, ``illegal_other``, ``other``. ``good_faith`` must be ``True`` (the route rejects
        anything else with 400).
        """
        body: Dict[str, Any] = {
            "share_token": share_token,
            "surface": surface,
            "category": category,
            "explanation": explanation,
            "reporter_name": reporter_name,
            "reporter_email": reporter_email,
            "good_faith": good_faith,
        }
        return self._http.request("/v1/studio/abuse-reports", body=body, ext=ext, no_retry=True).json() or {}
