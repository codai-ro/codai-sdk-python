"""Transcripts: ``/v1/transcripts/*``, ``/v1/transcript-folders``, ``/v1/transcript-vocabulary`` and the tus
``/v1/uploads`` endpoint — voice recordings → diarized RO/EN transcripts → insights (summary, key points, actions,
suggested agent prompts). Feature-flagged per account (404 until enabled). Bodies are snake_case."""

from __future__ import annotations

import base64
import re
import urllib.parse
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from .._http import CodaiError, RequestExtensions, frame_json
from ._base import Resource, enc

__all__ = [
    "Transcripts",
    "TranscriptFolders",
    "TranscriptShares",
    "TranscriptVocabulary",
    "Uploads",
    "upload_id_from_location",
]

TUS_HEADERS = {"Tus-Resumable": "1.0.0"}
TUS_CHUNK_BYTES = 8 * 1024 * 1024
BINARY_EXPORT_FORMATS = ("pdf", "docx")


def _one(transcript_id: str, suffix: str = "") -> str:
    return f"/v1/transcripts/{enc(transcript_id)}{suffix}"


def _ext(ext: Optional[RequestExtensions], headers: Dict[str, str]) -> RequestExtensions:
    """Merge raw tus headers into an extensions bag (``headers`` key)."""
    merged: Dict[str, Any] = dict(ext or {})
    merged["headers"] = {**(merged.get("headers") or {}), **headers}
    return merged  # type: ignore[return-value]


def upload_id_from_location(location: str) -> str:
    """Last path segment of a tus ``Location`` header (absolute or relative)."""
    path = re.sub(r"[?#].*$", "", location).rstrip("/")
    upload_id = urllib.parse.unquote(path[path.rfind("/") + 1 :])
    if not upload_id:
        raise CodaiError(f"tus: no upload id in Location {location}", 0, None)
    return upload_id


class TranscriptFolders(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/transcript-folders``."""
        return self._json("/v1/transcript-folders", ext=ext)

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/transcript-folders`` — upsert on ``name``."""
        return self._json("/v1/transcript-folders", ext=ext, method="POST", body=body)

    def update(self, folder_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/transcript-folders/{id}``."""
        return self._json(f"/v1/transcript-folders/{enc(folder_id)}", ext=ext, method="PATCH", body=body)

    def delete(self, folder_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/transcript-folders/{id}`` — transcripts stay, ``folder_id`` cleared."""
        self._http.request(f"/v1/transcript-folders/{enc(folder_id)}", ext=ext, method="DELETE")


class TranscriptVocabulary(Resource):
    def get(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/transcript-vocabulary``."""
        return self._json("/v1/transcript-vocabulary", ext=ext)

    def put(self, terms: List[str], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PUT /v1/transcript-vocabulary`` — replaces the whole list."""
        return self._json("/v1/transcript-vocabulary", ext=ext, method="PUT", body={"terms": terms})


class TranscriptShares(Resource):
    def create(
        self,
        transcript_id: str,
        expires_in_days: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/transcripts/{id}/shares`` → ``{id, token, url, expiresAt}``. Read-only public link
        (``https://hub.codai.ro/t/<token>``); the token/url are returned ONCE (only a hash is stored).
        Omit ``expires_in_days`` (1..365) for a link that never expires."""
        body: Dict[str, Any] = {} if expires_in_days is None else {"expiresInDays": int(expires_in_days)}
        return self._json(_one(transcript_id, "/shares"), ext=ext, method="POST", body=body, no_retry=True)

    def list(self, transcript_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/transcripts/{id}/shares`` — active links; ``url`` is always ``None`` (token not recoverable)."""
        return self._json(_one(transcript_id, "/shares"), ext=ext)["data"]

    def revoke(self, transcript_id: str, share_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/transcripts/{id}/shares/{shareId}`` — the public URL answers 404 from then on."""
        self._http.request(_one(transcript_id, f"/shares/{enc(share_id)}"), ext=ext, method="DELETE")


class Uploads(Resource):
    def capabilities(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``OPTIONS /v1/uploads`` — tus version, extensions and max size (from headers)."""
        res = self._http.request("/v1/uploads", ext=_ext(ext, TUS_HEADERS), method="OPTIONS")
        max_size = res.header("tus-max-size")
        return {
            "version": res.header("tus-version"),
            "extensions": [s.strip() for s in (res.header("tus-extension") or "").split(",") if s.strip()],
            "max_size": int(max_size) if max_size else None,
        }

    def create(
        self, length: Optional[int], metadata: Dict[str, str], ext: Optional[RequestExtensions] = None
    ) -> str:
        """``POST /v1/uploads`` — tus creation; returns the upload id."""
        headers = dict(TUS_HEADERS)
        if length is None:
            headers["Upload-Defer-Length"] = "1"
        else:
            headers["Upload-Length"] = str(length)
        md = ",".join(f"{k} {base64.b64encode(v.encode('utf-8')).decode('ascii')}" for k, v in metadata.items())
        if md:
            headers["Upload-Metadata"] = md
        res = self._http.request("/v1/uploads", ext=_ext(ext, headers), method="POST", raw_body=b"", no_retry=True)
        loc = res.header("location")
        if not loc:
            raise CodaiError("tus: create response has no Location header", res.status, None)
        return upload_id_from_location(loc)

    def offset(self, upload_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Optional[int]]:
        """tus ``HEAD /v1/uploads/{id}`` — bytes the server holds (resume point)."""
        res = self._http.request(f"/v1/uploads/{enc(upload_id)}", ext=_ext(ext, TUS_HEADERS), method="HEAD")
        length = res.header("upload-length")
        return {"offset": int(res.header("upload-offset") or 0), "length": int(length) if length else None}

    def append(
        self,
        upload_id: str,
        offset: int,
        chunk: bytes,
        length: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> int:
        """tus ``PATCH /v1/uploads/{id}`` — append one chunk at ``offset``; returns the new offset."""
        headers = {**TUS_HEADERS, "Upload-Offset": str(offset)}
        if length is not None:
            headers["Upload-Length"] = str(length)
        res = self._http.request(
            f"/v1/uploads/{enc(upload_id)}",
            ext=_ext(ext, headers),
            method="PATCH",
            raw_body=bytes(chunk),
            content_type="application/offset+octet-stream",
        )
        nxt = int(res.header("upload-offset") or -1)
        if nxt <= offset:
            raise CodaiError(f"tus: server offset {nxt} did not advance past {offset}", res.status, None)
        return nxt


class Transcripts(Resource):
    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.folders = TranscriptFolders(http)
        self.vocabulary = TranscriptVocabulary(http)
        self.uploads = Uploads(http)
        self.shares = TranscriptShares(http)

    def list(
        self,
        folder_id: Optional[str] = None,
        tag: Optional[str] = None,
        pinned: Optional[bool] = None,
        status: Optional[str] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/transcripts`` — pinned first, newest next; page with ``next_cursor``."""
        query = {
            "folder_id": folder_id,
            "tag": tag,
            "pinned": None if pinned is None else ("true" if pinned else "false"),
            "status": status,
            "cursor": cursor,
            "limit": limit,
        }
        return self._json("/v1/transcripts", ext=ext, query=query)

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/transcripts`` — status ``recording``; idempotent on ``client_id``."""
        return self._json("/v1/transcripts", ext=ext, method="POST", body=body)

    def get(self, transcript_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/transcripts/{id}`` — speakers, utterances (word timings), bookmarks, latest insights."""
        return self._json(_one(transcript_id), ext=ext)

    def update(self, transcript_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/transcripts/{id}`` — setting ``title`` locks it."""
        return self._json(_one(transcript_id), ext=ext, method="PATCH", body=body)

    def delete(self, transcript_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/transcripts/{id}`` — row + audio objects."""
        self._http.request(_one(transcript_id), ext=ext, method="DELETE")

    def finalize(self, transcript_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/transcripts/{id}/finalize`` — attach tus uploads + bookmarks → ``queued`` (202)."""
        return self._json(_one(transcript_id, "/finalize"), ext=ext, method="POST", body=body)

    def retranscribe(self, transcript_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/transcripts/{id}/retranscribe`` (not retried)."""
        return self._json(_one(transcript_id, "/retranscribe"), ext=ext, method="POST", body={}, no_retry=True)

    def reanalyze(self, transcript_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/transcripts/{id}/reanalyze`` — new insights version (not retried)."""
        return self._json(_one(transcript_id, "/reanalyze"), ext=ext, method="POST", body={}, no_retry=True)

    def publish_live(self, transcript_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> None:
        """``POST /v1/transcripts/{id}/live`` — the recording device's live caption, fanned out to viewers (204)."""
        self._json(_one(transcript_id, "/live"), ext=ext, method="POST", body=body)

    def add_bookmark(self, transcript_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/transcripts/{id}/bookmarks``."""
        return self._json(_one(transcript_id, "/bookmarks"), ext=ext, method="POST", body=body)

    def rename_speaker(
        self, transcript_id: str, label: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PATCH /v1/transcripts/{id}/speakers/{label}`` — name a speaker / mark yourself (``is_owner``)."""
        return self._json(_one(transcript_id, f"/speakers/{enc(label)}"), ext=ext, method="PATCH", body=body)

    def edit_utterance(
        self, transcript_id: str, seq: int, text: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PATCH /v1/transcripts/{id}/utterances/{seq}`` — correct one utterance."""
        return self._json(_one(transcript_id, f"/utterances/{int(seq)}"), ext=ext, method="PATCH", body={"text": text})

    def audio(self, transcript_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/transcripts/{id}/audio`` — signed playback URLs per track (empty after the 30-day retention)."""
        return self._json(_one(transcript_id, "/audio"), ext=ext)

    def export(self, transcript_id: str, format: str = "md", ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/transcripts/{id}/export?format=md|txt|srt|vtt|json|pdf|docx``. Text formats →
        ``{text, filename, content_type}``; ``pdf`` / ``docx`` → ``{bytes, filename, content_type}``."""
        res = self._http.request(_one(transcript_id, "/export"), ext=ext, query={"format": format})
        m = re.search(r"filename\*=UTF-8''([^;]+)", res.header("content-disposition") or "", re.I)
        filename = urllib.parse.unquote(m.group(1)) if m else None
        if format in BINARY_EXPORT_FORMATS:
            return {"bytes": bytes(res.data), "filename": filename, "content_type": res.header("content-type")}
        return {"text": res.data.decode("utf-8"), "filename": filename, "content_type": res.header("content-type")}

    def public_view(self, token: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/public/transcripts/{token}`` — read-only view behind a share link (no key required; 404 for
        unknown / expired / revoked links)."""
        return self._json(f"/v1/public/transcripts/{enc(token)}", ext=ext)

    def accept_prompt(self, transcript_id: str, index: int, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/transcripts/{id}/prompts/{index}/accept`` — suggested agent prompt → pending prompt."""
        return self._json(_one(transcript_id, f"/prompts/{int(index)}/accept"), ext=ext, method="POST", body={}, no_retry=True)

    def usage(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/transcripts/usage`` — this month's allowance."""
        return self._json("/v1/transcripts/usage", ext=ext)

    def search(
        self,
        q: str,
        mode: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/transcripts/search`` — full-text (+ semantic in ``hybrid``)."""
        return self._json("/v1/transcripts/search", ext=ext, query={"q": q, "mode": mode, "limit": limit})

    def ask(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/transcripts/ask`` — answer across your recordings with ``[n]`` citations (not retried)."""
        return self._json("/v1/transcripts/ask", ext=ext, method="POST", body=body, no_retry=True)

    def stream(self, ext: Optional[RequestExtensions] = None) -> Iterator[Dict[str, Any]]:
        """``GET /v1/transcripts/stream`` — yields ``{"op", "id", "status"?, "progress"?, "title"?}`` per
        ``transcript`` event (keepalives skipped). The server closes after 55 min."""
        for frame in self._http.sse("/v1/transcripts/stream", ext=ext):
            if frame.event != "transcript":
                continue
            data = frame_json(frame)
            if isinstance(data, dict):
                yield data

    def upload_audio(
        self,
        data: Union[bytes, bytearray, memoryview],
        track: str = "mic",
        transcript_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        chunk_size: int = TUS_CHUNK_BYTES,
        upload_id: Optional[str] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> str:
        """Upload one audio track with tus 1.0 (resumable): creates the upload (or resumes ``upload_id`` from the
        server's offset), PATCHes ≤ 8 MB chunks and returns the upload id to pass to ``finalize``."""
        raw = bytes(data)
        total = len(raw)
        chunk = max(1, min(chunk_size, TUS_CHUNK_BYTES))
        offset = 0
        if upload_id:
            offset = int(self.uploads.offset(upload_id, ext=ext)["offset"] or 0)
        else:
            md = {"track": track}
            if transcript_id:
                md["transcript"] = transcript_id
            if duration_ms is not None:
                md["durationMs"] = str(duration_ms)
            upload_id = self.uploads.create(total, md, ext=ext)
        if on_progress:
            on_progress(offset, total)
        while offset < total:
            offset = self.uploads.append(upload_id, offset, raw[offset : offset + chunk], ext=ext)
            if on_progress:
                on_progress(offset, total)
        return upload_id
