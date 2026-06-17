# Coverage map: Context Engineering (chapter 1.5)

> Research-derived spec for what the chapter must cover so a reader understands the discipline of
> curating the model's context window — and where to stop, handing depth to the sibling chapters
> that own it. Built from a multi-angle sweep (vendor/primary, academic/benchmark, practitioner,
> the skeptical read, and the term's own provenance). Review and trim the **Must-cover** list; that
> sets the chapter's scope. Bar: definitive but tight (the Gang-of-Four / Wikipedia test), not
> exhaustive. **This is a foundations/framing chapter, not a pattern chapter** — its job is the
> mental model and the vocabulary, not a build.
>
> **Last reviewed: 2026-06-16.** This topic moves fast (the vocabulary settled only mid-2025; the
> benchmarks are < 18 months old). Carry a "Last reviewed" stamp on the published chapter and
> re-sweep it on any refresh.

## The mental model (what the reader must leave with)

**The context window IS the program.** What you put into it, and what you deliberately leave out,
determines the model's behavior more than any other lever you have. Every token in the window —
system prompt, tool schemas, retrieved knowledge, memory, few-shot examples, message history —
competes for one shared, finite budget, and each item pays *twice*: once in tokens (cost and
latency) and once in **degraded attention** (the model gets measurably less reliable as the window
fills, well before the advertised limit). Context engineering is the discipline of curating that
window — finding, in Anthropic's phrase, "the smallest possible set of high-signal tokens that
maximize the likelihood of the desired outcome." Prompt engineering is one slice of it (how you
word the instructions); context engineering owns the whole window across a multi-step trajectory.

## Must-cover (for the framing to land)

Ranked. Each: why it matters, the failure mode if skipped, maturity, lead citation. `[*]` = the
stub already gestures at it; `[+]` = gap to fill. (The current stub is skeleton-only, so nearly all
are `[+]`.)

1. **The thesis: the context window is the program** `[+]` — the chapter's whole reason to exist.
   Behavior is governed more by what's in the window than by any other choice; "context" is not just
   the prompt but everything that lands in the window during inference. *Skip it:* the reader keeps
   tuning prompt wording while the real lever (what else is in the window) goes unmanaged.
   **Established** (the practice) / **Emerging** (as a named, first-class discipline). (Anthropic,
   "Effective context engineering for AI agents," 2025-09-29.)

2. **Everything competes for one budget** `[+]` — system prompt, tool schemas, retrieved chunks,
   memory, few-shot examples, and message history all draw on the *same* finite window; adding one
   crowds the others. *Skip it:* the reader treats each input source in isolation and the window
   silently overflows or gets diluted. **Established.** (Anthropic 2025; LangChain "Context
   Engineering," 2025-07-02 — context as instructions / knowledge / tools.)

3. **The two costs every item pays: tokens AND degraded attention** `[+]` — *the standing lens of
   this whole reference, and the heart of this chapter.* Each token costs money and latency, and
   *also* spends a finite "attention budget" — more in the window means less reliable use of any of
   it. Name both costs explicitly and tie them to the mitigation (inject the minimal relevant
   subset). *Skip it:* the reader thinks a bigger window is a free lunch and stuffs it. **Standard**
   (the principle). (Anthropic 2025 — "attention budget," "every new token introduced depletes this
   budget.")

4. **Context rot / degradation — attention fails before the advertised limit** `[+]` — the
   empirical backbone. Performance degrades *continuously* as input grows; a 200K window can show
   significant degradation far below 200K, and it is worse for low-similarity / multi-distractor /
   multi-hop tasks. **Cite the finding and the live source; do NOT freeze a single token number** —
   the threshold is task-dependent and model-dependent. *Skip it:* the reader trusts the spec sheet
   and builds an agent that quietly rots mid-run. **Emerging** (the named phenomenon, fast-moving
   evidence) / **Established** (the underlying effect). (Chroma "Context Rot," Hong/Troynikov/Huber,
   2025-07-14; the founding "Lost in the Middle," Liu et al., arXiv:2307.03172, for the U-shape.)

5. **Context engineering vs. prompt engineering** `[+]` — the disambiguation the title demands.
   Prompt engineering = how you word the instructions (takes the window as given); context
   engineering = curating the *whole* window across a trajectory (instructions are one slice).
   Present the honest skeptical read here (item under Maturity / skeptic below): is this just a
   rebrand? *Skip it:* the reader can't tell the new discipline from the old skill, and the
   "Emerging" maturity claim looks unearned. **Emerging** (the term, settled mid-2025). (Anthropic
   2025 for both definitions; Willison "Context engineering," 2025-06-27, for the provenance and the
   honest case that it's a *correction*, not pure rebrand.)

6. **Progressive disclosure — the general principle** `[+]` — reveal only the relevant subset of
   tools / skills / context on demand, rather than front-loading everything (just-in-time retrieval:
   keep lightweight identifiers — paths, queries, links — and load at runtime). **Note it here as
   the principle; hand the depth to 2.3 Skills.** *Skip it:* the reader has no general name for the
   single most important mitigation, and 1.5 / 2.3 don't connect. **Established** (the idea) /
   **Emerging** (as a codified standard via Agent Skills). (Anthropic 2025, "just-in-time" /
   "progressive disclosure"; depth → 2.3 Skills.)

7. **The named failure modes of a badly-curated window** `[+]` — a compact, citable taxonomy so the
   chapter feeds the Anti-Patterns Catalog: **poisoning** (an error/hallucination lodges in context
   and gets re-referenced), **distraction** (window so long the model over-weights it vs. training),
   **confusion** (superfluous content drags quality down), **clash** (contradictory
   info/tools in the window). *Skip it:* "curate the window" stays abstract with no concrete way it
   goes wrong. **Established.** (Drew Breunig, "How Contexts Fail," 2025-06-22; echoed by LangChain
   2025.)

## Mention-and-link (one line, a pointer, not a section)

- **Compaction / summarization** — the *when-it's-already-too-big* mitigation → **5.4 Compaction**.
- **Retrieval (RAG)** — pulling external knowledge into the window selectively → **5.2 Retrieval (RAG)**.
- **Memory** — persisting and re-loading state across the window's edge (note-taking, store) → **5.3 Memory** (and **5.1 State, Not Memory** for the distinction).
- **Skills / progressive disclosure depth** — the three load levels, the security cost → **2.3 Skills**.
- **Tool-schema bloat** — schemas ride in input tokens on every call; keep the tool set small → **2.1 Tool Use** (this chapter names the cost; 2.1 owns the contract).
- **Cost / prompt caching** — keeping stable content first to maximize cache hits → **8.4 Controlling Cost**.
- **Sub-agent context isolation** — a clean window per worker, condensed summaries back → **3.3 Orchestrator-Workers** / Part IX Multi-Agent.

## Out of scope (name it, point somewhere)

- **How to compact / summarize** (algorithms, triggers) → 5.4 Compaction.
- **How to retrieve** (chunking, embeddings, rerankers) → 5.2 RAG.
- **Memory architectures** (episodic/procedural, stores) → 5.3 Memory.
- **The Skills standard** (`SKILL.md`, three load levels, skill security) → 2.3 Skills.
- **Per-model context-window sizes / pricing** — volatile; cite the live vendor doc, never a snapshot.
- **Transformer attention internals** (quadratic cost, FlashAttention) — name the *why* in one line; the mechanism is not this chapter's job.

## Maturity summary

- **Standard:** the underlying principle that each window item pays in tokens *and* attention, so you
  inject the minimal relevant subset; the U-shaped / lost-in-the-middle effect is settled science.
- **Established:** the practices — curate the window, mind degradation, prefer just-in-time loading;
  the four context-failure modes as a working taxonomy; progressive disclosure as an idea.
- **Emerging:** "context engineering" as a *named, first-class discipline* (vocabulary settled only
  mid-2025); "context rot" as a named phenomenon with still-accumulating, task-dependent evidence;
  progressive disclosure codified as a standard (Agent Skills, late 2025).
- **Contested:** the strong "prompt engineering is dead, context engineering replaces it" framing
  (overclaim — it subsumes, it doesn't erase); any single quoted degradation threshold or per-model
  rate; vendor million-/multi-million-token window claims as *usable* end-to-end.

**AUTHOR-SIGNED VERDICT: Established.** (Overrides the researcher's "Emerging" pitch.) The author's
argument, which the chapter should make its spine: context engineering is not a young, settling
discipline — it is arguably *the first* discipline of AI-enabled apps, so foundational that
practitioners stopped naming it. Deciding what goes in the window was the work from the moment apps
started calling an LLM. The recent vocabulary ("context engineering," 2025) named an old practice; it
did not invent a new one. So the chapter's honest read is **Established, bordering on so-obvious-it's-
invisible** — and the interesting move is *re-surfacing* it as a first-class concern, not selling it
as new. (The supporting research on *degradation* — context rot, lost-in-the-middle — is genuinely
recent and still accumulating; that is what keeps the "Last reviewed" stamp on, not the discipline's
maturity.) **Do not pitch this as Emerging.** **Carry a "Last reviewed" stamp** for the research, not
the verdict.

## On companion code

**CODE: NO (recommended).** This is a framing/foundations chapter; its deliverable is the mental
model and the vocabulary, and every concrete mechanism (compaction, retrieval, memory, skills) is
owned by a sibling chapter that carries its own code. Forcing code here would either duplicate a
sibling or invent a toy that teaches nothing the prose doesn't. *Optional, only if the author wants
one concrete anchor:* a tiny, read-only "what's in the window right now" budget illustration — a
function that lists the window's components (system prompt / tools / history / retrieved / memory)
with their token shares — purely to make "everything competes for one budget" tangible. If built,
keep it LangGraph-flavored (project default) and minimal, and have it route through coder-tester per
house rule. Default stance: ship the chapter without code.

## Sources (verified live, 2026-06-16)

**Vendor / primary:**
- Anthropic, "Effective context engineering for AI agents," 2025-09-29 — anthropic.com/engineering/effective-context-engineering-for-ai-agents. *(The anchor source: "attention budget," "smallest possible set of high-signal tokens," definitions of both context- and prompt-engineering, just-in-time / progressive disclosure, compaction, note-taking, sub-agents.)*
- LangChain, "Context Engineering," 2025-07-02 — langchain.com/blog/context-engineering-for-agents. *(Write/Select/Compress/Isolate; context as instructions/knowledge/tools.)*
- OpenAI GPT-5.x prompting guidance — developers.openai.com / cookbook.openai.com. *(Caching: stable content first, dynamic last; agentic scaffolding spectrum. Use for the cost mention-and-link.)*
- Google, Gemini "Long context" docs — ai.google.dev/gemini-api/docs/long-context. *(Million-token windows + the honest caveat that the window is a shared sum; context caching. Use as the "big window ≠ free" foil.)*

**Academic / benchmark:**
- Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," arXiv:2307.03172 (TACL 2023) — the founding U-shape finding. **Verified.**
- Chroma, "Context Rot: How Increasing Input Tokens Impacts LLM Performance" — Hong, Troynikov, Huber, 2025-07-14 — trychroma.com/research/context-rot; repo github.com/chroma-core/context-rot. *(18 models; continuous non-uniform degradation; needle-question similarity, distractors, LongMemEval, repeated-words.)* **Verified.**
- Wang, Min, Zou, "Intelligence Degradation in Long-Context LLMs: Critical Threshold Determination…," arXiv:2601.15300 — a *current* threshold study. **Verified it exists; the specific threshold value was not extractable from metadata — re-read the body before quoting any number.** Use as "the literature is now hunting for the threshold," not for a hard figure.

**Practitioner / skeptical / provenance:**
- Simon Willison, "Context engineering," 2025-06-27 — simonwillison.net/2025/jun/27/context-engineering/. *(The honest case: a correction, not pure rebrand; the Karpathy/Lütke origin.)*
- Drew Breunig, "How Contexts Fail and How to Fix Them," 2025-06-22 — dbreunig.com. *(The four failure modes.)*
- Timothy B. Lee, "Context rot: the emerging challenge…," 2025-11-10 — understandingai.org. *(The skeptical read: advertised windows aren't usable end-to-end; cites Chroma, Adobe, METR.)*

> **Verify before quoting:** (1) Any specific degradation token-threshold or per-model accuracy
> drop — task- and model-dependent; cite the finding and the live source, never a frozen number.
> (2) Vendor context-window sizes/pricing — rot fast. (3) arXiv:2601.15300 — confirm the threshold
> figure against the paper body before reproducing it. (4) The Agent Skills token figures (≈80
> tokens/skill discovery) belong to 2.3 Skills; if cited here, re-verify against the standard.

## Open questions for the author

1. **Maturity call:** RESOLVED → **Established** (author override; see AUTHOR-SIGNED VERDICT above).
   The practice is old and foundational; only the name is new. Chapter argues exactly that.
2. **Code:** confirm **no companion code** (recommended). Or do you want the optional read-only
   "what's in the window" budget illustration as one concrete anchor?
3. **The skeptic, how hard:** how sharply do we hit the "context engineering is just prompt
   engineering rebranded" critique — a paragraph of honest doubt, or a lighter touch? (The reference
   sells credibility, so I lean: name it squarely, then make the honest case for the term.)
4. **Failure-mode taxonomy:** include Breunig's four named modes (poisoning / distraction /
   confusion / clash) in-chapter, or demote them to a single line + link into the Anti-Patterns
   Catalog?
5. **Carrier instance:** do we want an *In Listing Studio* callout here (e.g., the 9-step pipeline
   deliberately *not* carrying all prior steps' raw output forward — each step gets a curated
   window)? It's a clean, production-grounded illustration of the thesis if you have the war story.
6. **Last-reviewed cadence:** agree this chapter gets re-swept on a fixed interval (it's one of the
   fastest-moving in Part I)?
