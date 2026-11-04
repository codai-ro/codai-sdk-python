"""``client.creatives`` localisation (E-11b) against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_ID = "7a1b2c3d-0000-4000-8000-000000000050"
_BASE = f"/v1/studio/creatives/{_ID}"
_EDIT = {"seq": 6, "doc_hash": "h", "changed": ["doc"], "warnings": [], "rebased": False}


def test_locales_passes_locale_units_and_paging(client, stub):
    status = {
        "head_seq": 5,
        "source": "en",
        "glossary": ["codai"],
        "total": 2,
        "locales": [{"locale": "ro", "tone": None, "translated": 1, "missing": 1, "stale": 0, "voice": 0}],
        "units": [{"key": "doc:title", "translation": "Reduceri de vară"}],
        "units_total": 2,
    }
    stub.reply(200, status)
    stub.reply(200, {**status, "units": None})
    assert client.creatives.locales(_ID, locale="ro", units=True, offset=0, limit=50)["units"][0]["key"] == "doc:title"
    client.creatives.locales(_ID)
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"{_BASE}/locales", "locale=ro&units=1&offset=0&limit=50"),
        ("GET", f"{_BASE}/locales", ""),
    ]


def test_localize_sends_only_given_fields(client, stub):
    result = {**_EDIT, "locales": [{"locale": "ro", "translated": 12, "remaining": 0, "voice_clips": 0}], "cost_micro_usd": 1800}
    stub.reply(200, result)
    r = client.creatives.localize(_ID, ["ro", "de"], tone="formal", glossary=("codai",), only_missing=False)
    assert r["cost_micro_usd"] == 1800
    assert (stub.last.method, stub.last.path) == ("POST", f"{_BASE}/localize")
    assert stub.last.json == {"locales": ["ro", "de"], "tone": "formal", "glossary": ["codai"], "only_missing": False}


def test_localize_unavailable_raises_503(client, stub):
    stub.reply(503, {"error": {"message": "Translation unavailable.", "type": "api_error", "code": "localize_unavailable"}})
    with pytest.raises(CodaiError) as e:
        client.creatives.localize(_ID, ["ro"])
    assert e.value.status == 503


def test_fork_locale_posts_to_the_encoded_locale(client, stub):
    fork = {"id": "f1", "object": "studio.creative", "locale": "pt-BR", "fork_of": {"creative_id": _ID, "seq": 6}}
    stub.reply(201, fork)
    stub.reply(201, fork)
    assert client.creatives.fork_locale(_ID, "pt-BR", title="Promo (pt-BR)", seq=6)["fork_of"]["seq"] == 6
    client.creatives.fork_locale(_ID, "pt-BR")
    assert [(r.method, r.path, r.json) for r in stub.requests] == [
        ("POST", f"{_BASE}/locales/pt-BR/fork", {"title": "Promo (pt-BR)", "seq": 6}),
        ("POST", f"{_BASE}/locales/pt-BR/fork", {}),
    ]


def test_locale_reaches_compiled_captions_lint_render_and_frame(client, stub):
    stub.reply(200, {"head_seq": 6, "html": "<html>"})
    stub.reply(200, "1\n00:00:00,000 --> 00:00:01,000\nSalut\n", {"Content-Type": "text/plain; charset=utf-8"})
    stub.reply(200, "WEBVTT\n", {"Content-Type": "text/vtt; charset=utf-8"})
    stub.reply(200, {"head_seq": 6, "issues": [], "fixable": 0})
    stub.reply(200, {"head_seq": 6, "issues": [], "fixable": 0})
    stub.reply(202, {"render_id": "r1", "cached": False})
    stub.reply(200, {"status": "succeeded", "frames": []})
    client.creatives.compiled(_ID, format="16x9", locale="ro")
    assert client.creatives.captions_srt(_ID, locale="ro").startswith("1\n")
    client.creatives.captions_vtt(_ID, node_id="captions", locale="de")
    client.creatives.lint(_ID, locale="ro")
    client.creatives.lint(_ID)
    client.creatives.render(_ID, {"quality": "draft"}, locale="ro")
    client.creatives.frame(_ID, t_ms=[0], locale="ro")
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"{_BASE}/compiled", "format=16x9&locale=ro"),
        ("GET", f"{_BASE}/captions.srt", "locale=ro"),
        ("GET", f"{_BASE}/captions.vtt", "node_id=captions&locale=de"),
        ("POST", f"{_BASE}/lint", ""),
        ("POST", f"{_BASE}/lint", ""),
        ("POST", f"{_BASE}/render", ""),
        ("POST", f"{_BASE}/frame", ""),
    ]
    assert stub.requests[3].json == {"locale": "ro"}
    assert stub.requests[4].json is None
    assert stub.requests[5].json == {"quality": "draft", "locale": "ro"}
    assert stub.requests[6].json == {"t_ms": [0], "locale": "ro"}
