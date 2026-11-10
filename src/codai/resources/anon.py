"""``client.anon`` — guest chat without an account (``/v1/anon/*``).

Mirrors ``packages/sdk/src/resources/anon.ts``; wire contract in
``docs/design/anon-chat-contract.md``.

``challenge()`` and ``create_session()`` need no key (the gateway ignores the
bearer on them, so ``Codai(api_key="guest")`` works). The returned ``token``
(``anon_v1.*``) is then the ``api_key`` of a second client used for
``chat.completions.create(...)`` and ``anon.status()``. ``import_chat()`` runs on
a client built with the NEW account's API key right after sign-up.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from .._http import RequestExtensions
from ._base import Resource

__all__ = ["Anon", "solve_pow"]


def _leading_zero_bits_hex(hex_digest: str) -> int:
    bits = 0
    for ch in hex_digest:
        n = int(ch, 16)
        if n == 0:
            bits += 4
            continue
        return bits + (4 - n.bit_length())
    return bits


def solve_pow(nonce: str, device_id: str, bits: int, max_tries: int = 50_000_000) -> str:
    """Smallest decimal counter for which ``sha256_hex(f"{nonce}:{device_id}:{counter}")`` has at
    least ``bits`` leading zero bits. Returns it as a string (``proof.pow.counter``)."""
    for i in range(max_tries):
        counter = str(i)
        digest = hashlib.sha256(f"{nonce}:{device_id}:{counter}".encode("utf-8")).hexdigest()
        if _leading_zero_bits_hex(digest) >= bits:
            return counter
    raise RuntimeError("codai: proof-of-work not solved within max_tries")


class Anon(Resource):
    def challenge(self, surface: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/anon/challenge`` — single-use nonce (5 min) + ``pow_bits``. No key needed.
        ``surface`` is one of web, android, ios, desktop, vscode, wear, tv."""
        return self._json("/v1/anon/challenge", ext=ext, query={"surface": surface})

    def create_session(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/anon/session`` — exchange the nonce + one proof for a 2-hour guest token.
        ``accept_terms`` / ``confirm_adult`` must be ``True`` (the user accepted the click-wrap)."""
        return self._json("/v1/anon/session", ext=ext, method="POST", body=body)

    def status(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/anon/status`` — sessions/messages left today and ``budget_open``.
        Authenticates with the client's ``api_key``, which must be the guest token."""
        return self._json("/v1/anon/status", ext=ext)

    def import_chat(
        self,
        anon_token: str,
        messages: List[Dict[str, str]],
        title: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/anon/import`` — store the local guest history as a cloud session of the
        account. Call on a client built with the NEW account's API key; each guest token
        imports once (409 ``anon_already_imported``)."""
        body: Dict[str, Any] = {"anon_token": anon_token, "messages": list(messages)}
        if title is not None:
            body["title"] = title
        return self._json("/v1/anon/import", ext=ext, method="POST", body=body)

    def start_guest_session(
        self, surface: str, device_id: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """Challenge → proof-of-work → session, with ``accept_terms`` / ``confirm_adult`` set (only
        call after the user accepted the click-wrap). ``device_id`` is a UUID v4 generated once per
        install and persisted."""
        ch = self.challenge(surface, ext=ext)
        counter = solve_pow(ch["nonce"], device_id, int(ch["pow_bits"]))
        return self.create_session(
            {
                "surface": surface,
                "device_id": device_id,
                "nonce": ch["nonce"],
                "accept_terms": True,
                "confirm_adult": True,
                "proof": {"pow": {"counter": counter}},
            },
            ext=ext,
        )
