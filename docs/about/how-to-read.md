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

### About the war stories

Listing Studio is invented. The scars are not.

The systems I actually shipped these patterns in are private and will stay that way, so the
stories are recast into this commerce world: the domain changes, the specialists get new hats, the
product loses its name. What survives the recasting is everything that makes a war story worth
reading: the argument in the design review, the thing that broke, the fix that didn't work, the
number that mattered. When you read *"we almost shipped a router,"* someone almost shipped a
router. It just wasn't a router for supplier feeds.

The alternative was to strip the stories down until they were safe, which is how you get prose
like *"the production system this carrier recasts exhibited the failure mode described above."*
True, unobjectionable, and worth nobody's time. I'd rather tell you the story in a costume than
not tell you the story.

Anything **not** grounded in first-hand experience is labelled as what it is: demonstrated in the
companion repo, drawn from research, or reasoned. That line never moves.

## The shape of every chapter

Each chapter hits the same beats, so you always know where to look:

1. **The gloss:** one italic line under the title. What this is, in miniature.
2. **Why you'd reach for it:** the way in. A scar, a failure, a provocation, then what the pattern
   costs you if you skip it.
3. **What it actually is:** the definition, who makes the decision (the model, or your code?), and
   how it differs from the two or three patterns it gets confused with.
4. **How to do it:** a shape diagram, code pulled from a tested file so the prose can't drift from
   reality, and one run traced step by step.
5. **Gotchas:** the real costs, when *not* to use it, and the anti-pattern it feeds, which lands in
   the [catalog](../catalogs/anti-patterns.md).
6. **In short:** what I'd actually do.
7. **The lens line, then sources:** maturity (Standard / Established / Emerging / Contested),
   who decides, what the claim is grounded in, and every citation.

That last one sits at the *bottom* on purpose. It's how you check the work, not how you start
reading. If you want the verdicts across every pattern at a glance, the
[quick-reference](../catalogs/quick-reference.md) is one table.

## Suggested paths

- **The whole argument, in order:** [Foundations](../foundations/index.md) →
  [The Unit](../the-unit/index.md) → [Composition](../composition/index.md).
- **Just the genuinely-new patterns:** [Tool Use](../the-unit/tool-use.md),
  [Evaluator-Optimizer](../composition/evaluator-optimizer.md),
  [Orchestrator-Workers](../composition/fan-out.md), [The Specialist Panel](../composition/specialist-panel.md).
- **The deflations:** [Routing & Dispatch](../composition/the-router-that-isnt.md), then
  the [Anti-Patterns Catalog](../catalogs/anti-patterns.md).

> **This site is a work in progress.**
> The v1 launch slice (Foundations, The Unit, Composition, a little Craft, State-Not-Memory,
> and the Anti-Patterns Catalog) is being filled in chapter by chapter. Pages marked *stub*
> are scaffolding, not finished writing. [Contributions welcome.](../contributing.md)
