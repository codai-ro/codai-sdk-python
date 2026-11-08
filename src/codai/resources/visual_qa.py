"""``/v1/vqa/*`` — Visual QA (operator-only: every call needs a key whose owner is ``super_admin``, 403 otherwise).

References: a finding is ``UI-<n>`` (the bare number also works), a screen is ``SCR-<surface>-<route-slug>``.
Agent workflow: ``findings(status="todo")`` -> ``claim("UI-142")`` -> fix -> ``resolve("UI-142", "fixed",
fix_ref="<sha>")`` -> ``recapture(["SCR-hub-ops-agentq"], finding="UI-142")``. ``verified`` is never set by a call:
a clean re-capture sets it asynchronously. Baseline approval is hub-only and not part of this API.

``open_run`` / ``record_captures`` / ``finish_run`` / ``claim_recaptures`` / ``finish_recapture`` are for the
capture runner.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Union

from .._http import RequestExtensions
from ._base import Resource, enc

__all__ = ["VisualQa"]

Ref = Union[str, int]


def _ref(value: Ref) -> str:
    s = str(value).strip()
    return enc(s.upper() if s.lower().startswith("ui-") else f"UI-{s}")


def _csv(value: Union[str, Iterable[str], None]) -> Optional[str]:
    if value is None or isinstance(value, str):
        return value or None
    return ",".join(str(v) for v in value) or None


class VisualQa(Resource):
    """Visual QA findings, re-captures and capture-runner calls."""

    def findings(
        self,
        status: Union[str, Iterable[str], None] = None,
        severity: Union[str, Iterable[str], None] = None,
        surface: Optional[str] = None,
        screen: Optional[str] = None,
        run: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/vqa/findings`` — each item has ``ref`` (``UI-<n>``) and ``atlasUrl``."""
        query = {
            "status": _csv(status),
            "severity": _csv(severity),
            "surface": surface,
            "screen": screen,
            "run": run,
            "limit": limit,
        }
        return self._json("/v1/vqa/findings", ext=ext, query=query) or {}

    def finding(self, ref: Ref, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vqa/findings/{ref}`` — finding, comments and the capture that last reported it."""
        return self._json(f"/v1/vqa/findings/{_ref(ref)}", ext=ext) or {}

    def claim(self, ref: Ref, agent: Optional[str] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vqa/findings/{ref}/claim`` — ``in-progress`` as ``agent``; 409 when not claimable."""
        body = {"agent": agent} if agent else {}
        return self._json(f"/v1/vqa/findings/{_ref(ref)}/claim", ext=ext, method="POST", body=body) or {}

    def resolve(
        self,
        ref: Ref,
        status: str,
        fix_ref: Optional[str] = None,
        note: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vqa/findings/{ref}/resolve`` — ``status`` is ``fixed`` | ``wontfix`` | ``todo``; 409 on a bad
        transition."""
        body: Dict[str, Any] = {"status": status}
        if fix_ref:
            body["fixRef"] = fix_ref
        if note:
            body["note"] = note
        return self._json(f"/v1/vqa/findings/{_ref(ref)}/resolve", ext=ext, method="POST", body=body) or {}

    def comment(self, ref: Ref, body: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vqa/findings/{ref}/comments``."""
        return self._json(f"/v1/vqa/findings/{_ref(ref)}/comments", ext=ext, method="POST", body={"body": body}) or {}

    def recapture(
        self, screens: Iterable[str], finding: Optional[Ref] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/vqa/recaptures`` -> ``{"id", "state": "queued"}``. Asynchronous; a ``fixed`` finding on those
        screens flips to ``verified`` when the fresh capture no longer reports it."""
        body: Dict[str, Any] = {"screens": list(screens)}
        if finding is not None:
            body["finding"] = str(finding)
        return self._json("/v1/vqa/recaptures", ext=ext, method="POST", body=body) or {}

    def summary(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vqa/summary`` — finding counts and the latest run."""
        return self._json("/v1/vqa/summary", ext=ext) or {}

    def runs(self, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vqa/runs``."""
        return self._json("/v1/vqa/runs", ext=ext, query={"limit": limit}) or {}

    def run(self, run_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vqa/runs/{id}`` — run and finding counts."""
        return self._json(f"/v1/vqa/runs/{enc(run_id)}", ext=ext) or {}

    def captures(
        self,
        run: Optional[str] = None,
        surface: Optional[str] = None,
        config: Optional[str] = None,
        screen: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/vqa/captures`` — latest capture per screen/config/state, or every capture of ``run``."""
        query = {"run": run, "surface": surface, "config": config, "screen": screen, "limit": limit}
        return self._json("/v1/vqa/captures", ext=ext, query=query) or {}

    def baselines(
        self, screens: Union[str, Iterable[str], None] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``GET /v1/vqa/baselines`` — approved baselines (approval itself is hub-only)."""
        return self._json("/v1/vqa/baselines", ext=ext, query={"screens": _csv(screens)}) or {}

    # ── capture runner ────────────────────────────────────────────────────

    def open_run(self, run: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vqa/runs`` — idempotent on ``id``."""
        return self._json("/v1/vqa/runs", ext=ext, method="POST", body=run) or {}

    def record_captures(
        self, run_id: str, captures: List[Dict[str, Any]], ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/vqa/runs/{id}/captures`` — at most 50 captures per call."""
        return (
            self._json(f"/v1/vqa/runs/{enc(run_id)}/captures", ext=ext, method="POST", body={"captures": captures})
            or {}
        )

    def finish_run(self, run_id: str, finish: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vqa/runs/{id}/finish``."""
        return self._json(f"/v1/vqa/runs/{enc(run_id)}/finish", ext=ext, method="POST", body=finish) or {}

    def claim_recaptures(self, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vqa/recaptures/claim`` — atomically claim queued re-captures."""
        return self._json("/v1/vqa/recaptures/claim", ext=ext, query={"limit": limit}) or {}

    def finish_recapture(
        self, recapture_id: int, run_id: Optional[str], ok: bool, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/vqa/recaptures/{id}/finish``."""
        body = {"runId": run_id, "ok": ok}
        return self._json(f"/v1/vqa/recaptures/{int(recapture_id)}/finish", ext=ext, method="POST", body=body) or {}
