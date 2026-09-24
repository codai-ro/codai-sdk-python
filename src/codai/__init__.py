"""codai — official Python SDK for the codai AI gateway.

Zero-dependency (stdlib urllib) client mirroring the TypeScript ``codai-sdk``:

    from codai import Codai

    client = Codai(api_key="codai_...", session_id="my-session")

    # resource groups — one method per gateway operation
    result = client.chat.completions.create({"messages": [{"role": "user", "content": "hello"}]})
    print(result.content, result.routed_to)

    for delta in client.chat.completions.stream({"messages": [{"role": "user", "content": "hi"}]}):
        print(delta, end="")

    run = client.agents.runs.create({"task": "summarize the repo structure"})
    for ev in client.agents.runs.stream(run["id"]):
        print(ev["event"], ev["data"])

    # 0.1.x convenience methods keep working
    result = client.chat([{"role": "user", "content": "hello"}])
    client.feedback(result.request_id, 1)

Every method takes an optional ``ext={...}`` bag of ``X-Codai-*`` extension
headers (``effort``, ``thinking``, ``cache``, ``device``, ``compact``, ...).
Memory tools and skills are GATEWAY-NATIVE: pass a stable ``session_id`` and
the model uses them server-side.
"""

from __future__ import annotations

from typing import Any, Dict, Generator, List, Optional

from ._http import CodaiError, HttpClient, RequestExtensions, SseFrame, extension_headers, frame_json, read_sse
from ._operations import OPERATION_METHODS, STREAMING_OPERATIONS
from .resources import (
    Account,
    AgentRunResult,
    Agents,
    Audio,
    Chat,
    ChatResult,
    ChatStream,
    Devices,
    Embeddings,
    EphemeralToken,
    Feedback,
    Health,
    Hosts,
    Messages,
    Models,
    Orgs,
    PhoneModels,
    Receipts,
    Responses,
    Sessions,
    Tasks,
    Tokens,
    Tools,
)

__all__ = [
    "Codai",
    "CodaiError",
    "ChatResult",
    "ChatStream",
    "AgentRunResult",
    "EphemeralToken",
    "HttpClient",
    "RequestExtensions",
    "SseFrame",
    "OPERATION_METHODS",
    "STREAMING_OPERATIONS",
    "extension_headers",
    "frame_json",
    "read_sse",
]
__version__ = "0.2.1"


class _CallableGroup:
    """A resource group that is also callable — keeps ``client.chat(...)``,
    ``client.embeddings(...)``, ``client.models()`` and ``client.feedback(...)``
    from 0.1.x working while exposing the new sub-methods as attributes."""

    def __init__(self, target: Any, fn: Any) -> None:
        self._target = target
        self._fn = fn

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._fn(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._target, name)


class Codai:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://ai.codai.ro",
        session_id: Optional[str] = None,
        timeout: float = 120.0,
        max_retries: int = 2,
        device: Optional[str] = None,
        device_name: Optional[str] = None,
        device_platform: Optional[str] = None,
        client: Optional[str] = None,
        defaults: Optional[RequestExtensions] = None,
        opener: Any = None,
    ) -> None:
        if not api_key:
            raise ValueError("Codai: api_key is required")
        merged: Dict[str, Any] = dict(defaults or {})
        for key, value in (
            ("session_id", session_id),
            ("device", device),
            ("device_name", device_name),
            ("device_platform", device_platform),
            ("client", client),
        ):
            if value:
                merged[key] = value
        self.http = HttpClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            defaults=merged,
            opener=opener,
        )
        http = self.http

        self.messages = Messages(http)
        self.responses = Responses(http)
        self.audio = Audio(http)
        self.tokens = Tokens(http)
        self.health = Health(http)
        self.agents = Agents(http)
        self.tools = Tools(http)
        self.tasks = Tasks(http)
        self.sessions = Sessions(http)
        self.devices = Devices(http)
        self.hosts = Hosts(http)
        self.orgs = Orgs(http)
        self.account = Account(http)
        self.receipt = Receipts(http)
        self.phone_models = PhoneModels(http)

        self.chat: Any = _CallableGroup(Chat(http), self._legacy_chat)
        self.embeddings: Any = _CallableGroup(Embeddings(http), self._legacy_embeddings)
        self.models: Any = _CallableGroup(Models(http), self._legacy_models)
        self.feedback: Any = _CallableGroup(Feedback(http), self._legacy_feedback)

    # ------------------------------------------------------------ 0.1.x API
    @property
    def api_key(self) -> str:
        return self.http.api_key

    @property
    def base_url(self) -> str:
        return self.http.base_url

    @property
    def session_id(self) -> Optional[str]:
        return self.http.defaults.get("session_id")

    @property
    def timeout(self) -> float:
        return self.http.timeout

    @property
    def max_retries(self) -> int:
        return self.http.max_retries

    def _legacy_chat(
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
        ext: Optional[RequestExtensions] = None,
    ) -> ChatResult:
        body = self._legacy_body(messages, model, temperature, max_tokens, tools)
        return self.chat.completions.create(
            body, ext=self._legacy_ext(agent_mode, compact, best_of, session_id, ext)
        )

    def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str = "codai",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        agent_mode: bool = False,
        session_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Generator[str, None, None]:
        """Streaming chat — generator of text deltas (0.1.x shape).
        ``chat.completions.stream()`` also exposes raw chunks and ``.final``."""
        body = self._legacy_body(messages, model, temperature, max_tokens, None)
        stream: ChatStream = self.chat.completions.stream(
            body, ext=self._legacy_ext(agent_mode, None, None, session_id, ext)
        )
        yield from stream.text()

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
        return self.agents.run(body)

    def _legacy_feedback(self, request_id: str, rating: int, comment: Optional[str] = None) -> None:
        body: Dict[str, Any] = {"event_id": request_id, "rating": rating}
        if comment:
            body["comment"] = comment
        self.feedback.submit(body)

    def _legacy_models(self) -> List[Dict[str, Any]]:
        return self.models.list()

    def mint_token(self, scope: str, ttl_seconds: Optional[int] = None) -> Dict[str, Any]:
        """Mint an ephemeral scoped token; returns ``{"token", "expires_at", "scope"}`` (0.1.x shape)."""
        return self.tokens.create(scope, ttl_seconds).raw

    def _legacy_embeddings(
        self,
        input: Any,
        model: str = "codai-embed",
        dimensions: Optional[int] = None,
    ) -> List[List[float]]:
        body: Dict[str, Any] = {"model": model, "input": input}
        if dimensions is not None:
            body["dimensions"] = dimensions
        return self.embeddings.create(body).embeddings

    def transcribe(
        self,
        file_bytes: bytes,
        filename: str = "audio.webm",
        model: str = "codai-transcribe",
    ) -> str:
        """Speech-to-text via multipart upload (max 25 MB). Returns transcript."""
        return self.audio.transcribe(file_bytes, filename=filename, model=model)

    def speech(
        self,
        input: str,
        model: str = "codai-tts",
        voice: str = "alloy",
    ) -> bytes:
        """Text-to-speech. Returns audio bytes (default mp3)."""
        return self.audio.speech({"model": model, "input": input, "voice": voice})

    # ---------------------------------------------------------- internal
    @staticmethod
    def _legacy_body(
        messages: List[Dict[str, Any]],
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        tools: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"model": model, "messages": messages}
        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if tools:
            body["tools"] = tools
        return body

    @staticmethod
    def _legacy_ext(
        agent_mode: bool,
        compact: Optional[str],
        best_of: Optional[int],
        session_id: Optional[str],
        ext: Optional[RequestExtensions],
    ) -> Dict[str, Any]:
        out: Dict[str, Any] = dict(ext or {})
        if session_id:
            out["session_id"] = session_id
        if agent_mode:
            out["mode"] = "agent"
        if compact:
            out["compact"] = compact
        if best_of is not None:
            out["best_of"] = best_of
        return out
