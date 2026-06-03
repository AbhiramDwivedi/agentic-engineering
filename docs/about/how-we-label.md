# How We Label

> **The decision it resolves:** how do you know what to trust here — what's standard, what's
> hype, and how do I know I'm not just reading another confident overclaim?

The internet does not need another confident guide to agents. What's actually scarce — the thing
this reference is built around — is an honest answer to *"is this real, is it standard, and how do
you know?"*

So every technique carries two quiet signals, and they're delivered in plain prose, not as a
dashboard. **No rings, no quadrants, no blips.** If you've seen a technology radar, this is
deliberately the opposite register: a sentence you could imagine Martin Fowler writing.

## 1. The maturity verdict

A single, honestly-argued line near the top of each chapter places the technique on a four-rung
scale:

| Verdict | What it means | How to read it |
|---|---|---|
| **Standard** | The accepted default. | Reach for it without much debate. |
| **Established** | Proven and common, with known trade-offs. | Safe, but know the trade-offs. |
| **Emerging** | Gaining traction, still settling. | Adopt deliberately; expect change. |
| **Contested** | Overclaimed or disputed. | Lead with the skeptical read before you commit. |

The verdict is the anti-hype function. When something is widely *talked about* but rarely *beats
the simpler thing*, it gets **Contested**, and the chapter says why. Concept and framing chapters
carry no verdict (`n/a`). Fast-moving topics also get a **Last reviewed** date, because a verdict
on this month's model landscape is only as good as its date.

## 2. Cited evidence

Every non-obvious claim footnotes a source — a paper, a primary doc, or a benchmark. Two kinds of
evidence both count, and the chapter is explicit about which it's leaning on:

!!! production "From production"
    Where I've actually shipped a technique in a real, revenue-bearing system, you'll see a
    callout like this — with the first-hand detail: the failure that taught the lesson, the
    number that mattered, the thing that broke at 2 a.m. This is the strongest evidence on the
    site, but it is *added on top of* researched coverage, never a substitute for it.

!!! inrepo "In the companion repo"
    Where a technique is demonstrated in **Listing Studio** (the public commerce code this site
    teaches through) rather than drawn from production, it's marked like this. The code is real
    and runs; it just didn't carry real money.

Everything else is grounded in cited research. **Sources are mandatory** — that requirement is the
single thing that most separates this reference from the overclaimers.

## Why labelling beats "trust me"

For you, the reader: the verdict tells you how hard to lean on what follows, and the citation
lets you check the work. For the reference itself: breadth is easy to fake, but *labelled,
sourced* breadth is not. That discipline is the moat.

It's also a [contribution rule](../contributing.md). Every pull request carries a maturity verdict
and cites its evidence. A PR that overclaims — confident prose about something untested, or a
coined label sold as canon — gets sent back, however good the writing. When in doubt, **downgrade
the claim.**

---

Next: [How to read this →](how-to-read.md)
