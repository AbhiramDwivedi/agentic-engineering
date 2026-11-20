# Coverage map: The Specialist Panel (chapter 3.5)

> **Budget:** standard pattern, ~2,000-2,800 prose words to the end of *In short* (code, sources,
> and cross-links excluded). **Ruled 2026-09-07**, replacing the flagship row the stub inherited
> from 3.5 sitting in the origin-set four. One sentence why: tool use, evaluator-optimizer, and
> orchestrator-workers each carry a vendor-named workflow, a multi-year research lineage, and a
> production-scale case study behind their "model decides" claim, and item 1 below finds this
> chapter has none of the three settled. Its closest primary-source analogues, Mixture-of-Agents
> and Solo Performance Prompting, are thinner and narrower than any citation anchoring the other
> three, and whether the pattern clears the litmus at all is an open question rather than a
> premise. A chapter that has to settle whether its own premise holds before arguing anything else
> is a standard chapter carrying a hard question, not a flagship.

> Research-derived spec for what the chapter must cover to let a reader tell a genuine panel from
> three parallel prompts wearing job titles, and to know when the pattern is worth its extra
> calls. Built from a 7-angle sweep (vendor/primary docs, academic/benchmarks, security/failure
> modes, the skeptical read, the alias sweep, the daily-tool angle, the everyday-engineer angle);
> see "Sweep angles run and skipped" below. A second-editorial pass (logged below, just before
> Open questions) checked every finding of an independent review against primary sources before
> folding it in.
>
> The chapter path (`docs/composition/specialist-panel.md`) is a stub with no real prose: a gloss
> line, a placeholder `*Also called: multi-persona reasoning, mixture-of-roles, council/debate.*`,
> and an unargued `Maturity: Emerging` line. All three are evaluated below, not assumed, and none
> survives unchanged: the alias line conflates a same-pass panel with an iterative adversarial
> mechanism (see Aliases); the maturity line needs a split with no unqualified positive tier (see
> Maturity summary); and the mental model the reference has already published in two shipped
> chapters turns out to describe two different mechanisms (see item 1, the map's central
> finding). Review and trim the **Must-cover** list; that sets the chapter's scope. Bar:
> definitive but tight (the Gang-of-Four / Wikipedia test), not exhaustive. This map lands at six
> must-cover items, tighter than the usual target, because two candidate items (security,
> framework mechanics) were demoted to a Gotcha and to Reader-verifiable anchors on review; see
> item 1's neighbours below and the Second-reviewer pass.

> **Thesis** (the one sentence the chapter argues) — **RULED 2026-09-07, see Orchestrator
> rulings.** Neither candidate below is used, because each presupposes a resolution of item 1 that
> is the author's to make. The chapter argues the boundary itself, which is true either way:
>
> **_A specialist panel is a structural decision only where something decides, before any
> specialist runs, which experts this particular input calls for. Run a fixed roster on every
> input and what you have is parallel ensembling wearing job titles: often worth its calls, but it
> earns that on demonstrated benefit, never on the word "specialist"._**
>
> The two original candidates are kept below as the wordings to switch to if the author rules
> option A or option C at the PR.
>
> - **If the chapter resolves toward dynamic, pre-execution selection (item 1's option A):**
>   *A panel earns the genuinely-new claim only where something decides, before any specialist
>   runs, which experts this particular input calls for; run a fixed roster on every input and
>   merge the output, and you have parallelization wearing job titles, not a fourth genuinely-new
>   pattern.*
> - **If the chapter resolves toward the fixed roster as the honest default (item 1's option C):**
>   *A fixed specialist panel is Standard parallel ensembling, not a distinct agentic pattern; its
>   benefit must be demonstrated against one well-scoped multi-criteria call, and persona labels
>   alone are not evidence of diversity.*

## The mental model (what the reader must leave with)

[1.2 Who Decides?](../foundations/who-decides.md) defines the test this chapter must pass in one
sentence: "A structural decision is one that changes the control flow: which step runs next,
whether to loop again, how many parallel branches to spawn, which path to take."[^who-decides-def]
Apply that definition literally to a specialist panel and two very different mechanisms are on the
table. Run a fixed roster of personas on every input and blend their output: nothing about that
changes which branches run, so by 1.2's own words nothing structural happened, and the shape is
Anthropic's own **voting** variant of Parallelization under a different name, "running the same
task multiple times to get diverse outputs," instanced by "several different prompts" reviewing
code or evaluating content from different angles.[^anthropic-bea] This reference's own coverage
map for 3.3 already ruled that shape out of composition-pattern status, calling it "a reliability
technique, not composition."[^fanout-map] Decide, before any specialist runs, *which* of a small
named set of viewpoints actually applies to this input, and the branch count itself changes: that
is a real structural decision, and Solo Performance Prompting is direct, peer-reviewed evidence
that a model can do exactly this — "given an input task, SPP first generates a list of
participants with different personas... we let the language model identify the personas
dynamically instead of manually defining them" — with a stated limit: the paper reports the
benefit "only emerges in GPT-4 and does not appear in less capable models, such as GPT-3.5-turbo
and Llama2-13b-chat."[^spp] Whether the carrier, and the chapter, land on the first mechanism or
the second is item 1's open question, and it is not this map's to settle.

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation. All items are fresh
gaps against the current stub, which has no argued prose yet.

1. **The litmus boundary, argued to a decision point, not resolved** — the chapter's spine
   question, and this map's central finding: as specified today, across three shipped chapters and
   the carrier bible, the reference does not agree with itself about what this pattern's model-made
   decision is. [1.2 Who Decides?](../foundations/who-decides.md) states the tell in print: "**It
   picks a persona.** The model chooses which kind of expert to reason as before it
   answers,"[^who-decides] language that describes a *selection* made before generation. [3.3
   Orchestrator-Workers](../composition/fan-out.md) calls 3.5 "a **fixed set** of
   personas,"[^fanout-crossref] and [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md)
   calls it "**fixed personas** judging one input once,"[^eo-crossref] both describing the opposite
   of a selection. `meta/carrier-bible.md` §7 specifies the fixed reading exactly: three named
   personas that "reason independently, then a reconcile step merges them," every time, for every
   product.[^carrier-bible] Three options, and each has a real cost the author should see before
   ruling.
   - **Option A — pre-execution selection.** The model, or a step ahead of the panel, decides
     *which* of a small, named set of viewpoints applies to this input, before any specialist runs,
     and that decision determines which branches execute. This is the only formulation that
     satisfies 1.2's own definition of a structural decision, because it is the only one that
     changes which branches run. It must be held to two conditions to count at all. First, the
     decision has to happen *before* execution, not after: a downstream step that lets every
     specialist run and then drops the ones whose output turned out to be out of scope is
     reconciliation wearing selection's clothes, not selection, and collapses into option B.
     Second, it has to be distinguished from two near neighbours that already own similar shapes:
     [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md)'s LLM routing picks one
     mutually exclusive category and sends the input down a single path; [3.3
     Orchestrator-Workers](../composition/fan-out.md)'s dynamic half decides how many pieces to
     decompose an open-ended task into. A panel's selection, if it clears the bar, is neither: it is
     a multi-label admit-or-skip call over a small, fixed, *named* vocabulary of professional
     viewpoints (turn each of N named lenses on or off for this input), which is a real third shape
     if the chapter can show it, but this sweep found no vendor-named workflow describing that exact
     shape. Solo Performance Prompting is the closest published evidence that dynamic,
     input-conditioned persona identification is a real, working mechanism,[^spp] but SPP selects
     from an open vocabulary the model invents per task, sequentially, inside one context, not a
     small fixed named set, in parallel, across independent calls — extending its finding to this
     chapter's architecture is a reasoned extrapolation, not a directly evidenced one, and SPP's own
     benefit is reported for GPT-4-class models only.[^spp]
   - **Option B — the reconcile step's judgment.** The model's decision lives in weighing or
     synthesizing disagreement among the panel's outputs, not in which personas ran. Mixture-of-
     Agents is real evidence that an LLM aggregator reading several full candidate responses and
     synthesizing one outperforms a mechanical ranking baseline: the paper states plainly that
     Mixture-of-Agents "significantly outperforms LLM rankers" and that "the aggregator does not
     simply select one of the generated answers... but potentially performs sophisticated
     aggregation."[^moa] But 1.2's own definition is explicit that a structural decision changes
     *control flow* — which step runs next, whether to loop, how many branches, which path — and
     weighing claims into a merged answer changes the answer, not the control flow. By 1.2's own
     words, this option does not clear the bar the reference already set for itself, which is why
     this map does not offer it as a live third path forward.
   - **Option C — accept the fixed roster as the honest default, and reconsider whether 3.5
     belongs among the genuinely-new four at all.** This is the plainest reading of the evidence
     the sweep found: no vendor names a workflow matching option A's shape; MoA's own strongest
     evidence (item 4) argues for heterogeneous *models*, not prompted personas from one model; and
     the persona-null result (item 4) finds persona prompts often do not even change output quality.
     Taking C has a real blast radius the author should weigh before ruling, not discover after:
     1.2's own four tells become three, and its worked table and running example both need a line
     removed;[^who-decides-def] the home-page architecture diagram renders 3.5 as a rounded
     ("model decides") node today and would need to become a rectangle;[^homepage-map] the
     [quick-reference](../catalogs/quick-reference.md) table's "Specialist panel | the model" row
     would need to move columns; and 3.3's and 3.4's own published cross-references to 3.5 (both
     quoted above) would need a wording pass regardless of which option is chosen, since both
     currently assert, in already-shipped prose, that "the model decides" for 3.5.
   *Skip resolving this and the chapter either drafts against a mechanism the carrier does not
   build, or narrows an already-published claim (1.2's) without saying so, which breaks the promise
   a reference makes to a reader who lands on 1.2 first.* **n/a** (definitional; this is the
   question the rest of the map is organized around; full framing is repeated in Open questions
   1 below, and this map does not choose among A, B, or C).
2. **The architecture taxonomy: the axes that actually separate these mechanisms** — the reader's
   tool for placing any "several LLM calls, one input" system on a grid instead of treating them as
   interchangeable. Five axes, independently varying: **membership** (a fixed roster decided at
   author time, versus input-selected membership decided per run); **model diversity**
   (homogeneous, one model in different roles, versus heterogeneous, genuinely different
   underlying models); **context** (each call isolated, versus a shared context all participants
   read and write); **interaction** (one independent pass per participant, versus iterative
   back-and-forth across rounds); and **aggregation** (a deterministic vote or rank, versus
   generative synthesis by a model). Placed on this grid: self-consistency is fixed, homogeneous,
   isolated, single-pass, deterministic-vote;[^selfconsistency] Mixture-of-Agents is fixed
   membership, heterogeneous, isolated-then-shared-at-aggregation, single-pass-per-layer,
   generative-synthesis;[^moa] multi-agent debate is fixed membership, either homogeneous or
   heterogeneous, shared-by-exchange, multi-round-iterative, judge-or-consensus
   aggregation;[^debate][^divergent] Solo Performance Prompting is input-selected membership, one
   model, single shared context, sequential turns inside it, no separate
   aggregation-step;[^spp] the panel-of-judges variant is fixed membership, heterogeneous by
   design, isolated, single-pass, majority-or-consensus over evaluation scores rather than
   drafts.[^poll] *Skip it:* a reader treats these as five names for one idea and cannot tell why
   one paper's positive result does not transfer to a same-model, fixed-roster, single-pass panel.
   **n/a** (definitional; feeds item 1 and demotes a longer neighbour-by-neighbour catalogue to
   mention-and-link).
3. **The evaluation and ablation contract: how a panel proves it earned its extra calls** — a
   definitive chapter has to tell the reader what to measure, not only what to build. Compare a
   candidate panel against four baselines: one well-scoped multi-criteria prompt asking a single
   call to cover every specialist's concern at once; the single best specialist alone; same-model
   self-consistency (repeated samples, no persona variation, deterministic
   vote);[^selfconsistency] and, where feasible, a heterogeneous-model ensemble. Score on final
   output quality, omission recall (did the panel catch what the single call missed, the reason to
   run it at all), disagreement preservation (does a genuine conflict between specialists survive
   into something the reconciler or a human can see, or does it get smoothed away), latency, and
   cost. The persona-null result is the reason this cannot be skipped: persona choice was found to
   be effectively arbitrary for factual-task accuracy in the paper's own tests,[^persona-null] and a
   separate debate-specific study found apparent multi-agent gains can disappear entirely against
   properly tuned single-agent baselines.[^mad-limits] *Skip it:* a team ships a panel that reads
   more thorough, never measures it against the one-call alternative, and cannot tell a real gain
   from a longer, more expensive answer that says the same thing three ways. **n/a** (methodology;
   → [4.2 Evaluation](../craft/proving-it-works.md) for the full measurement depth).
4. **The persona-diversity ceiling: same model, correlated blind spots, and personas that do not
   reliably help** — the load-bearing skeptical finding, and the reason no unqualified positive
   maturity tier survives this sweep. Zheng et al. (EMNLP Findings 2024) tested 162 roles across
   2,410 factual questions and four model families and found persona system prompts yield no
   accuracy gain on fact-based QA, and usually slightly worsen it.[^persona-null] Where the panel's
   personas and the reconciler are the same underlying model, the self-preference and
   self-enhancement findings this reference already names for evaluator-optimizer apply here too:
   Panickssery et al. (NeurIPS 2024) find self-recognition correlates with self-preference,[^selfpref]
   and Zheng, L. et al. (NeurIPS 2023) separately document self-enhancement bias in
   judges.[^judge-bias] These are two related findings from two different literatures, not one
   result replicated twice, and the chapter should say so precisely rather than claim independent
   replication of a single claim. The multi-agent-debate literature converges on the same caution
   at larger scale: Smit, Grinsztajn, Duckworth, Barrett, and Pretorius (ICML 2024) show debate does
   not reliably beat self-consistency or ensembling baselines once tuned fairly,[^mad-limits] and a
   2025 study across five debate methods, nine benchmarks, and four base models found debate often
   loses to plain chain-of-thought and self-consistency, naming model heterogeneity, not more
   personas from one model, as the fix.[^mad-heterogeneity] *Skip it:* a team ships three personas
   on one model, sees output that reads more varied without being more correct, and has no
   framework for why. **Emerging** (dynamic persona selection and heterogeneous-model synthesis, as
   techniques with real but narrow evidence); **Contested** (same-model, prompt-only persona
   diversity as a reliable quality lever, at all). (Zheng, M. et al., EMNLP Findings 2024,
   arXiv:2311.10054;[^persona-null] Panickssery et al., NeurIPS 2024,
   arXiv:2404.13076;[^selfpref] Smit et al., ICML 2024, arXiv:2311.17371;[^mad-limits]
   arXiv:2502.08788.[^mad-heterogeneity])
5. **The reconcile step: a typed output contract, not a blend** — mirroring 3.3's synthesizer
   discipline and 3.4's revise-edge discipline, adapted to a single pass with no loop. A reconciler
   that returns prose is a black box; a reconciler that returns a typed verdict is auditable. Give
   it a contract: accepted claims (with which specialist each came from), rejected claims (with the
   stated reason), unresolved conflicts (where two specialists disagree and neither is
   overruled), missing specialists (a call that errored, timed out, or returned nothing, reported
   as a structured absence, never a silent gap), and an escalation status a caller can act on. Four
   controls make that contract trustworthy rather than decorative, each responding to a documented
   judge pathology: mask each specialist's provenance from the reconciler where the underlying
   model is shared, since self-preference tracks recognized authorship;[^selfpref] randomize the
   order specialists are presented in, since position bias is independently
   documented;[^judge-bias] preserve a genuine minority objection in the output rather than let
   majority framing erase it, the direct fix for the "averaged into agreement" failure; and require
   an explicit abstain-or-escalate path when the reconciler cannot resolve a conflict, rather than a
   forced pick. *Skip it:* a compliance reviewer's required disclosure loses a word-count fight with
   an SEO-optimized headline inside an opaque reconcile call, and nothing in the output says a
   conflict ever happened. **n/a** (engineering discipline, reasoned from 3.3's and 3.4's own
   published rules plus the judge-bias literature above; → [4.2
   Evaluation](../craft/proving-it-works.md) for judge-validation methodology in depth).
6. **Cost, merged with context economy: scales with panel width, not below it** — every persona
   call reads the input in full, so total spend scales with panel size plus one reconcile call, the
   same shape 3.3's fixed half has, not a lighter one: this is not necessarily cheaper than a
   dynamic fan-out that some inputs resolve to zero or one worker, and the chapter must not claim
   it is. Pass each specialist only the fields its own viewpoint needs, not the whole record, the
   same context-economy discipline [1.5 Context Engineering](../foundations/context-engineering.md)
   already argues generally: a bloated shared context degrades attention as well as spending
   tokens, and a panel that hands every specialist everything pays both costs at once. State the
   shape (a small, fixed multiplier over one call, plus reconcile), not a number; this sweep found
   no published cost figure specific to persona-panel ensembling. The one number that matters is
   comparative, and item 3 already requires it: benchmark against the single well-scoped
   multi-criteria call before claiming the panel is worth its multiple. *Skip it:* a team assumes a
   small, bounded roster is cheap by comparison and never runs the one benchmark that would tell
   them whether the extra calls bought anything. **n/a** (arithmetic). (→ [8.4 Controlling
   Cost](../production/controlling-cost.md); [1.5 Context
   Engineering](../foundations/context-engineering.md).)

## Mention-and-link (one line, a pointer, not a section)

- **The augmented-LLM atom** each persona-call is one instance of, already framed as "the same node
  wearing different personas" → [1.4 The Augmented LLM](../foundations/the-augmented-llm.md).
- **Orchestrator-workers**, the sibling that decides a subtask count; distinguish precisely from
  option A's membership-selection shape (item 1) → [3.3
  Orchestrator-Workers](../composition/fan-out.md).
- **LLM routing**, the sibling that picks one mutually exclusive category; distinguish precisely
  from option A's multi-label admit-or-skip shape (item 1) → [3.2 Routing &
  Dispatch](../composition/the-router-that-isnt.md).
- **Evaluator-optimizer**, the sibling that loops on one draft against a verdict; this chapter's
  panel judges once, in parallel, with no revision round → [3.4
  Evaluator-Optimizer](../composition/evaluator-optimizer.md).
- **Iterative, adversarial multi-agent debate** in depth (rounds of rebuttal, judge-managed
  argument), Mixture-of-Agents' layered aggregation in depth, and software-team role-play
  architectures (ChatDev, MetaGPT, CAMEL) named only in item 2 → [9.2
  Multi-Agent](../frontier/more-than-one-agent.md) (coding-team variant also touches [9.6 Coding
  Agents](../frontier/coding-agents.md)).
- **LLM-as-judge methodology and panel-of-judges evaluation** (PoLL, judge-human agreement) in
  depth → [4.2 Evaluation](../craft/proving-it-works.md).
- **Security.** A fixed panel with no inter-agent messaging and no distinct tools or privileges per
  specialist is not a new attack surface: 3.3's own carrier instance already has every worker read
  the same shared listing, so a panel sharing one input is not a distinguishing risk, and the
  existing "treat outputs as untrusted" discipline already covers it → [2.1 Tool
  Use](../the-unit/tool-use.md), [3.3 Orchestrator-Workers](../composition/fan-out.md). If a
  variant gives personas distinct tools, memory, or privileges, escalate properly to [4.6 Prompt
  Injection & the Lethal Trifecta](../craft/prompt-injection.md) and OWASP's Agentic Top 10
  ASI07/ASI08 rather than reasoning from this chapter's carrier case.
- **Framework and daily-tool mechanics** (OpenAI Agents SDK, Google ADK, CrewAI) are anchors, not
  argument; see Reader-verifiable anchors below, and the Stage-2 code brief for exact API shapes.
- **Structured output** as the typed contract each persona's verdict and the reconciler's merged
  result rely on → [2.2 Structured Output](../the-unit/structured-output.md).
- **Escalation when the panel can't be reconciled** → [4.3
  Human-in-the-Loop](../craft/human-in-the-loop.md).
- **Cheap model per persona, stronger model for reconcile** → [8.2 Which
  Model?](../production/which-model.md).
- **Fine-tuning distinct persona models** rather than prompting one model into several roles →
  [8.3 To Train or to Prompt](../production/train-or-prompt.md).
- **A fixed panel dressed as a decision** as the anti-pattern this chapter's Gotchas should feed,
  the direct sibling of 3.3's "fixed list in a planner's costume" → [Anti-Patterns
  Catalog](../catalogs/anti-patterns.md).

## Out of scope (name it, point out)

- Iterative, adversarial multi-agent debate mechanics (rounds, rebuttal protocols, judge-managed
  argument) → [9.2 Multi-Agent](../frontier/more-than-one-agent.md).
- Mixture-of-Agents' layered architecture in depth, and ChatDev / MetaGPT / CAMEL as full
  architectures → [9.2](../frontier/more-than-one-agent.md) / [9.6](../frontier/coding-agents.md);
  name only here, per item 2.
- LLM-as-judge methodology, PoLL's tuning, and judge-human agreement measurement → [4.2
  Evaluation](../craft/proving-it-works.md).
- Fine-tuning separate models per persona → [8.3 To Train or to
  Prompt](../production/train-or-prompt.md).
- Full security treatment beyond the Gotcha-level pointer above: the OWASP Top 10 for Agentic
  Applications taxonomy in depth → [G. The Security Posture
  Map](../catalogs/security-posture.md) (planned) and [4.6](../craft/prompt-injection.md).
- Exact current API shapes for OpenAI Agents SDK, Google ADK, and CrewAI → the Stage-2 code brief
  and each vendor's own docs; this chapter cites the shape via Reader-verifiable anchors only.
- Live benchmark numbers (AlpacaEval, MT-Bench leaderboards) → link, do not hardcode; they rot.

## Maturity summary

- **Standard:** parallel model calls with a merge step, as a mechanism (inherits 3.3's verdict for
  the fixed-parallel shape; no claim here rises above this for the fixed-roster case).
- **Emerging:** the model (or a step ahead of the panel) deciding which persona's viewpoint applies
  per input, before execution — the mechanism that would make 1.2's published tell and option A
  literally true, evidenced narrowly by Solo Performance Prompting for GPT-4-class models and
  unevidenced for the parallel, fixed-vocabulary form this chapter would need;[^spp] heterogeneous-
  model synthesis (Mixture-of-Agents' own strongest result), real but not yet a workflow a mid-size
  team reaches for by default.[^moa]
- **Contested:** same-model, prompt-only persona diversity as a reliable quality lever at all
  (Zheng, M. et al. 2024's null result on factual tasks);[^persona-null] multi-agent debate as a
  general-purpose improvement over single-agent baselines absent model heterogeneity (Smit et al.
  2024; arXiv:2502.08788);[^mad-limits][^mad-heterogeneity] billing a fixed panel run every time as
  the model "deciding" anything, the same over-orchestration failure
  [3.2](../composition/the-router-that-isnt.md) and [3.3](../composition/fan-out.md) each name for
  their own neighbours.

**No tier above carries an "Established" component**, and that is deliberate: this sweep found no
vendor-named workflow, no multi-year research lineage, and no production-scale case study
supporting a fixed-persona panel specifically, only adjacent evidence (MoA, PoLL, SPP) that each
argues for a different mechanism than this chapter's stub describes. **Recommended verdict for the
chapter as a whole:** "Standard (fixed parallel execution, as a mechanism) · Emerging (dynamic
persona selection; heterogeneous-model synthesis) · Contested (same-model prompted-persona panels
as a quality improvement)." This is a harder line than 3.3's or 3.4's two-part splits, both of
which keep an Established half; this chapter currently has none, and the author should treat that
as a live question about whether 3.5 belongs in the origin-set four at all, not a foregone
conclusion. See Open questions.

## Aliases

This sweep found no external term that is a true synonym for the mechanism as the current stub
describes it: a fixed roster of personas, run in parallel on one input, merged by a single
reconcile pass, with no selection step and no revision round. Every published name below covers a
materially different mechanism on item 2's taxonomy, which is itself evidence for item 1's finding
that "specialist panel" may be naming an assembly of borrowed pieces rather than one established
pattern.

**House terms** (the stub's own placeholders, not attributable to an external source):
multi-persona reasoning; mixture-of-roles.

**Related, not synonyms** (each occupies a different cell on item 2's taxonomy; treat as
confusable neighbours, not alternate names):
- **Solo Performance Prompting / multi-persona self-collaboration / cognitive synergy** — Wang et
  al.'s own terms (NAACL 2024, arXiv:2307.05300).[^spp] The closest published match to a
  *selection* mechanism, but sequential and single-context, not parallel calls.
- **Mixture-of-Agents (MoA)** — Wang et al.'s own name (arXiv:2406.04692).[^moa]
  Heterogeneous-model aggregation, not same-model persona prompting.
- **multi-agent debate / MAD** — Du et al.'s and Liang et al.'s own term.[^debate][^divergent]
  Iterative and adversarial, not a single pass.
- **Panel of LLM evaluators / PoLL** — Verga et al.'s own name.[^poll] Evaluation-specific, not
  drafting.
- **self-consistency** — Wang et al.'s own term.[^selfconsistency] No persona variation; the
  no-persona floor on item 2's taxonomy.
- **role-play** — ChatDev/MetaGPT/CAMEL's own framing for the software-team variant.
- **crew (CrewAI)** — CrewAI's own term for a role-based agent team; CrewAI's default sequential
  process runs roles in order, not in parallel.
- **Multi-Agent Collaboration** — the umbrella chapter title both Gulli books use (Gulli, *Agentic
  Design Patterns*, 2025, ch. 7, per the publisher's public table of contents;[^gulli-adp] Gulli &
  Nawalgaria, *Building AI Agents*, 2026 public draft, ch. 6). Broader than this chapter, covers
  any multi-agent architecture; not verified this sweep to name this chapter's specific
  single-pass, fixed-roster shape as its own sub-pattern.
- **Multi-agent collaboration** — Andrew Ng's own name for one of his four widely cited agentic
  design patterns (2024).[^ng] Same breadth caveat.
- **council / debate** — the stub's own placeholder; struck as a standalone alias and folded into
  the debate entry above, since it names the iterative mechanism, not a synonym for a single-pass
  panel.

## Reader-verifiable anchors

- **The OpenAI Agents SDK's current, maintained orchestration docs** describe exactly this
  chapter's shape as a live pattern: "a manager agent keeps control of the conversation and calls
  specialist agents through `Agent.as_tool()`," used "when you want one agent to own the final
  answer, combine outputs from multiple specialists, or enforce shared SDK guardrails in one
  place."[^oai-orchestration] This is the primary anchor: current core documentation, not an
  example notebook.
- **The OpenAI Agents SDK's cookbook example, with a caveat.** "Parallel Agents with the OpenAI
  Agents SDK" runs four specialized agents (features, pros/cons, sentiment, purchase
  recommendation) concurrently over one product review via `asyncio.gather`, then a meta-agent
  combines their labelled outputs.[^oai-parallel] The notebook itself states plainly that it is "a
  toy example that you likely wouldn't parallelize in the real world" — cite it for the shape, not
  as evidence the pattern is production-proven.[^oai-parallel]
- **Google's ADK, with a caveat.** `ParallelAgent` runs sub-agents concurrently in isolated
  branches with no automatic state-sharing and no built-in aggregator, confirming the reconcile
  step is always the caller's job, never the framework's.[^adk-parallel] Current ADK docs state
  that, starting in ADK 2.0 for Python and Go, templated workflow agents including
  `ParallelAgent` "have been superseded by more flexible workflow structures, including graph-based
  workflows and dynamic workflows" — cite the deterministic, no-aggregator behavior as a durable
  design fact, and verify which workflow style the reader's ADK version actually
  ships.[^adk-superseded]

## Incidents

No dedicated, named public postmortem describing a specialist-panel or persona-ensemble failure
specifically (as opposed to a general multi-agent system failure) was found this sweep. State that
plainly rather than force a citation, the same posture 3.3's and 3.4's own coverage maps took for
their comparable gaps. The closest adjacent evidence is general, not panel-specific: Cemri et al.'s
MAST taxonomy sorts real multi-agent failures into 14 modes across three categories, from 1,600+
annotated traces across seven frameworks (NeurIPS 2025, Datasets and Benchmarks
Track), already the anchor for 3.3's Gotchas.[^mast] Judge self-enhancement bias (item 4) is the
closest thing to a measured, first-party "incident" on the reconcile side specifically, and it is
directly citable.[^judge-bias]

## Named-idea candidates

None survive this pass. **"The costume test"** is struck: it tests whether the prose sounds
rhetorical, not who controls the control flow, so it fails the litmus's own bar before it ever
reaches a reader. **"A narrow brain is harder to fool"** could not be verified against a public
primary source this pass: a fetch of the 2026 public draft did not reach its chapter 6 content, so
it is struck rather than kept on trust, per the rule that an attributed phrase stays only if a
reader could check it in a public source. If the author can independently confirm the phrase and
its chapter location in that draft, it can be reconsidered for the narrow-brief argument only (give
each specialist a scoped brief, which resists scope creep and injection better than one generalist
instruction), never as cover for persona-diversity-as-quality-lever, which item 4 undercuts; record
alongside it that the phrase asserts injection resistance without its own supporting evidence, a
claim the author would be making, not the source.

## Sources

Vendor/primary: Anthropic, "Building Effective Agents" (2024-12-19) — the Parallelization
(sectioning/voting) definitions, the "several different prompts" code-review and content-
moderation examples for voting.[^anthropic-bea] OpenAI, current Agents SDK docs, "Agent
orchestration" (agents-as-tools).[^oai-orchestration] OpenAI, developers.openai.com cookbook,
"Parallel Agents with the OpenAI Agents SDK."[^oai-parallel] Google, ADK docs, "Parallel
agents."[^adk-parallel][^adk-superseded] CrewAI, "Agents" docs (role/goal/backstory).[^crewai]
Security (named only, see Mention-and-link): OWASP Top 10 for Agentic Applications 2026, ASI07
Insecure Inter-Agent Communication, ASI08 Cascading Failures.[^owasp-agentic] Academic:
Mixture-of-Agents, arXiv:2406.04692;[^moa] Self-Consistency, arXiv:2203.11171;[^selfconsistency]
multi-agent debate, Du et al., arXiv:2305.14325;[^debate] Liang et al., arXiv:2305.19118 (EMNLP
2024);[^divergent] Solo Performance Prompting, Wang et al., arXiv:2307.05300 (NAACL
2024);[^spp] Smit, Grinsztajn, Duckworth, Barrett, Pretorius, "Should we be going MAD?,"
arXiv:2311.17371 (ICML 2024);[^mad-limits] "Stop Overvaluing Multi-Agent Debate,"
arXiv:2502.08788;[^mad-heterogeneity] Zheng, M. et al., persona-null-result, arXiv:2311.10054
(EMNLP Findings 2024);[^persona-null] Panickssery et al., arXiv:2404.13076 (NeurIPS 2024, reused
from 3.4);[^selfpref] Zheng, L. et al., MT-Bench judge bias, arXiv:2306.05685 (NeurIPS 2023, reused
from 3.4);[^judge-bias] Verga et al., "Replacing Judges with Juries," arXiv:2404.18796;[^poll]
Cemri et al., "Why Do Multi-Agent LLM Systems Fail?," arXiv:2503.13657 (NeurIPS 2025, Datasets and
Benchmarks Track), reused from 3.3.[^mast] Named-only, not cited for a claim: ChatDev,
arXiv:2307.07924;[^chatdev] MetaGPT, arXiv:2308.00352;[^metagpt] CAMEL, arXiv:2303.17760 (NeurIPS
2023).[^camel] Gulli, *Agentic Design Patterns* (2025), ch. 7, per publisher table of contents,
full text not independently verified this sweep.[^gulli-adp] Gulli & Nawalgaria, *Building AI
Agents* (2026 public draft), ch. 6, title only, per publisher/author-circulated table of contents;
no specific claim from its body is cited in this map. Andrew Ng, public posts naming four agentic
design patterns (2024).[^ng] Internal: [1.2 Who Decides?](../foundations/who-decides.md) (the tell
this map finds inconsistent with 3.3/3.4's own text, and its own definition of a structural
decision, quoted in the mental model); [3.3 Orchestrator-Workers coverage map](fan-out.md) (the
voting-is-not-composition ruling); `meta/carrier-bible.md` §7 (the panel personas, and the fixed-
roster spec this map flags); [docs/index.md](../index.md) (the home-page architecture
diagram).[^carrier-bible][^homepage-map]

> **Verify before quoting:** Mixture-of-Agents' leaderboard numbers (AlpacaEval, MT-Bench, FLASK)
> are snapshot results from mid-2024 and are not repeated in this map for that reason; cite the
> finding (an LLM aggregator over heterogeneous proposers beats a ranking baseline, and beats
> repeated sampling from one model) and the live source, never a frozen score. The OWASP Top 10 for
> Agentic Applications 2026 was newly announced (2025-12-09) at the time of this sweep; re-confirm
> category names and numbering against the live document before the chapter ships. Gulli's
> *Agentic Design Patterns* (2025) ch. 7 and Gulli & Nawalgaria's 2026 draft ch. 6 are cited here
> only for their chapter titles, confirmed against publicly available tables of contents; no claim
> about either chapter's body content is made or should be attributed without a direct read that
> reaches that chapter. CrewAI's and Google ADK's exact current API surfaces should be re-confirmed
> against the versions the reader will install; ADK in particular is mid-transition away from the
> templated `ParallelAgent` workflow style as of this sweep.

## Sweep angles run and skipped

- **Vendor/primary docs — ran fully.** Anthropic's own definition of voting (with its worked
  examples) fetched directly; OpenAI's current orchestration docs and cookbook example, Google
  ADK's ParallelAgent docs (including its ADK 2.0 supersession notice), and CrewAI's docs each
  checked live for Reader-verifiable anchors.
- **Academic + benchmarks — ran fully.** Mixture-of-Agents, self-consistency, both multi-agent
  debate founding papers, Solo Performance Prompting, and PoLL each verified directly against their
  full text, not the abstract alone, given how load-bearing the exact mechanism claims turned out
  to be (MoA's proposer composition and ranker comparison; SPP's dynamic-identification mechanism
  and its GPT-4-only limitation). The persona-null-result paper and both debate-skepticism papers
  were read specifically because they are this chapter's load-bearing skeptical evidence.
- **Security / failure modes — ran, then demoted.** OWASP's 2026 Agentic Applications categories
  were checked for exact naming (ASI08 is "Cascading Failures," not "Cascading Agent Failures");
  on review, the fixed-roster carrier case does not present a distinguishing security story beyond
  what 2.1 and 3.3 already cover, so this angle's output moved from a must-cover item to a Gotcha-
  level mention-and-link.
- **Practitioner writeups — ran narrowly.** No independent, citable third-party production writeup
  specific to a fixed-persona panel (as opposed to general multi-agent systems, already covered by
  3.3's vendor-sourced practitioner account) was found this sweep.
- **The skeptical read — ran, and it reshaped the whole map.** The persona-null-result paper and
  the two debate-skepticism papers were read directly, not summarized from a secondary source,
  because they are what forced this map away from any unqualified positive maturity tier.
- **The alias sweep — ran.** Andrew Ng's four-patterns posts, CrewAI's docs, and both Gulli books'
  public tables of contents were checked directly; no claim from either Gulli book's body text is
  cited in this map, only chapter titles confirmed against public listings.
- **The everyday-engineer angle — ran, narrowly.** GitHub-issue-level search for CrewAI/LangGraph
  patterns running multiple role-based agents in parallel surfaced the same "no built-in
  aggregator" pattern the primary docs already document; no distinct new finding.
- **The daily-tool angle — ran.** OpenAI's current orchestration docs, its cookbook example, and
  ADK's own documented supersession notice together supply the three reader-verifiable anchors.
- **Incidents — ran, and came back thin**, as stated plainly in the Incidents section above rather
  than papered over with an approximate citation.

## Second-reviewer pass (Codex, 2026-09-05)

An independent review of this map's prior draft raised 13 findings. Each was checked against
primary sources before being folded in; none was applied on the reviewer's say-so alone.

1. **ACCEPTED.** 1.2's own definition ("a structural decision... changes the control flow") is
   quoted in the mental model and confirms weighing claims at reconcile does not qualify; item 1
   and Open question 1 were rewritten to present the full argument, without this map choosing
   among A, B, or C, per editorial ruling that the classification call belongs to the author.
2. **ACCEPTED.** The prior thesis was unfalsifiable; replaced with two resolution-conditioned
   candidates (one per live option), and the mental model was tightened to state the mechanism
   distinction plainly rather than gesture at "a verdict a single prompt could not."
3. **ACCEPTED.** Verified directly against the paper: MoA's default proposers are heterogeneous
   models (Qwen, WizardLM, LLaMA-3, Mixtral, dbrx); the aggregator is compared explicitly against
   an LLM-ranker baseline, not "mechanical vote-aggregation"; and the paper's own ablation shows
   multiple different LLMs outperforming repeated single-model sampling. Maturity summary rewritten
   to Standard/Emerging/Contested with no Established component; frozen benchmark numbers dropped.
4. **PARTIAL.** Operational detail with no public primary source, and a reference no reader could
   check, were removed from the map body; the map cites public primary sources only from here on.
   Production-grounding potential is retained but scoped exactly as 3.3's and 3.4's maps scope
   theirs (see Author-only questions), with no more operational detail than those maps carry.
5. **ACCEPTED.** Added as must-cover item 3 (inside the requested top four): baselines, measures,
   and a pointer to 4.2 for methodology depth.
6. **ACCEPTED.** Verified directly: SPP's own text states the model "identifies the personas
   dynamically instead of manually defining them," with the benefit reported for GPT-4 only, not
   GPT-3.5-turbo or Llama2-13b-chat. Promoted into item 1's mechanism discussion and the mental
   model; noted that if the chapter stays parallel-only and fixed, 1.2's tell describes SPP-like
   dynamic selection, not the shape being built.
7. **ACCEPTED.** Added as must-cover item 2, five axes (membership, model diversity, context,
   interaction, aggregation); SPP, MoA, debate, PoLL, and self-consistency placed on it in one
   clause each; the prior neighbour-by-neighbour catalogue demoted to Mention-and-link.
8. **ACCEPTED.** Item on the reconcile step (now item 5) extended with a typed reconciler-output
   contract (accepted claims, rejected claims with reasons, unresolved conflicts, missing
   specialists, escalation status) and four controls (provenance masking, randomized order,
   minority-objection preservation, abstain/escalate), each tied to a specific cited bias.
9. **ACCEPTED.** "Cheaper than orchestrator-workers" struck as unsupported; cost item merged with
   context economy (item 6), and a single-call-baseline benchmark requirement added, cross-linked
   to item 3.
10. **ACCEPTED.** Security demoted from a must-cover item to a Mention-and-link Gotcha-level
    pointer; the "inverted attack surface" claim struck after confirming 3.3's own published carrier
    text already has every fixed worker read the same shared listing, so a panel sharing one input
    is not a distinguishing risk. Framework mechanics demoted out of must-cover into Reader-
    verifiable anchors and the Stage-2 code brief.
11. **PARTIAL.** Both prior anchors kept, now with verified caveats (the OpenAI cookbook page
    states it is "a toy example you likely wouldn't parallelize in the real world"; ADK's current
    docs confirm `ParallelAgent`-style templated workflows are superseded as of ADK 2.0). Added one
    current, non-archived anchor: the OpenAI Agents SDK's live "agents as tools" orchestration
    documentation.
12. **ACCEPTED.** All six citation fixes verified and applied: Smit et al.'s author order corrected
    against the arXiv abstract page (Smit, Duckworth, Grinsztajn, Barrett, Pretorius), later corrected to the PMLR published order (Smit, Grinsztajn, Duckworth, Barrett, Pretorius), which governs because the footnote credits ICML; OWASP ASI08
    confirmed as "Cascading Failures"; the MoA characterization and its frozen numbers fixed per
    finding 3; "independently replicated" removed from the self-preference/self-enhancement
    framing (now stated as two related findings from two literatures); MAST given a direct citation
    with its own venue and scale, not only an internal map pointer; the CrewAI superlative removed.
13. **ACCEPTED.** Aliases split into house terms, and "related, not synonyms" each with its own
    source; "the costume test" struck outright; "a narrow brain is harder to fool" struck per the
    fallback rule after a direct fetch of the public draft could not reach its chapter 6 content to
    verify the phrase, with the reviewer's unresolved objection (it asserts injection resistance
    with no supporting evidence of its own) recorded for the author in case it is reconsidered
    later against a confirmed source.

## Orchestrator rulings (Stage 1.6, 2026-09-07)

Settled so the chapter could be written. Each is a question of fact or craft, not of authorship;
all are reversible at PR review.

1. **Thesis: the boundary framing**, quoted in full in the Thesis block above. The map's two
   candidates each assume the author already ruled item 1; this one states what is true under
   every option, so the chapter has a real argument to make without pre-empting a decision that
   changes files it does not own. It is also what the Stage-2 code actually demonstrates: a fixed
   roster with a pure-code reconciler, honestly labelled.
2. **Budget row: standard pattern (~2,000-2,800 prose words)**, not the inherited flagship row.
   Every positive maturity claim in this map is qualified, and the origin-set question below is
   unresolved. A flagship budget would be writing to a status the evidence does not support.
3. **Maturity: "Standard (fixed parallel execution) · Emerging (dynamic persona selection;
   heterogeneous-model synthesis) · Contested (same-model prompted-persona panels as a quality
   improvement)."** No Established component. Adopted as recommended; the sweep found no evidence
   that would carry one.
4. **Alias line.** Ship a conventional `*Also called:*` line carrying only the terms that are
   genuine retrieval synonyms, and handle the rest in prose as neighbours rather than names for
   the same thing. Mixture-of-Agents, Solo Performance Prompting, debate, and self-consistency are
   named in the text as related-but-different, never in the alias line.
5. **Who decides, in the lens line: split, on the 3.3 precedent.** `your code (the fixed roster) /
   the model (the personas, where selection is dynamic)`. This is true under every option below,
   so the chapter does not have to pre-empt the author's ruling to state its own verdict honestly.

## Author-only questions (Stage 1.6 — shipped at the default, author rules at the PR)

No agent may decide these. Each ships at the conservative default; the pull request carries them
as a checklist.

1. **Does the specialist panel still belong among the genuinely-new four?** The full argument is
   in Must-cover item 1: **A**, amend the carrier so persona selection happens before execution
   and write the chapter as an explicit composite; **B**, locate the decision in the reconcile
   step, which item 1 argues fails 1.2's own definition of a structural decision[^who-decides-def]
   and is not offered as a live path; **C**, accept the fixed roster as the honest default and
   drop 3.5 from the origin set.
   - *Default shipped:* **neither A nor C is asserted.** The chapter states its own split verdict
     and makes no claim about origin-set membership in either direction. **Nothing outside
     `docs/composition/specialist-panel.md` is edited.**
   - *What changes if the author rules C:* `CLAUDE.md`'s origin-set four becomes three; 1.2's four
     tells and its worked example[^who-decides]; the home-page diagram's node shape for
     3.5[^homepage-map]; the quick-reference row; and the published cross-references in
     3.3[^fanout-crossref] and 3.4[^eo-crossref]. That is a separate PR, not this one.
   - *What changes if the author rules A:* `meta/carrier-bible.md` §7[^carrier-bible] gains
     pre-execution persona selection, and the chapter is rewritten as a composite of 3.2 and 3.3.
2. **Named idea.** Both prior candidates are struck; the sweep could not source either.
   - *Default shipped:* **no coinage.** The chapter argues its idea without branding it.
3. **"From production." callout.**
   - *Default shipped:* **no callout.** Grounding reads `companion repo + research`. Only the
     author can say whether a first-hand story exists here, and if so, scoped as 3.3 and 3.4 scope
     theirs: Listing Studio step 5 mechanics only, entirely in carrier terms.

[^who-decides-def]: This reference, [1.2 Who Decides?](../foundations/who-decides.md): "A
structural decision is one that changes the control flow: which step runs next, whether to loop
again, how many parallel branches to spawn, which path to take."
[^who-decides]: This reference, [1.2 Who Decides?](../foundations/who-decides.md): "It picks a
persona. The model chooses which kind of expert to reason as before it answers."
[^fanout-crossref]: This reference, [3.3 Orchestrator-Workers](../composition/fan-out.md): "it
hands the same input to a fixed set of personas and reconciles their views, so the model picks the
lens on the work and never the count of workers."
[^eo-crossref]: This reference, [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md):
"[3.5 The Specialist Panel] runs fixed personas over one input once and nothing revises."
[^carrier-bible]: `meta/carrier-bible.md`, §7: "For step 5 (content blocks) and anywhere
multi-persona reasoning appears, the three specialist personas are commerce ones... They reason
independently, then a reconcile step merges them."
[^homepage-map]: `docs/index.md`, the home-page architecture diagram: 3.5 is rendered as
`SP("3.5 Specialist Panel")`, a rounded mermaid node, the diagram's convention for "the model
decides," the same shape used for 3.3 and 3.4.
[^fanout-map]: This reference, [3.3 coverage map](fan-out.md), Out of scope: "Voting /
self-consistency is out entirely: it is a reliability/eval technique, not composition."
[^mast]: Cemri, M. et al., "Why Do Multi-Agent LLM Systems Fail?" (NeurIPS 2025, Datasets and
Benchmarks Track). The MAST taxonomy: 14 failure modes clustered into 3 categories (specification
and system design issues, inter-agent misalignment, task verification and termination), from 1,600+
annotated traces across 7 multi-agent frameworks. The abstract does not state a task count; an
earlier "200+ tasks" figure was removed 2026-09-07 after it could not be located in the paper. <https://arxiv.org/abs/2503.13657>;
proceedings: <https://papers.nips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html>
[^anthropic-bea]: Anthropic, "Building Effective Agents" (2024-12-19). Parallelization: "LLMs can
sometimes work simultaneously on a task and have their outputs aggregated programmatically."
Voting: "running the same task multiple times to get diverse outputs," instanced by "reviewing a
piece of code for vulnerabilities, where several different prompts review and flag the code if
they find a problem," and "evaluating whether a given piece of content is inappropriate, with
multiple prompts evaluating different aspects." <https://www.anthropic.com/research/building-effective-agents>
[^moa]: Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., Zou, J., "Mixture-of-Agents Enhances Large
Language Model Capabilities" (2024). A layered architecture where each layer's agents take every
prior-layer agent's output as auxiliary input; default proposers are heterogeneous open models
(Qwen1.5-110B-Chat, Qwen1.5-72B-Chat, WizardLM-8x22B, LLaMA-3-70B-Instruct, Mixtral-8x22B-v0.1,
dbrx-instruct). The aggregator "significantly outperforms LLM rankers" and "does not simply select
one of the generated answers... but potentially performs sophisticated aggregation." An ablation
comparing "single-proposer" (repeated sampling from one model at temperature 0.7) against
"multiple-proposer" (different LLMs) finds "using multiple different LLMs consistently yielded
better results." Leaderboard scores are snapshot and not repeated here; see the live source.
Open-source implementation: github.com/togethercomputer/moa. <https://arxiv.org/abs/2406.04692>
[^selfconsistency]: Wang, X. et al., "Self-Consistency Improves Chain of Thought Reasoning in
Language Models" (2022). Samples multiple reasoning paths from one prompt (no persona variation)
and selects the most consistent final answer by marginalizing over samples; a deterministic
vote/marginalization, not a model-rendered aggregation. <https://arxiv.org/abs/2203.11171>
[^debate]: Du, Y., Li, S., Torralba, A., Tenenbaum, J.B., Mordatch, I., "Improving Factuality and
Reasoning in Language Models through Multiagent Debate" (2023). N agents independently answer,
then see each other's responses and revise over multiple rounds (a standard setup: 3 agents, 2
rounds); debate, not a single-pass panel. <https://arxiv.org/abs/2305.14325>
[^divergent]: Liang, T. et al., "Encouraging Divergent Thinking in Large Language Models through
Multi-Agent Debate" (EMNLP 2024). Names the Degeneration-of-Thought (DoT) problem: once a model
commits to a stance, reflection alone cannot dislodge it even when wrong; proposes a "tit for tat"
debate with a managing judge. <https://arxiv.org/abs/2305.19118>
[^spp]: Wang, Z., Mao, S., Wu, W., Ge, T., Wei, F., Ji, H., "Unleashing the Emergent Cognitive
Synergy in Large Language Models: A Task-Solving Agent through Multi-Persona Self-Collaboration"
(NAACL 2024). Names its method Solo Performance Prompting (SPP): "given an input task, SPP first
generates a list of participants with different personas... we let the language model identify the
personas dynamically instead of manually defining them." States plainly that "cognitive synergy
only emerges in GPT-4 and does not appear in less capable models, such as GPT-3.5-turbo and
Llama2-13b-chat." One model, several personas simulated in sequence within a single multi-turn
context, not parallel independent calls. <https://arxiv.org/abs/2307.05300>
[^mad-limits]: Smit, A.P., Grinsztajn, N., Duckworth, P., Barrett, T.D., Pretorius, A., "Should we be
going MAD? A Look at Multi-Agent Debate Strategies for LLMs" (ICML 2024). Multi-agent debating
systems do not reliably outperform self-consistency or ensembling baselines; some MAD systems
(e.g. Multi-Persona) perform better only after hyperparameter tuning, suggesting sensitivity rather
than inherent superiority. <https://arxiv.org/abs/2311.17371>
[^mad-heterogeneity]: "Stop Overvaluing Multi-Agent Debate -- We Must Rethink Evaluation and
Embrace Model Heterogeneity" (submitted 2025-02-12, rev. 2025-06-21). Systematic evaluation of 5
MAD methods across 9 benchmarks and 4 foundation models: MAD often fails to outperform single-agent
Chain-of-Thought and Self-Consistency baselines despite far higher inference cost; proposes
Heter-MAD (heterogeneous foundation models) as a consistent fix. <https://arxiv.org/abs/2502.08788>
[^persona-null]: Zheng, M. et al., "When 'A Helpful Assistant' Is Not Really Helpful: Personas in
System Prompts Do Not Improve Performances of Large Language Models" (EMNLP Findings 2024). 162
roles across 6 relationship types and 8 expertise domains, tested against 2,410 factual questions
across 4 model families: adding any persona to a system prompt yields no accuracy gain on
fact-based QA, and usually slightly worsens it. <https://arxiv.org/abs/2311.10054>
[^selfpref]: Panickssery, A., Bowman, S., Feng, S., "LLM Evaluators Recognize and Favor Their Own
Generations" (NeurIPS 2024). Self-recognition ability correlates with self-preference bias. A
related but distinct finding from the judge-bias paper below, not a replication of it. Reused from
the 3.4 coverage map. <https://arxiv.org/abs/2404.13076>
[^judge-bias]: Zheng, L. et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS
2023, Datasets & Benchmarks track). Documents position, verbosity, and self-enhancement bias in LLM
judges. Reused from the 3.4 coverage map; disambiguated by full author list from Zheng, M. et al.
above, a different paper and a different Zheng. <https://arxiv.org/abs/2306.05685>
[^poll]: Verga, P. et al., "Replacing Judges with Juries: Evaluating LLM Generations with a Panel
of Diverse Models" (2024). A Panel of LLM evaluators (PoLL) of small models from different
providers beats a single large judge across six datasets, with reduced bias and cost.
<https://arxiv.org/abs/2404.18796>
[^owasp-agentic]: OWASP GenAI Security Project, "OWASP Top 10 for Agentic Applications" (2026
edition, announced 2025-12-09). ASI07 Insecure Inter-Agent Communication, ASI08 Cascading
Failures. <https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>
[^oai-orchestration]: OpenAI, Agents SDK docs, "Agent orchestration." "Agents as tools": "a manager
agent keeps control of the conversation and calls specialist agents through `Agent.as_tool()`,"
used "when a specialist should help with a bounded subtask but should not take over the
user-facing conversation," and "when you want one agent to own the final answer, combine outputs
from multiple specialists, or enforce shared SDK guardrails in one place."
<https://openai.github.io/openai-agents-python/multi_agent/>
[^oai-parallel]: OpenAI, developers.openai.com cookbook, "Parallel Agents with the OpenAI Agents
SDK." Four specialized agents (features, pros/cons, sentiment, recommendation) run concurrently via
`asyncio.gather` over one product review; a meta-agent combines their labelled outputs. States
plainly: "this notebook present[s] a toy example that you likely wouldn't parallelize in the real
world." <https://developers.openai.com/cookbook/examples/agents_sdk/parallel_agents>
[^adk-parallel]: Google, Agent Development Kit docs, "Parallel agents" (workflow agents).
`ParallelAgent` runs sub-agents concurrently, each in its own execution branch with no automatic
sharing of conversation history or state between branches; execution is deterministic and not
controlled by a model. <https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/>
[^adk-superseded]: Google, ADK docs (current): "Starting in ADK 2.0 for Python and Go, templated
workflows have been superseded by more flexible workflow structures, including graph-based
workflows and dynamic workflows." Verify which workflow style the reader's ADK version ships before
citing `ParallelAgent` as the current recommended shape. <https://adk.dev/agents/workflow-agents/parallel-agents/>
[^crewai]: CrewAI, "Agents" and "Crafting Effective Agents" docs. The `role` / `goal` / `backstory`
triad as a persona vocabulary; verify current process types (`Process.sequential` and hierarchical)
against the version the reader installs. <https://docs.crewai.com>
[^chatdev]: Qian, C. et al., "ChatDev: Communicative Agents for Software Development" (2023).
Named only, per item 2; not cited for a specific claim in this map. <https://arxiv.org/abs/2307.07924>
[^metagpt]: Hong, S. et al., "MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework"
(2023, ICLR 2024). Named only. <https://arxiv.org/abs/2308.00352>
[^camel]: Li, G. et al., "CAMEL: Communicative Agents for 'Mind' Exploration of Large Language
Model Society" (NeurIPS 2023). Named only. <https://arxiv.org/abs/2303.17760>
[^gulli-adp]: Gulli, A., *Agentic Design Patterns: A Hands-On Guide to Building Intelligent
Systems* (2025). Chapter 7, "Multi-Agent Collaboration," per the publisher's public table of
contents; full chapter text not independently read or verified this sweep.
[^ng]: Ng, A., public posts (2024) naming four agentic design patterns: Reflection, Tool Use,
Planning, and Multi-Agent Collaboration.
