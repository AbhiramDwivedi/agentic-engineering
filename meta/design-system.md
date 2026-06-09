# The Design System

> **Why this exists:** a 39-chapter reference with outside contributors cannot stay consistent on
> goodwill. The design system is what makes the site read as one authored work rather than a pile
> of pages, and it is the precondition for crowd-sourcing: a contributor can match a written spec,
> not an inferred vibe. Read this before writing; it points to the rest.

The system has five layers.

## 1. Structure

The fixed chapter flow: **HEAD → Why → What → How → Gotchas → Foot**. Why comes first; the head
carries the one-line definition. Start every chapter from [`chapter-template.md`](chapter-template.md).
Parts and numbering: Part I-IX (roman), chapters `N.M`. Later chapters render muted ("planned") in
the nav so the full map is visible without implying it is all written.

**Titles are canonical nouns** ("Tool Use", "Fan-Out"), in the H1 and the nav both: a reference
gets cited and searched by its nouns. The evocative phrase the chapter used to carry as a title
moves into the gloss line under the head, which doubles as the chapter's one-line entry in the
patterns index.

## 2. Components

The named, reusable blocks. Use them as defined; do not invent variants.

**Dual rendering is a hard constraint.** Every page must read correctly in two places: the
built site and GitHub's own file view (where readers and contributors will actually meet the
markdown). That rules out Material-only syntax in content: no `!!!` admonitions, no content
tabs, no attr_list buttons, no markdown inside block-level `<div>`s. Callouts are
bold-labelled blockquotes; the lens line is a single-line `<small>`; diagrams are mermaid
(GitHub renders it natively).

| Component | Markdown | Job |
|---|---|---|
| Lens line | one-line `<small class="chapter-meta">…</small>` | maturity · who-decides · grounding · last-reviewed |
| Maturity lens | prose, one line | Standard / Established / Emerging / Contested. Never a radar. |
| From production | `> **From production.** …` blockquote | a first-hand scar. Only if true. |
| In the companion repo | `> **In the companion repo.** …` blockquote | demonstrated, not shipped |
| In Listing Studio | `> **In Listing Studio.** …` blockquote | the carrier instance, three sentences max |
| Stub notice | `> **Stub.** …` blockquote | scaffolding, not finished writing |
| Code | inline, synced to a tested file by `tests/test_doc_sync.py` | shown in full, cannot drift |
| Expandable listing | `<details markdown><summary>…</summary>` around a code fence | long listings whose story the diagram + trace already tell; collapses on GitHub and the site both |
| Shape diagram | ` ```mermaid ` flowchart in How | the pattern's runtime shape, in the shared visual language |
| Framework differences | short `####` subsections | only where implementations differ (tabs are Material-only) |
| Citation | footnote | every non-obvious claim |
| See also | links | cross-links to related chapters |

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
3. **Build and run the companion example** for any chapter that shows code → real artifacts.
4. **Draft** in the reference register, anchored on 1-3.
5. **Adversarial QA panel** (independent agents): fact-checker, skeptic on the lenses,
   confidentiality scrubber, code-drift checker, prose-critic against the voice spec.
6. **Revise**, cutting hard.
7. **Author read** (taste gate): boring dies, overclaims get pulled.
8. **Gates:** humanizer for residual tells, `mkdocs build --strict`, link check, citation
   re-verify, read-aloud cadence.

Agents do research and verification, where they are strong. The draft is written under the spec.
The human is the source of judgement and the final taste call, never the bottleneck on volume.
