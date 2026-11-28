# Coverage map: Retrieval (RAG) (chapter 5.2)

> Research-derived spec for what the chapter must cover so a reader can build, evaluate and
> debug retrieval for an agent, and where to stop. Angles run: vendor/primary docs (Anthropic
> only so far, see Open questions), academic, security/failure modes, skeptical read, alias
> sweep, daily-tool, everyday-engineer. Skipped: practitioner writeups (Angle 4, not run; the
> failure-point paper stands in), incident postmortems beyond the two disclosures under
> Incidents. No production grounding: nothing here is a first-hand claim.
> Bar: definitive but tight, not exhaustive.

## Thesis and budget

**Thesis:** Most RAG failures are search failures, not generation failures: whether your code
retrieves up front or the model searches through a tool, answer quality and tenant safety are
bounded by what the search returns, so build, measure and secure the search first.
**Budget:** standard pattern, about 2,000 to 2,800 words.

## Mental model

Retrieval is a search system you build and own; the model is one consumer of its output. Classic
RAG is a fixed lookup-then-generate pipeline your code runs on every query (not agentic).
Agentic retrieval hands the same search to the model as a tool. Who decides: your code (classic
pipeline) or the model (when to search and what to ask, via tool use, 2.1), while your code still
owns ranking, access control, context caps and loop limits (2.5, 2.6). Retrieved text is
untrusted input that competes for the window.

## Must-cover (ranked)

`[+]` = the current stub is empty, so every item is new.

1. **Classic RAG: the pipeline and why it exists** `[+]` - embed the query, fetch top-k chunks,
   put them in the prompt, generate. Grounds the model in data it was not trained on and can
   cite. *Skip it:* nothing else can be placed. **Standard.** (Lewis et al., arXiv:2005.11401.)
2. **Agentic retrieval (agentic RAG): retrieval as a tool** `[+]` - the model issues its own
   queries, reads results, re-queries or stops. Pipeline = code decides; tool = model decides.
   Costs in tokens and in degraded attention: latency, extra loops, context spent on dead-end
   searches, termination rules (2.5). *Skip it:* the reader thinks RAG and agents are separate
   worlds. **Established** for search wrapped as a tool; **Emerging** for autonomous multi-step
   query planning and RL-trained search. (Anthropic, "Building Effective Agents", 2024-12-19;
   ReAct arXiv:2210.03629; Search-R1 arXiv:2503.09516; survey arXiv:2501.09136.)
3. **Chunking, with contextual retrieval as one option** `[+]` - size, boundaries and overlap
   change recall; chunks lose context when cut from their document. Contextual retrieval
   prepends a short model-written note to each chunk before indexing; prompt caching amortizes
   the cost. Vendor-reported gains only, one benchmark, not replicated here. Parsing is 6.1.
   *Skip it:* good documents, bad hits. **Established** (chunking craft; source gap, see Open
   questions); **Emerging** (contextual retrieval). (Anthropic, 2024-09-19.)
4. **Hybrid search: lexical plus dense, fused** `[+]` - BM25 catches exact tokens (SKUs, error
   codes) that embeddings blur; dense catches paraphrase; fuse by rank. *Skip it:* exact-match
   queries fail silently. **Established.** (BEIR arXiv:2104.08663; reciprocal rank fusion, Cormack
   et al. SIGIR 2009, not opened, verify.)
5. **Reranking** `[+]` - retrieve wide, rerank with a cross-encoder or model, keep a few. *Skip
   it:* the right chunk is retrieved but ranked out of the window. **Established.** (Anthropic
   contextual retrieval; BEIR.)
6. **Query formulation and pre-filtering** `[+]` - conversational follow-ups fail raw embedding
   unless rewritten; filter by tenant, category or ACL before ranking, because post-filtering top-k
   can return nothing. *Skip it:* "what about the red one?" retrieves noise. **Established**
   (rewriting, Ma et al., arXiv:2305.14283, EMNLP 2023); filtering is **Standard** practice
   (OWASP LLM08:2025).
7. **Long context versus RAG** `[+]` - Anthropic's advice: a small static corpus can go in the
   prompt with caching. Li et al.: long context beats RAG on average given resources, RAG is far
   cheaper, and routing between them keeps most accuracy (routing is 3.2). Long windows degrade
   by position (arXiv:2307.03172; depth is 1.5). Cost economics: 8.4. *Skip it:* teams build an
   index they did not need. **Contested.** (arXiv:2407.16833.)
8. **Evaluate retrieval separately from generation** `[+]` - labeled queries and recall@k or rank
   metrics first; faithfulness and answer quality second. Different faults need different fixes.
   *Skip it:* you tune the prompt for a search bug. **Standard** (offline IR metrics, BEIR);
   **Emerging** (LLM-judged RAG metrics, RAGAS arXiv:2309.15217). Judge mechanics: 4.2.
9. **Failure modes, provenance and index lifecycle** `[+]` - Barnett et al.'s seven failure points
   (arXiv:2401.05856; PDF read): missing content, missed top-ranked documents, not in
   context (consolidation limits), not extracted, wrong format, incorrect specificity, incomplete.
   Separately, and not from that paper: stale or contradictory sources, over-retrieval diluting the
   window, fabricated or misattributed citations even with the right passage in context (Gao et
   al., ALCE, arXiv:2305.14627, EMNLP 2023), and index staleness, deleted-document and ACL sync,
   embedding-model lock-in (ingestion is 6.1; groundedness checks 4.4). Failure-return contract:
   an empty or low-confidence result comes back as structured "found nothing relevant", not an
   empty string. **Established** (the contract, the taxonomy as a checklist).
10. **Retrieval is an attack and leak surface** `[+]` - poisoned documents steer answers
    (PoisonedRAG, about 90% success with five injected texts per question on its test setup);
    multi-tenant stores leak across users unless access control sits in the retrieval layer.
    Injection depth: 4.6; identity and PII: 8.5. *Skip it:* one merchant's helpdesk retrieves
    another merchant's private policy docs. **Standard** (ACL and tenant pre-filtering);
    **Contested** (poisoning and injection defenses). (OWASP LLM08:2025; arXiv:2402.07867.)

## Mention-and-link

- Context budget, "inject the minimal subset" → 1.5. Run state versus facts → 5.1; write
  policy, forgetting, memory retrieval → 5.3 (semantic knowledge base is this chapter's).
- Parsing, cleaning, freshness pipelines → 6.1. Injection → 4.6; judges → 4.2; groundedness → 4.4.
- RAG versus fine-tuning → 8.3. Tool retrieval for huge catalogs → 2.1. Compaction → 5.4.
- Loop limits and harness → 2.5, 2.6; routing → 3.2; cost → 8.4; locks, PII, identity → 8.5.
- GraphRAG: one line; targets corpus-wide questions; **Emerging** (Edge et al., arXiv:2404.16130).

## Out of scope

Vector database selection and HNSW tuning; embedding leaderboards (link MTEB, do not freeze
scores); fine-tuning retrievers (8.3); Self-RAG and RL-trained retrieval as methods (cite only:
arXiv:2310.11511, 2503.09516).

## Maturity summary

- **Standard:** the classic pipeline; offline IR metrics; ACL and tenant pre-filtering.
- **Established:** hybrid search, reranking, chunking craft, query rewriting, retrieval as a tool,
  the failure checklist.
- **Emerging:** contextual retrieval, LLM-judged RAG metrics, autonomous multi-step search,
  RL-trained search, GraphRAG.
- **Contested:** long context versus RAG; poisoning defenses; "RAG is dead / solved".
- **Chapter verdict:** split. **Standard** for classic retrieval-augmented grounding over corpora
  too large or costly for the window; **Established** for agentic retrieval. Fast-moving: carry
  "Last reviewed". The stub's single Standard needs updating.

## Aliases (feeds `*Also called:*`; needs author sign-off)

retrieval-augmented generation, RAG, knowledge-base retrieval, grounding (broader vendor term),
semantic search / vector search (a subset, often misused as a synonym; inherited from the stub),
"agentic RAG" (survey arXiv:2501.09136; used for the retrieval-as-tool variant), just-in-time
retrieval / agentic search (Anthropic, 2025-09-29). Candidate, unverified: "file search"
(vendor APIs).

## Reader-verifiable anchors

- Claude Code loads CLAUDE.md up front and explores with glob and grep on demand, not a
  pre-built embedding index; the same post says runtime exploration is slower than pre-computed
  retrieval, the honest cost of the agentic variant (Anthropic, 2025-09-29).
- Indexed counterpart: a vendor `file_search` or an IDE codebase index; pick one and open its
  docs at draft time (not opened here).

## Incidents

Two public disclosures, both indirect injection through retrieved text. Slack AI (PromptArmor,
August 2024): a poisoned public-channel message retrieved alongside a private secret made the
assistant emit a link carrying the secret; the citation named only the private channel. Microsoft
365 Copilot "EchoLeak", CVE-2025-32711 (Reddy and Gujral, arXiv:2509.10540, 2025-09-06): a crafted
email caused zero-click exfiltration. Controls: trust-boundary separation, ACL and provenance
scoping at retrieval (4.6 owns the mechanism).

## Carrier and code seam

- Carrier: **merchant helpdesk** (retrieval over policy and how-to docs) is home; the shopper
  assistant over the catalog is the second case (exact SKU versus paraphrase makes hybrid
  concrete). Listing Studio itself is not a retrieval surface.
- Code: needed. `listing-studio/` has no retrieval package; `helpdesk_mcp/docs_server.py` holds
  a fake in-memory corpus only. New small offline package, `listing-studio/retrieval/`: toy
  lexical and dense scorers, rank fusion, retrieval exposed as a tool with a structured empty
  result, recall@k over labeled queries. No network, no vector DB. Three provider tabs
  (LangGraph default, OpenAI Responses, Anthropic Messages) wrap the same tool.

## Quotable-line candidates (author accepts or strikes)

"Retrieval is a search system with a model attached." "Measure the search before the answer."
No named idea earned.

## Open questions for the author

1. Chapter verdict: split Standard / Established (proposed), or Established throughout?
2. Does semantic-as-knowledge-base stay here, with episodic memory in 5.3?
3. Provider-tab scope for `retrieval/`: all three, or LangGraph plus one?
4. Vendor primary docs (OpenAI, Google, Anthropic Citations, LangChain, LlamaIndex) are not yet
   opened; run that pass at draft time?
5. Chunking needs a source beyond one vendor post; accept a thinner Established claim?

## Sources

Lewis et al. arXiv:2005.11401 (2020-05-22, NeurIPS 2020); ReAct, Yao et al. arXiv:2210.03629
(2022-10-06, ICLR 2023); Lost in the Middle, Liu et al. arXiv:2307.03172 (2023-07-06, TACL); Self-RAG
arXiv:2310.11511; RAGAS arXiv:2309.15217; BEIR arXiv:2104.08663; Barnett et al. arXiv:2401.05856
(2024-01-11); PoisonedRAG arXiv:2402.07867; GraphRAG arXiv:2404.16130; Li et al. arXiv:2407.16833
(EMNLP 2024 industry); Singh et al. arXiv:2501.09136 (2025-01-15); Search-R1 arXiv:2503.09516;
Ma et al. arXiv:2305.14283 (2023-05-23, EMNLP 2023); Gao et al. arXiv:2305.14627 (2023-05-24,
EMNLP 2023); Reddy and Gujral arXiv:2509.10540. Anthropic: "Introducing Contextual Retrieval"
(2024-09-19); "Building Effective Agents" (2024-12-19); "Effective context engineering for AI
agents" (2025-09-29). PromptArmor, Slack AI disclosure (August 2024). OWASP LLM08:2025. Cormack et
al. RRF (SIGIR 2009): not opened.

> **Verify before quoting:** vendor percentages are the vendor's own; PoisonedRAG's 90% is its
> test setup only; context-window figures rot.

## Map review (Stage 1.5)

Reviewer: Gemini, as an independent second engine. Verified against primary pages where noted.

1. Thesis and budget missing: accepted-modified, added a thesis in the reviewer's spirit, budget row added.
2. Barnett and RRF unread, #9 misattributed: accepted-modified, Barnett PDF read and seven points listed exactly, other failures split out; RRF still unopened (403), flagged.
3. Standard verdict contradicts evidence: accepted-modified, split verdict adopted, author to confirm.
4. False "None found" on incidents: accepted, Slack AI page and EchoLeak paper (arXiv:2509.10540) opened and confirmed.
5. Missing query rewriting, citations, index lifecycle: accepted, Ma and ALCE verified (arXiv pages), folded into #6 and #9.
6. Contextual retrieval bloat, single-vendor bias: accepted-modified, folded into #3; vendor docs not opened, parked as open question 4.
7. "Front controller" misuse, missing Who decides: accepted, both fixed.
8. Missing neighbour seams: accepted, 2.5, 2.6, 3.2, 8.4, 8.5 added (plain text, no links).
9. Sub-verdicts misaligned: accepted-modified, #2, #8, #10 split; chunking source gap logged, not invented.
10. Aliases: accepted-modified, fabricated quote removed, subset caveat added; book chapter titles rejected as not aliases; other synonyms unverified, only "file search" kept as candidate.
11. Angle 4 dropped, no open questions: accepted, Angle 4 recorded as skipped, questions added.
12. Venues, URLs, Contextual BM25: accepted-modified, venues added where verified or well known; "Contextual BM25" dropped with the figures (item 13).
13. Frozen pricing and thresholds: accepted, dollar figure, percentages and 200k removed.
14. Anchors duplicated: accepted-modified, merged; indexed anchor left to draft time, unopened.
15. Named-idea slogans: accepted, moved to quotable lines.
16. Carrier phrasing, provider tabs, hygiene: accepted, leak recast, no-production note and three tabs added, stray phrases deleted.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis as folded. The verdict is split, as the map proposes:
   - Standard for grounding over corpora too large for the window.
   - Established for search wrapped as a tool.
   - Emerging for autonomous multi-step retrieval planning.
   - Contested for long context versus RAG.

   The top line names the chapter verdict as Standard; the prose argues the split. Author checklist.
2. Scope: semantic knowledge bases stay in 5.2. Episodic and user memory belong to 5.3 Real Memory, referenced in plain text.
3. Code: a new package `listing-studio/retrieval/`, as the map specifies. It holds:
   - toy lexical and dense scorers;
   - RRF fusion;
   - a retrieval tool that returns a structured empty result;
   - recall@k over a labeled fixture.

   Provider tabs (LangGraph, OpenAI Responses, Anthropic Messages) show retrieval-as-tool wiring only. They are illustration files, compile-checked. Tests use stdlib and pydantic only.
4. Citations: RRF (Cormack et al., SIGIR 2009) is cited only if the paper is opened before ship; otherwise RRF is described without a citation. Any chunking advice needs a second non-vendor source or is softened to "a common starting point". The vendor-docs pass is done by the fact-checker.
5. Security: the tenant-isolation and indirect-injection paragraph stays, citing the Slack AI and EchoLeak sources. The full treatment is deferred to 4.6 Prompt Injection & the Lethal Trifecta.
6. No From-production callout and no coinage. Shipped chapters are not edited.

## Reconcile log (Stage 5)

Prose critic:
1. "Most retrieval bugs" uncited quantifier: fixed, sentence cut; "rarely flags" softened to "often does not flag".
2. Hook's "eight labelled queries" outran the evaluation: fixed, now "a small labelled test set with one error-code query"; "a few dozen" kept in In short.
3. Closing aphorism in In short: fixed, cut.
4. Tenant pre-filter stated four times (five, counting Security): fixed. Kept the mechanism (Query and filter) and the session source (scale-up); Security reduced to the leak, one Standard verdict with the OWASP cite and the 8.5 link; the separate Standard sentence cut.
5. Vendor caveat in the chunking body: fixed, caveat left to the footnote.
6. Toy caveats under Evaluating it: fixed, folded to one clause.
7. "The question is open": fixed, replaced with "measure both on your own queries before you route".
8. Prompt-for-search-bug gotcha restated the thesis: fixed, cut.
9. Carrier naming drift: fixed, "the merchant helpdesk assistant" at first use.
10. Two tool names: fixed, one name, `search_docs`, in code, tabs and walkthrough.
11. "fits comfortably": fixed, "comfortably" cut; the size threshold was not added, because map review item 13 removed frozen thresholds.
12. Established verdict restated the paragraph above: fixed, reduced to "for the two reasons above".
13. Signposting lead-in to the Claude Code anchor: fixed.
14. "ranked eleventh" assumed k=10: fixed, "ranked just below the cutoff".
15. GraphRAG in the neighbours paragraph: fixed, moved to the maturity paragraph.
16. "The model decides nothing about the search": fixed, cut.

Fact checker:
1. Survey footnote claimed the paper gives the term: fixed, footnote reworded as a survey and taxonomy.
2. OWASP "cross-tenant" and "weak access partitioning": fixed, "multi-tenant" in body and footnote; the duplicate OWASP sentence in Query and filter cut.
3. CAIN 2024 and TACL 2024 years: TACL 2024 confirmed on the ACL Anthology (volume 12); CAIN 2024 could not be confirmed from an opened page, so it was dropped from the Barnett footnote.
4. Contextual-retrieval figures not quoted: no change needed.
5. Search-R1 date: no change needed.
6. "established fix" for rewriting: softened to "a common fix". "Standard practice" for pre-filtering now carries the OWASP cite.
7. Cross-encoder undefined: fixed, glossed.

Cold reader:
- tenant, top k, BM25, cosine, cross-encoder, pre-filter and post-filter: fixed, each glossed at first use.
- RRF k=60: fixed, defined as a smoothing constant distinct from the top-k cutoff, cited to Cormack et al. (SIGIR 2009, paper opened; k=60 fixed in a pilot).
- recall@1 against a code default of 3: fixed. Figures now quoted at the default k=3 (the fixture gives 5/8, 7/8, 8/8 at both k=1 and k=3) and the test asserts at the default.
- Build test (`Chunk`, `CORPUS`, `CONCEPTS`, `tokens`, `LABELED_QUERIES` never shown; repo link without URL): fixed. The scorer listing now includes `CONCEPTS` and `tokens`; `Chunk`, `CORPUS` and `LABELED_QUERIES` are glossed; the repo callout links the package.
- Toy dense "returns nothing" against the opening's real neighbours: fixed, step 2 says a real embedding returns the wrong pages instead.
- "lands near the top" not shown: fixed, scoped to this fixture.
- Two tool names: fixed (see prose critic 10).
- Anthropic tab reading `content[0].text`: fixed, joins the text blocks.
- LangGraph tab without imports: rejected, imports live in the linked companion file, as in other chapters' tabs.
- No real embedding model called: rejected, the toy is deliberate (map ruling 3).
- Lightly glossed terms (augmented LLM, just-in-time retrieval, LLM-judged, LLM08, Self-Route): rejected for this pass; each is glossed in context or by its footnote, and the 2,800-word ceiling leaves no room. "Listing Studio" appears only in the repo path, which needs no gloss.
- Scorer listing used `Counter`, `math` and `re` without imports: fixed, the listing now starts at the imports.

Second-engine draft review (OpenAI Codex):
1. Provider tabs drop response items, handle one tool call, assume text first: fixed. Both raw-SDK tabs keep every output item, return one result per call, loop under a cap and stop on a direct answer, following the 2.1 idiom. Mocked protocol tests rejected: the tests may not import provider SDKs; the prose now says the tabs are compile-checked only.
2. Unsupported prevalence claim: fixed (prose critic 1).
3. Low relevance confused with no result: fixed. "Zero means no match" scoped to the toy; `found=True` described as candidates, with the password-policy-for-Canada case, now a test.
4. Tenant filter and provenance not in code: softened. The prose says the companion corpus is single-tenant and does not implement the filter; building it is out of this chapter's code scope.
5. Conflicting sources: rejected, not in must-cover; index lifecycle belongs to 6.1.
6. Evaluation excludes end-to-end failures: fixed, one sentence adds unanswerable and no-search cases.
7. RRF uncited, rescue overgeneralized: fixed (cold reader, RRF).
8. Ma does not establish conversational rewriting: softened to "a common fix"; no new citation added.
9. Standard verdict for the composite: rejected, kept Standard per ruling 1; the fact-checker found the split verdict holds. Listed for the author.
10. Trace implies a model run: fixed, labelled illustrative, with the test boundary stated.
11. "No grip", "blind to paraphrase": softened to "often has little grip" and "tends to miss paraphrase".
12. Seam destinations and code-block count: 4.2 corrected to 4.6 in ruling 5; caps stay linked to 2.5 and 2.6; block count rejected, the listings are the argument.
13. Aliases and the indexed anchor: aliases unchanged pending author sign-off; the review-log wording in item 10 corrected. The indexed-anchor item is closed without a vendor anchor: the chapter's reader-verifiable anchor is Claude Code's grep-and-glob search, and adding the OpenAI file-search page would not fit the budget.

Also: the access-control phrase dropped from one of In short's two mentions; walkthrough step 2 hedged ("would likely return").
