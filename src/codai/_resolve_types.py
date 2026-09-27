"""Typed dictionaries for the codai Resolve API.

generated — do not edit. Source: apps/docs/openapi/en/resolve.yaml.
Regenerate with ``python scripts/gen-types.py --spec resolve`` (see that script's docstring).

Every ``components.schemas`` entry is a ``TypedDict`` (``total=False`` when the
schema has optional fields; a ``_<Name>Required`` base carries the required
keys of mixed schemas). Non-object schemas (enums, unions, arrays) are type
aliases. ``<operationId>Body`` / ``<operationId>Response`` name each
operation's JSON request body and first 2xx JSON response.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

class ResolveHealth(TypedDict):
    ok: bool
    service: str


class ResolveValidationDetails(TypedDict):
    """Zod `flatten()` output returned when the intake body fails schema validation."""
    formErrors: List[str]
    fieldErrors: Dict[str, List[str]]


class ResolveError(TypedDict):
    """Flat error envelope used by every Resolve endpoint. Not the gateway `{ error: { code, message } }` shape."""
    error: Union[str, ResolveValidationDetails]


class _ResolveIntakeRequired(TypedDict):
    repo_url: str


class ResolveIntake(_ResolveIntakeRequired, total=False):
    """Body of `POST /v1/resolve/jobs`. Provide `issue_url` or `issue_text` (at least one)."""
    issue_url: str
    issue_text: str
    test_command: str
    callback_url: str


# `free` (first 3 resolves per user), `t7` ($7), `t19` ($19), `t49` ($49). Prices are in USD micros on the wire.
ResolveTier = Literal['free', 't7', 't19', 't49']


# Lifecycle: `triage → quoted → accepted → running → resolved | failed`, plus `declined`
ResolveJobStatus = Literal['triage', 'quoted', 'declined', 'accepted', 'running', 'resolved', 'failed', 'error']


class _ResolveQuoteRequired(TypedDict):
    id: str
    status: Literal['quoted', 'accepted']
    tier: ResolveTier
    quote_micro_usd: int
    triage_reason: str
    free_tier_remaining: int


class ResolveQuote(_ResolveQuoteRequired, total=False):
    """`201` body — the job was quoted (`quoted`) or auto-accepted on the free tier (`accepted`)."""
    callback_secret: str


class _ResolveDeclinedRequired(TypedDict):
    id: str
    status: str
    decline_reason: str


class ResolveDeclined(_ResolveDeclinedRequired, total=False):
    """`200` body — triage declined the issue. The job is persisted with `status: declined` and is never billed."""
    callback_secret: str


class ResolveAccepted(TypedDict):
    """Accepted"""
    id: str
    status: str


class ResolveInsufficientFunds(TypedDict):
    """`402` body of `POST /v1/resolve/jobs/{id}/accept` when the wallet cannot hold the quote."""
    error: str
    balance: int
    required: int
    currency: str
    topup_url: str


class ResolveJob(TypedDict):
    """Full job view returned by `GET /v1/resolve/jobs/{id}`. Nullable fields are `null` until the corresponding stag…"""
    id: str
    status: ResolveJobStatus
    repo_url: str
    tier: Optional[ResolveTier]
    quote_micro_usd: Optional[int]
    triage_reason: Optional[str]
    decline_reason: Optional[str]
    fail_reason: Optional[str]
    cost_micro_usd: int
    attestation_id: Optional[str]
    attestation_url: Optional[str]
    created_at: str
    completed_at: Optional[str]


class ResolveReproTest(TypedDict):
    """Repro test written by the agent when you did not supply `test_command`."""
    path: str
    content: Optional[str]


class _ResolveAttestationEnvelopeSignaturesItemRequired(TypedDict):
    sig: str


class ResolveAttestationEnvelopeSignaturesItem(_ResolveAttestationEnvelopeSignaturesItemRequired, total=False):
    keyid: str


class ResolveAttestationEnvelope(TypedDict):
    """DSSE v1 envelope. `payload` is base64 of the RFC 8785 (JCS) canonical statement JSON"""
    payloadType: str
    payload: str
    signatures: List[ResolveAttestationEnvelopeSignaturesItem]


class ResolveAttestation(TypedDict):
    """Public execution proof. Everything needed to reproduce the verification locally."""
    id: str
    kind: str
    repo_url: str
    base_commit: str
    patch: str
    repro_test: Optional[ResolveReproTest]
    test_command: str
    regression_command: Optional[str]
    test_output_before: str
    test_output_after: str
    regression_output: Optional[str]
    runner_image_digest: str
    started_at: str
    verified_at: str
    signature: Optional[ResolveAttestationEnvelope]


class ResolveKey(TypedDict):
    """Verification key"""
    keyid: str
    algorithm: str
    payload_type: str
    encoding: str
    public_key_pem: str


class ResolveKeys(TypedDict):
    """Verification keys"""
    keys: List[ResolveKey]


# `job.quoted` (paid quote ready), `job.declined` (triage refused), `job.resolved` (verified fix + attestation),…
ResolveWebhookEventName = Literal['job.quoted', 'job.declined', 'job.resolved', 'job.failed', 'job.error']


class ResolveWebhookJob(TypedDict):
    """Snapshot of the job at send time. Nullable fields are `null` until the corresponding stage has run."""
    id: str
    status: ResolveJobStatus
    tier: Optional[ResolveTier]
    quote_micro_usd: Optional[int]
    repo_url: str
    decline_reason: Optional[str]
    fail_reason: Optional[str]
    cost_micro_usd: int
    attestation_id: Optional[str]
    attestation_url: Optional[str]
    completed_at: Optional[str]


class ResolveWebhookEvent(TypedDict):
    """JSON body POSTed to `callback_url`. Verify `x-codai-signature` over the raw bytes before trusting it."""
    event: ResolveWebhookEventName
    job: ResolveWebhookJob
    sent_at: str


# GET /health — 200 response
ResolveHealthResponse = ResolveHealth


# POST /v1/resolve/jobs — request body
CreateResolveJobBody = ResolveIntake


# POST /v1/resolve/jobs — 200 response
CreateResolveJobResponse = ResolveDeclined


# POST /v1/resolve/jobs — 201 response
CreateResolveJobResponse201 = ResolveQuote


# GET /v1/resolve/jobs/{id} — 200 response
GetResolveJobResponse = ResolveJob


# POST /v1/resolve/jobs/{id}/accept — 200 response
AcceptResolveJobResponse = ResolveAccepted


# GET /v1/resolve/attestations/{id} — 200 response
GetResolveAttestationResponse = ResolveAttestation


# GET /v1/resolve/keys — 200 response
GetResolveKeysResponse = ResolveKeys


__all__ = [
    'AcceptResolveJobResponse',
    'CreateResolveJobBody',
    'CreateResolveJobResponse',
    'CreateResolveJobResponse201',
    'GetResolveAttestationResponse',
    'GetResolveJobResponse',
    'GetResolveKeysResponse',
    'ResolveAccepted',
    'ResolveAttestation',
    'ResolveAttestationEnvelope',
    'ResolveAttestationEnvelopeSignaturesItem',
    'ResolveDeclined',
    'ResolveError',
    'ResolveHealth',
    'ResolveHealthResponse',
    'ResolveInsufficientFunds',
    'ResolveIntake',
    'ResolveJob',
    'ResolveJobStatus',
    'ResolveKey',
    'ResolveKeys',
    'ResolveQuote',
    'ResolveReproTest',
    'ResolveTier',
    'ResolveValidationDetails',
    'ResolveWebhookEvent',
    'ResolveWebhookEventName',
    'ResolveWebhookJob',
]
