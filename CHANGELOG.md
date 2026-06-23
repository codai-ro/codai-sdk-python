# Changelog

All notable changes to `codai-sdk` are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/dragoscv/codai-sdk-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dragoscv/codai-sdk-python/releases/tag/v0.1.0
