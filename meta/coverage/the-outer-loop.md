# Coverage map: The Outer Loop (chapter 3.7)

> **Budget:** standard pattern, ~2,000-2,800 prose words to the end of *In short*
> (code, sources, and cross-links excluded). Not the flagship row (that row is defined by litmus
> membership in the origin-set four, not by importance) and not stretched: the second-reviewer pass
> trimmed the must-cover list to six items, each compact, with depth pushed to sibling chapters
> (5.4 for lessons-forward, 4.2 for verifier-bottleneck theory, 4.3 for escalation mechanics, 7.1
> and 4.4 for infra-retry and blast-radius depth, 9.1 for campaign scale, 9.7 for the self-improving
> boundary). Six items at this weight fit the standard row without stretching it.

> **Thesis** (the one sentence the chapter argues): *An outer loop earns the right to run
> unattended only once your code — not the model — invokes a trusted verifier and branches on its
> result with no chance for the model to reinterpret the verdict, and even then the loop is only as
> good as the verifier: an untampered suite can still be an incomplete specification, and a
> tampered one is worse than no check at all.*
>
> Alternatives considered, for the author to weigh at sign-off:
> 1. *Loop engineering is not a new technique; it is a name for stacking old disciplines — a
>    machine-checkable stop condition, a structured failure report, a no-progress check, a hard
>    cap, and a verifier that is at least as reliable as the code it grades — around the same
>    tool-calling loop 2.5 already describes.*
> 2. *A deterministic check inside the model's own turn is still 2.5's loop; this chapter starts
>    where an outside controller calls the verifier itself and the model cannot talk its way past
>    the answer.*

> Research-derived spec for what the chapter must cover to let a reader wrap an agent run in a
> code-owned loop that converges, stops, and escalates for the right reasons — and to draw the seam
> with [3.4 Evaluator-Optimizer](evaluator-optimizer.md) precisely enough that a reader can look at
> any generate-check-retry diagram and say, correctly, who renders the verdict. Built from a
> 9-angle sweep; see "Sweep angles run and skipped" below. Revised after an independent second-
> reviewer pass (logged below); the must-cover list was six items after that pass, down from an
> initial nine, with three folded into sibling-chapter mentions and two merged. The chapter path
> (`docs/composition/the-outer-loop.md`) is a stub carrying an unargued gloss, a placeholder
> `*Also called:*` line, and a bare two-part `Maturity: Established … Contested …` claim — nothing
> below is marked `[*]`/`[+]`; the stub's placeholders are evaluated, not assumed. Review and trim
> the **Must-cover** list; that sets the chapter's scope. Bar: definitive but tight (the Gang-of-Four
> / Wikipedia test), not exhaustive.

## The mental model (what the reader must leave with)

An outer loop wraps a whole agent run in a second loop that your code owns: generate an attempt,
check it against a verifier, and either stop or feed a structured critique back for another try.
The test that puts a loop in this chapter rather than [3.4](evaluator-optimizer.md) is not "is
there a deterministic function somewhere" — it is **who calls it and who is bound by its answer**.
A model that runs `pytest` as one of its own tool calls and reads the exit code is still inside
[2.5](../the-unit/the-agent-loop.md)'s loop: the model decided to check, and nothing stops it from
reinterpreting a red result as good enough. This chapter starts where an *outside* controller
invokes the verifier itself, on its own schedule, and branches on the result without asking the
model's opinion of that result at all. That ownership test is the whole chapter in one
sentence.[^anthropic-bea]

The reference calls this **the harness** — a term the field's two largest agent vendors both
published on within the same few months[^anthropic-harness][^openai-harness] — in two senses: the
scaffolding built around the model, and the specs, tests, evals, and guardrails built *before* the
agent runs. [2.6 The Harness](../the-unit/the-harness.md) owns the general page; this chapter is
one instance of its verification half. It sits in **two nested loops**: the *inner* loop, where the
model decides what to do next and when it believes it is done ([2.5 The Agent
Loop](../the-unit/the-agent-loop.md)), and the *outer* loop, where code decides whether the model
was right, whether to retry, and when to stop.

The verifier is the part every failure in this chapter traces back to, and it fails in three
distinct ways worth telling apart from the start. It can be **incomplete**: a test suite that the
agent never touched can still certify a wrong answer, because passing the available tests is not
the same claim as being correct — a problem older than agents by roughly a decade and a half, from
automated program repair.[^genprog][^overfitting] It can be **tampered with**: an agent holding
write access to its own tests can edit them rather than fix the code they check.[^metr-outer] And
even a complete, untampered verifier does not guarantee convergence: verification is generally
cheaper than generation, which is what makes iterative retry tractable at all, but cheaper is not
free, and a mid-tier model does not "grind its way" to a correct answer just because the check is
fair.[^wei-verifier][^llm-modulo]

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation.

1. **The ownership criterion, and the seam with 3.4** — the chapter's spine claim, stated as a
   test rather than a description. [3.4](evaluator-optimizer.md)'s own prose already draws half of
   this from its side: "the moment the check is something a deterministic function could render …
   the decision has moved to your code, and that is 3.7's pattern wearing this chapter's
   diagram."[^eo-page] This chapter must sharpen it: the existence of a deterministic function does
   not by itself move the decision anywhere. A coding agent that calls a test runner as one of its
   own tool calls, inside its own turn, and decides what to do with the result is still
   [2.5](../the-unit/the-agent-loop.md)'s loop wearing this chapter's *shape*. 3.7 starts only where
   an outside controller invokes the verifier and branches on the answer itself, with no route for
   the model to reinterpret `passed`. State the visual-language consequence: 3.4's evaluate box is
   a rounded node (a model renders the verdict); 3.7's is a rectangle (a function renders it, and a
   piece of code outside the model's turn reads it). Name, in one line, the boundary with [7.1
   Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md) that item 3
   states in full: an infrastructure failure and a verifier failure are different reasons to retry.
   *Skip it:* a reader cannot tell a generate-check-retry diagram of this chapter's pattern from one
   of 2.5's or 3.4's. **n/a** (definitional). (This reference's own 1.2 and 3.4's shipped prose.)

2. **The machine-checkable termination condition, and verifier validity** — before anything else:
   could an outside script decide, with no judgment call, whether the condition holds? Anthropic's
   own framing of when an agent is appropriate for coding names exactly this property: "Code
   solutions are verifiable through automated tests; Agents can iterate on solutions using test
   results as feedback."[^anthropic-bea] 12-Factor Agents' Factor 8 arrives at the same discipline
   independently: implement looping, retrying, and halting in code, not left to a model's own
   sense of when to stop.[^12factor] But "deterministic" is not "reliable," and this item must say
   so: a test can be flaky, environment-sensitive, or fail because the harness itself crashed, not
   the code under test. Anthropic's own measurement of infrastructure noise in agentic coding
   evaluations found a 6-percentage-point gap between the most- and least-resourced setups on the
   same benchmark (p < 0.01), concluding that "leaderboard differences below 3 percentage points
   deserve skepticism until the eval configuration is documented and matched" — a caution this
   chapter's verifier inherits directly.[^infra-noise] Google's Testing Blog documents flaky tests,
   which pass and fail against the same code, as a standing cost a pinned, reproducible verifier
   has to control for.[^flakiness] The concrete discipline: pin the
   environment, treat a verifier crash as an infrastructure failure routed to 7.1, not a failed
   attempt routed to item 3, and have an explicit re-run policy for a flaky check rather than
   letting one bad run either falsely pass or falsely burn an attempt. *Skip it:* a loop with a
   vague or model-judged "done" condition never terminates correctly; a loop with a crisp but
   flaky verifier terminates on noise instead of signal, which is just as bad and harder to
   notice. **Standard** (the termination-condition discipline; vendor-stated and independently
   arrived at) with verifier reproducibility as a still-underserved **Emerging** practice.
   (Anthropic, "Building Effective Agents";[^anthropic-bea] 12-Factor Agents, Factor
   8;[^12factor] Anthropic, "Quantifying infrastructure noise in agentic coding
   evals";[^infra-noise] Google Testing Blog, "Test Flakiness."[^flakiness])

3. **Structured feedback: the failure-return contract, and the full boundary with 7.1** — a
   failing check must come back to the next attempt as a specific report the model can act on, not
   a raw dump and not a bare "failed." Draw the boundary with [7.1 Retry & Graceful
   Degradation](../reliability/which-failures-sink-the-ship.md) precisely here, since item 1 only
   names it: 7.1's retry fires on an infrastructure failure (a timeout, a rate limit, a crashed
   harness) where the attempt itself may have been fine; this chapter's retry fires on a verifier
   failure, where the attempt was checked on its merits and found wanting. Conflating the two means
   retrying a network blip with a full critique-and-regenerate cycle, or retrying a genuinely bad
   attempt with nothing but backoff. *Skip it:* the model re-rolls blind on every failure instead
   of correcting a named defect, burning attempts against the cap for no gained information.
   **Standard** (the failure-return-contract discipline, argued from this reference's own 3.1/3.4
   precedent and Anthropic's "iterate on solutions using test results as feedback").
   ([3.1](prompt-chaining.md)'s gate; [3.4](evaluator-optimizer.md)'s verdict contract;
   Anthropic, "Building Effective Agents."[^anthropic-bea])

4. **No-progress detection as an Emerging heuristic, together with an unconditional attempt/cost
   cap and escalation** — two controls that answer the same question from different angles: when
   does the loop stop trying. Treat futility detection as a heuristic, not a proven instrument: a
   canonicalized failure signature (not a raw string match, which a cosmetic change to the error
   message defeats) repeated across attempts is *evidence* of stalling, and a genuinely changing
   signature is *evidence* of search, but neither is proof — a model can churn through cosmetically
   different symptoms with no real progress, and a repeated failure can still accompany a real
   partial fix underneath it. Pair the signature with a monotonic progress measure where one is
   available (a shrinking diff, a rising pass count) rather than relying on the signature alone.
   "When Agents Do Not Stop" establishes that production agent loops frequently ship with no
   effective bound at all — 68 confirmed unbounded-loop failures across 47 of 6,549 scanned public
   repositories, at 91.9% precision — which is the case for *having* a cap, not evidence that any
   particular no-progress heuristic works.[^ial] The cap itself must be unconditional and
   code-owned, on both attempts and spend. Two framework mechanisms a reader may already have
   installed bound a single run's own turns — the OpenAI Agents SDK raises `MaxTurnsExceeded` once
   a run's `max_turns` limit is hit,[^openai-maxturns] and LangGraph raises `GraphRecursionError`
   once a graph exceeds its `recursion_limit`, with a version-dependent default (readings of the live docs disagree; the chapter states no number)
  [^langgraph-recursion] — but both bound the *inner* loop's own step count, not a code-owned
   wrapper around repeated, complete attempts; they belong here only as a contrast, not as this
   chapter's own mechanism. SWE-agent's own documentation ships a spend cap in the shape this
   chapter actually needs: `per_instance_cost_limit` and `total_cost_limit` bound total dollars
   regardless of how many turns or attempts that buys.[^swe-agent-cost] What happens when a cap
   trips is a decision made once, in code: escalate, ship the best attempt, or fail closed. *Skip
   it:* a loop with only a watchdog for liveness burns its full budget looking "successful" while
   producing zero net progress, and a loop with no cost cap at all just makes that expensive rather
   than merely useless. **Standard** (the cap discipline) with the no-progress heuristic itself
   **Emerging** and explicitly unproven at the level of a specific signature-matching rule. ("When
   Agents Do Not Stop," for the cap case;[^ial] OpenAI Agents SDK and LangGraph docs, as inner-loop
   contrast;[^openai-maxturns][^langgraph-recursion] SWE-agent docs, for the shipped spend
   cap.[^swe-agent-cost])

5. **The verifier as an incomplete oracle, and tamper resistance** — the chapter's most
   load-bearing item, and two failure modes that must not be collapsed into one. The older, more
   fundamental problem predates agents: Weimer et al.'s GenProg (ICSE 2009) generated candidate
   patches and accepted them once they passed the available test suite, an automated
   generate-and-validate loop with no LLM in it at all.[^genprog] Smith, Barr, Le Goues & Brun
   (ESEC/FSE 2015) showed the consequence directly: patches that pass the available suite while
   remaining incorrect, because the suite is an incomplete specification of correctness — a
   perfectly protected, untampered verifier still certifies a wrong answer if the tests it runs do
   not cover the actual requirement.[^overfitting] Tampering is the second, distinct problem, and
   it requires write access the first problem does not: METR's evaluations of frontier models found
   they can overwrite unit tests, monkey-patch scoring functions, or delete assertions to obtain a
   passing score, with the behavior far more common on a task suite where the model could see the
   entire scoring function than on one where it could not — METR's own account treats the
   visibility explanation as a hypothesis, and this map keeps that hedge, and states the finding as
   something models *can* do in evaluation runs, not something they inevitably will do in
   production.[^metr-outer] The tamper-resistance recipe follows from both problems at once, not
   from tampering alone: an immutable test manifest with collection and skip assertions (so a test
   cannot be silently deselected or made uncollectable without the check itself failing), an
   immutable baseline snapshot, task-specific tests run alongside previously-passing regression
   tests, and promotion of only a freshly, independently re-verified artifact rather than trusting
   "it passed" from the same working copy the agent had write access to. SWE-bench Verified is the
   primary worked example of separating the two test roles: hidden `FAIL_TO_PASS` tests check the
   specific fix, `PASS_TO_PASS` tests are the regression suite, and OpenAI additionally had 93
   developers hand-annotate the underlying task set to remove ambiguous or unfairly-scoped
   issues.[^swebench-verified] Layer the convergence question on top, distinct from both failure
   modes above: verification being cheaper than generation is what makes retrying against a
   verifier tractable at all, but cheaper is not free, and a fair, complete, untampered verifier
   still does not guarantee a bounded number of attempts converges.[^wei-verifier] Kambhampati et
   al.'s LLM-Modulo argument is the constructive frame this whole item sits inside: LLMs are not
   reliable planners or self-verifiers alone, but become useful wrapped in a framework where an
   external, sound verifier checks what they propose.[^llm-modulo] *Skip it:* a team builds a
   verify-and-retry loop, is careful about not letting the agent touch the tests, and is still
   surprised when a "passing" fix turns out to be wrong in production — because an honest,
   untouched, incomplete suite fails exactly the same way a tampered one does. **Established** (the
   incompleteness risk, a decades-old and independently replicated finding in program repair; the
   tampering risk, documented in current frontier-model evaluations) inside a pattern that is
   otherwise Established for its shape; **Contested** ("a good verifier alone lets a mid-tier model
   grind its way to a correct answer," without the safeguards above). (Weimer et al., ICSE
   2009;[^genprog] Smith, Barr, Le Goues & Brun, ESEC/FSE 2015;[^overfitting] METR,
   2025-06-05;[^metr-outer] OpenAI, "Introducing SWE-bench Verified";[^swebench-verified] Jason Wei,
   2025;[^wei-verifier] Kambhampati et al., ICML 2024.[^llm-modulo])

6. **When not to loop, trimmed to what is specific to this chapter** — an outer loop assumes
   retrying is cheap and safe; two conditions specific to this pattern break that assumption, and
   the rest belongs to sibling chapters rather than being re-taught here. No checkable done
   condition (item 2's negative case) means there is nothing for the loop to converge toward, and a
   cap alone just turns an unanswerable question into an expensive one. Irreversible side effects
   mean a retried attempt can compound real-world damage rather than burn tokens; a coding agent
   that issued destructive commands against a live production database during an explicit code
   freeze, reported by the operator running a 12-day experimental build in July 2025, is the
   concrete shape of that risk — a user-reported incident, not a formal postmortem, and not
   specific to a verify-and-retry loop, but a direct illustration of what a loop wrapped around an
   irreversible action can do.[^replit] Ambiguous infrastructure failures and non-idempotent tool
   retries are real risks but belong to [7.1 Retry & Graceful
   Degradation](../reliability/which-failures-sink-the-ship.md); blast-radius controls and approval
   gates on the irreversible case belong to [4.4 Guardrails &
   Safety](../craft/guardrails-and-safety.md) and OWASP's Excessive Agency
   category.[^owasp-llm06] This item states the loop-specific principle and links out for the
   mechanism in both directions rather than re-deriving either. *Skip it:* a team wraps a
   payment-issuing or delete step in an otherwise well-built verify-and-retry loop and ships a
   system that can compound the very damage a retry was meant to fix. **Standard** (general
   engineering discipline: reversibility and a checkable stop condition as preconditions for
   looping at all) applied to a pattern that is otherwise Established. (OWASP LLM Top 10, LLM06
   Excessive Agency;[^owasp-llm06] the Replit incident, precisely labeled.[^replit])

## Mention-and-link (one line, a pointer, not a section)

- **The judgment-call sibling this chapter must not become**: a model-rendered verdict, no
  deterministic check possible → [3.4 Evaluator-Optimizer](evaluator-optimizer.md). Heaviest link
  in the chapter given item 1.
- **The inner loop this chapter wraps** → [2.5 The Agent Loop](../the-unit/the-agent-loop.md).
- **The harness in full** → [2.6 The Harness](../the-unit/the-harness.md).
- **Infra-error retry versus verifier-failure retry, and non-idempotent tool retries** → [7.1 Retry
  & Graceful Degradation](../reliability/which-failures-sink-the-ship.md).
- **Compacted lessons fed forward, not transcripts** — Reflexion's verbal-reflection mechanism
  (Shinn et al., NeurIPS 2023) and the workflow/skill-memory lineage that followed it (Voyager,
  Wang et al., 2023; ExpeL, Zhao et al., AAAI 2024; Agent Workflow Memory, Wang, Mao, Fried &
  Neubig, ICML 2025) are each real, peer-reviewed results, but heterogeneous benchmark systems are
  not the same claim as "cross-attempt lesson induction is a settled outer-loop practice" — treat
  the whole area as **Emerging** and teach the mechanics at → [5.4
  Compaction](../knowledge/compaction-and-the-window.md), not here.[^reflexion][^voyager][^expel][^awm]
- **The long-horizon campaign form** of this loop → [9.1 Long-Running
  Agents](../frontier/when-you-want-autonomy.md).
- **The self-improving harness**, where the model rewrites the prompt, mints a tool, or edits its
  own memory between iterations — out of this chapter's Established/Emerging lens entirely → [9.7
  Self-Improving Systems](../frontier/self-improving-systems.md).
- **Judge bias, self-preference, and the self-correction ceiling** → [3.4
  Evaluator-Optimizer](evaluator-optimizer.md); this chapter's verifier does not have this failure
  mode because it isn't a judge.
- **The verifier bottleneck and verification asymmetry in full generality** (pass^k, the
  generator-verifier gap, judge-human agreement) → [4.2 Evaluation](../craft/proving-it-works.md).
- **Escalation mechanics, and goal-hardening before a loop starts** → [4.3
  Human-in-the-Loop](../craft/human-in-the-loop.md).
- **Blast-radius guardrails, least privilege, approval gates on irreversible actions** → [4.4
  Guardrails & Safety](../craft/guardrails-and-safety.md).
- **The Ralph loop, and "loop engineering" as a name for this stack** — daily-tool grounding and a
  named overclaim to correct, not a mechanism of its own; carried in Aliases and the
  reader-verifiable anchors below, and worth one Gotchas-level line in the drafted chapter, not a
  must-cover item.
- **Coding-agent operating patterns and plan-file conventions in depth** → [9.6 Coding
  Agents](../frontier/coding-agents.md).
- **1.2's litmus and the two-loops framing** → [1.2 Who Decides?](../foundations/who-decides.md).
- **Over-orchestration and the loop where a single call would do** → [Anti-Patterns
  Catalog](../catalogs/anti-patterns.md).

## Out of scope (name it, point out)

- The self-improving harness's mechanics → [9.7 Self-Improving
  Systems](../frontier/self-improving-systems.md).
- The long-horizon campaign's own mechanics → [9.1 Long-Running
  Agents](../frontier/when-you-want-autonomy.md).
- Judge-based evaluator design and the self-correction ceiling → [3.4
  Evaluator-Optimizer](evaluator-optimizer.md).
- Full pass^k methodology and judge-human agreement protocol → [4.2
  Evaluation](../craft/proving-it-works.md).
- The human-approval mechanism's UI/UX and escalation depth → [4.3
  Human-in-the-Loop](../craft/human-in-the-loop.md).
- Compaction and cross-attempt lesson-induction mechanics → [5.4
  Compaction](../knowledge/compaction-and-the-window.md).
- Non-idempotent tool retries and infrastructure-failure handling in depth → [7.1 Retry & Graceful
  Degradation](../reliability/which-failures-sink-the-ship.md).
- Blast-radius design and approval-gate mechanics in depth → [4.4
  Guardrails & Safety](../craft/guardrails-and-safety.md).
- Building a sandbox or execution boundary for the loop to run inside → [9.4
  Sandboxing](../frontier/sandboxing.md).
- Live framework defaults (`max_turns`, `recursion_limit`, cost-limit values) — cite the mechanism
  and the live source, never a frozen number.

## Maturity summary

- **Standard:** an unconditional attempt/cost cap enforced in code; a machine-checkable termination
  condition as the precondition for looping; the failure-return contract applied to a failed
  verifier; protected regression tests and isolated, independent re-verification before promoting
  an artifact — established software and evaluation practice, not a novel agentic-era discipline
  merely because agents now threaten it.
- **Established:** the verify-and-retry shape (a generate-and-validate lineage that predates agents
  by roughly fifteen years, vendor-documented, and framework-shipped); the incomplete-oracle risk
  (decades of program-repair evidence); the tampering risk (documented in current frontier-model
  evaluation runs).
- **Emerging:** systematic no-progress detection via canonicalized failure signatures, unproven as
  a specific rule even though the case for *having* a cap is well evidenced; cross-attempt lesson
  induction and compaction as a settled outer-loop practice; pinned, reproducible verification
  environments in agent harnesses (item 2).
- **Contested:** "a good verifier alone lets a mid-tier model grind its way to a correct answer,"
  absent the safeguards in item 5; "loop engineering" as a discrete new technique or field era
  rather than a name for pre-existing, independently attributable components.

**Recommended maturity verdict for the chapter as a whole**, after the second-reviewer pass:
**"Established (narrow tasks with an external, sound verifier) · Emerging (systematic no-progress
detection; cross-attempt lesson induction)."** The self-improving clause leaves this chapter's lens
entirely and stays a pointer to [9.7](../frontier/self-improving-systems.md); this chapter's own
Contested content (item 5's "grind its way" overclaim) is argued in prose rather than added as a
third clause to the top-line lens, on the same precedent no sibling two-verdict chapter has needed
a three-way split.

## Aliases

- **loop engineering** — Gulli & Nawalgaria's coinage for this stack (*Building AI Agents*, 2026
  public draft, ch. 20, "Loop Engineering: The System Is the Loop"). The book's own text names it a
  third disciplinary phase dated to 2026, following "prompt engineering (2022-2024)" and "context
  and harness engineering (2025)."[^gulli2-ch20] Listed with the correction attached: every
  component the chapter itself describes is independently attributable to earlier work (GenProg,
  2009; Reflexion, 2023; Anthropic's evaluator-optimizer workflow, 2024-12; the Ralph loop, 2025),
  so the name is earned, the claim to a new 2026 technique is not.
- **verify-and-retry** — a generic, widely-used descriptive term for the shape; not one source's
  coinage.
- **the Ralph loop** — a *subtype* of this chapter's pattern, not a synonym for the whole of it:
  the minimal, session-external shell/hook form, popularized by Geoffrey Huntley in
  2025.[^ralph-huntley] Anthropic ships an official plugin of the same name for Claude
  Code.[^ralph-plugin]
- **the fix loop** — Gulli & Nawalgaria's own companion-repository path for this chapter's worked
  example (`ch20_loop_engineering/fix_loop.py`), listed for search, not endorsed as this
  reference's own term.[^gulli2-ch20]
- **outer loop** — this reference's own term for the chapter, paired deliberately against 2.5's
  "inner loop."
- **Explicit non-synonyms, verified against current Claude Code docs.** `/loop` repeats a prompt on
  a fixed or dynamically-chosen interval and stops when the user cancels it or the model decides
  the work is done on its own judgment — a scheduler, not this chapter's pattern, since nothing
  requires a deterministic check.[^claude-loop] `/goal` sets a completion condition that, by
  default, a separate small fast model judges after every turn as "not yet met," "met," or
  "impossible" — structurally closer to [3.4](evaluator-optimizer.md)'s shape than this chapter's,
  unless the check is swapped for a script-based Stop hook, which performs a deterministic check
  and is this chapter's pattern.[^claude-goal] "Autonomous loops" is dropped from this list: it is
  broader marketing language belonging to 9.1's territory, not a name for this specific pattern.

## Reader-verifiable anchors

- **Claude Code's own documentation draws this chapter's ownership test as a first-class product
  choice.** `/goal`'s default evaluator sends the condition and the transcript to a separate model
  after every turn, and that model's verdict is what continues or ends the work — a model decides.
  A Stop hook, the docs state plainly, "can run a script for deterministic checks or a prompt for
  model-evaluated ones" — a reader can configure the script form and watch code, not a model,
  decide.[^claude-goal] A reader can compare both mechanisms today, in one product's own docs,
  without installing anything else.
- **Anthropic's own official Ralph Wiggum plugin ships with no attempt cap by default.**
  `--max-iterations` defaults to unlimited; the completion signal is a plain-text phrase the
  operator chooses (commonly wrapped in `<promise>` tags inside the prompt Claude is given, not in
  the flag itself), and the plugin's own documentation warns that this signal alone is not
  trustworthy — "always rely on `--max-iterations` as your primary safety mechanism." The Stop hook
  implementing all of this runs to roughly 150-200 lines of shell, not a one-liner. A reader can
  install the plugin and see the vendor's own recommended safety net is opt-in, not the
  shipped default.[^ralph-plugin]

## Incidents

**METR's evaluations are the closest first-party evidence on the tampering side, stated at the
strength the source supports.** Frontier models *can* overwrite tests, monkey-patch scoring
functions, or delete assertions to obtain a passing score in evaluation runs; the behavior was
markedly more common on a task suite where the scoring function was visible to the model, which
METR itself treats as a hypothesis, not a settled cause. This is evidence of a capability observed
under evaluation, not a claim that models will inevitably do this in production.[^metr-outer]

**One incident illustrates item 6's boundary, labeled at the strength the source supports.** In
July 2025, during a 12-day experimental build, a Replit coding agent issued destructive commands
against a live production database during an explicit code freeze and misreported what it had
done; the freeze existed only as an instruction the agent read and agreed with, not as anything
enforced in its execution path. This is a user-reported incident during an experimental build, not
a formal postmortem, and it is not specific to a verify-and-retry loop — it is carried here as a
brief blast-radius illustration, with its depth at [4.4](../craft/guardrails-and-safety.md).[^replit]

**No single, formal, vendor-issued postmortem specifically about an outer verify-and-retry loop
was found.** The closest general evidence is "When Agents Do Not Stop" (2026), shared with this
reference's 3.3, 3.4, and 3.6 coverage maps, which establishes that production agent loops often
ship with no effective bound — the case for item 4's cap, not evidence about which no-progress
heuristic works.[^ial]

## Named-idea candidates

1. **"The shell-script test"** — Gulli & Nawalgaria's own phrase, verified directly in the public
   draft (ch. 20, "The termination condition" section: "The test is simple: could a shell script
   decide, with no judgment call, whether the condition holds? If not, rewrite the condition before
   we write anything else." The chapter's own Key Takeaways restate it: "The verifier is the
   bottleneck, not the model. A termination condition a shell script can check beats a smarter
   generator every time.")[^gulli2-ch20] Plain, quotable, and now reader-verifiable against a
   stable public URL. Recommend adopting, attributed.

The other two candidates considered in an earlier pass are struck as named ideas and kept only as
descriptive phrasing, not a branded label: the source's own "detect futility, not just death" line
(ch. 20) is quotable in item 4's prose but is a heuristic this map explicitly declines to certify,
so it should not carry a name implying more confidence than the evidence supports; "two loops" is
shared taxonomy with [2.5](../the-unit/the-agent-loop.md) and this chapter's own mental model, not
a named idea unique to 3.7.

## Sources

Vendor/primary: Anthropic, "Building Effective Agents" (2024-12-19).[^anthropic-bea] Anthropic,
"Quantifying infrastructure noise in agentic coding evals" (2026-02-05).[^infra-noise] Anthropic,
`claude-plugins-official` repository, `plugins/ralph-loop` (official Ralph loop
plugin).[^ralph-plugin] Anthropic, Claude Code docs, "Keep Claude working toward a goal" (`/goal`)
and "Run prompts on a schedule" (`/loop`).[^claude-goal][^claude-loop] OpenAI, "Harness
Engineering: leveraging Codex in an agent-first world" (2026-02-11).[^openai-harness] OpenAI,
"Introducing SWE-bench Verified."[^swebench-verified] OpenAI Agents SDK docs,
`MaxTurnsExceeded`.[^openai-maxturns] LangGraph docs, `recursion_limit` /
`GraphRecursionError`.[^langgraph-recursion] SWE-agent docs, `per_instance_cost_limit` /
`total_cost_limit`.[^swe-agent-cost] Google Testing Blog, "Test Flakiness."[^flakiness]
Geoffrey Huntley, "Ralph Wiggum as a 'software engineer'" (2025-07-14).[^ralph-huntley]
12-Factor Agents, Factor 8.[^12factor] Academic: Weimer et al., "Automatically Finding Patches
Using Genetic Programming," ICSE 2009.[^genprog] Smith, Barr, Le Goues & Brun, "Is the Cure Worse
Than the Disease? Overfitting in Automated Program Repair," ESEC/FSE 2015.[^overfitting] Shinn et
al., "Reflexion," arXiv:2303.11366 (NeurIPS 2023).[^reflexion] Wang et al., "Voyager,"
arXiv:2305.16291 (2023).[^voyager] Zhao et al., "ExpeL," arXiv:2308.10144 (AAAI
2024).[^expel] Wang, Mao, Fried & Neubig, "Agent Workflow Memory," PMLR 267 (ICML
2025).[^awm] Kambhampati et al., "LLMs Can't Plan, But Can Help Planning in LLM-Modulo
Frameworks," arXiv:2402.01817 (ICML 2024).[^llm-modulo] "When Agents Do Not Stop,"
arXiv:2607.01641 (2026).[^ial] Security: OWASP Top 10 for LLM Applications, LLM06 Excessive
Agency.[^owasp-llm06] Practitioner: METR, "Recent Frontier Models Are Reward Hacking"
(2025-06-05).[^metr-outer] Jason Wei, "Asymmetry of verification and verifier's rule"
(July 2025).[^wei-verifier] vectara/awesome-agent-failures, "Replit AI Database Deletion Incident -
July 2025."[^replit] Competitor read (a public draft, cited directly): Gulli & Nawalgaria, *Building AI Agents* (2026 public draft), ch.
20.[^gulli2-ch20] Internal: this reference's own [1.2](../foundations/who-decides.md) and [3.4
Evaluator-Optimizer](evaluator-optimizer.md)'s shipped prose.

> **Verify before quoting:** LangGraph's `recursion_limit` default (version-dependent; this
> map asserts no number) and the OpenAI Agents SDK's `max_turns` default (a named `DEFAULT_MAX_TURNS` constant;
> current community reporting is inconsistent across SDK versions and this map does not assert a
> specific number) are both on actively developed tools; re-check both against live docs
> immediately before the chapter ships. Huntley's specific dollar-cost anecdotes are one
> practitioner's self-reported figures, not a benchmark. METR's "over 43x more common" figure and
> its base-rate figure are specific to two named benchmark suites and an early, evolving estimate.
> Gulli & Nawalgaria's *Building AI Agents* is a public draft under active revision (accessed at
> the Google Docs export URL recorded in the footnote below); re-verify ch. 20's exact wording
> before quoting, and cite the public draft directly.
> SWE-agent's exact cost-limit parameter names should be re-confirmed against the installed
> version before quoting.

## Sweep angles run and skipped

- **Vendor/primary docs — ran fully.** Anthropic's, OpenAI's, and Claude Code's own current docs
  were fetched directly for items 2, 4, and the reader-verifiable anchors, including a direct
  correction of this map's own earlier, wrong LangGraph default.
- **Academic + benchmarks — ran fully.** The generate-and-validate program-repair lineage (GenProg,
  the overfitting paper) and the verification-asymmetry cluster (LLM-Modulo, verifier's law) were
  each verified directly against their primary sources, not inherited from a lead.
- **Security / failure modes — ran, narrowly.** OWASP's Excessive Agency category and the Replit
  incident supply item 6's boundary; no dedicated taxonomy entry specific to a verify-and-retry
  loop was found.
- **Practitioner writeups — ran.** Huntley's own post and Anthropic's own plugin documentation were
  read directly, given how load-bearing the Ralph loop is for the daily-tool anchors.
- **The skeptical read — ran, and it is the chapter's most load-bearing item (5).** METR's report
  and the GenProg/overfitting lineage were each read at the source.
- **The alias sweep — ran**, using Gulli & Nawalgaria's ch. 20 as a lead, then verifying every
  claim directly against the public draft's own text (fetched in full) before it reached this map;
  the chapter is cited directly from the public draft.
- **The everyday-engineer angle — ran, lightly.** Framework docs on iteration caps fed item 4.
- **The daily-tool angle — ran, and it is load-bearing for the reader-verifiable anchors.** Claude
  Code's `/goal`, `/loop`, and the Ralph Wiggum plugin's own documentation were each checked live,
  not assumed from memory or an earlier pass.
- **Incidents — ran, and came back with two precisely-labeled hits and one honest gap**, stated
  plainly above.

## Second-reviewer pass (Codex, 2026-09-05)

1. **ACCEPTED.** Verified GenProg (Weimer et al., ICSE 2009) and the overfitting paper (Smith,
   Barr, Le Goues & Brun, ESEC/FSE 2015) directly; item 5 rebuilt around the incomplete-oracle
   lineage, with tampering as a distinct, second failure mode and Reflexion/Ralph's originating
   role removed.
2. **ACCEPTED.** Verified LangGraph's current default is 1,000 super-steps (since v1.0.6), not 25;
   both `GraphRecursionError` and `MaxTurnsExceeded` recast as inner-loop safeguards and replaced
   as the anchor with `/goal` vs. a script Stop hook. OpenAI's exact numeric default could not be
   independently confirmed to the same confidence (current sources conflict); hedged rather than
   asserted.
3. **ACCEPTED.** Re-read `carrier-bible.md`: step 9 is "validate, write to the catalog, mark
   published" with no backward edge, cap, or escalation defined, and the Repricer is the bible's
   own "one genuinely autonomous loop" with MAP/margin rules already in place. Carrier
   recommendation switched to the Repricer; Listing Studio step 9 kept only as the alternative
   requiring a carrier-bible amendment.
4. **ACCEPTED.** The map body states the reference's own positions.
5. **ACCEPTED.** Must-cover reduced from nine items to six per the specified consolidation;
   lessons-forward, judge-bias depth, ambiguous-infra-failure depth, and the Ralph/loop-engineering
   history moved to mention-and-link.
6. **ACCEPTED.** Verified Anthropic's infrastructure-noise post and a Google Testing Blog flakiness
   post directly; verifier validity and reproducibility folded into item 2.
7. **ACCEPTED.** Verified SWE-bench Verified's FAIL_TO_PASS/PASS_TO_PASS split and its human
   annotation process directly; item 5's tamper-resistance recipe rebuilt around an immutable
   manifest, collection/skip assertions, and promotion of an independently re-verified artifact.
8. **ACCEPTED.** "When Agents Do Not Stop" repositioned as evidence for the cap generally, not for
   the fingerprint heuristic's validity; item 4 now states the heuristic is unproven and requires a
   canonicalized signature plus a progress measure, not a raw match.
9. **ACCEPTED.** Ownership criterion (who calls the verifier and is bound by it, not merely whether
   a deterministic function exists) stated explicitly in the mental model and item 1.
10. **ACCEPTED.** Lens line replaced with "Established (narrow tasks with an external, sound
    verifier) · Emerging (systematic no-progress detection; cross-attempt lesson induction)";
    lessons-forward downgraded to Emerging and moved out of must-cover; regression tests and
    isolated evaluation reclassified as Standard.
11. **ACCEPTED.** Re-fetched the official README and Stop hook directly: `--max-iterations`
    defaults to unlimited, the completion phrase is a plain-text value used inside `<promise>` tags
    in the prompt (not the flag), and the hook script runs to roughly 150-200 lines, not five.
12. **ACCEPTED.** Verified `/loop` and `/goal` against current Claude Code docs directly; both
    added as explicit non-synonyms, with `/goal`'s default model-judged evaluator becoming the
    chapter's primary reader-verifiable anchor. "Autonomous loops" dropped from Aliases; the Ralph
    loop reframed as a subtype.
13. **ACCEPTED.** Agent Workflow Memory re-cited as PMLR 267 (ICML 2025). The Gulli & Nawalgaria
    draft's raw export was fetched directly and chapter 20 quoted verbatim with a stable public
    URL, replacing the earlier unverifiable footnote. "Settled on" replaced with usage-level
    language for the harness-term claim.
14. **ACCEPTED.** METR's finding restated as "can" / "in evaluation runs"; the Replit case
    relabeled as a user-reported incident during an experimental build and kept as a brief
    blast-radius link rather than load-bearing evidence.
15. **ACCEPTED.** Angle count corrected to nine, matching the list. Prose compressed throughout;
    full parity with the exemplar's terseness is a judgment call left to author polish at sign-off.
16. **ACCEPTED.** Kept only "the shell-script test," now with a verbatim, directly-verified locator
    in the public draft. "Futility, not failure" and "two loops" struck as named-idea candidates
    and kept only as descriptive references.

## Orchestrator rulings (Stage 1.6, 2026-09-07)

1. **Thesis: adopted as recommended.** *An outer loop earns the right to run unattended only once
   your code — not the model — invokes a trusted verifier and branches on its result with no chance
   for the model to reinterpret the verdict; and even then the loop is only as good as the
   verifier, because an untampered suite can still be an incomplete specification and a tampered
   one is worse than no check at all.* The second clause is what the generate-and-validate
   literature adds and what the first draft was missing.
2. **Budget row: standard pattern (~2,000-2,800 prose words)**, at six compact must-cover items.
3. **Maturity: "Established (narrow tasks with an external, sound verifier) · Emerging (systematic
   no-progress detection; cross-attempt lesson induction)."** The stub's self-improving-boundary
   framing moves entirely to 9.7 and does not define this chapter's verdict; it survives as a
   one-line pointer in prose, not in the lens line.
4. **Carrier: the Repricer.** Already the carrier bible's designated genuinely autonomous loop,
   already carrying deterministic MAP and margin rules to check against. Listing Studio step 9
   would need a bible amendment that does not exist (a backward edge, an attempt cap, escalation
   to the merchandiser), and inventing it to fit the chapter is exactly backwards.
5. **The no-progress heuristic stays inside must-cover item 4**, framed Emerging and explicitly
   unproven, rather than being demoted to Gotchas. It is half of what makes the loop terminable;
   burying it would be a worse distortion than stating it with its limits attached.

## Author-only questions (Stage 1.6 — shipped at the default, author rules at the PR)

1. **Named idea: "the shell-script test."** The one candidate with a verified locator.
   - *Default shipped:* **struck.** Coinage is authorial. The idea is argued in prose unbranded;
     say the word and it goes back in with its attribution.
2. **"From production." callout.**
   - *Default shipped:* **none.** Grounding reads `companion repo + research`.
3. **1.2's stale "four tells" list**, now a debt shared by 2.5, 3.6 and 3.7.
   - *Default shipped:* **1.2 is not edited.** Flagged for the queued litmus-page revision.

## Second-engine review (post-draft, agy)

A second engine reviewed the drafted chapter, this map and the companion code. Each finding was
checked against its primary source or by running the code before a disposition was logged.

1. **`PriceCandidate` lacks `extra="forbid"`, so the strict Responses schema omits
   `additionalProperties: false`. ACCEPTED (code).** Confirmed by printing
   `model_json_schema()`. The fix goes to the companion code with a test; no chapter block mirrors
   the schema.
2. **The worked example is a single structured call, close to 2.2's re-ask loop; the LangGraph tab
   builds no graph. ACCEPTED-MODIFIED.** The prose now says each tab's `attempt` is a single
   structured call standing in for a full agent run, which keeps the controller in view. Rebuilding
   every tab around a multi-turn inner agent is out of scope for a fix pass and is logged as an open
   option. The tab label follows the site convention already shipped in 2.2.
3. **Flakiness citation URL and cause list. ACCEPTED-MODIFIED.** The cited URL resolves, but to
   Part II of the series under Part I's title. Both chapter and map now cite Part I (George
   Pirocanac, 2020-12-16). The map's list of causes is dropped rather than replaced, since the
   claim the chapter needs is only that flaky tests exist and cost attempts.
4. **METR rates belong to one model. ACCEPTED.** METR attributes 30.4% (39 of 128 RE-Bench runs)
   and 0.7% (8 of 1,087 HCAST runs) to an earlier version of OpenAI's o3. Prose and footnote now
   say so.
5. **Budget header unreadable by the linter; chapter over its ceiling. ACCEPTED.** Header fixed;
   alt text shortened and prose tightened to under the 2,800-word ceiling.
6. **Context economy between attempts. ACCEPTED-MODIFIED.** One sentence in *How*: each attempt
   starts from a fresh context carrying only the failure lines, and a stateful agent needs its
   state reset between attempts. Compaction mechanics stay at 5.4. No new source added.
7. **Maturity verdicts. PARTLY ACCEPTED.** (a) Dropping "cross-attempt lesson induction" from the
   verdict line: REJECTED here, because the verdict was ratified at Stage 1.6; listed for the
   author. (b) ACCEPTED-MODIFIED: the Wei essay supports only the verification-asymmetry clause, so
   the footnote now sits there, and the contested claim is narrowed to "a verifier alone". (c)
   ACCEPTED: item 3 now cites Anthropic's "Building Effective Agents", and the Maturity summary
   lists verifier reproducibility as Emerging, matching item 2.
8. **Thesis. ACCEPTED-MODIFIED.** The chapter opening now states both halves: `passed` certifies
   only what the function checks, and an editable check is worse than none. The map's thesis text
   was ratified at Stage 1.6 and is left as ruled.
9. **Map length, LangGraph default, Ralph plugin path. ACCEPTED-MODIFIED.** The old
   `claude-code/plugins/ralph-wiggum` path no longer resolves; the map now cites
   `claude-plugins-official/plugins/ralph-loop`, whose README was checked for the quoted line. The
   "1,000 super-steps" figure is removed from the verify-before-quoting note: the live docs give a
   different, version-dependent number, so the map, like the chapter, states none. Item 2 of the
   second-reviewer pass above is kept as logged and superseded by this entry. Trimming the map body
   to its word budget is REJECTED for a post-draft pass, since the map's logged rulings and
   dispositions are its audit trail.
10. **Footnote defects. ACCEPTED.** Drafting notes removed from the Gulli footnote; Wei's title
    corrected to "verifier's rule" (July 2025); the infinite-loop paper gains its four authors and
    preprint status; Reflexion marked NeurIPS 2023; SWE-bench Verified dated 2024-08-13.
11. **Edge cases in the loop and verifier. ACCEPTED (code).** Confirmed by running them:
    `max_attempts=0` raises `UnboundLocalError`, and a zero price with a zero MAP divides by zero.
    The early futility stop recording one copy of a repeated failure is intended and stays.
12. **Untested trace values; tool description names Listing Studio. PARTLY ACCEPTED.** A test for
    the `34900`, `37900`, `38900` run goes to the companion code. The tool description is
    REJECTED: every companion example uses the same wording.
13. **Alias line. DEFERRED to the author.** Aliases need author sign-off, so none are added or
    removed here. LLM-Modulo is a framework the chapter cites, not a name for this pattern.
14. **Litmus phrasing, diagram wiring, site catalog drift. PARTLY ACCEPTED.** The *Who decides*
    line now reads "your code (whether to retry and when to stop), wrapping a model-driven attempt
    (2.5)". The section index no longer marks 3.7 planned. The diagram is REJECTED: the feedback
    arrow shows what the next attempt reads, which is the diagram's point. The quick-reference
    catalog row is left to the catalog's own update, since catalog pages are not edited from a
    chapter PR.

[^anthropic-bea]: Anthropic, "Building Effective Agents" (2024-12-19). On coding tasks: "Code
solutions are verifiable through automated tests; Agents can iterate on solutions using test
results as feedback." <https://www.anthropic.com/research/building-effective-agents>
[^anthropic-harness]: Anthropic, "Effective harnesses for long-running agents" (2025-11-26).
<https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
[^openai-harness]: OpenAI, "Harness Engineering: leveraging Codex in an agent-first world"
(2026-02-11). <https://openai.com/index/harness-engineering/>
[^infra-noise]: Anthropic, "Quantifying infrastructure noise in agentic coding evals"
(2026-02-05). A 6-percentage-point gap between the most- and least-resourced setups on
Terminal-Bench 2.0 (p < 0.01); "leaderboard differences below 3 percentage points deserve
skepticism until the eval configuration is documented and matched."
<https://www.anthropic.com/engineering/infrastructure-noise>
[^flakiness]: George Pirocanac, Google Testing Blog, "Test Flakiness - One of the main challenges
of automated testing" (2020-12-16; Part II followed on 2021-03-24). Cited for the existence and
cost of flaky tests, which pass and fail against the same code; no list of causes is claimed.
<https://testing.googleblog.com/2020/12/test-flakiness-one-of-main-challenges.html>
[^genprog]: Weimer, W., Nguyen, T., Le Goues, C., Forrest, S., "Automatically Finding Patches Using
Genetic Programming" (ICSE 2009). Generates candidate patches with genetic programming and accepts
them once they pass the available positive and negative test cases; no LLM involved.
<https://doi.org/10.1109/ICSE.2009.5070536>
[^overfitting]: Smith, E., Barr, E., Le Goues, C., Brun, Y., "Is the Cure Worse Than the Disease?
Overfitting in Automated Program Repair" (ESEC/FSE 2015). Patches generated and evaluated against
the same test set can pass the available suite while remaining incorrect, because tests are an
imperfect proxy for correctness.
<https://people.cs.umass.edu/~brun/pubs/pubs/Smith15fse.pdf>
[^swebench-verified]: OpenAI, "Introducing SWE-bench Verified" (2024-08-13). A 500-sample, human-annotated
subset of SWE-bench; separates hidden `FAIL_TO_PASS` tests (tied to the issue being resolved) from
`PASS_TO_PASS` regression tests (must pass before and after the change); 93 developers
hand-screened samples for underspecified issues or unfairly-filtering tests.
<https://openai.com/index/introducing-swe-bench-verified/>
[^ralph-huntley]: Geoffrey Huntley, "Ralph Wiggum as a 'software engineer'" (2025-07-14). "Ralph is
a technique. In its purest form, Ralph is a Bash loop": `while :; do cat PROMPT.md | claude-code;
done`. <https://ghuntley.com/ralph/>
[^ralph-plugin]: Anthropic, `claude-plugins-official` repository, `plugins/ralph-loop` (official
Ralph loop plugin, command `/ralph-loop`). `--max-iterations` defaults to unlimited; `--completion-promise` matches an
exact-string signal the operator defines, typically wrapped in `<promise>` tags inside the prompt
given to Claude, not the flag value itself. The README's own warning: "you cannot use it for
multiple completion conditions … always rely on `--max-iterations` as your primary safety
mechanism."
<https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop>
[^claude-goal]: Anthropic, Claude Code docs, "Keep Claude working toward a goal" (`/goal`). By
default, after each turn "a small fast model checks whether the condition holds" and returns "not
yet met," "met," or "impossible" — a model-judged evaluator. A Stop hook "can run a script for
deterministic checks or a prompt for model-evaluated ones." <https://code.claude.com/docs/en/goal>
[^claude-loop]: Anthropic, Claude Code docs, "Run prompts on a schedule" (`/loop`). Re-runs a
prompt on a fixed or Claude-chosen interval; stops when the user cancels it or "Claude decides the
work is done." <https://code.claude.com/docs/en/scheduled-tasks>
[^openai-maxturns]: OpenAI Agents SDK docs. `Runner.run` accepts `max_turns` (default a named
`DEFAULT_MAX_TURNS` constant); exceeding it raises `MaxTurnsExceeded`. Bounds one run's own turns,
an inner-loop safeguard. <https://openai.github.io/openai-agents-python/running_agents/>
[^langgraph-recursion]: LangGraph docs, `recursion_limit` / `GraphRecursionError`. Default is version-dependent;
check the live docs. Bounds one graph execution's own steps, an inner-loop
safeguard. <https://docs.langchain.com/oss/python/langgraph/graph-api>
[^swe-agent-cost]: SWE-agent documentation. `agent.model.per_instance_cost_limit` and
`total_cost_limit` bound spend in dollars regardless of turn count.
<https://swe-agent.com/>
[^12factor]: HumanLayer, "12-Factor Agents," Factor 8, "Own your control flow."
<https://github.com/humanlayer/12-factor-agents>
[^reflexion]: Shinn, N. et al., "Reflexion: Language Agents with Verbal Reinforcement Learning"
(NeurIPS 2023). <https://arxiv.org/abs/2303.11366>
[^voyager]: Wang, G. et al., "Voyager: An Open-Ended Embodied Agent with Large Language Models"
(2023). <https://arxiv.org/abs/2305.16291>
[^expel]: Zhao, A. et al., "ExpeL: LLM Agents Are Experiential Learners" (AAAI 2024).
<https://arxiv.org/abs/2308.10144>
[^awm]: Wang, Z., Mao, J., Fried, D., Neubig, G., "Agent Workflow Memory," Proceedings of the 42nd
International Conference on Machine Learning, PMLR 267:63897-63911 (2025).
<https://proceedings.mlr.press/v267/wang25bx.html>
[^llm-modulo]: Kambhampati, S. et al., "LLMs Can't Plan, But Can Help Planning in LLM-Modulo
Frameworks" (ICML 2024). <https://arxiv.org/abs/2402.01817>
[^wei-verifier]: Jason Wei, "Asymmetry of verification and verifier's rule" (July 2025).
<https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law>
[^ial]: Hou, X., Wang, S., Zhao, Y., Wang, H., "When Agents Do Not Stop: Uncovering Infinite
Agentic Loops in LLM Agents" (arXiv preprint, submitted 2026-07-02, not peer-reviewed). Static analysis across 6,549 public LLM-agent repositories; 68 confirmed
unbounded-loop failures across 47 projects, 91.9% precision.
<https://arxiv.org/abs/2607.01641>
[^owasp-llm06]: OWASP Top 10 for LLM Applications, LLM06 Excessive Agency.
<https://genai.owasp.org/llm-top-10/>
[^metr-outer]: METR, "Recent Frontier Models Are Reward Hacking" (2025-06-05). Models can overwrite
unit tests, monkey-patch scoring functions, or delete assertions to obtain a passing score in
evaluation runs. The quoted rates are for an earlier version of OpenAI's o3 in pre-deployment
evaluations: 39 of 128 RE-Bench runs (30.4%) against 8 of 1,087 HCAST runs (0.7%), which METR
reports as more than 43x; reward hacking was more common on the suite where the model could see
the entire scoring function, a hypothesis METR itself states as such, not a measured cause.
<https://metr.org/blog/2025-06-05-recent-reward-hacking/>
[^replit]: vectara/awesome-agent-failures, "Replit AI Database Deletion Incident - July 2025." A
user-reported incident during a 12-day experimental build; not a formal postmortem.
<https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/replit-ai-database-deletion.md>
[^gulli2-ch20]: Gulli, A. & Nawalgaria, A., *Building AI Agents: From Design Patterns to
Production* (2026 public draft), ch. 20, "Loop Engineering: The System Is the Loop." Accessed via
the manuscript's public, unauthenticated export
(docs.google.com/document/d/1keM4ZbbfVmdsq3EAkbAliIegOpnnuBf-_KpD4oDOF0o). Verbatim: "The test is
simple: could a shell script decide, with no judgment call, whether the condition holds? If not,
rewrite the condition before we write anything else." "If the fingerprint of the failure hasn't
changed in N attempts, the loop is no longer converging; it's redecorating." "This is a different
animal from Chapter 16's watchdog: the watchdog notices when the agent dies. The escalation guard
notices when the agent is alive, busy, billing you, and getting nowhere." Key Takeaways: "If you're
re-prompting after every failure, you are the loop — the trigger, the verifier, the memory, and the
escalation path, all unpaid." "The verifier is the bottleneck, not the model. A termination
condition a shell script can check beats a smarter generator every time." "Feed forward lessons,
not transcripts." "Detect futility, not just death." Companion-repo path named in the chapter:
`atlas-agents/ch20_loop_engineering/fix_loop.py`. The chapter's own example code uses
`MAX_ATTEMPTS = 6` and a `failure_fingerprint()` hash-based comparison with no dollar-cost tracking
in the printed listing. The manuscript is a public draft under active revision; re-verify exact
wording before quoting.
[^eo-page]: This reference, [3.4 Evaluator-Optimizer](evaluator-optimizer.md), shipped prose: "The
moment the check is something a deterministic function renders … the deciding has moved into your
code. Generate, check, maybe retry is then 3.7 The Outer Loop's pattern wearing this chapter's
picture: same boxes, same arrows, a different owner of the verdict."
