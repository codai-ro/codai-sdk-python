"""``client.resolve`` against the stub, plus parity with resolve.yaml operationIds."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from pathlib import Path

import pytest
import yaml

from codai import (
    RESOLVE_OPERATION_METHODS,
    Codai,
    ResolveError,
    ResolveInsufficientFundsError,
    attestation_statement,
    verify_attestation_with_keys,
    verify_resolve_webhook,
)

SPEC = Path(__file__).resolve().parents[3] / "apps" / "docs" / "openapi" / "en" / "resolve.yaml"
JOB = "11111111-2222-4333-8444-555555555555"


@pytest.fixture
def rclient(stub) -> Codai:
    return Codai(api_key="codai_test", resolve_base_url=stub.url, max_retries=0, timeout=5)


def test_every_resolve_operation_is_mapped_and_callable(rclient):
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    ids = {op["operationId"] for item in spec["paths"].values() for op in item.values() if isinstance(op, dict) and "operationId" in op}
    assert set(RESOLVE_OPERATION_METHODS) == ids
    for dotted in RESOLVE_OPERATION_METHODS.values():
        node = rclient
        for part in dotted.split("."):
            node = getattr(node, part)
        assert callable(node)


def test_submit_posts_intake_with_bearer(rclient, stub):
    stub.reply(201, {"id": JOB, "status": "quoted", "tier": "t7"})
    r = rclient.resolve.submit({"repo_url": "https://github.com/o/r", "issue_url": "https://github.com/o/r/issues/1"})
    assert r["status"] == "quoted"
    assert stub.last.method == "POST" and stub.last.path == "/v1/resolve/jobs"
    assert stub.last.headers["authorization"] == "Bearer codai_test"
    assert stub.last.json["repo_url"] == "https://github.com/o/r"


def test_submit_requires_issue(rclient):
    with pytest.raises(TypeError):
        rclient.resolve.submit({"repo_url": "https://github.com/o/r"})


def test_accept_sends_empty_body(rclient, stub):
    stub.reply(202, {"id": JOB, "status": "accepted"})
    r = rclient.resolve.accept(JOB)
    assert r["status"] == "accepted"
    assert stub.last.method == "POST"
    assert stub.last.path == f"/v1/resolve/jobs/{JOB}/accept"
    assert stub.last.body == b""


def test_accept_402_maps_to_insufficient_funds(rclient, stub):
    body = {
        "error": "insufficient_funds",
        "balance": 0,
        "required": 7_000_000,
        "currency": "micro_eur",
        "topup_url": "https://pay.codai.ro/checkout?topup=10",
    }
    stub.reply(402, body)
    with pytest.raises(ResolveInsufficientFundsError) as ei:
        rclient.resolve.accept(JOB)
    assert ei.value.status == 402
    assert ei.value.required == 7_000_000
    assert ei.value.topup_url.endswith("topup=10")
    assert ei.value.bundle_url is None


def test_accept_402_on_t7_carries_bundle_url(rclient, stub):
    body = {
        "error": "insufficient_funds",
        "balance": 0,
        "required": 7_000_000,
        "currency": "micro_eur",
        "topup_url": "https://pay.codai.ro/checkout?topup=10",
        "bundle_url": "https://pay.codai.ro/checkout?bundle=resolve10",
    }
    stub.reply(402, body)
    with pytest.raises(ResolveInsufficientFundsError) as ei:
        rclient.resolve.accept(JOB)
    assert ei.value.bundle_url == "https://pay.codai.ro/checkout?bundle=resolve10"
    assert "bundle=resolve10" in str(ei.value)


def test_accept_reports_paid_with_and_balance_route(rclient, stub):
    stub.reply(200, {"id": JOB, "status": "accepted", "paid_with": "credit", "held_micro_eur": 0})
    r = rclient.resolve.accept(JOB)
    assert r["paid_with"] == "credit" and r["held_micro_eur"] == 0
    stub.reply(200, {"fix_credits": 9, "intro_available": False, "wallet_micro_eur": 2_000_000})
    assert rclient.resolve.balance() == {"fix_credits": 9, "intro_available": False, "wallet_micro_eur": 2_000_000}
    assert stub.last.method == "GET" and stub.last.path == "/v1/resolve/balance"


def test_409_maps_to_resolve_error(rclient, stub):
    stub.reply(409, {"error": "job is not quoted"})
    with pytest.raises(ResolveError) as ei:
        rclient.resolve.accept(JOB)
    assert ei.value.status == 409 and ei.value.detail == "job is not quoted"
    assert not isinstance(ei.value, ResolveInsufficientFundsError)


def test_attestation_accepts_url(rclient, stub):
    stub.reply(200, {"id": "att-1"})
    rclient.resolve.attestation("https://resolve.codai.ro/v1/resolve/attestations/att-1")
    assert stub.last.path == "/v1/resolve/attestations/att-1"


def test_wait_for_polls_until_terminal(rclient, stub):
    stub.reply(200, {"id": JOB, "status": "running"})
    stub.reply(200, {"id": JOB, "status": "resolved"})
    seen = []
    job = rclient.resolve.wait_for(JOB, interval=0.01, on_poll=lambda j: seen.append(j["status"]))
    assert job["status"] == "resolved" and seen == ["running", "resolved"]


# --- webhooks -----------------------------------------------------------------

_SECRET = "whsec_test_secret"
_NOW = 1_790_000_000
_RAW = '{"event":"job.resolved","job":{"id":"' + JOB + '","status":"resolved"},"sent_at":"2026-09-27T00:00:00.000Z"}'


def _sign(t: int, body: str, secret: str = _SECRET) -> str:
    mac = hmac.new(secret.encode(), f"{t}.{body}".encode(), hashlib.sha256).hexdigest()
    return f"t={t},v1={mac}"


def test_submit_sends_callback_url_and_returns_secret(rclient, stub):
    stub.reply(201, {"id": JOB, "status": "quoted", "tier": "t7", "callback_secret": "whsec_abc"})
    r = rclient.resolve.submit({
        "repo_url": "https://github.com/o/r",
        "issue_text": "it crashes on x",
        "callback_url": "https://ci.example.com/hook",
    })
    assert r["callback_secret"] == "whsec_abc"
    assert stub.last.json["callback_url"] == "https://ci.example.com/hook"


def test_verify_resolve_webhook_accepts_service_signature_str_and_bytes():
    header = _sign(_NOW, _RAW)
    assert verify_resolve_webhook(_SECRET, _RAW, header, now=_NOW) is True
    assert verify_resolve_webhook(_SECRET, _RAW.encode(), header, now=_NOW) is True


def test_verify_resolve_webhook_rejects_tampering_and_garbage():
    header = _sign(_NOW, _RAW)
    assert verify_resolve_webhook(_SECRET, _RAW + " ", header, now=_NOW) is False
    assert verify_resolve_webhook("whsec_other", _RAW, header, now=_NOW) is False
    assert verify_resolve_webhook(_SECRET, _RAW, "v1=deadbeef", now=_NOW) is False
    assert verify_resolve_webhook(_SECRET, _RAW, f"t={_NOW},v1=zz", now=_NOW) is False
    assert verify_resolve_webhook(_SECRET, _RAW, "", now=_NOW) is False
    assert verify_resolve_webhook(_SECRET, _RAW, None, now=_NOW) is False
    assert verify_resolve_webhook("", _RAW, header, now=_NOW) is False


def test_verify_resolve_webhook_tolerance_window():
    assert verify_resolve_webhook(_SECRET, _RAW, _sign(_NOW - 300, _RAW), now=_NOW) is True
    assert verify_resolve_webhook(_SECRET, _RAW, _sign(_NOW - 301, _RAW), now=_NOW) is False
    assert verify_resolve_webhook(_SECRET, _RAW, _sign(_NOW + 301, _RAW), now=_NOW) is False
    assert verify_resolve_webhook(_SECRET, _RAW, _sign(_NOW - 3600, _RAW), tolerance_seconds=7200, now=_NOW) is True
    t = int(time.time())
    assert verify_resolve_webhook(_SECRET, _RAW, _sign(t, _RAW)) is True


# --- signed attestations (R3) ---------------------------------------------------

_PT = "application/vnd.codai.resolve.attestation+json;v=1"
_ATT = {
    "id": "1f2c1a3e-8d4b-4f8e-9a1b-0c2d3e4f5a6b",
    "kind": "codai.resolve.attestation.v0",
    "repo_url": "https://github.com/o/r",
    "base_commit": "abc123",
    "patch": "diff --git a/x b/x\n+ünïcode\n",
    "repro_test": {"path": "tests/test_x.py", "content": "def test_x(): assert 1\n"},
    "test_command": "pytest -q tests/test_x.py",
    "regression_command": None,
    "test_output_before": "1 failed",
    "test_output_after": "1 passed",
    "regression_output": None,
    "runner_image_digest": "sha256:deadbeef",
    "started_at": "2026-09-27T08:00:00.000Z",
    "verified_at": "2026-09-27T08:05:00.000Z",
}


def _h(s):
    return None if s is None else hashlib.sha256(s.encode()).hexdigest()


def _statement_bytes(a) -> bytes:
    # Independent re-implementation of apps/resolve attestationStatement + JCS.
    st = {
        "kind": "codai.resolve.attestation.v1",
        "attestation_id": a["id"],
        "repo_url": a["repo_url"],
        "base_commit": a["base_commit"],
        "patch_sha256": _h(a["patch"]),
        "repro_test": {"path": a["repro_test"]["path"], "sha256": _h(a["repro_test"]["content"])} if a["repro_test"] else None,
        "test_command": a["test_command"],
        "regression_command": a["regression_command"],
        "test_output_before_sha256": _h(a["test_output_before"]),
        "test_output_after_sha256": _h(a["test_output_after"]),
        "regression_output_sha256": _h(a["regression_output"]),
        "runner_image_digest": a["runner_image_digest"],
        "started_at": a["started_at"],
        "verified_at": a["verified_at"],
    }
    return json.dumps(st, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _envelope(body: bytes, sig: bytes = b"\x30\x00") -> dict:
    return {"payloadType": _PT, "payload": base64.b64encode(body).decode(), "signatures": [{"keyid": "k1", "sig": base64.b64encode(sig).decode()}]}


def test_unsigned_attestation_needs_no_keys_or_crypto(rclient, stub):
    assert rclient.resolve.verify_attestation({**_ATT, "signature": None}) == {"ok": False, "reason": "UNSIGNED"}
    assert stub.requests == []


def test_statement_mismatch_is_pure_stdlib():
    att = {**_ATT, "signature": _envelope(_statement_bytes(_ATT))}
    for tamper in ({"patch": "x"}, {"test_output_after": "0 passed"}, {"repro_test": {"path": "tests/test_x.py", "content": "evil"}}):
        assert verify_attestation_with_keys({**att, **tamper}, {"keys": []}) == {"ok": False, "reason": "STATEMENT_MISMATCH"}
    bad_type = {**att, "signature": {**att["signature"], "payloadType": "application/vnd.codai.rules+json;v=1"}}
    assert verify_attestation_with_keys(bad_type, {"keys": []}) == {"ok": False, "reason": "BAD_PAYLOAD_TYPE"}
    assert attestation_statement(_ATT) == json.loads(_statement_bytes(_ATT))


def test_keys_hits_public_route(rclient, stub):
    stub.reply(200, {"keys": []})
    assert rclient.resolve.keys() == {"keys": []}
    assert stub.last.method == "GET" and stub.last.path == "/v1/resolve/keys"


def test_signature_verifies_like_the_service_signs(rclient, stub):
    pytest.importorskip("cryptography")
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    def pem(k):
        return k.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()

    signer, other = ec.generate_private_key(ec.SECP256R1()), ec.generate_private_key(ec.SECP256R1())
    body = _statement_bytes(_ATT)
    t = _PT.encode()
    pae = b"DSSEv1 %d %s %d " % (len(t), t, len(body)) + body
    att = {**_ATT, "signature": _envelope(body, signer.sign(pae, ec.ECDSA(hashes.SHA256())))}

    def keys(k):
        return {"keys": [{"keyid": "k1", "algorithm": "ECDSA_P256_SHA256", "payload_type": _PT, "encoding": "DSSE v1", "public_key_pem": pem(k)}]}

    assert verify_attestation_with_keys(att, keys(signer)) == {"ok": True, "keyid": "k1"}
    assert verify_attestation_with_keys(att, keys(other)) == {"ok": False, "reason": "BAD_SIGNATURE"}
    stub.reply(200, keys(signer))
    assert rclient.resolve.verify_attestation(att) == {"ok": True, "keyid": "k1"}
    assert stub.last.path == "/v1/resolve/keys"
