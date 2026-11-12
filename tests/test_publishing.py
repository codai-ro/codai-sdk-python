"""``client.publishing`` (SX-30) against the http.server stub."""

from __future__ import annotations


def test_connections(client, stub):
    stub.reply(200, {"object": "list", "enabled": True, "data": []})
    stub.reply(200, {"authorize_url": "https://accounts.google.com/x", "state": "s", "code_verifier": "v"})
    stub.reply(200, {"object": "studio.connection", "id": "c1"})
    stub.reply(200, {"object": "studio.connection", "id": "c1", "deleted": True})
    p = client.publishing
    assert p.list_connections()["enabled"] is True
    assert p.start_connection()["state"] == "s"
    assert p.exchange_connection("k", "s", "v")["id"] == "c1"
    assert p.delete_connection("c 1")["deleted"] is True
    r = stub.requests
    assert [(x.method, x.path) for x in r] == [
        ("GET", "/v1/studio/connections"),
        ("POST", "/v1/studio/connections/youtube/start"),
        ("POST", "/v1/studio/connections/youtube/exchange"),
        ("DELETE", "/v1/studio/connections/c%201"),
    ]
    assert r[2].json == {"code": "k", "state": "s", "code_verifier": "v"}


def test_publications(client, stub):
    pub = {"object": "studio.publication", "id": "p1", "phase": "queued"}
    stub.reply(200, {"object": "studio.publish_draft"})
    stub.reply(202, pub)
    stub.reply(200, pub)
    stub.reply(200, {**pub, "phase": "cancelled"})
    p = client.publishing
    p.draft("r1", "T", hashtags=["ai"])
    body = {
        "render_id": "r1",
        "connection_id": "c1",
        "title": "T",
        "privacy": "unlisted",
        "made_for_kids": False,
        "contains_synthetic_media": True,
    }
    assert p.create(body)["id"] == "p1"
    assert p.retrieve("p1")["phase"] == "queued"
    assert p.cancel("p1")["phase"] == "cancelled"
    r = stub.requests
    assert [(x.method, x.path) for x in r] == [
        ("POST", "/v1/studio/publish/draft"),
        ("POST", "/v1/studio/publish"),
        ("GET", "/v1/studio/publish/p1"),
        ("POST", "/v1/studio/publish/p1/cancel"),
    ]
    assert r[0].json == {"render_id": "r1", "title": "T", "hashtags": ["ai"]}
    assert r[1].json == body
