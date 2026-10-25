"""``client.transcripts`` against the http.server stub: routes, query encoding, export, SSE and the tus upload."""

from __future__ import annotations

import base64

import pytest

from codai import Codai, CodaiError
from codai.resources.transcripts import upload_id_from_location

from conftest import Reply


def test_transcript_routes(client, stub):
    stub.reply(200, {"data": [], "next_cursor": None})
    client.transcripts.list(folder_id="f1", pinned=True, limit=10)
    assert stub.last.method == "GET" and stub.last.path == "/v1/transcripts"
    assert stub.last.query == "folder_id=f1&pinned=true&limit=10"
    stub.reply(201, {"id": "t1", "status": "recording"})
    assert client.transcripts.create({"client_id": "c1", "source": "desktop"})["id"] == "t1"
    assert stub.last.method == "POST" and stub.last.json == {"client_id": "c1", "source": "desktop"}
    stub.reply(200, {"id": "t 1"})
    client.transcripts.get("t 1")
    assert stub.last.path == "/v1/transcripts/t%201"
    stub.reply(202, {"id": "t1", "status": "queued"})
    client.transcripts.finalize("t1", {"uploads": [{"id": "u1", "track": "mic"}]})
    assert stub.last.method == "POST" and stub.last.path == "/v1/transcripts/t1/finalize"
    stub.reply(200, {"label": "spk:0", "name": "Ana"})
    client.transcripts.rename_speaker("t1", "spk:0", {"name": "Ana"})
    assert stub.last.method == "PATCH" and stub.last.path == "/v1/transcripts/t1/speakers/spk%3A0"
    stub.reply(200, {"seq": 3})
    client.transcripts.edit_utterance("t1", 3, "corectat")
    assert stub.last.path == "/v1/transcripts/t1/utterances/3" and stub.last.json == {"text": "corectat"}
    stub.reply(201, {"id": "p1", "created": True})
    client.transcripts.accept_prompt("t1", 2)
    assert stub.last.path == "/v1/transcripts/t1/prompts/2/accept"
    stub.reply(204, None)
    assert client.transcripts.delete("t1") is None
    assert stub.last.method == "DELETE"


def test_transcript_search_ask_folders_vocabulary(client, stub):
    stub.reply(200, {"hits": []})
    client.transcripts.search("buget", mode="hybrid", limit=5)
    assert stub.last.path == "/v1/transcripts/search" and stub.last.query == "q=buget&mode=hybrid&limit=5"
    stub.reply(200, {"answer": "x", "citations": []})
    client.transcripts.ask({"question": "Ce am decis?"})
    assert stub.last.method == "POST" and stub.last.path == "/v1/transcripts/ask"
    stub.reply(201, {"id": "f1", "name": "Clienți"})
    client.transcripts.folders.create({"name": "Clienți"})
    assert stub.last.path == "/v1/transcript-folders"
    stub.reply(200, {"terms": ["codai"]})
    client.transcripts.vocabulary.put(["codai"])
    assert stub.last.method == "PUT" and stub.last.json == {"terms": ["codai"]}


def test_transcript_export_reads_text_and_filename(client, stub):
    stub.on(
        lambda _r: Reply(
            200,
            "# Ședință",
            {"Content-Type": "text/markdown; charset=utf-8", "Content-Disposition": "attachment; filename*=UTF-8''%C8%98edin%C8%9B%C4%83.md"},
        )
    )
    out = client.transcripts.export("t1", "md")
    assert stub.last.query == "format=md"
    assert out == {"text": "# Ședință", "filename": "Ședință.md", "content_type": "text/markdown; charset=utf-8"}


def test_transcript_export_pdf_returns_bytes(client, stub):
    pdf = b"%PDF-1.7\n\x00\xff binary"
    stub.on(
        lambda _r: Reply(
            200,
            pdf,
            {
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment; filename=\"Sedinta.pdf\"; filename*=UTF-8''%C8%98edin%C8%9B%C4%83.pdf",
            },
        )
    )
    out = client.transcripts.export("t1", "pdf")
    assert stub.last.query == "format=pdf"
    assert out == {"bytes": pdf, "filename": "Ședință.pdf", "content_type": "application/pdf"}


def test_transcript_shares_and_public_view(client, stub):
    token = "x" * 43
    stub.reply(201, {"id": "s1", "token": token, "url": f"https://hub.codai.ro/t/{token}", "expiresAt": None})
    created = client.transcripts.shares.create("t1", expires_in_days=7)
    assert created["url"].endswith(token)
    assert stub.last.method == "POST" and stub.last.path == "/v1/transcripts/t1/shares"
    assert stub.last.json == {"expiresInDays": 7}
    stub.reply(201, {"id": "s2", "token": token, "url": "u", "expiresAt": None})
    client.transcripts.shares.create("t1")
    assert stub.last.json == {}
    stub.reply(200, {"data": [{"id": "s1", "url": None, "createdAt": "2026-10-06T00:00:00Z", "expiresAt": None}]})
    assert client.transcripts.shares.list("t1") == [
        {"id": "s1", "url": None, "createdAt": "2026-10-06T00:00:00Z", "expiresAt": None}
    ]
    stub.reply(204, None)
    assert client.transcripts.shares.revoke("t1", "s1") is None
    assert stub.last.method == "DELETE" and stub.last.path == "/v1/transcripts/t1/shares/s1"
    view = {"title": "T", "createdAt": "x", "durationMs": 1, "speakers": [], "utterances": [], "insights": None}
    stub.reply(200, view)
    assert client.transcripts.public_view(token) == view
    assert stub.last.path == f"/v1/public/transcripts/{token}"


def test_transcript_stream_yields_transcript_events_only(client, stub):
    stub.sse([": keepalive\n\n", 'event: transcript\ndata: {"op":"progress","id":"t1","progress":0.5}\n\n', "event: ping\ndata: {}\n\n"])
    assert list(client.transcripts.stream()) == [{"op": "progress", "id": "t1", "progress": 0.5}]


def test_upload_id_from_location():
    assert upload_id_from_location("https://ai.codai.ro/v1/uploads/abc%20d?x=1") == "abc d"
    assert upload_id_from_location("/v1/uploads/u1/") == "u1"
    with pytest.raises(CodaiError):
        upload_id_from_location("/")


def test_upload_audio_creates_and_patches_chunks(client, stub):
    held = {"offset": 0}

    def create(r):
        md = dict(part.split(" ") for part in r.headers["upload-metadata"].split(","))
        assert base64.b64decode(md["track"]) == b"mic" and base64.b64decode(md["transcript"]) == b"t1"
        assert r.headers["tus-resumable"] == "1.0.0" and r.headers["upload-length"] == "10"
        return Reply(201, None, {"Location": "/v1/uploads/u1", "Tus-Resumable": "1.0.0"})

    def patch(r):
        assert r.headers["upload-offset"] == str(held["offset"])
        assert r.headers["content-type"] == "application/offset+octet-stream"
        held["offset"] += len(r.body)
        return Reply(204, None, {"Upload-Offset": str(held["offset"])})

    stub.on(create)
    for _ in range(3):
        stub.on(patch)
    seen = []
    uid = client.transcripts.upload_audio(b"0123456789", transcript_id="t1", chunk_size=4, on_progress=lambda a, b: seen.append((a, b)))
    assert uid == "u1"
    assert [r.method for r in stub.requests] == ["POST", "PATCH", "PATCH", "PATCH"]
    assert seen == [(0, 10), (4, 10), (8, 10), (10, 10)]


def test_upload_audio_resumes_from_server_offset(client, stub):
    stub.on(lambda _r: Reply(200, None, {"Upload-Offset": "6", "Upload-Length": "10"}))
    stub.on(lambda r: Reply(204, None, {"Upload-Offset": str(6 + len(r.body))}))
    assert client.transcripts.upload_audio(b"0123456789", upload_id="u9") == "u9"
    assert [r.method for r in stub.requests] == ["HEAD", "PATCH"]
    assert stub.requests[1].body == b"6789"


def test_upload_append_rejects_stuck_offset(client, stub):
    stub.reply(204, None, {"Upload-Offset": "0"})
    with pytest.raises(CodaiError):
        client.transcripts.uploads.append("u1", 0, b"abc")


def test_upload_capabilities_parses_headers(client, stub):
    stub.reply(204, None, {"Tus-Version": "1.0.0", "Tus-Extension": "creation, termination", "Tus-Max-Size": "1073741824"})
    caps = client.transcripts.uploads.capabilities()
    assert stub.last.method == "OPTIONS"
    assert caps == {"version": "1.0.0", "extensions": ["creation", "termination"], "max_size": 1073741824}


def test_ask_is_not_retried(stub):
    c = Codai(api_key="codai_test", base_url=stub.url, max_retries=2, timeout=5)
    stub.reply(503, {"error": {"code": "unavailable", "message": "down"}})
    with pytest.raises(CodaiError):
        c.transcripts.ask({"question": "x"})
    assert len(stub.requests) == 1
