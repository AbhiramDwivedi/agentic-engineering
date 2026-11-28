# Coverage map: Compaction (chapter 5.4)

> Spec for the chapter, not a draft. Stub at `docs/knowledge/compaction-and-the-window.md` has no prose, so nothing is marked `[*]`/`[+]`. Sweep angles run: vendor docs, academic and benchmarks, practitioner writeups, skeptical read, daily-tool, everyday-engineer (partial: Claude Code's documented thrash stop only), incidents (none found). Alias sweep: partial (Gulli books not checked). Neighbours: 1.5 Context Engineering (shipped; owns the rot evidence and the four curation moves), 2.6 The Harness (compaction seat, pinned rules, `pre_compact`), 5.1 State, Not Memory, 5.3 Memory (unwritten). Sources opened 2026-11-28 except LangGraph `trim_messages` and Google ADK (not opened; check before naming). Last reviewed 2026-11.

## The mental model

A full window is not a healthy one: reliability falls as input grows, well before the advertised limit, so the aim is a smaller, denser window. Compaction is a family of lossy rewrites of history your code already holds: clear old tool results, trim to a recent window, summarize the middle, offload to files and keep a pointer, or isolate work in a sub-agent whose window is thrown away. Each trades tokens for information, and the loss is silent: the model does not know what the summary dropped.

**Who decides (litmus):** split. Your code decides when (trigger), what is protected (pins, excluded tools, kept turns) and whether to proceed (archive first, keep the original if the summary fails). The model decides what the summary says, the one model-made choice here. Clearing and trimming are pure code. Say so per rung.

**Thesis:** "Reach for the lightest rewrite that works: clear old tool results before you summarize anything, and keep whatever must survive in pins or state your code owns, because a summary drops specifics without telling you and only a probe will find out." ("Cannot read back" applies only to OpenAI's opaque item, item 3; Anthropic and framework summaries are readable text.)

## Must-cover (ranked)

1. **The problem, one paragraph.** Degradation is Established; thresholds are model- and task-dependent, never quote one. Lead: Liu et al. arXiv:2307.03172; RULER 2404.06654 (17 models claiming 32K+, about half held up at 32K); NoLiMa 2502.05167 (ICML 2025; 11 of 13 models below half their short-context baseline at 32K); Chroma "Context Rot" (2025-07-14; holds task complexity constant while varying input length; says it is not exhaustive of real-world use). Depth stays in 1.5.
2. **Strategy ladder, lightest first.** (a) clear stale tool results; (b) trim or window; (c) summarize older turns; (d) offload to files and keep a pointer; (e) isolate in a sub-agent. Anthropic: tool-result clearing is "One of the safest lightest touch forms of compaction" (2025-09-29). Observations dominate: about 84% of an average SWE-agent turn on SWE-bench Lite-50 (Lindenbauer). Litmus: a, b, d code; c, e the model writes. Manus's "restorable compression" (keep the URL, drop the page) is what makes a and d safe. Established (shipped by three vendors, two frameworks); which rung wins is Emerging (item 4).
3. **Features, as of 2026-11 (volatile, beta).** Cite live docs, mark every parameter for re-check.
   - Anthropic has three paths. **On demand**: beta header `compact-2026-09-04`, top-level `compaction` parameter; the overview says "Use on-demand compaction wherever it is available"; variants keep recent turns verbatim or run in the background. **Token threshold**: separate header `compact-2026-01-12`, edit type `compact_20260112`; default trigger 150,000, minimum 50,000 input tokens; `pause_after_compaction` lets you reinsert recent turns. **Your own summarizer**. The two headers are distinct, one per mode. Custom `instructions` replace the default prompt; the summary is readable text in the `compaction` block; an extra sampling step is billed under `usage.iterations`.
   - Anthropic context editing: `clear_tool_uses_20250919` (default trigger 100,000, keep 3, `clear_at_least`, `exclude_tools`), header `context-management-2025-06-27`; "Your client application maintains the full, unmodified conversation history".
   - OpenAI Responses: `context_management` with `compact_threshold`, `/responses/compact`; the returned item "is opaque and not intended to be human-interpretable", and with `previous_response_id` "do not manually prune". This is the one case you cannot read back; you can only probe it. Guide is undated. The OpenAI Agents SDK has compaction sessions (cited in 5.1).
   - Claude Code and the Agent SDK: auto-compaction, `/compact <focus>`, a "Compact Instructions" section in CLAUDE.md, a stop after repeated refills; the docs say "detailed instructions from early in the conversation may be lost". Codex CLI has `/compact` and auto-compaction (verify).
   - LangChain: `SummarizationMiddleware` (trigger by fraction, tokens or messages; keeps last 20 by default; custom `summary_prompt`; never fires if no trigger) and `ContextEditingMiddleware`. Check `trim_messages` (langchain-core or LangGraph?) and Google ADK context compaction before naming either.
   Established as a feature class; each parameter Emerging.
4. **Which rung wins: thin evidence, not a dispute.** Lindenbauer et al. 2508.21433 (JetBrains Research, TU Munich; NeurIPS 2025 DL4C workshop): SWE-agent, SWE-bench Verified, five configurations; observation masking matched summarization at lower cost, hybrid 7% cheaper than masking and 11% than summarization; authors call generality initial. Factory Research (2025-12-16) compares summarizers only (Factory "anchored iterative summarization" 3.70, Anthropic 3.44, OpenAI 3.35 of 5, a 0.26 to 0.35 point gap, six dimensions scored by a GPT-5.2 judge, run by a vendor that sells one contender); no masking arm, so it says nothing about masking versus summarizing; artifact tracking "remains an unsolved problem". Satish et al. 2609.32961 (preprint): about 35,000 runs, three open-weight models; on Terminal-Bench with Qwen, roughly a third of the tokens could take 20-80% longer. Teach: masking first, measure before summarizing. Emerging. Do not repeat scores as a ranking.
5. **What to pin, and what never lives only in the transcript.** Pin the standing rules, task statement, plan and open decisions, needed identifiers. Rules that must hold go in code (2.6); durable facts and control flow go in state (5.1). Placement matters: Lost in the Middle says keep pins and the summary at the window's start or end. Recitation is the alternative to pinning: Manus rewrites a todo list so the plan sits "into the end of the context". Link 2.6 for pin cost. Established.
6. **Writing the summary, the one step the model decides.** A schema beats free prose: task, decisions with reasons, artifacts touched, open items, next step. Custom instructions replace the default prompt (Anthropic) and Claude Code takes Compact Instructions. Anchored (incremental) summarization summarizes only the new span and merges it (Factory); a summary of a summary compounds loss ("compact again", Anthropic). Litmus: model writes, your code supplies the schema. Emerging.
7. **What compaction loses, and how to test it.** Losses are silent and skew to specifics: file lists, exact values, reasons, instructions given once. Probe: write questions whose answers sit only in the dropped span (recall, artifacts changed, next step, why), compact, score (Factory's four probe types). Add pinned-survives and unpinned-lost regressions. A substring probe tests presence, not recall; a model-judged probe is prose only and needs its own check (4.2). Emerging.
8. **Cost and cache.** Cache writes cost more than base input and reads much less; link the live pricing table, state no values. Clearing "invalidates cached prompt prefixes" (`clear_at_least` so each clear pays for itself); place a breakpoint after the system prompt so it survives a new summary. Compaction adds a sampling call; Satish shows token savings are not cost savings. Established mechanics, Emerging policy.
9. **Policy and failure, what is new here.** Set the threshold from a measured knee, not the hard limit; keep the last N turns verbatim; archive before rewriting; refill loop (Claude Code stops after a few attempts). Failure contract: if the summary is empty, raises or is refused, history is unchanged and the run continues or stops by policy. Anthropic: null `content` means nothing compacted; if safeguards block it, `content` is also null and `stop_reason` is `refusal`. Link 2.6 for the seat. Established triggers; Emerging tuning.
10. **When not to compact; offload and isolate in a paragraph.** Short runs, exact-value work (offload to a file), safety rules (code), or when smaller tool outputs or a sub-agent is the real fix. Cognition: compression is "hard to do well" and "You will still eventually hit a limit". Manus: files "unlimited in size, persistent by nature". Link 3.3, 5.1, 5.3. Optional: MemGPT (2310.08560, unverified) for 5.3.

## Mention-and-link

2.6 The Harness (seat, trigger, `pre_compact`); 1.5 Context Engineering (rot, four moves); 5.1 State, Not Memory; 5.3 Memory (planned); 4.2 Evaluation (judge calibration); 3.3 Orchestrator-Workers; 5.2 RAG (planned); Prompt Injection (injected content surviving a summary).

## Out of scope

Long-context training, KV-cache compression, embedding compression, token-pruning research (name once), price lists, leaderboard scores.

## Maturity summary

**Established:** threshold and on-demand compaction as shipped features, tool-result clearing, pinning, cache mechanics (consistent with 2.6, which rates the compaction trigger Established). **Emerging:** choosing a strategy by evidence, probe testing, trigger tuning, opaque server-side behaviour. Chapter-meta line, 2.6 style: Established (mechanisms) · Emerging (strategy choice and testing) · Last reviewed 2026-11. Argued sentence: the mechanisms are shipped and the problem is measured, but the evidence for which rung to use is one SWE-agent study plus a vendor benchmark. No Contested item: no source argues summarization beats masking.

## Aliases (partial)

context compression, summarization (stub); compaction (Anthropic, Claude Code, OpenAI); context editing, tool-result clearing (Anthropic); observation masking (Lindenbauer); summarization middleware (LangChain); context compression (Factory). Gulli books unchecked.

## Reader-verifiable anchors

Claude Code: `/context`, then `/compact focus on <topic>`; docs: "detailed instructions from early in the conversation may be lost." API: the `compaction` block and `usage.iterations`.

## Carrier section

Listing Studio, bulk ingest of a few hundred supplier rows in one session. The window fills with feed rows; "drafts only" is pinned; a mid-run decision (supplier confirmed the height range for one SKU; use it, not the spec sheet) exists only in a message. Compact: the pin survives, the decision is lost unless written to state, a later row contradicts it. Fix: mask first, pin, write the decision to state, probe. Do not cite 2.6's run details unless 2.6 is merged. Avoid the below-floor price story. No "From production:" callout without author input.

## Code and demo plan (offline; stdlib + pydantic + anyio only, no langgraph)

Standalone package `compaction/`, stating in prose that it generalises 2.6's placeholder into a real summarizer seat (after 2.6 merges, may reuse `harness.compact`; coder-tester must check the dependency before Stage 2). Pieces: `Message` (pydantic: role, content, `pinned`); `estimate_tokens` (word count, labelled an estimate); `mask_observations(history, keep_last, archive)` replacing old tool results with a placeholder that carries a key (`[result 7 masked; archive key r7]`); `compact(history, summarize, budget_tokens, keep_last, archive)` triggering on the estimate, archiving first, keeping pins and recent turns, replacing the middle with one summary, returning history unchanged if `summarize` returns empty, raises or returns a refusal sentinel; deterministic `fake_summarizer` that drops specifics; `render(state) -> Message` putting the state record into the window each call (5.1 pattern); `probe(window, questions)` over `render(state) + history`, a presence probe. Tests: (1) pinned survives, unpinned lost; (2) archive holds the full history; (3) empty, raising and refusing summarizers leave history unchanged; (4) masking keeps the last N and the archive restores a masked result by key; (5) probe fails before the decision is written to state, passes after `render` includes it; (6) trigger fires on the token estimate, not message count. Anchors: `compact`, `mask_observations`, `probe`. No numeric claims beyond test counts.

## Gotchas (feed Anti-Patterns)

Compacting short runs; summarizing when masking would do; a decision held only in a message; trusting the summary without a probe; triggering at the hard limit; compacting a summary again without re-pinning; treating a substring probe as recall; checking only for null content and missing a refusal.

## Incidents

None found. State plainly; do not manufacture one.

## Named-idea candidates

"Pin, offload, then summarize" (an ordering); "the lossy write". Offer, do not force.

## Sources (opened 2026-11-28)

- Anthropic: Effective context engineering <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>; docs Context editing, Compaction overview, Compaction on demand, Compaction keeping recent turns, Compaction at a token threshold, Prompt caching, all under <https://platform.claude.com/docs/en/build-with-claude/> (`context-editing`, `compaction`, `compaction-on-demand`, `compaction-keep-recent-turns`, `compaction-threshold`, `prompt-caching`)
- Claude Code <https://code.claude.com/docs/en/how-claude-code-works>; Agent SDK loop <https://code.claude.com/docs/en/agent-sdk/agent-loop>
- OpenAI Compaction guide <https://developers.openai.com/api/docs/guides/compaction> (undated); Agents SDK sessions <https://openai.github.io/openai-agents-python/sessions/>
- LangChain middleware <https://docs.langchain.com/oss/python/langchain/middleware/built-in>
- Chroma <https://www.trychroma.com/research/context-rot>; arXiv 2307.03172, 2404.06654, 2502.05167, 2508.21433, 2609.32961
- Factory <https://factory.com/news/evaluating-compression>; Manus <https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus>; Cognition <https://cognition.com/blog/dont-build-multi-agents>

## Verify before quoting

Every provider parameter, default and beta header (volatile); OpenAI page undated; Factory scores (vendor-run, no ranking); Satish is an unreviewed preprint; LangGraph `trim_messages`, Google ADK, Codex CLI compaction and MemGPT not verified. Anchor code on symbol names.

## Map review (Stage 1.5)

An independent review by Claude Opus, standing in for codex (unavailable), produced 19 findings. Each was checked against the opened primary source (Factory, Anthropic compaction overview and threshold pages, Claude Code, Chroma, Manus, Satish abstract) and folded in with the disposition below.

- 1 accepted: "modest" is not in the Factory article (verified); quote dropped, 0.26 to 0.35 point gap, GPT-5.2 judge, six dimensions, "anchored iterative summarization" added, and the no-masking-arm caveat stated.
- 2 accepted: thesis restated as the lightest-rung-first decision; "cannot read back" confined to OpenAI's item.
- 3 accepted: on-demand `compact-2026-09-04` and threshold `compact-2026-01-12` verified on the live pages as separate headers; Anthropic recommends on-demand; "pages disagree" removed; sub-pages added to Sources.
- 4 accepted: Chroma holds task complexity constant (verified); wording corrected.
- 5 accepted: Contested bullet dropped; recast as "masking first, measure before summarizing", Emerging.
- 6 accepted: split Established/Emerging meta line, consistent with 2.6.
- 7 accepted: new item 6, writing the summary.
- 8 accepted: `render(state)` step added; probe reads `render(state) + history`; named a presence probe.
- 9 accepted: `archive` callback and keyed placeholder for masking; token-estimate trigger.
- 10 accepted-modified: standalone package chosen (path b), 2.6 dependency flagged for coder-tester.
- 11 accepted-modified: Agents SDK sessions and Agent SDK page added; Codex CLI and Google ADK listed as unverified, to check before naming.
- 12 accepted: placement and Manus recitation added to item 5; Manus wording verified.
- 13 accepted: item 9 narrowed to what is new; pin-cost line replaced with a link to 2.6.
- 14 accepted: refusal path verified on the threshold page; added to item 9 and test 3.
- 15 accepted: Claude Code quote corrected to the live "detailed instructions ... may be lost".
- 16 accepted-modified: sweep header now names the unopened sources; `trim_messages` ownership still open.
- 17 accepted: pricing values removed; relationship only.
- 18 accepted: Satish names Terminal-Bench, Qwen, open-weight models (verified in the abstract).
- 19 accepted: body trimmed to the budget, Gotchas section added, open questions moved out of the map to the PR checklist. MemGPT kept as an unverified optional mention.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. The thesis is as folded in. The writer may tighten it into one sentence but must keep its two decisions: use the lightest rung first, and keep what must survive in pins or in state your code owns.
2. Maturity is a split line. The mechanisms (clearing tool results, trimming, summarizing, provider compaction) are Established. The evidence on long-context degradation and on masking versus summarizing is Emerging or Contested. Last reviewed is 2026-11.
3. Masking before summarizing is presented as the recommendation that follows from the thesis, with the evidence and its limits stated. Factory compares summarizers only and is vendor-run.
4. Offloading and sub-agent isolation get one paragraph each, pointing to 5.1 and 9.2. The compaction seat (trigger, pinned rules, archive) is pointed to 2.6 and not re-taught.
5. Code is a standalone package, `listing-studio/compaction/`. 2.6 is unmerged, so no import from it. Tests are offline and import only stdlib, pydantic and anyio, with a scripted summarizer. Provider examples are illustration files and are compile-checked only. Anthropic examples use only header names verified on the live docs.
6. Unverified items (`trim_messages` ownership, Google ADK, Codex CLI, MemGPT) are named only once a source is opened. Otherwise they are cut.
7. No From-production callout and no coinage. The demo's pinned fact is "drafts only".
