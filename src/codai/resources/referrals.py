"""``client.referrals`` — ``GET /v1/referrals``; redeem / consent go through ``PATCH /v1/account``.

Mirrors ``packages/sdk/src/resources/referrals.ts``.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["Referrals"]


class Referrals(Resource):
    def get(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/referrals`` — stats, redeem deadline and invitees (masked, no PII)."""
        return self._json("/v1/referrals", ext=ext)

    def redeem(self, code: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """Redeem a referrer's code (their username) — ``PATCH /v1/account {"referral_code"}``.
        Allowed within 7 days of signup; the outcome is in ``referral_result``."""
        return self._json("/v1/account", ext=ext, method="PATCH", body={"referral_code": code})

    def set_consent(self, consent: bool, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """Opt in/out of the referral programme — ``PATCH /v1/account {"referral_consent"}``."""
        return self._json("/v1/account", ext=ext, method="PATCH", body={"referral_consent": bool(consent)})
