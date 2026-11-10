"""assets: resumable uploads (GCS session), ingest and search."""

from __future__ import annotations

import io
import json

import pytest

from conftest import Reply

from codai import CodaiError

ID = "7d0f2c1e-0000-4000-8000-000000000003"
G = 262144
COMPLETED = {"asset": {"asset_id": ID, "kind": "upload", "status": "ready"}, "ingest": {"status": "queued"}}


def _session(stub, **over):
    body = {
        "id": ID,
        "object": "studio.upload",
        "upload_url": f"{stub.url}/upload/session?upload_id=SECRET",
        "chunk_granularity": G,
        "max_bytes": 4294967296,
        "expires_at": "2026-11-11T00:00:00.000Z",
    }
    body.update(over)
    return body


def _r308(last=None):
    return lambda _r: Reply(308, b"", {} if last is None else {"Range": f"bytes=0-{last}"})


def test_create_upload_posts_body_with_idempotency_key(client, stub):
    stub.reply(201, _session(stub))
    r = client.assets.create_upload("a.mp4", "video/mp4", 10, ingest=False, idempotency_key="up-1")
    assert stub.last.method == "POST"
    assert stub.last.path == "/v1/assets/uploads"
    assert stub.last.headers["idempotency-key"] == "up-1"
    assert stub.last.json == {"filename": "a.mp4", "mime": "video/mp4", "bytes": 10, "ingest": False}
    assert r["object"] == "studio.upload"


def test_complete_quota_ingest_run_ingest_search_routes(client, stub):
    stub.reply(200, COMPLETED)
    stub.reply(200, {"used_bytes": 1, "limit_bytes": 53687091200, "max_file_bytes": 4294967296})
    stub.reply(200, {"status": "none"})
    stub.reply(202, {"status": "queued", "quote_micro_usd": 50})
    stub.reply(200, {"object": "list", "data": [{"asset_id": ID, "t_ms": 1500, "kind": "frame", "score": 0.8}]})
    assert client.assets.complete_upload(ID) == COMPLETED
    assert client.assets.quota()["limit_bytes"] == 53687091200
    assert client.assets.ingest(ID)["status"] == "none"
    assert client.assets.run_ingest(ID, language="ro", idempotency_key="ing-1")["status"] == "queued"
    assert client.assets.search("red car", limit=5)["data"][0]["t_ms"] == 1500
    got = [(r.method, r.path) for r in stub.requests]
    assert got == [
        ("POST", f"/v1/assets/uploads/{ID}/complete"),
        ("GET", "/v1/assets/quota"),
        ("GET", f"/v1/assets/{ID}/ingest"),
        ("POST", f"/v1/assets/{ID}/ingest"),
        ("GET", "/v1/assets/search"),
    ]
    assert stub.requests[3].json == {"language": "ro"}
    assert stub.requests[3].headers["idempotency-key"] == "ing-1"
    assert stub.requests[4].query == "q=red+car&limit=5"


def test_run_ingest_without_language_sends_empty_object(client, stub):
    stub.reply(202, {"status": "running"})
    client.assets.run_ingest(ID)
    assert stub.last.json == {}


def test_upload_308_flow_without_api_key_then_complete(client, stub, tmp_path):
    total = 2 * G + 100
    path = tmp_path / "clip.mp4"
    path.write_bytes(bytes(i % 251 for i in range(total)))
    stub.reply(201, _session(stub))
    stub.on(_r308(G - 1))
    stub.on(_r308(2 * G - 1))
    stub.reply(200, b"")
    stub.reply(200, COMPLETED)
    progress = []
    r = client.assets.upload(path, chunk_size=G, on_progress=lambda s, t: progress.append(s))
    assert r == COMPLETED
    create = stub.requests[0]
    assert create.json == {"filename": "clip.mp4", "mime": "video/mp4", "bytes": total, "ingest": True}
    puts = [x for x in stub.requests if x.method == "PUT"]
    assert [p.headers["content-range"] for p in puts] == [
        f"bytes 0-{G - 1}/{total}",
        f"bytes {G}-{2 * G - 1}/{total}",
        f"bytes {2 * G}-{total - 1}/{total}",
    ]
    for p in puts:
        assert p.path == "/upload/session"
        assert "authorization" not in p.headers
    assert len(puts[2].body) == 100
    assert puts[1].body == path.read_bytes()[G : 2 * G]
    assert (stub.last.method, stub.last.path) == ("POST", f"/v1/assets/uploads/{ID}/complete")
    assert progress == [G, 2 * G, total]


def test_upload_resumes_failed_chunk_from_status_query(client, stub):
    total = 3 * G
    data = bytes(i % 7 for i in range(total))
    stub.reply(201, _session(stub))
    stub.on(_r308(G - 1))  # chunk 1 ok
    stub.reply(503, b"")  # chunk 2 fails
    stub.on(_r308(G + 1000 - 1))  # status: storage kept 1000 bytes of chunk 2
    stub.on(_r308(2 * G + 999))  # resend from G+1000
    stub.reply(201, b"")  # last chunk done
    stub.reply(200, COMPLETED)
    client.assets.upload(data, filename="a.wav", mime="audio/wav", chunk_size=G, retry_delay=0)
    puts = [x for x in stub.requests if x.method == "PUT"]
    assert [p.headers["content-range"] for p in puts] == [
        f"bytes 0-{G - 1}/{total}",
        f"bytes {G}-{2 * G - 1}/{total}",
        f"bytes */{total}",
        f"bytes {G + 1000}-{2 * G + 999}/{total}",
        f"bytes {2 * G + 1000}-{total - 1}/{total}",
    ]
    assert puts[2].body == b""
    assert puts[3].body == data[G + 1000 : 2 * G + 1000]
    assert stub.last.path == f"/v1/assets/uploads/{ID}/complete"


class _Pipe(io.RawIOBase):
    """A non-seekable binary stream."""

    def __init__(self, data: bytes) -> None:
        self._buf = io.BytesIO(data)
        self.name = "clip.webm"

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def read(self, n: int = -1) -> bytes:
        return self._buf.read(n)


def test_upload_non_seekable_stream_and_done_reported_by_status(client, stub):
    total = 2 * G
    data = bytes([0]) * G + bytes([4]) * G
    stub.reply(201, _session(stub))
    stub.on(_r308(G - 1))
    stub.reply(503, b"")  # last chunk errors...
    stub.reply(200, b"")  # ...but the status query says it finished
    stub.reply(200, COMPLETED)
    client.assets.upload(_Pipe(data), size=total, chunk_size=G, retry_delay=0)
    puts = [x for x in stub.requests if x.method == "PUT"]
    assert puts[0].body[:1] == b"\x00" and puts[1].body[:1] == b"\x04"
    assert puts[2].headers["content-range"] == f"bytes */{total}"
    assert json.loads(stub.requests[0].body)["mime"] == "video/webm"
    assert stub.last.method == "POST"


def test_upload_gives_up_and_validates_chunk_size(client, stub):
    stub.reply(201, _session(stub))
    stub.reply(500, b"")
    stub.reply(500, b"")
    stub.reply(500, b"")
    with pytest.raises(CodaiError) as e:
        client.assets.upload(b"0123456789", filename="a.png", max_chunk_retries=1, retry_delay=0)
    assert e.value.status == 500
    with pytest.raises(ValueError, match="multiple of 262144"):
        client.assets.upload(b"0123456789", filename="a.png", chunk_size=1000)
