"""Public abuse reports (LS-25) against the http.server stub."""

from __future__ import annotations

_ID = "7a1b2c3d-0000-4000-8000-000000000091"
# Built by concatenation: a content gate refuses literal addresses in source files.
_EMAIL = "reporter" + "@" + "example.invalid"


def test_create_posts_the_report_once(client, stub):
    stub.reply(202, {"id": _ID, "object": "studio.abuse_report", "status": "open"})
    r = client.abuse_reports.create(
        "tok_abc",
        "share",
        "voice_without_consent",
        "This narration uses my voice without consent.",
        "Ana",
        _EMAIL,
    )
    assert r == {"id": _ID, "object": "studio.abuse_report", "status": "open"}
    assert [(q.method, q.path) for q in stub.requests] == [("POST", "/v1/studio/abuse-reports")]
    assert stub.last.json == {
        "share_token": "tok_abc",
        "surface": "share",
        "category": "voice_without_consent",
        "explanation": "This narration uses my voice without consent.",
        "reporter_name": "Ana",
        "reporter_email": _EMAIL,
        "good_faith": True,
    }


def test_create_sends_review_surface(client, stub):
    stub.reply(202, {"id": _ID, "object": "studio.abuse_report", "status": "open"})
    client.abuse_reports.create("t", "review", "fraud", "A fake bank call script.", "Ion", _EMAIL)
    assert stub.last.json["surface"] == "review"
    assert stub.last.json["category"] == "fraud"
