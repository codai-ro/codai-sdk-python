"""Shared plumbing for resource classes."""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict, List, Optional

from .._http import HttpClient, HttpResponse, RequestExtensions

__all__ = ["Resource", "enc", "request_id_of", "list_of"]


def enc(value: str) -> str:
    """Percent-encode one path segment (mirrors ``encodeURIComponent``)."""
    return urllib.parse.quote(str(value), safe="")


def request_id_of(res: HttpResponse) -> Optional[str]:
    return res.header("x-codai-trace-id") or res.header("x-request-id")


def list_of(raw: Any, key: str) -> List[Dict[str, Any]]:
    value = raw.get(key) if isinstance(raw, dict) else None
    return list(value) if isinstance(value, list) else []


class Resource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def _json(self, path: str, ext: Optional[RequestExtensions] = None, **kwargs: Any) -> Any:
        return self._http.json(path, ext=ext, **kwargs)
