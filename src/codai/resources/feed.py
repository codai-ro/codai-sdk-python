"""The public feed: ``/v1/feed/*`` — posts, comments and replies, profiles, follows, search and tags, likes, reports
and blocked authors (AL-300, AL-301, AL-320..AL-324)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .._http import RequestExtensions
from ._base import Resource, enc, list_of

__all__ = ["Feed", "FeedImage", "FEED_GUIDELINES_VERSION"]

#: Community guidelines version the gateway currently requires on create (``feed.me()`` is authoritative).
FEED_GUIDELINES_VERSION = "2026-10-28"


@dataclass
class FeedImage:
    """A post image (``GET /v1/feed/images/{postId}/{index}``)."""

    data: bytes
    content_type: str


def _post(post_id: str, suffix: str = "") -> str:
    return f"/v1/feed/posts/{enc(post_id)}{suffix}"


def _media(post_id: str, suffix: str = "") -> str:
    return f"/v1/feed/media/{enc(post_id)}{suffix}"


class Feed(Resource):
    def list(
        self,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        kind: Optional[str] = None,
        author: Optional[str] = None,
        lang: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        *,
        scope: Optional[str] = None,
        q: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/feed`` — ``{"posts", "next_cursor"}``, newest first; pass ``next_cursor`` back as ``cursor``.

        ``lang`` (``en`` / ``ro``) keeps posts in that language plus posts without one.
        ``scope="following"`` keeps only authors you follow; ``q`` searches the text (diacritics-insensitive, a
        leading ``#x`` / ``@x`` acts as ``tag`` / ``author``); ``tag`` keeps posts with that hashtag.
        """
        query = {
            "cursor": cursor,
            "limit": limit,
            "kind": kind,
            "author": author,
            "lang": lang,
            "scope": scope,
            "q": q,
            "tag": tag,
        }
        return self._json("/v1/feed", ext=ext, query=query)

    def tags(
        self,
        prefix: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> List[Dict[str, Any]]:
        """``GET /v1/feed/tags`` — ``[{"tag", "count"}]``, the most used hashtags of the last 30 days."""
        return list_of(self._json("/v1/feed/tags", ext=ext, query={"prefix": prefix, "limit": limit}), "tags")

    def follow(self, username: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/feed/follows`` — ``{"following": True, "username"}`` (idempotent).

        Raises 400 for yourself, 404 ``user_not_found`` for an unknown user or a block either way, 429 above
        200 follows a day.
        """
        return self._json("/v1/feed/follows", ext=ext, method="POST", body={"username": username})

    def unfollow(self, username: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/feed/follows/{username}`` — raises 404 ``follow_not_found`` when you were not following."""
        self._http.request(f"/v1/feed/follows/{enc(username)}", ext=ext, method="DELETE")

    def follows(
        self,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/feed/follows`` — ``{"follows": [{"username", "badge", "created_at"}], "next_cursor"}``."""
        return self._json("/v1/feed/follows", ext=ext, query={"cursor": cursor, "limit": limit})

    def user(
        self,
        username: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        kind: Optional[str] = None,
        lang: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/feed/users/{username}`` — ``{"profile", "posts", "next_cursor"}``.

        Raises 404 ``user_not_found`` when no active user has that username or they blocked you;
        ``profile["blocked"]`` is true (and ``posts`` empty) when you blocked them.
        ``profile["following"]``, ``follower_count`` and ``following_count`` describe the follow graph.
        """
        query = {"cursor": cursor, "limit": limit, "kind": kind, "lang": lang}
        return self._json(f"/v1/feed/users/{enc(username)}", ext=ext, query=query)

    def me(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/feed/me`` — ``{"username", "suggested_username", "guidelines_version"}``."""
        return self._json("/v1/feed/me", ext=ext)

    def get(self, post_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/feed/posts/{id}`` — the post."""
        return self._json(_post(post_id), ext=ext)["post"]

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/feed/posts`` — ``{"kind", "body", "link_url"?, "images"?, "client_id"?, "guidelines_version"}``.

        Raises 409 ``username_required``, 400 ``guidelines_required`` or 422 ``image_rejected``; a repeated
        ``client_id`` returns the existing post.
        """
        return self._json("/v1/feed/posts", ext=ext, method="POST", body=body)["post"]

    def delete(self, post_id: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/feed/posts/{id}`` — your own posts only."""
        self._http.request(_post(post_id), ext=ext, method="DELETE")

    def like(self, post_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/feed/posts/{id}/like`` — ``{"like_count", "liked_by_me"}`` (idempotent)."""
        return self._json(_post(post_id, "/like"), ext=ext, method="POST")

    def unlike(self, post_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/feed/posts/{id}/like`` — ``{"like_count", "liked_by_me"}`` (idempotent)."""
        return self._json(_post(post_id, "/like"), ext=ext, method="DELETE")

    def report(
        self,
        post_id: str,
        reason: str,
        details: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> None:
        """``POST /v1/feed/posts/{id}/report`` — reason ``spam|harassment|hate|sexual|violence|illegal|ip|other``."""
        body: Dict[str, Any] = {"reason": reason}
        if details is not None:
            body["details"] = details
        self._json(_post(post_id, "/report"), ext=ext, method="POST", body=body)

    def comments(
        self,
        post_id: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/feed/posts/{id}/comments`` — ``{"comments", "next_cursor"}``, oldest first."""
        return self._json(_post(post_id, "/comments"), ext=ext, query={"cursor": cursor, "limit": limit})

    def comment(
        self,
        post_id: str,
        body: str,
        guidelines_version: str,
        client_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        *,
        parent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/feed/posts/{id}/comments`` — ``{"comment", "comment_count"}``.

        ``parent_id`` replies to a visible top-level comment of the same post (one level only). Raises 409
        ``username_required``, 400 ``guidelines_required`` / ``invalid_parent`` or 429 above 60 comments per
        hour; a repeated ``client_id`` returns the existing comment.
        """
        payload: Dict[str, Any] = {"body": body, "guidelines_version": guidelines_version}
        if parent_id is not None:
            payload["parent_id"] = parent_id
        if client_id is not None:
            payload["client_id"] = client_id
        return self._json(_post(post_id, "/comments"), ext=ext, method="POST", body=payload)

    def delete_comment(self, comment_id: str, ext: Optional[RequestExtensions] = None) -> int:
        """``DELETE /v1/feed/comments/{id}`` — your comment or any on your post; returns the new comment count."""
        return int(self._json(f"/v1/feed/comments/{enc(comment_id)}", ext=ext, method="DELETE")["comment_count"])

    def report_comment(
        self,
        comment_id: str,
        reason: str,
        details: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> None:
        """``POST /v1/feed/comments/{id}/report`` — idempotent per comment; 400 for your own comment."""
        body: Dict[str, Any] = {"reason": reason}
        if details is not None:
            body["details"] = details
        self._json(f"/v1/feed/comments/{enc(comment_id)}/report", ext=ext, method="POST", body=body)

    def blocks(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/feed/blocks`` — ``[{"username", "created_at"}]``."""
        return list_of(self._json("/v1/feed/blocks", ext=ext), "blocks")

    def block(
        self,
        post_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
        *,
        username: Optional[str] = None,
    ) -> Optional[str]:
        """``POST /v1/feed/blocks`` — blocks the author of ``post_id`` or ``username`` (exactly one); returns the username."""
        if (post_id is None) == (username is None):
            raise ValueError("pass exactly one of post_id or username")
        body = {"post_id": post_id} if post_id is not None else {"username": username}
        return self._json("/v1/feed/blocks", ext=ext, method="POST", body=body).get("username")

    def unblock(self, username: str, ext: Optional[RequestExtensions] = None) -> None:
        """``DELETE /v1/feed/blocks/{username}``."""
        self._http.request(f"/v1/feed/blocks/{enc(username)}", ext=ext, method="DELETE")

    def image(self, post_id: str, index: int, ext: Optional[RequestExtensions] = None) -> FeedImage:
        """``GET /v1/feed/images/{postId}/{index}`` — public; usually you just load the image ``url``."""
        res = self._http.request(f"/v1/feed/images/{enc(post_id)}/{int(index)}", ext=ext)
        return FeedImage(data=res.data, content_type=res.header("content-type") or "application/octet-stream")

    def preview_image(self, post_id: str, ext: Optional[RequestExtensions] = None) -> FeedImage:
        """``GET /v1/feed/previews/{postId}`` — public; usually you just load ``link_preview["image_url"]``."""
        res = self._http.request(f"/v1/feed/previews/{enc(post_id)}", ext=ext)
        return FeedImage(data=res.data, content_type=res.header("content-type") or "application/octet-stream")

    def media_url(self, post_id: str) -> str:
        """Public URL of a post's video/audio (``GET /v1/feed/media/{postId}``, 302 to a 10-minute signed URL)."""
        return self._http.url(_media(post_id))

    def media_poster_url(self, post_id: str) -> str:
        """Public poster URL of a post's video (``GET /v1/feed/media/{postId}/poster``, 302)."""
        return self._http.url(_media(post_id, "/poster"))

    def public_post(self, post_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/public/feed/posts/{id}`` — no key needed; 404 unless the author opted in to the public web."""
        return self._json(f"/v1/public/feed/posts/{enc(post_id)}", ext=ext)["post"]

    def public_user(
        self,
        username: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/public/feed/users/{username}`` — ``{"profile", "posts", "next_cursor"}``; 404 unless opted in."""
        return self._json(f"/v1/public/feed/users/{enc(username)}", ext=ext, query={"cursor": cursor, "limit": limit})

    def public_sitemap(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/public/feed/sitemap`` — ``{"posts": [{"id", "username", "updated_at"}], "users": [...]}``."""
        return self._json("/v1/public/feed/sitemap", ext=ext)
