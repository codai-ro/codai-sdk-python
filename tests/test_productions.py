"""``client.productions`` (Studio brief -> promo video, RC-20) against the http.server stub."""

from __future__ import annotations

import pytest

_ID = "6d1e2f3a-4b5c-4d6e-8f70-8192a3b4c5d6"
_RUNNING = {"id": _ID, "object": "studio.production", "status": "running", "phase": "render"}
_DONE = {**_RUNNING, "status": "succeeded", "phase": "ready", "render_id": "r2"}


def test_create_posts_only_set_fields_and_idempotency_key(client, stub):
    stub.reply(202, _RUNNING)
    p = client.productions.create("Un promo pentru aplicația noastră", language="ro", narration=False, idempotency_key="p1")
    assert p["phase"] == "render"
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", "/v1/studio/productions")
    assert req.json == {"brief": "Un promo pentru aplicația noastră", "language": "ro", "narration": False}
    assert req.headers["idempotency-key"] == "p1"


def test_retrieve_encodes_id(client, stub):
    stub.reply(200, _DONE)
    assert client.productions.retrieve("a/b")["render_id"] == "r2"
    assert (stub.requests[0].method, stub.requests[0].path) == ("GET", "/v1/studio/productions/a%2Fb")


def test_run_creates_then_waits(client, stub):
    stub.reply(202, _RUNNING)
    stub.reply(200, {**_RUNNING, "phase": "qa"})
    stub.reply(200, _DONE)
    assert client.productions.run("A promo for our app", interval=0.01)["status"] == "succeeded"
    assert [r.method for r in stub.requests] == ["POST", "GET", "GET"]


def test_wait_times_out(client, stub):
    stub.reply(200, _RUNNING)
    with pytest.raises(TimeoutError):
        client.productions.wait(_ID, interval=0.05, timeout=0.01)
