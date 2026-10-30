"""``client.settings`` against the http.server stub: GET / PATCH routes, the optional version and the 409 state."""

from __future__ import annotations

import pytest

from codai import CodaiError, settings_conflict_current

VIEW = {
    "settings": {
        "transcripts": {"waveform": "bars", "haptics": True, "liveText": True, "target": "auto", "language": None},
        "appearance": {
            "colorTheme": "builtin.midnight",
            "lightTheme": "builtin.light",
            "darkTheme": "builtin.dark",
            "mode": "dark",
            "accent": "teal",
            "skin": "focus",
            "amoled": True,
            "font": "brand",
        },
    },
    "version": 2,
    "updatedAt": "2026-10-10T12:00:00.000Z",
}


def test_settings_get_and_update(client, stub):
    stub.reply(200, VIEW)
    assert client.settings.get() == VIEW
    assert stub.last.method == "GET" and stub.last.path == "/v1/settings"

    stub.reply(200, VIEW)
    client.settings.update({"transcripts": {"waveform": "bars"}}, version=1)
    assert stub.last.method == "PATCH" and stub.last.path == "/v1/settings"
    assert stub.last.json == {"settings": {"transcripts": {"waveform": "bars"}}, "version": 1}

    stub.reply(200, VIEW)
    client.settings.update({"transcripts": {"language": None}})
    assert stub.last.json == {"settings": {"transcripts": {"language": None}}}


def test_settings_update_appearance(client, stub):
    stub.reply(200, VIEW)
    out = client.settings.update({"appearance": {"accent": "teal", "amoled": True}})
    assert stub.last.json == {"settings": {"appearance": {"accent": "teal", "amoled": True}}}
    assert out["settings"]["appearance"]["skin"] == "focus"


def test_appearance_settings_type_is_generated():
    from codai._types import AppearanceSettings, UserSettings

    assert set(AppearanceSettings.__annotations__) == {
        "colorTheme", "lightTheme", "darkTheme", "mode", "accent", "skin", "amoled", "font",
    }
    assert "appearance" in UserSettings.__annotations__


def test_settings_version_conflict_carries_current(client, stub):
    stub.reply(
        409,
        {
            "error": {"message": "stale", "type": "invalid_request_error", "code": "version_conflict"},
            "current": VIEW,
        },
    )
    with pytest.raises(CodaiError) as info:
        client.settings.update({"transcripts": {"haptics": False}}, version=1)
    assert info.value.status == 409 and info.value.code == "version_conflict"
    assert settings_conflict_current(info.value) == VIEW
    assert settings_conflict_current(ValueError("x")) is None
