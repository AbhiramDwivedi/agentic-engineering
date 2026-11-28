# Coverage map: State, Not Memory (chapter 5.1)

> Research-derived spec for chapter 5.1, to be trimmed and signed off by the author. It is a spec, not
> a first draft. Budget: deflation / disambiguation, ~1,500-2,000 words. Sweep angles run: vendor and
> primary docs, academic, practitioner and daily-tool, alias sweep, skeptical read. Skipped: security
> (touched only in Gotchas). Not swept: the Gulli books. Incidents: none found.
>
> **Last reviewed: 2026-11.** Vendor docs here move quarterly; carry the stamp.

## Thesis

Most of what teams call agent memory is state with a durable backend. Build it as typed, reduced,
checkpointed state your code owns, and add memory only when a future run must behave differently
because of this one. Plain label: "state first, memory later" (not a coinage).

## The mental model

**State is what this run needs to finish. Memory is what a future run needs to behave differently.**
State has a schema, a writer, a reducer and a lifetime bounded by the run or thread. It lives in your
code and database; the model sees only the slice you render into its window. Memory needs a write
policy, retrieval and forgetting, which is 5.3.

**Who decides.** State: your code (schema, reducers, checkpointer; ordinary engineering). Memory
writes: the model, when it chooses what to keep (the memory tool: "Claude stores what it learns").
Memory written by a fixed code policy (a Store write in a node) is still memory by scope but
code-decides, so it is not agentic.

## Must-cover (ranked)

`[+]` = gap to fill; the stub is skeleton only. Shipped 1.4 and 1.5 already point here (1.5 says state
and memory "both reload into the window"); honour that.

1. **The boundary test, and the vocabulary that disagrees** `[+]`. Ask two questions of any stored
   thing. Reader: does this run need it to finish, or does a future run need it to behave
   differently? Writer: does code write it by schema, or does the model choose what to keep? Vendors
   name the same things differently, and the chapter says so: LangGraph calls thread state
   "short-term memory" and the Store "long-term memory" ("retain information across different
   conversations or sessions"); OpenAI Sessions give "built-in session memory"; CoALA (arXiv
   2309.02427) defines working memory as information held "for the current decision cycle", which is
   state under another name. Borderline cases worked through the test:
   - ADK `user:` and `app:` keys (adk.dev/sessions/state): "shared across all sessions for that user"
     and "across all users and sessions". The field is called state, but a future run reads it to
     behave differently, so by this test it is memory in state's clothing. `temp:` ("discarded after
     the invocation") is state under any reading.
   - LangGraph Store: cross-thread, so memory by the reader test. A node-coded write is code-decides;
     a model-chosen write is model-decides.
   - Progress files and the Anthropic memory tool (item 6): the sharpest case.

   *Skip it:* a vector store bolted on to fix what a missing field would have fixed.
2. **Schema, reducers and merge rules as one contract** `[+]`. Typed record, partial updates from
   nodes, one writer per key where possible. The default reducer overwrites ("replaces the left value
   with the right"); `operator.add` appends; `add_messages` appends and updates by ID. Failure modes
   differ by case. Parallel writes to one unreduced key in one step raise
   `INVALID_CONCURRENT_GRAPH_UPDATE` ("the graph will throw this error because there is uncertainty
   around how to update the internal state"; fix: declare a reducer). Silent loss is the sequential
   case: a later node overwrites an earlier node's field. *Skip it:* state becomes a bag of strings
   and a later node clobbers an earlier one unseen. **Standard** for typed state; **Established**
   for reducers.
3. **Persistence is still state** `[+]`. A checkpointer snapshots state per thread (`thread_id`);
   `InMemorySaver`/`MemorySaver` lose everything on restart ("all checkpoints are lost"); `SqliteSaver`
   is labelled local development storage and `PostgresSaver` is the production recommendation. One
   claim only: checkpointed state is state, not memory. Resume, save points, cancellation and
   durable-execution requirements belong to 7.3; link there. **Established.**
4. **State versus the window** `[+]`. State is not the context: a node renders a minimal slice into
   the prompt (1.5's budget argument); unrendered state costs no attention. Counter-case: OpenAI
   Agents SDK Sessions load the whole item history ahead of new input by default
   (`SessionSettings(limit=None)`), so state and window are one object unless you set `limit=N` or
   use a compaction session. *Skip it:* full state re-sent every call. **Established.**
5. **Execution state versus business state** `[+]`. 12-Factor Agents factor 5 argues to unify them
   ("you can engineer your application so that you can infer all execution state from the context
   window") and concedes separating them "can be worthwhile". Its "business state" is the event
   thread, not the typed domain record. Counterpoint: whatever the window compacts away is lost
   control flow. Position: control flow (step, retries, pending approvals) in typed fields. Present
   as a trade-off, no separate tier; LangGraph's typed channels and ADK's typed state are de facto
   dissents.
6. **Progress files: the disambiguation's hardest case** `[+]`. When one task outlasts one context
   window, state moves to files and git: progress log, feature list with pass flags, init script,
   descriptive commits (Justin Young, 2025-11-26). Argue the call with the boundary test: scoped to
   one task and read to finish it, so state. Cite the opposing label honestly: the memory-tool page
   files exactly this pattern under "Multisession software development pattern", stored in
   `/memories`, and says it "turns memory into a recovery mechanism". The harness article uses
   neither word for the mechanism. The same artifact is state or memory depending on whether its
   reader is the same task or a later one. **Emerging** as a practice; the memory-tool page is
   marked stable.
7. **Where to stop** `[+]`. One short paragraph and a hand-off: memory is state plus a write policy,
   retrieval and forgetting. Memory-tool detail, CoALA's taxonomy and MemGPT are 5.3's lead
   citations; do not teach them here.

## Mention-and-link

- 1.4 The Augmented LLM: typed state and node (shipped). Do not re-teach `ListingState`.
- 1.5 Context Engineering: window budget, attention cost (shipped). Link, do not repeat.
- 2.5 The Agent Loop (planned): owns how the transcript accrues; 5.1 owns the typed record outside it.
- 3.7 The Outer Loop (planned): 5.1 gives the record's shape; 3.7 owns when to retry.
- 4.3 Human-in-the-Loop: pausing on a checkpoint.
- 5.2 Retrieval: knowledge, not state. 5.3 Memory: the learned half and the memory tool in depth.
  5.4 Compaction. 7.3 Checkpointing: save points, cancellation, resumption, durable execution.

## Out of scope

Memory architectures and retention policy (5.3). Vector stores (5.2). Summarisation (5.4). Resume
demos and durable-execution engines (7.3).

## Maturity summary

- **Standard:** the typed state schema.
- **Established:** reducers; per-thread checkpointing; state kept separate from the window.
- **Emerging:** model-managed memory writes; progress-file harnesses.
- No tier: execution versus business state (a trade-off; one hedged practitioner opinion).

**Chapter verdict candidate: Established** (downgraded from the stub's Standard). Re-derived from the
map's own citations: the practice, typed reduced checkpointed state, is Standard engineering. But the
chapter's claim is the distinction, and the map's own sources file state under "memory" (LangGraph,
OpenAI, CoALA) or let state outlive the session (ADK `user:`/`app:`), with no non-vendor source that
calls it fundamental. The vocabulary is not settled, which is why the chapter exists. Reasoned
verdict, flagged in the PR. Last reviewed 2026-11.

## Aliases (for `*Also called:*`)

Short-term memory, thread state (LangGraph memory docs); session state (ADK); Sessions (OpenAI
Agents SDK); working memory (CoALA, which treats it as a kind of memory). Needs author sign-off; the
stub has no alias line.

## Reader-verifiable anchors

- LangGraph with the in-memory saver: restart the process and the thread's state is gone.
- OpenAI Agents SDK `SQLiteSession`: with no file path it is an "In-memory database (lost when
  process ends)", so persistence is shown only if you pass a path.

## Incidents

None found specific to state-versus-memory confusion. Do not invent one.

## Carrier section (Stockwell, Listing Studio)

Anchor: the pipeline's `ListingState` in `listing-studio/augmented_llm/state.py`. As shipped it is a
`TypedDict` with three fields: `supplier_sku`, `title` and `price_cents` (optional until the price
node runs). It has no step status and no `launch_package` (that is a carrier-bible Listing field).
5.1's companion code extends it in a new 5.1 module (step status, one parallel-written key), not in
the 1.4 file. Use "a merchant" until a person recurs; attach a name only then. State half in Listing
Studio: one run, one Listing, thread scoped. Memory half in the shopper assistant (the carrier bible
names it for multi-turn state versus memory): "the shopper's garage size is remembered next visit"
is cleaner than a merchant tone preference. Companion code, at most two demos: (1) a reducer test
that asserts `INVALID_CONCURRENT_GRAPH_UPDATE` on a parallel unreduced key, then the reducer that
fixes it; (2) durable versus in-memory saver. No resume demo (7.3). A "From production:" callout is
the author's; this map makes no first-hand claim.

## Gotchas (feed the Anti-Patterns Catalog)

- Cargo-cult memory (already in the catalog under that name): a vector store used to carry one
  task's state.
- Unreduced parallel write to one key: raises; the silent version is a later node overwriting an
  earlier one.
- In-memory checkpointer shipped to production.
- State and window conflated: full history re-sent every call.
- Control flow inferred from message text, then compacted away.
- Schema change breaks persisted threads (a field rename breaks every paused run; ordinary data
  engineering, reasoned, no agent-specific citation).
- State bloat and PII in checkpoints; `thread_id` collisions across tenants.
- A progress file treated as memory and never pruned.

## Named-idea candidates

None earned. Plain label "state first, memory later"; author may strike.

## Sources (opened 2026-11-27 unless marked)

1. LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
2. LangGraph memory: https://docs.langchain.com/oss/python/langgraph/memory
3. LangGraph Graph API: https://docs.langchain.com/oss/python/langgraph/graph-api
4. LangGraph error page: https://docs.langchain.com/oss/python/langgraph/errors/INVALID_CONCURRENT_GRAPH_UPDATE
5. Google ADK sessions: https://adk.dev/sessions/ and state: https://adk.dev/sessions/state/
6. OpenAI Agents SDK sessions: https://openai.github.io/openai-agents-python/sessions/
7. Anthropic memory tool: https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
8. Justin Young, Anthropic, "Effective harnesses for long-running agents", 2025-11-26: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
9. 12-Factor Agents factor 5: https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md
10. Sumers, Yao, Narasimhan, Griffiths, "Cognitive Architectures for Language Agents", arXiv 2309.02427 (2023-09-05, v3 2024-03-15, TMLR). Working-memory definition taken from the second reviewer's full-text read; not re-opened here.
11. Packer et al., "MemGPT", arXiv 2310.08560 (2023-10-12, v2 2024-02-12). Cited for 5.3, not taught here.

## Verify before quoting

Unverified: LangGraph durable-execution requirements (7.3's); CoALA full text (re-open before
quoting). Saver and SDK class names rot; re-open before quoting, anchor code on symbol names. Gulli
books not swept (the ADP book likely has an ADK Session/State/Memory chapter; check for aliases).

## Author-only questions (conservative defaults)

1. "From production:" callout? Default: none.
2. May the chapter argue against factor 5? Default: trade-off with a mild stated preference.
3. Add an `*Also called:*` line? Default: no, until signed off.
4. Maturity: map recommends Established, the stub says Standard. Default: Established, flagged in PR.
5. Durable-execution engines? Default: no, 7.3.
6. Sweep the Gulli books for aliases? Default: not run; flagged.
7. The stub carries `*Grounding:* production`. That is a first-hand production claim only the author
   can make; the stub is left untouched. Conservative default would be `companion repo + research`.

## Second-reviewer pass (Claude Opus; codex unavailable, usage limit)

Each finding checked against the primary source, then folded in or rejected.

1. Parallel write raises: accepted. Error page opened; quote and fix confirmed. Item 2, Gotchas, demo rewritten.
2. `ListingState` fields: accepted. Opened `state.py`: three fields only. Carrier section rewritten.
3. "Converges" and boundary test: accepted. ADK state, LangGraph memory and OpenAI pages opened; item 1 rewritten with the test and worked cases. CoALA text taken from the reviewer, not re-opened.
4. Progress file vs memory-tool page: accepted. Memory-tool section opened; "turns memory into a recovery mechanism" quoted in item 6.
5. Litmus line: accepted. Who-decides paragraph added.
6a. Chapter verdict: accepted-modified. Downgraded to Established (reviewer offered Standard-for-half or Established); chose the stricter reading.
6b. Item 6 Contested: accepted. Now a trade-off with no tier; `how-we-label.md` definition checked.
6c. Item 9 tier: accepted. Moved to Gotchas as reasoned.
7. Bloat and seams: accepted-modified. Merged schema and reducers, cut persistence and memory items, two demos. Seven items, not six, because progress files are the hardest case.
8. Grounding production: accepted. Author-only item 7; stub untouched.
9. Chapter number: accepted. 1.4 confirmed in `mkdocs.yml`; anti-patterns name confirmed.
10. Sessions: accepted. Both facts confirmed on the OpenAI page.
11. Savers: accepted. Wording per the reviewer's reading of the persistence page; not re-opened.
12. 12-Factor: accepted. Factor 12 dropped and alias removed; factor 5 text not re-opened.
13. Citations: accepted. TMLR and working-memory alias added.
14. Out-of-repo reference: accepted. Reworded.
15. Carrier name and surface: accepted. Carrier bible confirms the shopper assistant line.
16. Thesis and budget: accepted. Both added; design-system budget row confirmed.

## Orchestrator rulings (Stage 1.6, 2026-11-27)

- **Thesis (binding):** "Most of what teams call agent memory is state with a durable backend. Build it as typed, reduced, checkpointed state your code owns, and add memory only when a future run must behave differently because of this one."
- **Spine:** items 1 to 7 as ranked; the boundary test (reader question + writer question) is the chapter's explanatory diagram candidate. Budget ceiling ~2,500 prose words (a disambiguation chapter; 5.3 owns memory depth, 7.3 owns resume).
- **Maturity:** Established (author-only item 4 default), with typed state Standard and progress files Emerging in the prose. Last reviewed 2026-11.
- **Code (at most two demos):** (1) a parallel unreduced key raising `INVALID_CONCURRENT_GRAPH_UPDATE`, then the reducer that fixes it; (2) in-memory versus durable checkpointer across a simulated restart. New module, `ListingState` in 1.4 untouched. Shopper assistant appears in prose only, for the memory half.
- **Vocabulary:** say plainly that vendors use "memory" for things this chapter calls state; "state first, memory later" is a plain label, not a coinage.
- **Author-only defaults:** as listed above (no From-production callout; trade-off on factor 5; no new alias line; Established flagged; durable-execution engines deferred to 7.3). The stub's "Grounding: production" ships as "research + companion repo" and is flagged in the PR.
