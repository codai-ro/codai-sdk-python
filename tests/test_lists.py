"""``client.lists`` and ``client.schedules.audit`` against the http.server stub."""

from __future__ import annotations

LIST = {"id": "l1", "name": "Inbox", "preset": "inbox"}
ITEM = {"id": "i1", "list_id": "l1", "title": "x"}


def test_lists_json_routes(client, stub):
    stub.reply(200, {"lists": [LIST]})
    assert client.lists.list() == [LIST]
    assert (stub.last.method, stub.last.path, stub.last.query) == ("GET", "/v1/lists", "")

    stub.reply(200, {"lists": []})
    client.lists.list(archived=True)
    assert stub.last.query == "archived=1"

    stub.reply(201, {"list": LIST})
    assert client.lists.create({"name": "Books"}) == LIST
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/lists", {"name": "Books"})

    stub.reply(200, {"ok": True})
    assert client.lists.reorder(["a", "b"]) == {"ok": True}
    assert (stub.last.method, stub.last.path, stub.last.json) == ("PATCH", "/v1/lists/order", {"ids": ["a", "b"]})

    stub.reply(200, {"list": LIST})
    assert client.lists.update("l 1", {"name": "N"}) == LIST
    assert (stub.last.method, stub.last.path) == ("PATCH", "/v1/lists/l%201")

    stub.reply(200, {"ok": True})
    client.lists.delete("l1")
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/lists/l1")

    stub.reply(200, {"items": [ITEM]})
    assert client.lists.items("l1", done=True, limit=5) == [ITEM]
    assert (stub.last.path, stub.last.query) == ("/v1/lists/l1/items", "done=1&limit=5")

    stub.reply(200, {"item": ITEM})
    assert client.lists.update_item("i1", {"done": True}) == ITEM
    assert (stub.last.method, stub.last.path, stub.last.json) == ("PATCH", "/v1/lists/items/i1", {"done": True})

    stub.reply(200, {"ok": True})
    client.lists.delete_item("i1")
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/lists/items/i1")


def test_lists_add_and_share_accept_200_and_201(client, stub):
    stub.reply(201, {"item": ITEM, "created": True})
    assert client.lists.add("l1", {"url": "https://x.ro", "client_id": "c1"})["created"] is True
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/lists/l1/items")

    stub.reply(200, {"item": ITEM, "created": False})
    assert client.lists.add("l1", {"url": "https://x.ro"})["created"] is False

    stub.reply(201, {"item": ITEM, "list": LIST, "created": True})
    assert client.lists.share({"text": "hi", "auto": True})["list"] == LIST
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/share", {"text": "hi", "auto": True})


def test_lists_export_markdown_and_image(client, stub):
    stub.reply(200, "# Inbox\n- [ ] x\n", {"Content-Type": "text/markdown"})
    assert client.lists.export_markdown("l1") == "# Inbox\n- [ ] x\n"
    assert stub.last.path == "/v1/lists/l1/export.md"

    stub.reply(200, b"\x01\x02\x03", {"Content-Type": "image/webp"})
    img = client.lists.image("i1")
    assert img.data == b"\x01\x02\x03" and img.content_type == "image/webp"
    assert stub.last.path == "/v1/lists/items/i1/image"


def test_lists_stream_yields_only_list_frames(client, stub):
    stub.sse(
        [
            ": ping\n\n",
            'event: list\ndata: {"op":"item","listId":"l1","itemId":"i1"}\n\n',
            "event: other\ndata: {}\n\n",
            'event: list\ndata: {"op":"lists"}\n\n',
        ]
    )
    assert list(client.lists.stream()) == [{"op": "item", "listId": "l1", "itemId": "i1"}, {"op": "lists"}]
    assert stub.last.path == "/v1/lists/stream"


def test_schedules_audit(client, stub):
    entry = {"id": 1, "action": "schedule.create", "actor": "user", "at": "now", "detail": {}}
    stub.reply(200, {"audit": [entry]})
    assert client.schedules.audit() == [entry]
    assert (stub.last.method, stub.last.path, stub.last.query) == ("GET", "/v1/schedules/audit", "")

    stub.reply(200, {"audit": []})
    client.schedules.audit(schedule_id="s1", limit=10)
    assert stub.last.query == "schedule_id=s1&limit=10"
