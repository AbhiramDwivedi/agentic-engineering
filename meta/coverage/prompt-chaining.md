# Coverage map: Prompt Chaining (chapter 3.1)

> **Thesis** (the one sentence the chapter argues): *You split the prompt not for modularity but
> because a single call cannot reliably hold the task, and the split is worthless without a gate.*
>
> **Budget:** standard pattern, ~2,000-2,800 prose words to the end of *In short* (code, sources,
> and cross-links excluded). A ceiling, not a target.
>
> Covering a must-cover item in one clause is complete coverage. Length is not coverage.

> Research-derived spec for what the chapter must cover to let a reader build a reliable
> multi-step pipeline, and where to stop. Built from a 4-angle sweep (vendor/primary docs,
> academic, failure-mode/compounding-error, skeptical read); practitioner writeups were
> checked but yielded consensus rather than a citable primary source, see the note under
> Mention-and-link. Review and trim the **Must-cover** list; that sets the chapter's scope.
> Bar: definitive but tight (the Gang-of-Four / Wikipedia test), not exhaustive. The chapter
> path is a stub with no real prose yet, so nothing below is marked `[*]`/`[+]`.

> **Signed off: 2026-07-03 (author).** Decisions at sign-off: the CoT and two-pass boundary
> items merged into item 4; the two recent preprints stay, cited hedged as directional; the
> OpenAI guide's wording pinned from the author's downloaded PDF (live URL 403s); **item 5
> (chain vs. the agent loop) added by author request.** This 9-item list is the chapter's
> contract.

## The mental model (what the reader must leave with)

Prompt chaining is a task decomposed into an ordered sequence of model calls, where each
step's output becomes the next step's input and your code owns the order and what is allowed
to pass the gate between steps. On this book's litmus test it is the **honest draw**:
structurally it is an old idea, a pipeline, and your code decides the sequence, not the model,
so it fails the "genuinely new" test cleanly. But the reason you reach for it is not old: you
split the task because a single model call cannot reliably hold the whole thing end to end,
context degrades as it fills, a wrong turn early in the reasoning compounds silently through
everything that follows, and you need a checkpoint to catch that before it reaches the next
step, not only at the end. Old structure, new reason. (Listing Studio's own nine-step pipeline,
already established across the reference as the running carrier, *is* this pattern at the
top level; the chapter should lean on it rather than invent a new example.)

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation.

1. **The definition, and the honest-draw argument** — decompose into an ordered sequence of
   LLM calls, each processing the last one's output; ideal when a task cleanly decomposes into
   fixed subtasks. State explicitly that the *structure* is an old pipeline (your code decides
   the order) while the *reason to split* is new (one call can't hold the task: context limits,
   attention degradation, error compounding, the need to validate mid-flight). Skip it and the
   chapter either oversells chaining as agentic or undersells why it's still worth a chapter.
   **Standard.** (Anthropic, "Building Effective Agents": prompt chaining "decomposes a task
   into a sequence of steps, where each LLM call processes the output of the previous one,"
   "ideal for situations where the task can be easily and cleanly decomposed into fixed
   subtasks. The main goal is to trade off latency for higher accuracy, by making each LLM
   call an easier task.")
2. **The gate: programmatic checks between steps** — Anthropic's own diagram names this
   explicitly: add a programmatic check ("gate") on any intermediate step to confirm the
   process is still on track before continuing. This is the chapter's failure-return-contract
   obligation: a failed gate must come back as a structured, recoverable signal (retry the
   step with the validation error, same shape as 2.2's re-ask loop; route to a human; or abort
   the chain loudly), never a silent pass-through or a raw exception. *Skip it:* a bad
   intermediate output flows downstream untouched and the failure surfaces late, expensively,
   or not at all. **Standard.** (Anthropic, ibid., the "gate" in the workflow diagram; pattern
   continuous with [2.2 Structured Output](../the-unit/structured-output.md)'s re-ask loop.)
3. **Why gates matter: compounding failure down the chain** — the reliability math. For *m*
   sequential steps with independent per-step error, end-to-end success falls off fast:
   illustratively, 99% per-step accuracy across 10 steps is ~90%, across 100 steps is ~37%.
   The exact numbers are illustrative, not to be frozen or over-cited as authoritative; the
   shape of the argument (errors compound multiplicatively, not additively) is what must land.
   *Skip it:* the chapter's push for gates reads as unmotivated caution instead of an argued
   cost. **Established** (the math is a direct consequence of independent-step probability,
   corroborated by several practitioner writeups independently deriving the same shape);
   **Emerging** (the specific architectural fixes beyond a simple gate, e.g. consensus voting
   across resampled steps). (Patel et al., "The Six Sigma Agent," arXiv:2601.22290 — a very
   recent, non-peer-reviewed industry-lab preprint; cite the formula and the shape of the
   finding, not the paper as a settled authority.)
4. **Definitional boundaries: not chain-of-thought, and two-pass generation folds in here**
   *(merged from two items at author sign-off, 2026-07-03)* — the two conflations readers
   bring. First, chain-of-thought is one model call reasoning stepwise inside a single
   response; prompt chaining is multiple discrete calls, each a full round trip, with your
   code inspecting and gating what crosses the boundary. Readers who conflate them import
   CoT's single-call intuitions (no gate, no external state, no extra cost) onto a pattern
   where none of that holds. Second, two-pass generation (draft, then refine in a second
   pass) is prompt chaining at the finest possible grain: two steps, fixed order, your code
   decides to run the second call. It is *not* evaluator-optimizer (3.4): no model-judged
   rubric, no loop; the second pass is a fixed, unconditional call, not a decision the model
   makes about whether to continue. *Skip it:* readers treat CoT and chaining as
   interchangeable, and the reference either bills two-pass as a distinct pattern (against
   the book's own "cut/merge" ruling) or never mentions it and a reader wonders where it
   went. **n/a — definitional and scope decisions, not external maturity claims.** (Wei et
   al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models,"
   arXiv:2201.11903; house stance, `DECISIONS.md` / `CLAUDE.md`: "merge two-pass
   generation... fold in, don't bill as distinct.")
5. **The comparison: a chain vs. the agent loop** *(added at author sign-off, 2026-07-03)* —
   the pattern's nearest look-alike on the other end of the control spectrum. A chain fixes
   the sequence in code before the run; an agent loop hands the model the next-step decision
   and runs until an exit condition is reached (a final output, a response with no tool
   calls, an error, or a turn cap). It is the book's litmus applied to control flow. Where
   each wins: the chain for unattended production pipelines, where predictable cost and
   latency, per-step gates, and debuggability matter more than flexibility; the loop for
   open-ended tasks whose shape is not known upfront, today most visibly interactive and
   local coding agents, though unattended server-side loops exist (deep research; the
   repricing/restock agent surface). The felt split ("loops are for local work, chains are
   for agentic apps") is a real practitioner observation, but the underlying axis is
   supervision and reliability tolerance, not deployment location: a loop usually runs with
   a human or a hard cap watching it, while an unattended pipeline wants determinism.
   *Skip it:* readers reach for a loop on a fixed pipeline (buying nondeterminism they don't
   need) or hand-build a chain for a task only a loop can shape. Term note: "loop
   engineering" is not standard vocabulary; the chapter says "the agent loop", defines it on
   first use, and points to [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md)
   for the spectrum and [9.1 Autonomous Agents](../frontier/when-you-want-autonomy.md) for
   loop depth rather than teaching the loop here. **Established** (the distinction is
   vendor-documented on both sides). (OpenAI, "A Practical Guide to Building Agents," p. 14,
   verbatim and dash-free: "Every orchestration approach needs the concept of a 'run',
   typically implemented as a loop that lets agents operate until an exit condition is
   reached. Common exit conditions include tool calls, a certain structured output, errors,
   or reaching a maximum number of turns." Anthropic, "Building Effective Agents," the
   workflows-vs-agents distinction.)
6. **The cost you're paying: latency and money, traded for reliability** — every step is a
   full model round trip: more tokens, more latency, more dollars, in exchange for each
   individual call being an easier, more reliable task. Name this trade explicitly rather than
   let it be implicit. *Skip it:* readers chain reflexively without weighing the honest cost
   against a single well-scoped call. **Standard.** (Anthropic, ibid., "trade off latency for
   higher accuracy.")
7. **What crosses the gate is a context-budget decision** — each step should receive a window
   curated for its job, not the accumulated output of every prior step; the accumulation is
   exactly the naive failure mode [1.5 Context Engineering](../foundations/context-engineering.md)
   already names as a Listing Studio illustration. Name both costs here (tokens, and the
   attention degradation from carrying dead weight forward) and the mitigation (inject the
   minimal relevant subset per step), then point to 1.5 for the depth. *Skip it:* a chain
   silently turns into the thing that made a single mega-prompt fail in the first place, just
   spread across more calls. **Established**, inherited from 1.5's own verdict. (Cross-link,
   not a new claim; source is 1.5's own citations.)
8. **The academic pedigree: decomposition is an old, validated idea** — two anchors, from
   different fields, that predate the "agentic" vocabulary and ground chaining as engineering
   discipline rather than a 2024 invention. *Skip it:* the chapter reads as if Anthropic
   invented step decomposition in 2024, when the case for it (transparency, controllability,
   compositional accuracy) was already made in HCI and NLP research two years earlier.
   **Established.** (Wu, Terry, Cai, "AI Chains: Transparent and Controllable Human-AI
   Interaction by Chaining Large Language Model Prompts," CHI 2022, DOI
   10.1145/3491102.3517582 — chaining prompts into inspectable, editable intermediate steps
   improved task quality *and* user-perceived transparency/control/collaboration in a 20-person
   study. Zhou et al., "Least-to-Most Prompting Enables Complex Reasoning in Large Language
   Models," arXiv:2205.10625 — sequentially solving decomposed subproblems, each aided by the
   prior subproblem's answer, generalizes to harder problems than seen in the prompt and beats
   chain-of-thought on compositional tasks.)
9. **The skeptical read: when chaining is the wrong call** — two overclaims to name. First,
   growing context windows do not eliminate the case for decomposition, but they do shift it:
   when steps have low cross-step dependency (low "task noise"), chunking a long input still
   helps; when steps are highly entangled, a single well-scoped call can beat an artificially
   chained one, and the chain adds pure aggregation-error surface for no benefit. Second,
   over-decomposition is a real anti-pattern in its own right: too many tiny steps multiplies
   latency, cost, and the number of gates that can each independently fail, without a
   commensurate reliability gain once each step is already easy enough for the model to do
   reliably in one shot. *Skip it:* the chapter reads as "always decompose," which is exactly
   the reflex this reference exists to push back on. **Emerging** (the noise-based framework
   for predicting when decomposition helps is a 2025 preprint, unsettled); **Contested**
   ("maximal decomposition is always safer" as a default habit). (Xu et al., "When Does Divide
   and Conquer Work for Long Context LLM? A Noise Decomposition Framework," arXiv:2506.16411 —
   chunking helps when per-chunk model-degradation noise dominates, hurts when cross-chunk
   task-dependency noise dominates.)

## Mention-and-link (one line, a pointer, not a section)

- **The augmented-LLM unit** each chain node is built from → [1.4 The Augmented LLM](../foundations/the-augmented-llm.md).
- **Structured output as the inter-step contract** (the typed object a gate validates, the
  re-ask-with-structured-error loop this chapter's gate reuses) → [2.2 Structured Output](../the-unit/structured-output.md).
- **Conditional branching between steps** is the router's job, not chaining's; a chain that
  picks its next step from a classifier is 3.2's pattern wearing a chain's clothes →
  [3.2 Front Controller](the-router-that-isnt.md).
- **Parallel, independent steps** (no ordering dependency) are fan-out, not a chain →
  [3.3 Orchestrator-Workers](fan-out.md).
- **The model judging its own output and deciding to loop** is evaluator-optimizer, the
  genuinely-new sibling this chapter must not be confused with → [3.4 Evaluator-Optimizer](evaluator-optimizer.md).
- **A failed gate that needs a person, not a retry** → [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md).
- **Where chaining sits among the five named workflow patterns**, and the workflow-vs-agent
  spectrum this pattern lives entirely on the workflow end of → [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md).
- **LangGraph as the reference sequential-graph shape** (nodes, edges, `StateGraph`) — cite the
  shape, do not teach the framework's API; the multi-provider code tabs carry the how. →
  LangChain docs, "Workflows and agents" (docs.langchain.com/oss/python/langgraph/workflows-agents).
- **Practitioner consensus was checked, not cited as a primary source.** Multiple independent
  practitioner writeups converge on the same two claims (validation gates between steps are
  not optional; splitting a task lowers per-call failure rate at the cost of more round trips)
  without a single authoritative source worth quoting over the vendor docs above. Treat this as
  corroboration of items 1–3, not a citation to add.

## Out of scope (name it, point out)

- Prompt wording and management at each individual step → [4.1 Prompt Management](../craft/prompts-are-source-code.md).
- Building the LangGraph/LCEL chain API itself, or any framework's chain-construction syntax
  → the framework's own docs; this chapter shows the shape via the multi-provider code tabs,
  not a framework tutorial.
- Parallel/fan-out variants of decomposition → [3.3 Orchestrator-Workers](fan-out.md).
- The model deciding whether to continue looping against a quality bar → [3.4 Evaluator-Optimizer](evaluator-optimizer.md).
- Deep treatment of context curation mechanics (what exactly to summarize, compact, or carry
  forward) → [1.5 Context Engineering](../foundations/context-engineering.md) and
  [5.4 Compaction](../knowledge/compaction-and-the-window.md); this chapter only names the cost
  at the gate.

## Maturity summary

- **Standard:** prompt chaining as a named workflow pattern; the sequence-of-calls-with-a-gate
  shape; the latency-for-reliability trade; treating each step's output as something you check
  before it crosses the boundary.
- **Established:** the compounding-error argument for why gates matter (the math itself); the
  academic decomposition pedigree (AI Chains, Least-to-Most); context curation across chain
  steps (inherits 1.5's verdict).
- **Emerging:** architectural fixes for compounding error beyond a simple gate (consensus/
  resampling across steps); the noise-based framework for predicting exactly when decomposition
  helps versus hurts under long context.
- **Contested:** "decompose maximally, always" as a reflexive default; presenting the pattern
  itself as agentic rather than the litmus's honest draw.

## Sources

Vendor/primary: Anthropic, "Building Effective Agents" (2024-12-19), for the prompt-chaining
definition, the "gate" concept, and the latency-for-accuracy trade
(anthropic.com/research/building-effective-agents). OpenAI, "A Practical Guide to Building
Agents" (April 2025)
(openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/) — the live
page 403s to non-browser fetches, so wording was verified 2026-07-03 against the author's
downloaded PDF (34 pp.). Verbatim, p. 4: "A workflow is a sequence of steps that must be
executed to meet the user's goal" (dash-free, safe to quote directly), and, corroborating the
honest-draw / who-decides framing: applications that integrate LLMs but do not use them to
control workflow execution ("think simple chatbots, single-turn LLMs, or sentiment
classifiers") "are not agents" — the full sentence contains an em-dash, so the chapter must
paraphrase it or quote only the dash-free fragments, or it trips the zero-dash gate. The guide
never names "prompt chaining" as a pattern (that taxonomy is Anthropic's); cite it only for the
workflow definition and the code-vs-model-control boundary. LangChain,
"Workflows and agents" (docs.langchain.com/oss/python/langgraph/workflows-agents), the reference
sequential-graph shape. Academic: Wu, Terry, Cai, "AI Chains: Transparent and Controllable
Human-AI Interaction by Chaining Large Language Model Prompts," CHI 2022, DOI
10.1145/3491102.3517582. Zhou et al., "Least-to-Most Prompting Enables Complex Reasoning in
Large Language Models," arXiv:2205.10625. Wei et al., "Chain-of-Thought Prompting Elicits
Reasoning in Large Language Models," arXiv:2201.11903 (for the CoT/chaining boundary).
Failure-mode / compounding error: Patel et al. (Lyzr Research), "The Six Sigma Agent,"
arXiv:2601.22290 — recent, non-peer-reviewed; cite the formula's shape, not as a settled
authority. Skeptical: Xu et al., "When Does Divide and Conquer Work for Long Context LLM? A
Noise Decomposition Framework," arXiv:2506.16411.

> **Verify before quoting:** the compounding-error percentages (99%
> per-step at 10/100 steps) are illustrative applications of `(1-p)^m`, not a benchmark result
> to freeze — reproduce the arithmetic yourself rather than quoting the paper's numbers as
> found data. arXiv:2601.22290 and arXiv:2506.16411 are both very recent (2025/2026) preprints
> from industry-lab or small-team authors, not yet peer-reviewed or widely cited — treat their
> specific claims as directional, and re-check whether a more established citation has since
> superseded them.
