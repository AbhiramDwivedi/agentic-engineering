---
description: Run the full chapter-production pipeline (research → sign-off → code → draft → QA → gates)
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

## Stage 1 — Coverage research, then STOP for sign-off

Spawn **coverage-researcher** with the chapter title and slug. It writes
`meta/coverage/<slug>.md`.

Then **stop and present the must-cover list (and the open questions) to the author for
trimming and sign-off. Do not proceed to any later stage in the same turn.** Scope is a human
decision; the signed-off must-cover list is the chapter's contract.

## Stage 2 — Companion code

From the signed-off map, list the code the chapter needs (which anchors, demonstrating what,
in which `listing-studio/` file). Spawn **coder-tester** with that list. It reports back the
anchor names and green tests. If the chapter needs no new code, say so and skip.

## Stage 3 — Draft

Spawn **chapter-writer** with: the signed-off coverage map, the anchor names and files from
stage 2, and the chapter path. It returns the full chapter markdown plus its list of
unverified items.

> **Maintainer enhancement (optional).** The draft may instead be produced by a multi-engine
> fusion step: several engines draft the same full-chapter brief and an Opus reviewer fuses their
> coverage onto the chapter-writer draft as the spine (which alone carries the anchored, tested
> code). This runs only from the private planning workspace, where the extra engines' CLIs are
> authed. Contributors without it use **chapter-writer** alone, the portable default. Either way
> the output is one draft at the chapter path; everything from Stage 4 on is identical.

## Stage 4 — Adversarial QA (parallel)

Spawn **prose-critic** and **fact-checker** on the draft at the same time. Both get the
chapter path; the fact-checker also gets the coverage-map path. The critic returns
line-referenced voice and carrier-continuity findings; the fact-checker returns per-citation
verdicts, the must-cover completeness walk (covered / partial / missing per signed-off item),
and its own read on the maturity verdict. A **missing** must-cover item sends the draft back
to stage 3; it is not reconcilable away.

## Stage 5 — Reconcile

Apply the findings yourself, cutting hard. Technical fidelity wins conflicts: code blocks,
citations, and links must survive intact. If the fact-checker downgraded the maturity verdict,
the chapter takes the downgrade. Anything the critic flagged that you keep, you must be able
to defend as semantically load-bearing.

## Stage 6 — Gates (all must pass)

```bash
cd listing-studio && python -m pytest          # includes doc-sync
cd .. && mkdocs build --strict
python meta/prose_lint.py docs/<chapter>.md
```

Run the **humanizer** skill on the final prose. Re-check dual rendering by eye: no `!!!`, no
content tabs, callouts as blockquotes, one-line `<small class="chapter-meta">`.

## Stage 7 — Ship

Update the `mkdocs.yml` nav entry (drop "(planned)", canonical-noun title). Maintainer only:
run the confidentiality sweep from the private planning workspace before anything is pushed;
contributors instead note in the PR that examples are carrier-world only. Present the result
to the author with a one-paragraph summary of what the QA panel changed; commit only when the
author approves.
