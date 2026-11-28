# Coverage map: Planning & Task Decomposition (chapter 3.6)

> **Thesis** (the one sentence the chapter argues): *Plan-and-execute lets the model write the
> sequence once and your code decide when, if ever, to ask again — trading the step-by-step loop's
> adaptivity for a plan your code can validate and budget before anything runs, and risking a bad
> plan staying frozen for however long that trigger takes to fire.*
>
> Alternatives considered, for the author to weigh at sign-off:
> 1. *A model-written plan gives code a checkpoint it can validate and budget before execution, but
>    every step fixed before observing the world trades away a chance to adapt.*
> 2. *The model deciding the plan is genuinely new; deciding not to re-ask it at every step is your
>    code's oldest trick, and conflating the two is how a fixed pipeline gets sold as autonomy.*

> **Budget:** standard pattern, ~2,000-2,800 prose words to the end of *In short* (code, sources,
> and cross-links excluded). A ceiling, not a target. **Not** the flagship row: 3.6 sits outside the
> origin-set genuinely-new four (tool use, evaluator-optimizer, orchestrator-workers, specialist
> panel) that inherit the flagship budget. The must-cover list below runs seven items after a
> second-reviewer pass trimmed and merged the first draft's nine; most of the remaining depth
> already has a paid-for home next door — the step-by-step loop's mechanics belong to 2.5, the
> deterministic verify-and-retry loop to 3.7, and the approval gate to 4.3. This chapter's job is
> comparative and taxonomic (place plan-and-execute among its neighbours and its own family)
> rather than exhaustive, which is what keeps it in the standard row.

> Research-derived spec for what the chapter must cover to let a reader tell a genuinely
> model-written plan from a fixed pipeline wearing "planning" as a label, place plan-and-execute
> correctly against the step-by-step loop next door, and validate a plan before trusting it with
> anything. Built from an 8-angle sweep; see "Sweep angles run and skipped" below. The chapter path
> (`docs/composition/planning.md`) is a stub carrying an unargued `Maturity: Established` line, a
> placeholder alias list, and no real prose, so nothing below is marked `[*]`/`[+]` against
> existing text — this is a fresh map, and the stub's three placeholders are evaluated, not
> assumed, below. This version incorporates a second-reviewer pass (see that section, placed just
> before Open questions) that corrected a load-bearing inconsistency in the first draft's ownership
> model; read that section before trusting anything about who re-consults whom. Review and trim the
> **Must-cover** list; that sets the chapter's scope. Bar: definitive but tight (the Gang-of-Four /
> Wikipedia test), not exhaustive.

## The mental model (what the reader must leave with)

Planning is the model deciding a sequence of steps toward a goal before your code has committed to
running all of them. That decision is always genuinely new by this reference's litmus — nothing in
the pre-LLM toolbox writes a plan tailored to a specific, novel input. What varies, and what "plan-
and-execute" as a casual label routinely hides, is a second, independent decision: **how often your
code goes back and asks the model to reconsider.** That second decision is a spectrum, not a
binary, and the chapter's job is to put a name on each point rather than let "plan-and-execute"
mean three different architectures depending on who is using the phrase.

At one end sits **static plan-first**: the model writes the whole sequence once, and code executes
every step without returning to the model at all, barring the ordinary per-step tool calls that
aren't planning calls. In the middle sits **trigger-based replanning**: code executes from the
existing plan and consults the model again only when a defined event fires — a step fails, a
budget or check comes back negative — never on an ordinary success. At the far end sits **step-wise
reconsult**: the model is consulted after every single step, which is functionally continuous with
[2.5 The Agent Loop](../the-unit/the-agent-loop.md)'s step-by-step, ReAct-style architecture, even
when the implementation still calls itself "plan-and-execute" and still maintains an explicit
`Plan` object. That last case is not hypothetical or rare: it is what LangGraph's own reference
plan-and-execute notebook actually does (item 5 below), which is exactly why this spectrum has to
be named precisely rather than assumed.

None of these three points is "more agentic" than another — all three still have the model
deciding the sequence, which is what earns this pattern its place among the "model decides"
patterns. What differs is a code-owned decision layered on top: whether, and how often, to ask
again. Static plan-first buys the most predictability (one model call, a validated artifact, a
budget fixed before anything runs) at the highest risk of freezing a bad plan; step-wise reconsult
buys the most adaptivity at the cost of losing the very thing that made "plan-and-execute" worth
naming separately from the agent loop in the first place. The chapter's honest job is to place a
real system on this spectrum from its code, not from what its authors called it.

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation. All items are fresh
gaps against the current stub, which has no argued prose yet.

1. **The litmus line and the three-way spectrum, drawn precisely** — the spine claim. On this
   reference's test, the model deciding the decomposition and the order is genuinely new; the
   question of *when your code asks again* (never, on a trigger, or every step) is a second,
   code-owned decision layered on top, argued in full in the mental model above. Draw the boundary
   against the three chapters this one is most often confused with: against
   [2.5 The Agent Loop](../the-unit/the-agent-loop.md) (step-wise reconsult is this chapter's far
   end and 2.5's whole territory — the difference is a matter of degree, not kind, and the chapter
   must say so plainly rather than pretend a bright line exists); against
   [3.3 Orchestrator-Workers](fan-out.md) (the model sizes a *parallel*, independent fan-out — how
   many workers, not what order — while this chapter is *ordered*, sequential steps, one waiting on
   the last); and against [3.7 The Outer Loop](the-outer-loop.md) (a *deterministic* verifier
   wrapped around a whole run, code deciding pass/fail, no model-authored sequence at all — a
   validated plan from this chapter can be the thing 3.7's loop executes and re-verifies, but the
   two are not the same pattern). One live 2026 claim is worth correcting on the page, because it
   is exactly the conflation this item exists to prevent: Gulli & Nawalgaria's public draft
   *Building AI Agents* argues that reasoning models have "collapsed" the interleaved ReAct loop
   into one large planning call followed by a deterministic executor.[^gulli2-ch22] That is not an
   inversion of anything — one planning call plus a deterministic executor is static plan-first, a
   2023 idea (item 2), and what changed is which model performs the planning call, not the shape of
   the trade. *Skip it:* the chapter either bills step-wise reconsult as a distinct, more advanced
   architecture than the agent loop (it is the agent loop), or lets a fashionable, uncited 2026
   claim stand as though explicit planning were obsolete. **n/a** (definitional; the litmus verdict
   is orthogonal to maturity, argued in full below). (Reasoned from this reference's own 1.2 and
   1.3; corrected against Gulli & Nawalgaria, *Building AI Agents* (2026 public draft), ch. 22,
   "What's Next," cited by name as the primary source for the claim being
   corrected.[^gulli2-ch22])

2. **The architecture family, placed on the spectrum, one clause each** — a compact taxonomy so a
   reader can locate any "planning agent" they meet, rather than treating each framework's spelling
   as a new idea. **Plan-and-Solve** (Wang et al., ACL 2023) is the prompting-level root: one call,
   instructed to devise a plan and then carry it out, with no separate execution step at all yet —
   the origin agent frameworks later split into two roles.[^plansolve] **ReWOO** (Xu et al., 2023)
   sits at the static end proper: it fully decouples reasoning from tool observations, planning
   every tool call up front with placeholder variables specifically to avoid the token cost of
   re-prompting after every observation.[^rewoo] **LLMCompiler** (Kim et al., 2023) plans a *DAG*
   rather than a line — a planner emits parallel-and-sequential tool-call structure a task-fetching
   unit dispatches as dependencies clear — and is best read as a bridge toward
   [3.3 Orchestrator-Workers](fan-out.md): once a plan has independent branches, executing it is
   partly this chapter's territory and partly 3.3's.[^llmcompiler] **HuggingGPT** (Shen et al.,
   2023) is a second bridge case, planning a sequence of calls to a *zoo of specialized models*
   rather than a fixed action set — closer to [2.1 Tool Use](../the-unit/tool-use.md)'s tool-
   selection problem wearing a planning hat than a distinct architecture.[^hugginggpt] **ADaPT**
   (Prasad et al., *Findings of ACL: NAACL 2024*) sits at the trigger-based middle: it recursively
   decomposes a subtask into a fresh sub-plan only when the executor fails it, reporting gains of
   up to 28.3 points on ALFWorld, up to 27 on WebShop, and up to 33 on TextCraft over strong
   baselines including flat ReAct and flat plan-and-execute — direct evidence that neither static
   extreme is the general answer.[^adapt] One honesty note that this item exists to state plainly:
   LangGraph's own reference plan-and-execute tutorial, the framework example most readers will
   actually copy, calls its `replan_step` unconditionally after *every* executed step, regardless
   of success — placing the most commonly copied "plan-and-execute" implementation at the step-wise
   end of the spectrum, not the static end its name implies.[^langgraph-replan] *Skip it:* a reader
   meets one framework's "planner/executor" nodes, assumes it demonstrates static plan-first, and
   is wrong about the very property (no reconsultation) that made the pattern worth its own name.
   **Established** (a named, multiply-replicated 2023-2024 research family). (Citations above.)

3. **The selection boundary: when each point on the spectrum actually wins** — the must-cover item
   the first draft of this map omitted, and the one that turns the taxonomy in item 2 into a design
   decision rather than a trivia list. Static plan-first wins when step effects and dependencies are
   knowable well enough in advance that later observations are unlikely to change earlier decisions
   — exactly ReWOO's own motivating case, where decoupling reasoning from observation is a pure
   efficiency win because the observations were not going to change the plan anyway.[^rewoo]
   Trigger-based and step-wise reconsult earn their extra model calls precisely where that
   assumption breaks: AdaPlanner (Sun et al., NeurIPS 2023) was built because "static plans that
   are not adaptable to environmental feedback" cause performance to degrade as task complexity and
   plan horizon grow, and its closed-loop refinement (in-plan and out-of-plan) is the direct
   empirical answer.[^adaplanner] The practical test for a reader building a real system: if you
   can write down, before the first step runs, the conditions under which the plan would need to
   change, you likely have a trigger-based case (check for those conditions, replan only then); if
   you cannot enumerate them because each observation could plausibly redirect the next action, you
   have a step-wise case, and the honest move is to stop calling it "plan-and-execute" and build
   [2.5](../the-unit/the-agent-loop.md)'s loop instead. *Skip it:* a team picks static plan-first by
   default because it is cheaper, meets an environment where step 3's outcome routinely invalidates
   step 5, and gets a confidently wrong plan executed to completion with no mechanism to catch it.
   **Established** (the trade-off itself, argued from citable, replicated research); **n/a** (the
   selection heuristic offered above is reasoned from that research, not itself an external claim).
   (ReWOO;[^rewoo] AdaPlanner.[^adaplanner])

4. **The plan contract and its validation, split into what code can check and what it cannot** —
   the harness half of this chapter, and the stub gloss's own promise ("code that validates a plan
   before anything runs") made precise rather than left to imply more than it can support. Split
   two categories cleanly, because conflating them is the single most consequential mistake a
   reader can make here. **Structural validation** is fully code's job and fully achievable: schema
   conformance (does the plan parse as the typed contract [2.2 Structured
   Output](../the-unit/structured-output.md) defines?), tool/capability existence (does every step
   name a real, registered capability?), dependency acyclicity (does the step graph actually
   terminate?), and a hard step-count and cost budget enforced regardless of what the model would
   prefer. **Semantic verification** — does this plan actually reach the goal, do its steps' stated
   preconditions hold — is categorically different and code alone cannot do it: Kambhampati et al.'s
   LLM-Modulo framework is explicit that a *sound* verifier, external to the LLM, is what closes
   this gap, and that trusting an LLM's own claim that its plan is correct is exactly the failure
   mode this chapter's skeptical read (item 6) documents.[^llm-modulo] Say plainly when no such
   sound verifier exists, which is most real commerce settings — nothing formally checks whether a
   given sequence of listing-pipeline steps is the *right* one — and name the honest fallback: a
   human approval gate on the consequential or irreversible steps a plan names, not a false
   confidence that "validated" means "correct."
   ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md) owns that gate in depth.) A plan step
   also needs more structure than a bare tool name to make this checking possible at all: a stable
   id, an intended outcome (the subgoal it exists to achieve, not merely "call this tool" — the
   distinction LLMCompiler's dependency graph and LLM-Modulo's verifier interface both depend on),
   its declared dependencies, the capability it is admissible to invoke, what counts as completion
   evidence, a status field, and — feeding item 5 directly — a failure-report shape. *Skip it:* a
   plan that names a tool that doesn't exist, loops forever because no budget was ever checked, or
   "passes validation" and ships an incoherent sequence because validation only ever checked shape,
   never reachability. **Standard** (structural validation and bounded execution, an instance of
   general input-validation discipline this reference states elsewhere) for a **harness** whose
   semantic half has **no sound automated default** and routes to a human gate instead. (Kambhampati
   et al., ICML 2024;[^llm-modulo] LLMCompiler;[^llmcompiler] reasoned from item 2's citations.)

5. **Replanning ownership and the failure-return contract, stated once and consistently** — this
   reference's standing rule that a failed step must come back to the model as a structured,
   recoverable message, applied here with one non-negotiable ownership statement: **the model
   authors the original plan and any revised plan it is asked for; code owns validation, execution
   scheduling, the replan trigger itself, the budget, and whether replanning is permitted at all.**
   A model consulted after every ordinary step, success or failure, is the step-wise end of item
   1's spectrum, not a variant of static planning wearing a different name — say this explicitly, it
   is the single most common source of confusion this chapter has to resolve. When a step does
   fail, the executor packages the failure as a specific, structured report (which step, which
   check, what the observed state was) rather than an opaque "failed," so a replan call — if code's
   trigger logic decides one is warranted — has something to act on. Two decisions belong in code,
   made once, deliberately, not discovered at the moment a cap is hit: whether a failed step
   triggers a full replan (expensive, recovers from a structurally wrong plan) or a local retry of
   just that step (cheap, cannot fix a bad plan); and what happens when replanning itself does not
   converge — escalate to a person ([4.3](../craft/human-in-the-loop.md)), fail closed, or ship the
   best partial result. A carrier-consistent illustration of a structured failure report, described
   qualitatively rather than with an invented number (per this reference's own rule that
   quantitative specifics come from the companion code, never imagination): a pricing step in a
   sequential plan reports back "step 4, price-check: proposed `price_cents` falls below the MAP
   floor," not a raw exception — MAP is a minimum advertised price, so the violation to guard
   against is undercutting it, not exceeding it. *Skip it:* a step failure either crashes the whole
   run or is silently swallowed and the plan limps forward on stale assumptions, the general
   silent-failure anti-pattern this reference already names. **Standard** (the failure-return-
   contract discipline itself, argued from this reference's own 3.1/3.3/3.4 precedent) applied to a
   family that is Established. (LangGraph plan-and-execute tutorial, for the shape of a replan step
   done honestly;[^langgraph-replan] this reference's own prior chapters.)

6. **The skeptical read: autonomous planning correctness is not established, and the constructive
   answer is external verification, not abandonment** — the finding that keeps this pattern's
   maturity from being a flat "Established," and the citation that carries the Contested half of
   the verdict below. Valmeekam, Marquez, Sreedharan & Kambhampati's "Critical Investigation" found
   GPT-4 generated fully executable, correct plans autonomously in an average of roughly 12% of
   cases across the paper's tested classical-planning domains and prompting setup — a benchmark-
   specific figure, not a universal rate for "how often LLMs can plan," and the chapter must state
   it with that qualification every time.[^critical-investigation] The same paper reports markedly
   better results in an "LLM-Modulo" setting, where an external verifier checks the model's proposed
   plan rather than trusting it outright — the direct empirical link to item 4's validation
   argument.[^critical-investigation] PlanBench (Valmeekam et al., NeurIPS 2023 Datasets and
   Benchmarks track) is the extensible benchmark suite this and related papers build on, designed
   specifically to distinguish genuine planning from retrieval of memorized, planning-flavored
   text.[^planbench] Kambhampati et al.'s "LLM-Modulo Frameworks" (ICML 2024, spotlight) is the
   constructive half this deflation needs, per this reference's own rule that a deflation is always
   followed by the constructive answer on the same page: autoregressive LLMs cannot, by themselves,
   reliably plan or self-verify their own plans, but are genuinely useful *inside* a framework where
   a sound, external verifier checks and critiques what the LLM proposes.[^llm-modulo] *Skip it:*
   the chapter's other items read as endorsing "give the model a goal and let it plan," which the
   strongest available evidence says fails on its own far more often than a production system can
   tolerate. **Contested** (autonomous, unscaffolded planning correctness, as a technique to trust
   without external checking) inside a pattern whose validated-execution half is Standard/Emerging
   per the maturity summary below. (Valmeekam et al.;[^critical-investigation] Valmeekam et al.,
   NeurIPS 2023;[^planbench] Kambhampati et al., ICML 2024.[^llm-modulo])

7. **Security: OWASP's Agent Goal Hijack (ASI01), and an honest read of its own flagship example**
   — the OWASP GenAI Security Project's "Top 10 for Agentic Applications" (announced 2025-12-09) is
   the field's first dedicated agentic-risk taxonomy, and this chapter is the natural owner of its
   first-ranked risk: ASI01, Agent Goal Hijack, an attacker redirecting an agent's objective through
   content it reads rather than code it runs.[^owasp-asi] OWASP's own announcement names *EchoLeak*
   (CVE-2025-32711, a zero-click prompt-injection vulnerability in Microsoft 365 Copilot disclosed
   by Aim Security in 2025) as its illustrative ASI01 case, and the chapter must engage with that
   naming rather than claim no incident exists.[^owasp-asi][^echoleak] An honest read, though: the
   published EchoLeak exploit chain is a single-turn hijack — a hidden instruction causes one
   response to embed exfiltrated data in an auto-fetched image URL — with no evidence a multi-step
   *plan* was rewritten in the way this chapter is about; it is a purer instance of the general
   prompt-injection-to-exfiltration chain [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md)
   owns (untrusted content, a tool with private data, an exfiltration channel — the lethal
   trifecta), not a planner-hijacking case. This chapter's narrower, planning-specific instance of
   ASI01 is the one OWASP's own defenses target directly and that a multi-step plan uniquely
   exposes: an injected instruction that reaches the *planner* rewrites every subsequent step, so
   one poisoned input corrupts an entire remaining sequence rather than one call's output. Name
   EchoLeak, credit it to 4.6 as the general case, and state the narrower planning case explicitly.
   The published defenses — hard caps on autonomous loops, plan-validation checkpoints, and
   approval gates on irreversible actions — are items 4 and 5's controls restated from the security
   side.[^owasp-asi] *Skip it:* a reader treats "the model wrote a bad plan" and "an attacker
   rewrote the model's goal" as the same failure with the same fix, or assumes this chapter owns an
   incident (EchoLeak) that in fact belongs to a sibling chapter. **Standard** (treating planner
   input as untrusted, capping autonomous loops, gating irreversible actions) applied to a **newly
   named, Emerging** taxonomy entry, roughly nine months old at this writing. (OWASP GenAI Security
   Project, "Top 10 for Agentic Applications," 2025-12-09;[^owasp-asi] EchoLeak / CVE-2025-32711
   disclosure.[^echoleak])

## Mention-and-link (one line, a pointer, not a section)

- **The step-by-step loop this chapter contrasts against**, and the far end of item 1's spectrum
  (ReAct-style, implicit continuous replanning, no separate plan artifact) →
  [2.5 The Agent Loop](../the-unit/the-agent-loop.md). Heaviest link in the chapter given item 1.
- **The deterministic verify-and-retry loop** a validated plan's execution can be wrapped in;
  termination conditions and futility detection in full → [3.7 The Outer
  Loop](the-outer-loop.md).
- **Parallel, independent fan-out with a dynamically sized worker count** — this chapter's
  ordered, sequential sibling → [3.3 Orchestrator-Workers](fan-out.md). LLMCompiler's DAG-shaped
  plan (item 2) is the bridge case where 3.6 and 3.3 meet.
- **The agency spectrum** this pattern sits on (a bounded-agency middle point: the model decides
  the plan, code owns the walk) → [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md).
- **The typed contract** a plan and each step's report rely on → [2.2 Structured
  Output](../the-unit/structured-output.md).
- **The approval gate for an irreversible step a plan names** → [4.3
  Human-in-the-Loop](../craft/human-in-the-loop.md).
- **Interactive spec engineering / goal-hardening interrogation** (asking clarifying questions
  before planning, so the plan is built on a well-specified goal rather than a vague one — the
  human half of planning) → [4.1 Prompt Architecture &
  Management](../craft/prompts-are-source-code.md), with a pointer back here.
- **Plan-quality evaluation, separate from end-to-end task success** — end-to-end success cannot
  tell you whether a failure came from decomposition, execution, or replanning; a real eval suite
  for this pattern measures plan executability/feasibility, goal attainment, and replan frequency
  or unnecessary-step count as distinct signals, informed by PlanBench's plan-generation framing
  and LLMCompiler's own separate accuracy/latency/cost reporting.[^planbench][^llmcompiler] Named
  here in one clause, taught in full → [4.2 Evaluation](../craft/proving-it-works.md).
- **Chain-of-thought, Tree of Thoughts, and search-based planning (LATS)** as the reasoning-budget
  end of this family, where the "plan" is a search over reasoning paths rather than an executable
  step list → [4.5 Reasoning & Thinking Budgets](../craft/reasoning-and-thinking-budgets.md). Named
  here, taught there.
- **The plan as a piece of state the agent must persist and re-consult**, not a transcript — the
  general principle this chapter's plan artifact is one instance of → [5.1 State, Not
  Memory](../knowledge/state-not-memory.md).
- **What crosses forward into each step's context as the plan is walked** (curate, don't carry
  the whole transcript) → [5.4 Compaction](../knowledge/compaction-and-the-window.md).
- **The repricer's full autonomous loop in depth** — this chapter's carrier illustration, treated
  at long-horizon scale → [9.1 Long-Running Agents](../frontier/when-you-want-autonomy.md).
- **Framework mechanics** (LangGraph's planner/executor/replanner notebook; Google ADK's
  `PlanReActPlanner`/`BuiltInPlanner`) — verified against current docs for this map, but demoted
  out of must-cover prose per this reference's own precedent (3.4's map demoted its own framework-
  spellings item the same way): one compact ecosystem paragraph in *How*, plus the Stage-2 code
  brief, carry this, not a numbered must-cover item.
- **Claude Code, Cursor, and Codex plan modes, and ROADMAP-style plan-file operating patterns, in
  full depth** → [9.6 Coding Agents](../frontier/coding-agents.md).
- **The general prompt-injection-to-exfiltration chain** (the lethal trifecta: untrusted content, a
  tool with access to private data, an exfiltration channel), including the EchoLeak incident in
  full → [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md). Item 7 names
  EchoLeak and explains why its full treatment lives there, not here.
- **The Security Posture Map's eventual ASI01 row** should point here once that catalog page is
  built out beyond its current stub → [G. The Security Posture
  Map](../catalogs/security-posture.md).
- **Over-planning and the agent that should have been a script** as anti-patterns → [Anti-Patterns
  Catalog](../catalogs/anti-patterns.md).

## Out of scope (name it, point out)

- Classical AI planning theory (STRIPS/PDDL, HTN planning) beyond what's needed to understand why
  PlanBench's domains are a fair test — cite Kambhampati's own framing, do not teach classical
  planning.
- Tree of Thoughts and LATS's search mechanics (MCTS, value functions, backtracking) in depth →
  [4.5 Reasoning & Thinking Budgets](../craft/reasoning-and-thinking-budgets.md); name them here
  only as the search-based branch of the planning family.
- The full termination-condition and futility-detection framework for a wrapped execution loop →
  [3.7 The Outer Loop](the-outer-loop.md); this chapter names the replan trigger, 3.7 owns the
  general theory.
- Building a custom plan-representation DSL or exact LangGraph/ADK API syntax in depth → vendor
  docs and the Stage-2 code brief; this chapter shows the shape via the multi-provider tabs, not a
  framework tutorial.
- The human-approval mechanism's UI/UX and escalation depth → [4.3
  Human-in-the-Loop](../craft/human-in-the-loop.md).
- Full plan-quality evaluation methodology (metric definitions, measurement protocol) → [4.2
  Evaluation](../craft/proving-it-works.md); this chapter names the metrics in one clause.
- Self-improving loops that rewrite their own planning prompt or strategy (`/grill-me`-style goal
  interrogation as a scaffold-mutation technique, evolutionary planning) → [9.7 Self-Improving
  Systems](../frontier/self-improving-systems.md); this chapter's replanning is within-run, not
  across-run learning.
- The general prompt-injection/exfiltration incident literature, EchoLeak included → [4.6 Prompt
  Injection & the Lethal Trifecta](../craft/prompt-injection.md); this chapter names the narrower
  planner-specific instance only.
- Live leaderboard or framework-version-specific numbers (ADK's exact default iteration counts,
  any coding agent's exact version history) — cite the mechanism and the live source, never a
  frozen snapshot.

## Maturity summary

- **Standard:** structural plan validation before execution (schema, tool existence, dependency
  acyclicity, a hard step and cost budget) and a human approval gate on irreversible steps, both
  instances of general engineering discipline this reference states elsewhere; the failure-return-
  contract discipline applied to a failed plan step.
- **Established:** a model authoring a visible, inspectable plan a human or a piece of code can
  review before anything runs — evidenced by the shipped plan modes in daily coding tools (below)
  and Anthropic's own lead-agent planning step; the 2023-2024 research family (Plan-and-Solve,
  ReWOO, LLMCompiler, HuggingGPT, ADaPT, AdaPlanner) as a named, multiply-replicated set of
  architectures.
- **Emerging:** static plan-first or trigger-based replanning as a common, proven *execution*
  architecture in production — the strongest evidence this sweep found is research papers (2023),
  a widely copied framework tutorial that actually reconsults every step rather than staying static
  (item 2), and human-approval-gated coding tools whose execution phase, once approved, resumes the
  ordinary step-by-step loop rather than walking a fixed plan unattended (item 5's Reader-
  verifiable anchors below); this is real, growing, and short of "documented common use" for the
  execution architecture specifically, distinct from the plan-as-artifact claim above. The OWASP
  Agent Goal Hijack (ASI01) taxonomy entry itself, roughly nine months old at this writing, is
  likewise Emerging.
- **Contested:** unscaffolded, autonomous planning correctness — an LLM generating a fully
  executable, correct plan with no external check — as a technique to trust in production
  (Valmeekam et al.'s ~12% benchmark-specific finding); "reasoning models have made explicit
  planning obsolete" as a 2026 claim (item 1's correction).

**Recommended maturity verdict for the chapter as a whole:** a three-part split, one tier richer
than the two-part precedent [3.3](fan-out.md) and [3.4](evaluator-optimizer.md) used, because the
evidence here genuinely separates into three claims rather than two — **"Standard (structural
validation and a human approval gate) · Emerging (a model-written plan as a common, proven
execution architecture) · Contested (autonomous planning correctness with no external check)."**
The stub's current bare "Established" reads as endorsing "give the model a goal and let it plan,
unattended, in production," which nothing in this sweep's evidence supports; the three-part split
is what keeps the chapter honest about exactly what is proven, what is real but still consolidating,
and what is not proven at all.

## Aliases

True synonyms for this chapter's pattern, each sourced:

- **planning** — Anthropic's "autonomous agents" framing, in which agents "plan and operate
  independently."[^anthropic-bea]
- **plan-and-execute** — LangChain's own term for the agent-framework architecture.[^langchain-plan]
- **planner-executor** — the shared node-role naming this family's frameworks converge on
  independently (LangGraph's `plan_step`/`execute_step`/`replan_step`; Google ADK's Plan → Reason →
  Act → Observe → Replan structure).[^langgraph-replan][^adk-planner]
- **task decomposition** — the term the academic decomposition literature uses for a model choosing
  its own subtask split (Khot et al.'s "Decomposed Prompting" explicitly permits a model-generated,
  recursive decomposition, not a human-fixed one); cited jointly with
  [3.1](prompt-chaining.md)'s own, separate use of the same literature for a different point (there,
  grounding the case for splitting a task into calls at all; here, grounding the case for a model
  choosing that split itself) — cite once, do not claim the two chapters' uses contrast.[^decomposed][^least-to-most]
- **static planning / static plan** — AdaPlanner's own contrasting term for the non-adaptive case
  its paper argues against, a legitimate sourced name for item 1's static end of the
  spectrum.[^adaplanner]

Related ideas, not synonyms — each names something adjacent, sourced, and homed elsewhere or noted
as a correction:

- **prioritization** — Gulli's *Agentic Design Patterns* (2025), ch. 20; a related but distinct
  concept (ordering competing goals, not decomposing one). Verify exact chapter content against the
  print edition before citing further.[^gulli-adp]
- **goal setting** — Gulli's *Agentic Design Patterns*, ch. 11, "Goal Setting & Monitoring"; only
  the goal-specification half is adjacent to this chapter, and it is closer to
  [4.1](../craft/prompts-are-source-code.md)'s territory than this one's.[^gulli-adp]
- **Plan-ReAct** — Google ADK's `PlanReActPlanner` class name for its specific Plan → Reason → Act
  → Observe → Replan structure, a concrete implementation rather than a general synonym for the
  pattern.[^adk-planner]
- **plan mode** — the daily-tool UI feature name (Claude Code, Cursor); names a human-approval
  workflow built around a visible plan, not the execution architecture this chapter is about (see
  Reader-verifiable anchors).[^cc-plan][^cursor-plan]
- **"Reasoning Agents"** — Gulli & Nawalgaria's *Building AI Agents* (2026 draft) framing for what
  item 1 corrects as plan-and-execute under a new name; listed to be corrected, not adopted as a
  synonym.[^gulli2-ch22]
- **interactive spec engineering** — the human half of planning (goal-hardening interrogation
  before a plan is written), homed at [4.1](../craft/prompts-are-source-code.md) with a pointer
  back here.[^gulli2-ch20]

## Reader-verifiable anchors

Both anchors below demonstrate a **visible, human-approved plan artifact**, not this chapter's
execution-architecture spectrum (item 1) directly — a distinction the chapter must state, since
neither tool's post-approval execution phase actually walks a fixed plan unattended; both resume
their ordinary step-by-step tool-calling loop once a human approves.

- **Claude Code's plan mode is a live, checkable restriction, not a description**: entering it
  (`Shift+Tab` twice, or `/plan`) confines the session to read-only tools — Read, Glob, Grep, LS,
  WebSearch, WebFetch, Task, AskUserQuestion — and no edit, write, or command-running tool becomes
  available again until a drafted plan is explicitly approved, which a reader can verify by trying
  to edit a file mid-plan and watching it refuse.[^cc-plan]
- **Cursor's Plan Mode produces an inspectable, editable artifact, not just a description**:
  entering it researches the codebase, asks clarifying questions, and writes an editable Markdown
  plan file a person can revise line by line before any edit runs — a reader can open that file and
  see exactly what the model proposed.[^cursor-plan]

Community reporting describes a comparable read-only planning mode in OpenAI's Codex CLI; this
sweep could not confirm the specific mode names, keybindings, or version number against an OpenAI-
hosted primary source, so it is named here only as a lead for the fact-checker, not cited as a
verified anchor.

## Incidents

**EchoLeak (CVE-2025-32711)**, a zero-click prompt-injection vulnerability in Microsoft 365
Copilot disclosed by Aim Security in 2025, is OWASP's own named illustration of ASI01 Agent Goal
Hijack.[^owasp-asi][^echoleak] As argued in item 7, it is best classified as a general prompt-
injection-to-exfiltration incident (a hidden instruction causing one response to embed exfiltrated
data in an auto-fetched image URL) rather than a planning-specific one — no evidence surfaced this
sweep that a multi-step plan was rewritten. Full treatment belongs to
[4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md); this chapter names it,
attributes it correctly, and states why it is not claimed as its own.

No dedicated, named incident specific to a multi-step *planner* being hijacked (as opposed to a
single-turn response) was found this sweep. The closest evidenced material is the well-documented
AutoGPT/BabyAGI planning-agent failure pattern from 2023: both projects popularized "give an LLM a
goal and let it plan and act autonomously," and independently reported, reproducible causes
followed directly from skipping this chapter's controls — vague, non-measurable goals ("research
X," "improve Y") with no completion criterion; no comparison between a new plan and previously
executed ones, so the agent could not recognize it was repeating itself; and no iteration or cost
cap, so nothing stopped a loop once it started.[^autogpt-failures] Specific reconstructed usage
figures circulating in secondary compilations (multi-hour, multi-hundred-call sessions) trace to a
compiled case-study writeup rather than a linkable original incident report, so this map states the
failure pattern and its documented causes without repeating an unverifiable number.[^autogpt-failures]
A 2026 static-analysis study by Hou, Wang, Zhao & Wang, already cited in this reference's 3.3 and
3.4 coverage maps for the general case, scanned 6,549 public LLM-agent repositories and confirmed
68 real unbounded-loop failures across 47 projects at 91.9% precision — the same failure class,
now measured at scale.[^ial] This material feeds the chapter's Gotchas section directly (an
unbounded or non-converging replanning loop is the same failure whether the goal was vague by
accident or hijacked on purpose).

## Named-idea candidates

1. **"The predictability tax"** — paid in adaptivity: what code buys, and gives up, by fixing a
   plan and only walking it instead of re-consulting the model every step. Directly names item 1's
   spine claim; offered, not forced.

("Reciting the todo list," offered in the first draft of this map, is struck: it names a
state/memory behavior — the model re-reading its own persisted notes — that belongs to
[5.1](../knowledge/state-not-memory.md) or [5.3](../knowledge/real-memory.md), not this chapter's
planning-versus-execution axis.)

## Sources

Vendor/primary: Anthropic, "Building Effective Agents" (2024-12-19) — the "autonomous agents"
definition and the ground-truth/environment-feedback framing.[^anthropic-bea] Anthropic, "How we
built our multi-agent research system" (2025-06-13) — the lead agent's own planning step and its
practice of saving the plan to persistent memory against context truncation.[^anthropic-multiagent]
LangChain, "Plan-and-Execute Agents" (2023-05-10).[^langchain-plan] LangChain/LangGraph,
`plan-and-execute` reference notebook (GitHub, `langchain-ai/langgraph`).[^langgraph-replan] Google,
Agent Development Kit docs — planners (`PlanReActPlanner`, `BuiltInPlanner`).[^adk-planner]
HumanLayer, "12-Factor Agents," Factor 8 ("Own your control flow").[^12factor] Claude Code / Agent
SDK docs, "Choose a permission mode" and "Track todos."[^cc-plan] Cursor, "Introducing Plan Mode"
and Plan Mode docs.[^cursor-plan] Academic: Yao et al., "ReAct," arXiv:2210.03629 (ICLR 2023) — the
step-by-step baseline this chapter contrasts against, already cited in this reference's 2.1 and 3.1
coverage.[^react] Wang et al., "Plan-and-Solve Prompting," arXiv:2305.04091 (ACL
2023).[^plansolve] Xu et al., "ReWOO," arXiv:2305.18323 (2023).[^rewoo] Kim et al., "An LLM
Compiler for Parallel Function Calling," arXiv:2312.04511 (2023, revised 2024).[^llmcompiler] Shen
et al., "HuggingGPT," arXiv:2303.17580 (2023).[^hugginggpt] Prasad et al., "ADaPT: As-Needed
Decomposition and Planning with Language Models," *Findings of the Association for Computational
Linguistics: NAACL 2024*, pp. 4226-4252.[^adapt] Sun et al., "AdaPlanner: Adaptive Planning from
Feedback with Language Models," arXiv:2305.16653 (NeurIPS 2023).[^adaplanner] Zhou et al., "Least-
to-Most Prompting," arXiv:2205.10625, shared with 3.1.[^least-to-most] Khot et al., "Decomposed
Prompting," arXiv:2210.02406.[^decomposed] Valmeekam, Marquez, Sreedharan & Kambhampati, "On the
Planning Abilities of Large Language Models: A Critical Investigation," arXiv:2305.15771
(2023).[^critical-investigation] Valmeekam et al., "PlanBench," arXiv:2206.10498 (NeurIPS 2023 D&B
track).[^planbench] Kambhampati et al., "LLMs Can't Plan, But Can Help Planning in LLM-Modulo
Frameworks," arXiv:2402.01817 (ICML 2024).[^llm-modulo] Hou, Wang, Zhao & Wang, "When Agents Do Not
Stop: Uncovering Infinite Agentic Loops in LLM Agents," arXiv:2607.01641 (2026), shared with 3.3
and 3.4.[^ial] Security: OWASP GenAI Security Project, "Top 10 for Agentic Applications"
(2025-12-09), ASI01 Agent Goal Hijack, naming EchoLeak.[^owasp-asi] EchoLeak / CVE-2025-32711
disclosure reporting (Aim Security, 2025).[^echoleak] Practitioner: AutoGPT/BabyAGI planning-
failure documentation, a maintained case-study collection and contemporary GitHub issue
reports.[^autogpt-failures] Competitor read (leads only, never quoted as a citation): Gulli &
Nawalgaria, *Building AI Agents* (2026 public draft), chs. 1, 11, 20, 22.[^gulli2-ch20][^gulli2-ch11][^gulli2-ch22]
Internal: this reference's own [1.2](../foundations/who-decides.md),
[1.3](../foundations/workflow-or-agent.md), and 3.1/3.3/3.4 coverage maps, for the litmus, spectrum,
and two-verdict-lens precedent this map draws on and extends to three tiers.

> **Verify before quoting:** every plan-mode keybinding, default tool set, and mode name for Claude
> Code and Cursor (Reader-verifiable anchors) is on an actively developed product and should be
> re-checked against the live docs immediately before the chapter ships — this sweep found Claude
> Code's task-tracking tools are, as of this writing, opt-in rather than default on the newest
> model families, a detail easy to get stale. ADK's `PlanReActPlanner`/`BuiltInPlanner` class names
> and defaults should get the same re-check; this sweep confirmed them via search-summarized
> documentation, not a direct fetch of the current API reference page, and they sit in an actively
> developed framework. The exact current URL for LangGraph's plan-and-execute notebook should be
> re-confirmed immediately before the chapter ships — this material has already moved and been
> re-consolidated at least once, and the citation here points to the `main`-branch example path,
> which can move again. The LLMCompiler latency/cost multipliers and ADaPT's percentage-point gains
> are each paper's own reported benchmark results, not a vendor-measured production snapshot; cite
> them as "reported in the paper," not as a general expectation. Valmeekam et al.'s ~12% figure is
> specific to the paper's chosen classical-planning domains and prompting setup; cite the finding
> and the qualification, never the number as a universal rate. The OWASP Top 10 for Agentic
> Applications is roughly nine months old at this writing and under active revision; re-verify the
> exact ASI01 wording and ranking, and the EchoLeak characterization, against the canonical document
> (not a third-party summary) before the chapter ships. No OpenAI-hosted primary source for Codex
> CLI's planning-mode behavior was confirmed this sweep; do not cite specific mode names or version
> numbers for it without one.

## Sweep angles run and skipped

- **Vendor/primary docs — ran fully.** Anthropic's two posts (fetched directly, not from memory);
  LangChain's original post and its GitHub reference notebook; Google ADK's planner docs; Claude
  Code's and Cursor's plan-mode documentation, each checked live for the Reader-verifiable anchors.
  Codex CLI's plan-mode behavior was checked but could not be pinned to an OpenAI-hosted primary
  source; flagged rather than cited.
- **Academic + benchmarks — ran fully, and extended in a second-reviewer pass.** The founding
  architecture family (Plan-and-Solve, ReWOO, LLMCompiler, HuggingGPT, ADaPT) and the skeptical-
  read cluster (the Critical Investigation, PlanBench, LLM-Modulo) each verified directly against
  arXiv or the paper's own venue record. AdaPlanner (arXiv:2305.16653) was added in the
  second-reviewer pass as the citation that carries item 3's selection-boundary argument. Tree of
  Thoughts and LATS were verified but judged out of scope for depth (→ 4.5).
- **Security / failure modes — ran, and it is a full must-cover item (7), corrected in a
  second-reviewer pass.** OWASP's "Top 10 for Agentic Applications" (2025-12-09) was fetched from
  its own announcement page directly; a second-reviewer pass caught that the same announcement
  names EchoLeak as its ASI01 illustration, which the first draft had missed, stating "no dedicated
  incident found" incorrectly. EchoLeak was then independently verified (CVE-2025-32711, Aim
  Security) and assessed on the merits as belonging primarily to 4.6, not this chapter.
- **Practitioner writeups — ran.** LangChain's original post functions as a first-party
  practitioner account of the agent-framework architecture; the AutoGPT/BabyAGI failure
  documentation is practitioner-level evidence, named honestly as such, with an invented usage
  figure from the first draft removed in the second-reviewer pass once its source could not be
  traced to a linkable original report.
- **The skeptical read — ran, and it is the chapter's most load-bearing item (6) alongside item 1.**
  The Kambhampati-group papers were read directly, not inherited from a secondary source, given how
  load-bearing the ~12% finding is for the maturity verdict; the second-reviewer pass confirmed
  this figure was already correctly qualified as benchmark-specific in the first draft.
- **The alias sweep — ran**, using the neighbouring canon (Anthropic, Gulli's two books, Google
  ADK, LangChain, 12-Factor Agents) as lead sources, then verifying or independently sourcing each
  name before it reached this map. A second-reviewer pass split the result into true synonyms and
  related-but-distinct ideas, since the first draft had listed several related concepts (goal
  setting, prioritization, plan mode) as if they were synonyms.
- **The everyday-engineer angle — ran, lightly.** The AutoGPT/BabyAGI GitHub-issue material doubles
  as the everyday-engineer angle: the specific, reproducible mistakes (vague goals, no progress
  comparison, no cap) are exactly what a first-time builder of a planning agent still gets wrong.
- **The daily-tool angle — ran.** Claude Code's and Cursor's plan modes were checked against their
  current documentation; a second-reviewer pass corrected the first draft's framing of what these
  anchors actually demonstrate (a visible, approved plan artifact, not this chapter's no-reconsult
  execution architecture), and removed an unverified claim about Codex CLI's specific mode
  taxonomy.
- **Incidents — ran**, and the second-reviewer pass corrected a real gap: the first draft's "no
  incident found" line was wrong given OWASP's own EchoLeak example, now addressed directly above.

## Second-reviewer pass (Codex, 2026-09-05)

A second reviewer (OpenAI Codex) read the first draft of this map. Each finding below was verified
against primary sources, not accepted on say-so; disposition and reasoning follow.

1. **Replan ownership inconsistency (BLOCKER).** **ACCEPTED.** The first draft had the model
   deciding "when to replan" in item 1 while item 3 assigned that decision to code, and cited
   LangGraph's tutorial (which replans after every step) as support for a static, no-reconsult
   architecture. Fixed throughout: the model authors plans and revisions; code owns the trigger,
   scheduling, budget, and whether replanning is permitted; the three-way spectrum (static /
   trigger-based / step-wise) now makes the LangGraph tutorial's actual behavior an honest example
   of the step-wise end, not a counterexample smuggled in as the static case.
2. **Structural vs. semantic validation conflated (BLOCKER).** **ACCEPTED.** Verified directly
   against Kambhampati et al., ICML 2024: the paper is explicit that a sound external verifier, not
   structural checking, is what LLM-Modulo adds. Item 4 now splits the two categories and states
   plainly that no sound automated verifier exists for most real settings, routing to a human gate.
3. **Architecture family contradicts the chapter's own definition (BLOCKER).** **ACCEPTED.** Fixed
   by replacing the five-name catalogue's flat framing with the three-way spectrum from item 1 as
   the organizer; ADaPT and the LangGraph tutorial are now placed honestly (trigger-based and
   step-wise respectively) rather than folded into an undifferentiated "the family."
4. **MAP logic reversed; invented $12 figure (BLOCKER).** **ACCEPTED.** MAP is a floor; the
   violation is undercutting it, not exceeding it. Fixed in item 5's carrier illustration, and the
   invented dollar amount was removed per this reference's own rule that numbers come from the
   companion code, never imagination.
5. **Missing selection-boundary item (MAJOR).** **ACCEPTED.** Added as item 3, carried by ReWOO's
   own efficiency motivation and AdaPlanner (Sun et al., NeurIPS 2023, arXiv:2305.16653), a paper
   the first draft's sweep missed and this pass verified directly.
6. **Missing plan-quality evaluation (MAJOR).** **PARTIAL.** The underlying point is right, but per
   this reference's own precedent for keeping a standard-pattern chapter from bloating (3.4's map
   demoted its own comparable item the same way), this is added as a Mention-and-link to
   [4.2 Evaluation](../craft/proving-it-works.md) naming plan executability, goal attainment, and
   replan frequency as the three distinguishing metrics, not as an eighth full must-cover item.
7. **Underspecified plan-step contract (MAJOR).** **ACCEPTED.** Folded into item 4: a step now
   needs a stable id, an intended outcome distinct from a bare tool call, declared dependencies,
   an admissible capability, completion evidence, a status field, and a failure-report shape.
8. **List bloat across items 2, 6, 7, 8, 9 (MAJOR).** **ACCEPTED.** The must-cover list is
   restructured from nine items to seven: the Gulli correction folded into item 1 (one paragraph,
   not a standalone item); the AutoGPT/BabyAGI history moved to Incidents (feeding the chapter's
   Gotchas, not a must-cover item); framework/daily-tool mechanics demoted to a Mention-and-link
   plus the Reader-verifiable anchors, per 3.4's own precedent for the same move; LLMCompiler and
   HuggingGPT are now explicitly framed as bridge cases in item 2, not co-equal architectures.
9. **"Established" too generous (MAJOR).** **ACCEPTED, with a refinement.** Re-derived from the
   citations actually in hand: the evidence supports "Established" for a model authoring a visible,
   inspectable plan (daily tools, Anthropic's lead agent), but only "Emerging" for static or
   trigger-based execution as a common, proven production architecture, since the most-copied
   reference implementation (LangGraph's tutorial) turns out to be step-wise, and the plan-mode
   tools' execution phase resumes the ordinary agent loop rather than walking a fixed plan
   unattended. Landed on a three-part split (Standard / Emerging / Contested) rather than the
   reviewer's flat "Emerging" recommendation, because the evidence genuinely separates into three
   distinct claims — see the Maturity summary for the full argument.
10. **Citation errors (MAJOR), seven sub-findings.** **ACCEPTED, all seven**, each independently
    re-verified this pass: Least-to-Most and Decomposed Prompting are model-generated, not
    code-fixed, decompositions (the false contrast is removed; the shared citation with 3.1 is kept
    but reframed); ADaPT is now cited as Prasad et al., *Findings of ACL: NAACL 2024*, pp. 4226-4252,
    with "up to" 28.3/27/33-point gains, not a flat universal claim; the LangGraph footnote now
    points to the actual GitHub reference notebook (`langchain-ai/langgraph`,
    `examples/plan-and-execute/plan-and-execute.ipynb`), whose `plan_step`/`execute_step`/
    `replan_step`/`should_end` functions were read directly to confirm the per-step replan
    behavior; the Codex CLI Plan/Pair/Execute claim is removed as a cited anchor (kept only as an
    unverified, uncredited lead); the AutoGPT "300+ calls over two hours" figure is removed and the
    failure pattern is described without an unverifiable number; "When Agents Do Not Stop" now
    credits Hou, Wang, Zhao & Wang, with the 6,549/68/47/91.9% figures re-confirmed against the
    abstract; the Valmeekam ~12% figure's qualification is kept as already correct (this
    sub-finding noted the first draft got it right).
11. **Aliases mostly not synonyms.** **ACCEPTED.** The Aliases section is now split into true
    synonyms (planning, plan-and-execute, planner-executor, task decomposition, static planning —
    the last newly sourced from AdaPlanner's own contrasting term) and a separate "related ideas,
    not synonyms" list (prioritization, goal setting, Plan-ReAct, plan mode, "Reasoning Agents,"
    interactive spec engineering). "Reciting the todo list" is struck as a named-idea candidate;
    "the predictability tax" is kept with its taxed dimension (adaptivity) stated explicitly.
12. **Anchor framing and the missed EchoLeak incident.** **ACCEPTED.** The Reader-verifiable
    anchors now state explicitly that both tools demonstrate a visible, approved plan artifact, not
    this chapter's no-reconsult execution semantics. EchoLeak is now named and assessed on the
    merits in both item 7 and Incidents, rather than the first draft's incorrect "none found."
13. **Thesis absolutism; editorial-process wording in the map body; unestablished carrier architecture claim
    (MINOR).** **ACCEPTED, all three.** The thesis no longer claims execution proceeds "without
    asking again"; it now says code decides "when, if ever, to ask again," with the reviewer's own
    alternative kept as a listed option. Process fingerprints naming this reference's own
    editorial workflow are removed from the map body; "origin-set
    four" is kept, since it is public vocabulary already used in this reference's own shipped
    coverage maps (3.3, 3.4). The Repricer carrier note is corrected in Open questions below: the
    carrier bible does not yet specify which point on this chapter's spectrum the Repricer actually
    uses, and that gap is now a proposed one-line carrier-bible amendment for the author rather than
    an assumed fact.

## Orchestrator rulings (Stage 1.6, 2026-09-07)

Settled so the chapter could be written; reversible at PR review.

1. **Thesis: adopted as recommended** — *"Plan-and-execute lets the model write the sequence once
   and your code decide when, if ever, to ask again, trading the step-by-step loop's adaptivity
   for a plan your code can validate and budget before anything runs, and risking a bad plan
   staying frozen for however long that trigger takes to fire."* The "when, if ever" is
   load-bearing: it is what makes replanning a code-owned trigger rather than a model whim, and it
   is the correction the second reviewer forced.
2. **Budget row: standard pattern (~2,000-2,800 prose words).** Easier to hold at seven must-cover
   items than at the first draft's nine.
3. **Maturity: the three-part split, adopted** — "Standard (structural validation, human approval
   gate) · Emerging (a model-written plan as a common, proven execution architecture) · Contested
   (autonomous planning correctness with no external check)." Richer than 3.3/3.4's two-part
   precedent because the evidence genuinely separates into three claims, and collapsing it would
   force one of them into a tier its sources do not support.
4. **Security becomes a named section**, not a Gotchas bullet, on the [3.3](fan-out.md) precedent.
   Item 7 carries enough weight to earn the controlled-menu "Security & trust" slot.
5. **EchoLeak framing: the narrow split, adopted.** Named here, credited primarily to 4.6, with
   only the planner-hijack case claimed by this chapter.
6. **Codex CLI plan mode: cite a primary source or cut the mention.** No OpenAI-hosted primary
   source was found this sweep, only third-party reporting. The fact-checker resolves this at
   Stage 4; absent a primary source the chapter does not name Codex CLI's mode taxonomy at all.

## Author-only questions (Stage 1.6 — shipped at the default, author rules at the PR)

1. **The proposed `carrier-bible.md` §5 amendment.** The bible does not say *where on this
   chapter's spectrum* the Repricer sits. Proposed line: *"The Repricer plans a review cycle's
   price adjustments up front and only re-consults the model when a competitor move or a guardrail
   breach triggers a replan — a trigger-based case, not a step-wise loop."*
   - *Default shipped:* **the bible is not edited.** The chapter uses the Repricer only for what
     §5 already specifies, and illustrates the spectrum's three points without asserting which one
     the Repricer occupies. If the author accepts the amendment, the carrier illustration tightens
     in a follow-up edit.
2. **Named idea: "the predictability tax"** (what a frozen plan pays in adaptivity).
   - *Default shipped:* **struck.** The idea is argued in prose without a branded name.
3. **"From production." callout.**
   - *Default shipped:* **none.** Grounding reads `companion repo + research`.
4. **1.2's "four tells" list is stale.** [1.2 Who Decides?](../foundations/who-decides.md) still
   says "There are four tells," which predates the ruling that the genuinely-new four are an
   origin set rather than a census — and planning is one of the things that passes the litmus on
   its own page. This chapter makes that inconsistency visible.
   - *Default shipped:* **1.2 is not edited.** Flagged for the already-queued litmus-page revision,
     which 2.5 and 3.7 will also press on.

[^anthropic-bea]: Anthropic, "Building Effective Agents" (2024-12-19). "Agents begin their work
with either a command from, or interactive discussion with, the human user. Once the task is
clear, agents plan and operate independently," gaining "'ground truth' from the environment at
each step (such as tool call results or code execution) to assess its progress." Contrasted with
workflows, "systems where LLMs and tools are orchestrated through predefined code paths."
<https://www.anthropic.com/research/building-effective-agents>
[^anthropic-multiagent]: Anthropic, "How we built our multi-agent research system" (2025-06-13).
The lead agent decomposes a query into subtasks and describes them to subagents; it begins by
"thinking through the approach and saving its plan to Memory to persist the context," since
exceeding the context window truncates the run and the plan must survive that.
<https://www.anthropic.com/engineering/multi-agent-research-system>
[^langchain-plan]: LangChain, "Plan-and-Execute Agents" (2023-05-10). Introduces the agent-
framework architecture as "heavily inspired by … BabyAGI and the recent Plan-and-Solve paper,"
"great for more complex long term planning, at the cost of more calls to the language model."
<https://www.langchain.com/blog/plan-and-execute-agents>
[^langgraph-replan]: LangChain/LangGraph, `plan-and-execute` reference notebook
(`langchain-ai/langgraph`, `examples/plan-and-execute/plan-and-execute.ipynb`). Defines `Plan` and
`Response` typed models, a `plan_step`, `execute_step`, and `replan_step`; the graph's edge from
`agent` (execute) to `replan` is unconditional, so `replan_step` runs after every single executed
step and decides whether to emit a final `Response` or a revised `Plan` — confirmed by reading the
functions directly, not inferred from the tutorial's name. Verify the current path against the
`main` branch before the chapter ships; this material has moved and been re-consolidated before.
<https://github.com/langchain-ai/langgraph/blob/main/examples/plan-and-execute/plan-and-execute.ipynb>
[^adk-planner]: Google, Agent Development Kit docs. `PlanReActPlanner`: constrains a model with no
native thinking support to emit a plan before any action, following Plan → Reason → Act → Observe
→ Replan. `BuiltInPlanner`: leans on a model's native extended-thinking support (Claude, Gemini
2.0+) instead. Verify current class names and defaults against google.github.io/adk-docs before
quoting; this is an actively developed framework, and this citation was confirmed via
search-summarized documentation, not a direct fetch of the current API reference.
<https://google.github.io/adk-docs/>
[^12factor]: HumanLayer, "12-Factor Agents," Factor 8, "Own your control flow." Recommends
implementing looping, retrying, and halting conditions in code rather than trusting the model to
self-regulate, to prevent runaway behavior and context-window overflow.
<https://github.com/humanlayer/12-factor-agents>
[^cc-plan]: Claude Code / Agent SDK docs, "Choose a permission mode" and "Track todos." Plan mode
(`Shift+Tab` twice, or `/plan`) restricts the session to read-only tools (Read, Glob, Grep, LS,
WebSearch, WebFetch, Task, AskUserQuestion) until a drafted plan is approved; approval resumes the
session's ordinary tool-calling loop rather than executing a fixed, unattended sequence. The
task-tracking tools (`TodoWrite`/`TaskCreate`/`TaskUpdate`) that let a session keep and update a
written todo list are, as of this writing, opt-in rather than default on the newest model families;
verify current defaults before quoting. <https://code.claude.com/docs/en/permission-modes>,
<https://code.claude.com/docs/en/agent-sdk/todo-tracking>
[^cursor-plan]: Cursor, "Introducing Plan Mode" and Plan Mode docs. Researches the codebase, asks
clarifying questions, and produces an editable Markdown plan file before any edit runs; entered
with `Shift+Tab`. Approving the plan resumes normal agent execution rather than an unattended,
fixed walk. <https://cursor.com/blog/plan-mode>, <https://cursor.com/docs/agent/plan-mode>
[^react]: Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," arXiv:2210.03629
(ICLR 2023). The step-by-step baseline this chapter contrasts plan-and-execute against; already
cited in this reference's 2.1 and 3.1 coverage. <https://arxiv.org/abs/2210.03629>
[^plansolve]: Wang, L. et al., "Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought
Reasoning by Large Language Models" (ACL 2023). Devise a plan dividing the task into subtasks,
then carry out the subtasks per the plan, in a single generation, addressing Zero-shot-CoT's
missing-step errors. <https://arxiv.org/abs/2305.04091>
[^rewoo]: Xu, B. et al., "ReWOO: Decoupling Reasoning from Observations for Efficient Augmented
Language Models" (2023). Plans all tool calls up front with placeholder variables rather than
interleaving reasoning and observation, reducing token consumption relative to ReAct-style loops.
<https://arxiv.org/abs/2305.18323>
[^llmcompiler]: Kim, S. et al., "An LLM Compiler for Parallel Function Calling" (2023, revised
2024). A Function Calling Planner emits an execution plan (a DAG of tool calls); a Task Fetching
Unit dispatches ready tasks; an Executor runs them. Reports latency speedup up to 3.7x and cost
savings up to 6.7x versus ReAct on the paper's benchmark tasks, with an accuracy improvement of
roughly 9%. <https://arxiv.org/abs/2312.04511>
[^hugginggpt]: Shen, Y. et al., "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in
Hugging Face" (2023). An LLM as controller performs task planning over a zoo of specialized
models, selecting which to invoke and in what order. <https://arxiv.org/abs/2303.17580>
[^adapt]: Prasad, A., Koller, A., Hartmann, M., Clark, P., Sabharwal, A., Bansal, M., Khot, T.,
"ADaPT: As-Needed Decomposition and Planning with Language Models," *Findings of the Association
for Computational Linguistics: NAACL 2024*, pp. 4226-4252. Recursively decomposes a subtask into a
fresh sub-plan only when the executor fails it, reporting success-rate gains of up to 28.3
percentage points on ALFWorld, up to 27 on WebShop, and up to 33 on TextCraft over strong
baselines including ReAct and flat plan-and-execute. <https://arxiv.org/abs/2311.05772>,
<https://aclanthology.org/2024.findings-naacl.264/>
[^adaplanner]: Sun, H., Zhuang, Y., Kong, L., Dai, B., Zhang, C., "AdaPlanner: Adaptive Planning
from Feedback with Language Models" (NeurIPS 2023). Argues "static plans that are not adaptable to
environmental feedback" degrade LLM agent performance as task complexity and plan horizon grow;
proposes closed-loop in-plan and out-of-plan refinement, reported to outperform baselines by 3.73%
and 4.11% on ALFWorld and MiniWoB++ respectively while using markedly fewer samples.
<https://arxiv.org/abs/2305.16653>
[^least-to-most]: Zhou, D. et al., "Least-to-Most Prompting Enables Complex Reasoning in Large
Language Models," arXiv:2205.10625. A model-generated decomposition into sequentially solved
subproblems; cited jointly with this reference's 3.1 coverage map, which uses the same paper for a
different point. <https://arxiv.org/abs/2205.10625>
[^decomposed]: Khot, T. et al., "Decomposed Prompting: A Modular Approach for Solving Complex
Tasks" (2022, revised 2023). Decomposes a complex task into simpler sub-tasks via a decomposer
prompt, delegated to a library of prompting-based LLM handlers; explicitly supports recursive
decomposition when a sub-task itself needs further splitting. <https://arxiv.org/abs/2210.02406>
[^critical-investigation]: Valmeekam, K., Marquez, M., Sreedharan, S., Kambhampati, S., "On the
Planning Abilities of Large Language Models: A Critical Investigation" (2023). GPT-4 generated
fully executable, correct plans autonomously in an average of roughly 12% of cases across the
paper's classical-planning domains and prompting setup, a benchmark-specific figure; performance
improves markedly in an "LLM-Modulo" setting with external verification.
<https://arxiv.org/abs/2305.15771>
[^planbench]: Valmeekam, K., Marquez, M., Olmo, A., Sreedharan, S., Kambhampati, S., "PlanBench: An
Extensible Benchmark for Evaluating Large Language Models on Planning and Reasoning about Change"
(NeurIPS 2023, Datasets and Benchmarks Track). An extensible benchmark suite built from classical-
planning domains, designed to distinguish genuine planning from retrieval of memorized,
planning-flavored text. <https://arxiv.org/abs/2206.10498>
[^llm-modulo]: Kambhampati, S. et al., "LLMs Can't Plan, But Can Help Planning in LLM-Modulo
Frameworks" (ICML 2024, spotlight). Argues autoregressive LLMs cannot, by themselves, reliably
plan or self-verify; a sound, external verifier is what a valid LLM-Modulo framework adds, distinct
from structural or syntactic checking. <https://arxiv.org/abs/2402.01817>
[^ial]: Hou, X., Wang, S., Zhao, Y., Wang, H., "When Agents Do Not Stop: Uncovering Infinite
Agentic Loops in LLM Agents" (2026). Static analysis across 6,549 public LLM-agent repositories;
manual review confirms 68 real unbounded-loop (IAL) failures across 47 projects, 91.9% precision.
Shared citation with this reference's 3.3 and 3.4 coverage maps. <https://arxiv.org/abs/2607.01641>
[^owasp-asi]: OWASP GenAI Security Project, Agentic Security Initiative, "OWASP Top 10 for Agentic
Applications" (announced 2025-12-09). Ten risk categories, ASI01 through ASI10; ASI01, Agent Goal
Hijack, is defined as an attacker redirecting an agent's objective through content it reads rather
than code it runs, and the announcement names EchoLeak by name as its illustration ("Hidden
prompts turned copilots into silent exfiltration engines"). Named defenses include hard caps on
autonomous loops, plan-validation checkpoints, and approval gates on irreversible actions.
Re-verify exact wording and ranking against the canonical document before quoting; this taxonomy is
new and under active revision.
<https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/>
[^echoleak]: EchoLeak, CVE-2025-32711: a zero-click prompt-injection vulnerability in Microsoft 365
Copilot disclosed by Aim Security (2025), chaining an indirect prompt injection (a hidden
instruction in an email) with an auto-fetched image URL to exfiltrate internal data with no user
interaction. Cite the disclosure and Microsoft's confirmation that the specific vulnerability was
patched server-side with no known in-the-wild exploitation; treat vendor and press writeups as
secondary corroboration, not a formal incident report. Verify current characterization against
Microsoft's own advisory before quoting further.
[^autogpt-failures]: AutoGPT and BabyAGI (2023) planning-agent failure documentation, including the
`vectara/awesome-agent-failures` maintained case-study collection and contemporary GitHub issue
reports. Documented causes: vague, non-measurable goals; no comparison of a new plan against
previously executed ones; no iteration or cost cap. Practitioner-level evidence, not a formal
vendor postmortem; specific reconstructed usage figures in secondary compilations are not repeated
here as they could not be traced to a linkable original report.
<https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/autogpt-planning-failures.md>
[^gulli-adp]: Antonio Gulli, *Agentic Design Patterns: A Hands-On Guide to Building Intelligent
Systems* (Springer Nature, 2025; ISBN 9783032014016). Ch. 6, "Planning"; ch. 20, "Prioritization";
ch. 11, "Goal Setting & Monitoring" (planning-adjacent half only). Free draft circulated by the
author; verify exact wording and chapter numbering against the print edition before quoting, per
this reference's standing caution on this source.
<https://link.springer.com/book/10.1007/978-3-032-01402-3>
[^gulli2-ch20]: Gulli, A. & Nawalgaria, *Building AI Agents: From Design Patterns to Production*
(2026 public draft), ch. 20, "Loop Engineering." Cited as the primary source for a goal-
interrogation checklist (verify against which environment; definition of done; attempt/budget cap;
policy for unspecified decisions), attributed as this book's framing.
[^gulli2-ch11]: Gulli, A. & Nawalgaria, *Building AI Agents* (2026 public draft), ch. 11, "Memory
and Agentic RAG." Cited as the primary source for a "Persistent Scratchpad" framing and its own
stated caveat that an agent must be actively prompted to re-read its own notes; the concept homes
at 5.1/5.3, not this chapter.
[^gulli2-ch22]: Gulli, A. & Nawalgaria, *Building AI Agents* (2026 public draft), ch. 22, "What's
Next." Cited as the primary source for the claim being corrected in item 1 (that reasoning models
have "collapsed" the ReAct loop into one planning call plus a deterministic executor); the
manuscript is a public draft and a legitimate primary citation in its own right.
