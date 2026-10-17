"""``client.billing`` (read-only), ``client.referrals`` and ``client.resolve.list/iterate`` against the stub."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from codai import Codai, CodaiError

JOB = "11111111-2222-4333-8444-555555555555"


def _overview(balance: float) -> Dict[str, Any]:
    return {
        "plan": {
            "tier_slug": "pro",
            "tier_label": "Pro",
            "tasks_per_month": 100,
            "tasks_used_this_month": 3,
            "has_active_subscription": True,
            "supports_byok": True,
            "subscription": None,
        },
        "wallet": {"balance_eur": balance, "next_expiry_at": None, "promo_granted_eur": 0, "history": []},
        "auto_topup": {
            "enabled": False,
            "threshold_eur": 5,
            "amount_eur": 20,
            "monthly_cap_eur": 100,
            "month_spent_eur": 0,
            "last_topup_at": None,
            "failures": 0,
        },
        "compute_reserve_eur": 0,
        "payment_methods": [],
        "links": {
            "billing": "https://hub.codai.ro/billing",
            "portal": "https://pay.codai.ro/portal",
            "topup": {"10": "https://pay.codai.ro/checkout?topup=10"},
            "checkout_plan": {},
        },
    }


def test_billing_get(client, stub):
    stub.reply(200, _overview(12.5))
    r = client.billing.get()
    assert r["wallet"]["balance_eur"] == 12.5
    assert stub.last.method == "GET" and stub.last.path == "/v1/billing"


def test_billing_invoices_unwraps_and_sends_limit(client, stub):
    inv = {"id": "inv_1", "kind": "invoice", "number": "CDI-0001", "issued_at": "2026-10-01T00:00:00Z",
           "total_eur": 19, "currency": "EUR", "efactura_status": None,
           "pdf_url": "https://hub.codai.ro/api/billing/fiscal/inv_1/pdf"}
    stub.reply(200, {"invoices": [inv]})
    assert client.billing.invoices(limit=5) == [inv]
    assert stub.last.path == "/v1/billing/invoices" and stub.last.query == "limit=5"


def test_billing_watch_balance_fires_once_per_crossing_and_only_reads(client, stub):
    for b in (10, 4, 3, 8, 2):
        stub.reply(200, _overview(b))
    lows: List[float] = []
    sleeps: List[float] = []
    n = client.billing.watch_balance(5, lambda bal, _b: lows.append(bal), interval_s=2, max_checks=5,
                                     sleep=sleeps.append)
    assert n == 5
    assert lows == [4.0, 2.0]
    assert sleeps == [2, 2, 2, 2]
    assert all(r.method == "GET" and r.path == "/v1/billing" for r in stub.requests)


def test_billing_watch_balance_survives_errors_and_stops_on_stopiteration(client, stub):
    stub.reply(500, {"error": {"message": "boom", "type": "server_error"}})
    stub.reply(200, _overview(1))
    errors: List[Exception] = []

    def on_low(_bal: float, _b: Dict[str, Any]) -> None:
        raise StopIteration

    n = client.billing.watch_balance(5, on_low, max_checks=10, on_error=errors.append, sleep=lambda _s: None)
    assert n == 2
    assert len(errors) == 1 and isinstance(errors[0], CodaiError)


def test_referrals_get_redeem_consent(client, stub):
    view = {"referral": None, "redeem_until": None, "referrals": [
        {"id": JOB, "referee": "#a1b2c3", "status": "pending",
         "created_at": "2026-10-01T00:00:00Z", "rewarded_at": None, "reward_eur": None}]}
    stub.reply(200, view)
    assert client.referrals.get() == view
    assert stub.last.method == "GET" and stub.last.path == "/v1/referrals"

    stub.reply(200, {"referral_result": "ok"})
    client.referrals.redeem("ana_pop")
    assert stub.last.method == "PATCH" and stub.last.path == "/v1/account"
    assert stub.last.json == {"referral_code": "ana_pop"}

    stub.reply(200, {})
    client.referrals.set_consent(False)
    assert stub.last.json == {"referral_consent": False}


@pytest.fixture
def rclient(stub) -> Codai:
    return Codai(api_key="codai_test", resolve_base_url=stub.url, max_retries=0, timeout=5)


def _job(i: str) -> Dict[str, Any]:
    return {"id": i, "status": "resolved", "repo_url": "https://github.com/o/r", "tier": "t7",
            "quote_micro_usd": 7000000, "triage_reason": None, "decline_reason": None, "fail_reason": None,
            "cost_micro_usd": 0, "attestation_id": None, "attestation_url": None,
            "created_at": "2026-10-16T00:00:00Z", "completed_at": None,
            "issue_url": None, "issue_title": "it crashes"}


def test_resolve_list_sends_csv_limit_cursor(rclient, stub):
    stub.reply(200, {"jobs": [_job("a")], "next_cursor": "c1"})
    page = rclient.resolve.list(status=["running", "quoted"], limit=10, cursor="c0")
    assert page["next_cursor"] == "c1" and page["jobs"][0]["issue_title"] == "it crashes"
    assert stub.last.path == "/v1/resolve/jobs"
    assert stub.last.query == "status=running%2Cquoted&limit=10&cursor=c0"


def test_resolve_iterate_follows_cursor(rclient, stub):
    stub.reply(200, {"jobs": [_job("a"), _job("b")], "next_cursor": "c1"})
    stub.reply(200, {"jobs": [_job("c")], "next_cursor": None})
    ids = [j["id"] for j in rclient.resolve.iterate(status="resolved", limit=2)]
    assert ids == ["a", "b", "c"]
    assert [r.query for r in stub.requests] == ["status=resolved&limit=2", "status=resolved&limit=2&cursor=c1"]
