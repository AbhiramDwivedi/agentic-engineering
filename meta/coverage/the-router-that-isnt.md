# Coverage map: Front Controller (chapter 3.2)

> Research-derived spec for what the chapter must cover to let a reader (a) build a static
> dispatch table correctly and (b) recognize genuine LLM routing when it's the right tool,
> without ever confusing the two. Built from a 5-angle sweep (vendor/primary docs, academic +
> benchmarks, security/failure modes, practitioner writeups/libraries, the skeptical read); see
> "Sweep angles" below for what each surfaced and what came up thin. The chapter path is a stub
> with no real prose yet (headings only), so nothing below is marked `[*]`/`[+]` against existing
> text — this is a fresh map, and the stub's inherited "Maturity: Standard" line should not be
> taken as settled; see item 1 and Maturity summary. Review and trim the **Must-cover** list; that
> sets the chapter's scope. Bar: definitive but tight (the Gang-of-Four / Wikipedia test), not
> exhaustive. **Deliberate exception to the usual ≤10 rule:** this chapter is the reference's only
> home for genuine LLM routing (no sibling chapter owns it), so it knowingly carries both litmus
> sides — the deflation (code decides) and the thing the deflation is often mistaken for (model
> decides) — in one page. Flagged as an open question below rather than assumed.

## The mental model (what the reader must leave with)

Two things get called "routing" in an agentic system, and only one of them is a decision. A
static dispatch table takes a label the caller already supplied — an event type, a message
kind — and looks up the handler that owns it; there is no judgment call anywhere in that path,
your code decided the whole thing at the moment it wrote the table. Genuine routing, the
workflow Anthropic actually named, starts from *unlabeled* input and spends a model call (or a
classifier) deciding which category it belongs to before anything else happens — a real
decision, made fresh on every request. The two look identical in a design review ("the router
picks the path") and cost, fail, and test in opposite ways: one is a `dict` lookup you unit-test
in milliseconds, the other is a non-deterministic call you eval like any other model output. The
reader should leave knowing which one they're looking at in five seconds, in any codebase,
regardless of what the function happens to be named — "router" tells you nothing; what's inside
the function does.

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation. All items are `[+]`
gaps against the current stub, which has no prose yet.

1. **The three-way split, defined precisely: no classifier / non-LLM classifier / LLM
   classifier** `[+]` — the chapter's spine claim, and it must be exact or it breaks two things at
   once. Anthropic defines routing as classifying an input and directing it to a specialized
   follow-up, with the classification "handled either by an LLM or a more traditional
   classification model/algorithm"; Gulli's independent definition allows an LLM-based,
   embedding-based, rule-based, or ML-model-based classifier. Both authorities agree the
   classifier need not be a model at all, let alone an LLM. So the correct deflation is not
   "routing needs an LLM" — it's sharper: **a static dispatch table has no classifier of any
   kind**, because the caller already supplied the label. That gives three buckets, not two: (a)
   no classifier — a dispatch table, pure code-decides; (b) a non-LLM classifier (embedding
   similarity, a trained ML model, a rules engine) — satisfies Anthropic's and Gulli's definition
   of "routing," but by *this reference's* litmus is still code-decides, because the augmented LLM
   never exercises judgment in the decision; (c) an LLM classifier — the only bucket that is
   genuinely new by the litmus, because the model itself makes the call. Bucket (b) is the one
   the chapter must get right or it either over-credits semantic-router-style tools as "agentic"
   or under-credits them as "just a dispatch table" — neither is accurate. *Skip it:* the chapter
   repeats the exact mislabel it exists to cure, or invents a new one in the other direction.
   **n/a** (definitional; the techniques in each bucket carry their own verdicts, see Maturity
   summary). (Anthropic, "Building Effective Agents," 19 Dec 2024; Gulli, *Agentic Design
   Patterns*, Ch. 2; this reference's own litmus, [1.2 Who Decides?](../foundations/who-decides.md).)
2. **The confusable-neighbours comparison** `[+]` — a hard requirement, and the chapter's most
   load-bearing table. At minimum: **front controller / dispatch** (code decides; decision made
   once, at table-authoring time, not per request; use when the label already exists) ·
   **embedding / semantic routing** e.g. the `semantic-router` library (code decides via a trained
   artifact; decision made per request by similarity search, no LLM call; use when categories are
   stable and you want routing latency near-zero without paying for a model call) · **LLM routing
   / intent classification** (model decides; one classification call up front, then control passes
   to a specialized handler; use when categories are fuzzy, evolving, or need natural-language
   judgment) · **tool use** (model decides, but repeatedly — a fresh choice on every turn inside a
   running conversation, not a one-time upfront split; → 2.1) · **skill selection** (model decides,
   but with *no separate classifier step at all* — the model reads a capability catalog inline and
   self-selects mid-response; → 2.3, which explicitly documents "selection is a catalog, not a
   router") · **agent handoffs** (OpenAI Agents SDK / Swarm-style transfer of control — model
   decides, implemented as a special tool call from *inside* a running agent, not an upfront split
   by an outside classifier; carries full conversation history to the new agent; → 9.2) ·
   **orchestrator-workers** (model decides, but the decision is *how many* workers and how to
   decompose the task, not *which one* branch to take; → 3.3) · **model cascading / cost routing**
   e.g. RouteLLM (routes between model *tiers* by predicted difficulty/cost, not between task
   *categories*; a production-cost concern, not a control-flow pattern; → 8.4). *Skip it:* this is
   the author-flagged confusion the chapter exists to resolve; without the table, readers keep
   reaching for the wrong pattern name in design reviews. **n/a** (comparison). (Composite of all
   sources below; the "router" naming trap in item 3 is the sharpest single example.)
3. **The "router" naming trap in code** `[+]` — a function's name never tells you which side of
   the litmus it's on. LangGraph's own `add_conditional_edges()` calls its callback a "router
   function" no matter what's inside it — the function can be a pure code-decided branch (e.g.
   this reference's own [3.1 Prompt Chaining](prompt-chaining.md) example,
   `route_after_gate`, which branches on a validation-error field with no classification at all)
   or a wrapper around an LLM classification call. Same keyword, opposite litmus answer. *Skip
   it:* a reader or contributor sees "router"/"route_*" in a codebase and assumes it's the
   genuinely-new pattern, when most `route_*` functions in production graphs are gates wearing a
   router's name. **n/a** (naming discipline). (LangGraph docs, "Graph API overview," conditional
   edges / router functions; this repo's own `route_after_gate`.)
4. **Static dispatch: the how, and the failure-return contract** `[+]` — the shape: a pre-labeled
   event or message arrives, a `dict`/`match` maps the label to a handler or subgraph; O(1),
   free, deterministic, unit-testable. The contract that's easy to skip: an unrecognized key must
   hit an explicit default/deny branch — logged, returned as a structured error — never a silent
   no-op or an uncaught `KeyError`; if the key originates from untrusted input, validate it before
   the lookup and never build the dispatch dynamically (`getattr`/`eval` on an attacker-influenced
   string). *Skip it:* unknown event types vanish with no trace, or a crafted key reaches code it
   was never meant to reach. **Standard** (the dispatch-table idiom predates "agentic" by decades;
   used in interpreters, event loops, and web frameworks alike). (Fowler, *Patterns of Enterprise
   Application Architecture*, "Front Controller"; Alur/Crupi/Malks, *Core J2EE Patterns*, "Front
   Controller" — both web-tier HTTP-request patterns, the closest named catalog entries but a
   generalization when applied to a generic event-type table; see naming note under Sources.)
5. **LLM routing: the how, and the failure-return contract** `[+]` — the shape: unlabeled input
   arrives, a model (or a classifier) reads it and emits a category, a second step runs that
   category's specialized prompt/tools; Anthropic notes the follow-up task can be a single call or
   a multi-step chain. The failure contract this pattern needs and easily skips: a named
   fallback/default route for low-confidence or off-taxonomy input, rather than forcing the
   classifier to guess — surface "not sure which category" as a structured signal, not a silent
   best-effort pick, and gate low-confidence routes behind a human. *Skip it:* every input gets
   forced into some category even when none fits, and the specialized handler downstream is
   working from a wrong premise with no error anywhere in the trace. **Established** (a named,
   vendor-documented workflow, in wide production use for support/triage systems). (Anthropic,
   ibid.; Gulli, ibid.; OpenAI, "A Practical Guide to Building Agents" — the "manager pattern,"
   where a central LLM delegates to specialist agents via tool calls, a routing-adjacent variant;
   → [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md) for the escalation path.)
6. **Cost and context economy: dispatch is free, routing pays every time** `[+]` — this is the
   deflation's sharpest edge, sharper than "it's not agentic": a dispatch table costs zero tokens
   and zero round trips, full stop. LLM routing pays a model call on every single request just to
   decide where to go, and the category list fed to the classifier scales the same way tool
   schemas do — more categories, more tokens, more chances to misclassify, the same ceiling
   pressure as 2.1's tool-count problem. Model cascading (routing between cheap and expensive
   *model tiers* rather than between task categories) is the cost-driven cousin of this same
   mechanism. *Skip it:* a team bolts an LLM classification pass onto a system that had a
   perfectly adequate static dispatch table, paying latency and money for a decision that never
   needed making. **Standard** (dispatch is free); **Emerging** (cost-aware model-cascading
   routing as a first-class technique — the benchmarks below are all roughly 2024-2025, still an
   active research area with no consensus default router). (RouteLLM, arXiv:2406.18665; Hybrid
   LLM, arXiv:2404.14618, ICLR 2024; RouterBench, arXiv:2403.12031; FrugalGPT, arXiv:2305.05176;
   → [8.4 Controlling Cost](../production/controlling-cost.md) for the depth.)
7. **Security: the dispatch key and the routing decision are both attack surface** `[+]` — two
   distinct risks when the input is untrusted (a webhook payload, a user message). For static
   dispatch: dynamic/`eval`-based dispatch on an attacker-influenced string is an old,
   non-LLM-specific code-injection risk — validate the key against a known set before lookup, and
   never build the branch dynamically from raw input. For LLM routing: a crafted input can try to
   steer the classifier into a higher-privilege or wrong-tenant handler, a confused-deputy-shaped
   risk; if a route grants elevated tools or data access downstream, that is exactly OWASP's
   Excessive Agency shape, not a new category. *Skip it:* a malformed or malicious input reaches a
   handler it should never reach, either by code injection (dispatch) or by fooling the classifier
   (routing). **Standard principle** (validate untrusted input, least privilege per-handler); the
   LLM-routing-specific manipulation risk itself is **thin evidence** — this sweep found no
   dedicated benchmark or incident writeup naming "routing hijacking" as a studied phenomenon, only
   the general OWASP categories it falls under; say so plainly rather than force a citation that
   doesn't exist yet. (OWASP Top 10 for LLM Applications 2025 — LLM01 Prompt Injection, LLM06
   Excessive Agency; → 4.4 Guardrails & Safety, → 8.5 Locks, PII & Identity for tenant isolation.)
8. **The reliability reality: misrouting is silent, and the accuracy/cost trade-off is real and
   still moving** `[+]` — a crashed dispatch is loud and obvious (an exception, a 500); a
   misrouted request is not — it looks like a normal answer from the wrong specialist, no
   exception anywhere, just the wrong prompt and tools engaged on a plausible-looking response.
   The benchmarks that measure router accuracy against cost (RouterBench, Hybrid LLM) show this
   trade-off is real and quantifiable, not solved: no single router wins on both axes today.
   *Skip it:* a team ships LLM routing and only discovers misclassification through downstream
   complaints, because nothing in the pipeline ever flags "this went to the wrong specialist."
   **Established** (misrouting-is-silent as a structural fact); **Emerging** (the specific
   accuracy/cost trade-off curves, which shift with every new model generation and have no settled
   benchmark leader). (RouterBench, arXiv:2403.12031; Hybrid LLM, arXiv:2404.14618; →
   [4.2 Evaluation](../craft/proving-it-works.md) for building a labeled eval set on the
   classifier itself.)

## Mention-and-link (one line, a pointer, not a section)

- **Tool use** — a per-step, repeated model decision inside a running turn, not routing's one-time
  upfront split → [2.1 Tool Use](../the-unit/tool-use.md).
- **Skill selection** — the model self-selects from a capability catalog inline, no separate
  classifier at all → [2.3 Skills](../the-unit/skills.md).
- **Orchestrator-workers** — the model decides *how many* workers and how to decompose, a
  different structural decision than picking one branch → [3.3 Orchestrator-Workers](fan-out.md).
- **Agent handoffs / multi-agent** — OpenAI Agents SDK / Swarm-style transfer of control via a
  special tool call from inside a running agent, full treatment lives elsewhere →
  [9.2 Multi-Agent](../frontier/more-than-one-agent.md).
- **Model cascading / cost-aware routing** — routing between model tiers by predicted
  difficulty/cost, a production-cost concern → [8.4 Controlling Cost](../production/controlling-cost.md).
- **Human-in-the-loop escalation** — the gate for low-confidence routing decisions →
  [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md).
- **Evaluation** — building a labeled accuracy eval for the classifier, same discipline as any
  model-judged step → [4.2 Evaluation](../craft/proving-it-works.md).
- **Guardrails** — confidence thresholds and default-deny handling as a guardrail instance →
  [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md).
- **Framework mechanics** — LangGraph `add_conditional_edges` / router functions, OpenAI Agents
  SDK `handoff()`: cite the shape, teach via the multi-provider code tabs, not a framework tour.

## Out of scope (name it, point out)

- Building a custom ML/NLP intent classifier from scratch (pre-LLM traditional classification) —
  Anthropic and Gulli both allow it as a routing classifier; cite that it's allowed, don't teach it.
- Deep multi-agent handoff architectures and swarm topologies → 9.2 Multi-Agent, 9.1 Autonomous
  Agents (planned).
- Model-cascading algorithm internals and RouteLLM's training methodology → 8.4 Controlling Cost.
- MCP-level tool/resource routing → 2.4 MCP.
- Framework-specific API surfaces in depth (LangGraph's exact `add_conditional_edges` signature,
  Agents SDK's `handoff()` parameters) → vendor docs; this chapter shows the shape via the
  multi-provider tabs only.
- The full web-tier Front Controller pattern as Fowler/Core J2EE originally scoped it (HTTP
  request dispatch, servlets, view resolution) — cite the provenance for the name, don't teach
  web-tier mechanics this reference has no other use for.

## Maturity summary

- **Standard:** the static dispatch table as a technique (decades-old CS idiom); validating
  untrusted keys before lookup; least privilege per-handler.
- **Established:** LLM-based routing/classification as a named, vendor-documented workflow
  (Anthropic Routing); non-LLM classifiers (embedding similarity, rule-based, traditional ML) as a
  routing technique — proven and in production, just not "genuinely new" by this reference's
  litmus, since no LLM judgment is exercised.
- **Emerging:** cost-aware model-cascading/routing between model tiers (RouteLLM, Hybrid LLM,
  RouterBench — all roughly 2024-2025, active research, no consensus default router yet);
  adversarial robustness of LLM/semantic routers against injection-steered misrouting — thin
  evidence base, reasoned from OWASP categories rather than a dedicated benchmark.
- **Contested:** billing a static dispatch table as "intelligent routing" or "agentic" — the
  deflation this chapter exists to correct, already named "Fake routing" in the
  [Anti-Patterns Catalog](../catalogs/anti-patterns.md); "agent handoffs" marketed as more
  than an orchestrator with workers (echoes 9.2 Multi-Agent's own Contested verdict).

## Sources

Vendor/primary: Anthropic, "Building Effective Agents" (19 Dec 2024,
anthropic.com/research/building-effective-agents) — the Routing workflow definition and the
LLM-or-traditional-classifier allowance. OpenAI, "A Practical Guide to Building Agents" (April
2025) — the manager vs. decentralized (handoff) patterns. OpenAI Agents SDK, "Handoffs"
(openai.github.io/openai-agents-python/handoffs/) — handoffs implemented as tools, full
conversation history transfer. LangChain/LangGraph docs, "Graph API overview"
(docs.langchain.com/oss/python/langgraph/graph-api) — conditional edges and router functions.
Software-architecture provenance for the chapter's current name: Fowler, *Patterns of Enterprise
Application Architecture*, "Front Controller" (martinfowler.com/eaaCatalog/frontController.html) —
"a controller that handles all requests for a Web site," a web-tier pattern; Alur, Crupi, Malks,
*Core J2EE Patterns* (Sun Microsystems, 2001) — Front Controller as a centralized J2EE request
handler, predating or contemporaneous with Fowler's catalog entry, also web-tier. Academic /
benchmarks: RouteLLM, Ong et al., arXiv:2406.18665; Hybrid LLM: Cost-Efficient and Quality-Aware
Query Routing, Ding et al., arXiv:2404.14618 (ICLR 2024); RouterBench, Hu et al., arXiv:2403.12031;
FrugalGPT, Chen, Zaharia, Zou, arXiv:2305.05176. Gulli, *Agentic Design Patterns* (Springer Nature,
2025; ISBN 9783032014016), Ch. 2 Routing — reused from this reference's own 1.2 citation; verify
exact wording against the print edition before quoting. Practitioner / library: aurelio-labs,
`semantic-router` (github.com/aurelio-labs/semantic-router) — embedding-based routing via kNN over
route utterances, the concrete example for bucket (b) in item 1. Security: OWASP Top 10 for LLM
Applications 2025 (genai.owasp.org/llm-top-10) — LLM01 Prompt Injection, LLM06 Excessive Agency.
Internal: [1.2 Who Decides?](../foundations/who-decides.md) (the litmus, the dispatcher
deflation already stated there in brief — this chapter is its "full treatment," per 1.2's own
forward link); [3.1 Prompt Chaining coverage map](prompt-chaining.md) (already commits "a chain
that picks its next step from a classifier is 3.2's pattern wearing a chain's clothes"); the
[Anti-Patterns Catalog](../catalogs/anti-patterns.md) ("Fake routing" entry, already live).

> **Verify before quoting:** RouteLLM's, Hybrid LLM's, and FrugalGPT's specific cost-savings
> percentages are benchmark-specific and rot fast (new model releases shift every curve); cite the
> finding — a router can trade cost for quality along a real, measurable curve — not a frozen
> number. Gulli's exact wording needs re-verification against the print edition (an inherited
> caveat from 1.2's own coverage map). The Fowler/Core J2EE "Front Controller" citations are stable
> (both are long-published, unrevised primary sources) but confirm the naming decision below before
> citing them as if the chapter's subject matches their scope one-to-one — it doesn't, and the
> chapter should say so rather than imply it. The router-security claim in item 7 has no dedicated
> primary source; if the fact-checker or author knows of a routing-specific injection incident or
> paper, upgrade the citation — as written it is reasoned from OWASP's general categories only.
> *(Resolved at Stage 4: the fact-check found a dedicated literature — "Rerouting LLM Routers,"
> arXiv:2501.01818, and "RerouteGuard," arXiv:2601.21380 — both verified against arXiv and now
> cited in the chapter's Gotchas. They target model-tier/cost routers, so the confused-deputy
> risk for task-category classifiers remains reasoned from OWASP; the chapter says so.)*

## Open questions for the author

- **Naming: keep "Front Controller," or retitle?** The nav title is "Front Controller"; the slug
  `the-router-that-isnt` and the gloss line already carry the "router" hook regardless of what the
  canonical noun is (the design system separates the two: H1/nav gets the boring precise noun, the
  evocative phrase lives in the gloss). Three options, with evidence:
  - **A — Keep "Front Controller."** *For:* it's a real, named pattern (Fowler's PoEAA, Core J2EE
    Patterns) with an "also called: dispatcher" line already in the stub; five existing pages
    already link to this chapter using the text "Front Controller" (who-decides.md ×3,
    quick-reference.md, anti-patterns.md, glossary.md), so keeping it costs nothing to update.
    *Against:* both Fowler's and Core J2EE's Front Controller are specifically web-tier, HTTP
    request-dispatch patterns (a single entry point for a *website*); this chapter's subject — an
    event-type-to-handler-graph table with no HTTP involved — is a generalization of that name, not
    a literal instance. A reader who looks up Fowler's actual definition may feel the term is
    stretched.
  - **B — Retitle to "Routing" (bare).** *For:* highest search/discoverability value — this is the
    term of art (Anthropic's own workflow name, RouteLLM, semantic-router, "LangGraph router
    function," "OpenAI routes requests to..."); it's what a practitioner actually types into a
    search bar. *Against:* self-undermining as a nav noun — a chapter titled "Routing" whose
    plurality of content is "this isn't routing" reads oddly as an H1, even though the design
    system's gloss-line mechanism is built to absorb exactly this kind of irony. Also risks
    implying the chapter is primarily about the LLM-routing workflow, when the deflation (static
    dispatch) is the load-bearing half.
  - **C — Retitle to "Routing & Dispatch" (recommended).** *For:* names both halves the chapter
    actually teaches, honestly and searchably, without overclaiming either one; "Front Controller"
    and "dispatcher" move to the "also called" line, preserving Fowler/Core J2EE provenance and
    keeping the existing internal link *text* reasonably close (a copy-edit, not a broken link,
    since links point at the slug/path, not the title); precedent for compound canonical nouns
    already exists in the nav ("Orchestrator-Workers"). *Against:* two-noun titles are otherwise
    rare in the current nav (one precedent, not a norm); a small sweep of ~5 pages' link *text*
    ("Front Controller" → whatever prose fits) is still a real, if minor, edit cost.
  - **Recommendation: C, "Routing & Dispatch."** It's the only option that doesn't require the
    chapter to either overclaim (bare "Routing") or undersell (bare "Front Controller," which
    buries the LLM-routing half this chapter uniquely owns) half of its own required content.
- **Does item 7 (security) earn its own "Security & trust" section?** The design system's
  controlled-extension menu allows promoting a real trust-boundary concern out of Gotchas into its
  own named section. The dispatch-key-injection risk is well-established and Standard; the
  LLM-routing-manipulation risk is real in principle but thin in evidence (no dedicated citation
  found this sweep). Recommend keeping it inside Gotchas/must-cover prose rather than promoting it,
  given the evidence is currently reasoned rather than sourced — but flag for reconsideration if the
  fact-checker turns up a stronger citation.
- **One shape diagram, or two?** The design system mandates "every pattern chapter carries one
  shape diagram in How," in the shared visual language (rounded = model decides, rectangle = your
  code decides). This chapter is the first to deliberately teach patterns on *both* sides of that
  language in one page. Does it get one diagram containing both shapes side by side (a dispatch
  rectangle next to a routing-call rounded node, visually contrastive), or does the "one diagram"
  rule bend here? Recommend one diagram, both shapes, explicitly contrastive — but this is a
  chapter-writer/design call, flagging so it isn't decided by default.
- **The lens line, for a two-sided verdict.** The stub's current lens line reads a single
  "Maturity: Standard" with a parenthetical aside. Given item 1's three-way split, does the lens
  line need to state two verdicts explicitly (e.g. "Standard (static dispatch) · Established (LLM
  routing)"), or does the parenthetical-aside format already in the stub cover it well enough? This
  may be a first precedent for the design system's lens-line format — worth a deliberate call
  rather than an inherited default.
- **Scope: is spanning both litmus sides in one chapter the right call, or does LLM routing want
  its own future page?** The chapter deliberately breaks the reference's usual per-chapter
  single-litmus-side pattern because no sibling chapter owns LLM routing. Confirm this is
  intentional and durable, not a temporary state — if the reference later wants a dedicated
  "Routing" chapter under a different part (e.g. alongside 3.3-3.5's genuinely-new patterns), this
  map's items 1, 2, 5, 6, 8 would need to move with it.
