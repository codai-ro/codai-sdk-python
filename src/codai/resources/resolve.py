"""codai Resolve — execution-verified bug fixes, no fix no fee.

Separate service (``https://resolve.codai.ro``, spec ``apps/docs/openapi/en/resolve.yaml``)
with a flat ``{"error": ...}`` body, so it runs on its own ``HttpClient`` and maps
failures to ``ResolveError`` / ``ResolveInsufficientFundsError``. Mirrors
``packages/sdk/src/resources/resolve.ts``.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import time
from typing import Any, Callable, Dict, Iterable, Optional, Union, cast

from .._http import CodaiError, HttpClient
from .._resolve_types import (
    ResolveAccepted,
    ResolveAttestation,
    ResolveHealth,
    ResolveIntake,
    ResolveJob,
)
from ._base import enc

__all__ = [
    "RESOLVE_TERMINAL_STATUSES",
    "Resolve",
    "ResolveError",
    "ResolveInsufficientFundsError",
    "verify_resolve_webhook",
]

RESOLVE_TERMINAL_STATUSES = frozenset({"resolved", "failed", "declined", "error"})
_ATTESTATION_PREFIX = re.compile(r"^.*/v1/resolve/attestations/")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def verify_resolve_webhook(
    secret: str,
    raw_body: Union[bytes, str],
    signature_header: Optional[str],
    tolerance_seconds: int = 300,
    now: Optional[float] = None,
) -> bool:
    """Verify a Resolve webhook delivery.

    ``x-codai-signature: t=<unix>,v1=<hex>`` with
    ``v1 = HMAC-SHA256(callback_secret, "<t>.<raw body>")``. Pass the RAW request body
    (before JSON parsing). Constant-time compare (``hmac.compare_digest``); a timestamp
    more than ``tolerance_seconds`` away from ``now`` (default: wall clock) is rejected.
    Returns ``False`` for any bad input, never raises.
    """
    if not secret or not signature_header:
        return False
    t: Optional[str] = None
    sigs: list[str] = []
    for part in signature_header.split(","):
        k, sep, v = part.partition("=")
        if not sep:
            continue
        k, v = k.strip(), v.strip()
        if k == "t":
            t = v
        elif k == "v1":
            sigs.append(v.lower())
    if not t or not t.isdigit() or not sigs:
        return False
    current = time.time() if now is None else now
    if abs(current - int(t)) > tolerance_seconds:
        return False
    body = raw_body.encode("utf-8") if isinstance(raw_body, str) else bytes(raw_body)
    expected = hmac.new(secret.encode("utf-8"), t.encode("ascii") + b"." + body, hashlib.sha256).hexdigest()
    return any(_HEX64.match(s) is not None and hmac.compare_digest(s, expected) for s in sigs)


class ResolveError(CodaiError):
    """Any non-2xx answer from the Resolve service. ``detail`` is the body's ``error``
    field: a message, or Zod ``flatten()`` details on a 400."""

    def __init__(self, message: str, status: int, body: Any, request_id: Optional[str] = None,
                 retry_after: Optional[int] = None) -> None:
        super().__init__(message, status, body, code=_code(body), request_id=request_id, retry_after=retry_after)
        err = body.get("error") if isinstance(body, dict) else None
        self.detail: Any = err if isinstance(err, (str, dict)) else None


class ResolveInsufficientFundsError(ResolveError):
    """``402`` on ``accept()`` — the wallet cannot hold the quote; the job stays ``quoted``.
    Open ``topup_url`` (pay.codai.ro checkout for the shortfall), then retry ``accept()``."""

    def __init__(self, message: str, body: Dict[str, Any], request_id: Optional[str] = None) -> None:
        super().__init__(message, 402, body, request_id=request_id)
        self.balance: int = int(body["balance"])
        self.required: int = int(body["required"])
        self.currency: str = str(body["currency"])
        self.topup_url: str = str(body["topup_url"])


def _code(body: Any) -> Optional[str]:
    err = body.get("error") if isinstance(body, dict) else None
    return err if isinstance(err, str) else None


def _to_resolve_error(path: str, err: CodaiError) -> CodaiError:
    if isinstance(err, ResolveError) or err.status == 0:
        return err
    body = err.body
    if (
        err.status == 402
        and isinstance(body, dict)
        and body.get("error") == "insufficient_funds"
        and isinstance(body.get("topup_url"), str)
    ):
        return ResolveInsufficientFundsError(
            f"codai-resolve {path} → 402: insufficient funds (balance {body.get('balance')}, "
            f"required {body.get('required')} {body.get('currency')}); top up at {body['topup_url']}",
            body,
            request_id=err.request_id,
        )
    detail = _code(body) or "request failed"
    return ResolveError(
        f"codai-resolve {path} → {err.status}: {detail}", err.status, body,
        request_id=err.request_id, retry_after=err.retry_after,
    )


class Resolve:
    """``client.resolve`` — submit, accept, poll and verify Resolve jobs."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def _call(self, path: str, **kwargs: Any) -> Any:
        try:
            return self._http.json(path, **kwargs)
        except CodaiError as e:
            raise _to_resolve_error(path, e) from e

    def submit(self, body: ResolveIntake) -> Dict[str, Any]:
        """``POST /v1/resolve/jobs`` — returns a quote (``status: quoted``), a free-tier
        auto-accept (``accepted``) or a decline (``declined``). Never retried."""
        if not body.get("issue_url") and not body.get("issue_text"):
            raise TypeError("resolve.submit: one of issue_url or issue_text is required")
        return cast(Dict[str, Any], self._call("/v1/resolve/jobs", method="POST", body=dict(body), no_retry=True))

    def get(self, job_id: str) -> ResolveJob:
        """``GET /v1/resolve/jobs/{id}`` — status, quote, reasons, cost, attestation pointer."""
        return cast(ResolveJob, self._call(f"/v1/resolve/jobs/{enc(job_id)}"))

    def accept(self, job_id: str) -> ResolveAccepted:
        """``POST /v1/resolve/jobs/{id}/accept`` — holds the quote on the wallet and starts
        the job. Raises ``ResolveInsufficientFundsError`` (402) or ``ResolveError`` 409."""
        return cast(
            ResolveAccepted,
            self._call(f"/v1/resolve/jobs/{enc(job_id)}/accept", method="POST", raw_body=b"", no_retry=True),
        )

    def attestation(self, id_or_url: str) -> ResolveAttestation:
        """``GET /v1/resolve/attestations/{id}`` — accepts the id or the job's ``attestation_url``."""
        att_id = _ATTESTATION_PREFIX.sub("", id_or_url)
        return cast(ResolveAttestation, self._call(f"/v1/resolve/attestations/{enc(att_id)}"))

    def health(self) -> ResolveHealth:
        """``GET /health`` — liveness of the Resolve service."""
        return cast(ResolveHealth, self._call("/health"))

    def wait_for(
        self,
        job_id: str,
        interval: float = 5.0,
        timeout: float = 1800.0,
        until: Optional[Iterable[str]] = None,
        on_poll: Optional[Callable[[ResolveJob], None]] = None,
    ) -> ResolveJob:
        """Poll ``get()`` until a terminal status (or one of ``until``). A ``quoted`` job
        does not move until you ``accept()`` it. Raises ``ResolveError`` (status 0) on timeout."""
        stop = frozenset(until) if until is not None else RESOLVE_TERMINAL_STATUSES
        deadline = time.monotonic() + timeout
        while True:
            job = self.get(job_id)
            if on_poll is not None:
                on_poll(job)
            if job["status"] in stop:
                return job
            left = deadline - time.monotonic()
            if left <= 0:
                raise ResolveError(f"codai-resolve job {job_id} still {job['status']} after {timeout}s", 0, job)
            time.sleep(min(interval, left))
