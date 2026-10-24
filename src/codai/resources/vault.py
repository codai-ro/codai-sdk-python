"""``/v1/vault/*`` — the zero-knowledge credentials vault (V-01..V-10). The server stores only ciphertext built
client-side (bundles, envelopes, sealed keys); this resource moves those blobs. The agent broker calls (``catalog``,
``use``, ``http_call``, ``resolve``) never return secret values. Device approval keys (V-27) hold public keys only:
``vault.devices`` enrols, lists, renames and revokes them. Free."""

from __future__ import annotations

import base64
import hashlib
from typing import Any, Dict, List, Optional

from .._http import HttpClient, RequestExtensions
from ._base import Resource, enc, list_of

__all__ = ["Vault", "VaultDevices", "vault_resolve_digest", "vault_resolve_message", "vault_unlock_message"]


def vault_unlock_message(challenge: str, device_id_or_passkey: str) -> str:
    """The UTF-8 message an unlock proof covers: ``codai-vault/unlock/v1|<challenge>|<device_id or "passkey">``."""
    return f"codai-vault/unlock/v1|{challenge}|{device_id_or_passkey}"


def vault_resolve_digest(handles: List[str], action: str) -> str:
    """``base64url_nopad(SHA-256(handles joined by "\\n" + "\\n\\n" + action))``, handles and action exactly as sent."""
    raw = hashlib.sha256(("\n".join(handles) + "\n\n" + action).encode("utf-8")).digest()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def vault_resolve_message(challenge: str, device_id: str, digest: str) -> str:
    """The UTF-8 message a resolve proof covers: ``codai-vault/resolve/v1|<challenge>|<device_id>|<digest>``."""
    return f"codai-vault/resolve/v1|{challenge}|{device_id}|{digest}"


def _seg(base: str, item_id: str, suffix: str = "") -> str:
    return f"{base}/{enc(item_id)}{suffix}"


def _clean(body: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in body.items() if v is not None}


class VaultDevices(Resource):
    """``/v1/vault/devices/*`` — hardware-backed device approval keys (public keys only; revocation is instant)."""

    def challenge(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/devices/challenge`` — single-use enrolment nonce (``nonce``, ``expires_at``), 5 minutes."""
        return self._json("/v1/vault/devices/challenge", ext=ext, method="POST", body={}, no_retry=True)

    def enroll(
        self,
        device_id: str,
        kind: str,
        name: str,
        surface: str,
        public_key: str,
        nonce: str,
        vault_signature: str,
        device_signature: str,
        attestation: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/devices`` — enrol (or re-enrol) a device key; returns the ``device`` (HTTP 201).

        ``attestation`` is ``{"android_chain": [...]}`` (required for ``android_keystore``) or
        ``{"tpm": {"attestation": ..., "cert_chain": ...}}`` (optional for ``windows_hello``)."""
        body = _clean(
            {
                "device_id": device_id,
                "kind": kind,
                "name": name,
                "surface": surface,
                "public_key": public_key,
                "nonce": nonce,
                "vault_signature": vault_signature,
                "device_signature": device_signature,
                "attestation": attestation,
            }
        )
        r = self._json("/v1/vault/devices", ext=ext, method="POST", body=body, no_retry=True)
        return r["device"]

    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/vault/devices`` — your device keys, revoked ones included, newest first."""
        return list_of(self._json("/v1/vault/devices", ext=ext), "devices")

    def rename(self, device_id: str, name: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/vault/devices/{id}`` — change the display name (1-80 characters)."""
        path = _seg("/v1/vault/devices", device_id)
        return self._json(path, ext=ext, method="PATCH", body={"name": name}, no_retry=True)["device"]

    def revoke(self, device_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/vault/devices/{id}`` — revoke at once; later proofs answer 403 ``device_revoked``."""
        return self._json(_seg("/v1/vault/devices", device_id), ext=ext, method="DELETE")


class Vault(Resource):
    """Vault account, items, rules, grants, approvals and the agent broker."""

    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)
        self.devices = VaultDevices(http)

    def account(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/account`` — bundle, fingerprint, default tier, revision (404 ``vault_not_setup``)."""
        return self._json("/v1/vault/account", ext=ext)

    def put_account(
        self, bundle: Dict[str, Any], revision: Optional[int] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PUT /v1/vault/account`` — upload the client-built bundle; updates send the current ``revision``."""
        body = _clean({"bundle": bundle, "revision": revision})
        return self._json("/v1/vault/account", ext=ext, method="PUT", body=body, no_retry=True)

    def set_default_tier(self, default_tier: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/vault/settings`` — default approval tier (``t1``..``t4``) for items without a rule."""
        body = {"default_tier": default_tier}
        return self._json("/v1/vault/settings", ext=ext, method="PATCH", body=body, no_retry=True)

    def update_settings(
        self,
        default_tier: Optional[str] = None,
        guards: Optional[Dict[str, Any]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PATCH /v1/vault/settings`` — ``default_tier`` and/or partial anomaly ``guards`` (V-32).

        ``guards`` keys: ``new_host``, ``burst_max`` (0 = off), ``burst_window_s``, ``hour_start`` / ``hour_end``
        (both ``None`` = hours off), ``tz``; merged over the current values. Returns the effective
        ``{"default_tier", "guards"}``. An anomaly forces t4 (``anomaly:new_host|burst|hour``)."""
        if default_tier is None and guards is None:
            raise ValueError("send default_tier and/or guards")
        body: Dict[str, Any] = {}
        if default_tier is not None:
            body["default_tier"] = default_tier
        if guards is not None:
            body["guards"] = dict(guards)  # keep explicit None (hours off)
        return self._json("/v1/vault/settings", ext=ext, method="PATCH", body=body, no_retry=True)

    def lock(self, via: Optional[str] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/lock`` — panic: revoke live grants, deny pending approvals, lock the vault (V-35).

        Agent uses then answer ``vault_locked``; device keys stay enrolled. Idempotent. Returns ``locked_at``,
        ``grants_revoked``, ``approvals_denied``."""
        body = _clean({"via": via})
        return self._json("/v1/vault/lock", ext=ext, method="POST", body=body, no_retry=True)

    def unlock_challenge(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/unlock/challenge`` — single-use challenge (``challenge``, ``expires_at``), 5 minutes."""
        return self._json("/v1/vault/unlock/challenge", ext=ext, method="POST", body={}, no_retry=True)

    def unlock(
        self,
        challenge: str,
        proof: Dict[str, Any],
        via: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/unlock`` — end a lock with a hardware-backed proof over :func:`vault_unlock_message`.

        ``proof`` is ``{"type": "device", "device_id": ..., "signature": ...}`` (phone/desktop key; watch keys get
        403 ``wear_t3_only``) or ``{"type": "passkey", "response": ...}`` whose WebAuthn challenge is
        base64url(SHA-256(the message with ``passkey``)). Returns ``{"unlocked": True}``."""
        body = _clean({"challenge": challenge, "proof": proof, "via": via})
        return self._json("/v1/vault/unlock", ext=ext, method="POST", body=body, no_retry=True)

    def limits(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/vault/limits`` — per-handle caps (``item_id``, ``per_minute``, ``per_day``, ``units_per_day``)."""
        return list_of(self._json("/v1/vault/limits", ext=ext), "limits")

    def set_limits(
        self,
        item_id: str,
        per_minute: Optional[int],
        per_day: Optional[int],
        units_per_day: Optional[int],
        ext: Optional[RequestExtensions] = None,
    ) -> Optional[Dict[str, Any]]:
        """``PUT /v1/vault/items/{id}/limits`` — all three sent; ``None`` removes a cap, all ``None`` removes the limits
        (returns ``None``). Over a cap the broker calls raise 429 ``vault_rate_limited`` with ``Retry-After``; an
        ``http`` use costs 2 units, other modes 1."""
        body = {"per_minute": per_minute, "per_day": per_day, "units_per_day": units_per_day}
        path = _seg("/v1/vault/items", item_id, "/limits")
        return self._json(path, ext=ext, method="PUT", body=body, no_retry=True).get("limits")

    def vaults(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/vaults`` — vaults you belong to, with your role and sealed vault key."""
        return self._json("/v1/vault/vaults", ext=ext)

    def create_vault(
        self,
        vault_id: str,
        encrypted_meta: str,
        sealed_key: Dict[str, Any],
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/vaults`` — register a vault created client-side (HTTP 201)."""
        body = {"id": vault_id, "encrypted_meta": encrypted_meta, "sealed_key": sealed_key}
        return self._json("/v1/vault/vaults", ext=ext, method="POST", body=body, no_retry=True)

    def items(self, since: Optional[str] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/items`` — envelopes you can read; with ``since`` (ISO) only later changes + tombstones."""
        return self._json("/v1/vault/items", ext=ext, query={"since": since})

    def put_item(
        self, item_id: str, envelope: Dict[str, Any], ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PUT /v1/vault/items/{id}`` — store an envelope (new = revision 1, update = revision + 1)."""
        return self._json(_seg("/v1/vault/items", item_id), ext=ext, method="PUT", body=envelope, no_retry=True)

    def delete_item(self, item_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/vault/items/{id}`` — tombstone; revokes grants and drops the cloud copy."""
        return self._json(_seg("/v1/vault/items", item_id), ext=ext, method="DELETE")

    def set_item_cloud(
        self, item_id: str, item: Optional[Dict[str, Any]], ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PUT /v1/vault/items/{id}/cloud`` — owner only: the decrypted item to seal with KMS, or ``None``."""
        path = _seg("/v1/vault/items", item_id, "/cloud")
        return self._json(path, ext=ext, method="PUT", body={"item": item}, no_retry=True)

    def rules(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/rules`` — policy rules (item, agent glob, mode -> tier)."""
        return self._json("/v1/vault/rules", ext=ext)

    def create_rule(
        self,
        tier: str,
        item_id: Optional[str] = None,
        agent: Optional[str] = None,
        mode: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/rules`` — add a rule (HTTP 201); host binding and honeytokens cannot be overridden."""
        body = _clean({"tier": tier, "item_id": item_id, "agent": agent, "mode": mode})
        return self._json("/v1/vault/rules", ext=ext, method="POST", body=body, no_retry=True)

    def delete_rule(self, rule_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/vault/rules/{id}``."""
        return self._json(_seg("/v1/vault/rules", rule_id), ext=ext, method="DELETE")

    def grants(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/grants`` — standing grants created by your approvals."""
        return self._json("/v1/vault/grants", ext=ext)

    def revoke_grant(self, grant_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/vault/grants/{id}`` — revoke immediately."""
        return self._json(_seg("/v1/vault/grants", grant_id), ext=ext, method="DELETE")

    def revoke_task_grants(self, task: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/grants/revoke-task`` — revoke every live grant of a task / session; ``{"revoked": n}``."""
        body = {"task": task}
        return self._json("/v1/vault/grants/revoke-task", ext=ext, method="POST", body=body, no_retry=True)

    def events(self, limit: Optional[int] = None, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/events`` — append-only audit log (never contains secret values)."""
        return self._json("/v1/vault/events", ext=ext, query={"limit": limit})

    def approvals(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/approvals`` — agent requests waiting for your decision."""
        return self._json("/v1/vault/approvals", ext=ext)

    def approval(self, approval_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/approvals/{id}`` — pending, approved, denied or expired."""
        return self._json(_seg("/v1/vault/approvals", approval_id), ext=ext)

    def decide(
        self,
        approval_id: str,
        decision: str,
        scope: str,
        signature: Optional[str] = None,
        step_up_acr: Optional[str] = None,
        via: Optional[str] = None,
        proof: Optional[Dict[str, Any]] = None,
        match_number: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/approvals/{id}/decide`` — send ``signature`` (v1 vault key) or ``proof``, never both.

        ``proof`` is ``{"type": "device", "device_id": ..., "signature": ...}`` (device key over the v2 message) or
        ``{"type": "passkey", "response": <AuthenticationResponseJSON>}``. A deny needs neither; a t4 approve needs a
        device or passkey proof, and Wear devices may approve t3 only. ``step_up_acr`` is deprecated: the gateway
        accepts and ignores it. ``match_number`` is the 2-digit number the user tapped (V-31); it needs a ``proof``
        over the approve/v3 message and is required for a t4 approve on requests that carry a preview."""
        if signature is not None and proof is not None:
            raise ValueError("send either signature or proof, not both")
        body = _clean(
            {
                "decision": decision,
                "scope": scope,
                "signature": signature,
                "step_up_acr": step_up_acr,
                "via": via,
                "proof": proof,
                "match_number": match_number,
            }
        )
        path = _seg("/v1/vault/approvals", approval_id, "/decide")
        return self._json(path, ext=ext, method="POST", body=body, no_retry=True)

    def catalog(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/catalog`` — items exposed to agents; no values."""
        return self._json("/v1/vault/catalog", ext=ext)

    def use(
        self,
        handle: str,
        mode: str,
        action: str,
        host: Optional[str] = None,
        purpose: Optional[str] = None,
        provenance: Optional[str] = None,
        chain: Optional[List[str]] = None,
        task: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/use`` — a policy decision for one use; t3/t4 return a pending approval id."""
        body = _clean(
            {
                "handle": handle,
                "mode": mode,
                "action": action,
                "host": host,
                "purpose": purpose,
                "provenance": provenance,
                "chain": chain,
                "task": task,
            }
        )
        return self._json("/v1/vault/use", ext=ext, method="POST", body=body, no_retry=True)

    def http_call(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/http`` — brokered HTTPS call (``handle``, ``url``, ...); HTTP 202 = approval required."""
        return self._json("/v1/vault/http", ext=ext, method="POST", body=_clean(body), no_retry=True) or {}

    def resolve_challenge(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/resolve/challenge`` — codai local brokers only; single-use challenge, 120 seconds."""
        return self._json("/v1/vault/resolve/challenge", ext=ext, method="POST", body={}, no_retry=True)

    def resolve(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/resolve`` — codai local brokers only; HTTP 202 = approval required.

        ``body["proof"]`` is required: ``{"device_id", "challenge", "signature"}`` where the device key signs
        :func:`vault_resolve_message` over a fresh :meth:`resolve_challenge` (400 ``proof_required`` /
        ``invalid_challenge``, 403 ``invalid_device_proof``).
        """
        return self._json("/v1/vault/resolve", ext=ext, method="POST", body=_clean(body), no_retry=True) or {}
