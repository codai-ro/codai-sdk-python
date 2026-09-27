"""codai Resolve — execution-verified bug fixes, no fix no fee.

Separate service (``https://resolve.codai.ro``, spec ``apps/docs/openapi/en/resolve.yaml``)
with a flat ``{"error": ...}`` body, so it runs on its own ``HttpClient`` and maps
failures to ``ResolveError`` / ``ResolveInsufficientFundsError``. Mirrors
``packages/sdk/src/resources/resolve.ts``.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
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
    ResolveKeys,
)
from ._base import enc

__all__ = [
    "RESOLVE_ATTESTATION_PAYLOAD_TYPE",
    "RESOLVE_TERMINAL_STATUSES",
    "Resolve",
    "ResolveError",
    "ResolveInsufficientFundsError",
    "attestation_statement",
    "verify_attestation_with_keys",
    "verify_resolve_webhook",
]

RESOLVE_TERMINAL_STATUSES = frozenset({"resolved", "failed", "declined", "error"})
RESOLVE_ATTESTATION_PAYLOAD_TYPE = "application/vnd.codai.resolve.attestation+json;v=1"
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


def _sha256(s: Optional[str]) -> Optional[str]:
    return None if s is None else hashlib.sha256(s.encode("utf-8")).hexdigest()


def _canonical(v: Any) -> str:
    # JCS for the statement's JSON subset (ASCII keys, strings/null/objects).
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _pae(payload_type: str, body: bytes) -> bytes:
    """DSSE v1 PAE: ``"DSSEv1" SP len(type) SP type SP len(body) SP body`` (byte lengths)."""
    t = payload_type.encode("utf-8")
    return b"DSSEv1 %d %s %d " % (len(t), t, len(body)) + body


def attestation_statement(att: ResolveAttestation) -> Dict[str, Any]:
    """The statement the Resolve service signs, recomputed from the attestation JSON."""
    rt = att.get("repro_test")
    return {
        "kind": "codai.resolve.attestation.v1",
        "attestation_id": att["id"],
        "repo_url": att["repo_url"],
        "base_commit": att["base_commit"],
        "patch_sha256": _sha256(att["patch"]),
        "repro_test": {"path": rt["path"], "sha256": _sha256(rt.get("content"))} if rt and rt.get("path") else None,
        "test_command": att["test_command"],
        "regression_command": att.get("regression_command"),
        "test_output_before_sha256": _sha256(att["test_output_before"]),
        "test_output_after_sha256": _sha256(att["test_output_after"]),
        "regression_output_sha256": _sha256(att.get("regression_output")),
        "runner_image_digest": att["runner_image_digest"],
        "started_at": att["started_at"],
        "verified_at": att["verified_at"],
    }


def verify_attestation_with_keys(att: ResolveAttestation, keys: ResolveKeys) -> Dict[str, Any]:
    """Verify a signed attestation offline against published keys.

    Returns ``{"ok": True, "keyid": ...}`` or ``{"ok": False, "reason": R}`` with R one of
    ``UNSIGNED`` (``signature`` is null — pre-2026-09-27), ``BAD_PAYLOAD_TYPE``,
    ``STATEMENT_MISMATCH`` (the signed statement differs from these fields) or
    ``BAD_SIGNATURE``. The statement check is pure stdlib and runs first; the ECDSA
    P-256/SHA-256 check needs the ``cryptography`` package and raises ``ImportError``
    when it is missing (the SDK itself is dependency-free).
    """
    env = att.get("signature")
    if not env or not env.get("signatures"):
        return {"ok": False, "reason": "UNSIGNED"}
    if env.get("payloadType") != RESOLVE_ATTESTATION_PAYLOAD_TYPE:
        return {"ok": False, "reason": "BAD_PAYLOAD_TYPE"}
    try:
        body = base64.b64decode(env["payload"], validate=True)
        signed = json.loads(body.decode("utf-8"))
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return {"ok": False, "reason": "STATEMENT_MISMATCH"}
    if _canonical(signed) != _canonical(attestation_statement(att)):
        return {"ok": False, "reason": "STATEMENT_MISMATCH"}

    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
    except ImportError as e:  # pragma: no cover - exercised only without cryptography
        raise ImportError(
            "codai: verifying attestation signatures needs the 'cryptography' package "
            "(pip install cryptography); the statement check passed"
        ) from e

    msg = _pae(env["payloadType"], body)
    for s in env["signatures"]:
        try:
            sig = base64.b64decode(s["sig"], validate=True)
        except (binascii.Error, ValueError, KeyError):
            continue
        for k in keys.get("keys", []):
            if k.get("payload_type") and k["payload_type"] != env["payloadType"]:
                continue
            try:
                pub = serialization.load_pem_public_key(k["public_key_pem"].encode("ascii"))
                if not isinstance(pub, ec.EllipticCurvePublicKey):
                    continue
                pub.verify(sig, msg, ec.ECDSA(hashes.SHA256()))
                return {"ok": True, "keyid": k["keyid"]}
            except (InvalidSignature, ValueError, TypeError):
                continue
    return {"ok": False, "reason": "BAD_SIGNATURE"}


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

    def keys(self) -> ResolveKeys:
        """``GET /v1/resolve/keys`` — public keys that sign attestations."""
        return cast(ResolveKeys, self._call("/v1/resolve/keys"))

    def verify_attestation(self, att: ResolveAttestation, keys: Optional[ResolveKeys] = None) -> Dict[str, Any]:
        """Verify ``att.signature`` and that the signed statement matches ``att``.
        Fetches ``keys()`` unless ``keys`` is given (pin them to avoid trusting the network).
        See ``verify_attestation_with_keys`` for results; needs ``cryptography`` for the
        signature step."""
        if not att.get("signature"):
            return {"ok": False, "reason": "UNSIGNED"}
        return verify_attestation_with_keys(att, keys if keys is not None else self.keys())

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
