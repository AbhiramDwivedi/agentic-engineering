# How to Read This

> **The decision it resolves:** where do *you* start, and what does each chapter promise?

This is a reference, not a course. You don't have to read it in order, but it does have an
order, and a shape every chapter shares.

## The carrier: Listing Studio

Patterns only make sense once you watch them crowd into a single system. So this reference
teaches through one: **Listing Studio**, a fictional commerce platform.

The primary surface is a pipeline. A merchandiser uploads a supplier's spreadsheet, drags in a
folder of product photos, and clicks one button: *Generate listing.* Behind that click, roughly
thirty model calls fire across nine steps: `ingest → clarify → categorize → write copy →
content blocks → price → assemble launch package → brand-voice polish → publish`, turning a
raw supplier feed into a finished, merchandised storefront listing.

A batch pipeline can't show everything, though. So the same fictional company runs a few sibling
surfaces, and we reach for them only when the pipeline genuinely can't make the point:

- a **shopper assistant** (a conversational agent, for multi-turn, memory, human-in-the-loop),
- a **merchant helpdesk** (retrieval over policies and docs, for RAG),
- a **repricing agent** (monitors competitors and acts, for genuine autonomy),
- a **category-research agent** (for research fan-out and synthesis).

One world, a few surfaces. The pipeline carries the first-hand *From production* stories; the
siblings are demonstrated in the companion repo.

## The shape of every chapter

Each chapter hits the same beats, so you always know where to look:

1. **The decision it resolves:** one line, up top.
2. **The way in:** a concrete hook, a scene, a question, a real failure.
3. **The durable principle:** the part that won't age.
4. **The litmus test:** model decides or code decides?
5. **How to do it:** code pulled from a tested file, so the prose can't drift from reality.
6. **When *not* to / the anti-pattern:** which feeds the [catalog](../catalogs/anti-patterns.md).
7. **In the carrier:** where this lives in Listing Studio.
8. **Maturity + evidence:** a quiet lens line up top (Standard / Established / Emerging /
   Contested), cited sources, and a *From production* note where I've shipped it.

## Suggested paths

- **The whole argument, in order:** [Foundations](../foundations/index.md) →
  [The Unit](../the-unit/index.md) → [Composition](../composition/index.md).
- **Just the genuinely-new patterns:** [Tool Use](../the-unit/tool-use.md),
  [Evaluator-Optimizer](../composition/evaluator-optimizer.md),
  [Fan-Out](../composition/fan-out.md), [The Specialist Panel](../composition/specialist-panel.md).
- **The deflations:** [The Router That Isn't One](../composition/the-router-that-isnt.md), then
  the [Anti-Patterns Catalog](../catalogs/anti-patterns.md).

> **This site is a work in progress.**
> The v1 launch slice (Foundations, The Unit, Composition, a little Craft, State-Not-Memory,
> and the Anti-Patterns Catalog) is being filled in chapter by chapter. Pages marked *stub*
> are scaffolding, not finished writing. [Contributions welcome.](../contributing.md)
