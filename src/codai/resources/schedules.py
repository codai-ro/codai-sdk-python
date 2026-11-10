"""codai Scheduler (ADR 0006): ``/v1/schedules/*``, ``/v1/schedule-runs/*``, ``/v1/scheduler/*``."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

from .._http import HttpClient, RequestExtensions, frame_json
from ._base import Resource, enc, list_of

__all__ = ["Schedules", "SchedulerHosts", "ScheduleExecutor", "Heartbeats"]


def _schedule(schedule_id: str, suffix: str = "") -> str:
    return f"/v1/schedules/{enc(schedule_id)}{suffix}"


def _run(run_id: str, suffix: str) -> str:
    return f"/v1/schedule-runs/{enc(run_id)}{suffix}"


class SchedulerHosts(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/scheduler/hosts`` — your devices as hosts (os, kind, tags, online)."""
        return list_of(self._json("/v1/scheduler/hosts", ext=ext), "hosts")

    def update(self, host_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/scheduler/hosts/{id}`` — ``name``, ``tags``, ``host_kind``, ``os``, ``arch``."""
        return self._json(f"/v1/scheduler/hosts/{enc(host_id)}", ext=ext, method="PATCH", body=body)


class ScheduleExecutor(Resource):
    """Host-side protocol (needs the ``device`` client option): claim → heartbeat → result."""

    def claim(self, ext: Optional[RequestExtensions] = None) -> Optional[Dict[str, Any]]:
        """``POST /v1/scheduler/claim`` — the next run for this device, or ``None`` (204). Lease 60 s."""
        res = self._http.request("/v1/scheduler/claim", ext=ext, method="POST", body={}, no_retry=True)
        return None if res.status == 204 else res.json()

    def heartbeat(
        self, run_id: str, attempt: int, log: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> None:
        """``POST /v1/schedule-runs/{id}/heartbeat`` — extend the lease; raises 409 when it was lost."""
        body: Dict[str, Any] = {"attempt": attempt}
        if log is not None:
            body["log"] = log
        self._http.request(_run(run_id, "/heartbeat"), ext=ext, method="POST", body=body, no_retry=True)

    def result(self, run_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/schedule-runs/{id}/result`` — ``{"attempt", "ok", "exit_code"?, "error"?, "log_tail"?, ...}``."""
        return self._json(_run(run_id, "/result"), ext=ext, method="POST", body=body, no_retry=True)

    def approve_command(
        self, schedule_id: str, command_hash: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/schedules/{id}/approve-command`` — this host approves the exact shell command hash."""
        return self._json(
            _schedule(schedule_id, "/approve-command"), ext=ext, method="POST", body={"command_hash": command_hash}
        )


class Heartbeats(Resource):
    """Dead-man switches for jobs codai does not run: the job calls ``ping_url`` (``/start``, ``/fail``, ``/<exit>``)."""

    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/heartbeats``."""
        return list_of(self._json("/v1/heartbeats", ext=ext), "heartbeats")

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/heartbeats`` — ``{"name", "period_s", "grace_s"?}``; the reply carries ``ping_url`` once."""
        return self._json("/v1/heartbeats", ext=ext, method="POST", body=body)

    def update(self, monitor_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/heartbeats/{id}`` — ``name``, ``period_s``, ``grace_s``, ``paused``."""
        return self._json(f"/v1/heartbeats/{enc(monitor_id)}", ext=ext, method="PATCH", body=body)

    def delete(self, monitor_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/heartbeats/{id}``."""
        self._http.request(f"/v1/heartbeats/{enc(monitor_id)}", ext=ext, method="DELETE")


class Schedules(Resource):
    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)
        self.hosts = SchedulerHosts(http)
        self.executor = ScheduleExecutor(http)

    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/schedules``."""
        return list_of(self._json("/v1/schedules", ext=ext), "schedules")

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/schedules`` — ``{"name", "kind", "spec", "trigger", "target"?, "policy"?, ...}``."""
        return self._json("/v1/schedules", ext=ext, method="POST", body=body)

    def preview(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/schedules/preview`` — ``{"text"}`` (RO/EN) or ``{"trigger"}`` → next runs + DST warning."""
        return self._json("/v1/schedules/preview", ext=ext, method="POST", body=body)

    def get(self, schedule_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/schedules/{id}``."""
        return self._json(_schedule(schedule_id), ext=ext)

    def update(self, schedule_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/schedules/{id}`` — a changed shell command clears every host approval."""
        return self._json(_schedule(schedule_id), ext=ext, method="PATCH", body=body)

    def delete(self, schedule_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/schedules/{id}``."""
        self._http.request(_schedule(schedule_id), ext=ext, method="DELETE")

    def run_now(self, schedule_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/schedules/{id}/run`` — ``{"queued": bool}`` (policy still applies)."""
        return self._json(_schedule(schedule_id, "/run"), ext=ext, method="POST", body={}, no_retry=True)

    def runs(self, schedule_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/schedules/{id}/runs``."""
        return list_of(self._json(_schedule(schedule_id, "/runs"), ext=ext), "runs")

    def recent_runs(self, limit: int = 50, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/schedule-runs?limit=``."""
        return list_of(self._json("/v1/schedule-runs", ext=ext, query={"limit": limit}), "runs")

    def decide(self, run_id: str, approve: bool, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/schedule-runs/{id}/decision`` — approve or skip a run waiting for you."""
        return self._json(_run(run_id, "/decision"), ext=ext, method="POST", body={"approve": approve})

    def pause(
        self, until: Optional[str] = None, resume_policy: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/schedules/pause`` — vacation mode until ``until`` (or until resumed)."""
        body: Dict[str, Any] = {}
        if until is not None:
            body["until"] = until
        if resume_policy is not None:
            body["resume_policy"] = resume_policy
        return self._json("/v1/schedules/pause", ext=ext, method="POST", body=body)

    def resume(self, backfill: Optional[bool] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/schedules/resume`` — ``backfill=True`` runs each missed schedule once."""
        return self._json("/v1/schedules/resume", ext=ext, method="POST", body={} if backfill is None else {"backfill": backfill})

    def audit(
        self, schedule_id: Optional[str] = None, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None
    ) -> List[Dict[str, Any]]:
        """``GET /v1/schedules/audit`` — append-only scheduler history, newest first (optionally one schedule)."""
        query = {"schedule_id": schedule_id, "limit": limit}
        return list_of(self._json("/v1/schedules/audit", ext=ext, query=query), "audit")

    def templates(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/schedules/templates``."""
        return self._json("/v1/schedules/templates", ext=ext)

    def render_template(
        self, template: str, params: Optional[Dict[str, Any]] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/schedules/templates`` — canonical prompt + draft create body (no write)."""
        return self._json("/v1/schedules/templates", ext=ext, method="POST", body={"template": template, "params": params or {}})

    def stream(self, ext: Optional[RequestExtensions] = None) -> Iterator[Dict[str, Any]]:
        """``GET /v1/schedules/stream`` — yields ``{"op", "id", "schedule_id"?, "state"?, "device_id"?}``."""
        for frame in self._http.sse("/v1/schedules/stream", ext=ext):
            if frame.event != "schedule":
                continue
            data = frame_json(frame)
            if isinstance(data, dict):
                yield data
