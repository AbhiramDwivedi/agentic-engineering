# Coverage map: Synthesis (chapter 6.2)

> Research-derived spec for what the chapter must cover. Angles run: vendor docs (Anthropic,
> OpenAI), academic, skeptical read, alias sweep, everyday-engineer. Skipped: OWASP (3.3 and 4.6
> own injection depth). Review and trim **Must-cover**; that sets scope. Bar: definitive but tight.

## Thesis, litmus, budget

**Thesis.** Multi-part model output fails at the seams, not inside the parts, so code must own
layout, order, source ids and fact checks, and the model fills bounded slots and runs at most one
diff-verified editing pass.

**Litmus: your code decides.** Layout, ordering, citation ids, checks and the publish gate are
code. The editing pass is a single call over assembled text with no control-flow decision, so it
is not a new pattern. "The humanizer pass" is a local coinage (1.2 files it as such); say so.
A checker that loops the writer is 3.4; one that escalates is 4.3.

**Budget:** Standard pattern, about 2,000 to 2,800 prose words, ending at In short.

## The mental model

Writing the parts is the easy half. A deliverable fails at the seams: two sections that
contradict, a voice that changes at paragraph four, a citation that lost its source in transit,
a layout invented differently each run. Fix: **code owns the structure, the order, the
citations and the checks; the model owns the prose inside each slot.** Synthesis is the fan-in
that starts where 3.3's `gather()` returns and ends at the publish gate. It is mostly
engineering you already know.

## Must-cover

Eight items. `[+]` = new ground (the stub is empty).

1. **Template-owned slot assembly** `[+]`: each part is a typed, bounded `Section` (id, body,
   source ids); code concatenates in a fixed order from a template; headings, units, required
   blocks and compliance footers come from the template. *Skip it:* one giant generation drifts,
   truncates, cannot be partly re-run, and a required block goes missing unnoticed. Anthropic's
   sectioning: independent subtasks, outputs "aggregated programmatically." LongWriter's
   AgentWrite (arXiv:2408.07055) is the outline-then-section precedent for long output. Slot
   schemas are 2.2; a mention. **Standard.**
2. **Citation carry-through** `[+]`: the source id is a field that travels from worker to final
   page, surviving reorder, merge and rewrite. Prefer API-level citations: Anthropic's return
   `cited_text` plus location pointers, and `cited_text` is not billed as output. Gotcha:
   citations and structured outputs cannot be enabled together (volatile; re-check), so keep ids
   in your own schema and verify in code. A valid pointer is not entailment: Liu, Zhang, Liang
   (arXiv:2304.09848) find 51.5 percent of sentences fully supported and 74.5 percent citation
   precision in 2023 search engines (directional), so a rewrite can break a claim while the id
   stays. **Established** (carry-through); **Emerging** (entailment checking).
3. **The editing pass, diff-checked** `[+]`: one call over the whole so voice, units and name
   spellings are uniform. It may reword, not add or delete facts; its output is diffed against
   its input for numbers, names and cited ids. Pass summaries plus the fact table, not full
   drafts, to the checks, and keep untouchable text at the edges ("Lost in the Middle,"
   arXiv:2307.03172); depth is 1.5 and 5.4. A full re-read and re-emit costs tokens (8.4).
   **Emerging** (fidelity of voice passes is barely measured).
4. **Deduplication across parts** `[+]`: parallel sections repeat the same selling point.
   Detect in code (normalized n-gram or embedding overlap), reword with a model only where
   flagged. *Skip it:* padded output. **Standard** (detection); **Emerging** (model rewrite).
5. **Contradiction checks and a resolution policy** `[+]`: parts written blind disagree. Extract
   a small typed fact table per section and compare in code (**Established**; extraction from
   free text is lossy), or have a model read pairs (**Emerging**). Mündler et al.
   (arXiv:2305.15852) measured self-contradiction inside one model's output (17.7 percent of
   ChatGPT sentences, 2023), an intra-generation baseline, not a cross-worker benchmark. The
   chapter must say what happens on a hit: canonical-source precedence, surface the conflict, or
   escalate (4.3). Never average it away.
6. **Long output and truncation** `[+]`: the output window is smaller than the input window.
   LongWriter reports models struggling past about 2,000 words of output (2024, directional).
   Treat `stop_reason == "max_tokens"` as truncation, not a result: Anthropic says raise the
   limit or continue, and append a notice so the reader knows. OpenAI's Responses API returns
   `status: "incomplete"` with `incomplete_details.reason: "max_output_tokens"`, and reasoning
   tokens count against that cap, so a visible answer can come back empty. Structural fix: item 1.
   **Standard.**
7. **Oversized or multi-hop parts** `[+]`: when parts will not fit one window, or passing them
   through the coordinator loses detail, write each part to external storage and pass references
   (Anthropic: subagents "pass lightweight references back," avoiding the "game of telephone").
   Stuff-in-one-window versus collapse-in-stages is plain engineering; no framework citation
   opened. **Established.**
8. **Partial failure and the publish gate** `[+]`: a failed or truncated section returns a typed
   `SectionResult` (ok, failed, truncated, reason), never an exception or empty string spliced
   in. Policy: refuse to publish with a required section missing; mark an optional one omitted.
   Gate: slots filled, no leaked placeholders or tool-call text, ids resolve, length in bounds,
   then a person approves the irreversible. *Skip it:* a clipped or fabricated page ships.
   **Standard**; depth is 4.3 and 4.4.

## Mention-and-link

3.3 Orchestrator-Workers (fan-out, `gather()`); 2.2 Structured Output; 3.4 Evaluator-Optimizer;
3.5 Specialist Panel (step 5 builds the content blocks); 4.3 and 4.4 (escalation, human gate);
1.5 Context Engineering; 5.4 Compaction; 5.2 retrieval grounding; 4.6 untrusted worker output;
6.1 ingestion; 6.3 streaming; 7.1 Retry & Graceful Degradation; 8.4 Controlling Cost.
Unmerged chapters are plain text, not links.

## Out of scope

Fan-out orchestration (3.3); evaluator design (3.4, 4.2); summarization as a research field;
layout engines, PDF and CMS publishing; fine-tuning for long output (8.3).

## Maturity summary

- **Standard:** template-owned assembly; `max_tokens` as truncation; typed partial failure; dedup detection.
- **Established:** citation carry-through; fact-table comparison; external references.
- **Emerging:** entailment after rewrite; fidelity of the editing pass; model contradiction
  detection and dedup rewrite; STORM (arXiv:2402.14207, a research system, not a product pattern).
- **Contested:** none. Avoid any "one prompt writes the whole polished document" framing.

Chapter verdict: **Established**. Argue the sub-claims: code-owned assembly is Standard, the
editing pass is Emerging.

## Aliases

Verified: **fan-in**, **aggregation** (Anthropic, "aggregated programmatically"),
**synthesizer** (Anthropic multi-agent post), **scatter-gather** (on 3.3). Stub aliases kept:
output assembly, deliverable assembly. "Citation agent" is a downstream stage in that post, not
a synonym; dropped. **Chain of Density** (Adams et al., arXiv:2309.04269, 8 Sep 2023) is a
neighbour, "see also." Not swept (unopened): LangChain/LangGraph, Google ADK, OpenAI, 12-Factor,
Gulli rows for this home.

## Reader-verifiable anchors

Citations docs: `cited_text` and location indices on documents passed with citations enabled.
A chat product's "continue" prompt after a cut-off answer shows item 6 on the reader's own
screen; name a specific public tool and cite its docs at draft time (not verified here).

## Incidents

No public multi-agent assembly postmortem found. Nearest: Anthropic's telephone-game note
(item 7).

## Named-idea candidates (author accepts or strikes)

- **Template-owned assembly** (item 1, plain noun phrase).
- **Diff-checked polish** (item 3; reconciles with "the humanizer pass," a local coinage).
- **Carry the id** (a citation is a field, not a sentence the model retypes).

## Carrier

Listing Studio step 7 into step 8: the listing page, one of the three `launch_package`
deliverables (listing, email, ad copy), is assembled from its sections, then gets the brand-voice polish. Beats use canonical Aldsworth desk attributes: description says
`desktop_size_in` 60x28 while the spec block says 60x30 (contradiction); the polish pass turns
`weight_capacity_lbs` 250 into 300, or drops the Prop 65 warning (fidelity diff catches it);
description, bullets and FAQ repeat one selling point (dedup). Category scout (research
fan-out and synthesis) is the second surface for items 2 and 7. No production claims here.

## Code seam

New `listing-studio/assembly/`: its own `SectionResult` (status ok/failed/truncated, source_ids)
that wraps 3.3's `WorkerResult` (four fields, `extra="forbid"`) without touching
`fan_out/schemas.py`; template renderer; fact-table contradiction check; fidelity diff
(numbers, names, ids); `max_tokens` guard. Offline with a fake model. LangGraph default,
provider tabs for the one call that matters.

## Sources

Anthropic, "Building effective agents"; "How we built our multi-agent research system"
(anthropic.com/engineering/multi-agent-research-system); Citations docs; "Handling stop reasons"
(platform.claude.com/docs/en/build-with-claude/handling-stop-reasons); structured outputs docs
(for slot schemas, 2.2); OpenAI reasoning guide (developers.openai.com/api/docs/guides/reasoning).
Adams et al., "From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting,"
arXiv:2309.04269. Bai et al., "LongWriter: Unleashing 10,000+ Word Generation from Long Context
LLMs," arXiv:2408.07055. Shao et al., "Assisting in Writing Wikipedia-like Articles From Scratch
with Large Language Models," arXiv:2402.14207. Mündler et al., "Self-contradictory
Hallucinations of Large Language Models: Evaluation, Detection and Mitigation," arXiv:2305.15852.
Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," arXiv:2307.03172. Liu,
Zhang, Liang, "Evaluating Verifiability in Generative Search Engines," arXiv:2304.09848.

> **Verify before quoting:** 17.7, 51.5, 74.5 percent and 2,000-word figures are 2023 and 2024
> era; the citations-versus-structured-outputs incompatibility is volatile. The stop-reasons
> page's "Ensuring complete responses" section was not read, so no continuation recipe is
> stated; open it before drafting.

## Open questions for the author

1. Grounding: the stub says `production`; this map makes no production claim. Keep `production`
   (a "From production:" callout) or change to companion repo plus research?
2. Accept the split verdict (code-owned assembly Standard, editing pass Emerging)?
3. Accept Category scout as a second surface, and the eight-item list?
4. Accept the named ideas, and "the humanizer pass" kept explicitly as a local coinage?

## Map review (Stage 1.5)

Reviewer: independent second engine. Findings 1-18; verdicts below.

- 1 Litmus wrong: accepted; who-decides.md files the humanizer pass under "coined name."
- 2 Thesis and budget missing: accepted; design-system.md budget row confirmed.
- 3a URL: accepted; page opened, `multi-agent-research-system` is live.
- 3b 4.5 vs 1.5: accepted; mkdocs.yml confirms 1.5 is Context Engineering.
- 3c Unread stop-reasons section: accepted-modified; verified raise/notice text, struck continuation recipe.
- 4 Carrier contradictions: accepted; bible confirms 60x30, 250 lbs, no box count, Category scout.
- 5 Topologies and external refs: accepted-modified; Anthropic reference verified, LangGraph/ADK claims unopened so uncited.
- 6 Entailment and conflict policy: accepted-modified; arXiv:2304.09848 figures verified, ALCE and Cognition unopened.
- 7 OpenAI, Gemini, reasoning tokens: accepted-modified; OpenAI verified, Gemini shapes not found on the page, omitted.
- 8 Verdicts: accepted-modified; item 3 Emerging, dedup split, extraction Established, split verdict kept as argued sub-claims.
- 9 Trim and neighbours: accepted; ten items cut to eight, links added as plain text.
- 10 Citations: accepted-modified; structured outputs URL and AgentWrite added (not re-opened), Mündler scoped.
- 11 Incidents: accepted-modified; off-carrier incident cut, Sun-Times unverified so excluded.
- 12 Open questions: accepted.
- 13 Titles and venues: accepted-modified; full titles restored, venues omitted as unopened.
- 14 Aliases: accepted-modified; "citation agent" dropped (verified downstream), extra sweeps recorded as not done.
- 15 Anchors: accepted-modified; tool naming deferred to draft since unverified.
- 16 Named ideas: accepted; "Parts, then pass" cut, humanizer reconciled.
- 17 `WorkerResult` conflict: accepted; fan-out doc shows four fields, `extra="forbid"`.
- 18 Out of scope for the map: noted, no action.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis as folded. The chapter verdict is Established, argued in the prose: code-owned assembly is Standard and the editing pass is Emerging. The litmus is "your code decides". (Author checklist.)
2. Grounding becomes companion repo plus research, replacing the stub's `production`. A first-hand claim is not ours to make. (Author checklist.)
3. Carriers: Listing Studio is primary and Category scout is the second surface. The eight-item must-cover list is accepted.
4. "The humanizer pass" stays plain descriptive wording. It is not bolded and not presented as a coinage. Other named ideas are also plain wording only. (Author checklist.)
5. Code: new `listing-studio/assembly/` as the map specifies, offline, with a fake model. It may import 3.3's `fan_out` schemas only if they exist on origin/main. Otherwise it defines a local `SectionResult` with no cross-package import. Tests use stdlib and pydantic only.
6. Carrier scope: commerce deliverables only (listing pages, category reports).
7. No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

QA orchestrator notes:

- Ad copy vs `launch_package`: fixed. The carrier bible makes ad copy a separate package deliverable, so the template is now the listing page only; the optional `ad_copy` slot became `faq` (the bible lists FAQ as a page content block) in code, tests, prose, diagram and alt text.
- Thesis restated five times: fixed. The subtitle no longer restates it; the second-paragraph restatement and the "fix, in miniature" paragraph are cut; the definition and In short carry it.
- `gate.py` cites 4.4 for the human gate: fixed to 4.3, file and mirrored block.
- Step 7/8/9 callout: verified against the carrier bible (step 7 assemble launch package, step 8 brand-voice polish, step 9 validate and publish). The "merchandiser approves" clause is not in the bible and was cut.
- Over budget: fixed. Argued words (prose_lint's budget measure) 2,711 before, 2,668 after, with glosses added.

Prose critic:

1. 4.4 vs 4.3 in gate docstring: fixed.
2. `launch_package` vs ad-copy slot: fixed (see above).
3. Thesis restatement: fixed (see above).
4. "One pass, keep unpolished" said four times: fixed; docstring and the loop gotcha's closing repeat trimmed.
5. "Everything in this chapter is the alternative" gotcha: fixed, gotcha cut.
6. "One giant generation cannot do that": fixed, merged into step 5.
7. "60 by 29 ... wrong in a new way": fixed, plain sentence.
8. "Detection is half the job": fixed.
9. "cheapest reliable" vs lossy extraction: fixed; "reliable" dropped, extraction labelled Emerging.
10. "The measured baseline is not comforting": fixed, cut.
11. Maturity paragraph as a tour of labels: fixed; argued prose kept, sub-labels left to the meta line.
12. Docstrings re-teaching prose: fixed for the `SectionResult` docstring and field comment, and the "stump" comments in both provider adapters.
13. "humanizer pass, which describes its job": fixed, now "step 8, the brand-voice polish (the humanizer pass)", matching the bible and 1.2.
14. "This chapter is the seam between them": fixed in the callout rewrite.
15. Context advice with no instance: fixed, anchored on the spec fact table and one-line summaries. 5.4 now linked, as in See also.
16. "every hop loses detail": fixed, "can lose".
17. "short slots rarely hit the cap": softened to "less likely".

Fact-checker:

1. gate.py 4.4: fixed.
2-10. Verified claims: no change. Footnote 4 title updated to the page's current title, "Stop reasons and fallback" (re-fetched).
11. Off-carrier incident: cut with its gotcha; see second-engine 15.
12. STORM and Chain of Density further-reading entries: verified (arXiv abstract pages: title, first author, year).
13. Step 7/8/9 callout: verified against the carrier bible; approval clause cut.
14-18. Cross-links, code claim, maturity, glosses: no change needed.

Cold reader:

- "slot" undefined: fixed, glossed in the definition.
- "fan-in" undefined: fixed, "the join after a fan-out".
- "humanizer pass": fixed, glossed as step 8, the brand-voice polish.
- `gather()`, `deliverable_id`: kept; they belong to 3.3, linked in the neighbours paragraph, and `WorkerResult` is now glossed.
- Model IDs unverifiable: rejected, the IDs are intentional.
- `launch_package`, steps 7/8/9: fixed, glossed in the callout.
- `WorkerResult` undefined: fixed, glossed in the collapsed block's summary.
- "4.4's human gate" unlinked: fixed, now 4.3, linked in prose.
- "entailment" undefined: fixed, glossed.
- "evaluator-optimizer loop" in gotcha: fixed; it was the wrong neighbour, now 3.7's outer loop, glossed as a code-owned verify-and-retry loop.
- Litmus step behind "adds no new pattern": fixed, who-decides test spelled out and linked to 1.2.
- Standard part vs Established overall: fixed by naming the younger parts.
- 17.7 percent jump: fixed, the missing step added (whole output in view vs sections that never see each other).
- "Prop and 65 disappear" with repeated mentions: fixed, "the counts fall" (the Counter subtracts counts).
- "short slots rarely hit the cap": softened.
- Alt text is a paragraph: rejected; it matches the SVG `<desc>` by design and carries the trace for non-visual readers.
- Imports not shown: fixed with a one-line note that listings omit imports.
- No facts field on `SectionResult`: fixed; prose now says it is a field you would add and that the companion code takes tables as given.
- No listing for the pair-reword call: rejected for budget; it is one model call through the same diff.
- `llm` undefined in the LangGraph tab: rejected; the tab shows the provider call only, as in other chapters.
- No run command for the companion: fixed, added to the callout.
- Three restatements before the first listing: fixed (thesis cuts).
- `launch_package` and "step 7, 8, 9" callouts without introduction: fixed, glossed.

Second-engine review (OpenAI Codex, on the draft):

1. "Both errors leave you with the unpolished page" is false for misses: fixed; prose now says a miss ships the changed text, names the number-swap case, and advises keeping must-not-change text out of the pass.
2. Conflicts do not feed the gate; gate checks pre-edit slot status: softened. The prose never claimed the gate consumes conflicts; unresolved ones go to a person. Wiring them into the gate is a design change beyond reconcile scope.
3. One trailing source marker per section loses claim-level binding: softened; the citation gotcha now says so.
4. Provider adapters raise and `polish_checked` catches nothing: fixed in code; `polish_checked` keeps the original text on a failed call, with a test.
5. `model_context_window_exceeded` treated as ok: fixed; verified on Anthropic's stop-reasons page, added to `CUT_OFF`, the Messages adapter, the prose, and a test.
6. Output-security boundary missing: fixed with a short gotcha (escape per destination, keep worker text in the data part of the prompt) linking 4.6.
7. Deterministic retry assigned to 3.4: fixed; 3.7 named for code-verifier loops in neighbours, docstring and gotcha; 3.4 kept for model grading.
8. Thesis contradicts its truncation example: fixed; the opening now says the cut-off warning fails only because the page required it. "At most one pass" kept as the chapter's recommendation.
9. 3.3 handoff ids do not match the template: softened; the template is now explicitly the listing page inside the package. No adapter added.
10. Trace and diagram disagree: fixed, trace labelled a second run; companion callout now says the conflict check runs on supplied fact tables.
11. "Established overall" not re-derived: softened; fact extraction from prose downgraded to Emerging in prose and meta line; overall verdict kept.
12. Lost-in-the-Middle over-applied: fixed, labelled a heuristic from retrieval tasks; primary advice is now to keep must-not-change text out of the pass.
13. Alias sweep unfinished: rejected for this stage; aliases ship at their conservative default and are on the author checklist.
14. Footnote 4 title stale; Citations limitation hedged: fixed both.
15. Off-carrier incident: cut; the set-difference line kept in the citation gotcha.
