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

class _ErrorErrorRequired(TypedDict):
    message: str
    type: Literal['invalid_request_error', 'subscription_required', 'rate_limit_error', 'upstream_error', 'server_error']
    code: Literal['bad_request', 'invalid_api_key', 'subscription_inactive', 'forbidden', 'not_found', 'payload_too_large', 'rate_limit_exceeded', 'quota_exceeded', 'upstream_error', 'internal_error', 'not_a_member', 'lease_held', 'seq_conflict', 'host_offline', 'host_timeout', 'rules_refused', 'search_unavailable', 'task_not_confirmable']


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
    tools: List[ChatTool]
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
    model: Literal['codai-tts', 'tts-1', 'tts', 'codai-tts-expressive', 'gpt-4o-mini-tts']
    voice: str
    response_format: str
    speed: float
    instructions: str


class _CoreTokenRequestRequired(TypedDict):
    scope: str


class CoreTokenRequest(_CoreTokenRequestRequired, total=False):
    """Ephemeral token request"""
    ttl_seconds: int


class CoreTokenResponse(TypedDict):
    """Ephemeral token"""
    token: str
    expires_at: str
    scope: Literal['realtime', 'audio', 'embeddings']


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
    freshness: Literal['day', 'week', 'month']
    country: str
    lang: str


class _ToolSearchResultRequired(TypedDict):
    title: str
    url: str
    snippet: str
    source: Literal['index', 'bnr', 'anm', 'fuel', 'osm', 'ins', 'wikipedia', 'github', 'stackexchange', 'docs', 'news', 'sitecc', 'commoncrawl', 'ddg', 'direct', 'crawler']
    verified: Literal[True]


class ToolSearchResult(_ToolSearchResultRequired, total=False):
    """One result from codai-search; the snippet was confirmed on the fetched page."""
    page_age: str


class ToolSearchResponseRerank(TypedDict):
    """Present when the cross-encoder reranker ran."""
    model: str
    ms: int
    n: int


class _ToolSearchResponseRequired(TypedDict):
    results: List[ToolSearchResult]
    provider: Literal['codai']
    took_ms: int
    cached: bool
    coverage: float
    sources_tried: List[str]
    degraded: List[str]
    intent: Literal['currency', 'weather', 'encyclopedic', 'code', 'docs', 'site', 'news', 'price', 'local', 'fuel', 'inflation', 'local_poi', 'general']


class ToolSearchResponse(_ToolSearchResponseRequired, total=False):
    """The codai-search JSON, returned verbatim by the gateway."""
    rerank: ToolSearchResponseRerank


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


# Kind of control a non-executor can send to the executor.
SessionControlKind = Literal['send', 'answer', 'approve', 'deny', 'cancel', 'steer', 'inject']


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
    role: SessionRole
    members: List[SessionMember]
    lease: Optional[SessionLease]
    presence: List[SessionPresence]


class SessionCreateRequest(TypedDict, total=False):
    session_key: str
    title: str
    e2e: bool


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


class SessionControl(TypedDict):
    """SessionControl"""
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


class _SessionDispatchRequestRequired(TypedDict):
    device_id: str
    text: str


class SessionDispatchRequest(_SessionDispatchRequestRequired, total=False):
    turn_id: str
    control_id: str


class _SessionDispatchResponseRequired(TypedDict):
    control_id: str
    seq: Optional[int]
    target_device_id: str
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


class DeviceListItem(TypedDict):
    """One registered device. Keys are camelCase for the timestamps, snake_case for `has_push_token` — exactly as the…"""
    id: str
    name: str
    platform: DevicePlatform
    capabilities: List[str]
    has_push_token: bool
    lastSeenAt: str
    createdAt: str


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


# Operation vocabulary the desktop host implements.
HostOp = Literal['shell', 'fs_read', 'fs_write', 'fs_list', 'fs_roots', 'info']


class HostPresence(TypedDict):
    """A device currently connected to `GET /v1/hosts/stream`."""
    device_id: str
    name: Optional[str]
    platform: Optional[str]
    os: Optional[str]
    hostname: Optional[str]
    roots: List[str]
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


class AccountConsent(TypedDict):
    """Accepted terms/privacy versions for one client surface."""
    surface: Literal['desktop', 'phone', 'console']
    terms_version: str
    privacy_version: str
    accepted_at: str


class AccountWalletHistoryEntry(TypedDict):
    """One line of the EUR wallet ledger (last 180 days, newest first, max 20)."""
    id: str
    delta_eur: float
    source: Literal['welcome_grant', 'referral_referee_grant', 'referral_referrer_grant', 'promo_grant', 'admin_grant', 'admin_revoke', 'purchase', 'usage_charge', 'expiry', 'auto_topup', 'task_refund', 'task_success_charge', 'credit_migration', 'compute_charge']
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
    referral_result: Optional[Literal['window_closed', 'none', 'invalid_code', 'self', 'already_referred', 'flagged', 'granted', 'cap_reached']]


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


# POST /v1/audio/transcriptions — request body
CreateTranscriptionBody = CoreTranscriptionRequest


# POST /v1/audio/transcriptions — 200 response
CreateTranscriptionResponse = CoreTranscriptionResponse


# POST /v1/audio/speech — request body
CreateSpeechBody = CoreSpeechRequest


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
ToolsSearchResponse = Union[ToolSearchResponse, ToolSearchProviderResponse]


# POST /v1/tools/fetch — request body
ToolsFetchBody = ToolFetchRequest


# POST /v1/tools/fetch — 200 response
ToolsFetchResponse = ToolFetchResponse


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


# GET /v1/account — 200 response
GetAccountResponse = AccountView


# PATCH /v1/account — request body
PatchAccountBody = AccountPatchRequest


# PATCH /v1/account — 200 response
PatchAccountResponse = AccountPatchResponse


# GET /v1/receipt — 200 response
GetReceiptResponse = AccountReceipt


# POST /v1/feedback — request body
SubmitFeedbackBody = AccountFeedbackRequest


class SubmitFeedbackResponse(TypedDict):
    ok: Literal[True]
    event_id: str


class ListPhoneModelsResponse(TypedDict):
    models: List[AccountPhoneModel]


__all__ = [
    'AccountConsent',
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
    'AddOrgMemberBody',
    'AddOrgMemberResponse',
    'AgentRun',
    'AgentRunAccepted',
    'AgentRunCreateRequest',
    'AgentRunRequest',
    'AgentRunStats',
    'AgentRunStatus',
    'AgentRunStep',
    'AgentSyncResult',
    'AgentUsage',
    'AppendSessionEventsBody',
    'AppendSessionEventsResponse',
    'CancelAgentRunResponse',
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
    'ChatTool',
    'ChatToolCall',
    'ChatToolCallFunction',
    'ChatToolFunction',
    'ChatUsage',
    'ChatUsagePromptTokensDetails',
    'ClaimSessionLeaseBody',
    'ClaimSessionLeaseResponse',
    'ConfirmTaskBody',
    'ConfirmTaskResponse',
    'CoreEmbeddingVector',
    'CoreEmbeddingsRequest',
    'CoreEmbeddingsResponse',
    'CoreEmbeddingsResponseUsage',
    'CoreHealth',
    'CoreHealthCheck',
    'CoreHealthReady',
    'CoreHealthReadyChecks',
    'CoreHealthReadyS1',
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
    'CreateChatCompletionBody',
    'CreateChatCompletionResponse',
    'CreateEmbeddingsBody',
    'CreateEmbeddingsResponse',
    'CreateEphemeralTokenBody',
    'CreateEphemeralTokenResponse',
    'CreateMessageBody',
    'CreateMessageResponse',
    'CreateOrgBody',
    'CreateOrgResponse',
    'CreateResponseBody',
    'CreateResponseResponse',
    'CreateSessionBody',
    'CreateSessionResponse',
    'CreateSessionShareBody',
    'CreateSessionShareResponse',
    'CreateSpeechBody',
    'CreateTranscriptionBody',
    'CreateTranscriptionResponse',
    'DeleteDeviceResponse',
    'DeleteSessionResponse',
    'DeleteSessionShareResponse',
    'DeviceListItem',
    'DevicePatch',
    'DevicePatched',
    'DevicePlatform',
    'DispatchToDeviceBody',
    'DispatchToDeviceResponse',
    'Error',
    'ErrorError',
    'ExecOnHostBody',
    'ExecOnHostResponse',
    'GetAccountResponse',
    'GetAgentRunResponse',
    'GetAgentRunStatsResponse',
    'GetHealthReadyResponse',
    'GetHealthResponse',
    'GetMyDispatchInboxResponse',
    'GetReceiptResponse',
    'GetSessionResponse',
    'GetStatusResponse',
    'GetTaskResponse',
    'GetTaskStatsResponse',
    'HeartbeatSessionLeaseResponse',
    'HostExecBody',
    'HostExecRequest',
    'HostExecResponse',
    'HostExecResultBody',
    'HostOp',
    'HostPresence',
    'ListAgentRunStepsResponse',
    'ListDevicesResponse',
    'ListHostsResponse',
    'ListModelsResponse',
    'ListOrgMembersResponse',
    'ListOrgsResponse',
    'ListPendingTasksResponse',
    'ListPhoneModelsResponse',
    'ListSessionControlsResponse',
    'ListSessionEventsResponse',
    'ListSessionSharesResponse',
    'ListSessionsResponse',
    'ListSessionsSharedWithMeResponse',
    'ListTasksResponse',
    'MarkSessionControlAppliedResponse',
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
    'OrgAddMemberBody',
    'OrgCreateShareBody',
    'OrgMember',
    'OrgRole',
    'OrgSessionRole',
    'OrgSessionShare',
    'OrgSharePrincipalType',
    'OrgSharedSession',
    'OrgWithRole',
    'PatchAccountBody',
    'PatchAccountResponse',
    'PostHostExecResultBody',
    'PostHostExecResultResponse',
    'ReleaseSessionLeaseResponse',
    'RemoveOrgMemberResponse',
    'RunAgentSyncBody',
    'RunAgentSyncResponse',
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
    'SubmitFeedbackBody',
    'SubmitFeedbackResponse',
    'SubmitSessionControlBody',
    'SubmitSessionControlResponse',
    'Task',
    'TaskConfirmRequest',
    'TaskConfirmResponse',
    'TaskEvidenceKind',
    'TaskNotConfirmableError',
    'TaskNotConfirmableErrorError',
    'TaskOutcome',
    'TaskStats',
    'TaskSurface',
    'ToolFetchRequest',
    'ToolFetchResponse',
    'ToolRulesRefusedError',
    'ToolRulesRefusedErrorError',
    'ToolRulesRefusedErrorErrorDetails',
    'ToolSearchProviderResponse',
    'ToolSearchProviderResponseResultsItem',
    'ToolSearchRequest',
    'ToolSearchResponse',
    'ToolSearchResponseRerank',
    'ToolSearchResult',
    'ToolsFetchBody',
    'ToolsFetchResponse',
    'ToolsSearchBody',
    'ToolsSearchResponse',
    'UpdateDeviceBody',
    'UpdateDeviceResponse',
    'UpdateSessionBody',
    'UpdateSessionResponse',
]
