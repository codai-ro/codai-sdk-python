"""``client.research`` (async deep research) + ``client.tools.search`` web filters against the http.server stub."""

from __future__ import annotations

import pytest

_ID = "3f0c9a7e-1b2d-4c5e-8f90-a1b2c3d4e5f6"
_QUEUED = {"id": _ID, "status": "queued", "created_at": "2026-10-18T10:00:00Z"}
_DONE = {
    "id": _ID,
    "status": "done",
    "created_at": "2026-10-18T10:00:00Z",
    "finished_at": "2026-10-18T10:01:10Z",
    "report": "Answer [S1].",
    "sources": [{"id": "S1", "title": "BNR", "url": "https://www.bnr.ro/"}],
    "searches": 4,
    "pages_read": 9,
}


def test_create_posts_only_set_fields(client, stub):
    stub.reply(202, _QUEUED)
    job = client.research.create("curs BNR", max_sources=5, include_domains=["bnr.ro"])
    assert job["status"] == "queued"
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", "/v1/research")
    assert req.json == {"question": "curs BNR", "max_sources": 5, "include_domains": ["bnr.ro"]}
    assert "idempotency-key" not in req.headers


def test_create_sends_idempotency_key_when_given(client, stub):
    stub.reply(202, _QUEUED)
    client.research.create("q", idempotency_key="job-1")
    assert stub.requests[0].headers["idempotency-key"] == "job-1"


def test_retrieve_encodes_id(client, stub):
    stub.reply(200, _DONE)
    assert client.research.retrieve("a/b")["report"] == "Answer [S1]."
    assert (stub.requests[0].method, stub.requests[0].path) == ("GET", "/v1/research/a%2Fb")


def test_wait_polls_until_done(client, stub):
    stub.reply(200, {**_QUEUED, "status": "running"})
    stub.reply(200, {**_QUEUED, "status": "running"})
    stub.reply(200, _DONE)
    job = client.research.wait(_ID, interval=0.01)
    assert job["status"] == "done"
    assert len(stub.requests) == 3


def test_wait_returns_failed_job(client, stub):
    stub.reply(200, {**_QUEUED, "status": "failed", "error": {"message": "boom"}})
    assert client.research.wait(_ID, interval=0.01)["error"]["message"] == "boom"


def test_wait_times_out(client, stub):
    stub.reply(200, {**_QUEUED, "status": "running"})
    with pytest.raises(TimeoutError):
        client.research.wait(_ID, interval=0.05, timeout=0.01)


def test_run_skips_polling_when_create_finished(client, stub):
    stub.reply(200, _DONE)
    job = client.research.run("q", wait_s=30)
    assert job["sources"][0]["id"] == "S1"
    assert stub.requests[0].json == {"question": "q", "wait_s": 30}
    assert len(stub.requests) == 1


def test_run_polls_a_202_job(client, stub):
    stub.reply(202, _QUEUED)
    stub.reply(200, _DONE)
    job = client.research.run("q", interval=0.01)
    assert job["status"] == "done"
    assert [r.method for r in stub.requests] == ["POST", "GET"]


def test_tools_search_forwards_filters(client, stub):
    stub.reply(200, {"results": [], "provider": "codai", "took_ms": 1, "cached": False})
    body = {
        "query": "react compiler",
        "include_domains": ["react.dev"],
        "exclude_domains": ["medium.com"],
        "published_after": "2026-01-01",
        "freshness": "year",
        "content_chars": 500,
    }
    client.tools.search(body)
    assert (stub.requests[0].method, stub.requests[0].path) == ("POST", "/v1/tools/search")
    assert stub.requests[0].json == body
