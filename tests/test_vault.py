"""``client.vault`` against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError, vault_unlock_message

ITEM = "0b7d1a2e-1111-4222-8333-444455556666"
DEVICE = {
    "id": "android-pixel.9a",
    "kind": "android_keystore",
    "name": "Pixel",
    "surface": "phone",
    "public_key": "spki",
    "attestation": "android-strongbox",
    "attestation_info": {},
    "created_at": "2026-10-19T00:00:00Z",
    "last_used_at": None,
    "revoked_at": None,
}


def test_vault_account_items_and_rules_routes(client, stub):
    stub.reply(200, {"fingerprint": "f", "default_tier": "t3", "revision": 2, "bundle": {}})
    assert client.vault.account()["revision"] == 2
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/vault/account")

    stub.reply(200, {"ok": True})
    client.vault.put_account({"slots": []}, revision=2)
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "PUT",
        "/v1/vault/account",
        {"bundle": {"slots": []}, "revision": 2},
    )

    stub.reply(200, {"ok": True})
    client.vault.set_default_tier("t2")
    assert (stub.last.method, stub.last.path, stub.last.json) == ("PATCH", "/v1/vault/settings", {"default_tier": "t2"})

    stub.reply(200, {"items": []})
    client.vault.items(since="2026-10-18T00:00:00Z")
    assert (stub.last.path, stub.last.query) == ("/v1/vault/items", "since=2026-10-18T00%3A00%3A00Z")

    env = {"id": ITEM, "vault_id": ITEM, "revision": 1, "wrapped_key": "w", "ciphertext": "c", "kind": "login"}
    stub.reply(200, {"ok": True})
    client.vault.put_item(ITEM, env)
    assert (stub.last.method, stub.last.path, stub.last.json) == ("PUT", f"/v1/vault/items/{ITEM}", env)

    stub.reply(200, {"ok": True})
    client.vault.set_item_cloud(ITEM, None)
    assert (stub.last.method, stub.last.path, stub.last.json) == ("PUT", f"/v1/vault/items/{ITEM}/cloud", {"item": None})

    stub.reply(200, {"ok": True})
    client.vault.delete_item(ITEM)
    assert (stub.last.method, stub.last.path) == ("DELETE", f"/v1/vault/items/{ITEM}")

    stub.reply(201, {"rule": {"id": "r1"}})
    client.vault.create_rule("t1", agent="codaid*")
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/vault/rules", {"tier": "t1", "agent": "codaid*"})

    stub.reply(200, {"events": []})
    client.vault.events(limit=5)
    assert (stub.last.path, stub.last.query) == ("/v1/vault/events", "limit=5")


def test_vault_broker_calls_and_approval_flow(client, stub):
    stub.reply(200, {"tier": "t3", "allowed": False, "reasons": ["needs approval"], "approval_id": "a 1"})
    d = client.vault.use("github", "http", "push", host="api.github.com")
    assert d["approval_id"] == "a 1"
    assert stub.last.json == {"handle": "github", "mode": "http", "action": "push", "host": "api.github.com"}

    stub.reply(200, {"status": "pending"})
    client.vault.approval("a 1")
    assert stub.last.path == "/v1/vault/approvals/a%201"

    stub.reply(200, {"status": "approved"})
    client.vault.decide("a 1", "approve", "once", "sig")
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "POST",
        "/v1/vault/approvals/a%201/decide",
        {"decision": "approve", "scope": "once", "signature": "sig"},
    )

    # 202 = approval required: returned as the body, not raised.
    stub.reply(202, {"approval_id": "a2"})
    r = client.vault.http_call({"handle": "github", "url": "https://api.github.com/user", "body": None})
    assert r == {"approval_id": "a2"}
    assert (stub.last.path, stub.last.json) == ("/v1/vault/http", {"handle": "github", "url": "https://api.github.com/user"})

    stub.reply(202, {"approvals": ["a3"]})
    assert client.vault.resolve({"handles": ["db"], "action": "run"}) == {"approvals": ["a3"]}
    assert stub.last.path == "/v1/vault/resolve"


def test_vault_devices_enrol_list_rename_revoke(client, stub):
    stub.reply(200, {"nonce": "n0", "expires_at": "2026-10-19T00:05:00Z"})
    assert client.vault.devices.challenge()["nonce"] == "n0"
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/vault/devices/challenge", {})

    stub.reply(201, {"device": DEVICE})
    d = client.vault.devices.enroll(
        DEVICE["id"],
        "android_keystore",
        "Pixel",
        "phone",
        "spki",
        "n0",
        "vs",
        "ds",
        attestation={"android_chain": ["leaf", "root"]},
    )
    assert d["attestation"] == "android-strongbox"
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "POST",
        "/v1/vault/devices",
        {
            "device_id": DEVICE["id"],
            "kind": "android_keystore",
            "name": "Pixel",
            "surface": "phone",
            "public_key": "spki",
            "nonce": "n0",
            "vault_signature": "vs",
            "device_signature": "ds",
            "attestation": {"android_chain": ["leaf", "root"]},
        },
    )

    stub.reply(200, {"devices": [DEVICE]})
    assert [x["id"] for x in client.vault.devices.list()] == [DEVICE["id"]]
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/vault/devices")

    stub.reply(200, {"device": {**DEVICE, "name": "Phone"}})
    assert client.vault.devices.rename(DEVICE["id"], "Phone")["name"] == "Phone"
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "PATCH",
        f"/v1/vault/devices/{DEVICE['id']}",
        {"name": "Phone"},
    )

    stub.reply(200, {"ok": True})
    assert client.vault.devices.revoke(DEVICE["id"]) == {"ok": True}
    assert (stub.last.method, stub.last.path) == ("DELETE", f"/v1/vault/devices/{DEVICE['id']}")


def test_vault_decide_with_v2_proofs_and_bare_deny(client, stub):
    proof = {"type": "device", "device_id": DEVICE["id"], "signature": "sig"}
    stub.reply(200, {"status": "approved"})
    client.vault.decide("a1", "approve", "once", via="phone", proof=proof)
    assert stub.last.json == {"decision": "approve", "scope": "once", "via": "phone", "proof": proof}

    passkey = {"type": "passkey", "response": {"id": "cred", "type": "public-key"}}
    stub.reply(200, {"status": "approved"})
    client.vault.decide("a1", "approve", "1h", proof=passkey)
    assert stub.last.json == {"decision": "approve", "scope": "1h", "proof": passkey}

    stub.reply(200, {"status": "denied"})
    client.vault.decide("a1", "deny", "once", via="phone")
    assert stub.last.json == {"decision": "deny", "scope": "once", "via": "phone"}

    with pytest.raises(ValueError):
        client.vault.decide("a1", "approve", "once", "sig", proof=proof)


def test_vault_guards_settings_lock_unlock(client, stub):
    guards = {"new_host": True, "burst_max": 5, "burst_window_s": 60, "hour_start": None, "hour_end": None, "tz": "UTC"}
    stub.reply(200, {"default_tier": "t3", "guards": guards})
    r = client.vault.update_settings(guards={"hour_start": None, "hour_end": None})
    assert r["guards"]["hour_start"] is None
    # explicit None survives: it means "hours off"
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "PATCH",
        "/v1/vault/settings",
        {"guards": {"hour_start": None, "hour_end": None}},
    )
    with pytest.raises(ValueError):
        client.vault.update_settings()

    stub.reply(200, {"locked_at": "2026-10-20T10:00:00Z", "grants_revoked": 2, "approvals_denied": 1})
    assert client.vault.lock(via="phone")["grants_revoked"] == 2
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/vault/lock", {"via": "phone"})

    stub.reply(200, {"locked_at": "2026-10-20T10:00:00Z", "grants_revoked": 0, "approvals_denied": 0})
    client.vault.lock()
    assert stub.last.json == {}

    stub.reply(200, {"challenge": "c0", "expires_at": "2026-10-20T10:05:00Z", "message_template": "t"})
    ch = client.vault.unlock_challenge()
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/vault/unlock/challenge", {})
    assert vault_unlock_message(ch["challenge"], DEVICE["id"]) == f"codai-vault/unlock/v1|c0|{DEVICE['id']}"
    assert vault_unlock_message("c0", "passkey") == "codai-vault/unlock/v1|c0|passkey"

    proof = {"type": "device", "device_id": DEVICE["id"], "signature": "sig"}
    stub.reply(200, {"unlocked": True})
    assert client.vault.unlock("c0", proof, via="phone") == {"unlocked": True}
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "POST",
        "/v1/vault/unlock",
        {"challenge": "c0", "proof": proof, "via": "phone"},
    )


def test_vault_limits_and_task_grants(client, stub):
    lim = {"item_id": ITEM, "per_minute": 5, "per_day": None, "units_per_day": 200}
    stub.reply(200, {"limits": [lim]})
    assert client.vault.limits() == [lim]
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/vault/limits")

    stub.reply(200, {"limits": lim})
    assert client.vault.set_limits(ITEM, 5, None, 200) == lim
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "PUT",
        f"/v1/vault/items/{ITEM}/limits",
        {"per_minute": 5, "per_day": None, "units_per_day": 200},
    )

    stub.reply(200, {"limits": None})
    assert client.vault.set_limits(ITEM, None, None, None) is None
    assert stub.last.json == {"per_minute": None, "per_day": None, "units_per_day": None}

    stub.reply(200, {"revoked": 3})
    assert client.vault.revoke_task_grants("task-1") == {"revoked": 3}
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "POST",
        "/v1/vault/grants/revoke-task",
        {"task": "task-1"},
    )


def test_vault_rate_limited_raises_with_retry_after(client, stub):
    err = {"error": {"message": "cap", "type": "rate_limit_error", "code": "vault_rate_limited"}}
    stub.reply(429, err, {"Retry-After": "60"})
    with pytest.raises(CodaiError) as ei:
        client.vault.use("github", "http", "push")
    assert ei.value.status == 429
    assert ei.value.code == "vault_rate_limited"
    assert ei.value.retry_after == 60
    assert len(stub.requests) == 1  # mutations are not retried
