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


def test_create_sends_quality_and_music(client, stub):
    stub.reply(202, {**_RUNNING, "quality": "draft", "music": False})
    p = client.productions.create("A promo for our delivery app", quality="draft", music=False)
    assert (p["quality"], p["music"]) == ("draft", False)
    assert stub.requests[0].json == {"brief": "A promo for our delivery app", "quality": "draft", "music": False}


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


_ASSET = "0b7d5a2e-1c3f-4e8a-9b6d-2f4e6a8c0d1e"
_CUT = {"id": _ID, "object": "studio.production", "kind": "cut", "status": "running", "phase": "ingest"}


def test_create_cut_posts_kind_cut_with_only_set_fields(client, stub):
    stub.reply(202, _CUT)
    p = client.productions.create_cut(
        "Un montaj pentru vlogul nostru", [_ASSET], pacing="punchy", captions=False, idempotency_key="c1"
    )
    assert p["kind"] == "cut"
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", "/v1/studio/productions")
    assert req.json == {
        "kind": "cut",
        "brief": "Un montaj pentru vlogul nostru",
        "asset_ids": [_ASSET],
        "pacing": "punchy",
        "captions": False,
    }
    assert req.headers["idempotency-key"] == "c1"


def test_cut_reads_decisions(client, stub):
    stub.reply(200, {"object": "studio.production.cut", "decisions": [{"id": "filler:f1", "enabled": True}]})
    d = client.productions.cut("a/b")
    assert d["decisions"][0]["id"] == "filler:f1"
    assert (stub.requests[0].method, stub.requests[0].path) == ("GET", "/v1/studio/productions/a%2Fb/cut")


def test_revise_cut_posts_overrides(client, stub):
    stub.reply(200, {"creative_id": "c1", "seq": 3, "branch": "cut-1", "decisions": [], "stats": {}, "warnings": []})
    r = client.productions.revise_cut(_ID, disabled=["filler:f1", "+zoom:3"], takes={"c1": "s4"}, base_seq=2)
    assert r["branch"] == "cut-1"
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", f"/v1/studio/productions/{_ID}/cut/revise")
    assert req.json == {"disabled": ["filler:f1", "+zoom:3"], "takes": {"c1": "s4"}, "base_seq": 2}


def test_revise_cut_prompt_and_story_fields(client, stub):
    stub.reply(200, {"creative_id": "c1", "seq": 4, "branch": "main", "decisions": [], "stats": {}, "warnings": [],
                     "prompt": {"path": "fast", "understood": ["about 60 s"], "explanation": None, "unmet": None,
                                "cost_micro_usd": 0}})
    r = client.productions.revise_cut(_ID, prompt="make it 60 s", plan_delta={"keep_only": ["s2"]},
                                      default_format="1x1", broll=False)
    assert r["prompt"]["path"] == "fast"
    assert stub.requests[0].json == {"prompt": "make it 60 s", "plan_delta": {"keep_only": ["s2"]},
                                     "default_format": "1x1", "broll": False}
    client.productions.revise_cut(_ID, reset_target=True, reset_story=True)
    assert stub.requests[1].json == {"target_s": None, "plan_delta": None}


def test_stock_search_query_and_result(client, stub):
    item = {"provider": "pexels", "id": "123", "credit": "Video by Jane Doe on Pexels"}
    stub.reply(200, {"object": "list", "data": [item], "providers_tried": ["pexels"], "warnings": [], "attribution": {}})
    r = client.stock.search("sunrise city", kind="video", max_duration=20, limit=5)
    assert r["data"][0]["credit"] == "Video by Jane Doe on Pexels"
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/studio/stock/search")
    assert stub.last.query == "q=sunrise+city&kind=video&max_duration=20&limit=5"


def test_stock_import_posts_item(client, stub):
    stub.reply(201, {"asset_id": "a1", "credit": "Video by Jane Doe on Pexels", "provider": "pexels"})
    a = client.stock.import_("pexels", "123", "video", target_width=1080)
    assert a["asset_id"] == "a1"
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/studio/stock/import")
    assert stub.last.json == {"provider": "pexels", "id": "123", "kind": "video", "target_width": 1080}
