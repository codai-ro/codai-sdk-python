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

MIT © codai
