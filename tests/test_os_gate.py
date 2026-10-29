"""``client.os_gate`` against the http.server stub: GET /v1/policy, POST /v1/os-gate/events and the 503 path."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from codai import CodaiError


def test_os_gate_policy(client, stub):
    stub.reply(200, {"os_gate": {"allow_override": False}})
    assert client.os_gate.policy() == {"os_gate": {"allow_override": False}}
    assert stub.last.method == "GET" and stub.last.path == "/v1/policy"


def test_os_gate_policy_unavailable_raises(client, stub):
    stub.reply(503, {"error": {"message": "down", "type": "server_error", "code": "policy_unavailable"}})
    with pytest.raises(CodaiError) as info:
        client.os_gate.policy()
    assert info.value.status == 503 and info.value.code == "policy_unavailable"


def test_os_gate_record_event(client, stub):
    stub.reply(202, {"ok": True})
    r = client.os_gate.record_event(
        "granted",
        ["win.uac_off"],
        "desktop",
        "0.9.4",
        "2026-10-19T21:00:00Z",
    )
    assert r == {"ok": True}
    assert stub.last.method == "POST" and stub.last.path == "/v1/os-gate/events"
    assert stub.last.json == {
        "action": "granted",
        "checks": ["win.uac_off"],
        "surface": "desktop",
        "app_version": "0.9.4",
        "at": "2026-10-19T21:00:00Z",
    }

    stub.reply(202, {"ok": True})
    when = datetime(2026, 10, 19, 21, 0, tzinfo=timezone.utc)
    client.os_gate.record_event("revoked", ["mac.sip_off", "mac.gatekeeper_off"], "codaid", "1.2.0", when)
    assert stub.last.json["at"] == when.isoformat()
    assert stub.last.json["checks"] == ["mac.sip_off", "mac.gatekeeper_off"]
