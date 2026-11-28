# Coverage map: Ingestion (chapter 6.1)

> Spec for what the chapter must cover. Angles run: vendor docs, academic/benchmarks, security,
> skeptical read, alias sweep, daily-tool, incidents, parser gotchas (folded from review).
> Skipped: practitioner writeups (no primary source beyond vendor docs).

**Thesis:** A model should be the last thing to touch a raw file, not the first: code parses
what is structured, isolates untrusted bytes behind a typed intermediate document with source
anchors, and calls vision only on the pages that need it.

**Budget:** Standard pattern, about 2,000 to 2,800 prose words.
**Carrier:** Listing Studio step 1 (ingest): Northvale Furnishings spreadsheet feed plus the
Aldsworth desk spec sheet and photos become a draft `Listing`.

## The mental model

Ingestion turns a file you did not write into a typed object your code owns, with a pointer
back to where each value came from. For a spreadsheet, code reads the cells; for a layout-heavy
PDF a vision model may read the page. Either way the output is a typed intermediate form, and
the content stays untrusted until code has checked it. Wrong attribute, wrong price, lost table:
most are decided here, quietly, before any model reasons about the product.

## Must-cover (9)

1. **Classify by content, route in code.** Sniff the real type (magic bytes, not extension),
   then route: sheet to a deterministic reader, text PDF to a parser, scan or photo to OCR or
   vision, Office/HTML files to a converter. A front controller, not LLM routing (code decides;
   3.2). *Skip it:* a mislabelled file takes the wrong path. **Standard.**
2. **Feeds are not documents.** Units, merged headers and locale numbers are code's job;
   determinism and exact arithmetic are the argument. The model resolves only what code cannot
   (a free-text "Size" column). Vendors differ here (Gemini reads `.xlsx`; Anthropic wants
   conversion), so the rule rests on determinism, not on one vendor's MIME list. **Standard.**
3. **Choosing a PDF path; benchmarks unsettled.** Paths: text-layer extraction; layout
   pipelines (Docling, Unstructured `hi_res`, LlamaParse); native vision input. Anthropic, OpenAI
   and Gemini all pair extracted text with page images (Gemini renders pages at 2 MP and
   extracts embedded text alongside). Rule: simple text layer, parse; tables, scans, columns,
   pipeline or vision; record which path made each value. OmniDocBench (arXiv:2412.07626) shows
   different strengths by document type; ParseBench (arXiv:2604.08538, LlamaIndex authors, so
   directional) finds no method strong on all five dimensions; olmOCR (arXiv:2502.18443) shows
   a small open model can be cheap. **Established** for "test on your own files"; **Contested**
   for "which parser wins."
4. **Parser errors cascade.** OHRBench (arXiv:2412.02592): OCR noise degrades downstream
   answers. A VLM can drop or invent cells silently. Mitigation: assert invariants (row counts,
   price ranges, GTIN check digits), spot-check, route doubtful pages to a human (4.3), evaluate
   (4.2). **Established.**
5. **Tables and images get their own treatment.** Keep a table as rows and cells; send the
   spec-sheet dimension diagram to a typed vision call (2.2), not OCR text. *Skip it:* a
   `height_range_in` of 25-50 lands under the wrong attribute. **Established.**
6. **Typed intermediate document with provenance.** Parse into elements (type, text, page,
   region) before extracting Listing fields (2.2); extraction never reads raw bytes. Every value
   keeps file, page and region, or sheet and cell. This gives a seam to test, cache and swap
   parsers, and a "show where this came from" review view. Docling's `DoclingDocument` is an
   instance, including its body/furniture split, which also keeps headers and boilerplate out of
   downstream context. **Established** (typed form); provenance **Standard** on deterministic
   parsers, **Emerging** as VLM bounding-box grounding. One-line pointer: chunking → 5.2.
7. **Untrusted bytes, twice.** Parser level: size caps (compressed and uncompressed, for zip
   bombs in Office Open XML), no external entities in XML-bearing files, server-generated
   filenames, parsers in a sandbox (9.4); OWASP File Upload and XXE cheat sheets. Model level:
   hidden or tiny text, metadata, image pixels carry instructions (OWASP LLM01 calls robust
   multimodal defenses open research). Trail of Bits (2025-08-21) hid text that appears only
   after downscale, against Gemini CLI, Vertex AI Studio, the Gemini web UI and API, Google
   Assistant and Genspark; advice: cap upload dimensions instead of downscaling, show the user
   what the model sees, require confirmation for sensitive actions. Parse with a no-tools
   model, emit typed fields, validate in code. Scrub PII at intake (8.5). Depth → 4.6.
   **Standard** risk; defenses **Established**, image defenses **Emerging**.
8. **Cost and context economy.** Native PDF pays for text and page image. Classify first, send
   only pages needing vision (per-page tier routing, **Emerging**), cache by content hash and
   count tokens (**Standard**). Dumping headers, legal boilerplate and irrelevant pages also
   degrades attention (Liu et al., arXiv:2307.03172; Anthropic, "Effective context engineering
   for AI agents," 2025-09-29). Never freeze per-page numbers. Depth → 8.4, 1.5.
9. **The failure-return contract.** Unparseable, encrypted, truncated or oversized files return
   a structured result (`status`, `reason`, `pages_ok`), never a raw exception or silent empty
   listing; partial success is flagged. Deterministic file failures **Standard**; partial-page
   VLM failure handling **Established**. Retry and degradation → 7.1.

## Mention-and-link

Prompt injection and the trifecta 4.6; guardrails 4.4; human review 4.3; evaluation 4.2;
extraction 2.2; chunking and retrieval 5.2; state 5.1; cost 8.4, 8.2; PII 8.5; sandboxing 9.4;
LLM routing 3.2; output 6.2; audio 6.4.

## Out of scope

Parser install and tuning guides; training OCR models; web scraping and browser agents (9.5);
retrieval quality (5.2); email and API-feed transport.

## Maturity summary

Lens line: **Maturity: Established · Who decides: your code (format routing, parse boundaries,
schema invariants, failure handling; the model fills a slot) · Grounding: companion repo and
research · Last reviewed: 2026-11.**
Standard: content routing, deterministic readers, treating files as untrusted. Established:
layout pipelines, native vision PDF input, typed intermediate form. Emerging: VLM-as-parser at
scale, per-page tier routing, VLM box grounding. Contested: "vision makes parsers obsolete"
and any single best-parser ranking.

## Aliases (author signs off)

Document parsing; document AI / layout analysis; Intelligent Document Processing (IDP);
document intelligence; multimodal ingestion (stub); ETL / extraction (stub). Gulli and
Nawalgaria "perception" wording unverified against the book; do not quote. Not an alias: "RAG
ingestion" (upstream half of 5.2).

## Reader-verifiable anchors

- Run the `docling` CLI on a multi-column PDF and open the emitted `DoclingDocument` JSON
  (`texts`, `tables`, `pictures`, furniture, bounding-box provenance).
- Anthropic's and OpenAI's PDF docs state each page yields extracted text plus a page image;
  Claude Code's `Read` requires a page range on long PDFs (confirm locally before quoting).

## Incidents

- Hidden prompts in arXiv preprints aimed at AI peer review (Nikkei Asia, 2025-07-01; Lin,
  arXiv:2507.06185 counts 18 papers): white or microscopic text. Caught by visible-text checks
  and no-tools parsing.
- EchoLeak, CVE-2025-32711 (Aim Security, June 2025): zero-click injection via crafted email in
  Microsoft 365 Copilot, fixed server-side. Lesson: untrusted-data boundaries, privilege
  isolation. Secondary sources only; open the MSRC advisory before quoting.

## Named-idea candidates

**Parse, then extract** (typed form between the stages). **Provenance anchors** (ordinary rule
otherwise).

## Sources (opened unless flagged)

Anthropic PDF support; OpenAI PDF guide; Gemini document processing,
aistudio.google.com/docs/document-processing (the ai.google.dev URL redirects here). Docling,
arXiv:2408.09869. Unstructured and LlamaParse docs. OmniDocBench arXiv:2412.07626; olmOCR
arXiv:2502.18443; OHRBench (J. Zhang et al.) arXiv:2412.02592; ParseBench (B. Zhang et al.)
arXiv:2604.08538. OWASP LLM01 (pin the 2025 versioned URL); OWASP File Upload cheat sheet.
Trail of Bits image scaling post.

> **Verify before quoting:** every page, size, token limit and tier name (vendors revise them);
> Unstructured coordinates and `text_as_html` flags per strategy; OWASP wording; EchoLeak
> primary; Gulli wording.

## Open questions for the author

1. Does untrusted-input security earn a `Security & trust` section from the controlled menu?
2. How deep on Office and HTML files, given they are barely evidenced here?
3. Confirm Grounding: companion repo + research.
4. Sign off aliases and "Parse, then extract" as a named idea.

## Map review (Stage 1.5)

Reviewer: an independent second engine. Verified against primary pages and repo files.

1. Thesis and budget missing: accepted (added; thesis adapted).
2. Lens line and grounding: accepted (set to companion repo + research).
3. Must-cover bloat (12 items): accepted (merged to 9; chunking demoted to a pointer).
4. Context economy, non-PDF formats, links: accepted (Gemini doc confirms Office support).
5. File-parser hazards: accepted (OWASP File Upload page confirms size, filename, sandbox).
6. Incidents "none found": accepted-modified (Nikkei and EchoLeak added; EchoLeak secondary only).
7. Maturity contradictions: accepted-modified (split per sub-claim; kept chapter Established).
8a. Gemini URL: rejected (ai.google.dev 301-redirects to the cited aistudio URL).
8b. Gemini renders pages as images: accepted (2 MP; confirmed on page).
8c. Anthropic MIME rule as lead: accepted (rule rests on determinism).
8d. Trail of Bits scope: accepted (verified product list and mitigations).
8e. Frozen limits: accepted (moved to Verify before quoting; Gemini limits verified, not quoted).
8f. ParseBench affiliation and Zhang collision: accepted-modified (authors include Suo; affiliation not on abstract page, so LlamaIndex stays "directional"; J. and B. Zhang split).
8g. Unstructured flags and OWASP slug: accepted-modified (left in Verify; not re-opened).
9. Anchors are API docs: accepted-modified (Docling CLI added; Claude Code `Read` unverified here).
10. Carrier contradiction: accepted (25-50 per carrier bible; dimension diagram; carrier declared).
11. Sweep disclosure and Open questions: accepted.
12. Aliases: accepted-modified (IDP, document intelligence added; Gulli wording left unquoted).
13. Named ideas: accepted ("Sniff, don't trust" struck).
14. Spelling: accepted (`catalogue` removed with the cost item rewrite).

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis as folded. Verdict: Established, Last reviewed 2026-11. Grounding: companion repo + research. (Author checklist.)
2. Code: yes, small. Add a new package `listing-studio/ingestion/` that holds:
   - stdlib parsers for CSV and simple HTML from a merchant supplier feed, producing a typed pydantic intermediate document with a source anchor on every field;
   - a page router that flags pages needing vision; vision itself is a scripted fake;
   - a test that injected instructions inside a feed field stay data.
   Tests use only stdlib and pydantic; no Office libraries.
3. Office and HTML depth: one paragraph, no deeper.
4. Security: a short "Security & trust" section is warranted. It covers untrusted bytes, gives one paragraph to indirect injection and refers to 4.2 in plain text. EchoLeak is quoted only if the MSRC advisory is opened; otherwise it is cut. (Author checklist.)
5. "Parse, then extract" appears as plain wording, not bolded as a named idea. Aliases are used only where sourced. (Author checklist.)
6. Strict carrier scope: supplier feeds, spec sheets and product photos only.
7. No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

Second-engine review of the draft. Each finding was checked against the chapter, the code or the source before acting.

Code and prose contradictions
- Hook names a wrong row, PDF anchors were page-level: fixed. `Page` now carries tables, `ingest_pages` emits one field per cell anchored `page 1, table 1, row 2, col capacity_lbs`, and the prose pays off the 250-pound row. SVG updated to match.
- `ingest_pages` flattened tables against the "keep a table as rows and cells" claim: fixed in code (cell-level elements); tests added; pytest passes.
- `ingest()` failed the hero PDF with no handoff: fixed. `ingest` takes a `pdf` reader and hands the file to it; with none it returns `failed`, "no pdf reader configured". The prose says which happens.
- No PDF-to-Page step: fixed. `Page` is shown, and the prose names the PDF library or layout parser that produces it.
- `has_diagram` unexplained: fixed (set upstream when the parser finds a figure; comment and prose).
- No per-element path field: fixed. `Element.read_by` ("code" or "vision") added and explained.
- The `25-50` example never paid off: fixed. The diagram yields the same value, giving two anchors for one value and a cross-check.
- `row 3, col sku` comment did not match the column: fixed (`supplier_sku`).
- Docstring and prose repeated the failure contract: fixed (docstring shortened, the "failure-return contract" coinage dropped).
- Second-engine 2, "never an exception" contradicted (an overflow row raised AttributeError; vision errors escaped; empty pages and empty vision answers returned ok): fixed in code with regression tests.
- Second-engine 4, CSV silently lost data (duplicate headers, missing cells, `.strip()`): fixed; duplicate headers and wrong cell counts now fail, and values are kept raw.
- Second-engine 5, HTML reader split nested markup and claimed "visible" cells: fixed (cell text accumulated to `</td>`; the prose says it evaluates no CSS).
- Second-engine 3, the intermediate form could not hold evidence: fixed for tables and reader identity. Vision values stay page-anchored, and the prose names bounding boxes as the Emerging step that would narrow them.

Carrier and confidentiality
- Carrier fit: fixed. Trigger lists use supplier feeds, spec sheets and photos; the PII example is a supplier sales contact in a spec-sheet footer.
- Second-engine 14, extraction placed "in a later step" against the carrier bible: fixed (the draft `Listing` is extracted before step 1 ends).

Prose
- Apparatus "the anti-pattern this chapter feeds the catalog": fixed (cut).
- Restated core claim ("The fix, in miniature"): fixed (cut). Second drop-or-invent sentence in the invariants paragraph: fixed (cut).
- olmOCR cited for a ranking claim it does not make: fixed (cut, footnote removed).
- Emerging verdict uncited and missing from the meta line: softened ("reasoned from those features rather than shown by a benchmark") and added to the meta line.
- Second-engine 9, verdicts not re-derivable: softened as above; Established kept for the boundary, which the OWASP, vendor and Docling sources support.
- Unlinked 4.6 in the body: fixed (linked). 9.4, 8.4, 8.5 and 7.1 are planned chapters, left as plain text by convention.
- Missing blank line before Security & trust: fixed.
- Closer near an aphorism: rejected. It states the litmus verdict, and the earlier restatement it competed with is gone.
- "the one where" implying the only such step: softened ("one where").
- "consistently lowered": softened (see OHRBench below).
- "a re-sent catalog costs nothing": fixed ("costs no model calls").
- Cold-reader terms: fixed by glossing anchor, typed document, text layer, magic bytes, ETL, front controller, `Listing`, layout pipeline, bounding box and grounding, GTIN, invariants, furniture, zip bomb, external entities, Listing Studio, the page router and `MAX_BYTES`. Alt text cut from about 230 words to about 65, so screen readers get a summary.
- Second-engine 6, routing on text length alone: softened (a production router also checks reading order and may try plain OCR first).
- Second-engine 7, thesis overreach: partly fixed. The native-PDF paragraph now says each vendor sends extracted page text alongside the page image; the thesis gloss and Gotcha 1 are kept, since they concern the raw file as the first reader, not native PDF input as such.
- Second-engine 10, sniffing presented too confidently: fixed ("routing hints; they do not prove a file is safe"; a zip signature fits any zip).
- Second-engine 12, aliases not sourced: rejected for this stage. Aliases are the author's call and are listed in the PR checklist.
- Second-engine 15, too much code: rejected. The cold reader's build test asked for more of it (`Page`, `MAX_BYTES`), and code does not count against the word budget.

Security
- Second-engine 1, injection guarantee false: fixed. The section now says no-tools parsing limits what ingestion can do, but the text flows on to extraction and copywriting, so later prompts must quote it as data. The CSV test is described as proving only that the parser is inert.

Citations
- OHRBench "consistently": softened to "tended to fall".
- OWASP LLM01 "open problem": fixed to "an area for further research".
- Docling bounding boxes: fixed to "where available".
- Unstructured URL: fixed to the partitioning page (verified 2026-11-28: strategies `auto`, `fast`, `hi_res`, `ocr_only`; `hi_res` extracts PDF tables and struggles with multi-column order).
- Nikkei Asia date: cut (not verifiable from a fetch).
- OWASP XXE cheat sheet: verified (title; "disable external entity resolution").
- Second-engine 11, Docling CLI: fixed to `docling convert` with `--to json` (verified; the default output is Markdown).
- Second-engine 8, billing generalized: fixed. Anthropic bills text tokens plus image tokens per page (verified); Gemini charges nothing extra for extracted text (verified).
- Second-engine 13: fixed. Lost in the Middle is cited as TACL 12:157-173 (2024) with the 2023 preprint; the Gemini page title is "Document understanding".
- Remaining sources: verified as cited by the fact-check; no change.

Index by report (every numbered finding maps to a line above)
- Prose critic 1-15: hook (1), tables (2), apparatus (3), `has_diagram` (4), PDF front door (5), restatement (6), `sku` comment (7), invoices (8), maturity (9), olmOCR (10), overclaims (11, three lines), docstrings (12), unlinked cross-references (13), blank line (14), closer (15).
- Fact checker 1-24: OHRBench (1), LLM01 (15), XXE (3, now verified), Unstructured (9), olmOCR (12, cut), Lost in the Middle (16, venue year corrected to TACL 2024), uncited Emerging (18, softened), exceptions (20, fixed with second-engine 2), cross-references (22, 4.6 linked, planned ones plain), undefined terms (23, glossed: GTIN, XXE as external entities, IDP left in the alias line, layout pipeline names Docling, `hi_res` and LlamaParse), maturity split (24, adopted). Items 2, 4-8, 10, 11, 13, 14, 17, 19 verified; 21 (model IDs) a known false positive.
- Cold reader, terms: all glossed as listed above; "static dispatch" now sits beside the glossed front controller; `parse_html` described in prose, not shown.
- Cold reader, missing steps: hidden-text step (softened, carried by the Security section); `25-50` payoff (fixed); "drop or invent a cell" (supported in Gotchas, restatement cut); verdict mix (softened); string `value` (fixed: "Extraction decides... ingestion keeps the string"); `%PDF` path (fixed, `pdf` handoff); `MAX_BYTES` (value stated in prose); vision JSON and path field (fixed: `read_by`, labelled values validated by code); typed vision call returns `field` elements (fixed); furniture (glossed).
- Cold reader, build test: `Page` shown, `MAX_BYTES` stated; PDF-to-Page named but not implemented; real vision call and Office conversion left out by the code-scope ruling (rejected: out of scope for a small example).
- Cold reader, alt text: shortened; blank line: fixed; dense vendor paragraph: merged into one sentence.
