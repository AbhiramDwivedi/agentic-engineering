# 1.5 Context Engineering

<small class="chapter-meta">**Maturity: Established** (the practice is as old as calling an LLM; only the name is new) · *Who decides:* your code (you curate the window the model reasons over) · *Grounding:* research · *Last reviewed:* 2026-06</small>

*The discipline of deciding what goes into the model's context window and what stays out. The window is the program: behaviour is governed more by what you put in it than by almost any other lever. Every token competes for one finite budget and pays twice, once in cost and latency and once in the model's attention.*

## Why you'd reach for it

You can write a perfect prompt and still get a worse answer than you did last week, because the prompt was never the whole input. The model reads everything you handed it that turn: the system instructions, the tool schemas, the retrieved documents, the running message history, whatever memory you reloaded, every few-shot example. That whole pile is the context window, and it is what the model actually reasons over. Tune the wording of one instruction while the pile around it grows unmanaged, and you are polishing a sentence inside a room that is filling with noise.

Here is the cost story. Listing Studio runs nine steps to turn a raw supplier feed into a published listing, and a naive version carries every step's full output forward: step 4 writes the copy, step 5 reads all of that copy plus the raw spec sheet plus the ingestion log plus the categorizer's reasoning, step 6 reads all of that again plus step 5, and so on. By the time the pricing step runs on the Aldsworth desk, the listing being built, the window holds eight steps of accumulated text, most of it irrelevant to setting a price within the MAP floor. The bill is the smaller problem. The real problem is that the model gets measurably less reliable as the window fills, and it fills well before the advertised limit, so the pricing step quietly makes worse calls precisely because the earlier steps were thorough. The pricing prompt was fine; the window it ran inside was not.

The fix is to treat the window as a budget you spend on purpose. Anthropic frames the goal as finding "the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."[^anthropic] You decide, per step, what the model needs to see to do that step well, and you leave the rest out, curating a window per node instead of replaying the whole transcript every time. That single discipline, applied across a trajectory, is context engineering.

Reach for it when:

- a multi-step agent or pipeline degrades the longer it runs, even though each individual prompt looks fine;
- you are adding retrieval, memory, or more tools, and need to know what the new tokens cost the rest of the window;
- responses get slower and more expensive as a conversation or a job grows, and quality does not keep pace;
- you are about to trust a vendor's advertised context length as if all of it were usable.

You do not need to think about it for a single short prompt with no tools and no history. There the prompt *is* the context, and ordinary prompt engineering covers you. Context engineering earns its name the moment the window has more than one author.

## What it actually is

Context engineering is the practice of curating everything that enters the model's context window across a task, so the model sees the high-signal subset and not the rest. The context window is the fixed span of tokens a model can attend to in one inference pass. Everything that competes for that span is "context": the system prompt, the tool definitions, retrieved knowledge, reloaded memory, few-shot examples, and the message history. Prompt engineering is one slice of this, how you word the instructions. Context engineering owns the whole window, and it owns it across many steps rather than one.[^anthropic][^langchain] Its glossary entry is [Context Engineering](../catalogs/glossary.md).

Two facts make it a discipline rather than a slogan.

First, **everything draws on one budget.** A context window is a single finite pool, and the system prompt, the tool schemas, the retrieved chunks, the memory, and the history all draw from it together. Add a fifth tool and its schema rides in the input on every call, shrinking the room left for the actual conversation. Paste in three more retrieved documents and you have less room for the model's own working notes. The sources do not add up to a bigger window; they share the one you have.[^langchain] Vendors quoting million-token windows do not change this. Google's own long-context guidance is explicit that the window is a shared sum and that filling it carries a cost, not a free upgrade.[^gemini]

Second, **every item pays twice.** Once in tokens, which is money and latency, and once in attention, which is reliability. The attention cost is the one teams miss. A model does not use a full window as well as an empty one. Anthropic puts it directly: a model has a finite "attention budget," and "every new token introduced depletes this budget," so the discipline is to spend it carefully.[^anthropic] The window is not free storage; it is a shared budget, and a bigger one is not a license to stuff it.

On the litmus test this reference runs, context engineering is a thing **your code decides.** The model reasons over the window; it does not assemble it. You choose what to retrieve, what to summarize, what to carry forward, what to drop. That makes it engineering, not a model-made decision, which is exactly why it is so easy to neglect: nothing in the model's behaviour forces you to do it, until the quality drops.

### The maturity call: established, and nearly invisible

The honest maturity verdict is **Established, bordering on so-obvious-it's-invisible.** This is a deliberate call, and worth arguing, because the easy move would be to file a 2025 term of art under "Emerging" and sell it as the new thing. It is not new.

Deciding what goes into the window was the work from the moment anyone wired an app to an LLM. The first time you chose which database rows to paste into a prompt, trimmed a chat history to fit, or picked three examples instead of ten, you were engineering context. The practice is arguably the *first* discipline of building with language models, so foundational that practitioners stopped naming it and just did it. What 2025 added was the vocabulary. Andrej Karpathy and others put a name to it, and Simon Willison argued the name was overdue precisely because the practice had outgrown "prompt engineering" without anyone relabelling it.[^willison] A named old practice is **Established**, not **Emerging**. The move this chapter makes is to re-surface a foundational concern as a first-class one, not to announce a discovery.

One part of the surrounding evidence genuinely is recent and still settling, and that is why this chapter carries a "Last reviewed" stamp. The research on how, exactly, attention degrades as the window fills (the "context rot" work, the lost-in-the-middle studies, the hunt for a degradation threshold) is less than two years old and accumulating fast. The stamp tracks that research, not the maturity of the discipline. The discipline is old. The measurements of why it matters are new.

### Is this just prompt engineering rebranded?

The skeptical reader's first question, and it deserves a straight answer rather than a dodge, since this reference sells credibility. The charge: "context engineering" is a marketing rebrand of "prompt engineering," the same skill with a more impressive name.

The honest answer is that it is a correction, not a rebrand, and that it subsumes prompt engineering without erasing it. Willison makes this case well: the term arose because "prompt engineering" had been narrowed in popular use to mean clever wording of a single instruction, while the actual job had grown to include everything else that lands in the window across a long task.[^willison] Prompt engineering is still real and still a slice of the work, how you phrase the instruction the model reads. Context engineering is the larger discipline that contains it: the instruction is one item in the window, and you are also responsible for the other items and for the window as a whole over time. So the correct framing is containment, not replacement. The overclaim to refuse is the strong "prompt engineering is dead" version. Nothing died. The scope of the job got named correctly.

This is the chapter's one disambiguation: context engineering is the whole-window, whole-trajectory discipline, of which prompt engineering is the single-instruction slice.

## How the discipline cashes out

The window is one shared budget, and the job is allocation. A diagram helps less here than naming the moves, because there is no single runtime shape; there is a recurring decision, made at every step, about what the next window should contain. Four moves recur across the literature.[^langchain]

**Write less in.** Inject the minimal relevant subset, not everything you have. This is the move the naive Listing Studio pipeline skips. The fix is unglamorous: each step gets a window built for that step, holding the current Listing and the few prior outputs it actually needs.

**Reveal on demand (progressive disclosure).** Rather than front-loading every tool, document, and instruction the agent might need, keep lightweight references (a file path, a query, a link, a tool name and one-line description) and load the heavy content only when a step actually reaches for it. Anthropic calls this just-in-time loading, and it does more to control a bloated window than any other single move.[^anthropic] This chapter names it as the general principle; the codified standard for packaging it, Agent Skills, and its three load levels and security cost, live in [2.3 Skills](../the-unit/skills.md). The glossary entry is [Progressive disclosure](../catalogs/glossary.md).

**Compress when it grows.** When a trajectory genuinely cannot avoid getting long, summarize the older content into a denser form so it keeps its signal at a fraction of the tokens. The how (when to trigger, what to keep, how to summarize without losing the thread) is [5.4 Compaction](../knowledge/compaction-and-the-window.md)'s job, not this chapter's.

**Isolate.** Give a sub-task its own clean window and hand back only a condensed result, so a worker's scratch work never pollutes the parent's context. This is one of the real reasons to reach for sub-agents, and [3.3 Orchestrator-Workers](../composition/fan-out.md) and Part IX carry the mechanism.

These four are how curation actually happens. The recurring source of new tokens that teams under-budget is the tool set itself: every tool's schema rides in the input on every call, so a sprawling tool list silently taxes every turn. This chapter names that cost; [2.1 Tool Use](../the-unit/tool-use.md) owns the contract and how to keep the set small.

> **In Listing Studio.** The nine-step pipeline deliberately does not carry every prior step's raw output forward. Each step receives a window curated for its job: the pricing step gets the attributes and the MAP rules, not the ingestion log or the full draft copy. Treat this as an illustration of curation, not a measured production claim.

### Context rot: attention fails before the limit

The empirical reason curation matters, and the part the "Last reviewed" stamp protects. The intuition that a model uses all of a 200K-token window equally well is wrong. Performance degrades as the input grows, continuously and non-uniformly, and it can degrade well before the advertised limit.

The founding result is "Lost in the Middle": across several models, accuracy on a retrieval task depended sharply on *where* in a long context the needed information sat, forming a U-shape, strong at the beginning and the end of the window and weakest in the middle.[^lostinmiddle] The more recent and more general result is Chroma's "Context Rot" study, which ran 18 models and found that performance falls off as input length grows, not in a clean cliff but continuously, and worse when the task is hard: low similarity between the question and the buried answer, multiple distractors, multi-hop reasoning.[^contextrot] The research is now actively hunting for where the degradation becomes severe, with threshold studies appearing, but the threshold is task-dependent and model-dependent, so there is no single number to quote and freezing one would mislead.[^threshold]

The practical takeaway survives without a number. A longer window is not a stronger one, the spec sheet's maximum is not a usable working size, and the safe assumption is that reliability falls as the window fills. Cite the finding and the live source; do not trust a frozen threshold.[^lee]

### The four ways a window fails

A compact taxonomy, useful enough that it feeds the [Anti-Patterns Catalog](../catalogs/anti-patterns.md). Drew Breunig named four distinct ways a badly-curated window degrades a model, and the names are worth keeping because they tell you *which* failure you are looking at:[^breunig]

- **Poisoning.** An error or a hallucination lodges in the context and then gets re-referenced as if it were true, so one bad token early contaminates everything downstream.
- **Distraction.** The window grows so long that the model over-weights its accumulated context and under-weights what it actually knows from training.
- **Confusion.** Superfluous content that is not wrong, just irrelevant, drags the quality of the response down by sheer presence.
- **Clash.** The window holds contradictory information or conflicting tool definitions, and the model has no clean way to reconcile them.

Each maps to a curation move. Poisoning argues for not blindly carrying an agent's own past output forward; distraction and confusion argue for writing less in; clash argues for isolating contexts that disagree. The taxonomy is a diagnostic: name the failure, then reach for the matching move.

## The skeptical read

The strong version of this discipline is overclaimed, and naming where keeps the chapter honest.

The first overclaim is the "prompt engineering is dead" framing, answered above: context engineering subsumes prompt engineering, it does not retire it.

The second is treating a bigger context window as a solution rather than a constraint. The marketing trend runs toward million- and multi-million-token windows, framed as the end of having to choose. The evidence above says otherwise: usable working size is smaller than advertised maximum, and the gap is real enough that practitioners and benchmarks both report it.[^contextrot][^lee] A larger window buys you more room to make the same mistakes more expensively. It does not remove the need to curate.

The third is any confident, frozen number for where degradation kicks in. The research is genuinely moving, the thresholds are task- and model-dependent, and a reference that quoted "quality falls off at N tokens" as a law would be selling exactly the false certainty it exists to fight. The defensible claim is the shape, not the coordinate: reliability falls continuously as the window fills, and you should measure it for your own task rather than trust a number from a paper or a slide.

What is *not* contested is the core. That each window item costs tokens and attention, that everything competes for one budget, and that the U-shaped lost-in-the-middle effect is real, are settled.[^anthropic][^lostinmiddle] The discipline is Established; only the precise measurements of its stakes are still being written.

## In short

Treat the context window as the program, because it is closer to the truth than treating the prompt as the program. Before tuning instruction wording, account for everything else in the window (tools, retrieved knowledge, memory, history) and curate it deliberately: inject the smallest high-signal subset for each step, load heavy content only on demand, compress what must stay long, and isolate sub-tasks in their own windows. Assume reliability falls as the window fills, well before the advertised limit, and design for that rather than trusting the spec sheet. The discipline is not new and not optional; the only new thing is that we finally have a name for it and a growing body of evidence for why it pays. The mechanisms it points to (retrieval, memory, compaction, skills) each get their own chapter; this one gives you the mental model and the vocabulary to use them well.

## Sources

[^anthropic]: Anthropic, "Effective context engineering for AI agents" (2025-09-29). The "attention budget" framing ("every new token introduced depletes this budget"), the goal of "the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome," the definitions of context engineering versus prompt engineering, and just-in-time / progressive disclosure. <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
[^langchain]: LangChain, "Context Engineering for Agents" (2025-07-02). Context as instructions, knowledge, and tools drawing on one budget; the write / select / compress / isolate framing of the curation moves. <https://www.langchain.com/blog/context-engineering-for-agents>
[^willison]: Simon Willison, "Context engineering" (2025-06-27). The provenance of the term (Karpathy, Lütke) and the honest case that it is a correction of an over-narrowed "prompt engineering," not a pure rebrand. <https://simonwillison.net/2025/Jun/27/context-engineering/>
[^lostinmiddle]: Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang, "Lost in the Middle: How Language Models Use Long Contexts," arXiv:2307.03172 (TACL 2023). The founding U-shape finding: accuracy is highest when relevant information is at the start or end of the context and degrades when it sits in the middle. <https://arxiv.org/abs/2307.03172>
[^contextrot]: Kelly Hong, Anton Troynikov, Jeff Huber (Chroma), "Context Rot: How Increasing Input Tokens Impacts LLM Performance" (2025-07-14). Across 18 models, performance degrades continuously and non-uniformly as input length grows, worse for low question-answer similarity, multiple distractors, and multi-hop tasks. Cite the finding, not a frozen threshold; the effect is task- and model-dependent. <https://www.trychroma.com/research/context-rot>
[^threshold]: A current threshold study (arXiv:2601.15300) confirms the literature is now hunting for where long-context degradation becomes severe. The threshold is task- and model-dependent; do not reproduce a number without re-reading the paper body. Treat as "the field is now looking for the threshold," not as a hard figure. **Verify before publish.**
[^lee]: Timothy B. Lee, "Context rot: the emerging challenge that could hold back LLM progress" (2025-11-10), understandingai.org. The skeptical read that advertised context windows are not usable end-to-end, citing Chroma, Adobe, and METR. <https://www.understandingai.org/p/context-rot-the-emerging-challenge> **Verify framing before publish.**
[^breunig]: Drew Breunig, "How Contexts Fail and How to Fix Them" (2025-06-22), dbreunig.com. The four named failure modes of a badly-curated window: poisoning, distraction, confusion, and clash. <https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html>
[^gemini]: Google, Gemini API "Long context" documentation. Million-token windows alongside the caveat that the window is a shared sum and that filling it carries a cost; context caching as a mitigation. Vendor window sizes change; cite the live doc, never a snapshot. <https://ai.google.dev/gemini-api/docs/long-context> **Verify before publish.**

## See also

- [1.4 The Augmented LLM](the-augmented-llm.md) for the base unit (a model plus tools plus a contract) whose every part lands in the window this chapter teaches you to curate.
- [2.1 Tool Use](../the-unit/tool-use.md), which owns the tool contract; this chapter only names the cost that every tool schema rides in the input on each call.
- [2.3 Skills](../the-unit/skills.md) for progressive disclosure as a codified standard (the three load levels and the security cost), the depth behind the principle named here.
- [5.1 State, Not Memory](../knowledge/state-not-memory.md) and [5.3 Memory](../knowledge/real-memory.md) for the distinction between graph state and persisted memory, both of which reload into the window.
- [5.2 Retrieval (RAG)](../knowledge/retrieval-rag.md) for how external knowledge gets selected into the window; this chapter says it competes for the budget, that one says how to fetch it.
- [5.4 Compaction](../knowledge/compaction-and-the-window.md) for the when-it's-already-too-big move: summarizing a long trajectory without losing the thread.
- [3.3 Orchestrator-Workers](../composition/fan-out.md) for sub-agent context isolation, giving a worker a clean window and taking back a condensed result.
- [8.4 Controlling Cost](../production/controlling-cost.md) for the cost side: ordering stable content first to maximize prompt-cache hits.
- [Anti-Patterns Catalog](../catalogs/anti-patterns.md), which collects the four window-failure modes named here (poisoning, distraction, confusion, clash) as anti-patterns to watch for.
