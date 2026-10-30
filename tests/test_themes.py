"""``client.themes`` against the http.server stub: GET /v1/themes, If-None-Match and the 304 shortcut."""

from __future__ import annotations

import pytest

from codai import CodaiError

THEME = {
    "id": "catalog.dracula",
    "name": "Dracula",
    "base": "dark",
    "accentHue": 300,
    "colors": {"bg": "#282a36", "foreground": "#f8f8f2"},
    "author": "Zeno Rocha",
    "license": {"spdx": "MIT", "copyright": "Copyright (c) Dracula Theme", "url": "https://example.com/LICENSE"},
    "source": {"repo": "dracula/visual-studio-code", "commit": "abc", "path": "theme.json", "url": "https://example.com"},
}
CATALOG = {"version": "2026.10.30-1", "etag": '"abc123"', "themes": [THEME]}


def test_themes_list_returns_catalog_without_if_none_match(client, stub):
    stub.reply(200, CATALOG, {"ETag": '"abc123"'})
    assert client.themes.list() == CATALOG
    assert stub.last.method == "GET" and stub.last.path == "/v1/themes"
    assert "if-none-match" not in stub.last.headers


def test_themes_list_with_etag_maps_304_to_not_modified(client, stub):
    stub.reply(304, None)
    assert client.themes.list(etag='"abc123"') == {"notModified": True}
    assert stub.last.headers["if-none-match"] == '"abc123"'


def test_themes_list_with_stale_etag_returns_fresh_catalog_and_keeps_ext_headers(client, stub):
    stub.reply(200, CATALOG)
    out = client.themes.list(etag='"old"', ext={"headers": {"x-extra": "1"}})
    assert out == CATALOG
    assert stub.last.headers["if-none-match"] == '"old"'
    assert stub.last.headers["x-extra"] == "1"


def test_themes_list_raises_on_error(client, stub):
    stub.reply(500, {"error": {"code": "internal_error", "message": "boom"}})
    with pytest.raises(CodaiError) as exc:
        client.themes.list()
    assert exc.value.status == 500


def test_catalog_types_are_generated():
    from codai._types import CatalogTheme, ThemesCatalog

    assert set(ThemesCatalog.__annotations__) == {"version", "etag", "themes"}
    assert {"id", "name", "base", "license", "source"} <= set(CatalogTheme.__annotations__)
