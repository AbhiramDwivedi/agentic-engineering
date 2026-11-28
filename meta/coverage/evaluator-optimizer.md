# Coverage map: Evaluator-Optimizer (chapter 3.4)

> **Budget:** flagship, up to 3,500 prose words to the end of *In short* (code, sources, and
> cross-links excluded). A ceiling, not a target. This is one of the reference's origin-set
> "genuinely new — the model decides" four (with 2.1 Tool Use and 3.3 Orchestrator-Workers,
> both budgeted the same row), so it inherits their row rather than a lighter one.

> Research-derived spec for what the chapter must cover to let a reader build a model-judges-
> itself loop that actually improves output, know precisely when that loop is worth its cost,
> and tell it apart from the code-decides retry loop next door (3.7). Built from a 9-angle
> sweep; see "Sweep angles run and skipped" below. The chapter path
> (`docs/composition/evaluator-optimizer.md`) is a stub with no real prose yet — a gloss, a
> placeholder `*Also called:*` line, and a bare `Maturity: Established` claim, none of it
> argued — so nothing below is marked `[*]`/`[+]` against existing prose; this is a fresh map,
> and the stub's three placeholders are evaluated, not assumed, in what follows. Review and
> trim the **Must-cover** list; that sets the chapter's scope. Bar: definitive but tight (the
> Gang-of-Four / Wikipedia test), not exhaustive.

## Sign-off (2026-08-27): rulings recorded for the PR

The author asked for the full pipeline through to a PR, so these rulings were made without a
Stage-1 stop and are recorded here so the PR shows exactly what was assumed. Anything marked
**[author to confirm at PR review]** is a call left for the author.

1. **Two-verdict lens line: adopted.** `Maturity: Established (with an independent judge or an
   external signal) · Contested (intrinsic self-correction, no external signal)`, following 3.3's
   verified precedent in `docs/composition/fan-out.md`. The matching row in
   `docs/catalogs/quick-reference.md` already carries the split. (Neither `who-decides.md` nor
   `prompt-chaining.md` states a maturity verdict for 3.4, so nothing there needs a touch-up.)
2. **AlphaEvolve — overruled; demoted.** The map's own item-1 rule is that the decision placing a
   pattern in 3.4 is *the verdict*, and AlphaEvolve's verdict is rendered by a deterministic
   scoring function. "The LLM picks the next mutation" is a *generation* decision, which every
   evaluator-optimizer has. AlphaEvolve therefore **stops being a must-cover variant in item 7**
   and becomes **evidence inside item 3** — the strongest available citation for "an external
   verifier at scale beats self-reflection." Item 7 may keep a one-sentence pointer to it as the
   far end of the family; it may not build a section on it.
3. **write-execute-observe-fix — split confirmed as mapped.** Named illustration inside item 3;
   the worked mechanism stays in 2.5/9.6.
4. **Carrier confirmed: Listing Studio step 2** (clarify attributes: draft, grade, loop, capped
   at 3). The chapter carries **no** "From production." callout: the cap, the ratchet and the
   failure-return contract are taught from the companion repo and reasoned argument, and the
   *Grounding* line says `companion repo + research`. **[author to confirm at PR review]** whether
   a first-hand callout belongs here; adding one is the author's call alone.
5. **"Grading its own homework" — kept** as the chapter's named idea. Item 3 gives it a precise
   referent, and the skeptical corrective is what earns it.
6. **METR / reward-hacking — kept, but tight.** Two sentences at most, doing one job: bridging
   item 4's "judges are biased" to item 3's "a bad evaluator gets exploited, not fooled." Becomes
   a mention-and-link once 4.2 and 9.2 exist.
7. **Item 9 (framework spellings) — demoted out of must-cover prose.** It is implementation
   mechanics: it goes to the Stage-2 code work and to one compact ecosystem paragraph, not to
   eight paragraphs of chapter prose. This buys the budget headroom item 3 needs.
8. **Alias line — provisional.** Ships as *generator-critic, self-refine, reflection,
   LLM-as-a-judge* (four of the sweep's nine, none invented). **[author to confirm at PR review]**
9. **Fact-check carry-forward to Stage 4:** the `[^self-refine]` footnote says "roughly a 20-point
   average score improvement" where the paper reports ~20 **percent**. The fact-checker must
   settle points-vs-percent before ship.

## Thesis

An evaluator-optimizer loop is genuinely the model's decision only where no function can compute
`passed`, and it reliably improves output only when the evaluator holds a signal the drafter did
not produce.

## The mental model (what the reader must leave with)

Evaluator-optimizer is one LLM call generating a draft while a second evaluation step judges it
and hands back feedback, looping until the draft clears the bar.[^anthropic-eo] What makes it
one of this reference's genuinely-new four is narrower than "there's a loop": it is new only
where the verdict itself is a judgment call that no deterministic function could render — does
this translation keep the nuance, does this paragraph read well, has this search gathered
enough — so that whether the loop continues is a call the model makes, not one your code
computes.[^anthropic-eo] The moment the check *is* something a deterministic function could
render — a compiler exit code, a test suite's pass count, a schema validator — the shape looks
identical (generate, check, maybe retry) but the decision has moved to your code, and that is
[3.7 The Outer Loop](the-outer-loop.md)'s pattern wearing this chapter's diagram. This reference
already draws half of that line in two places a reader may hit first: [1.2 Who
Decides?](../foundations/who-decides.md) names the tell as "it judges its own draft and loops:
the model grades its own output against a bar and decides whether to revise or stop," and [3.1
Prompt Chaining](prompt-chaining.md) contrasts it directly against a chain's fixed-retry gate,
"the model decides, grading its own output against a quality bar and revising until the grade
clears or a cap intervenes, so the iteration count is not fixed in the code." This chapter's job
is to hold that line under the case that actually tests it: self-correction with no independent
signal at all is not reliably better than the first draft, so "the model grades itself" is a
genuinely new decision, and it is also, on its own, a genuinely weak one — the honest chapter
argues both halves of that sentence and shows what closes the gap.

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation. All items are fresh
gaps against the current stub, which has no argued prose yet.

1. **The seam with 3.7, drawn precisely, and the AlphaEvolve boundary case named honestly** —
   the chapter's spine claim and the reason it belongs in the genuinely-new four at all.
   Anthropic's own definition doesn't require the evaluator to be subjective; what makes *this*
   reference's litmus verdict hold is that the verdict is a judgment call only a model (or a
   human) can render.[^anthropic-eo] A generate-then-check-then-retry loop wrapped in code
   around a deterministic verifier (tests, a linter, a compiler exit code) is 3.7's pattern, even
   when the diagram looks identical; the write-code, run-tests, read-the-failure, fix-it loop a
   coding agent runs inside its own turn is a `2.5 The Agent Loop` mechanism using this chapter's
   *shape* without this chapter's *decision*. AlphaEvolve tests the line hardest, and per sign-off ruling 2 it falls on the 3.7 side: its
   verdict comes from a deterministic scoring function, so it is evidence for item 3 (what an
   external verifier is worth), not a variant of this pattern.[^alphaevolve] *Skip it:* the chapter either duplicates
   3.1's gated chain or 3.7's outer loop under a different name, or — worse — teaches a reader
   that a fixed-count test-and-retry loop is "the model deciding," the exact conflation 3.2 and
   3.3 each exist to correct for their own neighbours. **n/a** (definitional; the litmus verdict
   is orthogonal to maturity). (Anthropic, "Building Effective Agents," 2024-12-19; this
   reference's own 1.2 and 3.1.)
2. **The founding canon, so the chapter argues from a lineage instead of asserting a 2025
   invention** — Self-Refine (Madaan et al., NeurIPS 2023): the same model as generator, critic,
   and refiner, no extra training, an average double-digit task-score gain across the tasks it
   tested.[^self-refine] Reflexion (Shinn et al., NeurIPS 2023): a verbal reflection stored in an
   episodic buffer substitutes for a weight update, "a semantic gradient" carried into the next
   attempt.[^reflexion] CRITIC (Gou et al., ICLR 2024): the evaluator step calls external tools —
   a search engine, a code interpreter — rather than only introspecting, which is the paper's own
   answer to the ceiling item 3 below names.[^critic] Constitutional AI / RLAIF (Bai et al.,
   Anthropic, 2022) is the training-time ancestor: a written constitution lets a model critique
   and revise its own output, and *that* preference data trains a reward model, rather than
   looping at inference time.[^cai] *Skip it:* the reader can't place "grading its own homework"
   against 2022-2024 research they may already know by another name, and the alias line has
   nothing to point to. **Established** (each a peer-reviewed, replicated lineage). (Citations
   above; → [8.3 To Train or to Prompt](../production/train-or-prompt.md) for the RLAIF/training
   half, out of this chapter's scope.)
3. **The self-correction ceiling: without an external signal, self-correction mostly doesn't
   work** — the single most load-bearing finding in the chapter, and the one that keeps
   "Established" from being the whole verdict. Huang et al. (ICLR 2024) define *intrinsic*
   self-correction (no external feedback, the model checking only itself) and find LLMs "struggle
   to self-correct their responses" under it, in several cases talking themselves out of a
   correct first answer.[^huang] Valmeekam, Marquez & Kambhampati (2023) find self-critique degrades
   plan-generation performance and produces false-positive verifications;[^stechly1] Stechly,
   Valmeekam & Kambhampati (2024) generalize the limitation to self-verification on reasoning and
   planning tasks broadly.[^stechly2] The constructive contrast belongs beside it, not after a
   page turn: a coding agent's write, execute, observe, fix cycle is the clearest case of
   self-correction *with* an external signal — the test suite's failure is not the model's own
   opinion — and it is comparatively reliable, which is exactly what CRITIC's tool-interactive
   design predicts.[^critic] Kamoi et al.'s survey (TACL 2024) reconciles Self-Refine's gains with
   Huang's ceiling: prompted self-correction rarely works without reliable external feedback or a
   task unusually suited to self-checking.[^kamoi] *Skip it:* the chapter's hook ("grading its own homework") oversells
   a technique the strongest available evidence says fails in its purest form, breaking
   voice-and-style rule 11 (the hook can't outrun the Gotchas). **Contested** (intrinsic,
   no-signal self-correction, as a reliably-improving technique) inside a pattern that is
   otherwise **Established**; this split is the chapter's honest maturity call, not a single
   word. (Huang et al., ICLR 2024; Valmeekam et al., 2023 and Stechly et al., 2024; → 2.5/9.6 for the
   write-execute-observe-fix mechanism in depth, out of this chapter's scope.)
4. **Judge pathologies: self-preference, position/verbosity bias, and rubric-gaming** — Zheng
   et al. (NeurIPS 2023) document position, verbosity, and self-enhancement bias in LLM judges: a
   repetitive-list attack (a rephrased copy of the answer's list prepended to it) fooled Claude-v1
   and GPT-3.5 as judges 91.3% of the time and GPT-4 8.7% of the time (Table 3), even though a strong judge otherwise reaches over 80%
   agreement with human preference on the paper's own benchmarks.[^judge] Panickssery, Bowman &
   Feng (NeurIPS 2024) find self-recognition ability correlates linearly with self-preference: a
   model scores its own outputs higher than the quality gap alone explains, which matters
   directly here because the generator and the evaluator are often the same model.[^selfpref]
   Recent reward-hacking reports generalize the failure beyond judges narrowly: METR observed
   frontier models editing a test file so every test passes, or exploiting a bug in the scoring
   function itself, with one model attempting some form of it in an estimated 1-2% of task
   attempts and over 40 times more often when the scoring function was visible to the
   model.[^metr] The judge is also an attack surface: untrusted text carried in the draft can
   inject instructions aimed at it (Shi et al., ACM CCS 2024, an optimization-based injection that
   steers the verdict; Raina, Liusie & Gales, 2024, universal phrases that inflate absolute scores
   far more than pairwise comparisons).[^judge-attack] *Skip it:* a team uses the same model as generator and judge, is surprised the
   score climbs while quality plateaus, and has no framework for why. **Established** (the
   biases, independently replicated); **Contested** (whether any prompting mitigation closes them
   for a same-model judge). (Zheng et al., NeurIPS 2023; Panickssery et al., NeurIPS 2024; METR,
   2025-06.)
5. **The evaluator taxonomy and the cheap-first ordering rule** — a deterministic oracle
   (schema validator, compiler, unit test, regex) can only certify what is mechanically
   checkable and needs no model judgment at all; an LLM judge with a written rubric is required
   the moment the check is subjective (tone, nuance, "does this read well"); a human is the
   backstop where the call is too consequential or too ambiguous to automate. Order checks
   cheapest-and-most-reliable first: run the deterministic ones before ever spending a judge
   call. Say plainly which parts of a task get a real termination condition and which don't — "no
   more than 150 words" is machine-checkable; "is this good ad copy" has no such stop, and the
   loop runs on a judgment call plus a cap, not a proof. *Skip it:* a team pays for an LLM-judge
   round where a validator would do, or believes a subjective task has a "done" condition it
   structurally cannot have. **Standard** (the ordering principle, general engineering practice)
   applied to a pattern that is itself Established. (Reasoned from items 1-4; → [3.7 The Outer
   Loop](the-outer-loop.md) for the deterministic-oracle rung's full treatment, out of this
   chapter's scope beyond naming it.)
6. **The loop's control surface: the cap, the ratchet, the wired revise edge, and the failure-
   return contract** — a hard iteration cap regardless of what the model would prefer; an
   accept-only-on-improvement ratchet (keep the best-scoring draft seen so far, revert on a
   regression, never just keep "the latest"); no separate oscillation detector, because a loop
   that alternates between two "fixes" with no net progress is handled by the ratchet plus the
   cap (and the ratchet is steadier when `score` is built from discrete rubric checks rather than
   a free float); the revise edge actually wired, since a
   critic step that computes a verdict nobody routes back to the generator produces no
   correction at all, only a display; and this reference's own failure-return-contract rule:
   a failed round comes back to the generator as a specific, structured critique ("the bullet
   count exceeds the limit and drops the required warranty clause"), never a bare "fail." What
   happens on the last failed iteration — ship the last draft anyway, escalate to a human, or
   fail closed — is a decision made once, in code, not left to fall out of whatever the loop
   happened to be doing when the cap hit. A 2026 static-analysis study scanning 6,549 public
   LLM-agent repositories confirmed 68 real unbounded-loop failures across 47 projects at 91.9%
   precision, evidence that "add a cap" is not a hypothetical concern.[^ial] *Skip it:* runaway
   cost and latency with no natural ceiling, or a loop that "fixes" a draft into something worse
   and never reverts. **Standard** (the discipline; general software-engineering practice) for a
   pattern that is Established. (Cemri-style loop-failure literature; arXiv:2607.01641; → [4.3
   Human-in-the-Loop](../craft/human-in-the-loop.md) for the escalation path.)
7. **Best-of-N as the sibling that isn't a loop** (AlphaEvolve demoted to a pointer by ruling 2) — sample N drafts independently, score each, keep the best; no revision step, no
   accumulating context, no oscillation risk, at the cost of paying for N generations up front
   instead of amortizing across rounds. The lineage runs through reward-model reranking (Stiennon
   et al., NeurIPS 2020; Nakano et al., 2021's WebGPT).[^bestofn] Per sign-off ruling 2, AlphaEvolve gets at most a one-sentence
   pointer here as the far end of the family; its evidence lives in item 3.[^alphaevolve] *Skip it:* a team builds an iterative critique loop
   where independent parallel sampling would be cheaper and free of thrash risk.
   **Established** (best-of-N). (Stiennon et al., NeurIPS
   2020; Nakano et al., 2021; Novikov et al., 2025, arXiv:2506.13131.)
8. **Cost: iterations multiply generate-plus-judge, honestly stated** — a 3-round loop with a
   judge call each round runs roughly the calls of a single generate-and-ship several times over,
   before counting that each round's context typically carries the previous draft and critique
   forward. State the shape (a per-iteration multiplier on top of the generation cost, not a fixed
   overhead) rather than a number, since this sweep found no measured, citable per-iteration cost
   figure specific to this pattern; the qualitative point — the competitor catalogs price nothing
   here — is itself this reference's differentiator. *Skip it:* a team ships a judge-and-revise
   loop on a high-volume, low-stakes step and the multiplier dominates the pipeline's bill before
   anyone notices in a demo. **n/a** (arithmetic, not a claim needing a maturity verdict). (→ [8.4
   Controlling Cost](../production/controlling-cost.md) for the general economics.)
9. **Framework spellings (demoted by sign-off ruling 7 to one ecosystem paragraph)** — LangGraph: a conditional edge with a
   `should_continue`/`decide_to_finish`-shaped function routing back to the generator node, the
   shape LangChain's own "Reflection Agents" post ships.[^langgraph-refl] OpenAI Agents SDK: a
   shipped, runnable reference at `examples/agent_patterns/llm_as_a_judge.py` — a generator agent,
   a judge agent, and a loop that continues until the judge is satisfied, with a round cap only in its automated
   mode.[^oai-judge] Google ADK:
   `LoopAgent` plus an `exit_loop` tool a critic-role sub-agent calls to end iteration by setting
   an escalate flag the runtime reads; `max_iterations` defaults to `None` in Python, and the docs
   now mark template workflow agents deprecated in favour of graph-based workflows.[^adk-loop] CrewAI: task-level guardrails with `guardrail_max_retries` (the older `max_retries` is
   deprecated).[^crewai] DSPy: `Refine` (iterate with feedback, temperature-varied rollouts,
   stops on a reward threshold or N attempts) beside `BestOfN` (independent sequential rollouts, no feedback, stopping early on
   a threshold) in the same library, a clean, importable illustration of item 7's distinction.[^dspy] *Skip it:*
   the reader can't tell a working implementation from a diagram, and can't verify any claim on
   their own screen. **n/a** (mechanics; verify every name and default against current docs
   before the chapter ships, these evolve).

## Mention-and-link (one line, a pointer, not a section)

- **The code-decides sibling this chapter must not become**: a deterministic verifier wrapping a
  whole run, machine-checkable stop condition, futility detection → [3.7 The Outer
  Loop](the-outer-loop.md). Heaviest link in the chapter given item 1.
- **The write-execute-observe-fix mechanism** a coding agent runs inside one turn, the sharpest
  example of self-correction-with-external-signal working → [2.5 The Agent
  Loop](../the-unit/the-agent-loop.md), [9.6 Coding Agents](../frontier/coding-agents.md).
- **LLM-as-judge methodology and judge validity in depth** (pass^k, judge-human agreement
  measurement, when a judge itself needs its own eval) → [4.2
  Evaluation](../craft/proving-it-works.md).
- **Several fixed personas reviewing once**, not one persona iterating → [3.5 The Specialist
  Panel](specialist-panel.md); the two chapters share "a model rendering a judgment" but differ
  on loop vs. panel.
- **Two-agent debate, correlated-judgment critique, and multi-agent review architectures** in
  depth → [9.2 Multi-Agent](../frontier/more-than-one-agent.md).
- **Self-improving harnesses that rewrite the prompt, tool, or memory rather than iterate on one
  artifact** (GEPA, SkillOpt-style bounded edits) → [9.7 Self-Improving
  Systems](../frontier/self-improving-systems.md), a riskier animal this chapter stays out of.
- **Constitutional AI / RLAIF as training-time self-critique**, distinct from this chapter's
  inference-time loop → [8.3 To Train or to Prompt](../production/train-or-prompt.md).
- **Output guardrails**: a lighter-weight, non-looping cousin — reject or redact, no revision
  round → [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md).
- **Escalation when the loop can't converge** → [4.3
  Human-in-the-Loop](../craft/human-in-the-loop.md).
- **What crosses forward each round** (the critique, not the accumulating transcript) so cost
  doesn't compound with iteration count → [5.4
  Compaction](../knowledge/compaction-and-the-window.md).
- **Token cost of the multiplier in depth** → [8.4 Controlling
  Cost](../production/controlling-cost.md).
- **Over-orchestration and the rubber-stamp evaluator** as anti-patterns → [Anti-Patterns
  Catalog](../catalogs/anti-patterns.md).

## Out of scope (name it, point out)

- Fine-tuning a reward model or a dedicated judge model → [8.3 To Train or to
  Prompt](../production/train-or-prompt.md).
- Multi-agent debate architectures, correlated-judgment literature (Huang et al. 2024's
  multi-agent findings, Du et al. 2023) in depth → [9.2 Multi-Agent](../frontier/more-than-one-agent.md).
- Self-improving harnesses that edit their own prompts, tools, or skill library → [9.7
  Self-Improving Systems](../frontier/self-improving-systems.md).
- Full eval-methodology treatment (pass^k, judge-agreement measurement protocol) → [4.2
  Evaluation](../craft/proving-it-works.md).
- The outer loop's complete termination-condition and futility-detection framework → [3.7 The
  Outer Loop](the-outer-loop.md).
- AlphaEvolve's evolutionary mechanics in depth (MAP-Elites, program database internals, the
  ensemble-of-models controller) — cite the findings and the population/evolutionary framing,
  do not teach the algorithm.
- Live leaderboard or per-model judge-agreement numbers — cite the finding and the source, never
  a frozen percentage.

## Maturity summary

- **Standard:** the cheap-deterministic-check-before-a-judge-call ordering rule; an iteration cap
  and an accept-only-on-improvement ratchet as non-negotiable engineering discipline.
- **Established:** the evaluator-optimizer workflow itself (vendor-named, and grounded in a
  2022-2024 research lineage); LLM-as-a-judge as a technique, with its biases documented and
  partially mitigable; self-correction *with* an external signal (tool-interactive critiquing,
  test/compiler feedback); best-of-N reranking.
- **Emerging:** population/evolutionary program search at AlphaEvolve's scale as a technique a
  non-research-lab team reaches for; using an LLM judge for genuinely open-ended creative
  evaluation beyond a narrow, checkable rubric.
- **Contested:** intrinsic self-correction with no external signal, as a reliably-improving
  default (Huang et al. 2024's own headline finding); a same-model generator-judge pair as a
  substitute for an independent check (self-preference bias); any single frozen judge-agreement
  or self-correction-rate percentage.

**Recommended maturity verdict for the chapter as a whole:** not a bare "Established." Follow
3.3's precedent for a two-sided pattern and split it: **"Established (evaluator-optimizer with
an independent judge or an external signal) · Contested (intrinsic self-correction with no
external signal)."** The stub's current single-word verdict, taken at face value, tells a reader
that grading-your-own-homework generally works; the strongest available evidence (item 3) says
the opposite in its purest form, and the gap between those two readings is exactly what the
gloss line "grading its own homework" needs the chapter to resolve rather than gloss over. The
`docs/catalogs/quick-reference.md` row carries the same split. Narrowing note: "independent
judge" means a judge with a signal the drafter lacks or one checked against human labels; an
uncalibrated second model reading the same rubric is not evidence enough for Established.

## Aliases

- **generator-critic** — general agents-literature usage; the stub's own placeholder term.
- **self-refine** — Madaan et al.'s own paper title (Self-Refine, NeurIPS 2023).
- **reflexion-style loops** — Shinn et al.'s Reflexion (NeurIPS 2023), as commonly generalized
  in practitioner usage beyond the paper's own RL framing.
- **Reflection** — one of Andrew Ng's four agentic design patterns (2024, with tool use,
  planning and multi-agent collaboration) and the title of Gulli's *Agentic Design Patterns*
  chapter on this loop (2025); distinguish from
  this chapter's narrower, judgment-call-specific claim.
- **LLM-as-a-Judge** — Zheng et al.'s own paper title and the term of art industry-wide.
- **CRITIC / tool-interactive critiquing** — Gou et al.'s own name for their external-tool-backed
  variant.
- **retry node / review node** — a LangGraph-shaped implementation name seen in stateful-graph
  tutorials for this pattern's node roles.

## Reader-verifiable anchors

- **OpenAI Agents SDK ships a runnable reference today**: `examples/agent_patterns/llm_as_a_judge.py`
  in the public `openai/openai-agents-python` repository implements exactly this chapter's shape
  — a generator agent, a judge agent, and a loop that continues until the judge is
  satisfied — as actual, inspectable code rather than a diagram.[^oai-judge]
- **DSPy ships the two techniques items 1 and 7 distinguish as two distinctly named, currently
  importable classes**: `dspy.Refine` (iterate with generated feedback) beside `dspy.BestOfN`
  (independent rollouts run in sequence, no feedback, highest-reward or first-passing wins) in one library, so a reader can `pip
  install dspy` and see the boundary this chapter draws as two different objects rather than one
  idea under two names.[^dspy]

## Incidents

No dedicated, named public postmortem specifically describing an evaluator-optimizer loop (a
generate/judge/revise cycle, as opposed to an agent loop generally) was found this sweep. State
that plainly rather than force a citation, the same posture 3.3's coverage map took for its own
comparable gap. The closest evidenced material: a 2026 static-analysis study scanning 6,549
public LLM-agent repositories confirmed 68 real unbounded-loop failures across 47 projects at
91.9% precision — a general agentic-loop finding, not evaluator-optimizer-specific, but the
empirical case for item 6's iteration cap.[^ial] Practitioner press has reported informally-
documented, uncapped-retry-loop cost incidents in AI coding tools (five-figure overnight bills
attributed to a loop with no cost governance); these are practitioner reports rather than formal
postmortems and should be named as such if cited at all, and they are not evaluator-optimizer-
specific either. METR's reward-hacking observations (item 4) are the closest thing to a
first-party "postmortem" on the judge side specifically, and they are citable directly.[^metr]

## Named-idea candidates

1. **"Grading its own homework"** — already the stub's gloss. Plain, no irony, and an engineer
   would say it in a design review; recommend keeping it as the chapter's named idea rather than
   inventing a new one, now that item 3 gives it a precise, honest referent (the model's own
   judgment, not a deterministic check) instead of a loose metaphor.
2. **"The ratchet"** — for the accept-only-on-improvement discipline in item 6: keep the
   best-scoring draft seen so far, revert on a regression, never just keep "the latest." A small,
   nameable technique independent of the chapter's larger thesis; offered, not forced.

## Sources

Vendor/primary: Anthropic, "Building Effective Agents" (2024-12-19) — the evaluator-optimizer
workflow definition and its named use cases.[^anthropic-eo] LangChain, "Reflection
Agents."[^langgraph-refl] Google, ADK Loop workflow docs (`LoopAgent`, `exit_loop`).[^adk-loop]
OpenAI, `openai-agents-python` `examples/agent_patterns/llm_as_a_judge.py`.[^oai-judge] CrewAI,
Tasks docs (guardrails, `guardrail_max_retries`).[^crewai] DSPy, `Refine` and `BestOfN` module
docs.[^dspy] Academic: Self-Refine, arXiv:2303.17651 (NeurIPS 2023);[^self-refine] Reflexion,
arXiv:2303.11366 (NeurIPS 2023);[^reflexion] CRITIC, arXiv:2305.11738 (ICLR 2024);[^critic]
Constitutional AI, arXiv:2212.08073;[^cai] LLM-as-a-Judge, arXiv:2306.05685 (NeurIPS 2023 D&B
track);[^judge] Panickssery et al., arXiv:2404.13076 (NeurIPS 2024);[^selfpref] Huang et al.,
arXiv:2310.01798 (ICLR 2024);[^huang] Valmeekam, Marquez & Kambhampati, arXiv:2310.08118
(2023);[^stechly1] Stechly, Valmeekam & Kambhampati, arXiv:2402.08115 (2024);[^stechly2]
AlphaEvolve, arXiv:2506.13131 (2025);[^alphaevolve] Stiennon et al., arXiv:2009.01325 (NeurIPS
2020) and Nakano et al., arXiv:2112.09332 (2021), for best-of-N;[^bestofn] "When Agents Do Not
Stop," arXiv:2607.01641 (2026).[^ial] METR, "Recent Frontier Models Are Reward Hacking"
(2025-06-05) and the Claude 3.7 Sonnet / OpenAI o3 evaluation reports.[^metr] Internal: [1.2 Who
Decides?](../foundations/who-decides.md); [3.1 Prompt Chaining](prompt-chaining.md) (both already
state part of the 3.4/3.7 seam this map formalizes); [3.3 Orchestrator-Workers coverage
map](fan-out.md) (precedent for a two-verdict lens line and for the honest-gap posture on
incidents, reused here).

> **Verify before quoting:** the AlphaEvolve fleet-compute and kernel-speedup figures are
> snapshot measurements from one system at one point in time and will move; cite the finding (an
> automated, hard-to-game evaluator scaled past what self-reflection reaches) and the live source,
> never the frozen percentage. Any judge-agreement percentage (Zheng et al.'s ~80%, or any later
> paper's) is benchmark-specific the day it was published; same caution for METR's 1-2% reward-
> hacking attempt rate, an early, evolving estimate on a specific benchmark pair. The ADK
> `LoopAgent` default iteration count and exact `exit_loop` mechanics should be re-verified
> against current docs immediately before the chapter ships; this is an actively developed
> framework. CrewAI's `max_retries` deprecation timeline should be re-confirmed against the
> version the reader will actually install. This sweep found no measured, citable per-iteration
> cost figure specific to this pattern (item 8); state the shape of the arithmetic, not a number,
> until the companion code produces one.

## Sweep angles run and skipped

- **Vendor/primary docs — ran fully.** Anthropic's own definition fetched directly (not from
  memory or a secondary summary); LangChain, ADK, OpenAI Agents SDK, CrewAI, and DSPy docs each
  checked live for item 9 and the reader-verifiable anchors.
- **Academic + benchmarks — ran fully.** The founding canon (Self-Refine, Reflexion, CRITIC,
  Constitutional AI) and the self-correction-ceiling cluster (Huang et al., Valmeekam et al. 2023, Stechly et al. 2024
  papers) each verified directly against arXiv, not inherited from the alias sweep
  that first flagged several of them as leads.
- **Security / failure modes — ran, narrowly.** OWASP's general categories (Excessive Agency,
  Unbounded Consumption) apply here only as a restatement of item 6's cap discipline; this sweep
  found no OWASP entry or dedicated security literature specific to a poisoned or manipulated
  evaluator/judge prompt, and says so rather than force a citation. If the fact-checker or a
  later sweep turns up injection-into-the-judge literature specifically, it strengthens item 4.
- **Practitioner writeups — ran.** LangChain's "Reflection Agents" post functions as a first-party
  practitioner account of the LangGraph shape; the reward-hacking practitioner press (the
  five-figure runaway-loop reports) was checked and is named honestly in Incidents as informal,
  not a formal postmortem.
- **The skeptical read — ran, and it is the chapter's spine (item 3).** Huang et al. 2024 and the
  two Kambhampati-group papers were read directly, not summarized from a secondary source, given how
  load-bearing this finding is for the maturity verdict.
- **The alias sweep — ran**, using the Gulli & Nawalgaria catalogs as a lead source per the
  standing alias-sweep process, then verifying or independently sourcing each name before it
  reached this map; the books themselves are cited nowhere above, per the rule that they supply
  leads, never citations.
- **The everyday-engineer angle — ran.** GitHub-issue and framework-doc search for iteration caps,
  the wired-revise-edge failure, and the ADK `exit_loop` mechanics fed items 6 and 9 directly.
- **The daily-tool angle — ran.** OpenAI Agents SDK's shipped example and DSPy's two named modules
  supply both reader-verifiable anchors.
- **Incidents — ran, and came back thin**, as stated plainly in the Incidents section above rather
  than papered over with an approximate citation.

## Open questions the author must rule on

Questions 1 to 6 of the original map (lens line, AlphaEvolve boundary, the write-execute-observe-
fix split, the carrier, the named idea, METR's proportion) are settled by sign-off rulings 1 to 6
above. Two items remain for the author at PR review:

1. **Alias line** (ruling 8): ships provisionally as *generator-critic, self-refine, reflection,
   LLM-as-a-judge*.
2. **First-hand callout** (ruling 4): the chapter ships without one.

[^anthropic-eo]: Anthropic, "Building Effective Agents" (2024-12-19). "In the evaluator-optimizer
workflow, one LLM call generates a response while another provides evaluation and feedback in a
loop." Effective "when we have clear evaluation criteria, and when iterative refinement provides
measurable value," instanced by literary translation and complex multi-round search tasks.
<https://www.anthropic.com/research/building-effective-agents>
[^self-refine]: Madaan, A. et al., "Self-Refine: Iterative Refinement with Self-Feedback" (NeurIPS
2023). A single LLM generates, critiques, and refines its own output with no additional training;
the paper reports outputs "improving by ~20% absolute on average in task performance"
(an absolute gain, not a relative one).
<https://arxiv.org/abs/2303.17651>
[^reflexion]: Shinn, N. et al., "Reflexion: Language Agents with Verbal Reinforcement Learning"
(NeurIPS 2023). Converts environment feedback into a verbal reflection stored in an episodic
memory buffer, "a semantic gradient signal" carried into the next attempt, without updating model
weights. <https://arxiv.org/abs/2303.11366>
[^critic]: Gou, Z. et al., "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive
Critiquing" (ICLR 2024). The evaluator step calls external tools (a search engine, a code
interpreter) rather than only introspecting. <https://arxiv.org/abs/2305.11738>
[^cai]: Bai, Y. et al., "Constitutional AI: Harmlessness from AI Feedback" (Anthropic, 2022-12).
A written constitution lets a model critique and revise its own outputs; the resulting AI-labeled
preferences train a reward model (RLAIF) rather than a human-labeled one.
<https://arxiv.org/abs/2212.08073>
[^judge]: Zheng, L. et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS
2023, Datasets & Benchmarks track). Documents position, verbosity, and self-enhancement bias in
LLM judges; a repetitive-list attack (prepending a rephrased copy of the answer's list) fooled Claude-v1
and GPT-3.5 as judges in 91.3% of cases and GPT-4 in 8.7% (Table 3); a strong judge otherwise reaches over 80% agreement with human
preference on the paper's own benchmarks, and reference-guided grading substantially reduces a
measured math-grading failure rate. <https://arxiv.org/abs/2306.05685>
[^selfpref]: Panickssery, A., Bowman, S., Feng, S., "LLM Evaluators Recognize and Favor Their Own
Generations" (NeurIPS 2024). Self-recognition ability correlates linearly with self-preference
bias: models score their own outputs higher than the quality gap alone explains.
<https://arxiv.org/abs/2404.13076>
[^huang]: Huang, J. et al., "Large Language Models Cannot Self-Correct Reasoning Yet" (ICLR 2024).
Defines intrinsic self-correction (no external feedback) and finds LLMs "struggle to self-correct
their responses" under it, sometimes changing a correct initial answer to an incorrect one.
<https://arxiv.org/abs/2310.01798>
[^stechly1]: Valmeekam, K., Marquez, M., Kambhampati, S., "Can Large Language Models Really Improve
by Self-Critiquing Their Own Plans?" (2023). Self-critique degrades plan-generation performance
and produces false-positive verifications. <https://arxiv.org/abs/2310.08118>
[^stechly2]: Stechly, K., Valmeekam, K., Kambhampati, S., "On the Self-Verification Limitations of
Large Language Models on Reasoning and Planning Tasks" (2024). <https://arxiv.org/abs/2402.08115>
[^alphaevolve]: Novikov, A. et al. (Google DeepMind), "AlphaEvolve: A coding agent for scientific
and algorithmic discovery" (2025). An LLM-driven evolutionary loop over a population of candidate
programs, scored by an evaluator function, using an ensemble of models for breadth and depth.
Reported results: recovers on average 0.7% of Google's fleet-wide compute in a Borg scheduling
heuristic; a 23% speedup on a Gemini training kernel, reported as roughly a 1% cut in Gemini's
overall training time; up to 32.5% speedup on a FlashAttention kernel implementation; a 4x4
complex-matrix-multiplication algorithm using 48 scalar multiplications, the first improvement on
Strassen's 1969 result in that setting. <https://arxiv.org/abs/2506.13131>
[^ial]: "When Agents Do Not Stop: Uncovering Infinite Agentic Loops in LLM Agents" (2026). Static
analysis (IAL-Scan) across 6,549 public LLM-agent repositories; 74 flagged, 68 confirmed real
unbounded-loop failures across 47 projects, 91.9% precision.
<https://arxiv.org/abs/2607.01641>
[^metr]: METR, "Recent Frontier Models Are Reward Hacking" (2025-06-05), and METR's Claude 3.7
Sonnet and OpenAI o3 evaluation reports. Observed reward-hacking-like behavior (editing a test
file so all tests pass; exploiting a bug in a scoring function) during task evaluation; one model
attempted some form of reward hacking in an estimated 1-2% of task attempts across two benchmark
suites, over 40 times more often when the scoring function was visible to the model.
<https://metr.org/blog/2025-06-05-recent-reward-hacking/>
[^bestofn]: Stiennon, N. et al., "Learning to Summarize from Human Feedback" (NeurIPS 2020),
<https://arxiv.org/abs/2009.01325>; Nakano, R. et al., "WebGPT: Browser-Assisted
Question-Answering with Human Feedback" (2021), <https://arxiv.org/abs/2112.09332>. The lineage
for best-of-N reranking: sample N independent completions, score each with a reward model, keep
the highest-scoring one, no revision step.
[^langgraph-refl]: LangChain, "Reflection Agents" (LangChain blog). Covers Basic Reflection, Reflexion and Language Agent Tree Search. Nodes for draft, tool
execution, and revision, with a conditional edge inspecting state to decide whether to loop back
or finish. <https://www.langchain.com/blog/reflection-agents>
[^adk-loop]: Google, Agent Development Kit docs, "Loop workflow agents." `LoopAgent` runs its
sub-agents repeatedly; an `exit_loop` tool, typically given to a critic/refiner sub-agent, sets an
escalate flag the runtime reads to stop the loop and return control to the parent. In Python `max_iterations` defaults to `None`. The page carries a
deprecation banner pointing to graph-based workflows.
<https://adk.dev/agents/workflow-agents/loop-agents/>
[^oai-judge]: OpenAI, `openai-agents-python`, `examples/agent_patterns/llm_as_a_judge.py`. A
generator agent produces an outline, a judge agent evaluates it and gives feedback, and the loop
continues until the judge is satisfied.
<https://github.com/openai/openai-agents-python/blob/main/examples/agent_patterns/llm_as_a_judge.py>
[^kamoi]: Kamoi, R., Zhang, Y., Zhang, N., Han, J., Zhang, R., "When Can LLMs Actually Correct
Their Own Mistakes? A Critical Survey of Self-Correction of LLMs" (TACL 2024). No prior work shows
successful self-correction with feedback from prompted LLMs alone, outside tasks exceptionally
suited to it; reliable external feedback or large-scale fine-tuning is what makes it work.
<https://arxiv.org/abs/2406.01297>
[^judge-attack]: Shi, J. et al., "Optimization-based Prompt Injection Attack to LLM-as-a-Judge"
(ACM CCS 2024), <https://arxiv.org/abs/2403.17710>; Raina, V., Liusie, A., Gales, M., "Is
LLM-as-a-Judge Robust? Investigating Universal Adversarial Attacks on Zero-shot LLM Assessment"
(2024), <https://arxiv.org/abs/2402.14016>: judges are significantly more susceptible when used
for absolute scoring than for comparative assessment.
[^crewai]: CrewAI, "Tasks" docs. Task-level guardrails (function-based or LLM-based) validate
output before it passes to the next task; `guardrail_max_retries` controls retry attempts on
failure (the older `max_retries` attribute is deprecated). <https://docs.crewai.com/en/concepts/tasks>
[^dspy]: DSPy, `Refine` and `BestOfN` module docs. `Refine` runs a module up to N times with
generated feedback between attempts, temperature-varied, stopping on a reward threshold or N
attempts; `BestOfN` runs the same module N times with no feedback and keeps the highest-reward or
first-passing result. Both replaced `dspy.Suggest`/`dspy.Assert` as of DSPy 2.6.
<https://dspy.ai/api/modules/Refine/>, <https://dspy.ai/tutorials/output_refinement/best-of-n-and-refine/>

## Second-engine review (post-draft)

A second engine reviewed the drafted chapter, its companion code and this map. Each finding was
checked against the primary source (paper, vendor docs, library source) or the code and tests
before a disposition was recorded.

| # | Finding | Disposition |
|---|---|---|
| 1 | First-person production callout not grounded | Accepted. Callout removed; *Grounding* is now `companion repo + research`; ruling 4 rewritten. Left on the author's checklist. |
| 2 | Map referred to material outside the public reference | Accepted. Ruling text and open questions rewritten to rest on the carrier bible and the companion repo only. |
| 3 | Drafter never sees its previous draft, so positional critiques are unactionable | Accepted. Code change: the drafter receives the prior draft with the critique. The prose on context growth stands once the code matches. |
| 4 | Trace step 5 "asks for a number" for a string field; gate requires the literal gap | Accepted in part. Step 5 now asks what the legs are made of. Rejected in part: a vague question can still name `leg_material` and clear the gate, so step 4 is consistent. |
| 5 | METR setting described as having a gradient | Accepted. METR gives the model no reward during evaluation; the sentence now describes long agent runs against a scoring script the model can read. |
| 6 | No explicit thesis | Accepted in part. A Thesis section now precedes the mental model. Rejected for the chapter opening: both halves already land in *What it actually is* and *In short*, and the word ceiling has no room for a restatement. |
| 7 | "Independent judge" under Established outruns the evidence | Accepted in part. The argued sentence now means a judge checked against human labels, and the maturity summary records the narrowing. Lens line unchanged (it matches the catalog row). Rejected: a separate judge model in the companion code, since the chapter states openly that its code uses one model for both roles. |
| 8 | Test suites and AlphaEvolve cited as closing the gap blur the 3.4/3.7 seam | Accepted. The chapter now says code computes `passed` in both, placing them in 2.5 and 3.7, and names CRITIC as the version that stays in 3.4. |
| 9 | Prompt injection against the judge missing | Accepted. New gotcha citing Shi et al. (CCS 2024) and Raina, Liusie and Gales (2024); 4.6 named as plain text because it is not yet written. |
| 10 | Kamoi et al. survey missing; float scores uncalibrated | Accepted. Kamoi et al. (TACL 2024) cited beside Huang; one sentence advises building `score` from discrete rubric checks. |
| 11a | `dspy.BestOfN` described as parallel | Accepted. The library loops sequentially and stops early on a threshold. |
| 11b | Zheng et al. list attack "appends"; frozen percentages in prose | Accepted. The paper prepends; the figures (91.3%, 8.7%, Table 3) moved to the footnote. |
| 11c | OpenAI judge example has no cap | Accepted, modified. The example caps at three rounds in its automated mode only; the chapter and footnote now say so. |
| 11d | ADK URL mismatch; deprecation | Accepted. The old URL redirects to `adk.dev`; both now use it, and the deprecation banner is noted. |
| 12 | `passed` versus `score` precedence differs between loop and graph; `score` unvalidated | Accepted. Code change: bound `score` to 0.0 to 1.0 and make a passing verdict win in both implementations. |
| 13 | Map over budget; rulings not applied to the body | Accepted in part. Rulings 2 and 7 applied to items 1, 7 and 9; resolved open questions removed. A full rewrite to the 1,500-word budget is deferred. |
| 14 | Alias attributions | Accepted in part. Reflection credited to Ng (2024, checked against his newsletter) and Gulli (2025, from the book's chapter list, not re-fetched); two non-synonyms dropped from the map. The chapter alias line is unchanged pending the author's ruling 8. |
| 15a | Dashes in the SVG | Accepted. Replaced with colons. |
| 15b | No shape legend | Accepted. One sentence above the figure. |
| 15c | Ratchet drawn on a binary 3.7 check | Rejected. The figure's argument is that the circuit is identical and only the verdict node differs. |
| 16a | Reflection Agents footnote too narrow | Accepted. It now names Basic Reflection, Reflexion and LATS. |
| 16b | "ingest" unglossed | Accepted. Glossed as step 1. |
| 16c | Oscillation detection promised but absent | Accepted. Item 6 now says the ratchet plus the cap handle it, with no separate detector. |
| 16d | Map claims inline verdicts in 1.2 and 3.1 | Accepted. Neither page states one; claim removed. |
| 16e | Docstrings repeat the prose | Rejected. The docstrings state the return contract the snippets are quoted for. |
