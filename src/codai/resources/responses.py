"""``POST /v1/responses`` — OpenAI Responses wire (JSON + ``response.*`` SSE)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from .._http import HttpClient, RequestExtensions, frame_json, read_sse
from ._base import Resource, request_id_of

__all__ = ["Responses", "ResponsesResult", "ResponsesStream", "ResponsesStreamResult"]


@dataclass
class ResponsesResult:
    output_text: str
    raw: Dict[str, Any]
    request_id: Optional[str]
    routed_to: Optional[str]
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class ResponsesStreamResult:
    output_text: str
    response: Optional[Dict[str, Any]]
    request_id: Optional[str]
    routed_to: Optional[str]
    headers: Dict[str, str]


class ResponsesStream:
    """Iterator of ``response.*`` events; ``text()`` yields output-text deltas; ``final`` after."""

    def __init__(self, http: HttpClient, body: Dict[str, Any], ext: Optional[RequestExtensions]) -> None:
        self._http = http
        self._body = body
        self._ext = ext
        self._consumed = False
        self.final: Optional[ResponsesStreamResult] = None

    def events(self) -> Iterator[Dict[str, Any]]:
        if self._consumed:
            raise RuntimeError("ResponsesStream can only be iterated once")
        self._consumed = True
        resp = self._http.open("/v1/responses", body=self._body, ext=self._ext, timeout=0, no_retry=True)
        headers = {k.lower(): v for k, v in dict(resp.headers).items()}
        text: List[str] = []
        response: Optional[Dict[str, Any]] = None
        try:
            for frame in read_sse(resp):
                ev = frame_json(frame)
                if not isinstance(ev, dict):
                    continue
                if not isinstance(ev.get("type"), str):
                    ev["type"] = frame.event
                kind = ev["type"]
                if kind == "response.output_text.delta" and isinstance(ev.get("delta"), str):
                    text.append(ev["delta"])
                elif kind == "response.completed" and isinstance(ev.get("response"), dict):
                    response = ev["response"]
                yield ev
                if kind == "response.completed":
                    break
        finally:
            resp.close()
            self.final = ResponsesStreamResult(
                output_text="".join(text),
                response=response,
                request_id=headers.get("x-codai-trace-id") or headers.get("x-request-id"),
                routed_to=headers.get("x-codai-routed-to"),
                headers=headers,
            )

    def text(self) -> Iterator[str]:
        for ev in self.events():
            if ev.get("type") == "response.output_text.delta" and isinstance(ev.get("delta"), str):
                yield ev["delta"]

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return self.events()


class Responses(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> ResponsesResult:
        payload = {**body, "model": body.get("model") or "codai", "stream": False}
        res = self._http.request("/v1/responses", body=payload, ext=ext)
        raw = res.json() or {}
        out = raw.get("output_text")
        return ResponsesResult(
            output_text=out if isinstance(out, str) else "",
            raw=raw,
            request_id=request_id_of(res),
            routed_to=res.header("x-codai-routed-to"),
            headers=res.headers,
        )

    def stream(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> ResponsesStream:
        payload = {**body, "model": body.get("model") or "codai", "stream": True}
        return ResponsesStream(self._http, payload, ext)
