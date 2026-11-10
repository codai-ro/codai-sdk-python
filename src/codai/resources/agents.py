"""``/v1/agents/*`` — synchronous runs and the persisted async run lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from .._http import HttpClient, RequestExtensions, frame_json
from ._base import Resource, enc, list_of

__all__ = ["Agents", "AgentRuns", "AgentRunResult"]


@dataclass
class AgentRunResult:
    result: str
    model: str
    event_id: Optional[str]
    usage: Optional[Dict[str, Any]] = field(default=None)
    raw: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)


class AgentRuns(Resource):
    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/agents/runs`` — 202 with the run ``id``."""
        return self._json("/v1/agents/runs", ext=ext, body=body)

    def get(self, id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/agents/runs/{id}``"""
        return self._json(f"/v1/agents/runs/{enc(id)}", ext=ext)

    def steps(self, id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/agents/runs/{id}/steps`` — newest first."""
        return list_of(self._json(f"/v1/agents/runs/{enc(id)}/steps", ext=ext), "steps")

    def stats(self, days: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/agents/runs/stats?days=``"""
        return self._json("/v1/agents/runs/stats", ext=ext, query={"days": days})

    def cancel(self, id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/agents/runs/{id}/cancel``"""
        return self._json(f"/v1/agents/runs/{enc(id)}/cancel", ext=ext, method="POST", body={})

    def stream(self, id: str, ext: Optional[RequestExtensions] = None) -> Iterator[Dict[str, Any]]:
        """``GET /v1/agents/runs/{id}/stream`` — yields ``{"event": "step"|"done"|"timeout", "data": {...}}``
        and stops after ``done`` / ``timeout``."""
        for frame in self._http.sse(f"/v1/agents/runs/{enc(id)}/stream", ext=ext):
            data = frame_json(frame)
            if not isinstance(data, dict):
                continue
            yield {"event": frame.event, "data": data}
            if frame.event in ("done", "timeout"):
                return


class Agents(Resource):
    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)
        self.runs = AgentRuns(http)

    def run(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> AgentRunResult:
        """``POST /v1/agents/run`` — blocks until the agent loop finishes."""
        res = self._http.request("/v1/agents/run", body=body, ext=ext)
        raw = res.json() or {}
        return AgentRunResult(
            result=str(raw.get("result") or ""),
            model=str(raw.get("model") or ""),
            event_id=raw.get("event_id") or res.header("x-codai-event-id"),
            usage=raw.get("usage"),
            raw=raw,
            headers=res.headers,
        )
