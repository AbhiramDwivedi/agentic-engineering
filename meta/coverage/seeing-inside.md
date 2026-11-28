# Coverage map: Observability (chapter 8.1)

> Research-derived spec for what 8.1 must cover. Angles run: vendor and primary docs (OTel GenAI
> repo, OpenAI, Anthropic, Claude Code, Langfuse, LangSmith, Braintrust, OpenInference, MCP),
> OWASP (PII only), MAST, alias sweep, everyday-engineer gotchas. Skipped: incidents (no primary
> postmortem found). Review and trim **Must-cover**; that sets scope.

**Thesis.** An agent rarely fails the same way twice, so a parent-linked trace of model calls and
tool calls is the only record you can debug from, and the real design choices are what stays out
of the trace by default and what is redacted before export, not which dashboard you buy.

**Budget:** standard pattern, about 2,000 to 2,800 prose words to the end of *In short*.
**Who decides:** your code (telemetry engineering applied to a run whose shape is unknown ahead
of time). **Grounding:** research + companion repo. No "From production" callout; the stub's
`research + production` label must change.

## The mental model

A service fails the same way twice; an agent run does not, so "request failed" tells you
nothing. The reliable record is the run itself: every model call, tool call, argument, result
and decision, in order, with its parent, kept at a cost you chose in advance (what to capture,
how much to keep, who may read it). 7.2 Observer owns the in-process event pattern; 8.1 owns the
telemetry from the moment an event leaves the process: span shape, the OTel GenAI vocabulary,
sampling, redaction at export, and reading a trace.

## Must-cover

Ranked. `[+]` = gap (stub only).

1. **The trace is the unit** `[+]`. A root span per run, child spans per model call and tool
   call, parents preserved across fan-out. OTel GenAI operation names (values of
   `gen_ai.operation.name`): `chat`, `execute_tool` (span name `execute_tool {gen_ai.tool.name}`),
   `invoke_agent`. Parent linkage must survive process boundaries: W3C `traceparent` across
   async workers, and MCP carries it in `params._meta.traceparent` (SEP-414, Final). Use
   `gen_ai.conversation.id` to join multi-turn sessions across traces. *Skip it:* flat logs that
   cannot be rejoined. **Standard** (spans as structure); exact names Emerging.
2. **The OTel GenAI conventions: what they are and how stable** `[+]`. Status Development. They
   moved to `open-telemetry/semantic-conventions-genai` (release v0.1.0, 2026-11-21, with
   breaking changes since v1.41.0); the old repo's pages say "moved". Required:
   `gen_ai.operation.name`, `gen_ai.provider.name`. Recommended: token usage including cache and
   reasoning. Opt-In: `gen_ai.input.messages`, `gen_ai.output.messages`,
   `gen_ai.system_instructions`, `gen_ai.tool.definitions`. Metrics carry alerts and aggregates
   once traces are sampled (e.g. `gen_ai.client.operation.duration`); traces carry debugging.
   *Skip it:* hard-coded names that were renamed. **Emerging.** Teach the shape, pin a version.
3. **Platforms: choose by where the data lives** `[+]`. Langfuse, LangSmith and Phoenix ingest
   OTLP; three vocabularies coexist (OTel GenAI, OpenInference, vendor-native) and each vendor
   reads more than one. Trade-off: OTLP-first ingest keeps you portable; proprietary SDK calls
   lock you in. Self-hosting matters when PII (item 5) forbids SaaS: Phoenix is Elastic License
   2.0 (source-available, not OSI open source); OpenInference is Apache-2.0 per its repo; Langfuse
   is self-hostable. No feature tables (they rot). **Established** (category); **Emerging**
   (any product's features).
4. **Defaults are decisions** `[+]`. OpenAI Agents SDK: "Tracing is enabled by default",
   `trace_include_sensitive_data` defaults to `True`, unavailable under Zero Data Retention,
   `OPENAI_AGENTS_DISABLE_TRACING=1` turns it off. Claude Code: telemetry needs
   `CLAUDE_CODE_ENABLE_TELEMETRY=1`; traces are beta ("off by default") behind
   `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` plus `OTEL_TRACES_EXPORTER`; prompt content is a
   separate opt-in. One ships content-on, one content-off. *Skip it:* full prompts reach a third
   party unnoticed. **Emerging** (two tools, one labelled beta).
5. **What to log, the capture ladder, and PII** `[+]`. Always: run, step and parent ids,
   operation, model and provider, tokens (cache, reasoning), finish reason, latency, error class,
   tool name, result verdict. Gated: message content, tool arguments and results, system prompt.
   Content by reference (`gen_ai.input.messages_ref`) for large or sensitive payloads. The spec
   warns message attributes are "likely to contain sensitive information including user/PII
   data" (OWASP LLM02:2025). Redact in your process before export. Langfuse `mask_otel_spans` can
   set or delete span attributes only (not names, ids, parents, resource attributes), runs after
   media handling, and a hook that raises drops the whole export batch. Policy and retention
   → 8.5. *Skip it:* prompts with personal data in a SaaS indefinitely. **Established** (opt-in
   capture, redact before export); **Emerging** (automated exporter redaction).
6. **Sampling** `[+]`. Head sampling decides at trace start and "cannot guarantee" keeping
   errors; tail sampling sees the whole trace but is stateful and often vendor-specific.
   Langfuse samples client-side, all-or-nothing per trace (`sample_rate`; JS follows OTel
   samplers). Agent wrinkle: runs are expensive, so keep all failures and low-verdict runs and
   sample the healthy majority (reasoned, not measured). *Skip it:* a bill that scales with
   success, or traces missing the runs you need. **Established** (OTel concept); **Emerging**
   (agent policy).
7. **Instrumentation gotchas** `[+]`. Auto-instrument first, add thin manual spans for your own
   decisions. Tag `gen_ai.response.model` (not only request model) and a prompt or code version so
   silent alias changes do not read as random regressions. `gen_ai.usage.cache_read.input_tokens`
   is a subset of `gen_ai.usage.input_tokens` in the spec, so do not add them. Export in batches,
   not synchronously, so telemetry never blocks the loop. **Established.**
8. **Debugging from a trace** `[+]`. Find the first span where the run diverged from intent, not
   the last that errored; read the tool result the model saw; diff against a passing sibling;
   check finish reasons and empty returns first. Backdrop: MAST (Cemri et al., arXiv:2503.13657,
   v1 2025-03-17), 1,600+ annotated traces. Traces feed offline regression sets and online
   scorers; scores attach back to traces (Braintrust writes them as `score` spans) → 4.2.
   *Skip it:* traces and still guessing. **Emerging** (practitioner-reasoned).
9. **Cost attribution** `[+]`. Token attributes plus a tenant or feature attribute on the root
   span give cost per run, per loop iteration, per tenant. Provider billing APIs lag and do not
   group per run, so per-run cost comes from your spans; reconcile against billing (Anthropic's
   legacy report API lands in about 5 minutes; its Analytics API in about 4 hours, up to 24). The
   spec defines no dollar-cost attribute. Endpoints and budgets → 8.4. **Standard** (token counts
   on spans); **Emerging** (billing reconciliation).

## Mention-and-link

7.2 Observer (in-process events, hook failure); 4.2 Evaluation (judges, calibration); 8.5 (PII
policy, retention, consent); 8.4 (cost levers, billing APIs); 2.5, 3.7 (stop conditions); 2.6
(harness hooks); 6.3 (streaming); 8.6 (governance); 8.7 (runtimes, liveness).

## Out of scope

Collector deployment beyond one path; vendor comparison tables; general SRE practice.

## Maturity summary

- **Standard:** spans, trace and parent ids, token counts on model calls.
- **Established:** tracing practice, OTLP transport, head vs tail sampling, opt-in capture and
  redact before export, instrumentation hygiene.
- **Emerging:** the OTel GenAI conventions, default-posture contrast, agent sampling policy,
  trace-driven debugging, billing reconciliation, automated redaction.
- **Contested:** vendor "OTel GenAI compliant" claims against a Development spec; uncalibrated
  online LLM-as-judge scoring; default-on full-prompt tracing.
- **Verdict:** Established (tracing practice) with Emerging (OTel GenAI conventions, online
  evals); keep "Last reviewed".

## Aliases

tracing, monitoring, telemetry (stub); LLM observability, agent observability, LLM tracing
(vendor docs); distributed tracing; execution trace. Book and framework aliases need author
sign-off; none invented.

## Reader-verifiable anchors

1. OpenAI Agents SDK: tracing is on by default; `OPENAI_AGENTS_DISABLE_TRACING=1` disables it.
2. Claude Code: with `CLAUDE_CODE_ENABLE_TELEMETRY=1` and `OTEL_LOGS_EXPORTER=console`,
   `OTEL_LOG_USER_PROMPTS` unset redacts prompt content; `1` includes it. This verifies event
   logging; trace export is a separate beta.

## Named-idea candidates

**Capture ladder** (ids always, content gated, content by reference): local plain wording, not
canon. Zero forced.

## Code seam

Listing-studio: a self-contained `telemetry/` package with its own minimal sink protocol (no
dependency on 7.2's `observer/`). An in-memory span exporter and a redacting span processor:
(a) a model span carries token counts and no content by default, (b) opt-in captures content,
(c) the redactor removes a merchant contact string from an attribute before export, (d) a raising
redactor does not crash the run. New pinned dependency `opentelemetry-sdk`. No vendor backend in
tests. **Code warranted**, small.

## Carrier

Listing Studio fan-out for span trees and propagation; Merchant helpdesk or Shopper assistant
for `gen_ai.conversation.id` and PII; Repricer for loop cost attribution.

## Sources

OTel GenAI conventions, `semantic-conventions-genai` v0.1.0 (`execute-tool.md`,
`client-inference.md`, `gen-ai-metrics.md`); OTel "Sampling"; OpenAI Agents SDK Tracing; Claude
Code Monitoring (code.claude.com/docs/en/monitoring-usage); Langfuse OTel, masking and sampling
pages; LangSmith OTel; Braintrust Online scoring (docs.braintrust.dev/observe/score-online);
OpenInference; Phoenix repo (ELv2); MCP SEP-414; Anthropic Usage and Cost API and Analytics API;
OWASP LLM02:2025; Cemri et al., arXiv:2503.13657.

> **Verify before quoting:** the spec surface moved in 2026; pin a release at draft time. Claude
> Code trace span names are unread; no sampling control was found. Token-usage metric names were
> not read exactly.

## Open questions for the author

1. Confirm grounding `research + companion repo` and drop the stub's production label.
2. Hand online evals fully to 4.2 (this map keeps two sentences).
3. Keep `telemetry/` decoupled from 7.2's `observer/`?
4. Adopt the split verdict (Established practice, Emerging conventions)?
5. Which book or framework aliases to carry in the "Also called" line?

## Map review (Stage 1.5)

Reviewer: an independent second engine. Disposition per finding (12 total).

1. Thesis, budget, litmus, grounding: accepted; header added, stub label flagged in open questions.
2. `execute_tool` and Anthropic billing: accepted; both verified on the primary pages, billing details moved to 8.4.
3. Propagation, conversation id, metrics: accepted-modified; SEP-414 and `conversation.id` verified, only `gen_ai.client.operation.duration` named because token metric names were not read.
4. Unverified claims and local dependency: accepted; Braintrust, Langfuse sampling, MAST re-opened, Claude Code sampling control not found, seam decoupled.
5. Bloat and seam creep: accepted; ten items folded to nine, online evals and billing details handed off.
6. Maturity verdicts: accepted-modified; downgraded and Contested filled, kept my own tier wording.
7. Everyday gotchas and OWASP: accepted-modified; OWASP and cache-token subset verified, OpenAI streaming-usage claim dropped as unverified.
8. Phoenix license and `mask_otel_spans`: accepted; ELv2 and attribute-only scope verified.
9. Open questions and carrier: accepted; added, email PII recast as merchant contact.
10. Aliases: accepted-modified; mechanics and heartbeat removed, Gulli titles not added (unopened here).
11. Anchor 2: accepted; env vars verified.
12. Hygiene: accepted; CI aside and v1.45.0 removed, capture ladder labelled local.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Grounding.** Change the stub's production label to research plus companion repo. (Author checklist.)
2. **Maturity.** Split verdict. The top line reads Established, the prose argues it, and the OTel GenAI conventions and online evals are named Emerging. (Author checklist.)
3. **Online evals.** Mention them only and point to 4.2 in plain text. The depth lives there.
4. **Code.** Approve `listing-studio/telemetry/`, decoupled from 7.2's `observer/`, using its own minimal sink. It covers the four tests named in the map. Tests use stdlib and pydantic only.
5. **Aliases.** Do not add an "Also called" line, since aliases need author sign-off. (Author checklist.)
6. **Unverified items.** The OpenAI streaming-usage gotcha and the exact OTel token-metric names stay out.
7. **Excluded.** No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

Inputs: prose critic, fact-checker, cold reader, and the second-engine draft review. Each finding was checked before acting.

1. Hook overpromises (Why vs Gotcha 1): fixed. The trace paragraph now says ids alone show order and outcome, and content capture is needed to find which step wrote 300; Gotcha 1 names the setting (`capture_content=True` behind `RedactingSink`, or `messages_ref`).
2. Three candidate causes never told apart: fixed. "Reading a trace" walks the desk ticket through what each cause looks like in the spans.
3. Thesis only in the closer: fixed. Stated at the end of the trace paragraph in Why.
4. `gen_ai.provider.name` required on every span: fixed. Verified against the v0.1.0 release notes; now model-call span only, and the tool span requires `gen_ai.tool.name`.
5. MAST "built by annotating 1,600+ traces": fixed. Verified against the arXiv abstract: built from 150 traces, dataset of 1,600+.
6. Usage and Cost API: fixed. Verified the page labels it legacy; prose and footnote say so.
7. Undefined terms: fixed. Glossed Sink, ContextVar, baggage, tracestate, SEP-414, `_meta`, Zero Data Retention, online scorers, regression sets, Phoenix; head and tail sampling defined at first use. "Tenant" replaced with "customer".
8. Link 4.2 Evaluation: rejected. It is still `(planned)` on main, so it stays plain text.
9. Repeated "X, not Y" disclaimers: fixed. Soft contrast flags went from 3 to 0.
10. Prose critic, abstraction with no instance in "Reading a trace": fixed (see 2).
11. Prose critic, L13 restates L9: softened. Cut the restating sentence in L9; kept the L13 line the cold reader would quote.
12. Prose critic, ZDR antecedent: fixed.
13. Prose critic, "vendor hooks" generalised from one vendor: fixed, now names Langfuse.
14. Prose critic, apparatus narration and announcing openers: fixed (four openers removed).
15. Prose critic, `conversation.id` non sequitur in the cross-process paragraph: fixed by cutting the sentence.
16. Prose critic, cliché closer in Security: fixed by cutting it.
17. Prose critic, "you pay per token" trigger: fixed, now cost attribution.
18. Prose critic, "token usage is recommended" reads as advice: fixed, attributed to the spec.
19. Prose critic, "distributed tracing backend": fixed.
20. Cold reader, why metrics survive sampling: fixed with one clause.
21. Cold reader, "a check" undefined: fixed ("an automated check").
22. Cold reader, build gaps (imports, a printing sink, real SDK reply shapes): rejected. The companion module carries the imports and an in-memory sink; word budget.
23. Cold reader, alt text too long: fixed, roughly halved with the same content.
24. Fact-checker, metric name: fixed by removing it. The second engine showed v0.1.0 moved inference off `gen_ai.client.operation.duration`; ruling 6 keeps exact metric names out.
25. Second engine, exporter failure can terminate the run: fixed. `span()` now swallows an exporter error; new test with a raising sink.
26. Second engine, captured input mutates after export: fixed. `traced_chat` stores a copy of the message list; new test.
27. Second engine, no error status or timestamps on spans: rejected for this chapter. The capture policy names error class and latency; extending the minimal tracer is out of budget.
28. Second engine, message payloads do not follow the spec's structured schema: rejected. The companion tracer is a minimal illustration; noted for the author.
29. Second engine, opening overclaims against the capture policy: softened by the fix in 1.
30. Second engine, "keep every failure" lacks implementation conditions: rejected. The paragraph already ties keeping failures to tail sampling and labels the policy unmeasured.
31. Second engine, Langfuse hook runs after media handling: rejected for budget; the cited page states it.
32. Second engine, observability confined to exported traces: rejected. The boundary with 7.2 is the map's scope call; on the author checklist.
33. Second engine, OTLP transport is not semantic portability: rejected. The text already says platforms map several vocabularies.
34. Second engine, alias line overrides ruling 5: rejected. The line predates the draft, in the stub already on main; left for the author.
35. Second engine, SDK listing is not "the same tree": fixed, now described as the root and first model-call span.
36. Second engine, Braintrust claim unverifiable: rejected. The fact-checker confirmed the quoted wording at the cited page.
