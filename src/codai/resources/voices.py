"""``client.voices`` — codai Studio custom voices, D37 voice passport (beta): the SEPARATE, revocable consent that
lets your own custom voice sing in your Music Room songs. The consent is recorded in the app (a ``purpose: singing``
recording session: the singing statement read aloud + a sung sample); these calls arm and revoke it. The sung result
approximates your timbre; it is not a faithful clone. Only where voice cloning is enabled for the account. Free."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["Voices"]


def _singing(voice_id: str) -> str:
    return f"/v1/studio/voices/{enc(voice_id)}/singing-consent"


class Voices(Resource):
    """Custom voices: the voice passport singing consent."""

    def add_singing_consent(
        self, voice_id: str, session_id: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/studio/voices/{id}/singing-consent`` — add the singing purpose from a finished singing recording
        session (liveness-checked statement + sung sample). Returns the voice with ``singing.status == "active"``.
        Never retried."""
        return (
            self._http.request(
                _singing(voice_id), ext=ext, method="POST", body={"session_id": session_id}, no_retry=True
            ).json()
            or {}
        )

    def revoke_singing_consent(self, voice_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/studio/voices/{id}/singing-consent`` — revoke ONLY the singing purpose (204). The sung sample is
        deleted at once; the voice keeps working for narration. Idempotent."""
        self._http.request(_singing(voice_id), ext=ext, method="DELETE")
