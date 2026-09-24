#!/usr/bin/env python3
"""Generate ``src/codai/_types.py`` from ``apps/docs/openapi/en/gateway.yaml``.

TypedDicts for every ``components.schemas`` entry plus a ``<operationId>Body`` /
``<operationId>Response`` alias for each operation's JSON request / 2xx body.
Deterministic: the same spec always produces byte-identical output, so a second
run is a no-op (the parity CI step diffs the committed file against a fresh run).

    .\\.venv\\Scripts\\python scripts/gen-types.py          # write
    .\\.venv\\Scripts\\python scripts/gen-types.py --check  # exit 1 when stale

Dev-only dependency: pyyaml (``pip install -e ".[dev]"``). The runtime SDK stays
zero-dependency — this script is never imported by the package.
"""

from __future__ import annotations

import keyword
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
SPEC = PKG.parents[1] / "apps" / "docs" / "openapi" / "en" / "gateway.yaml"
OUT = PKG / "src" / "codai" / "_types.py"

HTTP_METHODS = ("get", "post", "put", "patch", "delete")

HEADER = '''"""Typed dictionaries for the codai gateway API.

generated — do not edit. Source: apps/docs/openapi/en/gateway.yaml.
Regenerate with ``python scripts/gen-types.py`` (see that script's docstring).

Every ``components.schemas`` entry is a ``TypedDict`` (``total=False`` when the
schema has optional fields; a ``_<Name>Required`` base carries the required
keys of mixed schemas). Non-object schemas (enums, unions, arrays) are type
aliases. ``<operationId>Body`` / ``<operationId>Response`` name each
operation's JSON request body and first 2xx JSON response.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

'''


def pascal(value: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in re.split(r"[^A-Za-z0-9]+", value) if p)


def first_line(text: Optional[str]) -> str:
    if not text:
        return ""
    line = text.strip().splitlines()[0].strip()
    line = line.replace("\\", "\\\\").replace('"""', "'''")
    return line[:110] + ("…" if len(line) > 110 else "")


def union(parts: List[str]) -> str:
    seen: List[str] = []
    for p in parts:
        if p not in seen:
            seen.append(p)
    if len(seen) == 1:
        return seen[0]
    if "None" in seen:
        rest = [p for p in seen if p != "None"]
        inner = rest[0] if len(rest) == 1 else f"Union[{', '.join(rest)}]"
        return f"Optional[{inner}]"
    return f"Union[{', '.join(seen)}]"


class Generator:
    def __init__(self, spec: Dict[str, Any]) -> None:
        self.spec = spec
        self.schemas: Dict[str, Any] = spec["components"]["schemas"]
        self.blocks: List[Tuple[str, str]] = []
        self.emitted: Dict[str, str] = {}
        self.in_progress: set = set()

    # ------------------------------------------------------------ helpers
    @staticmethod
    def ref_name(ref: str) -> str:
        return ref.rsplit("/", 1)[1]

    def deref(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        seen = 0
        while isinstance(schema, dict) and "$ref" in schema and seen < 20:
            schema = self.schemas[self.ref_name(schema["$ref"])]
            seen += 1
        return schema

    def add_block(self, name: str, code: str) -> None:
        if name in self.emitted:
            return
        self.emitted[name] = code
        self.blocks.append((name, code))

    # ------------------------------------------------------- type mapping
    def ensure_schema(self, name: str) -> str:
        """Emit the named component schema (once) and return its Python name."""
        if name in self.emitted:
            return name
        if name in self.in_progress:  # cyclic reference — forward-ref string
            return f'"{name}"'
        self.in_progress.add(name)
        schema = self.schemas[name]
        expr = self.type_expr(schema, name, top_level=True)
        if expr != name:
            doc = first_line(schema.get("description") or schema.get("title"))
            comment = f"# {doc}\n" if doc else ""
            self.add_block(name, f"{comment}{name} = {expr}\n")
        self.in_progress.discard(name)
        return name

    def type_expr(self, schema: Any, hint: str, top_level: bool = False) -> str:
        if schema is None or schema is True or schema == {}:
            return "Any"
        if not isinstance(schema, dict):
            return "Any"
        if "$ref" in schema:
            name = self.ensure_schema(self.ref_name(schema["$ref"]))
            return f"Optional[{name}]" if schema.get("nullable") else name

        nullable = bool(schema.get("nullable"))
        expr: str
        if "allOf" in schema:
            expr = self.all_of(schema, hint)
        elif "oneOf" in schema or "anyOf" in schema:
            variants = schema.get("oneOf") or schema.get("anyOf") or []
            expr = union([self.type_expr(v, f"{hint}Option{i + 1}") for i, v in enumerate(variants)])
        elif "enum" in schema:
            values = schema["enum"]
            literals = [repr(v) for v in values if v is not None]
            if None in values:
                nullable = True
            expr = f"Literal[{', '.join(literals)}]" if literals else "None"
        else:
            t = schema.get("type")
            if isinstance(t, list):
                if "null" in t:
                    nullable = True
                expr = union(
                    [self.type_expr({**schema, "type": x}, hint) for x in t if x != "null"] or ["Any"]
                )
            elif t == "string":
                expr = "bytes" if schema.get("format") == "binary" else "str"
            elif t == "integer":
                expr = "int"
            elif t == "number":
                expr = "float"
            elif t == "boolean":
                expr = "bool"
            elif t == "null":
                expr = "None"
            elif t == "array":
                expr = f"List[{self.type_expr(schema.get('items'), hint + 'Item')}]"
            elif t == "object" or "properties" in schema:
                if schema.get("properties"):
                    expr = self.emit_object(hint, schema)
                else:
                    ap = schema.get("additionalProperties")
                    if isinstance(ap, dict) and ap:
                        expr = f"Dict[str, {self.type_expr(ap, hint + 'Value')}]"
                    else:
                        expr = "Dict[str, Any]"
            else:
                expr = "Any"
        if nullable and expr not in ("None", "Any") and not expr.startswith("Optional["):
            expr = f"Optional[{expr}]"
        return expr

    def all_of(self, schema: Dict[str, Any], hint: str) -> str:
        parts = schema["allOf"]
        merged: Dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        ref_only: Optional[str] = None
        extra_props = False
        for part in parts:
            if isinstance(part, dict) and "$ref" in part:
                ref_only = self.ref_name(part["$ref"]) if ref_only is None else ""
                resolved = self.deref(part)
            else:
                resolved = part
                if isinstance(part, dict) and part.get("properties"):
                    extra_props = True
            self._merge_into(merged, resolved)
        if len(parts) == 1 and ref_only and not extra_props:
            return self.ensure_schema(ref_only)
        merged["description"] = schema.get("description") or next(
            (p.get("description") for p in parts if isinstance(p, dict) and p.get("description")), None
        )
        if not merged["properties"]:
            return "Dict[str, Any]"
        return self.emit_object(hint, merged)

    def _merge_into(self, merged: Dict[str, Any], part: Dict[str, Any]) -> None:
        if not isinstance(part, dict):
            return
        if "allOf" in part:
            for sub in part["allOf"]:
                self._merge_into(merged, self.deref(sub) if "$ref" in sub else sub)
        for key, prop in (part.get("properties") or {}).items():
            merged["properties"][key] = prop
        for key in part.get("required") or []:
            if key not in merged["required"]:
                merged["required"].append(key)

    def emit_object(self, name: str, schema: Dict[str, Any]) -> str:
        if name in self.emitted:
            return name
        props: Dict[str, Any] = schema.get("properties") or {}
        required = [k for k in (schema.get("required") or []) if k in props]
        fields: List[Tuple[str, str]] = []
        for key in props:  # YAML order — deterministic
            fields.append((key, self.type_expr(props[key], f"{name}{pascal(key)}")))
        if name in self.emitted:  # emitted through a cycle while resolving children
            return name
        doc = first_line(schema.get("description") or schema.get("title"))
        docstring = f'    """{doc}"""\n' if doc else ""
        bad_key = any(not k.isidentifier() or keyword.iskeyword(k) for k, _ in fields)
        req_fields = [(k, t) for k, t in fields if k in required]
        opt_fields = [(k, t) for k, t in fields if k not in required]

        if bad_key:
            # Functional form: keys that are Python keywords (``from``, ``pass``) cannot
            # appear in a class body. Mixed required/optional collapses to total=False.
            total = "True" if not opt_fields else "False"
            body = ",\n".join(f"        {k!r}: {t}" for k, t in fields)
            comment = f"# {doc}\n" if doc else ""
            code = f"{comment}{name} = TypedDict(\n    {name!r},\n    {{\n{body},\n    }},\n    total={total},\n)\n"
            self.add_block(name, code)
            return name

        lines: List[str] = []
        if req_fields and opt_fields:
            base = f"_{name}Required"
            lines.append(f"class {base}(TypedDict):")
            lines.extend(f"    {k}: {t}" for k, t in req_fields)
            lines.append("")
            lines.append("")
            lines.append(f"class {name}({base}, total=False):")
            if docstring:
                lines.append(docstring.rstrip("\n"))
            lines.extend(f"    {k}: {t}" for k, t in opt_fields)
        else:
            total = "" if req_fields else ", total=False"
            lines.append(f"class {name}(TypedDict{total}):")
            if docstring:
                lines.append(docstring.rstrip("\n"))
            lines.extend(f"    {k}: {t}" for k, t in fields)
        self.add_block(name, "\n".join(lines) + "\n")
        return name

    # ---------------------------------------------------------- operations
    def emit_operations(self) -> None:
        for path, item in self.spec["paths"].items():
            for method in HTTP_METHODS:
                op = item.get(method)
                if not isinstance(op, dict) or not op.get("operationId"):
                    continue
                op_id = op["operationId"]
                base = op_id[:1].upper() + op_id[1:]
                content = (op.get("requestBody") or {}).get("content") or {}
                for ct in ("application/json", "multipart/form-data"):
                    if ct in content and "schema" in content[ct]:
                        expr = self.type_expr(content[ct]["schema"], f"{base}Body")
                        if expr != f"{base}Body":
                            self.add_block(
                                f"{base}Body", f"# {method.upper()} {path} — request body\n{base}Body = {expr}\n"
                            )
                        break
                first_expr: Optional[str] = None
                for code in sorted(op.get("responses") or {}):
                    if not str(code).startswith("2"):
                        continue
                    rcontent = (op["responses"][code].get("content") or {}).get("application/json")
                    if not rcontent or "schema" not in rcontent:
                        continue
                    alias = f"{base}Response" if first_expr is None else f"{base}Response{code}"
                    expr = self.type_expr(rcontent["schema"], alias)
                    if first_expr is None:
                        first_expr = expr
                    elif expr == first_expr:
                        continue
                    if expr != alias:
                        self.add_block(alias, f"# {method.upper()} {path} — {code} response\n{alias} = {expr}\n")

    # -------------------------------------------------------------- render
    def render(self) -> str:
        for name in self.schemas:  # YAML order
            self.ensure_schema(name)
        self.emit_operations()
        out = [HEADER]
        for _, code in self.blocks:
            out.append(code)
            out.append("\n\n")
        names = sorted(n for n in self.emitted if not n.startswith("_"))
        out.append("__all__ = [\n" + "".join(f"    {n!r},\n" for n in names) + "]\n")
        text = "".join(out)
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        return text.rstrip("\n") + "\n"


def main(argv: List[str]) -> int:
    with SPEC.open("r", encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    text = Generator(spec).render()
    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"STALE: {OUT} differs from a fresh generation", file=sys.stderr)
            return 1
        print(f"OK: {OUT} is up to date")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({text.count(chr(10))} lines, {len(spec['components']['schemas'])} schemas)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
