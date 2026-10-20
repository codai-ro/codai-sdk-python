"""``client.batches`` (E-11b) against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError

_ID = "9b1c2d3e-0000-4000-8000-000000000060"
_TPL = "5d2e8f1a-3b4c-4d5e-9f60-7a8b9c0d1e2f"
_BASE = "/v1/studio/batches"
_CSV = "headline,price\nVara la mare,199\n"


def _batch(status, **extra):
    return {"id": _ID, "title": "Promo", "status": status, "zip": {"status": "none", "url": None, "error": None}, **extra}


def test_create_and_dry_run_send_the_body_with_dry_run(client, stub):
    stub.reply(200, {"dry_run": True, "rows": 1, "valid": 1, "errors": []})
    stub.reply(201, {"batch": _batch("queued")})
    assert client.batches.dry_run({"template_id": _TPL}, csv=_CSV, mapping={"price": None})["valid"] == 1
    assert client.batches.create({"template_id": _TPL}, csv=_CSV, render=True, quality="draft")["batch"]["status"] == "queued"
    assert [(r.method, r.path) for r in stub.requests] == [("POST", _BASE), ("POST", _BASE)]
    assert stub.requests[0].json == {"source": {"template_id": _TPL}, "csv": _CSV, "mapping": {"price": None}, "dry_run": True}
    assert stub.requests[1].json == {
        "source": {"template_id": _TPL},
        "csv": _CSV,
        "render": True,
        "quality": "draft",
        "dry_run": False,
    }


def test_create_forwards_ai_label(client, stub):
    stub.reply(201, {"batch": _batch("queued")})
    client.batches.create({"template_id": _TPL}, csv=_CSV, render=True, ai_label="corner")
    assert stub.requests[0].json == {
        "source": {"template_id": _TPL},
        "csv": _CSV,
        "render": True,
        "ai_label": "corner",
        "dry_run": False,
    }


def test_create_with_every_row_invalid_raises_400(client, stub):
    stub.reply(400, {"error": {"message": "Every row is invalid.", "type": "invalid_request_error", "code": "invalid_rows"}})
    with pytest.raises(CodaiError) as e:
        client.batches.create({"creative_id": _ID, "seq": 3}, sheet={"creative_id": _TPL})
    assert e.value.status == 400
    assert stub.last.json == {"source": {"creative_id": _ID, "seq": 3}, "sheet": {"creative_id": _TPL}, "dry_run": False}


def test_list_get_cancel_retry_zip_routes(client, stub):
    stub.reply(200, {"batches": [_batch("running")], "next_before": None})
    stub.reply(200, {"batch": _batch("running"), "rows": [{"idx": 0, "status": "done"}]})
    stub.reply(200, _batch("cancelled"))
    stub.reply(200, _batch("running"))
    stub.reply(202, _batch("completed", zip={"status": "building", "url": None, "error": None}))
    assert len(client.batches.list(limit=10)["batches"]) == 1
    assert client.batches.get(_ID, rows=True, status="done", limit=20)["rows"][0]["status"] == "done"
    assert client.batches.cancel(_ID)["status"] == "cancelled"
    assert client.batches.retry(_ID)["status"] == "running"
    assert client.batches.zip(_ID)["zip"]["status"] == "building"
    assert [(r.method, r.path, r.query) for r in stub.requests] == [
        ("GET", _BASE, "limit=10"),
        ("GET", f"{_BASE}/{_ID}", "rows=1&status=done&limit=20"),
        ("POST", f"{_BASE}/{_ID}/cancel", ""),
        ("POST", f"{_BASE}/{_ID}/retry", ""),
        ("POST", f"{_BASE}/{_ID}/zip", ""),
    ]


def test_export_csv_returns_text(client, stub):
    csv = "headline,price,creative_id,status,error,render_url\nVara la mare,199,,done,,\n"
    stub.reply(200, csv, {"Content-Type": "text/csv; charset=utf-8"})
    assert client.batches.export_csv(_ID) == csv
    assert (stub.last.method, stub.last.path) == ("GET", f"{_BASE}/{_ID}/export.csv")


def test_wait_polls_until_finished(client, stub):
    stub.reply(200, {"batch": _batch("queued")})
    stub.reply(200, {"batch": _batch("running")})
    stub.reply(200, {"batch": _batch("completed")})
    assert client.batches.wait(_ID, interval=0.01)["status"] == "completed"
    assert len(stub.requests) == 3


def test_wait_times_out(client, stub):
    stub.reply(200, {"batch": _batch("running")})
    with pytest.raises(TimeoutError):
        client.batches.wait(_ID, interval=0.05, timeout=0.01)
