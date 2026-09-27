"""``client.resolve`` against the stub, plus parity with resolve.yaml operationIds."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from codai import (
    RESOLVE_OPERATION_METHODS,
    Codai,
    ResolveError,
    ResolveInsufficientFundsError,
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
