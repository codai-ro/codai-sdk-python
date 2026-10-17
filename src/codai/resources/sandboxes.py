"""``/v1/sandboxes`` — agent sandboxes (beta): isolated gVisor containers with a persistent ``/workspace``,
no network by default, artifacts from ``/workspace/out`` as scanned, signed links."""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict, Iterator, List, Mapping, Optional, Union

from .._http import RequestExtensions, frame_json
from ._base import Resource, enc

__all__ = ["Sandboxes", "SandboxFiles", "SandboxFile"]

_EXEC_KEYS = ("cmd", "shell", "language", "code", "env", "cwd", "timeout_seconds", "stdin", "inputs")
_CREATE_KEYS = ("template", "ttl_seconds", "egress", "metadata")


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
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/sandboxes`` — start a sandbox.

        ``ttl_seconds`` 60–86400 (default 3600). ``egress``: ``{"mode": "none"}`` (default),
        ``{"mode": "allowlist", "domains": [...]}`` (≤ 20) or ``{"mode": "preset", "preset": "pypi" | "npm"}``.
        """
        body = _body(_CREATE_KEYS, {"template": template, "ttl_seconds": ttl_seconds, "egress": egress, "metadata": metadata})
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
        """``POST /v1/sandboxes/{id}/snapshot`` — ``{object, bytes, sha256}``."""
        body: Dict[str, Any] = {"name": name} if name is not None else {}
        return self._json(_base(sandbox_id, "/snapshot"), ext=ext, method="POST", body=body)

    def delete(self, sandbox_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/sandboxes/{id}`` — destroy the sandbox and its workspace (204)."""
        self._http.request(_base(sandbox_id), ext=ext, method="DELETE")

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
