#!/usr/bin/env python3
"""Deterministic prose linter for the reference's chapters.

It does NOT judge quality. It flags pattern-detectable tells at high recall, with
line numbers, so a human (or the editor pass) can rule on each. It also prints a
few stylometric metrics so you can compare a draft against plain, good prose.

The point: an LLM reviewer reads for sense and forgives patterns (it missed an
em-dash this project shipped once). A regex does not forgive. Run this in the
gates next to the build.

It also enforces the dual-rendering constraint (design-system.md §2): Material-only
syntax that the strict build happily passes but GitHub's file view renders as
garbage. Those are HARD fails.

Usage:  python meta/prose_lint.py <file.md> [more.md ...] [--hard-only]
        --hard-only: report and fail on hard rules only (the CI mode; soft
        flags need human judgment and would over-flag stubs).
Exit:   non-zero if any HARD tell is present in any file.
"""
from __future__ import annotations

import re
import statistics
import sys

# --- patterns: (label, regex, hard?) -------------------------------------------------
HARD = True
SOFT = False

PATTERNS = [
    ("em/en dash", r"[—–]", HARD),
    ("curly quote", r"[“”‘’]", HARD),
    # negative parallelism / contrast reflex (humanizer S9)
    ("not only / not just", r"\bnot (only|just|merely)\b", SOFT),
    ("isn't...it's contrast", r"\b(is|are|was|were)n['’]t\b[^.?!]{0,40}\bit['’]?s\b", SOFT),
    ("'..., not ...' contrast", r",\s+not\s+\w+", SOFT),
    ("'. It is X' contrast", r"\.\s+It['’]?s?\s+(is\s+)?\w+\.", SOFT),
    ("tailing negation", r",\s+no\s+\w+\.", SOFT),
    # copula avoidance (humanizer S8)
    ("copula avoidance", r"\b(serves as|stands as|boasts|marks a|represents a|functions as|acts as)\b", SOFT),
    # persuasive-authority tropes (humanizer S27)
    ("authority trope", r"\b(the real question|at its core|what really matters|fundamentally|the heart of the matter|the deeper issue|in reality)\b", SOFT),
    # signposting (humanizer S28)
    ("signposting", r"\b(let['’]s (dive|explore|break|look)|here['’]s what you need|in this (section|chapter) we|without further ado)\b", SOFT),
    # filler / hedging (humanizer S23/24)
    ("filler phrase", r"\b(in order to|due to the fact|at this point in time|it is important to note|it['’]s worth noting|that said|the ability to|in the event that)\b", SOFT),
    # AI vocabulary (humanizer S7)
    ("AI vocab", r"\b(delve|leverage|utilize|robust|seamless|vibrant|tapestry|testament|underscore[sd]?|showcase[sd]?|intricate|intricacies|pivotal|crucial|foster(s|ing)?|garner|interplay)\b", SOFT),
    # significance inflation (humanizer S1)
    ("significance inflation", r"\b(is a testament|plays a (vital|key|crucial|pivotal) role|marking a (pivotal|key) moment|sets the stage|evolving landscape|reshap(es|ing))\b", SOFT),
    # -ing superficial analysis tacked on (humanizer S3)
    ("trailing -ing clause", r",\s+(highlighting|underscoring|emphasizing|reflecting|symbolizing|showcasing|ensuring|fostering|enabling|allowing)\b", SOFT),
    # over-signposted significance
    ("editorializing significance", r"\b(the whole point|the entire (value|point)|exactly what separates|the key (thing|point) (is|here)|importantly)\b", SOFT),
    # intensifiers
    ("intensifier", r"\b(very|really|truly|entirely|genuinely|simply|clearly|obviously|vast(ly)?|incredibly)\b", SOFT),
    # colon-zinger: ': a/the <short restatement>' at clause end
    ("colon-zinger", r":\s+(a|an|the)\s+\w+(\s+\w+){0,6}\.", SOFT),
]

# --- dual-rendering violations (design-system.md §2): Material-only syntax that
# --- breaks on GitHub's file view. mkdocs build --strict does NOT catch these.
DUAL_RENDER = [
    ("admonition (!!!/???)", re.compile(r"^\s*(!{3}|\?{3}\+?)(\s|$)")),
    # Content tabs are banned EXCEPT the sanctioned multi-provider labels (design-system.md):
    ('content tab (=== "...")',
     re.compile(r'^\s*===\s+"(?!(?:LangGraph|OpenAI Responses API|Anthropic Messages API)")')),
    ("attr_list button ({ .md-button })", re.compile(r"\{\s*\.md-button")),
    ("markdown inside <div>", re.compile(r"<div[^>]*\bmarkdown\b", re.I)),
]

AI_HEADER_FILLER = re.compile(r"^#{1,6}\s")
NOMINALIZATION = re.compile(r"\b\w{4,}(tion|ment|ity|ness|ance|ence)\b", re.I)
ADVERB = re.compile(r"\b\w{3,}ly\b", re.I)


def strip_noise(lines: list[str]) -> list[tuple[int, str]]:
    """Return (line_no, text) for prose only: drop code fences, includes, HTML
    comments, the chapter-meta div, footnote defs, and bare URLs."""
    out: list[tuple[int, str]] = []
    in_fence = False
    in_comment = False
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if "<!--" in line:
            in_comment = True
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if "--8<--" in line:
            continue
        if line.strip().startswith('<div class="chapter-meta"') or line.strip() == "</div>":
            continue
        if re.match(r"^\[\^[^\]]+\]:", line):  # footnote definition (URLs, refs)
            continue
        # strip inline markdown link targets but keep the visible text
        line = re.sub(r"\]\([^)]+\)", "]", line)
        line = re.sub(r"<https?://[^>]+>", "", line)
        out.append((i, line))
    return out


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def dual_render_hits(lines: list[str]) -> dict[str, list[int]]:
    """Scan raw lines (code fences excluded) for Material-only syntax."""
    hits: dict[str, list[int]] = {}
    in_fence = False
    for i, raw in enumerate(lines, 1):
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for label, rx in DUAL_RENDER:
            if rx.search(raw):
                hits.setdefault(label, []).append(i)
    return hits


def main(path: str, hard_only: bool = False) -> int:
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    prose = strip_noise(lines)
    prose_text = " ".join(t for _, t in prose if not AI_HEADER_FILLER.match(t))

    hits: dict[str, list[int]] = {}
    hard_count = 0
    for label, pat, hard in PATTERNS:
        rx = re.compile(pat, re.I)
        for ln, text in prose:
            if AI_HEADER_FILLER.match(text):
                # still check headers for hard fails + title-case, but skip prose-only rules
                if not hard and label not in ("em/en dash", "curly quote"):
                    continue
            for _ in rx.finditer(text):
                hits.setdefault(label, []).append(ln)
                if hard:
                    hard_count += 1

    # title-case header check (humanizer S17): section headers (##+) only, not the H1 title
    for ln, text in prose:
        if text.startswith("##"):
            words = re.findall(r"[A-Za-z][A-Za-z'-]+", text[text.index(" "):])
            caps = [w for w in words if w[0].isupper() and w.lower() not in ("i",)]
            if len(words) >= 3 and len(caps) >= max(3, int(0.8 * len(words))):
                hits.setdefault("title-case header", []).append(ln)

    # dual-rendering: HARD, scanned on raw lines (these live outside prose too)
    dr = dual_render_hits(lines)
    for label, lns in dr.items():
        hits.setdefault(label, []).extend(lns)
        hard_count += len(lns)

    if hard_only:
        for label, lns in sorted(hits.items()):
            is_hard = label in ("em/en dash", "curly quote") or label in dr
            if is_hard:
                shown = ", ".join(map(str, lns[:12])) + (" ..." if len(lns) > 12 else "")
                print(f"  {path}: [HARD] {label} x{len(lns)}: lines {shown}")
        return 1 if hard_count else 0

    # --- metrics ---
    words = re.findall(r"[A-Za-z'’]+", prose_text)
    wc = len(words)
    sents = sentences(prose_text)
    lens = [len(re.findall(r"[A-Za-z'’]+", s)) for s in sents] or [0]
    nominal = len(NOMINALIZATION.findall(prose_text))
    adverbs = len(ADVERB.findall(prose_text))
    contrast = sum(len(hits.get(k, [])) for k in (
        "not only / not just", "isn't...it's contrast", "'..., not ...' contrast", "'. It is X' contrast"))

    def per_k(n: int) -> float:
        return round(1000 * n / wc, 1) if wc else 0.0

    print(f"\n=== prose_lint: {path} ===")
    print(f"words: {wc}   sentences: {len(sents)}")
    if len(lens) > 1:
        print(f"sentence length: mean {statistics.mean(lens):.1f}, stdev {statistics.pstdev(lens):.1f}, "
              f"short(<8) {100*sum(1 for x in lens if x < 8)//len(lens)}%, long(>30) {100*sum(1 for x in lens if x > 30)//len(lens)}%")
    print(f"per 1000 words -> contrast: {per_k(contrast)}, nominalizations: {per_k(nominal)}, "
          f"adverbs(-ly): {per_k(adverbs)}, intensifiers: {per_k(len(hits.get('intensifier', [])))}")
    print("  (rough plain-prose targets: contrast < 8, nominalizations < 35, sentence stdev > 5)")

    print("\n--- flags (review each; high recall, not all are wrong) ---")
    if not hits:
        print("  none")
    labelled = PATTERNS + [("title-case header", "", SOFT)] + [(lab, "", HARD) for lab, _ in DUAL_RENDER]
    for label, _pat, hard in labelled:
        if label in hits:
            lns = hits[label]
            tag = "HARD" if hard else "soft"
            shown = ", ".join(map(str, lns[:12])) + (" ..." if len(lns) > 12 else "")
            print(f"  [{tag}] {label} x{len(lns)}: lines {shown}")

    print()
    if hard_count:
        print(f"FAIL: {hard_count} hard tell(s) present (dash/quote or dual-render violation). Fix before shipping.")
        return 1
    print("OK: no hard tells. Review soft flags with judgment.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    hard_only = "--hard-only" in args
    paths = [a for a in args if a != "--hard-only"]
    if not paths:
        print("usage: python meta/prose_lint.py <file.md> [more.md ...] [--hard-only]")
        sys.exit(2)
    rc = 0
    for p in paths:
        rc |= main(p, hard_only=hard_only)
    if hard_only:
        print("OK: no hard tells in any file." if rc == 0 else "FAIL: hard tell(s) present (see above).")
    sys.exit(rc)
