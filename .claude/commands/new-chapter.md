---
description: Run the full chapter-production pipeline (research → adversarial review → code → draft → QA → gates → PR)
argument-hint: <chapter number and title, e.g. "2.2 Structured Output">
---

Run the chapter-production pipeline for: **$ARGUMENTS**

You are the orchestrator. The specialist agents in `.claude/agents/` do the heavy work; you
sequence them, carry context between them, and reconcile. Do not write the chapter yourself,
and do not let a later stage start before its input exists.

## Stage 0 — Resolve

Find the chapter's stub under `docs/` and its entry in the `mkdocs.yml` nav. Read
`CLAUDE.md` and skim the `meta/` constitution if you have not this session. Confirm the
canonical-noun title. If the chapter already has substantial text, treat this as a rewrite:
the coverage map must mark existing coverage `[*]` and gaps `[+]`.

## Stage 1 — Coverage research

Spawn **coverage-researcher** with the chapter title and slug. It writes
`meta/coverage/<slug>.md`.

**The map is a spec, not an essay.** Budget the body (header note through Named-idea candidates)
to **~1,500 words**; Sources, the sweep log, and the Stage 1.5 disposition log sit outside the
budget. The exemplar `meta/coverage/tool-use.md` is under 900 words and covers a flagship chapter.
A map that argues its own case at chapter length has stopped being a contract and started being a
first draft, and it makes the review below cost more than the chapter it governs.

## Stage 1.5 — Independent adversarial review, then fold-in (required)

A coverage map reviewed only by the agent that wrote it is not reviewed. Before the map governs
anything, a **second, independent engine** reviews it.

1. **Write the review brief** to `<staging>/<slug>.codex-review.brief.md`. It names the map path
   and the repo root, and asks for findings on: (A) must-cover gaps; (B) bloat and seam violations
   against neighbouring chapters; (C) maturity verdicts re-derived from the cited evidence;
   (D) citations, vendor claims, and tool defaults verified against current primary sources;
   (E) the thesis; (F) the litmus line; (G) aliases, anchors, named-idea candidates;
   (H) internal contradictions and carrier-bible consistency; (I) confidentiality — any trace of
   private process, private documents, or the maintainer's workspace in a file that ships
   publicly. Cap it at ~1,800 words, findings grouped **BLOCKER / MAJOR / MINOR**, ending in a
   one-line verdict. State plainly: *do not rewrite the map, do not modify any file.*

2. **Run the reviewer.** Maintainers use the OpenAI Codex CLI (see the private workspace's
   `/new-chapter` for the exact invocation). Contributors without a second CLI may use any
   second model, or a second `coverage-researcher` instance briefed as an adversary — the
   requirement is independence from the agent that wrote the map, not a specific vendor.

3. **Fold in through the original researcher, never yourself.** Resume the researcher that wrote
   the map, hand it the review, and require it to **verify each finding against primary sources
   before accepting it** — reviewers are confidently wrong often enough that unverified fold-in
   trades one error for another. It records every finding in a `## Second-reviewer pass` section
   of the map with a disposition: accepted / partial / rejected, and why. A rejected finding needs
   the counter-evidence written down.

4. **Re-verify the map** after fold-in: footnote refs match definitions in both directions, the
   word budget holds, and the confidentiality scan is clean. Tell the researcher up front that the
   map body must never mention a private read, the assignment, the maintainer, or a private
   workspace — the map ships publicly. The sweep and disposition logs may reference lead sources;
   the body may not.

## Stage 1.6 — Author-only questions (non-blocking)

Stage 1.5 settles scope, evidence, and seams. Three things it cannot settle, because they are not
questions of fact:

- **First-hand production claims.** Only the author knows what they actually shipped. No agent may
  add or widen a "From production." callout.
- **Coinage.** A named idea is authorial voice, not a research finding.
- **Anything that edits a shipped chapter, the nav, or the constitution.** Blast radius beyond the
  chapter is the author's call.

Collect these in an `## Author-only questions` section, each with **a stated conservative default**
— no production claim, no coinage, no cross-chapter edit. **The pipeline proceeds on the defaults
and does not stop here.** Carry the list forward; it becomes a checklist in the pull request, where
the author rules on it with the finished chapter in front of them rather than a spec.

## Stage 2 — Companion code

From the reviewed map, list the code the chapter needs (which anchors, demonstrating what,
in which `listing-studio/` file). Spawn **coder-tester** with that list. It reports back the
anchor names and green tests. If the chapter needs no new code, say so and skip.

## Stage 3 — Draft

Spawn **chapter-writer** with: the reviewed coverage map, the anchor names and files from
stage 2, and the chapter path. It returns the full chapter markdown plus its list of
unverified items.

> **Maintainer enhancement (optional).** The draft may instead be produced by a multi-engine
> fusion step: several engines draft the same full-chapter brief and a reviewer on the strongest
> available model fuses their
> coverage onto the chapter-writer draft as the spine (which alone carries the anchored, tested
> code). This runs only from the private planning workspace, where the extra engines' CLIs are
> authed. Contributors without it use **chapter-writer** alone, the portable default. Either way
> the output is one draft at the chapter path; everything from Stage 4 on is identical.

## Stage 3.5 — The explanatory diagram

Spawn **diagrammer** with the chapter path and its coverage-map path. It draws the one diagram the
chapter carries, the definition in picture form, and places it under the crisp definition
paragraph in *What it actually is*. It runs after the draft on purpose: the drawing states the
argument the chapter actually made, not the one the outline promised.

It writes the `.svg` and the image line, nothing else. If it reports that the drawing and the
definition paragraph disagree, reconcile that now rather than at Stage 5 — usually the prose is
the thing that drifted.

## Stage 4 — Adversarial QA (parallel)

Spawn **prose-critic**, **fact-checker**, and **cold-reader** on the draft at the same time. All
three get the chapter path; the fact-checker also gets the coverage-map path; the cold-reader gets
**only** the chapter path (it reads cold, by design). The critic returns line-referenced voice and
carrier-continuity findings; the fact-checker returns per-citation verdicts, the must-cover
completeness walk (covered / partial / missing per must-cover item), and its own read on the
maturity verdict; the cold-reader returns the everyday-engineer read: the ninety-second test, every
undefined term at the point it was met, the build test on the How, the verify test, and the line it
would quote (or that there is none), and the picture-alone test on the diagram in *What*. A **missing** must-cover item sends the draft back to stage 3;
it is not reconcilable away. A cold-reader "no" on the ninety-second test or "no line worth
quoting" is an interest-bar failure and also goes back to stage 3.

## Stage 5 — Reconcile

Apply the findings yourself, cutting hard. Technical fidelity wins conflicts: code blocks,
citations, and links must survive intact. If the fact-checker downgraded the maturity verdict,
the chapter takes the downgrade. Anything the critic flagged that you keep, you must be able
to defend as semantically load-bearing. Cold-reader findings are fixed by **defining, glossing,
and linking**, never by thinning the argument or cutting the chapter to the reader's current
knowledge; the page must lift the reader, not meet them where they stand.

## Stage 6 — Gates (all must pass)

```bash
cd listing-studio && python -m pytest          # includes doc-sync
cd .. && mkdocs build --strict
python meta/prose_lint.py docs/<chapter>.md --diagram-strict   # HARD-fails signposting + narrated-significance and a What section with no diagram; reports a slop score
```

Run the **humanizer** (de-slop) pass on the final prose as a separate editor, never the writer
reviewing itself: it must clear every prose_lint HARD tell and drive the reported slop score down
(cadence, signposting, performed fragmentation). Then re-check dual rendering by eye. Re-check dual rendering by eye: no `!!!`, no
content tabs, callouts as blockquotes, one-line `<small class="chapter-meta">`.

## Stage 7 — Ship as a pull request

1. Update the `mkdocs.yml` nav entry: drop `(planned)`, canonical-noun title.
2. **Maintainer only, non-negotiable:** run the confidentiality sweep from the private planning
   workspace over everything the branch touches, before anything is pushed. Contributors instead
   note in the PR that examples are carrier-world only.
3. Branch off `main` (never off another chapter's branch), commit, push, open the PR.

**The pull request is the author's review point.** It is where scope, voice, and claims get
judged, with the finished chapter in hand. Its body carries, in this order:

- the thesis in one line, and the word count against the budget row;
- the maturity verdict and the one sentence arguing it;
- **Author-only questions** — the Stage 1.6 list, as an unchecked checklist, each with the
  conservative default the chapter currently ships. These are the decisions no agent was allowed
  to make: production claims, coinage, cross-chapter edits;
- what the QA panel changed, in one paragraph;
- anything the fact-checker could not verify, listed plainly.

Do not merge. Opening the PR is where the pipeline ends.
