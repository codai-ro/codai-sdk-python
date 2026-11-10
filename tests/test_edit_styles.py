"""``client.edit_styles`` and ``client.productions.restyle_cut`` (SX-44) against the http.server stub."""

from __future__ import annotations

import pytest

_PROD = "6d1e2f3a-4b5c-4d6e-8f70-8192a3b4c5d6"
_KNOBS = {
    "pacing": "punchy",
    "captions": {"preset": "karaoke-pop", "max_words_per_line": 3},
    "zoom": "heavy",
    "broll": {"density": "dense", "stock": True, "generated": "images"},
    "reframe": "fast",
}
_OWN = {"id": 7, "object": "studio.edit_style", "builtin": False, "name": "Mine", "knobs": _KNOBS, "status": "private"}


def test_list_create_update_delete(client, stub):
    stub.reply(200, {"object": "list", "builtin": [], "styles": [_OWN]})
    stub.reply(201, _OWN)
    stub.reply(200, {**_OWN, "name": "Renamed"})
    stub.reply(200, {"id": 7, "object": "studio.edit_style", "deleted": True})
    e = client.edit_styles
    assert e.list(lang="ro", gallery=True)["styles"][0]["id"] == 7
    assert e.create("Mine", _KNOBS)["status"] == "private"
    assert e.update(7, name="Renamed")["name"] == "Renamed"
    assert e.delete(7)["deleted"] is True
    r = stub.requests
    assert [(x.method, x.path) for x in r] == [
        ("GET", "/v1/studio/edit-styles"),
        ("POST", "/v1/studio/edit-styles"),
        ("PATCH", "/v1/studio/edit-styles/7"),
        ("DELETE", "/v1/studio/edit-styles/7"),
    ]
    assert r[0].query == "lang=ro&gallery=1"
    assert r[1].json == {"name": "Mine", "knobs": _KNOBS}
    assert r[2].json == {"name": "Renamed"}


def test_update_without_fields_raises(client):
    with pytest.raises(ValueError):
        client.edit_styles.update(7)


def test_submit_gallery_copy_report_moderation(client, stub):
    stub.reply(200, {**_OWN, "status": "pending"})
    stub.reply(200, {"object": "list", "data": [{**_OWN, "id": 9, "author": "ana"}], "next_cursor": None})
    stub.reply(201, {**_OWN, "id": 10, "copied_from": 9})
    stub.reply(201, {"created": True, "hidden": False})
    stub.reply(200, {"object": "list", "data": []})
    stub.reply(200, {**_OWN, "status": "approved"})
    e = client.edit_styles
    assert e.submit(7)["status"] == "pending"
    assert e.gallery(limit=12, cursor=40)["data"][0]["author"] == "ana"
    assert e.copy(9)["copied_from"] == 9
    assert e.report(9, "spam", details="ads") == {"created": True, "hidden": False}
    assert e.moderation_queue(status="pending")["data"] == []
    assert e.moderate(7, "approve")["status"] == "approved"
    r = stub.requests
    assert [(x.method, x.path) for x in r] == [
        ("POST", "/v1/studio/edit-styles/7/submit"),
        ("GET", "/v1/studio/edit-styles/gallery"),
        ("POST", "/v1/studio/edit-styles/9/copy"),
        ("POST", "/v1/studio/edit-styles/9/report"),
        ("GET", "/v1/studio/edit-styles/moderation"),
        ("POST", "/v1/studio/edit-styles/7/moderate"),
    ]
    assert r[1].query == "limit=12&cursor=40"
    assert r[3].json == {"reason": "spam", "details": "ads"}
    assert r[4].query == "status=pending"
    assert r[5].json == {"action": "approve"}


def test_restyle_cut_posts_style_and_returns_job(client, stub):
    job = {"id": "j1", "object": "studio.production", "kind": "cut_restyle", "status": "running", "phase": "broll"}
    stub.reply(
        200,
        {
            "creative_id": "c1",
            "seq": 4,
            "branch": "main",
            "decisions": [],
            "stats": {},
            "warnings": [],
            "style": "builtin:fast-social",
            "broll_slots_needed": 5,
            "broll_job": job,
        },
    )
    stub.reply(200, {**job, "status": "succeeded", "phase": "ready", "seq": 5})
    r = client.productions.restyle_cut(_PROD, "fast-social", base_seq=3)
    assert r["style"] == "builtin:fast-social"
    assert client.productions.retrieve(r["broll_job"]["id"])["seq"] == 5
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", f"/v1/studio/productions/{_PROD}/cut/restyle")
    assert req.json == {"style": "fast-social", "base_seq": 3}
    assert stub.requests[1].path == "/v1/studio/productions/j1"


def test_restyle_cut_numeric_style_without_broll(client, stub):
    stub.reply(200, {"creative_id": "c1", "seq": 4, "broll_job": None})
    client.productions.restyle_cut(_PROD, 7, fetch_broll=False)
    assert stub.requests[0].json == {"style": 7, "fetch_broll": False}


def test_cut_variants_retrieve_and_select(client, stub):
    score = {"total": 81, "hook": 90, "flow": 75, "value": 80, "fit": 60, "source": "blend", "weakest_axis": "fit"}
    body = {"object": "studio.production.cut_variants", "variants": [{"id": "v2", "score": score}], "judged": True}
    stub.reply(200, body)
    stub.reply(200, body)
    stub.reply(200, {"creative_id": "c1", "seq": 4, "variant": "v2", "score": score})
    p = client.productions
    assert p.cut_variants(_PROD, n=2, judge=False)["variants"][0]["id"] == "v2"
    assert p.retrieve_cut_variants(_PROD)["judged"] is True
    assert p.select_cut_variant(_PROD, "v2", base_seq=3)["seq"] == 4
    r = stub.requests
    assert [(x.method, x.path) for x in r] == [
        ("POST", f"/v1/studio/productions/{_PROD}/cut/variants"),
        ("GET", f"/v1/studio/productions/{_PROD}/cut/variants"),
        ("POST", f"/v1/studio/productions/{_PROD}/cut/select"),
    ]
    assert r[0].json == {"n": 2, "judge": False}
    assert r[2].json == {"variant": "v2", "base_seq": 3}


def test_cut_wave3_methods(client, stub):
    hooks = {"object": "studio.production.cut_hooks", "judged": True, "hooks": [{"id": "h1", "sentence": "s7"}]}
    topics = {"object": "studio.production.cut_topics", "topics": [{"id": "t1", "label": "Pricing"}]}
    stub.reply(200, hooks)
    stub.reply(200, hooks)
    stub.reply(200, {"object": "studio.production.cut_lengths", "presets": [{"id": "30", "target_s": 30}]})
    stub.reply(200, {"object": "studio.production.cut_attention", "heuristic": True, "dips": []})
    stub.reply(200, topics)
    stub.reply(200, topics)
    stub.reply(200, {"object": "studio.production.cut_renders", "renders": [{"id": "30", "creative_id": "c2"}]})
    stub.reply(202, {"id": "e1", "kind": "podcast", "spotify_upload_url": "https://creators.spotify.com/pod/login"})
    p = client.productions
    assert p.cut_hooks(_PROD, n=2, judge=True)["hooks"][0]["sentence"] == "s7"
    assert p.retrieve_cut_hooks(_PROD)["judged"] is True
    assert p.cut_lengths(_PROD)["presets"][0]["target_s"] == 30
    assert p.cut_attention(_PROD)["heuristic"] is True
    assert p.cut_topics(_PROD, refresh=False)["topics"][0]["label"] == "Pricing"
    assert p.retrieve_cut_topics(_PROD)["topics"][0]["id"] == "t1"
    assert p.cut_renders(_PROD, "lengths", ids=["30"], quality="final", idempotency_key="k1")["renders"][0]["id"] == "30"
    e = p.cut_podcast(_PROD, notes=False, include_video=False, mp3={"channels": 1, "bitrate_k": 128})
    assert e["kind"] == "podcast"
    r = stub.requests
    base = f"/v1/studio/productions/{_PROD}/cut"
    assert [(x.method, x.path) for x in r] == [
        ("POST", f"{base}/hooks"),
        ("GET", f"{base}/hooks"),
        ("GET", f"{base}/lengths"),
        ("GET", f"{base}/attention"),
        ("POST", f"{base}/topics"),
        ("GET", f"{base}/topics"),
        ("POST", f"{base}/renders"),
        ("POST", f"{base}/podcast"),
    ]
    assert r[0].json == {"n": 2, "judge": True}
    assert r[4].json == {"refresh": False}
    assert r[6].json == {"kind": "lengths", "ids": ["30"], "quality": "final"}
    assert r[6].headers["idempotency-key"] == "k1"
    assert r[7].json == {"notes": False, "include_video": False, "mp3": {"channels": 1, "bitrate_k": 128}}


def test_revise_and_create_cut_wave3_fields(client, stub):
    stub.reply(200, {"creative_id": "c1", "seq": 5, "voice_cleanup_job": "j1"})
    stub.reply(200, {"creative_id": "c1", "seq": 6})
    stub.reply(202, {"id": _PROD, "kind": "cut"})
    p = client.productions
    assert p.revise_cut(_PROD, hook="s7", topics=["t1"], drop=["s9"], voice_cleanup=True)["voice_cleanup_job"] == "j1"
    p.revise_cut(_PROD, reset_hook=True, topics=[])
    p.create_cut("A ten char brief", ["a1"], voice_cleanup="off")
    r = stub.requests
    assert r[0].json == {"hook": "s7", "topics": ["t1"], "drop": ["s9"], "voice_cleanup": True}
    assert r[1].json == {"topics": [], "hook": None}
    assert r[2].json["voice_cleanup"] == "off"
