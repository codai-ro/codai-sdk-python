"""Typed dictionaries for the codai gateway API.

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

class _VqaRunInputRequired(TypedDict):
    id: str
    tier: str
    driver: str


class VqaRunInput(_VqaRunInputRequired, total=False):
    sha: str
    pr: Optional[int]
    target: str
    shards: int
    screens: int


class _VqaRunFinishRequired(TypedDict):
    status: Literal['passed', 'failed', 'cancelled']
    wallSeconds: float
    costUsd: float


class VqaRunFinish(_VqaRunFinishRequired, total=False):
    aiCostUsd: float
    manifestKey: str


class _VqaRunRequired(TypedDict):
    id: str
    tier: str
    driver: str
    status: str


class VqaRun(_VqaRunRequired, total=False):
    """A capture run."""
    captures: int
    issues: int
    failed: int
    changed: int


class _VqaIssueInputRequired(TypedDict):
    rule: str
    severity: Literal['P0', 'P1', 'P2', 'P3']
    source: str
    message: str
    fingerprint: str


class VqaIssueInput(_VqaIssueInputRequired, total=False):
    box: Optional[List[float]]
    sel: Optional[str]
    evidence: Dict[str, Any]


class VqaCaptureInputBlobs(TypedDict, total=False):
    full: Optional[str]
    thumb: Optional[str]
    video: Optional[str]
    trace: Optional[str]
    dom: Optional[str]


class _VqaCaptureInputDiffRequired(TypedDict):
    kind: str
    percent: float


class VqaCaptureInputDiff(_VqaCaptureInputDiffRequired, total=False):
    blob: Optional[str]


class _VqaCaptureInputRequired(TypedDict):
    screenId: str
    surface: str
    config: str
    ok: bool
    width: int
    height: int
    dpr: float
    theme: str
    locale: str
    blobs: VqaCaptureInputBlobs
    issues: List[VqaIssueInput]


class VqaCaptureInput(_VqaCaptureInputRequired, total=False):
    state: str
    error: Optional[str]
    diff: Optional[VqaCaptureInputDiff]
    vitals: Dict[str, Optional[float]]
    navigatedTo: List[str]


class VqaCaptureResult(TypedDict):
    captureId: int
    health: int
    created: List[int]
    seen: List[int]
    verified: List[int]


class VqaCaptureUrls(TypedDict, total=False):
    full: Optional[str]
    thumb: Optional[str]
    video: Optional[str]
    trace: Optional[str]
    dom: Optional[str]
    diff: Optional[str]


class _VqaCaptureRequired(TypedDict):
    id: int
    screenId: str
    config: str
    urls: VqaCaptureUrls


class VqaCapture(_VqaCaptureRequired, total=False):
    """A stored capture; `urls` are hub blob-proxy links."""
    runId: str
    surface: str
    health: int


class _VqaFindingRequired(TypedDict):
    number: int
    ref: str
    status: Literal['todo', 'in-progress', 'fixed', 'verified', 'wontfix']
    severity: Literal['P0', 'P1', 'P2', 'P3']
    screenId: str
    title: str
    atlasUrl: str


class VqaFinding(_VqaFindingRequired, total=False):
    """A visual QA finding, addressed as `UI-<n>`."""
    rule: str
    surface: str
    config: Optional[str]
    captureId: Optional[int]
    claimedBy: Optional[str]
    fixRef: Optional[str]


class VqaFindingCount(TypedDict):
    surface: str
    severity: str
    status: str
    n: int


class MemoryItem(TypedDict):
    """One stored memory."""
    id: str
    tier: Literal['semantic', 'episodic', 'procedural', 'graph']
    content: str
    importance: float
    createdAt: str


class MemoryList(TypedDict):
    memories: List[MemoryItem]
    total: int


class MemoryHit(TypedDict):
    """One search result."""
    id: str
    tier: Literal['semantic', 'episodic', 'procedural', 'graph']
    content: str
    relevance: float


class MemorySearchResult(TypedDict):
    memories: List[MemoryHit]


class _ListRequired(TypedDict):
    id: str
    name: str
    preset: Literal['inbox', 'wishlist', 'notes', 'custom']
    icon: Optional[str]
    color: Optional[str]
    position: int
    show_in_share: bool
    price_watch: bool
    archived: bool
    created_at: str
    updated_at: str


class List(_ListRequired, total=False):
    """A list. Presets (`inbox`, `wishlist`, `notes`) cannot be deleted; your own lists have `preset` = `custom`."""
    item_count: int


class ListItemEnrichmentPrice(TypedDict):
    amount: float
    currency: str


class ListItemEnrichment(TypedDict, total=False):
    """Filled in the background by link unfurling, the Inbox suggestion and the price watch. Every field is optional."""
    siteName: str
    image: str
    description: str
    price: ListItemEnrichmentPrice
    availability: Literal['in_stock', 'out_of_stock', 'preorder', 'unknown']
    suggestedListId: str
    fetchedAt: str
    watchedAt: str
    error: str


class ListItemSource(TypedDict, total=False):
    """Where the item came from."""
    app: str
    device: str
    surface: Literal['phone', 'desktop', 'hub', 'mcp', 'cli', 'wear', 'api']


class ListItem(TypedDict):
    """One item of a list."""
    id: str
    list_id: str
    client_id: Optional[str]
    kind: Literal['text', 'link', 'product', 'media', 'file']
    title: Optional[str]
    body: Optional[str]
    url: Optional[str]
    media_key: Optional[str]
    mime: Optional[str]
    enrichment: ListItemEnrichment
    source: ListItemSource
    pinned: bool
    done: bool
    remind_at: Optional[str]
    created_at: str
    updated_at: str


class _ListCreateInputRequired(TypedDict):
    name: str


class ListCreateInput(_ListCreateInputRequired, total=False):
    icon: Optional[str]
    color: Optional[str]
    show_in_share: bool
    price_watch: bool


class ListPatchInput(TypedDict, total=False):
    name: str
    icon: Optional[str]
    color: Optional[str]
    show_in_share: bool
    price_watch: bool
    archived: bool


class ListItemInput(TypedDict, total=False):
    """At least one of `text`, `url` or `media_key` is required."""
    text: str
    url: str
    title: str
    media_key: str
    mime: str
    client_id: str
    remind_at: Optional[str]
    source: ListItemSource


class ListItemPatchInput(TypedDict, total=False):
    title: Optional[str]
    body: Optional[str]
    done: bool
    pinned: bool
    remind_at: Optional[str]
    list_id: str


class ListItemCreated(TypedDict):
    item: ListItem
    created: bool


class ListOk(TypedDict):
    ok: Literal[True]


class _FeedPostImageRequired(TypedDict):
    url: str


class FeedPostImage(_FeedPostImageRequired, total=False):
    width: int
    height: int


class FeedPostAuthor(TypedDict):
    username: Optional[str]
    is_me: bool
    badge: Optional[Literal['team']]


class FeedLinkPreview(TypedDict):
    """Preview of a link, fetched once when the post was created."""
    url: str
    title: Optional[str]
    description: Optional[str]
    site_name: Optional[str]
    image_url: Optional[str]


class FeedPost(TypedDict):
    """A feed post. The only author identity exposed is the public username."""
    id: str
    kind: Literal['project', 'seeking', 'idea']
    body: str
    link_url: Optional[str]
    images: List[FeedPostImage]
    author: FeedPostAuthor
    like_count: int
    liked_by_me: bool
    status: Literal['visible', 'hidden', 'removed']
    moderation_reason: Optional[str]
    created_at: str
    lang: Optional[Literal['en', 'ro']]
    comment_count: int
    link_preview: Optional[FeedLinkPreview]


class FeedPage(TypedDict):
    posts: List[FeedPost]
    next_cursor: Optional[str]


class FeedMe(TypedDict):
    username: Optional[str]
    suggested_username: Optional[str]
    guidelines_version: str


class _FeedPostCreateInputRequired(TypedDict):
    kind: Literal['project', 'seeking', 'idea']
    body: str
    guidelines_version: str


class FeedPostCreateInput(_FeedPostCreateInputRequired, total=False):
    link_url: Optional[str]
    images: List[str]
    client_id: str


class _FeedReportInputRequired(TypedDict):
    reason: Literal['spam', 'harassment', 'hate', 'sexual', 'violence', 'illegal', 'ip', 'other']


class FeedReportInput(_FeedReportInputRequired, total=False):
    details: str


class FeedLikeState(TypedDict):
    like_count: int
    liked_by_me: bool


class FeedBlock(TypedDict):
    username: Optional[str]
    created_at: str


class FeedCommentAuthor(TypedDict):
    username: Optional[str]
    is_me: bool
    badge: Optional[Literal['team']]


class FeedComment(TypedDict):
    """A comment on a feed post. The only author identity exposed is the public username."""
    id: str
    post_id: str
    body: str
    author: FeedCommentAuthor
    status: Literal['visible', 'hidden', 'removed']
    created_at: str


class FeedCommentPage(TypedDict):
    comments: List[FeedComment]
    next_cursor: Optional[str]


class _FeedCommentCreateInputRequired(TypedDict):
    body: str
    guidelines_version: str


class FeedCommentCreateInput(_FeedCommentCreateInputRequired, total=False):
    client_id: str


class FeedCommentCreated(TypedDict):
    comment: FeedComment
    comment_count: int


class FeedProfile(TypedDict):
    """A public feed profile. Never includes a name, e-mail, avatar or user id."""
    username: str
    badge: Optional[Literal['team']]
    is_me: bool
    blocked: bool
    post_count: int
    first_post_at: Optional[str]


class FeedProfilePage(TypedDict):
    profile: FeedProfile
    posts: List[FeedPost]
    next_cursor: Optional[str]


class ShareRequest(TypedDict, total=False):
    """Same fields as an item, plus the target. Without `list_id` and `preset` the share goes to Inbox in auto mode."""
    text: str
    url: str
    title: str
    media_key: str
    mime: str
    client_id: str
    remind_at: Optional[str]
    source: ListItemSource
    list_id: str
    preset: Literal['inbox', 'wishlist', 'notes']
    auto: bool


class ShareResponse(TypedDict):
    item: ListItem
    list: List
    created: bool


class _HeartbeatMonitorRequired(TypedDict):
    id: str
    name: str
    period_s: int
    grace_s: int
    status: Literal['new', 'up', 'late', 'down', 'paused']


class HeartbeatMonitor(_HeartbeatMonitorRequired, total=False):
    """A heartbeat monitor."""
    tz: Optional[str]
    last_ping_at: Optional[str]
    last_start_at: Optional[str]
    last_exit_code: Optional[int]
    ping_url: str
    created_at: Optional[str]
    updated_at: Optional[str]


class _ScheduleInputRequired(TypedDict):
    name: str
    kind: Literal['agent', 'shell', 'http', 'chain', 'phone_action']
    spec: Dict[str, Any]
    trigger: Dict[str, Any]


class ScheduleInput(_ScheduleInputRequired, total=False):
    """Schedule fields. `kind` selects the shape of `spec`: agent `{prompt, skill?, permissions?}`, shell `{command, …"""
    description: Optional[str]
    enabled: bool
    target: Dict[str, Any]
    failover: List[List[str]]
    native: bool
    policy: Dict[str, Any]
    misfire: Literal['skip', 'once', 'all_within']
    misfire_window_min: int
    overlap: Literal['skip', 'queue', 'kill']
    timeout_s: int
    retries: int
    retry_backoff_s: int
    late_after_s: Optional[int]
    alert_on_fail: bool
    template: Optional[str]


class ScheduleApprovalsItem(TypedDict, total=False):
    device_id: str
    command_hash: str
    approved_at: str


class _ScheduleRequired(TypedDict):
    id: str
    name: str
    enabled: bool
    kind: Literal['agent', 'shell', 'http', 'chain', 'phone_action']
    trigger: Dict[str, Any]
    target: Dict[str, Any]
    upcoming: List[str]


class Schedule(_ScheduleRequired, total=False):
    """A scheduled task."""
    description: Optional[str]
    spec: Dict[str, Any]
    failover: List[List[str]]
    native: bool
    policy: Dict[str, Any]
    misfire: Literal['skip', 'once', 'all_within']
    misfire_window_min: int
    overlap: Literal['skip', 'queue', 'kill']
    timeout_s: int
    retries: int
    retry_backoff_s: int
    late_after_s: Optional[int]
    alert_on_fail: bool
    template: Optional[str]
    command_hash: Optional[str]
    next_run_at: Optional[str]
    last_run_at: Optional[str]
    approvals: List[ScheduleApprovalsItem]
    created_at: str
    updated_at: str


class _ScheduleRunRequired(TypedDict):
    id: str
    schedule_id: str
    scheduled_for: str
    state: Literal['pending', 'awaiting_approval', 'claimed', 'running', 'succeeded', 'failed', 'timed_out', 'skipped', 'cancelled']
    attempt: int


class ScheduleRun(_ScheduleRunRequired, total=False):
    """One execution of a schedule."""
    device_id: Optional[str]
    started_at: Optional[str]
    finished_at: Optional[str]
    exit_code: Optional[int]
    cost_micro_usd: Optional[int]
    log_tail: Optional[str]
    session_id: Optional[str]
    error: Optional[str]
    created_at: str


class _ScheduleAuditEntryRequired(TypedDict):
    id: int
    action: Literal['schedule.create', 'schedule.update', 'schedule.delete', 'schedule.run_now', 'scheduler.pause', 'scheduler.resume', 'run.approve', 'run.skip', 'command.approve', 'heartbeat.create', 'heartbeat.update', 'heartbeat.delete', 'schedule.auto_pause', 'schedule.budget_skip', 'run.late', 'heartbeat.down']
    actor: Literal['user', 'host', 'hub', 'mcp', 'system']
    detail: Dict[str, Any]
    at: str


class ScheduleAuditEntry(_ScheduleAuditEntryRequired, total=False):
    """One audit log entry. Entries cannot be edited or deleted while the account exists."""
    schedule_id: Optional[str]
    heartbeat_id: Optional[str]
    run_id: Optional[str]
    device_id: Optional[str]


class _SchedulerHostRequired(TypedDict):
    id: str
    name: str
    platform: str
    online: bool


class SchedulerHost(_SchedulerHostRequired, total=False):
    """A device that can execute schedules."""
    os: Optional[str]
    arch: Optional[str]
    host_kind: Optional[str]
    tags: List[str]
    capabilities: List[str]
    last_seen_at: str
    app_version: Optional[str]


class _ErrorErrorRequired(TypedDict):
    message: str
    type: Literal['invalid_request_error', 'subscription_required', 'rate_limit_error', 'upstream_error', 'server_error']
    code: Literal['bad_request', 'invalid_api_key', 'subscription_inactive', 'forbidden', 'not_found', 'payload_too_large', 'rate_limit_exceeded', 'quota_exceeded', 'upstream_error', 'internal_error', 'not_a_member', 'lease_held', 'seq_conflict', 'host_offline', 'host_timeout', 'rules_refused', 'search_unavailable', 'task_not_confirmable', 'slug_taken', 'project_has_environments', 'already_has_env', 'not_enrollable', 'not_byo', 'invalid_transition', 'already_member', 'vm_per_dev_single_member', 'last_owner', 'insufficient_balance', 'key_scope_forbidden', 'assets_unavailable', 'asset_not_found', 'too_many_renders', 'renders_unavailable', 'timeline_too_long', 'not_a_timeline', 'invalid_cursor', 'templates_unavailable', 'url_blocked', 'invalid_tokens', 'unsupported_media', 'kind_mismatch', 'node_not_found', 'invalid_pick', 'duplicate_key', 'unknown_var', 'invalid_var_value', 'unsupported_kind', 'too_long', 'stale', 'not_supported_for_kind', 'unsupported_format', 'too_large', 'not_implemented', 'version_conflict', 'settings_unavailable', 'ai_label_required', 'sandbox_concurrency_limit', 'sandbox_busy', 'sandbox_daily_limit', 'invalid_ttl', 'workspace_too_large', 'sandbox_paused_limit', 'sandbox_capacity']


class ErrorError(_ErrorErrorRequired, total=False):
    details: Dict[str, Any]


class Error(TypedDict):
    error: ErrorError


class ChatContentPartOption1(TypedDict):
    type: Literal['text']
    text: str


class ChatContentPartOption2ImageUrl(TypedDict):
    url: str


class ChatContentPartOption2(TypedDict):
    type: Literal['image_url']
    image_url: ChatContentPartOption2ImageUrl


# One part of a multi-part message content array. Only `text` and `image_url` parts are interpreted; other part …
ChatContentPart = Union[ChatContentPartOption1, ChatContentPartOption2]


class ChatToolCallFunction(TypedDict):
    name: str
    arguments: str


class ChatToolCall(TypedDict):
    """Chat tool call"""
    id: str
    type: Literal['function']
    function: ChatToolCallFunction


class _ChatMessageRequired(TypedDict):
    role: Literal['system', 'developer', 'user', 'assistant', 'tool', 'function']


class ChatMessage(_ChatMessageRequired, total=False):
    """OpenAI chat message. `content` is a string or an array of content parts; assistant messages may carry `tool_ca…"""
    content: Optional[Union[str, List[ChatContentPart]]]
    name: str
    tool_call_id: str
    tool_calls: List[ChatToolCall]


class _ChatToolFunctionRequired(TypedDict):
    name: str


class ChatToolFunction(_ChatToolFunctionRequired, total=False):
    description: str
    parameters: Dict[str, Any]


class ChatTool(TypedDict):
    """Chat tool definition"""
    type: Literal['function']
    function: ChatToolFunction


class ChatResponseFormatJsonSchema(TypedDict, total=False):
    """Only for `type: json_schema`."""
    name: str
    description: str
    schema: Dict[str, Any]
    strict: bool


class _ChatResponseFormatRequired(TypedDict):
    type: Literal['text', 'json_object', 'json_schema']


class ChatResponseFormat(_ChatResponseFormatRequired, total=False):
    """Structured-output control. `json_object` / `json_schema` inject a system instruction and validate the output a…"""
    json_schema: ChatResponseFormatJsonSchema


class ChatCompletionRequestStreamOptions(TypedDict, total=False):
    """Accepted for OpenAI compatibility; `include_usage` is effectively always on."""
    include_usage: bool


class SandboxEgressOption1(TypedDict):
    """No network"""
    mode: Literal['none']


class SandboxEgressOption2(TypedDict):
    """Domain allowlist"""
    mode: Literal['allowlist']
    domains: List[str]


class SandboxEgressOption3(TypedDict):
    """Preset"""
    mode: Literal['preset']
    preset: Literal['pypi', 'npm']


# Outbound network, on both backends. `none` (default) has no network at all; `allowlist` lets HTTPS reach at mo…
SandboxEgress = Union[SandboxEgressOption1, SandboxEgressOption2, SandboxEgressOption3]


class _ChatSandboxToolRequired(TypedDict):
    type: Literal['codai_sandbox']


class ChatSandboxTool(_ChatSandboxToolRequired, total=False):
    """Server-side tool: the gateway replaces it with `sandbox_bash`, `sandbox_python`, `sandbox_edit` and `sandbox_f…"""
    egress: SandboxEgress
    template: Literal['codai-base']


class _ChatCompletionRequestRequired(TypedDict):
    messages: List[ChatMessage]


class ChatCompletionRequest(_ChatCompletionRequestRequired, total=False):
    """OpenAI Chat Completions body. Unknown fields are accepted (passthrough) and forwarded to OpenAI-compatible ups…"""
    model: str
    stream: bool
    stream_options: ChatCompletionRequestStreamOptions
    max_tokens: int
    max_completion_tokens: int
    temperature: float
    top_p: float
    top_k: int
    stop: Union[str, List[str]]
    tools: List[Union[ChatTool, ChatSandboxTool]]
    tool_choice: Union[Literal['auto', 'none', 'required'], Dict[str, Any]]
    response_format: ChatResponseFormat
    reasoning_effort: Literal['minimal', 'low', 'medium', 'high', 'max']
    n: int
    user: str
    metadata: Dict[str, Any]


class ChatUsagePromptTokensDetails(TypedDict, total=False):
    """Present on OpenAI-compatible upstreams and on every stream usage chunk; absent on non-stream Anthropic respons…"""
    cached_tokens: int


class _ChatUsageRequired(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatUsage(_ChatUsageRequired, total=False):
    """Chat usage"""
    prompt_tokens_details: ChatUsagePromptTokensDetails
    cache_creation_input_tokens: int


class ChatCompletionResponseChoicesItem(TypedDict):
    index: int
    message: ChatMessage
    finish_reason: Optional[Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call']]


class ChatCompletionResponse(TypedDict):
    """Chat completion"""
    id: str
    object: Literal['chat.completion']
    created: int
    model: str
    choices: List[ChatCompletionResponseChoicesItem]
    usage: ChatUsage


class ChatResponsesInputItemContentOption2Item(TypedDict, total=False):
    type: str
    text: str


class ChatResponsesInputItem(TypedDict, total=False):
    """A message item (`role` + `content`) or a typed item. `function_call_output` becomes a `tool` message, `functio…"""
    type: str
    role: Literal['system', 'developer', 'user', 'assistant']
    content: Union[str, List[ChatResponsesInputItemContentOption2Item]]
    call_id: str
    output: Union[str, List[Dict[str, Any]]]
    name: str
    arguments: str


class _ChatResponsesToolFunctionRequired(TypedDict):
    name: str


class ChatResponsesToolFunction(_ChatResponsesToolFunctionRequired, total=False):
    description: str
    parameters: Dict[str, Any]


class _ChatResponsesToolRequired(TypedDict):
    type: str


class ChatResponsesTool(_ChatResponsesToolRequired, total=False):
    """Only `type: function` is forwarded. Flat (`name`, `description`, `parameters`) and chat-style nested (`functio…"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: ChatResponsesToolFunction


class ChatResponsesRequestReasoning(TypedDict, total=False):
    """Only `effort` is mapped (`xhigh` → `max`, `none` → `minimal`, unknown values dropped). Ignored when `x-codai-e…"""
    effort: Literal['minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'none']


class ChatResponsesRequest(TypedDict, total=False):
    """Responses request"""
    model: str
    input: Union[str, List[ChatResponsesInputItem]]
    instructions: str
    stream: bool
    max_output_tokens: int
    temperature: float
    top_p: float
    tools: List[ChatResponsesTool]
    tool_choice: Union[str, Dict[str, Any]]
    reasoning: ChatResponsesRequestReasoning
    previous_response_id: str
    background: bool


class ChatResponsesOutputItemOption1(TypedDict):
    """Function call"""
    type: Literal['function_call']
    id: str
    call_id: str
    name: str
    arguments: str
    status: Literal['completed']


class ChatResponsesOutputItemOption2ContentItem(TypedDict):
    type: Literal['output_text']
    text: str
    annotations: List[Any]


class ChatResponsesOutputItemOption2(TypedDict):
    """Message"""
    type: Literal['message']
    id: str
    role: Literal['assistant']
    status: Literal['completed']
    content: List[ChatResponsesOutputItemOption2ContentItem]


# Responses output item
ChatResponsesOutputItem = Union[ChatResponsesOutputItemOption1, ChatResponsesOutputItemOption2]


class ChatResponsesUsageInputTokensDetails(TypedDict):
    cached_tokens: int


class ChatResponsesUsage(TypedDict):
    """Responses usage"""
    input_tokens: int
    input_tokens_details: ChatResponsesUsageInputTokensDetails
    output_tokens: int
    total_tokens: int


class ChatResponsesResponse(TypedDict):
    """Responses response"""
    id: str
    object: Literal['response']
    created_at: int
    status: Literal['completed']
    model: str
    output: List[ChatResponsesOutputItem]
    output_text: str
    usage: ChatResponsesUsage


class _MsgCacheControlRequired(TypedDict):
    type: Literal['ephemeral']


class MsgCacheControl(_MsgCacheControlRequired, total=False):
    """Anthropic prompt-cache breakpoint. Accepted on the wire; the gateway manages cache breakpoints itself."""
    ttl: Literal['5m', '1h']


class _MsgInputContentBlockOption1Required(TypedDict):
    type: Literal['text']
    text: str


class MsgInputContentBlockOption1(_MsgInputContentBlockOption1Required, total=False):
    """Text block"""
    cache_control: MsgCacheControl


class MsgInputContentBlockOption2Source(TypedDict):
    """Base64 image source. Translated to a `data:` URL for the upstream."""
    type: Literal['base64']
    media_type: str
    data: str


class MsgInputContentBlockOption2(TypedDict):
    """Image block"""
    type: Literal['image']
    source: MsgInputContentBlockOption2Source


class MsgInputContentBlockOption3(TypedDict):
    """Tool use block"""
    type: Literal['tool_use']
    id: str
    name: str
    input: Any


class MsgInputContentBlockOption4ContentOption2Item(TypedDict):
    type: Literal['text']
    text: str


class _MsgInputContentBlockOption4Required(TypedDict):
    type: Literal['tool_result']
    tool_use_id: str
    content: Union[str, List[MsgInputContentBlockOption4ContentOption2Item]]


class MsgInputContentBlockOption4(_MsgInputContentBlockOption4Required, total=False):
    """Tool result block"""
    is_error: bool
    cache_control: MsgCacheControl


# `text` and `image` are valid in user turns; `tool_use` in assistant turns; `tool_result` in the user turn
MsgInputContentBlock = Union[MsgInputContentBlockOption1, MsgInputContentBlockOption2, MsgInputContentBlockOption3, MsgInputContentBlockOption4]


class MsgInputMessage(TypedDict):
    """Input message"""
    role: Literal['user', 'assistant']
    content: Union[str, List[MsgInputContentBlock]]


class _MsgRequestSystemOption2ItemRequired(TypedDict):
    type: Literal['text']
    text: str


class MsgRequestSystemOption2Item(_MsgRequestSystemOption2ItemRequired, total=False):
    cache_control: MsgCacheControl


class _MsgToolRequired(TypedDict):
    name: str
    input_schema: Dict[str, Any]


class MsgTool(_MsgToolRequired, total=False):
    """Tool definition"""
    description: str


class MsgToolChoiceOption1(TypedDict):
    type: Literal['auto', 'any']


class MsgToolChoiceOption2(TypedDict):
    type: Literal['tool']
    name: str


# `auto` lets the model decide, `any` forces some tool call, `tool` forces a named tool. On Fable 5 / 5.1
MsgToolChoice = Union[MsgToolChoiceOption1, MsgToolChoiceOption2]


class MsgRequestMetadata(TypedDict, total=False):
    """Only `user_id` is used; it is forwarded as the upstream `user` field."""
    user_id: str


class MsgThinkingConfigOption1(TypedDict):
    type: Literal['enabled']
    budget_tokens: int


class MsgThinkingConfigOption2(TypedDict):
    type: Literal['adaptive']


# Anthropic extended-thinking config. Accepted for SDK compatibility but NOT forwarded — the gateway decides
MsgThinkingConfig = Union[MsgThinkingConfigOption1, MsgThinkingConfigOption2]


class _MsgRequestRequired(TypedDict):
    model: str
    messages: List[MsgInputMessage]
    max_tokens: int


class MsgRequest(_MsgRequestRequired, total=False):
    """Public Anthropic Messages request. Unknown top-level fields pass validation and are ignored unless listed"""
    system: Union[str, List[MsgRequestSystemOption2Item]]
    temperature: float
    top_p: float
    top_k: float
    stop_sequences: List[str]
    stream: bool
    tools: List[MsgTool]
    tool_choice: MsgToolChoice
    metadata: MsgRequestMetadata
    thinking: MsgThinkingConfig
    reasoning_effort: Literal['minimal', 'low', 'medium', 'high', 'max']


class MsgResponseContentBlockOption1(TypedDict):
    """Text block"""
    type: Literal['text']
    text: str


class MsgResponseContentBlockOption2(TypedDict):
    """Tool use block"""
    type: Literal['tool_use']
    id: str
    name: str
    input: Any


# `text` or `tool_use`. `thinking` blocks appear only inside native Anthropic streams, never in the JSON
MsgResponseContentBlock = Union[MsgResponseContentBlockOption1, MsgResponseContentBlockOption2]


class _MsgUsageRequired(TypedDict):
    input_tokens: int
    output_tokens: int


class MsgUsage(_MsgUsageRequired, total=False):
    """Usage"""
    cache_read_input_tokens: int
    cache_creation_input_tokens: int


class MsgResponse(TypedDict):
    """Non-streaming response. `model` echoes the requested model or alias, not the upstream that answered (see `x-co…"""
    id: str
    type: Literal['message']
    role: Literal['assistant']
    model: str
    content: List[MsgResponseContentBlock]
    stop_reason: Literal['end_turn', 'max_tokens', 'stop_sequence', 'tool_use']
    stop_sequence: Optional[str]
    usage: MsgUsage


class SystemOneRequestItemsItem(TypedDict):
    id: str
    state: Union[str, Dict[str, Any], List[Any]]


class _SystemOneQuestionRequired(TypedDict):
    type: Literal['choice', 'score', 'noul']
    instructions: str


class SystemOneQuestion(_SystemOneQuestionRequired, total=False):
    criteria: Union[Dict[str, Optional[str]], List[str]]


class _SystemOneRequestRequired(TypedDict):
    questions: Dict[str, SystemOneQuestion]


class SystemOneRequest(_SystemOneRequestRequired, total=False):
    """Send exactly one of `state` (single) or `items` (batch)."""
    state: Union[str, Dict[str, Any], List[Any]]
    items: List[SystemOneRequestItemsItem]
    timeout_ms: int
    fallback: Literal['none', 'codai-fast']
    model: str


class _SystemOneAnswerRequired(TypedDict):
    type: Literal['choice', 'score', 'noul']


class SystemOneAnswer(_SystemOneAnswerRequired, total=False):
    choice: str
    score: float
    noul: float
    confidence: float
    probabilities: Dict[str, float]
    legend: Dict[str, str]


class SystemOneResponseItemsItem(TypedDict):
    id: str
    answers: Dict[str, SystemOneAnswer]


class SystemOneResponseUsage(TypedDict, total=False):
    input_tokens: int
    output_tokens: int


class _SystemOneResponseRequired(TypedDict):
    model: str
    usage: SystemOneResponseUsage
    latency_ms: int


class SystemOneResponse(_SystemOneResponseRequired, total=False):
    """`answers` for a single `state`, `items` for a batch."""
    answers: Dict[str, SystemOneAnswer]
    items: List[SystemOneResponseItemsItem]
    fallback_used: bool


class _CoreEmbeddingsRequestRequired(TypedDict):
    input: Union[str, List[str]]


class CoreEmbeddingsRequest(_CoreEmbeddingsRequestRequired, total=False):
    """OpenAI-compatible embeddings body. Unknown fields are accepted and ignored."""
    model: str
    dimensions: int
    user: str
    encoding_format: Literal['float']


class CoreEmbeddingVector(TypedDict):
    """Embedding vector"""
    object: Literal['embedding']
    index: int
    embedding: List[float]


class CoreEmbeddingsResponseUsage(TypedDict):
    prompt_tokens: int
    total_tokens: int


class CoreEmbeddingsResponse(TypedDict):
    """Embeddings response"""
    object: Literal['list']
    data: List[CoreEmbeddingVector]
    model: str
    usage: CoreEmbeddingsResponseUsage


# Output aspect ratio. Overrides `size`.
CoreImageAspectRatio = Literal['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9', '9:21', '1:4', '4:1', '1:8', '8:1']


# Output resolution. `codai-image` supports all four, `codai-image-fast` only `1K`, `codai-image-pro` `1K`, `2K`…
CoreImageSize = Literal['512', '1K', '2K', '4K']


class _CoreImageInputRequired(TypedDict):
    b64_json: str


class CoreImageInput(_CoreImageInputRequired, total=False):
    """Input image"""
    mime_type: Literal['image/png', 'image/jpeg', 'image/webp', 'image/heic', 'image/heif']


# `b64_json` (default) returns the bytes inline, base64-encoded — the original shape. `url` stores the result as…
MediaResponseFormat = Literal['b64_json', 'url']


class _CoreImagesRequestRequired(TypedDict):
    prompt: str


class CoreImagesRequest(_CoreImagesRequestRequired, total=False):
    """OpenAI-compatible image generation body. Unknown fields are accepted and ignored."""
    model: Literal['codai-image', 'codai-image-fast', 'codai-image-pro', 'gemini-3.1-flash-image', 'gemini-3.1-flash-lite-image', 'gemini-3-pro-image', 'gemini-2.5-flash-image', 'imagen-4', 'imagen-4-fast']
    n: int
    size: Literal['1024x1024', '1536x1024', '1024x1536', '1792x1024', '1024x1792']
    aspect_ratio: CoreImageAspectRatio
    image_size: CoreImageSize
    reference_images: List[CoreImageInput]
    reference_asset_ids: List[str]
    response_format: MediaResponseFormat
    negative_prompt: str
    user: str


class _CoreImageEditRequestRequired(TypedDict):
    prompt: str
    image: Union[CoreImageInput, List[CoreImageInput]]


class CoreImageEditRequest(_CoreImageEditRequestRequired, total=False):
    """JSON body for `POST /v1/images/edits`. Unknown fields are accepted and ignored."""
    model: Literal['codai-image', 'codai-image-fast', 'codai-image-pro', 'gemini-3.1-flash-image', 'gemini-3.1-flash-lite-image', 'gemini-3-pro-image', 'gemini-2.5-flash-image', 'imagen-4', 'imagen-4-fast']
    n: int
    size: Literal['1024x1024', '1536x1024', '1024x1536', '1792x1024', '1024x1792']
    aspect_ratio: CoreImageAspectRatio
    image_size: CoreImageSize
    negative_prompt: str
    response_format: MediaResponseFormat


class _CoreImageEditFormRequired(TypedDict):
    prompt: str
    image: List[bytes]


class CoreImageEditForm(_CoreImageEditFormRequired, total=False):
    """OpenAI-style multipart form for `POST /v1/images/edits`. `mask` is rejected with 400."""
    model: str
    n: int
    size: str
    aspect_ratio: CoreImageAspectRatio
    image_size: CoreImageSize
    negative_prompt: str
    response_format: MediaResponseFormat


# What produced the asset.
AssetKind = Literal['music', 'video', 'image', 'speech', 'render', 'upload', 'sfx', 'document', 'preview']


class AssetDto(TypedDict):
    """A codai Studio asset. Returned by `/v1/assets` and, with `response_format: "url"`, in the `data` of the image,…"""
    asset_id: str
    kind: AssetKind
    status: Literal['pending', 'ready', 'failed', 'deleted']
    model: str
    url: Optional[str]
    mime_type: str
    bytes: int
    duration_seconds: Optional[float]
    width: Optional[int]
    height: Optional[int]
    created_at: str
    expires_at: Optional[str]


class AssetList(TypedDict):
    """Asset page"""
    object: Literal['list']
    data: List[AssetDto]
    next_before: Optional[str]


# Broad category of a sound effect.
SfxCategory = Literal['impact', 'whoosh', 'ui', 'notification', 'transition', 'ambience', 'foley', 'scifi', 'cartoon', 'nature', 'crowd', 'other']


class SfxDto(TypedDict):
    """One sound from the codai Studio library (or the Freesound CC0 fallback). Always licensed CC0-1.0."""
    sfx_id: str
    name: str
    category: SfxCategory
    tags: List[str]
    duration_seconds: float
    mime_type: str
    license: Literal['CC0-1.0']
    source: str
    preview_url: str


class SfxList(TypedDict):
    """Sound-effect search results"""
    object: Literal['list']
    data: List[SfxDto]
    source: Literal['library', 'library+freesound']


class AssetDeleted(TypedDict):
    """Deleted asset"""
    id: str
    object: Literal['asset']
    deleted: Literal[True]


# `16:9` is 1920×1080, `9:16` is 1080×1920, `1:1` is 1080×1080 and `4:5` is 1080×1350; it must match the root `d…
StudioRenderAspectRatio = Literal['16:9', '9:16', '1:1', '4:5']


# `final` renders at full resolution with a loudness pass to -14 LUFS. `draft` renders at 15 fps with a 540p sho…
StudioRenderQuality = Literal['draft', 'final']


# Visible AI label burned into the video (EU AI Act art. 50(4)): `corner` is a small "AI-generated" label (RO "G…
StudioRenderAiLabel = Literal['none', 'corner', 'end_card']


# `data`, `poster_url` and `cost_micro_usd` are set only when `succeeded`; `error` only when `failed`.
StudioRenderStatus = Literal['queued', 'rendering', 'succeeded', 'failed']


class _StudioRenderCreateRequired(TypedDict):
    html: str


class StudioRenderCreate(_StudioRenderCreateRequired, total=False):
    """Studio render request"""
    model: str
    variables: Dict[str, Any]
    aspect_ratio: StudioRenderAspectRatio
    quality: StudioRenderQuality
    fps: Literal[24, 25, 30]
    title: str
    ai_label: StudioRenderAiLabel


class _StudioRenderAcceptedRequired(TypedDict):
    id: str
    object: Literal['studio.render']
    status: Literal['queued']
    model: str
    quality: StudioRenderQuality
    aspect_ratio: StudioRenderAspectRatio
    fps: int
    price_micro_usd_per_second: str
    minimum_micro_usd: str


class StudioRenderAccepted(_StudioRenderAcceptedRequired, total=False):
    """Queued render"""
    ai_label: StudioRenderAiLabel


class StudioRenderQa(TypedDict):
    """Render QA report"""
    duration_seconds: float
    width: int
    height: int
    lufs: Optional[float]
    warnings: List[Literal['silent_audio', 'no_audio', 'lufs_off_target']]


class StudioTimelineMusic(TypedDict):
    """Timeline music"""
    asset_id: str
    volume: float


class StudioSceneNarration(TypedDict):
    """Scene narration"""
    text: str
    asset_id: Optional[str]
    seconds: Optional[float]


class _StudioTimelineSceneRequired(TypedDict):
    id: str
    kind: Literal['image', 'video']
    asset_id: str
    seconds: float
    fit: Literal['cover', 'contain']
    prompt: Optional[str]
    narration: Optional[StudioSceneNarration]
    revision: int
    asset: Optional[AssetDto]
    narration_asset: Optional[AssetDto]


class StudioTimelineScene(_StudioTimelineSceneRequired, total=False):
    """Timeline scene"""
    video_volume: float


class StudioTimeline(TypedDict):
    """Render timeline"""
    transition: Literal['fade', 'none']
    music: Optional[StudioTimelineMusic]
    scenes: List[StudioTimelineScene]


class _StudioRenderRequired(TypedDict):
    id: str
    object: Literal['studio.render']
    status: StudioRenderStatus
    progress: float
    quality: StudioRenderQuality
    aspect_ratio: StudioRenderAspectRatio
    fps: int
    error: Optional[str]


class StudioRender(_StudioRenderRequired, total=False):
    """Studio render"""
    qa: Optional[StudioRenderQa]
    cost_micro_usd: Optional[str]
    data: List[AssetDto]
    poster_url: Optional[str]
    stage: Optional[str]
    title: Optional[str]
    parent_render_id: Optional[str]
    root_render_id: Optional[str]
    timeline: Optional[StudioTimeline]
    creative_id: str
    ai_label: StudioRenderAiLabel


class CreativeAudioRenderRequest(TypedDict, total=False):
    """Body of `POST /v1/studio/creatives/{id}/render` for a creative of `kind: audio` (mixdown + mastering + exports…"""
    formats: List[Literal['wav', 'mp3', 'flac']]
    stems: bool
    lrc: bool
    loudness: Union[Literal['streaming', 'podcast', 'broadcast'], float]
    title: str


class CreativeAudioRenderOutput(TypedDict):
    kind: Literal['mix', 'stem', 'lrc']
    format: Literal['wav', 'mp3', 'flac', 'lrc']
    track_id: Optional[str]
    mime_type: str


class CreativeAudioRenderAccepted(TypedDict):
    """Queued audio render"""
    render_id: str
    id: str
    object: Literal['studio.render']
    status: Literal['queued']
    target: Literal['audio']
    model: str
    creative_id: str
    seq: int
    formats: List[Literal['wav', 'mp3', 'flac']]
    stems: bool
    lrc: bool
    target_lufs: float
    true_peak_db: float
    duration_seconds: float
    outputs: List[CreativeAudioRenderOutput]
    quote_micro_usd: str
    price_micro_usd_per_second: str
    minimum_micro_usd: str
    stems_surcharge_pct: int
    cached: Literal[False]


class StudioAudioRenderDataItem(TypedDict):
    asset_id: str
    kind: AssetKind
    status: Literal['pending', 'ready', 'failed', 'deleted']
    model: str
    url: Optional[str]
    mime_type: str
    bytes: int
    duration_seconds: Optional[float]
    width: Optional[int]
    height: Optional[int]
    created_at: str
    expires_at: Optional[str]
    output: Literal['mix', 'stem', 'lrc']
    format: Literal['wav', 'mp3', 'flac', 'lrc']
    track_id: Optional[str]


class _StudioAudioRenderRequired(TypedDict):
    id: str
    object: Literal['studio.render']
    status: StudioRenderStatus
    model: str
    target: Literal['audio']
    creative_id: str
    formats: List[Literal['wav', 'mp3', 'flac']]
    stems: bool
    lrc: bool
    target_lufs: float
    error: Optional[str]


class StudioAudioRender(_StudioAudioRenderRequired, total=False):
    """An audio creative render as returned by `GET /v1/studio/renders/{id}` (`target: audio`)."""
    progress: Optional[float]
    stage: Optional[str]
    duration_seconds: Optional[float]
    qa: Optional[Dict[str, Any]]
    cost_micro_usd: str
    data: List[StudioAudioRenderDataItem]


class StudioRenderListItem(TypedDict):
    """Render summary"""
    id: str
    object: Literal['studio.render']
    status: StudioRenderStatus
    title: Optional[str]
    quality: StudioRenderQuality
    aspect_ratio: StudioRenderAspectRatio
    fps: int
    duration_seconds: Optional[float]
    cost_micro_usd: str
    created_at: str
    parent_render_id: Optional[str]
    root_render_id: Optional[str]
    has_timeline: bool
    scene_count: int
    ai_label: StudioRenderAiLabel


class StudioRenderList(TypedDict):
    """Render list"""
    object: Literal['list']
    data: List[StudioRenderListItem]
    next_before: Optional[str]


class _StudioTimelineSceneInputNarrationRequired(TypedDict):
    text: str


class StudioTimelineSceneInputNarration(_StudioTimelineSceneInputNarrationRequired, total=False):
    """Narration synthesized now and played 0.3 s into the scene."""
    voice: str
    language: str


class _StudioTimelineSceneInputRequired(TypedDict):
    kind: Literal['image', 'video']
    asset_id: str


class StudioTimelineSceneInput(_StudioTimelineSceneInputRequired, total=False):
    """Timeline scene input"""
    id: str
    seconds: float
    fit: Literal['cover', 'contain']
    video_volume: float
    prompt: str
    narration: StudioTimelineSceneInputNarration


class StudioNarrationDefaults(TypedDict, total=False):
    """Narration defaults"""
    model: Literal['codai-speech', 'codai-speech-expressive']
    voice: str
    language: str
    instructions: str


class _StudioTimelineCreateRequired(TypedDict):
    scenes: List[StudioTimelineSceneInput]


class StudioTimelineCreate(_StudioTimelineCreateRequired, total=False):
    """Timeline render request"""
    model: str
    title: str
    aspect_ratio: Literal['16:9', '9:16', '1:1']
    quality: StudioRenderQuality
    fps: Literal[24, 25, 30]
    transition: Literal['fade', 'none']
    music_asset_id: str
    music_volume: float
    narration_defaults: StudioNarrationDefaults


class _StudioTimelineAcceptedRequired(TypedDict):
    id: str
    object: Literal['studio.render']
    status: Literal['queued']
    model: str
    quality: StudioRenderQuality
    aspect_ratio: StudioRenderAspectRatio
    fps: int
    price_micro_usd_per_second: str
    minimum_micro_usd: str
    narration_cost_micro_usd: str
    scene_count: int
    duration_seconds: float
    root_render_id: str


class StudioTimelineAccepted(_StudioTimelineAcceptedRequired, total=False):
    """Queued timeline render"""
    creative_id: Optional[str]
    ai_label: StudioRenderAiLabel


# Creative kind
CreativeKind = Literal['video', 'image', 'deck', 'doc', 'sheet', 'audio']


class _CreativeAudioClipGenerationRequired(TypedDict):
    provider: str
    model: str


class CreativeAudioClipGeneration(_CreativeAudioClipGenerationRequired, total=False):
    """How the clip was generated (public codai provider / model ids, never an upstream name)."""
    prompt: str
    seed: int
    parentClipId: str
    op: str


class _CreativeAudioClipRequired(TypedDict):
    id: str
    assetId: str
    startMs: float


class CreativeAudioClip(_CreativeAudioClipRequired, total=False):
    """One clip of an audio asset on a track. `inMs` / `outMs` are SOURCE offsets: the clip ends on the timeline at `…"""
    inMs: float
    outMs: float
    gainDb: float
    duck: bool
    fadeInMs: float
    fadeOutMs: float
    fadeCurve: Literal['linear', 'exp', 's']
    pan: float
    stretch: float
    pitchSemitones: float
    loop: bool
    color: str
    generation: CreativeAudioClipGeneration
    locked: bool


class CreativeAudioTrackSendsItem(TypedDict):
    busId: str
    gainDb: float


class _CreativeAudioFxRequired(TypedDict):
    id: str
    type: Literal['eq', 'compressor', 'reverb', 'delay', 'limiter', 'gate', 'deesser', 'pitch', 'chorus', 'saturation']
    params: Dict[str, float]


class CreativeAudioFx(_CreativeAudioFxRequired, total=False):
    """Creative audio effect"""
    bypass: bool


class CreativeAudioTrackAutomationItemPointsItem(TypedDict):
    tMs: float
    value: float


class CreativeAudioTrackAutomationItem(TypedDict):
    target: str
    points: List[CreativeAudioTrackAutomationItemPointsItem]


class CreativeAudioTrackMidiClipsItem(TypedDict):
    """`{ id, startMs, durationMs, notes: [{ id?, pitch 0–127, startMs, durationMs, velocity 1–127 }], cc?, instrumen…"""
    id: str
    startMs: float
    durationMs: float
    notes: List[Dict[str, Any]]


class _CreativeAudioTrackRequired(TypedDict):
    id: str
    role: Literal['voice', 'music', 'sfx', 'drums', 'bass', 'keys', 'guitar', 'vocal', 'lead', 'pad', 'fx', 'bus', 'podcast_host', 'podcast_guest']
    clips: List[CreativeAudioClip]


class CreativeAudioTrack(_CreativeAudioTrackRequired, total=False):
    """Creative audio track"""
    name: str
    kind: Literal['audio', 'midi', 'bus']
    gainDb: float
    pan: float
    mute: bool
    solo: bool
    locked: bool
    sends: List[CreativeAudioTrackSendsItem]
    fx: List[CreativeAudioFx]
    automation: List[CreativeAudioTrackAutomationItem]
    midiClips: List[CreativeAudioTrackMidiClipsItem]


class CreativeAudioMetaKey(TypedDict):
    tonic: Literal['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
    mode: Literal['major', 'minor']


class CreativeAudioMeta(TypedDict, total=False):
    """Song / episode metadata."""
    bpm: float
    key: CreativeAudioMetaKey
    timeSignature: List[int]
    language: str
    loudnessTarget: Union[Literal['streaming', 'podcast', 'broadcast'], float]
    sampleRate: Literal[44100, 48000]


class _CreativeAudioSectionRequired(TypedDict):
    id: str
    kind: Literal['intro', 'verse', 'pre_chorus', 'chorus', 'bridge', 'outro', 'instrumental', 'custom']
    startMs: float
    durationMs: float


class CreativeAudioSection(_CreativeAudioSectionRequired, total=False):
    """Creative audio section"""
    label: str
    lyrics: str
    styleHint: str
    locked: bool


class CreativeAudioMaster(TypedDict, total=False):
    """Master bus. Unset fields resolve to `meta.loudnessTarget` (or -14 LUFS) and a -1 dBTP true peak."""
    fx: List[CreativeAudioFx]
    targetLufs: float
    truePeakDb: float
    limiter: bool


class _CreativeAudioLyricsItemRequired(TypedDict):
    startMs: float
    endMs: float
    text: str


class CreativeAudioLyricsItem(_CreativeAudioLyricsItemRequired, total=False):
    sectionId: str


class _CreativeAudioHumanLogItemRequired(TypedDict):
    op: str
    actor: Literal['human', 'ai']
    ts: str


class CreativeAudioHumanLogItem(_CreativeAudioHumanLogItemRequired, total=False):
    detail: str


class _CreativeAudioRequired(TypedDict):
    tracks: List[CreativeAudioTrack]


class CreativeAudio(_CreativeAudioRequired, total=False):
    """`doc.audio`: the audio timeline of every creative (voice / music / sfx tracks of a video) and the whole docume…"""
    meta: CreativeAudioMeta
    sections: List[CreativeAudioSection]
    master: CreativeAudioMaster
    lyrics: List[CreativeAudioLyricsItem]
    humanLog: List[CreativeAudioHumanLogItem]


class _CreativeCastRequired(TypedDict):
    id: str
    name: str
    kind: Literal['character', 'product']
    refAssetIds: List[str]


class CreativeCast(_CreativeCastRequired, total=False):
    """Cast entry"""
    description: str


class _CreativeDocRequired(TypedDict):
    schemaVersion: Literal[1]
    kind: CreativeKind
    title: str
    formats: List[Dict[str, Any]]
    defaultFormat: str
    brand: Dict[str, Any]
    vars: Dict[str, Any]
    assets: Dict[str, Any]
    scenes: List[Dict[str, Any]]
    audio: CreativeAudio


class CreativeDoc(_CreativeDocRequired, total=False):
    """One plain-JSON document per creative: scenes of id-addressed nodes ordered by fractional `orderKey`s, plus"""
    fps: Literal[24, 25, 30]
    locale: str
    meta: Dict[str, Any]
    cast: List[CreativeCast]


class CreativeOp(TypedDict):
    """One edit, addressed by id. The `op` name selects the shape (all strict, validated by `@codai/creative-core`):"""
    op: Literal['setProps', 'setLayout', 'setTiming', 'setAnim', 'insertNode', 'removeNode', 'moveNode', 'addScene', 'removeScene', 'updateScene', 'moveScene', 'setVar', 'removeVar', 'setAsset', 'replaceAsset', 'setAudioClip', 'removeAudioClip', 'setBrand', 'restyle', 'adaptFormat', 'setControl', 'setMeta', 'setLocaleText', 'setLocale', 'setLocalization', 'trimVideo', 'splitVideo', 'setVideoRate', 'addCast', 'updateCast', 'removeCast', 'addSection', 'updateSection', 'removeSection', 'moveSection', 'addTrack', 'updateTrack', 'removeTrack', 'splitClip', 'trimClip', 'moveClip', 'setFades', 'addMidiClip', 'removeMidiClip', 'updateMidiNotes', 'setMaster', 'setLyrics']


class _CreativeCreateRequestRequired(TypedDict):
    kind: CreativeKind


class CreativeCreateRequest(_CreativeCreateRequestRequired, total=False):
    """Create creative request"""
    title: str
    doc: CreativeDoc
    template: str
    vars: Dict[str, str]
    brand_kit_id: str


class CreativeVersion(TypedDict):
    seq: int
    doc_hash: str


class Creative(TypedDict):
    """Studio creative"""
    id: str
    object: Literal['studio.creative']
    kind: CreativeKind
    title: str
    head_seq: int
    version: CreativeVersion
    doc: CreativeDoc


class _CreativeDetailRequired(TypedDict):
    id: str
    object: Literal['studio.creative']
    kind: CreativeKind
    title: str
    head_seq: int
    seq: int
    doc_hash: str
    doc: CreativeDoc
    assets: Dict[str, AssetDto]


class CreativeDetail(_CreativeDetailRequired, total=False):
    """Studio creative with document"""
    forked_from_version_id: Optional[str]
    created_at: str
    updated_at: str


class CreativeListItem(TypedDict):
    """Creative list item"""
    id: str
    object: Literal['studio.creative']
    kind: CreativeKind
    title: str
    head_seq: int
    updated_at: str


class CreativeList(TypedDict):
    """Creative list"""
    object: Literal['list']
    data: List[CreativeListItem]
    next_before: Optional[str]


class CreativeDeleted(TypedDict):
    """Deleted creative"""
    id: str
    object: Literal['studio.creative']
    deleted: Literal[True]


class CreativeOutline(TypedDict):
    """Creative outline"""
    head_seq: int
    outline: str
    formats: List[Dict[str, Any]]
    vars: Dict[str, Any]


class CreativeFindRequestQueryOption2(TypedDict, total=False):
    text: str
    type: str
    sceneId: str
    assetId: str
    locked: bool


class CreativeFindRequest(TypedDict):
    """Find request"""
    query: Union[str, CreativeFindRequestQueryOption2]


class CreativeFindResult(TypedDict):
    """Find result"""
    head_seq: int
    ids: List[str]


class CreativeSubtreeRequest(TypedDict, total=False):
    """Send `ids` or `sceneId`."""
    ids: List[str]
    sceneId: str


class CreativeSubtreeNodesItem(TypedDict):
    sceneId: str
    node: Dict[str, Any]


class CreativeSubtree(TypedDict):
    """Subtree"""
    head_seq: int
    scenes: List[Dict[str, Any]]
    nodes: List[CreativeSubtreeNodesItem]
    missing: List[str]


class _CreativeOpsRequestRequired(TypedDict):
    base_seq: int
    ops: List[CreativeOp]


class CreativeOpsRequest(_CreativeOpsRequestRequired, total=False):
    """Ops request"""
    intent: str
    author: Literal['user', 'agent']
    force: bool


class CreativeOpsResult(TypedDict):
    """Ops result"""
    seq: int
    doc_hash: str
    changed: List[str]
    warnings: List[str]
    rebased: bool


class CreativeRestyleRequest(TypedDict, total=False):
    """Exactly one of `brand_kit_id` and `tokens`."""
    brand_kit_id: str
    tokens: Dict[str, Union[str, float]]
    base_seq: int
    snap: bool
    fonts: bool
    force: bool


class CreativeVersionList(TypedDict):
    """Creative version list"""
    object: Literal['list']
    data: List[CreativeVersion]
    next_before_seq: Optional[int]


class CreativeRevertRequest(TypedDict):
    """Revert request"""
    seq: int


class CreativeRevertResult(TypedDict):
    """Revert result"""
    id: str
    head_seq: int
    seq: int
    author: str
    intent: Optional[str]
    created_at: str
    doc_hash: str


class CreativeForkRequest(TypedDict, total=False):
    """Fork request"""
    seq: int
    title: str


# `off_brand_color`, `outside_platform_safe_zone`, `text_too_small`, `flashing` (keyframes) and `text_overflow_l…
CreativeLintCode = Literal['low_contrast', 'outside_safe_area', 'empty_text', 'captions_no_words', 'captions_no_clip', 'missing_asset', 'scene_zero_duration', 'too_long', 'chart_no_svg', 'unresolved_ref', 'empty_list', 'off_brand_color', 'outside_platform_safe_zone', 'text_too_small', 'missing_alt', 'missing_captions', 'reading_speed', 'flashing', 'missing_translation', 'stale_translation', 'text_overflow_locale']


class _CreativeLintIssueRequired(TypedDict):
    code: CreativeLintCode
    severity: Literal['error', 'warning']
    message: str
    target: str


class CreativeLintIssue(_CreativeLintIssueRequired, total=False):
    """Lint issue"""
    value: float
    format: str
    fixable: bool
    locale: str


class CreativeLintResult(TypedDict):
    """Lint result"""
    head_seq: int
    issues: List[CreativeLintIssue]
    fixable: int


# `bold-pill` (white bold words on a dark pill, the default), `clean-outline` (outlined text, no background), `k…
CaptionPresetId = Literal['bold-pill', 'clean-outline', 'karaoke-pop', 'minimal']


# `tiktok`, `reels`, `shorts` are 1080×1920, `feed-square` 1080×1080, `feed-portrait` 1080×1350 and `youtube` 19…
PlatformId = Literal['tiktok', 'reels', 'shorts', 'feed-square', 'feed-portrait', 'youtube']


class CreativeCaptionsRequest(TypedDict, total=False):
    """Captions request"""
    clip_id: str
    base_seq: int
    preset: CaptionPresetId
    node_id: str
    script: str
    language: str
    retranscribe: bool
    force: bool


class CreativeTranscriptCutRequestRemoveItem(TypedDict):
    from_word: int
    to_word: int


class _CreativeTranscriptCutRequestRequired(TypedDict):
    node_id: str
    remove: List[CreativeTranscriptCutRequestRemoveItem]


class CreativeTranscriptCutRequest(_CreativeTranscriptCutRequestRequired, total=False):
    """Transcript cut request"""
    base_seq: int
    force: bool


class CreativeTranscriptCutResultRemovedItem(TypedDict):
    in_ms: float
    out_ms: float


class CreativeTranscriptCutResult(TypedDict):
    """Transcript cut result"""
    seq: int
    doc_hash: str
    changed: List[str]
    warnings: List[str]
    rebased: bool
    node_id: str
    pieces: List[str]
    removed: List[CreativeTranscriptCutResultRemovedItem]
    removed_ms: float
    words: int


class _CreativeRegenerateNodeRequestRequired(TypedDict):
    prompt: str


class CreativeRegenerateNodeRequest(_CreativeRegenerateNodeRequestRequired, total=False):
    """Regenerate node request"""
    model: str
    aspect_ratio: Literal['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9', '9:21']
    base_seq: int
    force: bool


class CreativeRegenerateNodeResult(TypedDict):
    """Regenerate node result"""
    seq: int
    doc_hash: str
    changed: List[str]
    warnings: List[str]
    rebased: bool
    node_id: str
    asset_id: str
    cast_id: Optional[str]
    reference_asset_ids: List[str]
    cost_micro_usd: str


class CreativeCaptionsResult(TypedDict):
    """Captions result"""
    seq: int
    doc_hash: str
    changed: List[str]
    warnings: List[str]
    rebased: bool
    node_id: str
    words: int
    cached: bool
    corrected: bool
    cost_micro_usd: int


class _CreativeAdaptRequestRequired(TypedDict):
    platforms: List[PlatformId]


class CreativeAdaptRequest(_CreativeAdaptRequestRequired, total=False):
    """Adapt request"""
    base_seq: int
    focal: Literal['none', 'vision']
    force: bool


class CreativeAdaptFormat(TypedDict):
    """Adapted format"""
    platform: PlatformId
    format_id: str
    width: int
    height: int


class CreativeFocalPoint(TypedDict):
    """Focal point"""
    x: float
    y: float


class CreativeAdaptResult(TypedDict):
    """Adapt result"""
    seq: int
    doc_hash: str
    changed: List[str]
    warnings: List[str]
    rebased: bool
    formats: List[CreativeAdaptFormat]
    focal: Optional[Dict[str, CreativeFocalPoint]]


class CreativeLintFixRequest(TypedDict, total=False):
    """Lint fix request"""
    base_seq: int
    codes: List[CreativeLintCode]
    agent: bool
    force: bool


class CreativeLintFixed(TypedDict):
    """Fixed issue"""
    code: CreativeLintCode
    target: str


class CreativeLintFixResultAgent(TypedDict):
    """The agent pass (`agent: true`), `null` or absent otherwise."""
    ops: int
    cost_micro_usd: int


class _CreativeLintFixResultRequired(TypedDict):
    seq: int
    changed: List[str]
    warnings: List[str]
    rebased: bool
    fixed: List[CreativeLintFixed]
    remaining: List[CreativeLintIssue]


class CreativeLintFixResult(_CreativeLintFixResultRequired, total=False):
    """Lint fix result"""
    doc_hash: str
    agent: Optional[CreativeLintFixResultAgent]


class _ControlOptionsItemRequired(TypedDict):
    value: Union[str, float]


class ControlOptionsItem(_ControlOptionsItemRequired, total=False):
    label: str


class _ControlRequired(TypedDict):
    kind: Literal['text', 'color', 'slider', 'toggle', 'select', 'image']


class Control(_ControlRequired, total=False):
    """Tweak control"""
    label: str
    group: str
    min: float
    max: float
    step: float
    options: List[ControlOptionsItem]
    multiline: bool


class PanelControl(TypedDict):
    """Panel control"""
    key: str
    label: str
    control: Control
    value: Union[str, float, bool]
    type: Literal['text', 'number', 'color', 'image', 'boolean']
    locked: bool


class CreativeControls(TypedDict):
    """Tweak panel"""
    head_seq: int
    controls: List[PanelControl]


class _CreativeLocaleUnitRequired(TypedDict):
    key: str
    node_id: Optional[str]
    kind: Literal['text', 'list', 'table', 'chart', 'alt', 'caption', 'notes', 'title', 'var', 'html', 'param', 'cell', 'captions', 'narration']
    text: str
    translation: Optional[str]
    by: Optional[Literal['agent', 'user']]
    stale: bool
    locked: bool


class CreativeLocaleUnit(_CreativeLocaleUnitRequired, total=False):
    """Translatable unit"""
    max_chars: Optional[int]


class CreativeLocaleStatusLocalesItem(TypedDict):
    locale: str
    tone: Optional[Literal['formal', 'informal']]
    translated: int
    missing: int
    stale: int
    voice: int


class _CreativeLocaleStatusRequired(TypedDict):
    head_seq: int
    source: Optional[str]
    glossary: List[str]
    total: int
    locales: List[CreativeLocaleStatusLocalesItem]


class CreativeLocaleStatus(_CreativeLocaleStatusRequired, total=False):
    """Locales of a creative"""
    units: List[CreativeLocaleUnit]
    units_total: int


class _CreativeLocalizeRequestRequired(TypedDict):
    locales: List[str]


class CreativeLocalizeRequest(_CreativeLocalizeRequestRequired, total=False):
    """Localize request"""
    base_seq: int
    tone: Literal['formal', 'informal']
    glossary: List[str]
    only_missing: bool
    voice: bool
    force: bool


class CreativeLocalizeResultLocalesItem(TypedDict):
    locale: str
    translated: int
    remaining: int
    voice_clips: int


class CreativeLocalizeResult(TypedDict):
    """Localize result"""
    seq: int
    doc_hash: str
    changed: List[str]
    warnings: List[str]
    rebased: bool
    locales: List[CreativeLocalizeResultLocalesItem]
    cost_micro_usd: Union[str, int]


class CreativeLocaleForkRequest(TypedDict, total=False):
    """Locale fork request"""
    title: str
    seq: int


class CreativeLocaleForkResultVersion(TypedDict):
    seq: int
    doc_hash: str


class CreativeLocaleForkResultForkOf(TypedDict):
    creative_id: str
    seq: int


class CreativeLocaleForkResult(TypedDict):
    """Locale fork result"""
    id: str
    object: Literal['studio.creative']
    kind: CreativeKind
    title: str
    head_seq: int
    version: CreativeLocaleForkResultVersion
    doc: CreativeDoc
    locale: str
    fork_of: CreativeLocaleForkResultForkOf


class _CreativeCompiledRequired(TypedDict):
    head_seq: int
    format: str
    width: int
    height: int
    duration_ms: int
    html: str


class CreativeCompiled(_CreativeCompiledRequired, total=False):
    """Compiled composition"""
    kind: CreativeKind


class CreativeRenderRequest(TypedDict, total=False):
    """Creative render request"""
    format: str
    quality: StudioRenderQuality
    fps: Literal[24, 25, 30]
    title: str
    locale: str
    ai_label: StudioRenderAiLabel


class _CreativeRenderAcceptedRequired(TypedDict):
    render_id: str
    id: str
    object: Literal['studio.render']
    status: Literal['queued']
    creative_id: str
    seq: int
    model: str
    quality: StudioRenderQuality
    aspect_ratio: StudioRenderAspectRatio
    format: str
    fps: int
    duration_seconds: float
    price_micro_usd_per_second: str
    minimum_micro_usd: str


class CreativeRenderAccepted(_CreativeRenderAcceptedRequired, total=False):
    """Queued creative render"""
    cached: Literal[False]
    ai_label: StudioRenderAiLabel


class _CreativeRenderCachedRequired(TypedDict):
    render_id: str
    id: str
    object: Literal['studio.render']
    status: Literal['succeeded']
    cached: Literal[True]
    creative_id: str
    seq: int
    model: str
    quality: StudioRenderQuality
    aspect_ratio: StudioRenderAspectRatio
    format: str
    fps: int
    duration_seconds: float
    data: List[AssetDto]


class CreativeRenderCached(_CreativeRenderCachedRequired, total=False):
    """The render that already exists for this exact document version, format, quality and fps (no new charge)."""
    poster_url: Optional[str]
    cost_micro_usd: Optional[str]
    ai_label: StudioRenderAiLabel


class _CreativeFrameRequestRequired(TypedDict):
    t_ms: List[int]


class CreativeFrameRequest(_CreativeFrameRequestRequired, total=False):
    """Frame request"""
    format: str
    exact: bool
    version: int
    locale: str


class CreativeFrame(TypedDict):
    """Still frame"""
    t_ms: int
    url: str
    width: int
    height: int
    cached: bool


class CreativeFrames(TypedDict):
    """Creative frames"""
    object: Literal['studio.creative.frames']
    frame_job_id: Optional[str]
    status: Literal['succeeded']
    frames: List[CreativeFrame]
    head_seq: int
    billed_micro_usd: str


class CreativeFrameJob(TypedDict):
    """Running frame job"""
    object: Literal['studio.creative.frame_job']
    frame_job_id: str
    status: Literal['running']
    head_seq: int


class _CreativeCommentRequestRequired(TypedDict):
    t_ms: int
    comment: str
    base_seq: int


class CreativeCommentRequest(_CreativeCommentRequestRequired, total=False):
    """Frame comment"""
    node_id: str
    scene_id: str
    apply: bool


class CreativeCommentResultVersion(TypedDict):
    """The new version; `null` with `apply: false`."""
    seq: int
    doc_hash: str


class _CreativeCommentResultRequired(TypedDict):
    head_seq: int
    applied_ops: int
    summary: str
    version: Optional[CreativeCommentResultVersion]


class CreativeCommentResult(_CreativeCommentResultRequired, total=False):
    """Comment result"""
    ops: List[CreativeOp]


class BrandKitTokens(TypedDict):
    """Flat token map, the same shape as a creative `brand.tokens` (reference them as `{ "$token": "primary" }`). Col…"""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    headingFont: str
    bodyFont: str


# Design Tokens (DTCG 2025.10) document of a kit. `color` holds the 5 roles (`primary`, `secondary`, `accent`,
BrandKitDtcg = TypedDict(
    'BrandKitDtcg',
    {
        '$schema': str,
        'color': Dict[str, Any],
        'font': Dict[str, Any],
        'radius': Dict[str, Any],
        '$extensions': Dict[str, Any],
    },
    total=False,
)


class BrandKitContrastPair(TypedDict):
    """Brand kit contrast pair"""
    foreground: str
    background: str
    ratio: float
    aa: bool


class BrandKit(TypedDict):
    """Brand kit"""
    id: str
    object: Literal['studio.brand_kit']
    name: str
    source_url: Optional[str]
    tokens: BrandKitTokens
    logo_asset_id: Optional[str]
    logo_url: Optional[str]
    logo_mime_type: Optional[str]
    created_at: str
    updated_at: str
    dtcg: BrandKitDtcg
    contrast: List[BrandKitContrastPair]


class _BrandKitExtractRequestOption1Required(TypedDict):
    url: str


class BrandKitExtractRequestOption1(_BrandKitExtractRequestOption1Required, total=False):
    """From a web page"""
    name: str


class _BrandKitExtractRequestOption2Required(TypedDict):
    logo_asset_id: str


class BrandKitExtractRequestOption2(_BrandKitExtractRequestOption2Required, total=False):
    """From a logo"""
    name: str


# Exactly one source: a public web page (`url`) or one of your logo images (`logo_asset_id`).
BrandKitExtractRequest = Union[BrandKitExtractRequestOption1, BrandKitExtractRequestOption2]


class _BrandKitCreateRequestTokensRequired(TypedDict):
    primary: str
    secondary: str
    accent: str
    background: str
    text: str


class BrandKitCreateRequestTokens(_BrandKitCreateRequestTokensRequired, total=False):
    """Flat token map: the 5 colours as `#rrggbb` (all required) and optional fonts (up to 100 characters)."""
    headingFont: str
    bodyFont: str


class _BrandKitCreateRequestRequired(TypedDict):
    name: str


class BrandKitCreateRequest(_BrandKitCreateRequestRequired, total=False):
    """Exactly one of `tokens` and `dtcg`."""
    tokens: BrandKitCreateRequestTokens
    dtcg: BrandKitDtcg
    logo_asset_id: str
    source_url: str


class BrandKitUpdateRequestTokens(TypedDict, total=False):
    """Partial flat token map merged onto the current kit (colours `#rrggbb`, fonts up to 100 characters)."""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    headingFont: str
    bodyFont: str


class BrandKitUpdateRequest(TypedDict, total=False):
    """At least one field; not `tokens` and `dtcg` together."""
    name: str
    tokens: BrandKitUpdateRequestTokens
    dtcg: BrandKitDtcg
    logo_asset_id: Optional[str]


class BrandKitList(TypedDict):
    """Brand kit list"""
    object: Literal['list']
    data: List[BrandKit]


class BrandKitDeleted(TypedDict):
    """Brand kit deleted"""
    id: str
    object: Literal['studio.brand_kit']
    deleted: Literal[True]


class CreativeTemplateVar(TypedDict):
    """One variable of a template: which node property it replaces and its default value."""
    type: Literal['text', 'image']
    label: str
    default: str
    node_id: str
    prop: Literal['text', 'image']


class _CreativeTemplateRequired(TypedDict):
    id: str
    object: Literal['studio.template']
    title: str
    kind: CreativeKind
    source_creative_id: Optional[str]
    source_seq: int
    vars_schema: Dict[str, CreativeTemplateVar]
    thumbnail_url: Optional[str]
    created_at: str


class CreativeTemplate(_CreativeTemplateRequired, total=False):
    """A private template saved from one of your creatives. `doc` is present on create and retrieve, not in lists."""
    source: Literal['own', 'starter']
    description: str
    category: str
    locale: str
    months: List[int]
    scene_count: int
    doc: Dict[str, Any]


class _SaveTemplateRequestVarsItemRequired(TypedDict):
    node_id: str
    prop: Literal['text', 'image']
    key: str


class SaveTemplateRequestVarsItem(_SaveTemplateRequestVarsItemRequired, total=False):
    label: str


class _SaveTemplateRequestRequired(TypedDict):
    vars: List[SaveTemplateRequestVarsItem]


class SaveTemplateRequest(_SaveTemplateRequestRequired, total=False):
    """Save template request"""
    title: str
    seq: int


# Media op id
MediaOpId = Literal['image.remove_background', 'image.upscale', 'image.inpaint', 'image.outpaint', 'image.erase', 'audio.separate_stems', 'audio.denoise', 'audio.to_midi', 'audio.master', 'audio.analyze', 'music.generate_ace', 'music.repaint', 'music.extend', 'music.cover', 'sfx.generate']


class _MediaOpRequired(TypedDict):
    id: MediaOpId
    title: str
    lane: Literal['gpu', 'vertex', 'cpu']
    mode: Literal['sync', 'async']
    engine: str
    input_kinds: List[str]
    min_inputs: int
    max_inputs: int
    output_kind: str
    available: bool
    quote_micro_usd: int
    quote_micro_eur: int


class MediaOp(_MediaOpRequired, total=False):
    """One catalogue entry of `GET /v1/studio/media-ops`."""
    note: str


StudioLyricsSectionKind = Literal['intro', 'verse', 'pre_chorus', 'chorus', 'bridge', 'outro', 'instrumental', 'custom']


class _StudioLyricsRequestRequired(TypedDict):
    brief: str
    language: Literal['ro', 'en']


class StudioLyricsRequest(_StudioLyricsRequestRequired, total=False):
    """Lyrics request"""
    genre: str
    mood: str
    structure: List[StudioLyricsSectionKind]
    syllables_per_line: int
    rhyme_scheme: Literal['AABB', 'ABAB', 'free']
    lines_per_section: int
    title: str


class StudioLyricsLine(TypedDict):
    """Checked lyric line"""
    text: str
    syllables: int
    rhyme: str
    letter: str
    off: bool


class StudioLyricsSectionsItem(TypedDict):
    kind: StudioLyricsSectionKind
    lines: List[StudioLyricsLine]


class StudioLyricsReport(TypedDict):
    """Syllable and rhyme check of the returned lyrics."""
    lines: int
    off_lines: int
    off_ratio: float
    pairs: int
    rhymed: int
    repair_ratio: float


class StudioLyrics(TypedDict):
    """Written lyrics"""
    object: Literal['studio.lyrics']
    title: Optional[str]
    language: Literal['ro', 'en']
    rhyme_scheme: Literal['AABB', 'ABAB', 'free']
    syllables_per_line: Optional[int]
    sections: List[StudioLyricsSectionsItem]
    text: str
    report: StudioLyricsReport
    repaired: bool
    cost_micro_usd: str


class _StudioLyricsAlignRequestRequired(TypedDict):
    creative_id: str
    clip_id: str
    lyrics_text: str


class StudioLyricsAlignRequest(_StudioLyricsAlignRequestRequired, total=False):
    """Lyrics alignment request"""
    language: Literal['ro', 'en']
    apply: bool
    base_seq: int
    retranscribe: bool


class _StudioLyricsAlignmentLinesItemRequired(TypedDict):
    startMs: float
    endMs: float
    text: str


class StudioLyricsAlignmentLinesItem(_StudioLyricsAlignmentLinesItemRequired, total=False):
    sectionId: str


class _StudioLyricsAlignmentRequired(TypedDict):
    object: Literal['studio.lyrics_alignment']
    creative_id: str
    clip_id: str
    applied: bool
    lines: List[StudioLyricsAlignmentLinesItem]
    lrc: str
    match_ratio: float
    cached: bool
    cost_micro_usd: str


class StudioLyricsAlignment(_StudioLyricsAlignmentRequired, total=False):
    """Lyrics alignment"""
    seq: int
    doc_hash: str


class MediaOpList(TypedDict):
    """Media op catalogue"""
    object: Literal['list']
    quote_basis: str
    data: List[MediaOp]


class MediaOpRequest(TypedDict, total=False):
    """`asset_ids` are the inputs, in order; `params` are validated strictly per op (unknown keys are rejected):"""
    asset_ids: List[str]
    params: Dict[str, Any]
    mask_png_b64: str


class MediaOpQuote(TypedDict):
    """Media op quote"""
    object: Literal['media_op.quote']
    op: MediaOpId
    mode: Literal['sync', 'async']
    quote_micro_usd: int
    quote_micro_eur: int


class MediaOpResult(TypedDict):
    """Media op result"""
    object: Literal['media_op.result']
    op: MediaOpId
    status: Literal['ready']
    outputs: List[AssetDto]
    analysis: Optional[Dict[str, Any]]
    cost_micro_usd: int


class MediaOpJob(TypedDict):
    """Media op job"""
    object: Literal['media_op.job']
    id: str
    op: MediaOpId
    status: Literal['pending', 'ready', 'failed']
    parent_asset_id: Optional[str]
    outputs: List[AssetDto]
    analysis: Optional[Dict[str, Any]]
    error: Optional[str]
    cost_micro_usd: int
    created_at: str
    updated_at: str


# What the production builds: `video` (MP4), `image` (PNG), `deck` (PPTX), `doc` (DOCX), `sheet` (XLSX), `audio`…
StudioProductionKind = Literal['video', 'image', 'deck', 'doc', 'sheet', 'audio', 'carousel', 'print']


class _StudioProductionCreateRequired(TypedDict):
    brief: str


class StudioProductionCreate(_StudioProductionCreateRequired, total=False):
    """Studio production request"""
    kind: StudioProductionKind
    language: Literal['en', 'ro']
    aspect_ratio: Literal['16:9', '9:16', '1:1']
    duration_s: int
    starter: str
    voice: str
    narration: bool
    budget_micro_usd: int
    title: str


class StudioProductionQa(TypedDict, total=False):
    issues: List[str]
    fixes: int
    skipped: str


class StudioProductionOutput(TypedDict):
    """A built output of a non-video production: the regular Studio asset plus its `role`. `url` is a 1 h signed GET,…"""
    asset_id: str
    kind: AssetKind
    status: Literal['pending', 'ready', 'failed', 'deleted']
    model: str
    url: Optional[str]
    mime_type: str
    bytes: int
    duration_seconds: Optional[float]
    width: Optional[int]
    height: Optional[int]
    created_at: str
    expires_at: Optional[str]
    role: Literal['image', 'cover', 'document', 'pages', 'pdf', 'audio']


class _StudioProductionRequired(TypedDict):
    id: str
    object: Literal['studio.production']
    status: Literal['running', 'succeeded', 'failed']
    phase: Literal['storyboard', 'assets', 'render', 'qa', 'repair', 'ready', 'failed']
    brief: str
    language: Literal['en', 'ro']
    aspect_ratio: Literal['16:9', '9:16', '1:1']
    title: Optional[str]
    starter: Optional[str]
    scenes: int
    creative_id: Optional[str]
    render_id: Optional[str]
    first_render_id: Optional[str]
    qa: Optional[StudioProductionQa]
    budget_micro_usd: str
    spent_micro_usd: str
    warnings: List[str]
    error: Optional[str]
    created_at: str


class StudioProduction(_StudioProductionRequired, total=False):
    """Studio production"""
    duration_s: Optional[int]
    kind: StudioProductionKind
    output_asset_id: Optional[str]
    outputs: List[StudioProductionOutput]


class _MusicRoomCreateRequired(TypedDict):
    brief: str


class MusicRoomCreate(_MusicRoomCreateRequired, total=False):
    """Music Room request"""
    language: Literal['ro', 'en']
    genre: str
    duration_seconds: int
    vocals: bool
    timbre: str
    voice_passport_id: str
    instruments: List[str]
    auto: bool
    budget_micro_usd: int
    title: str


class MusicRoomPlanVariantSectionsItem(TypedDict):
    id: str
    kind: str
    bars: int


# A member of the Music Room team.
MusicRole = Literal['producer', 'composer', 'lyricist', 'arranger', 'drums', 'bass', 'guitar', 'keys', 'strings', 'brass', 'winds', 'balkan_lead', 'balkan_rhythm', 'percussion', 'synth', 'vocal_producer', 'sound_designer', 'mix_engineer', 'mastering_engineer', 'critic', 'rights']


class MusicRoomPlanVariantInstrumentationItem(TypedDict):
    role: MusicRole
    instrument_id: str


class MusicRoomPlanVariant(TypedDict):
    """Music Room plan variant"""
    title: str
    genre_id: str
    bpm: float
    meter: str
    mode_id: str
    sections: List[MusicRoomPlanVariantSectionsItem]
    instrumentation: List[MusicRoomPlanVariantInstrumentationItem]
    rationale: str


class _MusicRoomGateRequired(TypedDict):
    kind: Literal['plan', 'demo', 'final']
    since: str


class MusicRoomGate(_MusicRoomGateRequired, total=False):
    """The gate the song waits at (`null` when it is not waiting)."""
    variants: List[MusicRoomPlanVariant]


class _MusicRoomTeamItemRequired(TypedDict):
    role: MusicRole
    name: str
    status: Literal['done', 'playing', 'waiting']


class MusicRoomTeamItem(_MusicRoomTeamItemRequired, total=False):
    instrument_id: Optional[str]
    track_id: Optional[str]
    rationale: Optional[str]


class _MusicRoomCritiqueIssuesItemRequired(TypedDict):
    role: MusicRole
    problem: str
    fix: str


class MusicRoomCritiqueIssuesItem(_MusicRoomCritiqueIssuesItemRequired, total=False):
    section_id: Optional[str]


class MusicRoomCritique(TypedDict):
    """The critic's last review."""
    round: int
    scores: Dict[str, float]
    verdict: Literal['ship', 'revise']
    issues: List[MusicRoomCritiqueIssuesItem]


class MusicRoomListeningFeaturesAesthetics(TypedDict):
    """Meta Audiobox Aesthetics, about 1-10: CE content enjoyment, CU content usefulness, PC production complexity, P…"""
    CE: float
    CU: float
    PC: float
    PQ: float


class MusicRoomListeningFeatures(TypedDict, total=False):
    """Measured listening features of the master (codai-studio-media). `null` when the measurement was unavailable."""
    duration_seconds: Optional[float]
    spectral_centroid_hz: Optional[float]
    spectral_centroid_std_hz: Optional[float]
    spectral_flatness: Optional[float]
    onset_rate_per_s: Optional[float]
    onset_rate_cv: Optional[float]
    crest_factor_db: Optional[float]
    loudness_range_lu: Optional[float]
    stereo_width: Optional[float]
    loudness_timeline_lufs: List[Optional[float]]
    aesthetics: Optional[MusicRoomListeningFeaturesAesthetics]


class MusicRoomListeningVerdictImpressions(TypedDict):
    """Impressions from 0 to 10 per aspect; `vocals` is `null` for an instrumental."""
    groove: float
    melody: float
    mix: float
    vocals: Optional[float]
    humanness: float
    genre_fit: float


class MusicRoomListeningVerdictNotesItem(TypedDict):
    at_seconds: float
    note: str


class MusicRoomListeningVerdict(TypedDict):
    """The Gemini listener's verdict. `null` when the listener was unavailable."""
    impressions: MusicRoomListeningVerdictImpressions
    notes: List[MusicRoomListeningVerdictNotesItem]
    ai_tells: List[str]
    summary: str


class MusicRoomListening(TypedDict):
    """Music Room listening"""
    features: Optional[MusicRoomListeningFeatures]
    verdict: Optional[MusicRoomListeningVerdict]
    model: Optional[str]


class MusicRoomCopyRiskMatchesItem(TypedDict, total=False):
    id: str
    title: str
    score: float


class MusicRoomCopyRisk(TypedDict):
    """Melody similarity against the reference corpus."""
    max_score: float
    matches: List[MusicRoomCopyRiskMatchesItem]


class MusicRoomQuota(TypedDict):
    within: bool
    used: int
    included: int


class MusicRoom(TypedDict):
    """Music Room song"""
    id: str
    object: Literal['studio.music_room']
    status: Literal['running', 'waiting', 'succeeded', 'failed']
    phase: Literal['plan', 'gate_plan', 'compose', 'lyrics', 'arrange', 'parts', 'render_demo', 'gate_demo', 'vocals', 'mix', 'master', 'critique', 'gate_final', 'ready', 'failed']
    gate: Optional[MusicRoomGate]
    brief: str
    language: Literal['ro', 'en']
    genre_id: Optional[str]
    title: Optional[str]
    creative_id: Optional[str]
    demo_asset_id: Optional[str]
    final_asset_id: Optional[str]
    stems_asset_ids: List[str]
    team: List[MusicRoomTeamItem]
    critique: Optional[MusicRoomCritique]
    listening: Optional[MusicRoomListening]
    robot_score: Optional[float]
    copy_risk: Optional[MusicRoomCopyRisk]
    credits: List[str]
    quota: MusicRoomQuota
    budget_micro_usd: str
    spent_micro_usd: str
    warnings: List[str]
    error: Optional[str]
    created_at: str


class MusicRoomChooseOption1(TypedDict):
    """Plan gate answer"""
    gate: Literal['plan']
    variant: int


class MusicRoomChooseOption2(TypedDict):
    """Demo gate answer"""
    gate: Literal['demo']
    approve: Literal[True]


class MusicRoomChooseOption3(TypedDict):
    """Final gate answer"""
    gate: Literal['final']
    approve: Literal[True]


# The answer to the gate the song waits at.
MusicRoomChoose = Union[MusicRoomChooseOption1, MusicRoomChooseOption2, MusicRoomChooseOption3]


class _MusicRoomDirectRequired(TypedDict):
    role: MusicRole
    direction: str


class MusicRoomDirect(_MusicRoomDirectRequired, total=False):
    """Music Room direction"""
    section_id: str


class MusicPluginValidation(TypedDict):
    """Result of the codai plugin validator on the cloud build (load, state round trip, render, determinism, 44.1 kHz…"""
    verdict: Literal['compatible', 'limited']
    issues: List[str]


class MusicPluginParamsItem(TypedDict):
    id: int
    name: str
    min: float
    max: float
    default: float
    hint: str


class _MusicPluginRequired(TypedDict):
    object: Literal['studio.music_plugin']
    format: Literal['clap', 'vst3']
    plugin_id: str
    name: str
    vendor: str
    version: str
    kind: Literal['instrument', 'effect']
    licence: Literal['GPL-3.0-or-later', 'LGPL-3.0-or-later', 'MIT']
    credit: str
    source: str
    summary: str
    good_for: List[str]
    where: Literal['cloud']
    desktop_install: bool
    params: List[MusicPluginParamsItem]


class MusicPlugin(_MusicPluginRequired, total=False):
    """A plugin of the codai cloud plugin set."""
    validation: Optional[MusicPluginValidation]


class MusicPluginList(TypedDict):
    """Music Room plugin list"""
    object: Literal['list']
    data: List[MusicPlugin]


class MusicPluginRefInputParamsItem(TypedDict):
    id: int
    value: float


class _MusicPluginRefInputRequired(TypedDict):
    format: Literal['clap', 'vst3']
    plugin_id: str


class MusicPluginRefInput(_MusicPluginRefInputRequired, total=False):
    """A plugin on a track. Cloud plugins fill `name`, `vendor` and version and default to `where: cloud`; a desktop-…"""
    name: str
    vendor: str
    where: Literal['cloud', 'local']
    preset: str
    params: List[MusicPluginRefInputParamsItem]
    state_b64: str


class _MusicRoomSetPluginRequired(TypedDict):
    role: MusicRole
    plugin: Optional[MusicPluginRefInput]


class MusicRoomSetPlugin(_MusicRoomSetPluginRequired, total=False):
    """Music Room player plugin"""
    effects: List[MusicPluginRefInput]


class _MusicRoomListRequired(TypedDict):
    object: Literal['list']
    data: List[MusicRoom]


class MusicRoomList(_MusicRoomListRequired, total=False):
    """Music Room song list"""
    has_more: bool


class CreativeTemplateList(TypedDict):
    """Creative template list"""
    object: Literal['list']
    data: List[CreativeTemplate]


class CreativeTemplateDeleted(TypedDict):
    """Creative template deleted"""
    id: str
    object: Literal['studio.template']
    deleted: Literal[True]


class _CreativePrintLintIssueRequired(TypedDict):
    code: str
    severity: Literal['error', 'warning']
    message: str
    target: str


class CreativePrintLintIssue(_CreativePrintLintIssueRequired, total=False):
    """Prepress issue"""
    value: float
    format: str
    fixable: bool


class StudioExportError(TypedDict):
    """Why the export failed (`timeout`, `too_large`, a render error code); `null` otherwise."""
    code: str
    message: str


class _StudioExportRequired(TypedDict):
    id: str
    object: Literal['studio.export']
    status: Literal['queued', 'running', 'succeeded', 'failed']
    creative_id: str
    seq: int
    format: str
    fps: Literal[24, 25, 30]
    filename: str
    url: Optional[str]
    expires_at: Optional[str]
    bytes: Optional[int]
    rendered_seconds: Optional[float]
    cost_micro_usd: Optional[int]
    warnings: List[str]
    error: Optional[StudioExportError]
    created_at: str


class StudioExport(_StudioExportRequired, total=False):
    """An export of a video creative, downloadable once `status` is `succeeded`: an FCPXML zip with `project.fcpxml` …"""
    kind: Literal['fcpxml', 'lottie', 'carousel_png', 'carousel_pdf', 'print_pdf']
    pages: Optional[int]
    boxes: Optional[bool]
    lint: List[CreativePrintLintIssue]
    container: Literal['json', 'dotlottie']


class StudioBatchCreateRequestSource(TypedDict, total=False):
    """Exactly one of `template_id` or `creative_id` (optionally at `seq`)."""
    template_id: str
    creative_id: str
    seq: int


class _StudioBatchCreateRequestSheetRequired(TypedDict):
    creative_id: str


class StudioBatchCreateRequestSheet(_StudioBatchCreateRequestSheetRequired, total=False):
    """A sheet creative whose first (or `node_id`) table is the data. Exactly one of `csv` or `sheet`."""
    node_id: str


class StudioBatchCreateRequestLocalize(TypedDict, total=False):
    """Options for rows with a `locale` column."""
    tone: Literal['formal', 'informal']
    glossary: List[str]


class _StudioBatchCreateRequestRequired(TypedDict):
    source: StudioBatchCreateRequestSource


class StudioBatchCreateRequest(_StudioBatchCreateRequestRequired, total=False):
    """Batch request"""
    csv: str
    sheet: StudioBatchCreateRequestSheet
    delimiter: Literal[',', ';', '\t']
    mapping: Dict[str, Optional[str]]
    title: str
    render: bool
    quality: StudioRenderQuality
    format: str
    ai_label: StudioRenderAiLabel
    localize: StudioBatchCreateRequestLocalize
    dry_run: bool


class StudioBatchColumn(TypedDict):
    """Batch column"""
    name: str
    index: int
    maps_to: Optional[str]
    kind: Literal['var', 'reserved', 'ignored']


class _StudioBatchRowErrorRequired(TypedDict):
    row: int
    message: str


class StudioBatchRowError(_StudioBatchRowErrorRequired, total=False):
    """Batch row error"""
    column: Optional[str]


class StudioBatchDryRunPreviewItem(TypedDict):
    row: int
    title: Optional[str]
    locale: Optional[str]
    format: Optional[str]
    vars: Dict[str, Any]


class StudioBatchDryRunEstimate(TypedDict):
    renders: int
    localized_rows: int


class StudioBatchDryRun(TypedDict):
    """Batch dry run"""
    dry_run: Literal[True]
    columns: List[StudioBatchColumn]
    unmapped_vars: List[str]
    rows: int
    valid: int
    errors: List[StudioBatchRowError]
    preview: List[StudioBatchDryRunPreviewItem]
    estimate: StudioBatchDryRunEstimate


# Batch status
StudioBatchStatus = Literal['queued', 'running', 'completed', 'failed', 'cancelled']


# Batch row status
StudioBatchRowStatus = Literal['pending', 'created', 'localized', 'rendering', 'done', 'failed', 'skipped']


class StudioBatchSource(TypedDict):
    kind: Literal['template', 'creative']
    id: str
    seq: Optional[int]


class StudioBatchColumns(TypedDict):
    """The CSV header and the column mapping."""
    header: List[str]
    columns: List[StudioBatchColumn]
    unmapped_vars: List[str]


class StudioBatchZip(TypedDict):
    status: Literal['none', 'building', 'ready', 'failed']
    url: Optional[str]
    error: Optional[str]


class StudioBatch(TypedDict):
    """Studio batch"""
    id: str
    title: str
    status: StudioBatchStatus
    source: StudioBatchSource
    total: int
    done: int
    failed: int
    pending: int
    skipped: int
    options: Dict[str, Any]
    columns: StudioBatchColumns
    cost_micro_usd: Union[str, int]
    zip: StudioBatchZip
    created_at: str
    updated_at: str
    finished_at: Optional[str]


class StudioBatchRow(TypedDict):
    """Batch row"""
    idx: int
    status: StudioBatchRowStatus
    creative_id: Optional[str]
    render_id: Optional[str]
    render_url: Optional[str]
    locale: Optional[str]
    title: Optional[str]
    error: Optional[str]
    cost_micro_usd: Union[str, int]


class _StudioBatchDetailRequired(TypedDict):
    batch: StudioBatch


class StudioBatchDetail(_StudioBatchDetailRequired, total=False):
    """Batch with rows"""
    rows: List[StudioBatchRow]


class StudioBatchList(TypedDict):
    """Batch list"""
    batches: List[StudioBatch]
    next_before: Optional[str]


class _CreativeVariantsRequestRequired(TypedDict):
    base_seq: int


class CreativeVariantsRequest(_CreativeVariantsRequestRequired, total=False):
    """Variants request"""
    count: int
    focus: List[Literal['hook', 'title', 'cta', 'visual', 'copy']]
    brief: str
    render: bool
    format: str


class _CreativeVariantRequired(TypedDict):
    creative_id: str
    label: str
    rationale: str
    applied_ops: int
    head_seq: int
    render_id: Optional[str]


class CreativeVariant(_CreativeVariantRequired, total=False):
    """Variant"""
    render_error: str


class CreativeVariantsResult(TypedDict):
    """Variants result"""
    object: Literal['studio.creative.variants']
    group_id: str
    base_seq: int
    variants: List[CreativeVariant]


class _CreativeVariantListVariantsItemRenderRequired(TypedDict):
    id: str
    status: Literal['queued', 'succeeded', 'failed']


class CreativeVariantListVariantsItemRender(_CreativeVariantListVariantsItemRenderRequired, total=False):
    """Stored state of the draft render (`queued` until a poll finishes it)."""
    poster_url: Optional[str]
    url: Optional[str]
    error: str


class CreativeVariantListVariantsItem(TypedDict):
    creative_id: str
    title: str
    label: str
    rationale: str
    status: Literal['candidate', 'winner', 'rejected']
    applied_ops: int
    head_seq: int
    render_id: Optional[str]
    render: Optional[CreativeVariantListVariantsItemRender]


class CreativeVariantList(TypedDict):
    """Variant list"""
    object: Literal['studio.creative.variants']
    group_id: Optional[str]
    base_seq: Optional[int]
    variants: List[CreativeVariantListVariantsItem]


class CreativeVariantPickRequest(TypedDict):
    """Pick request"""
    base_seq: int


class CreativeVariantPickResultVersion(TypedDict):
    seq: int
    doc_hash: str


class CreativeVariantPickResult(TypedDict):
    """Pick result"""
    head_seq: int
    version: CreativeVariantPickResultVersion
    winner: str
    rebased: bool


# `view` = read-only preview (optionally remixable); `review` = comments and, with `can_approve`, decisions.
StudioShareKind = Literal['view', 'review']


class _StudioShareCreateRequestRequired(TypedDict):
    kind: StudioShareKind


class StudioShareCreateRequest(_StudioShareCreateRequestRequired, total=False):
    """Share link request"""
    label: str
    expires_in_days: Union[int, str]
    seq: int
    allow_remix: bool
    can_approve: bool


class StudioShare(TypedDict):
    """Share link"""
    id: str
    object: Literal['studio.share']
    kind: StudioShareKind
    url: None
    label: str
    pinned_seq: Optional[int]
    allow_remix: bool
    can_approve: bool
    expires_at: Optional[str]
    created_at: str
    last_used_at: Optional[str]


class StudioShareCreated(TypedDict):
    """New share link"""
    id: str
    object: Literal['studio.share']
    kind: StudioShareKind
    token: str
    url: str
    label: str
    pinned_seq: Optional[int]
    allow_remix: bool
    can_approve: bool
    expires_at: Optional[str]
    created_at: str


class StudioShareList(TypedDict):
    """Share link list"""
    object: Literal['list']
    data: List[StudioShare]


# `draft` → `in_review` → `approved` or `changes_requested`.
StudioReviewStatus = Literal['draft', 'in_review', 'approved', 'changes_requested']


class StudioReviewThreads(TypedDict):
    open: int
    total: int


class StudioReview(TypedDict):
    """Review state"""
    object: Literal['studio.review']
    creative_id: str
    status: StudioReviewStatus
    head_seq: int
    requested_seq: Optional[int]
    requested_at: Optional[str]
    approved_seq: Optional[int]
    approved_doc_hash: Optional[str]
    approved_is_head: bool
    decided_by: Optional[str]
    decided_at: Optional[str]
    decision_note: Optional[str]
    threads: StudioReviewThreads


class StudioReviewUpdateRequest(TypedDict):
    """Review action"""
    action: Literal['request', 'reset']


class StudioReviewCommentAuthor(TypedDict):
    kind: Literal['owner', 'reviewer']
    name: Optional[str]


class StudioReviewComment(TypedDict):
    """Review comment"""
    id: str
    kind: Literal['comment', 'decision']
    decision: Optional[Literal['approve', 'request_changes']]
    author: StudioReviewCommentAuthor
    body: str
    created_at: str


class StudioReviewThread(TypedDict):
    """Review thread"""
    id: str
    node_id: Optional[str]
    scene_id: Optional[str]
    t_ms: Optional[int]
    seq: int
    status: Literal['open', 'resolved']
    resolved_by: Optional[str]
    resolved_at: Optional[str]
    created_at: str
    comments: List[StudioReviewComment]


class StudioReviewThreadList(TypedDict):
    """Review thread list"""
    object: Literal['list']
    data: List[StudioReviewThread]


class _StudioReviewThreadCreateRequestRequired(TypedDict):
    body: str


class StudioReviewThreadCreateRequest(_StudioReviewThreadCreateRequestRequired, total=False):
    """New owner thread"""
    node_id: str
    scene_id: str
    t_ms: int


class StudioReviewReplyRequest(TypedDict):
    """Owner reply"""
    body: str


class StudioVoiceSingingConsentRequest(TypedDict):
    session_id: str


class StudioVoiceSinging(TypedDict):
    """Singing consent (beta)"""
    status: Literal['none', 'active', 'revoked']
    consented_at: Optional[str]
    revoked_at: Optional[str]
    quality: Literal['beta']


class StudioVoice(TypedDict):
    """Custom voice"""
    id: str
    object: Literal['studio.voice']
    label: str
    locale: str
    kind: Literal['ai_clone']
    display_name: str
    created_at: str
    singing: StudioVoiceSinging


class _StudioVoiceRevocationRequestRequired(TypedDict):
    email: str
    voice_owner_name: str
    details: str


class StudioVoiceRevocationRequest(_StudioVoiceRevocationRequestRequired, total=False):
    """Voice takedown request"""
    evidence_url: str


class StudioVoiceRevocation(TypedDict):
    """Voice takedown ticket"""
    id: str
    object: Literal['studio.voice_revocation']
    status: Literal['open']


class StudioAbuseReportRequest(TypedDict):
    """Abuse report"""
    share_token: str
    surface: Literal['share', 'review']
    category: Literal['voice_without_consent', 'impersonation', 'fraud', 'election', 'illegal_other', 'other']
    explanation: str
    reporter_name: str
    reporter_email: str
    good_faith: Literal[True]


class StudioAbuseReport(TypedDict):
    """Abuse report ticket"""
    id: str
    object: Literal['studio.abuse_report']
    status: Literal['open']


class StudioRemixRequest(TypedDict, total=False):
    """Remix request"""
    title: str


class StudioRemixResultVersion(TypedDict):
    seq: int
    doc_hash: str


class StudioRemixResultRemixedFrom(TypedDict):
    share_id: str
    seq: int


class _StudioRemixResultRequired(TypedDict):
    id: str
    object: Literal['studio.creative']
    kind: CreativeKind
    title: str
    head_seq: int
    version: StudioRemixResultVersion
    doc: CreativeDoc
    remixed_from: StudioRemixResultRemixedFrom


class StudioRemixResult(_StudioRemixResultRequired, total=False):
    """Remix result"""
    warnings: List[str]


class StudioPublicReview(TypedDict):
    """Public review state"""
    status: StudioReviewStatus
    requested_seq: Optional[int]
    approved_seq: Optional[int]
    approved_is_head: bool
    decided_by: Optional[str]
    decided_by_kind: Literal['self_declared']
    decided_at: Optional[str]


class StudioPublicShareFormatsItem(TypedDict):
    id: str
    width: int
    height: int


class StudioPublicShareCompiledOption2(TypedDict):
    format: str
    width: int
    height: int
    duration_ms: int
    html: str


class StudioPublicShare(TypedDict):
    """Shared creative"""
    object: Literal['studio.public_share']
    kind: StudioShareKind
    title: str
    creative_kind: CreativeKind
    seq: int
    doc_hash: str
    allow_remix: bool
    can_approve: bool
    formats: List[StudioPublicShareFormatsItem]
    default_format: str
    locales: List[str]
    compiled: Optional[StudioPublicShareCompiledOption2]
    review: Optional[StudioPublicReview]
    threads: Optional[List[StudioReviewThread]]


class _StudioPublicThreadCreateRequestRequired(TypedDict):
    name: str
    body: str


class StudioPublicThreadCreateRequest(_StudioPublicThreadCreateRequestRequired, total=False):
    """New reviewer thread"""
    node_id: str
    scene_id: str
    t_ms: int


class StudioPublicReplyRequest(TypedDict):
    """Reviewer reply"""
    name: str
    body: str


class StudioPublicNameRequest(TypedDict):
    """Reviewer name"""
    name: str


class _StudioPublicDecisionRequestRequired(TypedDict):
    name: str
    decision: Literal['approve', 'request_changes']
    seq: int


class StudioPublicDecisionRequest(_StudioPublicDecisionRequestRequired, total=False):
    """Review decision"""
    note: str


class CreativeErrorErrorConflictsItem(TypedDict, total=False):
    target: str
    head_prop: str
    prop: str


class _CreativeErrorErrorRequired(TypedDict):
    message: str
    type: str
    code: Literal['invalid_request', 'stale', 'invalid', 'not_found', 'locked', 'duplicate_id', 'too_large', 'not_supported_for_kind', 'unsupported_format', 'asset_not_found', 'not_implemented', 'frame_failed', 'too_many_frame_jobs', 'no_edit', 'timeout', 'fetch_failed', 'extract_failed', 'kind_mismatch', 'node_not_found', 'invalid_pick', 'duplicate_key', 'unknown_var', 'invalid_var_value', 'unsupported_kind', 'too_long', 'ai_label_required', 'no_lyrics', 'unsupported_media']


class CreativeErrorError(_CreativeErrorErrorRequired, total=False):
    head_seq: int
    conflicts: List[CreativeErrorErrorConflictsItem]
    path: str
    op_index: int
    max_bytes: int
    kind: str
    text: str
    reason: str


class CreativeError(TypedDict):
    """The standard error envelope; creative errors add fields inside `error`: `head_seq` and `conflicts` on 409"""
    error: CreativeErrorError


class CreativeBuildRequest(TypedDict, total=False):
    """Creative build request"""
    seq: int
    preview: bool
    filename: str


class StudioCreativeFromDocumentVersion(TypedDict):
    seq: int
    doc_hash: str


class StudioCreativeFromDocument(TypedDict):
    """The creative made from (or already linked to) a Studio document, at its head version."""
    id: str
    object: Literal['studio.creative']
    kind: CreativeKind
    title: str
    head_seq: int
    version: StudioCreativeFromDocumentVersion
    doc: CreativeDoc
    document_id: str
    existing: bool


class DocumentPreviewOption1(TypedDict):
    id: str
    object: Literal['studio.preview']
    status: Literal['queued']


class _DocumentRequired(TypedDict):
    id: str
    object: Literal['studio.document']
    type: Optional[Literal['deck', 'doc', 'sheet']]
    theme: Optional[str]
    model: str
    title: Optional[str]
    version: int
    based_on: Optional[str]
    warnings: List[str]
    file: AssetDto


class Document(_DocumentRequired, total=False):
    """Studio document"""
    cost_micro_usd: str
    preview: Optional[DocumentPreviewOption1]
    spec: Optional[Dict[str, Any]]
    latest_preview_id: Optional[str]
    creative_id: Optional[str]


class StudioCreativeBuild(TypedDict):
    """A deck, doc or sheet creative built into a new version of its Studio document."""
    object: Literal['studio.creative_build']
    creative_id: str
    seq: int
    warnings: List[str]
    document: Document


class CreativePagedBuildRequest(TypedDict, total=False):
    """Carousel / print build request"""
    seq: int
    format: Literal['png', 'pdf']
    format_id: str
    crop_marks: bool
    filename: str
    preview: bool


class StudioCreativePagedBuildPrint(TypedDict, total=False):
    """Print PDFs only — physical sheet and PDF boxes."""
    sheet_mm: List[float]
    trim_offsets_pt: Optional[List[float]]
    bleed_offsets_pt: Optional[List[float]]
    color_profile: str
    crop_marks: bool
    pdf_x4: bool


class StudioCreativePagedBuild(TypedDict):
    """A carousel or print creative queued for its paged export; download it from `export.url` once the export succee…"""
    object: Literal['studio.creative_build']
    creative_id: str
    seq: int
    kind: Literal['carousel', 'print']
    format: Literal['png', 'pdf']
    format_id: str
    pages: int
    quote_micro_usd: str
    warnings: List[str]
    lint: List[CreativePrintLintIssue]
    print: Optional[StudioCreativePagedBuildPrint]
    document: None
    export: StudioExport


class StudioPostCopyRequest(TypedDict, total=False):
    """Post copy request"""
    platforms: List[Literal['instagram', 'linkedin', 'tiktok', 'x', 'facebook']]
    language: Literal['ro', 'en']
    brief: str
    tone: str
    seq: int


class StudioPostCopyPlatformsItemLimits(TypedDict, total=False):
    caption: int
    hashtags: int
    alt: int


class StudioPostCopyPlatformsItem(TypedDict):
    platform: Literal['instagram', 'linkedin', 'tiktok', 'x', 'facebook']
    caption: str
    hashtags: List[str]
    text: str
    chars: int
    limits: StudioPostCopyPlatformsItemLimits


class StudioPostCopyAltItem(TypedDict):
    scene_id: str
    text: str


class StudioPostCopyFixesItem(TypedDict, total=False):
    platform: str
    field: Literal['caption', 'hashtags', 'alt']
    message: str


class StudioPostCopy(TypedDict):
    """Post copy"""
    object: Literal['studio.post_copy']
    creative_id: str
    seq: int
    kind: Literal['carousel', 'image', 'video']
    language: Literal['ro', 'en']
    platforms: List[StudioPostCopyPlatformsItem]
    alt: List[StudioPostCopyAltItem]
    fixes: List[StudioPostCopyFixesItem]
    cost_micro_usd: str


class StudioSceneRegenerateVisualOption1(TypedDict):
    asset_id: str


class StudioSceneRegenerateVisualOption2(TypedDict, total=False):
    prompt: str
    model: str
    seconds: Literal[4, 6, 8]


class StudioSceneRegenerateNarrationOption1(TypedDict):
    asset_id: str


class StudioSceneRegenerateNarrationOption2(TypedDict, total=False):
    text: str
    voice: str


class StudioSceneRegenerate(TypedDict, total=False):
    """At least one of `visual` and `narration` is required."""
    visual: Union[StudioSceneRegenerateVisualOption1, StudioSceneRegenerateVisualOption2]
    narration: Optional[Union[StudioSceneRegenerateNarrationOption1, StudioSceneRegenerateNarrationOption2]]
    quality: StudioRenderQuality


class _StudioSceneRegenerateAcceptedRequired(TypedDict):
    id: str
    object: Literal['studio.render']
    status: Literal['queued']
    parent_render_id: str
    root_render_id: str
    scene_id: str
    scene_cost_micro_usd: str
    price_micro_usd_per_second: str
    minimum_micro_usd: str


class StudioSceneRegenerateAccepted(_StudioSceneRegenerateAcceptedRequired, total=False):
    """Queued scene regeneration"""
    ai_label: StudioRenderAiLabel


# `codai-light` / `codai-dark` use Manrope and the codai brand colours; `corporate` uses Aptos (Office falls bac…
DocumentTheme = Literal['codai-light', 'codai-dark', 'corporate']


class _DocumentRunRequired(TypedDict):
    text: str


class DocumentRun(_DocumentRunRequired, total=False):
    """A piece of text with inline formatting."""
    bold: bool
    italic: bool
    underline: bool
    code: bool
    link: str
    footnote: str


# Plain text (up to 10 000 characters) or 1..200 formatted runs.
DocumentRichText = Union[str, List[DocumentRun]]


class DocumentBulletOption2(TypedDict):
    text: DocumentRichText
    level: int


# A list item: rich text, or `{ text, level }` with an indent level of 0..3.
DocumentBullet = Union[DocumentRichText, DocumentBulletOption2]


class _DocumentImageRequired(TypedDict):
    asset_id: str
    alt: str


class DocumentImage(_DocumentImageRequired, total=False):
    """One of your ready image assets. `alt` is required (accessibility; it becomes the alt text in the file and the …"""
    caption: str


class DocumentChartSeriesItem(TypedDict):
    name: str
    values: List[float]


class _DocumentChartRequired(TypedDict):
    chart_type: Literal['bar', 'column', 'line', 'area', 'pie', 'doughnut', 'scatter', 'vega']
    alt: str


class DocumentChart(_DocumentChartRequired, total=False):
    """Native editable chart in PPTX; in DOCX and XLSX (and for `vega` everywhere) a Vega-Lite PNG, with the data as …"""
    title: str
    categories: List[str]
    series: List[DocumentChartSeriesItem]
    stacked: bool
    number_format: str
    vega_lite: Dict[str, Any]


class _DocumentTableRequired(TypedDict):
    columns: List[str]
    rows: List[List[Optional[Union[str, float]]]]


class DocumentTable(_DocumentTableRequired, total=False):
    """A table of 1..20 columns and up to 500 rows; a row may be shorter than `columns`, never longer."""
    header: bool
    align: List[Literal['left', 'center', 'right']]
    caption: str


class DocumentColumn(TypedDict, total=False):
    """One side of a `two_column` slide."""
    heading: str
    text: DocumentRichText
    bullets: List[DocumentBullet]
    image: DocumentImage
    chart: DocumentChart


class _DeckSlideOption1Required(TypedDict):
    layout: Literal['title']
    title: str


class DeckSlideOption1(_DeckSlideOption1Required, total=False):
    """Title slide."""
    subtitle: str
    notes: str


class _DeckSlideOption2Required(TypedDict):
    layout: Literal['section']
    title: str


class DeckSlideOption2(_DeckSlideOption2Required, total=False):
    """Section divider."""
    subtitle: str
    notes: str


class _DeckSlideOption3Required(TypedDict):
    layout: Literal['bullets']
    title: str
    bullets: List[DocumentBullet]


class DeckSlideOption3(_DeckSlideOption3Required, total=False):
    """Title and 1..12 bullets."""
    notes: str


class _DeckSlideOption4Required(TypedDict):
    layout: Literal['two_column']
    title: str
    left: DocumentColumn
    right: DocumentColumn


class DeckSlideOption4(_DeckSlideOption4Required, total=False):
    """Two columns."""
    notes: str


class _DeckSlideOption5Required(TypedDict):
    layout: Literal['image']
    image: DocumentImage


class DeckSlideOption5(_DeckSlideOption5Required, total=False):
    """Full image."""
    title: str
    notes: str


class _DeckSlideOption6Required(TypedDict):
    layout: Literal['chart']
    title: str
    chart: DocumentChart


class DeckSlideOption6(_DeckSlideOption6Required, total=False):
    """One chart."""
    notes: str


class _DeckSlideOption7Required(TypedDict):
    layout: Literal['table']
    title: str
    table: DocumentTable


class DeckSlideOption7(_DeckSlideOption7Required, total=False):
    """One table."""
    notes: str


class _DeckSlideOption8Required(TypedDict):
    layout: Literal['quote']
    quote: str


class DeckSlideOption8(_DeckSlideOption8Required, total=False):
    """A quotation."""
    attribution: str
    notes: str


class _DeckSlideOption9StatsItemRequired(TypedDict):
    value: str
    label: str


class DeckSlideOption9StatsItem(_DeckSlideOption9StatsItemRequired, total=False):
    delta: str


class _DeckSlideOption9Required(TypedDict):
    layout: Literal['stats']
    stats: List[DeckSlideOption9StatsItem]


class DeckSlideOption9(_DeckSlideOption9Required, total=False):
    """1..4 big numbers."""
    title: str
    notes: str


class _DeckSlideOption10ItemsItemRequired(TypedDict):
    date: str
    label: str


class DeckSlideOption10ItemsItem(_DeckSlideOption10ItemsItemRequired, total=False):
    detail: str


class _DeckSlideOption10Required(TypedDict):
    layout: Literal['timeline']
    title: str
    items: List[DeckSlideOption10ItemsItem]


class DeckSlideOption10(_DeckSlideOption10Required, total=False):
    """A timeline of 2..8 items."""
    notes: str


class _DeckSlideOption11Required(TypedDict):
    layout: Literal['closing']
    title: str


class DeckSlideOption11(_DeckSlideOption11Required, total=False):
    """Closing slide."""
    subtitle: str
    contact: str
    notes: str


# A slide, chosen by `layout`. Every layout accepts `notes`.
DeckSlide = Union[DeckSlideOption1, DeckSlideOption2, DeckSlideOption3, DeckSlideOption4, DeckSlideOption5, DeckSlideOption6, DeckSlideOption7, DeckSlideOption8, DeckSlideOption9, DeckSlideOption10, DeckSlideOption11]


class _DeckSpecRequired(TypedDict):
    slides: List[DeckSlide]


class DeckSpec(_DeckSpecRequired, total=False):
    """Spec of a `deck` (PPTX), 1..60 slides."""
    aspect: Literal[969, 243]
    footer: str
    slide_numbers: bool


class DocBlockOption1(TypedDict):
    """Heading level 1..4."""
    type: Literal['heading']
    level: int
    text: str


class _DocBlockOption2Required(TypedDict):
    type: Literal['paragraph']
    text: DocumentRichText


class DocBlockOption2(_DocBlockOption2Required, total=False):
    """Paragraph."""
    align: Literal['left', 'center', 'right', 'justify']


class _DocBlockOption3Required(TypedDict):
    type: Literal['list']
    items: List[DocumentBullet]


class DocBlockOption3(_DocBlockOption3Required, total=False):
    """Bulleted or numbered list."""
    ordered: bool


class DocBlockOption4(TypedDict):
    """Table."""
    type: Literal['table']
    table: DocumentTable


class DocBlockOption5(TypedDict):
    """Image."""
    type: Literal['image']
    image: DocumentImage


class DocBlockOption6(TypedDict):
    """Chart."""
    type: Literal['chart']
    chart: DocumentChart


class _DocBlockOption7Required(TypedDict):
    type: Literal['quote']
    text: str


class DocBlockOption7(_DocBlockOption7Required, total=False):
    """Quotation."""
    attribution: str


class DocBlockOption8(TypedDict):
    """Page break."""
    type: Literal['page_break']


# A block of a `doc`, chosen by `type`.
DocBlock = Union[DocBlockOption1, DocBlockOption2, DocBlockOption3, DocBlockOption4, DocBlockOption5, DocBlockOption6, DocBlockOption7, DocBlockOption8]


class _DocSpecRequired(TypedDict):
    blocks: List[DocBlock]


class DocSpec(_DocSpecRequired, total=False):
    """Spec of a `doc` (DOCX), 1..2000 blocks."""
    page_size: Literal['A4', 'Letter']
    orientation: Literal['portrait', 'landscape']
    header: str
    footer: str
    page_numbers: bool
    toc: bool


class SheetCellOption5(TypedDict):
    formula: str


class SheetCellOption6(TypedDict):
    date: str


# A cell: text, number, boolean, empty, `{ formula }` (without the leading `=`) or `{ date }` (ISO date or datet…
SheetCell = Optional[Union[str, float, bool, SheetCellOption5, SheetCellOption6]]


class _SheetColumnsItemRequired(TypedDict):
    header: str


class SheetColumnsItem(_SheetColumnsItemRequired, total=False):
    width: float
    format: Literal['text', 'integer', 'number', 'percent', 'ron', 'eur', 'usd', 'date', 'datetime']


class _SheetConditionalItemRequired(TypedDict):
    range: str
    rule: Literal['gt', 'lt', 'between', 'eq', 'color_scale', 'data_bar']


class SheetConditionalItem(_SheetConditionalItemRequired, total=False):
    value: float
    value2: float
    style: Literal['good', 'bad', 'neutral']


class _SheetChartsItemRequired(TypedDict):
    chart: DocumentChart


class SheetChartsItem(_SheetChartsItemRequired, total=False):
    anchor: str


class _SheetRequired(TypedDict):
    name: str
    rows: List[List[SheetCell]]


class Sheet(_SheetRequired, total=False):
    """One worksheet. Column formats use ro-RO conventions: `ron` `#,##0.00 "lei"`, `eur` `#,##0.00 "€"`, `usd` `"$"#…"""
    columns: List[SheetColumnsItem]
    freeze_header: bool
    autofilter: bool
    totals: bool
    conditional: List[SheetConditionalItem]
    charts: List[SheetChartsItem]


class SheetSpec(TypedDict):
    """Spec of a `sheet` (XLSX): 1..20 uniquely named sheets, at most 200 000 cells in total."""
    sheets: List[Sheet]


class _DocumentCreateRequestRequired(TypedDict):
    type: Literal['deck', 'doc', 'sheet']
    spec: Union[DeckSpec, DocSpec, SheetSpec]


class DocumentCreateRequest(_DocumentCreateRequestRequired, total=False):
    """Studio document request"""
    model: Literal['codai-docs']
    theme: DocumentTheme
    title: str
    language: str
    filename: str
    based_on: str
    preview: bool


class DocumentPreviewAccepted(TypedDict):
    """Queued preview"""
    id: str
    object: Literal['studio.preview']
    status: Literal['queued']
    document_id: Optional[str]
    price_micro_usd_per_page: str
    minimum_micro_usd: str


class DocumentPreviewPagesItem(TypedDict):
    page: int
    url: str
    width: Optional[int]
    height: Optional[int]


class DocumentPreview(TypedDict):
    """Document preview"""
    id: str
    object: Literal['studio.preview']
    document_id: Optional[str]
    model: str
    status: Literal['queued', 'rendering', 'succeeded', 'failed']
    error: Optional[str]
    page_count: Optional[int]
    cost_micro_usd: str
    pdf: Optional[AssetDto]
    pages: List[DocumentPreviewPagesItem]
    contact_sheet_url: Optional[str]


class DocumentVideoRequestNarrate(TypedDict, total=False):
    """Speak each slide (notes, else title and bullets); billed now."""
    model: Literal['codai-speech', 'codai-speech-expressive']
    voice: str
    language: str
    instructions: str


class DocumentVideoRequest(TypedDict, total=False):
    """Deck video request"""
    quality: StudioRenderQuality
    seconds_per_slide: float
    transition: Literal['fade', 'none']
    music_asset_id: str
    narrate: DocumentVideoRequestNarrate


class _DocumentVideoAcceptedRequired(TypedDict):
    id: str
    object: Literal['studio.render']
    status: Literal['queued']
    model: str
    quality: StudioRenderQuality
    aspect_ratio: StudioRenderAspectRatio
    fps: int
    price_micro_usd_per_second: str
    minimum_micro_usd: str
    preview_id: str
    narration_cost_micro_usd: str
    slides: int
    duration_seconds: float


class DocumentVideoAccepted(_DocumentVideoAcceptedRequired, total=False):
    ai_label: StudioRenderAiLabel


class _CoreImageDataRequired(TypedDict):
    b64_json: str


class CoreImageData(_CoreImageDataRequired, total=False):
    """Generated image"""
    mime_type: str


class CoreImagesResponse(TypedDict):
    """Image generation response"""
    created: int
    data: List[Union[CoreImageData, AssetDto]]


class _CoreTranscriptionRequestRequired(TypedDict):
    file: bytes


class CoreTranscriptionRequest(_CoreTranscriptionRequestRequired, total=False):
    """Multipart form fields. Only the listed fields are forwarded; anything else is dropped."""
    model: Literal['codai-transcribe', 'whisper-1', 'whisper', 'gpt-4o-mini-transcribe']
    language: str
    prompt: str
    response_format: str
    temperature: str


class CoreTranscriptionResponse(TypedDict, total=False):
    """The upstream JSON is returned unchanged. With `verbose_json` extra fields (`language`, `duration`, `segments`,…"""
    text: str


class _CoreSpeechRequestRequired(TypedDict):
    input: str


class CoreSpeechRequest(_CoreSpeechRequestRequired, total=False):
    """Speech request"""
    model: Literal['codai-tts', 'tts-1', 'tts', 'codai-tts-expressive', 'gpt-4o-mini-tts', 'codai-speech', 'codai-speech-expressive']
    voice: str
    response_format: str
    speed: float
    instructions: str
    language: str
    timestamps: bool
    store: bool


class SpeechWord(TypedDict):
    """Word timing"""
    word: str
    start: float
    end: float


class _SpeechJsonRequired(TypedDict):
    object: Literal['audio.speech']
    model: str
    voice: str
    language: str
    mime_type: str
    duration_seconds: float
    cost_micro_usd: str


class SpeechJson(_SpeechJsonRequired, total=False):
    """Returned by `POST /v1/audio/speech` when `timestamps` or `store` is true."""
    b64_json: str
    asset: AssetDto
    words: Optional[List[SpeechWord]]


class MusicTrackMeta(TypedDict, total=False):
    """Extra fields on each `/v1/audio/music` item."""
    lyrics: Optional[str]
    caption: Optional[str]
    lyrics_match: Optional[float]
    warnings: List[str]


class _SpeechStreamRequestRequired(TypedDict):
    input: str


class SpeechStreamRequest(_SpeechStreamRequestRequired, total=False):
    """Streaming speech request"""
    model: Literal['codai-tts-ro', 'azure-speech']
    voice: str
    response_format: Literal['pcm', 'mp3']
    speed: float


class _SpeechStreamEventRequired(TypedDict):
    type: Literal['start', 'audio', 'viseme', 'word', 'done', 'error']


class SpeechStreamEvent(_SpeechStreamEventRequired, total=False):
    """The `data` of one SSE frame; the SSE `event` name equals `type`."""
    delta: str
    id: int
    offsetMs: int
    durationMs: int
    text: str
    voice: str
    format: str
    sample_rate: int
    audio_ms: Optional[int]


class _CoreTokenRequestRequired(TypedDict):
    scope: str


class CoreTokenRequest(_CoreTokenRequestRequired, total=False):
    """Ephemeral token request"""
    ttl_seconds: int


class CoreTokenResponse(TypedDict):
    """Ephemeral token"""
    token: str
    expires_at: str
    scope: Literal['realtime', 'audio', 'embeddings', 'live']


class CoreModelCapabilities(TypedDict):
    """Model capabilities"""
    tools: bool
    vision: bool
    streaming: bool
    maxInputTokens: int
    maxOutputTokens: int


class _CoreModelPricingRequired(TypedDict):
    input_usd_per_mtok: float
    output_usd_per_mtok: float
    cached_input_usd_per_mtok: float
    cache_write_usd_per_mtok: float
    exact: bool


class CoreModelPricing(_CoreModelPricingRequired, total=False):
    """List price in USD per million tokens, so a client can show a per-turn cost and a pre-turn estimate from the to…"""
    by_route: Dict[str, "CoreModelPricing"]


class _CoreModelCodaiRequired(TypedDict):
    kind: Literal['alias', 'concrete']
    type: Literal['chat', 'embedding']
    capabilities: CoreModelCapabilities


class CoreModelCodai(_CoreModelCodaiRequired, total=False):
    """Non-OpenAI extension with routing and capability flags."""
    routesTo: List[str]
    pricing: CoreModelPricing


class CoreModel(TypedDict):
    """Model"""
    id: str
    object: Literal['model']
    created: Literal[0]
    owned_by: Literal['codai', 'codai-upstream']
    codai: CoreModelCodai


class CoreModelList(TypedDict):
    """Model list"""
    object: Literal['list']
    data: List[CoreModel]


class CoreHealth(TypedDict):
    """Liveness"""
    ok: Literal[True]
    features: List[str]


class _CoreHealthCheckRequired(TypedDict):
    ok: bool


class CoreHealthCheck(_CoreHealthCheckRequired, total=False):
    """Readiness check"""
    error: str


class CoreHealthReadyChecks(TypedDict):
    db: CoreHealthCheck
    schema: CoreHealthCheck
    registry: CoreHealthCheck


class _CoreHealthReadyS1Required(TypedDict):
    mode: Literal[False, 'shadow', True]


class CoreHealthReadyS1(_CoreHealthReadyS1Required, total=False):
    """Informational reachability of the codai-s1 sidecar; never affects `ok`."""
    ok: bool
    ms: int
    error: str


class CoreHealthReady(TypedDict):
    """Readiness"""
    ok: bool
    checks: CoreHealthReadyChecks
    s1: CoreHealthReadyS1


class CoreStatusProvider(TypedDict):
    """Provider status"""
    id: str
    kind: str
    label: str
    healthy: bool


class CoreStatus(TypedDict):
    """Status"""
    ok: Literal[True]
    aliases: List[str]
    providers: List[CoreStatusProvider]


class _AgentRunRequestRequired(TypedDict):
    task: str


class AgentRunRequest(_AgentRunRequestRequired, total=False):
    """Body of `POST /v1/agents/run`."""
    context: str
    system: str
    model: str
    max_steps: int


class _AgentRunCreateRequestRequired(TypedDict):
    task: str


class AgentRunCreateRequest(_AgentRunCreateRequestRequired, total=False):
    """Body of `POST /v1/agents/runs`; extends the synchronous request."""
    context: str
    system: str
    model: str
    max_steps: int
    budget_seconds: int
    client_request_id: str


# Run lifecycle — `queued` → `running` → one of `completed`, `failed`, `cancelled`.
AgentRunStatus = Literal['queued', 'running', 'completed', 'failed', 'cancelled']


class AgentUsage(TypedDict):
    """Aggregate token counts for the whole run."""
    prompt_tokens: int
    completion_tokens: int


class AgentSyncResult(TypedDict):
    """Response of `POST /v1/agents/run`."""
    result: str
    status: Literal['completed']
    usage: AgentUsage
    model: str
    event_id: Optional[str]


class AgentRunAccepted(TypedDict):
    """Response of `POST /v1/agents/runs` (HTTP 202)."""
    id: str
    status: Literal['queued']
    poll: str


class AgentRun(TypedDict):
    """Poll view of a persisted run (`GET /v1/agents/runs/{id}`)."""
    id: str
    status: AgentRunStatus
    task: str
    model: Optional[str]
    result: Optional[str]
    error: Optional[str]
    step_count: int
    usage: AgentUsage
    created_at: str
    started_at: Optional[str]
    finished_at: Optional[str]


class AgentRunStep(TypedDict):
    """One persisted step, as stored (camelCase keys)."""
    id: str
    runId: str
    seq: int
    kind: Literal['plan', 'tool_call', 'observation', 'answer']
    summary: Optional[str]
    detail: Any
    latencyMs: Optional[int]
    createdAt: str


class _AgentRunStatsRequired(TypedDict):
    window_days: int
    total: int


class AgentRunStats(_AgentRunStatsRequired, total=False):
    """Aggregates over your runs in the window. Only `window_days` and `total` are guaranteed; the remaining"""
    completed: int
    failed: int
    cancelled: int
    in_flight: int
    prompt_tokens: int
    completion_tokens: int
    avg_steps: int
    avg_latency_ms: int


class _ToolSearchRequestRequired(TypedDict):
    query: str


class ToolSearchRequest(_ToolSearchRequestRequired, total=False):
    """Body of `POST /v1/tools/search`."""
    max_results: int
    freshness: Literal['day', 'week', 'month', 'year']
    include_domains: List[str]
    exclude_domains: List[str]
    published_after: str
    published_before: str
    content_chars: int
    country: str
    lang: str
    mode: Literal['codai', 'google', 'fast', 'deep']
    depth: Literal['fast', 'deep']
    fallback: Literal['auto', 'off']


class _ToolSearchResultRequired(TypedDict):
    title: str
    url: str
    snippet: str
    source: Literal['index', 'bnr', 'anm', 'fuel', 'osm', 'ins', 'wikipedia', 'github', 'stackexchange', 'docs', 'news', 'sitecc', 'commoncrawl', 'ddg', 'releases', 'registry', 'engine', 'mdn', 'mslearn', 'hn', 'osv', 'endoflife', 'openalex', 'crossref', 'arxiv', 'europepmc', 'doaj', 'core', 'wiktionary', 'openstax', 'ocw', 'dexonline', 'direct', 'slug', 'crawler']
    verified: Literal[True]


class ToolSearchResult(_ToolSearchResultRequired, total=False):
    """One result from codai-search; the snippet was confirmed on the fetched page."""
    page_age: str
    published_at: Optional[str]
    crawled_at: Optional[str]
    content: str


class ToolSearchResponseRerank(TypedDict):
    """Present when the cross-encoder reranker ran."""
    model: str
    ms: int
    n: int


class ToolSearchResponseGoogleSourcesItem(TypedDict, total=False):
    title: str
    url: str


class ToolSearchResponseGoogle(TypedDict, total=False):
    """Present only when the automatic fallback ran (see `fallback`). A separate result set from Grounding with"""
    answer: str
    sources: List[ToolSearchResponseGoogleSourcesItem]
    queries: List[str]
    search_suggestions_html: Optional[str]
    attribution: str
    cached: bool


class _ToolSearchResponseFallbackRequired(TypedDict):
    used: bool


class ToolSearchResponseFallback(_ToolSearchResponseFallbackRequired, total=False):
    """Whether the automatic Google fallback was used, and why."""
    hedged: bool
    reason: Literal['few_results', 'low_coverage', 'no_results', 'codai_unavailable', 'google_failed', 'budget_exhausted']


class _ToolSearchResponseRequired(TypedDict):
    results: List[ToolSearchResult]
    provider: Literal['codai']
    took_ms: int
    cached: bool
    coverage: float
    sources_tried: List[str]
    degraded: List[str]
    intent: Literal['currency', 'weather', 'encyclopedic', 'code', 'docs', 'site', 'news', 'price', 'local', 'fuel', 'inflation', 'local_poi', 'academic', 'definition', 'education', 'general']


class ToolSearchResponse(_ToolSearchResponseRequired, total=False):
    """The codai-search JSON, returned verbatim by the gateway."""
    notes: List[str]
    complete: bool
    rerank: ToolSearchResponseRerank
    google: ToolSearchResponseGoogle
    fallback: ToolSearchResponseFallback


class ToolSearchGoogleResponseSourcesItem(TypedDict):
    title: str
    url: str


class ToolSearchGoogleResponse(TypedDict):
    """Returned for `mode: google`. A short answer grounded by Google Search plus the pages it cites. Google's terms"""
    provider: Literal['google']
    answer: str
    sources: List[ToolSearchGoogleResponseSourcesItem]
    queries: List[str]
    search_suggestions_html: Optional[str]
    attribution: Literal['Grounding with Google Search']
    cached: bool


class _ToolSearchProviderResponseResultsItemRequired(TypedDict):
    title: str
    url: str
    snippet: str


class ToolSearchProviderResponseResultsItem(_ToolSearchProviderResponseResultsItemRequired, total=False):
    age: str


class ToolSearchProviderResponse(TypedDict):
    """Reduced shape returned only by gateways WITHOUT codai-search that configured a third-party search provider."""
    results: List[ToolSearchProviderResponseResultsItem]
    provider: str
    took_ms: int
    cached: bool


class _ToolFetchRequestRequired(TypedDict):
    url: str


class ToolFetchRequest(_ToolFetchRequestRequired, total=False):
    """Body of `POST /v1/tools/fetch`."""
    max_chars: int
    focus: str
    format: Literal['markdown', 'text']


class _ToolFetchResponseRequired(TypedDict):
    url: str
    final_url: str
    content_type: str
    content: str
    chars: int
    truncated: bool
    took_ms: int
    cached: bool


class ToolFetchResponse(_ToolFetchResponseRequired, total=False):
    """Extracted content plus metadata. Optional metadata keys are omitted when the page lacks them."""
    title: str
    byline: str
    description: str
    canonical: str
    lang: str


class _ResearchRequestRequired(TypedDict):
    question: str


class ResearchRequest(_ResearchRequestRequired, total=False):
    """Body of `POST /v1/research`."""
    time_budget_s: int
    max_sources: int
    include_domains: List[str]
    published_after: str
    output_schema: Dict[str, Any]
    wait_s: float


class ResearchSource(TypedDict):
    """Research source"""
    id: str
    title: str
    url: str


class ResearchJobError(TypedDict):
    message: str


class _ResearchJobRequired(TypedDict):
    id: str
    status: Literal['queued', 'running', 'done', 'failed']
    created_at: str


class ResearchJob(_ResearchJobRequired, total=False):
    """A deep-research job. Result fields are present only when `status` is `done`, `error` only when it is `failed`."""
    finished_at: str
    report: str
    answer: Dict[str, Any]
    sources: List[ResearchSource]
    searches: int
    pages_read: int
    error: ResearchJobError


class _CardDataResponseRequired(TypedDict):
    block: Optional[Dict[str, Any]]
    provenance: Dict[str, Any]


class CardDataResponse(_CardDataResponseRequired, total=False):
    """A ready-to-render card block from `@codai/cards` plus where its data came from."""
    results: List[Dict[str, Any]]
    route: Optional[Dict[str, Any]]
    result: Dict[str, Any]
    documents: List[Dict[str, Any]]


class ToolRulesRefusedErrorErrorDetails(TypedDict):
    tool: Literal['web_search', 'browser_fetch']
    rule_id: Optional[str]
    decision: str


class ToolRulesRefusedErrorError(TypedDict):
    message: str
    type: Literal['invalid_request_error']
    code: Literal['rules_refused']
    details: ToolRulesRefusedErrorErrorDetails


class ToolRulesRefusedError(TypedDict):
    """A rule of yours denied the tool call (HTTP 403)."""
    error: ToolRulesRefusedErrorError


# Task outcome. `open` while running; `pass`/`fail`/`error` from an exec verdict; `unconfirmed` after the idle
TaskOutcome = Literal['pass', 'fail', 'error', 'unconfirmed', 'confirmed', 'cancelled', 'open']


# What closed the task — a machine verdict, a re-execution, your confirmation, or nothing yet.
TaskEvidenceKind = Literal['exec_verdict', 'reexec', 'user_confirmed', 'none']


# Client surface that opened the task.
TaskSurface = Literal['proxy', 'desktop', 'cli', 'resolve', 'sandbox', 'mobile', 'hub']


class Task(TypedDict):
    """Wire view of a task. Money is integer micros (USD for cost, EUR for charges); dates are ISO 8601."""
    id: str
    surface: TaskSurface
    session_key: Optional[str]
    client_task_id: Optional[str]
    title: Optional[str]
    outcome: TaskOutcome
    evidence_kind: TaskEvidenceKind
    evidence_ref: Optional[str]
    requests: int
    cost_micro_usd: int
    charged_micro_eur: int
    billed_success: bool
    billable_at: Optional[str]
    confirm_deadline_at: Optional[str]
    opened_at: str
    last_activity_at: str
    closed_at: Optional[str]
    note: Optional[str]


# Counts over tasks opened at or after `since`.
TaskStats = TypedDict(
    'TaskStats',
    {
        'since': str,
        'opened': int,
        'confirmed': int,
        'pass': int,
        'unconfirmed': int,
        'billed': int,
    },
    total=True,
)


class _TaskConfirmRequestRequired(TypedDict):
    outcome: Literal['confirmed', 'fail']


class TaskConfirmRequest(_TaskConfirmRequestRequired, total=False):
    """Body of `POST /v1/tasks/{id}/confirm`."""
    note: str


class TaskConfirmResponse(TypedDict):
    """Outcome of the confirmation. Keys are camelCase, unlike the `Task` object."""
    taskId: str
    outcome: Literal['confirmed', 'fail']
    billed: bool
    refundedMicroEur: int


class TaskNotConfirmableErrorError(TypedDict):
    message: str
    type: Literal['invalid_request_error']
    code: Literal['task_not_confirmable']


class TaskNotConfirmableError(TypedDict):
    """The task cannot be confirmed any more (HTTP 409)."""
    error: TaskNotConfirmableErrorError


# Role of a principal on a session; `owner` ≥ `editor` ≥ `viewer`.
SessionRole = Literal['viewer', 'editor', 'owner']


# Kind of control a non-executor can send to the executor. `hydrate` asks the executor to upload the transcript …
SessionControlKind = Literal['send', 'answer', 'approve', 'deny', 'cancel', 'steer', 'inject', 'pause', 'resume', 'hydrate']


class Session(TypedDict):
    """A shared session as returned by create/patch and embedded in list/detail."""
    id: str
    session_key: str
    owner_user_id: str
    title: Optional[str]
    created_at: str
    last_event_at: str
    last_seq: int
    executor_device_id: Optional[str]
    lease_expires_at: Optional[str]
    e2e: bool
    archived: bool
    stub: bool


class SessionListItem(TypedDict):
    id: str
    session_key: str
    owner_user_id: str
    title: Optional[str]
    created_at: str
    last_event_at: str
    last_seq: int
    executor_device_id: Optional[str]
    lease_expires_at: Optional[str]
    e2e: bool
    archived: bool
    stub: bool
    role: SessionRole
    presence_count: int


class SessionMemberDevice(TypedDict):
    device_id: str
    name: str
    platform: Literal['android', 'ios', 'web', 'desktop', 'cli', 'agent']
    last_seen_at: str
    remote: bool


class SessionMember(TypedDict):
    user_id: str
    role: SessionRole
    remote: bool
    devices: List[SessionMemberDevice]


class SessionLease(TypedDict):
    """Live executor lease; `null` on the wire when free or expired."""
    device_id: str
    expires_at: str


class SessionPresence(TypedDict):
    """Ephemeral per-instance presence entry."""
    device_id: str
    user_id: str
    role: SessionRole
    executor: bool
    last_seen: int
    driving: bool
    remote: bool


class SessionDetail(TypedDict):
    id: str
    session_key: str
    owner_user_id: str
    title: Optional[str]
    created_at: str
    last_event_at: str
    last_seq: int
    executor_device_id: Optional[str]
    lease_expires_at: Optional[str]
    e2e: bool
    archived: bool
    stub: bool
    role: SessionRole
    members: List[SessionMember]
    lease: Optional[SessionLease]
    presence: List[SessionPresence]


class SessionCreateRequest(TypedDict, total=False):
    session_key: str
    title: str
    e2e: bool
    stub: bool


class SessionPatchRequest(TypedDict, total=False):
    """At least one of `title` / `archived` is required."""
    title: Optional[str]
    archived: bool


class SessionEvent(TypedDict):
    """SessionEvent"""
    seq: int
    kind: str
    ts: int
    sender_device_id: str
    turn_id: Optional[str]
    client_event_id: Optional[str]
    payload: Dict[str, Any]


class _SessionIncomingEventRequired(TypedDict):
    kind: str


class SessionIncomingEvent(_SessionIncomingEventRequired, total=False):
    ts: int
    turn_id: str
    client_event_id: str
    payload: Dict[str, Any]


class _SessionEventsAppendRequestRequired(TypedDict):
    events: List[SessionIncomingEvent]


class SessionEventsAppendRequest(_SessionEventsAppendRequestRequired, total=False):
    expected_last_seq: int


class SessionEventsAppendResponseEventsItem(TypedDict):
    client_event_id: Optional[str]
    seq: int


class SessionEventsAppendResponse(TypedDict):
    last_seq: int
    accepted: int
    events: List[SessionEventsAppendResponseEventsItem]


class _SessionControlRequestRequired(TypedDict):
    id: str
    kind: SessionControlKind


class SessionControlRequest(_SessionControlRequestRequired, total=False):
    text: str
    turn_id: str
    ask_id: str


class SessionControlAccepted(TypedDict):
    accepted: Literal[True]
    seq: Optional[int]
    duplicate: bool


class _SessionControlRequired(TypedDict):
    id: str
    kind: SessionControlKind
    text: Optional[str]
    turn_id: Optional[str]
    ask_id: Optional[str]
    from_device_id: str
    target_device_id: Optional[str]
    seq: Optional[int]
    applied: bool
    created_at: str


class SessionControl(_SessionControlRequired, total=False):
    """SessionControl"""
    mode: Literal['open']


class _SessionDispatchRequestRequired(TypedDict):
    device_id: str


class SessionDispatchRequest(_SessionDispatchRequestRequired, total=False):
    mode: Literal['send', 'open']
    text: str
    turn_id: str
    control_id: str


class _SessionDispatchResponseRequired(TypedDict):
    control_id: str
    seq: Optional[int]
    target_device_id: str
    mode: Literal['send', 'open']
    queued: Literal[True]
    pushed: bool
    duplicate: bool


class SessionDispatchResponse(_SessionDispatchResponseRequired, total=False):
    push_reason: str


class SessionLeaseClaimRequest(TypedDict, total=False):
    device_id: str
    force: bool


class SessionLeaseResponse(TypedDict):
    session_id: str
    device_id: str
    expires_at: str


class SessionDispatchInboxSessionsItem(TypedDict):
    id: str
    session_key: str
    title: Optional[str]
    controls: List[SessionControl]


class SessionDispatchInbox(TypedDict):
    device_id: str
    sessions: List[SessionDispatchInboxSessionsItem]


# Client platform; anything else sent in `x-codai-device-platform` is stored as `agent`.
DevicePlatform = Literal['android', 'ios', 'web', 'desktop', 'cli', 'agent']


class _DeviceListItemRequired(TypedDict):
    id: str
    name: str
    platform: DevicePlatform
    capabilities: List[str]
    has_push_token: bool
    lastSeenAt: str
    createdAt: str
    online: bool


class DeviceListItem(_DeviceListItemRequired, total=False):
    """One registered device. Keys are camelCase for the timestamps, snake_case for `has_push_token` — exactly as the…"""
    app_version: Optional[str]


class DevicePatch(TypedDict, total=False):
    """At least one of the two fields is required."""
    push_token: Optional[str]
    capabilities: List[str]


class DevicePatched(TypedDict):
    """Device (after patch)"""
    id: str
    name: str
    platform: DevicePlatform
    capabilities: List[str]
    has_push_token: bool
    lastSeenAt: str


# Operation vocabulary hosts implement (codai desktop; `iphone` = the codai iPhone bridge, cap `iphone`).
HostOp = Literal['shell', 'fs_read', 'fs_write', 'fs_list', 'fs_roots', 'info', 'iphone']


class _HostIphoneArgsRequired(TypedDict):
    tool: str


class HostIphoneArgs(_HostIphoneArgsRequired, total=False):
    """`args` of op `iphone`, validated by the gateway. Tool names and their arguments are those of the local `codai-…"""
    args: Dict[str, Any]


class HostPresence(TypedDict):
    """A device currently connected to `GET /v1/hosts/stream`."""
    device_id: str
    name: Optional[str]
    platform: Optional[str]
    os: Optional[str]
    hostname: Optional[str]
    roots: List[str]
    caps: List[str]
    environment_id: Optional[str]
    since: int
    last_seen: int


class _HostExecBodyRequired(TypedDict):
    op: HostOp


class HostExecBody(_HostExecBodyRequired, total=False):
    """Host exec request body"""
    args: Dict[str, Any]
    timeout_ms: int
    label: str


class _HostExecRequestRequired(TypedDict):
    req_id: str
    op: HostOp
    args: Dict[str, Any]
    timeout_ms: int
    from_device_id: str
    ts: int


class HostExecRequest(_HostExecRequestRequired, total=False):
    """The `data` of an `exec` SSE event delivered to the host."""
    label: str


class _HostExecResultBodyRequired(TypedDict):
    ok: bool


class HostExecResultBody(_HostExecResultBodyRequired, total=False):
    """Host exec result body"""
    result: Any
    error: str


class HostExecResponse(TypedDict):
    """Host exec response"""
    req_id: str
    ok: bool
    result: Any
    error: Optional[str]


# Role inside an org.
OrgRole = Literal['owner', 'admin', 'member']


# Role granted on a session.
OrgSessionRole = Literal['viewer', 'editor', 'owner']


# Who a share is for.
OrgSharePrincipalType = Literal['user', 'org', 'link']


class OrgSessionShare(TypedDict):
    """Session share"""
    id: str
    session_id: str
    principal_type: OrgSharePrincipalType
    principal_id: Optional[str]
    role: OrgSessionRole
    has_token: bool
    expires_at: Optional[str]
    created_by_user_id: str
    created_at: str


class _OrgCreateShareBodyRequired(TypedDict):
    principal_type: OrgSharePrincipalType


class OrgCreateShareBody(_OrgCreateShareBodyRequired, total=False):
    """Create share body"""
    principal_id: str
    role: OrgSessionRole
    expires_at: str


class OrgSharedSession(TypedDict):
    """A session object (same wire shape as `GET /v1/sessions/{id}`) plus your effective role and the share that gran…"""
    id: str
    session_key: str
    owner_user_id: str
    title: Optional[str]
    created_at: str
    last_event_at: str
    last_seq: int
    executor_device_id: Optional[str]
    lease_expires_at: Optional[str]
    e2e: bool
    archived: bool
    role: OrgSessionRole
    share_id: str


class OrgWithRole(TypedDict):
    """The stored org row (camelCase, as persisted) plus the caller's role."""
    id: str
    name: str
    ownerUserId: str
    createdAt: str
    role: OrgRole


class OrgMember(TypedDict):
    """Org member"""
    user_id: str
    role: OrgRole
    created_at: str
    email: Optional[str]


class OrgAddMemberBody(TypedDict, total=False):
    """Exactly one of `user_id` or `email` is required."""
    user_id: str
    email: str
    role: OrgRole


# How a project's environments are shared. `shared_vm` (default) — one machine, many members; `container` — one …
ProjectIsolation = Literal['shared_vm', 'container', 'vm_per_dev']


# `byo` (bring your own machine; the daemon enrols with a token) is open to every key. `openstack` / `hetzner` a…
EnvironmentProvider = Literal['byo', 'openstack', 'hetzner', 'local', 'gce']


# Lifecycle state. `byo` starts in `pending` and reaches `enrolling` when the daemon enrols; managed providers s…
EnvironmentState = Literal['pending', 'creating', 'enrolling', 'starting', 'running', 'stopping', 'stopped', 'archiving', 'archived', 'destroying', 'destroyed', 'error']


# Role of a member on an environment; `owner` ≥ `maintainer` ≥ `developer` ≥ `viewer`.
EnvironmentRole = Literal['owner', 'maintainer', 'developer', 'viewer']


# Who may reach a published port through the preview router. `public` needs `maintainer` to set.
PortVisibility = Literal['owner', 'org', 'authenticated', 'public']


PortProtocol = Literal['http', 'https', 'tcp']


class _ProjectRequired(TypedDict):
    id: str
    ownerUserId: str
    orgId: Optional[str]
    name: str
    slug: str
    repoUrl: Optional[str]
    defaultBranch: str
    devcontainerPath: Optional[str]
    isolation: ProjectIsolation
    settings: Dict[str, Any]
    createdAt: str
    updatedAt: str


class Project(_ProjectRequired, total=False):
    """The stored project row (camelCase, as persisted)."""
    prebuildPoolSize: int
    prebuildProvider: Literal['openstack', 'hetzner']
    prebuildSize: str


class _ProjectCreateBodyRequired(TypedDict):
    name: str


class ProjectCreateBody(_ProjectCreateBodyRequired, total=False):
    """Create project body"""
    slug: str
    repo_url: Optional[str]
    default_branch: str
    devcontainer_path: Optional[str]
    isolation: ProjectIsolation
    org_id: Optional[str]


class ProjectPatchBody(TypedDict, total=False):
    """At least one field is required."""
    name: str
    repo_url: Optional[str]
    default_branch: str
    devcontainer_path: Optional[str]
    isolation: ProjectIsolation
    prebuild_pool_size: int
    prebuild_provider: Literal['openstack', 'hetzner']
    prebuild_size: Literal['small', 'medium', 'large']


class _EnvironmentRequired(TypedDict):
    id: str
    projectId: str
    ownerUserId: str
    orgId: Optional[str]
    forUserId: Optional[str]
    for_user_id: Optional[str]
    name: str
    slug: str
    provider: EnvironmentProvider
    region: Optional[str]
    size: Optional[str]
    state: EnvironmentState
    stateReason: Optional[str]
    deviceId: Optional[str]
    providerRef: Optional[str]
    publicIp: Optional[str]
    idleTimeoutMinutes: int
    lastActivityAt: Optional[str]
    startedAt: Optional[str]
    stoppedAt: Optional[str]
    hourlyRateMicroEur: Optional[int]
    includedHoursUsedSeconds: int
    metadata: Dict[str, Any]
    createdAt: str
    updatedAt: str


class Environment(_EnvironmentRequired, total=False):
    """The stored environment row (camelCase, as persisted) plus snake_case `for_user_id` and, when known, the projec…"""
    isolation: ProjectIsolation
    prebuild: bool


class _EnvironmentCreateBodyRequired(TypedDict):
    project_id: str
    provider: EnvironmentProvider


class EnvironmentCreateBody(_EnvironmentCreateBodyRequired, total=False):
    """Create environment body"""
    name: str
    slug: str
    region: str
    size: str
    idle_timeout_minutes: int
    budget_micro_eur: Optional[int]


class EnvironmentPatchBody(TypedDict, total=False):
    """Provide `name` and/or `idle_timeout_minutes`."""
    name: str
    idle_timeout_minutes: int


class AlreadyHasEnvErrorError(TypedDict):
    message: str
    type: Literal['invalid_request_error']
    code: Literal['already_has_env']


class AlreadyHasEnvError(TypedDict):
    """The `Error` envelope plus the id of your existing live environment in this `vm_per_dev` project."""
    error: AlreadyHasEnvErrorError
    environment_id: str


class InsufficientFundsErrorError(TypedDict):
    type: str
    code: str
    message: str
    quote_micro_eur: int
    balance_micro_eur: int


class InsufficientFundsError(TypedDict):
    """Shared 402 money-gate error (RC-01): every paid Studio / media action places a wallet hold of its quote first."""
    error: InsufficientFundsErrorError


class StudioQuote(TypedDict):
    object: str
    action: str
    quote_micro_usd: str
    quote_micro_eur: str
    balance_micro_eur: Optional[str]
    sufficient: bool


class InsufficientBalanceErrorError(TypedDict):
    message: str
    type: Literal['invalid_request_error']
    code: Literal['insufficient_balance']
    required_micro_eur: int
    balance_micro_eur: int


class InsufficientBalanceError(TypedDict):
    """The `Error` envelope plus the one-hour amount the wallet must hold and what it holds now."""
    error: InsufficientBalanceErrorError


# Environment transition
EnvironmentTransition = TypedDict(
    'EnvironmentTransition',
    {
        'environment': Environment,
        'from': EnvironmentState,
        'to': EnvironmentState,
    },
    total=True,
)


class EnvironmentEnrollBody(TypedDict):
    """Enrol body"""
    token: str
    device_id: str
    daemon_version: str
    os: str
    arch: str


class _EnvironmentEnrolledRequired(TypedDict):
    environment_id: str
    relay_url: str


class EnvironmentEnrolled(_EnvironmentEnrolledRequired, total=False):
    """Enrolled"""
    api_key: str


class EnvironmentEnrollToken(TypedDict):
    """Enrolment token"""
    token: str
    expires_at: str
    environment_id: str


class EnvironmentMember(TypedDict):
    """Environment member"""
    user_id: str
    role: EnvironmentRole
    email: Optional[str]
    name: Optional[str]
    linux_username: Optional[str]
    port_range_start: Optional[int]
    ssh_public_key: bool
    provisioned_at: Optional[str]
    created_at: str


class EnvironmentMemberCreated(TypedDict):
    """Environment member (created)"""
    user_id: str
    role: EnvironmentRole
    linux_username: Optional[str]
    port_range_start: Optional[int]


class EnvironmentAddMemberBody(TypedDict, total=False):
    """Exactly one of `user_id` or `email` is required."""
    user_id: str
    email: str
    role: EnvironmentRole


class EnvironmentMemberRoleBody(TypedDict):
    """Member role body"""
    role: EnvironmentRole


class EnvironmentSshKeyBody(TypedDict):
    """SSH key body"""
    public_key: str


class EnvironmentSshCertBody(TypedDict):
    """SSH certificate request body"""
    public_key: str


class EnvironmentSshCert(TypedDict):
    """SSH certificate"""
    certificate: str
    principal: str
    valid_before: str
    host: Optional[str]


class EnvironmentSshCaKeys(TypedDict):
    """SSH CA public keys"""
    public_keys: List[str]


class EnvironmentPort(TypedDict):
    """Published port"""
    id: str
    environmentId: str
    port: int
    protocol: PortProtocol
    label: Optional[str]
    visibility: PortVisibility
    openedByUserId: Optional[str]
    createdAt: str
    updatedAt: str


class _EnvironmentPortBodyRequired(TypedDict):
    visibility: PortVisibility


class EnvironmentPortBody(_EnvironmentPortBodyRequired, total=False):
    """Publish port body"""
    label: Optional[str]
    protocol: PortProtocol


class _EnvironmentTaskCreateRequired(TypedDict):
    prompt: str


class EnvironmentTaskCreate(_EnvironmentTaskCreateRequired, total=False):
    """Queue task body"""
    branch: str


class EnvironmentTaskQueued(TypedDict):
    """Queued task"""
    task_id: str
    session_id: str
    status: Literal['queued']


class EnvironmentTaskResult(TypedDict, total=False):
    """Filled when the task finishes; every field may be null."""
    diff_stat: Optional[str]
    commit_sha: Optional[str]
    branch: Optional[str]
    preview_url: Optional[str]
    error: Optional[str]


class EnvironmentTaskOutputSignature(TypedDict):
    """Agent output signature (experimental)"""
    alg: str
    context: str
    key_id: str
    sig: str
    signed_at: str


class EnvironmentTask(TypedDict):
    """Agent task"""
    id: str
    environment_id: str
    user_id: str
    session_id: Optional[str]
    prompt: str
    branch: Optional[str]
    status: Literal['queued', 'running', 'done', 'failed']
    result: EnvironmentTaskResult
    created_at: str
    started_at: Optional[str]
    finished_at: Optional[str]
    output_signature: Optional[EnvironmentTaskOutputSignature]


class _AgentOutputKeyRequired(TypedDict):
    enabled: bool
    note: str


class AgentOutputKey(_AgentOutputKeyRequired, total=False):
    """Agent output signing key (experimental)"""
    alg: str
    context: str
    key_id: str
    public_key: str


class _AgentOutputVerifyRequestSignatureRequired(TypedDict):
    sig: str


class AgentOutputVerifyRequestSignature(_AgentOutputVerifyRequestSignatureRequired, total=False):
    key_id: str


class AgentOutputVerifyRequest(TypedDict):
    """Verify agent output"""
    payload: Dict[str, Any]
    signature: AgentOutputVerifyRequestSignature


class _AgentOutputVerifyResultRequired(TypedDict):
    valid: bool
    key_id: str
    note: str


class AgentOutputVerifyResult(_AgentOutputVerifyResultRequired, total=False):
    """Agent output verification result"""
    reason: Literal['unknown_key']


class ProvenanceFinding(TypedDict):
    """Provenance finding"""
    kind: Literal['c2pa', 'riff_info', 'id3', 'mp4_ai_mark', 'xmp']
    present: bool
    ai_marked: bool
    codai: bool
    details: Dict[str, Any]


class ProvenanceCheckResult(TypedDict):
    """Provenance check result"""
    media_type: Literal['image/png', 'image/jpeg', 'image/webp', 'audio/wav', 'audio/mpeg', 'video/mp4']
    findings: List[ProvenanceFinding]
    codai_generated: bool
    synthid_checked: Literal[False]
    signature_verified: Literal[False]


class EnvironmentSecret(TypedDict):
    """Secret (name only)"""
    name: str
    created_by_user_id: Optional[str]
    created_at: str
    updated_at: str


class EnvironmentSecretBody(TypedDict):
    """Set secret body"""
    value: str


class EnvironmentSecretSet(TypedDict):
    """Secret set"""
    name: str
    updated: bool


class EnvironmentEvent(TypedDict):
    """One append-only audit row (camelCase, as stored)."""
    id: int
    environmentId: str
    actorUserId: Optional[str]
    actorKind: Literal['user', 'agent', 'system', 'daemon']
    kind: str
    payload: Dict[str, Any]
    createdAt: str


class EnvironmentDetail(TypedDict):
    """Environment detail"""
    environment: Environment
    isolation: ProjectIsolation
    role: EnvironmentRole
    members: List[EnvironmentMember]
    ports: List[EnvironmentPort]
    events: List[EnvironmentEvent]


class _RelayListeningPortRequired(TypedDict):
    port: int


class RelayListeningPort(_RelayListeningPortRequired, total=False):
    """A port the daemon observed listening inside the environment (not necessarily published)."""
    pid: int
    process: str


class RelayGitState(TypedDict):
    """Git state (relay)"""
    branch: str
    dirty: bool
    ahead: int
    behind: int
    worktrees: List[str]


class _RelayLockRequired(TypedDict):
    name: str
    holder: str


class RelayLock(_RelayLockRequired, total=False):
    """A lock the daemon reports in its heartbeat (build lock, commit mutex, …)."""
    since: Optional[str]


class RelayAttachedClient(TypedDict):
    """A device or agent socket attached to the environment, on any relay instance."""
    client_id: str
    user_id: str
    role: EnvironmentRole
    kind: Literal['device', 'agent']
    device_id: Optional[str]
    name: Optional[str]
    platform: Optional[str]
    attached_at: str


class RelayEnvironmentStatusDaemonOption1(TypedDict):
    daemon_version: str
    os: str
    arch: str
    capabilities: List[str]


class RelayEnvironmentStatus(TypedDict):
    """What the relay knows about the daemon of an environment. Detail fields are `null`/empty unless the daemon's so…"""
    environment_id: str
    online: bool
    instance: Optional[str]
    last_heartbeat: Optional[int]
    activity: Optional[Literal['idle', 'human', 'agent']]
    ports: List[RelayListeningPort]
    git_state: Optional[RelayGitState]
    daemon: Optional[RelayEnvironmentStatusDaemonOption1]
    streams: int
    attached: List[RelayAttachedClient]
    locks: List[RelayLock]
    clients: int


class AccountDeleteRequest(TypedDict):
    """Typed confirmation of the account e-mail."""
    confirm_email: str


class AccountDeleteResponse(TypedDict):
    """Scheduled account deletion"""
    ok: bool
    scheduled_for: str
    grace_days: int
    cancel_url: str


class AccountConsent(TypedDict):
    """Accepted terms/privacy versions for one client surface."""
    surface: Literal['desktop', 'phone', 'console', 'ios']
    terms_version: str
    privacy_version: str
    accepted_at: str


class AccountWalletHistoryEntry(TypedDict):
    """One line of the EUR wallet ledger (last 180 days, newest first, max 20)."""
    id: str
    delta_eur: float
    source: Literal['welcome_grant', 'referral_referee_grant', 'referral_referrer_grant', 'promo_grant', 'admin_grant', 'admin_revoke', 'purchase', 'usage_charge', 'expiry', 'auto_topup', 'task_refund', 'task_success_charge', 'credit_migration', 'compute_charge', 'sandbox_charge']
    expires_at: Optional[str]
    promo: Optional[str]
    multiplier: Optional[float]
    list_eur: Optional[float]
    note: Optional[str]
    created_at: str


class AccountWallet(TypedDict):
    """Spendable EUR balance, promo-grant headroom and recent ledger history."""
    balance_eur: float
    next_expiry_at: Optional[str]
    promo_granted_eur: float
    promo_cap_eur: float
    history: List[AccountWalletHistoryEntry]


class AccountPromo(TypedDict):
    """The best (lowest multiplier) promotion applicable to the user right now."""
    slug: str
    title: str
    banner_en: Optional[str]
    banner_ro: Optional[str]
    multiplier: float
    ends_at: str


class AccountReferral(TypedDict):
    """Referral programme status for the caller as a referrer."""
    username: Optional[str]
    consented: bool
    share_url: Optional[str]
    invited: int
    rewarded: int
    pending: int
    flagged: int
    earned_eur: float
    month_remaining: int
    lifetime_remaining: int
    reward_eur: float
    referee_reward_eur: float
    qualify_spend_eur: float


class AccountGrowth(TypedDict):
    """Wallet, promotion and referral data shared by GET and PATCH responses. Each block is `null` when its lookup fa…"""
    wallet: Optional[AccountWallet]
    promo: Optional[AccountPromo]
    referral: Optional[AccountReferral]


class AccountViewUser(TypedDict):
    id: str
    email: str
    name: Optional[str]
    username: Optional[str]
    suggested_username: Optional[str]


class AccountViewKey(TypedDict):
    id: str
    app_id: Optional[str]


class AccountViewPlan(TypedDict):
    tier: Optional[str]
    status: str
    current_period_end: Optional[str]
    cancel_at_period_end: bool
    has_billing_account: bool
    max_routing_tier: Optional[Literal['small', 'medium', 'large', 'frontier']]


class AccountViewUsage(TypedDict):
    tasks_today: int
    tasks_per_day: Optional[int]
    tasks_month: int
    tasks_per_month: Optional[int]
    budget_eur_per_day: Optional[float]
    budget_eur_per_month: Optional[float]
    credits: float


class AccountViewFeatures(TypedDict):
    byok: bool
    subagents: bool
    persistent_memory: bool
    limits_exempt: bool


class AccountView(TypedDict):
    """Full account card returned by `GET /v1/account`."""
    wallet: Optional[AccountWallet]
    promo: Optional[AccountPromo]
    referral: Optional[AccountReferral]
    user_id: str
    email: str
    training_opt_out: bool
    consents: List[AccountConsent]
    user: AccountViewUser
    key: AccountViewKey
    plan: AccountViewPlan
    usage: AccountViewUsage
    referral_redeem_until: Optional[str]
    features: AccountViewFeatures
    billing_url: Literal['https://codai.ro/api/mobile/billing']


class AccountPatchRequest(TypedDict, total=False):
    """Strict object — unknown keys are rejected and at least one field must be present."""
    training_opt_out: bool
    consents: AccountConsent
    username: str
    referral_consent: bool
    referral_code: str


class AccountPatchResponse(TypedDict):
    """Returned by `PATCH /v1/account`."""
    wallet: Optional[AccountWallet]
    promo: Optional[AccountPromo]
    referral: Optional[AccountReferral]
    user_id: str
    email: str
    training_opt_out: bool
    consents: List[AccountConsent]
    username_error: Optional[Literal['invalid', 'taken', 'change_limit']]
    referral_result: Optional[Literal['window_closed', 'none', 'invalid_code', 'self', 'already_referred', 'flagged', 'pending_payment', 'granted', 'cap_reached']]


class BillingSubscription(TypedDict):
    """The subscription behind the current plan (no Stripe ids)."""
    status: str
    current_period_end: Optional[str]
    cancel_at_period_end: bool
    monthly_eur: Optional[float]


class BillingPlan(TypedDict):
    """Current plan, task allowance and subscription."""
    tier_slug: str
    tier_label: str
    tasks_per_month: Optional[int]
    tasks_used_this_month: int
    has_active_subscription: bool
    supports_byok: bool
    subscription: Optional[BillingSubscription]


class BillingWalletEntry(TypedDict):
    """One line of the EUR wallet ledger, newest first."""
    id: str
    source: str
    delta_eur: float
    note: Optional[str]
    promo: Optional[str]
    expires_at: Optional[str]
    created_at: str


class BillingWallet(TypedDict):
    """Spendable EUR balance, next expiry, promo grants and recent ledger history."""
    balance_eur: float
    next_expiry_at: Optional[str]
    promo_granted_eur: float
    history: List[BillingWalletEntry]


class BillingAutoTopup(TypedDict):
    """Automatic wallet top-up settings and this month's activity (change them on hub.codai.ro)."""
    enabled: bool
    threshold_eur: float
    amount_eur: float
    monthly_cap_eur: float
    month_spent_eur: float
    last_topup_at: Optional[str]
    failures: int


class BillingPaymentMethod(TypedDict):
    """A saved card, without any Stripe id."""
    brand: Optional[str]
    last4: Optional[str]
    exp_month: Optional[int]
    exp_year: Optional[int]
    is_default: bool
    expired: bool


class BillingLinks(TypedDict):
    """Browser links for every billing action; the API itself never starts a payment."""
    billing: str
    portal: str
    topup: Dict[str, str]
    checkout_plan: Dict[str, str]


class Billing(TypedDict):
    """Read-only billing overview returned by `GET /v1/billing`."""
    plan: BillingPlan
    wallet: BillingWallet
    auto_topup: BillingAutoTopup
    compute_reserve_eur: float
    payment_methods: List[BillingPaymentMethod]
    links: BillingLinks


class BillingInvoice(TypedDict):
    """One invoice or credit note issued through brivio."""
    id: str
    kind: Literal['invoice', 'credit_note']
    number: str
    issued_at: str
    total_eur: float
    currency: str
    efactura_status: Optional[str]
    pdf_url: str


class BillingInvoiceList(TypedDict):
    """Fiscal documents, newest first."""
    invoices: List[BillingInvoice]


class ReferralRow(TypedDict):
    """One invitee as the hub referrals page shows it; never their email, name or user id."""
    id: str
    referee: str
    status: Literal['pending', 'qualified', 'rewarded', 'flagged', 'rejected']
    created_at: str
    rewarded_at: Optional[str]
    reward_eur: Optional[float]


class ReferralsView(TypedDict):
    """Referral stats, redeem deadline and invitees returned by `GET /v1/referrals`."""
    referral: Optional[AccountReferral]
    redeem_until: Optional[str]
    referrals: List[ReferralRow]


class AccountReceiptByUpstreamItem(TypedDict):
    upstream_model: str
    events: int
    cost_micro_usd: int


AccountReceiptWindow = TypedDict(
    'AccountReceiptWindow',
    {
        'from': Optional[str],
        'to': str,
        'session_id': Optional[str],
    },
    total=True,
)


class AccountReceipt(TypedDict):
    """Aggregated usage for the caller. Micro-USD fields are integers; only `cost_usd` is converted."""
    events: int
    tasks: int
    cost_micro_usd_total: int
    cost_usd: float
    prompt_tokens: int
    completion_tokens: int
    cached_read_tokens: int
    cache_write_tokens: int
    by_upstream: List[AccountReceiptByUpstreamItem]
    window: AccountReceiptWindow


# A rating plus one target. Zod rejects the body when none of the three targets is present.
AccountFeedbackRequest = Any


class _AccountPhoneModelRequired(TypedDict):
    id: str
    name: str
    file: str
    sizeBytes: int
    url: str
    expiresAt: str


class AccountPhoneModel(_AccountPhoneModelRequired, total=False):
    """One catalog entry with a short-lived signed download URL. Extra publisher keys pass through unchanged."""
    sha256: str
    backends: List[str]
    base: str
    notes: str


# How deliveries are authenticated and normalized (see `POST /v1/hooks/{id}`).
TriggerSource = Literal['github', 'sentry', 'gcp', 'generic', 'form', 'manual']


TriggerSeverity = Literal['info', 'low', 'medium', 'high', 'critical']


TriggerResolvedMode = Literal['notify', 'assisted', 'autopilot']


class TriggerPolicySmart(TypedDict):
    """Thresholds used by `smart` mode. Keywords win over severity."""
    assistedAt: TriggerSeverity
    autopilotAt: TriggerSeverity
    keywords: Dict[str, TriggerResolvedMode]


# Inside quiet hours autopilot degrades to assisted and assisted to notify.
TriggerPolicyQuietHours = TypedDict(
    'TriggerPolicyQuietHours',
    {
        'from': str,
        'to': str,
        'tz': str,
    },
    total=True,
)


class TriggerPolicyTarget(TypedDict):
    kind: Literal['any', 'device', 'environment']
    id: Optional[str]


class TriggerPolicy(TypedDict):
    """The trigger policy with every default filled in (as returned by the API)."""
    mode: Literal['notify', 'assisted', 'autopilot', 'smart']
    smart: TriggerPolicySmart
    subjects: List[str]
    minSeverity: TriggerSeverity
    permissions: Literal['read', 'edit', 'pr']
    quietHours: Optional[TriggerPolicyQuietHours]
    budgetMicroUsdPerEvent: int
    budgetMicroUsdPerDay: int
    maxSessionsPerHour: int
    dedupeWindowMin: int
    promptTemplate: str
    skill: Optional[str]
    target: TriggerPolicyTarget
    ttlMin: int


class Trigger(TypedDict):
    id: str
    name: str
    source: TriggerSource
    enabled: bool
    policy: TriggerPolicy
    hook_url: str
    last_event_at: Optional[str]
    created_at: str


class TriggerWithSecret(TypedDict):
    id: str
    name: str
    source: TriggerSource
    enabled: bool
    policy: TriggerPolicy
    hook_url: str
    last_event_at: Optional[str]
    created_at: str
    secret: str


class _TriggerCreateRequired(TypedDict):
    name: str
    source: TriggerSource


class TriggerCreate(_TriggerCreateRequired, total=False):
    policy: Dict[str, Any]
    enabled: bool


class TriggerPatch(TypedDict, total=False):
    name: str
    policy: Dict[str, Any]
    enabled: bool


class TriggerTestFire(TypedDict, total=False):
    title: str
    message: str
    severity: TriggerSeverity
    url: str
    subject: str


class _TriggerEventCardRequired(TypedDict):
    source: TriggerSource
    kind: str
    title: str
    summary: str
    severity: TriggerSeverity
    dedupeKey: str
    labels: List[str]
    resolved: bool


class TriggerEventCard(_TriggerEventCardRequired, total=False):
    """A delivery normalized into one source-independent shape."""
    url: str
    subject: str


class _TriggerDecisionRequired(TypedDict):
    action: Literal['ignore', 'append', 'close', 'notify', 'start']
    reason: str


class TriggerDecision(_TriggerDecisionRequired, total=False):
    """What the policy decided for one event and why (`reason` is shown on the session)."""
    mode: TriggerResolvedMode
    wanted: TriggerResolvedMode
    sessionId: str


class TriggerEvent(TypedDict):
    id: int
    deliveryId: str
    status: Literal['received', 'processed', 'failed', 'ignored']
    card: TriggerEventCard
    decision: Optional[TriggerDecision]
    sessionId: Optional[str]
    attempts: int
    error: Optional[str]
    receivedAt: str
    processedAt: Optional[str]


class Notification(TypedDict):
    id: int
    userId: str
    kind: str
    severity: TriggerSeverity
    title: str
    body: str
    url: Optional[str]
    sessionId: Optional[str]
    triggerEventId: Optional[int]
    readAt: Optional[str]
    createdAt: str


PromptStatus = Literal['open', 'launched', 'sent', 'answered', 'verified', 'done', 'dismissed', 'superseded']


PromptSource = Literal['vscode', 'cli', 'desktop', 'phone', 'agent', 'hub', 'manual', 'transcript']


class PromptReport(TypedDict):
    """LLM verification report of a prompt."""
    verdict: Literal['done', 'partial', 'not_started']
    summary: str
    changed: List[str]
    remaining: List[str]
    evidence: Literal['transcript+diff', 'transcript', 'diff']
    model: str
    at: str


class _PromptRecurrenceOption1Required(TypedDict):
    every: Literal['day', 'week', 'month']


class PromptRecurrenceOption1(_PromptRecurrenceOption1Required, total=False):
    at: str


class PromptRecurrenceOption2(TypedDict):
    on: Literal['session_end']


# `{ every: day | week | month, at?: HH:MM }` (UTC): once the prompt left `open`, its next occurrence is created
PromptRecurrence = Union[PromptRecurrenceOption1, PromptRecurrenceOption2]


class PromptLaunchConfig(TypedDict, total=False):
    """Preset used when the prompt is launched."""
    agent: str
    model: str
    folder: str


class Prompt(TypedDict):
    """A pending prompt. Timestamps are ISO strings or `null`."""
    id: str
    title: str
    prompt: str
    status: PromptStatus
    source: PromptSource
    repo: Optional[str]
    tracker: Optional[str]
    goal_key: Optional[str]
    not_before: Optional[str]
    auto_run: bool
    target_device_id: Optional[str]
    origin: Dict[str, Any]
    notified_at: Optional[str]
    launched_at: Optional[str]
    run_session_id: Optional[str]
    done_at: Optional[str]
    sent_at: Optional[str]
    answered_at: Optional[str]
    verified_at: Optional[str]
    match_ref: Optional[str]
    match_turn_id: Optional[str]
    match_score: Optional[float]
    base_sha: Optional[str]
    head_sha: Optional[str]
    report: Optional[PromptReport]
    report_at: Optional[str]
    created_at: str
    updated_at: str
    tags: List[str]
    priority: int
    recurrence: Optional[PromptRecurrence]
    next_prompt_id: Optional[str]
    launch: Optional[PromptLaunchConfig]
    is_template: bool


class PromptCreated(TypedDict):
    id: str
    title: str
    prompt: str
    status: PromptStatus
    source: PromptSource
    repo: Optional[str]
    tracker: Optional[str]
    goal_key: Optional[str]
    not_before: Optional[str]
    auto_run: bool
    target_device_id: Optional[str]
    origin: Dict[str, Any]
    notified_at: Optional[str]
    launched_at: Optional[str]
    run_session_id: Optional[str]
    done_at: Optional[str]
    sent_at: Optional[str]
    answered_at: Optional[str]
    verified_at: Optional[str]
    match_ref: Optional[str]
    match_turn_id: Optional[str]
    match_score: Optional[float]
    base_sha: Optional[str]
    head_sha: Optional[str]
    report: Optional[PromptReport]
    report_at: Optional[str]
    created_at: str
    updated_at: str
    tags: List[str]
    priority: int
    recurrence: Optional[PromptRecurrence]
    next_prompt_id: Optional[str]
    launch: Optional[PromptLaunchConfig]
    is_template: bool
    created: bool
    superseded: int


class _PromptCreateRequired(TypedDict):
    prompt: str


class PromptCreate(_PromptCreateRequired, total=False):
    title: str
    source: PromptSource
    repo: str
    tracker: str
    goal_key: str
    not_before: Optional[str]
    auto_run: bool
    target_device_id: Optional[str]
    origin: Dict[str, Any]
    tags: List[str]
    priority: int
    recurrence: Optional[PromptRecurrence]
    next_prompt_id: Optional[str]
    launch: Optional[PromptLaunchConfig]
    is_template: bool


class PromptPatch(TypedDict, total=False):
    title: str
    prompt: str
    status: PromptStatus
    not_before: Optional[str]
    auto_run: bool
    target_device_id: Optional[str]
    tracker: Optional[str]
    tags: List[str]
    priority: int
    recurrence: Optional[PromptRecurrence]
    next_prompt_id: Optional[str]
    launch: Optional[PromptLaunchConfig]
    is_template: bool


class PromptEvent(TypedDict):
    """One history entry of a prompt."""
    kind: Literal['created', 'edited', 'status', 'launched', 'recurred', 'chained', 'verified']
    detail: Dict[str, Any]
    created_at: str


class _PromptBulkRequestRequired(TypedDict):
    ids: List[str]
    action: Literal['done', 'dismiss', 'delete', 'snooze', 'tag', 'untag', 'priority']


class PromptBulkRequest(_PromptBulkRequestRequired, total=False):
    not_before: str
    tags: List[str]
    priority: int


# Lifecycle: `recording` → `uploading` → `queued` → `transcribing` → `analyzing` → `ready`, or `failed`.
TranscriptStatus = Literal['recording', 'uploading', 'queued', 'transcribing', 'analyzing', 'ready', 'failed']


# Shapes the insights; `auto` lets the model choose.
TranscriptTemplate = Literal['auto', 'meeting', 'brainstorm', 'journal', 'interview', 'lecture']


# `mic` = your microphone; `system` = loopback (the other participants); `mixed` = both in one track.
TranscriptTrackKind = Literal['mic', 'system', 'mixed']


class Transcript(TypedDict):
    id: str
    client_id: str
    title: str
    status: TranscriptStatus
    source: Literal['desktop', 'phone', 'wear', 'web', 'vscode', 'tv', 'api']
    template: TranscriptTemplate
    language_hint: str
    language: Optional[str]
    folder_id: Optional[str]
    pinned: bool
    tags: List[str]
    feed_memory: bool
    started_at: str
    duration_ms: int
    error: Optional[str]
    audio_available: bool
    ready_at: Optional[str]
    created_at: str
    updated_at: str


class TranscriptDetailProcessingOption1(TypedDict):
    kind: Literal['transcribe', 'analyze']
    attempts: int
    max_attempts: int
    last_error: Optional[str]
    next_attempt_at: Optional[str]


class TranscriptDetailTracksItem(TypedDict):
    kind: TranscriptTrackKind
    bytes: int


class Speaker(TypedDict):
    label: str
    name: Optional[str]
    is_owner: bool
    talk_ms: int


class _UtteranceWordsItemRequired(TypedDict):
    w: str
    s: int
    e: int


class UtteranceWordsItem(_UtteranceWordsItemRequired, total=False):
    c: float


class Utterance(TypedDict):
    seq: int
    speaker: str
    start_ms: int
    end_ms: int
    text: str
    language: Optional[str]
    words: List[UtteranceWordsItem]
    edited: bool


class Bookmark(TypedDict):
    id: str
    at_ms: int
    label: Optional[str]


class TranscriptCitation(TypedDict):
    """A span of the recording, [startMs, endMs) in milliseconds."""
    startMs: int
    endMs: int


class _TranscriptCitedTextRequired(TypedDict):
    text: str


class TranscriptCitedText(_TranscriptCitedTextRequired, total=False):
    cite: TranscriptCitation


class _TranscriptInsightsActionsItemRequired(TypedDict):
    text: str


class TranscriptInsightsActionsItem(_TranscriptInsightsActionsItemRequired, total=False):
    owner: str
    due: str
    cite: TranscriptCitation


class _TranscriptInsightsPromptsItemRequired(TypedDict):
    title: str
    prompt: str


class TranscriptInsightsPromptsItem(_TranscriptInsightsPromptsItemRequired, total=False):
    repo: str
    cite: TranscriptCitation


class _TranscriptInsightsRequired(TypedDict):
    version: int
    model: str
    created_at: str
    accepted_prompts: Dict[str, str]
    title: str
    summary: str
    template: TranscriptTemplate
    language: str
    keyPoints: List[TranscriptCitedText]
    actions: List[TranscriptInsightsActionsItem]
    decisions: List[TranscriptCitedText]
    openQuestions: List[TranscriptCitedText]
    tags: List[str]
    prompts: List[TranscriptInsightsPromptsItem]


class TranscriptInsights(_TranscriptInsightsRequired, total=False):
    """Latest analysis version. Envelope keys are snake_case; the analysis body keys are camelCase as stored."""
    project: str


class TranscriptDetail(TypedDict):
    id: str
    client_id: str
    title: str
    status: TranscriptStatus
    source: Literal['desktop', 'phone', 'wear', 'web', 'vscode', 'tv', 'api']
    template: TranscriptTemplate
    language_hint: str
    language: Optional[str]
    folder_id: Optional[str]
    pinned: bool
    tags: List[str]
    feed_memory: bool
    started_at: str
    duration_ms: int
    error: Optional[str]
    audio_available: bool
    ready_at: Optional[str]
    created_at: str
    updated_at: str
    live_preview: Optional[str]
    processing: Optional[TranscriptDetailProcessingOption1]
    tracks: List[TranscriptDetailTracksItem]
    speakers: List[Speaker]
    utterances: List[Utterance]
    bookmarks: List[Bookmark]
    insights: Optional[TranscriptInsights]


class _TranscriptCreateRequired(TypedDict):
    source: Literal['desktop', 'phone', 'wear', 'web', 'vscode', 'tv', 'api']
    client_id: str
    started_at: str


class TranscriptCreate(_TranscriptCreateRequired, total=False):
    title: str
    template: TranscriptTemplate
    language_hint: str
    tracks: List[TranscriptTrackKind]
    folder_id: Optional[str]
    feed_memory: bool


class TranscriptPatch(TypedDict, total=False):
    title: str
    folder_id: Optional[str]
    pinned: bool
    tags: List[str]
    template: TranscriptTemplate
    feed_memory: bool


class TranscriptFinalizeUploadsItem(TypedDict):
    track: TranscriptTrackKind
    upload_id: str


class _TranscriptFinalizeBookmarksItemRequired(TypedDict):
    at_ms: int


class TranscriptFinalizeBookmarksItem(_TranscriptFinalizeBookmarksItemRequired, total=False):
    label: str


class _TranscriptFinalizeRequired(TypedDict):
    duration_ms: int
    uploads: List[TranscriptFinalizeUploadsItem]


class TranscriptFinalize(_TranscriptFinalizeRequired, total=False):
    bookmarks: List[TranscriptFinalizeBookmarksItem]
    live_preview: str


class TranscriptFolder(TypedDict):
    id: str
    name: str
    color: Optional[str]
    position: int


class _TranscriptFolderInputRequired(TypedDict):
    name: str


class TranscriptFolderInput(_TranscriptFolderInputRequired, total=False):
    color: str


class TranscriptsSettings(TypedDict):
    waveform: Literal['ring', 'bars', 'blob', 'dot', 'off']
    haptics: bool
    liveText: bool
    target: Literal['auto', 'phone', 'watch']
    language: Optional[str]


class UserSettings(TypedDict):
    transcripts: TranscriptsSettings


class SettingsResponse(TypedDict):
    settings: UserSettings
    version: int
    updatedAt: Optional[str]


class _SettingsPatchRequestRequired(TypedDict):
    settings: Dict[str, Any]


class SettingsPatchRequest(_SettingsPatchRequestRequired, total=False):
    version: int


class _SettingsConflictErrorRequired(TypedDict):
    message: str
    type: Literal['invalid_request_error', 'subscription_required', 'rate_limit_error', 'upstream_error', 'server_error']
    code: Literal['bad_request', 'invalid_api_key', 'subscription_inactive', 'forbidden', 'not_found', 'payload_too_large', 'rate_limit_exceeded', 'quota_exceeded', 'upstream_error', 'internal_error', 'not_a_member', 'lease_held', 'seq_conflict', 'host_offline', 'host_timeout', 'rules_refused', 'search_unavailable', 'task_not_confirmable', 'slug_taken', 'project_has_environments', 'already_has_env', 'not_enrollable', 'not_byo', 'invalid_transition', 'already_member', 'vm_per_dev_single_member', 'last_owner', 'insufficient_balance', 'key_scope_forbidden', 'assets_unavailable', 'asset_not_found', 'too_many_renders', 'renders_unavailable', 'timeline_too_long', 'not_a_timeline', 'invalid_cursor', 'templates_unavailable', 'url_blocked', 'invalid_tokens', 'unsupported_media', 'kind_mismatch', 'node_not_found', 'invalid_pick', 'duplicate_key', 'unknown_var', 'invalid_var_value', 'unsupported_kind', 'too_long', 'stale', 'not_supported_for_kind', 'unsupported_format', 'too_large', 'not_implemented', 'version_conflict', 'settings_unavailable', 'ai_label_required', 'sandbox_concurrency_limit', 'sandbox_busy', 'sandbox_daily_limit', 'invalid_ttl', 'workspace_too_large', 'sandbox_paused_limit', 'sandbox_capacity']


class SettingsConflictError(_SettingsConflictErrorRequired, total=False):
    details: Dict[str, Any]


class SettingsConflict(TypedDict):
    error: SettingsConflictError
    current: SettingsResponse


class PolicyResponseOsGate(TypedDict):
    allow_override: bool


class PolicyResponse(TypedDict):
    os_gate: PolicyResponseOsGate


class OsGateEvent(TypedDict):
    action: Literal['granted', 'revoked']
    checks: List[Literal['win.uac_off', 'win.uac_no_prompt', 'win.elevated', 'win.defender_rtp_off', 'mac.sip_off', 'mac.gatekeeper_off', 'mac.filevault_off', 'linux.root', 'linux.root_container', 'linux.sudo_nopasswd', 'linux.no_screen_lock', 'android.no_secure_lock', 'android.lock_unknown', 'android.adb_enabled', 'android.rooted', 'wear.no_secure_lock']]
    surface: Literal['desktop', 'headless', 'codaid', 'phone', 'mobile_agent', 'wear', 'vscode']
    app_version: str
    at: str


class OsGateEventAccepted(TypedDict):
    ok: bool


class TranscriptVocabulary(TypedDict):
    terms: List[str]


class TranscriptPromptAccepted(TypedDict):
    prompt_id: str
    created: bool


class TranscriptShareCreateRequest(TypedDict, total=False):
    expiresInDays: int


class TranscriptShareCreated(TypedDict):
    id: str
    token: str
    url: str
    expiresAt: Optional[str]


class TranscriptShare(TypedDict):
    id: str
    url: None
    createdAt: str
    expiresAt: Optional[str]


class PublicTranscriptCite(TypedDict):
    startMs: int
    endMs: int


class PublicTranscriptSpeakersItem(TypedDict):
    label: str
    name: Optional[str]


class PublicTranscriptUtterancesItem(TypedDict):
    speaker: str
    startMs: int
    endMs: int
    text: str


class _PublicTranscriptInsightsOption2KeyPointsItemRequired(TypedDict):
    text: str


class PublicTranscriptInsightsOption2KeyPointsItem(_PublicTranscriptInsightsOption2KeyPointsItemRequired, total=False):
    cite: PublicTranscriptCite


class _PublicTranscriptInsightsOption2ActionsItemRequired(TypedDict):
    text: str


class PublicTranscriptInsightsOption2ActionsItem(_PublicTranscriptInsightsOption2ActionsItemRequired, total=False):
    owner: str
    due: str
    cite: PublicTranscriptCite


class PublicTranscriptInsightsOption2(TypedDict):
    summary: str
    keyPoints: List[PublicTranscriptInsightsOption2KeyPointsItem]
    actions: List[PublicTranscriptInsightsOption2ActionsItem]


class PublicTranscript(TypedDict):
    title: str
    createdAt: str
    durationMs: int
    speakers: List[PublicTranscriptSpeakersItem]
    utterances: List[PublicTranscriptUtterancesItem]
    insights: Optional[PublicTranscriptInsightsOption2]


class UsageRow(TypedDict):
    """One group of usage. Token counts and `tasks` are sums over the window."""
    key: Optional[str]
    requests: int
    errors: int
    tasks: int
    prompt_tokens: int
    completion_tokens: int
    cached_read_tokens: int
    cost_micro_usd: str


# Usage of the calling account for one window, grouped by one dimension.
UsageReport = TypedDict(
    'UsageReport',
    {
        'from': str,
        'to': str,
        'group_by': Literal['day', 'key', 'device', 'app', 'platform', 'model', 'client', 'tag'],
        'data': List[UsageRow],
    },
    total=True,
)


class ApiKeyInfo(TypedDict):
    """One of your API keys. Timestamps are ISO strings or `null`; the secret is never returned."""
    id: str
    label: Optional[str]
    prefix: str
    enabled: bool
    kind: Optional[Literal['device', 'user', 'app', 'service']]
    app: Optional[str]
    device_id: Optional[str]
    platform: Optional[str]
    client_version: Optional[str]
    tags: List[str]
    created_at: Optional[str]
    last_used_at: Optional[str]
    expires_at: Optional[str]
    idle_expiry_days: Optional[int]
    revoked_at: Optional[str]
    current: bool


class EnvironmentExecRequest(TypedDict, total=False):
    op: Literal['shell', 'fs_read', 'fs_write', 'fs_list', 'fs_roots', 'info', 'job_start', 'job_status', 'job_output', 'job_send', 'job_wait', 'job_kill', 'job_list']
    command: str
    args: Dict[str, Any]
    timeout_ms: int


class _EnvironmentExecResultRequired(TypedDict):
    ok: bool


class EnvironmentExecResult(_EnvironmentExecResultRequired, total=False):
    exit_code: Optional[int]
    stdout: str
    stderr: str
    timed_out: bool
    truncated: bool
    duration_ms: Optional[int]
    result: Any
    error: Optional[str]


class EnvironmentFileListEntriesItem(TypedDict):
    name: str
    kind: str
    size: int


class EnvironmentFileList(TypedDict):
    path: str
    entries: List[EnvironmentFileListEntriesItem]
    truncated: bool


class EnvironmentFile(TypedDict):
    path: str
    content: str
    size: int
    truncated: bool


class EnvironmentFileWritten(TypedDict):
    path: str
    bytes: int
    created: bool


class _EnvironmentJobStartRequestRequired(TypedDict):
    command: str


class EnvironmentJobStartRequest(_EnvironmentJobStartRequestRequired, total=False):
    cwd: str
    expected_s: int
    session: str


class _EnvironmentJobStartedRequired(TypedDict):
    job_id: int


class EnvironmentJobStarted(_EnvironmentJobStartedRequired, total=False):
    label: str


class EnvironmentJob(TypedDict):
    job: Optional[Dict[str, Any]]
    output: Dict[str, Any]


class SandboxCreate(TypedDict, total=False):
    """Create sandbox request"""
    backend: Literal['v1', 'v2']
    template: Literal['codai-base', 'brivio-acte', 'desktop']
    ttl_seconds: int
    egress: SandboxEgress
    metadata: Dict[str, str]


class SandboxUsage(TypedDict):
    exec_count: int
    exec_seconds: float


class _SandboxRequired(TypedDict):
    id: str
    object: Literal['sandbox']
    status: Literal['running', 'paused', 'stopped', 'expired', 'destroyed']
    backend: Literal['v1', 'v2']
    template: str
    egress: SandboxEgress
    created_at: str
    expires_at: str
    last_exec_at: Optional[str]
    metadata: Dict[str, str]
    usage: SandboxUsage


class Sandbox(_SandboxRequired, total=False):
    """Sandbox"""
    restored: bool


class _SandboxListRequired(TypedDict):
    data: List[Sandbox]


class SandboxList(_SandboxListRequired, total=False):
    """Sandbox list"""
    object: Literal['list']


class _SandboxInputRequired(TypedDict):
    path: str


class SandboxInput(_SandboxInputRequired, total=False):
    """One input file: inline `base64` or an https `url`; `sha256` is verified when given."""
    url: str
    base64: str
    sha256: str


class SandboxExecRequest(TypedDict, total=False):
    """Exactly one of `cmd`, `shell` or `language` + `code`."""
    cmd: List[str]
    shell: str
    language: Literal['python', 'bash']
    code: str
    env: Dict[str, str]
    cwd: str
    timeout_seconds: int
    stdin: str
    inputs: List[SandboxInput]


class SandboxRunRequest(TypedDict, total=False):
    """The fields of `SandboxCreate` plus those of `SandboxExecRequest`."""
    template: Literal['codai-base']
    ttl_seconds: int
    egress: SandboxEgress
    metadata: Dict[str, str]
    cmd: List[str]
    shell: str
    language: Literal['python', 'bash']
    code: str
    env: Dict[str, str]
    cwd: str
    timeout_seconds: int
    stdin: str
    inputs: List[SandboxInput]


class SandboxReceiptOutputsItem(TypedDict):
    path: str
    sha256: str
    bytes: int


class SandboxReceipt(TypedDict):
    """What ran and what it produced: image digest, hashes of the inputs and the command, every output file with its …"""
    image_digest: str
    template: str
    input_sha256: str
    command_sha256: str
    outputs: List[SandboxReceiptOutputsItem]
    generation_before: int
    generation_after: int


class SandboxArtifact(TypedDict):
    """Sandbox artifact"""
    id: str
    path: str
    bytes: int
    mime: str
    sha256: str
    scan: Literal['clean', 'infected', 'error']
    url: Optional[str]
    expires_at: Optional[str]


class SandboxArtifactList(TypedDict):
    """Sandbox artifact list"""
    data: List[SandboxArtifact]


class _SandboxExecResultRequired(TypedDict):
    exit_code: Optional[int]
    stdout: str
    stderr: str
    timed_out: bool
    duration_ms: int
    receipt: SandboxReceipt


class SandboxExecResult(_SandboxExecResultRequired, total=False):
    """Exec result"""
    artifacts: List[SandboxArtifact]


class SandboxExecEventOption1(TypedDict):
    """start"""
    type: Literal['start']
    exec_id: str
    instance: str
    restored: Literal['hot', 'gcs', 'empty']
    restore_ms: int


class SandboxExecEventOption2(TypedDict):
    """output"""
    type: Literal['stdout', 'stderr']
    data: str


class SandboxExecEventOption3(TypedDict):
    """truncated"""
    type: Literal['truncated']
    stream: Literal['stdout', 'stderr']


class SandboxExecEventOption4(TypedDict):
    """exit"""
    type: Literal['exit']
    exit_code: Optional[int]
    timed_out: bool
    duration_ms: int
    cpu_ms: int
    generation: int
    workspace_bytes: int
    changed: List[str]
    receipt: SandboxReceipt


class SandboxExecEventOption5(TypedDict):
    """error"""
    type: Literal['error']
    code: str
    message: str


# One SSE `data:` frame of an exec stream. The stream ends after `exit` or `error`.
SandboxExecEvent = Union[SandboxExecEventOption1, SandboxExecEventOption2, SandboxExecEventOption3, SandboxExecEventOption4, SandboxExecEventOption5]


class SandboxFileWritten(TypedDict):
    """File written"""
    path: str
    bytes: int
    sha256: str
    generation: int


class SandboxFileListEntriesItem(TypedDict):
    path: str
    bytes: int
    type: Literal['file', 'dir']
    mtime: str


class SandboxFileList(TypedDict):
    """Workspace listing"""
    entries: List[SandboxFileListEntriesItem]


class SandboxSnapshot(TypedDict):
    """Workspace snapshot"""
    object: str
    bytes: int
    sha256: str


class _SandboxRunCodeRequestRequired(TypedDict):
    code: str


class SandboxRunCodeRequest(_SandboxRunCodeRequestRequired, total=False):
    """Run code request"""
    timeout_seconds: int


class SandboxRunCodeResultError(TypedDict):
    """The uncaught exception, or null."""
    name: str
    value: str
    traceback: str


class SandboxRunCodeResult(TypedDict):
    """Run code result"""
    stdout: str
    stderr: str
    result: Optional[str]
    error: Optional[SandboxRunCodeResultError]
    duration_ms: int
    execution_count: int
    kernel_restarted: bool


class SandboxResumedUsage(TypedDict):
    exec_count: int
    exec_seconds: float


class SandboxResumed(TypedDict):
    id: str
    object: Literal['sandbox']
    status: Literal['running', 'paused', 'stopped', 'expired', 'destroyed']
    backend: Literal['v1', 'v2']
    restored: bool
    template: str
    egress: SandboxEgress
    created_at: str
    expires_at: str
    last_exec_at: Optional[str]
    metadata: Dict[str, str]
    usage: SandboxResumedUsage
    ready_ms: int


class _SandboxForkRequestRequired(TypedDict):
    count: int


class SandboxForkRequest(_SandboxForkRequestRequired, total=False):
    """Fork sandbox request"""
    ttl_seconds: int


class SandboxForkResultDataItemError(TypedDict):
    """Why this child failed (it is not running)."""
    code: str
    message: str


class _SandboxForkResultDataItemRequired(TypedDict):
    id: str
    restored: bool
    ready_ms: int


class SandboxForkResultDataItem(_SandboxForkResultDataItemRequired, total=False):
    error: SandboxForkResultDataItemError


class SandboxForkResult(TypedDict):
    """Fork result"""
    object: Literal['list']
    parent_id: str
    data: List[SandboxForkResultDataItem]


class _SandboxPreviewRequestRequired(TypedDict):
    port: int


class SandboxPreviewRequest(_SandboxPreviewRequestRequired, total=False):
    """Preview URL request"""
    ttl_seconds: int


class SandboxPreview(TypedDict):
    """Preview URL"""
    port: int
    url: str
    expires_at: str


class VaultGuards(TypedDict):
    new_host: bool
    burst_max: int
    burst_window_s: int
    hour_start: Optional[int]
    hour_end: Optional[int]
    tz: str


class _VaultAccountRequired(TypedDict):
    bundle: Dict[str, Any]
    fingerprint: str
    default_tier: Literal['t1', 't2', 't3', 't4']
    revision: int


class VaultAccount(_VaultAccountRequired, total=False):
    locked_at: Optional[str]
    lock_reason: Optional[Literal['panic', 'honeytoken']]
    guards: VaultGuards
    key_scopes: Optional[List[Literal['vault.read', 'vault.add']]]
    digest_opt_out: bool


class VaultItemLimits(TypedDict):
    item_id: str
    per_minute: Optional[int]
    per_day: Optional[int]
    units_per_day: Optional[int]


class VaultLockResult(TypedDict):
    locked_at: str
    grants_revoked: int
    approvals_denied: int


class VaultUnlockChallenge(TypedDict):
    challenge: str
    expires_at: str
    message_template: str


class _VaultItemEnvelopeRequired(TypedDict):
    id: str
    vault_id: str
    revision: int
    wrapped_key: str
    ciphertext: str
    kind: Literal['login', 'api_key', 'env', 'ssh_key', 'oauth_token', 'note', 'card', 'identity', 'passkey']


class VaultItemEnvelope(_VaultItemEnvelopeRequired, total=False):
    slug: Optional[str]
    agent_meta: Optional[Dict[str, Any]]
    honeytoken: bool


class _VaultUseDecisionRequired(TypedDict):
    tier: Literal['t0', 't1', 't2', 't3', 't4', 'deny']
    allowed: bool
    reasons: List[str]


class VaultUseDecision(_VaultUseDecisionRequired, total=False):
    approval_id: Optional[str]
    match_number: Optional[str]
    action_hash: str
    cloud_usable: bool


class VaultDeviceKey(TypedDict):
    id: str
    kind: Literal['android_keystore', 'windows_hello', 'cli_ed25519', 'ios_secure_enclave']
    name: str
    surface: Literal['phone', 'wear', 'desktop', 'cli']
    public_key: str
    attestation: Literal['android-strongbox', 'android-tee', 'tpm', 'hello-unattested', 'software', 'ios-unattested']
    attestation_info: Dict[str, Any]
    created_at: str
    last_used_at: Optional[str]
    revoked_at: Optional[str]


class VaultDeviceChallenge(TypedDict):
    nonce: str
    expires_at: str


class VaultResolveChallenge(TypedDict):
    challenge: str
    expires_at: str


class VaultResolveProof(TypedDict):
    device_id: str
    challenge: str
    signature: str


class VaultDeviceEnrollAttestationOption1(TypedDict):
    android_chain: List[str]


class VaultDeviceEnrollAttestationOption2Tpm(TypedDict):
    attestation: str
    cert_chain: str


class VaultDeviceEnrollAttestationOption2(TypedDict):
    tpm: VaultDeviceEnrollAttestationOption2Tpm


class _VaultDeviceEnrollRequired(TypedDict):
    device_id: str
    kind: Literal['android_keystore', 'windows_hello', 'cli_ed25519', 'ios_secure_enclave']
    name: str
    surface: Literal['phone', 'wear', 'desktop', 'cli']
    public_key: str
    nonce: str
    vault_signature: str
    device_signature: str


class VaultDeviceEnroll(_VaultDeviceEnrollRequired, total=False):
    attestation: Union[VaultDeviceEnrollAttestationOption1, VaultDeviceEnrollAttestationOption2]


class VaultApprovalProofOption1(TypedDict):
    type: Literal['device']
    device_id: str
    signature: str


class VaultApprovalProofOption2(TypedDict):
    type: Literal['passkey']
    response: Dict[str, Any]


# Proven step-up for a decision. `device`: an enrolled device key signs `codai-vault/approve/v2|<approval_id>|<a…
VaultApprovalProof = Union[VaultApprovalProofOption1, VaultApprovalProofOption2]


class _VaultAddRequestCreateRequired(TypedDict):
    kind: Literal['login', 'api_key', 'env', 'ssh_key', 'oauth_token', 'note', 'card', 'identity', 'passkey']
    title: str
    purpose: str


class VaultAddRequestCreate(_VaultAddRequestCreateRequired, total=False):
    slug: str
    hosts: List[str]
    env_var: str
    fields: List[str]
    task: str


class VaultAddRequestCreated(TypedDict):
    id: str
    url: Optional[str]
    status: Literal['pending', 'completed', 'cancelled', 'expired']
    expires_at: str


class VaultAddRequestStatus(TypedDict):
    id: str
    status: Literal['pending', 'completed', 'cancelled', 'expired']
    slug: Optional[str]
    handle: Optional[str]
    item_id: Optional[str]
    expires_at: str


class VaultAddRequest(TypedDict):
    id: str
    status: Literal['pending', 'completed', 'cancelled', 'expired']
    agent: str
    kind: Literal['login', 'api_key', 'env', 'ssh_key', 'oauth_token', 'note', 'card', 'identity', 'passkey']
    title: str
    slug: Optional[str]
    hosts: List[str]
    env_var: Optional[str]
    fields: List[str]
    purpose: str
    task: Optional[str]
    handle: Optional[str]
    item_id: Optional[str]
    expires_at: str
    completed_at: Optional[str]
    created_at: str


class VaultEmergencyContact(TypedDict):
    id: str
    role: Literal['grantor', 'grantee']
    email: Optional[str]
    other_name: Optional[str]
    status: Literal['invited', 'accepted', 'sealed', 'requested', 'granted', 'revoked']
    delay_hours: Literal[24, 48, 72]
    vault_ids: List[str]
    grantee_fingerprint: Optional[str]
    grantee_public_keys: Optional[Dict[str, Any]]
    request_reason: Optional[str]
    requested_at: Optional[str]
    release_at: Optional[str]
    granted_at: Optional[str]
    denied_at: Optional[str]
    created_at: str


class VaultEmergencyDataVaultsItem(TypedDict):
    id: str
    encrypted_meta: str
    sealed_key: Dict[str, Any]


class VaultEmergencyDataItemsItem(TypedDict):
    id: str
    vault_id: str
    revision: int
    wrapped_key: str
    ciphertext: str
    kind: str
    slug: Optional[str]
    agent_meta: Any


class VaultEmergencyData(TypedDict):
    vaults: List[VaultEmergencyDataVaultsItem]
    items: List[VaultEmergencyDataItemsItem]


class VaultRotationEntry(TypedDict):
    item_id: str
    slug: Optional[str]
    title: Optional[str]
    kind: str
    interval_days: Optional[int]
    rotated_at: Optional[str]
    due_at: Optional[str]
    overdue: bool
    breached: bool
    breach_count: int
    breach_checked_at: Optional[str]
    snoozed_until: Optional[str]
    provider: Optional[Literal['stripe', 'github_pat', 'openai', 'google_api_key', 'other']]
    create_url: Optional[str]


class VaultDeriver(TypedDict):
    item_id: str
    provider: Literal['aws_sts', 'gcp_sa', 'cloudflare', 'github_app']
    config: Dict[str, Any]
    max_ttl_s: int
    updated_at: str


class VaultDerived(TypedDict):
    provider: Literal['aws_sts', 'gcp_sa', 'cloudflare', 'github_app']
    values: Dict[str, str]
    env: Dict[str, str]
    expires_at: str


class VaultQuorum(TypedDict):
    m: int
    scope: Literal['critical', 'high']


class VaultSealedKey(TypedDict):
    alg: Literal['xwing-hkdf-xchacha20poly1305']
    ct: str
    wrapped: str


class _VaultSummaryRequired(TypedDict):
    id: str
    kind: Literal['personal', 'shared']
    owner_user_id: str
    org_id: Optional[str]
    encrypted_meta: str
    role: Literal['owner', 'manager', 'editor', 'viewer']
    sealed_key: Dict[str, Any]
    quorum: Optional[VaultQuorum]
    rotation_needed_at: Optional[str]
    key_epoch: int


class VaultSummary(_VaultSummaryRequired, total=False):
    updated_at: str


class VaultMember(TypedDict):
    user_id: str
    email: Optional[str]
    name: Optional[str]
    role: Literal['owner', 'manager', 'editor', 'viewer']
    fingerprint: Optional[str]
    key_epoch: int
    added_at: str


class VaultMemberCandidatePublicKeys(TypedDict):
    kem: str
    sign: str


class VaultMemberCandidate(TypedDict):
    user_id: str
    email: Optional[str]
    name: Optional[str]
    fingerprint: str
    public_keys: VaultMemberCandidatePublicKeys


class _VaultApprovalQuorumRequired(TypedDict):
    m: int
    approvals: int
    needed: int


class VaultApprovalQuorum(_VaultApprovalQuorumRequired, total=False):
    voted: bool


class VaultVoteProofOption1(TypedDict):
    type: Literal['device']
    device_id: str
    signature: str


class VaultVoteProofOption2(TypedDict):
    type: Literal['passkey']
    response: Dict[str, Any]


# Proof for a quorum vote, over approve/v4: `codai-vault/approve/v4|<approval_id>|<action_hash>|<decision>|once|…
VaultVoteProof = Union[VaultVoteProofOption1, VaultVoteProofOption2]


class VaultSimulationRow(TypedDict):
    event_id: str
    at: str
    item_id: Optional[str]
    title: Optional[str]
    agent: str
    chain: List[str]
    mode: str
    host: Optional[str]
    current_tier: Literal['t0', 't1', 't2', 't3', 't4', 'deny']
    simulated_tier: Literal['t0', 't1', 't2', 't3', 't4', 'deny']
    reasons: List[str]
    source: Literal['event', 'approval']


class VaultSimulation(TypedDict):
    evaluated: int
    changed: int
    grants: Literal['none']
    rows: List[VaultSimulationRow]


class VaultReceiptKey(TypedDict):
    kid: str
    alg: Literal['ES256']
    pem: str


# POST /v1/chat/completions — request body
CreateChatCompletionBody = ChatCompletionRequest


# POST /v1/chat/completions — 200 response
CreateChatCompletionResponse = ChatCompletionResponse


# POST /v1/responses — request body
CreateResponseBody = ChatResponsesRequest


# POST /v1/responses — 200 response
CreateResponseResponse = ChatResponsesResponse


# POST /v1/messages — request body
CreateMessageBody = MsgRequest


# POST /v1/messages — 200 response
CreateMessageResponse = MsgResponse


# POST /v1/embeddings — request body
CreateEmbeddingsBody = CoreEmbeddingsRequest


# POST /v1/embeddings — 200 response
CreateEmbeddingsResponse = CoreEmbeddingsResponse


# POST /v1/images/generations — request body
CreateImageBody = CoreImagesRequest


# POST /v1/images/generations — 200 response
CreateImageResponse = CoreImagesResponse


class _CreateMusicBodyRequired(TypedDict):
    prompt: str


class CreateMusicBody(_CreateMusicBodyRequired, total=False):
    model: Literal['codai-music', 'codai-music-pro', 'codai-music-legacy']
    lyrics: str
    instrumental: bool
    bpm: int
    duration_seconds: int
    language: str
    negative_prompt: str
    seed: int
    n: int
    response_format: MediaResponseFormat


class CreateMusicResponseDataItemOption1(TypedDict, total=False):
    b64_json: str
    mime_type: str
    duration_seconds: float
    sample_rate: int
    lyrics: Optional[str]
    caption: Optional[str]
    lyrics_match: Optional[float]
    warnings: List[str]


class _CreateMusicResponseDataItemOption2Required(TypedDict):
    asset_id: str
    kind: AssetKind
    status: Literal['pending', 'ready', 'failed', 'deleted']
    model: str
    url: Optional[str]
    mime_type: str
    bytes: int
    duration_seconds: Optional[float]
    width: Optional[int]
    height: Optional[int]
    created_at: str
    expires_at: Optional[str]


class CreateMusicResponseDataItemOption2(_CreateMusicResponseDataItemOption2Required, total=False):
    lyrics: Optional[str]
    caption: Optional[str]
    lyrics_match: Optional[float]
    warnings: List[str]


class CreateMusicResponse(TypedDict, total=False):
    created: int
    model: str
    data: List[Union[CreateMusicResponseDataItemOption1, CreateMusicResponseDataItemOption2]]


class CreateVideoBodyImage(TypedDict, total=False):
    b64_json: str
    mime_type: Literal['image/png', 'image/jpeg']


class _CreateVideoBodyRequired(TypedDict):
    prompt: str


class CreateVideoBody(_CreateVideoBodyRequired, total=False):
    model: str
    negative_prompt: str
    seconds: Literal[4, 6, 8]
    aspect_ratio: Literal['16:9', '9:16']
    resolution: Literal['720p', '1080p']
    audio: bool
    image: CreateVideoBodyImage
    reference_asset_ids: List[str]
    seed: int


class CreateVideoResponse(TypedDict, total=False):
    id: str
    object: str
    status: str
    model: str
    seconds: int
    resolution: Literal['720p', '1080p']
    audio: bool
    asset_id: str
    estimated_cost_micro_usd: str


class GetVideoResponseDataItemOption1(TypedDict, total=False):
    b64_json: str
    mime_type: str


class GetVideoResponse(TypedDict, total=False):
    id: str
    object: str
    status: Literal['running', 'succeeded', 'failed', 'filtered']
    error: str
    seconds: int
    data: List[Union[GetVideoResponseDataItemOption1, AssetDto]]


# GET /v1/assets — 200 response
ListAssetsResponse = AssetList


# GET /v1/assets/{id} — 200 response
GetAssetResponse = AssetDto


# DELETE /v1/assets/{id} — 200 response
DeleteAssetResponse = AssetDeleted


# GET /v1/studio/renders — 200 response
ListRendersResponse = StudioRenderList


# POST /v1/studio/renders — request body
CreateRenderBody = StudioRenderCreate


# POST /v1/studio/renders — 202 response
CreateRenderResponse = StudioRenderAccepted


# GET /v1/studio/renders/{id} — 200 response
GetRenderResponse = Union[StudioRender, StudioAudioRender]


# POST /v1/studio/timelines — request body
CreateTimelineBody = StudioTimelineCreate


# POST /v1/studio/timelines — 202 response
CreateTimelineResponse = StudioTimelineAccepted


# POST /v1/studio/renders/{id}/scenes/{sceneId}/regenerate — request body
RegenerateRenderSceneBody = StudioSceneRegenerate


# POST /v1/studio/renders/{id}/scenes/{sceneId}/regenerate — 202 response
RegenerateRenderSceneResponse = StudioSceneRegenerateAccepted


# POST /v1/studio/documents — request body
CreateDocumentBody = DocumentCreateRequest


# POST /v1/studio/documents — 200 response
CreateDocumentResponse = Document


# GET /v1/studio/documents/{id} — 200 response
RetrieveDocumentResponse = Document


# POST /v1/studio/documents/{id}/creative — 200 response
CreateCreativeFromDocumentResponse = StudioCreativeFromDocument


class CreateDocumentPreviewBody(TypedDict, total=False):
    model: str


# POST /v1/studio/documents/{id}/previews — 202 response
CreateDocumentPreviewResponse = DocumentPreviewAccepted


# GET /v1/studio/previews/{id} — 200 response
RetrievePreviewResponse = DocumentPreview


# POST /v1/studio/documents/{id}/video — request body
CreateDocumentVideoBody = DocumentVideoRequest


# POST /v1/studio/documents/{id}/video — 202 response
CreateDocumentVideoResponse = DocumentVideoAccepted


# GET /v1/studio/sfx — 200 response
SearchSfxResponse = SfxList


# POST /v1/studio/sfx/{sfx_id}/import — 200 response
ImportSfxResponse = AssetDto


# GET /v1/studio/creatives — 200 response
ListCreativesResponse = CreativeList


# POST /v1/studio/creatives — request body
CreateCreativeBody = CreativeCreateRequest


# POST /v1/studio/creatives — 201 response
CreateCreativeResponse = Creative


# GET /v1/studio/creatives/{id} — 200 response
GetCreativeResponse = CreativeDetail


# DELETE /v1/studio/creatives/{id} — 200 response
DeleteCreativeResponse = CreativeDeleted


# GET /v1/studio/creatives/{id}/outline — 200 response
GetCreativeOutlineResponse = CreativeOutline


# POST /v1/studio/creatives/{id}/find — request body
FindCreativeNodesBody = CreativeFindRequest


# POST /v1/studio/creatives/{id}/find — 200 response
FindCreativeNodesResponse = CreativeFindResult


# POST /v1/studio/creatives/{id}/subtree — request body
GetCreativeSubtreeBody = CreativeSubtreeRequest


# POST /v1/studio/creatives/{id}/subtree — 200 response
GetCreativeSubtreeResponse = CreativeSubtree


# POST /v1/studio/creatives/{id}/ops — request body
ApplyCreativeOpsBody = CreativeOpsRequest


# POST /v1/studio/creatives/{id}/ops — 200 response
ApplyCreativeOpsResponse = CreativeOpsResult


# POST /v1/studio/creatives/{id}/restyle — request body
RestyleCreativeBody = CreativeRestyleRequest


# POST /v1/studio/creatives/{id}/restyle — 200 response
RestyleCreativeResponse = CreativeOpsResult


# POST /v1/studio/creatives/{id}/captions — request body
CaptionCreativeBody = CreativeCaptionsRequest


# POST /v1/studio/creatives/{id}/captions — 200 response
CaptionCreativeResponse = CreativeCaptionsResult


# POST /v1/studio/creatives/{id}/transcript-cut — request body
TranscriptCutCreativeBody = CreativeTranscriptCutRequest


# POST /v1/studio/creatives/{id}/transcript-cut — 200 response
TranscriptCutCreativeResponse = CreativeTranscriptCutResult


# POST /v1/studio/creatives/{id}/nodes/{nodeId}/regenerate — request body
RegenerateCreativeNodeBody = CreativeRegenerateNodeRequest


# POST /v1/studio/creatives/{id}/nodes/{nodeId}/regenerate — 200 response
RegenerateCreativeNodeResponse = CreativeRegenerateNodeResult


# POST /v1/studio/creatives/{id}/adapt — request body
AdaptCreativeBody = CreativeAdaptRequest


# POST /v1/studio/creatives/{id}/adapt — 200 response
AdaptCreativeResponse = CreativeAdaptResult


# GET /v1/studio/creatives/{id}/locales — 200 response
GetCreativeLocalesResponse = CreativeLocaleStatus


# POST /v1/studio/creatives/{id}/localize — request body
LocalizeCreativeBody = CreativeLocalizeRequest


# POST /v1/studio/creatives/{id}/localize — 200 response
LocalizeCreativeResponse = CreativeLocalizeResult


# POST /v1/studio/creatives/{id}/locales/{locale}/fork — request body
ForkCreativeLocaleBody = CreativeLocaleForkRequest


# POST /v1/studio/creatives/{id}/locales/{locale}/fork — 201 response
ForkCreativeLocaleResponse = CreativeLocaleForkResult


# GET /v1/studio/creatives/{id}/versions — 200 response
ListCreativeVersionsResponse = CreativeVersionList


# POST /v1/studio/creatives/{id}/revert — request body
RevertCreativeBody = CreativeRevertRequest


# POST /v1/studio/creatives/{id}/revert — 200 response
RevertCreativeResponse = CreativeRevertResult


# POST /v1/studio/creatives/{id}/fork — request body
ForkCreativeBody = CreativeForkRequest


# POST /v1/studio/creatives/{id}/fork — 201 response
ForkCreativeResponse = Creative


class LintCreativeBody(TypedDict, total=False):
    """Lint request"""
    locale: str


# POST /v1/studio/creatives/{id}/lint — 200 response
LintCreativeResponse = CreativeLintResult


# POST /v1/studio/creatives/{id}/lint/fix — request body
FixCreativeLintBody = CreativeLintFixRequest


# POST /v1/studio/creatives/{id}/lint/fix — 200 response
FixCreativeLintResponse = CreativeLintFixResult


# GET /v1/studio/creatives/{id}/controls — 200 response
GetCreativeControlsResponse = CreativeControls


# GET /v1/studio/creatives/{id}/compiled — 200 response
GetCreativeCompiledResponse = CreativeCompiled


# POST /v1/studio/creatives/{id}/render — request body
RenderCreativeBody = Union[CreativeRenderRequest, CreativeAudioRenderRequest]


# POST /v1/studio/creatives/{id}/render — 200 response
RenderCreativeResponse = CreativeRenderCached


# POST /v1/studio/creatives/{id}/render — 202 response
RenderCreativeResponse202 = Union[CreativeRenderAccepted, CreativeAudioRenderAccepted]


# POST /v1/studio/creatives/{id}/frame — request body
CreateCreativeFrameBody = CreativeFrameRequest


# POST /v1/studio/creatives/{id}/frame — 200 response
CreateCreativeFrameResponse = CreativeFrames


# POST /v1/studio/creatives/{id}/frame — 202 response
CreateCreativeFrameResponse202 = CreativeFrameJob


# GET /v1/studio/creatives/{id}/frames/{jobId} — 200 response
GetCreativeFrameJobResponse = CreativeFrames


# GET /v1/studio/creatives/{id}/frames/{jobId} — 202 response
GetCreativeFrameJobResponse202 = CreativeFrameJob


# GET /v1/studio/creatives/{id}/export.fcpxml — 202 response
ExportCreativeFcpxmlResponse = StudioExport


# GET /v1/studio/creatives/{id}/export.lottie — 200 response
ExportCreativeLottieResponse = Union[StudioExport, Dict[str, Any]]


# POST /v1/studio/creatives/{id}/comments — request body
CommentCreativeBody = CreativeCommentRequest


# POST /v1/studio/creatives/{id}/comments — 200 response
CommentCreativeResponse = CreativeCommentResult


# GET /v1/studio/creatives/{id}/variants — 200 response
ListCreativeVariantsResponse = CreativeVariantList


# POST /v1/studio/creatives/{id}/variants — request body
CreateCreativeVariantsBody = CreativeVariantsRequest


# POST /v1/studio/creatives/{id}/variants — 200 response
CreateCreativeVariantsResponse = CreativeVariantsResult


# POST /v1/studio/creatives/{id}/variants/{variantId}/pick — request body
PickCreativeVariantBody = CreativeVariantPickRequest


# POST /v1/studio/creatives/{id}/variants/{variantId}/pick — 200 response
PickCreativeVariantResponse = CreativeVariantPickResult


# POST /v1/studio/creatives/{id}/template — request body
SaveCreativeTemplateBody = SaveTemplateRequest


# POST /v1/studio/creatives/{id}/template — 201 response
SaveCreativeTemplateResponse = CreativeTemplate


# POST /v1/studio/creatives/{id}/build — request body
BuildCreativeBody = Union[CreativeBuildRequest, CreativePagedBuildRequest]


# POST /v1/studio/creatives/{id}/build — 200 response
BuildCreativeResponse = StudioCreativeBuild


# POST /v1/studio/creatives/{id}/build — 202 response
BuildCreativeResponse202 = StudioCreativePagedBuild


# POST /v1/studio/creatives/{id}/post-copy — request body
WriteCreativePostCopyBody = StudioPostCopyRequest


# POST /v1/studio/creatives/{id}/post-copy — 200 response
WriteCreativePostCopyResponse = StudioPostCopy


# POST /v1/studio/brand-kits/extract — request body
ExtractBrandKitBody = BrandKitExtractRequest


# POST /v1/studio/brand-kits/extract — 201 response
ExtractBrandKitResponse = BrandKit


# GET /v1/studio/brand-kits — 200 response
ListBrandKitsResponse = BrandKitList


# POST /v1/studio/brand-kits — request body
CreateBrandKitBody = BrandKitCreateRequest


# POST /v1/studio/brand-kits — 201 response
CreateBrandKitResponse = BrandKit


# GET /v1/studio/brand-kits/{id} — 200 response
GetBrandKitResponse = BrandKit


# PATCH /v1/studio/brand-kits/{id} — request body
UpdateBrandKitBody = BrandKitUpdateRequest


# PATCH /v1/studio/brand-kits/{id} — 200 response
UpdateBrandKitResponse = BrandKit


# DELETE /v1/studio/brand-kits/{id} — 200 response
DeleteBrandKitResponse = BrandKitDeleted


# GET /v1/studio/brand-kits/{id}/dtcg — 200 response
ExportBrandKitDtcgResponse = BrandKitDtcg


# POST /v1/studio/productions — request body
CreateStudioProductionBody = StudioProductionCreate


# POST /v1/studio/productions — 202 response
CreateStudioProductionResponse = StudioProduction


# GET /v1/studio/productions/{id} — 200 response
GetStudioProductionResponse = StudioProduction


# GET /v1/studio/music-room — 200 response
ListStudioMusicRoomsResponse = MusicRoomList


# POST /v1/studio/music-room — request body
CreateStudioMusicRoomBody = MusicRoomCreate


# POST /v1/studio/music-room — 202 response
CreateStudioMusicRoomResponse = MusicRoom


# GET /v1/studio/music-room/quota — 200 response
GetStudioMusicRoomQuotaResponse = MusicRoomQuota


# GET /v1/studio/music-room/plugins — 200 response
ListStudioMusicRoomPluginsResponse = MusicPluginList


# GET /v1/studio/music-room/plugins/{format}/{pluginId} — 200 response
GetStudioMusicRoomPluginResponse = MusicPlugin


# GET /v1/studio/music-room/{id} — 200 response
GetStudioMusicRoomResponse = MusicRoom


# POST /v1/studio/music-room/{id}/choose — request body
ChooseStudioMusicRoomBody = MusicRoomChoose


# POST /v1/studio/music-room/{id}/choose — 200 response
ChooseStudioMusicRoomResponse = MusicRoom


# POST /v1/studio/music-room/{id}/direct — request body
DirectStudioMusicRoomBody = MusicRoomDirect


# POST /v1/studio/music-room/{id}/direct — 202 response
DirectStudioMusicRoomResponse = MusicRoom


# POST /v1/studio/music-room/{id}/plugin — request body
SetStudioMusicRoomTrackPluginBody = MusicRoomSetPlugin


# POST /v1/studio/music-room/{id}/plugin — 202 response
SetStudioMusicRoomTrackPluginResponse = MusicRoom


# GET /v1/studio/media-ops — 200 response
ListStudioMediaOpsResponse = MediaOpList


# POST /v1/studio/media-ops/{op}/quote — request body
QuoteStudioMediaOpBody = MediaOpRequest


# POST /v1/studio/media-ops/{op}/quote — 200 response
QuoteStudioMediaOpResponse = MediaOpQuote


# POST /v1/studio/media-ops/{op} — request body
RunStudioMediaOpBody = MediaOpRequest


# POST /v1/studio/media-ops/{op} — 200 response
RunStudioMediaOpResponse = MediaOpResult


# POST /v1/studio/media-ops/{op} — 202 response
RunStudioMediaOpResponse202 = MediaOpJob


# GET /v1/studio/media-ops/jobs/{id} — 200 response
GetStudioMediaOpJobResponse = MediaOpJob


# POST /v1/studio/lyrics — request body
WriteStudioLyricsBody = StudioLyricsRequest


# POST /v1/studio/lyrics — 200 response
WriteStudioLyricsResponse = StudioLyrics


# POST /v1/studio/lyrics/align — request body
AlignStudioLyricsBody = StudioLyricsAlignRequest


# POST /v1/studio/lyrics/align — 200 response
AlignStudioLyricsResponse = StudioLyricsAlignment


# GET /v1/studio/templates — 200 response
ListCreativeTemplatesResponse = CreativeTemplateList


# GET /v1/studio/templates/{id} — 200 response
GetCreativeTemplateResponse = CreativeTemplate


# DELETE /v1/studio/templates/{id} — 200 response
DeleteCreativeTemplateResponse = CreativeTemplateDeleted


# GET /v1/studio/exports/{id} — 200 response
GetStudioExportResponse = StudioExport


# GET /v1/studio/quote — 200 response
GetStudioQuoteResponse = StudioQuote


# GET /v1/studio/batches — 200 response
ListStudioBatchesResponse = StudioBatchList


# POST /v1/studio/batches — request body
CreateStudioBatchBody = StudioBatchCreateRequest


# POST /v1/studio/batches — 200 response
CreateStudioBatchResponse = StudioBatchDryRun


# POST /v1/studio/batches — 201 response
CreateStudioBatchResponse201 = StudioBatchDetail


# GET /v1/studio/batches/{id} — 200 response
GetStudioBatchResponse = StudioBatchDetail


# POST /v1/studio/batches/{id}/cancel — 200 response
CancelStudioBatchResponse = StudioBatch


# POST /v1/studio/batches/{id}/retry — 200 response
RetryStudioBatchResponse = StudioBatch


# POST /v1/studio/batches/{id}/zip — 200 response
ZipStudioBatchResponse = StudioBatch


# GET /v1/studio/creatives/{id}/shares — 200 response
ListCreativeSharesResponse = StudioShareList


# POST /v1/studio/creatives/{id}/shares — request body
CreateCreativeShareBody = StudioShareCreateRequest


# POST /v1/studio/creatives/{id}/shares — 201 response
CreateCreativeShareResponse = StudioShareCreated


# GET /v1/studio/creatives/{id}/review — 200 response
GetCreativeReviewResponse = StudioReview


# POST /v1/studio/creatives/{id}/review — request body
UpdateCreativeReviewBody = StudioReviewUpdateRequest


# POST /v1/studio/creatives/{id}/review — 200 response
UpdateCreativeReviewResponse = StudioReview


# GET /v1/studio/creatives/{id}/review/threads — 200 response
ListCreativeReviewThreadsResponse = StudioReviewThreadList


# POST /v1/studio/creatives/{id}/review/threads — request body
CreateCreativeReviewThreadBody = StudioReviewThreadCreateRequest


# POST /v1/studio/creatives/{id}/review/threads — 201 response
CreateCreativeReviewThreadResponse = StudioReviewThread


# POST /v1/studio/creatives/{id}/review/threads/{threadId}/replies — request body
ReplyCreativeReviewThreadBody = StudioReviewReplyRequest


# POST /v1/studio/creatives/{id}/review/threads/{threadId}/replies — 201 response
ReplyCreativeReviewThreadResponse = StudioReviewThread


# POST /v1/studio/creatives/{id}/review/threads/{threadId}/resolve — 200 response
ResolveCreativeReviewThreadResponse = StudioReviewThread


# POST /v1/studio/creatives/{id}/review/threads/{threadId}/reopen — 200 response
ReopenCreativeReviewThreadResponse = StudioReviewThread


# POST /v1/studio/shares/{token}/remix — request body
RemixStudioShareBody = StudioRemixRequest


# POST /v1/studio/shares/{token}/remix — 201 response
RemixStudioShareResponse = StudioRemixResult


# POST /v1/studio/voices/{id}/singing-consent — request body
AddStudioVoiceSingingConsentBody = StudioVoiceSingingConsentRequest


# POST /v1/studio/voices/{id}/singing-consent — 200 response
AddStudioVoiceSingingConsentResponse = StudioVoice


# POST /v1/studio/voice-revocations — request body
CreateVoiceRevocationBody = StudioVoiceRevocationRequest


# POST /v1/studio/voice-revocations — 202 response
CreateVoiceRevocationResponse = StudioVoiceRevocation


# POST /v1/studio/abuse-reports — request body
CreateStudioAbuseReportBody = StudioAbuseReportRequest


# POST /v1/studio/abuse-reports — 202 response
CreateStudioAbuseReportResponse = StudioAbuseReport


# GET /v1/public/studio/shares/{token} — 200 response
GetPublicStudioShareResponse = StudioPublicShare


# POST /v1/public/studio/reviews/{token}/threads — request body
CreatePublicReviewThreadBody = StudioPublicThreadCreateRequest


# POST /v1/public/studio/reviews/{token}/threads — 201 response
CreatePublicReviewThreadResponse = StudioReviewThread


# POST /v1/public/studio/reviews/{token}/threads/{threadId}/replies — request body
ReplyPublicReviewThreadBody = StudioPublicReplyRequest


# POST /v1/public/studio/reviews/{token}/threads/{threadId}/replies — 201 response
ReplyPublicReviewThreadResponse = StudioReviewThread


# POST /v1/public/studio/reviews/{token}/threads/{threadId}/resolve — request body
ResolvePublicReviewThreadBody = StudioPublicNameRequest


# POST /v1/public/studio/reviews/{token}/threads/{threadId}/resolve — 200 response
ResolvePublicReviewThreadResponse = StudioReviewThread


# POST /v1/public/studio/reviews/{token}/threads/{threadId}/reopen — request body
ReopenPublicReviewThreadBody = StudioPublicNameRequest


# POST /v1/public/studio/reviews/{token}/threads/{threadId}/reopen — 200 response
ReopenPublicReviewThreadResponse = StudioReviewThread


# POST /v1/public/studio/reviews/{token}/decision — request body
DecidePublicReviewBody = StudioPublicDecisionRequest


# POST /v1/public/studio/reviews/{token}/decision — 200 response
DecidePublicReviewResponse = StudioPublicReview


# POST /v1/images/edits — request body
EditImageBody = CoreImageEditRequest


# POST /v1/images/edits — 200 response
EditImageResponse = CoreImagesResponse


# POST /v1/systemone — request body
CreateSystemOneBody = SystemOneRequest


# POST /v1/systemone — 200 response
CreateSystemOneResponse = SystemOneResponse


# POST /v1/audio/transcriptions — request body
CreateTranscriptionBody = CoreTranscriptionRequest


# POST /v1/audio/transcriptions — 200 response
CreateTranscriptionResponse = CoreTranscriptionResponse


# POST /v1/audio/speech — request body
CreateSpeechBody = CoreSpeechRequest


# POST /v1/audio/speech — 200 response
CreateSpeechResponse = SpeechJson


# POST /v1/audio/speech/stream — request body
CreateSpeechStreamBody = SpeechStreamRequest


# POST /v1/tokens — request body
CreateEphemeralTokenBody = CoreTokenRequest


# POST /v1/tokens — 200 response
CreateEphemeralTokenResponse = CoreTokenResponse


# GET /v1/models — 200 response
ListModelsResponse = CoreModelList


# GET /health — 200 response
GetHealthResponse = CoreHealth


# GET /health/ready — 200 response
GetHealthReadyResponse = CoreHealthReady


# GET /status — 200 response
GetStatusResponse = CoreStatus


# POST /v1/agents/run — request body
RunAgentSyncBody = AgentRunRequest


# POST /v1/agents/run — 200 response
RunAgentSyncResponse = AgentSyncResult


# POST /v1/agents/runs — request body
CreateAgentRunBody = AgentRunCreateRequest


# POST /v1/agents/runs — 202 response
CreateAgentRunResponse = AgentRunAccepted


# GET /v1/agents/runs/stats — 200 response
GetAgentRunStatsResponse = AgentRunStats


# GET /v1/agents/runs/{id} — 200 response
GetAgentRunResponse = AgentRun


class ListAgentRunStepsResponse(TypedDict):
    id: str
    steps: List[AgentRunStep]


class CancelAgentRunResponse(TypedDict):
    id: str
    status: Literal['cancelled']


# POST /v1/tools/search — request body
ToolsSearchBody = ToolSearchRequest


# POST /v1/tools/search — 200 response
ToolsSearchResponse = Union[ToolSearchResponse, ToolSearchProviderResponse, ToolSearchGoogleResponse]


# POST /v1/tools/fetch — request body
ToolsFetchBody = ToolFetchRequest


# POST /v1/tools/fetch — 200 response
ToolsFetchResponse = ToolFetchResponse


# POST /v1/research — request body
CreateResearchBody = ResearchRequest


# POST /v1/research — 200 response
CreateResearchResponse = ResearchJob


# GET /v1/research/{id} — 200 response
GetResearchResponse = ResearchJob


class _ToolsGroundBodyRequired(TypedDict):
    image: str
    instruction: str


class ToolsGroundBody(_ToolsGroundBodyRequired, total=False):
    width: int
    height: int


class _ToolsGroundResponseRequired(TypedDict):
    found: bool
    x_norm: Optional[float]
    y_norm: Optional[float]
    conf: Optional[float]
    model: str
    took_ms: int


class ToolsGroundResponse(_ToolsGroundResponseRequired, total=False):
    x: int
    y: int
    raw: str


# GET /v1/cards/weather — 200 response
CardsWeatherResponse = CardDataResponse


# GET /v1/cards/places — 200 response
CardsPlacesResponse = CardDataResponse


# GET /v1/cards/geocode — 200 response
CardsGeocodeResponse = CardDataResponse


# GET /v1/cards/fx — 200 response
CardsFxResponse = CardDataResponse


# GET /v1/cards/route — 200 response
CardsRouteResponse = CardDataResponse


# GET /v1/cards/track — 200 response
CardsTrackResponse = CardDataResponse


# GET /v1/cards/efactura — 200 response
CardsEfacturaResponse = CardDataResponse


class _CardsProductBodyRequired(TypedDict):
    url: str


class CardsProductBody(_CardsProductBodyRequired, total=False):
    lang: Literal['en', 'ro']


# POST /v1/cards/product — 200 response
CardsProductResponse = CardDataResponse


class CardsUnfurlBody(TypedDict):
    url: str


# POST /v1/cards/unfurl — 200 response
CardsUnfurlResponse = CardDataResponse


class CardsRenderBodyBlock(TypedDict):
    """A `chart` or `qr` card block."""
    type: str


class _CardsRenderBodyRequired(TypedDict):
    block: CardsRenderBodyBlock


class CardsRenderBody(_CardsRenderBodyRequired, total=False):
    format: Literal['png', 'svg']
    width: int
    height: int
    theme: Literal['light', 'dark']
    scale: int


class ListTasksResponse(TypedDict):
    tasks: List[Task]
    next_cursor: Optional[str]


class ListPendingTasksResponse(TypedDict):
    tasks: List[Task]


# GET /v1/tasks/stats — 200 response
GetTaskStatsResponse = TaskStats


# GET /v1/tasks/{id} — 200 response
GetTaskResponse = Task


# POST /v1/tasks/{id}/confirm — request body
ConfirmTaskBody = TaskConfirmRequest


# POST /v1/tasks/{id}/confirm — 200 response
ConfirmTaskResponse = TaskConfirmResponse


class ListSessionsResponse(TypedDict):
    sessions: List[SessionListItem]


# POST /v1/sessions — request body
CreateSessionBody = SessionCreateRequest


# POST /v1/sessions — 200 response
CreateSessionResponse = Session


# GET /v1/sessions/{id} — 200 response
GetSessionResponse = SessionDetail


# PATCH /v1/sessions/{id} — request body
UpdateSessionBody = SessionPatchRequest


# PATCH /v1/sessions/{id} — 200 response
UpdateSessionResponse = Session


class DeleteSessionResponse(TypedDict):
    deleted: Literal[True]
    id: str


class ListSessionEventsResponse(TypedDict):
    last_seq: int
    events: List[SessionEvent]


# POST /v1/sessions/{id}/events — request body
AppendSessionEventsBody = SessionEventsAppendRequest


# POST /v1/sessions/{id}/events — 200 response
AppendSessionEventsResponse = SessionEventsAppendResponse


class ListSessionControlsResponse(TypedDict):
    controls: List[SessionControl]


# POST /v1/sessions/{id}/control — request body
SubmitSessionControlBody = SessionControlRequest


# POST /v1/sessions/{id}/control — 200 response
SubmitSessionControlResponse = SessionControlAccepted


class MarkSessionControlAppliedResponse(TypedDict):
    id: str
    applied: Literal[True]


# POST /v1/sessions/{id}/dispatch — request body
DispatchToDeviceBody = SessionDispatchRequest


# POST /v1/sessions/{id}/dispatch — 200 response
DispatchToDeviceResponse = SessionDispatchResponse


# POST /v1/sessions/{id}/lease — request body
ClaimSessionLeaseBody = SessionLeaseClaimRequest


# POST /v1/sessions/{id}/lease — 200 response
ClaimSessionLeaseResponse = SessionLeaseResponse


# PUT /v1/sessions/{id}/lease — 200 response
HeartbeatSessionLeaseResponse = SessionLeaseResponse


class ReleaseSessionLeaseResponse(TypedDict):
    session_id: str
    released: bool


# GET /v1/devices/me/dispatch — 200 response
GetMyDispatchInboxResponse = SessionDispatchInbox


class ListDevicesResponse(TypedDict):
    devices: List[DeviceListItem]


# PATCH /v1/devices/{id} — request body
UpdateDeviceBody = DevicePatch


# PATCH /v1/devices/{id} — 200 response
UpdateDeviceResponse = DevicePatched


class DeleteDeviceResponse(TypedDict):
    deleted: Literal[True]
    id: str


class RevokeSelfKeyResponse(TypedDict):
    revoked: bool
    id: str


class ListHostsResponse(TypedDict):
    hosts: List[HostPresence]


# POST /v1/hosts/{deviceId}/exec — request body
ExecOnHostBody = HostExecBody


# POST /v1/hosts/{deviceId}/exec — 200 response
ExecOnHostResponse = HostExecResponse


# POST /v1/hosts/exec/{reqId}/result — request body
PostHostExecResultBody = HostExecResultBody


class PostHostExecResultResponse(TypedDict):
    ok: Literal[True]


class ListSessionsSharedWithMeResponse(TypedDict):
    sessions: List[OrgSharedSession]


class ListSessionSharesResponse(TypedDict):
    shares: List[OrgSessionShare]


# POST /v1/sessions/{id}/shares — request body
CreateSessionShareBody = OrgCreateShareBody


class _CreateSessionShareResponseRequired(TypedDict):
    id: str
    session_id: str
    principal_type: OrgSharePrincipalType
    principal_id: Optional[str]
    role: OrgSessionRole
    has_token: bool
    expires_at: Optional[str]
    created_by_user_id: str
    created_at: str


class CreateSessionShareResponse(_CreateSessionShareResponseRequired, total=False):
    token: str


class DeleteSessionShareResponse(TypedDict):
    deleted: Literal[True]
    id: str


class ListOrgsResponse(TypedDict):
    orgs: List[OrgWithRole]


class CreateOrgBody(TypedDict):
    name: str


# POST /v1/orgs — 201 response
CreateOrgResponse = OrgWithRole


class ListOrgMembersResponse(TypedDict):
    org_id: str
    members: List[OrgMember]


# POST /v1/orgs/{id}/members — request body
AddOrgMemberBody = OrgAddMemberBody


class AddOrgMemberResponse(TypedDict):
    org_id: str
    user_id: str
    role: OrgRole


class RemoveOrgMemberResponse(TypedDict):
    deleted: Literal[True]
    org_id: str
    user_id: str


class ListProjectsResponse(TypedDict):
    projects: List[Project]


# POST /v1/projects — request body
CreateProjectBody = ProjectCreateBody


class CreateProjectResponse(TypedDict):
    project: Project


class GetProjectResponse(TypedDict):
    project: Project
    environments: List[Environment]


# PATCH /v1/projects/{id} — request body
UpdateProjectBody = ProjectPatchBody


class UpdateProjectResponse(TypedDict):
    project: Project


class DeleteProjectResponse(TypedDict):
    deleted: Literal[True]
    id: str


class ListEnvironmentsResponse(TypedDict):
    environments: List[Environment]


# POST /v1/environments — request body
CreateEnvironmentBody = EnvironmentCreateBody


class _CreateEnvironmentResponseRequired(TypedDict):
    environment: Environment


class CreateEnvironmentResponse(_CreateEnvironmentResponseRequired, total=False):
    prebuild_claimed: bool


# POST /v1/environments/enroll — request body
EnrollEnvironmentBody = EnvironmentEnrollBody


# POST /v1/environments/enroll — 200 response
EnrollEnvironmentResponse = EnvironmentEnrolled


# GET /v1/environments/{id} — 200 response
GetEnvironmentResponse = EnvironmentDetail


# PATCH /v1/environments/{id} — request body
UpdateEnvironmentBody = EnvironmentPatchBody


class UpdateEnvironmentResponse(TypedDict):
    environment: Environment


# POST /v1/environments/{id}/start — 200 response
StartEnvironmentResponse = EnvironmentTransition


# POST /v1/environments/{id}/stop — 200 response
StopEnvironmentResponse = EnvironmentTransition


# POST /v1/environments/{id}/archive — 200 response
ArchiveEnvironmentResponse = EnvironmentTransition


# POST /v1/environments/{id}/destroy — 200 response
DestroyEnvironmentResponse = EnvironmentTransition


# POST /v1/environments/{id}/enroll-token — 201 response
CreateEnvironmentEnrollTokenResponse = EnvironmentEnrollToken


class ListEnvironmentMembersResponse(TypedDict):
    members: List[EnvironmentMember]


# POST /v1/environments/{id}/members — request body
AddEnvironmentMemberBody = EnvironmentAddMemberBody


class AddEnvironmentMemberResponse(TypedDict):
    member: EnvironmentMemberCreated


# PUT /v1/environments/{id}/members/me/ssh-key — request body
SetMyEnvironmentSshKeyBody = EnvironmentSshKeyBody


class SetMyEnvironmentSshKeyResponse(TypedDict):
    user_id: str
    ssh_public_key: Literal[True]


# POST /v1/environments/{id}/members/me/ssh-cert — request body
IssueMyEnvironmentSshCertBody = EnvironmentSshCertBody


# POST /v1/environments/{id}/members/me/ssh-cert — 200 response
IssueMyEnvironmentSshCertResponse = EnvironmentSshCert


# GET /v1/environments/{id}/ssh-ca — 200 response
GetEnvironmentSshCaResponse = EnvironmentSshCaKeys


# PATCH /v1/environments/{id}/members/{userId} — request body
SetEnvironmentMemberRoleBody = EnvironmentMemberRoleBody


class SetEnvironmentMemberRoleResponseMember(TypedDict):
    user_id: str
    role: EnvironmentRole


class SetEnvironmentMemberRoleResponse(TypedDict):
    member: SetEnvironmentMemberRoleResponseMember


class RemoveEnvironmentMemberResponse(TypedDict):
    deleted: Literal[True]
    user_id: str


class ListEnvironmentPortsResponse(TypedDict):
    ports: List[EnvironmentPort]


# PUT /v1/environments/{id}/ports/{port} — request body
SetEnvironmentPortBody = EnvironmentPortBody


class SetEnvironmentPortResponse(TypedDict):
    port: EnvironmentPort


class SetEnvironmentPortResponse201(TypedDict):
    port: EnvironmentPort


class RemoveEnvironmentPortResponse(TypedDict):
    deleted: Literal[True]
    port: int


class ListEnvironmentSecretsResponse(TypedDict):
    secrets: List[EnvironmentSecret]


# PUT /v1/environments/{id}/secrets/{name} — request body
SetEnvironmentSecretBody = EnvironmentSecretBody


# PUT /v1/environments/{id}/secrets/{name} — 200 response
SetEnvironmentSecretResponse = EnvironmentSecretSet


class RemoveEnvironmentSecretResponse(TypedDict):
    deleted: Literal[True]
    name: str


class ListEnvironmentTasksResponse(TypedDict):
    data: List[EnvironmentTask]


# POST /v1/environments/{id}/tasks — request body
CreateEnvironmentTaskBody = EnvironmentTaskCreate


# POST /v1/environments/{id}/tasks — 202 response
CreateEnvironmentTaskResponse = EnvironmentTaskQueued


class GetEnvironmentTaskResponse(TypedDict):
    task: EnvironmentTask


# POST /v1/environments/{id}/exec — request body
ExecEnvironmentBody = EnvironmentExecRequest


# POST /v1/environments/{id}/exec — 200 response
ExecEnvironmentResponse = EnvironmentExecResult


# GET /v1/verify/agent-output/key — 200 response
GetAgentOutputKeyResponse = AgentOutputKey


# POST /v1/verify/agent-output — request body
VerifyAgentOutputBody = AgentOutputVerifyRequest


# POST /v1/verify/agent-output — 200 response
VerifyAgentOutputResponse = AgentOutputVerifyResult


class AnonChallengeResponse(TypedDict):
    nonce: str
    pow_bits: int
    expires_at: str


class AnonCreateSessionBodyProofPow(TypedDict, total=False):
    counter: str


class AnonCreateSessionBodyProofAppAttest(TypedDict, total=False):
    key_id: str
    attestation: str
    assertion: str


class AnonCreateSessionBodyProof(TypedDict, total=False):
    """Exactly one of pow, turnstile, play_integrity, app_attest."""
    pow: AnonCreateSessionBodyProofPow
    turnstile: str
    play_integrity: str
    app_attest: AnonCreateSessionBodyProofAppAttest


class AnonCreateSessionBody(TypedDict):
    surface: Literal['web', 'android', 'ios', 'desktop', 'vscode', 'wear', 'tv']
    device_id: str
    nonce: str
    accept_terms: Literal[True]
    confirm_adult: Literal[True]
    proof: AnonCreateSessionBodyProof


class AnonCreateSessionResponseLimits(TypedDict, total=False):
    sessions_per_day: int
    sessions_left: int
    messages_per_session: int
    messages_left: int
    soft_wall_at: int
    resets_at: str


class _AnonCreateSessionResponseRequired(TypedDict):
    token: str
    session_id: str
    expires_at: str
    limits: AnonCreateSessionResponseLimits


class AnonCreateSessionResponse(_AnonCreateSessionResponseRequired, total=False):
    signup_url: str
    terms_version: str


class AnonStatusResponseLimits(TypedDict, total=False):
    sessions_per_day: int
    sessions_left: int
    messages_per_session: int
    messages_left: int
    soft_wall_at: int
    resets_at: str


class AnonStatusResponse(TypedDict, total=False):
    budget_open: bool
    limits: AnonStatusResponseLimits


class AnonImportBodyMessagesItem(TypedDict):
    role: Literal['user', 'assistant']
    content: str


class _AnonImportBodyRequired(TypedDict):
    anon_token: str
    messages: List[AnonImportBodyMessagesItem]


class AnonImportBody(_AnonImportBodyRequired, total=False):
    title: str


class AnonImportResponse(TypedDict):
    session_id: str


# POST /v1/public/provenance/check — 200 response
CheckProvenanceResponse = ProvenanceCheckResult


# GET /v1/account — 200 response
GetAccountResponse = AccountView


# PATCH /v1/account — request body
PatchAccountBody = AccountPatchRequest


# PATCH /v1/account — 200 response
PatchAccountResponse = AccountPatchResponse


# DELETE /v1/account — request body
DeleteAccountBody = AccountDeleteRequest


# DELETE /v1/account — 200 response
DeleteAccountResponse = AccountDeleteResponse


# GET /v1/billing — 200 response
GetBillingResponse = Billing


# GET /v1/billing/invoices — 200 response
ListBillingInvoicesResponse = BillingInvoiceList


# GET /v1/referrals — 200 response
GetReferralsResponse = ReferralsView


# GET /v1/settings — 200 response
GetSettingsResponse = SettingsResponse


# PATCH /v1/settings — request body
PatchSettingsBody = SettingsPatchRequest


# PATCH /v1/settings — 200 response
PatchSettingsResponse = SettingsResponse


# GET /v1/policy — 200 response
GetPolicyResponse = PolicyResponse


# POST /v1/os-gate/events — request body
RecordOsGateEventBody = OsGateEvent


# POST /v1/os-gate/events — 202 response
RecordOsGateEventResponse = OsGateEventAccepted


# GET /v1/receipt — 200 response
GetReceiptResponse = AccountReceipt


# POST /v1/feedback — request body
SubmitFeedbackBody = AccountFeedbackRequest


class SubmitFeedbackResponse(TypedDict):
    ok: Literal[True]
    event_id: str


class ListPhoneModelsResponse(TypedDict):
    models: List[AccountPhoneModel]


class ListTriggersResponse(TypedDict):
    data: List[Trigger]
    sources: List[TriggerSource]


# POST /v1/triggers — request body
CreateTriggerBody = TriggerCreate


# POST /v1/triggers — 201 response
CreateTriggerResponse = TriggerWithSecret


# PATCH /v1/triggers/{id} — request body
UpdateTriggerBody = TriggerPatch


# PATCH /v1/triggers/{id} — 200 response
UpdateTriggerResponse = Trigger


class DeleteTriggerResponse(TypedDict):
    id: str
    deleted: Literal[True]


class RotateTriggerSecretResponse(TypedDict):
    id: str
    secret: str


class SetTriggerSecretBody(TypedDict):
    secret: str


class SetTriggerSecretResponse(TypedDict):
    id: str
    replaced: bool


# POST /v1/triggers/{id}/test — request body
TestTriggerBody = TriggerTestFire


class TestTriggerResponse(TypedDict):
    event_id: int
    decision: TriggerDecision
    session_id: Optional[str]
    card: TriggerEventCard


class ListTriggerEventsResponse(TypedDict):
    data: List[TriggerEvent]


class ListNotificationsResponse(TypedDict):
    data: List[Notification]


class MarkNotificationsReadBody(TypedDict, total=False):
    ids: List[int]


class MarkNotificationsReadResponse(TypedDict):
    read: int


class DeleteNotificationResponse(TypedDict):
    deleted: int


class DeleteNotificationsBody(TypedDict):
    ids: List[int]


class DeleteNotificationsResponse(TypedDict):
    deleted: int


class PauseSchedulesBody(TypedDict, total=False):
    until: Optional[str]
    resume_policy: Literal['skip', 'backfill']


# POST /v1/schedules/pause — 200 response
PauseSchedulesResponse = Dict[str, Any]


class ResumeSchedulesBody(TypedDict, total=False):
    backfill: bool


# POST /v1/schedules/resume — 200 response
ResumeSchedulesResponse = Dict[str, Any]


# GET /v1/schedules/templates — 200 response
ListScheduleTemplatesResponse = Dict[str, Any]


class _RenderScheduleTemplateBodyRequired(TypedDict):
    template: str


class RenderScheduleTemplateBody(_RenderScheduleTemplateBodyRequired, total=False):
    params: Dict[str, Any]


# POST /v1/schedules/templates — 200 response
RenderScheduleTemplateResponse = Dict[str, Any]


class ListHeartbeatsResponse(TypedDict):
    heartbeats: List[HeartbeatMonitor]


class _CreateHeartbeatBodyRequired(TypedDict):
    name: str
    period_s: int


class CreateHeartbeatBody(_CreateHeartbeatBodyRequired, total=False):
    grace_s: int
    tz: str


# POST /v1/heartbeats — 201 response
CreateHeartbeatResponse = HeartbeatMonitor


class UpdateHeartbeatBody(TypedDict, total=False):
    name: str
    period_s: int
    grace_s: int
    paused: bool


# PATCH /v1/heartbeats/{id} — 200 response
UpdateHeartbeatResponse = HeartbeatMonitor


class ListSchedulesResponse(TypedDict):
    schedules: List[Schedule]


# POST /v1/schedules — request body
CreateScheduleBody = ScheduleInput


# POST /v1/schedules — 201 response
CreateScheduleResponse = Schedule


class PreviewScheduleBody(TypedDict, total=False):
    text: str
    trigger: Dict[str, Any]
    tz: str


class _PreviewScheduleResponseRequired(TypedDict):
    ok: bool


class PreviewScheduleResponse(_PreviewScheduleResponseRequired, total=False):
    reason: Literal['not_understood', 'invalid']
    trigger: Dict[str, Any]
    next_runs: List[str]
    dst_warning: bool


class ListScheduleAuditResponse(TypedDict):
    audit: List[ScheduleAuditEntry]


# GET /v1/schedules/{id} — 200 response
GetScheduleResponse = Schedule


# PATCH /v1/schedules/{id} — request body
UpdateScheduleBody = Dict[str, Any]


# PATCH /v1/schedules/{id} — 200 response
UpdateScheduleResponse = Schedule


class RunScheduleResponse(TypedDict):
    queued: bool


class ListScheduleRunsResponse(TypedDict):
    runs: List[ScheduleRun]


class ApproveScheduleCommandBody(TypedDict):
    command_hash: str


class ApproveScheduleCommandResponse(TypedDict):
    approved: bool
    device_id: str


class ListRecentScheduleRunsResponse(TypedDict):
    runs: List[ScheduleRun]


class DecideScheduleRunBody(TypedDict):
    approve: bool


# POST /v1/schedule-runs/{id}/decision — 200 response
DecideScheduleRunResponse = ScheduleRun


class _HeartbeatScheduleRunBodyRequired(TypedDict):
    attempt: int


class HeartbeatScheduleRunBody(_HeartbeatScheduleRunBodyRequired, total=False):
    log: str


class _ReportScheduleRunResultBodyRequired(TypedDict):
    attempt: int
    ok: bool


class ReportScheduleRunResultBody(_ReportScheduleRunResultBodyRequired, total=False):
    exit_code: Optional[int]
    error: Optional[str]
    log_tail: str
    cost_micro_usd: int
    session_id: Optional[str]
    timed_out: bool


# POST /v1/schedule-runs/{id}/result — 200 response
ReportScheduleRunResultResponse = ScheduleRun


class ListSchedulerHostsResponse(TypedDict):
    hosts: List[SchedulerHost]


class UpdateSchedulerHostBody(TypedDict, total=False):
    name: str
    tags: List[str]
    host_kind: Literal['pc', 'phone', 'watch', 'vm', 'cloud']
    os: Literal['windows', 'macos', 'linux', 'android', 'wearos', 'ios']
    arch: str


# PATCH /v1/scheduler/hosts/{id} — 200 response
UpdateSchedulerHostResponse = Dict[str, Any]


class ClaimScheduleRunResponse(TypedDict):
    run: ScheduleRun
    schedule: Schedule
    host_approved: bool


class ListPromptsResponse(TypedDict):
    data: List[Prompt]


# POST /v1/prompts — request body
CreatePromptBody = PromptCreate


# POST /v1/prompts — 200 response
CreatePromptResponse = PromptCreated


# POST /v1/prompts/bulk — request body
BulkPromptsBody = PromptBulkRequest


class BulkPromptsResponse(TypedDict):
    updated: int


# GET /v1/prompts/{id} — 200 response
GetPromptResponse = Prompt


# PATCH /v1/prompts/{id} — request body
UpdatePromptBody = PromptPatch


# PATCH /v1/prompts/{id} — 200 response
UpdatePromptResponse = Prompt


class DeletePromptResponse(TypedDict):
    deleted: int


class ListPromptEventsResponse(TypedDict):
    events: List[PromptEvent]


# POST /v1/prompts/{id}/instantiate — 201 response
InstantiatePromptResponse = Prompt


class LaunchPromptBody(TypedDict, total=False):
    device_id: str


class LaunchPromptResponse(TypedDict):
    session_id: str
    device_id: str
    pushed: bool


class VerifyPromptsBody(TypedDict, total=False):
    ids: List[str]
    all_active: bool


class _VerifyPromptsResponseResultsItemRequired(TypedDict):
    id: str
    ok: bool


class VerifyPromptsResponseResultsItem(_VerifyPromptsResponseResultsItemRequired, total=False):
    verdict: Literal['done', 'partial', 'not_started']
    error: str


class VerifyPromptsResponse(TypedDict):
    results: List[VerifyPromptsResponseResultsItem]


class _MatchPromptBodyRequired(TypedDict):
    ref: str


class MatchPromptBody(_MatchPromptBodyRequired, total=False):
    turn_id: str
    score: float
    sent_at: str
    answered: bool
    base_sha: str


class MatchPromptResponse(TypedDict):
    prompt: Prompt


class VerifyPromptBody(TypedDict, total=False):
    transcript: str
    diff: str
    head_sha: str
    files: List[str]


class VerifyPromptResponse(TypedDict):
    prompt: Prompt
    report: PromptReport


# POST /v1/hooks/{id} — request body
ReceiveTriggerHookBody = Dict[str, Any]


class ReceiveTriggerHookResponse(TypedDict):
    accepted: Literal[True]
    duplicate: bool
    event_id: int


class ListTranscriptsResponse(TypedDict):
    transcripts: List[Transcript]
    next_cursor: Optional[str]


# POST /v1/transcripts — request body
CreateTranscriptBody = TranscriptCreate


# POST /v1/transcripts — 201 response
CreateTranscriptResponse = Transcript


class GetTranscriptUsageResponse(TypedDict):
    used_ms: int
    cap_ms: int
    remaining_ms: int
    period_start: str


class SearchTranscriptsResponseHitsItem(TypedDict):
    transcript_id: str
    title: str
    start_ms: int
    end_ms: int
    speaker: str
    snippet: str


class SearchTranscriptsResponseTitlesItem(TypedDict):
    id: str
    title: str


class SearchTranscriptsResponse(TypedDict):
    hits: List[SearchTranscriptsResponseHitsItem]
    titles: List[SearchTranscriptsResponseTitlesItem]


class _AskTranscriptsBodyRequired(TypedDict):
    question: str


class AskTranscriptsBody(_AskTranscriptsBodyRequired, total=False):
    transcript_ids: List[str]


class AskTranscriptsResponseSourcesItem(TypedDict):
    n: int
    transcript_id: str
    title: str
    start_ms: int
    end_ms: int
    text: str


class AskTranscriptsResponse(TypedDict):
    answer: str
    sources: List[AskTranscriptsResponseSourcesItem]


# GET /v1/transcripts/{id} — 200 response
GetTranscriptResponse = TranscriptDetail


# PATCH /v1/transcripts/{id} — request body
UpdateTranscriptBody = TranscriptPatch


# PATCH /v1/transcripts/{id} — 200 response
UpdateTranscriptResponse = Transcript


# POST /v1/transcripts/{id}/finalize — request body
FinalizeTranscriptBody = TranscriptFinalize


# POST /v1/transcripts/{id}/finalize — 200 response
FinalizeTranscriptResponse = Transcript


# POST /v1/transcripts/{id}/retranscribe — 202 response
RetranscribeTranscriptResponse = Transcript


# POST /v1/transcripts/{id}/reanalyze — 202 response
ReanalyzeTranscriptResponse = Transcript


class _PublishTranscriptLiveBodyRequired(TypedDict):
    device: Literal['phone', 'wear', 'desktop']
    elapsed_ms: int


class PublishTranscriptLiveBody(_PublishTranscriptLiveBodyRequired, total=False):
    finals: str
    partial: str
    level: float
    paused: bool


class _AddTranscriptBookmarkBodyRequired(TypedDict):
    at_ms: int


class AddTranscriptBookmarkBody(_AddTranscriptBookmarkBodyRequired, total=False):
    label: str


# POST /v1/transcripts/{id}/bookmarks — 201 response
AddTranscriptBookmarkResponse = Bookmark


class _UpdateTranscriptSpeakerBodyRequired(TypedDict):
    name: str


class UpdateTranscriptSpeakerBody(_UpdateTranscriptSpeakerBodyRequired, total=False):
    is_owner: bool


class UpdateTranscriptSpeakerResponse(TypedDict):
    label: str
    name: str
    is_owner: bool


class UpdateTranscriptUtteranceBody(TypedDict):
    text: str


class UpdateTranscriptUtteranceResponse(TypedDict):
    seq: int
    text: str
    edited: bool


class GetTranscriptAudioResponseTracksItem(TypedDict):
    kind: TranscriptTrackKind
    mime: str
    url: str


class _GetTranscriptAudioResponseRequired(TypedDict):
    tracks: List[GetTranscriptAudioResponseTracksItem]


class GetTranscriptAudioResponse(_GetTranscriptAudioResponseRequired, total=False):
    expires_in: int


# GET /v1/transcripts/{id}/export — 200 response
ExportTranscriptResponse = TranscriptDetail


# POST /v1/transcripts/{id}/prompts/{index}/accept — 200 response
AcceptTranscriptPromptResponse = TranscriptPromptAccepted


class ListTranscriptSharesResponse(TypedDict):
    data: List[TranscriptShare]


# POST /v1/transcripts/{id}/shares — request body
CreateTranscriptShareBody = TranscriptShareCreateRequest


# POST /v1/transcripts/{id}/shares — 201 response
CreateTranscriptShareResponse = TranscriptShareCreated


# GET /v1/public/transcripts/{token} — 200 response
GetPublicTranscriptResponse = PublicTranscript


class ListTranscriptFoldersResponse(TypedDict):
    folders: List[TranscriptFolder]


# POST /v1/transcript-folders — request body
CreateTranscriptFolderBody = TranscriptFolderInput


# POST /v1/transcript-folders — 201 response
CreateTranscriptFolderResponse = TranscriptFolder


class UpdateTranscriptFolderBody(TypedDict, total=False):
    name: str
    color: str
    position: int


# PATCH /v1/transcript-folders/{id} — 200 response
UpdateTranscriptFolderResponse = TranscriptFolder


# GET /v1/transcript-vocabulary — 200 response
GetTranscriptVocabularyResponse = TranscriptVocabulary


# PUT /v1/transcript-vocabulary — request body
PutTranscriptVocabularyBody = TranscriptVocabulary


# PUT /v1/transcript-vocabulary — 200 response
PutTranscriptVocabularyResponse = TranscriptVocabulary


class ListListsResponse(TypedDict):
    lists: List[List]


# POST /v1/lists — request body
CreateListBody = ListCreateInput


class CreateListResponse(TypedDict):
    list: List


class ReorderListsBody(TypedDict):
    ids: List[str]


# PATCH /v1/lists/order — 200 response
ReorderListsResponse = ListOk


# PATCH /v1/lists/items/{itemId} — request body
UpdateListItemBody = ListItemPatchInput


class UpdateListItemResponse(TypedDict):
    item: ListItem


# DELETE /v1/lists/items/{itemId} — 200 response
DeleteListItemResponse = ListOk


# PATCH /v1/lists/{id} — request body
UpdateListBody = ListPatchInput


class UpdateListResponse(TypedDict):
    list: List


# DELETE /v1/lists/{id} — 200 response
DeleteListResponse = ListOk


class ListListItemsResponse(TypedDict):
    items: List[ListItem]


# POST /v1/lists/{id}/items — request body
AddListItemBody = ListItemInput


# POST /v1/lists/{id}/items — 200 response
AddListItemResponse = ListItemCreated


# POST /v1/share — request body
ShareToListBody = ShareRequest


# POST /v1/share — 200 response
ShareToListResponse = ShareResponse


# GET /v1/feed — 200 response
ListFeedResponse = FeedPage


# GET /v1/feed/me — 200 response
GetFeedMeResponse = FeedMe


# POST /v1/feed/posts — request body
CreateFeedPostBody = FeedPostCreateInput


class CreateFeedPostResponse(TypedDict):
    post: FeedPost


class CreateFeedPostResponse201(TypedDict):
    post: FeedPost


class GetFeedPostResponse(TypedDict):
    post: FeedPost


class DeleteFeedPostResponse(TypedDict):
    deleted: Literal[True]


# POST /v1/feed/posts/{id}/like — 200 response
LikeFeedPostResponse = FeedLikeState


# DELETE /v1/feed/posts/{id}/like — 200 response
UnlikeFeedPostResponse = FeedLikeState


# POST /v1/feed/posts/{id}/report — request body
ReportFeedPostBody = FeedReportInput


class ReportFeedPostResponse(TypedDict):
    reported: Literal[True]


# GET /v1/feed/posts/{id}/comments — 200 response
ListFeedCommentsResponse = FeedCommentPage


# POST /v1/feed/posts/{id}/comments — request body
CreateFeedCommentBody = FeedCommentCreateInput


# POST /v1/feed/posts/{id}/comments — 200 response
CreateFeedCommentResponse = FeedCommentCreated


class DeleteFeedCommentResponse(TypedDict):
    deleted: Literal[True]
    comment_count: int


# POST /v1/feed/comments/{id}/report — request body
ReportFeedCommentBody = FeedReportInput


class ReportFeedCommentResponse(TypedDict):
    reported: Literal[True]


class ListFeedBlocksResponse(TypedDict):
    blocks: List[FeedBlock]


class BlockFeedAuthorBody(TypedDict, total=False):
    post_id: str
    username: str


class BlockFeedAuthorResponse(TypedDict):
    blocked: Literal[True]
    username: Optional[str]


class UnblockFeedAuthorResponse(TypedDict):
    blocked: Literal[False]


# GET /v1/feed/users/{username} — 200 response
GetFeedUserResponse = FeedProfilePage


# GET /v1/usage — 200 response
GetUsageResponse = UsageReport


class ListKeysResponse(TypedDict):
    data: List[ApiKeyInfo]


class SetKeyTagsBody(TypedDict):
    tags: List[str]


class SetKeyTagsResponse(TypedDict):
    id: str
    tags: List[str]


# GET /v1/memory — 200 response
ListMemoriesResponse = MemoryList


class _CreateMemoryBodyRequired(TypedDict):
    content: str


class CreateMemoryBody(_CreateMemoryBodyRequired, total=False):
    importance: float


class CreateMemoryResponse(TypedDict):
    id: str


class DeleteAllMemoriesResponse(TypedDict):
    deleted: Dict[str, int]
    total: int


# GET /v1/memory/search — 200 response
SearchMemoriesResponse = MemorySearchResult


class DeleteMemoryResponse(TypedDict):
    deleted: bool


# GET /v1/sandboxes — 200 response
ListSandboxesResponse = SandboxList


# POST /v1/sandboxes — request body
CreateSandboxBody = SandboxCreate


# POST /v1/sandboxes — 201 response
CreateSandboxResponse = Sandbox


# GET /v1/environments/{id}/files — 200 response
ListEnvironmentFilesResponse = EnvironmentFileList


# GET /v1/environments/{id}/files/{path} — 200 response
GetEnvironmentFileResponse = EnvironmentFile


# PUT /v1/environments/{id}/files/{path} — 200 response
PutEnvironmentFileResponse = EnvironmentFileWritten


# POST /v1/environments/{id}/jobs — request body
StartEnvironmentJobBody = EnvironmentJobStartRequest


# POST /v1/environments/{id}/jobs — 201 response
StartEnvironmentJobResponse = EnvironmentJobStarted


# GET /v1/environments/{id}/jobs/{jobId} — 200 response
GetEnvironmentJobResponse = EnvironmentJob


# POST /v1/sandboxes/run — request body
RunSandboxBody = SandboxRunRequest


# POST /v1/sandboxes/run — 200 response
RunSandboxResponse = SandboxExecResult


# GET /v1/sandboxes/{id} — 200 response
GetSandboxResponse = Sandbox


# POST /v1/sandboxes/{id}/exec — request body
ExecSandboxBody = SandboxExecRequest


# POST /v1/sandboxes/{id}/exec — 200 response
ExecSandboxResponse = SandboxExecResult


# GET /v1/sandboxes/{id}/files — 200 response
ListSandboxFilesResponse = SandboxFileList


# PUT /v1/sandboxes/{id}/files/{path} — 200 response
PutSandboxFileResponse = SandboxFileWritten


# GET /v1/sandboxes/{id}/artifacts — 200 response
ListSandboxArtifactsResponse = SandboxArtifactList


class SnapshotSandboxBody(TypedDict, total=False):
    name: str


# POST /v1/sandboxes/{id}/snapshot — 200 response
SnapshotSandboxResponse = SandboxSnapshot


# POST /v1/sandboxes/{id}/run_code — request body
RunSandboxCodeBody = SandboxRunCodeRequest


# POST /v1/sandboxes/{id}/run_code — 200 response
RunSandboxCodeResponse = SandboxRunCodeResult


class ResetSandboxKernelResponse(TypedDict):
    ok: Literal[True]


# POST /v1/sandboxes/{id}/pause — 200 response
PauseSandboxResponse = Sandbox


# POST /v1/sandboxes/{id}/resume — 200 response
ResumeSandboxResponse = SandboxResumed


# POST /v1/sandboxes/{id}/fork — request body
ForkSandboxBody = SandboxForkRequest


# POST /v1/sandboxes/{id}/fork — 200 response
ForkSandboxResponse = SandboxForkResult


# POST /v1/sandboxes/{id}/preview — request body
PreviewSandboxBody = SandboxPreviewRequest


# POST /v1/sandboxes/{id}/preview — 200 response
PreviewSandboxResponse = SandboxPreview


# GET /v1/vault/account — 200 response
GetVaultAccountResponse = VaultAccount


class _PutVaultAccountBodyRequired(TypedDict):
    bundle: Dict[str, Any]


class PutVaultAccountBody(_PutVaultAccountBodyRequired, total=False):
    revision: int


# PUT /v1/vault/account — 200 response
PutVaultAccountResponse = Dict[str, Any]


class PatchVaultSettingsBodyGuards(TypedDict, total=False):
    """Any subset of `VaultGuards`; `hour_start` and `hour_end` are both null (off) or both set."""
    new_host: bool
    burst_max: int
    burst_window_s: int
    hour_start: Optional[int]
    hour_end: Optional[int]
    tz: str


class PatchVaultSettingsBody(TypedDict, total=False):
    default_tier: Literal['t1', 't2', 't3', 't4']
    guards: PatchVaultSettingsBodyGuards
    digest_opt_out: bool


class _PatchVaultSettingsResponseRequired(TypedDict):
    default_tier: Literal['t1', 't2', 't3', 't4']
    guards: VaultGuards


class PatchVaultSettingsResponse(_PatchVaultSettingsResponseRequired, total=False):
    digest_opt_out: bool


class LockVaultBody(TypedDict, total=False):
    via: Literal['hub', 'desktop', 'phone', 'wear', 'extension']


# POST /v1/vault/lock — 200 response
LockVaultResponse = VaultLockResult


# POST /v1/vault/unlock/challenge — 200 response
CreateVaultUnlockChallengeResponse = VaultUnlockChallenge


class _UnlockVaultBodyRequired(TypedDict):
    challenge: str
    proof: VaultApprovalProof


class UnlockVaultBody(_UnlockVaultBodyRequired, total=False):
    via: Literal['hub', 'desktop', 'phone', 'wear', 'extension']


class UnlockVaultResponse(TypedDict):
    unlocked: bool


class ListVaultLimitsResponse(TypedDict):
    limits: List[VaultItemLimits]


class SetVaultItemLimitsBody(TypedDict):
    per_minute: Optional[int]
    per_day: Optional[int]
    units_per_day: Optional[int]


class SetVaultItemLimitsResponse(TypedDict):
    limits: Optional[VaultItemLimits]


class ListVaultsResponse(TypedDict):
    vaults: List[VaultSummary]


class _CreateVaultBodyRequired(TypedDict):
    id: str
    encrypted_meta: str
    sealed_key: Dict[str, Any]


class CreateVaultBody(_CreateVaultBodyRequired, total=False):
    org_id: str


# POST /v1/vault/vaults — 201 response
CreateVaultResponse = Dict[str, Any]


# GET /v1/vault/items — 200 response
ListVaultItemsResponse = Dict[str, Any]


# PUT /v1/vault/items/{id} — request body
PutVaultItemBody = VaultItemEnvelope


# PUT /v1/vault/items/{id} — 200 response
PutVaultItemResponse = Dict[str, Any]


# DELETE /v1/vault/items/{id} — 200 response
DeleteVaultItemResponse = Dict[str, Any]


class SetVaultItemCloudBody(TypedDict):
    item: Optional[Dict[str, Any]]


# PUT /v1/vault/items/{id}/cloud — 200 response
SetVaultItemCloudResponse = Dict[str, Any]


# GET /v1/vault/rules — 200 response
ListVaultRulesResponse = Dict[str, Any]


class _CreateVaultRuleBodyRequired(TypedDict):
    tier: Literal['t0', 't1', 't2', 't3', 't4', 'deny']


class CreateVaultRuleBody(_CreateVaultRuleBodyRequired, total=False):
    item_id: Optional[str]
    agent: Optional[str]
    mode: Optional[Literal['env', 'http', 'autofill', 'ssh_sign', 'reveal']]


# POST /v1/vault/rules — 201 response
CreateVaultRuleResponse = Dict[str, Any]


# DELETE /v1/vault/rules/{id} — 200 response
DeleteVaultRuleResponse = Dict[str, Any]


# GET /v1/vault/grants — 200 response
ListVaultGrantsResponse = Dict[str, Any]


class RevokeVaultTaskGrantsBody(TypedDict):
    task: str


class RevokeVaultTaskGrantsResponse(TypedDict):
    revoked: int


# DELETE /v1/vault/grants/{id} — 200 response
RevokeVaultGrantResponse = Dict[str, Any]


# GET /v1/vault/events — 200 response
ListVaultEventsResponse = Dict[str, Any]


class _ListVaultApprovalsResponseApprovalsItemRequired(TypedDict):
    id: str


class ListVaultApprovalsResponseApprovalsItem(_ListVaultApprovalsResponseApprovalsItemRequired, total=False):
    quorum: Optional[VaultApprovalQuorum]


class ListVaultApprovalsResponse(TypedDict):
    approvals: List[ListVaultApprovalsResponseApprovalsItem]


# GET /v1/vault/approvals/{id} — 200 response
GetVaultApprovalResponse = Dict[str, Any]


class _DecideVaultApprovalBodyRequired(TypedDict):
    decision: Literal['approve', 'deny']
    scope: Literal['once', 'task', '1h', '8h']


class DecideVaultApprovalBody(_DecideVaultApprovalBodyRequired, total=False):
    signature: str
    proof: VaultApprovalProof
    step_up_acr: Optional[str]
    via: Literal['hub', 'desktop', 'phone', 'wear', 'extension', 'qr']
    match_number: str


# POST /v1/vault/approvals/{id}/decide — 200 response
DecideVaultApprovalResponse = Dict[str, Any]


# POST /v1/vault/devices/challenge — 200 response
CreateVaultDeviceChallengeResponse = VaultDeviceChallenge


class ListVaultDevicesResponse(TypedDict):
    devices: List[VaultDeviceKey]


# POST /v1/vault/devices — request body
EnrollVaultDeviceBody = VaultDeviceEnroll


class EnrollVaultDeviceResponse(TypedDict):
    device: VaultDeviceKey


class RenameVaultDeviceBody(TypedDict):
    name: str


class RenameVaultDeviceResponse(TypedDict):
    device: VaultDeviceKey


class RevokeVaultDeviceResponse(TypedDict):
    ok: bool


# GET /v1/vault/catalog — 200 response
VaultCatalogResponse = Dict[str, Any]


class _VaultUseBodyRequired(TypedDict):
    handle: str
    mode: Literal['env', 'http', 'autofill', 'ssh_sign', 'reveal']
    action: str


class VaultUseBody(_VaultUseBodyRequired, total=False):
    host: Optional[str]
    purpose: str
    provenance: Literal['user', 'agent', 'untrusted']
    chain: List[str]
    task: Optional[str]


# POST /v1/vault/use — 200 response
VaultUseResponse = VaultUseDecision


class _VaultHttpBodyRequired(TypedDict):
    handle: str
    url: str


class VaultHttpBody(_VaultHttpBodyRequired, total=False):
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD']
    headers: Dict[str, str]
    body: Optional[str]
    purpose: str
    provenance: Literal['user', 'agent', 'untrusted']
    chain: List[str]
    task: Optional[str]


# POST /v1/vault/http — 200 response
VaultHttpResponse = Dict[str, Any]


# POST /v1/vault/resolve/challenge — 200 response
CreateVaultResolveChallengeResponse = VaultResolveChallenge


class _VaultResolveBodyRequired(TypedDict):
    handles: List[str]
    action: str
    proof: VaultResolveProof


class VaultResolveBody(_VaultResolveBodyRequired, total=False):
    purpose: str
    provenance: Literal['user', 'agent', 'untrusted']
    chain: List[str]
    task: Optional[str]


# POST /v1/vault/resolve — 200 response
VaultResolveResponse = Dict[str, Any]


# POST /v1/vault/add-requests — request body
CreateVaultAddRequestBody = VaultAddRequestCreate


# POST /v1/vault/add-requests — 201 response
CreateVaultAddRequestResponse = VaultAddRequestCreated


class LookupVaultAddRequestBody(TypedDict):
    token: str


# POST /v1/vault/add-requests/lookup — 200 response
LookupVaultAddRequestResponse = VaultAddRequest


# GET /v1/vault/add-requests/{id} — 200 response
GetVaultAddRequestResponse = VaultAddRequestStatus


# DELETE /v1/vault/add-requests/{id} — 200 response
CancelVaultAddRequestResponse = VaultAddRequestStatus


class CompleteVaultAddRequestBody(TypedDict):
    item_id: str


# POST /v1/vault/add-requests/{id}/complete — 200 response
CompleteVaultAddRequestResponse = VaultAddRequestStatus


class ListVaultEmergencyResponse(TypedDict):
    outgoing: List[VaultEmergencyContact]
    incoming: List[VaultEmergencyContact]


class _InviteVaultEmergencyBodyRequired(TypedDict):
    email: str
    delay_hours: Literal[24, 48, 72]


class InviteVaultEmergencyBody(_InviteVaultEmergencyBodyRequired, total=False):
    vault_ids: List[str]


class InviteVaultEmergencyResponse(TypedDict):
    id: str


class AcceptVaultEmergencyBody(TypedDict):
    token: str


# POST /v1/vault/emergency/accept — 200 response
AcceptVaultEmergencyResponse = VaultEmergencyContact


class SealVaultEmergencyBodySealedKeysValue(TypedDict):
    alg: Literal['xwing-hkdf-xchacha20poly1305']
    ct: str
    wrapped: str


class SealVaultEmergencyBody(TypedDict):
    grantee_fingerprint: str
    sealed_keys: Dict[str, SealVaultEmergencyBodySealedKeysValue]


# PUT /v1/vault/emergency/{id}/seal — 200 response
SealVaultEmergencyResponse = VaultEmergencyContact


class UpdateVaultEmergencyBody(TypedDict, total=False):
    delay_hours: Literal[24, 48, 72]
    vault_ids: List[str]


# PATCH /v1/vault/emergency/{id} — 200 response
UpdateVaultEmergencyResponse = VaultEmergencyContact


class RevokeVaultEmergencyResponse(TypedDict):
    id: str
    status: Literal['revoked']


class RequestVaultEmergencyBody(TypedDict, total=False):
    reason: str


# POST /v1/vault/emergency/{id}/request — 200 response
RequestVaultEmergencyResponse = VaultEmergencyContact


# POST /v1/vault/emergency/{id}/deny — 200 response
DenyVaultEmergencyResponse = VaultEmergencyContact


# POST /v1/vault/emergency/{id}/approve — 200 response
ApproveVaultEmergencyResponse = VaultEmergencyContact


# GET /v1/vault/emergency/{id}/vault-data — 200 response
GetVaultEmergencyDataResponse = VaultEmergencyData


class ListVaultRotationResponse(TypedDict):
    items: List[VaultRotationEntry]


class SetVaultItemRotationBody(TypedDict, total=False):
    interval_days: Optional[int]
    provider: Optional[Literal['stripe', 'github_pat', 'openai', 'google_api_key', 'other']]
    snoozed_until: Optional[str]


class SetVaultItemRotationResponse(TypedDict):
    item_id: str
    interval_days: Optional[int]
    provider: Optional[Literal['stripe', 'github_pat', 'openai', 'google_api_key', 'other']]
    snoozed_until: Optional[str]


class MarkVaultItemRotatedResponse(TypedDict):
    item_id: str
    rotated_at: Optional[str]


class ReportVaultBreachesBodyResultsItem(TypedDict):
    item_id: str
    count: int


class ReportVaultBreachesBody(TypedDict):
    results: List[ReportVaultBreachesBodyResultsItem]


class ReportVaultBreachesResponse(TypedDict):
    recorded: int
    newly_breached: int


class ListVaultDeriversResponse(TypedDict):
    derivers: List[VaultDeriver]


class SetVaultItemDeriverBody(TypedDict):
    provider: Literal['aws_sts', 'gcp_sa', 'cloudflare', 'github_app']
    config: Dict[str, Any]
    max_ttl_s: int


class SetVaultItemDeriverResponse(TypedDict):
    deriver: VaultDeriver


class DeleteVaultItemDeriverResponse(TypedDict):
    deleted: bool


class _DeriveVaultCredentialBodyRequired(TypedDict):
    handle: str
    action: str
    proof: VaultResolveProof


class DeriveVaultCredentialBody(_DeriveVaultCredentialBodyRequired, total=False):
    purpose: str
    provenance: Literal['user', 'agent', 'untrusted']
    chain: List[str]
    task: Optional[str]
    ttl_s: int


# POST /v1/vault/derive — 200 response
DeriveVaultCredentialResponse = VaultDerived


class DeriveVaultCredentialResponse202(TypedDict):
    status: Literal['approval_required']
    tier: str
    approval_id: str
    match_number: Optional[str]
    reasons: List[str]


class ListVaultMembersResponse(TypedDict):
    members: List[VaultMember]


class ListVaultMemberCandidatesResponse(TypedDict):
    candidates: List[VaultMemberCandidate]


class AddVaultMemberBody(TypedDict):
    role: Literal['manager', 'editor', 'viewer']
    sealed_key: VaultSealedKey
    fingerprint: str


class AddVaultMemberResponse(TypedDict):
    member: VaultMember


class UpdateVaultMemberBody(TypedDict):
    role: Literal['manager', 'editor', 'viewer']


class UpdateVaultMemberResponse(TypedDict):
    member: VaultMember


class _RemoveVaultMemberResponseRequired(TypedDict):
    removed: bool


class RemoveVaultMemberResponse(_RemoveVaultMemberResponseRequired, total=False):
    rotation_needed_at: Optional[str]


class RotateVaultKeyBodyMembersItem(TypedDict):
    user_id: str
    sealed_key: VaultSealedKey


class RotateVaultKeyBodyItemsItem(TypedDict):
    id: str
    revision: int
    wrapped_key: str
    ciphertext: str


class RotateVaultKeyBody(TypedDict):
    key_epoch: int
    encrypted_meta: str
    members: List[RotateVaultKeyBodyMembersItem]
    items: List[RotateVaultKeyBodyItemsItem]


class RotateVaultKeyResponse(TypedDict):
    key_epoch: int


class _SetVaultQuorumBodyRequired(TypedDict):
    m: Optional[int]


class SetVaultQuorumBody(_SetVaultQuorumBodyRequired, total=False):
    scope: Literal['critical', 'high']


class SetVaultQuorumResponse(TypedDict):
    quorum: Optional[VaultQuorum]


class VoteVaultApprovalBody(TypedDict):
    decision: Literal['approve', 'deny']
    proof: VaultVoteProof


class VoteVaultApprovalResponse(TypedDict):
    status: Literal['pending', 'approved', 'denied']
    quorum: VaultApprovalQuorum


class _SimulateVaultPolicyBodyRulesItemRequired(TypedDict):
    tier: Literal['t0', 't1', 't2', 't3', 't4', 'deny']


class SimulateVaultPolicyBodyRulesItem(_SimulateVaultPolicyBodyRulesItemRequired, total=False):
    item_id: Optional[str]
    agent: Optional[str]
    mode: Optional[Literal['env', 'http', 'autofill', 'ssh_sign', 'reveal']]


class SimulateVaultPolicyBody(TypedDict, total=False):
    rules: List[SimulateVaultPolicyBodyRulesItem]
    default_tier: Literal['t1', 't2', 't3', 't4']
    since: str
    limit: int


# POST /v1/vault/policy/simulate — 200 response
SimulateVaultPolicyResponse = VaultSimulation


class ListVaultReceiptKeysResponse(TypedDict):
    keys: List[VaultReceiptKey]


class VqaListRunsResponse(TypedDict):
    runs: List[VqaRun]


# POST /v1/vqa/runs — request body
VqaCreateRunBody = VqaRunInput


class VqaCreateRunResponse(TypedDict):
    ok: Literal[True]


class VqaGetRunResponse(TypedDict):
    run: VqaRun
    counts: List[VqaFindingCount]


class VqaRecordCapturesBody(TypedDict):
    captures: List[VqaCaptureInput]


class VqaRecordCapturesResponse(TypedDict):
    ok: bool
    results: List[VqaCaptureResult]


# POST /v1/vqa/runs/{id}/finish — request body
VqaFinishRunBody = VqaRunFinish


class VqaFinishRunResponse(TypedDict):
    ok: bool
    run: VqaRun


class VqaListCapturesResponse(TypedDict):
    captures: List[VqaCapture]


class VqaListBaselinesResponse(TypedDict):
    baselines: List[Dict[str, Any]]


class VqaListFindingsResponse(TypedDict):
    findings: List[VqaFinding]


class VqaGetFindingResponse(TypedDict):
    finding: VqaFinding
    comments: List[Dict[str, Any]]
    capture: Optional[VqaCapture]


class VqaClaimFindingBody(TypedDict, total=False):
    agent: str


class VqaClaimFindingResponse(TypedDict):
    ok: bool
    finding: VqaFinding


class _VqaResolveFindingBodyRequired(TypedDict):
    status: Literal['fixed', 'wontfix', 'todo']


class VqaResolveFindingBody(_VqaResolveFindingBodyRequired, total=False):
    fixRef: str
    note: str


class VqaResolveFindingResponse(TypedDict):
    ok: bool
    finding: VqaFinding


class VqaCommentFindingBody(TypedDict):
    body: str


class VqaCommentFindingResponse(TypedDict):
    ok: bool
    comment: Dict[str, Any]


class _VqaRequestRecaptureBodyRequired(TypedDict):
    screens: List[str]


class VqaRequestRecaptureBody(_VqaRequestRecaptureBodyRequired, total=False):
    finding: str


class VqaRequestRecaptureResponse(TypedDict):
    id: int
    state: Literal['queued']


class VqaClaimRecapturesResponse(TypedDict):
    recaptures: List[Dict[str, Any]]


class VqaFinishRecaptureBody(TypedDict):
    runId: Optional[str]
    ok: bool


class VqaFinishRecaptureResponse(TypedDict):
    ok: Literal[True]


class VqaSummaryResponse(TypedDict):
    counts: List[VqaFindingCount]
    latestRun: Optional[VqaRun]


__all__ = [
    'AcceptTranscriptPromptResponse',
    'AcceptVaultEmergencyBody',
    'AcceptVaultEmergencyResponse',
    'AccountConsent',
    'AccountDeleteRequest',
    'AccountDeleteResponse',
    'AccountFeedbackRequest',
    'AccountGrowth',
    'AccountPatchRequest',
    'AccountPatchResponse',
    'AccountPhoneModel',
    'AccountPromo',
    'AccountReceipt',
    'AccountReceiptByUpstreamItem',
    'AccountReceiptWindow',
    'AccountReferral',
    'AccountView',
    'AccountViewFeatures',
    'AccountViewKey',
    'AccountViewPlan',
    'AccountViewUsage',
    'AccountViewUser',
    'AccountWallet',
    'AccountWalletHistoryEntry',
    'AdaptCreativeBody',
    'AdaptCreativeResponse',
    'AddEnvironmentMemberBody',
    'AddEnvironmentMemberResponse',
    'AddListItemBody',
    'AddListItemResponse',
    'AddOrgMemberBody',
    'AddOrgMemberResponse',
    'AddStudioVoiceSingingConsentBody',
    'AddStudioVoiceSingingConsentResponse',
    'AddTranscriptBookmarkBody',
    'AddTranscriptBookmarkResponse',
    'AddVaultMemberBody',
    'AddVaultMemberResponse',
    'AgentOutputKey',
    'AgentOutputVerifyRequest',
    'AgentOutputVerifyRequestSignature',
    'AgentOutputVerifyResult',
    'AgentRun',
    'AgentRunAccepted',
    'AgentRunCreateRequest',
    'AgentRunRequest',
    'AgentRunStats',
    'AgentRunStatus',
    'AgentRunStep',
    'AgentSyncResult',
    'AgentUsage',
    'AlignStudioLyricsBody',
    'AlignStudioLyricsResponse',
    'AlreadyHasEnvError',
    'AlreadyHasEnvErrorError',
    'AnonChallengeResponse',
    'AnonCreateSessionBody',
    'AnonCreateSessionBodyProof',
    'AnonCreateSessionBodyProofAppAttest',
    'AnonCreateSessionBodyProofPow',
    'AnonCreateSessionResponse',
    'AnonCreateSessionResponseLimits',
    'AnonImportBody',
    'AnonImportBodyMessagesItem',
    'AnonImportResponse',
    'AnonStatusResponse',
    'AnonStatusResponseLimits',
    'ApiKeyInfo',
    'AppendSessionEventsBody',
    'AppendSessionEventsResponse',
    'ApplyCreativeOpsBody',
    'ApplyCreativeOpsResponse',
    'ApproveScheduleCommandBody',
    'ApproveScheduleCommandResponse',
    'ApproveVaultEmergencyResponse',
    'ArchiveEnvironmentResponse',
    'AskTranscriptsBody',
    'AskTranscriptsResponse',
    'AskTranscriptsResponseSourcesItem',
    'AssetDeleted',
    'AssetDto',
    'AssetKind',
    'AssetList',
    'Billing',
    'BillingAutoTopup',
    'BillingInvoice',
    'BillingInvoiceList',
    'BillingLinks',
    'BillingPaymentMethod',
    'BillingPlan',
    'BillingSubscription',
    'BillingWallet',
    'BillingWalletEntry',
    'BlockFeedAuthorBody',
    'BlockFeedAuthorResponse',
    'Bookmark',
    'BrandKit',
    'BrandKitContrastPair',
    'BrandKitCreateRequest',
    'BrandKitCreateRequestTokens',
    'BrandKitDeleted',
    'BrandKitDtcg',
    'BrandKitExtractRequest',
    'BrandKitExtractRequestOption1',
    'BrandKitExtractRequestOption2',
    'BrandKitList',
    'BrandKitTokens',
    'BrandKitUpdateRequest',
    'BrandKitUpdateRequestTokens',
    'BuildCreativeBody',
    'BuildCreativeResponse',
    'BuildCreativeResponse202',
    'BulkPromptsBody',
    'BulkPromptsResponse',
    'CancelAgentRunResponse',
    'CancelStudioBatchResponse',
    'CancelVaultAddRequestResponse',
    'CaptionCreativeBody',
    'CaptionCreativeResponse',
    'CaptionPresetId',
    'CardDataResponse',
    'CardsEfacturaResponse',
    'CardsFxResponse',
    'CardsGeocodeResponse',
    'CardsPlacesResponse',
    'CardsProductBody',
    'CardsProductResponse',
    'CardsRenderBody',
    'CardsRenderBodyBlock',
    'CardsRouteResponse',
    'CardsTrackResponse',
    'CardsUnfurlBody',
    'CardsUnfurlResponse',
    'CardsWeatherResponse',
    'ChatCompletionRequest',
    'ChatCompletionRequestStreamOptions',
    'ChatCompletionResponse',
    'ChatCompletionResponseChoicesItem',
    'ChatContentPart',
    'ChatContentPartOption1',
    'ChatContentPartOption2',
    'ChatContentPartOption2ImageUrl',
    'ChatMessage',
    'ChatResponseFormat',
    'ChatResponseFormatJsonSchema',
    'ChatResponsesInputItem',
    'ChatResponsesInputItemContentOption2Item',
    'ChatResponsesOutputItem',
    'ChatResponsesOutputItemOption1',
    'ChatResponsesOutputItemOption2',
    'ChatResponsesOutputItemOption2ContentItem',
    'ChatResponsesRequest',
    'ChatResponsesRequestReasoning',
    'ChatResponsesResponse',
    'ChatResponsesTool',
    'ChatResponsesToolFunction',
    'ChatResponsesUsage',
    'ChatResponsesUsageInputTokensDetails',
    'ChatSandboxTool',
    'ChatTool',
    'ChatToolCall',
    'ChatToolCallFunction',
    'ChatToolFunction',
    'ChatUsage',
    'ChatUsagePromptTokensDetails',
    'CheckProvenanceResponse',
    'ChooseStudioMusicRoomBody',
    'ChooseStudioMusicRoomResponse',
    'ClaimScheduleRunResponse',
    'ClaimSessionLeaseBody',
    'ClaimSessionLeaseResponse',
    'CommentCreativeBody',
    'CommentCreativeResponse',
    'CompleteVaultAddRequestBody',
    'CompleteVaultAddRequestResponse',
    'ConfirmTaskBody',
    'ConfirmTaskResponse',
    'Control',
    'ControlOptionsItem',
    'CoreEmbeddingVector',
    'CoreEmbeddingsRequest',
    'CoreEmbeddingsResponse',
    'CoreEmbeddingsResponseUsage',
    'CoreHealth',
    'CoreHealthCheck',
    'CoreHealthReady',
    'CoreHealthReadyChecks',
    'CoreHealthReadyS1',
    'CoreImageAspectRatio',
    'CoreImageData',
    'CoreImageEditForm',
    'CoreImageEditRequest',
    'CoreImageInput',
    'CoreImageSize',
    'CoreImagesRequest',
    'CoreImagesResponse',
    'CoreModel',
    'CoreModelCapabilities',
    'CoreModelCodai',
    'CoreModelList',
    'CoreModelPricing',
    'CoreSpeechRequest',
    'CoreStatus',
    'CoreStatusProvider',
    'CoreTokenRequest',
    'CoreTokenResponse',
    'CoreTranscriptionRequest',
    'CoreTranscriptionResponse',
    'CreateAgentRunBody',
    'CreateAgentRunResponse',
    'CreateBrandKitBody',
    'CreateBrandKitResponse',
    'CreateChatCompletionBody',
    'CreateChatCompletionResponse',
    'CreateCreativeBody',
    'CreateCreativeFrameBody',
    'CreateCreativeFrameResponse',
    'CreateCreativeFrameResponse202',
    'CreateCreativeFromDocumentResponse',
    'CreateCreativeResponse',
    'CreateCreativeReviewThreadBody',
    'CreateCreativeReviewThreadResponse',
    'CreateCreativeShareBody',
    'CreateCreativeShareResponse',
    'CreateCreativeVariantsBody',
    'CreateCreativeVariantsResponse',
    'CreateDocumentBody',
    'CreateDocumentPreviewBody',
    'CreateDocumentPreviewResponse',
    'CreateDocumentResponse',
    'CreateDocumentVideoBody',
    'CreateDocumentVideoResponse',
    'CreateEmbeddingsBody',
    'CreateEmbeddingsResponse',
    'CreateEnvironmentBody',
    'CreateEnvironmentEnrollTokenResponse',
    'CreateEnvironmentResponse',
    'CreateEnvironmentTaskBody',
    'CreateEnvironmentTaskResponse',
    'CreateEphemeralTokenBody',
    'CreateEphemeralTokenResponse',
    'CreateFeedCommentBody',
    'CreateFeedCommentResponse',
    'CreateFeedPostBody',
    'CreateFeedPostResponse',
    'CreateFeedPostResponse201',
    'CreateHeartbeatBody',
    'CreateHeartbeatResponse',
    'CreateImageBody',
    'CreateImageResponse',
    'CreateListBody',
    'CreateListResponse',
    'CreateMemoryBody',
    'CreateMemoryResponse',
    'CreateMessageBody',
    'CreateMessageResponse',
    'CreateMusicBody',
    'CreateMusicResponse',
    'CreateMusicResponseDataItemOption1',
    'CreateMusicResponseDataItemOption2',
    'CreateOrgBody',
    'CreateOrgResponse',
    'CreateProjectBody',
    'CreateProjectResponse',
    'CreatePromptBody',
    'CreatePromptResponse',
    'CreatePublicReviewThreadBody',
    'CreatePublicReviewThreadResponse',
    'CreateRenderBody',
    'CreateRenderResponse',
    'CreateResearchBody',
    'CreateResearchResponse',
    'CreateResponseBody',
    'CreateResponseResponse',
    'CreateSandboxBody',
    'CreateSandboxResponse',
    'CreateScheduleBody',
    'CreateScheduleResponse',
    'CreateSessionBody',
    'CreateSessionResponse',
    'CreateSessionShareBody',
    'CreateSessionShareResponse',
    'CreateSpeechBody',
    'CreateSpeechResponse',
    'CreateSpeechStreamBody',
    'CreateStudioAbuseReportBody',
    'CreateStudioAbuseReportResponse',
    'CreateStudioBatchBody',
    'CreateStudioBatchResponse',
    'CreateStudioBatchResponse201',
    'CreateStudioMusicRoomBody',
    'CreateStudioMusicRoomResponse',
    'CreateStudioProductionBody',
    'CreateStudioProductionResponse',
    'CreateSystemOneBody',
    'CreateSystemOneResponse',
    'CreateTimelineBody',
    'CreateTimelineResponse',
    'CreateTranscriptBody',
    'CreateTranscriptFolderBody',
    'CreateTranscriptFolderResponse',
    'CreateTranscriptResponse',
    'CreateTranscriptShareBody',
    'CreateTranscriptShareResponse',
    'CreateTranscriptionBody',
    'CreateTranscriptionResponse',
    'CreateTriggerBody',
    'CreateTriggerResponse',
    'CreateVaultAddRequestBody',
    'CreateVaultAddRequestResponse',
    'CreateVaultBody',
    'CreateVaultDeviceChallengeResponse',
    'CreateVaultResolveChallengeResponse',
    'CreateVaultResponse',
    'CreateVaultRuleBody',
    'CreateVaultRuleResponse',
    'CreateVaultUnlockChallengeResponse',
    'CreateVideoBody',
    'CreateVideoBodyImage',
    'CreateVideoResponse',
    'CreateVoiceRevocationBody',
    'CreateVoiceRevocationResponse',
    'Creative',
    'CreativeAdaptFormat',
    'CreativeAdaptRequest',
    'CreativeAdaptResult',
    'CreativeAudio',
    'CreativeAudioClip',
    'CreativeAudioClipGeneration',
    'CreativeAudioFx',
    'CreativeAudioHumanLogItem',
    'CreativeAudioLyricsItem',
    'CreativeAudioMaster',
    'CreativeAudioMeta',
    'CreativeAudioMetaKey',
    'CreativeAudioRenderAccepted',
    'CreativeAudioRenderOutput',
    'CreativeAudioRenderRequest',
    'CreativeAudioSection',
    'CreativeAudioTrack',
    'CreativeAudioTrackAutomationItem',
    'CreativeAudioTrackAutomationItemPointsItem',
    'CreativeAudioTrackMidiClipsItem',
    'CreativeAudioTrackSendsItem',
    'CreativeBuildRequest',
    'CreativeCaptionsRequest',
    'CreativeCaptionsResult',
    'CreativeCast',
    'CreativeCommentRequest',
    'CreativeCommentResult',
    'CreativeCommentResultVersion',
    'CreativeCompiled',
    'CreativeControls',
    'CreativeCreateRequest',
    'CreativeDeleted',
    'CreativeDetail',
    'CreativeDoc',
    'CreativeError',
    'CreativeErrorError',
    'CreativeErrorErrorConflictsItem',
    'CreativeFindRequest',
    'CreativeFindRequestQueryOption2',
    'CreativeFindResult',
    'CreativeFocalPoint',
    'CreativeForkRequest',
    'CreativeFrame',
    'CreativeFrameJob',
    'CreativeFrameRequest',
    'CreativeFrames',
    'CreativeKind',
    'CreativeLintCode',
    'CreativeLintFixRequest',
    'CreativeLintFixResult',
    'CreativeLintFixResultAgent',
    'CreativeLintFixed',
    'CreativeLintIssue',
    'CreativeLintResult',
    'CreativeList',
    'CreativeListItem',
    'CreativeLocaleForkRequest',
    'CreativeLocaleForkResult',
    'CreativeLocaleForkResultForkOf',
    'CreativeLocaleForkResultVersion',
    'CreativeLocaleStatus',
    'CreativeLocaleStatusLocalesItem',
    'CreativeLocaleUnit',
    'CreativeLocalizeRequest',
    'CreativeLocalizeResult',
    'CreativeLocalizeResultLocalesItem',
    'CreativeOp',
    'CreativeOpsRequest',
    'CreativeOpsResult',
    'CreativeOutline',
    'CreativePagedBuildRequest',
    'CreativePrintLintIssue',
    'CreativeRegenerateNodeRequest',
    'CreativeRegenerateNodeResult',
    'CreativeRenderAccepted',
    'CreativeRenderCached',
    'CreativeRenderRequest',
    'CreativeRestyleRequest',
    'CreativeRevertRequest',
    'CreativeRevertResult',
    'CreativeSubtree',
    'CreativeSubtreeNodesItem',
    'CreativeSubtreeRequest',
    'CreativeTemplate',
    'CreativeTemplateDeleted',
    'CreativeTemplateList',
    'CreativeTemplateVar',
    'CreativeTranscriptCutRequest',
    'CreativeTranscriptCutRequestRemoveItem',
    'CreativeTranscriptCutResult',
    'CreativeTranscriptCutResultRemovedItem',
    'CreativeVariant',
    'CreativeVariantList',
    'CreativeVariantListVariantsItem',
    'CreativeVariantListVariantsItemRender',
    'CreativeVariantPickRequest',
    'CreativeVariantPickResult',
    'CreativeVariantPickResultVersion',
    'CreativeVariantsRequest',
    'CreativeVariantsResult',
    'CreativeVersion',
    'CreativeVersionList',
    'DecidePublicReviewBody',
    'DecidePublicReviewResponse',
    'DecideScheduleRunBody',
    'DecideScheduleRunResponse',
    'DecideVaultApprovalBody',
    'DecideVaultApprovalResponse',
    'DeckSlide',
    'DeckSlideOption1',
    'DeckSlideOption10',
    'DeckSlideOption10ItemsItem',
    'DeckSlideOption11',
    'DeckSlideOption2',
    'DeckSlideOption3',
    'DeckSlideOption4',
    'DeckSlideOption5',
    'DeckSlideOption6',
    'DeckSlideOption7',
    'DeckSlideOption8',
    'DeckSlideOption9',
    'DeckSlideOption9StatsItem',
    'DeckSpec',
    'DeleteAccountBody',
    'DeleteAccountResponse',
    'DeleteAllMemoriesResponse',
    'DeleteAssetResponse',
    'DeleteBrandKitResponse',
    'DeleteCreativeResponse',
    'DeleteCreativeTemplateResponse',
    'DeleteDeviceResponse',
    'DeleteFeedCommentResponse',
    'DeleteFeedPostResponse',
    'DeleteListItemResponse',
    'DeleteListResponse',
    'DeleteMemoryResponse',
    'DeleteNotificationResponse',
    'DeleteNotificationsBody',
    'DeleteNotificationsResponse',
    'DeleteProjectResponse',
    'DeletePromptResponse',
    'DeleteSessionResponse',
    'DeleteSessionShareResponse',
    'DeleteTriggerResponse',
    'DeleteVaultItemDeriverResponse',
    'DeleteVaultItemResponse',
    'DeleteVaultRuleResponse',
    'DenyVaultEmergencyResponse',
    'DeriveVaultCredentialBody',
    'DeriveVaultCredentialResponse',
    'DeriveVaultCredentialResponse202',
    'DestroyEnvironmentResponse',
    'DeviceListItem',
    'DevicePatch',
    'DevicePatched',
    'DevicePlatform',
    'DirectStudioMusicRoomBody',
    'DirectStudioMusicRoomResponse',
    'DispatchToDeviceBody',
    'DispatchToDeviceResponse',
    'DocBlock',
    'DocBlockOption1',
    'DocBlockOption2',
    'DocBlockOption3',
    'DocBlockOption4',
    'DocBlockOption5',
    'DocBlockOption6',
    'DocBlockOption7',
    'DocBlockOption8',
    'DocSpec',
    'Document',
    'DocumentBullet',
    'DocumentBulletOption2',
    'DocumentChart',
    'DocumentChartSeriesItem',
    'DocumentColumn',
    'DocumentCreateRequest',
    'DocumentImage',
    'DocumentPreview',
    'DocumentPreviewAccepted',
    'DocumentPreviewOption1',
    'DocumentPreviewPagesItem',
    'DocumentRichText',
    'DocumentRun',
    'DocumentTable',
    'DocumentTheme',
    'DocumentVideoAccepted',
    'DocumentVideoRequest',
    'DocumentVideoRequestNarrate',
    'EditImageBody',
    'EditImageResponse',
    'EnrollEnvironmentBody',
    'EnrollEnvironmentResponse',
    'EnrollVaultDeviceBody',
    'EnrollVaultDeviceResponse',
    'Environment',
    'EnvironmentAddMemberBody',
    'EnvironmentCreateBody',
    'EnvironmentDetail',
    'EnvironmentEnrollBody',
    'EnvironmentEnrollToken',
    'EnvironmentEnrolled',
    'EnvironmentEvent',
    'EnvironmentExecRequest',
    'EnvironmentExecResult',
    'EnvironmentFile',
    'EnvironmentFileList',
    'EnvironmentFileListEntriesItem',
    'EnvironmentFileWritten',
    'EnvironmentJob',
    'EnvironmentJobStartRequest',
    'EnvironmentJobStarted',
    'EnvironmentMember',
    'EnvironmentMemberCreated',
    'EnvironmentMemberRoleBody',
    'EnvironmentPatchBody',
    'EnvironmentPort',
    'EnvironmentPortBody',
    'EnvironmentProvider',
    'EnvironmentRole',
    'EnvironmentSecret',
    'EnvironmentSecretBody',
    'EnvironmentSecretSet',
    'EnvironmentSshCaKeys',
    'EnvironmentSshCert',
    'EnvironmentSshCertBody',
    'EnvironmentSshKeyBody',
    'EnvironmentState',
    'EnvironmentTask',
    'EnvironmentTaskCreate',
    'EnvironmentTaskOutputSignature',
    'EnvironmentTaskQueued',
    'EnvironmentTaskResult',
    'EnvironmentTransition',
    'Error',
    'ErrorError',
    'ExecEnvironmentBody',
    'ExecEnvironmentResponse',
    'ExecOnHostBody',
    'ExecOnHostResponse',
    'ExecSandboxBody',
    'ExecSandboxResponse',
    'ExportBrandKitDtcgResponse',
    'ExportCreativeFcpxmlResponse',
    'ExportCreativeLottieResponse',
    'ExportTranscriptResponse',
    'ExtractBrandKitBody',
    'ExtractBrandKitResponse',
    'FeedBlock',
    'FeedComment',
    'FeedCommentAuthor',
    'FeedCommentCreateInput',
    'FeedCommentCreated',
    'FeedCommentPage',
    'FeedLikeState',
    'FeedLinkPreview',
    'FeedMe',
    'FeedPage',
    'FeedPost',
    'FeedPostAuthor',
    'FeedPostCreateInput',
    'FeedPostImage',
    'FeedProfile',
    'FeedProfilePage',
    'FeedReportInput',
    'FinalizeTranscriptBody',
    'FinalizeTranscriptResponse',
    'FindCreativeNodesBody',
    'FindCreativeNodesResponse',
    'FixCreativeLintBody',
    'FixCreativeLintResponse',
    'ForkCreativeBody',
    'ForkCreativeLocaleBody',
    'ForkCreativeLocaleResponse',
    'ForkCreativeResponse',
    'ForkSandboxBody',
    'ForkSandboxResponse',
    'GetAccountResponse',
    'GetAgentOutputKeyResponse',
    'GetAgentRunResponse',
    'GetAgentRunStatsResponse',
    'GetAssetResponse',
    'GetBillingResponse',
    'GetBrandKitResponse',
    'GetCreativeCompiledResponse',
    'GetCreativeControlsResponse',
    'GetCreativeFrameJobResponse',
    'GetCreativeFrameJobResponse202',
    'GetCreativeLocalesResponse',
    'GetCreativeOutlineResponse',
    'GetCreativeResponse',
    'GetCreativeReviewResponse',
    'GetCreativeSubtreeBody',
    'GetCreativeSubtreeResponse',
    'GetCreativeTemplateResponse',
    'GetEnvironmentFileResponse',
    'GetEnvironmentJobResponse',
    'GetEnvironmentResponse',
    'GetEnvironmentSshCaResponse',
    'GetEnvironmentTaskResponse',
    'GetFeedMeResponse',
    'GetFeedPostResponse',
    'GetFeedUserResponse',
    'GetHealthReadyResponse',
    'GetHealthResponse',
    'GetMyDispatchInboxResponse',
    'GetPolicyResponse',
    'GetProjectResponse',
    'GetPromptResponse',
    'GetPublicStudioShareResponse',
    'GetPublicTranscriptResponse',
    'GetReceiptResponse',
    'GetReferralsResponse',
    'GetRenderResponse',
    'GetResearchResponse',
    'GetSandboxResponse',
    'GetScheduleResponse',
    'GetSessionResponse',
    'GetSettingsResponse',
    'GetStatusResponse',
    'GetStudioBatchResponse',
    'GetStudioExportResponse',
    'GetStudioMediaOpJobResponse',
    'GetStudioMusicRoomPluginResponse',
    'GetStudioMusicRoomQuotaResponse',
    'GetStudioMusicRoomResponse',
    'GetStudioProductionResponse',
    'GetStudioQuoteResponse',
    'GetTaskResponse',
    'GetTaskStatsResponse',
    'GetTranscriptAudioResponse',
    'GetTranscriptAudioResponseTracksItem',
    'GetTranscriptResponse',
    'GetTranscriptUsageResponse',
    'GetTranscriptVocabularyResponse',
    'GetUsageResponse',
    'GetVaultAccountResponse',
    'GetVaultAddRequestResponse',
    'GetVaultApprovalResponse',
    'GetVaultEmergencyDataResponse',
    'GetVideoResponse',
    'GetVideoResponseDataItemOption1',
    'HeartbeatMonitor',
    'HeartbeatScheduleRunBody',
    'HeartbeatSessionLeaseResponse',
    'HostExecBody',
    'HostExecRequest',
    'HostExecResponse',
    'HostExecResultBody',
    'HostIphoneArgs',
    'HostOp',
    'HostPresence',
    'ImportSfxResponse',
    'InstantiatePromptResponse',
    'InsufficientBalanceError',
    'InsufficientBalanceErrorError',
    'InsufficientFundsError',
    'InsufficientFundsErrorError',
    'InviteVaultEmergencyBody',
    'InviteVaultEmergencyResponse',
    'IssueMyEnvironmentSshCertBody',
    'IssueMyEnvironmentSshCertResponse',
    'LaunchPromptBody',
    'LaunchPromptResponse',
    'LikeFeedPostResponse',
    'LintCreativeBody',
    'LintCreativeResponse',
    'List',
    'ListAgentRunStepsResponse',
    'ListAssetsResponse',
    'ListBillingInvoicesResponse',
    'ListBrandKitsResponse',
    'ListCreateInput',
    'ListCreativeReviewThreadsResponse',
    'ListCreativeSharesResponse',
    'ListCreativeTemplatesResponse',
    'ListCreativeVariantsResponse',
    'ListCreativeVersionsResponse',
    'ListCreativesResponse',
    'ListDevicesResponse',
    'ListEnvironmentFilesResponse',
    'ListEnvironmentMembersResponse',
    'ListEnvironmentPortsResponse',
    'ListEnvironmentSecretsResponse',
    'ListEnvironmentTasksResponse',
    'ListEnvironmentsResponse',
    'ListFeedBlocksResponse',
    'ListFeedCommentsResponse',
    'ListFeedResponse',
    'ListHeartbeatsResponse',
    'ListHostsResponse',
    'ListItem',
    'ListItemCreated',
    'ListItemEnrichment',
    'ListItemEnrichmentPrice',
    'ListItemInput',
    'ListItemPatchInput',
    'ListItemSource',
    'ListKeysResponse',
    'ListListItemsResponse',
    'ListListsResponse',
    'ListMemoriesResponse',
    'ListModelsResponse',
    'ListNotificationsResponse',
    'ListOk',
    'ListOrgMembersResponse',
    'ListOrgsResponse',
    'ListPatchInput',
    'ListPendingTasksResponse',
    'ListPhoneModelsResponse',
    'ListProjectsResponse',
    'ListPromptEventsResponse',
    'ListPromptsResponse',
    'ListRecentScheduleRunsResponse',
    'ListRendersResponse',
    'ListSandboxArtifactsResponse',
    'ListSandboxFilesResponse',
    'ListSandboxesResponse',
    'ListScheduleAuditResponse',
    'ListScheduleRunsResponse',
    'ListScheduleTemplatesResponse',
    'ListSchedulerHostsResponse',
    'ListSchedulesResponse',
    'ListSessionControlsResponse',
    'ListSessionEventsResponse',
    'ListSessionSharesResponse',
    'ListSessionsResponse',
    'ListSessionsSharedWithMeResponse',
    'ListStudioBatchesResponse',
    'ListStudioMediaOpsResponse',
    'ListStudioMusicRoomPluginsResponse',
    'ListStudioMusicRoomsResponse',
    'ListTasksResponse',
    'ListTranscriptFoldersResponse',
    'ListTranscriptSharesResponse',
    'ListTranscriptsResponse',
    'ListTriggerEventsResponse',
    'ListTriggersResponse',
    'ListVaultApprovalsResponse',
    'ListVaultApprovalsResponseApprovalsItem',
    'ListVaultDeriversResponse',
    'ListVaultDevicesResponse',
    'ListVaultEmergencyResponse',
    'ListVaultEventsResponse',
    'ListVaultGrantsResponse',
    'ListVaultItemsResponse',
    'ListVaultLimitsResponse',
    'ListVaultMemberCandidatesResponse',
    'ListVaultMembersResponse',
    'ListVaultReceiptKeysResponse',
    'ListVaultRotationResponse',
    'ListVaultRulesResponse',
    'ListVaultsResponse',
    'LocalizeCreativeBody',
    'LocalizeCreativeResponse',
    'LockVaultBody',
    'LockVaultResponse',
    'LookupVaultAddRequestBody',
    'LookupVaultAddRequestResponse',
    'MarkNotificationsReadBody',
    'MarkNotificationsReadResponse',
    'MarkSessionControlAppliedResponse',
    'MarkVaultItemRotatedResponse',
    'MatchPromptBody',
    'MatchPromptResponse',
    'MediaOp',
    'MediaOpId',
    'MediaOpJob',
    'MediaOpList',
    'MediaOpQuote',
    'MediaOpRequest',
    'MediaOpResult',
    'MediaResponseFormat',
    'MemoryHit',
    'MemoryItem',
    'MemoryList',
    'MemorySearchResult',
    'MsgCacheControl',
    'MsgInputContentBlock',
    'MsgInputContentBlockOption1',
    'MsgInputContentBlockOption2',
    'MsgInputContentBlockOption2Source',
    'MsgInputContentBlockOption3',
    'MsgInputContentBlockOption4',
    'MsgInputContentBlockOption4ContentOption2Item',
    'MsgInputMessage',
    'MsgRequest',
    'MsgRequestMetadata',
    'MsgRequestSystemOption2Item',
    'MsgResponse',
    'MsgResponseContentBlock',
    'MsgResponseContentBlockOption1',
    'MsgResponseContentBlockOption2',
    'MsgThinkingConfig',
    'MsgThinkingConfigOption1',
    'MsgThinkingConfigOption2',
    'MsgTool',
    'MsgToolChoice',
    'MsgToolChoiceOption1',
    'MsgToolChoiceOption2',
    'MsgUsage',
    'MusicPlugin',
    'MusicPluginList',
    'MusicPluginParamsItem',
    'MusicPluginRefInput',
    'MusicPluginRefInputParamsItem',
    'MusicPluginValidation',
    'MusicRole',
    'MusicRoom',
    'MusicRoomChoose',
    'MusicRoomChooseOption1',
    'MusicRoomChooseOption2',
    'MusicRoomChooseOption3',
    'MusicRoomCopyRisk',
    'MusicRoomCopyRiskMatchesItem',
    'MusicRoomCreate',
    'MusicRoomCritique',
    'MusicRoomCritiqueIssuesItem',
    'MusicRoomDirect',
    'MusicRoomGate',
    'MusicRoomList',
    'MusicRoomListening',
    'MusicRoomListeningFeatures',
    'MusicRoomListeningFeaturesAesthetics',
    'MusicRoomListeningVerdict',
    'MusicRoomListeningVerdictImpressions',
    'MusicRoomListeningVerdictNotesItem',
    'MusicRoomPlanVariant',
    'MusicRoomPlanVariantInstrumentationItem',
    'MusicRoomPlanVariantSectionsItem',
    'MusicRoomQuota',
    'MusicRoomSetPlugin',
    'MusicRoomTeamItem',
    'MusicTrackMeta',
    'Notification',
    'OrgAddMemberBody',
    'OrgCreateShareBody',
    'OrgMember',
    'OrgRole',
    'OrgSessionRole',
    'OrgSessionShare',
    'OrgSharePrincipalType',
    'OrgSharedSession',
    'OrgWithRole',
    'OsGateEvent',
    'OsGateEventAccepted',
    'PanelControl',
    'PatchAccountBody',
    'PatchAccountResponse',
    'PatchSettingsBody',
    'PatchSettingsResponse',
    'PatchVaultSettingsBody',
    'PatchVaultSettingsBodyGuards',
    'PatchVaultSettingsResponse',
    'PauseSandboxResponse',
    'PauseSchedulesBody',
    'PauseSchedulesResponse',
    'PickCreativeVariantBody',
    'PickCreativeVariantResponse',
    'PlatformId',
    'PolicyResponse',
    'PolicyResponseOsGate',
    'PortProtocol',
    'PortVisibility',
    'PostHostExecResultBody',
    'PostHostExecResultResponse',
    'PreviewSandboxBody',
    'PreviewSandboxResponse',
    'PreviewScheduleBody',
    'PreviewScheduleResponse',
    'Project',
    'ProjectCreateBody',
    'ProjectIsolation',
    'ProjectPatchBody',
    'Prompt',
    'PromptBulkRequest',
    'PromptCreate',
    'PromptCreated',
    'PromptEvent',
    'PromptLaunchConfig',
    'PromptPatch',
    'PromptRecurrence',
    'PromptRecurrenceOption1',
    'PromptRecurrenceOption2',
    'PromptReport',
    'PromptSource',
    'PromptStatus',
    'ProvenanceCheckResult',
    'ProvenanceFinding',
    'PublicTranscript',
    'PublicTranscriptCite',
    'PublicTranscriptInsightsOption2',
    'PublicTranscriptInsightsOption2ActionsItem',
    'PublicTranscriptInsightsOption2KeyPointsItem',
    'PublicTranscriptSpeakersItem',
    'PublicTranscriptUtterancesItem',
    'PublishTranscriptLiveBody',
    'PutEnvironmentFileResponse',
    'PutSandboxFileResponse',
    'PutTranscriptVocabularyBody',
    'PutTranscriptVocabularyResponse',
    'PutVaultAccountBody',
    'PutVaultAccountResponse',
    'PutVaultItemBody',
    'PutVaultItemResponse',
    'QuoteStudioMediaOpBody',
    'QuoteStudioMediaOpResponse',
    'ReanalyzeTranscriptResponse',
    'ReceiveTriggerHookBody',
    'ReceiveTriggerHookResponse',
    'RecordOsGateEventBody',
    'RecordOsGateEventResponse',
    'ReferralRow',
    'ReferralsView',
    'RegenerateCreativeNodeBody',
    'RegenerateCreativeNodeResponse',
    'RegenerateRenderSceneBody',
    'RegenerateRenderSceneResponse',
    'RelayAttachedClient',
    'RelayEnvironmentStatus',
    'RelayEnvironmentStatusDaemonOption1',
    'RelayGitState',
    'RelayListeningPort',
    'RelayLock',
    'ReleaseSessionLeaseResponse',
    'RemixStudioShareBody',
    'RemixStudioShareResponse',
    'RemoveEnvironmentMemberResponse',
    'RemoveEnvironmentPortResponse',
    'RemoveEnvironmentSecretResponse',
    'RemoveOrgMemberResponse',
    'RemoveVaultMemberResponse',
    'RenameVaultDeviceBody',
    'RenameVaultDeviceResponse',
    'RenderCreativeBody',
    'RenderCreativeResponse',
    'RenderCreativeResponse202',
    'RenderScheduleTemplateBody',
    'RenderScheduleTemplateResponse',
    'ReopenCreativeReviewThreadResponse',
    'ReopenPublicReviewThreadBody',
    'ReopenPublicReviewThreadResponse',
    'ReorderListsBody',
    'ReorderListsResponse',
    'ReplyCreativeReviewThreadBody',
    'ReplyCreativeReviewThreadResponse',
    'ReplyPublicReviewThreadBody',
    'ReplyPublicReviewThreadResponse',
    'ReportFeedCommentBody',
    'ReportFeedCommentResponse',
    'ReportFeedPostBody',
    'ReportFeedPostResponse',
    'ReportScheduleRunResultBody',
    'ReportScheduleRunResultResponse',
    'ReportVaultBreachesBody',
    'ReportVaultBreachesBodyResultsItem',
    'ReportVaultBreachesResponse',
    'RequestVaultEmergencyBody',
    'RequestVaultEmergencyResponse',
    'ResearchJob',
    'ResearchJobError',
    'ResearchRequest',
    'ResearchSource',
    'ResetSandboxKernelResponse',
    'ResolveCreativeReviewThreadResponse',
    'ResolvePublicReviewThreadBody',
    'ResolvePublicReviewThreadResponse',
    'RestyleCreativeBody',
    'RestyleCreativeResponse',
    'ResumeSandboxResponse',
    'ResumeSchedulesBody',
    'ResumeSchedulesResponse',
    'RetranscribeTranscriptResponse',
    'RetrieveDocumentResponse',
    'RetrievePreviewResponse',
    'RetryStudioBatchResponse',
    'RevertCreativeBody',
    'RevertCreativeResponse',
    'RevokeSelfKeyResponse',
    'RevokeVaultDeviceResponse',
    'RevokeVaultEmergencyResponse',
    'RevokeVaultGrantResponse',
    'RevokeVaultTaskGrantsBody',
    'RevokeVaultTaskGrantsResponse',
    'RotateTriggerSecretResponse',
    'RotateVaultKeyBody',
    'RotateVaultKeyBodyItemsItem',
    'RotateVaultKeyBodyMembersItem',
    'RotateVaultKeyResponse',
    'RunAgentSyncBody',
    'RunAgentSyncResponse',
    'RunSandboxBody',
    'RunSandboxCodeBody',
    'RunSandboxCodeResponse',
    'RunSandboxResponse',
    'RunScheduleResponse',
    'RunStudioMediaOpBody',
    'RunStudioMediaOpResponse',
    'RunStudioMediaOpResponse202',
    'Sandbox',
    'SandboxArtifact',
    'SandboxArtifactList',
    'SandboxCreate',
    'SandboxEgress',
    'SandboxEgressOption1',
    'SandboxEgressOption2',
    'SandboxEgressOption3',
    'SandboxExecEvent',
    'SandboxExecEventOption1',
    'SandboxExecEventOption2',
    'SandboxExecEventOption3',
    'SandboxExecEventOption4',
    'SandboxExecEventOption5',
    'SandboxExecRequest',
    'SandboxExecResult',
    'SandboxFileList',
    'SandboxFileListEntriesItem',
    'SandboxFileWritten',
    'SandboxForkRequest',
    'SandboxForkResult',
    'SandboxForkResultDataItem',
    'SandboxForkResultDataItemError',
    'SandboxInput',
    'SandboxList',
    'SandboxPreview',
    'SandboxPreviewRequest',
    'SandboxReceipt',
    'SandboxReceiptOutputsItem',
    'SandboxResumed',
    'SandboxResumedUsage',
    'SandboxRunCodeRequest',
    'SandboxRunCodeResult',
    'SandboxRunCodeResultError',
    'SandboxRunRequest',
    'SandboxSnapshot',
    'SandboxUsage',
    'SaveCreativeTemplateBody',
    'SaveCreativeTemplateResponse',
    'SaveTemplateRequest',
    'SaveTemplateRequestVarsItem',
    'Schedule',
    'ScheduleApprovalsItem',
    'ScheduleAuditEntry',
    'ScheduleInput',
    'ScheduleRun',
    'SchedulerHost',
    'SealVaultEmergencyBody',
    'SealVaultEmergencyBodySealedKeysValue',
    'SealVaultEmergencyResponse',
    'SearchMemoriesResponse',
    'SearchSfxResponse',
    'SearchTranscriptsResponse',
    'SearchTranscriptsResponseHitsItem',
    'SearchTranscriptsResponseTitlesItem',
    'Session',
    'SessionControl',
    'SessionControlAccepted',
    'SessionControlKind',
    'SessionControlRequest',
    'SessionCreateRequest',
    'SessionDetail',
    'SessionDispatchInbox',
    'SessionDispatchInboxSessionsItem',
    'SessionDispatchRequest',
    'SessionDispatchResponse',
    'SessionEvent',
    'SessionEventsAppendRequest',
    'SessionEventsAppendResponse',
    'SessionEventsAppendResponseEventsItem',
    'SessionIncomingEvent',
    'SessionLease',
    'SessionLeaseClaimRequest',
    'SessionLeaseResponse',
    'SessionListItem',
    'SessionMember',
    'SessionMemberDevice',
    'SessionPatchRequest',
    'SessionPresence',
    'SessionRole',
    'SetEnvironmentMemberRoleBody',
    'SetEnvironmentMemberRoleResponse',
    'SetEnvironmentMemberRoleResponseMember',
    'SetEnvironmentPortBody',
    'SetEnvironmentPortResponse',
    'SetEnvironmentPortResponse201',
    'SetEnvironmentSecretBody',
    'SetEnvironmentSecretResponse',
    'SetKeyTagsBody',
    'SetKeyTagsResponse',
    'SetMyEnvironmentSshKeyBody',
    'SetMyEnvironmentSshKeyResponse',
    'SetStudioMusicRoomTrackPluginBody',
    'SetStudioMusicRoomTrackPluginResponse',
    'SetTriggerSecretBody',
    'SetTriggerSecretResponse',
    'SetVaultItemCloudBody',
    'SetVaultItemCloudResponse',
    'SetVaultItemDeriverBody',
    'SetVaultItemDeriverResponse',
    'SetVaultItemLimitsBody',
    'SetVaultItemLimitsResponse',
    'SetVaultItemRotationBody',
    'SetVaultItemRotationResponse',
    'SetVaultQuorumBody',
    'SetVaultQuorumResponse',
    'SettingsConflict',
    'SettingsConflictError',
    'SettingsPatchRequest',
    'SettingsResponse',
    'SfxCategory',
    'SfxDto',
    'SfxList',
    'ShareRequest',
    'ShareResponse',
    'ShareToListBody',
    'ShareToListResponse',
    'Sheet',
    'SheetCell',
    'SheetCellOption5',
    'SheetCellOption6',
    'SheetChartsItem',
    'SheetColumnsItem',
    'SheetConditionalItem',
    'SheetSpec',
    'SimulateVaultPolicyBody',
    'SimulateVaultPolicyBodyRulesItem',
    'SimulateVaultPolicyResponse',
    'SnapshotSandboxBody',
    'SnapshotSandboxResponse',
    'Speaker',
    'SpeechJson',
    'SpeechStreamEvent',
    'SpeechStreamRequest',
    'SpeechWord',
    'StartEnvironmentJobBody',
    'StartEnvironmentJobResponse',
    'StartEnvironmentResponse',
    'StopEnvironmentResponse',
    'StudioAbuseReport',
    'StudioAbuseReportRequest',
    'StudioAudioRender',
    'StudioAudioRenderDataItem',
    'StudioBatch',
    'StudioBatchColumn',
    'StudioBatchColumns',
    'StudioBatchCreateRequest',
    'StudioBatchCreateRequestLocalize',
    'StudioBatchCreateRequestSheet',
    'StudioBatchCreateRequestSource',
    'StudioBatchDetail',
    'StudioBatchDryRun',
    'StudioBatchDryRunEstimate',
    'StudioBatchDryRunPreviewItem',
    'StudioBatchList',
    'StudioBatchRow',
    'StudioBatchRowError',
    'StudioBatchRowStatus',
    'StudioBatchSource',
    'StudioBatchStatus',
    'StudioBatchZip',
    'StudioCreativeBuild',
    'StudioCreativeFromDocument',
    'StudioCreativeFromDocumentVersion',
    'StudioCreativePagedBuild',
    'StudioCreativePagedBuildPrint',
    'StudioExport',
    'StudioExportError',
    'StudioLyrics',
    'StudioLyricsAlignRequest',
    'StudioLyricsAlignment',
    'StudioLyricsAlignmentLinesItem',
    'StudioLyricsLine',
    'StudioLyricsReport',
    'StudioLyricsRequest',
    'StudioLyricsSectionKind',
    'StudioLyricsSectionsItem',
    'StudioNarrationDefaults',
    'StudioPostCopy',
    'StudioPostCopyAltItem',
    'StudioPostCopyFixesItem',
    'StudioPostCopyPlatformsItem',
    'StudioPostCopyPlatformsItemLimits',
    'StudioPostCopyRequest',
    'StudioProduction',
    'StudioProductionCreate',
    'StudioProductionKind',
    'StudioProductionOutput',
    'StudioProductionQa',
    'StudioPublicDecisionRequest',
    'StudioPublicNameRequest',
    'StudioPublicReplyRequest',
    'StudioPublicReview',
    'StudioPublicShare',
    'StudioPublicShareCompiledOption2',
    'StudioPublicShareFormatsItem',
    'StudioPublicThreadCreateRequest',
    'StudioQuote',
    'StudioRemixRequest',
    'StudioRemixResult',
    'StudioRemixResultRemixedFrom',
    'StudioRemixResultVersion',
    'StudioRender',
    'StudioRenderAccepted',
    'StudioRenderAiLabel',
    'StudioRenderAspectRatio',
    'StudioRenderCreate',
    'StudioRenderList',
    'StudioRenderListItem',
    'StudioRenderQa',
    'StudioRenderQuality',
    'StudioRenderStatus',
    'StudioReview',
    'StudioReviewComment',
    'StudioReviewCommentAuthor',
    'StudioReviewReplyRequest',
    'StudioReviewStatus',
    'StudioReviewThread',
    'StudioReviewThreadCreateRequest',
    'StudioReviewThreadList',
    'StudioReviewThreads',
    'StudioReviewUpdateRequest',
    'StudioSceneNarration',
    'StudioSceneRegenerate',
    'StudioSceneRegenerateAccepted',
    'StudioSceneRegenerateNarrationOption1',
    'StudioSceneRegenerateNarrationOption2',
    'StudioSceneRegenerateVisualOption1',
    'StudioSceneRegenerateVisualOption2',
    'StudioShare',
    'StudioShareCreateRequest',
    'StudioShareCreated',
    'StudioShareKind',
    'StudioShareList',
    'StudioTimeline',
    'StudioTimelineAccepted',
    'StudioTimelineCreate',
    'StudioTimelineMusic',
    'StudioTimelineScene',
    'StudioTimelineSceneInput',
    'StudioTimelineSceneInputNarration',
    'StudioVoice',
    'StudioVoiceRevocation',
    'StudioVoiceRevocationRequest',
    'StudioVoiceSinging',
    'StudioVoiceSingingConsentRequest',
    'SubmitFeedbackBody',
    'SubmitFeedbackResponse',
    'SubmitSessionControlBody',
    'SubmitSessionControlResponse',
    'SystemOneAnswer',
    'SystemOneQuestion',
    'SystemOneRequest',
    'SystemOneRequestItemsItem',
    'SystemOneResponse',
    'SystemOneResponseItemsItem',
    'SystemOneResponseUsage',
    'Task',
    'TaskConfirmRequest',
    'TaskConfirmResponse',
    'TaskEvidenceKind',
    'TaskNotConfirmableError',
    'TaskNotConfirmableErrorError',
    'TaskOutcome',
    'TaskStats',
    'TaskSurface',
    'TestTriggerBody',
    'TestTriggerResponse',
    'ToolFetchRequest',
    'ToolFetchResponse',
    'ToolRulesRefusedError',
    'ToolRulesRefusedErrorError',
    'ToolRulesRefusedErrorErrorDetails',
    'ToolSearchGoogleResponse',
    'ToolSearchGoogleResponseSourcesItem',
    'ToolSearchProviderResponse',
    'ToolSearchProviderResponseResultsItem',
    'ToolSearchRequest',
    'ToolSearchResponse',
    'ToolSearchResponseFallback',
    'ToolSearchResponseGoogle',
    'ToolSearchResponseGoogleSourcesItem',
    'ToolSearchResponseRerank',
    'ToolSearchResult',
    'ToolsFetchBody',
    'ToolsFetchResponse',
    'ToolsGroundBody',
    'ToolsGroundResponse',
    'ToolsSearchBody',
    'ToolsSearchResponse',
    'Transcript',
    'TranscriptCitation',
    'TranscriptCitedText',
    'TranscriptCreate',
    'TranscriptCutCreativeBody',
    'TranscriptCutCreativeResponse',
    'TranscriptDetail',
    'TranscriptDetailProcessingOption1',
    'TranscriptDetailTracksItem',
    'TranscriptFinalize',
    'TranscriptFinalizeBookmarksItem',
    'TranscriptFinalizeUploadsItem',
    'TranscriptFolder',
    'TranscriptFolderInput',
    'TranscriptInsights',
    'TranscriptInsightsActionsItem',
    'TranscriptInsightsPromptsItem',
    'TranscriptPatch',
    'TranscriptPromptAccepted',
    'TranscriptShare',
    'TranscriptShareCreateRequest',
    'TranscriptShareCreated',
    'TranscriptStatus',
    'TranscriptTemplate',
    'TranscriptTrackKind',
    'TranscriptVocabulary',
    'TranscriptsSettings',
    'Trigger',
    'TriggerCreate',
    'TriggerDecision',
    'TriggerEvent',
    'TriggerEventCard',
    'TriggerPatch',
    'TriggerPolicy',
    'TriggerPolicyQuietHours',
    'TriggerPolicySmart',
    'TriggerPolicyTarget',
    'TriggerResolvedMode',
    'TriggerSeverity',
    'TriggerSource',
    'TriggerTestFire',
    'TriggerWithSecret',
    'UnblockFeedAuthorResponse',
    'UnlikeFeedPostResponse',
    'UnlockVaultBody',
    'UnlockVaultResponse',
    'UpdateBrandKitBody',
    'UpdateBrandKitResponse',
    'UpdateCreativeReviewBody',
    'UpdateCreativeReviewResponse',
    'UpdateDeviceBody',
    'UpdateDeviceResponse',
    'UpdateEnvironmentBody',
    'UpdateEnvironmentResponse',
    'UpdateHeartbeatBody',
    'UpdateHeartbeatResponse',
    'UpdateListBody',
    'UpdateListItemBody',
    'UpdateListItemResponse',
    'UpdateListResponse',
    'UpdateProjectBody',
    'UpdateProjectResponse',
    'UpdatePromptBody',
    'UpdatePromptResponse',
    'UpdateScheduleBody',
    'UpdateScheduleResponse',
    'UpdateSchedulerHostBody',
    'UpdateSchedulerHostResponse',
    'UpdateSessionBody',
    'UpdateSessionResponse',
    'UpdateTranscriptBody',
    'UpdateTranscriptFolderBody',
    'UpdateTranscriptFolderResponse',
    'UpdateTranscriptResponse',
    'UpdateTranscriptSpeakerBody',
    'UpdateTranscriptSpeakerResponse',
    'UpdateTranscriptUtteranceBody',
    'UpdateTranscriptUtteranceResponse',
    'UpdateTriggerBody',
    'UpdateTriggerResponse',
    'UpdateVaultEmergencyBody',
    'UpdateVaultEmergencyResponse',
    'UpdateVaultMemberBody',
    'UpdateVaultMemberResponse',
    'UsageReport',
    'UsageRow',
    'UserSettings',
    'Utterance',
    'UtteranceWordsItem',
    'VaultAccount',
    'VaultAddRequest',
    'VaultAddRequestCreate',
    'VaultAddRequestCreated',
    'VaultAddRequestStatus',
    'VaultApprovalProof',
    'VaultApprovalProofOption1',
    'VaultApprovalProofOption2',
    'VaultApprovalQuorum',
    'VaultCatalogResponse',
    'VaultDerived',
    'VaultDeriver',
    'VaultDeviceChallenge',
    'VaultDeviceEnroll',
    'VaultDeviceEnrollAttestationOption1',
    'VaultDeviceEnrollAttestationOption2',
    'VaultDeviceEnrollAttestationOption2Tpm',
    'VaultDeviceKey',
    'VaultEmergencyContact',
    'VaultEmergencyData',
    'VaultEmergencyDataItemsItem',
    'VaultEmergencyDataVaultsItem',
    'VaultGuards',
    'VaultHttpBody',
    'VaultHttpResponse',
    'VaultItemEnvelope',
    'VaultItemLimits',
    'VaultLockResult',
    'VaultMember',
    'VaultMemberCandidate',
    'VaultMemberCandidatePublicKeys',
    'VaultQuorum',
    'VaultReceiptKey',
    'VaultResolveBody',
    'VaultResolveChallenge',
    'VaultResolveProof',
    'VaultResolveResponse',
    'VaultRotationEntry',
    'VaultSealedKey',
    'VaultSimulation',
    'VaultSimulationRow',
    'VaultSummary',
    'VaultUnlockChallenge',
    'VaultUseBody',
    'VaultUseDecision',
    'VaultUseResponse',
    'VaultVoteProof',
    'VaultVoteProofOption1',
    'VaultVoteProofOption2',
    'VerifyAgentOutputBody',
    'VerifyAgentOutputResponse',
    'VerifyPromptBody',
    'VerifyPromptResponse',
    'VerifyPromptsBody',
    'VerifyPromptsResponse',
    'VerifyPromptsResponseResultsItem',
    'VoteVaultApprovalBody',
    'VoteVaultApprovalResponse',
    'VqaCapture',
    'VqaCaptureInput',
    'VqaCaptureInputBlobs',
    'VqaCaptureInputDiff',
    'VqaCaptureResult',
    'VqaCaptureUrls',
    'VqaClaimFindingBody',
    'VqaClaimFindingResponse',
    'VqaClaimRecapturesResponse',
    'VqaCommentFindingBody',
    'VqaCommentFindingResponse',
    'VqaCreateRunBody',
    'VqaCreateRunResponse',
    'VqaFinding',
    'VqaFindingCount',
    'VqaFinishRecaptureBody',
    'VqaFinishRecaptureResponse',
    'VqaFinishRunBody',
    'VqaFinishRunResponse',
    'VqaGetFindingResponse',
    'VqaGetRunResponse',
    'VqaIssueInput',
    'VqaListBaselinesResponse',
    'VqaListCapturesResponse',
    'VqaListFindingsResponse',
    'VqaListRunsResponse',
    'VqaRecordCapturesBody',
    'VqaRecordCapturesResponse',
    'VqaRequestRecaptureBody',
    'VqaRequestRecaptureResponse',
    'VqaResolveFindingBody',
    'VqaResolveFindingResponse',
    'VqaRun',
    'VqaRunFinish',
    'VqaRunInput',
    'VqaSummaryResponse',
    'WriteCreativePostCopyBody',
    'WriteCreativePostCopyResponse',
    'WriteStudioLyricsBody',
    'WriteStudioLyricsResponse',
    'ZipStudioBatchResponse',
]
