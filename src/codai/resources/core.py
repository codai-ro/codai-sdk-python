"""Core endpoints: embeddings, audio, ephemeral tokens, models, health."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .._http import RequestExtensions
from ._base import Resource, list_of

__all__ = [
    "Audio",
    "Embeddings",
    "EmbeddingsResult",
    "EphemeralToken",
    "Health",
    "Models",
    "SpeechResult",
    "SystemOne",
    "Tokens",
    "TranscriptionResult",
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


# ---------------------------------------------------------------- system one
class SystemOne(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/systemone`` — typed decisions from codai-s1.

        ``body`` = ``{"state": ..., "questions": {id: {"type": "choice"|"score"|"noul", ...}}}``.
        Raises ``CodaiError`` on 503 ``s1_unavailable``; keep a local fallback — the gateway never
        substitutes a generative model.
        """
        return self._http.request("/v1/systemone", body=body, ext=ext).json() or {}


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
        """``POST /v1/tokens`` — mint a 60–3600 s token bound to ``realtime`` | ``audio`` | ``embeddings``."""
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
