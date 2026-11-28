# Coverage map: Self-Improving Systems (chapter 9.7)

> Research-derived spec for what the chapter must cover so a reader can tell which "self-improving"
> claims are engineering they can use today and which are research. Sweeps run: academic and
> benchmarks, vendor and tool docs, skeptical read, alias sweep, security and failure modes.
> Review and trim **Must-cover**; that sets scope. Last swept 2026-11-28.

## Thesis

Across-run self-improvement is useful only when its gains survive evaluation outside the feedback
used to select its edits, and when the evaluator and the promotion path are out of the optimizer's reach.

## Mental model

"Self-improving" names one loop with several different artifacts inside it (a prompt, a skill, a
memory, a program, the harness, the weights). The litmus split: the model proposes edits and
actions; your code scores, promotes and rolls back. A prompt that tells an agent to keep or
discard its own experiments is instruction, not enforcement. Persistence means future reuse, not
merely crossing a process boundary.

## Must-cover

Ranked. `[+]` = gap (the stub has no body).

1. **Update target** `[+]`: prompt, skill document, memory or context playbook, program or harness
   code, weights. Different blast radius and rollback per target. The survey organizes the field by
   target and by driving signal; attribute it. *Skip it:* every claim borrows credit from the
   strongest target. **Emerging** (as taxonomy). (Ren et al., arXiv:2607.13104.)
2. **Prompt optimization against a metric** `[+]`: evolve prompts against a dev set offline; the
   artifact is a diffable text file. GEPA reports beating GRPO by 6% on average (up to 20%) with up
   to 35x fewer rollouts, and MIPROv2 by over 10%; DSPy is the programming model; OPRO the earlier
   line. Gotcha, verified in source: `dspy.GEPA.compile` falls back to the trainset when `valset`
   is omitted (it logs a warning), so the default optimizes and validates on the same data.
   **Established offline** (as engineering); the general result is **Emerging** (authors' benchmarks).
   (arXiv:2507.19457; 2310.03714; 2309.03409.)
3. **The selection gate, and its limits** `[+]`: accept an edit only if it improves data the
   proposer did not train on; bound edit size; log rejected edits. Three data roles must stay
   apart: feedback the optimizer learns from, selection data queried repeatedly to accept or
   reject, and a final test touched once. Repeated accept/reject queries overfit the selection
   set (adaptive overfitting), and a strict-improvement rule can select noise, so use
   uncertainty-aware comparisons and regression checks. SkillOpt gates on a selection split,
   reports on a separate test split, and feeds rejected-edit score drops to later reflection; VERSE
   reports self-evolution helped only with execution-based verification. The gate is a control,
   not proof that drift is prevented. Statistical depth belongs to 4.2. **Emerging** (preprints).
   (SkillOpt arXiv:2605.23904; VERSE arXiv:2610.02616; Blum and Hardt, arXiv:1502.04585.)
4. **Skills, memory and context that learn** `[+]`: Voyager (verified skill library); Reflexion
   (verbal lessons; 91% pass@1 HumanEval as reported, but that is repeated attempts with task
   feedback, the 3.4 boundary, not durable gain on unseen tasks); ACE (arXiv:2510.04618, ICLR
   2026): offline and online playbook adaptation via incremental curation, reports about +10.6% on
   agent benchmarks and names context collapse (repeated rewrites erode detail) and brevity bias.
   ACE is counterpressure: structure and curation matter beside acceptance. Include context
   economy: accumulated lessons cost tokens and attention, so retrieve, prune, consolidate and
   regression-check them. Loading mechanics live in 2.3 and 5.3, attention cost in 1.5, compaction
   in 5.4. **Emerging.** (Voyager arXiv:2305.16291; Reflexion arXiv:2303.11366.)
5. **Evolutionary program search with an external evaluator** `[+]`: AlphaEvolve; an LLM mutates
   code, automated evaluators score it, a population is kept. Reported: 4x4 complex matrix
   multiplication in 48 scalar multiplications. The verifier does the work, not the model's
   self-judgment; it transfers only where a cheap honest score exists. **Emerging** (demonstrated
   research capability, not common practice). (arXiv:2506.13131.)
6. **Self-modifying agents** `[+]`: DGM (archive of coding agents editing their own code;
   SWE-bench 20.0% to 50.0%, Polyglot 14.2% to 30.7%, as reported; Section 4.4 includes
   cross-benchmark and cross-model held-out transfer); Hyperagents (the improvement procedure is
   itself editable); ADAS and STOP precursors; STOP measured generated code bypassing its
   sandbox. Report as the authors' results under sandboxing and oversight. The DGM paper warns that
   changes optimized only for a benchmark "might inadvertently introduce vulnerabilities."
   **Emerging as research; Contested as a production practice** (no independent production
   replication found). (arXiv:2505.22954; 2603.19461; 2408.08435; 2310.02304.)
7. **Authority boundary and the evaluator as attack surface** `[+]`: the optimizer may change
   only an externally enforced editable surface. The evaluator, execution boundary, permissions
   policy, hooks and promotion step stay outside it; reviewing an evaluator diff afterward cannot
   stop a candidate that weakens it mid-trial. Name the threats as reasoned scenarios, not
   incidents: gameable metric, deleted test, loosened threshold, same-family judge. Harness
   controls are 2.6, isolation 9.4; 9.7 owns the proposed changes inside them. Mitigations:
   hold-out the proposer cannot read, deterministic checks beside judged ones. **Established as a
   risk class** (specific incidence not measured). Huang et al. (arXiv:2310.01798) supports only
   that intrinsic self-correction without external feedback is unreliable.
8. **Promotion and failure contract** `[+]`: a self-change is a change request: versioned diff,
   hard gate or human reviewer, rollback, log. A rejected or crashed candidate returns to the
   optimizer as a structured message; the live system is untouched. Artifact management belongs
   to 4.1, governance to 8.6. **Emerging** as applied to self-modification.
9. **Cost and when not to** `[+]`: candidates cost rollouts plus evaluation; budget scales with
   population times iterations; the selection set needs refreshing. Do not self-improve what you
   cannot score or cannot undo. General budgets in 8.4. **Established** (engineering).

## Mention-and-link

- Within-run critic and revise: 3.4. Weights and the train-or-prompt ladder: 8.3.
- Eval design, judges, held-out statistics: 4.2. Memory writes and poisoning: 5.3.
- The outer verify-and-retry loop: 3.7. Poisoned feedback becoming poisoned update: 4.6.
- Human approval gates: 4.3.
- Online agentic RL from traffic: AReaL2.0 (arXiv:2607.01120) is a position paper with an
  exploratory prototype and no efficacy results; one line, not evidence.

## Out of scope

Training-time RL algorithms (GRPO, PPO); synthetic-data self-training; recursive
self-improvement forecasts; building an evolutionary framework.

## Maturity summary

- **Established:** offline prompt optimization against a dev set (engineering); the
  gameable-evaluator risk; cost discipline.
- **Emerging:** skill, memory and context evolution; harness optimization with execution-based
  verification; evolutionary program search; the update-target taxonomy.
- **Contested:** self-modifying agents as a production practice; unsupervised self-improvement
  claims outside tasks with a cheap honest score (autoresearch-style loops).
- **Chapter verdict: Emerging / Contested.** Argue it as "Established offline, Emerging for
  skills, context and harness, Contested past that." "Unmeasured" is a qualifier, not a tier.

## Aliases

Umbrella synonyms: self-evolving agents; self-improving agents (Ren et al. survey title;
Hyperagents abstract); scaffold or harness self-improvement (STOP, VERSE). Mechanisms and
examples, not synonyms: automated agent design (ADAS); open-ended evolution (DGM); evolutionary
coding agent (AlphaEvolve); prompt optimization, reflective prompt evolution (DSPy, GEPA, OPRO);
skill evolution (SkillOpt); verbal reinforcement learning (Reflexion); skill library (Voyager);
autoresearch (Karpathy's repository). The Gulli-book comparison is incomplete here: no chapter
mapping was recorded. The "Also called" cell needs author sign-off.

## Reader-verifiable anchors

- `pip install gepa` and `dspy.GEPA` (gepa-ai/gepa README, verified): a reader can run a public
  prompt optimizer. The anchor must pass an explicit `valset`; the omitted-valset fallback above
  is the everyday gotcha. `compile` requires exactly one of `auto`, `max_full_evals`,
  `max_metric_calls`.
- Karpathy's `autoresearch` (MIT): `program.md` instructs the agent to keep a commit if
  `val_bpb` improved and `git reset` otherwise, under a fixed five-minute training budget. The
  agent decides keep or discard by following instructions; no controller enforces it. Use it as
  the contrast case for the litmus line, not as "code decides."

## Incidents

None found with a primary postmortem. The field publishes risk in authors' safety sections (DGM,
STOP), not production postmortems. Do not invent one.

## Named-idea candidates (author accepts or strikes)

- **Three data roles** (feedback, selection, final test) as the discipline behind the gate.
- **The evaluator is the attack surface.** "Update target" is the survey's axis, not an earned
  named idea.

## Carrier

Primary: Listing Studio's description-writing prompt optimized against a proposed, fictional
fixture of merchant edits (a text file you review); a skill document for a recurring catalog fix
gated on a held-out set of listings. Contested end: the Repricer rewriting its own rules is what
the authority boundary must stop. AlphaEvolve is shown research-only. No "From production:" line
is drafted here; that is the author's call.

## Seams

3.4 owns within-run critic and revise; 9.7 owns changes that persist for future reuse. 5.3 owns
memory mechanics, 9.7 the gate on learned writes. 4.2 owns evaluator design and statistics. 2.6
owns the harness, 9.4 isolation. 8.3 owns weights. Neighbours 3.4, 4.2, 4.6, 5.4 exist as open
PRs; a final check against their text is owed.

## Code seam

NONE recommended. A gate function is about forty lines and the prose carries it; real optimizers
are library calls. If the author wants one: a `self_improving` package with a gate (propose,
score on selection split, accept or reject, log) using a stub scorer, offline.

## Sources

Agrawal et al., GEPA, arXiv:2507.19457 (v2 2026-02-14). Khattab et al., DSPy, arXiv:2310.03714.
Yang et al., OPRO, arXiv:2309.03409. Novikov et al., AlphaEvolve, arXiv:2506.13131. Zhang, Hu, Lu,
Lange, Clune, Darwin Godel Machine, arXiv:2505.22954. Zhang et al., Hyperagents, arXiv:2603.19461.
Hu, Lu, Clune, ADAS, arXiv:2408.08435. Zelikman et al., STOP, arXiv:2310.02304. Yang et al.,
SkillOpt, arXiv:2605.23904. Wang et al., VERSE, arXiv:2610.02616. Ren et al., Self-Improvements
in Modern Agentic Systems: A Survey, arXiv:2607.13104. Yan et al., AReaL2.0, arXiv:2607.01120.
Wang et al., Voyager, arXiv:2305.16291. Shinn et al., Reflexion, arXiv:2303.11366. Huang et al.,
arXiv:2310.01798. Zhang et al., Agentic Context Engineering, arXiv:2510.04618 (2025-10-06; ICLR
2026). Blum and Hardt, The Ladder, arXiv:1502.04585 (2015-02-16). Karpathy, autoresearch
(github.com/karpathy/autoresearch). gepa-ai/gepa README; stanfordnlp/dspy `gepa.py`.

## Verify before quoting

2026 preprints (SkillOpt, VERSE, Hyperagents, AReaL2.0, survey) are not peer-reviewed as far as
the pages showed; cite as reported. Figures below abstract level (SkillOpt 52 combinations,
VERSE 42.3% vs 39.2%) must be re-opened. Check GEPA numbers against v2. The Ren et al. axis came
from the abstract. Library APIs and autoresearch details are volatile. Mark "Last reviewed."

## Open questions for the author

1. Verdict wording: split ("Established offline, Emerging, Contested") or Emerging / Contested?
2. Code: none (recommended) or a small gate listing?
3. Include the Repricer as the cautionary carrier?
4. Rung 6 scope: one paragraph of DGM or a fuller section?
5. Alias line sign-off; any first-hand "From production:" use of prompt optimization?

## Map review (Stage 1.5)

Second engine. Sources opened: GEPA README, DSPy `gepa.py`, autoresearch
`program.md`, ACE, Blum and Hardt, SkillOpt v2 (first 100k chars), DGM v3 (first 100k chars).

1. Held-out gate vs adaptive overfitting: accepted-modified; Blum and Hardt and SkillOpt's selection/test split confirm it, folded as three data roles.
2. Immutable authority boundary: accepted; STOP sandbox measurement stands, folded into item 7.
3. Missing ACE: accepted; verified, folded into item 4 as counterpressure.
4. Context economy: accepted; added to item 4 with 2.3/5.3/1.5/5.4 links.
5. autoresearch "code decides": accepted; program.md shows the agent decides, reframed as contrast case.
6. Reflexion as durable evidence: accepted; reframed as the 3.4 boundary.
7. Maturity tiers: accepted; AlphaEvolve to Emerging, DGM held-out transfer confirmed in 4.4, Contested kept for production claims only.
8. Huang et al. over-cited: accepted; scoped to intrinsic correction, threats labeled reasoned scenarios.
9. Thesis and unsupported "narrower target" claim: accepted-modified; claim removed, thesis rewritten.
10. Ownership duplication: accepted-modified; links to 4.1, 8.6, 8.4 exist in nav; AReaL moved to mention-and-link.
11. GEPA anchor unverified: accepted; install, `dspy.GEPA` and valset fallback verified in source.
12. Production wording: accepted; "most deployed" and data-center example removed, fixture labeled fictional.
13. AReaL2.0 maturity: accepted-modified; stated as a position paper with an exploratory prototype.
14. Alias list: accepted; split and Reflexion term fixed, Gulli comparison marked incomplete.
15. Rung numbering and editorial residue: accepted; ladder renamed to update targets, "this run" text removed.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Maturity.** Top line is Emerging / Contested. The prose argues the split: offline prompt optimization is Established, skills/context/harness self-editing is Emerging, and anything past that is Contested. AlphaEvolve is Emerging. Last reviewed 2026-11.
2. **Code.** None. A small gate fragment is allowed in prose, labelled illustrative. The tested gate goes on the author checklist.
3. **Carrier.** The Repricer is the cautionary carrier, described generically. No carrier bible edit.
4. **DGM.** One paragraph.
5. **Finding 13 and the unopened AReaL2.0/Reflexion claims.** The writer verifies each on its primary page or cuts it.
6. **Omit.** No aliases, no coinage, no From-production callout.

## Reconcile log (Stage 5)

Fact-check:

1. Budget assert is in the `dspy.GEPA` constructor, not `compile`: fixed in prose and footnote (re-checked in `gepa.py`).
2. VERSE "only when verified": fixed to "in a controlled study".
3. DGM vulnerabilities quote is Section 5, not 4.4: fixed in prose ("safety discussion") and footnote.
4. AReaL2.0 is one implementation, not the paper's name: fixed in the gotcha and footnote.
5. SkillOpt accepts strict improvements, against the margin advice: fixed; the chapter says so and tells the reader to add the margin.
6. "No independent production replication" as a negative claim: softened to "none found as of 2026-11".

Prose critique:

1. Opening restates one point four times: fixed; L13 and L15 closers cut.
2. L15 double closer: fixed (cut).
3. Gate restated at L57-63: fixed; the numbered round collapsed to the two details the figure cannot show.
4. Apparatus narration at L57, L69, L93: fixed in all three; L93 now ends on the concrete failure.
5. STOP sandbox bypass buried in How: fixed; moved to Security & trust, "reported incidents" now "production incidents".
6. Hyperagents dead clause and precursor lineage: fixed; Hyperagents given its consequence (the editable surface widens to the improvement procedure, as its abstract states; the suggested "the gate becomes editable" was softened because the abstract does not say it), ADAS line and footnote cut.
7. VERSE buried: fixed; it now leads as the evidence for the thesis.
8. "Every loop that works" universal: fixed to "Loops scored on sampled data".
9. Gotcha restating L26: fixed; replaced with a new gotcha (a revertible file with irreversible effects).
10. Carrier drift (merchant uploads): fixed to supplier feed and reviewer.
11. Signposting at L34, "sharp edge", "worth remembering": fixed.
12. L67 number stack: fixed; split into two sentences, scope first.
13. L75 link dump: fixed; 1.5 and 5.4 moved to See also.
14. "Playbooks rot" gotcha restated the pruning paragraph: cut for budget.
15. Public-tool anchor for the skills rung: rejected; it would add an unverified claim about a tool's write path, and the chapter is at its 2,800 budget.
16. Maturity triple repeated in In short: rejected; In short gives actions, not labels.

Cold reader:

1. GEPA and DSPy glossed at first use: fixed.
2. val_bpb, rollouts, pass@1, HumanEval, SWE-bench, Polyglot, promotion and rung defined: fixed.
3. validation set / valset / fixture / development set / selection set: fixed; "selection set" is the one term, mapped once to DSPy's `valset` (and feedback set to `trainset`).
4. No runnable starting point: fixed; a minimal `dspy.GEPA` metric and compile sketch added, checked against DSPy's `gepa.py` (five-argument metric, exactly one budget option, `reflection_lm` required). Not a tested listing.
5. Contested verdict reasoning missing: fixed; the overclaim named is reading sandboxed, overseen benchmark gains as production readiness.
6. Huang et al. extrapolation: fixed; the step from reasoning self-correction to self-judged edits is stated.
7. Established despite self-reported gains: fixed by the verdict change below.
8. Diagram missing the feedback set: fixed; the proposer card and alt text now say "reads failures in the feedback set". Alt text shortened; the SVG desc keeps the full description.
9. Strict-improvement noise step missing: fixed; the accumulation step is stated.
10. Uncertainty-aware test and regression check: glossed.
11. Reflexion boundary blurry: fixed; its memory carries across attempts at one task, not to new tasks.
12. "Why not review the evaluator before promotion?": rejected; the sentence already says the scores came from the weakened evaluator.
13. Sample sizes, margin size, lethal trifecta and harness glosses: rejected; no verified figure exists for sample size or margin, and the other two link to their owning chapters.

Verdict change: Stage 1.6 ruling 1 ("offline prompt optimization is Established") revised to match 8.3. Eval-driven prompt tuning is Established; the optimizers that automate it are Emerging, because GEPA's headline figures are its authors' own. Top line unchanged at Emerging / Contested.
