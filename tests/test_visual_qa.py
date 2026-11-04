"""client.visual_qa against the http.server stub: ref normalisation, query/body shapes and error surfacing."""

from __future__ import annotations

from urllib.parse import parse_qs

import pytest

from codai import CodaiError


def test_findings_joins_filters(client, stub):
    stub.reply(200, {"findings": [{"ref": "UI-142"}]})
    r = client.visual_qa.findings(status=["todo", "in-progress"], severity="P0", surface="hub")
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/vqa/findings")
    assert parse_qs(stub.last.query) == {"status": ["todo,in-progress"], "severity": ["P0"], "surface": ["hub"]}
    assert r["findings"][0]["ref"] == "UI-142"


def test_claim_and_resolve_normalise_ref(client, stub):
    stub.reply(200, {"ok": True, "finding": {"status": "in-progress"}})
    stub.reply(200, {"ok": True, "finding": {"status": "fixed"}})
    client.visual_qa.claim(142)
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/vqa/findings/UI-142/claim")
    client.visual_qa.resolve("ui-7", "fixed", fix_ref="abc123")
    assert stub.last.path == "/v1/vqa/findings/UI-7/resolve"
    assert stub.last.json == {"status": "fixed", "fixRef": "abc123"}


def test_recapture_body(client, stub):
    stub.reply(200, {"id": 9, "state": "queued"})
    r = client.visual_qa.recapture(["SCR-hub-ops-agentq"], finding="UI-142")
    assert stub.last.path == "/v1/vqa/recaptures"
    assert stub.last.json == {"screens": ["SCR-hub-ops-agentq"], "finding": "UI-142"}
    assert r == {"id": 9, "state": "queued"}


def test_bad_transition_raises(client, stub):
    stub.reply(409, {"error": {"code": "bad_transition", "message": "no"}})
    with pytest.raises(CodaiError) as e:
        client.visual_qa.resolve("UI-1", "todo")
    assert e.value.status == 409
