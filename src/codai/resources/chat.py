"""``POST /v1/chat/completions`` — OpenAI Chat Completions wire (JSON + SSE)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from .._http import HttpClient, RequestExtensions, frame_json, read_sse
from ._base import Resource, request_id_of

__all__ = ["Chat", "ChatCompletions", "ChatResult", "ChatStream", "ChatStreamResult", "merge_tool_call"]


@dataclass
class ChatResult:
    content: str
    raw: Dict[str, Any]
    request_id: Optional[str]
    routed_to: Optional[str]
    exec_verify: Optional[str]
    usage: Optional[Dict[str, int]]
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    event_id: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class ChatStreamResult:
    content: str
    tool_calls: List[Dict[str, Any]]
    request_id: Optional[str]
    routed_to: Optional[str]
    exec_verify: Optional[str]
    usage: Optional[Dict[str, int]]
    finish_reason: Optional[str]
    headers: Dict[str, str]


def _to_usage(u: Any) -> Optional[Dict[str, int]]:
    if not isinstance(u, dict):
        return None
    out = {
        "prompt_tokens": int(u.get("prompt_tokens") or 0),
        "completion_tokens": int(u.get("completion_tokens") or 0),
    }
    details = u.get("prompt_tokens_details")
    if isinstance(details, dict) and details.get("cached_tokens") is not None:
        out["cached_tokens"] = int(details["cached_tokens"])
    return out


def merge_tool_call(acc: Dict[int, Dict[str, Any]], index: int, fragment: Dict[str, Any]) -> None:
    """Merge one streamed ``tool_calls`` delta into the accumulator (arguments concatenate)."""
    existing = acc.setdefault(index, {"index": index})
    for key, val in fragment.items():
        if key == "index":
            continue
        if key == "function" and isinstance(val, dict):
            fn = existing.get("function") or {}
            for fk, fv in val.items():
                if fk == "arguments":
                    fn["arguments"] = str(fn.get("arguments") or "") + str(fv or "")
                else:
                    fn[fk] = fv
            existing["function"] = fn
        else:
            existing[key] = val


class ChatStream:
    """Iterator of text deltas; ``chunks()`` yields the raw ``chat.completion.chunk``
    dicts; ``final`` holds the aggregated result once the stream is exhausted."""

    def __init__(self, http: HttpClient, body: Dict[str, Any], ext: Optional[RequestExtensions]) -> None:
        self._http = http
        self._body = body
        self._ext = ext
        self._consumed = False
        self.final: Optional[ChatStreamResult] = None

    def chunks(self) -> Iterator[Dict[str, Any]]:
        if self._consumed:
            raise RuntimeError("ChatStream can only be iterated once")
        self._consumed = True
        resp = self._http.open("/v1/chat/completions", body=self._body, ext=self._ext, timeout=0, no_retry=True)
        headers = {k.lower(): v for k, v in dict(resp.headers).items()}
        content: List[str] = []
        tool_calls: Dict[int, Dict[str, Any]] = {}
        usage: Optional[Dict[str, int]] = None
        finish_reason: Optional[str] = None
        try:
            for frame in read_sse(resp):
                if frame.data == "[DONE]":
                    break
                chunk = frame_json(frame)
                if not isinstance(chunk, dict):
                    continue
                if chunk.get("usage"):
                    usage = _to_usage(chunk["usage"])
                choices = chunk.get("choices") or []
                choice = choices[0] if choices else {}
                if choice.get("finish_reason"):
                    finish_reason = choice["finish_reason"]
                delta = choice.get("delta") or {}
                for tc in delta.get("tool_calls") or []:
                    idx = tc.get("index")
                    merge_tool_call(tool_calls, idx if isinstance(idx, int) else 0, tc)
                if delta.get("content"):
                    content.append(delta["content"])
                yield chunk
        finally:
            resp.close()
            self.final = ChatStreamResult(
                content="".join(content),
                tool_calls=[tool_calls[k] for k in sorted(tool_calls)],
                request_id=headers.get("x-codai-trace-id") or headers.get("x-request-id"),
                routed_to=headers.get("x-codai-routed-to"),
                exec_verify=headers.get("x-codai-exec-verify"),
                usage=usage,
                finish_reason=finish_reason,
                headers=headers,
            )

    def text(self) -> Iterator[str]:
        for chunk in self.chunks():
            choices = chunk.get("choices") or []
            delta = (choices[0].get("delta") or {}) if choices else {}
            if delta.get("content"):
                yield delta["content"]

    def __iter__(self) -> Iterator[str]:
        return self.text()


class ChatCompletions(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> ChatResult:
        """Non-streaming completion. ``body`` is the OpenAI request (``model`` defaults to ``codai``)."""
        payload = {**body, "model": body.get("model") or "codai", "stream": False}
        res = self._http.request("/v1/chat/completions", body=payload, ext=ext)
        raw = res.json() or {}
        choices = raw.get("choices") or []
        message = (choices[0].get("message") or {}) if choices else {}
        content = message.get("content")
        return ChatResult(
            content=content if isinstance(content, str) else "",
            tool_calls=list(message.get("tool_calls") or []),
            raw=raw,
            request_id=request_id_of(res),
            event_id=res.header("x-codai-event-id"),
            routed_to=res.header("x-codai-routed-to"),
            exec_verify=res.header("x-codai-exec-verify"),
            usage=_to_usage(raw.get("usage")),
            headers=res.headers,
        )

    def stream(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> ChatStream:
        """Streaming completion: iterate for text deltas, ``.chunks()`` for raw chunks, ``.final`` after."""
        payload = {**body, "model": body.get("model") or "codai", "stream": True}
        return ChatStream(self._http, payload, ext)


class Chat(Resource):
    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)
        self.completions = ChatCompletions(http)
