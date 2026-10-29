"""LIVE smoke test against a running gateway — NOT part of the pytest suite.

    $env:CODAI_API_KEY = '<key>'; $env:CODAI_BASE_URL = 'http://127.0.0.1:8787'
    .\\.venv\\Scripts\\python scripts/smoke_local.py

Exercises models.list, chat (non-stream + stream), account.get, receipt.get,
tasks.list, devices.list, hosts.list and prints one status line per call.
Never prints the key or full bodies. Exit code 1 when any call fails.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from codai import Codai, CodaiError  # noqa: E402

api_key = os.environ.get("CODAI_API_KEY")
base_url = os.environ.get("CODAI_BASE_URL", "http://127.0.0.1:8787")
model = os.environ.get("CODAI_SMOKE_MODEL", "gemini-2.5-flash")
if not api_key:
    print("CODAI_API_KEY is required", file=sys.stderr)
    sys.exit(2)

client = Codai(
    api_key=api_key,
    base_url=base_url,
    max_retries=0,
    timeout=60,
    session_id=f"sdk-py-smoke-{int(time.time() * 1000)}",
    device=os.environ.get("CODAI_SMOKE_DEVICE", "5dc0de00-0000-4000-8000-00000000c0da"),
    device_platform="cli",
    client="codai-sdk-python-smoke/0.2.0",
)

failures = 0


def step(name: str, fn: Callable[[], Any], summary: Callable[[Any], str]) -> None:
    global failures
    t0 = time.time()
    try:
        v = fn()
        print(f"OK   {name:<22} {int((time.time() - t0) * 1000):>5} ms  {summary(v)}")
    except CodaiError as e:
        failures += 1
        print(f"FAIL {name:<22} {int((time.time() - t0) * 1000):>5} ms  HTTP {e.status} code={e.code or '-'} {e}")
    except Exception as e:  # noqa: BLE001
        failures += 1
        print(f"FAIL {name:<22} {int((time.time() - t0) * 1000):>5} ms  {e!r}")


print(f"codai-sdk (python) live smoke → {base_url} (model {model}, key length {len(api_key)})")

step(
    "models.list",
    lambda: client.models.list(),
    lambda m: f"{len(m)} models; has {model}: {any(x.get('id') == model for x in m)}",
)

step(
    "chat (non-stream)",
    lambda: client.chat.completions.create(
        {"model": model, "messages": [{"role": "user", "content": "Reply with exactly the word PONG."}], "max_tokens": 64},
        ext={"effort": "minimal"},
    ),
    lambda r: (
        f"status 200 routed={r.routed_to} content={r.content.strip()!r} "
        f"tokens={(r.usage or {}).get('prompt_tokens')}/{(r.usage or {}).get('completion_tokens')} "
        f"event_id={'yes' if r.event_id else 'no'}"
    ),
)


def _stream() -> Any:
    s = client.chat.completions.stream(
        {"model": model, "messages": [{"role": "user", "content": "Count from 1 to 5, digits separated by spaces."}], "max_tokens": 64},
        ext={"effort": "minimal"},
    )
    n = sum(1 for _ in s.chunks())
    return n, s.final


step(
    "chat (stream)",
    _stream,
    lambda v: (
        f"status 200 chunks={v[0]} routed={v[1].routed_to} content={v[1].content.strip()!r} "
        f"finish={v[1].finish_reason} usage={'yes' if v[1].usage else 'no'}"
    ),
)

step(
    "chat_stream (legacy)",
    lambda: "".join(client.chat_stream([{"role": "user", "content": "Reply with exactly the word OK."}], model=model, max_tokens=64)),
    lambda t: f"status 200 text={t.strip()!r}",
)

step(
    "account.get",
    lambda: client.account.get(),
    lambda a: f"status 200 keys={sorted(a.keys())[:8]}",
)

step(
    "receipt.get",
    lambda: client.receipt.get(),
    lambda r: f"status 200 keys={sorted(r.keys())[:8]}",
)

step(
    "tasks.list",
    lambda: client.tasks.list(limit=5),
    lambda p: f"status 200 tasks={len(p.get('tasks') or [])} next_cursor={'yes' if p.get('next_cursor') else 'no'}",
)

step(
    "devices.list",
    lambda: client.devices.list(),
    lambda d: f"status 200 devices={len(d)}",
)

step(
    "hosts.list",
    lambda: client.hosts.list(),
    lambda h: f"status 200 hosts={len(h)}",
)

step(
    "health.get",
    lambda: client.health.get(),
    lambda h: f"status 200 ok={h.get('ok')} keys={sorted(h.keys())[:6]}",
)

print(f"{'FAILED' if failures else 'PASSED'}: {failures} failure(s)")
sys.exit(1 if failures else 0)
