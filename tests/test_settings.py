"""``client.settings`` against the http.server stub: GET / PATCH routes, the optional version and the 409 state."""

from __future__ import annotations

import pytest

from codai import CodaiError, settings_conflict_current

VIEW = {
    "settings": {
        "transcripts": {"waveform": "bars", "haptics": True, "liveText": True, "target": "auto", "language": None}
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
