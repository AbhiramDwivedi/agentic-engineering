# Contributing

This is a **crowd-sourced, maintainer-curated** reference. The judgement here is meant to be
argued with, and improved.

## What's welcome

Pretty much everything:

- **New patterns or use cases** you've shipped or built.
- **Sharpening a litmus test:** make the case that a "model decides" pattern is really
  "code decides," or vice versa.
- **Weather updates:** a model changed, a framework's API moved, a price dropped.
- **Corrections:** a wrong claim, a broken example, a dead link.
- **Examples and translations.**

One maintainer reviews and merges every pull request. Nothing lands without review, and a
better-argued change to the core thesis is welcome. The bar is *"is it more honest, better
grounded?"*, not *"is it mine?"*

## Before you write: the design system

The reference reads as one authored work because every chapter follows a shared spec. Read these
first (in the repo under `meta/`):

- **`meta/design-system.md`:** the five layers and the components, start here.
- **`meta/chapter-template.md`:** copy this to begin a chapter. The fixed Why / What / How /
  Gotchas flow.
- **`meta/voice-and-style.md`:** the reference register, the blandness checklist, the tell-list.
- **`meta/carrier-bible.md`:** the Listing Studio world. Pull every concrete specific from here;
  do not invent your own.

## The two rules that are non-negotiable

The standard is high so the surface can stay open. Every PR must:

1. **Carry a maturity lens and cite its evidence**, and not overclaim.

    | Lens | Means |
    |---|---|
    | **Standard** | the accepted default |
    | **Established** | proven and common, with known trade-offs |
    | **Emerging** | gaining traction, still settling |
    | **Contested** | overclaimed or disputed. Lead with the skeptical read |

    Every non-obvious claim needs a source (paper / primary doc / benchmark). Where it's
    first-hand, mark it with a *From production* or *In the companion repo* callout. No confident
    prose about something untested. No coined label sold as canon. When in doubt, **downgrade the
    claim.**

2. **Back code claims with a tested snippet.** Code samples are included from real files in the
    repo (via MkDocs snippet includes), not pasted as assertions. If you add a code claim, add
    the file it's extracted from.

## Confidentiality

Everything is taught through the public **Listing Studio** commerce world. Do not contribute
material that identifies a specific private/proprietary system, its real personas, or its
internal artifacts. Recast it into the commerce setting so the idea travels without the baggage.

## Mechanics

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   ·   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve          # live preview at http://127.0.0.1:8000
```

Then open a PR against `main`. Keep it focused: one pattern, one fix, or one chapter per PR
makes review fast.
