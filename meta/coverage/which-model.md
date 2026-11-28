# Coverage map: Which Model? (chapter 8.2)

> **Thesis:** Choosing one model for a whole product is the wrong unit of decision: steps fail
> differently, every hosted model is retired on the vendor's calendar, and the cheapest model that
> passes your own per-step cases beats a flagship picked off a leaderboard.
>
> **Budget:** standard pattern, ~2,000-2,800 prose words (code, sources and the map excluded).
>
> Research-derived spec: what the chapter must cover to let a reader choose, tier and retire models
> as an engineering decision, and where to stop. Angles run: vendor primary docs, academic papers,
> gateway docs, skeptical read, alias sweep, daily tool. Primary pages read 2026-11-28; two long
> Anthropic pages were read only in part (noted in Sources).

## The mental model

Model choice is a decision your code and your eval make, not a leaderboard lookup. Give each step
its own pick, put the pick in configuration behind one seam, and treat every swap as an eval run.
What lasts is the method (own cases, per-step tiers, a seam, a migration cadence), never a model name.

## Must-cover

1. **Choose by your own cases, one rung at a time** `[+]`. Anthropic: "Having a good evaluation set
   is the most important step"; start efficiency-first or capability-first, then move one rung on
   eval evidence. OpenAI's selection and evals guidance to be opened and cited (not yet read). The
   real unit is cost per passed case, not price per token. *Skip it:* you buy someone else's task.
   **Established** (Anthropic page; second vendor pending). Harness and judge checks belong to 4.2;
   effort before a swap is one sentence plus a link to 4.5.
2. **Tier by step, not by product** `[+]`. Listing Studio's roughly thirty calls are not one
   difficulty: extraction and classify steps versus reasoning and drafting. Small model for narrow
   schema-bound steps, frontier for open reasoning; capability gates decide first (multimodal input,
   strict schemas, effective context), then latency and rate limits; prompts tuned to one family
   rarely transfer unchanged. **Established** (practice); "a small model matches a large one on
   schema tasks" is **Emerging** (arXiv:2510.03847 is a secondary survey, abstract read; pair or
   replace with Belcak et al., arXiv:2506.02153, to be read).
3. **Cascades and advisor/executor: a pointer, with the measured limits** `[+]`. Learned routers and
   cascades (FrugalGPT arXiv:2305.05176; Hybrid LLM arXiv:2404.14618; RouteLLM arXiv:2406.18665) are
   author-reported on fixed benchmarks, none on an agent pipeline. Anthropic's "Optimizing for cost
   and intelligence" is the corrective to "cheap model plus expensive checker always wins": the
   coding pairing gained 1.7 points "at the edge of run-to-run noise" for about 2.1 times the cost,
   and a chart-reading pairing scored 7 points below the executor alone. **Emerging**, vendor-measured.
   Security: tier routers are an attack surface (Shafran et al. arXiv:2501.01818; RerouteGuard
   arXiv:2601.21380, both deferred by 3.2). Ownership of cascades is the lead open question.
4. **A model swap changes behavior, so every swap is an eval run** `[+]`. Drift is documented
   (Chen, Zaharia, Zou, arXiv:2307.09009). Anthropic's breaking-changes notes show the parameter
   surface moves across model generations too (thinking, `tool_choice`, sampling settings; exact
   migration URL to be added). Run the same agent against N models with your real tool schemas
   before committing. **Established** (practice; evidence is one drift study plus vendor notes).
5. **Open-weight versus API** `[+]`. Axes: data residency, volume break-even, ops burden, capability
   gap, license; serving via vLLM's OpenAI-compatible server. Contest "local is the only option for
   residency": hosted vendors offer regional endpoints (Anthropic's US-only inference option at a
   1.1x multiplier; Amazon Bedrock and Google Cloud Vertex AI price regional endpoints at a 10
   percent premium, per Anthropic's pricing page). **Established** (axes); **Contested** (any
   break-even, which depends on utilization). Small-model failure taxonomy is thin (the International
   Tool Calling Dataset, arXiv:2603.05515, abstract read); **Emerging.**
6. **Lock-in and the abstraction seam** `[+]`. One config seam, not a framework; an OpenAI-compatible
   endpoint is often enough, a gateway (LiteLLM, SDK or proxy) is one choice. State the costs:
   lowest-common-denominator features, lag on provider parameters, and a prompt cache that does not
   follow you (hits need 100 percent identical prefixes; Anthropic's cache sits per model and is
   isolated per organization, plus per workspace on the Claude API, AWS and Foundry but per
   organization only on Bedrock and Google-managed deployments; cross-model reuse is not promised).
   Gateway risk: it concentrates provider keys, and LiteLLM 1.82.7 and 1.82.8 were compromised on
   2026-03-24 via a CI action (reported by JFrog, Snyk, InfoQ; the project's own postmortem not
   found). Open OWASP LLM Top 10 2025 (LLM03 supply chain, LLM10 unbounded consumption) or drop it.
   **Established** (a seam); the gateway is a taste call. 7.1 owns fallback; 1.6 owns framework lock-in.
7. **Deprecation and the migration cadence** `[+]`. Anthropic: "at least 60 days' notice" for
   public models, states Active / Legacy / Deprecated / Retired, retired requests return a 404;
   OpenAI: at least 6 months for GA models, 3 for specialised variants, as little as 2 weeks for
   previews. Google's Vertex versus Developer API lifecycle to be opened. Practice: pin dated IDs,
   audit usage by model, calendar the retirement, run the 4.2 set on the replacement early. Dated
   examples are historical snapshots; re-read the table on drafting day. **Standard** (pin and
   track); **Established** (eval-gated migration, depends on 4.2). Contest the folk claim of
   quarterly price rises: Anthropic's page shows an announced increase that did not happen and
   lower list prices on newer models in a tier.

Seven items. Out of the chapter: caching, batching and surcharge mechanics (8.4); dated price
tables (Appendix D, read-on-date rule). Seam: 3.2 owns task-category routing; here "routing" means
choosing a tier.

## Mention-and-link

- Eval harness, benchmarks, error bars → 4.2. Thinking and effort budgets → 4.5.
- Task routing and the classify call → 3.2. Fallback chain, degradation → 7.1. Fine-tune → 8.3.
  Cost controls, caching, batching, cascades in depth → 8.4. Orchestrator-workers → 3.3.
- Structured-output reliability across models → 2.2. Framework lock-in → 1.6.
- Per-model cost and drift in traces → 8.1. Hosting → 8.7. Residency and compliance → 8.6.

## Out of scope

A ranking of current models (rots monthly); leaderboards and contamination (4.2); fine-tuning and
GPU serving internals; gateway product comparisons beyond one paragraph.

## Maturity summary

- **Standard:** pin versions, read retirement notices, keep the model name in config.
- **Established:** own-case eval over leaderboards; tiering by step; re-run evals on every swap;
  eval-gated migration; open-weight axes.
- **Emerging:** learned routers and cascades on agent pipelines; advisor/executor; small-model
  parity on schema tasks.
- **Contested:** quoted cost-reduction percentages; break-even points; "always use gateway X".
- **Chapter verdict (proposed): Established** (eval-gated per-step selection and lifecycle) ·
  **Emerging** (tier routing, advisor/executor). Corrects the stub's *Emerging*; Last reviewed dated.
- *Who decides:* your code (per-step config, eval-gated swaps, lifecycle); your code via a learned
  router (cascades, if kept); the model (advisor/executor). *Grounding:* companion code + research.

## Aliases

*Also called:* model selection, model portability, model tiering, model-agnostic, LLM gateway or
proxy, model cascade (FrugalGPT), query routing (Hybrid LLM), LLM routing (RouteLLM), efficiency-first
/ capability-first (Anthropic). Open: Gulli (2025) ch. 16 Resource-Aware Optimization, Google ADK,
LangChain `init_chat_model`, SLM and BYOM terms; unverified. Collision: "routing" here means a tier,
in 3.2 a task; advisor/executor and orchestrator/worker are named patterns, not aliases (3.3).

## Reader-verifiable anchors

- Claude Code's `/model` switcher and per-subagent `model:` frontmatter or `CLAUDE_CODE_SUBAGENT_MODEL`
  (Claude Code subagent docs, to cite); Codex CLI `--model`; Cursor's model picker. Verify before use.
- Anthropic's model-deprecations page: dated IDs, four lifecycle states, the 60-day line.

## Incidents

- OpenAI, "Expanding on what we missed with sycophancy" (2025-05-02): the April 2025 GPT-4o update
  and rollback. Guardrail: dated snapshots plus eval gates before a rolling change reaches users.
- LiteLLM 2026-03-24 compromise: key concentration in a gateway. Guardrail: pin, scope credentials.
- No public postmortem of a missed deprecation found; say so, invent none. A claimed 2026-10 second
  LiteLLM incident (1.107.0) is unverified; do not cite.

## Named-idea candidates

"Model per step" (tier by step, not by product). Author may strike it. ("The seam" struck: Feathers' term.)

## Carrier

Listing Studio's thirty-call pipeline gives the tiering table. Siblings only if needed: shopper
assistant (latency, small model); bulk catalog onboarding for non-urgent batch work. "Swap the model
is a config change" is carrier-bible text; the chapter shows the seam that makes it true.

## Code seam

New package `listing-studio/model_select/` (not `routing/`, which is 3.2's): per-step model config
plus a same-pipeline-N-models comparison reusing the 4.2 harness with fake clients, offline and
testable. Model IDs live only in config; prose links the live deprecation table.

## Sources (opened 2026-11-28 unless dated)

- Anthropic: "Choosing the right model"; "Optimizing for cost and intelligence" and "Prompt caching"
  (first 100,000 characters read each); "Model deprecations"; "Pricing" (platform.claude.com/docs/en/...)
- OpenAI: developers.openai.com/api/docs/deprecations and /pricing; OpenAI sycophancy postmortem, 2025-05-02
- LiteLLM docs; vLLM docs; JFrog and Snyk write-ups of the 2026-03-24 compromise
- Ding et al., Hybrid LLM, arXiv:2404.14618; Ong et al., RouteLLM, arXiv:2406.18665 (v4 Feb 2025);
  Chen, Zaharia, Zou, FrugalGPT, arXiv:2305.05176 and arXiv:2307.09009 (venues to confirm)
- arXiv:2510.03847 and arXiv:2603.05515 (abstracts only); arXiv:2501.01818, arXiv:2601.21380 (cited by 3.2)
- To open: OpenAI selection guide, Google lifecycle docs, OWASP LLM Top 10 2025, arXiv:2506.02153

> **Verify before quoting:** prices, model IDs and retirement dates change; re-read on drafting day
> and write the date beside each. Quote cost-reduction percentages as author-reported.

## Open questions for the author

1. Cascades: 8.2 or 8.4? 3.2, quick-reference and 8.4's stub all assign them to 8.4. Default: a
   pointer here, depth in 8.4.
2. Prose budget row: standard (~2,000-2,800), or framing if cascades move out?
3. Dated price tables in-chapter or Appendix D? Default: Appendix D.
4. Approve the new `model_select/` package.
5. Keep or strike the named idea "Model per step".

## Map review (Stage 1.5)

Reviewer: Gemini. Findings checked against repo files and primary pages 2026-11-28.

1. Source-book leak: accepted-modified; contest lines removed, claims now stand on vendor pages.
2. Missing thesis and budget: accepted; both added.
3. Missing lens line: accepted; split who-decides added.
4. Cascade seam collision: accepted-modified; confirmed against 3.2, quick-reference, 8.4; demoted to pointer, raised as Q1.
5. Wrong chapter 1.5: accepted; mkdocs.yml confirms 1.6.
6. Must-cover bloat: accepted; eleven items merged to seven.
7. Security gap: accepted-modified; both papers confirmed cited in 3.2; LiteLLM March incident confirmed, the October one not.
8. Google and OpenAI gaps, new axes: accepted-modified; axes added, Google and OpenAI docs listed as still to open, Vertex "12-month" claim unverified.
9. Overrated verdicts: accepted; item 1 and 7 verdicts qualified, chapter verdict split.
10. Citation errors: accepted-modified; "7 points" confirmed (chart-reading, not the coding pairing) and fixed; caching scope corrected from the page; venues and extra papers left as to-confirm, not verified.
11. Anchors: accepted-modified; daily-tool anchors added, citation of Claude Code docs still to do.
12. "No incidents" false: accepted-modified; OpenAI postmortem confirmed (2025-05-02), LiteLLM March only.
13. Invented "restock agent": accepted; carrier-bible has no such surface.
14. Model IDs and seam collision: accepted; `routing/` is 3.2's, IDs moved to config.
15. Missing open questions: accepted; added.
16. Alias gaps: accepted; orchestrator/worker removed, others added unverified.
17. "The seam" name: accepted; struck.
18. Unnamed partners, expiring example: accepted; named, dated examples marked historical.
19. Over budget: accepted; trimmed to near 1,500 words of body.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis as folded. Verdict is Established, which corrects the stub's Emerging. Tier routing and advisor/executor are Emerging, with one sentence each. (Author checklist: the verdict change.)
2. Cascades are owned by 8.4. 8.2 gives them one pointer paragraph in plain text.
3. Dated price tables do not go in the chapter. Prices appear only as "check the vendor page", and any dated table belongs to Appendix D. (Author checklist.)
4. Code: approve the new `listing-studio/model_select/` package, with a per-step config and an N-model comparison over fake clients. It may reuse the eval harness only if that package exists on origin/main. Otherwise it gets a local minimal scorer. Tests use stdlib and pydantic only.
5. "Model per step" is plain wording, not bolded and not canon. (Author checklist.)
6. The LiteLLM supply-chain incident on 2026-03-24 may be cited from opened sources. The second incident, the Vertex lifecycle claim and the arXiv venues are cut unless the fact-checker opens them.
7. No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

QA notes from the orchestrator:
- Tie contradiction (prose said a tie promotes the challenger; code, tests and diagram are strict): fixed. Prose now says `choose` is strict throughout; a cheaper tie is a manual call with cost figures, and a retirement is the one case where the replacement only has to match.
- Apparatus narration ("the thesis asks for one more thing"; "the anti-pattern to log in the catalog"): fixed, both cut.
- Bottle, tent and lamp not in the carrier bible: fixed. Cases are now the Aldsworth sit-stand desk, the bunk bed and the phone case in the prose, the SVG (labels and desc), the alt text, the companion tests and the three provider examples; doc-sync and pytest pass.
- Sycophancy dates: verified against the OpenAI post (rollout began April 24, completed April 25, rollback began April 28; published 2025-05-02). Fixed in the footnote and in Gotcha 4, which wrongly said "three days later".
- Cold-cache claim unsourced: softened. The body now states only the documented exact-prefix and per-organization rules, says the docs are silent on reuse across models, and advises not counting on it.
- `choose` ignores cost: fixed by saying so plainly next to the code and giving the cost check as a separate manual step.

Prose-critic:
1. Tie contradiction: fixed (as above).
2. L88 apparatus: fixed.
3. L126 apparatus: fixed.
4. Carrier products: fixed (as above).
5. Counterfactual step 5: fixed; it is now a visibly separate run.
6. L17 restatement: fixed; trimmed and turned into the definition of case and eval run.
7. Alias line strategies: fixed; efficiency-first/capability-first removed from Also called (still in Further reading). Author checklist.
8. Router-attack detail in Gotcha 5: softened to one clause with the two citations kept.
9. LiteLLM detail and residency gotcha: LiteLLM cut to one sentence; residency kept as a gotcha but surcharge figures removed (also honours ruling 3).
10. Read dates in body: fixed; moved to footnotes.
11. "standard practice" non sequitur and "reduces to this method": fixed; per-step extension owned as the chapter's.
12. L132 echo closer: fixed.
13. Contrast closers: rejected; one remaining is informative.
14. "they choose": fixed.
15. False dichotomy: fixed ("forces a compromise on one of the two steps").
16. "efficiency-first" undefined: fixed by glossing in plain words.
17. Docstrings re-teach prose: rejected; companion-anchored, low priority.
18. "The seam": fixed ("A provider gateway has a price", call site glossed).
19. "often needs rework": softened to "expect to retune".

Fact-checker:
2. "told developers ... email": fixed ("notified developers", "that notice").
5. "as little as two weeks": fixed to the page's "much shorter notice, such as two weeks".
8. Sycophancy dates: fixed (as above).
16. Cold cache: softened (as above).
20. `init_chat_model` accepts `provider:model`: kept; it is LangChain's documented format.
21. OpenAI-compatible endpoints: kept; low risk, vLLM cited.
23. "thirty model calls": cut; the carrier bible marks the count unconfirmed. Nine steps kept.
All other items verified, no action.

Cold-reader:
- "eval run", "cases", "flagship", "efficiency-first": fixed by glossing.
- `client` undefined in the tabs: fixed with a sentence defining it and the provider dispatch.
- Four steps shown vs nine: fixed ("this chapter's table shows four of them").
- l.88 cost formula and code mismatch: fixed (as above).
- l.84 hard to track: fixed (separate run).
- "anti-pattern to log in the catalog": fixed.
- `Client`, `Case`, `score` not printed; effective context, executor unglossed: rejected for this pass; types are described in prose and the files are linked through the companion repo.
- 60-day arithmetic: rejected; 61 days, consistent.

Second engine (OpenAI Codex) on the draft:
1. Selection contract: fixed in prose (strict quality rule, separate cost check, retirement match rule); code left strict.
2. End-to-end gate: rejected for this pass; one-step comparisons are the chapter's scope and 4.2 owns pipeline evals.
3. Provider seam ignores `provider`: softened; prose now says a mixed table dispatches on the provider half.
4. Dated names vs pinned snapshots: rejected for this pass; not raised by QA, flagged to the author.
5. License gate: fixed with a clause in Gotcha 7.
6. Context economy: rejected; capability gate kept, 1.5 owns it.
7. Pending research leads in the map: rejected; map-housekeeping, not chapter content.
8. Maturity conflation: softened via the per-step extension sentence.
9. Neighbour material: softened (router attacks and surcharges trimmed).
10. Reader-verifiable anchor and alias line: alias fixed; anchor rejected (would add length past budget).
11. Thesis overclaim: fixed ("forces a compromise").
12. Thirty calls: fixed (cut).
13. Unregistered product: fixed.
14. OpenAI notice exception, regional wording: regional wording removed with the figures; notice wording aligned to the page.
15. Literature claim: fixed ("the studies cited here do not test agent pipelines").
