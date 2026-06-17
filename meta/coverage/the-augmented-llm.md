# Coverage map: The Augmented LLM (chapter 1.4)

> Research-derived spec for what the chapter must cover to leave a reader holding the *base unit*
> every later pattern composes — a model plus tools, plus a structured-output contract, plus
> (sometimes) retrieval/memory — and the graph/state substrate that unit runs on. Built from a
> 3-angle sweep (vendor/primary docs, framework docs, practitioner/skeptical read). Security and
> deep benchmark angles were **deliberately light** here: this is a framing-leaning concept
> chapter that *assembles* the unit; the failure modes and benchmarks live in the chapters that
> own each part (2.1 Tool Use carries the OWASP + tau-bench load). Review and trim **Must-cover**;
> that sets scope. Bar: definitive but tight (the Gang-of-Four / Wikipedia test), not exhaustive.

## The mental model (what the reader must leave with)

Every agentic system in this reference is built from one repeating atom: a model call, *augmented*
with the things a bare model lacks — tools to reach outside its weights, a structured-output
contract so its result is something code can act on, and optionally retrieval and memory to widen
what it knows. That atom is Anthropic's "augmented LLM." It does not run in a vacuum: it sits in a
**node on a state graph**, where the node reads the current state, calls the augmented unit, and
returns an enriched state for the next node. Patterns later in the book (chaining, fan-out,
evaluator-optimizer, the panel) are just *arrangements of this same node*. Get the unit and the
substrate, and everything downstream is composition. The chapter assembles the unit and points
forward to where each augmentation is taught; it does not teach any augmentation in depth here.

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation. `[*]` = the stub head
already asserts it; `[+]` = to write.

1. **The definition: model + augmentations** `[+]` — the augmented LLM is a bare model plus
   *tools* (reach outside the weights), a *structured-output contract* (a result code can trust),
   and *optionally* retrieval and memory. Name all four; mark which are load-bearing (tools +
   contract) vs. optional (retrieval, memory). *Skip it:* the reader treats "a model" and "an
   agentic unit" as the same thing and never sees what makes the unit composable. **Standard.**
   (Anthropic, *Building Effective Agents* — "the basic building block … an LLM enhanced with
   augmentations such as retrieval, tools, and memory.")
2. **This is the atom everything composes from** `[+]` — every later pattern (Part III
   composition, the craft chapters) is an *arrangement of this one unit*, not a new primitive.
   State the through-line explicitly so the reader reads the rest of the book through it. *Skip it:*
   each later pattern reads as a fresh invention; the spine's "it's still engineering" thesis
   loses its mechanical anchor. **Standard** (the framing). (Anthropic, *Building Effective
   Agents*; cross-ref 1.1 It's Still Engineering, 1.2 Who Decides?)
3. **The graph/state substrate — the runtime model the whole reference assumes** `[+]` — a node
   reads state, calls the unit, returns an *enriched* state; edges sequence nodes; this is the
   runtime every chapter quietly stands on. Define node / state / edge at the depth needed to read
   later diagrams, no more. *Skip it:* later mermaid diagrams and the "nodes on a graph" language
   have no home; the reader can't place where a pattern runs. **Standard** (state-graph as the
   common substrate). (LangGraph Graph API: nodes are functions that take state and return a
   partial update; state has a schema + reducers. Note this as *one* concrete instance of a
   general model, not the only framework.)
4. **The augmentation map — where each part is taught (mention-and-link, not taught here)** `[+]` —
   tools → 2.1, structured output → 2.2, retrieval → 5.2, memory → 5.3, context/the window → 1.5,
   state vs. memory → 5.1. One sentence each, as forward pointers. *Skip it:* the chapter either
   balloons into re-teaching its four siblings, or leaves the reader not knowing where to go next.
   **n/a** (navigation). (Internal cross-refs; respect the spine.)
5. **The maturity call, argued** `[+]` — argue **Standard**: the augmented LLM as the base unit is
   the accepted default — Anthropic names it the basic building block, every major vendor SDK ships
   the augmentations as first-class, and the dominant orchestration frameworks (LangGraph et al.)
   are built on the state-graph-of-nodes model. *Skip it:* the chapter asserts a tier the
   fact-checker can't re-derive. **Standard.** (Anthropic *Building Effective Agents*; vendor SDKs;
   LangGraph state-graph docs.)
6. **The litmus reading: the unit is where "who decides" gets concrete** `[+]` — inside the unit,
   *the model decides* whether to call a tool / what to retain, while *your code* owns the node
   wiring, the contract, and whether a result is allowed to matter. The base unit is exactly where
   the book's decision axis becomes mechanical. *Skip it:* the litmus lens stays abstract one
   chapter past where it could be grounded. **n/a** (classification framing). (1.2 Who Decides?)
7. **The minimal worked unit (the anchored example)** `[+]` — one graph node over a state object:
   read state → one model call with one tool + a typed output contract → return enriched state.
   This is the chapter's concrete payload and the thing that makes the abstraction land. *Skip it:*
   the chapter is all prose and the reader never sees the atom as code. **Standard.** (Companion
   code; see CODE below.)

> **Context-economy note (standing lens).** The unit is also where the token bill starts: every
> tool schema, retrieved chunk, and memory item rides in the window and taxes attention. Name the
> cost *once* here as a property of the unit, then point to 1.5 Context Engineering (the general
> principle) and 2.1 §7 (tool-schema bloat) for the depth. Do not teach mitigation here.

> **Failure-path note (standing lens).** Since the unit *consumes* its own tool results, name the
> contract once: a failed augmentation returns to the model as a structured, recoverable message,
> not a raw exception. The depth lives in 2.1 Tool Use (Gotcha 5); here it is a one-line property
> of the loop, so the chapter doesn't sell a happy-path-only atom.

## Mention-and-link (one line, a pointer, not a section)

- **Tool use** — the model choosing to call a typed function → 2.1 Tool Use.
- **Structured output** — the typed contract on the model's result → 2.2 Structured Output.
- **Retrieval (RAG)** — augmenting the unit with fetched knowledge → 5.2 Retrieval.
- **Memory** — what the unit retains across turns → 5.3 Memory; and the distinction it's often
  confused with → 5.1 State, Not Memory.
- **Context engineering** — the window *is* the program; what to put in the unit's prompt → 1.5.
- **MCP** — connecting tools to the unit at scale → 2.4 MCP.
- **Frameworks** — whether you need LangGraph at all to build this unit → 1.6.
- **Workflow vs. agent** — how many of these units, wired by code vs. by the model → 1.3.

## Out of scope (name it, point somewhere)

- Tool schema design, `tool_choice`, the tool loop, injection → 2.1 (owns it; do not re-teach).
- Constrained decoding / JSON-mode internals → 2.2.
- RAG architecture (chunking, embeddings, retrievers) → 5.2.
- Memory types (episodic/procedural) and when you need them → 5.3.
- State persistence, reducers in depth, checkpointing → 5.1 / 5.4 / 7.3.
- LangGraph API surface beyond "a node reads state and returns an update" → framework docs / 1.6.
- Multi-unit orchestration (chaining, fan-out, panels) → Part III.

## Maturity summary

- **Standard:** the augmented LLM as the base unit; tools + structured output as the load-bearing
  augmentations; the state-graph-of-nodes runtime model as the dominant orchestration substrate.
- **Established:** retrieval and memory as augmentations (proven, but optional and situational —
  most pipelines don't need them, which is itself worth saying).
- **Emerging:** nothing the chapter must commit to; the moving parts (which framework, how much
  memory) are deferred to 1.6 / 5.x.
- **Contested:** none owned here — the "every app needs an autonomous agent" overclaim belongs to
  1.3 (Workflow or Agent?), not this chapter.

## Sources

Primary: Anthropic, "Building Effective Agents" (2024), <https://www.anthropic.com/research/building-effective-agents>
(the augmented-LLM building block: model + retrieval + tools + memory; "simple, composable
patterns"). Framework: LangGraph Graph API overview, <https://docs.langchain.com/oss/python/langgraph/graph-api>
(nodes are functions taking state and returning a partial update; state schema + reducers; the
node-on-a-graph runtime). Vendor SDKs ship the augmentations as first-class: OpenAI tools /
structured outputs and Anthropic tool use (cite the concrete pages already used in 2.1 to keep the
reference internally consistent). Cross-refs: this repo's 1.1, 1.2, 1.3, 1.5, 2.1, 2.2, 5.1–5.3.

> **Verify before quoting:** the LangGraph API surface moves (class names, `create_agent` vs.
> graph-builder spelling); pin the exact call against the version in `listing-studio/pyproject.toml`
> before quoting, and prefer "a node reads state and returns an update" framing over any specific
> method name. Re-confirm the exact wording of the Anthropic "augmentations such as retrieval,
> tools, and memory" line before reproducing it as a quote.

---

## CODE: yes

This is a concept chapter, but the abstraction ("the atom everything composes from") is exactly the
kind that dies without one concrete instance. The chapter needs **one minimal, tested example: a
single augmented-LLM unit as one graph node over a state object** — the smallest thing that shows
all three load-bearing pieces (a model call, one tool, a typed output contract) and the substrate
(read state → return enriched state) in one frame. It must reuse the existing carrier artifacts
(the Aldsworth desk, `check_price`, `supplier_sku`, `price_cents`, `draft → review`) so it reads as
the same world as 2.1, not a fresh toy.

**Convention (settled):** LangGraph default, with OpenAI Responses + Anthropic Messages as alternate
`<details>`/content-tab panes. Inline code synced to anchored source via `tests/test_doc_sync.py`.

**Proposed anchors** (new file, e.g. `listing-studio/foundations/augmented_llm_langgraph.py`, with
`tools.py`-style raw-SDK siblings if the alternate panes are shown):

- `state` — the typed state object the node reads and writes (a minimal `Listing`-shaped
  `TypedDict`/Pydantic state: `supplier_sku`, `price_cents`, `status`). *Demonstrates:* the graph
  carries a typed state, not loose dicts; this is the substrate.
- `unit` — the augmented unit itself: one model call bound to one tool (`check_price`, reused from
  2.1) **and** a typed output contract (the structured result the model must fill). *Demonstrates:*
  model + tool + contract = the atom, in one place.
- `node` — the node function: `def price_node(state) -> state` that reads state, invokes the unit,
  and returns the enriched state (e.g. `price_cents` set, `status` advanced). *Demonstrates:* a node
  reads state, calls the unit, returns enriched state — the one sentence the substrate section turns
  on.

Keep it ruthlessly minimal: this example must *not* re-teach the tool loop (2.1 owns it) or
constrained decoding (2.2 owns it). It exists only to show the unit-and-substrate shape in one
readable frame. The `node` anchor is the load-bearing one; if the chapter must show only one block,
show that. Coordinate with the coder-tester so `check_price` and the state field names match the
carrier bible and 2.1 byte-for-byte (the doc-sync test will enforce it).

## Open questions for the author

1. **Depth of the substrate section.** How much state-graph vocabulary does 1.4 own vs. defer? My
   map gives just enough to read later diagrams (node / state / edge) and pushes reducers,
   persistence, and checkpointing to 5.1 / 5.4 / 7.3. Is that the right cut, or should 1.4 carry a
   fuller "here is the runtime model" treatment since it's the first place the reader meets it?
2. **Retrieval + memory: name-and-defer, or one worked sentence each?** I have them as
   mention-and-link only (taught in 5.2 / 5.3). Confirm we don't even sketch them here beyond
   "optional augmentations," to protect the spine.
3. **Does the code show all three panes (LangGraph + Responses + Anthropic), or LangGraph only?**
   2.1 shows all three. For a *foundations* chapter, LangGraph-only (with the raw SDKs deferred to
   2.1/2.2) may keep the atom clearer. Your call on whether the alternate panes earn their room here.
4. **One node, or a two-node fragment?** A single node shows the unit; a two-node fragment (node →
   node, state flowing between) shows the *substrate* more honestly but risks straying toward
   composition (Part III). I lean single-node + a one-line "and the next node reads what this one
   returned." Confirm.
5. **Litmus tier line.** The template HEAD wants a *Who decides* tag. For an assembly/concept
   chapter the honest answer is "both, by design" (model decides inside the unit; your code owns the
   wiring). Is "both / n/a" acceptable in the HEAD, or do you want a single committed token?
