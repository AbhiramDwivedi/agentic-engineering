<!--
  CHAPTER TEMPLATE. Copy this file to start a chapter. Delete these comments as you go.
  Flow: HEAD (scan) -> WHY -> WHAT -> HOW -> GOTCHAS -> FOOT.
  WHY comes first so a reader deciding whether they need this chapter is served; the HEAD
  carries the one-line definition so a reader who already knows they need it is served too.
  Pull every concrete specific from meta/carrier-bible.md. Obey meta/voice-and-style.md.

  COMPLETENESS CHECK (the classic pattern form, kept as content, not as headings).
  The Alexandrian fields map onto our flow; before a chapter ships, confirm each is answered:
    Context + Problem  -> Why (the gap, the cost story)
    Forces             -> Why (trigger list) + Gotchas (the tensions and costs)
    Solution           -> What (the concept) + How (the working minimum, then the scale-up)
    Resulting context  -> Gotchas (liabilities) + In short (the weighted recommendation)
    Related patterns   -> See also (and SAY WHY each link relates, never a bare list)
    Example            -> the carrier callout + the companion repo
  We deliberately do NOT use those headings: this is a read-through reference in prose, not
  a form-filled catalog. The form is the checklist; the prose is the page.
-->

# N.M Canonical Pattern Name

<!--
  TITLE: the canonical noun the field searches for ("Tool Use", "Fan-Out"), never the evocative
  phrase. The evocative phrase opens the gloss line below instead. References get cited and
  Googled by their nouns.
-->

<!-- HEAD: the scan. A reader who reads only this knows what it is and whether they need it. -->
<div class="chapter-meta" markdown>
**Maturity: <Standard|Established|Emerging|Contested|n/a>** (<half-sentence justification>) · *Who decides:* <the model | your code | a feature | n/a> · *Grounding:* <production | companion repo | research | reasoned>
<!-- add for fast-moving topics:  · *Last reviewed:* YYYY-MM -->
</div>

*<The gloss: optionally open with the evocative phrase, then the definition in miniature, problem to solution, in one or two sentences. This line is also the chapter's entry in the patterns index, so it must stand alone.>*

## Why you'd reach for it
<!--
  Fixed shape, four beats:
    1. THE GAP: what is missing without this, stated plainly. Include the sharp edge, what
       the system does WRONG (not just can't do) when the gap is hit.
    2. THE COST STORY: one concrete carrier scenario where the gap burns you, with the cost
       in time / money / risk (the leadership framing).
    3. THE FIX, in miniature: how this pattern closes the gap, two or three sentences.
    4. THE TRIGGER LIST: when you need it, as a short scannable bulleted list, then the
       counter-trigger (when you don't, and the simpler thing instead).
  A brief "From production" opening is allowed when a real scar is the best way in.
-->

## What it actually is
<!--
  A crisp, quotable definition (one paragraph). Then commit to both labels:
    - Litmus: does the model decide, or your code? Genuinely new, or familiar?
    - Maturity: which tier, and the cited basis for it.
  Then disambiguate from neighbours: "this is X, not Y" (e.g. dispatch is not LLM routing).
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
  Then the minimal code version (the cheapest thing that works). AFTER THE CODE, ONE RUN
  AS A NUMBERED TRACE: what the model called, what the code answered, how it ended. Five
  plain steps teach the runtime behaviour faster than a paragraph about the code does.
  THEN THE MULTIPLICITY SCALE-UP: the singular-to-plural step every production reader hits
  (one tool -> several tools, one worker -> a pool, one turn -> a conversation). A chapter
  that shows only the toy singular is incomplete; show the structural delta, not a second
  full listing.
  SIMPLICITY RULE: the example exists to teach the concept, never to show off the system.
  No internal field names or infra detail beyond what the point needs; the carrier callout
  is three sentences at most. When in doubt, cut the apparatus and keep the trace.
  Code is shown INLINE in a ```python block, copied verbatim from a tested source file that
  carries `# --8<-- [start:name] / [end:name]` anchors; `tests/test_doc_sync.py` fails CI if
  the chapter and the source drift. Never paste code that has no anchored, tested source.
  Show it in the carrier:
-->

!!! example "In Listing Studio"
    <Where this lives in the pipeline or a sibling surface, with real field names from the bible.>

<!-- Framework differences, where they matter, go in tabs:
=== "LangGraph"
=== "Plain Python"
-->

## Gotchas
<!--
  The real costs: latency, spend, complexity, non-determinism.
  When NOT to use it, and the simpler thing instead. Name the anti-pattern it feeds.
  Failure modes, with a production scar where one exists:
-->

!!! production "From production"
    <A real failure and what it taught. Only if true and first-hand. Otherwise delete.>

## In short
<!-- A weighted recommendation, not a summary. What you would actually do. -->

## Sources
<!-- Footnotes. Every non-obvious claim above carries one. -->

## See also
<!-- Cross-links to related chapters. -->
