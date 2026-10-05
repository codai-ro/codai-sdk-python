"""Projects and environments: ``/v1/projects/*`` and ``/v1/environments/*`` (members, ports, secrets)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import HttpClient, RequestExtensions
from ._base import Resource, enc, list_of

__all__ = [
    "EnvironmentMembers",
    "EnvironmentPorts",
    "EnvironmentSecrets",
    "EnvironmentTasks",
    "Environments",
    "Projects",
]


def _env(env_id: str, suffix: str = "") -> str:
    return f"/v1/environments/{enc(env_id)}{suffix}"


# ------------------------------------------------------------------ projects
class Projects(Resource):
    def list(self, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/projects`` — projects you own plus those of your orgs, newest first."""
        return list_of(self._json("/v1/projects", ext=ext), "projects")

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/projects`` — returns the project; 409 ``slug_taken`` when the slug is already yours."""
        return self._json("/v1/projects", ext=ext, body=body)["project"]

    def get(self, project_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/projects/{id}`` — ``{"project": {...}, "environments": [...]}``."""
        return self._json(f"/v1/projects/{enc(project_id)}", ext=ext)

    def update(self, project_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/projects/{id}`` — owner or org owner/admin; the slug cannot change."""
        return self._json(f"/v1/projects/{enc(project_id)}", ext=ext, method="PATCH", body=body)["project"]

    def delete(self, project_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/projects/{id}`` — 409 ``project_has_environments`` until every environment is destroyed."""
        return self._json(f"/v1/projects/{enc(project_id)}", ext=ext, method="DELETE")


# -------------------------------------------------------------- environments
class EnvironmentMembers(Resource):
    def list(self, env_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/environments/{id}/members`` — any role."""
        return list_of(self._json(_env(env_id, "/members"), ext=ext), "members")

    def add(self, env_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/{id}/members`` — exactly one of ``user_id`` / ``email``."""
        return self._json(_env(env_id, "/members"), ext=ext, body=body)["member"]

    def set_ssh_key(self, env_id: str, public_key: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PUT /v1/environments/{id}/members/me/ssh-key`` — one ``authorized_keys`` line."""
        return self._json(
            _env(env_id, "/members/me/ssh-key"), ext=ext, method="PUT", body={"public_key": public_key}
        )

    def set_role(
        self, env_id: str, user_id: str, role: str, ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PATCH /v1/environments/{id}/members/{userId}`` — 409 ``last_owner`` on demoting the last owner."""
        return self._json(
            _env(env_id, f"/members/{enc(user_id)}"), ext=ext, method="PATCH", body={"role": role}
        )["member"]

    def remove(self, env_id: str, user_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/environments/{id}/members/{userId}`` — pass your own id to leave."""
        return self._json(_env(env_id, f"/members/{enc(user_id)}"), ext=ext, method="DELETE")

    def ssh_cert(self, env_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/{id}/members/me/ssh-cert`` — 12 h OpenSSH user certificate for your key."""
        return self._json(_env(env_id, "/members/me/ssh-cert"), ext=ext, method="POST", body=body, no_retry=True)


class EnvironmentTasks(Resource):
    def list(self, env_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/environments/{id}/tasks`` — fire-and-forget agent tasks run in the environment."""
        return self._json(_env(env_id, "/tasks"), ext=ext)

    def create(self, env_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/{id}/tasks`` — queued; you get a notification when it finishes."""
        return self._json(_env(env_id, "/tasks"), ext=ext, method="POST", body=body, no_retry=True)

    def get(self, env_id: str, task_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/environments/{id}/tasks/{taskId}``"""
        return self._json(_env(env_id, f"/tasks/{enc(task_id)}"), ext=ext)


class EnvironmentPorts(Resource):
    def list(self, env_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/environments/{id}/ports`` — published (forwarded) ports."""
        return list_of(self._json(_env(env_id, "/ports"), ext=ext), "ports")

    def set(
        self, env_id: str, port: int, body: Dict[str, Any], ext: Optional[RequestExtensions] = None
    ) -> Dict[str, Any]:
        """``PUT /v1/environments/{id}/ports/{port}`` — publish or change visibility (upsert)."""
        return self._json(_env(env_id, f"/ports/{enc(str(port))}"), ext=ext, method="PUT", body=body)["port"]

    def remove(self, env_id: str, port: int, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/environments/{id}/ports/{port}`` — unpublish."""
        return self._json(_env(env_id, f"/ports/{enc(str(port))}"), ext=ext, method="DELETE")


class EnvironmentSecrets(Resource):
    def list(self, env_id: str, ext: Optional[RequestExtensions] = None) -> List[Dict[str, Any]]:
        """``GET /v1/environments/{id}/secrets`` — names and timestamps only, never values."""
        return list_of(self._json(_env(env_id, "/secrets"), ext=ext), "secrets")

    def set(self, env_id: str, name: str, value: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PUT /v1/environments/{id}/secrets/{name}`` — upsert; ``name`` is ``ENV_STYLE``."""
        return self._json(_env(env_id, f"/secrets/{enc(name)}"), ext=ext, method="PUT", body={"value": value})

    def remove(self, env_id: str, name: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``DELETE /v1/environments/{id}/secrets/{name}``"""
        return self._json(_env(env_id, f"/secrets/{enc(name)}"), ext=ext, method="DELETE")


class Environments(Resource):
    def __init__(self, http: HttpClient) -> None:
        super().__init__(http)
        self.members = EnvironmentMembers(http)
        self.ports = EnvironmentPorts(http)
        self.secrets = EnvironmentSecrets(http)
        self.tasks = EnvironmentTasks(http)

    def ssh_ca(self, env_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/environments/{id}/ssh-ca`` — CA public keys to trust (``@cert-authority`` lines)."""
        return self._json(_env(env_id, "/ssh-ca"), ext=ext)

    def list(
        self,
        project_id: Optional[str] = None,
        for_user_id: Optional[str] = None,
        ext: Optional[RequestExtensions] = None,
    ) -> List[Dict[str, Any]]:
        """``GET /v1/environments?project_id=&for_user_id=me`` — newest first, every state."""
        raw = self._json("/v1/environments", ext=ext, query={"project_id": project_id, "for_user_id": for_user_id})
        return list_of(raw, "environments")

    def create(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments`` — ``byo`` starts ``pending``; managed providers start ``creating``."""
        return self._json("/v1/environments", ext=ext, body=body, no_retry=True)["environment"]

    def enroll(self, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/enroll`` — daemon side; the one-time ``codai_env_…`` token is the credential.

        The token is consumed on success, so this call is never retried.
        """
        return self._json("/v1/environments/enroll", ext=ext, body=body, no_retry=True)

    def get(self, env_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``GET /v1/environments/{id}`` — environment, your role, members, ports, recent events."""
        return self._json(_env(env_id), ext=ext)

    def update(self, env_id: str, body: Dict[str, Any], ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``PATCH /v1/environments/{id}`` — ``name`` and/or ``idle_timeout_minutes`` (5..1440)."""
        return self._json(_env(env_id), ext=ext, method="PATCH", body=body)["environment"]

    def start(self, env_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/{id}/start`` — managed providers only (``stopped`` → ``starting``)."""
        return self._json(_env(env_id, "/start"), ext=ext, method="POST")

    def stop(self, env_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/{id}/stop`` — managed providers only (``running`` → ``stopping``)."""
        return self._json(_env(env_id, "/stop"), ext=ext, method="POST")

    def archive(self, env_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/{id}/archive`` — keeps history, releases the machine."""
        return self._json(_env(env_id, "/archive"), ext=ext, method="POST")

    def destroy(self, env_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/{id}/destroy`` — owner only; terminal."""
        return self._json(_env(env_id, "/destroy"), ext=ext, method="POST")

    def enroll_token(self, env_id: str, ext: Optional[RequestExtensions] = None) -> Dict[str, Any]:
        """``POST /v1/environments/{id}/enroll-token`` — ``byo`` only; a 30-minute one-time token for ``enroll()``."""
        return self._json(_env(env_id, "/enroll-token"), ext=ext, method="POST", no_retry=True)
