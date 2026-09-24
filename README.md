# codai-sdk — Python SDK

[![PyPI version](https://img.shields.io/pypi/v/codai-sdk.svg)](https://pypi.org/project/codai-sdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/codai-sdk.svg)](https://pypi.org/project/codai-sdk/)
[![license](https://img.shields.io/pypi/l/codai-sdk.svg)](./LICENSE)

Official Python client for the [codai](https://codai.ro) AI gateway.
Zero dependencies (stdlib only), Python 3.9+.

```bash
pip install codai-sdk
```

> You need a codai API key. Get one at **[codai.ro](https://codai.ro)**.
> The import name stays `codai`:

```python
from codai import Codai

client = Codai(api_key="ck-...", session_id="my-project")

# Chat (OpenAI-compatible, smart-routed)
result = client.chat([{"role": "user", "content": "Explain asyncio.gather"}])
print(result.content)
print(result.routed_to)   # which model actually served

# Streaming
for delta in client.chat_stream([{"role": "user", "content": "hi"}]):
    print(delta, end="", flush=True)

# Server-side agent loop
run = client.agents_run("Find and summarize the TODOs in this codebase")
print(run.result)

# Feedback (improves routing for everyone)
client.feedback(result.request_id, 1)
```

## codai extensions

| Option            | Effect                               |
| ----------------- | ------------------------------------ |
| `session_id`      | Session memory + routing stickiness  |
| `agent_mode=True` | Plan-and-execute loop (Pro+)         |
| `compact="auto"`  | Server-side context compaction       |
| `best_of=0/3`     | Disable / force best-of-N ensembling |

## Resource groups (0.2.0)

Every gateway operation is a method on the client, grouped exactly like the
TypeScript SDK (`camelCase` → `snake_case`). The 0.1.x helpers above still
work — `client.chat([...])` and `client.chat.completions.create({...})` are
the same call. Every method takes an optional `ext={...}` bag of `X-Codai-*`
headers (`effort`, `thinking`, `thinking_budget`, `cache`, `no_task`,
`task_id`, `device`, `compact`, `best_of`, `share_token`, … plus raw `headers`).

| Attribute          | Methods                                                                                                            | Gateway                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------- |
| `chat.completions` | `create`, `stream`                                                                                                 | `POST /v1/chat/completions`                  |
| `messages`         | `create`, `stream`                                                                                                 | `POST /v1/messages` (Anthropic wire)         |
| `responses`        | `create`, `stream`                                                                                                 | `POST /v1/responses` (OpenAI Responses wire) |
| `embeddings`       | `create`                                                                                                           | `POST /v1/embeddings`                        |
| `audio`            | `transcribe`, `transcribe_detailed`, `speech`, `speech_detailed`                                                   | `/v1/audio/*`                                |
| `tokens`           | `create`                                                                                                           | `POST /v1/tokens`                            |
| `models`           | `list`                                                                                                             | `GET /v1/models`                             |
| `health`           | `get`, `ready`, `status`                                                                                           | `/health`, `/health/ready`, `/status`        |
| `agents`           | `run`; `runs.create/get/steps/stats/cancel/stream`                                                                 | `/v1/agents/*`                               |
| `tools`            | `search`, `fetch`                                                                                                  | `/v1/tools/*`                                |
| `tasks`            | `list`, `pending`, `stats`, `get`, `confirm`                                                                       | `/v1/tasks/*`                                |
| `sessions`         | `create`, `list`, `get`, `update`, `delete`, `dispatch`, `stream`; `events.*`, `controls.*`, `lease.*`, `shares.*` | `/v1/sessions/*`                             |
| `devices`          | `list`, `update`, `delete`, `dispatch_inbox`                                                                       | `/v1/devices/*`                              |
| `hosts`            | `list`, `exec`, `post_result`, `stream`                                                                            | `/v1/hosts/*`                                |
| `orgs`             | `create`, `list`; `members.list/add/remove`                                                                        | `/v1/orgs/*`                                 |
| `account`          | `get`, `update`                                                                                                    | `/v1/account`                                |
| `receipt`          | `get`                                                                                                              | `GET /v1/receipt`                            |
| `feedback`         | `submit`                                                                                                           | `POST /v1/feedback`                          |
| `phone_models`     | `list`                                                                                                             | `GET /v1/phone/models`                       |

```python
from codai import Codai, CodaiError

client = Codai(api_key="codai_...", device="5dc0de00-0000-4000-8000-00000000c0da")

# Chat with extension headers; raw chunks + aggregate on streams
r = client.chat.completions.create(
    {"model": "codai", "messages": [{"role": "user", "content": "hi"}]},
    ext={"effort": "high", "thinking": True, "thinking_budget": 8192},
)
print(r.content, r.routed_to, r.usage)

stream = client.chat.completions.stream({"messages": [{"role": "user", "content": "hi"}]})
for delta in stream:            # text deltas; stream.chunks() for raw chunk dicts
    print(delta, end="")
print(stream.final.usage, stream.final.tool_calls)

# Anthropic / OpenAI Responses wires
client.messages.create({"messages": [{"role": "user", "content": "hi"}], "max_tokens": 200}).text
client.responses.create({"input": "hi"}).output_text

# Async agent run + SSE progress
run = client.agents.runs.create({"task": "Summarise the repo README."})
for ev in client.agents.runs.stream(run["id"]):
    if ev["event"] == "done":
        print(ev["data"]["status"], ev["data"]["result"])

# Tasks, account, receipt
page = client.tasks.list(limit=20)
print(client.account.get()["plan"], client.receipt.get(since="2026-09-01T00:00:00Z"))

# Shared sessions (needs a device id on the client) and hosts
s = client.sessions.create({"title": "pairing"})
for ev in client.sessions.stream(s["id"], after=0):
    print(ev["event"], ev["data"].get("seq"))
print(client.hosts.list())

try:
    client.orgs.members.add("org-1", {"user_id": "u", "role": "member"})
except CodaiError as e:
    print(e.status, e.code, e.request_id, e.retry_after)
```

Typed request/response shapes live in `codai._types` (generated from the
OpenAPI spec — `TypedDict`s such as `ChatCompletionRequest`, `Task`,
`SessionEvent`, `CreateSessionShareResponse`).

## Development

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest -q             # unit + OpenAPI parity tests, no network
.venv/Scripts/python scripts/gen-types.py     # regenerate src/codai/_types.py
```

MIT © codai
