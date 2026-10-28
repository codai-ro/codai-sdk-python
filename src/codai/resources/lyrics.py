"""``/v1/studio/lyrics`` — codai Studio lyrics writer and karaoke alignment (MU-06).

``write`` turns a brief into original lyrics in Romanian or English (one bounded ``codai`` turn, checked line by line
for syllables and the rhyme scheme; one repair turn when more than 30 % of the lines miss). Token-metered
(``codai::lyrics``) under a small wallet hold. ``align`` matches written lyrics to the word timestamps of one clip of
an audio / video creative and writes the timed lines with one ``setLyrics`` edit (``apply=False`` only returns them),
plus an LRC file; cached clip words are free, a fresh transcription bills ``codai::lyrics-align``. Both honour
``Idempotency-Key``; alignment is 403 ``residency_unavailable`` for EU data-residency accounts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["Lyrics"]

_BASE = "/v1/studio/lyrics"


def _idem(key: Optional[str], ext: Optional[RequestExtensions]) -> Optional[Dict[str, Any]]:
    if not key:
        return dict(ext) if ext else None
    merged: Dict[str, Any] = dict(ext or {})
    merged["headers"] = {**dict(merged.get("headers") or {}), "Idempotency-Key": key}
    return merged


def _compact(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


class Lyrics(Resource):
    """Write song lyrics and align them to an audio clip."""

    def write(
        self,
        brief: str,
        language: str,
        *,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        structure: Optional[Sequence[str]] = None,
        syllables_per_line: Optional[int] = None,
        rhyme_scheme: Optional[str] = None,
        lines_per_section: Optional[int] = None,
        title: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/lyrics`` — a ``studio.lyrics``: ``sections`` (every line with ``syllables``, ``rhyme``,
        ``letter``, ``off``), the whole song as ``text`` (``[kind]`` headers), a ``report`` and ``repaired``.
        ``language`` is ``ro`` or ``en``; ``rhyme_scheme`` ``AABB`` | ``ABAB`` | ``free`` (default)."""
        structure_list: Optional[List[str]] = list(structure) if structure is not None else None
        body = _compact(
            {
                "brief": brief,
                "language": language,
                "genre": genre,
                "mood": mood,
                "structure": structure_list,
                "syllables_per_line": syllables_per_line,
                "rhyme_scheme": rhyme_scheme,
                "lines_per_section": lines_per_section,
                "title": title,
            }
        )
        return (
            self._json(
                _BASE, ext=_idem(idempotency_key, ext), method="POST", body=body, no_retry=not idempotency_key
            )
            or {}
        )

    def align(
        self,
        creative_id: str,
        clip_id: str,
        lyrics_text: str,
        *,
        language: Optional[str] = None,
        apply: Optional[bool] = None,
        base_seq: Optional[int] = None,
        retranscribe: Optional[bool] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/studio/lyrics/align`` — a ``studio.lyrics_alignment``: timed ``lines``, ``lrc``,
        ``match_ratio``, ``cached`` and, when applied, ``seq`` / ``doc_hash`` of the new version."""
        body = _compact(
            {
                "creative_id": creative_id,
                "clip_id": clip_id,
                "lyrics_text": lyrics_text,
                "language": language,
                "apply": apply,
                "base_seq": base_seq,
                "retranscribe": retranscribe,
            }
        )
        return (
            self._json(
                f"{_BASE}/align",
                ext=_idem(idempotency_key, ext),
                method="POST",
                body=body,
                no_retry=not idempotency_key,
            )
            or {}
        )
