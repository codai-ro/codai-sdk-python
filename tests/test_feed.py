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


COMMENT = {
    "id": "c1",
    "post_id": "p1",
    "body": "nice",
    "author": {"username": "d", "is_me": True, "badge": None},
    "status": "visible",
    "created_at": "2026-10-28T10:00:00Z",
}


def test_feed_round2_routes(client, stub):
    stub.reply(200, {"posts": [], "next_cursor": None})
    client.feed.list(lang="ro")
    assert (stub.last.path, stub.last.query) == ("/v1/feed", "lang=ro")

    profile = {"username": "codai", "badge": "team", "is_me": False, "blocked": False, "post_count": 12, "first_post_at": None}
    stub.reply(200, {"profile": profile, "posts": [POST], "next_cursor": None})
    assert client.feed.user("Co dai", cursor="c1", limit=5, kind="project", lang="en")["profile"]["badge"] == "team"
    assert (stub.last.method, stub.last.path, stub.last.query) == (
        "GET",
        "/v1/feed/users/Co%20dai",
        "cursor=c1&limit=5&kind=project&lang=en",
    )

    stub.reply(200, {"comments": [COMMENT], "next_cursor": None})
    assert client.feed.comments("p1", cursor="x", limit=10)["comments"] == [COMMENT]
    assert (stub.last.path, stub.last.query) == ("/v1/feed/posts/p1/comments", "cursor=x&limit=10")

    stub.reply(201, {"comment": COMMENT, "comment_count": 4})
    assert client.feed.comment("p1", "nice", "2026-10-28", client_id="k1")["comment_count"] == 4
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "POST",
        "/v1/feed/posts/p1/comments",
        {"body": "nice", "guidelines_version": "2026-10-28", "client_id": "k1"},
    )

    stub.reply(200, {"comment": COMMENT, "comment_count": 4})
    client.feed.comment("p1", "again", "2026-10-28")
    assert stub.last.json == {"body": "again", "guidelines_version": "2026-10-28"}

    stub.reply(200, {"deleted": True, "comment_count": 3})
    assert client.feed.delete_comment("c1") == 3
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/feed/comments/c1")

    stub.reply(201, {"reported": True})
    client.feed.report_comment("c1", "spam", details="ads")
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "POST",
        "/v1/feed/comments/c1/report",
        {"reason": "spam", "details": "ads"},
    )

    stub.reply(201, {"blocked": True, "username": "codai"})
    assert client.feed.block(username="codai") == "codai"
    assert stub.last.json == {"username": "codai"}

    stub.reply(201, {"blocked": True, "username": "other"})
    assert client.feed.block("p2") == "other"
    assert stub.last.json == {"post_id": "p2"}

    with pytest.raises(ValueError):
        client.feed.block()
    with pytest.raises(ValueError):
        client.feed.block("p2", username="codai")


def test_feed_user_not_found_raises(client, stub):
    stub.reply(404, {"error": {"message": "Not found", "type": "invalid_request_error", "code": "user_not_found"}})
    with pytest.raises(codai.CodaiError) as e:
        client.feed.user("ghost")
    assert (e.value.status, e.value.code) == (404, "user_not_found")


def test_feed_preview_image(client, stub):
    stub.reply(200, b"\x09", {"Content-Type": "image/webp"})
    img = client.feed.preview_image("p1")
    assert (img.data, img.content_type) == (b"\x09", "image/webp")
    assert stub.last.path == "/v1/feed/previews/p1"


def test_feed_round3_routes(client, stub):
    stub.reply(200, {"posts": [], "next_cursor": None})
    client.feed.list(limit=5, scope="following", q="România", tag="agents")
    assert (stub.last.path, stub.last.query) == ("/v1/feed", "limit=5&scope=following&q=Rom%C3%A2nia&tag=agents")

    stub.reply(200, {"tags": [{"tag": "agents", "count": 4}]})
    assert client.feed.tags(prefix="ag", limit=3) == [{"tag": "agents", "count": 4}]
    assert (stub.last.path, stub.last.query) == ("/v1/feed/tags", "prefix=ag&limit=3")

    stub.reply(201, {"following": True, "username": "ana_m"})
    assert client.feed.follow("ana_m") == {"following": True, "username": "ana_m"}
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/feed/follows", {"username": "ana_m"})

    stub.reply(200, {"following": False})
    client.feed.unfollow("ana m")
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/feed/follows/ana%20m")

    follow = {"username": "ana_m", "badge": None, "created_at": "2026-10-30T10:00:00Z"}
    stub.reply(200, {"follows": [follow], "next_cursor": None})
    assert client.feed.follows(cursor="x", limit=10)["follows"] == [follow]
    assert (stub.last.path, stub.last.query) == ("/v1/feed/follows", "cursor=x&limit=10")

    reply = {**COMMENT, "id": "c2", "parent_id": "c1", "mentions": ["ana_m"]}
    stub.reply(201, {"comment": reply, "comment_count": 2})
    assert client.feed.comment("p1", "Agreed @ana_m", "2026-10-28", client_id="k2", parent_id="c1")["comment"] == reply
    assert stub.last.json == {
        "body": "Agreed @ana_m",
        "guidelines_version": "2026-10-28",
        "parent_id": "c1",
        "client_id": "k2",
    }

    stub.reply(200, {"post": POST})
    assert client.feed.public_post("p1") == POST
    assert stub.last.path == "/v1/public/feed/posts/p1"

    stub.reply(200, {"profile": {"username": "ana_m"}, "posts": [], "next_cursor": None})
    client.feed.public_user("ana_m", limit=2)
    assert (stub.last.path, stub.last.query) == ("/v1/public/feed/users/ana_m", "limit=2")

    stub.reply(200, {"posts": [], "users": []})
    assert client.feed.public_sitemap() == {"posts": [], "users": []}
    assert stub.last.path == "/v1/public/feed/sitemap"

    assert client.feed.media_url("p 1").endswith("/v1/feed/media/p%201")
    assert client.feed.media_poster_url("p1").endswith("/v1/feed/media/p1/poster")


def test_feed_unfollow_not_found_raises(client, stub):
    stub.reply(404, {"error": {"message": "Not following", "type": "invalid_request_error", "code": "follow_not_found"}})
    with pytest.raises(codai.CodaiError) as e:
        client.feed.unfollow("ana_m")
    assert (e.value.status, e.value.code) == (404, "follow_not_found")
