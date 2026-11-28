# Coverage map: Retry & Graceful Degradation (chapter 7.1)

> Spec for what the chapter must cover so a reader can decide, per failure, what to retry, what to
> fall back on, and what should stop the run. Angles run: vendor docs (Anthropic, OpenAI, Stripe),
> distributed-systems canon (AWS, Google SRE, Fowler), daily-tool SDK defaults, alias sweep.
> Skipped: academic benchmarks (no founding LLM paper exists; say so), OWASP (4.4), practitioner
> writeups beyond one 12-Factor Agents cite, incidents (none with a primary source).
> **Prose budget:** about 2,200 words (a deflation with one constructive answer, not a survey).

**Thesis (falsifiable):** Unclassified retries do more damage in an agent than in a web service,
because the SDK already retries under you, one 429 can be a rate limit or a hard spend cap, and
replaying a timed-out write tool turns a blip into a duplicate action; so classify each failure
before you retry, fall back, or stop.

## Mental model

The "your code decides" half of the litmus: old engineering with a model in the slot. Every failure
is transient (retry with backoff, jitter, a budget), recoverable by substitution (cheaper tier,
second provider), or terminal (stop and say so). Wrong retry amplifies an outage or double-charges;
wrong stop turns a blip into an incident.

## Must-cover

1. **Classify first** `[+]`. Transient: 408, 429 (rate), 5xx, Anthropic 529 (`overloaded_error`;
   OpenAI's analogue is 503), timeouts, 409 only for a transient lock conflict. Terminal: 400,
   401, 403, 404, 413. Spend caps are terminal despite their code: Anthropic returns a 400 for a
   spend limit you set, and a 429 `rate_limit_error` with `enforced_spend_limit_reached` and no
   `retry-after` for the tier monthly cap; OpenAI `insufficient_quota` is also a 429. HTTP 200
   failures count: `max_tokens` truncation and safety refusals are terminal stops (never fail over
   around a refusal; see 4.4); context overflow is recoverable by compaction, not retry (see 5.4).
   **Standard.** (Anthropic API errors, opened; OpenAI error codes; stop reasons to re-verify.)
2. **Backoff with full jitter, bounded** `[+]`. Honour `retry-after`; cap attempts and elapsed
   time. **Standard.** (Brooker 2015; SRE ch. 22.)
3. **What the SDKs already do; one layer owns retry** `[+]`. Anthropic and OpenAI Python SDKs both
   default to 2 retries (3 total attempts), jittered backoff of about 0.5 to 8 s, `x-should-retry`
   then `retry-after`, 10-minute timeout. LangGraph `RetryPolicy` (`max_attempts=3`, to re-verify)
   stacks on top: 3 x 3 = 9 attempts per call out of the box. Pick one owner, set `max_retries`
   to match. **Standard.** (SDK docs; SRE ch. 22.)
4. **Retry budgets and shedding** `[+]`. SRE gives two budgets: ch. 21 (Cuervo) a per-request cap
   of three attempts plus a per-client rule that retries continue only while the retry ratio stays
   below 10%; ch. 22 (Ulrich) a per-process example of 60 retries per minute. **Standard.**
5. **Timeouts, deadlines, streams** `[+]`. A timeout means unknown outcome: the call may still
   bill and a write may still commit. Use one end-to-end deadline per run, not independent
   per-call timeouts. A stream can error after a 200 (Anthropic SSE `error` event; OpenAI
   `response.failed` and `response.incomplete`); decide whether to discard partial output.
   **Standard** (timeouts); **Established** (mid-stream recovery). (Brooker 2019, to open; SRE
   ch. 22 deadlines; vendor streaming docs.)
6. **Idempotency of tool side effects** `[+]`. Retrying the model call is safe; replaying a tool
   that ran is not. Two replays: transport retry, and the model re-calling after an error. Key
   derived from run and step, reused on resume. Stripe: key header, first response replayed
   (including cached 500s), keys kept at least 24 hours then reusable. **Standard** (keys);
   **Established** (for agent tools). (Stripe idempotent requests.)
7. **The litmus boundary** `[+]`. Code retries transport failures silently; a semantic tool
   failure crosses into the model loop as a compact error (`is_error` on Anthropic and MCP
   `isError`; OpenAI has no flag, only a string in `output`), costing context each time (12-Factor
   Agents factor 9). The re-call loop belongs to 2.1, 2.5, 2.6. **Established.**
8. **Degradation ladder and failover** `[+]`. Full agent, smaller same-provider model, cached or
   templated result, queue and tell the user, clear failure. Trigger after retries are spent.
   Label degraded answers; never substitute silently. Same-provider tier fallback is
   **Established**; automatic cross-provider failover is **Emerging**: provider wire state
   (`previous_response_id`, signed thinking blocks) cannot cross, so keep canonical app-owned
   message state (5.1, 7.3), and cache hits are lost. Test the fallback path. Cost-driven
   cascades belong to 8.4, gateways to 8.2.
9. **Circuit breakers** `[+]`. Closed, open, half-open; per provider or model. Caveat: per-process
   breakers do not share state across workers and misfire at low request volume. **Standard.**
   (Fowler, 6 March 2014; Nygard not opened.)

## Mention-and-link

Verify-and-retry on quality → 3.7 (a verifier crash is a 7.1 failure, not a 3.7 attempt).
Harness, stop conditions → 2.6; inner loop → 2.5. Resume, replay, dead letters → 7.3.
Observer → 7.2. Human escalation → 4.3. Compaction → 5.4. Safety failover → 4.4. Gateway → 8.2;
cost → 8.4. Schema re-ask → 2.2. Supervisors, watchdogs → 8.7. Tool errors → 6.3.

## Out of scope

SDK minutiae beyond defaults; building a gateway; batch API retries.

## Maturity summary

Standard: classification, backoff, budgets, timeouts, idempotency keys, breakers, degradation as
principle. Established: agent-tool idempotency, `is_error` contract, same-provider fallback,
mid-stream recovery. Emerging: automatic cross-provider failover. **Contested:** unbounded
"self-healing" model retries, and drop-in failover without per-provider evals. Chapter verdict:
**Standard**, argued as old practice with a model in the slot.

## Aliases (all need author sign-off)

resilience, backoff, fallback (stub). Also: exception handling and recovery (Gulli, *Agentic
Design Patterns*, 2025, ch. 12), fault tolerance, failover, load shedding, circuit breaker,
fallback chain, degradation ladder; "self-healing" to deflate. Gulli and Nawalgaria (2026)
chapter per alias to be recorded before shipping. "Graceful degradation" vs "graceful shutdown"
(7.3) merits one sentence.

## Reader-verifiable anchors

- In a REPL, `Anthropic().max_retries` and `OpenAI().max_retries` print `2`; `.timeout` shows 600.
- LangGraph `RetryPolicy()` prints `max_attempts=3`, `jitter=True`. SDK debug logging shows
  `x-should-retry` and `retry-after` on a real response.

## Named-idea candidates (accept or strike)

**Retry only what could succeed.** **One layer owns retry** (from SRE ch. 22).

## Carrier

Listing Studio step 4 (`write copy`) on the Aldsworth desk carries the timeout case; Repricer
carries idempotency on `price_cents` writes; the shopper assistant carries the ladder. Examples are
carrier illustrations; no production claims. **Stub fix:** change the stub's `Grounding: production`
to `research + companion repo` (or `research` if no code ships).

## Sources

Anthropic, "Errors" (platform.claude.com/docs/en/api/errors); Anthropic Python SDK and "Handle
tool calls" docs; OpenAI "Error codes" and openai-python README; Stripe "Idempotent requests";
Brooker, "Exponential Backoff And Jitter," AWS Architecture Blog, 4 March 2015, and "Timeouts,
retries, and backoff with jitter," Amazon Builders' Library, 2019 (not opened); Cuervo, "Handling
Overload," ch. 21, and Ulrich, "Addressing Cascading Failures," ch. 22, *Site Reliability
Engineering* (O'Reilly, 2016); Fowler, "CircuitBreaker," 6 March 2014. Re-open SDK defaults before
shipping.

## Open questions for the author

1. Sign off the aliases and the two named-idea candidates.
2. Cross-provider failover: teach as Emerging with costs, or one paragraph only?
3. Companion code, or prose only? (Grounding label depends on it.)
4. Prose budget of about 2,200 words: accept?

## Map review (Stage 1.5)

1. Thesis, budget, open questions missing: accepted, added.
2. SRE 10% budget: accepted, verified in ch. 21 (Cuervo); my warning was wrong.
3. 400 vs 429 spend limit: accepted, verified in Anthropic errors page.
4. HTTP 200 stops and context overflow: accepted-modified, stop reasons and OpenAI events flagged to re-verify.
5. Timeout ambiguity, deadlines, wire state: accepted, Brooker 2019 flagged unopened.
6. Item 7 litmus blur, merge 8 and 9, links: accepted.
7. Maturity downgrades and Contested list: accepted.
8. Aliases: accepted-modified, Gulli chapter numbers still to confirm.
9. Anchors: accepted, replaced with REPL checks.
10. Carrier names and RetryPolicy: accepted, bible verified (write copy, Repricer).
11. Stub grounding mismatch: accepted; stub grounding changed to research + companion repo.
12. 409 and 529: accepted.
13. Retry-count math: accepted.
14. Stripe and breaker caveats: accepted, Stripe retention not re-opened.
15. Dates and Brooker 2019: accepted-modified, 2015 date from reviewer, unverified.
16. Skipped angles, SRE attribution: accepted.
17. Carrier phrasing: accepted.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Thesis:** as folded. Classify every failure before retrying, falling back or stopping. The way in is the duplicate write: a timed-out write tool replayed on the merchant helpdesk or the repricer. Maturity is Standard, with one argued sentence. Cross-provider failover is Emerging, and "self-healing" unbounded retries are Contested.
2. **Code:** yes, as a new package `listing-studio/resilience/`. It contains:
   - an error classifier (transient, substitutable, terminal), including the two meanings of 429;
   - a backoff-and-jitter retry with a retry budget and an injected clock and RNG;
   - an ordered fallback chain;
   - a write tool with an idempotency key, which proves that a replay does not duplicate the effect.

   Tests are offline and run against a fake provider. A circuit breaker gets a paragraph and a link to Fowler, with no code.
3. **Cross-provider failover:** one paragraph. 8.2 owns model choice, so name 8.2 in plain text.
4. **Named-idea candidates:** "Retry only what could succeed" and "One layer owns retry" may appear as plain sentences. They must not be bolded or presented as named canon. They go on the author checklist.
5. **Also called:** include only terms the map sources from the literature (fallback chain, retry with backoff). Leave out any Gulli-only alias. This goes on the author checklist.
6. **Quote limits:** the SRE 10% retry ratio may be quoted only with its chapter citation. Brooker's posts are cited only if opened before ship; otherwise cut them. Do not quote any prompt-cache loss figure; it may be stated as reasoning only.
7. **Callouts and shipped chapters:** no From-production callout and no coinage. Shipped chapters are not edited, and 3.7's link to 7.1 already exists.

## Reconcile log (Stage 5)

Orchestrator notes:

1. Timeout retry vs write replay: fixed. A timeout is transient only when `idempotent=True`; a keyless write that times out is one call, and a test pins it.
2. Context overflow as substitutable: fixed. The substitutable class is gone; overflow is terminal (smaller rungs have no larger window) and the prose points to compaction (5.4).
3. Full jitter citation: fixed. Cites Brooker, "Exponential Backoff And Jitter," AWS Architecture Blog, 2015.
4. Refusal and max_tokens: fixed. Terminal for an identical resend, with the vendor remedies (raise max_tokens or continue; retry a refusal on another model) cited to Anthropic's stop-reasons page. Refusal fallback left terminal as a policy call.
5. insufficient_quota status code: fixed. Stated as a 429 with its error codes, cited to OpenAI's error docs; the classifier treats every spend cap as terminal whatever the status.
6. Show `ProviderError`: fixed. It is inside the quoted classify region.

Second-engine draft review (SE):

- SE1 billing errors retried: fixed. Every spend cap, including OpenAI's `insufficient_quota` codes, is terminal; tests pin it.
- SE2 logical action identity across model re-calls: softened. A re-call is a new step with a new key; the error tells the model to check before retrying. No redesign; author checklist.
- SE3 no end-to-end deadline: softened. The deadline is stated as per rung; a run-wide deadline must be passed down by the caller. Author checklist.
- SE4 disabling SDK retries drops `x-should-retry`: fixed. The adapter passes it through as `code="no_retry"`.
- SE5 budget misattributed to SRE: fixed. The 10% ratio is cited to SRE; the floor of 3 is attributed to the listing.
- SE6 exhaustion lets the next rung run; a spend cap blocks a cached rung: deferred, code unchanged; open item on the checklist.
- SE7 truncation and refusal overgeneral: fixed. Terminal only for an identical resend, vendor remedies cited.
- SE8 idempotency contract constraints: fixed. Concurrency, parameter mismatch and restart caveats added, with Stripe's parameter comparison.
- SE9 stream recovery left open: fixed. The SDK does not retry stream errors; partial output is discarded on writes and labelled degraded on prose.
- SE10 nine attempts conditional: softened. The count is tied to each layer's default settings.
- SE11 maturity verdicts not re-derivable: softened. Keys on agent tools moved to Emerging; the unsupported "contested" labels were removed.
- SE12 comparative thesis: rejected. The chapter makes no "more damage" claim.
- SE13 SVG fallback contradiction: fixed. The substitutable path is gone; the fallback box is "the next model in the chain".
- SE14 aliases and anchors: alias line kept to the two literature terms; author checklist.
- SE15 listing volume: rejected. The listings stay inside the code diet and the tests use one SKU.
- SE16 verification status not carried: fixed. The meta line carries the Emerging note and "Last reviewed".

Prose critic (PC):

- PC1 hook and classifier disagree on timeouts: fixed via the `idempotent` flag.
- PC2 substitutable case contradicts the chain: fixed; the class is removed.
- PC3 "safest retry" aphorism: fixed, cut.
- PC4 apparatus narration about the catalog: fixed, reworded.
- PC5 "sold as self-healing" vague attribution: fixed, Gotcha rewritten.
- PC6 maturity restated in Gotchas: fixed, removed.
- PC7 closer: fixed, rewritten around the spend cap.
- PC8 scoping said twice: fixed, the second statement cut.
- PC9 the ~200-word classifier paragraph: softened, trimmed.
- PC10 "covers the opening's case": fixed, cut.
- PC11 "Leave them on and add nothing": fixed, cut.
- PC12 "Decide in advance" hedge: fixed, a recommendation is given.
- PC13 "standard lists" attribution: fixed, cut.
- PC14 H1 metaphor not in the body: kept as the title; author checklist.
- PC15 "retried forever" strawman: fixed, cut.
- PC16 "every client" quantifier: fixed.
- PC17 "?." after 8.2's title: fixed, sentence reworded.
- PC18 alias line needs sign-off: author checklist.

Fact checker (FC):

- FC1, FC3 to FC10, FC12, FC13, FC16: verified; kept.
- FC2 `insufficient_quota` status: fixed, stated as a 429 and cited.
- FC11 12-Factor threshold weak: softened to "a run of consecutive errors, about three in its example".
- FC14 `max_tokens` remedy: fixed, cited to the stop-reasons page.
- FC15 refusal remedy: fixed, cited; the fallback is left terminal as a policy call.
- FC17 cache and failover judgments: softened; cache stated as reasoning, failover kept Emerging.
- FC18 unfootnoted claims: fixed; the transient-list attribution is cut and the SDK 409 claim is cited.
- FC19 model IDs: rejected, intentional.

Cold reader (CR):

- CR1 `ProviderError` and adapter not shown: fixed, `ProviderError` is quoted and the adapter glossed.
- CR2 context overflow contradiction: fixed, overflow is terminal in prose, code and diagram.
- CR3 terms used before definition (idempotency key, fallback chain, merchandiser, SDK retries, context overflow, the SRE book, MCP): fixed by glossing.
- CR4 cross-references without links: rejected. Unmerged chapters stay plain text.
- CR5 companion repo not linked: rejected for now; the meta line names it.

Citations: the full-jitter post is cited with its year only, since the day could not be re-confirmed from the page.

