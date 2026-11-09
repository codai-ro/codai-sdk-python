"""``client.templates`` + ``creatives.save_template`` against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_ID = "5d2e8f1a-3b4c-4d5e-9f60-7a8b9c0d1e2f"
_CID = "7a1b2c3d-0000-4000-8000-000000000031"
_BASE = "/v1/studio/templates"
_TPL = {
    "id": _ID,
    "object": "studio.template",
    "title": "Promo 9:16",
    "kind": "video",
    "source_creative_id": _CID,
    "source_seq": 7,
    "vars_schema": {
        "headline": {"type": "text", "label": "Headline", "default": "Big sale", "node_id": "n_title", "prop": "text"}
    },
    "thumbnail_url": None,
    "created_at": "2026-10-14T09:00:00Z",
}
_PICK = {"node_id": "n_title", "prop": "text", "key": "headline", "label": "Headline"}


def test_save_list_retrieve_delete(client, stub):
    stub.reply(201, {**_TPL, "doc": {}})
    stub.reply(200, {"object": "list", "data": [_TPL]})
    stub.reply(200, {**_TPL, "doc": {}})
    stub.reply(200, {"id": _ID, "object": "studio.template", "deleted": True})
    saved = client.creatives.save_template(_CID, vars=[_PICK], title="Promo 9:16", seq=7)
    assert saved["vars_schema"]["headline"]["default"] == "Big sale"
    t = client.templates
    assert len(t.list(kind="video", limit=5)["data"]) == 1
    assert t.retrieve("a/b")["title"] == "Promo 9:16"
    assert t.delete(_ID)["deleted"] is True
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("POST", f"/v1/studio/creatives/{_CID}/template", ""),
        ("GET", _BASE, "kind=video&limit=5"),
        ("GET", f"{_BASE}/a%2Fb", ""),
        ("DELETE", f"{_BASE}/{_ID}", ""),
    ]
    assert stub.requests[0].json == {"vars": [_PICK], "title": "Promo 9:16", "seq": 7}


def test_create_creative_from_template(client, stub):
    stub.reply(201, {"id": _CID, "object": "studio.creative", "kind": "video", "head_seq": 1})
    client.creatives.create({"kind": "video", "template": _ID, "vars": {"headline": "Autumn sale"}})
    assert stub.requests[0].json == {"kind": "video", "template": _ID, "vars": {"headline": "Autumn sale"}}


def test_node_not_found(client, stub):
    stub.reply(400, {"error": {"message": "no such node", "type": "invalid_request_error", "code": "node_not_found"}})
    with pytest.raises(CodaiError) as e:
        client.creatives.save_template(_CID, vars=[{"node_id": "nope", "prop": "text", "key": "x"}])
    assert e.value.code == "node_not_found"
