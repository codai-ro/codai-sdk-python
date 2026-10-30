"""``client.brand_kits`` against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_ID = "3c9a1e2f-5b7d-4f60-8a1b-2c3d4e5f6a7b"
_BASE = "/v1/studio/brand-kits"
_KIT = {
    "id": _ID,
    "object": "studio.brand_kit",
    "name": "Acme",
    "source_url": "https://acme.example/",
    "tokens": {
        "primary": "#1a73e8",
        "secondary": "#0b8043",
        "accent": "#f9ab00",
        "background": "#ffffff",
        "text": "#202124",
        "headingFont": "Poppins",
        "bodyFont": "Inter",
    },
    "logo_asset_id": None,
    "logo_url": None,
    "logo_mime_type": None,
    "created_at": "2026-10-14T09:00:00Z",
}


def test_extract_list_retrieve_delete(client, stub):
    stub.reply(201, _KIT)
    stub.reply(200, {"object": "list", "data": [_KIT]})
    stub.reply(200, _KIT)
    stub.reply(200, {"id": _ID, "object": "studio.brand_kit", "deleted": True})
    b = client.brand_kits
    assert b.extract("https://acme.example/", name="Acme")["tokens"]["primary"] == "#1a73e8"
    assert len(b.list(limit=5)["data"]) == 1
    assert b.retrieve("a/b")["name"] == "Acme"
    assert b.delete(_ID)["deleted"] is True
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("POST", f"{_BASE}/extract", ""),
        ("GET", _BASE, "limit=5"),
        ("GET", f"{_BASE}/a%2Fb", ""),
        ("DELETE", f"{_BASE}/{_ID}", ""),
    ]
    assert stub.requests[0].json == {"url": "https://acme.example/", "name": "Acme"}


def test_create_creative_with_brand_kit(client, stub):
    stub.reply(201, {"id": "c1", "object": "studio.creative", "kind": "image", "head_seq": 1})
    client.creatives.create({"kind": "image", "brand_kit_id": _ID})
    assert stub.requests[0].json == {"kind": "image", "brand_kit_id": _ID}


def test_url_blocked(client, stub):
    stub.reply(400, {"error": {"message": "blocked", "type": "invalid_request_error", "code": "url_blocked"}})
    with pytest.raises(CodaiError) as e:
        client.brand_kits.extract("https://10.0.0.1/")
    assert e.value.code == "url_blocked"


_DTCG = {
    "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
    "color": {
        "$type": "color",
        "primary": {"$value": "#017080"},
        "secondary": {"$value": "#23abbc"},
        "accent": {"$value": "#e6b731"},
        "background": {"$value": "#f7f8fa"},
        "text": {"$value": "#0f1115"},
    },
    "font": {"$type": "fontFamily", "heading": {"$value": ["Manrope"]}, "body": {"$value": ["Inter"]}},
}


def test_create_with_tokens_or_dtcg(client, stub):
    stub.reply(201, _KIT)
    stub.reply(201, _KIT)
    client.brand_kits.create("Acme", tokens=_KIT["tokens"])
    client.brand_kits.create("Acme", dtcg=_DTCG, logo_asset_id=_ID, source_url="https://acme.example/")
    assert [(r.method, r.path) for r in stub.requests] == [("POST", _BASE), ("POST", _BASE)]
    assert stub.requests[0].json == {"name": "Acme", "tokens": _KIT["tokens"]}
    assert stub.requests[1].json == {
        "name": "Acme",
        "dtcg": _DTCG,
        "logo_asset_id": _ID,
        "source_url": "https://acme.example/",
    }


def test_create_requires_exactly_one_of_tokens_and_dtcg(client, stub):
    with pytest.raises(ValueError):
        client.brand_kits.create("Acme")
    with pytest.raises(ValueError):
        client.brand_kits.create("Acme", tokens=_KIT["tokens"], dtcg=_DTCG)
    assert stub.requests == []


def test_update_patches_and_clears_logo_only_when_asked(client, stub):
    stub.reply(200, {**_KIT, "logo_asset_id": None})
    stub.reply(200, _KIT)
    assert client.brand_kits.update(_ID, tokens={"primary": "#0b5cff"}, logo_asset_id=None)["logo_asset_id"] is None
    client.brand_kits.update(_ID, name="Acme 2")
    assert [(r.method, r.path) for r in stub.requests] == [("PATCH", f"{_BASE}/{_ID}"), ("PATCH", f"{_BASE}/{_ID}")]
    assert stub.requests[0].json == {"tokens": {"primary": "#0b5cff"}, "logo_asset_id": None}
    assert stub.requests[1].json == {"name": "Acme 2"}


def test_update_rejects_empty_or_tokens_with_dtcg(client, stub):
    with pytest.raises(ValueError):
        client.brand_kits.update(_ID)
    with pytest.raises(ValueError):
        client.brand_kits.update(_ID, tokens={"primary": "#000000"}, dtcg=_DTCG)
    assert stub.requests == []


def test_export_dtcg_returns_the_document(client, stub):
    exported = {**_DTCG, "$extensions": {"ro.codai": {"kit_id": _ID, "name": "Acme", "logo_asset_id": None}}}
    stub.reply(200, exported)
    assert client.brand_kits.export_dtcg(_ID) == exported
    assert (stub.requests[0].method, stub.requests[0].path) == ("GET", f"{_BASE}/{_ID}/dtcg")


def test_extract_from_logo_asset(client, stub):
    stub.reply(201, {**_KIT, "source_url": None, "logo_asset_id": _ID})
    assert client.brand_kits.extract(logo_asset_id=_ID, name="Acme")["logo_asset_id"] == _ID
    assert stub.requests[0].path == f"{_BASE}/extract"
    assert stub.requests[0].json == {"logo_asset_id": _ID, "name": "Acme"}


def test_extract_requires_exactly_one_source(client, stub):
    with pytest.raises(ValueError):
        client.brand_kits.extract()
    with pytest.raises(ValueError):
        client.brand_kits.extract("https://acme.example/", logo_asset_id=_ID)
    assert stub.requests == []


def test_invalid_tokens_raises_codai_error(client, stub):
    stub.reply(
        400,
        {
            "error": {
                "message": "invalid tokens",
                "type": "invalid_request_error",
                "code": "invalid_tokens",
                "details": {"issues": ["color.text missing"]},
            }
        },
    )
    with pytest.raises(CodaiError) as e:
        client.brand_kits.create("Bad", dtcg={"color": {}})
    assert e.value.code == "invalid_tokens"


def test_creatives_restyle_sends_only_given_fields(client, stub):
    cid = "7a1b2c3d-0000-4000-8000-000000000031"
    result = {"seq": 5, "doc_hash": "h", "changed": ["doc"], "warnings": [], "rebased": False}
    stub.reply(200, result)
    stub.reply(200, result)
    assert client.creatives.restyle(cid, brand_kit_id=_ID, snap=True, fonts=False) == result
    client.creatives.restyle(cid, tokens={"primary": "#0b5cff", "radius": 8}, base_seq=4, force=True)
    assert [(r.method, r.path) for r in stub.requests] == [
        ("POST", f"/v1/studio/creatives/{cid}/restyle"),
        ("POST", f"/v1/studio/creatives/{cid}/restyle"),
    ]
    assert stub.requests[0].json == {"brand_kit_id": _ID, "snap": True, "fonts": False}
    assert stub.requests[1].json == {"tokens": {"primary": "#0b5cff", "radius": 8}, "base_seq": 4, "force": True}


def test_creatives_restyle_requires_exactly_one_of_kit_and_tokens(client, stub):
    with pytest.raises(ValueError):
        client.creatives.restyle("c1")
    with pytest.raises(ValueError):
        client.creatives.restyle("c1", brand_kit_id=_ID, tokens={"primary": "#000000"})
    assert stub.requests == []
