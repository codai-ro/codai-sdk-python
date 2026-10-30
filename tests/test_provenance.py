"""Public AI-provenance checker (LS-28) against the http.server stub."""

from __future__ import annotations

_RESULT = {
    "media_type": "audio/wav",
    "findings": [{"kind": "riff_info", "present": True, "ai_marked": True, "codai": True, "details": {}}],
    "codai_generated": True,
    "synthid_checked": False,
    "signature_verified": False,
}


def test_check_posts_the_raw_bytes_once(client, stub):
    stub.reply(200, _RESULT)
    r = client.provenance.check(b"RIFF....WAVE", content_type="audio/wav")
    assert r == _RESULT
    assert [(q.method, q.path) for q in stub.requests] == [("POST", "/v1/public/provenance/check")]
    assert stub.last.body == b"RIFF....WAVE"
    assert stub.last.headers.get("content-type") == "audio/wav"


def test_check_reads_a_path(client, stub, tmp_path):
    stub.reply(200, _RESULT)
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"\x00\x00\x00\x18ftypisom")
    client.provenance.check(f)
    assert stub.last.body == b"\x00\x00\x00\x18ftypisom"
    assert stub.last.headers.get("content-type") == "application/octet-stream"
