# The Litmus Test

> **The decision it resolves:** is a given pattern genuinely new, or a familiar one wearing an
> "agentic" costume?

Most of what gets sold as a new "agentic pattern" is an ordinary design pattern with a language
model dropped into one slot. A few are genuinely new. One question tells them apart, and it is the
spine of this whole reference:

> **Who makes the structural decision: the model, or your code?**

**If the model makes the call, it is genuinely new.** It decides to reach for a tool, judges its
own draft and loops, sizes its own work, or picks which kind of expert to reason as. Nothing in the
pre-LLM toolbox could make a judgement call in the middle of a control flow.

**If your code makes the call and the model is just the worker inside the structure, it is a
pattern you already know.** A lookup that routes a request, a loop that retries on failure, a
callback that fires when a step finishes. Useful, necessary, and not new.

This is a *classification* lens (is it new?), not a *quality* one (is it proven?). The two are
orthogonal axes, and [How We Label](how-we-label.md) carries the second. When in doubt, downgrade
the claim.

**The full treatment is [1.2 Who Decides?](../foundations/who-decides.md):** the four "model
decides" tells, the honest three-way split (four genuinely new, four just engineering, three that
are not patterns, and one honest draw), the dispatcher-is-not-routing deflation, and why
mislabelling changes what a system costs and how you have to test it.

---

Next: [How we label →](how-we-label.md) · [How to read this →](how-to-read.md)
