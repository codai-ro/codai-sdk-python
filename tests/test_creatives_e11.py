"""``client.creatives`` captions / adapt / lint fix / controls (E-11a) against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_ID = "7a1b2c3d-0000-4000-8000-000000000040"
_BASE = f"/v1/studio/creatives/{_ID}"
_EDIT = {"seq": 4, "doc_hash": "h", "changed": ["captions"], "warnings": [], "rebased": False}


def test_captions_sends_only_given_fields(client, stub):
    result = {**_EDIT, "node_id": "captions", "words": 42, "cached": False, "corrected": True, "cost_micro_usd": 6000}
    stub.reply(200, result)
    stub.reply(200, {**result, "cached": True, "cost_micro_usd": 0})
    assert client.creatives.captions(_ID, preset="karaoke-pop", script="Salut, lume!", retranscribe=False) == result
    assert client.creatives.captions(_ID)["cached"] is True
    assert [(r.method, r.path) for r in stub.requests] == [("POST", f"{_BASE}/captions"), ("POST", f"{_BASE}/captions")]
    assert stub.requests[0].json == {"preset": "karaoke-pop", "script": "Salut, lume!", "retranscribe": False}
    assert stub.requests[1].json == {}


def test_captions_srt_and_vtt_return_text(client, stub):
    srt = "1\n00:00:00,000 --> 00:00:01,200\nȘtiri bune\n"
    vtt = "WEBVTT\n\n00:00.000 --> 00:01.200\nȘtiri bune\n"
    stub.reply(200, srt, {"Content-Type": "text/plain; charset=utf-8"})
    stub.reply(200, vtt, {"Content-Type": "text/vtt; charset=utf-8"})
    assert client.creatives.captions_srt(_ID, node_id="captions", seq=3) == srt
    assert client.creatives.captions_vtt(_ID) == vtt
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"{_BASE}/captions.srt", "node_id=captions&seq=3"),
        ("GET", f"{_BASE}/captions.vtt", ""),
    ]


def test_captions_srt_without_captions_raises_404(client, stub):
    stub.reply(404, {"error": {"message": "No captions.", "type": "invalid_request_error", "code": "not_found"}})
    with pytest.raises(CodaiError) as e:
        client.creatives.captions_srt(_ID)
    assert e.value.status == 404


def test_adapt_sends_platforms_and_focal(client, stub):
    result = {
        **_EDIT,
        "formats": [{"platform": "feed-portrait", "format_id": "4x5", "width": 1080, "height": 1350}],
        "focal": None,
    }
    stub.reply(200, result)
    r = client.creatives.adapt(_ID, ["tiktok", "feed-portrait"], focal="vision", base_seq=3)
    assert r["formats"][0]["format_id"] == "4x5"
    assert (stub.last.method, stub.last.path) == ("POST", f"{_BASE}/adapt")
    assert stub.last.json == {"platforms": ["tiktok", "feed-portrait"], "focal": "vision", "base_seq": 3}


def test_lint_fix_sends_codes_and_agent(client, stub):
    result = {**_EDIT, "fixed": [{"code": "text_too_small", "target": "title"}], "remaining": [], "agent": None}
    stub.reply(200, result)
    stub.reply(200, {**result, "agent": {"ops": 2, "cost_micro_usd": 1200}})
    assert client.creatives.lint_fix(_ID, codes=("text_too_small",))["fixed"][0]["code"] == "text_too_small"
    assert client.creatives.lint_fix(_ID, agent=True, force=True)["agent"]["ops"] == 2
    assert [(r.method, r.path) for r in stub.requests] == [("POST", f"{_BASE}/lint/fix"), ("POST", f"{_BASE}/lint/fix")]
    assert stub.requests[0].json == {"codes": ["text_too_small"]}
    assert stub.requests[1].json == {"agent": True, "force": True}


def test_controls_gets_the_panel(client, stub):
    panel = {
        "head_seq": 3,
        "controls": [
            {"key": "accent", "label": "Accent", "control": {"kind": "color"}, "value": "#e6b731", "type": "color", "locked": False}
        ],
    }
    stub.reply(200, panel)
    assert client.creatives.controls(_ID) == panel
    assert (stub.last.method, stub.last.path) == ("GET", f"{_BASE}/controls")
