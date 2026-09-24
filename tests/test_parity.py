"""OpenAPI parity gate: every ``operationId`` in the gateway spec maps to exactly
one method on the ``Codai`` client, the mapping table names no operation the spec
lacks, and SSE-only operations are generator methods. Also checks that the
committed ``_types.py`` is what ``scripts/gen-types.py`` would produce."""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

from codai import OPERATION_METHODS, STREAMING_OPERATIONS, Codai

PKG = Path(__file__).resolve().parents[1]
SPEC = PKG.parents[1] / "apps" / "docs" / "openapi" / "en" / "gateway.yaml"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


def read_operations() -> List[Dict[str, Any]]:
    with SPEC.open("r", encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    ops: List[Dict[str, Any]] = []
    for path, item in spec["paths"].items():
        for method, op in item.items():
            if method not in HTTP_METHODS or not isinstance(op, dict) or not op.get("operationId"):
                continue
            content_types = [
                ct
                for code, r in (op.get("responses") or {}).items()
                if str(code).startswith("2")
                for ct in ((r or {}).get("content") or {})
            ]
            sse_only = bool(content_types) and all(ct == "text/event-stream" for ct in content_types)
            ops.append({"id": op["operationId"], "method": method, "path": path, "sse_only": sse_only})
    return ops


def resolve(root: Any, dotted: str) -> Any:
    node = root
    for key in dotted.split("."):
        node = getattr(node, key, None)
        if node is None:
            return None
    return node


OPS = read_operations()
CLIENT = Codai(api_key="x")


def test_spec_has_operations_with_unique_ids():
    assert len(OPS) > 50
    ids = [o["id"] for o in OPS]
    assert len(set(ids)) == len(ids)


def test_every_operation_id_has_a_mapping():
    missing = [f"{o['id']} ({o['method'].upper()} {o['path']})" for o in OPS if o["id"] not in OPERATION_METHODS]
    assert missing == []


def test_mapping_has_no_stale_keys():
    ids = {o["id"] for o in OPS}
    assert [k for k in OPERATION_METHODS if k not in ids] == []


def test_every_mapped_method_resolves_to_a_callable():
    broken = [f"{k} → {v}" for k, v in OPERATION_METHODS.items() if not callable(resolve(CLIENT, v))]
    assert broken == []


def test_every_mapped_method_path_is_unique():
    values = list(OPERATION_METHODS.values())
    assert len(set(values)) == len(values)


def test_sse_only_operations_are_generator_methods():
    for op in OPS:
        fn = resolve(CLIENT, OPERATION_METHODS[op["id"]])
        assert op["sse_only"] == (op["id"] in STREAMING_OPERATIONS), f"{op['id']} sse_only flag"
        assert inspect.isgeneratorfunction(fn) == op["sse_only"], f"{op['id']} → {OPERATION_METHODS[op['id']]} generator shape"


def test_mapping_mirrors_typescript_sdk_when_present():
    """Same operationId → same path modulo camelCase/snake_case, so both SDKs feel identical."""
    ts = PKG.parent / "sdk" / "src" / "operations.ts"
    if not ts.exists():
        pytest.skip("TypeScript SDK not checked out")
    import re

    pairs = re.findall(r"^\s*(\w+):\s*'([\w.]+)',", ts.read_text(encoding="utf-8"), re.M)
    ts_map = {k: v for k, v in pairs}
    assert set(ts_map) == set(OPERATION_METHODS)
    snake = lambda s: re.sub(r"(?<!^)(?<!\.)(?=[A-Z])", "_", s).lower()  # noqa: E731
    assert {k: snake(v) for k, v in ts_map.items()} == OPERATION_METHODS


def test_generated_types_are_up_to_date():
    gen = PKG / "scripts" / "gen-types.py"
    spec_mod = importlib.util.spec_from_file_location("gen_types", gen)
    assert spec_mod and spec_mod.loader
    mod = importlib.util.module_from_spec(spec_mod)
    spec_mod.loader.exec_module(mod)
    with SPEC.open("r", encoding="utf-8") as fh:
        fresh = mod.Generator(yaml.safe_load(fh)).render()
    committed = (PKG / "src" / "codai" / "_types.py").read_text(encoding="utf-8")
    assert committed == fresh, "src/codai/_types.py is stale — run scripts/gen-types.py"


def test_generated_types_import_and_cover_every_schema():
    from codai import _types

    with SPEC.open("r", encoding="utf-8") as fh:
        schemas = yaml.safe_load(fh)["components"]["schemas"]
    missing = [name for name in schemas if not hasattr(_types, name)]
    assert missing == []
    assert "generated — do not edit" in _types.__doc__
