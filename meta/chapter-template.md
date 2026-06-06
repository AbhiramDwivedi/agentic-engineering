<!--
  CHAPTER TEMPLATE. Copy this file to start a chapter. Delete these comments as you go.
  Flow: HEAD (scan) -> WHY -> WHAT -> HOW -> GOTCHAS -> FOOT.
  WHY comes first so a reader deciding whether they need this chapter is served; the HEAD
  carries the one-line definition so a reader who already knows they need it is served too.
  Pull every concrete specific from meta/carrier-bible.md. Obey meta/voice-and-style.md.
-->

# N.M Chapter Title

<!-- HEAD: the scan. A reader who reads only this knows what it is and whether they need it. -->
<div class="chapter-meta" markdown>
**Maturity: <Standard|Established|Emerging|Contested|n/a>** (<half-sentence justification>) · *Who decides:* <the model | your code | a feature | n/a> · *Grounding:* <production | companion repo | research | reasoned>
<!-- add for fast-moving topics:  · *Last reviewed:* YYYY-MM -->
</div>

*<One or two sentences: the decision this chapter resolves, and the definition in miniature.>*

## Why you'd reach for it
<!--
  Motivation. The problem it solves and what breaks without it. The cost of getting it wrong,
  in time / money / risk (the leadership framing). The trigger: when you need it, when you don't.
  A brief "From production" opening is allowed here when a real scar is the best way in.
-->

## What it actually is
<!--
  A crisp, quotable definition (one paragraph). Then commit to both verdicts:
    - Litmus: does the model decide, or your code? Genuinely new, or familiar?
    - Maturity: which tier, and the cited basis for it.
  Then disambiguate from neighbours: "this is X, not Y" (e.g. dispatch is not LLM routing).
-->

## How to do it
<!--
  Minimal version first (the cheapest thing that works), then scale up.
  Code is INCLUDED from a tested file, never pasted:
      ```python
      --8<-- "listing-studio/path/to/file.py:anchor"
      ```
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
  When NOT to use it, and the simpler thing instead — name the anti-pattern it feeds.
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
