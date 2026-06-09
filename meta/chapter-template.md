<!--
  CHAPTER TEMPLATE. Copy this file to start a chapter. Delete these comments as you go.
  Flow: HEAD (scan) -> WHY -> WHAT -> HOW -> GOTCHAS -> FOOT.
  WHY comes first so a reader deciding whether they need this chapter is served; the HEAD
  carries the one-line definition so a reader who already knows they need it is served too.
  Pull every concrete specific from meta/carrier-bible.md. Obey meta/voice-and-style.md.
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
  Motivation. The problem it solves and what breaks without it. The cost of getting it wrong,
  in time / money / risk (the leadership framing). The trigger: when you need it, when you don't.
  A brief "From production" opening is allowed here when a real scar is the best way in.
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
  Then the minimal code version (the cheapest thing that works), then scale up.
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
