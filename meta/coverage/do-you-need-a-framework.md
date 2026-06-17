# Coverage map: Do You Even Need a Framework? (chapter 1.6)

> Research-derived spec for what the chapter must cover so a reader can make the build-vs-buy call
> for an agentic system *honestly* — when a framework earns its place, when raw SDK calls are the
> better answer — and where to stop. Built from a 5-angle sweep (vendor primary docs, the framework
> landscape, the durable-execution value prop, the skeptical/lock-in read, practitioner build-vs-buy
> writeups). Review and trim the **Must-cover** list; that sets the chapter's scope.
> Bar: definitive but tight (the Gang-of-Four / Wikipedia test), not exhaustive.
>
> **This is a decision chapter, not a technique chapter.** It owns a *discipline* (build-vs-buy for
> agent plumbing), not a pattern. The decision discipline is durable; the specific tools are weather.
> Treat the tool landscape as mention-and-link to the appendices — do NOT freeze a feature matrix here.

## The mental model (what the reader must leave with)

An agent framework is an abstraction over plumbing you would otherwise write yourself — the tool/loop
glue, state and checkpointing, streaming, retries, observability hooks, and graph orchestration. It
costs you an abstraction to learn and debug, indirection, hidden control flow, and lock-in.

**AUTHOR-SIGNED STANCE (overrides the researcher's SDK-first default): framework-positive.** The
author's lived position, which is the chapter's thesis: *most teams shipping a real agentic system
should use a framework, and it is hard to name many situations where you genuinely shouldn't.* The
plumbing is real, you will rebuild it badly, and a framework that already solved it is usually the
right call. The author shipped on **LangGraph in production because its benefits earned it** — state,
checkpointing, graph orchestration — not because a demo used it. So the chapter does NOT lead with
"start with the raw SDK and avoid frameworks"; it leads framework-positive, then gives the honest
counter-view its fair hearing.

Crucially, the chapter must **fairly present the SDK-first camp** — Anthropic's *Building Effective
Agents* explicitly recommends starting with LLM APIs directly and warns that framework abstractions
"can obscure the underlying prompts and responses, making them harder to debug." Steelman it, then
resolve to the author's view: the cases where SDK-direct wins are narrow (a single agent calling one
or two tools, a throwaway, a team that must own every layer), and for most production systems the
framework pays. The one caution that survives intact: **never adopt a framework because a blog post
used it** — that's cargo-culting, and choosing *which* framework on evidence is the real skill.

## Must-cover (for an honest build-vs-buy call)

Ranked. Each: why it matters, the failure mode if skipped, maturity, lead citation. `[+]` = not yet in
the stub (the stub is skeleton-only, so all are `[+]`).

1. **The default, stated honestly: for a real production system, reach for a framework** `[+]` — the
   author's signed thesis (see AUTHOR-SIGNED STANCE). The plumbing is real and you'll rebuild it
   badly; a framework that solved it usually earns its place. Present the SDK-first counter-camp
   *fairly* (Anthropic, *Building Effective Agents*: "start by using LLM APIs directly"; the
   debugging-opacity caution) and steelman it, then resolve to the framework-positive read with the
   narrow exceptions named (single agent + one or two tools; throwaway; must-own-every-layer). *Skip
   it:* the chapter reads as the generic "you probably don't need a framework" take and loses the
   author's actual, contrarian, production-earned position. **Standard** (the build-vs-buy discipline;
   the *direction* of the default is the author's argued call, presented with both sides). (Anthropic
   for the counter-view; author's production experience for the resolution.)
2. **What a framework actually gives you** `[+]` — name the plumbing concretely so the value is legible:
   state management + **durable execution / checkpointing** (crash-resume, the "what happens when step 7
   fails" answer), streaming, retries, the tool/loop glue, observability hooks, and graph/handoff
   orchestration. *Skip it:* the decision is made on vibes; the reader can't tell what they'd be
   rebuilding. **Established.** (LangGraph checkpointer docs; durable-execution writeups; cross-framework
   landscape pieces.)
3. **What a framework costs you** `[+]` — an abstraction to learn and debug; indirection; **hidden
   control flow** (you can't see the prompts actually sent); lock-in (esp. cloud-coupled runtimes);
   version churn. *Skip it:* the reader buys the upside blind to the tax — the single most common
   regret in practitioner writeups. **Established / Contested** (the lock-in severity is disputed).
   (Anthropic: abstraction "can obscure the underlying prompts and responses, making them harder to
   debug"; practitioner accounts of fighting the abstraction.)
4. **The decision criteria (the heart of the chapter)** `[+]` — the honest axes: team familiarity; how
   much of the plumbing you'd otherwise rebuild (and would you rebuild it *well*); how non-standard
   your control flow is; how much you value owning the stack / avoiding lock-in; whether this is core
   to your product. Frame as a short reasoned checklist, not a scorecard. *Skip it:* the chapter
   diagnoses without prescribing. **Established / Standard** (build-vs-buy is timeless engineering).
   (Composio build-vs-buy framework; product/eng build-vs-buy writeups.)
5. **The rule: "adopt when the plumbing IS the framework's whole value"** `[+]` — the quotable
   heuristic that ties 1-4 together; the corollary that "a single agent calling one or two tools" is
   firmly SDK territory, and graph-shaped / multi-agent / durable control flow is where a framework
   starts to pay. *Skip it:* the reader has criteria but no crisp default to anchor on. **Standard.**
   (Anthropic; landscape consensus pieces.)
6. **Don't cargo-cult the framework (the anti-pattern)** `[+]` — the named failure this chapter feeds
   to the Anti-Patterns Catalog: adopting LangGraph (or any framework) because a blog/demo used it,
   not because the decision criteria pointed there. Also: "frameworks make it tempting to add
   complexity when a simpler setup would suffice." *Skip it:* the chapter loses its sharpest, most
   shareable point. **Standard** (as a caution). (Anthropic; "thin wrappers over provider APIs + MCP"
   trend.)
7. **A thought-leader comparison: LangGraph vs CrewAI** `[+]` — AUTHOR-REQUESTED, in-chapter (not just
   pointed away). Take an opinionated, credible position contrasting the two most representative
   choices: **LangGraph** (graph-first, explicit state and checkpointing, low-level control — what the
   author shipped on) versus **CrewAI** (role/crew-first, higher-level multi-agent abstraction, faster
   to stand up, less control). Say what each is *for*, who should pick which, and why — a real call,
   not a both-are-great survey. Keep it prose-first (the design system bans scorecard/radar visuals); a
   small honest trade-off table is acceptable if it stays a few rows, not a feature matrix. **This is
   the chapter's most perishable content, so fence it hard:** open with an explicit "this comparison is
   a snapshot and *will* change — re-decide on current evidence" disclaimer, carry a **"Last reviewed
   2026-06"** stamp, and route the exhaustive/live matrix to the appendices. Name the other categories
   in one line each (vendor Agents SDKs; cloud-coupled stacks Google ADK / AWS Bedrock AgentCore /
   Microsoft Agent Framework; durable-execution engines Temporal/Inngest; AutoGen) but spend the
   comparison budget on LangGraph-vs-CrewAI. *Skip it:* the chapter ducks the concrete call the reader
   actually came for. **Emerging / weather** (the tools); the *decision* is durable, the *verdict*
   dates. (Live framework docs — re-verify every capability claim at write time; see Sources.)
8. **From production: why we chose LangGraph** `[+]` — AUTHOR-PROVIDED grounding. A short *From
   production:* callout: the author shipped a real agentic system on LangGraph and it earned its place
   on its benefits — explicit state, checkpointing/durable execution, graph orchestration — chosen on
   the decision criteria above, not because a demo used it. This is the chapter practicing the
   discipline it preaches: a framework adopted for legible reasons. **Confidentiality:** describe the
   *benefits that drove the choice*, framed in carrier-world terms; no domain-specific framing beyond
   what the chapter already establishes, and no real fingerprint. The scrubber must clear this callout.
   *Skip it:* the framework-positive thesis reads as opinion with no skin in the game. **n/a** (a
   grounded stance). (Author production experience; DECISIONS.md.)

## Mention-and-link (one line, a pointer, not a section)

- **Live framework comparison / feature matrix** → Appendix **D. State of Play 2026** (disposable, dated)
  and Appendix **C. Decision Frameworks** (the framework-choice guide). This chapter argues the
  *decision*; the appendices hold the *perishable specifics*.
- **Workflow vs. agent** (whether you even need agentic control flow at all) → 1.3 Workflow or Agent?
  (Decide *that* before you decide *how to build it*.)
- **The augmented LLM as the base unit** the SDK gives you for free → 1.4 The Augmented LLM.
- **What checkpointing/durable execution actually is** as a reliability technique → 7.3 Checkpointing.
- **Tool/loop plumbing** the framework wraps → 2.1 Tool Use; **MCP** as the connectivity layer that is
  increasingly the thin-wrapper alternative to a heavy framework → 2.4 MCP.
- **Observability hooks** vs. rolling your own tracing → 8.1 Observability.
- **Multi-agent orchestration** (a major reason teams reach for a framework) → 9.2 Multi-Agent.
- **Context economy note:** a framework's prompt templates and injected scaffolding ride in the context
  window and can bloat it invisibly — a hidden cost of indirection; depth in 1.5 Context Engineering.

## Out of scope (name it, point out)

- **A framework tutorial / how to use LangGraph.** This chapter decides *whether*, not *how*. Building
  with the chosen tool is the rest of the book (the companion code teaches LangGraph by example).
- **A frozen feature-by-feature comparison table** → Appendix D (dated) / Appendix C.
- **Durable-execution mechanics** (replay, event history) → 7.3 Checkpointing.
- **Multi-agent framework deep-dives** → Part IX.
- **N parallel framework codebases.** Per DECISIONS.md, the companion code is LangGraph-only; "other
  framework" is prose asides + one bake-off, not maintained parallel implementations.

## Maturity summary

- **Standard:** the build-vs-buy *discipline* itself; the cargo-cult caution (never adopt because a
  demo used it). The chapter's framework-positive *default* is the author's argued call (presented
  with the SDK-first counter-camp steelmanned), not a neutral fact — label it as a reasoned position.
- **Established:** the named costs (abstraction tax, hidden control flow, debugging cost); the named
  benefits (state/checkpointing, streaming, retries, orchestration); the decision criteria.
- **Emerging / weather:** every specific tool and its current capabilities; the vendor-SDK-vs-framework
  balance (shifting as SDKs absorb framework features) — carries the "Last reviewed" stamp.
- **Contested:** how severe framework lock-in really is (cloud-coupled runtimes vs. portable
  frameworks); whether "no framework, thin wrappers + MCP" is the new default or a phase; any claim
  that one framework is "production-ready" and others aren't.

## Sources

Vendor / primary: Anthropic, *Building Effective Agents*
(anthropic.com/research/building-effective-agents) — the load-bearing primary source for the
SDK-first default and the abstraction/debugging caution (quote it directly, not a blog about it).
LangGraph durable-execution / checkpointer docs (langchain-ai.github.io / langchain docs). Durable
execution: Inngest "Durable Execution: The Key to Harnessing AI Agents in Production"; Temporal +
Agents-SDK integration writeups. Build-vs-buy: Composio "Build vs. buy AI agent integrations: a 2026
decision framework"; ProductSchool / Hatchworks build-vs-buy framings. Landscape (dated, for
categories only — link, do not hardcode): O'Reilly Radar "The AI Agents Stack (2026 Edition)";
JetBrains "Top Agentic Frameworks 2026"; Firecrawl "Best open source agent frameworks 2026";
cross-framework comparisons (LangGraph / OpenAI Agents SDK / Google ADK / AWS Bedrock / Microsoft
Agent Framework / CrewAI / AutoGen). Skeptical read: practitioner accounts of "fighting the
abstraction" and migrating to thin wrappers over provider APIs + MCP. Project: DECISIONS.md
(LangGraph as pragmatic stack match; not an endorsement), carrier-bible.md.

> **Verify before quoting:** every tool name, capability, and "who has feature X" claim is volatile —
> re-verify against the live appendices and primary docs at write time, and re-stamp "Last reviewed".
> The Anthropic quotes are stable; the landscape is not. Cite the finding and the live source, never a
> frozen feature matrix or version number.

## Open questions for the author

All RESOLVED by author sign-off (2026-06-17):
1. **Code:** NO companion code. Conceptual decision chapter; the LangGraph-vs-CrewAI contrast is prose,
   not a tested snippet.
2. **How explicit about LangGraph?** Name it plainly — LangGraph and CrewAI are the in-chapter
   thought-leader comparison (item 7), and the *From production:* callout (item 8) names LangGraph as
   the production choice.
3. **Decision criteria — checklist vs. prose?** Prose-first, argued. A small honest trade-off table is
   allowed for the LangGraph/CrewAI contrast only if it stays a few rows; no scorecard/radar.
4. **Default direction:** framework-positive (author override). Frameworks usually earn their place;
   SDK-first is the fairly-presented counter-view with narrow exceptions. Not a both-sides wash.
5. **War story:** YES — *From production:* the author shipped on LangGraph because its benefits earned
   it (item 8). Frame on the benefits that drove the choice; scrub all real-product fingerprints.
6. **Perishability:** the LangGraph/CrewAI verdict is fenced with a "this will change, re-decide on
   current evidence" disclaimer + "Last reviewed 2026-06" stamp.
