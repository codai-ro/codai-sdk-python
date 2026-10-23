# Changelog

All notable changes to `codai-sdk` are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.69.0] - 2026-10-23

- `MusicRoom.listening`: what the Music Room critic heard (listening features, Audiobox Aesthetics, Gemini listener
  verdict) — new `MusicRoomListening` TypedDict; `None` before the critic ran. The `critic_text_only` warning is now
  documented (the critic could not listen to the master and judged from the score).

## [0.68.0] - 2026-10-22

- Music Room (MR-09..MR-17): new `client.studio` namespace with `studio.music_room` — a team of role agents writes,
  plays, sings and mixes a song with three approval gates. `create(brief, language=, genre=, duration_seconds=,
vocals=, timbre=, voice_passport_id=, instruments=, auto=, budget_micro_usd=, title=, idempotency_key=)`
  (`POST /v1/studio/music-room`), `get(id)`, `list(limit=, before=)`, `quota()`, `choose(id, gate, variant=,
approve=)`, `direct(id, role, direction, section_id=, idempotency_key=)` and `wait(id, until_gate=, interval=,
timeout=)`; constant `MUSIC_ROOM_TERMINAL_STATUSES`.
- Regenerated `_types.py`: `MusicRoomCreate`, `MusicRoom`, `MusicRoomPlanVariant`, `MusicRole`, `MusicRoomChoose`,
  `MusicRoomDirect`, `MusicRoomQuota`, `MusicRoomList`.
- Voice passport (D37, beta): new `client.voices` with `add_singing_consent(voice_id, session_id)`
  (`POST /v1/studio/voices/{id}/singing-consent`, never retried) and `revoke_singing_consent(voice_id)` (204): your own
  custom voice singing in Music Room songs, a separate revocable consent; the result approximates your timbre.
  Regenerated `_types.py`: `StudioVoice`, `StudioVoiceSinging`, `StudioVoiceSingingConsentRequest`.

## [0.67.0] - 2026-10-20

- Creatives (CX-07/08/09): `creatives.build(..., format=, format_id=, crop_marks=)` builds carousel (`png` | `pdf`)
  and print (`pdf`, PDF/X-4) creatives, which answer HTTP 202 with a queued export job in `export`; new helper
  `is_paged_build(r)` and `creatives.build_and_wait(...)` (build, then `exports.wait` the export).
- `creatives.post_copy(creative_id, platforms=, language=, brief=, tone=, seq=, idempotency_key=)`
  (`POST /v1/studio/creatives/{id}/post-copy`): caption + hashtags per platform and alt text per slide; token-metered.
- `creatives.transcript_cut(creative_id, node_id=, remove=, base_seq=, force=)`
  (`POST /v1/studio/creatives/{id}/transcript-cut`): delete transcript word ranges from a video clip; free.
- `creatives.regenerate_node(creative_id, node_id, prompt=, model=, aspect_ratio=, base_seq=, force=,
idempotency_key=)` (`POST /v1/studio/creatives/{id}/nodes/{nodeId}/regenerate`): new picture for an image node,
  cast-consistent; billed like an image generation.
- `media_ops.quote` / `run` / `run_and_wait` accept `mask_png_b64=` for `image.inpaint` / `image.erase`.
- `videos.create` / `images.generate` document `reference_asset_ids` (Studio image assets as references).
- Regenerated `_types.py`: `CreativeCast`, `CreativePagedBuildRequest`, `StudioCreativePagedBuild`,
  `CreativePrintLintIssue`, `StudioPostCopyRequest`, `StudioPostCopy`, `CreativeTranscriptCutRequest` / `Result`,
  `CreativeRegenerateNodeRequest` / `Result`; `CreativeOp` gains `trimVideo`, `splitVideo`, `setVideoRate`,
  `addCast`, `updateCast`, `removeCast`; `StudioExport.kind` gains `carousel_png`, `carousel_pdf`, `print_pdf`.

## [0.66.0] - 2026-10-20

- New `client.media_ops` for codai Studio media operations (AR-02): `list()`, `quote(op, asset_ids, params)`,
  `run(op, asset_ids, params, idempotency_key=)` (a `media_op.result` for sync ops, a `media_op.job` for async ops),
  `job(id)`, `wait(id, interval=, timeout=)` and `run_and_wait(...)`; helpers `is_media_op_job`,
  `MEDIA_JOB_TERMINAL_STATUSES`.
- Creatives: `CreativeKind` gains `audio` (songs and podcasts); new generated types `CreativeAudio`,
  `CreativeAudioTrack`, `CreativeAudioClip`, `CreativeAudioSection`, `CreativeAudioFx` and the media-op schemas.
- New `client.lyrics` (MU-06): `write(brief, language, genre=, mood=, structure=, syllables_per_line=,
rhyme_scheme=, lines_per_section=, title=, idempotency_key=)` (`POST /v1/studio/lyrics`) and `align(creative_id,
clip_id, lyrics_text, language=, apply=, base_seq=, retranscribe=, idempotency_key=)` (`POST /v1/studio/lyrics/align`,
  timed lines + LRC).
- `client.creatives.render_audio(creative_id, formats=, stems=, lrc=, loudness=, title=, idempotency_key=)` (MU-05):
  mixdown + mastering + exports of an `audio` creative. New generated types `StudioLyrics*`,
  `CreativeAudioRenderRequest`, `CreativeAudioRenderAccepted`, `StudioAudioRender`; `RenderCreativeBody` /
  `RenderCreativeResponse202` / `GetRenderResponse` are now video | audio unions. The live jam WebSocket
  (`/v1/studio/jam`) has no Python helper; see the Lyrics & live jam docs page for the protocol.

## [0.65.0] - 2026-10-20

- Vault guards v4 (V-18, V-19, V-21, V-32, V-35): `vault.update_settings(default_tier=, guards=)` changes the anomaly
  guards (new host in 30 days, burst, allowed hours; an anomaly forces t4 with reason `anomaly:new_host|burst|hour`);
  `vault.lock(via=)` is the panic lock (revokes grants, denies pending approvals, agent uses then answer
  `vault_locked`); `vault.unlock_challenge()` + `vault.unlock(challenge, proof)` end a lock with a device-key or
  passkey proof over `vault_unlock_message(challenge, device_id_or_passkey)`; `vault.limits()` /
  `vault.set_limits(item_id, per_minute, per_day, units_per_day)` manage per-handle caps (over a cap the broker calls
  raise a 429 error with code `vault_rate_limited` and `Retry-After`); `vault.revoke_task_grants(task)` ends the
  grants of a finished task. Generated types gain `VaultGuards`, `VaultItemLimits`, `VaultLockResult`,
  `VaultUnlockChallenge`.

## [0.64.0] - 2026-10-20

- Prompt organisation (PR-04/05/07): prompt rows carry `tags`, `priority` (0–3), `recurrence`
  (`{"every": "day"|"week"|"month", "at"?}` or `{"on": "session_end"}`), `next_prompt_id`, `launch`
  (`{"agent"?, "model"?, "folder"?}`) and `is_template`, also accepted by `prompts.create` / `prompts.update`.
  `prompts.list` takes `tag` (str or list, AND), `priority_min`, `q`, `templates="only"|"exclude"`, `sort` and `order`.
- New prompt methods: `prompts.export_prompts(format="csv"|"md", ...)` (`GET /v1/prompts/export`, returns the text),
  `prompts.bulk(ids, action, ...)` (`POST /v1/prompts/bulk` → `{"updated": n}`), `prompts.events(id)`
  (`GET /v1/prompts/{id}/events`) and `prompts.instantiate(id)` (`POST /v1/prompts/{id}/instantiate`).
- Generated types: `Prompt` gains the organise fields, new `PromptRecurrence`, `PromptLaunchConfig`, `PromptEvent`,
  `PromptBulkRequest`; sessions gain `stub` (create with `stub: True` for a title-only mirror) and
  `SessionControlKind` gains `hydrate` (session owner only) to ask the executor for the transcript.

## [0.63.0] - 2026-10-19

- Sandboxes v2 are generally available and the default backend: `sandboxes.create()` without `backend` starts a
  v2 pod (the gateway falls back to v1 when v2 is unavailable for the key; read `backend` on the reply). Pass
  `backend="v1"` for Cloud Run.
- v2 now accepts `egress` (`pypi` / `npm` preset or an allowlist, through the codai egress proxy), `inputs` on
  exec and `artifacts()`; the image ships Node 24 + npm. `snapshot()` stays v1 only (409 `not_supported_on_v2`).
- Documented caps: 5 running v2 sandboxes per user (429 `sandbox_concurrency_limit`), 10 paused per user
  (429 `sandbox_paused_limit` on `pause()`), platform capacity 503 `sandbox_capacity` (retry). Docstrings only;
  no signature changes.

## [0.62.0] - 2026-10-20

- New `client.os_gate` for the OS protection gate: `policy()` (`GET /v1/policy`, `{"os_gate": {"allow_override": bool}}`
  folded over every org of the caller, strictest wins; a 503 `policy_unavailable` means keep your cached value) and
  `record_event(action, checks, surface, app_version, at)` (`POST /v1/os-gate/events`, 202 `{"ok": True}`; audit an
  override granted/revoked with check ids, surface, app version and time only). Typed shapes `PolicyResponse`,
  `OsGateEvent`, `OsGateEventAccepted` in `codai._types`.

## [0.61.0] - 2026-10-20

- `client.memory.delete_all()` (`DELETE /v1/memory?confirm=all`, AL-234): erase every memory of your account in one
  call; returns `{"deleted": {tier: n}, "total": n}`.

## [0.60.0] - 2026-10-19

- Vault approvals bind the request preview and use number matching (V-30/V-31): `vault.use` / `vault.http` /
  `vault.resolve` answers carry `match_number`; `vault.decide(..., match_number=...)` sends the number the user
  tapped with a device or passkey proof over the approve/v3 message (403 `match_required` / `match_mismatch`).

## [0.59.0] - 2026-10-19

- New `client.productions` for codai Studio brief → promo video (RC-20): `create(brief, language=, aspect_ratio=,
starter=, voice=, narration=, budget_micro_usd=, title=, idempotency_key=)`, `retrieve(id)`, `wait(id)`, `run(brief)`.

## [0.58.0] - 2026-10-19

- Studio templates (RC-29): `client.templates.list(source=, locale=, month=)`; lists include the 40 built-in starter
  templates (`source: "starter"`, ids `starter:<slug>:<en|ro>`) after your own. A starter id works in `retrieve`,
  `creatives.create({"template": ...})` and batch `template_id`.

## [0.57.0] - 2026-10-19

- New `client.vault.devices` for hardware-backed device approval keys (V-27): `challenge()`,
  `enroll(device_id, kind, name, surface, public_key, nonce, vault_signature, device_signature, attestation=)`,
  `list()`, `rename(device_id, name)` and `revoke(device_id)`.
- `vault.decide(..., proof=)` sends a v2 proof (`{"type": "device", "device_id", "signature"}` or
  `{"type": "passkey", "response"}`); `signature` is now optional (a deny needs no proof), passing both raises
  `ValueError`, and `step_up_acr` is deprecated (ignored by the gateway).
- Regenerated `_types.py` from the current OpenAPI spec.

## [0.56.0] - 2026-10-19

- New `client.research` for async deep research (`POST /v1/research`, `GET /v1/research/{id}`):
  `create(question, time_budget_s=, max_sources=, include_domains=, published_after=, output_schema=, wait_s=,
idempotency_key=)`, `retrieve(job_id)`, `wait(job_id, interval=3.0, timeout=360.0)` and `run(question, ...)`
  (create + wait). `RESEARCH_TERMINAL_STATUSES` exported.
- `tools.search` / `tools.fetch` docstrings and generated types follow the shared web tools contract (domain,
  publish-date and freshness filters, `content_chars`, `published_at` vs `crawled_at`, `notes`; fetch `max_chars`
  default 8000, max 40000).
- Regenerated `_types.py` from the current OpenAPI spec.

## [0.55.0] - 2026-10-19

- `billing.studio_quote(action, ...)` — `GET /v1/studio/quote`: the price of a codai Studio action (USD and wallet
  EUR micros) and your spendable balance before you run it.
- `ext={"idempotency_key": ...}` sends `Idempotency-Key`: a retried billed Studio POST replays the first answer
  instead of charging twice (24 h).
- Paid Studio calls can now answer 402 `insufficient_funds` (`quote_micro_eur`, `balance_micro_eur`) as a `CodaiError`.

## [0.54.0] - 2026-10-18

- Vault: `client.vault` covers every `/v1/vault/*` route (account, settings, vaults, items, cloud copy, rules,
  grants, events, approvals + `decide`, and the agent broker `catalog` / `use` / `http_call` / `resolve`). The server
  only stores ciphertext built client-side; the broker calls never return secret values. Typed dicts for the
  `Vault*` schemas.
- Studio share links: `creatives.create_share(..., expires_in_days=...)` also accepts `"never"`; omitted now means 30 days
  (was: never expires).
- Public review dicts carry `decided_by_kind` (`"self_declared"`): the approver name is typed by the link holder, not verified.

## [0.53.0] - 2026-10-17

- Sandboxes v2 (closed canary): `sandboxes.create(backend="v2", template=...)` with templates `codai-base`,
  `brivio-acte` and `desktop`; the sandbox dict carries `backend` (`v1` | `v2`), optional `restored`, status `paused`.
- New methods: `sandboxes.run_code(id, code, timeout_seconds=None)` (persistent Python kernel),
  `sandboxes.reset_kernel(id)`, `sandboxes.pause(id)`, `sandboxes.resume(id)` (`restored`, `ready_ms`),
  `sandboxes.fork(id, count, ttl_seconds=None)` (1-5 children, per-child `restored` / `error`) and
  `sandboxes.preview(id, port, ttl_seconds=None)` (signed `*.sbx.codai.ro` URL, at most 1 h).

## [0.52.1] - 2026-10-16

- `WalletLedgerEntry.source` literal gains `sandbox_charge`: the agent sandbox exec-time debit (EUR 0.10 per
  exec-hour after 10 free exec-hours a month), written every 5 minutes once sandbox billing is switched on.

## [0.52.0] - 2026-10-16

- `provenance.check(file, content_type=...)` — public AI-provenance checker (`POST /v1/public/provenance/check`,
  no key needed, at most 25 MB; `file` is bytes or a path): reports C2PA manifest presence and claimed issuer, the
  WAV RIFF INFO, MP3 ID3 and MP4 `udta/meta` AI marks and image XMP. `signature_verified` and `synthid_checked`
  are always `False`.

## [0.51.0] - 2026-10-16

- `client.sandboxes` (beta) — agent sandboxes over REST (`/v1/sandboxes`): `create` / `list` / `retrieve`, `exec`
  (blocking; `exit_code`, `stdout`, `stderr` and a reproducibility `receipt`), `exec_stream` (generator of event
  dicts: `start`, `stdout`, `stderr`, `truncated`, `exit`, `error`), `files.put` / `files.get` (returns `SandboxFile`
  with `data` + `sha256`) / `files.list`, `artifacts` (scanned files from `/workspace/out` with signed 1 h links),
  `snapshot`, `delete` and one-shot `run`. `exec`, `exec_stream` and `run` accept `idempotency_key=`.
- Chat `tools` items may now be `{"type": "codai_sandbox", "egress": ..., "template": ...}` (`ChatSandboxTool` in
  `codai._types`): the gateway runs bash / Python server-side in a sandbox per session and returns the artifacts.
- REST exec over Environments: `environments.exec(env_id, {"command": ..., "op": ..., "args": ..., "timeout_ms": ...})`
  (blocking relay op, shell results flattened to `exit_code` / `stdout` / `stderr`), `environments.files.list` /
  `get` / `put` (UTF-8 text, ≤ 2 MB) and `environments.jobs.start` / `get` (status + output). No WebSocket client
  needed; 409 `environment_offline`, 504 `host_timeout`.

## [0.50.0] - 2026-10-16

- `abuse_reports.create(share_token, surface, category, explanation, reporter_name, reporter_email, good_faith=True)` —
  `POST /v1/studio/abuse-reports` (public, no key needed): DSA art. 16 notice about illegal or abusive content on a
  codai Studio share (`surface="share"`) or review (`"review"`) link — categories `voice_without_consent`,
  `impersonation`, `fraud`, `election`, `illegal_other`, `other`. Answers 202
  `{id, object: "studio.abuse_report", status: "open"}`, also for an unknown link (no enumeration). Never retried.
  `CreateStudioAbuseReportBody` / `CreateStudioAbuseReportResponse` types.

## [0.49.0] - 2026-10-16

- `resolve.list(status=None, limit=None, cursor=None)` — `GET /v1/resolve/jobs`, your Resolve jobs newest first
  (`{"jobs", "next_cursor"}`; `status` = a string or a list sent as a comma list), and `resolve.iterate(status, limit)`,
  a generator that follows `next_cursor`. `ResolveJob` gains `issue_url` and `issue_title`; `ResolveJobList` type.
- `billing` (READ-ONLY, never starts a payment): `billing.get()` — `GET /v1/billing`; `billing.invoices(limit=None)` —
  `GET /v1/billing/invoices`; `billing.watch_balance(threshold_eur, on_low, interval_s=60, max_checks=None)` polls
  `get()` and calls `on_low(balance_eur, billing)` once per crossing below the threshold.
- `referrals`: `referrals.get()` — `GET /v1/referrals`; `referrals.redeem(code)` and `referrals.set_consent(bool)` call
  `PATCH /v1/account` with `referral_code` / `referral_consent`.

## [0.48.0] - 2026-10-16

- `voice_revocations.create(email, voice_owner_name, details, evidence_url=None)` — `POST /v1/studio/voice-revocations`
  (public, no key needed): asks for a voice cloned in codai Studio to be taken down; answers 202
  `{id, object: "studio.voice_revocation", status: "open"}` and never echoes the input (only the sha256 of the e-mail
  is stored). Never retried. `CreateVoiceRevocationBody` / `CreateVoiceRevocationResponse` types. Custom (cloned) voices
  themselves are not in the SDK while the feature flag is off.

## [0.47.0] - 2026-10-16

- Lottie export: `creatives.export_lottie(id, format=None, formats=None, seq=None, container=None)` —
  `GET /v1/studio/creatives/{id}/export.lottie` exports a video creative as a Lottie animation (Bodymovin JSON with
  embedded images, or a dotLottie `.lottie` archive with `container="dotlottie"`; `formats="all"` for every format),
  free and synchronous: the export comes back already `succeeded` with a signed `url` and the fidelity report in
  `warnings`. `creatives.download_lottie(...)` returns the file itself (`{bytes, filename, content_type}`).
  `StudioExport` gains `kind` (`"fcpxml"` | `"lottie"`) and `container` (Lottie only); `ExportCreativeLottieResponse`.

## [0.46.0] - 2026-10-16

- `ai_label` (`"none"` | `"corner"` | `"end_card"`, EU AI Act art. 50(4)): in the `renders.create` / `renders.render`
  body, as `creatives.render(id, ai_label=...)` and `batches.create(..., ai_label=...)` / `dry_run`. Burns a visible
  "AI-generated" label (corner for the whole video, or a ~2 s end card) into the MP4. Omitted = `corner` when the render
  uses TTS narration or AI-generated images, else `none`; `none` with TTS narration is a 400 `ai_label_required`.
  Render replies report the resolved `ai_label`, and so do `renders.list` items (`"none"` for renders from before the
  label existed).

## [0.45.2] - 2026-10-16

- `client.memory.list/search/create/delete` — your persistent memory over REST (`/v1/memory`), the same store
  the MCP memory tools use. Search and create are metered as `memory:search` / `memory:create`.

## [0.45.1] - 2026-10-15

- `allow_remix` on view share links now defaults to `false` server-side (E-13 legal review): pass
  `allow_remix: true` to let link holders remix the creative into their own account.

## [0.45.0] - 2026-10-15

- Share links: `creatives.create_share(id, kind, label=None, expires_in_days=None, seq=None, allow_remix=None,
can_approve=None)` — `POST /v1/studio/creatives/{id}/shares` returns the public `url` and its `token` once;
  `creatives.list_shares(id)` and `creatives.revoke_share(id, share_id)`.
- Review: `creatives.review(id)`, `request_review(id)`, `reset_review(id)` (`draft` → `in_review` → `approved` |
  `changes_requested`, approval pins the version); threads: `review_threads(id, status=None)`,
  `create_review_thread(id, body, node_id=None, scene_id=None, t_ms=None)`, `reply_review_thread`,
  `resolve_review_thread`, `reopen_review_thread`, `delete_review_comment`.
- New `client.shares` (token or whole link): `get(link, format=None, locale=None)` (no key needed),
  `remix(link, title=None)`, and through review links `comment(link, name, body, …)`, `reply`, `resolve`, `reopen`,
  `decide(link, name, decision, seq, note=None)`. `codai.share_token_from(value)` extracts the token. All free.
- Generated types: `StudioShare*`, `StudioReview*`, `StudioPublicShare`, `StudioPublicReview`, `StudioRemix*`.

## [0.44.0] - 2026-10-15

- Localisation: `creatives.locales(id, locale=None, units=None, offset=None, limit=None)` —
  `GET /v1/studio/creatives/{id}/locales`; `creatives.localize(id, locales, tone=None, glossary=None, only_missing=None,
voice=None, base_seq=None, force=None)` — `POST /v1/studio/creatives/{id}/localize` translates every text into up to
  10 BCP-47 locales as per-locale overrides in one new version (token-metered; `voice=True` narrates voice clips again,
  billed); `creatives.fork_locale(id, locale, title=None, seq=None)` —
  `POST /v1/studio/creatives/{id}/locales/{locale}/fork` saves a locale as a new creative.
- `locale=` keyword on `creatives.compiled`, `render`, `frame`, `captions_srt`, `captions_vtt` and `lint`. Lint
  codes `missing_translation`, `stale_translation`, `text_overflow_locale` and issue `locale`; new ops
  `setLocaleText`, `setLocale`, `setLocalization`.
- Batches: new `client.batches` — `create(source, csv=None, sheet=None, delimiter=None, mapping=None, title=None,
render=None, quality=None, format=None, localize=None)`, `dry_run(...)` (same arguments, nothing stored), `list`,
  `get(id, rows=None, status=None, offset=None, limit=None)`, `cancel`, `retry`, `export_csv` (status CSV text),
  `zip` (ZIP of finished renders) and `wait(id, interval=3.0, timeout=600.0)`.
- Generated types: `CreativeLocaleStatus`, `CreativeLocaleUnit`, `CreativeLocalizeRequest`, `CreativeLocalizeResult`,
  `CreativeLocaleForkRequest`, `CreativeLocaleForkResult`, `StudioBatch*`.

## [0.43.0] - 2026-10-15

- Auto-captions: `creatives.captions(id, clip_id=None, preset=None, node_id=None, script=None, language=None,
retranscribe=None, base_seq=None, force=None)` — `POST /v1/studio/creatives/{id}/captions` transcribes a voice clip
  word by word (words cached on the asset, free next time), corrects the spelling with the script and adds or updates a
  captions node as one new version (`node_id`, `words`, `cached`, `corrected`, `cost_micro_usd`; a fresh
  transcription is billed at the speech-to-text rate). `creatives.captions_srt(id, node_id=None, seq=None)` /
  `captions_vtt(...)` return the captions as SRT / WebVTT text.
- Platforms: `creatives.adapt(id, platforms, focal=None, base_seq=None, force=None)` —
  `POST /v1/studio/creatives/{id}/adapt` adds one format per platform (`tiktok`, `reels`, `shorts`, `feed-square`,
  `feed-portrait`, `youtube`) with text kept inside the platform safe zone; `focal="vision"` (token-metered) finds
  image focal points. New ops `adaptFormat` and `setControl`.
- Lint: issues gain `format` and `fixable` and the codes `empty_list`, `off_brand_color`,
  `outside_platform_safe_zone`, `text_too_small`, `missing_alt`, `missing_captions`, `reading_speed`, `flashing`;
  the result adds `fixable`. `creatives.lint_fix(id, codes=None, agent=None, base_seq=None, force=None)` —
  `POST /v1/studio/creatives/{id}/lint/fix`: deterministic fixes are free, `agent=True` adds one billed `codai` turn.
- Tweak panel: `creatives.controls(id)` — `GET /v1/studio/creatives/{id}/controls`.
- Render aspect ratio `4:5` (1080×1350).
- Generated types: `CreativeCaptionsRequest`, `CreativeCaptionsResult`, `CaptionPresetId`, `PlatformId`,
  `CreativeAdaptRequest`, `CreativeAdaptResult`, `CreativeLintCode`, `CreativeLintFixRequest`,
  `CreativeLintFixResult`, `Control`, `PanelControl`, `CreativeControls`.

## [0.42.0] - 2026-10-14

- Brand kits as Design Tokens (DTCG 2025.10): kits now carry `dtcg` (the canonical document), `contrast` (WCAG ratio
  - `aa` for text/background, primary/background, background/primary, accent/background, secondary/background) and
    `updated_at`; `tokens` also carries the document aliases (`color.bg`, `color.fg`, `color.accent`,
    `font.heading`, `font.body`), extra colours and `radius`.
- `brand_kits.create(name, tokens=… | dtcg=…, logo_asset_id=…, source_url=…)` — `POST /v1/studio/brand-kits`
  (exactly one of `tokens` / `dtcg`, else `ValueError`; 400 `invalid_tokens`), `brand_kits.update(id, name=…,
tokens=…, dtcg=…, logo_asset_id=…)` — `PATCH /v1/studio/brand-kits/{id}` (`logo_asset_id=None` removes the logo),
  `brand_kits.export_dtcg(id)` — `GET /v1/studio/brand-kits/{id}/dtcg`. Free.
- `brand_kits.extract(url=None, name=None, logo_asset_id=None)` — exactly one of `url` / `logo_asset_id` (else
  `ValueError`); from a logo image one vision turn reads the palette (400 `unsupported_media`).
- `creatives.restyle(id, brand_kit_id=None, tokens=None, base_seq=None, snap=None, fonts=None, force=None)` —
  `POST /v1/studio/creatives/{id}/restyle`: re-applies a kit as one new version (literal brand colours become token
  refs, `snap` maps the rest to the nearest kit colour, fonts by role, locked nodes skipped unless `force`). Free.
- Generated types: `BrandKitDtcg`, `BrandKitContrastPair`, `BrandKitCreateRequest`, `BrandKitUpdateRequest`,
  `CreativeRestyleRequest`.

## [0.41.0] - 2026-10-14

- Documents as creatives: `creatives.from_document(document_id)` — `POST /v1/studio/documents/{id}/creative` turns a
  Studio deck / doc / sheet into an editable creative (slides = scenes with `layout` + `notes`, doc pages = a `flow`
  group, sheets = a `cell_grid` + chart nodes; nodes carry semantic `role`s). Idempotent: returns the creative plus
  `document_id` and `existing` (HTTP 201 new / 200 already linked). Free.
- `creatives.build(creative_id, seq=None, preview=None, filename=None)` — `POST /v1/studio/creatives/{id}/build` builds
  the creative back into PPTX / DOCX / XLSX as a new version of its document: `{object: "studio.creative_build",
creative_id, seq, warnings, document}`; 400 `not_supported_for_kind` / `invalid_spec`. Files are free;
  `preview=True` queues the billed document preview.
- Regenerated `_types.py`: `StudioCreativeFromDocument`, `CreativeBuildRequest`, `StudioCreativeBuild`,
  `Document.creative_id`, `CreativeCompiled.kind`, the `createCreativeFromDocument` / `buildCreative` operations.

## [0.40.0] - 2026-10-14

- FCPXML export: `creatives.export_fcpxml(id, format=None, seq=None)` — `GET /v1/studio/creatives/{id}/export.fcpxml`
  queues a zip with an FCPXML 1.10 project (one clip + marker per scene, audio on its own lanes) and its media
  (per-scene MP4 segments, voice / music / sfx files) for Final Cut Pro, DaVinci Resolve or Premiere (FCPXML import).
  Returns `{id, status: "queued", creative_id, seq, format, fps, filename, url, expires_at, bytes, rendered_seconds,
cost_micro_usd, warnings, error, created_at}`; 400 `unsupported_kind` / `unsupported_format` / `too_long`. Only newly
  rendered seconds are billed, at the final render price (cached segments are free).
- `exports.retrieve(id)` — `GET /v1/studio/exports/{id}` (free); `exports.wait(id, interval=3.0, timeout=900.0)` polls
  until `succeeded` (signed `url`, valid 1 h) or `failed` and returns the final export; `TimeoutError` after `timeout`.

## [0.39.0] - 2026-10-14

- Templates from your own creatives: `creatives.save_template(id, vars=[…], title=…, seq=…)` —
  `POST /v1/studio/creatives/{id}/template`: each `vars` entry (`{"node_id", "prop": "text" | "image", "key",
"label"?}`) turns a text node's text or an image node's asset into a template variable (current value = default).
  Returns `{id, title, kind, source_creative_id, source_seq, vars_schema, thumbnail_url, created_at, doc}`; 400
  `node_not_found` / `invalid_pick` / `duplicate_key`. Free; templates are private.
- `templates.list(kind=…, limit=…)`, `.retrieve(id)` (with `doc`), `.delete(id)` — free.
- `creatives.create({"kind": …, "template": …, "vars": {…}})` starts version 1 from a template with the var values
  applied (400 `kind_mismatch` / `unknown_var` / `invalid_var_value`, 404 unknown template).

## [0.38.0] - 2026-10-14

- Cards: `cards.product(url, lang=None)` — `POST /v1/cards/product`: a `products` card block with one item read from
  a public https product page's schema.org `Product` JSON-LD (or OpenGraph product tags): name, image, price +
  currency (lowest offer), old price, rating (0-5), reviews, seller, availability badge (en/ro). Only what the page
  states, never sponsored; SSRF-guarded like `unfurl`, cached 6 h, shares its 500/day limit; 422 `product_not_found`.

## [0.37.0] - 2026-10-14

- Brand kits: `brand_kits.extract(url, name=…)` — `POST /v1/studio/brand-kits/extract`: fetches a public https page
  (SSRF-guarded), one bounded `codai` model turn picks the palette (primary, secondary, accent, background, text) and
  the heading / body fonts, the logo is stored as an `image` asset. Returns `{id, name, source_url, tokens,
logo_asset_id, logo_url, logo_mime_type, created_at}`; 400 `url_blocked`, 422 `fetch_failed` / `extract_failed`,
  504 `timeout`. Token-metered (`codai::brand-kit-extract`).
- `brand_kits.list(limit=…)`, `.retrieve(id)`, `.delete(id)` — free.
- `creatives.create({"kind": …, "brand_kit_id": …})` applies a kit to version 1 (`brand = {kitId, tokens}` + logo asset).

## [0.36.0] - 2026-10-14

- A/B variants of a creative: `creatives.variants(id, base_seq=…, count=…, focus=[…], brief=…, render=…, format=…)`
  — `POST /v1/studio/creatives/{id}/variants`: one bounded `codai` model turn proposes up to 5 variants (focus hook /
  title / cta / visual / copy), each saved as a fork with the ops applied plus a queued draft render. Returns
  `{group_id, base_seq, variants: [{creative_id, label, rationale, applied_ops, head_seq, render_id}]}`; 422
  `no_edit`, 504 `timeout` after 90 s. Token-metered (`codai::creative-variants`), draft renders billed on their poll.
- `creatives.list_variants(id)` — `GET …/variants`: the latest group with `status` and the stored render state.
- `creatives.pick_variant(id, variant_id, base_seq=…)` — `POST …/variants/{variantId}/pick`: the winner's ops onto the
  original (rebased like `edit`, 409 `stale` on overlap), statuses updated.

## [0.35.0] - 2026-10-14

- `SessionControlKind` gains `pause` and `resume`: `POST /v1/sessions/{id}/control` with `kind="pause"`
  parks the running turn at its next step boundary (after the current tool calls), `kind="resume"` continues the
  same turn. Editors may send both (same trust as `cancel`). Executors report the state with a `run_state` event
  `{"state": "paused" | "running"}`.

## [0.34.0] - 2026-10-12

- `creatives.comment(id, t_ms=…, comment=…, base_seq=…, node_id=…, scene_id=…, apply=…)` —
  `POST /v1/studio/creatives/{id}/comments`: a comment pinned on a frame becomes an edit (one bounded `codai` model
  turn proposes ops, applied like `edit`). Returns `{head_seq, applied_ops, summary, version}`; 409 `stale` on an
  overlapping change, 422 `no_edit` when the model made no edit, 504 `timeout` after 60 s. Token-metered
  (`codai::creative-comment`).

## [0.33.0] - 2026-10-12

- `creatives.frame(id, t_ms=[…], format=…, exact=…, version=…)` — `POST /v1/studio/creatives/{id}/frame` now returns
  PNG still frames (`{object: "studio.creative.frames", status: "succeeded", frames, billed_micro_usd}`) or a running
  job (`{object: "studio.creative.frame_job", status: "running", frame_job_id}`) when they are not ready within ~90 s.
  `exact=True` cuts frames from a draft render of the covering scenes. Cached frames are free; 60 frame jobs per UTC
  day are free, then billed. The old `frame(id, body)` dict form is replaced by keyword arguments.
- `creatives.frame_job(id, job_id)` — `GET /v1/studio/creatives/{id}/frames/{jobId}`, polls a frame job.
- `creatives.render` may now answer 200 with the identical existing render (`cached: True`, no new charge); new
  renders carry `cached: False`.

## [0.32.0] - 2026-10-12

- `cards.route(from_=…, to=…, origin=…, destination=…, mode=…, depart_at=…)` — `GET /v1/cards/route`, travel time
  from Google Routes (`route` summary + `map` block); billed $0.010 traffic-aware driving, $0.005 walk / bike / transit.
- `cards.track(awb, carrier=…)` — `GET /v1/cards/track`, parcel history (Sameday live; FAN Courier, Cargus, DPD with a
  gateway carrier contract only).
- `cards.efactura(limit=…)` — `GET /v1/cards/efactura`, your fiscal documents issued through Brivio with their ANAF
  e-Factura status.

## [0.31.0] - 2026-10-12

- `client.creatives` — codai Studio editable creative documents (ECD) with an append-only version history:
  `list(kind, before, limit)`, `create(body)`, `retrieve(id, seq=None)`, `outline`, `find(id, query)`,
  `subtree(id, ids=None, scene_id=None)`, `edit(id, base_seq, ops, intent=None, author=None, force=None)`
  (`POST /v1/studio/creatives/{id}/ops`; a stale base is rebased, overlapping changes raise `CodaiError` 409
  `stale`), `versions`, `revert(id, seq)`, `fork`, `delete`, `lint`, `compiled` (preview HTML with signed asset URLs)
  and `render` (queues a `codai-render`, HTTP 202; poll `renders.retrieve`). `frame` is reserved (501
  `not_implemented`). Everything except `render` is free.
- `create_timeline` replies carry `creative_id`; `renders.retrieve` reports `creative_id` for renders linked to a
  creative.
- Generated types: `Creative*` TypedDicts and the 15 creatives operation aliases.

## [0.30.0] - 2026-10-12

- `lists` resource — codai Lists + Share to codai: `list`, `create`, `reorder`, `update`, `delete`, `items`, `add`,
  `update_item`, `delete_item`, `image` (`ListItemImage(data, content_type)`), `export_markdown` (str), `share` (`POST /v1/share`,
  201 created / 200 dedupe) and `stream()` (generator) (`event: list` frames).
- `schedules.audit({ schedule_id?, limit? })` — `GET /v1/schedules/audit`, the append-only scheduler audit log.
- Generated types: 14 new operations (lists, share, schedule audit).

## [0.29.0] - 2026-10-12

- `cards.render(block, format=None, width=None, height=None, theme=None, scale=None)` — `POST /v1/cards/render`:
  renders a `chart` or `qr` card block to PNG (default) or SVG on the gateway and returns
  `CardsRendered(data, content_type, width, height)`. Free, 2000 renders per user per day. Mermaid `diagram` / `math`
  blocks are not supported yet (422 `render_unsupported`).
- Generated types: operation `cardsRender`.

## [0.28.0] - 2026-10-11

- Studio scene timelines on `client.renders`: `create_timeline(body)` for `POST /v1/studio/timelines` (image/video
  scenes, optional narration billed now and a music bed; HTTP 202, poll with `retrieve`), `regenerate_scene(render_id,
scene_id, body)` for `POST /v1/studio/renders/{id}/scenes/{scene_id}/regenerate` (a new render with one scene
  replaced) and `list(before=None, limit=None, root_render_id=None)` for `GET /v1/studio/renders` (no polling, no URLs).
- `retrieve(render_id, expand_assets=True)` sends `?expand=assets`; timeline renders carry `timeline`,
  `parent_render_id`, `root_render_id` and `stage`.
- Generated types for `StudioRenderList`, `StudioTimelineCreate`, `StudioTimelineAccepted`, `StudioSceneRegenerate`,
  `StudioSceneRegenerateAccepted`, `StudioTimeline`; operations `listRenders`, `createTimeline`, `regenerateRenderScene`.

## [0.27.0] - 2026-10-11

- `client.cards` — typed card data from `/v1/cards/*`. Every JSON method returns `{"block": ..., "provenance": ...}`
  where `block` is already a valid `@codai/cards` block: `cards.weather(lat, lng, name=None)` (MET Norway, free),
  `cards.places(q=None, lat=None, lng=None, radius=None, type=None, limit=None, lang=None, region=None,
open_now=None)` (Google Places, billed $0.032 per call, 200/day), `cards.geocode(address)` (map block + raw
  `results`, billed $0.005), `cards.fx(source=None, from_=None, to=None, amount=None, quote=None, symbols=None)`
  (BNR / ECB, free), `cards.unfurl(url)` (links preview block, 500/day) and `cards.static_map(center=None,
markers=None, ...)` returning `CardsStaticMap(data, content_type, attribution)` for the PNG (billed $0.002, counted
  in the 500/day maps limit).
- Generated types for `CardDataResponse`; operations `cardsWeather`, `cardsPlaces`, `cardsGeocode`,
  `cardsStaticMap`, `cardsFx`, `cardsUnfurl`.

## [0.26.0] - 2026-10-11

- `schedules.pause/resume` (vacation mode with optional backfill), `schedules.templates/render_template`, and
  `client.heartbeats` (`list/create/update/delete`) for dead-man-switch monitors of crons codai does not run.

## [0.25.0] - 2026-10-11

- `client.schedules` — the codai Scheduler: `list`, `create`, `preview` (cron or plain words in English or Romanian →
  next runs + DST warning), `get`, `update`, `delete`, `run_now`, `runs`, `recent_runs`, `decide` (approve / skip a run
  waiting for you) and `stream`; `schedules.hosts.list/update` (devices as hosts: os, kind, tags); and the host executor
  protocol `schedules.executor.claim/heartbeat/result/approve_command`.
- `transcripts.publish_live` mapped to `publishTranscriptLive` in the operation table.

## [0.24.0] - 2026-10-10

- `client.settings` — account-level settings shared by every device of the account (per user, not per key):
  `client.settings.get()` for `GET /v1/settings` (full object with defaults, `version` 0 / `updatedAt` None until
  the first write) and `client.settings.update(partial, version=None)` for `PATCH /v1/settings` (deep merge, strict
  validation; a stale `version` raises a 409 `CodaiError` with code `version_conflict`).
  `settings_conflict_current(err)` returns the current state carried by that 409.
- Generated types for `SettingsResponse`, `UserSettings`, `TranscriptsSettings`, `SettingsPatchRequest`,
  `SettingsConflict`; operations `getSettings`, `patchSettings`.

## [0.23.0] - 2026-10-10

### Added

- `client.documents` — codai Studio documents (`codai-docs`): `create(body)` builds a deck (PPTX), doc (DOCX) or sheet
  (XLSX) from a JSON `spec` (free; `file` is an asset dict with `kind: "document"`), `retrieve(id)` returns it with the
  stored `spec`, `preview(id)` queues a `codai-docs-preview` preview (tagged PDF + page PNGs + contact sheet, HTTP 202),
  `retrieve_preview(preview_id)` polls it and `video(id, body)` turns a deck into an MP4 queued as a `codai-render`
  render (optional narration). Pollers `create_preview_and_wait(id, poll_interval=, timeout=)` returns the succeeded
  preview and `video_and_wait(id, body, poll_interval=, timeout=)` returns a `RenderResult`; both raise
  `RuntimeError` on `failed` and `TimeoutError` on timeout.
- Generated types: `DocumentCreateRequest`, `Document`, `DocumentPreview`, `DocumentPreviewAccepted`,
  `DocumentVideoRequest`, `DocumentVideoAccepted`, `DeckSpec`, `DocSpec`, `SheetSpec` and their parts; `AssetKind`
  gains `document` and `preview`.

## [0.22.0] - 2026-10-10

### Added

- `client.sfx` — the codai Studio sound-effects library (`codai-sfx`, curated CC0 sounds + a Freesound CC0-only
  fallback): `client.sfx.search(q=, category=, tags=, max_duration=, limit=)` for `GET /v1/studio/sfx` returns
  `SfxSearchResult` (`data`, `source`, `fallback_unavailable` from `x-codai-sfx-fallback: unavailable`; `tags` accepts
  a list) and `client.sfx.import_(sfx_id)` for `POST /v1/studio/sfx/{sfx_id}/import` returns the asset dict
  (`kind: "sfx"`, usable as `asset:<asset_id>` in renders). The method is `import_` because `import` is a Python
  keyword. Both are free.
- Generated types: `SfxDto`, `SfxCategory`, `SfxList`, `searchSfxResponse`, `importSfxResponse`; `AssetKind` gains
  `sfx`.

## [0.21.0] - 2026-10-10

### Added

- `client.audio.speech_json(body)` for `POST /v1/audio/speech` with `timestamps` and/or `store`: returns
  `SpeechJsonResult` with per-word timings (`words`), decoded `audio` or the stored studio `asset` (kind `speech`,
  usable as `asset:<id>` in renders), `duration_seconds`, `cost_micro_usd` and `timestamps_unavailable`
  (`x-codai-timestamps: unavailable`). Defaults to `codai-speech` and `timestamps: True`.
- Generated types: speech models `codai-speech` (Chirp 3 HD, 30 native Romanian voices) and
  `codai-speech-expressive` (Gemini 2.5 Flash TTS, honours `instructions`); request fields `language`, `timestamps`,
  `store`; new TypedDicts `SpeechJson`, `SpeechWord`, `MusicTrackMeta`; music request fields `lyrics`,
  `instrumental`, `bpm`, `duration_seconds`, `language` and the `codai-music` / `codai-music-pro` /
  `codai-music-legacy` model enum.
- `MusicResult.tracks` (per-item `lyrics`, `caption`, `lyrics_match`, `warnings`) and `MusicResult.warnings`
  (e.g. `lyrics_mismatch` for best-effort non-English lyrics).

### Changed

- `codai-music` is now Lyria 3 Clip (30 s MP3 with vocals); Lyria 2 stays available as `codai-music-legacy`.
- `audio.speech()` / `speech_detailed()` no longer send the Azure default `voice: "alloy"` for `codai-speech*` models.
- `music.generate()` client timeout floor raised from 180 s to 300 s (Lyria 3 Pro songs).

## [0.20.0] - 2026-10-10

### Added

- `client.renders` for codai Studio renders (`codai-render`, HyperFrames HTML composition → MP4, up to 180 s at
  1080p): `create(body)` (`POST /v1/studio/renders`, HTTP 202), `retrieve(id)` (`GET /v1/studio/renders/{id}`, status
  - `progress` + `qa`) and `render(body, poll_interval=, timeout=)`, which polls until `succeeded` and returns a
    `RenderResult` (`asset`, `poster_url`, `qa`, `cost_micro_usd`); raises `RuntimeError` on `failed` and
    `TimeoutError` on timeout.
- Regenerated `_types.py` (`StudioRender*` schemas, the `createRender` / `getRender` operations, the
  `asset_not_found`, `too_many_renders` and `renders_unavailable` error codes).

## [0.19.0] - 2026-10-10

### Added

- `client.assets` for codai Studio assets (`/v1/assets`, owner-scoped, kept 90 days): `list(kind=, before=, limit=)`,
  `iterate()` (follows `next_before`), `retrieve(id)`, `content_url(id)` (fresh 1 h signed URL), `content_path(id)`
  (authenticated `GET /v1/assets/{id}/content` redirect), `content(id)` (bytes) and `delete(id)`.
- `response_format: "url"` on `images.generate` / `images.edit` and `music.generate` bodies, and
  `response_format="url"` on `videos.retrieve` / `videos.generate`: results are stored as assets and returned in
  `ImagesResult.assets` / `MusicResult.assets` / `VideoResult.asset` (signed URLs) instead of bytes. The default
  `b64_json` behaviour is unchanged.
- Regenerated `_types.py` (`AssetDto`, `AssetKind`, `AssetList`, `AssetDeleted`, `MediaResponseFormat`, the four asset
  operations, `assets_unavailable` error code).

## [0.18.0] - 2026-10-09

### Added

- codai Studio media (US-only, English prompts): `music.generate(body)` -> `MusicResult` (`POST /v1/audio/music`,
  Lyria 2, 30 s WAV clips, timeout floor 180 s) and `videos.create` / `.retrieve(id)` /
  `.generate(body, poll_interval=5.0, timeout=300.0)` -> `VideoResult` (`POST /v1/videos` + `GET /v1/videos/{id}`,
  Veo 3.1 Fast; raises `RuntimeError` on `failed`/`filtered`, `TimeoutError` on timeout).

## [0.17.0] - 2026-10-08

### Added

- `client.tools.ground(body)` — `POST /v1/tools/ground`: locate a UI element described in words on an inline
  screenshot (codai's self-hosted GUI grounding model).

## [0.16.1] - 2026-10-07

### Added

- Web search result `source` gains `ocw` (MIT OpenCourseWare course records for education queries that name MIT / OCW).

## [0.16.0] - 2026-10-06

### Added

- `transcripts.export(id, "pdf" | "docx")` returns `{bytes, filename, content_type}`; text formats keep returning
  `{text, ...}`.
- `transcripts.shares.create(id, expires_in_days=None)` / `.list(id)` / `.revoke(id, share_id)` - read-only share
  links (`https://hub.codai.ro/t/<token>`; the token is returned once).
- `transcripts.public_view(token)` - the read-only view behind a share link.
- Types regenerated from the gateway spec (`TranscriptShare*`, `PublicTranscript`).

## [0.15.3] - 2026-10-06

### Added

- `TranscriptDetail` types gain `processing` (pending job: `kind`, `attempts`, `max_attempts`, `last_error`,
  `next_attempt_at`) - regenerated from the gateway spec.

## [0.15.2] - 2026-10-05

### Added

- `POST /v1/tools/search` types: request `depth: "fast" | "deep"` (deep = more sources, ~12 s budget); `mode`
  also accepts `fast` / `deep` as an alias (means `codai` with that depth).

## [0.15.1] - 2026-10-05

### Added

- `POST /v1/tools/search` types: request `fallback: "auto" | "off"` (automatic Grounding with Google Search when
  codai results are weak, returned as a separate `google` block + `fallback: { used, reason }`), new intents
  `academic` / `definition` / `education`, and new result sources (`mdn`, `mslearn`, `hn`, `osv`, `endoflife`,
  `openalex`, `crossref`, `arxiv`, `europepmc`, `doaj`, `core`, `wiktionary`, `openstax`, `dexonline`).

## [0.15.0] - 2026-10-05

### Added

- `client.usage.get(query)` → `GET /v1/usage`: your own requests, errors, tasks, tokens and cost grouped by
  `day` | `key` | `device` | `app` | `platform` | `model` | `client` | `tag`, filtered by `key`, `device`, `app`,
  `platform`, `model`, `tag`; `from` / `to` are inclusive `YYYY-MM-DD` (default last 30 days, max 400).
  `cost_micro_usd` is USD micros as a string. Unknown query keys raise `ValueError`.
- `client.keys.list(include_revoked=False)` → `GET /v1/keys`: your API keys with `kind`, `device_id`, `platform`,
  `client_version`, `tags` and `current`.
- `client.keys.set_tags(id, tags)` → `PATCH /v1/keys/{id}`: replace a key's tags (≤ 16, each ≤ 32 chars).
- Generated TypedDicts `UsageReport`, `UsageRow`, `ApiKeyInfo` (+ `getUsage` / `listKeys` / `setKeyTags` aliases).

## [0.14.0] - 2026-10-05

### Added

- `client.transcripts` — Transcripts API: `list` (folder / tag / pinned / status, cursor), `create`, `get`,
  `update`, `delete`, `finalize`, `retranscribe`, `reanalyze`, `add_bookmark`, `rename_speaker`,
  `edit_utterance`, `audio`, `export` (md / txt / srt / vtt / json → `{text, filename, content_type}`),
  `accept_prompt`, `usage`, `search` (lexical / hybrid), `ask`, `stream` (SSE generator), plus
  `transcripts.folders.*` and `transcripts.vocabulary.get|put`.
- `client.transcripts.upload_audio(data, track=, transcript_id=, chunk_size=, upload_id=, on_progress=)` —
  resumable tus 1.0 upload (`transcripts.uploads.capabilities|create|offset|append`).
- `PromptSource` gains `transcript`.

## [0.13.1] - 2026-10-05

### Added

- `POST /v1/tools/search` types: request `mode: "codai" | "google"` (default `codai`) and the
  `ToolSearchGoogleResponse` shape (Grounding with Google Search: `answer`, `sources`, `queries`,
  `search_suggestions_html`, `attribution`), plus the `releases` / `registry` / `engine` result sources.

## [0.13.0] - 2026-10-05

### Added

- Pending prompts track delivery: statuses `sent`, `answered`, `verified` and fields `sent_at`, `answered_at`,
  `verified_at`, `match_ref`, `match_turn_id`, `match_score`, `base_sha`, `head_sha`, `report`, `report_at`.
- `client.prompts.match(id, body)` → `POST /v1/prompts/:id/match`; `client.prompts.verify(id, body)` →
  `POST /v1/prompts/:id/verify` (report: done / partial / not started, what changed, what remains);
  `client.prompts.verify_many(body)` → `POST /v1/prompts/verify`; `client.prompts.stream()` → `GET /v1/prompts/stream`
  (SSE generator of `event: prompt` upserts / deletes).

## [0.12.0] - 2026-10-05

### Added

- `client.audio.speech_stream(body)` → `POST /v1/audio/speech/stream` (`codai-tts-ro`, Azure neural TTS with
  visemes): generator of `{"type": "start"|"audio"|"viseme"|"word"|"done"|"error", ...}`; `audio` events carry the
  decoded `audio_bytes`. `createSpeechStream` in the parity table.
- `client.system_one.batch(items, questions, timeout_ms=None, fallback=None)` — the same questions about up to 16
  states in one call; `system_one.create` documents the new `items`, `timeout_ms` and `fallback` fields and the
  `fallback_used` response flag.
- Ephemeral token scope `live` (realtime + audio) accepted by `tokens.create`.
- `_types.py` regenerated (`SpeechStreamRequest`, `SpeechStreamEvent`, batch fields on `SystemOneRequest` /
  `SystemOneResponse`).

### Not included

- No realtime (WebSocket) helper: the SDK is zero-dependency and the standard library has no WebSocket client, and
  `/v1/realtime` is outside the OpenAPI parity contract. Use `tokens.create("live")` and any WebSocket client against
  `wss://ai.codai.ro/v1/realtime?model=codai-transcribe-live&language=ro&key=<token>` (protocol in the docs,
  gateway → Embeddings, audio & realtime).

## [0.11.0] - 2026-10-02

### Added

- `client.devices.revoke_self_key()` — `POST /v1/keys/self/revoke`: the calling API key revokes itself (sign out).

## [0.10.0] - 2026-09-29

### Added

- `client.prompts.{list, create, get, update, delete, launch}` — pending prompts (`/v1/prompts/*`):
  ready-to-paste prompts left for a future chat, with `goal_key` supersede, `not_before` reminders
  (`prompt.due` notifications) and `launch` into a new session on a device. `launch` is never retried.
  `_types.py` regenerated (`Prompt`, `PromptCreate`, `PromptPatch`, `PromptCreated`, …).

## [0.9.0] - 2026-09-29

### Added

- `client.sessions.dispatch(session_id, *, device_id=..., text=..., mode="send"|"open", turn_id=..., control_id=...)`
  keyword form. `mode="open"` hands the session off — the target only opens it (no user turn), and
  `text`/`turn_id` are dropped. The positional `body` dict still works (keywords override its keys); a
  `send` without `text` now raises `ValueError` client-side instead of a server `400`.
- Regenerated `src/codai/_types.py`: `SessionDispatchRequest.mode` (`text` now optional),
  `SessionDispatchResponse.mode`, `SessionControl.mode` (`'open'` on handoff controls) and
  `DeviceListItem.online` (seen in the last 2 minutes).
- `client.images.edit({"prompt": ..., "image": {"b64_json": ..., "mime_type": ...} | [...]})` →
  `POST /v1/images/edits` (JSON body, 1–14 input images; `mask` unsupported). `editImage` in the
  parity table; `EditImageBody` / `CoreImageEditRequest` types.
- `ImagesResult.mime_types` and `ImagesResult.data_region` (`x-codai-data-region`, `eu` | `global`).
- `generate()` types gain `reference_images`, `aspect_ratio`, `image_size` and the
  `codai-image-fast` / `codai-image-pro` model ids.

### Changed

- `codai-image` is now `gemini-3.1-flash-image` on the Vertex EU endpoint (2.5 is shut down on
  2026-10-02 and served as `codai-image`). `cost_micro_usd` is usage-based (≈ $0.074 per default
  1K image) instead of a flat $0.04. The image request floor timeout is 150 s.

## [0.8.0] - 2026-09-29

### Added

- `client.images.generate({"prompt": ..., "n"?, "size"?, "negative_prompt"?, "model"?})` →
  `POST /v1/images/generations` (base64 only). Backed by `gemini-2.5-flash-image`; `model`
  defaults to `codai-image` (`imagen-4` / `imagen-4-fast` are legacy aliases). Flat $0.04 per
  returned image, reported as `cost_micro_usd`.
- EXPERIMENTAL, unaudited (HIDE protocol) agent-output signatures — provenance only, never
  authentication:
  - `EnvironmentTask.output_signature: Optional[EnvironmentTaskOutputSignature]` plus the
    `AgentOutputKey` / `AgentOutputVerifyRequest` / `AgentOutputVerifyResult` types
    (regenerated `src/codai/_types.py`).
  - `client.verify.agent_output_key()` → `GET /v1/verify/agent-output/key` and
    `client.verify.agent_output(payload, signature)` → `POST /v1/verify/agent-output`
    (public; never retried, 503 `signing_disabled` when signing is off).

## [0.7.0] - 2026-09-27

### Added

- Resolve pricing experiment (regenerated `src/codai/_resolve_types.py`):
  - `ResolveQuote` `intro_price_micro_eur` / `list_price_micro_eur` — present while the €1
    intro price applies to your first paid accept.
  - `ResolveAccepted` `paid_with` (`ResolvePaidWith`: `intro` | `credit` | `wallet` | `free`)
    and `held_micro_eur`; `ResolveJob.paid_with` once accepted.
  - `ResolveInsufficientFundsError.bundle_url` (`Optional[str]`) — fix-bundle checkout
    (10 t7 fixes for €49), set only for `t7` jobs; also appended to the error message.
  - `client.resolve.balance()` — `GET /v1/resolve/balance` (operation `getResolveBalance`) →
    `ResolveBalance {fix_credits, intro_available, wallet_micro_eur}`.

## [0.6.0] - 2026-09-27

### Added

- Signed Resolve attestations: `ResolveAttestation.signature` (DSSE envelope, `None` for
  pre-signing attestations) and `ResolveAttestationEnvelope` / `ResolveKeys` / `ResolveKey`
  types (regenerated `codai._resolve_types`).
- `client.resolve.keys()` — `GET /v1/resolve/keys` (operation `getResolveKeys`).
- `client.resolve.verify_attestation(att, keys=None)` and offline
  `verify_attestation_with_keys(att, keys)` → `{"ok": True, "keyid"}` or
  `{"ok": False, "reason": "UNSIGNED" | "BAD_SIGNATURE" | "STATEMENT_MISMATCH" | "BAD_PAYLOAD_TYPE"}`.
  The statement check is stdlib; the ECDSA signature check needs the optional
  `cryptography` package (lazy import, clear `ImportError` otherwise).
  `attestation_statement(att)` exposes the recomputed statement.

## [0.5.0] - 2026-09-27

### Added

- Resolve job webhooks: `callback_url` on `ResolveIntake`, one-time `callback_secret` on
  `ResolveQuote` / `ResolveDeclined`, and `ResolveWebhookEvent` / `ResolveWebhookEventName` /
  `ResolveWebhookJob` TypedDicts (regenerated `_resolve_types.py`).
- `verify_resolve_webhook(secret, raw_body, signature_header, tolerance_seconds=300, now=None)`
  — constant-time (`hmac.compare_digest`) check of `x-codai-signature: t=<unix>,v1=<hex>`
  with a timestamp window. Exported from `codai` and `codai.resources`.

## [0.4.0] - 2026-09-27

### Added

- `client.resolve` — codai Resolve (pay per verified fix, `https://resolve.codai.ro`,
  override with `resolve_base_url=`): `submit`, `get`, `accept`, `attestation`,
  `health`, `wait_for`. `ResolveError` / `ResolveInsufficientFundsError` (402 carries
  `topup_url`, `balance`, `required`). `RESOLVE_OPERATION_METHODS` maps every
  `resolve.yaml` operationId; `_resolve_types.py` is generated from it.

## [0.3.1] - 2026-09-26

### Changed

- Regenerated `_types.py`: project prebuild pool fields, environment `prebuild`
  and `prebuild_claimed` on create (CE-0072).

## [0.3.0] - 2026-09-25

### Added

- Projects + environments resources (26 operations), restoring full parity with the gateway
  OpenAPI (88 operations): `projects.{list,create,get,update,delete}`,
  `environments.{list,create,enroll,get,update,start,stop,archive,destroy,enroll_token}`,
  `environments.members.{list,add,set_ssh_key,set_role,remove}`,
  `environments.ports.{list,set,remove}` and `environments.secrets.{list,set,remove}`.
  `enroll`, `create` and `enroll_token` are never retried (the enrolment token is single-use).
- `_types.py` regenerated: `Project*` and `Environment*` TypedDicts.
- `system_one.create({"state", "questions"})` — typed decisions from codai-s1 (`POST /v1/systemone`,
  Choice / Score / Noul with calibrated probabilities). Raises on 503 `s1_unavailable`; keep a fallback.
- `triggers.*`, `notifications.*`, `environments.members.ssh_cert`, `environments.ssh_ca`,
  `environments.tasks.{list,create,get}` — parity with the TypeScript SDK.

## [0.2.1] - 2026-09-24

### Added

- `WalletLedgerEntry.source` literal gains `compute_charge` — the debit written every 10 minutes
  for a running managed cloud environment (F2). Additive; regenerated from the gateway OpenAPI.

## [0.2.0] - 2026-09-23

### Added

- Full gateway coverage: one method per `operationId` in `apps/docs/openapi/en/gateway.yaml`
  (62 operations), grouped like the TypeScript SDK — `client.chat.completions`, `messages`,
  `responses`, `embeddings`, `audio`, `tokens`, `models`, `health`, `agents` (+ `agents.runs`),
  `tools`, `tasks`, `sessions` (+ `events`, `controls`, `lease`, `shares`), `devices`, `hosts`,
  `orgs` (+ `members`), `account`, `receipt`, `feedback`, `phone_models`.
- `OPERATION_METHODS` (operationId → dotted method path) and `tests/test_parity.py`, which
  parses the OpenAPI spec and fails on a missing, stale or non-callable mapping and when the
  Python table diverges from the TypeScript one.
- Generated `codai._types` (`TypedDict`s for every schema plus `<operationId>Body` /
  `<operationId>Response`) from `scripts/gen-types.py`; the parity test fails when it is stale.
- SSE streams: `chat.completions.stream()` / `messages.stream()` / `responses.stream()` return
  iterables with `.text()`, raw chunks/events and a `.final` aggregate (content, tool calls,
  usage, finish reason, routing headers); `agents.runs.stream()`, `sessions.stream()` and
  `hosts.stream()` are generators of `{"event", "data"}` frames.
- `ext={...}` extension bag on every method covering all documented `X-Codai-*` request
  headers (`effort`, `thinking`, `thinking_budget`, `cache`, `no_task`, `task_id`, `device`,
  `compact`, `best_of`, `share_token`, …) plus raw `headers`; client-wide `defaults`, `device`,
  `device_name`, `device_platform`, `client` constructor options.
- `CodaiError.code`, `.request_id`, `.retry_after` parsed from the gateway error envelope.
- Dev extras `pip install -e ".[dev]"` (pyyaml + pytest); an `http.server` stub test suite.

### Changed

- `__version__` now reports the real version (`0.2.0`; it said `0.1.0` in 0.1.1).
- `chat_stream()` is built on `chat.completions.stream()`; 429/5xx retries add jitter.
- Runtime stays zero-dependency (stdlib `urllib`), Python 3.9+.

### Backward compatibility

- Every 0.1.x method keeps its name, signature and return shape: `chat()`, `chat_stream()`,
  `agents_run()`, `feedback()`, `models()`, `mint_token()`, `embeddings()`, `transcribe()`,
  `speech()`. `chat`, `embeddings`, `models` and `feedback` are callable resource groups, so
  `client.chat([...])` and `client.chat.completions.create({...})` are the same call.

## [0.1.1] - 2026-09-13

### Changed

- Repository moved to https://github.com/codai-ro/codai-sdk-python (project URLs updated). No code changes.

## [0.1.0] - 2026-06-23

### Added

- Initial public release.
- `Codai.chat()` — OpenAI-compatible completions with codai extensions
  (`session_id`, `agent_mode`, `compact`, `best_of`).
- `Codai.chat_stream()` — streaming via generator.
- `Codai.agents_run()` — server-side agent loop.
- `Codai.feedback()` — thumbs rating on a completed request.
- `Codai.models()` — list models available to the key.
- Zero dependencies (stdlib only), Python 3.9+.

[Unreleased]: https://github.com/codai-ro/codai-sdk-python/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/codai-ro/codai-sdk-python/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/codai-ro/codai-sdk-python/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/codai-ro/codai-sdk-python/releases/tag/v0.1.0
