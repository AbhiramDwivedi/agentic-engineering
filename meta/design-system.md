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

## 2. Components

The named, reusable blocks. Use them as defined; do not invent variants.

| Component | Markdown | Job |
|---|---|---|
| Lens line | `<div class="chapter-meta" markdown>` | maturity · who-decides · grounding · last-reviewed |
| Maturity lens | prose, one line | Standard / Established / Emerging / Contested. Never a radar. |
| From production | `!!! production` | a first-hand scar. Only if true. |
| In the companion repo | `!!! inrepo` | demonstrated, not shipped |
| In Listing Studio | `!!! example "In Listing Studio"` | the carrier instance |
| Code | inline, synced to a tested file by `tests/test_doc_sync.py` | shown in full, cannot drift |
| Framework differences | `=== "tabs"` | only where implementations differ |
| Citation | footnote | every non-obvious claim |
| See also | links | cross-links to related chapters |

## 3. Language

[`voice-and-style.md`](voice-and-style.md): the reference register, the rules, the blandness
checklist, the tell-list. The lyrical voice goes to the distribution posts, not the chapters.

## 4. Visual

Material theme, indigo, light/dark. The maturity treatment is quiet text, not a badge dashboard.
Two callout colours only: green for production, blue for the companion repo. Restraint is the
point. If it starts to look like a technology radar, it is wrong.

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
