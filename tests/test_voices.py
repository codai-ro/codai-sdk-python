"""Voice passport singing consent (D37, beta) against the http.server stub."""

from __future__ import annotations

_VOICE = "7a1b2c3d-0000-4000-8000-0000000000a1"
_SESSION = "7a1b2c3d-0000-4000-8000-0000000000b2"


def test_add_singing_consent_posts_the_session(client, stub):
    stub.reply(
        200,
        {
            "id": _VOICE,
            "object": "studio.voice",
            "singing": {"status": "active", "consented_at": "2026-10-22T10:05:00.000Z", "revoked_at": None,
                        "quality": "beta"},
        },
    )
    v = client.voices.add_singing_consent(_VOICE, _SESSION)
    assert v["singing"]["status"] == "active" and v["singing"]["quality"] == "beta"
    assert [(q.method, q.path) for q in stub.requests] == [("POST", f"/v1/studio/voices/{_VOICE}/singing-consent")]
    assert stub.last.json == {"session_id": _SESSION}


def test_revoke_singing_consent_deletes(client, stub):
    stub.reply(204)
    assert client.voices.revoke_singing_consent(_VOICE) is None
    assert [(q.method, q.path) for q in stub.requests] == [("DELETE", f"/v1/studio/voices/{_VOICE}/singing-consent")]
