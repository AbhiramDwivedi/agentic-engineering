# Coverage map: Controlling Cost (chapter 8.4)

> **Thesis:** Cutting an agent's per-token price rarely cuts its bill, because the bill is set by
> how many calls the loop makes and how much context each re-sends: take the zero-quality-loss wins
> first (stable cached prefixes, async tiers, hard loop caps), and judge every lever that trades
> quality for cost on cost per passed case.
>
> **Budget:** standard pattern, ~2,000-2,800 prose words (code, sources and the map excluded).
>
> Research-derived spec for the author to trim. Angles run: vendor primary docs (Anthropic, OpenAI,
> Google), academic papers, security (OWASP), skeptical read, alias sweep, daily tool,
> everyday-engineer. Incidents: none found in primary postmortem form. Primary pages opened
> 2026-11-28; the Anthropic caching and cost pages were read to their first 100,000 characters only.

## The mental model

An agent run re-sends its whole context every turn, so an uncached loop's input cost grows roughly
with the square of the turn count, plus output, which is priced higher than input and includes
hidden reasoning tokens on the vendors that bill them. Cost control is four moves: make the
repeated prefix cheap (caching), make waiting work cheap (batch), make easy calls cheap (cascade),
and make the total bounded (budgets in code). The first two lose no quality; the last two do, and
are judged on cost per passed case, never price per token.

## Must-cover

1. **Where the money goes** `[+]`. Re-sent context and tool schemas, output and reasoning tokens
   (priced above input; link 4.5 for budgets), call count, and long-context price tiers on some
   vendors (check each vendor's page; not verified here). Anthropic's multi-agent write-up reports
   agents using about 4 times and multi-agent systems about 15 times a chat's tokens, and token
   use alone explaining 80 percent of variance on BrowseComp. Contest "four agents, four times the
   bill": it is tokens, not agent count. Token hygiene is a free win: trim verbose tool output and
   schemas (→ 2.1). Measure first with per-step cost in traces (→ 8.1). *Skip it:* you optimise
   the wrong line. **Established.**
2. **Prompt caching, and why it misses** `[+]`. Portable rule: static prefix first, dynamic last.
   Anthropic: reads about 0.1x base input, writes 1.25x (5 minutes) or 2x (1 hour), prefix order
   tools, system, messages. OpenAI: on GPT-5.6 and later writes cost 1.25x (30 minutes) or 2.5x
   (12 hours), "not an additive fee"; earlier models have no write charge; `prompt_cache_key` keeps
   accounting separate per customer. Google: implicit caching on by default for its 2.5-generation models and
   newer, explicit caching optional; the page gave no discount rate or storage fee, so read it at
   drafting. Misses: changed tool definitions, `tool_choice`, images or thinking settings; a
   timestamp near the top; unstable JSON key order; prompts under the minimum (silent, no error);
   TTL expiry between slow turns; failover to another provider starts cold (→ 8.2, 7.1);
   mid-history context editing busts the prefix, so compaction trades against caching (→ 5.4).
   Verify with usage fields (`cache_read_input_tokens`, OpenAI `cached_tokens`) and alarm on hit
   rate. **Standard** (mechanism; label vendor wire details, numbers rot).
3. **Batch for work that can wait** `[+]`. Anthropic and OpenAI both discount batch 50 percent;
   OpenAI's batch takes only a 24h window, up to 50,000 requests or 200 MB; Anthropic's limits are
   100,000 requests or 256 MB (label each by vendor). Anthropic discounts stack with caching but
   hits are best-effort, so use the 1-hour TTL. OpenAI also has a synchronous Flex tier (page
   mentions it only in passing; verify). Fits Listing Studio bulk catalog onboarding, not live
   Merchant helpdesk replies. **Standard** (batch); **Established** (batch plus cache stacking).
4. **Model cascades and routing for cost** `[+]` (owned here; resolves 8.2's open question and
   3.2's deferral). Cheap model first, escalate on a checkable failure signal; Anthropic's recipe
   is run low and re-run only failures higher. Learned routers: FrugalGPT (Chen, Zaharia, Zou,
   arXiv:2305.05176, May 2023, up to 98 percent cost cut at GPT-4 parity, author-reported),
   RouteLLM (Ong et al., arXiv:2406.18665, v4 Feb 2025), Hybrid LLM (Ding et al.,
   arXiv:2404.14618, ICLR 2024, up to 40 percent fewer large-model calls), all on fixed
   benchmarks, none on a multi-step agent pipeline. Router attack surface: Rerouting LLM Routers
   (Shafran, Schuster, Ristenpart, Shmatikov, arXiv:2501.01818, Jan 2025), link not depth.
   Advisor/executor is the same economics with the model deciding when to consult: Anthropic's cost
   page shows a coding pairing +1.7 points "at the edge of run-to-run noise" for about 2.1x cost, a
   chart-reading pairing 7 points below the executor alone, and about 1,000 extra tokens per
   request; price the hard tail, not the median. Seam: 3.2 owns the classify call, 8.2 picks the
   tier per step, this chapter owns escalate-on-failure and its economics. Verdicts: deterministic
   gate **Established**; confidence-gated or learned cascade **Emerging**; advisor/executor as a
   cost lever and any quoted percentage **Contested**.
5. **Caps and budgets, enforced in code** `[+]`. `max_tokens` caps one response and the model
   cannot see it; too low raises cost per solved task (Anthropic cost page benchmark: a 16,384 cap
   cost more per solved task than 64,000; pin benchmark and model at drafting). Step caps, per-run
   and per-user dollar budgets, kill switch, workspace limits as backstop. Failure to name: an
   in-process global counter is not a per-user budget across tenants and replicas. Failure-return
   contract: a tripped budget returns a structured, non-retryable budget-exceeded result with
   partial work preserved, never a crash or a retry storm (→ 7.1, 7.3). OWASP LLM10 2025
   "Unbounded Consumption", including Denial of Wallet. Loop stop conditions → 2.5, 2.6; per-user
   identity → 8.5. **Established** (practice); mechanism varies by vendor.
6. **Action, plan and semantic caching: the risky tier** `[+]`. Plan caching (Zhang, Wornow,
   Wan, Olukotun, arXiv:2506.14852, NeurIPS 2025): reuse plan templates, abstract reports 50.31
   percent cost and 27.28 percent latency reduction at 96.61 percent of optimal accuracy.
   Semantic caching serves a stored answer for a "similar" query; fixed similarity thresholds give
   no correctness guarantee (vCache, Schroeder et al., arXiv:2502.03771, ICLR 2026), and
   CacheAttack (Zhang et al., arXiv:2601.23088, ICML 2026) hijacks responses via key collisions at
   an 86 percent hit rate. Exact-match caches of deterministic tool results are **Established**;
   keys carry tenant and every input that changes the answer. Plan caching **Emerging**; semantic
   answer caching **Contested**, never across tenants or for state-dependent answers.
7. **Cheap checks before expensive ones** `[+]`. Pre-screen (rules, regex, small classifier)
   before a model call; dedupe; stop early. One paragraph, arithmetic from the carrier code.
   **Established.**
8. **The quality-cost frontier and how to test a lever** `[+]`. Anthropic's split: caching, token
   hygiene and batch are free; model choice, effort, caps, budgets and multimodel pairings trade
   quality. Any trade-off lever is an eval run (→ 4.2) judged on cost per passed case (8.4
   introduces the unit; 8.2 uses it). Context editing cost more than it saved on a short run in
   Anthropic's own measurement: test, do not assume. **Established.**

## Mention-and-link

Choosing and tiering models, lock-in → 8.2. Traces → 8.1. Routing by task → 3.2. Retry and
degradation → 7.1. Effort budgets → 4.5. Compaction → 5.4. Context engineering → 1.5.
Fine-tuning a small model → 8.3. Self-hosting → 8.2, 8.7. Multi-agent cost → 9.2. Dated price
tables → Appendix D.

## Out of scope

KV-cache internals and serving-side optimisation (vLLM, speculative decoding), cache compression
research, a ranking of current prices, gateway product comparisons (8.2), billing mechanics.

## Maturity summary

- **Standard:** caching mechanism and static-first rule; batch for deferrable work; per-request
  token caps.
- **Established:** where the money goes and per-step measurement; code-enforced budgets and step
  caps; deterministic-gate cascades; pre-screening; exact-match caching; batch plus cache stacking.
- **Emerging:** learned or confidence-gated cascades; plan caching.
- **Contested:** semantic answer caching; advisor/executor as a cost lever; any quoted percentage.
- **Chapter verdict (proposed): Established**, with Emerging and Contested sub-verdicts named in
  prose; Last reviewed dated, volatile numbers flagged. *Who decides:* your code (prefix layout,
  batch, budgets, deterministic cascades; learned routers and semantic caches are trained or
  embedding artifacts inside your code); the model only when escalation is exposed as a tool call
  (advisor/executor, → 2.1). *Grounding:* research + companion repo (the stub says
  "research + production"; downgrade it, no production claim here).

## Aliases

*Also called:* prompt caching, context caching, prefix caching; batch API, Flex processing; model
cascade (FrugalGPT); LLM routing (RouteLLM); query routing (Hybrid LLM); escalation; semantic
cache; plan caching; denial of wallet (OWASP); token budget; LLM FinOps; resource-aware
optimization (Gulli, *Agentic Design Patterns*, 2025, ch. 16; not independently opened here;
Gulli and Nawalgaria 2026 sweep done at drafting). Collision: "routing" here means choosing a
tier by cost, in 3.2 choosing a task path.

## Reader-verifiable anchors

- Anthropic: the `usage` block shows `cache_read_input_tokens` and `cache_creation_input_tokens`;
  run one request twice and watch the second read.
- OpenAI: `usage.input_tokens_details.cached_tokens` on a call over the minimum length.
- Claude Code `/cost` and `/context` (to cite from its docs before use).

## Named-idea candidates

"Stable prefix" is existing vendor phrasing, not a coinage. "Cost per passed case" is shared with
8.2. Author may strike either.

## Carrier

Listing Studio's roughly thirty calls: a long static system prompt plus product-schema tools makes
the prefix-cache demo; bulk catalog onboarding is the batch case; the cascade gate wraps one
named step (categorize or copy); the **Repricer** shows the step cap (Category scout is only
lightly built). Numbers come from running the companion code; until measured, write qualitatively.

## Code seam

New package `listing-studio/cost/` (not `routing/`, 3.2's; not `model_select/`, 8.2's): a prompt
builder ordering static before dynamic, with a test that an early timestamp changes the prefix
hash; a cascade gate with a stubbed failure signal; a per-run budget guard returning a
budget-exceeded result. Offline with fake clients. Needs code: yes, small.

## Sources (opened 2026-11-28)

- Anthropic: Prompt caching, Batch processing, Pricing, Optimizing for cost and intelligence
  (platform.claude.com/docs/en/...), multi-agent research system (anthropic.com/engineering).
  Managed Agents and Claude Code docs: URLs to add at drafting.
- OpenAI: Prompt caching (developers.openai.com/api/docs/guides/prompt-caching); Batch
  (.../guides/batch). Google: caching (aistudio.google.com/docs/caching).
- OWASP Top 10 for LLM Applications 2025, LLM10.
- arXiv abstracts opened: 2305.05176, 2406.18665, 2404.14618, 2501.01818, 2506.14852, 2502.03771,
  2601.23088.

> **Verify before quoting:** every multiplier, discount, TTL, minimum and batch limit is a vendor
> snapshot dated 2026-11-28; cite the page, not the number. Cascade and plan-cache percentages are
> author-reported on fixed benchmarks. A GPTCache "30 percent mismatch" claim was unconfirmed; do
> not use it.

## Open questions for the author

1. Merge items 4 and 7 into a single cascade section, or keep pre-screening separate?
2. Does 8.4 or 8.2 formally introduce "cost per passed case"? Proposed: 8.4.
3. Companion code scope: is the three-piece `cost/` package right, or only the prefix demo?
4. Advisor/executor as Contested: acceptable for a technique Anthropic ships, given its own +1.7
   points at 2.1x cost?

## Map review (Stage 1.5)

Reviewer: second-engine review. Disposition per finding:

1. accepted-modified: opened and verified all four arXiv leads; dropped MeanCache; Anthropic page tails and Managed Agents/Claude Code URLs still to read at drafting, flagged in the map.
2. accepted: added OpenAI and Google caching and batch, corrected OpenAI write phrasing, labelled vendor limits; Google discount and storage fee not on the page, so left unstated.
3. accepted-modified: thesis rewritten as one falsifiable sentence on free wins versus cost per passed case.
4. accepted: gateway counter restated as a general rule; grounding downgraded to research + companion repo.
5. accepted-modified: added output/reasoning asymmetry, quadratic growth and long-context tiers; the tier claim is flagged unverified.
6. accepted: verdicts aligned; advisor Contested, confidence gate Emerging, batch plus cache split.
7. accepted: merged to 8 items, added token hygiene and sibling links (2.5, 2.6, 5.4, 7.3, 8.5).
8. accepted: budget-exhaustion contract and Open questions added.
9. accepted-modified: litmus line revised; the second CLI anchor dropped, not verified.
10. accepted: "interactive desk" removed, Repricer used, cascade step named.
11. rejected: arXiv pages for FrugalGPT and RouteLLM list no venue, so TMLR and ICLR 2025 are unconfirmed; Hybrid LLM ICLR 2024 is confirmed and added.
12. accepted: efficiency-first/capability-first removed, aliases added, spelling fixed, 8.4 proposed as home of the unit.
13. accepted: incidents header fixed; 8.2's map no longer cited as a source.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Code:** a new `listing-studio/cost/` package with three small pieces:
   - a prompt builder that puts static content before dynamic, with a prefix-hash test;
   - a cascade gate with a stubbed failure signal;
   - a per-run budget guard that returns a budget-exceeded result.

   It is offline and uses scripted clients.
2. **Verdict:** Established, with the Emerging and Contested sub-verdicts in prose. Advisor/executor stays Contested, as the map says.
3. **Cascade and pre-screening:** one item. Pre-screening is a cheap first rung of a cascade.
4. **"Cost per passed case":** introduced here as a plain metric description (cost divided by eval cases passed), not as a coinage. Since 8.2 is unmerged, it is mentioned in plain text.
5. **Dates:** no venue claims for FrugalGPT or RouteLLM. Drop any long-context price tier the map marks unverified.
6. **No From-production callout.** No new alias line.

## Reconcile log (Stage 5)

Prose critic:
1. L11 non-sequitur: fixed; the line now draws the budget conclusion the data supports.
2. Four-moves restatement: fixed; the "fix, in miniature" paragraph is cut.
3. Apparatus narration on the 8.2 boundary: fixed; filing language and the "routing" aside cut (See also keeps it).
4. Over budget: fixed; batch limits, write premiums and lifetimes moved to an Appendix D pointer, plus trims across the body.
5. "the prefix runs tools, system, messages" parse: fixed; the order is stated plainly and the "not an additive fee" quote dropped.
6. Vendor-snapshot housekeeping line: fixed; replaced by one sentence scoping the savings figures as vendor-reported.
7. "cost per solved task" drift: fixed; the chapter's own measure is used, and the source's figure keeps the source's wording.
8. `max_tokens` lead sentence: fixed.
9. "the page" referent: fixed; now "Anthropic recommends".
10. Output ratio sourced to batch prices: softened; now "Anthropic's price table", which the batch page carries.
11. Plan-caching false precision: fixed; rounded to about half the cost and a quarter less latency.
12. Gotcha 5 is a recommendation: fixed; retitled around the context-editing result.
13. Token hygiene unanchored: fixed; one concrete case added.

Fact-checker:
1. 80 percent claim: fixed; BrowseComp defined, "Anthropic's own evaluation", stated as a correlation that proves no cause.
2. `max_tokens` single runs: fixed; the Opus 5.5 result is marked as single runs that neither cap cut off.
3. Effort failure signal: fixed; the benchmark's own tests named as the signal.
4. Read-multiplier exceptions: fixed; "a twentieth on Opus 5.5 and Sonnet 5.5".
5. `run_with_budget` discards the stopped step and overshoots: fixed in code; the guard now checks the projected spend before each step and keeps the last completed output (also map review finding 8). Tests and the mirrored snippet updated.
6. Maturity line scope: fixed; Established now covers the mechanisms, with savings figures marked vendor-reported in the line and the prose.

Cold reader:
1. Terms: fixed by glossing cascade, prefix, `cache_control`, cache write versus read, hit rate, advisor/executor, effort, SWE-bench Pro, BrowseComp, context editing, the categorize step, and where the companion tests live.
2. Quadratic sum: fixed; the arithmetic is shown.
3. Output-ratio sentence led nowhere: fixed; it now says a long-reasoning step can outspend the re-sent context.
4. Break-even: fixed; the expected-cost inequality is shown (p above 0.2).
5. Advisor pairings unnamed: softened; each pairing is tied to its executor; the chapter adds no model names the source does not support.
6. Alt text too long: fixed; under 80 words, the SVG description matches, and the budget labels show the pre-step check.
7. Missing `import hashlib`: fixed; the snippet anchor now includes the import.
8. Unlinked chapter references: rejected; those chapters are not on main yet, so they stay plain text.
9. No live API call or batch code: rejected; the chapter shows the usage fields to check, and live API code is out of scope for offline companion code.
10. Vendors as their own evidence: softened; the maturity sentence now separates the mechanisms from the savings figures.

Second-engine review: the map findings above were rechecked against the draft. Finding 8 (partial-work preservation) is now in the code; the others hold as dispositioned.

Anti-patterns See also line: cut, because the catalog has no entry for either item it named.

Humanizer pass: vocabulary and cadence scan over the prose; lint slop score 0.7, no hard tells. Glosses not in the fact-checked draft were held to wording the sources support (BrowseComp and SWE-bench Pro named as benchmarks only, OpenAI minimum scoped to GPT-5.6 and later, workspace spend cap kept as the vendor term).
