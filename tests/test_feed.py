"""``client.feed`` against the http.server stub."""

from __future__ import annotations

import pytest

import codai

POST = {"id": "p1", "kind": "idea", "body": "x", "author": {"username": "d", "is_me": True}}


def test_feed_routes(client, stub):
    stub.reply(200, {"posts": [POST], "next_cursor": "c2"})
    assert client.feed.list(cursor="c1", limit=5, kind="idea")["next_cursor"] == "c2"
    assert (stub.last.method, stub.last.path, stub.last.query) == ("GET", "/v1/feed", "cursor=c1&limit=5&kind=idea")

    stub.reply(200, {"username": None, "suggested_username": "d_1", "guidelines_version": "2026-10-28"})
    assert client.feed.me()["guidelines_version"] == codai.FEED_GUIDELINES_VERSION
    assert stub.last.path == "/v1/feed/me"

    stub.reply(200, {"post": POST})
    assert client.feed.get("p 1") == POST
    assert stub.last.path == "/v1/feed/posts/p%201"

    body = {"kind": "idea", "body": "x", "guidelines_version": "2026-10-28"}
    stub.reply(201, {"post": POST})
    assert client.feed.create(body) == POST
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/feed/posts", body)

    stub.reply(200, {"deleted": True})
    client.feed.delete("p1")
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/feed/posts/p1")

    stub.reply(200, {"like_count": 1, "liked_by_me": True})
    assert client.feed.like("p1") == {"like_count": 1, "liked_by_me": True}
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/feed/posts/p1/like")

    stub.reply(200, {"like_count": 0, "liked_by_me": False})
    assert client.feed.unlike("p1")["liked_by_me"] is False
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/feed/posts/p1/like")

    stub.reply(201, {"reported": True})
    client.feed.report("p1", "spam", details="ads")
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "POST",
        "/v1/feed/posts/p1/report",
        {"reason": "spam", "details": "ads"},
    )

    stub.reply(200, {"blocks": [{"username": "other", "created_at": "2026-10-28T10:00:00Z"}]})
    assert client.feed.blocks()[0]["username"] == "other"

    stub.reply(201, {"blocked": True, "username": "other"})
    assert client.feed.block("p1") == "other"
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/feed/blocks", {"post_id": "p1"})

    stub.reply(200, {"blocked": False})
    client.feed.unblock("other")
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/feed/blocks/other")


def test_feed_username_required_raises(client, stub):
    stub.reply(409, {"error": {"message": "Choose a username", "type": "invalid_request_error", "code": "username_required"}})
    with pytest.raises(codai.CodaiError) as e:
        client.feed.create({"kind": "project", "body": "x", "guidelines_version": "2026-10-28"})
    assert e.value.status == 409
    assert e.value.code == "username_required"
