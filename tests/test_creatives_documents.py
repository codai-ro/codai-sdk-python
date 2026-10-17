"""``creatives.from_document`` + ``creatives.build`` against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_DOC = "5a7b2c3d-0000-4000-8000-000000000020"
_CID = "7a1b2c3d-0000-4000-8000-000000000041"


def _creative(existing: bool):
    return {
        "id": _CID,
        "object": "studio.creative",
        "kind": "deck",
        "title": "Rezultate T3",
        "head_seq": 1,
        "version": {"seq": 1, "doc_hash": "abc"},
        "doc": {"schemaVersion": 1, "kind": "deck", "title": "Rezultate T3", "scenes": []},
        "document_id": _DOC,
        "existing": existing,
    }


def _build(seq: int = 4):
    return {
        "object": "studio.creative_build",
        "creative_id": _CID,
        "seq": seq,
        "warnings": ["skipped node logo (shape) on s2"],
        "document": {
            "id": "5a7b2c3d-0000-4000-8000-000000000021",
            "object": "studio.document",
            "type": "deck",
            "version": 2,
            "based_on": _DOC,
            "creative_id": _CID,
            "cost_micro_usd": "0",
        },
    }


def test_from_document_posts_without_body(client, stub):
    stub.reply(201, _creative(False))
    stub.reply(200, _creative(True))
    first = client.creatives.from_document(_DOC)
    again = client.creatives.from_document("a/b")
    assert first["existing"] is False and first["document_id"] == _DOC
    assert again["existing"] is True
    assert [(r.method, r.path, r.query, r.body) for r in stub.requests] == [
        ("POST", f"/v1/studio/documents/{_DOC}/creative", "", b""),
        ("POST", "/v1/studio/documents/a%2Fb/creative", "", b""),
    ]


def test_build_sends_only_given_fields(client, stub):
    stub.reply(200, _build())
    stub.reply(200, _build(1))
    b = client.creatives.build(_CID, seq=4, preview=True, filename="raport.pptx")
    assert b["document"]["version"] == 2
    assert b["warnings"] == ["skipped node logo (shape) on s2"]
    client.creatives.build(_CID)
    assert [(r.method, r.path) for r in stub.requests] == [
        ("POST", f"/v1/studio/creatives/{_CID}/build"),
        ("POST", f"/v1/studio/creatives/{_CID}/build"),
    ]
    assert stub.requests[0].json == {"seq": 4, "preview": True, "filename": "raport.pptx"}
    assert stub.requests[1].json == {}


def test_errors_surface_codes(client, stub):
    stub.reply(409, {"error": {"message": "no spec", "type": "invalid_request_error", "code": "document_spec_missing"}})
    stub.reply(
        400,
        {"error": {"message": "video", "type": "invalid_request_error", "code": "not_supported_for_kind"}},
    )
    with pytest.raises(CodaiError) as e:
        client.creatives.from_document(_DOC)
    assert e.value.status == 409
    with pytest.raises(CodaiError) as e2:
        client.creatives.build(_CID)
    assert e2.value.code == "not_supported_for_kind"
