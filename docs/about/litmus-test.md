# The Litmus Test

> **The decision it resolves:** is a given pattern genuinely new, or a familiar one wearing an
> "agentic" costume?

A while back I made a list of the "agentic design patterns" in a system I'd built. A dozen of
them. I was a little proud of the list.

Then I looked harder. One I'd been about to file under the canonical "routing" pattern turned
out, in my code, to be a dictionary. The caller hands it a label, it looks up a function. I'd
been writing that exact thing since the 2000s. A few others were just retry loops and callbacks
that happened to live inside an agent.

Here's where I landed, and it's the spine of this whole reference:

## Building with agents is still engineering

The useful question was never "what are the agentic patterns?" It's **which of the patterns in
front of you are genuinely new because a model is making a decision, and which are the same ones
we've always used, with a model now sitting in one of the slots.**

So, for any pattern in your system, ask one question:

> **Who makes the decision: the model, or your code?**

**If the model makes the call, it's genuinely new.** It decides to reach for a tool. It judges
whether its own draft is good enough and loops if not. It reads a list and decides how many
workers to spawn. It picks which kind of expert to reason as. Nothing in the old toolbox could
make a judgement call in the middle of a control flow. These can.

**If your code makes the call and the model just does the work inside the structure, it's a
pattern you already know.** A lookup table that routes a request. A loop that retries on failure.
A callback that fires when a step finishes. Useful, necessary, and not new.

## The honest three-way split

Sort a realistic pattern set this way and the result is humbling.

| The model decides (new) | Your code decides (engineering you knew) | A feature, or a coined name |
|---|---|---|
| Tool use | Dispatch / front controller | Structured output |
| Evaluator-optimizer | Retry with backoff | Two-pass generation |
| Orchestrator-workers | Graceful degradation | The humanizer pass |
| Specialist-hat panel | The observer rule | |

And one honest draw: **prompt chaining**. Your code controls the order, so by the test it's just
a pipeline, an old idea. But you split the work up *because one model call couldn't hold the
whole task reliably*. An old structure, used for a new reason.

That gap is the point of this reference. Not which patterns you used. **Which ones the model
actually changed.**

## Why this matters beyond pedantry

Mislabelling a dictionary as "intelligent routing" isn't just imprecise. It sets the wrong
expectations for cost, failure modes, and testing. A dispatch table is deterministic and you
test it like any branch. A model making the routing call is non-deterministic and needs evals.
Calling them the same thing hides exactly the risk a technical leader needs to see.

When in doubt, **downgrade the claim**. It's the honest move, and it's the one that protects your
credibility.

---

Next: [How we label →](how-we-label.md) · [How to read this →](how-to-read.md)
