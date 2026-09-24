"""``POST /v1/messages`` — Anthropic Messages wire (JSON + named-event SSE)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from .._http import HttpClient, RequestExtensions, frame_json, read_sse
from ._base import Resource, request_id_of

__all__ = ["Messages", "MessageResult", "MessageStream", "MessageStreamResult"]


@dataclass
class MessageResult:
    text: str
    raw: Dict[str, Any]
    request_id: Optional[str]
    routed_to: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class MessageStreamResult:
    text: str
    stop_reason: Optional[str]
    usage: Optional[Dict[str, int]]
    request_id: Optional[str]
    routed_to: Optional[str]
    headers: Dict[str, str]


class MessageStream:
    """Iterator of Anthropic stream events (dicts with ``type``); ``text()`` yields
    ``text_delta`` payloads only; ``final`` is set once the stream ends."""

    def __init__(self, http: HttpClient, body: Dict[str, Any], ext: Optional[RequestExtensions]) -> None:
        self._http = http
        self._body = body
        self._ext = ext
        self._consumed = False
        self.final: Optional[MessageStreamResult] = None

    def events(self) -> Iterator[Dict[str, Any]]:
        if self._consumed:
            raise RuntimeError("MessageStream can only be iterated once")
        self._consumed = True
        resp = self._http.open("/v1/messages", body=self._body, ext=self._ext, timeout=0, no_retry=True)
        headers = {k.lower(): v for k, v in dict(resp.headers).items()}
        text: List[str] = []
        stop_reason: Optional[str] = None
        input_tokens = 0
        output_tokens = 0
        saw_usage = False
        try:
            for frame in read_sse(resp):
                ev = frame_json(frame)
                if not isinstance(ev, dict):
                    continue
                if not isinstance(ev.get("type"), str):
                    ev["type"] = frame.event
                kind = ev["type"]
                if kind == "message_start":
                    usage = (ev.get("message") or {}).get("usage") or {}
                    if usage:
                        saw_usage = True
                        input_tokens = int(usage.get("input_tokens") or 0)
                        output_tokens = int(usage.get("output_tokens") or 0)
                elif kind == "content_block_delta":
                    delta = ev.get("delta") or {}
                    if delta.get("type") == "text_delta" and isinstance(delta.get("text"), str):
                        text.append(delta["text"])
                elif kind == "message_delta":
                    delta = ev.get("delta") or {}
                    if delta.get("stop_reason"):
                        stop_reason = delta["stop_reason"]
                    usage = ev.get("usage") or {}
                    if usage:
                        saw_usage = True
                        output_tokens = int(usage.get("output_tokens") or output_tokens)
                yield ev
                if kind == "message_stop":
                    break
        finally:
            resp.close()
            self.final = MessageStreamResult(
                text="".join(text),
                stop_reason=stop_reason,
                usage={"input_tokens": input_tokens, "output_tokens": output_tokens} if saw_usage else None,
                request_id=headers.get("x-codai-trace-id") or headers.get("x-request-id"),
                routed_to=headers.get("x-codai-routed-to"),
                headers=headers,
            )

    def text(self) -> Iterator[str]:
        for ev in self.events():
            if ev.get("type") == "content_block_delta":
                delta = ev.get("delta") or {}
                if delta.get("type") == "text_delta" and isinstance(delta.get("text"), str):
                    yield delta["text"]

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return self.events()


class Messages(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> MessageResult:
        payload = {**body, "model": body.get("model") or "codai", "stream": False}
        res = self._http.request("/v1/messages", body=payload, ext=ext)
        raw = res.json() or {}
        text = "".join(
            b.get("text", "")
            for b in raw.get("content") or []
            if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)
        )
        return MessageResult(
            text=text,
            raw=raw,
            request_id=request_id_of(res),
            routed_to=res.header("x-codai-routed-to"),
            headers=res.headers,
        )

    def stream(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> MessageStream:
        payload = {**body, "model": body.get("model") or "codai", "stream": True}
        return MessageStream(self._http, payload, ext)
