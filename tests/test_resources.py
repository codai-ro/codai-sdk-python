"""Resource classes against the http.server stub, plus 0.1.x backward compatibility."""

from __future__ import annotations

import json

import codai
from codai import Codai, ChatResult


def _chat_response(content="PONG", tool_calls=None):
    msg = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "model": "codai",
        "choices": [{"index": 0, "message": msg, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 2, "prompt_tokens_details": {"cached_tokens": 4}},
    }


def test_version():
    assert codai.__version__ == "0.2.1"


def test_chat_completions_create(client, stub):
    stub.reply(
        200,
        _chat_response(),
        {"x-codai-routed-to": "gemini-2.5-flash", "x-request-id": "req-1", "x-codai-event-id": "ev-1"},
    )
    r = client.chat.completions.create(
        {"messages": [{"role": "user", "content": "ping"}]}, ext={"effort": "minimal"}
    )
    assert isinstance(r, ChatResult)
    assert r.content == "PONG"
    assert r.routed_to == "gemini-2.5-flash"
    assert r.request_id == "req-1"
    assert r.event_id == "ev-1"
    assert r.usage == {"prompt_tokens": 10, "completion_tokens": 2, "cached_tokens": 4}
    body = stub.last.json
    assert body["model"] == "codai" and body["stream"] is False
    assert stub.last.headers["x-codai-effort"] == "minimal"


def test_legacy_chat_still_works(client, stub):
    stub.reply(200, _chat_response("hi"), {"x-request-id": "req-2"})
    r = client.chat(
        [{"role": "user", "content": "hello"}],
        model="codai",
        max_tokens=5,
        agent_mode=True,
        compact="auto",
        best_of=3,
        session_id="s-1",
    )
    assert r.content == "hi" and r.request_id == "req-2"
    body = stub.last.json
    assert body == {"model": "codai", "messages": [{"role": "user", "content": "hello"}], "max_tokens": 5, "stream": False}
    h = stub.last.headers
    assert h["x-codai-mode"] == "agent"
    assert h["x-codai-compact"] == "1"
    assert h["x-codai-best-of"] == "3"
    assert h["x-codai-session-id"] == "s-1"


def _sse(*objs, done=True):
    frames = ["data: " + json.dumps(o) + "\n\n" for o in objs]
    if done:
        frames.append("data: [DONE]\n\n")
    return frames


def _chunk(delta, finish=None, usage=None):
    c = {"id": "c", "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
    if usage:
        c["usage"] = usage
    return c


def test_chat_stream_text_chunks_and_final(client, stub):
    stub.sse(
        _sse(
            _chunk({"role": "assistant", "content": "Hel"}),
            _chunk({"content": "lo"}),
            _chunk({"tool_calls": [{"index": 0, "id": "call_1", "type": "function", "function": {"name": "f", "arguments": '{"a'}}]}),
            _chunk({"tool_calls": [{"index": 0, "function": {"arguments": '":1}'}}]}, finish="tool_calls"),
            _chunk({}, usage={"prompt_tokens": 3, "completion_tokens": 4}),
        ),
        headers={"x-codai-routed-to": "m1", "x-codai-trace-id": "t-1"},
    )
    s = client.chat.completions.stream({"messages": [{"role": "user", "content": "x"}]})
    assert "".join(s) == "Hello"
    assert stub.last.json["stream"] is True
    f = s.final
    assert f is not None
    assert f.content == "Hello"
    assert f.tool_calls == [{"index": 0, "id": "call_1", "type": "function", "function": {"name": "f", "arguments": '{"a":1}'}}]
    assert f.finish_reason == "tool_calls"
    assert f.usage == {"prompt_tokens": 3, "completion_tokens": 4}
    assert f.routed_to == "m1" and f.request_id == "t-1"


def test_legacy_chat_stream_yields_text(client, stub):
    stub.sse(_sse(_chunk({"content": "a"}), _chunk({"content": "b"})))
    assert list(client.chat_stream([{"role": "user", "content": "x"}], agent_mode=True)) == ["a", "b"]
    assert stub.last.headers["x-codai-mode"] == "agent"


def test_messages_create_and_stream(client, stub):
    stub.reply(200, {"id": "msg", "content": [{"type": "text", "text": "Hi "}, {"type": "text", "text": "there"}]})
    r = client.messages.create({"messages": [{"role": "user", "content": "x"}], "max_tokens": 10})
    assert r.text == "Hi there"
    stub.sse(
        [
            'event: message_start\ndata: {"type":"message_start","message":{"usage":{"input_tokens":5,"output_tokens":0}}}\n\n',
            'event: content_block_delta\ndata: {"type":"content_block_delta","delta":{"type":"text_delta","text":"He"}}\n\n',
            'event: content_block_delta\ndata: {"type":"content_block_delta","delta":{"type":"text_delta","text":"y"}}\n\n',
            'event: message_delta\ndata: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":2}}\n\n',
            'event: message_stop\ndata: {"type":"message_stop"}\n\n',
        ]
    )
    s = client.messages.stream({"messages": [{"role": "user", "content": "x"}], "max_tokens": 10})
    assert "".join(s.text()) == "Hey"
    assert s.final.stop_reason == "end_turn"
    assert s.final.usage == {"input_tokens": 5, "output_tokens": 2}


def test_responses_create_and_stream(client, stub):
    stub.reply(200, {"id": "resp", "output_text": "done"})
    assert client.responses.create({"input": "x"}).output_text == "done"
    stub.sse(
        [
            'event: response.output_text.delta\ndata: {"type":"response.output_text.delta","delta":"ab"}\n\n',
            'event: response.completed\ndata: {"type":"response.completed","response":{"id":"resp","output_text":"ab"}}\n\n',
        ]
    )
    s = client.responses.stream({"input": "x"})
    assert "".join(s.text()) == "ab"
    assert s.final.response == {"id": "resp", "output_text": "ab"}


def test_embeddings_new_and_legacy(client, stub):
    stub.reply(200, {"data": [{"embedding": [0.1, 0.2]}]}, {"x-codai-embed-fallback": "azure"})
    r = client.embeddings.create({"input": "hi"})
    assert r.embeddings == [[0.1, 0.2]] and r.fallback == "azure"
    assert stub.last.json["model"] == "codai-embed"
    stub.reply(200, {"data": [{"embedding": [1.0]}]})
    assert client.embeddings(["a"], dimensions=8) == [[1.0]]
    assert stub.last.json["dimensions"] == 8


def test_models_new_and_legacy(client, stub):
    stub.reply(200, {"object": "list", "data": [{"id": "codai"}]})
    assert client.models.list() == [{"id": "codai"}]
    stub.reply(200, {"object": "list", "data": [{"id": "codai"}]})
    assert client.models() == [{"id": "codai"}]


def test_feedback_new_and_legacy(client, stub):
    stub.reply(200, {"ok": True})
    client.feedback("ev-1", -1, comment="wrong")
    assert stub.last.json == {"event_id": "ev-1", "rating": -1, "comment": "wrong"}
    stub.reply(200, {"ok": True})
    assert client.feedback.submit({"session_id": "s", "rating": 1}) == {"ok": True}


def test_tokens_and_mint_token(client, stub):
    # Placeholder tokens use the `codai_xxx` shape so the gitleaks allowlist recognises them.
    stub.reply(200, {"token": "codai_xxx_realtime", "expires_at": "2026-01-01T00:00:00Z", "scope": "realtime"})
    t = client.tokens.create("realtime", 600)
    assert t.token == "codai_xxx_realtime" and t.scope == "realtime"
    assert stub.last.json == {"scope": "realtime", "ttl_seconds": 600}
    stub.reply(200, {"token": "codai_xxx_audio", "expires_at": "…", "scope": "audio"})
    assert client.mint_token("audio")["token"] == "codai_xxx_audio"


def test_audio_transcribe_multipart_and_speech(client, stub):
    stub.reply(200, {"text": "hello world"})
    text = client.audio.transcribe(b"RIFF....", filename="clip.wav", language="en")
    assert text == "hello world"
    req = stub.last
    assert req.headers["content-type"].startswith("multipart/form-data; boundary=")
    assert b'name="file"; filename="clip.wav"' in req.body
    assert b'name="language"\r\n\r\nen' in req.body
    assert b"RIFF...." in req.body
    stub.reply(200, b"\xff\xfbMP3", {"Content-Type": "audio/mpeg"})
    audio = client.speech("hi")
    assert audio == b"\xff\xfbMP3"
    assert stub.last.json == {"model": "codai-tts", "input": "hi", "voice": "alloy"}


def test_agents_run_runs_and_stream(client, stub):
    stub.reply(200, {"result": "ok", "model": "codai", "event_id": "ev-9", "usage": {"steps": 2}})
    r = client.agents_run("do it", context="ctx")
    assert r.result == "ok" and r.event_id == "ev-9"
    assert stub.last.json == {"task": "do it", "context": "ctx"}
    stub.reply(202, {"id": "run-1", "status": "queued"})
    assert client.agents.runs.create({"task": "x"})["id"] == "run-1"
    stub.reply(200, {"steps": [{"seq": 1}]})
    assert client.agents.runs.steps("run/1") == [{"seq": 1}]
    assert stub.last.path == "/v1/agents/runs/run%2F1/steps"
    stub.reply(200, {"ok": True})
    client.agents.runs.cancel("run-1")
    assert stub.last.method == "POST" and stub.last.json == {}
    stub.sse(
        [
            'event: step\ndata: {"seq":1,"kind":"plan","summary":"s"}\n\n',
            'event: done\ndata: {"status":"completed","result":"r","error":null,"step_count":1}\n\n',
            'event: step\ndata: {"seq":99}\n\n',
        ]
    )
    events = list(client.agents.runs.stream("run-1"))
    assert [e["event"] for e in events] == ["step", "done"]
    assert events[1]["data"]["status"] == "completed"


def test_tasks_devices_hosts_account_receipt(client, stub):
    stub.reply(200, {"tasks": [], "next_cursor": None})
    client.tasks.list(outcome="pass", limit=10)
    assert stub.last.query == "outcome=pass&limit=10"
    stub.reply(200, {"ok": True})
    client.tasks.confirm("t1", {"outcome": "confirmed"})
    assert stub.last.path == "/v1/tasks/t1/confirm"
    stub.reply(200, {"devices": [{"id": "d1"}]})
    assert client.devices.list() == [{"id": "d1"}]
    stub.reply(200, {"ok": True})
    client.devices.update("d1", {"name": "Laptop"})
    assert stub.last.method == "PATCH" and stub.last.json == {"name": "Laptop"}
    stub.reply(200, {"hosts": []})
    assert client.hosts.list() == []
    stub.reply(200, {"ok": True, "result": {}})
    client.hosts.exec("dev-1", "fs.list", {"path": "/"}, timeout_ms=5000, label="ls")
    assert stub.last.json == {"op": "fs.list", "args": {"path": "/"}, "timeout_ms": 5000, "label": "ls"}
    stub.reply(200, {"plan": {"tier": "pro"}})
    assert client.account.get()["plan"]["tier"] == "pro"
    stub.reply(200, {"total_micro_usd": 1})
    client.receipt.get(session_id="s-1")
    assert stub.last.query == "session_id=s-1"


def test_sessions_group(stub):
    c = Codai(api_key="k", base_url=stub.url, max_retries=0, device="5dc0de00-0000-4000-8000-00000000c0da")
    stub.reply(201, {"id": "sess-1", "session_key": "k1"})
    s = c.sessions.create({"session_key": "k1", "title": "t"})
    assert s["created"] is True and s["id"] == "sess-1"
    assert stub.last.headers["x-codai-device"] == "5dc0de00-0000-4000-8000-00000000c0da"
    stub.reply(200, {"sessions": [{"id": "sess-1"}]})
    assert c.sessions.list(limit=5, archived=True) == [{"id": "sess-1"}]
    assert stub.last.query == "limit=5&archived=1&v=2"
    stub.reply(200, {"events": [], "next_after": 0})
    c.sessions.events.list("sess-1", after=3)
    assert stub.last.path == "/v1/sessions/sess-1/events" and stub.last.query == "after=3"
    stub.reply(200, {"holder_device_id": "d", "expires_at": "x"})
    c.sessions.lease.renew("sess-1")
    assert stub.last.method == "PUT"
    stub.reply(200, {"ok": True})
    c.sessions.controls.mark_applied("sess-1", "c1")
    assert stub.last.path == "/v1/sessions/sess-1/control/c1/applied" and stub.last.method == "POST"
    stub.reply(200, {"sessions": []})
    c.sessions.shares.shared_with_me()
    assert stub.last.path == "/v1/sessions/shared-with-me"
    stub.sse(
        [
            ": ping 15000\n\n",
            'event: event\ndata: {"v":1,"seq":4}\n\n',
            'event: presence\ndata: {"v":1,"device_id":"d","online":true}\n\n',
        ]
    )
    events = list(c.sessions.stream("sess-1", after=3))
    assert [e["event"] for e in events] == ["event", "presence"]
    assert stub.last.query == "after=3"


def test_orgs_group(client, stub):
    stub.reply(201, {"id": "org-1", "name": "acme", "role": "owner"})
    assert client.orgs.create("acme")["id"] == "org-1"
    stub.reply(200, {"members": [{"user_id": "u1"}]})
    assert client.orgs.members.list("org-1") == [{"user_id": "u1"}]
    stub.reply(200, {"ok": True})
    client.orgs.members.remove("org-1", "u1")
    assert stub.last.method == "DELETE" and stub.last.path == "/v1/orgs/org-1/members/u1"
