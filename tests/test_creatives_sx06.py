"""SX-06: named branches, compose frames, filmstrips and the Studio job queue."""

from __future__ import annotations

_ID = "7a1b2c3d-0000-4000-8000-000000000061"
_BASE = f"/v1/studio/creatives/{_ID}"

_BRANCH = {
    "object": "studio.creative.branch",
    "name": "shorter-cut",
    "head_seq": 6,
    "base_branch": "main",
    "base_seq": 5,
    "created_at": "2026-11-06T10:00:00.000Z",
    "updated_at": "2026-11-06T10:00:00.000Z",
}


def test_branches_create_delete(client, stub):
    stub.reply(200, {"object": "list", "data": [dict(_BRANCH, name="main", base_branch=None, base_seq=None), _BRANCH]})
    stub.reply(201, _BRANCH)
    stub.reply(200, {"object": "studio.creative.branch", "name": "shorter-cut", "deleted": True})
    c = client.creatives
    assert [b["name"] for b in c.branches(_ID)["data"]] == ["main", "shorter-cut"]
    assert c.create_branch(_ID, "shorter-cut", from_branch="main", seq=5)["base_seq"] == 5
    assert c.delete_branch(_ID, "shorter-cut")["deleted"] is True
    assert [(r.method, r.path) for r in stub.requests] == [
        ("GET", f"{_BASE}/branches"),
        ("POST", f"{_BASE}/branches"),
        ("DELETE", f"{_BASE}/branches/shorter-cut"),
    ]
    assert stub.requests[1].json == {"name": "shorter-cut", "from": "main", "seq": 5}


def test_branch_kwarg_reaches_every_branch_aware_call(client, stub):
    stub.reply(200, {"id": _ID, "branch": "shorter-cut"})
    stub.reply(200, {"object": "list", "branch": "shorter-cut", "data": [], "next_before_seq": None})
    stub.reply(200, {"seq": 7, "branch": "shorter-cut", "doc_hash": "h", "changed": [], "warnings": [], "rebased": False})
    stub.reply(200, {"id": _ID, "head_seq": 8, "seq": 8, "branch": "shorter-cut"})
    stub.reply(200, {"id": _ID, "head_seq": 9, "seq": 9, "branch": "main"})
    stub.reply(201, {"id": _ID})
    c = client.creatives
    c.retrieve(_ID, branch="shorter-cut")
    c.versions(_ID, limit=10, branch="shorter-cut")
    assert c.edit(_ID, base_seq=6, ops=[], branch="shorter-cut")["branch"] == "shorter-cut"
    c.revert(_ID, 5, branch="shorter-cut")
    c.revert(_ID, 4)
    c.fork(_ID, seq=6, branch="shorter-cut")
    r = stub.requests
    assert r[0].query == "branch=shorter-cut"
    assert r[1].query == "limit=10&branch=shorter-cut"
    assert r[2].json == {"base_seq": 6, "ops": [], "branch": "shorter-cut"}
    assert r[3].json == {"seq": 5, "branch": "shorter-cut"}
    assert r[4].json == {"seq": 4}
    assert r[5].json == {"seq": 6, "branch": "shorter-cut"}


def test_filmstrip_compose_frame_and_jobs(client, stub):
    stub.reply(200, {
        "object": "studio.creative.filmstrip",
        "frame_job_id": None,
        "status": "succeeded",
        "frames": [{"t_ms": 1500, "url": "https://x/f.png", "width": 320, "height": 180, "cached": True,
                    "clip_id": "clip-a"}],
        "head_seq": 3,
        "billed_micro_usd": "0",
    })
    stub.reply(202, {"object": "studio.creative.frame_job", "frame_job_id": "j", "status": "running", "head_seq": 3})
    stub.reply(200, {"object": "list", "data": [{"id": "a", "kind": "render", "status": "running", "progress": 0.4,
                                                 "stage": "encode", "title": None, "creative_id": _ID,
                                                 "created_at": None, "updated_at": None, "eta_ms": 12000,
                                                 "error": None}]})
    c = client.creatives
    fs = c.filmstrip(_ID, clip_ids=["clip-a"], branch="shorter-cut", idempotency_key="k1")
    assert fs["frames"][0]["clip_id"] == "clip-a"
    c.frame(_ID, t_ms=[0], engine="compose")
    jobs = c.jobs(creative_id=_ID, limit=5)
    assert jobs["data"][0]["kind"] == "render"
    r = stub.requests
    assert (r[0].method, r[0].path) == ("POST", f"{_BASE}/filmstrip")
    assert r[0].json == {"branch": "shorter-cut", "clip_ids": ["clip-a"]}
    assert r[0].headers.get("idempotency-key") == "k1"
    assert r[1].json == {"t_ms": [0], "engine": "compose"}
    assert (r[2].method, r[2].path, r[2].query) == ("GET", "/v1/studio/jobs", f"creative_id={_ID}&limit=5")
