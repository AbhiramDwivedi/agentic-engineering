# Coverage map: Who Decides? (chapter 1.2)

> Research-derived spec for the reference's central **classification lens** — *who makes the
> structural decision, the model or your code?* — and the honest three-way split it produces.
> This is a **framing chapter, not a technique chapter**: no companion code, no pattern to
> diagram, **maturity n/a** (this *is* the test the other chapters are scored against). Built from
> a 3-angle sweep (primary framing docs; the skeptical / anti-hype read; practitioner accounts of
> mislabelled "agentic" patterns). **An existing page already covers most of this**: 1.2 becomes
> the canonical home of the litmus test and `about/litmus-test.md` is trimmed to a pointer, so
> every must-cover item is marked `[*]` (already in the about page), `[*partial]`, or `[+]` (a gap
> 1.2 must add). Review and trim the **Must-cover** list; that sets the chapter's scope. Bar:
> definitive but tight (~5–8 items).

## The mental model (what the reader must leave with)

Most "agentic patterns" are ordinary engineering with a model dropped into one slot; only a few
are genuinely new. There is one question that sorts any pattern you meet: **who makes the
structural decision, the model or your code?** If the model decides — it calls a tool, judges its
own draft and loops, sizes its own work, picks a persona — the pattern is genuinely new, because
nothing in the old toolbox could make a judgement call inside a control flow. If your code decides
and the model is just the worker inside a fixed structure — a dispatch table, a retry loop, a
callback — it is a pattern you already know, and calling it "agentic" is marketing. This is a
**classification** lens (is it *new*?), deliberately orthogonal to the maturity lens (is it
*proven*?); both can appear on a later chapter without conflict. The reason it matters beyond
pedantry: the label sets the cost, the failure mode, and the testing strategy — get it wrong and
you hide exactly the risk a technical leader needs to see.

## Must-cover (for a complete, honest framing)

Ranked. Each: why it matters, the failure mode if skipped, the (framing-chapter) maturity stance,
and a lead citation. `[*]` = already in `about/litmus-test.md`; `[*partial]` = there but thin;
`[+]` = gap 1.2 must add.

1. **The "agentic vs. workflow" definition — touch it briefly, refuse to make it central** `[+]`
   — *(author directive, 2026-06-16: "this debate does not bring value — we lose either way. Present
   my view, other views, and iterate that the patterns here are useful in either case.")* There is
   no settled definition of "agentic," and a reference that pretends otherwise reads as naive — so
   acknowledge it, but **keep it to one tight passage and do not let it become the chapter's
   centre.** State three things and move on:
   - **The author's position (offer it as opinion, not fact):** *when you use an agent to do a piece
     of work, that's a **workflow**; when an agent decides **what to do next** — which step to take —
     that's an **agentic, agent-driven** app.* It is decision/control-based, and it has a like-minded
     published authority: **LangChain / Harrison Chase** — *"an agent is a system that uses an LLM to
     decide the control flow of an application."* Surface LangChain so the view isn't the author's
     alone.
   - **The other view, stated fairly (one line each, generous, no strawman):** others set a higher,
     autonomy/spectrum bar — Anthropic (*"agents dynamically direct their own processes"* vs.
     *"workflows…predefined code paths"*), OpenAI (*"independently accomplish tasks"*), Google/Gulli
     (goal-directed perceive→reason→act loops), Hugging Face *smolagents* (agency as *degrees*, where
     an LLM merely picking a branch is only *low* agency).
   - **The resolution that defuses it (the load-bearing move):** *it does not matter who wins the
     definition — the patterns in this reference are useful **either way.*** Workflow or agent, you
     still reach for the same tools, contracts, loops, and guardrails. Say this plainly and let the
     reader stop caring about the label.
   *Skip it:* the reference looks either partisan (asserts one definition as settled) or precious
   (sinks into a debate that adds no value and alienates both camps). **n/a** (framing). **Do NOT
   teach the spectrum here** — the deep autonomy/spectrum argument hands to **1.3 Workflow or
   Agent?**; 1.2 keeps only this brief beat plus the *pattern ≠ system* tension below (passing the
   litmus — an LLM made a structural call — is not the same as the *system* being an "agent" under
   the higher bar). Lead cites: LangChain (author's camp); Anthropic / OpenAI / Gulli / smolagents
   (the other camp); see Sources. Keep this beat to ~1–2 short paragraphs; the litmus (item 2) is
   the chapter's spine, not this.
2. **The one question, stated sharply** `[*]` — *who makes the structural decision, the model or
   your code?* The model deciding = genuinely new; your code deciding with the model as worker =
   a pattern you already know. *Skip it:* the whole reference loses its spine — there is no test
   to apply in later chapters. **n/a** (this is the lens). (Anthropic, *Building Effective Agents*
   — the workflow/agent distinction this lens generalises.)
3. **The four "model decides" tells, made concrete** `[*]` — calls a tool · judges its own draft
   and loops · reads a list and sizes its own work (worker count) · picks which persona to reason
   as. These are the four that pass, and each is owned by a later chapter (mention-and-link, do
   not teach). *Skip it:* the test stays abstract and a reader can't apply it. **n/a.** (Maps to
   2.1 / 3.4 / 3.3 / 3.5.)
4. **The honest three-way split (the table)** `[*]` — *model decides* (tool use, evaluator-
   optimizer, orchestrator-workers, specialist panel) · *your code decides* (front controller,
   retry, graceful degradation, observer) · *a feature or a coinage* (structured output, two-pass,
   humanizer). The split is the payoff: four genuinely new, four old, three not-patterns.
   *Skip it:* the deflation lands as assertion, not as a sorted result. **n/a.** (Spine; carrier =
   Listing Studio.)
5. **The dispatcher deflation — and Anthropic Routing, named precisely** `[*partial]` — the
   sharpest move: a static dispatch table (`event_type → graph` lookup) is **not** Anthropic's
   *Routing* pattern. Routing is one of Anthropic's five named workflows and *always contains a
   classification step* — a model (or an ML classifier) deciding which branch fits; a dispatch
   table has **no classifier**, a caller hands it a label and it looks one up. So the deflation is
   "this has no decision in it," not "the decision is cheap." *Skip it:* the reference repeats the
   exact mislabel it exists to cure. **n/a** (classification call); the deflation is the thesis in
   miniature. (Anthropic, *Building Effective Agents*, Routing.)  **← the citation to nail; see
   verify note.**
6. **The one honest draw: prompt chaining** `[*]` — by the test it's *your code decides* (a
   pipeline, an old idea) — but you split the task *because one model call can't hold it
   reliably*. Old structure, new reason. The honesty of naming a draw is part of the credibility.
   *Skip it:* the split looks too clean and the reader distrusts it. **n/a.** (→ 3.1 Prompt
   Chaining.)
7. **Why this matters beyond pedantry — cost, failure mode, testing** `[*]` — mislabelling a
   dictionary as "intelligent routing" sets the wrong expectations: a dispatch table is
   deterministic and unit-tested like any branch; a model making the call is non-deterministic and
   needs **evals**, not unit tests. This is the leadership payoff (cost / risk / how-you-test),
   and it forward-links the eval distinction. *Skip it:* the lens reads as a purist's word-game,
   not an engineering decision. **n/a.** (→ 4.2 Evaluation; → about/how-we-label.)
8. **The discipline: when in doubt, downgrade the claim** `[*]` — the standing rule the lens
   enforces and the contribution rule it feeds: never sell a "code decides" pattern as agentic,
   never sell a coinage as canon; if unsure, classify down. *Skip it:* the lens has no teeth as a
   review gate. **n/a.** (→ contributing.md; mirrors the how-we-label downgrade rule.)
9. **The lens is orthogonal to maturity (and to grounding)** `[+]` — explicitly state that
   *new* (this lens) and *proven* (the maturity lens) are different axes: a "code decides" pattern
   can be Standard and battle-tested; a "model decides" one can be Contested. Both labels co-exist
   on a chapter. *Skip it:* readers conflate "genuinely new" with "good / recommended." **n/a.**
   (→ about/how-we-label; design-system §5 taxonomy.)

## Mention-and-link (one line, a pointer, not a section)

Each cell of the split is OWNED by a later chapter; 1.2 names it and links forward, never teaches it.

- **Tool use** (the model calls a tool) → 2.1 Tool Use.
- **Structured output** (a capability, the junior partner to tool use — a *feature*, not a pattern) → 2.2.
- **Prompt chaining** (the draw) → 3.1 Prompt Chaining.
- **Front controller / dispatch** (the deflation; *not* LLM routing) → 3.2 Front Controller.
- **Orchestrator-workers** (the model sizes its own work) → 3.3 Orchestrator-Workers.
- **Evaluator-optimizer** (the model grades its own draft and loops) → 3.4 Evaluator-Optimizer.
- **Specialist panel** (the model picks the persona; our coinage) → 3.5 The Specialist Panel.
- **Retry & graceful degradation** (your code decides; generic resilience) → 7.1.
- **Observer / callbacks** (your code decides; report on every path) → 7.2.
- **Two-pass generation & the humanizer** (coinages; instances of broader ideas) → 6.2 / brand-voice polish.
- **The maturity lens & grounding** (the orthogonal trust axes) → about/how-we-label.
- **Eval vs. unit test** (why the non-deterministic branch needs evals) → 4.2 Evaluation.

## Out of scope (name it, point out)

- **Teaching any single pattern in the split** — each is a later chapter; here they are one line + a link.
- **What an "agent" is** (LLM + tools + contract) and **workflow vs. agent spectrum** → 1.4 The Augmented LLM / 1.3 Workflow or Agent?
- **The maturity tiers themselves** (Standard/Established/Emerging/Contested) → about/how-we-label.
- **The full Anthropic five-workflow taxonomy** as a tutorial → cite the source; the relevant pattern homes carry it (3.1–3.5).
- **The personal "list of 12 I was proud of" origin story** if the author wants it as a *distribution-post* hook rather than reference prose — see open questions.

## Open questions for the author

- **RESOLVED (2026-06-16, author):** the debate is **a brief beat in 1.2, not central**; the deep
  spectrum/autonomy half hands to **1.3**. Author's framing: *agent does the work = workflow; agent
  decides the next step = agentic;* present it as opinion, nod to the other camp, and resolve with
  "the patterns are useful either way." See must-cover #1. (Original analysis kept below for the record.)
- **Where does the definitional debate live — 1.2 or 1.3?** *(new; raised by the cross-authority
  sweep.)* The debate has two halves that split cleanly along this chapter's own seam:
  - **The classification half belongs in 1.2:** *is a given pattern genuinely new, or familiar?* —
    settled by the litmus (the model vs. your code makes the structural call). That is this chapter's
    job and the LangChain "decide the control flow" definition (Side A) is its natural anchor.
  - **The system-agency / spectrum half belongs in 1.3 Workflow or Agent?** which already **owns the
    spectrum** (per mkdocs nav and the existing Out-of-scope note): *is the whole system an agent or
    a workflow, and is "agentic" binary or a matter of degree?* — Anthropic's agent/workflow line,
    OpenAI's autonomy bar, and smolagents' levels (Side B) are spectrum content and live there.
  - **Recommendation — split, don't duplicate.** 1.2 **states the debate exists, plants the
    position, and names both camps in one tight passage** (so the chapter isn't naive), then **hands
    the spectrum/autonomy argument to 1.3** with a forward link rather than re-teaching it. The
    load-bearing move 1.2 must keep is the **tension callout**: *passing the litmus (an LLM made a
    structural call) is NOT the same as the system being an agent under Anthropic/smolagents* — i.e.
    classifying a **pattern** ≠ classifying a **system**. Keep that distinction explicit so 1.2 and
    1.3 don't blur. (Confirm the seam with the author; if 1.3 is deferred/planned, 1.2 may need to
    carry a fuller stub of the spectrum than otherwise.)
- **Item count vs. the stated bar.** The Must-cover list is now **9 items**; the chapter's own bar
  asks for ~5–8. The new debate item (#1) was an explicit add. If trimming back to bar, the
  lowest-risk merges are #8 (downgrade discipline) into #5/#7, or folding #9 (orthogonality) into the
  Maturity summary — author's call.

## Maturity summary (framing-chapter stance, not a tier)

This chapter carries **no maturity verdict — n/a — because it *is* the test other chapters are
scored against.** Its honest stance: the lens is a classification tool, not a quality judgement;
"genuinely new" is not a compliment and "you already knew it" is not a demotion. The *techniques*
this lens sorts each carry their own Standard / Established / Emerging / Contested verdict **in
their own chapters** — e.g. tool use trends Standard, the specialist panel is more Emerging/a
coinage, "fully autonomous agents" is Contested — and those verdicts live there, not here. The one
thing the chapter does assert with confidence is the deflation itself: that several widely-marketed
"agentic patterns" contain no model decision at all, and that the honest default when unsure is to
**downgrade the claim**.

## Sources

**The definitional debate must cite across authorities, not lean on Anthropic alone** (the author's
explicit pushback). Verified live June 2026; re-verify URLs/quotes at publish — several are
re-hosted or revised.

*Primary framing docs (the five authorities to map against the litmus):*

- **Anthropic, *Building Effective Agents*** (anthropic.com/research/building-effective-agents;
  published **19 Dec 2024**) — the load-bearing source. The five named workflows (prompt chaining,
  **routing**, parallelization, orchestrator-workers, evaluator-optimizer); the workflow-vs-agent
  distinction — *"Workflows are systems where LLMs and tools are orchestrated through predefined code
  paths"* vs *"Agents…are systems where LLMs dynamically direct their own processes and tool usage,
  maintaining control over how they accomplish tasks"*; both bucketed under the umbrella *"agentic
  systems."* **Side B anchor.**
- **Antonio Gulli, *Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems***
  (Springer Nature 2025, ISBN 9783032014016; a free pre-print draft was circulated publicly by the
  author; verify the canonical Springer link before quoting:
  https://link.springer.com/book/10.1007/978-3-032-01402-3).
  Gulli is a senior Google leader (Office of the CTO). Defines an agent as *"a system designed to
  perceive its environment and take actions to achieve a specific goal"* — **autonomy/goal-directed**
  framing (five-step perceive→reason→act loop; four levels of agent complexity, L0 reasoning engine →
  L3 multi-agent). **21 patterns**, with **Routing as Chapter 2**: *"dynamically directing user
  requests to specialized handlers, agents, or processing paths based on classification,"* where the
  classifier may be **LLM-based, embedding-based, rule-based, or ML-model-based**. **Use Gulli to
  corroborate the Routing deflation independently of Anthropic:** like Anthropic, his Routing
  explicitly admits a *non-LLM* classifier — so a label-lookup dispatch table with no classifier is
  *not* his Routing either. **Re-verify Gulli's exact intro wording against the book/PDF before
  quoting — the precise definition sentence is currently sourced via the free draft + secondary
  walkthroughs, not yet confirmed page-exact.**
- **Google, *Agents* whitepaper** (Wiesinger, Marlow, Vuskovic, Sept 2024;
  kaggle.com/whitepaper-agents) — *"a Generative AI agent…is an application that attempts to achieve a
  goal by observing the world and acting upon it using the tools that it has at its disposal."*
  Model + tools + orchestration layer (the "cognitive architecture"). Gulli's framing **aligns with**
  Google's goal-directed definition — worth noting since Gulli is Google.
- **OpenAI, *A practical guide to building agents*** (2025;
  cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) — *"Agents
  are systems that independently accomplish tasks on your behalf."* Core traits: uses an LLM to
  *manage workflow execution and make decisions*, recognises completion, self-corrects, can halt and
  hand back to a human, dynamically selects tools within guardrails. **Explicitly excludes** apps
  that integrate LLMs but don't use them to control workflow execution (single-turn chatbots,
  sentiment classifiers). **Side B anchor** (system-level, autonomy bar).
- **LangChain / Harrison Chase, "What is an agent?"** (blog.langchain.com; "uses an LLM to decide the
  control flow") — *"an agent is a system that uses an LLM to decide the control flow of an
  application."* Plus the **agentic spectrum** (chains → autonomous agents; the constrained-cognitive-
  architecture sweet spot). **Side A anchor — the closest published authority to the author's litmus.**
- **Hugging Face *smolagents*, "Introduction to Agents / levels of agency"**
  (huggingface.co/docs/smolagents/conceptual_guides/intro_agents) — **agency as a spectrum**: ☆☆☆ no
  agency · ★☆☆ LLM controls an if/else ("Router") · ★★☆ LLM controls tool execution / multi-step ·
  ★★★ multi-agent / code agents. Directly supports the binary-vs-spectrum fracture, and pointedly
  rates "LLM picks a branch" as only *low* agency. **Side B (spectrum) anchor.**

*Skeptical / Contested read (the anti-hype position the reference embodies):*

- **Simon Willison, "I think 'agent' may finally have a widely enough agreed upon definition…"**
  (simonwillison.net/2025/Sep/18/agents/; **18 Sept 2025**) — settled on *"An LLM agent runs tools
  in a loop to achieve a goal"* after years of dismissing the term; he crowdsourced **211
  definitions** grouped into 13 categories, and traces the ambiguity to Wooldridge (1994). Notes the
  competing autonomy framing (Altman: *"AI systems that can do work for you independently"*). The
  **"loop"** in his definition is itself a Side B nuance — one call is not a loop.
- **Gartner, "agent washing"** (coined 2025; gartner.com newsroom 2025-06-25, *"Over 40% of agentic
  AI projects will be canceled by end of 2027"*) — vendors rebrand RPA/chatbots as "agents" because
  *no universal definition exists*. This is the market-level Contested read; cite it to justify why
  the reference needs the litmus at all. Treat as industry-analyst signal, not a technical authority.

*Internal:* `about/litmus-test.md` (the existing page this chapter absorbs), `about/how-we-label.md`
(the orthogonal maturity lens), `meta/design-system.md` §5 (the taxonomy: litmus / maturity /
grounding), `SPINE.md` (the three-way split and per-cell chapter homes).

> **Volatile / uncertain attributions to flag at publish:** (a) **Gulli's exact intro definition
> sentence** — confirmed via the free draft + reputable walkthroughs, not yet page-exact against the
> Springer print; quote from the book/PDF directly. (b) **LangChain's "decide the control flow"
> wording** — Chase has said it in several venues (talks, the LangChain blog, Sequoia podcast);
> attribute to the canonical blog post, not a paraphrase. (c) **smolagents' star table** — wording
> may shift across doc revisions; cite the live conceptual-guide URL with an access date. (d) **Simon
> Willison's "211 definitions / 13 categories"** — figures from his own post; reproduce his numbers,
> don't round. (e) **OpenAI exclusions list** (chatbots/classifiers not agents) — paraphrased here;
> verify the exact phrasing in the PDF.

> **Verify before quoting:** Anthropic's *Building Effective Agents* page (URL above) is the
> load-bearing citation and the deflation hinges on quoting it correctly. **Verified June 2026:**
> the live URL resolves; Routing **is** one of the five named workflow patterns; it is defined as
> *"Routing classifies an input and directs it to a specialized followup task,"* with the
> classification *"handled … either by an LLM or a more traditional classification model/
> algorithm."* **Precision the chapter must keep:** because Anthropic explicitly allows a
> *non-LLM* classifier, do **not** frame the deflation as "routing needs a model." Frame it as
> "routing always contains a **classification decision**; a dispatch table contains **none** — the
> caller already knows the label." That is what makes a static `event_type → graph` lookup *not*
> routing. Re-verify the quote and URL at publish time; Anthropic occasionally re-hosts this essay.
