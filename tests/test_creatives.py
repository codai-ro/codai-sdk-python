"""``client.creatives`` against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_ID = "7a1b2c3d-0000-4000-8000-000000000030"
_BASE = "/v1/studio/creatives"


def _creative(**over):
    c = {
        "id": _ID,
        "object": "studio.creative",
        "kind": "video",
        "title": "Teaser — ședință",
        "head_seq": 1,
        "version": {"seq": 1, "doc_hash": "a" * 64},
        "doc": {"schemaVersion": 1, "kind": "video", "title": "Teaser — ședință"},
    }
    c.update(over)
    return c


def test_create_list_retrieve_outline(client, stub):
    stub.reply(201, _creative())
    stub.reply(200, {"object": "list", "data": [], "next_before": None})
    stub.reply(200, _creative(seq=1, doc_hash="x", assets={}))
    stub.reply(200, {"head_seq": 1, "outline": 'video "x"', "formats": [], "vars": {}})
    c = client.creatives.create({"kind": "video", "title": "Teaser — ședință"})
    assert c["id"] == _ID and c["title"] == "Teaser — ședință"
    client.creatives.list(kind="video", limit=5)
    client.creatives.retrieve("a/b", seq=1)
    client.creatives.outline(_ID)
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("POST", _BASE, ""),
        ("GET", _BASE, "kind=video&limit=5"),
        ("GET", f"{_BASE}/a%2Fb", "seq=1"),
        ("GET", f"{_BASE}/{_ID}/outline", ""),
    ]
    assert stub.requests[0].json == {"kind": "video", "title": "Teaser — ședință"}


def test_edit_sends_only_given_fields(client, stub):
    stub.reply(200, {"seq": 2, "doc_hash": "b", "changed": ["title"], "warnings": [], "rebased": False})
    r = client.creatives.edit(_ID, base_seq=1, ops=[{"op": "setMeta", "title": "x"}], intent="retitle")
    assert r["seq"] == 2
    assert (stub.last.method, stub.last.path) == ("POST", f"{_BASE}/{_ID}/ops")
    assert stub.last.json == {"base_seq": 1, "ops": [{"op": "setMeta", "title": "x"}], "intent": "retitle"}


def test_edit_stale_raises(client, stub):
    stub.reply(409, {"error": {"message": "stale", "type": "invalid_request_error", "code": "stale",
                               "head_seq": 3, "conflicts": []}})
    with pytest.raises(CodaiError) as e:
        client.creatives.edit(_ID, base_seq=1, ops=[{"op": "setMeta", "title": "x"}])
    assert e.value.status == 409


def test_other_methods_paths(client, stub):
    stub.reply(200, {"head_seq": 1, "ids": ["title"]})
    stub.reply(200, {"head_seq": 1, "scenes": [], "nodes": [], "missing": []})
    stub.reply(200, {"object": "list", "data": [], "next_before_seq": None})
    stub.reply(200, {"id": _ID, "head_seq": 3, "seq": 3, "author": "user", "intent": "revert to 1",
                     "created_at": "x", "doc_hash": "c"})
    stub.reply(201, _creative())
    stub.reply(200, {"head_seq": 1, "issues": []})
    stub.reply(200, {"head_seq": 1, "format": "16x9", "width": 1920, "height": 1080, "duration_ms": 5000,
                     "html": "<html>"})
    stub.reply(202, {"render_id": "r1", "id": "r1", "object": "studio.render", "status": "queued", "cached": False})
    stub.reply(200, {"id": _ID, "object": "studio.creative", "deleted": True})
    c = client.creatives
    assert c.find(_ID, "hello")["ids"] == ["title"]
    c.subtree(_ID, scene_id="intro")
    c.versions(_ID, before_seq=9, limit=2)
    c.revert(_ID, 1)
    c.fork(_ID, seq=2)
    c.lint(_ID)
    assert c.compiled(_ID, format="16x9", scene="intro")["html"] == "<html>"
    assert c.render(_ID, {"quality": "draft"})["render_id"] == "r1"
    assert c.delete(_ID)["deleted"] is True
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("POST", f"{_BASE}/{_ID}/find", ""),
        ("POST", f"{_BASE}/{_ID}/subtree", ""),
        ("GET", f"{_BASE}/{_ID}/versions", "before_seq=9&limit=2"),
        ("POST", f"{_BASE}/{_ID}/revert", ""),
        ("POST", f"{_BASE}/{_ID}/fork", ""),
        ("POST", f"{_BASE}/{_ID}/lint", ""),
        ("GET", f"{_BASE}/{_ID}/compiled", "format=16x9&scene=intro"),
        ("POST", f"{_BASE}/{_ID}/render", ""),
        ("DELETE", f"{_BASE}/{_ID}", ""),
    ]
    assert stub.requests[0].json == {"query": "hello"}
    assert stub.requests[1].json == {"sceneId": "intro"}
    assert stub.requests[3].json == {"seq": 1}
    assert stub.requests[4].json == {"seq": 2}


_JOB = "5e6f7a8b-0000-4000-8000-000000000040"


def _frames(**over):
    f = {
        "object": "studio.creative.frames",
        "frame_job_id": _JOB,
        "status": "succeeded",
        "frames": [{"t_ms": 1500, "url": "https://x/f.png", "width": 1920, "height": 1080, "cached": False}],
        "head_seq": 3,
        "billed_micro_usd": "0",
    }
    f.update(over)
    return f


def test_frame_cached_job_and_poll(client, stub):
    running = {"object": "studio.creative.frame_job", "frame_job_id": _JOB, "status": "running", "head_seq": 3}
    stub.reply(200, _frames(frame_job_id=None))
    stub.reply(202, running)
    stub.reply(202, running)
    stub.reply(200, _frames())
    c = client.creatives
    hit = c.frame(_ID, t_ms=[1500])
    assert hit["status"] == "succeeded" and hit["frame_job_id"] is None
    job = c.frame(_ID, t_ms=[0, 1500], exact=True, format="16x9", version=3)
    assert job["status"] == "running" and job["frame_job_id"] == _JOB
    assert c.frame_job(_ID, _JOB)["status"] == "running"
    done = c.frame_job(_ID, _JOB)
    assert [f["t_ms"] for f in done["frames"]] == [1500] and done["billed_micro_usd"] == "0"
    assert [(r.method, r.path) for r in stub.requests] == [
        ("POST", f"{_BASE}/{_ID}/frame"),
        ("POST", f"{_BASE}/{_ID}/frame"),
        ("GET", f"{_BASE}/{_ID}/frames/{_JOB}"),
        ("GET", f"{_BASE}/{_ID}/frames/{_JOB}"),
    ]
    assert stub.requests[0].json == {"t_ms": [1500]}
    assert stub.requests[1].json == {"t_ms": [0, 1500], "exact": True, "format": "16x9", "version": 3}


def test_frame_errors_raise(client, stub):
    stub.reply(429, {"error": {"message": "busy", "type": "rate_limit_error", "code": "too_many_frame_jobs"}})
    stub.reply(404, {"error": {"message": "no", "type": "invalid_request_error", "code": "not_found"}})
    with pytest.raises(CodaiError) as e:
        client.creatives.frame(_ID, t_ms=[0])
    assert e.value.status == 429
    with pytest.raises(CodaiError) as e2:
        client.creatives.frame_job(_ID, "nope")
    assert e2.value.status == 404


def test_comment(client, stub):
    stub.reply(200, {"head_seq": 4, "applied_ops": 1, "summary": "Bigger.", "version": {"seq": 4, "doc_hash": "h"}})
    stub.reply(422, {"error": {"message": "no", "type": "invalid_request_error", "code": "no_edit",
                               "text": "Looks good.", "reason": "no_tool_call"}})
    c = client.creatives
    r = c.comment(_ID, t_ms=1200, comment="bigger", base_seq=3, node_id="title")
    assert r["applied_ops"] == 1 and r["version"]["seq"] == 4
    with pytest.raises(CodaiError) as e:
        c.comment(_ID, t_ms=0, comment="nice", base_seq=4, apply=False)
    assert e.value.status == 422
    assert [(r.method, r.path) for r in stub.requests] == [
        ("POST", f"{_BASE}/{_ID}/comments"),
        ("POST", f"{_BASE}/{_ID}/comments"),
    ]
    assert stub.requests[0].json == {"t_ms": 1200, "comment": "bigger", "base_seq": 3, "node_id": "title"}
    assert stub.requests[1].json == {"t_ms": 0, "comment": "nice", "base_seq": 4, "apply": False}


def test_variants_list_pick(client, stub):
    stub.reply(200, {"object": "studio.creative.variants", "group_id": "g1", "base_seq": 3,
                     "variants": [{"creative_id": "v1", "label": "Red", "rationale": "r", "applied_ops": 1,
                                   "head_seq": 2, "render_id": "r1"}]})
    stub.reply(200, {"object": "studio.creative.variants", "group_id": "g1", "base_seq": 3, "variants": []})
    stub.reply(200, {"head_seq": 4, "version": {"seq": 4, "doc_hash": "h"}, "winner": "v1", "rebased": False})
    c = client.creatives
    v = c.variants(_ID, base_seq=3, count=2, focus=["hook", "cta"], render=False)
    assert v["variants"][0]["render_id"] == "r1"
    assert c.list_variants(_ID)["group_id"] == "g1"
    assert c.pick_variant(_ID, "v/1", base_seq=3)["winner"] == "v1"
    assert [(r.method, r.path) for r in stub.requests] == [
        ("POST", f"{_BASE}/{_ID}/variants"),
        ("GET", f"{_BASE}/{_ID}/variants"),
        ("POST", f"{_BASE}/{_ID}/variants/v%2F1/pick"),
    ]
    assert stub.requests[0].json == {"base_seq": 3, "count": 2, "focus": ["hook", "cta"], "render": False}
    assert stub.requests[2].json == {"base_seq": 3}


def test_render_sends_ai_label(client, stub):
    stub.reply(202, {"render_id": "r2", "id": "r2", "object": "studio.render", "status": "queued",
                     "cached": False, "creative_id": _ID, "seq": 3, "ai_label": "end_card"})
    r = client.creatives.render(_ID, {"quality": "final"}, ai_label="end_card")
    assert stub.requests[0].json == {"quality": "final", "ai_label": "end_card"}
    assert r["ai_label"] == "end_card"


def test_render_cached_200(client, stub):
    stub.reply(200, {"render_id": "r1", "id": "r1", "object": "studio.render", "status": "succeeded",
                     "cached": True, "creative_id": _ID, "seq": 3, "data": []})
    r = client.creatives.render(_ID, {"quality": "draft"})
    assert r["cached"] is True and r["status"] == "succeeded"
