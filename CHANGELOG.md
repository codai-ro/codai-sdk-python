# Changelog

All notable changes to `codai-sdk` are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
