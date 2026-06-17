# Coverage map: It's Still Engineering (chapter 1.1)

> Research-derived spec for what the **opening framing chapter** must cover to earn the reader's
> trust and set up the whole reference, and where to stop. This is a FRAMING chapter, not a
> technique: there is no companion code, no pattern to diagram, and **maturity is `n/a`**. So the
> must-cover list is about the *completeness and honesty of the argument* and the citations that
> back its non-obvious claims — not production-safety items. Built from a 3-angle sweep that fits a
> framing chapter (vendor/primary framing docs; the skeptical read on agent hype; practitioner
> framing). Review and trim the **Must-cover** list; that sets the chapter's scope.
> Bar: definitive but tight (the Gang-of-Four / Wikipedia test), not exhaustive.

## The mental model (what the reader must leave with)

Building with agents is still engineering. Most things sold as "agentic patterns" are ordinary
design patterns with a model dropped into one slot; only a few are genuinely new, and the way to
tell them apart is to ask who makes the decision — the model or your code. That single deflation
is the promise of the whole reference: a trustworthy map that lets you tell signal from noise.
This chapter makes the reader *want* that map — it does not yet teach the test, the spectrum, or
the base unit (those are 1.2–1.4). It earns the thesis and hands off.

## Must-cover (for a complete, honest framing)

Ranked. Each: why it matters, the failure mode if skipped, maturity, lead citation. `[*]` = the
stub already gestures at it; `[+]` = not yet present (the stub is a bare skeleton, so most are `[+]`).

1. **The deflation, stated plainly: building with agents is still engineering** `[+]` — the
   thesis in one quotable line, and the claim that most "agentic patterns" are familiar design
   patterns with a model in one slot. *Skip it:* the chapter has no spine and the reference has no
   identity. **Maturity n/a** (it's the framing). Grounded in the author's own experience; the
   register echoes Fowler/Hammant reference writing (influence, not a load-bearing citation).
2. **The concrete anchor that makes the deflation land** `[+]` — one specific, lived "I had a
   list and looked harder" moment (the canonical version: a pattern about to be filed as
   "routing" turns out to be a dictionary lookup). The voice spec demands a concrete anchor;
   abstract claims must land on a specific memory. *Skip it:* the deflation reads as an opinion,
   not a discovery. **n/a.** Grounding: *From production* (recast; confidentiality-scrubbed).
   *(Boundary: the worked sort of the 12 patterns belongs to 1.2 — see open questions.)*
3. **Why this matters: mislabelling sets the wrong expectations for cost, failure, and testing**
   `[+]` — the stakes for a technical leader. A dictionary is deterministic and you unit-test it;
   a model making the call is non-deterministic and needs evals. Calling them the same thing hides
   the risk a CTO needs to see. *Skip it:* the deflation reads as pedantry, not a decision tool.
   **n/a.** (Mention-and-link the full argument to 1.2, which owns "why beyond pedantry".)
4. **The honest three-way split exists (named, not re-taught)** `[+]` — genuinely-new (model
   decides) / just-engineering (your code decides) / features-and-coinages, plus the one honest
   draw (prompt chaining: old structure, new reason). State that the split exists and that the
   reference is organized around it. *Skip it:* the reader can't see the shape of what's coming.
   **n/a.** *(Boundary: the actual sorting table is owned by 1.2 The Litmus Test — link, don't
   reproduce. This chapter names the three buckets; 1.2 fills them.)*
5. **The shared vocabulary this builds on (multiple authorities, not Anthropic alone)** `[+]` —
   *(author directive, 2026-06-16: don't lean on Anthropic as the sole source.)* Credit the common
   framing that the field converged on — the augmented LLM, workflow patterns, the autonomous-agent
   loop — citing **more than one authority** (Anthropic's "Building Effective Agents"; Google/Gulli's
   goal-directed agent definition; OpenAI's agents guide) and the simplicity-first instinct they
   share: *"add complexity only when it demonstrably improves outcomes."* The deflation is in honest
   dialogue with this shared vocabulary (a vocabulary list isn't a system). *Skip it:* the thesis
   floats free of the field's framing and looks unsourced — or worse, looks like it rests on one
   vendor. **n/a / Standard** (the framing is widely adopted across vendors). Lead citations:
   Anthropic + Google/Gulli + OpenAI (see 1.2's Sources for the full set). The *definitional debate*
   itself is owned by 1.2 — name the vocabulary here, don't argue the definition. *(Whether to
   enumerate the five workflows here or defer to 1.3 remains an open question.)*
6. **The skeptical read: "agent washing" / the hype gap** `[+]` — the chapter is the deflation,
   so it must name the overclaim it deflates: vendors rebranding any LLM-plus-a-call as an
   "agent." This is what makes the trust-map promise credible rather than self-congratulatory.
   *Skip it:* the chapter claims to cut through hype without showing the hype. **n/a** (the
   *framing*); the underlying field reality is **Contested** by design. Lead citations: Gartner
   "agent washing" / project-cancellation prediction; one practitioner "most agents are workflows"
   write-up. *(Verify-before-quoting: the 40%/130-vendor numbers rot — cite the finding, link the
   source, don't freeze the figure.)*
7. **The promise of this reference: the trust model in one sentence** `[+]` — what the reader
   gets in exchange for reading on: every technique labelled by how proven it is (maturity) and
   backed by cited evidence. This is the chapter's payoff and the contribution rule in miniature.
   *Skip it:* the reader has the diagnosis but no reason to believe the cure. **n/a.**
   (Mention-and-link the mechanics to *How We Label* and *How to Read This*.)

> Items 4 and 5 are the most likely trim/merge candidates if the author wants a leaner opener; 1–3
> and 6–7 are the irreducible core (the deflation, its anchor, its stakes, the hype it answers, the
> promise it makes).

## Mention-and-link (one line, a pointer, not a section)

- **The litmus test itself** — the "who decides?" question, the worked sort of a real pattern set,
  the three-way split table, and "why beyond pedantry" → **1.2 Who Decides?** (owns the test;
  this chapter only *names* that a test exists). Also the standalone [The Litmus Test](../about/litmus-test.md).
- **The workflow-vs-agent spectrum** and the honest truth that most production value sits on the
  workflow end → **1.3 Workflow or Agent?** (owns the spectrum and the five workflow patterns in
  depth).
- **The augmented-LLM base unit** (model + tools + a contract; the graph/state substrate) →
  **1.4 The Augmented LLM**.
- **Build-vs-buy / don't cargo-cult a framework** → **1.6 Do You Even Need a Framework?**
- **The carrier (Listing Studio) and the chapter shape** → [How to Read This](../about/how-to-read.md)
  (owns the carrier intro and the eight-beat chapter shape). This chapter may name Listing Studio
  in one sentence as the running example, then point here.
- **How maturity + evidence labels work** → [How We Label](../about/how-we-label.md).

## Out of scope (name it, point out)

- **Teaching the litmus test** (criteria, the sort, edge cases) → 1.2. This chapter sets it up only.
- **The five workflow patterns explained** (chaining/routing/parallelization/orchestrator-workers/
  evaluator-optimizer) → 1.3 and Part III. Name them at most; don't define them.
- **What an "agent" *is* vs. a workflow, rigorously** → 1.3.
- **Any pattern's mechanics, code, or shape diagram** → its own chapter (Parts II–III). No companion
  code here; no Mermaid pattern diagram (a framing chapter has no runtime shape to draw).
- **The full carrier tour and chapter-template walkthrough** → How to Read This.

## Maturity summary

**Maturity: `n/a`** — this is the reference's framing thesis, not a technique, so the four-tier
scale does not apply. State that plainly in the lens line and do **not** invent
Standard/Established/Emerging tiers for an argument. Instead, frame the *argument's honest stance*:

- The **deflation** ("still engineering") is a defensible, well-supported position, not a neutral
  fact — argue it, don't assert it. It is in dialogue with Anthropic's widely-adopted
  workflows-vs-agents framing (effectively **Standard** as shared vocabulary), which the chapter
  credits and extends rather than contradicts.
- The **hype it deflates** ("agentic" as marketing) is genuinely **Contested** territory — lead
  the skeptical read with evidence (agent-washing, project-cancellation findings), not with a
  sneer, and be generous to the ambition before disagreeing (the voice spec).
- Honesty discipline for this chapter specifically: no universal quantifiers ("everyone calls it
  routing," "nobody cites anything"), no invented statistics. The pull to overclaim is strongest in
  an opener's hook — this chapter is *selling* honesty, so it must model it.

## Sources

Primary / vendor framing: **Anthropic, "Building Effective Agents"**
(anthropic.com/research/building-effective-agents; published 2024-12-19; **verified live this
sweep**) — confirmed wording: workflows = "LLMs and tools orchestrated through predefined code
paths"; agents = "LLMs dynamically direct their own processes and tool usage"; the five workflow
patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer);
the augmented LLM building block; and the exact guidance *"add complexity only when it demonstrably
improves outcomes."* This is the chapter's one load-bearing external citation.

Skeptical read: Gartner, "Over 40% of Agentic AI Projects Will Be Canceled by End of 2027"
(gartner.com newsroom, 2025-06-25) and the related "agent washing" framing (only ~130 of thousands
of self-described agentic vendors deliver autonomy); practitioner write-ups on "most agents are
workflows / glorified chatbots" (e.g. SDxCentral "Was 2025 really the year of the AI agent?";
Futurum hype-vs-reality). Use these to evidence the overclaim the deflation answers.

Stance/register, *not* load-bearing citations: Martin Fowler's articles and Paul Hammant's
trunkbaseddevelopment.com (the reference register this site emulates); the author's own published
blog (first-party stance and voice, e.g. "Thunderstorms and Sunshine"). Cite these as influence,
never as the evidentiary backbone of a claim.

> **Verify before quoting:** the Gartner figures (40% cancellation, ~130 genuine vendors) and any
> "year of the agent" claim are directional and will rot — cite the finding and link the live
> source, never freeze the number. Re-confirm the Anthropic URL and the "demonstrably improves
> outcomes" wording at publish time (it is current as of this sweep).

## Sweep angles run vs. skipped

- **Vendor / primary framing docs** — RUN. Anthropic "Building Effective Agents" fetched and
  verified live. This is the chapter's anchor.
- **The skeptical read (agent hype / overclaim)** — RUN. Agent-washing and project-cancellation
  evidence located; this is the Contested half the deflation answers.
- **Practitioner framing** — RUN (light). "Most agents are workflows" practitioner accounts
  located to corroborate the skeptical read; the author's own production experience is the primary
  practitioner source (a *From production* anchor).
- **Academic + benchmarks** — SKIPPED. This is a framing/thesis chapter with no technique to
  measure; benchmark evidence belongs in the technique chapters (2.x, 3.x). No founding paper
  underwrites "it's still engineering."
- **Security / failure modes (OWASP, incidents)** — SKIPPED. No untrusted input, actions, or
  shared state are introduced here; safety coverage lives in the technique chapters and Part IV.

## Open questions the author must rule on (sign-off)

1. **How hard to lead with the deflation?** Cold-open on "it's still engineering" as the first
   line, or open with the lived "I had a list and looked harder" scene and let the deflation land
   second? (Voice spec favours hook-first; the reference register favours the definition up top.)
2. **Name Anthropic's five workflows here, or defer to 1.3?** Recommendation: name the *framing*
   (workflows vs. agents) and the simplicity guidance here; enumerate and explain the five only in
   1.3. Confirm.
3. **How much of the personal "I was proud of my list of 12" story belongs here vs. 1.2?**
   Recommendation: the *seed* of the story (the routing-is-a-dictionary realization) lands here as
   the anchor; the *worked sort* of all twelve and the three-way table belong to 1.2. Confirm the
   split so the two chapters don't tell the same story twice.
4. **Trim items 4 and/or 5?** Is naming the three-way split (item 4) redundant with the 1.2 link,
   and is the Anthropic framing (item 5) enough as one credited sentence rather than a beat?
5. **How explicit to be about confidentiality?** Include the honest line ("patterns drawn from a
   production system, recast in a commerce setting so the ideas travel") in this opener, or leave
   it to How to Read This?
6. **Does the trust-model promise (item 7) live here or is it fully delegated to How We Label?**
   Recommendation: one promise sentence here, mechanics linked out.
