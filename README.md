# agentic-engineering

The source for **[agentic-engineering.work](https://agentic-engineering.work)** — an honest,
curated reference on building with agents.

Most "agentic patterns" are ordinary design patterns with a model dropped into one slot. A few
are genuinely new. This reference sorts them with one question — **who makes the decision, the
model or your code?** — and labels every claim by how grounded it is (`[prod]` / `[repo]` /
`[call]` / `[weather]`).

It's a crowd-sourced, maintainer-curated reference. PRs welcome — see
[`docs/contributing.md`](docs/contributing.md).

## Repo layout (monorepo)

```
.
├── docs/              # the site content (MkDocs + Material)
├── listing-studio/    # the companion code — the carrier examples, as tested files
├── mkdocs.yml         # site config
└── .github/workflows/ # build + deploy to GitHub Pages
```

Code samples in the docs are included from real files in `listing-studio/` so the prose can't
drift from working code.

## Local development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   ·   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve     # http://127.0.0.1:8000
mkdocs build     # static site into ./site
```

## License

- **Prose:** Creative Commons (final terms TBD — CC-BY or CC-BY-SA).
- **Code:** MIT or Apache-2.0 (TBD).

See [`docs/contributing.md`](docs/contributing.md) before opening a PR.
