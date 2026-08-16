# Voice & Style

> **Why this exists:** the prose is the product, and the default failure of machine-written prose
> is not error, it is blandness: competent sentences that commit to nothing and teach nothing.
> This spec defines the target and gives a critic something concrete to enforce. An author cannot
> reliably judge their own blandness, so we do not rely on judgement. We rely on a rubric.

## The target register

This is a **reference**, written in the reference register, the one Fowler's articles and
Hammant's trunkbaseddevelopment.com live in: plain, declarative, organized, opinionated, concrete.
Authority comes from clear thinking and a stated position, not from lyrical sentences.

Plain is not impersonal, and it is not dull. Fowler writes "What most appeals to me about the debt
metaphor"; Hammant writes "merge hell" and "live happily ever after". First person, direct address
to the reader, a dry joke, and an opinion the author would defend at a conference all belong here.
What does not belong is the apparatus of the personal essay: the childhood memory, the weather
frame, the scene set for its own sake. Those go to the **distribution blog posts**. Same research,
two products: an authoritative chapter here, a warmer post that links to it.

An earlier version of this file said "do not try to make a reference chapter sing." That
over-corrected, and it produced pages that passed every gate and that nobody wanted to finish. The
bar now: **a competent, busy engineer should want to keep reading, and should be able to quote one
sentence to a colleague without editing it.** A chapter that is merely inoffensive has failed.

## The rules

1. **Lead with the claim, then the evidence.** Never bury the point under throat-clearing.
2. **A concrete instance within two sentences of any abstraction.** Every general claim lands on a
   specific: a Listing Studio field, a real number, a named failure. No claim travels alone.
3. **Commit.** State a position. "It depends" is only allowed if you immediately say *on what*, and
   then pick. The maturity lens and litmus test are mandatory commitments.
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
11. **The hook cannot outrun the Gotchas.** The strongest capability claim in the opening must
    survive the failure-modes section. If the chapter later says the pattern fails half the time,
    the hook cannot say the problem "goes away." State the capability and its boundary together.
    *Test: take the boldest sentence in the opening, then find where Gotchas qualifies it. If
    nothing does, one of the two is wrong.*
12. **Concept is portable; wire format is not.** Do not write that a mechanism is "the same on
    every API." The mental model is shared; the concrete fields differ by vendor (Anthropic
    `input_schema`, OpenAI `parameters` / `strict`), and any code sample is one vendor's shape, so
    label it. A schema validates *shape*, never *business truth*; say which you mean.
13. **Concept leads, carrier illustrates (the cold-reader rule).** A reader who lands here first,
    from a search, knowing nothing about Listing Studio, must be able to follow the opening and
    grasp what the chapter is about within two sentences. That is the whole rule. It is satisfied
    by a general statement of the problem, and it is equally satisfied by a carrier scene that
    glosses itself as it goes ("the front door of a supplier-feed pipeline") as long as the concept
    lands immediately. What it forbids is presupposition: carrier internals, personas, or pipeline
    steps used as if the reader already knows them. "Concrete" means specific, not carrier-insider.
    The chapter teaches the pattern, not the pipeline.
14. **Do not narrate the apparatus.** The maturity lens, the litmus test, the grounding label and
    the chapter's own structure are the editor's constitution, not furniture for the reader. Never
    write "on this book's litmus test", "which is why the lens line above carries two verdicts",
    "this reference files it under X", or any sentence explaining how the labels relate to one
    another. Make the call instead: "Structurally this is a 1970s batch pipeline. What is new is
    the reason you split." The reader who wants the system reads
    [How we label](../docs/about/how-we-label.md); everyone else wants the verdict, not a tour of
    the filing cabinet.
15. **Epistemic housekeeping lives in the footnote.** "Not peer-reviewed, so treat as directional",
    "paraphrased, exact wording pending verification against the print edition",
    "benchmark-specific the day it was published" all belong in the source note. The body states
    the claim at the confidence it has earned and moves on. Honest uncertainty about the *subject*
    stays in the body, where it is interesting ("no default router has settled"); bookkeeping about
    the *citation* goes below, where it is checkable.
16. **Anchor to the reader's own screen where you can.** Where a tool the reader already runs (a
    coding agent, a browser agent, a vendor agent SDK) visibly implements the mechanism, one
    sentence pointing at it beats a paragraph of abstraction, because the reader can go and check.
    "The sub-agent your coding agent spawns for a search is this pattern: a fresh window and a
    narrow brief" is verifiable; "orchestrators delegate to workers" is not. Name public tools
    plainly. The carrier is for the worked example, not a substitute for the world the reader
    lives in.
17. **Deflate to clarify, then build.** The deflation ("this is a dictionary") is a lens, not a
    mood. On the same page the reader gets the constructive answer: the proven way to do the thing,
    what it costs, what breaks. A chapter that only debunks fails the busy engineer as surely as
    one that only hypes, and it reads as contrarian for sport. 3.2 is the shape: the dict, then LLM
    routing done properly.

## The interest bar (checked before the critic, not after)

Every other gate in this pipeline optimizes against badness: tells, hedges, blandness, overclaims.
None of them can produce a page worth paying for, because avoiding all the bad things is not the
same as doing a good one. A draft that clears every negative gate and interests nobody is the
default failure mode of this whole system, and it is the one we now check for first.

Before a draft goes to the critic, it must clear three positive checks:

1. **A thesis.** One sentence, written into the coverage map before drafting, that the whole
   chapter argues. If the chapter can only be described as "everything about routing", it has no
   thesis and it will read as a survey. 3.2's thesis: *most things called routers are dictionaries,
   and the two mechanisms fail in opposite directions.* 3.1's: *you split the prompt not for
   modularity but because one call cannot hold the task, and the split is worthless without a gate.*
2. **A way in.** A story, a scar, a concrete failure, or a provocation inside the first two
   sentences. Not a definition. The definition arrives once the reader wants it.
3. **A line worth quoting.** At least one sentence a reader would paste into a team chat. It is
   earned by a specific or by a judgment the author owns, never by a manufactured aphorism (see the
   anti-samples in `voice-samples.md`). If you cannot find one in your own draft, you have written a
   summary of the topic rather than an argument about it. The line travels furthest when it is
   *falsifiable*: a specific claim a reader could test and argue with. 12-Factor Agents' "past
   roughly 40% context fill, quality degrades" is quoted across unaffiliated blogs for that reason;
   nobody quotes a survey.

A draft failing any of the three goes back before a single tell is counted.

**Sought, not gated: a name for the idea.** Where the chapter's central idea can carry a short,
plain name (*state, not memory*; *the router that isn't*; *the lethal trifecta*, borrowed with
credit), give it one and use it consistently: in the gloss, in the anti-patterns catalog, in the
quick-reference. Names are how a reference gets quoted for years (technical debt, the strangler fig,
trunk-based development); cute names are how it gets mocked. The test: would an engineer say it in
a design review without irony? Not every chapter has one, and a chapter is never sent back for
lacking one. It is sent back for manufacturing one (see the anti-samples in `voice-samples.md`).

## The blandness checklist (the critic scores against this)

A draft fails if it shows these. The prose-critic agent flags each by line.

- **Abstraction with no instance.** A general claim with no concrete anchor nearby.
- **Hedge with no recommendation.** "There are trade-offs to consider" and then no recommendation.
- **List-itis.** Bullets doing the work that argued prose should do.
- **Restatement.** The intro, body, and conclusion saying the same thing. Low information density.
- **Generic example.** A *vague* stand-in ("imagine an online store") where the specific carrier
  example (the standing desk in Listing Studio) would teach more. This flags vagueness, not
  generality: an abstraction that never lands on a specific fails, whether it opened the chapter or
  buried itself in the middle.
- **False balance.** Every option presented as equally good. A reference weights; it recommends.
- **No throughline.** Sections that do not build on each other toward the chapter's point. If the
  chapter has no thesis (see the interest bar above), this failure is guaranteed.
- **Apparatus narration.** The page explaining its own labels, sections, or classification scheme
  instead of using them (rule 14).
- **Unearned length.** Prose past the chapter's budget in `design-system.md` that is not the
  argument: a second worked example, a table the catalogs should own, a neighbour pattern
  re-explained instead of linked.
- **Hook outruns the chapter.** An opening claim the Gotchas later contradict (the pattern "just
  works", then a section on how often it does not).
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
- The **humanizer skill** (`.claude/skills/humanizer/`, checked into this repo; based on Wikipedia's "Signs of AI
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
- narrating the apparatus ("on this book's litmus test", "the lens line above carries two
  verdicts", "this reference files it under chaining")
- numbered section headings ("## 1. Why you'd reach for it"), which make a chapter read as a form
  that was filled in rather than an argument that was made
- the witness-protection war story: a first-hand scar told in passive, de-peopled prose ("the
  production system this carrier recasts exhibited the failure mode described above"). Recast the
  *world*, not the voice; see the carrier disclosure in `docs/about/how-to-read.md`
- docstrings and code comments that re-teach the surrounding prose

## How the critic and gates work together

The interest bar comes first, and it is a judgment call, not a lint: thesis, way in, quotable
line. Only a draft that clears it is worth reviewing. Then the deterministic linter catches the
mechanical tells, the humanizer audit catches the vocabulary and rhetorical patterns, and a
separate editor agent does the cut pass and scores the prose against the structural rules and the
three-jobs test, returning line-referenced findings rather than a rewrite the writer would just
rubber-stamp. The author reconciles for technical fidelity (code, citations, links must survive
intact). The final taste call is the author's, and anything flagged there is added to the living
tells list above.

**One writer owns the voice.** Where a draft is assembled from several engines (the private
`/fused-draft` harness), fuse for *coverage*: the union of what each engine found, the best
citations, the sharpest examples. Do not fuse for prose. Consensus prose is averaged prose, and
averaging is how personality dies. After the merge, one writer does a single continuous voice pass
over the whole chapter with `voice-samples.md` in context, rewriting rather than stitching. That
pass is a writing step and it comes last, after the merge and before the critic.
