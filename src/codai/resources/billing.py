"""``client.billing`` — READ-ONLY billing overview (``/v1/billing``, ``/v1/billing/invoices``) and codai Studio
price quotes (``/v1/studio/quote``).

Nothing here starts a payment: plan, top-up and portal actions are browser links in
``billing["links"]``. Mirrors ``packages/sdk/src/resources/billing.ts``.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from .._http import RequestExtensions
from ._base import Resource, list_of

__all__ = ["Billing"]


class Billing(Resource):
    def get(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/billing`` — plan, wallet, auto top-up, cards and pay links (read-only)."""
        return self._json("/v1/billing", ext=ext)

    def invoices(self, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/billing/invoices`` — fiscal invoices and credit notes, newest first."""
        return list_of(self._json("/v1/billing/invoices", ext=ext, query={"limit": limit}), "invoices")

    def studio_quote(
        self,
        action: str,
        seconds: Optional[float] = None,
        resolution: Optional[str] = None,
        audio: Optional[bool] = None,
        quality: Optional[str] = None,
        pages: Optional[int] = None,
        chars: Optional[int] = None,
        model: Optional[str] = None,
        n: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``GET /v1/studio/quote`` — what a Studio ``action`` (``video``, ``music``, ``render``, ``preview``,
        ``frames``, ``captions``, ``speech``, ``image``) costs in USD and wallet EUR micros, plus your spendable
        balance and ``sufficient``. Paid Studio calls answer 402 ``insufficient_funds`` when it is false. Free."""
        query: Dict[str, Any] = {
            "action": action,
            "seconds": seconds,
            "resolution": resolution,
            "audio": None if audio is None else ("true" if audio else "false"),
            "quality": quality,
            "pages": pages,
            "chars": chars,
            "model": model,
            "n": n,
        }
        return self._json("/v1/studio/quote", ext=ext, query=query) or {}

    def watch_balance(
        self,
        threshold_eur: float,
        on_low: Callable[[float, Dict[str, Any]], None],
        interval_s: float = 60.0,
        max_checks: Optional[int] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> int:
        """Poll ``get()`` every ``interval_s`` seconds and call ``on_low(balance_eur, billing)``
        once each time ``wallet.balance_eur`` crosses below ``threshold_eur`` (again only after
        it went back to >= threshold). Read-only: never creates a checkout — offer
        ``billing["links"]["topup"]`` instead. Blocks; stops after ``max_checks`` polls
        (``None`` = forever) or when ``on_low`` raises ``StopIteration``. Failed polls go to
        ``on_error`` (default: ignored) and polling continues. Returns the number of polls."""
        low = False
        checks = 0
        while max_checks is None or checks < max_checks:
            if checks:
                sleep(max(1.0, interval_s))
            checks += 1
            try:
                billing = self.get()
            except Exception as err:  # noqa: BLE001 — a failed poll must not stop the watcher
                if on_error is not None:
                    on_error(err)
                continue
            balance = float(billing["wallet"]["balance_eur"])
            if balance < threshold_eur:
                if not low:
                    low = True
                    try:
                        on_low(balance, billing)
                    except StopIteration:
                        return checks
            else:
                low = False
        return checks
