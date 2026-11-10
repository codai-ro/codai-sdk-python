"""``client.media_ops`` (Studio media operations, AR-02) against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError, is_media_op_job

_ASSET = "3f2b8c1e-0000-4000-8000-000000000001"
_JOB = "6d1e2f3a-4b5c-4d6e-8f70-8192a3b4c5d6"
_PENDING = {
    "object": "media_op.job",
    "id": _JOB,
    "op": "audio.separate_stems",
    "status": "pending",
    "parent_asset_id": _ASSET,
    "outputs": [],
    "analysis": None,
    "error": None,
    "cost_micro_usd": 0,
}
_READY = {**_PENDING, "status": "ready", "outputs": [{"asset_id": "v"}, {"asset_id": "d"}], "cost_micro_usd": 9000}


def test_list_and_quote(client, stub):
    stub.reply(200, {"object": "list", "quote_basis": "x", "data": [{"id": "image.upscale", "available": True}]})
    stub.reply(200, {"object": "media_op.quote", "op": "image.upscale", "mode": "sync", "quote_micro_usd": 2000,
                     "quote_micro_eur": 2236})
    assert client.media_ops.list()["data"][0]["id"] == "image.upscale"
    assert client.media_ops.quote("image.upscale", [_ASSET], {"scale": 2})["quote_micro_eur"] == 2236
    assert [(r.method, r.path) for r in stub.requests] == [
        ("GET", "/v1/studio/media-ops"),
        ("POST", "/v1/studio/media-ops/image.upscale/quote"),
    ]
    assert stub.requests[1].json == {"asset_ids": [_ASSET], "params": {"scale": 2}}


def test_run_sync_sends_body_and_idempotency_key(client, stub):
    stub.reply(200, {"object": "media_op.result", "op": "image.remove_background", "status": "ready",
                     "outputs": [{"asset_id": "a2"}], "analysis": None, "cost_micro_usd": 1100})
    r = client.media_ops.run("image.remove_background", [_ASSET], idempotency_key="k1")
    assert not is_media_op_job(r)
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", "/v1/studio/media-ops/image.remove_background")
    assert req.json == {"asset_ids": [_ASSET], "params": {}}
    assert req.headers["idempotency-key"] == "k1"


def test_run_and_wait_polls_the_job(client, stub):
    stub.reply(202, _PENDING)
    stub.reply(200, _PENDING)
    stub.reply(200, _READY)
    out = client.media_ops.run_and_wait("audio.separate_stems", [_ASSET], {"stems": 4}, interval=0.01)
    assert out["status"] == "ready" and out["cost_micro_usd"] == 9000
    assert [(r.method, r.path) for r in stub.requests] == [
        ("POST", "/v1/studio/media-ops/audio.separate_stems"),
        ("GET", f"/v1/studio/media-ops/jobs/{_JOB}"),
        ("GET", f"/v1/studio/media-ops/jobs/{_JOB}"),
    ]


def test_job_encodes_id_and_wait_times_out(client, stub):
    stub.reply(200, _PENDING)
    assert client.media_ops.job("a/b")["status"] == "pending"
    assert stub.requests[0].path == "/v1/studio/media-ops/jobs/a%2Fb"
    with pytest.raises(TimeoutError):
        client.media_ops.wait(_JOB, interval=0.05, timeout=0.01)


def test_unavailable_lane_raises(client, stub):
    stub.reply(503, {"error": {"message": "Media operations are not configured on this gateway.",
                               "type": "server_error", "code": "media_ops_unavailable"}})
    with pytest.raises(CodaiError):
        client.media_ops.run("audio.master", [_ASSET])
