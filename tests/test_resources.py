"""Resource classes against the http.server stub, plus 0.1.x backward compatibility."""

from __future__ import annotations

import json

import pytest

import codai
from codai import Codai, ChatResult, CodaiError


def _chat_response(content="PONG", tool_calls=None):
    msg = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "model": "codai",
        "choices": [{"index": 0, "message": msg, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 2, "prompt_tokens_details": {"cached_tokens": 4}},
    }


def test_version():
    assert codai.__version__ == "0.68.0"
def test_chat_completions_create(client, stub):
    stub.reply(
        200,
        _chat_response(),
        {"x-codai-routed-to": "gemini-2.5-flash", "x-request-id": "req-1", "x-codai-event-id": "ev-1"},
    )
    r = client.chat.completions.create(
        {"messages": [{"role": "user", "content": "ping"}]}, ext={"effort": "minimal"}
    )
    assert isinstance(r, ChatResult)
    assert r.content == "PONG"
    assert r.routed_to == "gemini-2.5-flash"
    assert r.request_id == "req-1"
    assert r.event_id == "ev-1"
    assert r.usage == {"prompt_tokens": 10, "completion_tokens": 2, "cached_tokens": 4}
    body = stub.last.json
    assert body["model"] == "codai" and body["stream"] is False
    assert stub.last.headers["x-codai-effort"] == "minimal"


def test_legacy_chat_still_works(client, stub):
    stub.reply(200, _chat_response("hi"), {"x-request-id": "req-2"})
    r = client.chat(
        [{"role": "user", "content": "hello"}],
        model="codai",
        max_tokens=5,
        agent_mode=True,
        compact="auto",
        best_of=3,
        session_id="s-1",
    )
    assert r.content == "hi" and r.request_id == "req-2"
    body = stub.last.json
    assert body == {"model": "codai", "messages": [{"role": "user", "content": "hello"}], "max_tokens": 5, "stream": False}
    h = stub.last.headers
    assert h["x-codai-mode"] == "agent"
    assert h["x-codai-compact"] == "1"
    assert h["x-codai-best-of"] == "3"
    assert h["x-codai-session-id"] == "s-1"


def test_images_generate_decodes_b64(client, stub):
    stub.reply(
        200,
        {
            "created": 1790000000,
            "data": [{"b64_json": "aW1nMQ==", "mime_type": "image/png"}, {"b64_json": "aW1nMg=="}],
        },
        {
            "x-codai-routed-to": "gemini-3.1-flash-image",
            "x-codai-data-region": "eu",
            "x-codai-cost-micro-usd": "147910",
        },
    )
    r = client.images.generate({"prompt": "a paper plane", "n": 2})
    assert r.images == [b"img1", b"img2"]
    assert r.mime_types == ["image/png", "image/png"]
    assert r.routed_to == "gemini-3.1-flash-image"
    assert r.data_region == "eu"
    assert r.cost_micro_usd == 147910
    assert stub.last.path == "/v1/images/generations"
    assert stub.last.json == {"prompt": "a paper plane", "n": 2, "model": "codai-image"}


def test_images_edit_posts_json(client, stub):
    stub.reply(
        200,
        {"created": 1790000000, "data": [{"b64_json": "aW1nMw==", "mime_type": "image/webp"}]},
        {"x-codai-routed-to": "gemini-3-pro-image", "x-codai-data-region": "global", "x-codai-cost-micro-usd": "135000"},
    )
    image = {"b64_json": "iVBORw0KGgoAAAANSUhEUg==", "mime_type": "image/png"}
    r = client.images.edit({"prompt": "make the sky orange", "image": image, "model": "codai-image-pro"})
    assert r.images == [b"img3"]
    assert r.mime_types == ["image/webp"]
    assert r.routed_to == "gemini-3-pro-image"
    assert r.data_region == "global"
    assert r.cost_micro_usd == 135000
    assert stub.last.path == "/v1/images/edits"
    assert stub.last.json == {"prompt": "make the sky orange", "image": image, "model": "codai-image-pro"}


def test_music_generate_decodes_wav(client, stub):
    stub.reply(
        200,
        {
            "created": 1790000000,
            "model": "lyria-002",
            "data": [{"b64_json": "d2F2MQ==", "mime_type": "audio/wav", "duration_seconds": 30, "sample_rate": 48000}],
        },
        {"x-codai-routed-to": "lyria-002", "x-codai-cost-micro-usd": "60000"},
    )
    r = client.music.generate({"prompt": "calm lo-fi piano"})
    assert r.clips == [b"wav1"]
    assert r.mime_types == ["audio/wav"]
    assert r.routed_to == "lyria-002"
    assert r.cost_micro_usd == 60000
    assert stub.last.path == "/v1/audio/music"
    assert stub.last.json == {"prompt": "calm lo-fi piano"}


def test_videos_generate_polls_until_succeeded(client, stub):
    job = {"id": "vid1.abc.def", "object": "video.job", "status": "running", "model": "veo", "seconds": 4,
           "estimated_cost_micro_usd": "400000"}
    stub.reply(202, job)
    stub.reply(200, {"id": "vid1.abc.def", "object": "video.job", "status": "running"})
    stub.reply(200, {"id": "vid1.abc.def", "object": "video.job", "status": "succeeded", "seconds": 4,
                     "data": [{"b64_json": "bXA0", "mime_type": "video/mp4"}]})
    r = client.videos.generate({"prompt": "a paper plane", "seconds": 4}, poll_interval=0.01)
    assert r.video == b"mp4"
    assert r.mime_type == "video/mp4"
    assert r.id == "vid1.abc.def"
    assert r.seconds == 4
    assert [(q.method, q.path) for q in stub.requests] == [
        ("POST", "/v1/videos"),
        ("GET", "/v1/videos/vid1.abc.def"),
        ("GET", "/v1/videos/vid1.abc.def"),
    ]
    assert stub.requests[0].json == {"prompt": "a paper plane", "seconds": 4}


def test_videos_generate_filtered_raises(client, stub):
    stub.reply(202, {"id": "vid1.x.y", "object": "video.job", "status": "running", "seconds": 8})
    stub.reply(200, {"id": "vid1.x.y", "object": "video.job", "status": "filtered", "error": "Blocked by the upstream safety filter"})
    with pytest.raises(RuntimeError, match="filtered: Blocked"):
        client.videos.generate({"prompt": "x"}, poll_interval=0.01)


def _asset(**over):
    a = {
        "asset_id": "7d0f2c1e-0000-4000-8000-000000000003",
        "kind": "image",
        "status": "ready",
        "model": "gemini-3.1-flash-image",
        "url": "https://storage.googleapis.com/b/u/i.png?X-Goog-Signature=abc",
        "mime_type": "image/png",
        "bytes": 1024,
        "duration_seconds": None,
        "width": 1024,
        "height": 1024,
        "created_at": "2026-10-10T08:00:00.000Z",
        "expires_at": "2026-10-10T09:00:00.000Z",
    }
    a.update(over)
    return a


def test_images_response_format_url_returns_assets(client, stub):
    stub.reply(200, {"created": 1790000000, "data": [_asset()]})
    r = client.images.generate({"prompt": "a paper plane", "response_format": "url"})
    assert r.images == []
    assert r.assets == [_asset()]
    assert r.mime_types == ["image/png"]
    assert stub.last.json["response_format"] == "url"


def test_music_response_format_url_returns_assets(client, stub):
    music = _asset(kind="music", mime_type="audio/wav", duration_seconds=30, width=None, height=None)
    stub.reply(200, {"created": 1790000000, "model": "lyria-002", "data": [music]})
    r = client.music.generate({"prompt": "calm lo-fi piano", "response_format": "url"})
    assert r.clips == []
    assert r.assets == [music]
    assert stub.last.json == {"prompt": "calm lo-fi piano", "response_format": "url"}


def test_music_lyria3_fields_pass_through_and_tracks_surface(client, stub):
    stub.reply(
        200,
        {
            "created": 1790000000,
            "model": "codai-music-pro",
            "data": [
                {
                    "b64_json": "bXAz",
                    "mime_type": "audio/mpeg",
                    "duration_seconds": 64.2,
                    "lyrics": "[0:4] Noaptea cade peste oraș",
                    "caption": "synth pop, bpm: 118",
                    "lyrics_match": 0.42,
                    "warnings": ["lyrics_mismatch"],
                }
            ],
        },
        {"x-codai-cost-micro-usd": "80000"},
    )
    body = {
        "model": "codai-music-pro",
        "prompt": "synth pop ballad",
        "lyrics": "Noaptea cade peste oraș",
        "bpm": 118,
        "duration_seconds": 60,
        "language": "ro",
        "instrumental": False,
    }
    r = client.music.generate(body)
    assert stub.last.json == body
    assert r.clips == [b"mp3"]
    assert r.mime_types == ["audio/mpeg"]
    assert r.tracks == [
        {
            "lyrics": "[0:4] Noaptea cade peste oraș",
            "caption": "synth pop, bpm: 118",
            "lyrics_match": 0.42,
            "warnings": ["lyrics_mismatch"],
        }
    ]
    assert r.warnings == ["lyrics_mismatch"]
    assert r.cost_micro_usd == 80000


def test_speech_json_defaults_codai_voice_with_timestamps(client, stub):
    stub.reply(
        200,
        {
            "object": "audio.speech",
            "model": "codai-speech",
            "voice": "Aoede",
            "language": "ro-RO",
            "mime_type": "audio/mpeg",
            "duration_seconds": 1.4,
            "b64_json": "bXAz",
            "words": [{"word": "Bună", "start": 0.1, "end": 0.5}, {"word": "ziua", "start": 0.55, "end": 1.0}],
            "cost_micro_usd": "480",
        },
    )
    r = client.audio.speech_json({"input": "Bună ziua", "language": "ro-RO"})
    assert stub.last.path == "/v1/audio/speech"
    assert stub.last.json == {"input": "Bună ziua", "language": "ro-RO", "model": "codai-speech", "timestamps": True}
    assert r.audio == b"mp3"
    assert r.words == [{"word": "Bună", "start": 0.1, "end": 0.5}, {"word": "ziua", "start": 0.55, "end": 1.0}]
    assert r.asset is None
    assert r.cost_micro_usd == 480
    assert r.duration_seconds == 1.4
    assert r.timestamps_unavailable is False


def test_speech_json_store_returns_asset_and_flags_unavailable_timestamps(client, stub):
    speech = _asset(kind="speech", model="codai-speech", mime_type="audio/mpeg", duration_seconds=1.4, width=None,
                    height=None)
    stub.reply(
        200,
        {"object": "audio.speech", "model": "codai-speech", "voice": "Charon", "language": "ro-RO",
         "mime_type": "audio/mpeg", "duration_seconds": 1.4, "asset": speech, "words": None, "cost_micro_usd": "480"},
        {"x-codai-timestamps": "unavailable"},
    )
    r = client.audio.speech_json({"input": "Salut", "voice": "Charon", "store": True, "timestamps": True})
    assert stub.last.json["store"] is True and stub.last.json["timestamps"] is True
    assert r.audio == b""
    assert r.asset == speech
    assert r.words is None
    assert r.timestamps_unavailable is True
    stub.reply(200, {"object": "audio.speech", "model": "codai-speech", "voice": "Aoede", "language": "ro-RO",
                     "mime_type": "audio/mpeg", "duration_seconds": 1, "asset": speech, "cost_micro_usd": "300"})
    client.audio.speech_json({"input": "Salut", "store": True})
    assert "timestamps" not in stub.last.json


def test_speech_codai_voice_does_not_inject_azure_default_voice(client, stub):
    stub.reply(200, b"\xff\xfbMP3", {"Content-Type": "audio/mpeg"})
    client.audio.speech({"input": "Salut", "model": "codai-speech"})
    assert stub.last.json == {"input": "Salut", "model": "codai-speech"}


def test_videos_generate_response_format_url_returns_asset(client, stub):
    video = _asset(kind="video", mime_type="video/mp4", duration_seconds=4, width=None, height=None)
    stub.reply(202, {"id": "vid1.u.u", "object": "video.job", "status": "running", "seconds": 4})
    stub.reply(200, {"id": "vid1.u.u", "object": "video.job", "status": "succeeded", "seconds": 4, "data": [video]})
    r = client.videos.generate({"prompt": "x", "seconds": 4}, poll_interval=0.01, response_format="url")
    assert r.asset == video
    assert r.video == b""
    assert r.mime_type == "video/mp4"
    assert stub.last.path == "/v1/videos/vid1.u.u"
    assert stub.last.query == "response_format=url"


def test_videos_retrieve_default_sends_no_query(client, stub):
    stub.reply(200, {"id": "vid1.a.b", "object": "video.job", "status": "running"})
    client.videos.retrieve("vid1.a.b")
    assert stub.last.query == ""


_RENDER_ID = "9c1d2e3f-0000-4000-8000-000000000010"
_RENDER_HTML = '<div data-composition-id="x" data-width="1920" data-height="1080"></div>'


def _render_queued():
    return {"id": _RENDER_ID, "object": "studio.render", "status": "queued", "model": "codai-render",
            "quality": "final", "aspect_ratio": "16:9", "fps": 30,
            "price_micro_usd_per_second": "10000", "minimum_micro_usd": "50000"}


def _render_status(status, **over):
    st = {"id": _RENDER_ID, "object": "studio.render", "status": status, "progress": 0.0, "quality": "final",
          "aspect_ratio": "16:9", "fps": 30, "error": None}
    st.update(over)
    return st


def test_renders_render_polls_until_succeeded(client, stub):
    mp4 = _asset(asset_id=_RENDER_ID, kind="render", model="codai-render", mime_type="video/mp4",
                 duration_seconds=31.2, width=1920, height=1080)
    qa = {"duration_seconds": 31.2, "width": 1920, "height": 1080, "lufs": -14.1, "warnings": []}
    stub.reply(202, _render_queued())
    stub.reply(200, _render_status("rendering", progress=0.4))
    stub.reply(200, _render_status("succeeded", progress=1, qa=qa, cost_micro_usd="320000", data=[mp4],
                                   poster_url="https://storage.googleapis.com/b/u/r.poster.jpg?X-Goog-Signature=abc"))
    r = client.renders.render({"html": _RENDER_HTML, "quality": "final"}, poll_interval=0.01)
    assert r.id == _RENDER_ID
    assert r.asset == mp4
    assert r.qa == qa
    assert r.cost_micro_usd == 320000
    assert r.poster_url and r.poster_url.endswith("X-Goog-Signature=abc")
    assert [(q.method, q.path) for q in stub.requests] == [
        ("POST", "/v1/studio/renders"),
        ("GET", f"/v1/studio/renders/{_RENDER_ID}"),
        ("GET", f"/v1/studio/renders/{_RENDER_ID}"),
    ]
    assert stub.requests[0].json == {"html": _RENDER_HTML, "quality": "final"}


def test_renders_create_and_retrieve(client, stub):
    stub.reply(202, _render_queued())
    stub.reply(200, _render_status("queued"))
    job = client.renders.create({"html": _RENDER_HTML})
    assert job["price_micro_usd_per_second"] == "10000"
    assert client.renders.retrieve(job["id"])["status"] == "queued"
    assert stub.last.path == f"/v1/studio/renders/{_RENDER_ID}"


def test_renders_render_failed_raises(client, stub):
    stub.reply(202, _render_queued())
    stub.reply(200, _render_status("failed", progress=0.2, error="lint_failed: missing data-duration"))
    with pytest.raises(RuntimeError, match="render failed: lint_failed"):
        client.renders.render({"html": _RENDER_HTML}, poll_interval=0.01)


def test_renders_render_timeout(client, stub):
    stub.reply(202, _render_queued())
    stub.reply(200, _render_status("rendering", progress=0.1))
    with pytest.raises(TimeoutError, match="did not finish"):
        client.renders.render({"html": _RENDER_HTML}, poll_interval=0.05, timeout=0.01)


def test_renders_list_query(client, stub):
    item = {"id": _RENDER_ID, "object": "studio.render", "status": "succeeded", "title": "Teaser",
            "quality": "final", "aspect_ratio": "16:9", "fps": 30, "duration_seconds": 10.0,
            "cost_micro_usd": "100000", "created_at": "2026-10-10T08:00:00.000Z", "parent_render_id": None,
            "root_render_id": _RENDER_ID, "has_timeline": True, "scene_count": 2}
    stub.reply(200, {"object": "list", "data": [item], "next_before": None})
    page = client.renders.list(before="2026-10-11T00:00:00Z", limit=10, root_render_id=_RENDER_ID)
    assert page["data"][0]["scene_count"] == 2
    assert stub.last.method == "GET" and stub.last.path == "/v1/studio/renders"
    assert "limit=10" in stub.last.query and f"root_render_id={_RENDER_ID}" in stub.last.query
    assert "before=2026-10-11T00%3A00%3A00Z" in stub.last.query
    stub.reply(200, {"object": "list", "data": [], "next_before": None})
    client.renders.list()
    assert stub.last.query == ""


def test_renders_create_timeline(client, stub):
    accepted = {**_render_queued(), "narration_cost_micro_usd": "1200", "scene_count": 2,
                "duration_seconds": 10, "root_render_id": _RENDER_ID}
    stub.reply(202, accepted)
    body = {"title": "Teaser", "scenes": [
        {"kind": "image", "asset_id": "3f2b8c1e-0000-4000-8000-000000000001", "narration": {"text": "Bună."}},
        {"kind": "video", "asset_id": "3f2b8c1e-0000-4000-8000-000000000002"},
    ]}
    job = client.renders.create_timeline(body)
    assert job["root_render_id"] == _RENDER_ID
    assert stub.last.method == "POST" and stub.last.path == "/v1/studio/timelines"
    assert stub.last.json == body


def test_renders_regenerate_scene(client, stub):
    accepted = {"id": "9c1d2e3f-0000-4000-8000-000000000021", "object": "studio.render", "status": "queued",
                "parent_render_id": _RENDER_ID, "root_render_id": _RENDER_ID, "scene_id": "s1",
                "scene_cost_micro_usd": "40000", "price_micro_usd_per_second": "10000",
                "minimum_micro_usd": "50000"}
    stub.reply(202, accepted)
    job = client.renders.regenerate_scene(_RENDER_ID, "s1", {"visual": {"prompt": "dusk"}, "narration": None})
    assert job["parent_render_id"] == _RENDER_ID
    assert stub.last.method == "POST"
    assert stub.last.path == f"/v1/studio/renders/{_RENDER_ID}/scenes/s1/regenerate"
    assert stub.last.json == {"visual": {"prompt": "dusk"}, "narration": None}


def test_renders_retrieve_expand_assets(client, stub):
    st = _render_status("queued", stage="generating_scene", parent_render_id=_RENDER_ID,
                        root_render_id=_RENDER_ID, timeline={"transition": "fade", "music": None, "scenes": []})
    stub.reply(200, st)
    r = client.renders.retrieve(_RENDER_ID, expand_assets=True)
    assert r["stage"] == "generating_scene"
    assert stub.last.query == "expand=assets"
    stub.reply(200, st)
    client.renders.retrieve(_RENDER_ID)
    assert stub.last.query == ""


def test_assets_list_query_and_iterate(client, stub):
    stub.reply(200, {"object": "list", "data": [_asset(asset_id="a")], "next_before": "2026-10-09T00:00:00.000Z"})
    stub.reply(200, {"object": "list", "data": [_asset(asset_id="b")], "next_before": None})
    ids = [a["asset_id"] for a in client.assets.iterate(kind="image", limit=1)]
    assert ids == ["a", "b"]
    assert stub.requests[0].path == "/v1/assets"
    assert stub.requests[0].query == "kind=image&limit=1"
    assert "before=2026-10-09T00%3A00%3A00.000Z" in stub.requests[1].query


def test_assets_retrieve_content_url_and_delete(client, stub):
    aid = "7d0f2c1e-0000-4000-8000-000000000003"
    stub.reply(200, _asset())
    assert client.assets.content_url(aid) == _asset()["url"]
    assert (stub.last.method, stub.last.path) == ("GET", f"/v1/assets/{aid}")
    stub.reply(200, {"id": aid, "object": "asset", "deleted": True})
    assert client.assets.delete(aid) == {"id": aid, "object": "asset", "deleted": True}
    assert (stub.last.method, stub.last.path) == ("DELETE", f"/v1/assets/{aid}")
    assert client.assets.content_path("a/b").endswith("/v1/assets/a%2Fb/content")


def test_assets_content_url_not_ready_raises(client, stub):
    stub.reply(200, _asset(status="pending", url=None, expires_at=None))
    with pytest.raises(RuntimeError, match="no content yet"):
        client.assets.content_url("x")


def test_assets_foreign_id_is_404(client, stub):
    stub.reply(404, {"error": {"message": "Not found", "type": "invalid_request_error", "code": "not_found"}})
    with pytest.raises(CodaiError) as e:
        client.assets.retrieve("nope")
    assert e.value.status == 404


_SFX = {
    "sfx_id": "kenney-impact-metal-heavy-001",
    "name": "Metal heavy 1",
    "category": "impact",
    "tags": ["metal", "heavy"],
    "duration_seconds": 0.62,
    "mime_type": "audio/ogg",
    "license": "CC0-1.0",
    "source": "kenney",
    "preview_url": "https://storage.googleapis.com/b/sfx/x.ogg?X-Goog-Signature=abc",
}


def test_sfx_search_query_and_result(client, stub):
    stub.reply(200, {"object": "list", "data": [_SFX], "source": "library"})
    r = client.sfx.search(q="metal hit", category="impact", tags=["metal", "heavy"], max_duration=2, limit=5)
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/studio/sfx")
    assert stub.last.query == "q=metal+hit&category=impact&tags=metal%2Cheavy&max_duration=2&limit=5"
    assert r.data == [_SFX] and r.source == "library" and r.fallback_unavailable is False


def test_sfx_search_reports_failed_fallback(client, stub):
    stub.reply(200, {"object": "list", "data": [], "source": "library"}, {"x-codai-sfx-fallback": "unavailable"})
    r = client.sfx.search()
    assert stub.last.query == ""
    assert r.fallback_unavailable is True and r.data == []


def test_sfx_import_returns_sfx_asset(client, stub):
    stub.reply(200, _asset(kind="sfx", model="codai-sfx", mime_type="audio/ogg"))
    a = client.sfx.import_("fs-123/x")
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/studio/sfx/fs-123%2Fx/import")
    assert a["kind"] == "sfx" and a["model"] == "codai-sfx"


def test_sfx_import_license_not_allowed(client, stub):
    stub.reply(400, {"error": {"message": "Only CC0", "type": "invalid_request_error", "code": "license_not_allowed"}})
    with pytest.raises(CodaiError) as e:
        client.sfx.import_("fs-9")
    assert e.value.status == 400


_DOC_ID = "5a7b2c3d-0000-4000-8000-000000000020"
_PREVIEW_ID = "6b8c3d4e-0000-4000-8000-000000000021"
_DECK_RENDER_ID = "7c9d4e5f-0000-4000-8000-000000000022"
_DECK_SPEC = {
    "slides": [
        {"layout": "title", "title": "Raport trimestrial", "subtitle": "T3 2026"},
        {"layout": "bullets", "title": "Rezultate", "bullets": ["Venituri în creștere", "Țintă atinsă"]},
    ]
}


def _document(**over):
    d = {"id": _DOC_ID, "object": "studio.document", "type": "deck", "theme": "codai-light", "model": "codai-docs",
         "title": "Raport trimestrial — ședință", "version": 1, "based_on": None, "warnings": [],
         "cost_micro_usd": "0", "preview": None,
         "file": _asset(asset_id=_DOC_ID, kind="document", model="codai-docs",
                        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        width=None, height=None)}
    d.update(over)
    return d


def _preview_accepted():
    return {"id": _PREVIEW_ID, "object": "studio.preview", "status": "queued", "document_id": _DOC_ID,
            "price_micro_usd_per_page": "2000", "minimum_micro_usd": "10000"}


def _preview(status, **over):
    p = {"id": _PREVIEW_ID, "object": "studio.preview", "document_id": _DOC_ID, "model": "codai-docs-preview",
         "status": status, "error": None, "page_count": None, "cost_micro_usd": "0", "pdf": None, "pages": [],
         "contact_sheet_url": None}
    p.update(over)
    return p


def _video_accepted():
    return {"id": _DECK_RENDER_ID, "object": "studio.render", "status": "queued", "model": "codai-render",
            "quality": "draft", "aspect_ratio": "16:9", "fps": 15, "price_micro_usd_per_second": "5000",
            "minimum_micro_usd": "25000", "preview_id": _PREVIEW_ID, "narration_cost_micro_usd": "4200",
            "slides": 2, "duration_seconds": 9.4}


def _deck_render(status, **over):
    st = {"id": _DECK_RENDER_ID, "object": "studio.render", "status": status, "progress": 0.0, "quality": "draft",
          "aspect_ratio": "16:9", "fps": 15, "error": None}
    st.update(over)
    return st


def test_documents_create_posts_spec(client, stub):
    stub.reply(200, _document())
    d = client.documents.create({"type": "deck", "theme": "codai-light", "spec": _DECK_SPEC})
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/studio/documents")
    assert stub.last.json == {"type": "deck", "theme": "codai-light", "spec": _DECK_SPEC}
    assert d["id"] == _DOC_ID and d["file"]["kind"] == "document"
    assert d["title"] == "Raport trimestrial — ședință"


def test_documents_create_invalid_spec_raises(client, stub):
    stub.reply(400, {"error": {"message": "spec.slides: Required", "type": "invalid_request_error",
                               "code": "invalid_spec"}})
    with pytest.raises(CodaiError) as e:
        client.documents.create({"type": "deck", "spec": {"slides": []}})
    assert e.value.status == 400


def test_documents_retrieve_returns_spec(client, stub):
    stub.reply(200, _document(spec=_DECK_SPEC, latest_preview_id=_PREVIEW_ID))
    d = client.documents.retrieve("a/b")
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/studio/documents/a%2Fb")
    assert d["spec"] == _DECK_SPEC and d["latest_preview_id"] == _PREVIEW_ID


def test_documents_preview_and_retrieve_preview(client, stub):
    stub.reply(202, _preview_accepted())
    stub.reply(200, _preview("rendering"))
    acc = client.documents.preview(_DOC_ID)
    assert (stub.requests[0].method, stub.requests[0].path) == ("POST", f"/v1/studio/documents/{_DOC_ID}/previews")
    assert stub.requests[0].json == {}
    assert acc["price_micro_usd_per_page"] == "2000"
    assert client.documents.retrieve_preview(acc["id"])["status"] == "rendering"
    assert (stub.last.method, stub.last.path) == ("GET", f"/v1/studio/previews/{_PREVIEW_ID}")


def test_documents_create_preview_and_wait_polls(client, stub):
    pages = [{"page": 1, "url": "https://storage.googleapis.com/b/u/p001.png?s=1", "width": 1280, "height": 720}]
    stub.reply(202, _preview_accepted())
    stub.reply(200, _preview("queued"))
    stub.reply(200, _preview("succeeded", page_count=1, cost_micro_usd="10000", pages=pages,
                             pdf=_asset(asset_id=_PREVIEW_ID, kind="preview", mime_type="application/pdf")))
    p = client.documents.create_preview_and_wait(_DOC_ID, poll_interval=0.01)
    assert p["status"] == "succeeded" and p["pages"] == pages and p["pdf"]["kind"] == "preview"
    assert [(q.method, q.path) for q in stub.requests] == [
        ("POST", f"/v1/studio/documents/{_DOC_ID}/previews"),
        ("GET", f"/v1/studio/previews/{_PREVIEW_ID}"),
        ("GET", f"/v1/studio/previews/{_PREVIEW_ID}"),
    ]


def test_documents_create_preview_and_wait_failed_raises(client, stub):
    stub.reply(202, _preview_accepted())
    stub.reply(200, _preview("failed", error="convert_failed: soffice timeout"))
    with pytest.raises(RuntimeError, match="preview failed: convert_failed"):
        client.documents.create_preview_and_wait(_DOC_ID, poll_interval=0.01)


def test_documents_create_preview_and_wait_timeout(client, stub):
    stub.reply(202, _preview_accepted())
    stub.reply(200, _preview("rendering"))
    with pytest.raises(TimeoutError, match="did not finish"):
        client.documents.create_preview_and_wait(_DOC_ID, poll_interval=0.05, timeout=0.01)


def test_documents_video_posts_body(client, stub):
    stub.reply(202, _video_accepted())
    body = {"quality": "draft", "transition": "fade", "narrate": {"model": "codai-speech", "language": "ro-RO"}}
    r = client.documents.video(_DOC_ID, body)
    assert (stub.last.method, stub.last.path) == ("POST", f"/v1/studio/documents/{_DOC_ID}/video")
    assert stub.last.json == body
    assert r["preview_id"] == _PREVIEW_ID and r["narration_cost_micro_usd"] == "4200"


def test_documents_video_and_wait_polls_renders(client, stub):
    mp4 = _asset(asset_id=_DECK_RENDER_ID, kind="render", model="codai-render", mime_type="video/mp4",
                 duration_seconds=9.4, width=1920, height=1080)
    qa = {"duration_seconds": 9.4, "width": 1920, "height": 1080, "lufs": None, "warnings": []}
    stub.reply(202, _video_accepted())
    stub.reply(200, _deck_render("queued"))
    stub.reply(200, _deck_render("succeeded", progress=1, data=[mp4], qa=qa, cost_micro_usd="47000",
                                 poster_url="https://storage.googleapis.com/b/u/r.poster.jpg?s=1"))
    r = client.documents.video_and_wait(_DOC_ID, {"quality": "draft"}, poll_interval=0.01)
    assert r.id == _DECK_RENDER_ID and r.asset == mp4 and r.qa == qa
    assert r.cost_micro_usd == 47000
    assert [(q.method, q.path) for q in stub.requests] == [
        ("POST", f"/v1/studio/documents/{_DOC_ID}/video"),
        ("GET", f"/v1/studio/renders/{_DECK_RENDER_ID}"),
        ("GET", f"/v1/studio/renders/{_DECK_RENDER_ID}"),
    ]


def test_documents_video_and_wait_failed_raises(client, stub):
    stub.reply(202, _video_accepted())
    stub.reply(200, _deck_render("failed", error="preview_failed: convert_failed"))
    with pytest.raises(RuntimeError, match="deck video failed: preview_failed"):
        client.documents.video_and_wait(_DOC_ID, poll_interval=0.01)


def test_documents_video_and_wait_timeout(client, stub):
    stub.reply(202, _video_accepted())
    stub.reply(200, _deck_render("rendering", progress=0.3))
    with pytest.raises(TimeoutError, match="did not finish"):
        client.documents.video_and_wait(_DOC_ID, poll_interval=0.05, timeout=0.01)


def _sse(*objs, done=True):
    frames = ["data: " + json.dumps(o) + "\n\n" for o in objs]
    if done:
        frames.append("data: [DONE]\n\n")
    return frames


def _chunk(delta, finish=None, usage=None):
    c = {"id": "c", "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
    if usage:
        c["usage"] = usage
    return c


def test_chat_stream_text_chunks_and_final(client, stub):
    stub.sse(
        _sse(
            _chunk({"role": "assistant", "content": "Hel"}),
            _chunk({"content": "lo"}),
            _chunk({"tool_calls": [{"index": 0, "id": "call_1", "type": "function", "function": {"name": "f", "arguments": '{"a'}}]}),
            _chunk({"tool_calls": [{"index": 0, "function": {"arguments": '":1}'}}]}, finish="tool_calls"),
            _chunk({}, usage={"prompt_tokens": 3, "completion_tokens": 4}),
        ),
        headers={"x-codai-routed-to": "m1", "x-codai-trace-id": "t-1"},
    )
    s = client.chat.completions.stream({"messages": [{"role": "user", "content": "x"}]})
    assert "".join(s) == "Hello"
    assert stub.last.json["stream"] is True
    f = s.final
    assert f is not None
    assert f.content == "Hello"
    assert f.tool_calls == [{"index": 0, "id": "call_1", "type": "function", "function": {"name": "f", "arguments": '{"a":1}'}}]
    assert f.finish_reason == "tool_calls"
    assert f.usage == {"prompt_tokens": 3, "completion_tokens": 4}
    assert f.routed_to == "m1" and f.request_id == "t-1"


def test_legacy_chat_stream_yields_text(client, stub):
    stub.sse(_sse(_chunk({"content": "a"}), _chunk({"content": "b"})))
    assert list(client.chat_stream([{"role": "user", "content": "x"}], agent_mode=True)) == ["a", "b"]
    assert stub.last.headers["x-codai-mode"] == "agent"


def test_messages_create_and_stream(client, stub):
    stub.reply(200, {"id": "msg", "content": [{"type": "text", "text": "Hi "}, {"type": "text", "text": "there"}]})
    r = client.messages.create({"messages": [{"role": "user", "content": "x"}], "max_tokens": 10})
    assert r.text == "Hi there"
    stub.sse(
        [
            'event: message_start\ndata: {"type":"message_start","message":{"usage":{"input_tokens":5,"output_tokens":0}}}\n\n',
            'event: content_block_delta\ndata: {"type":"content_block_delta","delta":{"type":"text_delta","text":"He"}}\n\n',
            'event: content_block_delta\ndata: {"type":"content_block_delta","delta":{"type":"text_delta","text":"y"}}\n\n',
            'event: message_delta\ndata: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":2}}\n\n',
            'event: message_stop\ndata: {"type":"message_stop"}\n\n',
        ]
    )
    s = client.messages.stream({"messages": [{"role": "user", "content": "x"}], "max_tokens": 10})
    assert "".join(s.text()) == "Hey"
    assert s.final.stop_reason == "end_turn"
    assert s.final.usage == {"input_tokens": 5, "output_tokens": 2}


def test_responses_create_and_stream(client, stub):
    stub.reply(200, {"id": "resp", "output_text": "done"})
    assert client.responses.create({"input": "x"}).output_text == "done"
    stub.sse(
        [
            'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"ab"}\n\n',
            'event: response.completed\ndata: {"type":"response.completed","response":{"id":"resp","output_text":"ab"}}\n\n',
        ]
    )
    s = client.responses.stream({"input": "x"})
    assert "".join(s.text()) == "ab"
    assert s.final.response == {"id": "resp", "output_text": "ab"}


def test_embeddings_new_and_legacy(client, stub):
    stub.reply(200, {"data": [{"embedding": [0.1, 0.2]}]}, {"x-codai-embed-fallback": "azure"})
    r = client.embeddings.create({"input": "hi"})
    assert r.embeddings == [[0.1, 0.2]] and r.fallback == "azure"
    assert stub.last.json["model"] == "codai-embed"
    stub.reply(200, {"data": [{"embedding": [1.0]}]})
    assert client.embeddings(["a"], dimensions=8) == [[1.0]]
    assert stub.last.json["dimensions"] == 8


def test_models_new_and_legacy(client, stub):
    stub.reply(200, {"object": "list", "data": [{"id": "codai"}]})
    assert client.models.list() == [{"id": "codai"}]
    stub.reply(200, {"object": "list", "data": [{"id": "codai"}]})
    assert client.models() == [{"id": "codai"}]


def test_feedback_new_and_legacy(client, stub):
    stub.reply(200, {"ok": True})
    client.feedback("ev-1", -1, comment="wrong")
    assert stub.last.json == {"event_id": "ev-1", "rating": -1, "comment": "wrong"}
    stub.reply(200, {"ok": True})
    assert client.feedback.submit({"session_id": "s", "rating": 1}) == {"ok": True}


def test_tokens_and_mint_token(client, stub):
    # Placeholder tokens use the `codai_xxx` shape so the gitleaks allowlist recognises them.
    stub.reply(200, {"token": "codai_xxx_realtime", "expires_at": "2026-01-01T00:00:00Z", "scope": "realtime"})
    t = client.tokens.create("realtime", 600)
    assert t.token == "codai_xxx_realtime" and t.scope == "realtime"
    assert stub.last.json == {"scope": "realtime", "ttl_seconds": 600}
    stub.reply(200, {"token": "codai_xxx_audio", "expires_at": "…", "scope": "audio"})
    assert client.mint_token("audio")["token"] == "codai_xxx_audio"


def test_audio_transcribe_multipart_and_speech(client, stub):
    stub.reply(200, {"text": "hello world"})
    text = client.audio.transcribe(b"RIFF....", filename="clip.wav", language="en")
    assert text == "hello world"
    req = stub.last
    assert req.headers["content-type"].startswith("multipart/form-data; boundary=")
    assert b'name="file"; filename="clip.wav"' in req.body
    assert b'name="language"\r\n\r\nen' in req.body
    assert b"RIFF...." in req.body
    stub.reply(200, b"\xff\xfbMP3", {"Content-Type": "audio/mpeg"})
    audio = client.speech("hi")
    assert audio == b"\xff\xfbMP3"
    assert stub.last.json == {"model": "codai-tts", "input": "hi", "voice": "alloy"}


def test_agents_run_runs_and_stream(client, stub):
    stub.reply(200, {"result": "ok", "model": "codai", "event_id": "ev-9", "usage": {"steps": 2}})
    r = client.agents_run("do it", context="ctx")
    assert r.result == "ok" and r.event_id == "ev-9"
    assert stub.last.json == {"task": "do it", "context": "ctx"}
    stub.reply(202, {"id": "run-1", "status": "queued"})
    assert client.agents.runs.create({"task": "x"})["id"] == "run-1"
    stub.reply(200, {"steps": [{"seq": 1}]})
    assert client.agents.runs.steps("run/1") == [{"seq": 1}]
    assert stub.last.path == "/v1/agents/runs/run%2F1/steps"
    stub.reply(200, {"ok": True})
    client.agents.runs.cancel("run-1")
    assert stub.last.method == "POST" and stub.last.json == {}
    stub.sse(
        [
            'event: step\ndata: {"seq":1,"kind":"plan","summary":"s"}\n\n',
            'event: done\ndata: {"status":"completed","result":"r","error":null,"step_count":1}\n\n',
            'event: step\ndata: {"seq":99}\n\n',
        ]
    )
    events = list(client.agents.runs.stream("run-1"))
    assert [e["event"] for e in events] == ["step", "done"]
    assert events[1]["data"]["status"] == "completed"


def test_tasks_devices_hosts_account_receipt(client, stub):
    stub.reply(200, {"tasks": [], "next_cursor": None})
    client.tasks.list(outcome="pass", limit=10)
    assert stub.last.query == "outcome=pass&limit=10"
    stub.reply(200, {"ok": True})
    client.tasks.confirm("t1", {"outcome": "confirmed"})
    assert stub.last.path == "/v1/tasks/t1/confirm"
    stub.reply(200, {"devices": [{"id": "d1"}]})
    assert client.devices.list() == [{"id": "d1"}]
    stub.reply(200, {"ok": True})
    client.devices.update("d1", {"name": "Laptop"})
    assert stub.last.method == "PATCH" and stub.last.json == {"name": "Laptop"}
    stub.reply(200, {"hosts": []})
    assert client.hosts.list() == []
    stub.reply(200, {"ok": True, "result": {}})
    client.hosts.exec("dev-1", "fs.list", {"path": "/"}, timeout_ms=5000, label="ls")
    assert stub.last.json == {"op": "fs.list", "args": {"path": "/"}, "timeout_ms": 5000, "label": "ls"}
    stub.reply(200, {"plan": {"tier": "pro"}})
    assert client.account.get()["plan"]["tier"] == "pro"
    stub.reply(200, {"total_micro_usd": 1})
    client.receipt.get(session_id="s-1")
    assert stub.last.query == "session_id=s-1"


def test_sessions_group(stub):
    c = Codai(api_key="k", base_url=stub.url, max_retries=0, device="5dc0de00-0000-4000-8000-00000000c0da")
    stub.reply(201, {"id": "sess-1", "session_key": "k1"})
    s = c.sessions.create({"session_key": "k1", "title": "t"})
    assert s["created"] is True and s["id"] == "sess-1"
    assert stub.last.headers["x-codai-device"] == "5dc0de00-0000-4000-8000-00000000c0da"
    stub.reply(200, {"sessions": [{"id": "sess-1"}]})
    assert c.sessions.list(limit=5, archived=True) == [{"id": "sess-1"}]
    assert stub.last.query == "limit=5&archived=1&v=2"
    stub.reply(200, {"events": [], "next_after": 0})
    c.sessions.events.list("sess-1", after=3)
    assert stub.last.path == "/v1/sessions/sess-1/events" and stub.last.query == "after=3"
    stub.reply(200, {"holder_device_id": "d", "expires_at": "x"})
    c.sessions.lease.renew("sess-1")
    assert stub.last.method == "PUT"
    stub.reply(200, {"ok": True})
    c.sessions.controls.mark_applied("sess-1", "c1")
    assert stub.last.path == "/v1/sessions/sess-1/control/c1/applied" and stub.last.method == "POST"
    stub.reply(200, {"sessions": []})
    c.sessions.shares.shared_with_me()
    assert stub.last.path == "/v1/sessions/shared-with-me"
    stub.sse(
        [
            ": ping 15000\n\n",
            'event: event\ndata: {"v":1,"seq":4}\n\n',
            'event: presence\ndata: {"v":1,"device_id":"d","online":true}\n\n',
        ]
    )
    events = list(c.sessions.stream("sess-1", after=3))
    assert [e["event"] for e in events] == ["event", "presence"]
    assert stub.last.query == "after=3"


def test_sessions_dispatch_send_and_open(stub):
    c = Codai(api_key="k", base_url=stub.url, max_retries=0, device="5dc0de00-0000-4000-8000-00000000c0da")
    stub.reply(202, {"control_id": "dispatch:x", "seq": 3, "target_device_id": "d2", "mode": "send"})
    # Legacy dict body keeps working unchanged.
    c.sessions.dispatch("sess-1", {"device_id": "d2", "text": "go"})
    assert stub.last.path == "/v1/sessions/sess-1/dispatch" and stub.last.method == "POST"
    assert stub.last.json == {"device_id": "d2", "text": "go"}
    c.sessions.dispatch("sess-1", device_id="d2", text="go", turn_id="t1")
    assert stub.last.json == {"device_id": "d2", "text": "go", "turn_id": "t1"}
    stub.reply(202, {"control_id": "dispatch:y", "seq": 4, "target_device_id": "d2", "mode": "open"})
    res = c.sessions.dispatch("sess-1", device_id="d2", mode="open", text="ignored", turn_id="t2")
    assert res["mode"] == "open"
    assert stub.last.json == {"device_id": "d2", "mode": "open"}
    c.sessions.dispatch("sess-1", {"device_id": "d2", "mode": "open"})
    assert stub.last.json == {"device_id": "d2", "mode": "open"}
    with pytest.raises(ValueError):
        c.sessions.dispatch("sess-1", device_id="d2")
    with pytest.raises(ValueError):
        c.sessions.dispatch("sess-1", text="go")


def test_orgs_group(client, stub):
    stub.reply(201, {"id": "org-1", "name": "acme", "role": "owner"})
    assert client.orgs.create("acme")["id"] == "org-1"
    stub.reply(200, {"members": [{"user_id": "u1"}]})
    assert client.orgs.members.list("org-1") == [{"user_id": "u1"}]
    stub.reply(200, {"ok": True})
    client.orgs.members.remove("org-1", "u1")
    assert stub.last.method == "DELETE" and stub.last.path == "/v1/orgs/org-1/members/u1"


def test_projects_and_environments_groups(client, stub):
    stub.reply(200, {"projects": [{"id": "p1"}]})
    assert client.projects.list() == [{"id": "p1"}]
    stub.reply(201, {"project": {"id": "p1"}})
    assert client.projects.create({"name": "brivio"}) == {"id": "p1"}
    assert stub.last.method == "POST" and stub.last.json == {"name": "brivio"}
    stub.reply(200, {"project": {"id": "p1", "name": "b2"}})
    assert client.projects.update("p1", {"name": "b2"})["name"] == "b2"
    assert stub.last.method == "PATCH" and stub.last.path == "/v1/projects/p1"
    stub.reply(200, {"deleted": True, "id": "p1"})
    client.projects.delete("p1")
    assert stub.last.method == "DELETE"

    stub.reply(200, {"environments": []})
    client.environments.list(project_id="p1", for_user_id="me")
    assert stub.last.query == "project_id=p1&for_user_id=me"
    stub.reply(201, {"environment": {"id": "e1"}})
    assert client.environments.create({"project_id": "p1", "provider": "byo", "name": "x"}) == {"id": "e1"}
    stub.reply(200, {"environment_id": "e1"})
    client.environments.enroll({"token": "codai_env_x", "device_id": "d", "daemon_version": "1", "os": "linux", "arch": "x64"})
    assert stub.last.path == "/v1/environments/enroll"
    for action in ("start", "stop", "archive", "destroy"):
        stub.reply(200, {"from": "a", "to": "b", "environment": {}})
        getattr(client.environments, action)("e1")
        assert stub.last.method == "POST" and stub.last.path == f"/v1/environments/e1/{action}"
    stub.reply(201, {"token": "codai_env_y"})
    client.environments.enroll_token("e1")
    assert stub.last.method == "POST" and stub.last.path == "/v1/environments/e1/enroll-token"

    stub.reply(200, {"ssh_public_key": True, "user_id": "u1"})
    client.environments.members.set_ssh_key("e1", "ssh-ed25519 AAAA a@b")
    assert stub.last.method == "PUT" and stub.last.path == "/v1/environments/e1/members/me/ssh-key"
    assert stub.last.json == {"public_key": "ssh-ed25519 AAAA a@b"}
    stub.reply(200, {"member": {"role": "viewer", "user_id": "u1"}})
    assert client.environments.members.set_role("e1", "u1", "viewer")["role"] == "viewer"
    assert stub.last.method == "PATCH" and stub.last.json == {"role": "viewer"}
    stub.reply(201, {"port": {"port": 3000}})
    assert client.environments.ports.set("e1", 3000, {"visibility": "org"}) == {"port": 3000}
    assert stub.last.method == "PUT" and stub.last.path == "/v1/environments/e1/ports/3000"
    stub.reply(201, {"name": "API_KEY", "updated": False})
    client.environments.secrets.set("e1", "API_KEY", "s3cr3t")
    assert stub.last.method == "PUT" and stub.last.json == {"value": "s3cr3t"}
    stub.reply(200, {"deleted": True, "name": "API_KEY"})
    client.environments.secrets.remove("e1", "API_KEY")
    assert stub.last.method == "DELETE" and stub.last.path == "/v1/environments/e1/secrets/API_KEY"


def test_projects_get_returns_full_reply(client, stub):
    reply = {"project": {"id": "p/1", "name": "brivio"}, "environments": [{"id": "e1"}]}
    stub.reply(200, reply)
    assert client.projects.get("p/1") == reply
    assert stub.last.method == "GET" and stub.last.path == "/v1/projects/p%2F1"
    assert stub.last.json is None


def test_environments_get_and_update(client, stub):
    detail = {"environment": {"id": "e1"}, "role": "owner", "members": [], "ports": [], "events": []}
    stub.reply(200, detail)
    assert client.environments.get("e 1") == detail
    assert stub.last.method == "GET" and stub.last.path == "/v1/environments/e%201"
    stub.reply(200, {"environment": {"id": "e1", "idle_timeout_minutes": 30}})
    out = client.environments.update("e1", {"name": "dev", "idle_timeout_minutes": 30})
    assert out == {"id": "e1", "idle_timeout_minutes": 30}
    assert stub.last.method == "PATCH" and stub.last.path == "/v1/environments/e1"
    assert stub.last.json == {"name": "dev", "idle_timeout_minutes": 30}


def test_environment_members_list_add_remove(client, stub):
    stub.reply(200, {"members": [{"user_id": "u1", "role": "owner"}]})
    assert client.environments.members.list("e1") == [{"user_id": "u1", "role": "owner"}]
    assert stub.last.method == "GET" and stub.last.path == "/v1/environments/e1/members"
    stub.reply(200, {})
    assert client.environments.members.list("e1") == []
    stub.reply(201, {"member": {"user_id": "u2", "role": "developer"}})
    out = client.environments.members.add("e1", {"email": "a@b.c", "role": "developer"})
    assert out == {"user_id": "u2", "role": "developer"}
    assert stub.last.method == "POST" and stub.last.path == "/v1/environments/e1/members"
    assert stub.last.json == {"email": "a@b.c", "role": "developer"}
    stub.reply(200, {"removed": True, "user_id": "u/2"})
    assert client.environments.members.remove("e1", "u/2") == {"removed": True, "user_id": "u/2"}
    assert stub.last.method == "DELETE" and stub.last.path == "/v1/environments/e1/members/u%2F2"


def test_environment_members_ssh_cert(client, stub):
    cert = {
        "certificate": "ssh-ed25519-cert-v01@openssh.com AAAA u-1",
        "host": "203.0.113.7",
        "principal": "u-0f1d2c3e",
        "valid_before": "2026-09-27T00:00:00.000Z",
    }
    stub.reply(200, cert)
    out = client.environments.members.ssh_cert("env/1", {"public_key": "ssh-ed25519 AAAA ana@laptop"})
    assert out == cert
    assert stub.last.method == "POST"
    assert stub.last.path == "/v1/environments/env%2F1/members/me/ssh-cert"
    assert stub.last.json == {"public_key": "ssh-ed25519 AAAA ana@laptop"}


def test_environment_members_ssh_cert_is_not_retried(stub):
    c = Codai(api_key="codai_test", base_url=stub.url, max_retries=2, timeout=5)
    stub.reply(503, {"error": {"message": "busy"}})
    with pytest.raises(CodaiError) as ei:
        c.environments.members.ssh_cert("e1", {"public_key": "ssh-ed25519 AAAA"})
    assert ei.value.status == 503
    assert len(stub.requests) == 1


def test_environments_ssh_ca(client, stub):
    keys = {"public_keys": ["ssh-ed25519 AAAA ca-current", "ssh-ed25519 BBBB ca-next"]}
    stub.reply(200, keys)
    assert client.environments.ssh_ca("e 1") == keys
    assert stub.last.method == "GET" and stub.last.path == "/v1/environments/e%201/ssh-ca"
    assert stub.last.json is None


def test_environment_tasks_list_create_get(client, stub):
    listing = {"tasks": [{"id": "t1", "status": "queued"}]}
    stub.reply(200, listing)
    assert client.environments.tasks.list("e1") == listing
    assert stub.last.method == "GET" and stub.last.path == "/v1/environments/e1/tasks"

    queued = {"task_id": "t1", "session_id": "s1", "status": "queued"}
    stub.reply(202, queued)
    out = client.environments.tasks.create("env/1", {"prompt": "add a /health route", "branch": "feat/health-route"})
    assert out == queued
    assert stub.last.method == "POST" and stub.last.path == "/v1/environments/env%2F1/tasks"
    assert stub.last.json == {"prompt": "add a /health route", "branch": "feat/health-route"}
    stub.reply(202, queued)
    client.environments.tasks.create("e1", {"prompt": "no branch"})
    assert stub.last.json == {"prompt": "no branch"}

    detail = {"task": {"id": "t/1", "status": "done"}}
    stub.reply(200, detail)
    assert client.environments.tasks.get("e 1", "t/1") == detail
    assert stub.last.method == "GET" and stub.last.path == "/v1/environments/e%201/tasks/t%2F1"


def test_environment_tasks_create_is_not_retried(stub):
    c = Codai(api_key="codai_test", base_url=stub.url, max_retries=2, timeout=5)
    stub.reply(503, {"error": {"message": "busy"}})
    with pytest.raises(CodaiError):
        c.environments.tasks.create("e1", {"prompt": "x"})
    assert len(stub.requests) == 1


def test_verify_agent_output_key_and_verify(client, stub):
    key = {"enabled": False, "note": "experimental"}
    stub.reply(200, key)
    assert client.verify.agent_output_key() == key
    assert stub.last.method == "GET" and stub.last.path == "/v1/verify/agent-output/key"

    verdict = {"valid": True, "key_id": "0123456789abcdef", "note": "experimental"}
    stub.reply(200, verdict)
    payload = {"v": 1, "task_id": "t1", "status": "done"}
    signature = {"sig": "c2ln", "key_id": "0123456789abcdef"}
    assert client.verify.agent_output(payload, signature) == verdict
    assert stub.last.method == "POST" and stub.last.path == "/v1/verify/agent-output"
    assert stub.last.json == {"payload": payload, "signature": signature}


def test_verify_agent_output_is_not_retried(stub):
    c = Codai(api_key="codai_test", base_url=stub.url, max_retries=2, timeout=5)
    stub.reply(503, {"error": {"code": "signing_disabled", "message": "off"}})
    with pytest.raises(CodaiError):
        c.verify.agent_output({}, {"sig": "x"})
    assert len(stub.requests) == 1


def test_environment_ports_list_remove_and_secrets_list(client, stub):
    stub.reply(200, {"ports": [{"port": 3000, "visibility": "org"}]})
    assert client.environments.ports.list("e1") == [{"port": 3000, "visibility": "org"}]
    assert stub.last.method == "GET" and stub.last.path == "/v1/environments/e1/ports"
    stub.reply(200, {"deleted": True, "port": 3000})
    assert client.environments.ports.remove("e1", 3000) == {"deleted": True, "port": 3000}
    assert stub.last.method == "DELETE" and stub.last.path == "/v1/environments/e1/ports/3000"
    stub.reply(200, {"secrets": [{"name": "API_KEY", "updated_at": "2026-09-26T00:00:00Z"}]})
    assert client.environments.secrets.list("e1") == [{"name": "API_KEY", "updated_at": "2026-09-26T00:00:00Z"}]
    assert stub.last.method == "GET" and stub.last.path == "/v1/environments/e1/secrets"
    stub.reply(200, {"secrets": None})
    assert client.environments.secrets.list("e1") == []


def test_notifications_delete_and_delete_many(client, stub):
    stub.reply(200, {"deleted": 1})
    assert client.notifications.delete(7) == {"deleted": 1}
    assert stub.last.method == "DELETE" and stub.last.path == "/v1/notifications/7"
    stub.reply(200, {"deleted": 2})
    assert client.notifications.delete_many([3, 4]) == {"deleted": 2}
    assert stub.last.method == "POST" and stub.last.path == "/v1/notifications/delete"
    assert stub.last.json == {"ids": [3, 4]}


def test_prompts_routes(client, stub):
    stub.reply(200, {"data": []})
    assert client.prompts.list(status="due", limit=5) == {"data": []}
    assert stub.last.method == "GET" and stub.last.path == "/v1/prompts"
    assert stub.last.query == "status=due&limit=5"
    stub.reply(201, {"id": "p1", "created": True, "superseded": 0})
    assert client.prompts.create({"prompt": "Goal: ship", "goal_key": "g1"})["created"] is True
    assert stub.last.method == "POST" and stub.last.path == "/v1/prompts"
    assert stub.last.json == {"prompt": "Goal: ship", "goal_key": "g1"}
    stub.reply(200, {"id": "p1"})
    client.prompts.get("p 1")
    assert stub.last.method == "GET" and stub.last.path == "/v1/prompts/p%201"
    stub.reply(200, {"id": "p1", "status": "done"})
    client.prompts.update("p1", {"status": "done"})
    assert stub.last.method == "PATCH" and stub.last.path == "/v1/prompts/p1"
    assert stub.last.json == {"status": "done"}
    stub.reply(200, {"deleted": 1})
    assert client.prompts.delete("p1") == {"deleted": 1}
    assert stub.last.method == "DELETE" and stub.last.path == "/v1/prompts/p1"
    stub.reply(200, {"session_id": "s1", "device_id": "d1", "pushed": True})
    assert client.prompts.launch("p1", device_id="d1")["session_id"] == "s1"
    assert stub.last.method == "POST" and stub.last.path == "/v1/prompts/p1/launch"
    assert stub.last.json == {"device_id": "d1"}


def test_prompt_launch_is_not_retried(stub):
    c = Codai(api_key="codai_test", base_url=stub.url, max_retries=2, timeout=5)
    stub.reply(503, {"error": {"code": "unavailable", "message": "down"}})
    with pytest.raises(CodaiError):
        c.prompts.launch("p1")
    assert len(stub.requests) == 1


def test_usage_get_routes_and_filters(client, stub):
    stub.reply(200, {"from": "2026-09-06", "to": "2026-10-05", "group_by": "day", "data": []})
    assert client.usage.get()["group_by"] == "day"
    assert stub.last.method == "GET" and stub.last.path == "/v1/usage"
    assert stub.last.query == ""
    row = {
        "key": "codai",
        "requests": 3,
        "errors": 0,
        "tasks": 1,
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "cached_read_tokens": 2,
        "cost_micro_usd": "1250000",
    }
    stub.reply(200, {"from": "2026-09-01", "to": "2026-09-30", "group_by": "model", "data": [row]})
    r = client.usage.get(
        {"from": "2026-09-01", "to": "2026-09-30", "group_by": "model", "device": "d1", "tag": "acme"}
    )
    assert r["data"][0]["cost_micro_usd"] == "1250000"
    assert stub.last.query == "from=2026-09-01&to=2026-09-30&group_by=model&device=d1&tag=acme"


def test_usage_get_rejects_unknown_query_keys(client):
    with pytest.raises(ValueError):
        client.usage.get({"groupBy": "day"})


def test_keys_list_and_set_tags(client, stub):
    stub.reply(200, {"data": []})
    assert client.keys.list() == {"data": []}
    assert stub.last.method == "GET" and stub.last.path == "/v1/keys" and stub.last.query == ""
    stub.reply(200, {"data": [{"id": "k1", "current": True}]})
    client.keys.list(include_revoked=True)
    assert stub.last.query == "include_revoked=true"
    stub.reply(200, {"id": "k 1", "tags": ["a", "b"]})
    assert client.keys.set_tags("k 1", ["a", "b"]) == {"id": "k 1", "tags": ["a", "b"]}
    assert stub.last.method == "PATCH" and stub.last.path == "/v1/keys/k%201"
    assert stub.last.json == {"tags": ["a", "b"]}
    stub.reply(200, {"id": "k1", "tags": []})
    client.keys.set_tags("k1", [])
    assert stub.last.json == {"tags": []}


def test_audio_speech_stream_yields_events_with_decoded_audio(client, stub):
    stub.sse(
        [
            'event: start\ndata: {"type":"start","model":"codai-tts-ro","voice":"ro-RO-AlinaNeural","format":"pcm"}\n\n',
            'event: audio\ndata: {"type":"audio","delta":"AAEC"}\n\n',
            'event: viseme\ndata: {"type":"viseme","id":4,"offsetMs":50}\n\n',
            'event: word\ndata: {"type":"word","text":"Salut","offsetMs":50,"durationMs":300}\n\n',
            'event: done\ndata: {"type":"done","audio_ms":400}\n\n',
        ]
    )
    events = list(client.audio.speech_stream({"input": "Salut", "voice": "emil"}))
    assert [e["type"] for e in events] == ["start", "audio", "viseme", "word", "done"]
    assert events[1]["audio_bytes"] == b"\x00\x01\x02"
    assert events[2] == {"type": "viseme", "id": 4, "offsetMs": 50}
    assert stub.last.path == "/v1/audio/speech/stream"
    assert stub.last.json == {"input": "Salut", "voice": "emil", "model": "codai-tts-ro"}


def test_system_one_batch_sends_items_timeout_and_fallback(client, stub):
    stub.reply(
        200,
        {
            "model": "codai-fast",
            "items": [{"id": "a", "answers": {"q": {"type": "noul", "noul": 0.8}}}],
            "usage": {"input_tokens": 3, "output_tokens": 1},
            "latency_ms": 9,
            "fallback_used": True,
        },
    )
    r = client.system_one.batch(
        [{"id": "a", "state": "salut"}],
        {"q": {"type": "noul", "instructions": "Greeting?"}},
        timeout_ms=800,
        fallback="codai-fast",
    )
    assert r["fallback_used"] is True and r["items"][0]["id"] == "a"
    assert stub.last.json == {
        "items": [{"id": "a", "state": "salut"}],
        "questions": {"q": {"type": "noul", "instructions": "Greeting?"}},
        "timeout_ms": 800,
        "fallback": "codai-fast",
    }


def test_tokens_live_scope(client, stub):
    fake = ".".join(["codai_eph_v1", "a", "b"])  # built at runtime so secret scanners skip the fixture
    stub.reply(200, {"token": fake, "expires_at": "2026-10-05T10:00:00Z", "scope": "live"})
    assert client.tokens.create("live").scope == "live"
    assert stub.last.json == {"scope": "live"}
