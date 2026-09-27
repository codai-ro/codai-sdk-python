"""Test fixtures: a stdlib ``http.server`` stub standing in for the gateway (no network)."""

from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlsplit

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from codai import Codai  # noqa: E402


class Recorded:
    def __init__(self, method: str, path: str, query: str, headers: Dict[str, str], body: bytes) -> None:
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body

    @property
    def json(self) -> Any:
        return json.loads(self.body) if self.body else None


class Reply:
    """What the stub answers: status, headers, body (bytes/str/dict) or SSE ``frames``."""

    def __init__(
        self,
        status: int = 200,
        body: Any = None,
        headers: Optional[Dict[str, str]] = None,
        sse: Optional[List[str]] = None,
    ) -> None:
        self.status = status
        self.body = body
        self.headers = headers or {}
        self.sse = sse


Handler = Callable[[Recorded], Reply]


class Stub:
    def __init__(self) -> None:
        self.requests: List[Recorded] = []
        self.handlers: List[Handler] = []
        self.default: Handler = lambda _r: Reply(200, {})
        self.server: Optional[ThreadingHTTPServer] = None

    def on(self, handler: Handler) -> None:
        """Queue a reply for the next request (FIFO); afterwards ``default`` is used."""
        self.handlers.append(handler)

    def reply(self, status: int = 200, body: Any = None, headers: Optional[Dict[str, str]] = None) -> None:
        self.on(lambda _r: Reply(status, body, headers))

    def sse(self, frames: List[str], headers: Optional[Dict[str, str]] = None) -> None:
        self.on(lambda _r: Reply(200, None, headers, sse=frames))

    @property
    def url(self) -> str:
        assert self.server is not None
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    @property
    def last(self) -> Recorded:
        return self.requests[-1]


def _make_handler(stub: Stub):
    class _H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_a: Any) -> None:  # silence
            pass

        def _serve(self) -> None:
            parts = urlsplit(self.path)
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else b""
            rec = Recorded(self.command, parts.path, parts.query, {k.lower(): v for k, v in self.headers.items()}, body)
            stub.requests.append(rec)
            handler = stub.handlers.pop(0) if stub.handlers else stub.default
            reply = handler(rec)
            if reply.sse is not None:
                self.send_response(reply.status)
                self.send_header("Content-Type", "text/event-stream")
                for k, v in reply.headers.items():
                    self.send_header(k, v)
                self.send_header("Connection", "close")
                self.end_headers()
                for frame in reply.sse:
                    self.wfile.write(frame.encode("utf-8"))
                    self.wfile.flush()
                self.close_connection = True
                return
            data: bytes
            if reply.body is None:
                data = b""
            elif isinstance(reply.body, bytes):
                data = reply.body
            elif isinstance(reply.body, str):
                data = reply.body.encode("utf-8")
            else:
                data = json.dumps(reply.body).encode("utf-8")
            self.send_response(reply.status)
            if not any(k.lower() == "content-type" for k in reply.headers):
                self.send_header("Content-Type", "application/json")
            for k, v in reply.headers.items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _serve

    return _H


@pytest.fixture
def stub():
    s = Stub()
    server = ThreadingHTTPServer(("127.0.0.1", 0), _make_handler(s))
    server.daemon_threads = True
    s.server = server
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    try:
        yield s
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture
def client(stub: Stub) -> Codai:
    return Codai(api_key="codai_test", base_url=stub.url, max_retries=0, timeout=5)
