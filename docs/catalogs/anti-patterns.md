# The Anti-Patterns Catalog

> **The decision it resolves:** which expensive mistakes is your design about to make?

Every chapter has a "when NOT to" section. This page aggregates them, the failure modes that
turn a slick demo into a system that quietly lies, burns money, or can't be trusted in production.
It's meant to be the most shareable page on the site: skim it before you build.

!!! note "Stub: the entries below are the spine; full write-ups land as each chapter does."

## The catalog

Each entry will grow into a short, honest write-up: the smell, why it's tempting, the real cost,
and the fix.

- **Cargo-cult memory:** bolting on a vector DB "for memory" when what you needed was
  [state](../knowledge/state-not-memory.md). Complexity with no payoff.
- **Fake routing:** billing a static dispatch table as intelligent
  [routing](../composition/the-router-that-isnt.md). Sets wrong expectations for cost and testing.
- **The agent that should've been a script:** reaching for autonomy where a deterministic
  pipeline was correct, cheaper, and testable.
- **Fine-tuning as a flinch:** training a model to fix what a better prompt or some context
  would have fixed. The most expensive rung on the ladder, climbed first.
- **The mega-prompt:** cramming a whole task into one call because splitting felt like
  over-engineering, then fighting reliability forever.
- **The silent failure:** a path through the graph that doesn't report back, so the UI shows
  progress that isn't real.
- **Vibes-based eval:** shipping changes because the new output "looks better," with no golden
  set and no judge.
- **Trusting structured output without validation:** assuming a schema-shaped response is a
  *correct* response.
- **Over-orchestration:** spawning agents and roles where one well-structured call would do;
  see [More Than One Agent](../frontier/more-than-one-agent.md).

## How to use this page

If you're reviewing a design, read every entry as a question: *are we doing this?* The honest
answer to even one of them usually saves a sprint.
