<!--
  CHAPTER TEMPLATE. Copy this file to start a chapter. Delete these comments as you go.
  Flow: gloss -> WHY -> WHAT -> HOW -> GOTCHAS -> IN SHORT -> lens line -> SOURCES -> SEE ALSO.

  BEFORE YOU DRAFT, two things must exist in meta/coverage/<slug>.md:
    - THE THESIS: one sentence the whole chapter argues. Not a topic ("routing"), an argument
      ("most things called routers are dictionaries, and the two mechanisms fail in opposite
      directions"). A chapter without one becomes a survey, and a survey is the thing readers
      close.
    - THE BUDGET: which row of the budget table in design-system.md this chapter is written to
      (deflation ~1,500-2,000 prose words; standard pattern ~2,000-2,800; flagship up to ~3,500;
      framing ~1,200-2,000). A ceiling, not a target.

  THE READING LINE COMES FIRST. The page opens on the gloss and then the way in. The lens line
  (maturity / who-decides / grounding) sits at the FOOT, above Sources. Nobody was ever pulled
  into a page by a grounding label.

  DO NOT NARRATE THE APPARATUS (voice-and-style rule 14). Never write "on this book's litmus
  test", "the lens line above carries two verdicts", or "this reference files it under X". Make
  the call in plain prose and move on.

  CONCEPT FIRST, CARRIER SECOND (the cold-reader rule). A reader landing here from a search,
  knowing nothing about Listing Studio, must grasp what the chapter is about within two
  sentences. A general statement of the problem does that. So does a carrier scene that glosses
  itself as it goes ("the front door of a supplier-feed pipeline"). What is forbidden is
  presupposition: carrier internals used as if the reader already knows them.

  COMPLETENESS CHECK (the classic pattern form, kept as content, not as headings).
  The Alexandrian fields map onto our flow; before a chapter ships, confirm each is answered:
    Context + Problem  -> Why (the gap, the cost story)
    Forces             -> Why (trigger list) + Gotchas (the tensions and costs)
    Solution           -> What (the concept) + How (the working minimum, then the scale-up)
    Resulting context  -> Gotchas (liabilities) + In short (the weighted recommendation)
    Related patterns   -> See also (and SAY WHY each link relates, never a bare list)
    Example            -> the carrier callout + the companion repo
  We deliberately do NOT use those headings: this is a read-through reference in prose, not
  a form-filled catalog. The form is the checklist; the prose is the page. Answering a field
  in one clause is a complete answer. Length is not coverage.
-->

# N.M Canonical Pattern Name

<!--
  TITLE: the canonical noun the field searches for ("Tool Use", "Fan-Out"), never the evocative
  phrase. The evocative phrase opens the gloss line below instead. References get cited and
  Googled by their nouns. Section headings below are UNNUMBERED.
-->

*<The gloss: optionally open with the evocative phrase, then the definition in miniature, problem
to solution, in one or two sentences. This line is also the chapter's entry in the patterns index,
so it must stand alone.>*

*Also called: <common aliases>.*

## Why you'd reach for it
<!--
  THE WAY IN COMES FIRST, and it is the most important paragraph in the chapter. A story, a scar,
  a concrete failure, or a provocation, inside the first two sentences. Not a definition; the
  definition arrives in What, once the reader wants it.

  A `> **From production.**` callout may BE the opening when the real scar is the best way in.
  Tell it like a person telling a colleague: first person, the actual argument, what nearly
  shipped. Recast the WORLD into the carrier, never the voice into passive de-peopled prose.

  Then, in whatever order the argument wants:
    - THE GAP: what is missing without this, stated generally, including the sharp edge (what the
      system does WRONG, not merely what it can't do).
    - THE COST STORY: the gap grounded in one concrete carrier scenario, with the cost in time,
      money, or risk.
    - THE FIX, in miniature: two or three sentences.
    - THE TRIGGER LIST: when you need it, short and scannable, then the counter-trigger (when you
      don't, and the simpler thing instead).
  These are beats to hit, not a running order to obey.
-->

## What it actually is
<!--
  A crisp, quotable definition (one paragraph). Then commit to both labels IN PLAIN PROSE, without
  naming the machinery:
    - Does the model decide, or your code? Genuinely new, or engineering you already knew?
    - How proven is it, and on what evidence?
  Then disambiguate from the neighbours it actually gets confused with. Two or three, in prose,
  each with a link. A comparison matrix across many patterns belongs in docs/catalogs/, not here.
  Epistemic housekeeping about citations ("preprint", "paraphrased") goes in the footnote.
-->

## How to do it
<!--
  THE SHAPE DIAGRAM comes first: one mermaid flowchart of the pattern's runtime shape.
  The visual language, on every diagram in the reference:
    - rounded nodes ( )   = the model decides
    - rectangles   [ ]    = your code decides
    - hexagons     {{ }}  = a capability, not a pattern
      ```mermaid
      flowchart LR
          A["your code"] --> B("the model decides") --> C["your code"]
      ```
  A hand-authored SVG may take the mermaid's place, and only its place, when boxes and arrows
  hide the thing the reader has to see. Argue for it; see design-system.md.
  Then ONE PRIMARY LISTING: the cheapest thing that works, ideally under 30 lines, with the
  contract it depends on beside it. AFTER THE CODE, ONE RUN AS A NUMBERED TRACE. Five plain steps
  teach runtime behaviour faster than a second listing does; when in doubt add a trace step, not
  more code.
  THEN THE MULTIPLICITY SCALE-UP: the singular-to-plural step every production reader hits (one
  tool -> several, one worker -> a pool). Show the structural delta, not a second full listing.
  CODE DIET (design-system.md): comments state constraints the code cannot show, never re-teach
  the prose. A listing whose story the diagram and trace already tell goes in
  `<details markdown><summary>` or stays in the companion repo behind a link.
  Code is shown INLINE in a ```python block, copied verbatim from a tested source file that
  carries `# --8<-- [start:name] / [end:name]` anchors; `tests/test_doc_sync.py` fails CI if
  the chapter and the source drift. Never paste code that has no anchored, tested source.
  Show it in the carrier (skip this callout when the carrier already carried the chapter's
  opening story; two tellings of the same thing is restatement):
-->

> **In Listing Studio.** <Where this lives in the pipeline or a sibling surface. Three sentences max.>

#### Wiring it to a provider
<!--
  The multi-provider content tabs (`=== "LangGraph"` first and default, then OpenAI Responses,
  then Anthropic Messages) go HERE, last in How, after the trace, so they never interrupt the
  reading line. Do not explain a framework's internals; the audience can read its docs.
-->

<!--
  OPTIONAL SECTIONS (controlled-extension menu, design-system.md §1). Insert here, AFTER How and
  BEFORE Gotchas, ONLY when the topic earns it, using these exact names and this order:
    ## Security & trust         - a real trust boundary (untrusted input, supply chain).
    ## Cost                     - token/compute/$ spend is a first-order design concern.
    ## Ecosystem & tooling      - a real distribution / sharing / tooling landscape.
    ## Operating in production  - observability, rollout, blast-radius, on-call.
    ## Evaluating it            - how you'd measure it works.
  A simple chapter uses none and keeps its sharp edges in Gotchas. Need a section the menu lacks?
  Propose it for sign-off; never invent one silently.
-->

## Gotchas
<!--
  The real costs: latency, spend, complexity, non-determinism.
  When NOT to use it, and the simpler thing instead. Name the anti-pattern it feeds.
  Failure modes, with a production scar where one exists:
-->

> **From production.** <A real failure and what it taught. Only if true and first-hand. Otherwise delete.>

## In short
<!-- A weighted recommendation, not a summary. What you would actually do. -->

<!-- THE LENS LINE, at the foot: metadata for the reader who is checking the work. -->
<small class="chapter-meta">**Maturity: <Standard|Established|Emerging|Contested|n/a>** (<half-sentence justification>) · *Who decides:* <the model | your code | a feature | n/a> · *Grounding:* <production | companion repo | research | reasoned></small>
<!-- add for fast-moving topics:  · *Last reviewed:* YYYY-MM. Keep the <small> on ONE line:
     Material-only syntax (divs with markdown, !!! admonitions, tabs) breaks GitHub rendering,
     and every page must read correctly in both places. -->

## Sources
<!-- Footnotes. Every non-obvious claim above carries one, and the epistemic caveats live here. -->

## See also
<!-- Cross-links to related chapters, each with a clause saying why it relates. -->

## Further reading
<!--
  A SHORT curated set of external deep-dives for the reader who wants more: the spec, the key
  paper, the primary doc, the best skeptical take. Roughly 4-6 items, each with a one-line "what
  it gives you". Distinct from Sources (per-claim footnotes) and See also (internal cross-links).
  Point to the canonical primary source, not a blog aggregator; prefer links already verified in
  Sources. Omit the section only if no good external deep-dive exists.
-->
