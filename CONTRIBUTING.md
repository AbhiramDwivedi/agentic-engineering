# Contributing

Thanks for wanting to sharpen the reference. The full guide lives at
[`docs/contributing.md`](docs/contributing.md), which is also rendered on the site.

The two non-negotiables, up front:

1. **Every contribution carries a maturity lens** (Standard / Established / Emerging /
   Contested) and argues it honestly.
2. **Every non-obvious claim cites its evidence**: a paper, a primary doc, or a benchmark.
   No confident prose about something untested, and no coinage sold as canon.

Code shown in chapters must come verbatim from a tested file in `listing-studio/`
(`tests/test_doc_sync.py` enforces this). Run `python -m pytest` in `listing-studio/` and
`mkdocs build --strict` before opening a PR.
