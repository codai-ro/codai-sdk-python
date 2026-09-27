"""Shared HTTP layer for every resource: base URL, bearer auth, ``X-Codai-*``
extension headers, retries, timeouts, JSON + SSE helpers and the ``CodaiError``
mapping of the gateway error envelope. stdlib only (``urllib``)."""

from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterator, Mapping, Optional, Tuple, Union

__all__ = [
    "CodaiError",
    "HttpClient",
    "HttpResponse",
    "RequestExtensions",
    "SseFrame",
    "extension_headers",
    "frame_json",
    "read_sse",
]

_RETRYABLE = {429, 500, 502, 503, 504}

# Per-request extension bag key → request header (values sent verbatim, booleans → 1/0).
EXTENSION_HEADERS: Dict[str, str] = {
    "session_id": "x-codai-session-id",
    "request_id": "x-request-id",
    "effort": "x-codai-effort",
    "thinking": "x-codai-thinking",
    "thinking_budget": "x-codai-thinking-budget",
    "thinking_pin": "x-codai-thinking-pin",
    "cache": "x-codai-cache",
    "no_task": "x-codai-no-task",
    "task_id": "x-codai-task-id",
    "task_outcome": "x-codai-task-outcome",
    "task_evidence": "x-codai-task-evidence",
    "client": "x-codai-client",
    "incognito": "x-codai-incognito",
    "no_recall": "x-codai-no-recall",
    "proven_only": "x-codai-proven-only",
    "new_session": "x-codai-new-session",
    "repo": "x-codai-repo",
    "agent_id": "x-codai-agent-id",
    "disable_subagents": "x-codai-disable-subagents",
    "mode": "x-codai-mode",
    "server_tools": "x-codai-server-tools",
    "orchestrate": "x-codai-orchestrate",
    "cascade": "x-codai-cascade",
    "best_of": "x-codai-best-of",
    "best_of_depth": "x-codai-best-of-depth",
    "reflect": "x-codai-reflect",
    "step_verify": "x-codai-step-verify",
    "plan": "x-codai-plan",
    "consensus": "x-codai-consensus",
    "compact": "x-codai-compact",
    "retrieval": "x-codai-retrieval",
    "heuristics": "x-codai-heuristics",
    "identity": "x-codai-identity",
    "playbook": "x-codai-playbook",
    "no_playbook": "x-codai-no-playbook",
    "debug": "x-codai-debug",
    "device": "x-codai-device",
    "device_name": "x-codai-device-name",
    "device_platform": "x-codai-device-platform",
    "push_token": "x-codai-push-token",
    "share_token": "x-codai-share-token",
}

RequestExtensions = Mapping[str, Any]
"""Extension bag: any key of ``EXTENSION_HEADERS`` (snake_case) plus an optional
``headers`` dict of raw extra headers. Mirrors ``CodaiRequestExtensions`` in the
TypeScript SDK (``session_id`` ↔ ``sessionId``)."""


def extension_headers(ext: Optional[RequestExtensions]) -> Dict[str, str]:
    """Translate an extensions bag into raw ``X-Codai-*`` headers."""
    out: Dict[str, str] = {}
    if not ext:
        return out
    for key, header in EXTENSION_HEADERS.items():
        value = ext.get(key)
        if value is None:
            continue
        if isinstance(value, bool):
            out[header] = "1" if value else "0"
        elif key == "compact" and value == "auto":
            out[header] = "1"
        else:
            out[header] = str(value)
    extra = ext.get("headers")
    if extra:
        out.update({str(k): str(v) for k, v in dict(extra).items()})
    unknown = [k for k in ext if k not in EXTENSION_HEADERS and k != "headers"]
    if unknown:
        raise ValueError(f"Codai: unknown extension option(s): {', '.join(sorted(unknown))}")
    return out


class CodaiError(Exception):
    """Non-2xx gateway response (after retries), or a network failure (``status == 0``)."""

    def __init__(
        self,
        message: str,
        status: int = 0,
        body: Any = None,
        code: Optional[str] = None,
        request_id: Optional[str] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.body = body
        self.code = code if code is not None else _extract_code(body)
        self.request_id = request_id
        self.retry_after = retry_after


def _extract_code(body: Any) -> Optional[str]:
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict) and isinstance(err.get("code"), str):
            return err["code"]
    return None


def _extract_message(body: Any) -> Optional[str]:
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict) and isinstance(err.get("message"), str):
            return err["message"]
    return None


class HttpResponse:
    """A completed (buffered) response: ``status``, lower-cased ``headers``, raw ``data``."""

    def __init__(self, status: int, headers: Mapping[str, str], data: bytes) -> None:
        self.status = status
        self.headers: Dict[str, str] = {k.lower(): v for k, v in headers.items()}
        self.data = data

    def json(self) -> Any:
        return json.loads(self.data.decode("utf-8")) if self.data else None

    def header(self, name: str) -> Optional[str]:
        return self.headers.get(name.lower())

    @property
    def request_id(self) -> Optional[str]:
        return self.header("x-codai-trace-id") or self.header("x-request-id")


class SseFrame:
    """One SSE frame: ``event`` (``message`` when the frame has none) and the joined ``data``."""

    __slots__ = ("event", "data")

    def __init__(self, event: str, data: str) -> None:
        self.event = event
        self.data = data

    def __repr__(self) -> str:  # pragma: no cover
        return f"SseFrame(event={self.event!r}, data={self.data[:60]!r})"


def frame_json(frame: SseFrame) -> Any:
    """Parse a frame's data as JSON; ``None`` for ``[DONE]`` / non-JSON payloads."""
    if frame.data == "[DONE]":
        return None
    try:
        return json.loads(frame.data)
    except ValueError:
        return None


def _parse_sse_block(block: str) -> Optional[SseFrame]:
    event = "message"
    data = []
    for line in block.split("\n"):
        if not line or line.startswith(":"):
            continue
        if line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            payload = line[5:]
            data.append(payload[1:] if payload.startswith(" ") else payload)
    if not data:
        return None
    return SseFrame(event, "\n".join(data))


def read_sse(raw: Any, chunk_size: int = 1024) -> Iterator[SseFrame]:
    """Iterate SSE frames from a file-like ``read(n)`` body (CRLF normalised)."""
    buffer = ""
    decoder_tail = b""
    while True:
        chunk = raw.read(chunk_size)
        if not chunk:
            break
        chunk = decoder_tail + chunk
        try:
            text = chunk.decode("utf-8")
            decoder_tail = b""
        except UnicodeDecodeError as e:
            text = chunk[: e.start].decode("utf-8")
            decoder_tail = chunk[e.start :]
        buffer += text.replace("\r\n", "\n")
        while "\n\n" in buffer:
            block, buffer = buffer.split("\n\n", 1)
            frame = _parse_sse_block(block)
            if frame is not None:
                yield frame
    if buffer.strip():
        frame = _parse_sse_block(buffer)
        if frame is not None:
            yield frame


Query = Optional[Mapping[str, Union[str, int, float, bool, None]]]


class HttpClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://ai.codai.ro",
        timeout: float = 120.0,
        max_retries: int = 2,
        defaults: Optional[RequestExtensions] = None,
        opener: Optional[urllib.request.OpenerDirector] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.defaults: Dict[str, Any] = dict(defaults or {})
        self._opener = opener or urllib.request.build_opener()

    # ------------------------------------------------------------------ url
    def url(self, path: str, query: Query = None) -> str:
        url = f"{self.base_url}{path}"
        if query:
            items = []
            for key, value in query.items():
                if value is None:
                    continue
                if isinstance(value, bool):
                    value = "1" if value else "0"
                items.append((key, str(value)))
            if items:
                url += "?" + urllib.parse.urlencode(items)
        return url

    def headers(self, ext: Optional[RequestExtensions] = None, json_body: bool = True) -> Dict[str, str]:
        h = {"Authorization": f"Bearer {self.api_key}"}
        if json_body:
            h["Content-Type"] = "application/json"
        h.update(extension_headers(self.defaults))
        h.update(extension_headers(ext))
        return h

    # -------------------------------------------------------------- request
    def _build(
        self,
        path: str,
        method: str,
        query: Query,
        body: Any,
        raw_body: Optional[bytes],
        content_type: Optional[str],
        ext: Optional[RequestExtensions],
    ) -> urllib.request.Request:
        has_json = body is not None
        headers = self.headers(ext, json_body=has_json)
        data: Optional[bytes] = None
        if has_json:
            data = json.dumps(body).encode("utf-8")
        elif raw_body is not None:
            data = raw_body
            if content_type:
                headers["Content-Type"] = content_type
        return urllib.request.Request(self.url(path, query), data=data, headers=headers, method=method)

    def open(
        self,
        path: str,
        method: Optional[str] = None,
        body: Any = None,
        query: Query = None,
        ext: Optional[RequestExtensions] = None,
        raw_body: Optional[bytes] = None,
        content_type: Optional[str] = None,
        timeout: Optional[float] = None,
        no_retry: bool = False,
        accept_status: Tuple[int, ...] = (),
    ) -> Any:
        """Perform a request and return the open ``http.client.HTTPResponse``
        (the caller reads / closes it). Raises ``CodaiError`` on non-2xx after
        retries on 429 / 5xx (multipart bodies and streams are never retried)."""
        method = method or ("POST" if body is not None or raw_body is not None else "GET")
        retries = 0 if (no_retry or raw_body is not None) else self.max_retries
        effective_timeout = self.timeout if timeout is None else timeout
        last_err: Optional[BaseException] = None
        for attempt in range(retries + 1):
            req = self._build(path, method, query, body, raw_body, content_type, ext)
            try:
                kwargs: Dict[str, Any] = {}
                if effective_timeout and effective_timeout > 0:
                    kwargs["timeout"] = effective_timeout
                return self._opener.open(req, **kwargs)
            except urllib.error.HTTPError as e:
                if e.code in accept_status:
                    return e
                if e.code in _RETRYABLE and attempt < retries:
                    e.close()
                    time.sleep(0.5 * 2**attempt + random.random() * 0.25)
                    continue
                raise self._to_error(path, e) from e
            except CodaiError:
                raise
            except Exception as e:  # noqa: BLE001 — network-level (URLError, timeout, reset)
                last_err = e
                if attempt < retries:
                    time.sleep(0.5 * 2**attempt)
                    continue
        raise CodaiError(f"codai {path} failed after retries: {last_err}", 0, None)

    def request(self, path: str, **kwargs: Any) -> HttpResponse:
        """Perform a request and buffer the whole body."""
        resp = self.open(path, **kwargs)
        try:
            data = resp.read()
            return HttpResponse(resp.status if hasattr(resp, "status") else resp.code, dict(resp.headers), data)
        finally:
            resp.close()

    def json(self, path: str, **kwargs: Any) -> Any:
        return self.request(path, **kwargs).json()

    def sse(self, path: str, **kwargs: Any) -> Iterator[SseFrame]:
        """Open a ``text/event-stream`` and yield parsed frames until the server closes."""
        kwargs.setdefault("timeout", 0)
        kwargs["no_retry"] = True
        resp = self.open(path, **kwargs)
        try:
            for frame in read_sse(resp):
                yield frame
        finally:
            resp.close()

    def sse_with_response(self, path: str, **kwargs: Any) -> Tuple[Any, Iterator[SseFrame]]:
        """Like ``sse`` but also returns the raw response (for headers) before iterating."""
        kwargs.setdefault("timeout", 0)
        kwargs["no_retry"] = True
        resp = self.open(path, **kwargs)

        def frames() -> Iterator[SseFrame]:
            try:
                for frame in read_sse(resp):
                    yield frame
            finally:
                resp.close()

        return resp, frames()

    # ---------------------------------------------------------------- errors
    @staticmethod
    def _to_error(path: str, e: urllib.error.HTTPError) -> CodaiError:
        body: Any = None
        try:
            raw = e.read()
            body = json.loads(raw) if raw else None
        except Exception:  # noqa: BLE001 — non-JSON error body
            body = None
        finally:
            e.close()
        headers = {k.lower(): v for k, v in dict(e.headers or {}).items()}
        retry_raw = headers.get("retry-after")
        retry_after = int(retry_raw) if retry_raw and retry_raw.isdigit() else None
        message = _extract_message(body)
        text = f"codai {path} → {e.code}: {message}" if message else f"codai {path} → {e.code}"
        return CodaiError(
            text,
            e.code,
            body,
            request_id=headers.get("x-codai-trace-id") or headers.get("x-request-id"),
            retry_after=retry_after,
        )
