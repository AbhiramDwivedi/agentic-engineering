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
- **Generic example.** "Imagine an online store" instead of the standing desk in Listing Studio.
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

## The structural rules (the deeper layer)

The word-list above catches vocabulary. It does not catch the sentence-level habits that make
machine prose feel synthetic even when every word is clean. These eight rules target structure
and stance. Each has a test.

1. **Explain, do not perform.** Cut any sentence whose main job is rhythm or a quotable ending.
   *Test: delete it. Is information lost? If no, it stays cut.*
2. **One person, talking to a colleague.** First and second person where natural.
   *Test: could you say this aloud to a coworker without wincing?*
3. **Kill the contrast reflex.** "Not X, it's Y" / ", not Y" / "isn't A, it's B" is allowed only
   when X is a real misconception worth correcting, never as setup for a punchy Y.
4. **No colon-zingers, no appositive drama.** A colon followed by a restatement-for-effect
   becomes a plain sentence.
5. **Concrete verbs and nouns over abstract "is" definitions** and nominalizations.
6. **Do not narrate significance.** Cut "the whole point", "exactly what separates",
   "importantly". Show the thing; let the reader weigh it.
7. **Earn assertions with a specific, not an intensifier.** Replace "the entire value",
   "without debate", "genuinely" with a fact, a number, or an example.
8. **Let rhythm follow content.** No default imperative-then-fragment beat.

Each reference paragraph must do at least one of three jobs: explain the code, state a cited
fact, or make a judgment the author owns. A paragraph doing none of the three is decoration; cut
it.

## The three revision passes (after the draft)

1. **Cut-for-information** (rule 1, applied to every sentence).
2. **Read-aloud** (does a person sound like this, or a press release?).
3. **Specificity** (every claim has a concrete anchor, or it goes).

## The toolchain that enforces this

- `python meta/prose_lint.py <file>` is a deterministic gate. It flags the pattern-detectable
  tells (em-dash, contrast reflex, colon-zinger, copula avoidance, AI vocabulary, rule of three,
  signposting) with line numbers, and prints stylometric metrics (contrast rate, nominalization
  density, sentence-length variance). High recall: it over-flags, and a judgment pass rules on
  each. A regex does not forgive a tell the way an LLM reviewer does.
- The **humanizer skill** (`~/.claude/skills/humanizer`, based on Wikipedia's "Signs of AI
  writing") runs as a tell-audit on the draft. Note its own guidance: for reference and technical
  text, plain and neutral is the correct human voice, so do not let it inject opinion or first
  person where the register does not call for it.
- The **editor is a different agent than the writer.** The cut and humanizer-audit pass runs in a
  fresh agent that did not write the draft, because a writer cannot reliably cut their own
  darlings (proven on this very chapter).

## The living tells list

Every tell we catch goes here so the same note is never needed twice. The linter reads from this
intent.

- the contrast reflex ("not X, it's Y"), used for rhythm rather than to correct a real error
- the manufactured aphorism as a section's closing line ("the model may propose, your tool disposes")
- narrating significance instead of showing it ("the whole point", "exactly what separates")
- the colon-then-restatement zinger
- the imperative-sentence-then-short-fragment metronome

## How the critic and gates work together

The deterministic linter catches the mechanical tells. The humanizer audit catches the
vocabulary and rhetorical patterns. A separate editor agent does the cut pass and scores the
prose against the structural rules and the three-jobs test, returning line-referenced findings,
not a rewrite the writer would just rubber-stamp. The author reconciles for technical fidelity
(code, citations, links must survive intact). Ram makes the final taste call, and whatever he
flags is added to the living tells list above.
