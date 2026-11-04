"""HTTP layer: auth/headers, query, extension bags, errors, retries, SSE parsing."""

from __future__ import annotations

import io
import json

import pytest

from codai import Codai, CodaiError, extension_headers, frame_json, read_sse
from codai._http import HttpClient


def test_bearer_json_and_url(client, stub):
    stub.reply(200, {"ok": True})
    res = client.http.request("/v1/models", body={"a": 1})
    req = stub.last
    assert req.method == "POST"
    assert req.path == "/v1/models"
    assert req.headers["authorization"] == "Bearer codai_test"
    assert req.headers["content-type"] == "application/json"
    assert req.json == {"a": 1}
    assert res.status == 200 and res.json() == {"ok": True}


def test_get_without_body_serialises_query_and_drops_none(client, stub):
    stub.reply(200, {})
    client.http.request("/v1/tasks", query={"limit": 5, "cursor": None, "applied": True})
    req = stub.last
    assert req.method == "GET"
    assert req.query == "limit=5&applied=1"
    assert "content-type" not in req.headers


def test_extension_headers_defaults_then_per_call(stub):
    c = Codai(
        api_key="k",
        base_url=stub.url,
        max_retries=0,
        session_id="sess-default",
        device="dev-1",
        client="codai-cli/1.0",
    )
    stub.reply(200, {})
    c.http.request(
        "/v1/chat/completions",
        body={},
        ext={
            "session_id": "sess-call",
            "effort": "high",
            "thinking": True,
            "thinking_budget": 8192,
            "cache": False,
            "compact": "auto",
            "best_of": "off",
            "headers": {"x-custom": "1"},
        },
    )
    h = stub.last.headers
    assert h["x-codai-session-id"] == "sess-call"
    assert h["x-codai-device"] == "dev-1"
    assert h["x-codai-client"] == "codai-cli/1.0"
    assert h["x-codai-effort"] == "high"
    assert h["x-codai-thinking"] == "1"
    assert h["x-codai-thinking-budget"] == "8192"
    assert h["x-codai-cache"] == "0"
    assert h["x-codai-compact"] == "1"
    assert h["x-codai-best-of"] == "off"
    assert h["x-custom"] == "1"


def test_extension_headers_rejects_unknown_key():
    with pytest.raises(ValueError, match="unknown extension option"):
        extension_headers({"sessionId": "camelCase-is-wrong"})


def test_error_envelope_maps_to_codai_error(client, stub):
    stub.reply(
        401,
        {"error": {"message": "Invalid or missing API key.", "type": "invalid_request_error", "code": "invalid_api_key"}},
        headers={"x-codai-trace-id": "trace-1"},
    )
    with pytest.raises(CodaiError) as ei:
        client.models.list()
    err = ei.value
    assert err.status == 401
    assert err.code == "invalid_api_key"
    assert err.request_id == "trace-1"
    assert "Invalid or missing API key." in str(err)
    assert err.body["error"]["code"] == "invalid_api_key"


def test_rate_limit_retry_after(client, stub):
    stub.reply(429, {"error": {"message": "slow", "type": "rate_limit_error", "code": "rate_limit_exceeded"}}, {"Retry-After": "7"})
    with pytest.raises(CodaiError) as ei:
        client.account.get()
    assert ei.value.status == 429
    assert ei.value.retry_after == 7


def test_retries_5xx_then_succeeds(stub, monkeypatch):
    monkeypatch.setattr("codai._http.time.sleep", lambda _s: None)
    c = Codai(api_key="k", base_url=stub.url, max_retries=2)
    stub.reply(503, {"error": {"message": "down", "type": "server_error", "code": "internal_error"}})
    stub.reply(200, {"data": [{"id": "codai"}]})
    assert c.models.list() == [{"id": "codai"}]
    assert len(stub.requests) == 2


def test_no_retry_on_4xx(stub):
    c = Codai(api_key="k", base_url=stub.url, max_retries=2)
    stub.reply(400, {"error": {"message": "bad", "type": "invalid_request_error", "code": "bad_request"}})
    with pytest.raises(CodaiError):
        c.models.list()
    assert len(stub.requests) == 1


def test_network_error_after_retries(monkeypatch):
    monkeypatch.setattr("codai._http.time.sleep", lambda _s: None)
    c = Codai(api_key="k", base_url="http://127.0.0.1:9", max_retries=1, timeout=0.5)
    with pytest.raises(CodaiError) as ei:
        c.models.list()
    assert ei.value.status == 0
    assert "failed after retries" in str(ei.value)


def test_accept_status_returns_body(client, stub):
    stub.reply(503, {"ok": False, "checks": {}})
    res = client.health.ready()
    assert res["http_status"] == 503
    assert res["ok"] is False


def test_read_sse_frames_events_multiline_comments_crlf():
    raw = io.BytesIO(
        b"event: step\ndata: {\"seq\":1}\n\n"
        b": ping 1000\n\n"
        b"data: line1\ndata: line2\n\n"
        b"event: done\r\ndata: {\"status\":\"completed\"}\r\n\r\n"
        b"data: [DONE]\n\n"
    )
    frames = list(read_sse(raw, chunk_size=7))
    assert [(f.event, f.data) for f in frames] == [
        ("step", '{"seq":1}'),
        ("message", "line1\nline2"),
        ("done", '{"status":"completed"}'),
        ("message", "[DONE]"),
    ]
    assert frame_json(frames[0]) == {"seq": 1}
    assert frame_json(frames[3]) is None


def test_read_sse_handles_utf8_split_across_chunks():
    payload = "data: " + json.dumps({"t": "ăîșț€"}, ensure_ascii=False) + "\n\n"
    raw = io.BytesIO(payload.encode("utf-8"))
    frames = list(read_sse(raw, chunk_size=3))
    assert frame_json(frames[0]) == {"t": "ăîșț€"}


def test_http_client_url_trims_trailing_slash():
    h = HttpClient(api_key="k", base_url="https://gw.test/")
    assert h.url("/v1/models") == "https://gw.test/v1/models"
    assert h.url("/v1/x", {"a": "b c", "n": 1}) == "https://gw.test/v1/x?a=b+c&n=1"
