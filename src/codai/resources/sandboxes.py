"""``/v1/sandboxes`` — agent sandboxes: isolated gVisor containers with a persistent ``/workspace``,
no network by default, artifacts from ``/workspace/out`` as scanned, signed links. Backend ``v2`` (default)
is a long-lived GKE pod with pause/resume, fork, a persistent kernel and preview URLs; ``v1`` (Cloud Run) on
request."""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict, Iterator, List, Mapping, Optional, Union

from .._http import RequestExtensions, frame_json
from ._base import Resource, enc

__all__ = ["Sandboxes", "SandboxFiles", "SandboxFile", "sandbox_pty_url"]

_EXEC_KEYS = ("cmd", "shell", "language", "code", "env", "cwd", "timeout_seconds", "stdin", "inputs")
_CREATE_KEYS = ("backend", "template", "ttl_seconds", "egress", "metadata")
# Pause / resume / fork wait for a snapshot or a pod start (server caps: 180 s snapshot, 240 s start).
_LIFECYCLE_TIMEOUT = 480.0


def _base(sandbox_id: str, suffix: str = "") -> str:
    return f"/v1/sandboxes/{enc(sandbox_id)}{suffix}"


def _file_path(path: str) -> str:
    """Percent-encode each segment of a workspace path, keeping the slashes."""
    return "/".join(urllib.parse.quote(s, safe="") for s in path.lstrip("/").split("/"))


def _body(keys: Any, values: Mapping[str, Any]) -> Dict[str, Any]:
    return {k: values[k] for k in keys if values.get(k) is not None}


def _idem(key: Optional[str], ext: Optional[RequestExtensions]) -> Optional[Dict[str, Any]]:
    if not key:
        return dict(ext) if ext else None
    merged: Dict[str, Any] = dict(ext or {})
    merged["headers"] = {**dict(merged.get("headers") or {}), "Idempotency-Key": key}
    return merged


def _exec_timeout(timeout_seconds: Optional[int]) -> float:
    return float((timeout_seconds or 120) + 60)


def sandbox_pty_url(base_url: str, sandbox_id: str, cols: Optional[int] = None, rows: Optional[int] = None) -> str:
    """``wss://…/v1/sandboxes/{id}/pty?cols=&rows=`` (``http`` → ``ws``); ``cols`` / ``rows`` 1–1000."""
    ws_base = base_url.rstrip("/")
    if ws_base.startswith("http"):
        ws_base = "ws" + ws_base[len("http") :]
    query: Dict[str, int] = {}
    for key, value in (("cols", cols), ("rows", rows)):
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 1000:
            raise ValueError(f"sandboxes.pty_url: {key} must be an integer in 1..1000")
        query[key] = value
    url = f"{ws_base}{_base(sandbox_id, '/pty')}"
    return f"{url}?{urllib.parse.urlencode(query)}" if query else url


class SandboxFile:
    """A downloaded workspace file: raw ``data`` plus the server's ``sha256`` (``x-sha256``)."""

    __slots__ = ("data", "sha256", "content_type")

    def __init__(self, data: bytes, sha256: Optional[str], content_type: Optional[str]) -> None:
        self.data = data
        self.sha256 = sha256
        self.content_type = content_type

    def __repr__(self) -> str:  # pragma: no cover
        return f"SandboxFile(bytes={len(self.data)}, sha256={self.sha256!r})"


class SandboxFiles(Resource):
    def put(
        self,
        sandbox_id: str,
        path: str,
        content: Union[bytes, str],
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PUT /v1/sandboxes/{id}/files/{path}`` — write raw bytes (≤ 100 MB) to ``/workspace/<path>``.

        Returns ``{path, bytes, sha256, generation}``.
        """
        data = content.encode("utf-8") if isinstance(content, str) else bytes(content)
        return self._json(
            _base(sandbox_id, f"/files/{_file_path(path)}"),
            ext=ext,
            method="PUT",
            raw_body=data,
            content_type="application/octet-stream",
        )

    def get(self, sandbox_id: str, path: str, ext: Optional[RequestExtensions] = None) -> SandboxFile:
        """``GET /v1/sandboxes/{id}/files/{path}`` — raw bytes of ``/workspace/<path>``."""
        res = self._http.request(_base(sandbox_id, f"/files/{_file_path(path)}"), ext=ext)
        return SandboxFile(res.data, res.header("x-sha256"), res.header("content-type"))

    def list(
        self, sandbox_id: str, path: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/sandboxes/{id}/files?path=`` — ``{"entries": [{path, bytes, type, mtime}]}``."""
        return self._json(_base(sandbox_id, "/files"), ext=ext, query={"path": path})


class Sandboxes(Resource):
    def __init__(self, http: Any) -> None:
        super().__init__(http)
        self.files = SandboxFiles(http)

    def create(
        self,
        template: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        egress: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, str]] = None,
        backend: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/sandboxes`` — start a sandbox.

        ``ttl_seconds`` default 3600, at most 86400 on v1 and 604800 on v2. ``egress`` (both backends):
        ``{"mode": "none"}`` (default), ``{"mode": "allowlist", "domains": [...]}`` (≤ 20) or
        ``{"mode": "preset", "preset": "pypi" | "npm"}``.
        ``backend`` defaults to ``"v2"``: a long-lived pod with memory snapshots and Node 24 + npm; its
        ``template`` is ``codai-base``, ``brivio-acte`` or ``desktop`` and the reply may carry ``restored``.
        When ``backend`` is omitted and v2 is unavailable for the key the gateway falls back to ``"v1"``
        (check ``backend`` on the reply). Errors: 429 ``sandbox_concurrency_limit`` (3 per key, 5 running v2
        per user), 503 ``sandbox_capacity`` (retry).
        """
        body = _body(
            _CREATE_KEYS,
            {
                "backend": backend,
                "template": template,
                "ttl_seconds": ttl_seconds,
                "egress": egress,
                "metadata": metadata,
            },
        )
        return self._json("/v1/sandboxes", ext=ext, method="POST", body=body)

    def list(self, status: Optional[str] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/sandboxes`` — ``{"data": [...]}``, newest first; optional ``status``."""
        return self._json("/v1/sandboxes", ext=ext, query={"status": status})

    def retrieve(self, sandbox_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/sandboxes/{id}``"""
        return self._json(_base(sandbox_id), ext=ext)

    def exec(
        self,
        sandbox_id: str,
        cmd: Optional[List[str]] = None,
        shell: Optional[str] = None,
        language: Optional[str] = None,
        code: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        stdin: Optional[str] = None,
        inputs: Optional[List[Dict[str, Any]]] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/sandboxes/{id}/exec`` — run one command (``cmd`` argv, ``shell`` line, or
        ``language`` + ``code``) and wait (≤ 900 s). Returns ``{exit_code, stdout, stderr, timed_out,
        duration_ms, receipt}``. Use :meth:`exec_stream` for live output."""
        body = _body(_EXEC_KEYS, locals())
        return self._json(
            _base(sandbox_id, "/exec"),
            ext=_idem(idempotency_key, ext),
            method="POST",
            body=body,
            timeout=_exec_timeout(timeout_seconds),
            no_retry=not idempotency_key,
        )

    def exec_stream(
        self,
        sandbox_id: str,
        cmd: Optional[List[str]] = None,
        shell: Optional[str] = None,
        language: Optional[str] = None,
        code: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        stdin: Optional[str] = None,
        inputs: Optional[List[Dict[str, Any]]] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Iterator[Dict[str, Any]]:
        """``POST /v1/sandboxes/{id}/exec`` with ``Accept: text/event-stream`` — yields event dicts
        (``start``, ``stdout``, ``stderr``, ``truncated``, then ``exit`` or ``error``)."""
        body = _body(_EXEC_KEYS, locals())
        merged: Dict[str, Any] = dict(_idem(idempotency_key, ext) or {})
        merged["headers"] = {**dict(merged.get("headers") or {}), "Accept": "text/event-stream"}
        for frame in self._http.sse(_base(sandbox_id, "/exec"), method="POST", body=body, ext=merged):
            event = frame_json(frame)
            if not isinstance(event, dict) or "type" not in event:
                continue
            yield event
            if event["type"] in ("exit", "error"):
                return

    def artifacts(self, sandbox_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/sandboxes/{id}/artifacts`` — ``{"data": [...]}`` from ``/workspace/out``
        (ClamAV-scanned, SHA-256, signed ``url`` valid 1 h; ``None`` unless ``scan == "clean"``)."""
        return self._json(_base(sandbox_id, "/artifacts"), ext=ext)

    def snapshot(
        self, sandbox_id: str, name: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/sandboxes/{id}/snapshot`` (v1 only; v2 answers 409 ``not_supported_on_v2``) —
        ``{object, bytes, sha256}``."""
        body: Dict[str, Any] = {"name": name} if name is not None else {}
        return self._json(_base(sandbox_id, "/snapshot"), ext=ext, method="POST", body=body)

    def run_code(
        self,
        sandbox_id: str,
        code: str,
        timeout_seconds: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/sandboxes/{id}/run_code`` (v2) — run Python in the persistent kernel (globals survive
        between calls, pause/resume and forks). Returns ``{stdout, stderr, result, error, duration_ms,
        execution_count, kernel_restarted}``."""
        body = _body(("code", "timeout_seconds"), {"code": code, "timeout_seconds": timeout_seconds})
        return self._json(
            _base(sandbox_id, "/run_code"),
            ext=ext,
            method="POST",
            body=body,
            timeout=_exec_timeout(timeout_seconds),
            no_retry=True,
        )

    def reset_kernel(self, sandbox_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``POST /v1/sandboxes/{id}/kernel/reset`` (v2) — restart the kernel; globals are lost, files kept."""
        self._json(_base(sandbox_id, "/kernel/reset"), ext=ext, method="POST")

    def pause(self, sandbox_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/sandboxes/{id}/pause`` (v2) — memory snapshot, then stop the pod (status ``paused``).
        At most 10 paused v2 sandboxes per user (429 ``sandbox_paused_limit``)."""
        return self._json(
            _base(sandbox_id, "/pause"), ext=ext, method="POST", timeout=_LIFECYCLE_TIMEOUT, no_retry=True
        )

    def resume(self, sandbox_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/sandboxes/{id}/resume`` (v2) — restore a paused sandbox. The sandbox plus
        ``restored`` (``False`` = cold start) and ``ready_ms``."""
        return self._json(
            _base(sandbox_id, "/resume"), ext=ext, method="POST", timeout=_LIFECYCLE_TIMEOUT, no_retry=True
        )

    def fork(
        self,
        sandbox_id: str,
        count: int,
        ttl_seconds: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/sandboxes/{id}/fork`` (v2) — start 1–5 copies of a running sandbox from a memory
        snapshot. ``{"object": "list", "parent_id", "data": [{id, restored, ready_ms, error?}]}``."""
        body = _body(("count", "ttl_seconds"), {"count": count, "ttl_seconds": ttl_seconds})
        return self._json(
            _base(sandbox_id, "/fork"),
            ext=ext,
            method="POST",
            body=body,
            timeout=_LIFECYCLE_TIMEOUT,
            no_retry=True,
        )

    def preview(
        self,
        sandbox_id: str,
        port: int,
        ttl_seconds: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/sandboxes/{id}/preview`` (v2) — signed HTTPS URL on ``*.sbx.codai.ro`` for ``port``
        (1024–65535, not 8080), valid ``ttl_seconds`` (60–3600, default 900). ``{port, url, expires_at}``."""
        body = _body(("port", "ttl_seconds"), {"port": port, "ttl_seconds": ttl_seconds})
        return self._json(_base(sandbox_id, "/preview"), ext=ext, method="POST", body=body)

    def delete(self, sandbox_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/sandboxes/{id}`` — destroy the sandbox and its workspace (204)."""
        self._http.request(_base(sandbox_id), ext=ext, method="DELETE")

    def pty_url(self, sandbox_id: str, cols: Optional[int] = None, rows: Optional[int] = None) -> str:
        """URL of ``GET /v1/sandboxes/{id}/pty`` — an interactive shell under a real pty over WebSocket (counts
        as the sandbox's one running exec; idle 15 min, max 60 min, billed as exec seconds).

        Send ``Authorization: Bearer <key>`` on the upgrade (keys in the query string are refused), e.g. with
        ``websockets``: ``websockets.connect(url, additional_headers={"Authorization": f"Bearer {key}"})``.
        Frames: binary ``[0x01][u32 0][bytes]`` DATA both ways, ``[0x02][u32 0][cols u16 BE][rows u16 BE]``
        RESIZE (client → sandbox); text ``{"t": "exit", "code", "reason"}`` / ``{"t": "error", "code",
        "message"}``. Refusals close with ``4000 + HTTP status``, backend failures with 1011."""
        return sandbox_pty_url(self._http.base_url, sandbox_id, cols=cols, rows=rows)

    def run(
        self,
        cmd: Optional[List[str]] = None,
        shell: Optional[str] = None,
        language: Optional[str] = None,
        code: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        stdin: Optional[str] = None,
        inputs: Optional[List[Dict[str, Any]]] = None,
        template: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        egress: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/sandboxes/run`` — one shot: create, write ``inputs`` under ``/workspace/in``, run,
        collect artifacts, destroy. Returns the exec result with ``artifacts``."""
        values = locals()
        body = {**_body(_CREATE_KEYS, values), **_body(_EXEC_KEYS, values)}
        return self._json(
            "/v1/sandboxes/run",
            ext=_idem(idempotency_key, ext),
            method="POST",
            body=body,
            timeout=_exec_timeout(timeout_seconds),
            no_retry=not idempotency_key,
        )
