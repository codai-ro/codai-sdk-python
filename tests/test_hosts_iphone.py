"""``client.hosts.iphone`` / caps + env on the host stream, and ``client.sandboxes.pty_url``."""

from __future__ import annotations

from urllib.parse import parse_qs

import pytest

from codai import Codai
from codai.resources.sandboxes import sandbox_pty_url

ENV = "7c1e2d3f-4a5b-4c6d-8e9f-0a1b2c3d4e5f"


def test_list_keeps_caps_and_environment_id(client, stub):
    stub.reply(
        200,
        {
            "hosts": [
                {
                    "device_id": "d1",
                    "name": "iPhone Ana",
                    "platform": "ios",
                    "os": "ios",
                    "hostname": "iPhone Ana",
                    "roots": [],
                    "caps": ["iphone", "video"],
                    "environment_id": ENV,
                    "since": 1,
                    "last_seen": 2,
                }
            ]
        },
    )
    (h,) = client.hosts.list()
    assert h["caps"] == ["iphone", "video"]
    assert h["environment_id"] == ENV


def test_iphone_posts_op_iphone(client, stub):
    stub.reply(200, {"req_id": "r1", "ok": True, "result": {"data": {"tapped": True}, "image": "data:image/jpeg;base64,AAA"}, "error": None})
    r = client.hosts.iphone("d1", "tap", {"x": 200, "y": 640}, timeout_ms=20_000)
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/hosts/d1/exec")
    assert stub.last.json == {"op": "iphone", "args": {"tool": "tap", "args": {"x": 200, "y": 640}}, "timeout_ms": 20_000}
    assert r["result"]["image"].startswith("data:image/jpeg;base64,")


def test_iphone_without_args(client, stub):
    stub.reply(200, {"req_id": "r2", "ok": True, "result": {"data": {}}, "error": None})
    client.hosts.iphone("d1", "screen")
    assert stub.last.json == {"op": "iphone", "args": {"tool": "screen"}}


def test_iphone_rejects_bad_tool_without_a_request(client, stub):
    with pytest.raises(ValueError):
        client.hosts.iphone("d1", "Tap-Now")
    assert stub.requests == []


def test_stream_sends_caps_and_env(client, stub):
    stub.sse(['event: hello\ndata: {"device_id":"d1","heartbeat_ms":15000}\n\n'])
    events = list(client.hosts.stream(os="ios", caps=["iphone", "video"], environment_id=ENV))
    assert events[0]["event"] == "hello"
    assert stub.last.path == "/v1/hosts/stream"
    q = parse_qs(stub.last.query)
    assert q["caps"] == ["iphone,video"]
    assert q["env"] == [ENV]
    assert q["os"] == ["ios"]


def test_pty_url():
    c = Codai(api_key="codai_test", base_url="https://ai.codai.ro/")
    assert c.sandboxes.pty_url("sb 1", cols=120, rows=32) == "wss://ai.codai.ro/v1/sandboxes/sb%201/pty?cols=120&rows=32"
    assert c.sandboxes.pty_url("sb1") == "wss://ai.codai.ro/v1/sandboxes/sb1/pty"
    assert sandbox_pty_url("http://localhost:8787", "sb1", rows=24) == "ws://localhost:8787/v1/sandboxes/sb1/pty?rows=24"
    for bad in ({"cols": 0}, {"rows": 1001}, {"cols": True}):
        with pytest.raises(ValueError):
            c.sandboxes.pty_url("sb1", **bad)
