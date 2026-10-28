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

__all__ = [
    "Vault",
    "VaultAddRequests",
    "VaultDevices",
    "VaultEmergency",
    "VaultMembers",
    "vault_approve_message_v4",
    "vault_resolve_digest",
    "vault_resolve_message",
    "vault_unlock_message",
]


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


def vault_approve_message_v4(
    approval_id: str,
    action_hash: str,
    decision: str,
    approver_user_id: str,
    device_id_or_passkey: str,
    preview_digest: str,
) -> str:
    """The UTF-8 message a quorum vote proof covers (approve/v4, V-33):
    ``codai-vault/approve/v4|<approval_id>|<action_hash>|<decision>|once|<approver_user_id>|<device_id>|<preview_digest>``.
    ``device_id_or_passkey`` is the approver's enrolled device id or ``passkey``."""
    return (
        f"codai-vault/approve/v4|{approval_id}|{action_hash}|{decision}|once|"
        f"{approver_user_id}|{device_id_or_passkey}|{preview_digest}"
    )


_UNSET: Any = object()


def _seg(base: str, item_id: str, suffix: str = "") -> str:
    return f"{base}/{enc(item_id)}{suffix}"


def _clean(body: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in body.items() if v is not None}


class VaultMembers(Resource):
    """``/v1/vault/vaults/{id}/members/*`` — org vault members (V-33). Vault keys are sealed client-side."""

    @staticmethod
    def _path(vault_id: str, user_id: Optional[str] = None) -> str:
        base = _seg("/v1/vault/vaults", vault_id, "/members")
        return base if user_id is None else f"{base}/{enc(user_id)}"

    def list(self, vault_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/vault/vaults/{id}/members`` — members, roles, confirmed fingerprints, key epochs."""
        return list_of(self._json(self._path(vault_id), ext=ext), "members")

    def candidates(self, vault_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/vault/vaults/{id}/candidates`` — owner/manager: org members with a vault account not yet in the
        vault (``user_id``, ``email``, ``name``, ``fingerprint``, ``public_keys``)."""
        return list_of(self._json(_seg("/v1/vault/vaults", vault_id, "/candidates"), ext=ext), "candidates")

    def add(
        self,
        vault_id: str,
        user_id: str,
        role: str,
        sealed_key: Dict[str, Any],
        fingerprint: str,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PUT /v1/vault/vaults/{id}/members/{userId}`` — seal the vault key to a member (``role`` ``manager``,
        ``editor`` or ``viewer``) after their ``fingerprint`` was shown and confirmed; 409 ``fingerprint_changed``."""
        body = {"role": role, "sealed_key": sealed_key, "fingerprint": fingerprint}
        return self._json(self._path(vault_id, user_id), ext=ext, method="PUT", body=body, no_retry=True)

    def update(
        self, vault_id: str, user_id: str, role: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PATCH /v1/vault/vaults/{id}/members/{userId}`` — change the role."""
        path = self._path(vault_id, user_id)
        return self._json(path, ext=ext, method="PATCH", body={"role": role}, no_retry=True)

    def remove(self, vault_id: str, user_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/vault/vaults/{id}/members/{userId}`` — remove (or leave); marks the vault for key rotation."""
        return self._json(self._path(vault_id, user_id), ext=ext, method="DELETE")


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


class VaultAddRequests(Resource):
    """``/v1/vault/add-requests/*`` — an agent asks the user to add a missing secret (V-17). No secret passes here."""

    def create(
        self,
        kind: str,
        title: str,
        purpose: str,
        slug: Optional[str] = None,
        hosts: Optional[List[str]] = None,
        env_var: Optional[str] = None,
        fields: Optional[List[str]] = None,
        task: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/add-requests`` — ``{id, url, status, expires_at}`` (HTTP 201); ``url`` is the hub link to
        show the user, ``None`` when an equivalent pending request was reused."""
        body = _clean(
            {
                "kind": kind,
                "title": title,
                "purpose": purpose,
                "slug": slug,
                "hosts": hosts,
                "env_var": env_var,
                "fields": fields,
                "task": task,
            }
        )
        return self._json("/v1/vault/add-requests", ext=ext, method="POST", body=body, no_retry=True)

    def get(self, request_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/add-requests/{id}`` — poll; once ``completed``, ``handle`` is the new ``{{vault:<slug>}}``."""
        return self._json(_seg("/v1/vault/add-requests", request_id), ext=ext)

    def cancel(self, request_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/vault/add-requests/{id}`` — cancel a pending request."""
        return self._json(_seg("/v1/vault/add-requests", request_id), ext=ext, method="DELETE")

    def lookup(self, token: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/add-requests/lookup`` — the full request by link token, signed-in owner only (404 else)."""
        body = {"token": token}
        return self._json("/v1/vault/add-requests/lookup", ext=ext, method="POST", body=body, no_retry=True)

    def complete(self, request_id: str, item_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/add-requests/{id}/complete`` — link the item you added; idempotent for the same item."""
        path = _seg("/v1/vault/add-requests", request_id, "/complete")
        return self._json(path, ext=ext, method="POST", body={"item_id": item_id}, no_retry=True)


class VaultEmergency(Resource):
    """``/v1/vault/emergency/*`` — emergency access (V-23): invite, seal vault keys, request, wait, release."""

    def _post(self, path: str, body: Dict[str, Any], ext: Optional[RequestExtensions]) -> Dict[str, Any]:
        return self._json(path, ext=ext, method="POST", body=body, no_retry=True)

    def list(self, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/emergency`` — ``{"outgoing": [...], "incoming": [...]}`` (revoked omitted)."""
        return self._json("/v1/vault/emergency", ext=ext)

    def invite(
        self,
        email: str,
        delay_hours: int,
        vault_ids: Optional[List[str]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/emergency`` — always HTTP 202 ``{"id"}`` (enumeration-safe); ``delay_hours`` 24, 48 or 72."""
        body = _clean({"email": email, "delay_hours": delay_hours, "vault_ids": vault_ids})
        return self._post("/v1/vault/emergency", body, ext)

    def accept(self, token: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/emergency/accept`` — the contact accepts with the emailed token (needs a vault account)."""
        return self._post("/v1/vault/emergency/accept", {"token": token}, ext)

    def seal(
        self,
        contact_id: str,
        grantee_fingerprint: str,
        sealed_keys: Dict[str, Dict[str, Any]],
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PUT /v1/vault/emergency/{id}/seal`` — grantor uploads vault keys sealed client-side to the contact
        (``{vault_id: {"alg", "ct", "wrapped"}}``)."""
        body = {"grantee_fingerprint": grantee_fingerprint, "sealed_keys": sealed_keys}
        path = _seg("/v1/vault/emergency", contact_id, "/seal")
        return self._json(path, ext=ext, method="PUT", body=body, no_retry=True)

    def update(
        self,
        contact_id: str,
        delay_hours: Optional[int] = None,
        vault_ids: Optional[List[str]] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PATCH /v1/vault/emergency/{id}`` — change the wait and/or the vaults (a vault change requires re-sealing)."""
        if delay_hours is None and vault_ids is None:
            raise ValueError("send delay_hours and/or vault_ids")
        body = _clean({"delay_hours": delay_hours, "vault_ids": vault_ids})
        path = _seg("/v1/vault/emergency", contact_id)
        return self._json(path, ext=ext, method="PATCH", body=body, no_retry=True)

    def revoke(self, contact_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/vault/emergency/{id}`` — grantor revokes or the contact declines."""
        return self._json(_seg("/v1/vault/emergency", contact_id), ext=ext, method="DELETE")

    def request(
        self, contact_id: str, reason: Optional[str] = None, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/vault/emergency/{id}/request`` — contact starts the wait; released at ``release_at`` unless
        denied."""
        return self._post(_seg("/v1/vault/emergency", contact_id, "/request"), _clean({"reason": reason}), ext)

    def deny(self, contact_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/emergency/{id}/deny`` — grantor denies a pending request (back to ``sealed``)."""
        return self._post(_seg("/v1/vault/emergency", contact_id, "/deny"), {}, ext)

    def approve(self, contact_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/emergency/{id}/approve`` — grantor grants a pending request now."""
        return self._post(_seg("/v1/vault/emergency", contact_id, "/approve"), {}, ext)

    def vault_data(self, contact_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/vault/emergency/{id}/vault-data`` — contact, status ``granted``: sealed vault keys + envelopes."""
        return self._json(_seg("/v1/vault/emergency", contact_id, "/vault-data"), ext=ext)


class Vault(Resource):
    """Vault account, items, rules, grants, approvals and the agent broker."""

    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)
        self.devices = VaultDevices(http)
        self.add_requests = VaultAddRequests(http)
        self.emergency = VaultEmergency(http)
        self.members = VaultMembers(http)

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
        digest_opt_out: Optional[bool] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PATCH /v1/vault/settings`` — ``default_tier``, partial anomaly ``guards`` (V-32) and/or
        ``digest_opt_out`` (weekly digest email, V-36).

        ``guards`` keys: ``new_host``, ``burst_max`` (0 = off), ``burst_window_s``, ``hour_start`` / ``hour_end``
        (both ``None`` = hours off), ``tz``; merged over the current values. Returns the effective
        settings. An anomaly forces t4 (``anomaly:new_host|burst|hour``)."""
        if default_tier is None and guards is None and digest_opt_out is None:
            raise ValueError("send default_tier, guards and/or digest_opt_out")
        body: Dict[str, Any] = {}
        if default_tier is not None:
            body["default_tier"] = default_tier
        if guards is not None:
            body["guards"] = dict(guards)  # keep explicit None (hours off)
        if digest_opt_out is not None:
            body["digest_opt_out"] = digest_opt_out
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
        """``GET /v1/vault/vaults`` — vaults you belong to, with your role and sealed vault key; org vaults add
        ``org_id``, ``quorum``, ``rotation_needed_at`` and ``key_epoch``."""
        return self._json("/v1/vault/vaults", ext=ext)

    def create_vault(
        self,
        vault_id: str,
        encrypted_meta: str,
        sealed_key: Dict[str, Any],
        org_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/vaults`` — register a vault created client-side (HTTP 201); ``org_id`` makes it an org
        vault (org owner/admin only)."""
        body = _clean({"id": vault_id, "encrypted_meta": encrypted_meta, "sealed_key": sealed_key, "org_id": org_id})
        return self._json("/v1/vault/vaults", ext=ext, method="POST", body=body, no_retry=True)

    def rotate_key(
        self,
        vault_id: str,
        key_epoch: int,
        encrypted_meta: str,
        members: List[Dict[str, Any]],
        items: List[Dict[str, Any]],
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/vaults/{id}/rotate`` — owner/manager: replace the vault key in one transaction.

        ``members`` = ``[{"user_id", "sealed_key"}]`` for every member, ``items`` = ``[{"id", "revision",
        "wrapped_key", "ciphertext"}]`` for every live item (max 2000), ``key_epoch`` = current + 1. A missing member
        or item raises 409 ``rotation_incomplete``. Clears ``rotation_needed_at``."""
        body = {"key_epoch": key_epoch, "encrypted_meta": encrypted_meta, "members": members, "items": items}
        path = _seg("/v1/vault/vaults", vault_id, "/rotate")
        return self._json(path, ext=ext, method="POST", body=body, no_retry=True)

    def set_quorum(
        self,
        vault_id: str,
        m: Optional[int],
        scope: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PUT /v1/vault/vaults/{id}/quorum`` — owner: ``m`` 2..9 with ``scope`` ``critical`` or ``high``; ``m=None``
        turns quorum off."""
        body: Dict[str, Any] = {"m": None} if m is None else _clean({"m": m, "scope": scope})
        path = _seg("/v1/vault/vaults", vault_id, "/quorum")
        return self._json(path, ext=ext, method="PUT", body=body, no_retry=True)

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

    def vote(
        self,
        approval_id: str,
        decision: str,
        proof: Dict[str, Any],
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/approvals/{id}/vote`` — quorum approvals (V-33): your vote with an approve/v4 ``proof``
        (:func:`vault_approve_message_v4`). A deny ends the request; the M-th approve grants one use. 409
        ``already_voted`` / ``not_pending``; :meth:`decide` on a quorum approval raises 409 ``quorum_required``."""
        body = {"decision": decision, "proof": proof}
        path = _seg("/v1/vault/approvals", approval_id, "/vote")
        return self._json(path, ext=ext, method="POST", body=body, no_retry=True)

    def simulate_policy(
        self,
        rules: Optional[List[Dict[str, Any]]] = None,
        default_tier: Optional[str] = None,
        since: Optional[str] = None,
        limit: Optional[int] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``POST /v1/vault/policy/simulate`` — replay past uses under draft ``rules`` / ``default_tier`` (read-only).
        Returns ``{"evaluated", "changed", "grants": "none", "rows"}``; grants and anomaly guards are not replayed."""
        body = _clean({"rules": rules, "default_tier": default_tier, "since": since, "limit": limit})
        return self._json("/v1/vault/policy/simulate", ext=ext, method="POST", body=body, no_retry=True)

    def receipt_keys(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/vault/receipts/keys`` — ES256 public keys (``kid``, ``alg``, ``pem``) that sign vault receipts."""
        return list_of(self._json("/v1/vault/receipts/keys", ext=ext), "keys")

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

    def hibp_range(self, prefix: str, ext: Optional[RequestExtensions] = None) -> str:
        """``GET /v1/vault/hibp/range/{prefix}`` — padded HIBP range (``SUFFIX:COUNT`` lines) for the first 5 hex chars
        of a SHA-1; compare locally, the password never leaves the client. 300 calls per user per hour."""
        if len(prefix) != 5 or any(c not in "0123456789abcdefABCDEF" for c in prefix):
            raise ValueError("prefix must be 5 hex characters")
        res = self._http.request(f"/v1/vault/hibp/range/{prefix.upper()}", ext=ext)
        return res.data.decode("utf-8")

    def rotation(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/vault/rotation`` — rotation queue: breached, overdue, soonest due; unscheduled last."""
        return list_of(self._json("/v1/vault/rotation", ext=ext), "items")

    def set_rotation(
        self,
        item_id: str,
        interval_days: Any = _UNSET,
        provider: Any = _UNSET,
        snoozed_until: Any = _UNSET,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PUT /v1/vault/items/{id}/rotation`` — any of ``interval_days`` (1-730), ``provider``, ``snoozed_until``
        (ISO); pass ``None`` to clear a value, omit it to leave it unchanged."""
        body = {
            k: v
            for k, v in {"interval_days": interval_days, "provider": provider, "snoozed_until": snoozed_until}.items()
            if v is not _UNSET
        }
        if not body:
            raise ValueError("send interval_days, provider and/or snoozed_until")
        path = _seg("/v1/vault/items", item_id, "/rotation")
        return self._json(path, ext=ext, method="PUT", body=body, no_retry=True)

    def mark_rotated(self, item_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/items/{id}/rotated`` — ``rotated_at`` = now, breach flag cleared."""
        path = _seg("/v1/vault/items", item_id, "/rotated")
        return self._json(path, ext=ext, method="POST", body={}, no_retry=True)

    def report_breaches(
        self, results: List[Dict[str, Any]], ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``POST /v1/vault/rotation/breach-report`` — local HIBP results ``[{"item_id", "count"}]`` (0 = clean),
        up to 500; returns ``{"recorded", "newly_breached"}``."""
        body = {"results": results}
        return self._json("/v1/vault/rotation/breach-report", ext=ext, method="POST", body=body, no_retry=True)

    def derivers(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/vault/derivers`` — derivers on items in your vaults (config only, never values)."""
        return list_of(self._json("/v1/vault/derivers", ext=ext), "derivers")

    def set_deriver(
        self,
        item_id: str,
        provider: str,
        config: Dict[str, Any],
        max_ttl_s: int,
        ext: Optional[RequestExtensions] = None,
    ) -> Dict[str, Any]:
        """``PUT /v1/vault/items/{id}/deriver`` — owner only; ``provider`` is ``aws_sts``, ``gcp_sa``, ``cloudflare`` or
        ``github_app``; config validated per provider. Returns the ``deriver``."""
        body = {"provider": provider, "config": config, "max_ttl_s": max_ttl_s}
        path = _seg("/v1/vault/items", item_id, "/deriver")
        return self._json(path, ext=ext, method="PUT", body=body, no_retry=True)["deriver"]

    def delete_deriver(self, item_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/vault/items/{id}/deriver`` — owner only; 404 when there is none."""
        return self._json(_seg("/v1/vault/items", item_id, "/deriver"), ext=ext, method="DELETE")

    def derive(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/vault/derive`` — codai local brokers only: a short-lived credential from a root item's deriver.

        Same ``proof`` as :meth:`resolve`, over ``handles = [handle]``. HTTP 202 (approval required) is returned as
        ``{"status": "approval_required", ...}``, not raised."""
        return self._json("/v1/vault/derive", ext=ext, method="POST", body=_clean(body), no_retry=True) or {}
