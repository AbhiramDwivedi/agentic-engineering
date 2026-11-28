# Coverage map: Reasoning & Thinking Budgets (chapter 4.5)

> **Thesis:** *Reasoning models absorbed chain-of-thought prompting into a billed output-token dial that can cost accuracy and latency when turned up, so start each task low and raise effort only where your own eval sweep shows the extra thinking pays.*
>
> **Budget:** standard pattern, ~2,000-2,800 prose words. It deflates explicit CoT prompting and still has to make the effort dial, thinking across turns, and the sweep work.
>
> **Litmus (split):** thinking itself is a model capability (a feature, like 2.2). Setting the effort dial, capping output tokens and N-sample voting are your code deciding. Tree-of-Thoughts-style search is the model deciding, in the harness (3.6).
>
> Sweep angles run: vendor docs (Anthropic, OpenAI, Google), academic, skeptical read, alias sweep, security, everyday-engineer traps. No primary postmortems found. Review and trim **Must-cover**; that sets scope.

## The mental model

"Think step by step" was a prompting trick; it is now a training outcome and an API dial. The engineer's job moves from writing the reasoning to buying it: how many output tokens, on which tasks, proven on your own cases. Thinking tokens are billed as output, count against the output cap and add latency, so the dial is a cost decision first. Visible reasoning is a summary, not a faithful record: a debugging aid, never evidence of why the model answered.

## Must-cover

Ranked. `[+]` = gap in the stub.

1. **CoT, self-consistency, ToT: which were absorbed** `[+]`
   - Wei et al. (arXiv:2201.11903), Kojima et al. (2205.11916), self-consistency (Wang et al., 2203.11171), Tree of Thoughts (Yao et al., 2305.10601).
   - Verdict: explicit CoT prompting is absorbed into reasoning models. Meincke et al. (2506.07142) find only marginal accuracy gain on reasoning models for far more time and tokens, and on non-reasoning models a small gain with less consistent answers. Sprague et al. (2409.12183): CoT helps mainly on math and symbolic tasks. Self-consistency survives as harness code (N samples plus a vote), which is 3.3 voting parallelization; contrast 3.4 (sequential critique) and 3.5 (distinct personas). ToT survives as search you build (3.6). *Skip it:* readers prepend "think step by step" and pay twice. **Established** (CoT on non-reasoning models, math and symbolic); **Superseded** (explicit CoT on reasoning models); **Emerging** (ToT outside research).
2. **Why it works: test-time compute** `[+]` . OpenAI "Learning to Reason with LLMs" (Sept 2024) launched the hidden-CoT paradigm; Snell et al. (2408.03314): inference compute can beat a bigger model, by difficulty; DeepSeek-R1 (2501.12948): RL on verifiable rewards; s1 (Muennighoff et al., 2501.19393): "budget forcing" controls thinking length at inference. One paragraph. **Established.**
3. **The dial, as portable mechanics** `[+]` . Token budget versus named effort level; model-decides-whether-to-think (adaptive) versus always-on; reasoning billed as output and counted against the cap (a low cap can end with no visible text); summary returned but full thinking billed; sampling parameters restricted (Anthropic returns 400 on non-default `temperature`, `top_p`, `top_k` on current models); changing effort or budget invalidates cache breakpoints, except where the provider offers per-message effort. Provider tabs carry wire shapes only: Anthropic `thinking: {type: "adaptive"}` plus `output_config.effort` (manual `budget_tokens` is 400 on 4.7 and later); OpenAI Responses `reasoning.effort`, `max_output_tokens`, `output_tokens_details.reasoning_tokens` (Chat Completions differs: `max_completion_tokens`, `completion_tokens_details`); Google `thinkingLevel` on current models (an older token budget is not documented on the cited page; recheck what each Gemini generation rejects). Effort is "a behavioral signal, not a strict token budget" and covers tool calls and text too. No per-model bound tables; they rot. *Skip it:* a model upgrade silently changes spend or breaks the request. **Established** (the dial); **Emerging** (the API surface, which changed inside a year).
4. **Thinking across tool turns** `[+]` . Interleaved thinking: reasoning between tool calls inside one turn. Anthropic adaptive mode does it automatically; the beta header `interleaved-thinking-2025-05-14` is manual-mode only and Opus 4.6 manual has none. OpenAI and Gemini need reasoning items or thought signatures returned. Thinking blocks must come back complete and unmodified, including `redacted_thinking` (filtering on `type == "thinking"` silently drops them). Retention differs by model: newer Claude models keep prior thinking in context and bill it as input, older ones strip it, so context grows (link 5.4). Forced `tool_choice` is rejected in manual mode; adaptive allows it on most models, with exceptions. Inner loop is 2.5; this chapter owns what thinking changes inside it. **Emerging** (the surface changed on all three vendors within a year).
5. **When reasoning hurts** `[+]` . Overthinking on trivial inputs (Chen et al., 2412.21187); inverse scaling in test-time compute (Gema et al., 2507.14417); CoT hurting where deliberation hurts humans (Liu et al., 2410.21333); Anthropic notes `max` effort can overthink structured output. Adversarial overthinking: OverThink (Kumar et al., 2502.02542) injects decoy tasks into retrieved context and inflates reasoning tokens 12x to 46x on text datasets; this is unbounded consumption (OWASP LLM10:2025), so cap effort and tokens on steps that read untrusted input. Practical costs: first-token latency, cap exhausted by thinking, cache invalidation. Do not freeze rates. **Established** (the failure); **Emerging** (predicting it).
6. **CoT faithfulness** `[+]` . Turpin (2305.04388), Lanham (2307.13702), Chen at Anthropic (2505.05410): stated reasoning can omit what drove the answer. Korbak et al. (2507.11473): monitoring it is "a new and fragile opportunity." Do not show thinking as justification, audit on it alone or guardrail on it (4.4, 4.3). **Contested** (as oversight); **Established** (not faithful by default).
7. **Measure whether it helps** `[+]` . Effort sweep: same cases, same grader, each level, with the no-thinking baseline. Record quality, output and thinking tokens, latency p50/p95, cost; pick the cheapest level where quality holds within error. Run repeats (4.2 owns the discipline). Starting-effort table capped at three or four rows, labelled a starting point your sweep overwrites. **Established** (the practice).

## Mention-and-link

- Per-request effort routing by difficulty or step: one paragraph, 3.2 and 8.4. **Emerging.**
- Agent loop and ReAct → 2.5. Plan-and-execute, ToT as planning → 3.6. Evaluator-optimizer → 3.4.
- Prompt versioning (effort belongs in pinned config) → 4.1. Eval design → 4.2. Guardrails → 4.4. Human review → 4.3.
- Model selection and cost → 8.2, 8.4. Logging reasoning-token spend and traces → 8.1. Streaming progress → 6.3.
- Compaction and prior thinking blocks → 5.4. Whole-loop task budgets → one line, 2.6.

## Out of scope

Training reasoning models (cite R1, 8.3); SDK minutiae and per-model effort tables; benchmark leaderboards; process reward models; prompting craft for reasoning models (4.1).

## Maturity summary

- **Standard:** reasoning tokens billed and capped as output.
- **Established:** CoT on non-reasoning models; the dial as a cost decision; test-time compute; overthinking; the sweep.
- **Superseded:** explicit CoT prompting on reasoning models.
- **Emerging:** ToT-style search in production; per-request routing; predicting overthinking; interleaved thinking across tools; the API surface.
- **Contested:** CoT as oversight signal; "reasoning models truly reason" (Shojaee et al., 2506.06941, reports collapse past a complexity threshold; Lawsen, 2506.09250, attributes much of it to output-token limits and unsolvable instances, so report it as contested, with both).

Proposed chapter verdict: **Established**, with a "Last reviewed" line. The stub's "largely absorbed" is right for CoT and wrong for the budget, the live decision.

## Aliases

- reasoning techniques (Gulli, *Agentic Design Patterns*, 2025, Ch. 17), chain-of-thought (Wei), zero-shot CoT (Kojima), hidden CoT.
- extended thinking, adaptive thinking, thinking budget, `budget_tokens` (Anthropic); reasoning effort (OpenAI, Anthropic `effort`); thinking level (Google); `/effort` and `ultrathink` in Claude Code (verify in its docs).
- test-time compute, inference-time scaling (Snell), budget forcing (s1).
- self-consistency (Wang), Tree of Thoughts (Yao), interleaved thinking (Anthropic).
- Wire-level only, not chapter synonyms: reasoning items, thought signatures.

## Reader-verifiable anchors

1. In Claude Code, run the documented effort command or setting and watch the change on a single prompt (verify the exact command in Claude Code docs before drafting).
2. Read the per-provider usage field on one request: Anthropic `usage.output_tokens_details.thinking_tokens` (documented on the Extended thinking page), OpenAI `output_tokens_details.reasoning_tokens`, Google `thoughtsTokenCount`; a low OpenAI `max_output_tokens` gives `status: incomplete`.

## Incidents

None found; vendor-documented traps (cap exhausted, incomplete responses, cache invalidation) go in Gotchas.

## Named-idea candidates

- **The reasoning bill**: thinking tokens are output tokens, so every effort level is an invoice line before it is a quality setting. Ours, not canon; optional. "Sweep, don't default" stays as prose advice in item 7.

## Carrier

Listing Studio, concept first. High effort where steps are multi-step and costly to get wrong: the Repricer, or the Aldsworth desk's compliance step. Low or none where volume and latency rule: Merchant helpdesk intake, or step 3 (categorize). The phone case (`NV-PHONECASE-01`) shows overthinking on a trivial input. A three-level sweep shows the dial; no numbers unless run. No production claims.

## Code seam

New package `listing-studio/reasoning_budget`: an offline effort sweep over a stub model (fixed cases, grader, per-level tokens, latency, cost, cheapest passing level). It demonstrates item 7 and the bill; no live API calls.

## Sources

Vendor (fetched 2026-11-28): Anthropic Thinking and Extended thinking (platform.claude.com/docs/en/build-with-claude/thinking, .../extended-thinking), Effort; OpenAI Reasoning models (developers.openai.com/api/docs/guides/reasoning); Google Gemini thinking (confirm canonical URL, ai.google.dev/gemini-api/docs/thinking versus aistudio.google.com/docs/thinking). OpenAI, "Learning to Reason with LLMs" (Sept 2024).

Papers (arXiv metadata checked 2026-11-28; venues to add at draft): Wei 2201.11903; Kojima 2205.11916; Wang 2203.11171; Yao 2305.10601; Snell 2408.03314; DeepSeek-AI 2501.12948; Muennighoff 2501.19393; Turpin 2305.04388; Lanham 2307.13702; Chen Y. 2505.05410; Korbak 2507.11473; Chen X. 2412.21187; Gema 2507.14417; Liu 2410.21333; Sprague 2409.12183; Meincke, Mollick, Mollick, Shapiro 2506.07142 (abstract read); Kumar et al. 2502.02542 (abstract read); Shojaee 2506.06941; Lawsen 2506.09250 (abstract read).

> **Verify before quoting:** every per-model default, range and deprecation is volatile; re-open before shipping. Papers not marked "abstract read" were checked at metadata level only; the fact-checker must open each.

## Open questions for the author

1. Run a real effort sweep in the companion package on Listing Studio step 1 or 3, or keep it stub-only?
2. Does the starting-effort table live in-chapter or in Decision Frameworks?
3. Keep "the reasoning bill" as a named idea, marked ours, or strike it?

## Map review (Stage 1.5)

Reviewer: Gemini. 17 findings.

1. Thesis and budget: accepted, added (thesis reworded, not verbatim).
2. Litmus split: accepted-modified, kept as a split verdict, shortened.
3. Scope trim: accepted, one section and a catalog-gap line deleted; Gulli 2025 named only as alias source.
4. Security skip: accepted, OverThink verified (arXiv abstract: 13x/46x/12x); `redacted_thinking` verified in Anthropic docs.
5. Sampling parameters and thinking retention: accepted, both verified in Anthropic docs.
6. Seam fixes: accepted, effort routing demoted to Mention-and-link, self-consistency pointed to 3.3.
7. Model-table bloat: accepted, per-model bounds removed.
8. Maturity: accepted-modified, CoT split Established/Superseded; interleaved thinking set to Emerging.
9. 2506.07142 misattribution: accepted, abstract opened; the variability claim was about non-reasoning models.
10. Vendor facts: accepted-modified, forced `tool_choice` caveat verified and Responses API labelled; Gemini 4 error, Flash-Lite `0` and per-message `output_config` cache claim unverified, so hedged for the fact-checker.
11. Missing sources: accepted, s1 (2501.19393) and Lawsen (2506.09250) abstracts opened; OpenAI Sept 2024 post not opened, flagged.
12. Carrier names: accepted, Repricer, Merchant helpdesk, categorize and phone case confirmed in the carrier bible.
13. Anchors and open questions: accepted-modified, open questions added; Claude Code command not verified, flagged for drafting.
14. Aliases: accepted-modified, Gulli attribution and extra aliases added; `/effort` and `ultrathink` unverified.
15. Weak named idea: accepted, "Sweep, don't default" struck.
16. Venues: accepted-modified, venues deferred to draft (not verified here); URL ambiguity flagged.
17. 8.1 pointer and table cap: accepted.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis as folded. Verdict: Established, with a "Last reviewed: 2026-11" line. Explicit CoT on reasoning models is Superseded, interleaved thinking across tools is Emerging, and CoT as an oversight signal is Contested. Each verdict gets one argued sentence.
2. Code: yes, but stub-only. The new package `listing-studio/reasoning_budget/` runs an offline effort sweep over a scripted model that picks the cheapest passing level and prints the bill. No live sweep on Listing Studio; that would be a first-hand claim, which is the author's call. Tests use stdlib and pydantic only.
3. The starting-effort table stays in this chapter, kept short and framed as "start here, then sweep". Every row needs a cited source or is stated as a default to test. It does not move to Decision Frameworks.
4. "The reasoning bill" is plain wording only. It is not bolded and not presented as a named idea. Author checklist.
5. Map items that stay unverified (the Gemini 4 thinkingBudget behaviour, per-message output_config caching, Claude Code /effort and ultrathink, the OpenAI Sept 2024 post) ship only if the fact-checker opens a primary source. Otherwise they are cut.
6. No From-production callout and no coinage. Shipped chapters are not edited. The 1.5 and 2.5 cross-references stay plain text if those chapters are unmerged.

## Reconcile log (Stage 5)

Orchestrator notes:

1. Anthropic usage reporting: fixed. `usage.output_tokens_details.thinking_tokens` verified on the Extended thinking page; the word-count heuristic is gone from the chapter and `effort_example.py`.
2. Google token budget footnote: softened. No primary source opened for a 2.5 token budget, so the footnote and map name only thinking levels and thought signatures.
3. Cross-vendor claim on Anthropic-only evidence: softened. One rule is stated as general; the other two are labelled Anthropic's guidance.
4. "Start low" versus the table's "medium": fixed. Subtitle and In short now say "start each step as low as its kind of work allows"; table rows give actions.
5. Cap fact restated about eight times: fixed. Repeats cut.
6. Aphoristic closers: fixed. Cut or replaced with the concrete result of the run.
7. Undefined terms: fixed. Adaptive thinking, `redacted_thinking`, p50/p95 and MDF are glossed on first use (plus reasoning model, grader, Prop 65, reasoning items, thought signatures).
8. SVG numbers: fixed. Bars, labels and `<desc>` match the scripted run (120/0.50, 1,920/0.50, 6,420/1.00, 15,120/0.50; medium shipped), and the panel is labelled as invented numbers.
9. Cap 5,000 versus 2,000: fixed. Default cap is 5,000 in code and prose; step 5 is the explicit experiment of dropping it to 2,000.
10. Build listing incomplete: fixed. Added the `sweep-cases` and `sweep-main` blocks, `cheapest_passing`, and anchors that include imports and clients; three new tests; pytest 142 passed.

QA and second-engine findings:

11. Forced `tool_choice` and Sonnet 5.5 thinking defaults: fixed. Verified on the Thinking page; no up-front thinking uses `between_tools`.
12. "Behavioral signal, not a strict token budget" quote: rejected as a finding. Verbatim on the Effort page.
13. Structured-output overthinking generalized to all models: softened. Attributed to Anthropic's guidance for one model at `max`.
14. `gpt-6.2-sol` rejects `none`; effort values are model-dependent: fixed in code comments and the OpenAI footnote. The model ID itself is intentional.
15. Per-message effort and caching: fixed. Verified on the Effort page; added to the cache gotcha.
16. Shojaee and Lawsen "reasoning at all" debate: cut for budget and scope; author checklist.
17. "Superseded" wording for explicit CoT in the maturity paragraph: softened to a plain statement that adaptive thinking narrows the gap.
18. Liu "implicit statistical learning" example and the Korbak "fragile because" clause: cut, not verifiable against the cited abstracts.
19. Truncated replies graded as passes: fixed. `stop_reason == "max_tokens"` returns empty text and grades as a failure (Anthropic tab).
20. LangGraph tab truncation detection: deferred. The field was not verified for the wrapper.
21. Statistical uncertainty versus the tolerance band: deferred, partly addressed by the floor-and-tolerance pick.
22. Pointer to whole-run budgets: deferred to a later chapter.
23. Tree-of-thoughts search attribution: fixed. The search loop is attributed to code.
24. Map wording on a scope trim and the `thinking_tokens` anchor: fixed in this map.
