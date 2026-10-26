"""``client.lyrics`` (MU-06) and ``client.creatives.render_audio`` (MU-05) against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_CREATIVE = "3f2b8c1e-0000-4000-8000-000000000001"
_RENDER = "6d1e2f3a-4b5c-4d6e-8f70-8192a3b4c5d6"
_LYRICS = {
    "object": "studio.lyrics",
    "title": "Vară",
    "language": "ro",
    "rhyme_scheme": "AABB",
    "syllables_per_line": 8,
    "sections": [
        {"kind": "verse", "lines": [{"text": "Soarele răsare iar", "syllables": 7, "rhyme": "ar", "letter": "A",
                                     "off": False}]},
    ],
    "text": "[verse]\nSoarele răsare iar",
    "report": {"lines": 1, "off_lines": 0, "off_ratio": 0, "pairs": 0, "rhymed": 0, "repair_ratio": 0},
    "repaired": False,
    "cost_micro_usd": "1200",
}


def test_write_sends_only_set_fields_and_idempotency_key(client, stub):
    stub.reply(200, _LYRICS)
    r = client.lyrics.write("o vară la mare", "ro", rhyme_scheme="AABB", syllables_per_line=8,
                            structure=["verse", "chorus"], idempotency_key="ly-1")
    assert r["sections"][0]["lines"][0]["letter"] == "A"
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", "/v1/studio/lyrics")
    assert req.json == {"brief": "o vară la mare", "language": "ro", "rhyme_scheme": "AABB",
                        "syllables_per_line": 8, "structure": ["verse", "chorus"]}
    assert req.headers["idempotency-key"] == "ly-1"


def test_align_posts_to_align_route(client, stub):
    stub.reply(200, {"object": "studio.lyrics_alignment", "creative_id": _CREATIVE, "clip_id": "vox1",
                     "applied": False, "lines": [{"startMs": 1200, "endMs": 3400, "text": "Soarele răsare iar"}],
                     "lrc": "[00:01.20]Soarele răsare iar", "match_ratio": 0.92, "cached": True,
                     "cost_micro_usd": "0"})
    r = client.lyrics.align(_CREATIVE, "vox1", "[verse]\nSoarele răsare iar", apply=False)
    assert r["lrc"].startswith("[00:01.20]")
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", "/v1/studio/lyrics/align")
    assert req.json == {"creative_id": _CREATIVE, "clip_id": "vox1", "lyrics_text": "[verse]\nSoarele răsare iar",
                        "apply": False}
    assert "idempotency-key" not in req.headers


def test_insufficient_funds_raises(client, stub):
    stub.reply(402, {"error": {"message": "Not enough credit.", "type": "insufficient_funds",
                               "code": "insufficient_funds"}})
    with pytest.raises(CodaiError):
        client.lyrics.write("abc", "en")


def test_render_audio_posts_audio_body(client, stub):
    stub.reply(202, {"render_id": _RENDER, "id": _RENDER, "object": "studio.render", "status": "queued",
                     "target": "audio", "formats": ["wav", "flac"], "stems": True, "lrc": True,
                     "outputs": [{"kind": "mix", "format": "wav", "track_id": None, "mime_type": "audio/wav"}],
                     "quote_micro_usd": "94500", "cached": False})
    r = client.creatives.render_audio(_CREATIVE, formats=["wav", "flac"], stems=True, loudness=-16,
                                      idempotency_key="mix-1")
    assert r["target"] == "audio"
    req = stub.requests[0]
    assert (req.method, req.path) == ("POST", f"/v1/studio/creatives/{_CREATIVE}/render")
    assert req.json == {"formats": ["wav", "flac"], "stems": True, "loudness": -16}
    assert req.headers["idempotency-key"] == "mix-1"
