"""client.cards against the http.server stub: query/body shapes, PNG bytes and error surfacing."""

from __future__ import annotations

from urllib.parse import parse_qs

import pytest

from codai import CardsRendered, CardsStaticMap, CodaiError

_WEATHER = {
    "block": {"type": "weather", "location": {"name": "București", "lat": 44.43, "lng": 26.1}},
    "provenance": {"source": "met_norway", "cached": True},
}


def test_weather_query_and_envelope(client, stub):
    stub.reply(200, _WEATHER)
    r = client.cards.weather(44.43, 26.1, name="București")
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/cards/weather")
    assert parse_qs(stub.last.query) == {"lat": ["44.43"], "lng": ["26.1"], "name": ["București"]}
    assert r["block"] == _WEATHER["block"] and r["provenance"]["source"] == "met_norway"


def test_places_drops_none_and_joins_types(client, stub):
    stub.reply(200, {"block": {"type": "places", "items": []}, "provenance": {"costMicroUsd": 32000}})
    r = client.cards.places(lat=44.4, lng=26.1, type=["restaurant", "cafe"], limit=5, open_now=True)
    assert stub.last.path == "/v1/cards/places"
    assert parse_qs(stub.last.query) == {
        "lat": ["44.4"],
        "lng": ["26.1"],
        "type": ["restaurant,cafe"],
        "limit": ["5"],
        "open_now": ["1"],
    }
    assert r["provenance"]["costMicroUsd"] == 32000


def test_geocode_returns_results(client, stub):
    stub.reply(200, {"block": {"type": "map"}, "results": [{"lat": 44.43, "lng": 26.1}], "provenance": {}})
    r = client.cards.geocode("Piața Victoriei", region="RO")
    assert stub.last.path == "/v1/cards/geocode"
    assert parse_qs(stub.last.query) == {"address": ["Piața Victoriei"], "region": ["RO"]}
    assert len(r["results"]) == 1


def test_static_map_returns_png_bytes(client, stub):
    png = b"\x89PNG\r\n\x1a\n"
    stub.reply(200, png, {"Content-Type": "image/png", "x-codai-attribution": "Google Maps"})
    m = client.cards.static_map(center="44.43,26.10", zoom=14, markers="44.43,26.10,A")
    assert stub.last.path == "/v1/cards/static-map"
    assert parse_qs(stub.last.query) == {"center": ["44.43,26.10"], "zoom": ["14"], "markers": ["44.43,26.10,A"]}
    assert isinstance(m, CardsStaticMap)
    assert m.data == png and m.content_type == "image/png" and m.attribution == "Google Maps"


def test_fx_maps_from_and_symbols(client, stub):
    stub.reply(200, {"block": {"type": "table"}, "provenance": {"source": "bnr"}})
    stub.reply(200, {"block": {"type": "metric"}, "provenance": {"source": "ecb"}})
    client.cards.fx(symbols=["EUR", "USD"])
    assert parse_qs(stub.last.query) == {"symbols": ["EUR,USD"]}
    client.cards.fx(source="ecb", from_="EUR", to="USD", amount=100)
    assert parse_qs(stub.last.query) == {"source": ["ecb"], "from": ["EUR"], "to": ["USD"], "amount": ["100"]}


def test_route_track_efactura_queries(client, stub):
    stub.reply(200, {"block": {"type": "map"}, "route": {"durationS": 900}, "provenance": {"source": "google_routes"}})
    stub.reply(200, {"block": None, "result": {"carrier": "fan", "configured": False}, "provenance": {}})
    stub.reply(200, {"block": None, "documents": [], "provenance": {"source": "brivio"}})
    r = client.cards.route(from_="Piața Romană", to="Otopeni", mode="walk")
    assert stub.last.path == "/v1/cards/route"
    assert parse_qs(stub.last.query) == {"from": ["Piața Romană"], "to": ["Otopeni"], "mode": ["walk"]}
    assert r["route"]["durationS"] == 900
    t = client.cards.track("2123456789012", carrier="fan")
    assert (stub.last.path, parse_qs(stub.last.query)) == (
        "/v1/cards/track",
        {"awb": ["2123456789012"], "carrier": ["fan"]},
    )
    assert t["result"]["configured"] is False
    e = client.cards.efactura(limit=5)
    assert (stub.last.path, parse_qs(stub.last.query)) == ("/v1/cards/efactura", {"limit": ["5"]})
    assert e["documents"] == []


def test_unfurl_posts_url_and_raises_on_block(client, stub):
    stub.reply(200, {"block": {"type": "links", "variant": "preview", "items": []}, "provenance": {"source": "page"}})
    r = client.cards.unfurl("https://codai.ro")
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/cards/unfurl")
    assert stub.last.json == {"url": "https://codai.ro"}
    assert r["block"]["type"] == "links"
    stub.reply(400, {"error": {"message": "blocked", "type": "invalid_request_error", "code": "unfurl_blocked"}})
    with pytest.raises(CodaiError) as e:
        client.cards.unfurl("http://169.254.169.254")
    assert e.value.status == 400 and e.value.code == "unfurl_blocked"


def test_product_posts_url_lang_and_raises_on_not_found(client, stub):
    stub.reply(200, {"block": {"type": "products", "items": []}, "provenance": {"source": "page"}})
    r = client.cards.product("https://shop.ro/cafea", lang="ro")
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/cards/product")
    assert stub.last.json == {"url": "https://shop.ro/cafea", "lang": "ro"}
    assert r["block"]["type"] == "products"
    stub.reply(422, {"error": {"message": "none", "type": "invalid_request_error", "code": "product_not_found"}})
    with pytest.raises(CodaiError) as e:
        client.cards.product("https://codai.ro")
    assert stub.last.json == {"url": "https://codai.ro"}
    assert e.value.status == 422 and e.value.code == "product_not_found"


def test_maps_not_configured_is_a_503(client, stub):
    stub.reply(503, {"error": {"message": "maps off", "type": "api_error", "code": "maps_not_configured"}})
    with pytest.raises(CodaiError) as e:
        client.cards.places(q="cafea")
    assert e.value.status == 503 and e.value.code == "maps_not_configured"


def test_render_posts_block_and_returns_image(client, stub):
    png = b"\x89PNG\r\n\x1a\n"
    stub.reply(200, png, {"Content-Type": "image/png", "x-codai-render-size": "960x600"})
    block = {"type": "qr", "data": "https://codai.ro"}
    r = client.cards.render(block, width=480, theme="dark")
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/cards/render")
    assert stub.last.json == {"block": block, "width": 480, "theme": "dark"}
    assert isinstance(r, CardsRendered)
    assert r.data == png and r.content_type == "image/png" and (r.width, r.height) == (960, 600)
    stub.reply(422, {"error": {"message": "no", "type": "invalid_request_error", "code": "render_unsupported"}})
    with pytest.raises(CodaiError) as e:
        client.cards.render({"type": "math", "tex": "x"})
    assert e.value.status == 422 and e.value.code == "render_unsupported"
