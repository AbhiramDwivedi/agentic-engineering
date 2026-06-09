# agentic-engineering

The source for **[agentic-engineering.work](https://agentic-engineering.work)**, an honest,
curated reference on building with agents.

Most "agentic patterns" are ordinary design patterns with a model dropped into one slot. A few
are genuinely new. This reference sorts them with one question, **who makes the decision, the
model or your code?**, and labels every technique by how proven it is (Standard / Established /
Emerging / Contested), with every non-obvious claim citing its evidence.

It's a crowd-sourced, maintainer-curated reference, and most chapters are still drafts or
stubs; that's by design, so the full map is visible while it fills in. PRs welcome. See
[`docs/contributing.md`](docs/contributing.md).

## Repo layout (monorepo)

```
.
├── docs/              # the site content (MkDocs + Material)
├── listing-studio/    # the companion code: the carrier examples, as tested files
├── meta/              # the design system, voice spec, and templates chapters are built from
├── mkdocs.yml         # site config
└── .github/workflows/ # tests + deploy to GitHub Pages
```

Code shown in the docs is copied verbatim from tested files in `listing-studio/`, and
`tests/test_doc_sync.py` fails CI if the prose and the source drift apart.

## Local development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   ·   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve     # http://127.0.0.1:8000
mkdocs build     # static site into ./site

cd listing-studio && python -m pytest   # companion code + doc-sync tests
```

## License

- **Prose** (`docs/`): [CC BY 4.0](LICENSE-CONTENT.md)
- **Code** (`listing-studio/` and everything else): [MIT](LICENSE)

See [`docs/contributing.md`](docs/contributing.md) before opening a PR.
