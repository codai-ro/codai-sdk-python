"""Lists and the share sheet: ``/v1/lists/*``, ``/v1/share``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional

from .._http import RequestExtensions, frame_json
from ._base import Resource, enc, list_of

__all__ = ["Lists", "ListItemImage"]


@dataclass
class ListItemImage:
    """An item image (``GET /v1/lists/items/{itemId}/image``)."""

    data: bytes
    content_type: str


def _list(list_id: str, suffix: str = "") -> str:
    return f"/v1/lists/{enc(list_id)}{suffix}"


def _item(item_id: str, suffix: str = "") -> str:
    return f"/v1/lists/items/{enc(item_id)}{suffix}"


class Lists(Resource):
    def list(self, archived: bool = False, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/lists`` — share-sheet order; presets are created on the first call."""
        query = {"archived": "1" if archived else None}
        return list_of(self._json("/v1/lists", ext=ext, query=query), "lists")

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/lists`` — ``{"name", "icon"?, "color"?, "show_in_share"?, "price_watch"?}``; returns the list."""
        return self._json("/v1/lists", ext=ext, method="POST", body=body)["list"]

    def reorder(self, ids: List[str], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/lists/order`` — the order of your lists (and of the share-sheet targets)."""
        return self._json("/v1/lists/order", ext=ext, method="PATCH", body={"ids": list(ids)})

    def stream(self, ext: Optional[RequestExtensions] = None) -> Iterator[Dict[str, Any]]:
        """``GET /v1/lists/stream`` — yields ``{"op": "lists"|"item"|"item_delete", "listId"?, "itemId"?}``."""
        for frame in self._http.sse("/v1/lists/stream", ext=ext):
            if frame.event != "list":
                continue
            data = frame_json(frame)
            if isinstance(data, dict):
                yield data

    def update(self, list_id: str, patch: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/lists/{id}`` — name, icon, color, share-sheet visibility, price watch, archived."""
        return self._json(_list(list_id), ext=ext, method="PATCH", body=patch)["list"]

    def delete(self, list_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/lists/{id}`` — custom lists only (presets raise 409 ``preset_list``)."""
        self._http.request(_list(list_id), ext=ext, method="DELETE")

    def items(
        self,
        list_id: str,
        done: bool = False,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> List[Dict[str, Any]]:
        """``GET /v1/lists/{id}/items`` — pinned first, then newest; done items only with ``done=True``."""
        query = {"done": "1" if done else None, "limit": limit}
        return list_of(self._json(_list(list_id, "/items"), ext=ext, query=query), "items")

    def add(self, list_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/lists/{id}/items`` — ``{"item", "created"}``; 201 created, 200 for a duplicate."""
        return self._json(_list(list_id, "/items"), ext=ext, method="POST", body=body)

    def update_item(
        self, item_id: str, patch: Dict[str, Any], ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PATCH /v1/lists/items/{itemId}`` — title, body, done, pinned, reminder; ``list_id`` moves it."""
        return self._json(_item(item_id), ext=ext, method="PATCH", body=patch)["item"]

    def delete_item(self, item_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/lists/items/{itemId}`` — also deletes its uploaded media."""
        self._http.request(_item(item_id), ext=ext, method="DELETE")

    def image(self, item_id: str, ext: Optional[RequestExtensions] = None) -> ListItemImage:
        """``GET /v1/lists/items/{itemId}/image`` — the uploaded image or the unfurled preview image."""
        res = self._http.request(_item(item_id, "/image"), ext=ext)
        return ListItemImage(data=res.data, content_type=res.header("content-type") or "application/octet-stream")

    def export_markdown(self, list_id: str, ext: Optional[RequestExtensions] = None) -> str:
        """``GET /v1/lists/{id}/export.md`` — the whole list as GitHub-flavoured Markdown."""
        return self._http.request(_list(list_id, "/export.md"), ext=ext).data.decode("utf-8")

    def share(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/share`` — ``{"item", "list", "created"}``; target ``list_id``, ``preset`` or auto (Inbox)."""
        return self._json("/v1/share", ext=ext, method="POST", body=body)
