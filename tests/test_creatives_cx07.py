"""Carousel / print ``build`` (202 export job), ``post_copy``, ``transcript_cut``, ``regenerate_node``,
``reference_asset_ids`` and ``mask_png_b64`` against the http.server stub."""

from __future__ import annotations

from codai import is_paged_build

_CID = "7a1b2c3d-0000-4000-8000-000000000051"
_EID = "3f0c9a7e-1b2d-4c5e-8f90-a1b2c3d4e5f7"
_ASSET = "3f2b8c1e-0000-4000-8000-000000000001"
_BASE = f"/v1/studio/creatives/{_CID}"


def _export(status: str):
    return {
        "id": _EID,
        "object": "studio.export",
        "kind": "carousel_png",
        "status": status,
        "creative_id": _CID,
        "seq": 3,
        "format": "4x5",
        "fps": 0,
        "filename": "spring-sale-4x5.zip",
        "url": "https://storage.example/x.zip" if status == "succeeded" else None,
        "expires_at": None,
        "bytes": None,
        "rendered_seconds": None,
        "cost_micro_usd": None,
        "warnings": [],
        "error": None,
        "created_at": "2026-10-20T10:00:00Z",
    }


def _paged(status: str = "queued"):
    return {
        "object": "studio.creative_build",
        "creative_id": _CID,
        "seq": 3,
        "kind": "carousel",
        "format": "png",
        "format_id": "4x5",
        "pages": 6,
        "quote_micro_usd": "12000",
        "warnings": [],
        "lint": [],
        "print": None,
        "document": None,
        "export": _export(status),
    }


def test_build_carousel_returns_202_export_job(client, stub):
    stub.reply(202, _paged())
    r = client.creatives.build(_CID, format="png", format_id="4x5")
    assert is_paged_build(r) is True
    assert r["export"]["id"] == _EID
    assert (stub.last.method, stub.last.path) == ("POST", f"{_BASE}/build")
    assert stub.last.json == {"format": "png", "format_id": "4x5"}
    assert is_paged_build({"object": "studio.creative_build", "document": {"id": "d"}}) is False


def test_build_and_wait_polls_the_export(client, stub):
    stub.reply(202, _paged())
    stub.reply(200, _export("running"))
    stub.reply(200, _export("succeeded"))
    e = client.creatives.build_and_wait(_CID, format="pdf", crop_marks=False, interval=0.01)
    assert e["status"] == "succeeded"
    assert [(r.method, r.path) for r in stub.requests] == [
        ("POST", f"{_BASE}/build"),
        ("GET", f"/v1/studio/exports/{_EID}"),
        ("GET", f"/v1/studio/exports/{_EID}"),
    ]
    assert stub.requests[0].json == {"format": "pdf", "crop_marks": False}


def test_build_and_wait_returns_deck_build_as_is(client, stub):
    deck = {"object": "studio.creative_build", "creative_id": _CID, "seq": 1, "warnings": [], "document": {"id": "d"}}
    stub.reply(200, deck)
    assert client.creatives.build_and_wait(_CID) == deck
    assert len(stub.requests) == 1


def test_post_copy_sends_body_and_idempotency_key(client, stub):
    stub.reply(
        200,
        {
            "object": "studio.post_copy",
            "creative_id": _CID,
            "seq": 3,
            "kind": "carousel",
            "language": "ro",
            "platforms": [{"platform": "linkedin", "caption": "Reduceri.", "hashtags": ["#reduceri"]}],
            "alt": [],
            "fixes": [],
            "cost_micro_usd": "2140",
        },
    )
    stub.reply(200, {"object": "studio.post_copy"})
    r = client.creatives.post_copy(_CID, platforms=["linkedin"], language="ro", idempotency_key="pc-1")
    assert r["platforms"][0]["hashtags"] == ["#reduceri"]
    assert (stub.requests[0].method, stub.requests[0].path) == ("POST", f"{_BASE}/post-copy")
    assert stub.requests[0].json == {"platforms": ["linkedin"], "language": "ro"}
    assert stub.requests[0].headers["idempotency-key"] == "pc-1"
    client.creatives.post_copy(_CID)
    assert stub.requests[1].json == {}
    assert "idempotency-key" not in stub.requests[1].headers


def test_transcript_cut(client, stub):
    stub.reply(200, {"seq": 5, "node_id": "clip", "pieces": ["clip", "clip-2"], "removed_ms": 600, "words": 2})
    r = client.creatives.transcript_cut(_CID, node_id="clip", remove=[{"from_word": 3, "to_word": 4}], base_seq=4)
    assert r["pieces"] == ["clip", "clip-2"]
    assert (stub.last.method, stub.last.path) == ("POST", f"{_BASE}/transcript-cut")
    assert stub.last.json == {"node_id": "clip", "remove": [{"from_word": 3, "to_word": 4}], "base_seq": 4}


def test_regenerate_node_encodes_id_and_sends_key(client, stub):
    stub.reply(200, {"seq": 6, "node_id": "hero/1", "asset_id": _ASSET, "cast_id": "ana", "reference_asset_ids": [_ASSET]})
    r = client.creatives.regenerate_node(
        _CID, "hero/1", prompt="Ana pe plajă", aspect_ratio="4:5", idempotency_key="rg-1"
    )
    assert r["cast_id"] == "ana"
    assert (stub.last.method, stub.last.path) == ("POST", f"{_BASE}/nodes/hero%2F1/regenerate")
    assert stub.last.json == {"prompt": "Ana pe plajă", "aspect_ratio": "4:5"}
    assert stub.last.headers["idempotency-key"] == "rg-1"


def test_videos_create_forwards_reference_asset_ids(client, stub):
    stub.reply(202, {"id": "v1", "status": "running"})
    client.videos.create({"prompt": "A red bike", "reference_asset_ids": [_ASSET]})
    assert stub.last.path == "/v1/videos"
    assert stub.last.json == {"prompt": "A red bike", "reference_asset_ids": [_ASSET]}


def test_media_ops_mask_png_b64_only_when_given(client, stub):
    stub.reply(200, {"object": "media_op.quote"})
    stub.reply(200, {"object": "media_op.result", "status": "ready", "outputs": []})
    stub.reply(200, {"object": "media_op.quote"})
    client.media_ops.quote("image.inpaint", [_ASSET], {"prompt": "sky"}, mask_png_b64="iVBOR")
    client.media_ops.run("image.erase", [_ASSET], mask_png_b64="iVBOR")
    client.media_ops.quote("image.upscale", [_ASSET])
    assert stub.requests[0].json == {"asset_ids": [_ASSET], "params": {"prompt": "sky"}, "mask_png_b64": "iVBOR"}
    assert stub.requests[1].json == {"asset_ids": [_ASSET], "params": {}, "mask_png_b64": "iVBOR"}
    assert stub.requests[2].json == {"asset_ids": [_ASSET], "params": {}}
