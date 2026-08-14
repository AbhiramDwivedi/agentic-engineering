# Coverage map: Orchestrator-Workers (chapter 3.3)

> Research-derived spec for what the chapter must cover to let a reader tell genuine dynamic
> fan-out from ordinary parallel concurrency, and build the former safely. Built from a 5-angle
> sweep (vendor/primary docs, academic/benchmarks, security/failure modes, practitioner
> writeups, the skeptical read); see "Sweep angles" below for what each surfaced and what was
> judged out of scope. The chapter path (`docs/composition/fan-out.md`) is a stub with no real
> prose yet (headings only, all placeholder text), so nothing below is marked `[*]`/`[+]` against
> existing text — this is a fresh map. The stub's inherited "Maturity: Established (parallelization
> is common; the model sizing its own work is the new part)" line should not be taken as settled;
> see item 1 and the Maturity summary below, which recommends refining it rather than accepting it
> as written. Review and trim the **Must-cover** list; that sets the chapter's scope. Bar:
> definitive but tight (the Gang-of-Four / Wikipedia test), not exhaustive.

## The mental model (what the reader must leave with)

Two things get called "fan-out" in an agentic system, and only one of them is a decision. Split a
task into three subtasks your code already knows about, run three model calls at once, and merge
the results: that is ordinary concurrency, a `for` loop with an async pool underneath, and it was
never agentic to begin with. Orchestrator-workers is the narrower, newer thing sitting next to it:
the model reads the task and decides how many workers to spawn and how to divide the work between
them, fresh on every input, before any worker runs. Anthropic names both and draws the line
precisely: Parallelization (sectioning or voting) has subtasks that are "pre-defined," while in
Orchestrator-workers "subtasks aren't pre-defined, but determined by the orchestrator based on the
specific input."[^anthropic-bea] Everything hard about this chapter follows from taking that line
seriously: a diagram of parallel boxes converging on a merge step looks identical whether your code
or the model decided the box count, and the reader must be able to tell which one they are looking
at from the code, not the picture.

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation. All items are fresh
gaps against the current stub, which has no prose yet.

1. **The litmus boundary, defined precisely: fixed parallel fan-out (Parallelization) vs.
   orchestrator-workers** — the chapter's spine claim, and the reason it is one of this
   reference's genuinely-new four at all. Anthropic's guide defines two neighbouring workflows:
   **Parallelization** ("LLMs can sometimes work simultaneously on a task and have their outputs
   aggregated programmatically"), with two variants, **sectioning** ("breaking a task into
   independent subtasks run in parallel") and **voting** (running the same task multiple times for
   diverse outputs, aggregated by vote); and **Orchestrator-workers** ("a central LLM dynamically
   breaks down tasks, delegates them to worker LLMs, and synthesizes their results"). Anthropic
   calls the two "topographically similar" and draws the line on exactly one axis: in
   Parallelization the subtasks are "pre-defined," while in Orchestrator-workers they "aren't
   pre-defined, but determined by the orchestrator based on the specific input."[^anthropic-bea]
   Only the second is genuinely new by this reference's litmus: a `for` loop over a list your code
   already knows (write these 3 named deliverables, always) is Parallelization/sectioning wearing
   this chapter's name, however parallel it looks in a diagram; the model must decide the
   decomposition and the worker count for the claim to hold. *Skip it:* the chapter, or its own
   carrier example (see Open questions), illustrates ordinary concurrency and calls it agentic,
   repeating the exact mistake [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md)
   exists to correct for routing. **n/a** (definitional; the two sides carry separate maturity
   verdicts, see Maturity summary). (Anthropic, "Building Effective Agents," 2024-12-19.)
2. **The fan-in: synthesis, merge-ordering discipline, and the partial-failure contract** — three
   related obligations that live at the point where workers rejoin. First, results must be
   gathered under a stable key (a subtask id, not arrival order): concurrent workers finish out of
   order, and a positional-append reducer silently reorders output; LangGraph's own dynamic
   fan-out mechanism writes worker results into a shared state key precisely so this is handled by
   the framework rather than by accident.[^langgraph] Second, the synthesizer, the step that
   reconciles N workers' output into one answer, is usually the pattern's real quality bottleneck,
   not the fan-out itself: Anthropic's own system has the lead agent "synthesize these results and
   decide whether more research is needed,"[^anthropic-multiagent] i.e. the fan-in is itself a
   judgment call, not a formality. Third, this reference's own failure-return-contract rule
   applies at the worker boundary: one worker failing among N must come back to the orchestrator
   as a structured, recoverable signal ("3 of 4 completed; worker 2 failed: `<reason>`"), never a
   raw exception that kills the whole fan-out, and never a silent drop of the missing piece.
   *Skip it:* nondeterministic output ordering that breaks a downstream assumption, a synthesis
   step that quietly averages away the one worker that got it right, or one bad worker silently
   reducing a four-part answer to three with no signal anywhere. **Established** (both the
   synthesis-as-bottleneck framing and the reducer/ordering discipline are directly evidenced in
   vendor material, not inferred). (Anthropic, "How we built our multi-agent research system,"
   2025-06-13; LangChain, "Graph API overview," the `Send` / map-reduce reducer pattern.)
3. **Cost: fan-out multiplies spend, by a lot** — the sharpest practical consequence of "the model
   decides how many workers." Anthropic's own published measurement: agents in general run
   roughly 4x the tokens of a single chat turn, and multi-agent systems roughly 15x, because every
   worker carries its own context window and the lead agent pays again to read and reconcile every
   worker's output.[^anthropic-multiagent] *Skip it:* a team ships dynamic fan-out on a task where
   the value doesn't clear that multiple, and the pattern is unaffordable in production before
   anyone notices in a demo. **Established** (a directly measured, published finding); the exact
   multiple is a snapshot from one system on one set of internal evals and will move with
   model/eval generation — cite the shape (an order-of-magnitude multiplier over single-agent
   chat), not the frozen number. (Anthropic, ibid.; → [8.4 Controlling
   Cost](../production/controlling-cost.md) for the general economics.)
4. **Context economy: what a worker's isolated window buys, and what it costs** — this
   reference's standing context-economy lens, applied at its most literal here. Each worker is a
   fresh instance of the augmented-LLM atom; [1.4 The Augmented LLM](../foundations/the-augmented-llm.md)
   already frames fan-out this way ("Fan-out is several of these nodes run in parallel"), with its
   own window, seeing none of its siblings' reasoning. That isolation is the mechanism that lets
   fan-out compress a broad task: Anthropic describes subagents "exploring different aspects of
   the question simultaneously before condensing the most important tokens for the lead research
   agent."[^anthropic-multiagent] It is also exactly what a worker structurally cannot do: read
   another worker's intermediate reasoning, notice it is about to duplicate work, or catch a
   conflicting assumption before it ships (this is also the seed of item 6's skeptical read). Only
   the condensed output should cross back to the orchestrator, never the transcript, the same
   forwarding discipline [3.1 Prompt Chaining](../composition/prompt-chaining.md)'s gate applies
   at one boundary, now required at N boundaries at once. *Skip it:* workers silently duplicate
   work, or the pattern gets reached for on a task that actually needed the sharing it structurally
   cannot provide. **Established** (inherits 1.5's verdict; the isolation-as-mechanism claim is
   Anthropic's own framing of why the pattern works at all). (Anthropic, ibid.; → [1.5 Context
   Engineering](../foundations/context-engineering.md).)
5. **Determinism and reproducibility** — Anthropic states plainly that "agents make dynamic
   decisions and are non-deterministic between runs, even with identical prompts," and that a
   single derailed step can send an entire run down an unpredictable trajectory.[^anthropic-multiagent]
   Fan-out multiplies this: it runs N such nondeterministic units concurrently, so the same input
   can produce a different worker count, a different decomposition, and a different final answer
   on two consecutive runs. *Skip it:* a single eval run or demo is treated as representative of
   the pattern's behavior generally, or a bug report can't be reproduced because the failing run's
   own decomposition can't be replayed. **Established** (a vendor-stated, acknowledged property of
   the architecture, not a bug awaiting a fix). (Anthropic, ibid.; → [4.2
   Evaluation](../craft/proving-it-works.md) for eval discipline under nondeterminism.)
6. **The skeptical read: two named companies, opposite defaults** — represent both sides plainly,
   not as strawman and rebuttal. Cognition's Walden Yan argues against fan-out to parallel
   subagents on the grounds that "actions carry implicit decisions, and conflicting decisions carry
   bad results," that subagents working in isolation "cannot see what the other was doing" and
   produce inconsistent output, and recommends a single-threaded linear agent with full shared
   context as the default, reserving any splitting for a compression step on long tasks, an
   approach the same post admits is "hard to get right."[^cognition] Anthropic's own post draws the
   boundary from the other side: multi-agent fan-out earns its cost on "tasks that involve heavy
   parallelization, information that exceeds single context windows, and interfacing with numerous
   complex tools," and names its own bad fit explicitly: "most coding tasks involve fewer truly
   parallelizable tasks than research, and LLM agents are not yet great at coordinating and
   delegating to other agents in real time."[^anthropic-multiagent] The two posts landed one day
   apart, 2025-06-12 and 2025-06-13, and are best read as the field's live disagreement rather than
   a rebuttal exchange — both from named practitioners with production systems on the line (Devin;
   Claude's Research feature). *Skip it:* the chapter reads as though only Anthropic's framing
   exists, when the most-cited counterargument comes from a company that builds an agent for
   exactly the domain, coding, Anthropic names as the bad fit. **Contested**, as a general-purpose
   default; the live disagreement is precisely about which tasks are the exception, not whether the
   mechanism works at all. (Cognition (Walden Yan), "Don't Build Multi-Agents," 2025-06-12;
   Anthropic, ibid., 2025-06-13.)
7. **Security: wider blast radius, and one poisoned worker taints the synthesis** — fan-out
   changes the shape of two OWASP risks this reference already names elsewhere. The attack surface
   is the *union* of every worker's inputs: N workers touching untrusted content (scraped pages,
   supplier documents, retrieved chunks) means N chances for an indirect prompt injection to land
   (OWASP LLM01). But the synthesizer's *trust* is the intersection, not the union: it reads and
   reconciles every worker's output into one answer, so a single compromised worker can taint the
   final result even though the other N-1 were clean — the same "treat results as untrusted input"
   discipline [2.1 Tool Use](../the-unit/tool-use.md) names for one tool call, now required at
   every worker boundary, feeding whatever downstream action the synthesized output triggers
   (OWASP LLM06 Excessive Agency). Uncapped dynamic worker spawning is its own instance of OWASP
   LLM10 Unbounded Consumption, and it is not hypothetical: Anthropic's own postmortem names
   "spawning 50 subagents for simple queries" as an early failure mode they had to guardrail
   against explicitly.[^anthropic-multiagent] *Skip it:* a single poisoned document reaches
   production through the one worker that read it, or an uncapped decomposition burns a budget on
   a query that needed one worker. **Standard principle** (least privilege, treat results as
   untrusted, bound the fan-out); this sweep found no dedicated academic literature on
   orchestrator-worker-specific injection, so say that plainly rather than force a citation that
   doesn't exist yet — the mitigations are reasoned from OWASP's general categories plus
   Anthropic's own incident, the same evidentiary posture 3.2's coverage map already took for its
   analogous gap. (OWASP Top 10 for LLM Applications 2025 — LLM01, LLM06, LLM10; Anthropic, ibid.,
   the subagent-spawning postmortem.)
8. **Framework mechanics: dynamic fan-out vs. a fixed set of parallel branches** — the concrete
   code-level version of item 1's boundary. LangGraph's `Send` API is the reference mechanism for
   genuine dynamic fan-out: a conditional edge returns a *list* of `Send(node_name, state)` objects
   whose length is decided at runtime, because "the number of edges may not be known" ahead of
   time — the map-reduce pattern LangGraph's own docs name for exactly this case.[^langgraph]
   Contrast a graph wired with a fixed number of parallel edges declared at graph-construction
   time: correct, useful, and Parallelization/sectioning in code, not this chapter's genuinely-new
   half. *Skip it:* a reader copies a fixed-branch-count example, believes they have built
   orchestrator-workers, and never notices the model never made a sizing decision. **n/a**
   (framework mechanics; cite the shape via the multi-provider tabs, not a framework tour).
   (LangChain, "Graph API overview," the `Send` / map-reduce API.)
9. **The reliability reality: a dedicated multi-agent failure taxonomy** — the empirical case for
   why fan-out needs *more* gating discipline, not less. MAST, built from over 200 tasks across
   seven popular multi-agent frameworks and 1,600+ annotated traces, sorts real multi-agent
   failures into 14 modes across three categories: specification issues, inter-agent
   misalignment, and task verification[^mast] — the coordination failures items 2 and 5 warn about
   are not hypothetical; they are the measured majority of what breaks in practice. *Skip it:* the
   chapter's cost and skeptical-read items read as abstract caution rather than a category-by-category,
   empirically grounded finding. **Established** (a peer-reviewed, empirically grounded taxonomy,
   NeurIPS 2025 Datasets & Benchmarks track). (Cemri et al., "Why Do Multi-Agent LLM Systems
   Fail?", arXiv:2503.13657.)

## Mention-and-link (one line, a pointer, not a section)

- **The litmus tell in brief** ("it sizes its own work... how many workers to spawn") is already
  stated in 1.2; this chapter is its full treatment → [1.2 Who
  Decides?](../foundations/who-decides.md).
- **The augmented-LLM atom** each worker is one instance of; fan-out is already framed there as
  "several of these nodes run in parallel" → [1.4 The Augmented
  LLM](../foundations/the-augmented-llm.md).
- **Context-window cost per worker and inter-agent message tokens**, the depth behind item 4 →
  [1.5 Context Engineering](../foundations/context-engineering.md).
- **The typed contract** each worker's output and the synthesizer's merge rely on →
  [2.2 Structured Output](../the-unit/structured-output.md).
- **Ordering-dependent steps are a chain, not a fan-out**; this chapter is only for
  independent subtasks with no sequencing requirement between them → [3.1 Prompt
  Chaining](../composition/prompt-chaining.md).
- **The confusable-neighbours table row** already distinguishes this chapter's "how many workers,
  how to decompose" from a one-time branch pick → [3.2 Routing &
  Dispatch](../composition/the-router-that-isnt.md).
- **The synthesizer judging its own reconciliation and looping** would be a nested
  evaluator-optimizer instance, not this chapter's subject → [3.4
  Evaluator-Optimizer](evaluator-optimizer.md).
- **The sharpest neighbour to disambiguate**: same input, several fixed personas reconciled, the
  model picks the *lens*, not the *count*, vs. this chapter's different subtasks where the model
  picks the *count* → [3.5 The Specialist Panel](specialist-panel.md).
- **Evaluating decomposition quality and worker-output quality under nondeterminism** →
  [4.2 Evaluation](../craft/proving-it-works.md).
- **Escalation when the synthesizer can't reconcile conflicting worker outputs** →
  [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md).
- **Cheap model per worker, strong model for synthesis**, the same per-step model choice 3.1 names
  → [8.2 Which Model?](../production/which-model.md).
- **Token-multiplier economics in depth, model cascading across workers** →
  [8.4 Controlling Cost](../production/controlling-cost.md).
- **The architecture/hype layer this pattern is the concrete mechanism for**; 9.2's own stub
  already states "most 'multi-agent' systems are one orchestrator with workers" — heavy two-way
  link → [9.2 Multi-Agent](../frontier/more-than-one-agent.md).
- **Over-orchestration**, the anti-pattern this chapter's Gotchas should feed → [Anti-Patterns
  Catalog](../catalogs/anti-patterns.md).

## Out of scope (name it, point out)

- Agent handoffs, swarm topologies, and the "manager pattern" as architectures in depth →
  [9.2 Multi-Agent](../frontier/more-than-one-agent.md).
- Voting / self-consistency (Anthropic's Parallelization sub-variant: run the same task N times,
  aggregate by vote) — name it for contrast against sectioning and orchestrator-workers, don't
  teach it; no chapter in the current nav owns plain Parallelization or voting as their own topic
  (see Open questions).
- Model cascading / cost-tier routing across workers → [8.4 Controlling
  Cost](../production/controlling-cost.md).
- The `Send` API's exact signature and reducer syntax in depth → vendor docs; this chapter shows
  the shape via the multi-provider tabs only.
- Deep treatment of context curation mechanics (exactly what to condense from a worker before it
  crosses back to the orchestrator) → [1.5 Context
  Engineering](../foundations/context-engineering.md) and [5.4
  Compaction](../knowledge/compaction-and-the-window.md).
- MAST's full 14-mode taxonomy in depth → cite the finding and the category count; do not
  reproduce the whole taxonomy table.
- Automated/algorithmic topology selection and decomposition (2025-2026 survey literature on
  designer/executor loops and RL-trained team decomposition) — real and active, but unsettled and
  not yet a teachable, citable default; name as Emerging in the Maturity summary, do not build a
  must-cover item on a moving research target.

## Maturity summary

- **Standard:** fixed-count parallel fan-out / scatter-gather / worker pools as a mechanism (a
  decades-old distributed-systems idiom, MapReduce-shaped); concurrent execution with a
  deterministic merge step.
- **Established:** dynamic orchestrator-workers as a named, vendor-documented workflow, shipping
  in a real product (Claude's Research feature); context isolation as the mechanism that makes the
  pattern's compression work; the cost multiplier as a measured (if snapshot) finding; the MAST
  failure taxonomy.
- **Emerging:** automated/algorithmic topology selection and decomposition (2025-2026 survey-stage
  research); no consensus default for *how* an orchestrator should decide its own decomposition
  strategy.
- **Contested:** whether dynamic multi-agent fan-out is a good default at all outside heavily
  parallelizable, low-shared-context tasks (Cognition's explicit counter-position, held by a
  company building a coding agent, the exact domain Anthropic itself names as the bad fit); billing
  a fixed, known-count parallel section as "the model orchestrating a team," the same
  over-orchestration/agent-washing failure [3.2](../composition/the-router-that-isnt.md) names for
  routing.

**Recommended maturity verdict for the chapter as a whole:** split it, the way
[3.2](../composition/the-router-that-isnt.md) already set precedent for a two-sided chapter —
**"Standard (fixed parallel fan-out) · Established (dynamic orchestrator-workers)."** I do not
fully agree with the stub's current single-word "Established": the technique itself deserves that
verdict, but collapsing both litmus sides into one word without an explicit split risks the exact
conflation this chapter exists to prevent — especially given that the carrier's own worked example
for this chapter currently reads as the fixed case (see Open questions, item 1). A single "Established"
line invites a reader (or a chapter-writer, or the carrier's own step-7 code) to treat "parallel and
proven" as sufficient, when the genuinely-new claim rests entirely on the model owning the
decomposition, not on the parallelism.

## Sources

Vendor/primary: Anthropic, "Building Effective Agents" (2024-12-19) — the Parallelization
(sectioning/voting) and Orchestrator-workers workflow definitions and the "pre-defined" vs.
"determined by the orchestrator" distinction that is this chapter's spine.
<https://www.anthropic.com/research/building-effective-agents> Anthropic, "How we built our
multi-agent research system" (2025-06-13) — the orchestrator-worker architecture in production
(Claude's Research feature), the token-multiplier finding (~4x agents vs. chat, ~15x multi-agent
vs. chat), the non-determinism admission, the coding-tasks-are-a-bad-fit caveat, the
subagent-spawning postmortem, and the lead-agent synthesis framing.
<https://www.anthropic.com/engineering/multi-agent-research-system> LangChain, "Graph API
overview" (LangGraph docs) — the `Send` API and map-reduce pattern, the reference mechanism for
dynamic, runtime-determined fan-out. <https://docs.langchain.com/oss/python/langgraph/graph-api>
Skeptical: Cognition (Walden Yan), "Don't Build Multi-Agents" (2025-06-12) — the fragmented-context
and conflicting-implicit-decisions argument against parallel subagent fan-out, and the
single-threaded-linear-agent recommendation. <https://cognition.ai/blog/dont-build-multi-agents>
(redirects to <https://cognition.com/blog/dont-build-multi-agents>). Academic: Cemri, M. et al.,
"Why Do Multi-Agent LLM Systems Fail?" (NeurIPS 2025, Datasets and Benchmarks Track) — the MAST
failure taxonomy, 14 modes across 3 categories, from 200+ tasks and 1,600+ annotated traces across
7 frameworks. <https://arxiv.org/abs/2503.13657> Security: OWASP, "Top 10 for LLM Applications
2025" — LLM01 Prompt Injection, LLM06 Excessive Agency, LLM10 Unbounded Consumption.
<https://genai.owasp.org/llm-top-10/> Internal: [1.2 Who
Decides?](../foundations/who-decides.md) (the litmus tell in brief); [1.4 The Augmented
LLM](../foundations/the-augmented-llm.md) (the atom fan-out composes); [3.2 Routing & Dispatch
coverage map](the-router-that-isnt.md) (precedent for a two-verdict lens line on a two-sided
chapter, and its own thin-evidence posture on a security gap, reused for item 7 here);
`meta/carrier-bible.md` (Listing Studio step 7 and the category-scout sibling surface, both
discussed in Open questions).

> **Verify before quoting:** the 4x/15x token multiplier and the internal-eval performance
> improvement Anthropic reports are both snapshots from one system on one set of evals in mid-2025
> and will shift with model and eval generation; cite the finding (fan-out costs an order of
> magnitude more than a single call) and the live source, never the frozen percentage. This sweep
> found no dedicated academic literature on injection or manipulation attacks specific to
> orchestrator-worker fan-out (as opposed to general multi-agent or model-routing literature); if
> the fact-checker turns up a closer match, upgrade the citation in item 7. The MAST paper's exact
> venue/track listing should be re-confirmed against the camera-ready NeurIPS 2025 proceedings
> before the chapter cites a specific page or table.

## Sweep angles run and skipped

- **Vendor/primary docs — ran fully.** Anthropic's two posts (the taxonomy source, and the deep
  real-world case study) and LangGraph's `Send` API docs. This is the strongest-evidenced angle
  for this chapter; both Anthropic sources are primary and directly on-topic.
- **Academic/benchmarks — ran, and pruned deliberately.** MAST (arXiv:2503.13657) is the one
  citable, peer-reviewed anchor. A broader scan of 2025-2026 survey and RL-decomposition
  literature (DyFlow, hierarchical-RL team decomposition, topology-selection surveys) turned up an
  active but unsettled research area; judged Emerging and named in the Maturity summary rather
  than built into a must-cover item, since none of it is a settled, teachable default yet.
- **Security/failure modes — ran.** OWASP LLM01/LLM06/LLM10 applied to the fan-out shape
  specifically (union of attack surface, intersection of synthesis trust, uncapped spawning). No
  dedicated orchestrator-worker-specific injection literature found; said so plainly rather than
  force a citation, mirroring 3.2's own posture on an analogous gap.
- **Practitioner writeups — partially covered by the vendor angle.** Anthropic's own
  "How we built..." post functions as a first-party practitioner account (the "50 subagents" and
  coordination-failure admissions are their own production postmortem, not third-party
  corroboration), so it is cited under vendor/primary rather than double-counted as a separate
  angle. No independent third-party production writeup with citable specifics was found this
  sweep; if the author has one, it strengthens item 9.
- **The skeptical read — ran.** Cognition/Walden Yan's post, verified directly and represented
  with its own recommended alternative (single-threaded linear agents), not reduced to a foil for
  Anthropic's framing.
- **Skipped deliberately:** a dedicated search for Mixture-of-Agents-style ensemble-aggregation
  academic work. It sits outside this chapter's scope per item 1's boundary (aggregation of N
  parallel *same*-task attempts is closer to voting than to orchestrator-workers), and no citation
  was verified live this sweep; flagged as a possible Further Reading candidate rather than
  asserted from memory.

## Ruled — author sign-off, 2026-07-29

**The must-cover list above is signed off as written, all nine items, no trims.** It is the
chapter's contract; a `missing` item at Stage 4 sends the draft back to Stage 3.

1. **Carrier example: resolved as A, not the recommended B.** The research sweep couldn't see the
   first-hand system and so had to hedge on whether option A was honestly available. It is: the
   author confirms first-hand grounding for both litmus halves. So step 7 stays the
   carrier home and splits in two: the three standard deliverables (listing, email, ad copy, always
   produced, code decides) as the deflated contrast, then a model-named list of extra deliverables
   with one worker each (compliance insert, MAP-safe ad variant, freight/assembly blurb, nothing at
   all for a simple product) as the genuinely-new half. `meta/carrier-bible.md` step 7 is amended to
   match. B was rejected because it would move the positive case onto a "reasoned / lightly built"
   surface and give up production grounding on the one chapter that has it; category scout stays a
   mention-and-link for the research-fan-out variant.
   **Collision guard:** the dynamic half is about *deliverables and channels*, never page sections.
   Step 5's content blocks belong to 3.5.
2. **Grounding: `production + research`,** as the stub already says. The fixed-plus-dynamic shape
   is first-hand, so the chapter carries one **"From production."** callout covering both halves.
   One label, not fragmented; recast into commerce, never the real domain.
3. **Two-verdict lens line: adopted.** `Maturity: Standard (fixed parallel fan-out) · Established
   (dynamic orchestrator-workers)`, with the matching two-part *Who decides* line (your code / the
   model). Follows 3.2's precedent, and item 1's split makes it necessary.
4. **Plain Parallelization gets its home here** — as the deflated half of item 1, named by name, not
   as its own teaching section. **Voting / self-consistency is out entirely**: it is a
   reliability/eval technique, not composition; 4.2 is its eventual home if it wants one.
5. **MAST and the cost multiplier stay here.** 9.2 and 8.4 don't exist yet; a gap now is worse than
   a cheap migration later.

### Record: the options considered and rejected

*Superseded by the rulings above — kept as the audit trail for why, not as live questions. Nothing
below is still open.*

- **The carrier's own worked example may not pass its own litmus — highest priority.**
  `meta/carrier-bible.md` step 7 ("assemble launch package: fan out to write listing + email + ad
  copy in parallel") is documented as three fixed, always-produced deliverables. As written, that
  is Anthropic's Parallelization/sectioning (code decides the branch count and composition every
  time), not orchestrator-workers (model decides how many and what to decompose) — see item 1.
  Three ways to resolve it, with trade-offs:
  - **A — Confirm the real system's step genuinely varied deliverable count/composition per
    product**, and add that detail to the carrier bible (e.g., a compliance-flagged product like
    the bunk bed gets an extra safety-insert deliverable a plain desk doesn't, or a low-margin SKU
    skips paid ad copy). *For:* keeps the strongest possible grounding (a real "From production"
    story) if it's actually true. *Against:* it may not be true; inventing a plausible-sounding
    trigger the real system never had would be exactly the kind of invented specificity the
    carrier bible's own warning (`"Numbers come from the code, not from imagination"`) exists to
    prevent, and this reference's confidentiality rule means the real code can't be checked from
    here to verify either way.
  - **B — Use the category-scout sibling surface as the primary illustration instead.** The
    carrier bible already earmarks it for "research fan-out and synthesis," "reasoned / lightly
    built" — a natural fit, and it mirrors Anthropic's own real-world case study (a research agent
    that decides how many sub-questions to investigate) almost exactly. Step 7 would then become
    the chapter's honest "looks like it, isn't" contrast case for item 1, which the chapter needs
    anyway. *For:* lower-risk than amending pipeline mechanics, and elegantly solves the
    both-sides-of-the-boundary requirement in one move. *Against:* the chapter's primary example
    moves from the flagship, most-grounded surface to a "reasoned / lightly built" one, a step down
    in grounding strength unless the coder-tester builds it out properly.
  - **C — Leave step 7 as the sole example and present it candidly as the deflated case**,
    teaching orchestrator-workers itself through a different, non-carrier illustration or through
    Anthropic's own research-agent case study directly. *For:* no carrier amendment needed.
    *Against:* breaks this reference's own "all examples live in the carrier world" discipline
    (CLAUDE.md non-negotiable #4) for the chapter's central positive case, which no other finished
    chapter has had to do.
  - **Recommend B**, provisionally, pending author confirmation of what the real system's step 7
    actually did (which settles whether A is even honestly available). This needs sign-off before
    `coder-tester` builds anything — get it wrong and either the companion code or the "genuinely
    new" claim itself is compromised.
- **Grounding: is any part of this chapter honestly "From production"?** Depends entirely on the
  above. If step 7 as documented is the deflated case, the "From production" callout (if the real
  system's step ever had one) may only support the **Standard**/fixed-fan-out half, and the
  **Established**/dynamic half may need to stay "companion repo" or "reasoned" grounding via
  category-scout instead of inheriting Listing Studio's usual production-grounded status.
- **The two-verdict lens line.** Recommend splitting the stub's single "Established" into the
  explicit two-part form 3.2 set precedent for — see Maturity summary above — with a matching
  two-part *Who decides* line (your code / the model). This is the second instance of a two-sided
  chapter after 3.2; worth the author's explicit, repeatable sign-off rather than a silent default,
  per 3.2's own open question on this exact point.
- **Does plain Parallelization (sectioning/voting) get a home anywhere in the nav, or does 3.3
  become its only home too, the way 3.2 became LLM routing's?** Neither sectioning nor voting
  appears in Part III's current five chapters. If a reader searching "parallelization" or "run
  three prompts and vote" lands on 3.3, the chapter may need to name and deflate both by name (not
  just contrast them implicitly against orchestrator-workers), the same knowing exception 3.2 took
  for routing. Flagging rather than assuming; if the reference later wants a dedicated
  parallelization/ensembling page, this map's items 1 and 8 would need to move with it.
- **Should the MAST taxonomy and the cost-multiplier finding live here permanently, or partly
  migrate to 9.2 / 8.4 once those are written?** Both citations describe multi-agent systems
  generally, of which orchestrator-workers is this reference's concrete, scoped instance (per
  9.2's own stub line: "most 'multi-agent' systems are one orchestrator with workers"). Recommend
  keeping the core citations here, since 3.3 is the mechanism chapter being written now, with 9.2
  inheriting only the hype/architecture-layer treatment when it lands; flag for reconsideration if
  9.2 later wants its own dedicated failure-taxonomy section.

[^anthropic-bea]: Anthropic, "Building Effective Agents" (2024-12-19). Parallelization: "LLMs can
sometimes work simultaneously on a task and have their outputs aggregated programmatically,"
sectioning ("breaking a task into independent subtasks run in parallel") and voting ("running the
same task multiple times to get diverse outputs"). Orchestrator-workers: "a central LLM
dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results," with
subtasks "not pre-defined, but determined by the orchestrator based on the specific input."
<https://www.anthropic.com/research/building-effective-agents>
[^anthropic-multiagent]: Anthropic, "How we built our multi-agent research system" (2025-06-13).
The orchestrator-worker architecture behind Claude's Research feature; the token-multiplier
finding; the non-determinism admission; the coding-tasks-are-a-worse-fit caveat; the
subagent-spawning postmortem; the lead-agent synthesis framing.
<https://www.anthropic.com/engineering/multi-agent-research-system>
[^langgraph]: LangChain, "Graph API overview" (LangGraph docs). The `Send` API: "Send takes two
arguments: first is the name of the node, and second is the state to pass to that node," used from
a conditional edge to fan out to a runtime-determined number of workers, the map-reduce pattern the
docs name for cases where "the number of edges may not be known" ahead of time.
<https://docs.langchain.com/oss/python/langgraph/graph-api>
[^cognition]: Cognition (Walden Yan), "Don't Build Multi-Agents" (2025-06-12). "Actions carry
implicit decisions, and conflicting decisions carry bad results"; parallel subagents "cannot see
what the other was doing"; recommends a single-threaded linear agent as the default.
<https://cognition.ai/blog/dont-build-multi-agents>
[^mast]: Cemri, M. et al., "Why Do Multi-Agent LLM Systems Fail?" (NeurIPS 2025, Datasets and
Benchmarks Track). The MAST taxonomy: 14 failure modes across 3 categories (specification issues,
inter-agent misalignment, task verification), from 200+ tasks and 1,600+ annotated traces across 7
multi-agent frameworks. <https://arxiv.org/abs/2503.13657>
