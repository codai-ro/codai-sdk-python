"""Single source of truth for OpenAPI parity: every ``operationId`` in
``apps/docs/openapi/en/gateway.yaml`` maps to exactly one dotted method path on
the ``Codai`` client. ``tests/test_parity.py`` parses the YAML and fails when an
operation is missing, mapped to a non-callable, or when this table carries a key
the YAML does not have. Mirrors ``OPERATION_METHODS`` in the TypeScript SDK
(camelCase → snake_case)."""

from __future__ import annotations

from typing import Dict, FrozenSet

OPERATION_METHODS: Dict[str, str] = {
    # Chat & Completions
    "createChatCompletion": "chat.completions.create",
    "createResponse": "responses.create",
    "createMessage": "messages.create",
    # Embeddings & Audio
    "createEmbeddings": "embeddings.create",
    "createSystemOne": "system_one.create",
    "createTranscription": "audio.transcribe",
    "createSpeech": "audio.speech",
    "createEphemeralToken": "tokens.create",
    # Models
    "listModels": "models.list",
    # Health
    "getHealth": "health.get",
    "getHealthReady": "health.ready",
    "getStatus": "health.status",
    # Agents
    "runAgentSync": "agents.run",
    "createAgentRun": "agents.runs.create",
    "getAgentRunStats": "agents.runs.stats",
    "getAgentRun": "agents.runs.get",
    "listAgentRunSteps": "agents.runs.steps",
    "streamAgentRun": "agents.runs.stream",
    "cancelAgentRun": "agents.runs.cancel",
    # Tools
    "toolsSearch": "tools.search",
    "toolsFetch": "tools.fetch",
    # Tasks
    "listTasks": "tasks.list",
    "listPendingTasks": "tasks.pending",
    "getTaskStats": "tasks.stats",
    "getTask": "tasks.get",
    "confirmTask": "tasks.confirm",
    # Sessions
    "createSession": "sessions.create",
    "listSessions": "sessions.list",
    "getSession": "sessions.get",
    "updateSession": "sessions.update",
    "deleteSession": "sessions.delete",
    "listSessionEvents": "sessions.events.list",
    "appendSessionEvents": "sessions.events.append",
    "listSessionControls": "sessions.controls.list",
    "submitSessionControl": "sessions.controls.submit",
    "markSessionControlApplied": "sessions.controls.mark_applied",
    "dispatchToDevice": "sessions.dispatch",
    "claimSessionLease": "sessions.lease.acquire",
    "heartbeatSessionLease": "sessions.lease.renew",
    "releaseSessionLease": "sessions.lease.release",
    "streamSession": "sessions.stream",
    # Devices
    "getMyDispatchInbox": "devices.dispatch_inbox",
    "listDevices": "devices.list",
    "updateDevice": "devices.update",
    "deleteDevice": "devices.delete",
    # Hosts
    "listHosts": "hosts.list",
    "streamHost": "hosts.stream",
    "execOnHost": "hosts.exec",
    "postHostExecResult": "hosts.post_result",
    # Orgs & Sharing
    "listSessionsSharedWithMe": "sessions.shares.shared_with_me",
    "listSessionShares": "sessions.shares.list",
    "createSessionShare": "sessions.shares.create",
    "deleteSessionShare": "sessions.shares.delete",
    "createOrg": "orgs.create",
    "listOrgs": "orgs.list",
    "listOrgMembers": "orgs.members.list",
    "addOrgMember": "orgs.members.add",
    "removeOrgMember": "orgs.members.remove",
    # Projects
    "listProjects": "projects.list",
    "createProject": "projects.create",
    "getProject": "projects.get",
    "updateProject": "projects.update",
    "deleteProject": "projects.delete",
    # Environments
    "listEnvironments": "environments.list",
    "createEnvironment": "environments.create",
    "enrollEnvironment": "environments.enroll",
    "getEnvironment": "environments.get",
    "updateEnvironment": "environments.update",
    "startEnvironment": "environments.start",
    "stopEnvironment": "environments.stop",
    "archiveEnvironment": "environments.archive",
    "destroyEnvironment": "environments.destroy",
    "createEnvironmentEnrollToken": "environments.enroll_token",
    "listEnvironmentMembers": "environments.members.list",
    "addEnvironmentMember": "environments.members.add",
    "setMyEnvironmentSshKey": "environments.members.set_ssh_key",
    "setEnvironmentMemberRole": "environments.members.set_role",
    "removeEnvironmentMember": "environments.members.remove",
    "listEnvironmentPorts": "environments.ports.list",
    "setEnvironmentPort": "environments.ports.set",
    "removeEnvironmentPort": "environments.ports.remove",
    "listEnvironmentSecrets": "environments.secrets.list",
    "setEnvironmentSecret": "environments.secrets.set",
    "removeEnvironmentSecret": "environments.secrets.remove",
    "issueMyEnvironmentSshCert": "environments.members.ssh_cert",
    "getEnvironmentSshCa": "environments.ssh_ca",
    "listEnvironmentTasks": "environments.tasks.list",
    "createEnvironmentTask": "environments.tasks.create",
    "getEnvironmentTask": "environments.tasks.get",
    "listTriggers": "triggers.list",
    "createTrigger": "triggers.create",
    "updateTrigger": "triggers.update",
    "deleteTrigger": "triggers.delete",
    "rotateTriggerSecret": "triggers.rotate_secret",
    "setTriggerSecret": "triggers.set_secret",
    "testTrigger": "triggers.test",
    "listTriggerEvents": "triggers.events",
    "receiveTriggerHook": "triggers.fire_hook",
    "listNotifications": "notifications.list",
    "markNotificationsRead": "notifications.mark_read",
    # Account
    "getAccount": "account.get",
    "patchAccount": "account.update",
    "getReceipt": "receipt.get",
    "submitFeedback": "feedback.submit",
    "listPhoneModels": "phone_models.list",
}

# Operations whose SDK method is a generator (SSE-only endpoints).
STREAMING_OPERATIONS: FrozenSet[str] = frozenset({"streamAgentRun", "streamSession", "streamHost"})
