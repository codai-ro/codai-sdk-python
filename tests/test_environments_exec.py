"""``client.environments.exec / files / jobs`` (SB2-03 REST exec) against the http.server stub."""

from __future__ import annotations

import pytest

from codai import CodaiError


def test_exec_posts_body(client, stub):
    stub.reply(200, {"ok": True, "exit_code": 0, "stdout": "hi\n", "stderr": ""})
    r = client.environments.exec("e1", {"command": "echo hi", "timeout_ms": 5000})
    assert r["exit_code"] == 0
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/environments/e1/exec")
    assert stub.last.json == {"command": "echo hi", "timeout_ms": 5000}


def test_exec_offline_raises(client, stub):
    stub.reply(409, {"error": {"code": "environment_offline", "message": "offline"}})
    with pytest.raises(CodaiError):
        client.environments.exec("e1", {"command": "ls"})


def test_files_list_get_put(client, stub):
    stub.reply(200, {"path": "/w", "entries": [], "truncated": False})
    client.environments.files.list("e1")
    assert (stub.last.method, stub.last.path, stub.last.query) == ("GET", "/v1/environments/e1/files", "")
    stub.reply(200, {"path": "/w", "entries": [], "truncated": False})
    client.environments.files.list("e1", "/w/src")
    assert stub.last.query == "path=%2Fw%2Fsrc"

    stub.reply(200, {"path": "/w/a b.txt", "content": "x", "size": 1, "truncated": False})
    r = client.environments.files.get("e1", "/w/a b.txt", max_bytes=100)
    assert r["content"] == "x"
    assert (stub.last.path, stub.last.query) == ("/v1/environments/e1/files/w/a%20b.txt", "max_bytes=100")

    stub.reply(200, {"path": "/w/n.txt", "bytes": 5, "created": True})
    w = client.environments.files.put("e1", "/w/n.txt", "hello")
    assert w["created"] is True
    assert (stub.last.method, stub.last.path, stub.last.body) == ("PUT", "/v1/environments/e1/files/w/n.txt", b"hello")
    assert "text/plain" in stub.last.headers.get("content-type", "")


def test_jobs_start_and_get(client, stub):
    stub.reply(201, {"job_id": 7, "label": "pnpm test"})
    assert client.environments.jobs.start("e1", {"command": "pnpm test"})["job_id"] == 7
    assert (stub.last.method, stub.last.path, stub.last.json) == (
        "POST",
        "/v1/environments/e1/jobs",
        {"command": "pnpm test"},
    )
    stub.reply(200, {"job": {"id": 7, "state": "running"}, "output": {"text": "", "next_offset": 0}})
    r = client.environments.jobs.get("e1", 7, since=10, tail=50)
    assert r["job"]["state"] == "running"
    assert (stub.last.method, stub.last.path, stub.last.query) == ("GET", "/v1/environments/e1/jobs/7", "since=10&tail=50")
