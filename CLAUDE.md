# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

## What this repo is

The source for **agentic-engineering.work**: an honest, curated reference on building with
agents, published with MkDocs + Material to GitHub Pages. The deliverable is prose plus the
tested companion code it quotes. This file is the entry point; the real constitution lives in
`meta/` — **read the relevant meta file before writing or editing anything**:

| File | What it governs |
|---|---|
| `meta/design-system.md` | Structure, components, dual-rendering constraint, diagram language |
| `meta/voice-and-style.md` | The reference register, blandness checklist, the tell-list |
| `meta/voice-samples.md` | Calibrated before/after samples of the target voice |
| `meta/chapter-template.md` | The chapter skeleton every pattern page is built from |
| `meta/carrier-bible.md` | The Listing Studio commerce world all examples live in |

## Non-negotiables

1. **Maturity lens + cited evidence.** Every chapter carries a maturity verdict (Standard /
   Established / Emerging / Contested) argued honestly in prose, and every non-obvious claim
   cites a source (paper, primary doc, benchmark) as a footnote. No confident prose about
   something untested; no coinage sold as canon. When in doubt, downgrade the claim.
2. **Dual rendering.** Every page must read correctly on the built site **and** GitHub's file
   view. Banned in content: `!!!` admonitions, content tabs, attr_list buttons
   (`{ .md-button }`), markdown inside block-level `<div>`s. Use instead: bold-labelled
   blockquotes for callouts (`> **In Listing Studio.** …`), a single-line
   `<small class="chapter-meta">…</small>` for the lens line, Mermaid for diagrams,
   `<details markdown><summary>` for expandable listings.
3. **Code cannot drift from prose.** Every code block shown in a chapter is copied verbatim
   from a tested file in `listing-studio/`, marked with `# --8<-- [start:NAME]/[end:NAME]`
   anchors; `listing-studio/tests/test_doc_sync.py` fails CI if they diverge. Never paste
   code into a chapter that has no anchored, tested source.
4. **All examples live in the Listing Studio carrier world** (see the carrier bible). Never
   claim production experience for something only demonstrated; `> **From production.**`
   callouts are reserved for first-hand scars and `> **In the companion repo.**` for
   demonstrations.
5. **Titles are canonical nouns** ("Tool Use", "Fan-Out") in both the H1 and `mkdocs.yml`
   nav; the evocative phrase lives in the italic gloss line under the head.
6. **Diagram visual language** (sitewide): rounded nodes `( )` = the model decides;
   rectangles `[ ]` = your code decides; hexagons `{{ }}` = a capability, not a pattern.

## Gates — run before every commit that touches `docs/` or `listing-studio/`

```bash
cd listing-studio && python -m pytest          # companion code + doc-sync tests
cd .. && mkdocs build --strict                  # zero warnings tolerated
python meta/prose_lint.py docs/<changed>.md     # voice gate (hard: em-dashes; soft: AI tells)
```

A `humanizer` skill is checked in at `.claude/skills/humanizer/` — run it on substantial new
prose before it ships. Soft lint flags default to rewrite; keep a flagged construction only
when it is semantically load-bearing.

## Agents — the production pipeline, checked in at `.claude/agents/`

| Agent | Model | Job |
|---|---|---|
| `coverage-researcher` | Opus | pre-writing deep research; emits the coverage map that sets scope |
| `chapter-writer` | Opus | drafts/revises chapters against the meta/ constitution |
| `prose-critic` | Opus | adversarial voice review; line-referenced findings, never rewrites |
| `fact-checker` | Sonnet | verifies every citation and claim; argues the maturity verdict |
| `coder-tester` | Sonnet | builds the anchored, tested companion code in `listing-studio/` |

The editor is always a different agent than the writer (see `meta/voice-and-style.md`).
**`/new-chapter <N.M Title>`** (`.claude/commands/new-chapter.md`) runs the whole pipeline:
coverage-researcher → **author signs off the must-cover list** → coder-tester → chapter-writer
→ prose-critic + fact-checker in parallel → reconcile → gates → ship. Scope sign-off is a hard
stop; never skip it.

## Layout

```
docs/              # site content; nav order lives in mkdocs.yml and must match
listing-studio/    # companion code: every chapter snippet's tested source
meta/              # the constitution (see table above) + prose_lint.py
.github/workflows/ # pytest + strict-build CI, deploy to GitHub Pages
```

Prose is CC BY 4.0, code is MIT. The site deploys from `main` via GitHub Actions; branch
protection requires the `pytest` and `build` checks on PRs.
