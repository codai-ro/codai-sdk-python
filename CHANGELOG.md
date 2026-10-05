# Changelog

All notable changes to `codai-sdk` are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.12.0] - 2026-10-05

### Added

- `client.audio.speech_stream(body)` → `POST /v1/audio/speech/stream` (`codai-tts-ro`, Azure neural TTS with
  visemes): generator of `{"type": "start"|"audio"|"viseme"|"word"|"done"|"error", ...}`; `audio` events carry the
  decoded `audio_bytes`. `createSpeechStream` in the parity table.
- `client.system_one.batch(items, questions, timeout_ms=None, fallback=None)` — the same questions about up to 16
  states in one call; `system_one.create` documents the new `items`, `timeout_ms` and `fallback` fields and the
  `fallback_used` response flag.
- Ephemeral token scope `live` (realtime + audio) accepted by `tokens.create`.
- `_types.py` regenerated (`SpeechStreamRequest`, `SpeechStreamEvent`, batch fields on `SystemOneRequest` /
  `SystemOneResponse`).

### Not included

- No realtime (WebSocket) helper: the SDK is zero-dependency and the standard library has no WebSocket client, and
  `/v1/realtime` is outside the OpenAPI parity contract. Use `tokens.create("live")` and any WebSocket client against
  `wss://ai.codai.ro/v1/realtime?model=codai-transcribe-live&language=ro&key=<token>` (protocol in the docs,
  gateway → Embeddings, audio & realtime).

## [0.11.0] - 2026-10-02

### Added

- `client.devices.revoke_self_key()` — `POST /v1/keys/self/revoke`: the calling API key revokes itself (sign out).

## [0.10.0] - 2026-09-29

### Added

- `client.prompts.{list, create, get, update, delete, launch}` — pending prompts (`/v1/prompts/*`):
  ready-to-paste prompts left for a future chat, with `goal_key` supersede, `not_before` reminders
  (`prompt.due` notifications) and `launch` into a new session on a device. `launch` is never retried.
  `_types.py` regenerated (`Prompt`, `PromptCreate`, `PromptPatch`, `PromptCreated`, …).

## [0.9.0] - 2026-09-29

### Added

- `client.sessions.dispatch(session_id, *, device_id=..., text=..., mode="send"|"open", turn_id=..., control_id=...)`
  keyword form. `mode="open"` hands the session off — the target only opens it (no user turn), and
  `text`/`turn_id` are dropped. The positional `body` dict still works (keywords override its keys); a
  `send` without `text` now raises `ValueError` client-side instead of a server `400`.
- Regenerated `src/codai/_types.py`: `SessionDispatchRequest.mode` (`text` now optional),
  `SessionDispatchResponse.mode`, `SessionControl.mode` (`'open'` on handoff controls) and
  `DeviceListItem.online` (seen in the last 2 minutes).
- `client.images.edit({"prompt": ..., "image": {"b64_json": ..., "mime_type": ...} | [...]})` →
  `POST /v1/images/edits` (JSON body, 1–14 input images; `mask` unsupported). `editImage` in the
  parity table; `EditImageBody` / `CoreImageEditRequest` types.
- `ImagesResult.mime_types` and `ImagesResult.data_region` (`x-codai-data-region`, `eu` | `global`).
- `generate()` types gain `reference_images`, `aspect_ratio`, `image_size` and the
  `codai-image-fast` / `codai-image-pro` model ids.

### Changed

- `codai-image` is now `gemini-3.1-flash-image` on the Vertex EU endpoint (2.5 is shut down on
  2026-10-02 and served as `codai-image`). `cost_micro_usd` is usage-based (≈ $0.074 per default
  1K image) instead of a flat $0.04. The image request floor timeout is 150 s.

## [0.8.0] - 2026-09-29

### Added

- `client.images.generate({"prompt": ..., "n"?, "size"?, "negative_prompt"?, "model"?})` →
  `POST /v1/images/generations` (base64 only). Backed by `gemini-2.5-flash-image`; `model`
  defaults to `codai-image` (`imagen-4` / `imagen-4-fast` are legacy aliases). Flat $0.04 per
  returned image, reported as `cost_micro_usd`.
- EXPERIMENTAL, unaudited (HIDE protocol) agent-output signatures — provenance only, never
  authentication:
  - `EnvironmentTask.output_signature: Optional[EnvironmentTaskOutputSignature]` plus the
    `AgentOutputKey` / `AgentOutputVerifyRequest` / `AgentOutputVerifyResult` types
    (regenerated `src/codai/_types.py`).
  - `client.verify.agent_output_key()` → `GET /v1/verify/agent-output/key` and
    `client.verify.agent_output(payload, signature)` → `POST /v1/verify/agent-output`
    (public; never retried, 503 `signing_disabled` when signing is off).

## [0.7.0] - 2026-09-27

### Added

- Resolve pricing experiment (regenerated `src/codai/_resolve_types.py`):
  - `ResolveQuote` `intro_price_micro_eur` / `list_price_micro_eur` — present while the €1
    intro price applies to your first paid accept.
  - `ResolveAccepted` `paid_with` (`ResolvePaidWith`: `intro` | `credit` | `wallet` | `free`)
    and `held_micro_eur`; `ResolveJob.paid_with` once accepted.
  - `ResolveInsufficientFundsError.bundle_url` (`Optional[str]`) — fix-bundle checkout
    (10 t7 fixes for €49), set only for `t7` jobs; also appended to the error message.
  - `client.resolve.balance()` — `GET /v1/resolve/balance` (operation `getResolveBalance`) →
    `ResolveBalance {fix_credits, intro_available, wallet_micro_eur}`.

## [0.6.0] - 2026-09-27

### Added

- Signed Resolve attestations: `ResolveAttestation.signature` (DSSE envelope, `None` for
  pre-signing attestations) and `ResolveAttestationEnvelope` / `ResolveKeys` / `ResolveKey`
  types (regenerated `codai._resolve_types`).
- `client.resolve.keys()` — `GET /v1/resolve/keys` (operation `getResolveKeys`).
- `client.resolve.verify_attestation(att, keys=None)` and offline
  `verify_attestation_with_keys(att, keys)` → `{"ok": True, "keyid"}` or
  `{"ok": False, "reason": "UNSIGNED" | "BAD_SIGNATURE" | "STATEMENT_MISMATCH" | "BAD_PAYLOAD_TYPE"}`.
  The statement check is stdlib; the ECDSA signature check needs the optional
  `cryptography` package (lazy import, clear `ImportError` otherwise).
  `attestation_statement(att)` exposes the recomputed statement.

## [0.5.0] - 2026-09-27

### Added

- Resolve job webhooks: `callback_url` on `ResolveIntake`, one-time `callback_secret` on
  `ResolveQuote` / `ResolveDeclined`, and `ResolveWebhookEvent` / `ResolveWebhookEventName` /
  `ResolveWebhookJob` TypedDicts (regenerated `_resolve_types.py`).
- `verify_resolve_webhook(secret, raw_body, signature_header, tolerance_seconds=300, now=None)`
  — constant-time (`hmac.compare_digest`) check of `x-codai-signature: t=<unix>,v1=<hex>`
  with a timestamp window. Exported from `codai` and `codai.resources`.

## [0.4.0] - 2026-09-27

### Added

- `client.resolve` — codai Resolve (pay per verified fix, `https://resolve.codai.ro`,
  override with `resolve_base_url=`): `submit`, `get`, `accept`, `attestation`,
  `health`, `wait_for`. `ResolveError` / `ResolveInsufficientFundsError` (402 carries
  `topup_url`, `balance`, `required`). `RESOLVE_OPERATION_METHODS` maps every
  `resolve.yaml` operationId; `_resolve_types.py` is generated from it.

## [0.3.1] - 2026-09-26

### Changed

- Regenerated `_types.py`: project prebuild pool fields, environment `prebuild`
  and `prebuild_claimed` on create (CE-0072).

## [0.3.0] - 2026-09-25

### Added

- Projects + environments resources (26 operations), restoring full parity with the gateway
  OpenAPI (88 operations): `projects.{list,create,get,update,delete}`,
  `environments.{list,create,enroll,get,update,start,stop,archive,destroy,enroll_token}`,
  `environments.members.{list,add,set_ssh_key,set_role,remove}`,
  `environments.ports.{list,set,remove}` and `environments.secrets.{list,set,remove}`.
  `enroll`, `create` and `enroll_token` are never retried (the enrolment token is single-use).
- `_types.py` regenerated: `Project*` and `Environment*` TypedDicts.
- `system_one.create({"state", "questions"})` — typed decisions from codai-s1 (`POST /v1/systemone`,
  Choice / Score / Noul with calibrated probabilities). Raises on 503 `s1_unavailable`; keep a fallback.
- `triggers.*`, `notifications.*`, `environments.members.ssh_cert`, `environments.ssh_ca`,
  `environments.tasks.{list,create,get}` — parity with the TypeScript SDK.

## [0.2.1] - 2026-09-24

### Added

- `WalletLedgerEntry.source` literal gains `compute_charge` — the debit written every 10 minutes
  for a running managed cloud environment (F2). Additive; regenerated from the gateway OpenAPI.

## [0.2.0] - 2026-09-23

### Added

- Full gateway coverage: one method per `operationId` in `apps/docs/openapi/en/gateway.yaml`
  (62 operations), grouped like the TypeScript SDK — `client.chat.completions`, `messages`,
  `responses`, `embeddings`, `audio`, `tokens`, `models`, `health`, `agents` (+ `agents.runs`),
  `tools`, `tasks`, `sessions` (+ `events`, `controls`, `lease`, `shares`), `devices`, `hosts`,
  `orgs` (+ `members`), `account`, `receipt`, `feedback`, `phone_models`.
- `OPERATION_METHODS` (operationId → dotted method path) and `tests/test_parity.py`, which
  parses the OpenAPI spec and fails on a missing, stale or non-callable mapping and when the
  Python table diverges from the TypeScript one.
- Generated `codai._types` (`TypedDict`s for every schema plus `<operationId>Body` /
  `<operationId>Response`) from `scripts/gen-types.py`; the parity test fails when it is stale.
- SSE streams: `chat.completions.stream()` / `messages.stream()` / `responses.stream()` return
  iterables with `.text()`, raw chunks/events and a `.final` aggregate (content, tool calls,
  usage, finish reason, routing headers); `agents.runs.stream()`, `sessions.stream()` and
  `hosts.stream()` are generators of `{"event", "data"}` frames.
- `ext={...}` extension bag on every method covering all documented `X-Codai-*` request
  headers (`effort`, `thinking`, `thinking_budget`, `cache`, `no_task`, `task_id`, `device`,
  `compact`, `best_of`, `share_token`, …) plus raw `headers`; client-wide `defaults`, `device`,
  `device_name`, `device_platform`, `client` constructor options.
- `CodaiError.code`, `.request_id`, `.retry_after` parsed from the gateway error envelope.
- Dev extras `pip install -e ".[dev]"` (pyyaml + pytest); an `http.server` stub test suite.

### Changed

- `__version__` now reports the real version (`0.2.0`; it said `0.1.0` in 0.1.1).
- `chat_stream()` is built on `chat.completions.stream()`; 429/5xx retries add jitter.
- Runtime stays zero-dependency (stdlib `urllib`), Python 3.9+.

### Backward compatibility

- Every 0.1.x method keeps its name, signature and return shape: `chat()`, `chat_stream()`,
  `agents_run()`, `feedback()`, `models()`, `mint_token()`, `embeddings()`, `transcribe()`,
  `speech()`. `chat`, `embeddings`, `models` and `feedback` are callable resource groups, so
  `client.chat([...])` and `client.chat.completions.create({...})` are the same call.

## [0.1.1] - 2026-09-13

### Changed

- Repository moved to https://github.com/codai-ro/codai-sdk-python (project URLs updated). No code changes.

## [0.1.0] - 2026-06-23

### Added

- Initial public release.
- `Codai.chat()` — OpenAI-compatible completions with codai extensions
  (`session_id`, `agent_mode`, `compact`, `best_of`).
- `Codai.chat_stream()` — streaming via generator.
- `Codai.agents_run()` — server-side agent loop.
- `Codai.feedback()` — thumbs rating on a completed request.
- `Codai.models()` — list models available to the key.
- Zero dependencies (stdlib only), Python 3.9+.

[Unreleased]: https://github.com/codai-ro/codai-sdk-python/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/codai-ro/codai-sdk-python/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/codai-ro/codai-sdk-python/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/codai-ro/codai-sdk-python/releases/tag/v0.1.0
