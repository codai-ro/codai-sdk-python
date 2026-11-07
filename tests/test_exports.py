"""``client.exports`` + ``creatives.export_fcpxml`` / ``export_lottie`` / ``download_lottie`` against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_ID = "3f0c9a7e-1b2d-4c5e-8f90-a1b2c3d4e5f6"
_CID = "7a1b2c3d-0000-4000-8000-000000000031"


def _exp(**over):
    base = {
        "id": _ID,
        "object": "studio.export",
        "status": "queued",
        "creative_id": _CID,
        "seq": 7,
        "format": "story",
        "fps": 30,
        "filename": "launch-teaser-story.fcpxml.zip",
        "url": None,
        "expires_at": None,
        "bytes": None,
        "rendered_seconds": None,
        "cost_micro_usd": None,
        "warnings": [],
        "error": None,
        "created_at": "2026-10-14T09:58:00Z",
    }
    base.update(over)
    return base


def test_export_fcpxml_query_and_retrieve(client, stub):
    stub.reply(202, _exp())
    stub.reply(202, _exp())
    stub.reply(200, _exp(status="running"))
    e = client.creatives.export_fcpxml(_CID, format="story", seq=7)
    assert e["status"] == "queued"
    client.creatives.export_fcpxml(_CID)
    assert client.exports.retrieve("a/b")["status"] == "running"
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"/v1/studio/creatives/{_CID}/export.fcpxml", "format=story&seq=7"),
        ("GET", f"/v1/studio/creatives/{_CID}/export.fcpxml", ""),
        ("GET", "/v1/studio/exports/a%2Fb", ""),
    ]


def test_export_lottie_query_and_ready_export(client, stub):
    ready = _exp(
        kind="lottie",
        container="dotlottie",
        status="succeeded",
        filename="launch-teaser-all.lottie",
        url="https://storage.example/x.lottie",
        cost_micro_usd="0",
        rendered_seconds=0,
    )
    stub.reply(200, ready)
    stub.reply(200, ready)
    e = client.creatives.export_lottie(_CID, formats="all", seq=7, container="dotlottie")
    assert e["kind"] == "lottie"
    assert e["container"] == "dotlottie"
    assert e["status"] == "succeeded"
    client.creatives.export_lottie(_CID)
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"/v1/studio/creatives/{_CID}/export.lottie", "formats=all&seq=7&container=dotlottie"),
        ("GET", f"/v1/studio/creatives/{_CID}/export.lottie", ""),
    ]


def test_download_lottie_returns_bytes_and_filename(client, stub):
    body = b'{"v":"5.12.2","meta":{"ai_generated":true}}'
    stub.reply(
        200,
        body,
        {
            "Content-Type": "application/json",
            "Content-Disposition": 'attachment; filename="launch-teaser-story.lottie.json"',
        },
    )
    f = client.creatives.download_lottie(_CID, format="story")
    assert f["bytes"] == body
    assert f["filename"] == "launch-teaser-story.lottie.json"
    assert f["content_type"] == "application/json"
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"/v1/studio/creatives/{_CID}/export.lottie", "format=story&download=1"),
    ]


def test_wait_polls_until_succeeded(client, stub):
    stub.reply(200, _exp())
    stub.reply(200, _exp(status="running"))
    stub.reply(200, _exp(status="succeeded", url="https://storage.example/x.zip", bytes=1024, cost_micro_usd=60000))
    e = client.exports.wait(_ID, interval=0.01)
    assert e["status"] == "succeeded"
    assert e["url"] == "https://storage.example/x.zip"
    assert len(stub.requests) == 3


def test_wait_returns_failed(client, stub):
    stub.reply(200, _exp(status="failed", error={"code": "timeout", "message": "took too long"}))
    e = client.exports.wait(_ID, interval=0.01)
    assert e["error"]["code"] == "timeout"


def test_wait_timeout(client, stub):
    stub.reply(200, _exp(status="running"))
    stub.reply(200, _exp(status="running"))
    with pytest.raises(TimeoutError):
        client.exports.wait(_ID, interval=0.05, timeout=0.01)


def test_unsupported_kind(client, stub):
    stub.reply(
        400,
        {"error": {"message": "only video creatives", "type": "invalid_request_error", "code": "unsupported_kind"}},
    )
    with pytest.raises(CodaiError) as e:
        client.creatives.export_fcpxml(_CID)
    assert e.value.code == "unsupported_kind"
