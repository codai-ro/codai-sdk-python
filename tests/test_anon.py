"""``client.anon`` (guest chat, no account) against the stub."""

from __future__ import annotations

import hashlib

from codai import Codai, solve_pow

DEVICE = "0b9d6c3e-6f1a-4c1e-9a43-2f5b7d8e9a10"
LIMITS = {
    "sessions_per_day": 3,
    "sessions_left": 2,
    "messages_per_session": 10,
    "messages_left": 10,
    "soft_wall_at": 8,
    "resets_at": "2026-10-29T00:00:00Z",
}


def _zero_bits(hex_digest: str) -> int:
    value = int(hex_digest, 16)
    return 256 - value.bit_length()


def _digest(nonce: str, counter: str) -> str:
    return hashlib.sha256(f"{nonce}:{DEVICE}:{counter}".encode()).hexdigest()


def test_solve_pow_bits_8_returns_smallest_valid_counter():
    counter = solve_pow("nonce-abc", DEVICE, 8)
    assert counter.isdigit()
    assert _zero_bits(_digest("nonce-abc", counter)) >= 8
    assert all(_zero_bits(_digest("nonce-abc", str(i))) < 8 for i in range(int(counter)))


def test_challenge_sends_surface(client, stub):
    stub.reply(200, {"nonce": "n", "pow_bits": 20, "expires_at": "2026-10-28T10:05:00Z"})
    r = client.anon.challenge("desktop")
    assert r["pow_bits"] == 20
    assert stub.last.method == "GET" and stub.last.path == "/v1/anon/challenge"
    assert stub.last.query == "surface=desktop"


def test_create_session_posts_body(client, stub):
    stub.reply(200, {"token": "anon_v1.a.b", "session_id": "s", "expires_at": "x", "limits": LIMITS})
    body = {"surface": "web", "device_id": DEVICE, "nonce": "n", "accept_terms": True,
            "confirm_adult": True, "proof": {"turnstile": "tok"}}
    r = client.anon.create_session(body)
    assert r["token"] == "anon_v1.a.b"
    assert stub.last.method == "POST" and stub.last.path == "/v1/anon/session"
    assert stub.last.json == body


def test_status_uses_the_guest_token_as_bearer(stub):
    guest = Codai(api_key="anon_v1.p.s", base_url=stub.url, max_retries=0, timeout=5)
    stub.reply(200, {"budget_open": True, "limits": LIMITS})
    assert guest.anon.status()["budget_open"] is True
    assert stub.last.method == "GET" and stub.last.path == "/v1/anon/status"
    assert stub.last.headers["authorization"] == "Bearer anon_v1.p.s"


def test_import_chat_omits_absent_title_and_sends_title_when_given(client, stub):
    msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    stub.reply(200, {"session_id": "sess-1"})
    assert client.anon.import_chat("anon_v1.p.s", msgs) == {"session_id": "sess-1"}
    assert stub.last.method == "POST" and stub.last.path == "/v1/anon/import"
    assert stub.last.json == {"anon_token": "anon_v1.p.s", "messages": msgs}

    stub.reply(200, {"session_id": "sess-2"})
    client.anon.import_chat("anon_v1.q.s", msgs, title="Trip")
    assert stub.last.json == {"anon_token": "anon_v1.q.s", "messages": msgs, "title": "Trip"}


def test_start_guest_session_chains_challenge_pow_session(client, stub):
    stub.reply(200, {"nonce": "nonce-xyz", "pow_bits": 8, "expires_at": "x"})
    stub.reply(200, {"token": "anon_v1.t.s", "session_id": "s", "expires_at": "x", "limits": LIMITS})
    r = client.anon.start_guest_session("vscode", DEVICE)
    assert r["token"] == "anon_v1.t.s"
    assert [q.path for q in stub.requests] == ["/v1/anon/challenge", "/v1/anon/session"]
    sent = stub.requests[1].json
    assert sent["surface"] == "vscode" and sent["device_id"] == DEVICE and sent["nonce"] == "nonce-xyz"
    assert sent["accept_terms"] is True and sent["confirm_adult"] is True
    assert _zero_bits(_digest("nonce-xyz", sent["proof"]["pow"]["counter"])) >= 8
