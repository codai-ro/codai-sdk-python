"""Studio share links, review threads and remix (E-12a) against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError, share_token_from

_ID = "7a1b2c3d-0000-4000-8000-000000000070"
_SHARE = "1b2c3d4e-0000-4000-8000-000000000071"
_THREAD = "2c3d4e5f-0000-4000-8000-000000000072"
_COMMENT = "3d4e5f60-0000-4000-8000-000000000073"
_TOK = "Ab" * 20 + "c_-"  # a syntactically valid (fake) 43-char share token
_BASE = f"/v1/studio/creatives/{_ID}"
_PUB = f"/v1/public/studio/reviews/{_TOK}"


def _thread(status="open"):
    return {
        "id": _THREAD,
        "node_id": "n1",
        "scene_id": None,
        "t_ms": 1200,
        "seq": 4,
        "status": status,
        "resolved_by": None,
        "resolved_at": None,
        "created_at": "2026-10-15T08:00:00Z",
        "comments": [],
    }


def test_share_token_from_accepts_tokens_and_view_review_links_only():
    assert len(_TOK) == 43
    assert share_token_from(f"  {_TOK} ") == _TOK
    assert share_token_from(f"https://hub.codai.ro/s/{_TOK}") == _TOK
    assert share_token_from(f"https://hub.codai.ro/r/{_TOK}?x=1#y") == _TOK
    assert share_token_from(f"https://hub.codai.ro/t/{_TOK}") is None
    assert share_token_from(f"ftp://hub.codai.ro/s/{_TOK}") is None
    assert share_token_from("short") is None


def test_create_list_revoke_share_routes_and_bodies(client, stub):
    stub.reply(201, {"id": _SHARE, "object": "studio.share", "kind": "view", "token": _TOK, "url": f"https://hub.codai.ro/s/{_TOK}"})
    stub.reply(200, {"object": "list", "data": [{"id": _SHARE, "url": None}]})
    stub.reply(204, None)
    assert client.creatives.create_share(_ID, "view", seq=3, allow_remix=False)["token"] == _TOK
    assert client.creatives.list_shares(_ID)["data"][0]["url"] is None
    assert client.creatives.revoke_share(_ID, _SHARE) is None
    assert [(r.method, r.path) for r in stub.requests] == [
        ("POST", f"{_BASE}/shares"),
        ("GET", f"{_BASE}/shares"),
        ("DELETE", f"{_BASE}/shares/{_SHARE}"),
    ]
    assert stub.requests[0].json == {"kind": "view", "seq": 3, "allow_remix": False}


def test_create_share_too_many_raises_409(client, stub):
    stub.reply(409, {"error": {"message": "Too many links.", "type": "invalid_request_error", "code": "too_many_shares"}})
    with pytest.raises(CodaiError) as e:
        client.creatives.create_share(_ID, "review", can_approve=True)
    assert e.value.status == 409
    assert stub.last.json == {"kind": "review", "can_approve": True}


def test_review_state_and_actions(client, stub):
    stub.reply(200, {"status": "draft"})
    stub.reply(200, {"status": "in_review"})
    stub.reply(200, {"status": "draft"})
    assert client.creatives.review(_ID)["status"] == "draft"
    assert client.creatives.request_review(_ID)["status"] == "in_review"
    assert client.creatives.reset_review(_ID)["status"] == "draft"
    assert [(r.method, r.path, r.json) for r in stub.requests] == [
        ("GET", f"{_BASE}/review", None),
        ("POST", f"{_BASE}/review", {"action": "request"}),
        ("POST", f"{_BASE}/review", {"action": "reset"}),
    ]


def test_owner_thread_routes(client, stub):
    stub.reply(200, {"object": "list", "data": [_thread()]})
    stub.reply(201, _thread())
    stub.reply(201, _thread())
    stub.reply(200, _thread("resolved"))
    stub.reply(200, _thread())
    stub.reply(204, None)
    assert len(client.creatives.review_threads(_ID, status="open")["data"]) == 1
    client.creatives.create_review_thread(_ID, "Logo mai mare", node_id="n1", t_ms=1200)
    client.creatives.reply_review_thread(_ID, _THREAD, "Gata")
    assert client.creatives.resolve_review_thread(_ID, _THREAD)["status"] == "resolved"
    assert client.creatives.reopen_review_thread(_ID, _THREAD)["status"] == "open"
    client.creatives.delete_review_comment(_ID, _COMMENT)
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"{_BASE}/review/threads", "status=open"),
        ("POST", f"{_BASE}/review/threads", ""),
        ("POST", f"{_BASE}/review/threads/{_THREAD}/replies", ""),
        ("POST", f"{_BASE}/review/threads/{_THREAD}/resolve", ""),
        ("POST", f"{_BASE}/review/threads/{_THREAD}/reopen", ""),
        ("DELETE", f"{_BASE}/review/comments/{_COMMENT}", ""),
    ]
    assert stub.requests[1].json == {"body": "Logo mai mare", "node_id": "n1", "t_ms": 1200}
    assert stub.requests[2].json == {"body": "Gata"}


def test_shares_get_and_remix_accept_a_link(client, stub):
    stub.reply(200, {"object": "studio.public_share", "seq": 3})
    stub.reply(201, {"id": _ID, "remixed_from": {"share_id": _SHARE, "seq": 3}})
    assert client.shares.get(f"https://hub.codai.ro/s/{_TOK}", locale="ro")["seq"] == 3
    assert client.shares.remix(_TOK, title="Copia mea")["remixed_from"]["seq"] == 3
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", f"/v1/public/studio/shares/{_TOK}", "locale=ro"),
        ("POST", f"/v1/studio/shares/{_TOK}/remix", ""),
    ]
    assert stub.requests[1].json == {"title": "Copia mea"}


def test_reviewer_routes_send_the_name(client, stub):
    link = f"https://hub.codai.ro/r/{_TOK}"
    stub.reply(201, _thread())
    stub.reply(201, _thread())
    stub.reply(200, _thread("resolved"))
    stub.reply(200, _thread())
    stub.reply(200, {"status": "approved", "approved_seq": 4})
    client.shares.comment(link, "Ana", "Super", t_ms=500)
    client.shares.reply(link, _THREAD, "Ana", "Da")
    client.shares.resolve(link, _THREAD, "Ana")
    client.shares.reopen(link, _THREAD, "Ana")
    assert client.shares.decide(link, "Ana", "approve", 4)["approved_seq"] == 4
    assert [(r.method, r.path, r.json) for r in stub.requests] == [
        ("POST", f"{_PUB}/threads", {"name": "Ana", "body": "Super", "t_ms": 500}),
        ("POST", f"{_PUB}/threads/{_THREAD}/replies", {"name": "Ana", "body": "Da"}),
        ("POST", f"{_PUB}/threads/{_THREAD}/resolve", {"name": "Ana"}),
        ("POST", f"{_PUB}/threads/{_THREAD}/reopen", {"name": "Ana"}),
        ("POST", f"{_PUB}/decision", {"name": "Ana", "decision": "approve", "seq": 4}),
    ]


def test_decide_stale_raises_409(client, stub):
    stub.reply(409, {"error": {"message": "Stale.", "type": "invalid_request_error", "code": "stale", "head_seq": 5}})
    with pytest.raises(CodaiError) as e:
        client.shares.decide(_TOK, "Ana", "request_changes", 4, note="Font")
    assert e.value.status == 409
    assert stub.last.json == {"name": "Ana", "decision": "request_changes", "seq": 4, "note": "Font"}


def test_not_a_share_link_raises_without_a_request(client, stub):
    with pytest.raises(ValueError):
        client.shares.get("https://example.com/x")
    assert stub.requests == []
