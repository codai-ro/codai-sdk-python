"""Public voice takedown tickets (E-12b) against the http.server stub."""

from __future__ import annotations

_ID = "7a1b2c3d-0000-4000-8000-000000000090"


def test_create_posts_the_ticket_once(client, stub):
    stub.reply(202, {"id": _ID, "object": "studio.voice_revocation", "status": "open"})
    r = client.voice_revocations.create("owner@example.com", "Ana", "Found my voice in a video.")
    assert r == {"id": _ID, "object": "studio.voice_revocation", "status": "open"}
    assert [(q.method, q.path) for q in stub.requests] == [("POST", "/v1/studio/voice-revocations")]
    assert stub.last.json == {
        "email": "owner@example.com",
        "voice_owner_name": "Ana",
        "details": "Found my voice in a video.",
    }


def test_create_sends_evidence_url_when_given(client, stub):
    stub.reply(202, {"id": _ID, "object": "studio.voice_revocation", "status": "open"})
    client.voice_revocations.create("o@example.com", "Ana", "x", evidence_url="https://example.com/v")
    assert stub.last.json["evidence_url"] == "https://example.com/v"
