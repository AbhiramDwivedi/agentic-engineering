# The Design System

> **Why this exists:** a 39-chapter reference with outside contributors cannot stay consistent on
> goodwill. The design system is what makes the site read as one authored work rather than a pile
> of pages, and it is the precondition for crowd-sourcing: a contributor can match a written spec,
> not an inferred vibe. Read this before writing; it points to the rest.

The system has five layers.

## 1. Structure

The fixed chapter flow: **gloss → Why → What → How → Gotchas → In short → lens line → Sources →
See also**. Start every chapter from [`chapter-template.md`](chapter-template.md). Parts and
numbering: Part I-IX (roman), chapters `N.M`. Later chapters render muted ("planned") in the nav so
the full map is visible without implying it is all written.

**The reading line comes first; the apparatus goes to the foot.** A chapter opens with its gloss
and then its way in, a scar or a failure or a provocation, because that is what decides whether
anyone reads the rest. The lens line (maturity, who-decides, grounding, last-reviewed) sits
immediately above **Sources**, where a reader checking the work looks for it, and the verdict also
appears in the [quick-reference](../docs/catalogs/quick-reference.md) table for anyone scanning
across patterns. It is metadata. It is not a headline, and it is a bad first impression: no reader
has ever been pulled into a page by a grounding label.

**Section headings are unnumbered.** `## Why you'd reach for it`, never `## 1. Why you'd reach for
it`. Numbering makes a page read as a form that was filled in.

**One chapter, one argument, sized to the argument.** Every chapter declares a thesis in its
coverage map before drafting (see the interest bar in `voice-and-style.md`), and the draft argues
that thesis. Length follows the weight of the idea, never the number of sections in the template:

| Chapter kind | Prose budget | Example |
|---|---|---|
| Deflation / disambiguation | ~1,500-2,000 words | 6.1 Retry & Backoff |
| Standard pattern | ~2,000-2,800 words | 3.1 Prompt Chaining, 3.2 Routing & Dispatch |
| Flagship (the genuinely-new four) | up to ~3,500 words | 2.1 Tool Use |
| Framing / concept | ~1,200-2,000 words | 1.2 Who Decides? |

Prose words, code excluded, and counted to the end of **In short** (sources and cross-links do not
count against the argument). These are ceilings, not targets; coming in under is good.

**Count the mechanisms you have to make work, not the ones you debunk.** A chapter is a deflation
only when the deflation is the whole chapter. 3.2 opens by deflating the dispatch table and then
has to teach LLM routing properly, with a taxonomy, a confidence floor, an escalation path, and an
eval discipline, so it is a standard-pattern chapter carrying a deflation, and it is budgeted as
one. Reaching for the wrong row is how a chapter either bloats or gets starved.

A chapter that wants more than its row must justify it by the idea, and the honest fix is nearly
always a link to the chapter that owns the material rather than a fuller treatment here. Material
that is reference-shaped rather than argument-shaped (a comparison matrix across many patterns, a
checklist) belongs in `docs/catalogs/`, not in a chapter.

**Optional sections, from a fixed menu (controlled extension).** The spine above is mandatory, so
every page reads the same way. A deep topic may add sections from a controlled menu, only when the
topic earns it, always with the same name and in the same slot (after How, before Gotchas):
**Security & trust** (a real trust boundary: untrusted input, supply chain), **Cost** (token or
compute spend is a first-order design concern), **Ecosystem & tooling** (a real distribution,
sharing, or tooling landscape), **Operating in production** (observability, rollout, blast-radius),
and **Evaluating it** (how you'd measure it works). A simple chapter uses none of these and keeps
its sharp edges in Gotchas; a chapter with a genuine security or distribution story promotes that
concern out of Gotchas into its own section. The menu is the controlled vocabulary, not a cage: if
a chapter needs a section the menu lacks, propose it for sign-off rather than inventing one
silently, so the menu grows deliberately and the reference keeps reading as authored, not assembled.

**Titles are canonical nouns** ("Tool Use", "Fan-Out"), in the H1 and the nav both: a reference
gets cited and searched by its nouns. The evocative phrase the chapter used to carry as a title
moves into the gloss line under the head, which doubles as the chapter's one-line entry in the
patterns index. **The alias line carries the neighbours' names.** `*Also called: …*` lists the
names the rest of the canon uses for the same idea (Anthropic's guide, OpenAI's, Google's, Gulli's
*Agentic Design Patterns*, Ng's four patterns, LangChain, 12-Factor Agents), so a reader searching
any of them lands here. The coverage map's alias sweep supplies it.

**Reference-shaped material lives in `docs/catalogs/`**, not in chapters: the anti-patterns
catalog, the quick-reference (with an *Also called* column), the decision frameworks, the dated
state of play, the glossary, the hardening checklist and the security posture map, and three
surfaces added 2026-08-15 for usability and long-run trust: **Reading Paths** (by use case and
role: the everyday engineer arrives with a problem, not a taxonomy — and, added 2026-08-16, *the
build path*: the chapters sequenced from a fifty-line loop to a production system, with the
companion repo growing along it and a feature → chapter traceability table; a build path, not a
build book), **the Incident File** (public
agent failures, cited, each mapped to the pattern or guardrail that would have caught it), and
**Changes** (a dated log of verdict moves and re-reviews). A chapter links to these; it never
re-teaches them.

## 2. Components

The named, reusable blocks. Use them as defined; do not invent variants.

**Dual rendering is a hard constraint.** Every page must read correctly in two places: the
built site and GitHub's own file view (where readers and contributors will actually meet the
markdown). That rules out Material-only syntax in content: no `!!!` admonitions, no attr_list buttons, no
markdown inside block-level `<div>`s. Content tabs are banned except for the multi-provider code
blocks below (the one accepted exception): there they render as clickable tabs on the site and
degrade to literal markers on GitHub's raw view, a tradeoff taken for the code-switching experience. Callouts are
bold-labelled blockquotes; the lens line is a single-line `<small>`; diagrams are mermaid
(GitHub renders it natively).

| Component | Markdown | Job |
|---|---|---|
| Lens line | one-line `<small class="chapter-meta">…</small>`, placed immediately above `## Sources` | maturity · who-decides · grounding · last-reviewed. When a verdict has moved, say so inline (`Established (was Contested, 2025-11)`) and log the move in `catalogs/changes.md` (created under Catalogs on first use); a visibly maintained verdict is what a reader trusts in 2028 |
| Maturity lens | prose, one line | Standard / Established / Emerging / Contested. Never a radar. |
| Alias line | `*Also called: …*` under the gloss | the neighbouring canon's names for the same idea (vendor guides, Gulli, Ng, LangChain, 12-Factor), for search and for the quick-reference's *Also called* column |
| Reader-verifiable anchor | one sentence in prose, naming a public tool | where a tool the reader runs (a coding agent, a browser agent, a vendor SDK) visibly implements the mechanism; lets the reader check the claim on their own screen (voice-and-style rule 16) |
| From production | `> **From production.** …` blockquote | the single first-hand-experience callout: a real scar or real hands-on use. Only if true. Public tools may be named (e.g. a scanner the author used); the confidential product is recast into the carrier, never named. |
| In the companion repo | `> **In the companion repo.** …` blockquote | demonstrated, not shipped |
| In Listing Studio | `> **In Listing Studio.** …` blockquote | the carrier instance, three sentences max |
| LLM-response quote | italic + quotes, e.g. *"I'd list it at $419."* | an imaginary model utterance; the italics mark it as the model talking, not the author or a cited source |
| Stub notice | `> **Stub.** …` blockquote | scaffolding, not finished writing |
| Code | inline, synced to a tested file by `tests/test_doc_sync.py` | shown in full, cannot drift |
| Expandable listing | `<details markdown><summary>…</summary>` around a code fence | long listings whose story the diagram + trace already tell; collapses on GitHub and the site both |
| Shape diagram | ` ```mermaid ` flowchart in How | the pattern's runtime shape, in the shared visual language |
| Mechanism diagram | hand-authored `.svg`, referenced as a plain image | rare: where the drawing hides the thing the reader actually has to see (3.1's splice; 3.3's worker count). Same visual language, and it takes the slot of whichever visual it supersedes (3.1's mermaid, 3.3's illustration) rather than being added alongside. Must stay legible as a still, because GitHub strips the animation |
| Framework differences | short `####` subsections | only where implementations differ (tabs are Material-only) |
| Citation | footnote | every non-obvious claim |
| See also | links | cross-links to related chapters |
| Further reading | links, annotated | a short curated set of external deep-dives (the spec, the key paper, the primary doc, the best skeptical take), each with a one-line reason. Distinct from Sources (per-claim footnotes) and See also (internal cross-links); points to canonical primary sources, not aggregators. |

### Code in a chapter (the diet)

Code earns its space by carrying the argument. A page that is half listing has stopped being prose,
and the reader who came for the idea leaves before the idea arrives.

- **One primary listing.** The minimal shape that makes the pattern real, ideally under 30 lines.
  The contract or schema it depends on may stand beside it.
- **Plain Python first.** The primary listing uses no framework, or the thinnest possible use of
  one; frameworks and vendor SDKs appear only in the provider tabs at the end of How. The test: a
  mid-level engineer with an HTTP client and a model key could build the minimal shape this
  afternoon. 3.2's `dispatch` and `route_message` are the pattern; practitioners' standing advice
  ("use the APIs directly, avoid abstraction layers") is the reason.
- **Comments state constraints the code cannot show.** They never narrate the next line, and they
  never re-teach the chapter. If a docstring explains the pattern, the prose already did it better;
  cut it in the source, not just in the chapter.
- **The trace does the teaching.** A numbered run trace after the code teaches runtime behaviour
  faster than a second listing does. Prefer adding a trace step over adding code.
- **Provider wiring goes last**, in a short `#### Wiring it to a provider` subsection at the end of
  How, after the trace, so it never interrupts the reading line.
- **A listing whose story the diagram and trace already tell** goes inside
  `<details markdown><summary>`, or stays in the companion repo behind a link.

### Multi-provider code examples

Code that differs only by SDK or framework is shown in **Material content tabs** (`=== "…"`), the
**LangGraph** tab first and active by default, then **OpenAI Responses API**, then the **Anthropic
Messages API**. Reuse the same tab labels across a page so the tabs link. They render as clickable
tabs on the site (the intended reading experience) and degrade to literal markers on GitHub; that
tradeoff is accepted. Do not explain the framework's internals, the audience can read its docs.
Every tab's code is tested companion code under doc-sync, which dedents the tab indentation before
matching. Per the diet above, the tab group is the *last* thing in How.

## 3. Language

[`voice-and-style.md`](voice-and-style.md): the reference register, the rules, the blandness
checklist, the tell-list. The lyrical voice goes to the distribution posts, not the chapters.

## 4. Visual

Material theme, indigo, light/dark. The maturity treatment is quiet text, not a badge dashboard.
Callouts are bold-labelled blockquotes (the dual-rendering constraint above); any colour styling
is a site-side CSS enhancement that must degrade cleanly on GitHub. Restraint is the point. If
it starts to look like a technology radar, it is wrong.

**Diagrams are mermaid** (diffable, PR-able) and share one visual language sitewide: **rounded
nodes = the model decides; rectangles = your code decides; hexagons = a capability, not a
pattern.** That is the litmus test drawn. Every pattern chapter carries one shape diagram in
How; the homepage carries the overall map in the same language. Plain theme colours, no custom
palettes per diagram.

**The one exception is a hand-authored SVG**, and it has to be argued for. Mermaid draws boxes and
arrows, which is enough for most patterns and not enough for a pattern whose difficulty is what
moves along the arrow. 3.1 is the case that earned it: a flowchart of the gated chain leaves the
splice, the previous answer becoming text inside the next prompt, entirely invisible, and that is
the part readers get wrong. 3.3 is the second: parallel boxes converging on a merge look the same
whether the box count came from a literal or from a model call, so that diagram runs two products
through the step and lets you count the workers, and it takes the chapter illustration's slot
because the illustration was making the same point less precisely. Such a diagram keeps the shared
visual language, replaces a visual rather than joining one, animates with SMIL only, carries its
palette in an internal `prefers-color-scheme` block, and must still teach when frozen, because
GitHub renders the still and drops the motion. That last one is a design constraint, not a
courtesy: build the finished state as the default and let the animation play up to it, never the
reverse.

## 5. Taxonomy and evidence

Defined once, linked everywhere:
- **Litmus test** (classification): the model decides / your code decides / a feature / a draw.
- **Maturity lens** (trust): Standard / Established / Emerging / Contested.
- **Grounding** (evidence): production / companion repo / research / reasoned.
- **The carrier**: all specifics come from [`carrier-bible.md`](carrier-bible.md). Numbers come
  from the code, never invented.

## The production pipeline

How a chapter is actually made, in order:

1. **Research** (agent fan-out) → a cited evidence pack; unsupported claims flagged.
2. **Interview the author** (informed by the research) → stance, the call, the war stories.
3. **Agree the thesis and the budget** → the one sentence the chapter argues, and which row of the
   budget table it is written to. Both go in the coverage map before a word is drafted.
4. **Build and run the companion example** for any chapter that shows code → real artifacts.
5. **Draft** in the reference register, anchored on 1-4.
6. **Voice pass**, one writer, continuous, over the whole chapter. Where several engines drafted,
   the merge happens first and fuses coverage only; the voice pass rewrites rather than stitches.
7. **Interest bar** (author or a fresh reader): thesis, way in, quotable line. A draft that fails
   goes back here, before anyone counts a tell. Boring dies at this gate, when the fix is cheap.
8. **Adversarial QA panel** (independent agents): fact-checker, skeptic on the lenses,
   confidentiality scrubber, code-drift checker, prose-critic against the voice spec.
9. **Revise**, cutting hard.
10. **Author read** (taste gate): overclaims get pulled.
11. **Gates:** humanizer for residual tells, `mkdocs build --strict`, link check, citation
    re-verify, read-aloud cadence.

Agents do research and verification, where they are strong. The draft is written under the spec.
The human is the source of judgement and the final taste call, never the bottleneck on volume.
