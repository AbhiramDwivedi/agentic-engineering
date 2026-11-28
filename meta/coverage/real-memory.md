# Coverage map: Memory (chapter 5.3)

> Research-derived spec. Angles run: vendor docs, academic and benchmarks, security and failure
> modes, skeptical read, alias sweep, daily-tool, everyday-engineer. Angles skipped: practitioner
> production postmortems (none found). Bar: definitive but tight. Budget: Standard pattern,
> ~2,000-2,800 words of chapter prose.

## Thesis

When the model writes memory, an unreliable author becomes the durable writer of its own future
context, so a memory layer needs write provenance, staleness checks and expiry, or it degrades
accuracy, turns one injected document into a persistent compromise, and loses to plain state plus search.

## The mental model

Memory is what a future run reads so it behaves differently; here the model helps decide what is
written, found again and dropped. 5.1 owns the half where code writes by schema; 5.3 owns the
half where the model chooses. Real memory needs three things state does not: a write policy,
retrieval, and forgetting, plus a path for the user to see and delete it. Most products that say
"memory" do not need it.

## Must-cover

Ranked. `[+]` = new for this chapter.

1. **The seam with 5.1: who writes, who reads** `[+]` - memory is the cell where a future run
   reads and the model chooses what to keep. Code-written memory (a fixed rule saving the garage
   size, a coded Store write, ADK session `user:` state) is ordinary engineering; say so and link
   5.1. Do not re-teach reducers or checkpointers. **Standard** (the distinction, via 5.1).
2. **Types: semantic, episodic, procedural** `[+]` - facts, past experiences as worked
   examples, rules that change behavior. CoALA names working memory plus long-term episodic,
   semantic and procedural (Sumers, Yao, Narasimhan, Griffiths, arXiv:2309.02427, TMLR 2024);
   LangGraph and LangMem document the same three. Procedural memory as code: Voyager skill
   library (arXiv:2305.16291); as verbal lessons: Reflexion (arXiv:2303.11366). Say which are
   model-decided. **Established** (vocabulary), **Emerging** (engineering).
3. **Write, retrieve, forget** `[+]` - write policy (hot path versus background after the
   conversation; MemGPT's model-paged context, arXiv:2310.08560, and sleep-time compute,
   arXiv:2504.13171, as lead citations), retrieval (Park et al., arXiv:2304.03442: a weighted
   combination of recency, importance, relevance, each rescaled 0-1), forgetting (decay,
   supersede, delete). "Memory without decay becomes noise" is a claim to cite, not assert.
   **Emerging.**
4. **Shipped shapes, compared** `[+]` - one short comparison, no feature matrix, developer
   surfaces first: Anthropic memory tool (`memory_20250818`, client-side file commands over a
   `/memories` directory your handler backs; the model decides, your code owns storage, caps,
   expiry, path validation); LangGraph Store with LangMem (namespaced JSON, manager and
   search tools); Letta self-edited memory blocks; Google ADK `MemoryService` versus session
   `user:` state and OpenAI Responses/Conversations (thread state only, you wire an external
   store); both flagged to open before drafting. Separate consumer products: ChatGPT saved
   memories, Claude Code auto memory. Pairs with compaction (5.4). **Emerging** (practice),
   **Contested** (which design wins).
5. **The handler contract** `[+]` - what the model sees when a write fails: structured,
   recoverable errors (quota exceeded, path rejected, untrusted source blocked, write
   conflict), not a stack trace. Gotchas: editing a pinned block mid-session invalidates the
   prompt-cache prefix (link 8.4); memory versus system-prompt precedence must be stated;
   concurrent writes race (link 8.5). **Emerging.**
6. **Memory poisoning** `[+]` - the security core. Rehberger: ChatGPT fake memories (May 2024);
   Gemini saved-info poisoned through an uploaded document using delayed tool invocation
   (Feb 2025, reported to Google Dec 2024, rated low likelihood and impact by Google): a second
   vendor makes it a class. Research: MINJA (arXiv:2503.03704) writes poison through ordinary
   queries; AgentPoison (arXiv:2407.12784) reports above 80% success at under 0.1% poison
   rate (author-reported). OWASP agentic list ASI06, memory and context poisoning (confirm
   official wording). Mitigations: provenance on every entry, tool and web content never writes
   unreviewed, scoped namespaces, read-only mode, user confirmation of writes, diff review.
   Link 4.6 and 4.3. **Established** threat, **Contested** defenses.
7. **Staleness and the fossilized fact** `[+]` - a stored claim goes stale silently, even a
   stored procedure. Timestamps, source pointers, verify-before-use for checkable facts,
   supersede-not-append, expiry (Anthropic docs advise deleting files not accessed in a long
   time). **Established** (the risk), **Emerging** (automated temporal invalidation).
8. **Privacy and consent** `[+]` - memory-specific only: per-user namespaces, user-visible and
   revocable memory, "deleted" versus "gone" (OpenAI states a 30-day log window), and a model's
   refusal to store sensitive data is not a control (Anthropic advises handler validation). Link
   8.5 and 8.6 for isolation, PII and erasure; no legal advice. **Standard** baseline (isolation
   via 8.5); **Established** concern.
9. **Evaluating memory** `[+]` - LoCoMo (arXiv:2402.17753), LongMemEval
   (arXiv:2410.10813, ICLR 2025: five abilities, 30% accuracy drop reported), MemoryAgentBench
   (arXiv:2507.05257: retrieval, test-time learning, long-range understanding, selective
   forgetting). Vendor claims are author-reported and disputed (Mem0 arXiv:2504.19413; Zep
   arXiv:2501.13956; Letta reports a plain file with grep scoring above Mem0's figure). Honest
   eval is your own: golden recall, stale-fact and update cases, abstention, poison-and-recover,
   ablation against no memory and full history in context. Link 4.2. **Contested** (benchmarks),
   **Established** (own golden and ablation evals).

## Mention-and-link

- State, reducers, checkpointers, `thread_id`: 5.1. Checkpointing: 7.3.
- Retrieval craft, chunking, rerank, hybrid search, GraphRAG: 5.2.
- Compaction, context editing: 5.4. Tool-argument validation: 2.1. Skills as author-written
  procedural memory: 2.3.
- Injection and the lethal trifecta: 4.6. Human review of writes: 4.3. Evals: 4.2.
- Cost and prompt caching: 8.4. Locks, PII, identity: 8.5. Governance: 8.6.
- Self-rewriting systems: 9.7. Long-running agents: 9.1. Tracing reads and writes: 8.1.

## Out of scope

Vector-database selection (5.2); provider SDK handler code beyond the code seam; long-context
architecture research; fine-tuning as memory (8.3); legal analysis.

## Maturity summary

- **Standard:** none for model-written mechanisms; per-user isolation is Standard via 8.5.
- **Established:** the vocabulary; injection and privacy threats; staleness as a risk.
- **Emerging:** write policies, forgetting, background consolidation, procedural memory, the
  memory tool as practice, automated invalidation.
- **Contested:** which architecture wins; vendor benchmark claims; whether most products need memory.

Chapter verdict: **Emerging**. The mechanisms ship and the threats are documented, but benchmarks
are young, vendor claims conflict, and no cited account shows a write policy that holds up.

## Litmus (is it new?)

The model decides what to write, update, forget and retrieve: genuinely agentic. Your code decides
trigger cadence, namespace scope, caps, TTL and provenance checks. Deterministic schema writes are
code-decides (5.1); code-triggered LLM extractors (LangMem background manager, Mem0) are hybrid:
code owns the trigger, the model owns the write decision. Say what model-decided buys (judgment)
and costs (poisoning and drift, items 6 and 7).

## Aliases

- Long-term memory, cross-session memory (LangGraph, OpenAI, Gulli books).
- Episodic / semantic / procedural memory (LangMem, CoALA).
- Memory blocks, core and archival memory, virtual context management (Letta, MemGPT).
- Saved memories (ChatGPT); auto memory (Claude Code); structured note-taking (Anthropic);
  Memory Bank (Google ADK).

## Reader-verifiable anchors

1. Claude Code docs print the table of CLAUDE.md (you write) versus auto memory (Claude writes);
   a reader can open a project's `MEMORY.md`.
2. ChatGPT Settings shows saved memories the user can read and delete; temporary chat avoids them.

## Carrier

Shopper assistant (garage is 200 sq ft, known next visit; see carrier-bible shopper assistant)
for semantic, episodic memory and privacy. Merchant helpdesk for a non-compliance preference
(preferred bullet formatting), not a MAP rule. Repricer for poisoning and staleness (remembered
competitor price, poisoned "approved" note). No "From production:" slot.

## Named-idea candidates (author to accept or strike)

- "Write, find, forget": the three decisions as the spine.
- "Write provenance": every entry carries author (user, model, tool output) and date.
- "Memory is a claim, not a fact": verify before it drives an action. Plain labels, not canon.

## Code seam

Needs code, small. New `listing-studio/memory/` (shopper assistant). Primary listing plain Python,
with tabs: LangGraph Store, OpenAI Responses with an external store, Anthropic `memory_20250818`
handler. Demonstrates per-user namespace, path or key validation, size cap, timestamp and source
per entry, structured write-failure returns, and an offline test that a poisoned write from a
tool result is rejected or flagged. Stub model, no embeddings (5.2).

## Sources (opened this pass unless marked)

Opened: CoALA 2309.02427 (types, TMLR camera-ready); Park et al. 2304.03442 (scoring);
MemoryAgentBench abstract 2507.05257; Rehberger Gemini post (embracethered.com, 2025-02-10).
Opened in the first pass: Anthropic memory tool docs; Claude Code memory docs; OpenAI Memory FAQ;
LangMem and LangChain memory concepts; Letta docs and benchmarking post; Rehberger ChatGPT post
(2024-05-22). Not opened, verify before quoting: OWASP ASI06 page (official URL unresolved),
Rehberger SpAIware (Sept 2024), Letta archival and sleep-time docs, Google ADK and OpenAI
developer memory docs, Zep and Mem0 papers, venues other than CoALA, Claude Code 200-line limit.

## Map review (Stage 1.5)

Reviewer: Gemini (second engine). Dispositions after checking primary sources.

1. Thesis and budget: accepted-modified, added both; thesis shortened.
2. Unopened sources: accepted-modified, opened CoALA, Park, MemoryAgentBench, Gemini post; OWASP page and SpAIware still unopened, header corrected, TODO resolved.
3. Branch citation and production callout: accepted, both removed.
4. Over-budget and vendor tour: accepted, items 4 to 6 merged, map cut to ~1,500 words.
5. Failure-return contract, angle 7: accepted, new item 5.
6. ADK, OpenAI APIs, 2026 essay: accepted-modified, ADK and OpenAI added flagged unopened; Lance Martin Nov 2026 essay and "dreaming" not added, unverifiable.
7. Seam links: accepted, item 8 narrowed, six links added.
8. Maturity verdicts: accepted-modified, item 4 Emerging, item 9 split, Standard line rewritten.
9. Litmus line: accepted, rewritten as code-trigger/model-write hybrid.
10. Gemini disclosure: accepted, verified Feb 2025 post, in item 6.
11. Code seam and carrier: accepted-modified, plain Python plus three tabs; MAP-rule example replaced.
12. Citation details: accepted-modified, CoALA TMLR added; MemoryAgentBench "conflict resolution" rejected (abstract says selective forgetting); Zep and other venues unverified, left out.
13. Alias gaps: accepted-modified, sub-mechanisms dropped, note-taking and Memory Bank added; book chapter numbers not cited.
14. Named idea: accepted, "Write provenance".

## Open questions for the author

1. Accept Emerging with no Standard mechanisms, given the stub's projection?
2. Code scope: `listing-studio/memory/` with three tabs, or prose-only?
3. Confirm 5.3 covers only model-written procedural memory (2.3 and 9.7 own the rest).

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Thesis and verdict.** The thesis stands as folded. The verdict is Emerging, with "Last reviewed: 2026-11". The prose may say that the underlying mechanisms (namespacing, TTL, provenance) are ordinary engineering. They are not given separate maturity rings. (Author checklist.)
2. **Scope.** Only model-written memory: episodic, semantic about the user, and procedural. Session state is in 5.1 and the semantic knowledge base is in 5.2; both are referenced in plain text where unmerged.
3. **Code.** Yes, as the map specifies: a new package, `listing-studio/memory/`, carried by the shopper assistant.
   - The primary listing is plain Python.
   - Three illustration tabs: LangGraph Store, OpenAI Responses with an external store, and the Anthropic memory tool handler. These are compile-checked only, and the memory tool type string is quoted only if the fact-checker opens the doc.
   - Offline tests: namespacing, key validation, size caps, provenance fields, structured write failures, and rejection of a poisoned tool-result write.
   - Tests use only stdlib and pydantic.
4. **Unopened sources.** OWASP ASI06, SpAIware, the ADK docs and the OpenAI docs ship only if the fact-checker opens them; otherwise they are cut.
5. **Exclusions.** No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

Second-engine review of the draft: OpenAI Codex. Each finding was checked against its source before acting.

**Prose review**
1. "Most common mistake" unsourced: softened to "the mistake to check for first".
2. Hook overclaims a vendor benchmark: fixed; now "in one vendor's own benchmark", and "less accurate the longer it runs" softened to "drifts as its entries age".
3. `expires_at` called provenance: fixed; provenance is author, source and written_at, expiry is separate.
4. Test fixture vs trace drift: fixed; the test now uses the trace's free-freight note and the 250 sq ft update, and the callout claims store-level checks only.
5. "Two vendors make a class": fixed; MINJA and AgentPoison now carry the claim.
6. "Park-style" unresolvable: fixed, "Generative Agents-style".
7. "Counter-trigger" apparatus word: fixed.
8. Provider comparison with no recommendation: fixed; recommends starting with an owned store.
9. Restating bullet ("the case for letting the model decide"): fixed, cut.
10. Overloaded benchmark sentence: fixed, split.
11. "It is a credulous author": rejected, kept; it carries the judgment the evidence then proves.
12. "X is where Y" signposting: fixed.
13. Imperative run of defences: fixed, now a list.
14. Code comments re-teaching prose: fixed for the two expiry comments (source and chapter in sync); poisoning-gate comment kept as mechanical.
15. Model-written text as bare quotes: fixed, italic quotes.
16. "Every later conversation": softened to "later conversations".

**Fact check**
17. Temporary chats can read memories: fixed.
18. LangMem page mentions neither CoALA nor a "background memory manager": fixed; CoALA cited on its own, LangMem said to use the same three types, "memory managers".
19. MINJA title: fixed to the current arXiv title, v1 title noted.
20. LongMemEval scope: fixed, "commercial chat assistants and long-context LLMs"; the ability list no longer merges extraction with multi-session reasoning.
21. Letta memory blocks served as V1 SDK (legacy): fixed in prose and footnote.
22. LangGraph Store claim uncited: fixed, LangChain long-term memory docs cited.
23. Prompt-cache claim uncited: fixed and narrowed to invalidation from the edit onward; Anthropic prompt caching docs cited.
24. Claude Code memory page title: fixed, "How Claude remembers your project". OpenAI page title also updated to "Memory in ChatGPT", LangMem to "Core Concepts".
25. Voyager, Reflexion, MemGPT, LoCoMo, Generative Agents (including min-max scaling of the three scores): opened this pass, all match.
26. CoALA not expanded in prose: fixed.

**Cold read**
27. MAP undefined: resolved by removal; the test fixture no longer uses it.
28. Hot path, sleep-time compute, namespace, supersession, ablate, prompt cache prefix: glossed at first use.
29. Constants and `_KEY` not shown: named beside their values in prose.
30. `ToolRuntime`, `REMEMBER` undefined: glossed under the tabs.
31. Companion repo never introduced: glossed.
32. CoALA and Voyager barely glossed: fixed.
33. Litmus not stated at the hybrid: fixed, "the litmus is who decides".
34. Emerging vs "ordinary engineering": fixed; the verdict is scoped to the model's write decision.
35. Why labelling matters more than the gate: fixed, the reason now follows in the same sentence.
36. Which design keeps memory in the prompt: fixed, mapped.
37. Recall deletes only when called: fixed, "the next recall deletes".
38. Keyword recall matching by luck: fixed, the shared word is named.
39. Alt text too long: fixed, about 70 words.
40. Also-called list reads as a keyword dump: fixed; trimmed to names for the whole technique (implementation and taxonomy names dropped). Flagged for the author.
41. Numbered cross-references not linked: rejected; those chapters are unmerged and stay plain text on purpose.
42. OpenAI Responses API sentence has no footnote: rejected; it describes ordinary function calling, not a non-obvious claim.

**Second-engine review (OpenAI Codex)**
43. Taint reset at the next user message is defeated by the cited Gemini delayed-invocation attack: fixed in prose. The rule now tags writes `tool` while any tool output remains in context, even after the user replies, and confirmation must cover the exact key and value. Checked against the Rehberger post. Softened rather than coded: no harness code added; the store tests still pass `author` directly and the callout says so.
44. `safe_path` accepted `/memories-other`, backslash and encoded traversal, and rename paths went unchecked: fixed in code and chapter; normalised containment check, every path field validated, a recoverable `tool_result` error returned; a new test covers the escapes.
45. Schema availability as the classification test: softened; the test is now whether you can list the facts in advance and have code fill them.
46. Context economy missing: fixed, one sentence capping what recall injects.
47. Supersession only works on an identical key: fixed in the trace; the rival-key case is stated with a mitigation.
48. Remembered text granting business authority: fixed; the floor is enforced in code (2.6) and memory never grants a permission.
49. Provider tabs bypass the store contract: softened; tabs labelled as wiring only, with what production adds.
50. Letta filesystem benchmark misdescribed: fixed; "plain file and grep" removed, configuration in the footnote, no causal claim.
51. Mandatory expiry beyond the evidence: softened to a default lifetime; maturity line narrowed to "no cited source tracks a write policy over months". Thesis rewrite not taken; the falsifiable test already sits in Evaluating it ("if memory does not beat both, take it out").
52. Trace and test values misaligned: fixed (see 4).
53. Cache and precedence claims: fixed (see 23); precedence now says the model may follow either and hard rules belong in code.
54. Session state assigned to 2.3 in the map ruling: fixed to 5.1. Retrieval-versus-memory distinction: rejected for budget; the neighbour paragraph stays.
55. Bibliographic titles: fixed (see 19 and 24).
56. Letta version scope: fixed (see 21). Alias distinctions: fixed (see 40).
57. Incident disposition: the two public disclosures are controlled research demonstrations, not observed incidents; no production incident found.
