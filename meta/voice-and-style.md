# Voice & Style

> **Why this exists:** the prose is the product, and the default failure of machine-written prose
> is not error, it is blandness: competent sentences that commit to nothing and teach nothing.
> This spec defines the target and gives a critic something concrete to enforce. An author cannot
> reliably judge their own blandness, so we do not rely on judgement. We rely on a rubric.

## The target register

This is a **reference**, written in the reference register, the one Fowler's articles and
Hammant's trunkbaseddevelopment.com live in: plain, declarative, organized, opinionated, concrete.
Authority comes from clear thinking and a stated position, not from lyrical sentences.

The lyrical, personal-essay voice (the scene-setting hook, the childhood memory, the weather
frame) is real and good, but it belongs in the **distribution blog posts**, not the reference
body. Same research, two products: a plain authoritative chapter here, a warmer post that links to
it. Do not try to make a reference chapter sing. Make it true, clear, and committed.

## The rules

1. **Lead with the claim, then the evidence.** Never bury the verdict under throat-clearing.
2. **A concrete instance within two sentences of any abstraction.** Every general claim lands on a
   specific: a Listing Studio field, a real number, a named failure. No claim travels alone.
3. **Commit.** State a position. "It depends" is only allowed if you immediately say *on what*, and
   then pick. The maturity and litmus verdicts are mandatory commitments.
4. **Hedge once, plainly, or not at all.** Honest uncertainty is good: "I don't know whether X;
   here is what we know." Reflexive hedging on every sentence is the enemy.
5. **Prose for argument, bullets for enumerations.** If a list is making an argument, it should be
   paragraphs. Reserve bullets for things that are genuinely a set.
6. **No em-dashes.** Standing author preference. Use periods, colons, commas, parentheses.
7. **Vary rhythm.** Mix long reasoning sentences with short ones. Uniform paragraph length is a
   tell. A one-line paragraph, used rarely, lands.
8. **No unsubstantiated claims.** No universal quantifiers ("everyone knows", "nobody does"), no
   invented statistics. Use defensible wording ("widely cited", "common in practice") and cite.
   The pull to overclaim is strongest in openings; that is exactly where credibility is won or
   lost.
9. **Use the carrier.** Examples come from Listing Studio (see the carrier bible), consistently.
10. **Earn every paragraph.** If a paragraph does not add information or move the argument, cut it.

## The blandness checklist (the critic scores against this)

A draft fails if it shows these. The prose-critic agent flags each by line.

- **Abstraction with no instance.** A general claim with no concrete anchor nearby.
- **Hedge with no verdict.** "There are trade-offs to consider" and then no recommendation.
- **List-itis.** Bullets doing the work that argued prose should do.
- **Restatement.** The intro, body, and conclusion saying the same thing. Low information density.
- **Generic example.** "Imagine an online store" instead of the heater in Listing Studio.
- **False balance.** Every option presented as equally good. A reference weights; it recommends.
- **No throughline.** Sections that do not build on each other toward the chapter's point.
- **Surface tells.** See the list below.

## The tell-list (avoid)

Words and constructions that mark machine prose. Not banned by reflex, but each one is a smell to
justify or cut:

- em-dashes (hard rule: none)
- "delve", "leverage", "utilize", "robust", "seamless", "in today's landscape", "ever-evolving"
- "it's worth noting", "it's important to note", "that said", "at the end of the day"
- "not just X, but Y" as a reflex
- a tricolon ("X, Y, and Z") in every other sentence
- opening a section with "In this section, we will..."
- a concluding paragraph that begins "In conclusion" or merely restates
- title-case headers and generic headers ("Overview", "Background", "Conclusion")

## How the critic uses this

The prose-critic agent reads a draft and returns line-referenced findings against the checklist
and tell-list, plus a one-line verdict per section: does it commit, is it concrete, does it earn
its place. It does not rewrite. The author (me) revises; the human (Ram) makes the final taste
call on whether a section is boring and should die.
