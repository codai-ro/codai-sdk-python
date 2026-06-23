"""codai — official Python SDK for the codai AI gateway.

Zero-dependency (stdlib urllib) client mirroring @codai/sdk:

    from codai import Codai

    client = Codai(api_key="ck-...", session_id="my-session")
    result = client.chat([{"role": "user", "content": "hello"}])
    print(result.content, result.routed_to)

    for delta in client.chat_stream([{"role": "user", "content": "hi"}]):
        print(delta, end="")

    run = client.agents_run("summarize the repo structure")
    client.feedback(result.request_id, 1)

Memory tools (memory_recall/memory_remember) and skills are GATEWAY-NATIVE:
pass a stable session_id and the model uses them server-side.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional

__all__ = ["Codai", "CodaiError", "ChatResult", "AgentRunResult"]
__version__ = "0.1.0"

_RETRYABLE = {429, 500, 502, 503, 504}


class CodaiError(Exception):
    def __init__(self, message: str, status: int = 0, body: Any = None) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


@dataclass
class ChatResult:
    content: str
    raw: Dict[str, Any]
    request_id: Optional[str]
    routed_to: Optional[str]
    exec_verify: Optional[str]
    usage: Optional[Dict[str, int]]


@dataclass
class AgentRunResult:
    result: str
    model: str
    event_id: Optional[str]
    usage: Optional[Dict[str, Any]] = field(default=None)


class Codai:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://ai.codai.ro",
        session_id: Optional[str] = None,
        timeout: float = 120.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError("Codai: api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session_id = session_id
        self.timeout = timeout
        self.max_retries = max_retries

    # ------------------------------------------------------------- chat
    def chat(
        self,
        messages: List[Dict[str, Any]],
        model: str = "codai",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        agent_mode: bool = False,
        compact: Optional[str] = None,
        best_of: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> ChatResult:
        body: Dict[str, Any] = {"model": model, "messages": messages, "stream": False}
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if tools:
            body["tools"] = tools
        headers = self._chat_headers(agent_mode, compact, best_of, session_id)
        status, resp_headers, data = self._request(
            "/v1/chat/completions", body, extra_headers=headers
        )
        raw = json.loads(data)
        choices = raw.get("choices") or []
        usage_raw = raw.get("usage") or {}
        return ChatResult(
            content=str((choices[0].get("message") or {}).get("content") or "")
            if choices
            else "",
            raw=raw,
            request_id=resp_headers.get("x-request-id"),
            routed_to=resp_headers.get("x-codai-routed-to"),
            exec_verify=resp_headers.get("x-codai-exec-verify"),
            usage=(
                {
                    "prompt_tokens": int(usage_raw.get("prompt_tokens") or 0),
                    "completion_tokens": int(usage_raw.get("completion_tokens") or 0),
                }
                if usage_raw
                else None
            ),
        )

    def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str = "codai",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        agent_mode: bool = False,
        session_id: Optional[str] = None,
    ) -> Generator[str, None, None]:
        body: Dict[str, Any] = {"model": model, "messages": messages, "stream": True}
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        headers = self._chat_headers(agent_mode, None, None, session_id)
        req = self._build_request("/v1/chat/completions", body, headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                buffer = b""
                for chunk in iter(lambda: resp.read(1024), b""):
                    buffer += chunk
                    while b"\n\n" in buffer:
                        frame, buffer = buffer.split(b"\n\n", 1)
                        for line in frame.split(b"\n"):
                            if not line.startswith(b"data:"):
                                continue
                            payload = line[5:].strip()
                            if payload == b"[DONE]":
                                return
                            try:
                                parsed = json.loads(payload)
                                delta = (
                                    (parsed.get("choices") or [{}])[0]
                                    .get("delta", {})
                                    .get("content")
                                )
                                if delta:
                                    yield delta
                            except json.JSONDecodeError:
                                continue
        except urllib.error.HTTPError as e:  # pragma: no cover
            raise CodaiError(f"codai stream → {e.code}", e.code, e.read()) from e

    # ------------------------------------------------------------ agents
    def agents_run(
        self,
        task: str,
        context: Optional[str] = None,
        system: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AgentRunResult:
        body: Dict[str, Any] = {"task": task}
        if context:
            body["context"] = context
        if system:
            body["system"] = system
        if model:
            body["model"] = model
        _, _, data = self._request("/v1/agents/run", body)
        raw = json.loads(data)
        return AgentRunResult(
            result=str(raw.get("result") or ""),
            model=str(raw.get("model") or ""),
            event_id=raw.get("event_id"),
            usage=raw.get("usage"),
        )

    # ---------------------------------------------------------- feedback
    def feedback(self, request_id: str, rating: int, comment: Optional[str] = None) -> None:
        body: Dict[str, Any] = {"event_id": request_id, "rating": rating}
        if comment:
            body["comment"] = comment
        self._request("/v1/feedback", body)

    # ------------------------------------------------------------ models
    def models(self) -> List[Dict[str, Any]]:
        _, _, data = self._request("/v1/models", None, method="GET")
        return json.loads(data).get("data") or []

    # ------------------------------------------------------------ tokens
    def mint_token(self, scope: str, ttl_seconds: Optional[int] = None) -> Dict[str, Any]:
        """Mint an ephemeral scoped token ('realtime'|'audio'|'embeddings').

        Returns {"token", "expires_at", "scope"}. Hand the token to a
        browser/webview client; it expires in 60-3600s and only works on
        its scope's surface.
        """
        body: Dict[str, Any] = {"scope": scope}
        if ttl_seconds is not None:
            body["ttl_seconds"] = ttl_seconds
        _, _, data = self._request("/v1/tokens", body)
        return json.loads(data)

    # -------------------------------------------------------- embeddings
    def embeddings(
        self,
        input: Any,
        model: str = "codai-embed",
        dimensions: Optional[int] = None,
    ) -> List[List[float]]:
        body: Dict[str, Any] = {"model": model, "input": input}
        if dimensions is not None:
            body["dimensions"] = dimensions
        _, _, data = self._request("/v1/embeddings", body)
        return [d["embedding"] for d in json.loads(data).get("data") or []]

    # ------------------------------------------------------------- audio
    def transcribe(
        self,
        file_bytes: bytes,
        filename: str = "audio.webm",
        model: str = "codai-transcribe",
    ) -> str:
        """Speech-to-text via multipart upload (max 25 MB). Returns transcript."""
        boundary = f"----codai{int(time.time() * 1000)}"
        parts = []
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{model}\r\n".encode()
        )
        parts.append(
            (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
                f"filename=\"{filename}\"\r\nContent-Type: application/octet-stream\r\n\r\n"
            ).encode()
        )
        parts.append(file_bytes)
        parts.append(f"\r\n--{boundary}--\r\n".encode())
        payload = b"".join(parts)
        req = urllib.request.Request(
            f"{self.base_url}/v1/audio/transcriptions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return str(json.loads(resp.read()).get("text") or "")
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read())
            except Exception:  # noqa: BLE001
                err_body = None
            raise CodaiError(f"codai /v1/audio/transcriptions → {e.code}", e.code, err_body) from e

    def speech(
        self,
        input: str,
        model: str = "codai-tts",
        voice: str = "alloy",
    ) -> bytes:
        """Text-to-speech. Returns audio bytes (default mp3)."""
        _, _, data = self._request(
            "/v1/audio/speech", {"model": model, "input": input, "voice": voice}
        )
        return data

    # ---------------------------------------------------------- internal
    def _chat_headers(
        self,
        agent_mode: bool,
        compact: Optional[str],
        best_of: Optional[int],
        session_id: Optional[str],
    ) -> Dict[str, str]:
        h: Dict[str, str] = {}
        session = session_id or self.session_id
        if session:
            h["x-codai-session-id"] = session
        if agent_mode:
            h["x-codai-mode"] = "agent"
        if compact:
            h["x-codai-compact"] = compact
        if best_of is not None:
            h["x-codai-best-of"] = str(best_of)
        return h

    def _build_request(
        self, path: str, body: Any, extra_headers: Optional[Dict[str, str]] = None, method: str = "POST"
    ) -> urllib.request.Request:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        headers.update(extra_headers or {})
        return urllib.request.Request(
            f"{self.base_url}{path}", data=data, headers=headers, method=method
        )

    def _request(
        self, path: str, body: Any, extra_headers: Optional[Dict[str, str]] = None, method: str = "POST"
    ) -> tuple:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            req = self._build_request(path, body, extra_headers, method)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.status, dict(resp.headers), resp.read()
            except urllib.error.HTTPError as e:
                if e.code in _RETRYABLE and attempt < self.max_retries:
                    time.sleep(0.5 * 2**attempt)
                    continue
                try:
                    err_body = json.loads(e.read())
                except Exception:  # noqa: BLE001
                    err_body = None
                raise CodaiError(f"codai {path} → {e.code}", e.code, err_body) from e
            except Exception as e:  # noqa: BLE001 — network-level
                last_err = e
                if attempt < self.max_retries:
                    time.sleep(0.5 * 2**attempt)
                    continue
        raise CodaiError(f"codai {path} failed after retries: {last_err}")
