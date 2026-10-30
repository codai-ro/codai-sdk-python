"""``client.memory`` against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError


def test_memory_list_routes_and_filters(client, stub):
    stub.reply(200, {"memories": [], "total": 0})
    assert client.memory.list() == {"memories": [], "total": 0}
    assert (stub.last.method, stub.last.path, stub.last.query) == ("GET", "/v1/memory", "")
    stub.reply(200, {"memories": [], "total": 0})
    client.memory.list(tier="episodic", limit=5, offset=10)
    assert stub.last.query == "tier=episodic&limit=5&offset=10"


def test_memory_search(client, stub):
    hit = {"id": "m1", "tier": "semantic", "content": "tea", "relevance": 0.9}
    stub.reply(200, {"memories": [hit]})
    r = client.memory.search("drinks", limit=3)
    assert r["memories"][0]["relevance"] == 0.9
    assert (stub.last.method, stub.last.path, stub.last.query) == ("GET", "/v1/memory/search", "q=drinks&limit=3")


def test_memory_create_omits_importance_unless_given(client, stub):
    stub.reply(201, {"id": "m2"})
    assert client.memory.create("prefers RON") == {"id": "m2"}
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/memory", {"content": "prefers RON"})
    stub.reply(201, {"id": "m3"})
    client.memory.create("x", importance=0.8)
    assert stub.last.json == {"content": "x", "importance": 0.8}


def test_memory_delete_and_404(client, stub):
    stub.reply(200, {"deleted": True})
    assert client.memory.delete("a/b") == {"deleted": True}
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/memory/a%2Fb")
    stub.reply(404, {"error": {"code": "not_found", "message": "No memory with that id."}})
    with pytest.raises(CodaiError):
        client.memory.delete("other")
