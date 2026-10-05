"""Core endpoints: embeddings, images, audio, ephemeral tokens, models, health."""

from __future__ import annotations

import base64
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from .._http import RequestExtensions, frame_json
from ._base import Resource, list_of

__all__ = [
    "Audio",
    "Embeddings",
    "EmbeddingsResult",
    "EphemeralToken",
    "Health",
    "Images",
    "ImagesResult",
    "Models",
    "SpeechResult",
    "SystemOne",
    "Tokens",
    "TranscriptionResult",
    "Verify",
]


# ---------------------------------------------------------------- embeddings
@dataclass
class EmbeddingsResult:
    embeddings: List[List[float]]
    raw: Dict[str, Any]
    routed_to: Optional[str]
    fallback: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


class Embeddings(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> EmbeddingsResult:
        """``POST /v1/embeddings`` — ``body`` has ``input`` (+ optional ``model``, ``dimensions``)."""
        payload = {**body, "model": body.get("model") or "codai-embed"}
        res = self._http.request("/v1/embeddings", body=payload, ext=ext)
        raw = res.json() or {}
        return EmbeddingsResult(
            embeddings=[list(d.get("embedding") or []) for d in raw.get("data") or []],
            raw=raw,
            routed_to=res.header("x-codai-routed-to"),
            fallback=res.header("x-codai-embed-fallback"),
            headers=res.headers,
        )


# ---------------------------------------------------------------- images
@dataclass
class ImagesResult:
    images: List[bytes]
    """Decoded image bytes, one per generated image (see ``mime_types``). Keep them as returned:
    images from the EU endpoint carry C2PA credentials + SynthID, and re-encoding strips C2PA."""
    raw: Dict[str, Any]
    routed_to: Optional[str]
    cost_micro_usd: Optional[int]
    """Usage-based charge for the request in micro-USD (``x-codai-cost-micro-usd``)."""
    headers: Dict[str, str] = field(default_factory=dict)
    mime_types: List[str] = field(default_factory=list)
    """MIME type of each entry in ``images`` (usually ``image/png``)."""
    data_region: Optional[str] = None
    """Vertex location that processed the request, ``eu`` or ``global`` (``x-codai-data-region``)."""


# Image generation typically takes 5-30 s (gateway upstream timeout 120 s); never cap below this.
_MIN_IMAGE_TIMEOUT = 150.0


class Images(Resource):
    def generate(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> ImagesResult:
        """``POST /v1/images/generations`` — ``body`` has ``prompt`` (+ optional ``model`` —
        ``codai-image`` (default, gemini-3.1-flash-image, EU), ``codai-image-fast``, ``codai-image-pro`` —
        ``n``, ``size``, ``aspect_ratio``, ``image_size``, ``negative_prompt``, and ``reference_images``:
        ``[{"b64_json": ..., "mime_type": "image/png"}]`` to keep a logo/palette/product consistent).
        Needs a real API key; ephemeral tokens are rejected."""
        return self._post("/v1/images/generations", body, ext)

    def edit(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> ImagesResult:
        """``POST /v1/images/edits`` (JSON body) — ``body`` has ``prompt`` and ``image`` (one
        ``{"b64_json": ..., "mime_type": ...}`` or a list of up to 14), plus the same optional fields as
        :meth:`generate`. ``mask`` is not supported: describe the region to change in ``prompt``."""
        return self._post("/v1/images/edits", body, ext)

    def _post(self, path: str, body: Dict[str, Any], ext: Optional[RequestExtensions]) -> ImagesResult:
        payload = {**body, "model": body.get("model") or "codai-image"}
        client_timeout = self._http.timeout
        timeout = client_timeout if not client_timeout else max(client_timeout, _MIN_IMAGE_TIMEOUT)
        res = self._http.request(path, body=payload, ext=ext, timeout=timeout)
        raw = res.json() or {}
        cost = res.header("x-codai-cost-micro-usd")
        data = raw.get("data") or []
        return ImagesResult(
            images=[base64.b64decode(d.get("b64_json") or "") for d in data],
            raw=raw,
            routed_to=res.header("x-codai-routed-to"),
            cost_micro_usd=int(cost) if cost is not None else None,
            headers=res.headers,
            mime_types=[d.get("mime_type") or "image/png" for d in data],
            data_region=res.header("x-codai-data-region"),
        )


# ---------------------------------------------------------------- system one
class SystemOne(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/systemone`` — typed decisions from codai-s1.

        ``body`` = ``{"state": ..., "questions": {id: {"type": "choice"|"score"|"noul", ...}}}``, or
        ``{"items": [{"id", "state"}], "questions": ...}`` for a batch (1-16 items → ``items[]``).
        Optional ``timeout_ms`` (100-5000) and ``fallback`` (``"codai-fast"``). Raises ``CodaiError``
        on 503 ``s1_unavailable``; keep a local fallback — the gateway substitutes a generative model
        only when ``fallback="codai-fast"`` is sent, and then the response has ``fallback_used: True``.
        """
        return self._http.request("/v1/systemone", body=body, ext=ext).json() or {}

    def batch(
        self,
        items: List[Dict[str, Any]],
        questions: Dict[str, Any],
        timeout_ms: Optional[int] = None,
        fallback: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """Same ``questions`` about up to 16 ``items`` (``[{"id", "state"}]``); returns ``{"items": [{"id", "answers"}], ...}``."""
        body: Dict[str, Any] = {"items": items, "questions": questions}
        if timeout_ms is not None:
            body["timeout_ms"] = timeout_ms
        if fallback is not None:
            body["fallback"] = fallback
        return self.create(body, ext)


# --------------------------------------------------------------------- audio
@dataclass
class TranscriptionResult:
    text: str
    raw: Dict[str, Any]
    routed_to: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class SpeechResult:
    audio: bytes
    content_type: str
    routed_to: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


def _multipart(fields: Dict[str, str], file_field: str, filename: str, file_bytes: bytes) -> "tuple[bytes, str]":
    boundary = f"----codai{int(time.time() * 1000)}"
    parts: List[bytes] = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    parts.append(
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; '
            f'filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'
        ).encode()
    )
    parts.append(file_bytes)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


class Audio(Resource):
    def transcribe(
        self,
        file: bytes,
        filename: str = "audio.webm",
        model: str = "codai-transcribe",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[float] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> str:
        """Speech-to-text (multipart, max 25 MB, never retried). Returns the transcript."""
        return self.transcribe_detailed(
            file, filename, model, language, prompt, response_format, temperature, ext
        ).text

    def transcribe_detailed(
        self,
        file: bytes,
        filename: str = "audio.webm",
        model: str = "codai-transcribe",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[float] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> TranscriptionResult:
        fields: Dict[str, str] = {"model": model}
        if language:
            fields["language"] = language
        if prompt:
            fields["prompt"] = prompt
        if response_format:
            fields["response_format"] = response_format
        if temperature is not None:
            fields["temperature"] = str(temperature)
        payload, content_type = _multipart(fields, "file", filename, file)
        res = self._http.request(
            "/v1/audio/transcriptions", method="POST", raw_body=payload, content_type=content_type, ext=ext
        )
        raw = res.json() or {}
        text = raw.get("text")
        return TranscriptionResult(
            text=text if isinstance(text, str) else "",
            raw=raw,
            routed_to=res.header("x-codai-routed-to"),
            headers=res.headers,
        )

    def speech(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> bytes:
        """Text-to-speech. ``body`` has ``input`` (+ ``model``, ``voice``, ``response_format``…). Returns audio bytes."""
        return self.speech_detailed(body, ext).audio

    def speech_detailed(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> SpeechResult:
        payload = {**body, "model": body.get("model") or "codai-tts", "voice": body.get("voice") or "alloy"}
        res = self._http.request("/v1/audio/speech", body=payload, ext=ext)
        return SpeechResult(
            audio=res.data,
            content_type=res.header("content-type") or "audio/mpeg",
            routed_to=res.header("x-codai-routed-to"),
            headers=res.headers,
        )

    def speech_stream(
        self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None
    ) -> Iterator[Dict[str, Any]]:
        """``POST /v1/audio/speech/stream`` — Azure neural TTS (``codai-tts-ro``) with lip-sync timing.

        ``body`` has ``input`` (+ ``voice``: ``alina`` (default) | ``emil`` | any Azure voice name,
        ``response_format``: ``pcm`` (default, PCM16 mono 24 kHz) | ``mp3``, ``speed`` 0.5-2.0).
        Yields ``{"type": "start"|"audio"|"viseme"|"word"|"done"|"error", ...}``; ``audio`` events
        also carry ``audio_bytes`` (the decoded ``delta``). Stops after ``done`` / ``error``.
        """
        payload = {**body, "model": body.get("model") or "codai-tts-ro"}
        for frame in self._http.sse("/v1/audio/speech/stream", method="POST", body=payload, ext=ext):
            data = frame_json(frame)
            if not isinstance(data, dict) or not isinstance(data.get("type"), str):
                continue
            if data["type"] == "audio" and isinstance(data.get("delta"), str):
                data["audio_bytes"] = base64.b64decode(data["delta"])
            yield data
            if data["type"] in ("done", "error"):
                return


# -------------------------------------------------------------------- tokens
@dataclass
class EphemeralToken:
    token: str
    expires_at: str
    scope: str
    raw: Dict[str, Any]


class Tokens(Resource):
    def create(
        self, scope: str, ttl_seconds: Optional[int] = None, ext: Optional[RequestExtensions] = None
    ) -> EphemeralToken:
        """``POST /v1/tokens`` — mint a 60–3600 s token bound to ``realtime`` | ``audio`` | ``embeddings``
        | ``live`` (realtime + audio in one token, for a live co-host's STT and TTS)."""
        body: Dict[str, Any] = {"scope": scope}
        if ttl_seconds is not None:
            body["ttl_seconds"] = ttl_seconds
        raw = self._json("/v1/tokens", ext=ext, body=body) or {}
        return EphemeralToken(
            token=str(raw.get("token") or ""),
            expires_at=str(raw.get("expires_at") or ""),
            scope=str(raw.get("scope") or scope),
            raw=raw,
        )


# -------------------------------------------------------------------- models
class Models(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/models`` — every model the calling key may address (``data[]``)."""
        return list_of(self._json("/v1/models", ext=ext), "data")


# -------------------------------------------------------------------- health
class Health(Resource):
    def get(self) -> Dict[str, Any]:
        """``GET /health`` — liveness."""
        return self._http.json("/health", no_retry=True)

    def ready(self) -> Dict[str, Any]:
        """``GET /health/ready`` — readiness; 503 is returned as a body with ``http_status``."""
        res = self._http.request("/health/ready", no_retry=True, accept_status=(503,))
        body = res.json() or {}
        body["http_status"] = res.status
        return body

    def status(self) -> Dict[str, Any]:
        """``GET /status`` — public provider status."""
        return self._http.json("/status", no_retry=True)


# ------------------------------------------------------------------- verify
class Verify(Resource):
    """EXPERIMENTAL, unaudited (HIDE protocol) verification of signed agent outputs.

    Provenance only, never authentication. Both endpoints are unauthenticated.
    """

    def agent_output_key(self) -> Dict[str, Any]:
        """``GET /v1/verify/agent-output/key`` — ``{"enabled": False, ...}`` when signing is off."""
        return self._http.json("/v1/verify/agent-output/key")

    def agent_output(self, payload: Dict[str, Any], signature: Dict[str, Any]) -> Dict[str, Any]:
        """``POST /v1/verify/agent-output`` — ``{"valid", "key_id", "reason"?}``; 503 ``signing_disabled``."""
        return self._http.json(
            "/v1/verify/agent-output",
            method="POST",
            body={"payload": payload, "signature": signature},
            no_retry=True,
        )
