"""PR-04 / PR-05 / PR-07 pending-prompt SDK methods: list filters, bulk, events, instantiate, export."""

from __future__ import annotations

import urllib.parse


def test_prompts_list_filters(client, stub):
    stub.reply(200, {"data": []})
    client.prompts.list(
        status="all",
        tag=["ops", "rc19"],
        priority_min=2,
        q="ship it",
        templates="only",
        sort="priority",
        order="desc",
    )
    assert stub.last.method == "GET" and stub.last.path == "/v1/prompts"
    assert urllib.parse.parse_qs(stub.last.query) == {
        "status": ["all"],
        "tag": ["ops,rc19"],
        "priority_min": ["2"],
        "q": ["ship it"],
        "templates": ["only"],
        "sort": ["priority"],
        "order": ["desc"],
    }
    stub.reply(200, {"data": []})
    client.prompts.list(tag="ops")
    assert stub.last.query == "tag=ops"


def test_prompts_create_and_update_carry_organise_fields(client, stub):
    stub.reply(201, {"id": "p1", "created": True, "superseded": 0})
    body = {"prompt": "p", "tags": ["ops"], "priority": 3, "recurrence": {"every": "day", "at": "07:00"}}
    client.prompts.create(body)
    assert stub.last.json == body
    stub.reply(200, {"id": "p1"})
    client.prompts.update("p1", {"next_prompt_id": "p2", "launch": {"model": "codai"}, "is_template": True})
    assert stub.last.json == {"next_prompt_id": "p2", "launch": {"model": "codai"}, "is_template": True}


def test_prompts_bulk_events_instantiate(client, stub):
    stub.reply(200, {"updated": 2})
    assert client.prompts.bulk(["p1", "p2"], "tag", tags=["x"]) == {"updated": 2}
    assert stub.last.method == "POST" and stub.last.path == "/v1/prompts/bulk"
    assert stub.last.json == {"ids": ["p1", "p2"], "action": "tag", "tags": ["x"]}
    stub.reply(200, {"updated": 1})
    client.prompts.bulk(["p1"], "snooze", not_before="2026-11-01")
    assert stub.last.json == {"ids": ["p1"], "action": "snooze", "not_before": "2026-11-01"}
    stub.reply(200, {"events": [{"kind": "created", "detail": {}, "created_at": "2026-10-20T00:00:00Z"}]})
    assert client.prompts.events("p 1")["events"][0]["kind"] == "created"
    assert stub.last.method == "GET" and stub.last.path == "/v1/prompts/p%201/events"
    stub.reply(201, {"id": "p9", "is_template": False})
    assert client.prompts.instantiate("p1")["id"] == "p9"
    assert stub.last.method == "POST" and stub.last.path == "/v1/prompts/p1/instantiate"


def test_prompts_export_returns_text(client, stub):
    stub.reply(200, 'title,status\r\n"a,b",open\r\n', {"content-type": "text/csv"})
    assert client.prompts.export_prompts(tag="ops") == 'title,status\r\n"a,b",open\r\n'
    assert stub.last.path == "/v1/prompts/export"
    assert urllib.parse.parse_qs(stub.last.query) == {"tag": ["ops"], "format": ["csv"]}
    stub.reply(200, "# Pending prompts\n", {"content-type": "text/markdown"})
    assert client.prompts.export_prompts("md", status="open").startswith("# Pending prompts")
    assert urllib.parse.parse_qs(stub.last.query) == {"status": ["open"], "format": ["md"]}
