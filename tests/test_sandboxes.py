"""``client.sandboxes`` against the http.server stub."""

from __future__ import annotations

import json

import pytest

from codai import CodaiError, SandboxFile

RECEIPT = {
    "image_digest": "sha256:x",
    "template": "codai-base",
    "input_sha256": "i",
    "command_sha256": "c",
    "outputs": [],
    "generation_before": 0,
    "generation_after": 1,
}


def test_create_list_retrieve(client, stub):
    stub.reply(201, {"id": "sb1", "object": "sandbox", "status": "running"})
    sb = client.sandboxes.create(ttl_seconds=600, egress={"mode": "preset", "preset": "pypi"})
    assert sb["id"] == "sb1"
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/sandboxes")
    assert stub.last.json == {"ttl_seconds": 600, "egress": {"mode": "preset", "preset": "pypi"}}
    stub.reply(201, {"id": "sb2"})
    client.sandboxes.create()
    assert stub.last.json == {}
    stub.reply(200, {"data": []})
    client.sandboxes.list()
    assert (stub.last.method, stub.last.path, stub.last.query) == ("GET", "/v1/sandboxes", "")
    stub.reply(200, {"data": []})
    client.sandboxes.list(status="running")
    assert stub.last.query == "status=running"
    stub.reply(200, {"id": "sb1"})
    client.sandboxes.retrieve("sb1")
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/sandboxes/sb1")


def test_exec_and_idempotency_key(client, stub):
    result = {"exit_code": 0, "stdout": "hi\n", "stderr": "", "timed_out": False, "duration_ms": 9, "receipt": RECEIPT}
    stub.reply(200, result)
    r = client.sandboxes.exec("sb1", shell="echo hi")
    assert r["stdout"] == "hi\n"
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/sandboxes/sb1/exec", {"shell": "echo hi"})
    assert "idempotency-key" not in stub.last.headers
    stub.reply(200, result)
    client.sandboxes.exec("sb1", language="python", code="print(1)", timeout_seconds=30, idempotency_key="k1")
    assert stub.last.json == {"language": "python", "code": "print(1)", "timeout_seconds": 30}
    assert stub.last.headers["idempotency-key"] == "k1"


def test_exec_stream_yields_events_until_exit(client, stub):
    exit_event = {
        "type": "exit",
        "exit_code": 0,
        "timed_out": False,
        "duration_ms": 5,
        "cpu_ms": 2,
        "generation": 1,
        "workspace_bytes": 10,
        "changed": ["out/act.pdf"],
        "receipt": RECEIPT,
    }
    stub.sse(
        [
            'data: {"type":"start","exec_id":"e1","instance":"i","restored":"hot","restore_ms":3}\n\n',
            ": ping\n\n",
            'data: {"type":"stdout","data":"\\u0219"}\n\n',
            'data: {"type":"stderr","data":"warn"}\n\n',
            f"data: {json.dumps(exit_event)}\n\n",
            'data: {"type":"stdout","data":"after"}\n\n',
        ]
    )
    events = list(client.sandboxes.exec_stream("sb1", cmd=["python3", "a.py"]))
    assert [e["type"] for e in events] == ["start", "stdout", "stderr", "exit"]
    assert events[1]["data"] == "ș"
    assert events[-1]["changed"] == ["out/act.pdf"]
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/sandboxes/sb1/exec")
    assert stub.last.headers["accept"] == "text/event-stream"
    assert stub.last.json == {"cmd": ["python3", "a.py"]}


def test_files_put_get_list(client, stub):
    stub.reply(200, {"path": "in/a b.txt", "bytes": 2, "sha256": "abc", "generation": 1})
    w = client.sandboxes.files.put("sb1", "/in/a b.txt", "hi")
    assert w["generation"] == 1
    assert (stub.last.method, stub.last.path, stub.last.body) == ("PUT", "/v1/sandboxes/sb1/files/in/a%20b.txt", b"hi")
    assert stub.last.headers["content-type"] == "application/octet-stream"
    stub.reply(200, b"%PDF-1.7", {"Content-Type": "application/pdf", "x-sha256": "deadbeef"})
    f = client.sandboxes.files.get("sb1", "out/act.pdf")
    assert isinstance(f, SandboxFile)
    assert (f.data, f.sha256, f.content_type) == (b"%PDF-1.7", "deadbeef", "application/pdf")
    assert stub.last.path == "/v1/sandboxes/sb1/files/out/act.pdf"
    stub.reply(200, {"entries": []})
    client.sandboxes.files.list("sb1", "out")
    assert (stub.last.path, stub.last.query) == ("/v1/sandboxes/sb1/files", "path=out")


def test_artifacts_snapshot_delete_run(client, stub):
    stub.reply(200, {"data": []})
    client.sandboxes.artifacts("sb1")
    assert (stub.last.method, stub.last.path) == ("GET", "/v1/sandboxes/sb1/artifacts")
    stub.reply(200, {"object": "o", "bytes": 1, "sha256": "s"})
    client.sandboxes.snapshot("sb1", name="v1")
    assert (stub.last.method, stub.last.path, stub.last.json) == ("POST", "/v1/sandboxes/sb1/snapshot", {"name": "v1"})
    stub.reply(204, None)
    assert client.sandboxes.delete("sb/1") is None
    assert (stub.last.method, stub.last.path) == ("DELETE", "/v1/sandboxes/sb%2F1")
    stub.reply(200, {"exit_code": 0, "stdout": "", "stderr": "", "timed_out": False, "duration_ms": 1, "artifacts": [], "receipt": RECEIPT})
    r = client.sandboxes.run(
        shell="python3 make.py",
        inputs=[{"path": "data.csv", "base64": "YQ=="}],
        egress={"mode": "none"},
        idempotency_key="run-1",
    )
    assert r["artifacts"] == []
    assert (stub.last.method, stub.last.path) == ("POST", "/v1/sandboxes/run")
    assert stub.last.json == {
        "egress": {"mode": "none"},
        "shell": "python3 make.py",
        "inputs": [{"path": "data.csv", "base64": "YQ=="}],
    }
    assert stub.last.headers["idempotency-key"] == "run-1"


def test_busy_is_a_codai_error(client, stub):
    stub.reply(409, {"error": {"code": "sandbox_busy", "message": "busy", "type": "invalid_request_error"}})
    with pytest.raises(CodaiError) as e:
        client.sandboxes.exec("sb1", shell="true")
    assert e.value.status == 409
