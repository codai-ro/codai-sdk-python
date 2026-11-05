"""``client.studio.music_room`` (Studio Music Room, MR-09..MR-17) against the http.server stub."""

from __future__ import annotations

import pytest

_ID = "7e2f3a4b-5c6d-4e7f-8091-a2b3c4d5e6f7"
_BASE = "/v1/studio/music-room"
_RUNNING = {"id": _ID, "object": "studio.music_room", "status": "running", "phase": "plan", "gate": None}
_AT_PLAN = {**_RUNNING, "status": "waiting", "phase": "gate_plan", "gate": {"kind": "plan", "since": "2026-10-22T00:01:00Z"}}
_DONE = {**_RUNNING, "status": "succeeded", "phase": "ready", "final_asset_id": "a9"}


def test_create_posts_only_set_fields_and_idempotency_key(client, stub):
    stub.reply(202, _RUNNING)
    r = client.studio.music_room.create(
        "o manea veselă de nuntă", language="ro", genre="manele", vocals=False, instruments=["balkan.accordion"],
        idempotency_key="mr-1",
    )
    assert r["object"] == "studio.music_room"
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", _BASE)
    assert req.json == {
        "brief": "o manea veselă de nuntă",
        "language": "ro",
        "genre": "manele",
        "vocals": False,
        "instruments": ["balkan.accordion"],
    }
    assert req.headers["idempotency-key"] == "mr-1"


def test_get_encodes_id_and_quota_and_list_paths(client, stub):
    stub.reply(200, _AT_PLAN)
    stub.reply(200, {"plan": "pro", "included": 4, "used": 1, "remaining": 3, "period_end": "2026-11-01T00:00:00Z"})
    stub.reply(200, {"object": "list", "data": [_RUNNING], "has_more": False})
    stub.reply(200, {"object": "list", "data": []})
    assert client.studio.music_room.get("a/b")["gate"]["kind"] == "plan"
    assert client.studio.music_room.quota()["remaining"] == 3
    assert len(client.studio.music_room.list(limit=5, before="2026-10-01T00:00:00Z")["data"]) == 1
    client.studio.music_room.list()
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"{_BASE}/a%2Fb", ""),
        ("GET", f"{_BASE}/quota", ""),
        ("GET", _BASE, "limit=5&before=2026-10-01T00%3A00%3A00Z"),
        ("GET", _BASE, ""),
    ]


def test_choose_builds_each_gate_answer(client, stub):
    for _ in range(3):
        stub.reply(200, _RUNNING)
    client.studio.music_room.choose(_ID, "plan", variant=2)
    client.studio.music_room.choose(_ID, "demo")
    client.studio.music_room.choose(_ID, "final", approve=True)
    assert [(r.method, r.path) for r in stub.requests] == [("POST", f"{_BASE}/{_ID}/choose")] * 3
    assert [r.json for r in stub.requests] == [
        {"gate": "plan", "variant": 2},
        {"gate": "demo", "approve": True},
        {"gate": "final", "approve": True},
    ]
    assert "idempotency-key" not in stub.requests[0].headers


def test_direct_posts_direction_with_idempotency_key(client, stub):
    stub.reply(202, _RUNNING)
    client.studio.music_room.direct(_ID, "drums", "fewer fills", section_id="chorus1", idempotency_key="d1")
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", f"{_BASE}/{_ID}/direct")
    assert req.json == {"role": "drums", "direction": "fewer fills", "section_id": "chorus1"}
    assert req.headers["idempotency-key"] == "d1"


_SURGE = {"object": "studio.music_plugin", "format": "clap", "plugin_id": "org.surge-synth-team.surge-xt", "name": "Surge XT"}


def test_plugins_and_plugin_paths(client, stub):
    stub.reply(200, {"object": "list", "data": [_SURGE]})
    stub.reply(200, {"object": "list", "data": []})
    stub.reply(200, _SURGE)
    assert client.studio.music_room.plugins(kind="instrument", q="synth pad")["data"][0]["name"] == "Surge XT"
    client.studio.music_room.plugins()
    assert client.studio.music_room.plugin("clap", "org.surge-synth-team.surge-xt")["name"] == "Surge XT"
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"{_BASE}/plugins", "kind=instrument&q=synth+pad"),
        ("GET", f"{_BASE}/plugins", ""),
        ("GET", f"{_BASE}/plugins/clap/org.surge-synth-team.surge-xt", ""),
    ]


def test_instruments_joins_ids_and_lists_all_without(client, stub):
    page = {"object": "list", "data": [{"id": "drums.kit_rock", "sfz": "Kit.sfz", "note_map": {"36": 48}}],
            "missing": [], "expires_at": "2026-10-30T11:00:00Z"}
    stub.reply(200, page)
    stub.reply(200, page)
    assert client.studio.music_room.instruments(["drums.kit_rock", "piano.grand"])["data"][0]["sfz"] == "Kit.sfz"
    client.studio.music_room.instruments()
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"{_BASE}/instruments", "ids=drums.kit_rock%2Cpiano.grand"),
        ("GET", f"{_BASE}/instruments", ""),
    ]


def test_set_track_plugin_posts_chain_with_idempotency_key_and_clears(client, stub):
    stub.reply(202, _RUNNING)
    stub.reply(202, _RUNNING)
    chain = {
        "role": "keys",
        "plugin": {"format": "clap", "plugin_id": "org.surge-synth-team.surge-xt", "preset": "Warm Pad"},
        "effects": [{"format": "clap", "plugin_id": "com.airwindows.galactic", "params": [{"id": 3, "value": 0.4}]}],
    }
    client.studio.music_room.set_track_plugin(_ID, chain, idempotency_key="p1")
    client.studio.music_room.set_track_plugin(_ID, {"role": "keys", "plugin": None})
    assert [(r.method, r.path) for r in stub.requests] == [("POST", f"{_BASE}/{_ID}/plugin")] * 2
    assert stub.requests[0].json == chain
    assert stub.requests[0].headers["idempotency-key"] == "p1"
    assert stub.requests[1].json == {"role": "keys", "plugin": None}
    assert "idempotency-key" not in stub.requests[1].headers


def test_export_project_posts_dawproject_format(client, stub):
    stub.reply(202, {"id": "e1", "object": "studio.export", "kind": "dawproject", "status": "running"})
    e = client.studio.music_room.export_project(_ID)
    assert e["kind"] == "dawproject"
    assert [(r.method, r.path) for r in stub.requests] == [("POST", f"{_BASE}/{_ID}/export")]
    assert stub.requests[0].query == "format=dawproject"


def test_wait_polls_past_gates_until_succeeded(client, stub):
    stub.reply(200, _RUNNING)
    stub.reply(200, _AT_PLAN)
    stub.reply(200, _DONE)
    assert client.studio.music_room.wait(_ID, interval=0.01)["final_asset_id"] == "a9"
    assert len(stub.requests) == 3


def test_wait_until_gate_returns_at_the_first_gate(client, stub):
    stub.reply(200, _RUNNING)
    stub.reply(200, _AT_PLAN)
    stub.reply(200, _DONE)
    r = client.studio.music_room.wait(_ID, until_gate=True, interval=0.01)
    assert r["status"] == "waiting" and r["gate"]["kind"] == "plan"
    assert len(stub.requests) == 2


def test_wait_times_out(client, stub):
    stub.reply(200, _RUNNING)
    with pytest.raises(TimeoutError):
        client.studio.music_room.wait(_ID, interval=0.05, timeout=0.01)
