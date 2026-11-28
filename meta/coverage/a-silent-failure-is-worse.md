# Coverage map: Observer (chapter 7.2)

> Research-derived spec for what 7.2 must cover to let a reader make every step of an agent run
> report itself, and where to stop. Angles run: vendor/primary docs, academic (one paper),
> failure modes (stop reasons, async), daily-tool, alias sweep, skeptical read (event noise, PII
> in sinks, model self-narration sold as observability). Skipped: OWASP, practitioner postmortems.
> Budget: Standard pattern chapter, about 2,000 to 2,800 prose words.

**Thesis.** Agent steps fail quietly (a refusal or truncation returned as HTTP 200, an empty
turn, a swallowed hook crash), so an observer that reports only exceptions leaves every UI and
dashboard lying; your code must emit fail-open, read-only events at every step boundary, empty and
degraded finishes included.

> Review and trim **Must-cover**; that sets scope. Bar: definitive but tight.

## The mental model (what the reader must leave with)

An agent run is a chain of steps your code owns, and any step can end without raising: an empty
result, a refusal returned as a normal response, a truncated answer, an exception swallowed in a
callback or a background task. The observer rule is that every step emits an event when it
starts, finishes or fails, to subscribers that cannot change the outcome. Code decides this, so
it is engineering the reader already knows, applied to a loop where the failures are quiet. Model-narrated status text is model-decided and unreliable; these events are code-decided at real step boundaries. Two
audiences read the same events: the user gets status, the operator gets telemetry. This chapter
owns the in-process event pattern; 8.1 owns what happens to events once they leave the process.

## Must-cover

Ranked. `[+]` = gap (stub only).

1. **The rule: an event on every step boundary, including the failure branch** `[+]`. Three
   lifecycle kinds (`start`, `end`, `error`); `end` carries an `outcome` of `ok`, `empty`,
   `partial` or `refused`, so a quiet finish is never read as success. *Skip it:* a path
   reports nothing and the UI shows progress that is not real. **Standard.** (Anthropic,
   "Building effective agents": agents "gain ground truth from the environment at each step".)
2. **The observer contract: publish without being able to affect the run** `[+]`. Subscribers
   are read-only; a slow or crashing one must not break or stall the run; run and step ids ride
   every event. Async sinks lose events quietly: a task with no strong reference "may get garbage
   collected at any time" (Python asyncio-task docs), unbounded queues grow, buffers vanish on
   exit. Use bounded drop-on-full queues and flush on shutdown (OpenTelemetry trace SDK
   `BatchSpanProcessor`; cancellation flush links to 7.3). *Skip it:* a logging bug kills a run.
   **Standard.** (Gamma et al. 1994 for the subject/observer split only, unopened.)
3. **The silent-failure catalog** `[+]`. HTTP 200 failures exist on every provider; the wire
   fields differ:
   - Anthropic: `refusal` is "a normal HTTP 200 response, not an error"; `max_tokens` truncates,
     even mid tool-use block; `end_turn` can carry empty content.
   - OpenAI Responses: `incomplete_details.reason` (`max_output_tokens`, `content_filter`);
     refusals as `type: "refusal"` content items.
   - Gemini: `finishReason` other than `STOP` (`MAX_TOKENS`, `SAFETY`, `RECITATION`,
     `MALFORMED_FUNCTION_CALL`).
   - Orchestration: a fan-out worker that returns nothing; a gate that fails with no message;
     `MaxTurnsExceeded` swallowed by a catch-all.
   - Language: an unretrieved asyncio exception logs only "Task exception was never retrieved".
   *Skip it:* success reported on an empty or partial result. **Standard** for checking stop
   reasons; the orchestration items are illustrative and uncited.
4. **Hooks as the in-process observer surface** `[+]`. Teach the shared pattern, put SDK
   specifics in provider tabs. Verified names: OpenAI Agents SDK `RunHooks` has `on_agent_start`,
   `on_agent_end`; `AgentHooks` has `on_start`, `on_end`; both have tool, llm and handoff hooks,
   and neither has an error hook. LangGraph `stream_mode` (`updates`, `custom`, `tasks`, `debug`)
   with `get_stream_writer()`. Claude Code: observe-only events are `Notification`,
   `SessionStart`, `StopFailure`; `Stop` and `SubagentStop` can block with exit 2, and
   `PostToolUse` can inject context, so those are harness, not observers. LangChain
   `on_tool_error`, `on_llm_error`, `on_chain_error`, `raise_error=False` by default. Google ADK
   `BasePlugin` has `on_model_error_callback` and `on_tool_error_callback`, but returning a value
   there recovers from the error, so it straddles observer and 7.1. OpenAI `error_handlers`
   (`model_refusal`, `ModelRefusalError`) are recovery overrides, contrast in 7.1. *Skip it:* the
   reader hand-rolls events the framework emits. **Standard**; names are volatile.
5. **Hook failure is itself a silent failure** `[+]`. Claude Code: exit 1 is a "non-blocking
   error", the action proceeds; `onFailure: "block"` (v2.1.295+) turns a crash, timeout or
   invalid output into a block, and has no effect on `Stop`, `SubagentStop` or background hooks.
   Claude Agent SDK: a throwing callback surfaces as `hook_callback_failed`; LangChain
   `raise_error=False`. Fix: observers fail open, a heartbeat or counter notices a dead sink,
   guards (2.6) fail closed. **Established.**
6. **One stream, two projections** `[+]`. User view short, ordered and tied to real events;
   operator view carries ids, durations, tokens, error classes. Never raw exceptions or prompts to
   the user. Rendering is 6.3; redaction is 8.5. **Established** (two SDK features, not a
   standard).
7. **Structural result check on the end event** `[+]`. The code sets `outcome` from presence and
   stop reason only; semantic verification is owned by 2.2, 3.1, 3.7 and 4.2, and the observer
   forwards their verdicts. MAST (Cemri et al., arXiv:2503.13657, NeurIPS 2025 Datasets and
   Benchmarks) documents task-verification failures across 1,600+ multi-agent traces; it shows
   the problem, not this fix. **Established.**
8. **Event schema minimum** `[+]`. `run_id`, `step_id`, `parent_id`, `kind`, `outcome`,
   monotonic timestamp, error class, redacted message, no user data by default. Parent id keeps
   fan-out reconstructable. **Established**, no standard. OTel GenAI semantic conventions are in
   Development status, so alignment with 8.1's attributes is **Emerging**.

## Mention-and-link

- **Tracing, OTel, dashboards, alerting, cost telemetry** -> 8.1. 7.2 ends where events leave the
  process.
- **Streaming to the browser, SSE, progress UI** -> 6.3. 7.2 supplies events; 6.3 renders them.
- **Hooks that gate** -> 2.6. A hook that can change the outcome is harness; one that cannot is
  observer. The observer sits outside the context window (zero token cost); feeding errors back
  into context is 1.5, 2.5, 3.7 and 7.1 (12-Factor Agents, Factor 9).
- **Retry, fallback, what stops the run** -> 7.1. Observer reports; 7.1 decides.
- **Checkpoint and resume** -> 7.3. **Loop caps** -> 2.5, 3.7. **Eval of traces** -> 4.2.
- **PII, locks, identity** -> 8.5.

## Out of scope

- Vendor tracing backends, OTel exporter setup, log retention, sampling -> 8.1.
- Building a UI for the events -> 6.3. SDK-by-SDK reference tables.

## Maturity summary

- **Standard:** emit on every step boundary; check provider stop reasons; hook surfaces exist in
  every major SDK.
- **Established:** the event and outcome schema; hook-failure handling; the two-projection split.
- **Emerging:** OTel GenAI attribute alignment; per-SDK event names ("Last reviewed").
- **Contested:** none found. Skeptical read (event noise, PII in sinks, self-narration) is
  covered as gotchas, not a dispute. Lens line to write: Maturity: Standard, Who decides: your
  code, Grounding: companion repo and cited research, Last reviewed: 2026-11. The stub's
  `Grounding: production` is not supported and is dropped.

## Aliases

callbacks (LangChain `BaseCallbackHandler`), hooks (Claude Code, Claude Agent SDK, OpenAI
`RunHooks`), lifecycle events (OpenAI Agents SDK module `lifecycle`), callbacks and plugins
(Google ADK), streaming events or stream modes (LangGraph). `middleware` is not a synonym: it
intercepts execution and belongs to 2.6.

## Reader-verifiable anchors

1. Claude Code: on `PreToolUse` with default `onFailure`, a hook that exits 1 is a "non-blocking
   error" and the action proceeds; exit 2 blocks. A one-line failing hook shows it.
2. Anthropic: `refusal` is a normal HTTP 200. Reproduce on demand with `max_tokens: 1`
   (`max_tokens` stop reason) or OpenAI `incomplete_details`, as refusals are hard to trigger.

## Incidents

None found with a primary postmortem. The July 2025 Replit database-deletion account (the agent
reportedly misreported recovery options) rests on the user's own posts and secondary reports, so
it is not cited; it belongs to 4.3/4.4 if used at all. Candidate for the Incident File if the
author wants a primary-source search later.

## Named-idea candidates (author accepts or strikes)

- **The observer rule** (already used in the catalog and nav; a restatement, not a coinage).
- **Outcome on every end** (plain wording only; no coinage).

## Code seam

Listing-studio package `observer/` (new, small): `EventSink` protocol, `emit()` that isolates
subscriber exceptions, and an instrumented wrapper over stubbed step callables that return a
`stop_reason`, since `prompt_chaining/chain.py` and `fan_out/gather.py` expose no per-step hooks
today (an optional `sink` parameter is the alternative). Anchored on Listing Studio's nine-step
graph (step 9, publish) and its live dashboard. Tests: (a) a raising sink does not break the run,
(b) an empty worker result ends with `outcome=empty`, (c) a `refusal` stop reason gives
`outcome=refused`, (d) a full queue drops and counts. Offline, no key. Provider tabs: LangGraph,
OpenAI Responses, Anthropic Messages. Code warranted.

## Sources

Anthropic, "Building effective agents" (anthropic.com/research/building-effective-agents).
Anthropic, "Handling stop reasons" (platform.claude.com/docs/en/build-with-claude/handling-stop-reasons).
Claude Agent SDK, "Intercept and control agent behavior with hooks"
(code.claude.com/docs/en/agent-sdk/hooks). Claude Code hooks reference
(code.claude.com/docs/en/hooks). LangGraph streaming (docs.langchain.com/oss/python/langgraph/streaming).
OpenAI Agents SDK lifecycle reference (openai.github.io/openai-agents-python/ref/lifecycle/) and
running agents (openai.github.io/openai-agents-python/running_agents/). langchain-core
`callbacks/base.py` (github.com/langchain-ai/langchain). Python asyncio-dev and asyncio-task docs (docs.python.org/3/library/). OpenAI Responses API
reference; Gemini API `FinishReason`; Google ADK plugins (adk.dev/plugins/); OpenTelemetry trace SDK. Cemri et al., "Why Do Multi-Agent LLM Systems
Fail?", arXiv:2503.13657 (submitted 2025-03-17, v3 2025-10-26; Cemri, Pan, Yang, Agrawal, Chopra,
Tiwari, Keutzer, Parameswaran, Klein, Ramchandran, Zaharia, Gonzalez, Stoica).

> **Verify before quoting:** Gamma et al. (1994) unopened. Hook names, `onFailure` versions and
> LangGraph `version="v2"` change often; re-open at draft time. OpenAI `.stream_events()` types
> and the top-level Responses `status` field were not read. Confirm `raise_error` by test.
> The `BatchSpanProcessor` and OTel GenAI status claims were not opened; check the OTel pages.

## Map review (Stage 1.5)

Reviewer: independent second engine. Findings checked against the pages and repo files.

1. Lens line and `production` grounding: accepted, stub claim dropped, full lens line given.
2. Thesis, budget, open questions: accepted, all added.
3. Four-event vs verdict contradiction: accepted-modified, three kinds plus `outcome`, "Four events" struck.
4. SDK errors in item 4: accepted, `on_start`/`on_end`, hook blocking and `onFailure: "block"` verified on the docs; `error_handlers` moved to a 7.1 contrast.
5. Cross-provider stop reasons: accepted-modified, `incomplete_details` and Gemini `finishReason` verified; top-level `status: "incomplete"` not confirmed, so omitted.
6. Google ADK and context boundary: accepted, ADK plugin callbacks verified (error callbacks recover).
7. Async observer failures: accepted, asyncio docs verified; OTel spec cited but unopened (flagged).
8. Seam violations and table bloat: accepted, items 4, 6, 7 narrowed.
9. Verdicts and skeptical read: accepted-modified, schema and split downgraded to Established, OTel alignment Emerging.
10. Citations: accepted-modified, Gamma scoped, MAST venue added, URLs fixed, Anthropic quote trimmed.
11. Carrier and seam: accepted, nine-step graph confirmed in carrier bible; "step 3 of 5" removed; tabs aligned.
12. Alias sweep: accepted-modified, `middleware` removed; Gulli rows not added (not re-read).
13. Anchor scoping: accepted.
14. Model-narration contrast: accepted, one sentence.
15. Links, URL drift, fetch notes: accepted, 8.5 and 1.5 linked, standard URL used.

## Open questions for the author

1. Item 7 seam: is a structural-only `outcome` acceptable, with semantics left to 2.2/3.7?
2. Is `outcome=refused` on `end` (not `error`) the right call for a refusal?
3. Drop `Grounding: production` for companion repo and research, or supply a first-hand claim?

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis as folded. The verdict is Standard. The schema and hook-failure handling are Established, and OTel GenAI alignment is Emerging with one sentence. 8.1 owns OTel in depth (plain text).
2. Grounding changes from the stub's `production` to companion repo plus research. (Author checklist.)
3. `outcome` is structural only: ok, empty, truncated, refused, error. A refusal is `outcome=refused` on the `end` event, not an error event, because a refusal is a completed step with a bad result. (Author checklist.)
4. Code: a new `listing-studio/observer/` package as the map specifies, offline, tested on stdlib, pydantic and anyio/asyncio only.
5. Unopened OTel claims (BatchSpanProcessor, GenAI status) ship only if the fact-checker opens them; otherwise cut. OpenAI top-level `status: "incomplete"` stays omitted.
6. No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

Sources: prose critic (PC), fact checker (FC), cold reader (CR), second-engine draft review by OpenAI Codex (CX).

- PC1/CX3, callout and See also made the observer control flow: fixed. The publish gate reads `outcome_of(result)` from the returned `StepResult`, never the event stream, because the bounded queue can drop events; See also for 3.1 says the same.
- PC2/FC5/CX1, LangGraph map sent Anthropic `max_tokens`/`refusal` to `end_turn`: fixed in `observer_langgraph.py` and the chapter (`NORMALISED` map covering OpenAI and Anthropic values, `model_context_window_exceeded` included); prose says to extend it per provider.
- FC4/CX1, OpenAI tab ignored `content_filter`: fixed. Filtered reads as refusal, any other incomplete reason as truncation (conservative for unknown reasons).
- CX1, Anthropic `model_context_window_exceeded` read as `ok`: fixed in `observer_example.py`; verified against Anthropic's stop-reasons page, which says to treat it as truncated.
- CX1, reverse the ruling that omits Responses `status`: rejected. Any non-null `incomplete_details` is now treated as an early stop, which covers the case without the extra field.
- CX2, `outcome_of` outside the `try` (a `None` result emitted only `start`): fixed; classification moved inside, new test `test_malformed_result_emits_error_not_just_start`. Cancellation and async callables: rejected for this chapter; the wrapper is synchronous and cancellation belongs with 7.3.
- PC3/CX16, "three events per step": fixed to two events per step.
- CX16, asyncio "one line": fixed to a logged diagnostic with its traceback.
- FC1/CX13, OTel URL moved: fixed to the semantic-conventions-genai README; Development status re-verified there.
- FC3, OpenAI link 301: fixed to developers.openai.com; `incomplete_details.reason` values and the `refusal` content item re-verified; prose now says "for example".
- FC2, NeurIPS venue unconfirmed: softened to arXiv:2503.13657 (OpenReview could not be read).
- FC8, "nine steps": kept; it is the carrier bible's canonical step table (nine rows). The bible's "to be confirmed" caveat is about the thirty-call count, which the chapter does not use.
- FC8, "a fan-out worker hands back nothing" uncited: softened to "can hand back nothing".
- CR, undefined terms: fixed by glossing fan-out, harness, middleware, batch span processor, OpenTelemetry and its semantic conventions, fail open/closed, normalised, and 12-Factor Agents' ninth factor. Claude Code hook names stay as cited names.
- CR build test, imports and consumer: fixed. The first code block now shows its imports and `logger`; a note says where `llm` and `client` come from; the chapter says it covers the emitting side and that the retry and gate code reads the outcome from the result. Companion test path named.
- CR, unlinked chapter numbers (2.6, 7.1, 7.3, 8.1, 6.3, 8.5, 3.7): rejected; those chapters are unmerged and stay plain text by convention.
- CR, "gpt-6.2-sol" looks invented: rejected; intentional model ID.
- PC4/CX12, tagline overclaims: fixed ("a step that ends badly says so even when it did not raise"); the opening's "every screen" softened to "the screens ... can show".
- PC5/CX9, token counts not in the event, and verdicts "forwarded as events of their own": fixed. Token counts dropped; a gate wrapped as its own step reports its verdict the same way.
- PC6, apparatus narration: fixed (catalog line cut; 8.1 pointer reworded).
- PC7/CX11, maturity labels narrated in prose: fixed. The paragraph argues plainly, says the schema is this example's design, and cites provider docs for stop-reason checks. Lens-line verdict unchanged (Standard, carve-outs per ruling 1).
- PC8, paragraph with six topics and an asyncio non sequitur: fixed; split, and the traps now apply to "the reader ... a thread or an asyncio task".
- PC9, comments re-teach prose: partly fixed (walkthrough and `raise` paragraph rewritten); code comments kept.
- PC10, privacy argument duplicated: fixed; the outcome paragraph now points to Gotcha 5.
- PC11, closing line repeated: fixed; In short ends on the heartbeat instruction.
- PC12, carrier step names: fixed; the scenario names step 4 write copy, step 8 brand-voice polish and step 9 publish.
- PC13, walkthrough restates code: fixed; compressed to one sentence.
- PC14, colon setup: fixed.
- CX4, `step_id` is per name, not per invocation: softened; prose says to add a per-invocation counter for retries or same-named workers. Code unchanged.
- CX5, `logger.exception` leaks the sink's message: fixed; `emit` logs the class name only, new test `test_sink_failure_logs_class_name_only`.
- CX6, `SessionStart` is not observe-only: fixed; dropped from the observe list, and the prose says the line runs through what a callback does.
- CX7, sinks still run synchronously: fixed by stating it; the draining reader is named as the reader's job, with a time-limited shutdown flush.
- CX8, provider tabs only compile-checked: rejected for now. Companion tests may import only stdlib, pydantic, mcp and anyio, so SDK response fixtures cannot run here; the core mapping is tested in `events.py`.
- CX10, SVG showed "run continues" after a raising step and numbered steps 1 to 3: fixed; labels are steps 1, 4 and 9, the error arrow reads "raises to the caller", and desc and alt text are updated.
- CX14, Windows exit-code exception and LangGraph `tasks` checkpointer prerequisite: rejected as not re-verified here; the chapter's claims stand as cited.
- CX15, alias sweep against both Gulli books unfinished: deferred to the author; aliases unchanged.
- FC6, FC7, FC9, FC10: no change needed.
