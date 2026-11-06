"""``POST /v1/public/provenance/check`` — check a file for the AI-provenance marks codai writes (C2PA manifest presence
and claimed issuer, WAV RIFF INFO, MP3 ID3 TXXX, MP4 udta/meta, image XMP). Public: the route does not require the key;
the file is not stored. C2PA signatures are not verified and SynthID is never checked (see the result flags). Free."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Union

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["Provenance", "PROVENANCE_MAX_BYTES"]

#: Largest file the checker accepts (25 MB).
PROVENANCE_MAX_BYTES = 25 * 1024 * 1024


class Provenance(Resource):
    """Public AI-provenance checker."""

    def check(
        self,
        file: Union[bytes, str, "os.PathLike[str]"],
        content_type: str = "application/octet-stream",
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Upload ``file`` (bytes or a path; PNG, JPEG, WebP, WAV, MP3 or MP4, at most 25 MB) and return
        ``{media_type, findings, codai_generated, synthid_checked, signature_verified}``. Never retried."""
        if isinstance(file, (bytes, bytearray)):
            data = bytes(file)
        else:
            with open(file, "rb") as fh:
                data = fh.read()
        return (
            self._http.request(
                "/v1/public/provenance/check",
                method="POST",
                raw_body=data,
                content_type=content_type,
                ext=ext,
                no_retry=True,
            ).json()
            or {}
        )
