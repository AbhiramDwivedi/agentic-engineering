# Coverage map: Checkpointing (chapter 7.3)

> Research-derived spec for what the chapter must cover so a reader can cancel and resume an
> agent run without repeating its side effects, and where to stop. Angles run: vendor and
> framework docs, academic (two 2026 preprints), practitioner and vendor-engine docs, skeptical
> read, daily-tool, incidents (searched, none public). OWASP touched through the rollback-attack
> papers and the poisoned-checkpoint risk. Review and trim **Must-cover**; that sets the scope.

**Thesis.** Checkpointing saves state between steps, not the step in flight; because a resumed
model will not emit the same call twice, a checkpointer without a journal of intent and fenced
side effects turns recovery into duplicate execution.
**Budget:** standard pattern with a code-decides deflation, about 2,000 to 2,800 words.
**Litmus:** your code decides. Checkpointing, replay, cancellation and effect fencing are
deterministic infrastructure; the model is the non-deterministic worker inside a step.
**Grounding:** companion repo plus research. No `From production` callout; the stub's
`production` label must be replaced.

## The mental model

Temporal's vendor framing is that "the checkpoint preserves your data, not your execution".
Saving the record after every step lets a cancelled or crashed run continue, but resume re-runs
the step that was in flight. So resumability needs two halves: a durable record of completed
steps (never redone), and a journal of each step's intent written before any effect crosses the
process boundary (so the step in flight can be replayed with identical arguments). Cancel is the
polite version of the same event: a stop your code chooses, at a seam it picked, with a save.

## Must-cover (for safe production use)

Each: why, failure if skipped, maturity, lead citation. `[+]` = new (stub has no body).

1. **Snapshot per step, and the step in flight re-runs** `[+]` : snapshot the record after every
   step under a run id; resume continues at the first unfinished step and re-executes the
   interrupted one from its start. 5.1 owns the record; 7.3 owns what you do with snapshots.
   *Skip it:* resume taught as free; effects before the crash point repeat. **Established.**
   (LangGraph Persistence; DBOS architecture. The "restarts the entire node from the beginning"
   quote is from the Interrupts page and covers pause/resume only; cite the durable-execution
   or Persistence page for crash replay after re-opening it.)
2. **Fencing external effects under non-deterministic replay (seam with 7.1)** `[+]` : retry (7.1)
   and resume (7.3) both depend on it. Journal the model's call and its key before the effect;
   on replay reuse the journaled call, so arguments are identical and the receiver dedupes
   cleanly. A key on `(run_id, step_id)` is a fail-closed guard: on strict servers a reused key
   with changed parameters returns an error (Stripe compares incoming parameters to the original
   and errors if they differ; v1 keys may be pruned after 24 hours), so a mutated replay fails
   loudly instead of silently duplicating. It also breaks when one step issues several calls.
   *Skip it:* idempotency passes in tests that mock the model and fails in production.
   Technique **Standard**; agent-safe replay **Emerging** (two preprints on attack testbeds, no
   field data). (Stripe idempotent requests; Restate deduplication; arXiv:2603.20625;
   arXiv:2608.29381.)
3. **Journal-and-replay engines versus a library checkpointer** `[+]` : Temporal, Restate and
   DBOS run the loop as deterministic orchestration with model calls and tools as recorded steps
   reused on replay; anything non-deterministic lives inside a step. A library checkpointer can
   also cache task results (LangGraph `@task`, unverified here, re-open); what it lacks is
   external worker supervision and automatic restart of a dead worker. *Skip it:* the reader
   thinks a SQLite saver gives crash recovery. Engines **Established**; agent integrations
   **Emerging** (Temporal's OpenAI Agents SDK integration GA 2026-03-23). (Temporal Workflows;
   DBOS; Restate.) 7.3 owns the journal-and-replay model; 8.7 owns supervision and hosting.
4. **Durability modes and replay versus fork** `[+]` : concept level, not an API tour. Writes may
   be synchronous, asynchronous or at exit, trading latency against a loss window if the process
   dies. Time travel replays from a checkpoint and re-runs model and tool calls, so it can differ
   and repeat effects; updating state forks and never rolls back. *Skip it:* time travel used as
   "undo". Checkpointing **Established**; time travel as debugging **Emerging**. (LangGraph
   Persistence; "Use time travel". Mode names and the default go in the LangGraph tab, only
   after the durable-execution page is opened.)
5. **Cancel and resume** `[+]` : cancel is a graceful signal the run handles and cleans up after;
   terminate is not. In Temporal an activity learns of cancellation through heartbeats. For an
   agent: check a cancel flag between steps and inside long tool calls, save, stop. Name the
   three stop paths (user cancel, budget stop, crash) and what each leaves. 8.4 owns budgets.
   *Skip it:* a stop button that kills the process mid-write. Graceful cancel **Standard**; for
   agents **Emerging** (support is fragmented across SDKs). (Temporal cancellation; 12-Factor
   Agents factor 6.)
6. **Granularity, payload economy and the failure return** `[+]` : what belongs inside a step
   versus between steps; keep raw blobs out of the checkpoint (they slow synchronous writes and
   reload stale payload into context); on a stale-state or key-mismatch rejection, return a
   structured error the loop can act on. *Skip it:* bloated checkpoints, opaque resume failures.
   **Emerging.** (LangGraph Persistence; 5.4 for context.)
7. **What state is safe to resume** `[+]` : resume the record, re-check the world. The price may
   have changed, a token expired, the approval aged out (4.3 owns expiry). Re-validate external
   dependencies; do not resume a run whose credentials were consumed. Include poisoned
   checkpoints (a resume replays an injected payload; roll back to a clean one) and authority
   resurrection (ACRFence), with OWASP ASI06 and ASI08 as the framing, to be opened before
   quoting. Retention: checkpoints accumulate and hold personal data (8.5 owns locks, PII and
   identity; 7.3 owns pruning). **Emerging** (five failure modes in arXiv:2608.29381).

## Mention-and-link (one line, a pointer)

- Typed record, reducers, thread scope, schema migration, tenant-namespaced `thread_id` → 5.1.
- Pausing for a person, `interrupt()`, request ids as keys, expiry → 4.3.
- Retry, backoff, fallback → 7.1. Traces and stalled-run detection → 7.2.
- Locks, PII, credential scoping → 8.5. Budget stops → 8.4. Queues, workers, hosting → 8.7.
- Campaign-length runs and progress files → 9.1. Compaction dropping control flow → 5.4.
- Verify-and-retry outer loop → 3.7; harness hooks and stop conditions → 2.6.

## Out of scope

- Operating Temporal, Restate or DBOS clusters. Agent memory across runs → 5.3. Saga theory.
- Prompt-prefix caching → 8.4 / 1.5. Serving-shape choice and managed runtimes → 8.7.

## Maturity summary

- **Standard:** idempotency keys for retried requests; graceful cancel versus hard kill.
- **Established:** per-step checkpointing; durable (not in-memory) savers; journal-and-replay
  engines; the "re-run the step in flight" rule.
- **Emerging:** agent-safe replay of model calls; agent cancellation; file or state rewind;
  time travel as a debugging tool; rollback-safety of checkpoints.
- **Contested (two real disputes):** whether a library checkpointer such as a Postgres saver
  suffices in production or a durable-execution engine is needed; whether checkpoint time travel
  is safe recovery once external effects exist.
- **Chapter verdict: Established** (state checkpointing and durable-execution engines) ·
  **Emerging** (agent-safe replay and rollback). Not Standard: engines are vendor products and
  agent-specific guarantees rest on docs and two v1 preprints.

## Aliases (the neighbouring canon)

- Stub: cancellation / resumption, durable state, save points.
- Added: checkpoint-restore (C/R), resumability (Google ADK), file checkpointing and `/rewind`
  (Claude Code), time travel (LangGraph), durable execution and journal (Temporal, Restate, DBOS).
- Class names (`InMemorySaver`, `PostgresSaver`) and engine primitives are terms, not aliases.
- Gulli, *Agentic Design Patterns* ch. 12, "Exception Handling and Recovery" (rollback and state
  recovery), is the nearest catalog entry; the books were not re-opened for this fold, the alias
  sweep checks them. Author confirms the `Also called` line.

## Reader-verifiable anchors

- Run a LangGraph graph, kill the process mid-node under one durability mode and then another,
  and compare what the thread shows on restart (re-open the durability docs to fix the modes).
- In Claude Code, edit a file, run `/rewind`, then change another file by shell command and see
  it left alone; checkpoints are pruned after 30 days by default (checkpointing docs).

## Incidents

None found as a public postmortem. Duplicate-effect cases appear only in the two preprints'
tables and attack demos. State plainly: evidence for the replay hazard is experimental.

## Named-idea candidates (author accepts or strikes)

- **Resume the record, re-check the world.**
- **Journal before effect** is the existing write-ahead and outbox idiom, not a coinage; use it
  as a gloss, not a named idea. "Key on the step, not the content" is struck: it does not hold.

## Code seam

New package `listing-studio/checkpointing/`, self-contained (offline, scripted model that returns
different arguments on replay), anchored on Listing Studio (Aldsworth desk, step 7 announcement
email, step 9 `publish`) and the repricer (stale `price_cents` on resume). The test shows: the
step in flight re-runs; a content-derived key fails on a mutated replay; a step key against a
strict receiver raises a parameter mismatch; a journaled replay dedupes cleanly. LangGraph tab
by the repo default (design-system and carrier-bible); Responses and Anthropic tabs only where
the SDKs show a resume surface (OpenAI background responses and cancel; Claude Agent SDK file
checkpointing and session resume; Google ADK resumability, all to be opened). No engine code.

## Sources (opened unless marked)

LangGraph: Persistence, Interrupts, "Use time travel" (docs.langchain.com/oss/python/langgraph/).
The durable-execution page did not load on this fold (it returned the checkpointers summary);
durability-mode names, default and `@task` are unverified, re-open before quoting. Temporal:
Workflows (docs.temporal.io/workflows); Cancellation, Python (docs.temporal.io/develop/python/workflows/cancellation);
OpenAI Agents SDK integration (GA 2026-03-23 per Temporal); blog "LangGraph in production:
Temporal's LangGraph Plugin adds Durable Execution" (2026-07-16, Ruhe, Hyde, Strauch; vendor).
DBOS (docs.dbos.dev/architecture). Restate (docs.restate.dev/concepts/durable_execution). Stripe,
"Idempotent requests" (docs.stripe.com/api/idempotent_requests; re-opened in this fold: parameter
comparison and 24-hour pruning confirmed). Claude Code "Checkpointing"
(code.claude.com/docs/en/checkpointing). 12-Factor Agents factor 6. Zheng, Yang, Zhang, Quinn,
"ACRFence", arXiv:2603.20625 (2026-03-21). Wu, Li, Jiang, Niu, Wang, Zhang, "Safe to Resume?",
arXiv:2608.29381 (2026-08-29).

## Open questions for the author

1. Override the stub's `Grounding: production` to companion repo plus research?
2. Confirm the Listing Studio plus repricer split for the worked example.
3. Which provider tabs earn space beyond LangGraph?
4. Confirm the 5.1 / 7.3 / 8.7 seams, and the `Also called` line.

## Map review (Stage 1.5)

Reviewer: Gemini. Verified against the Stripe docs (re-opened) and repo files.

1. Thesis, budget, litmus missing: accepted, added to the header.
2. "per memory" and unmerged-branch references: accepted, removed; package made self-contained.
3. Stub `production` grounding: accepted, Grounding line and open question added.
4. Stripe parameter mismatch: accepted, verified on the Stripe page; items 3 and 4 merged and
   "Key on the step" struck.
5. LangGraph durable-execution docs: accepted-modified, framing fixed to supervision versus
   library; the page would not load, so `@task` and the async default stay flagged unverified.
6. Must-cover bloat and seams: accepted-modified, trimmed to 7, schema versioning dropped, 8.4,
   8.5 and 8.7 added; the rewind item moved to anchors.
7. Gaps (vendor surfaces, granularity, poisoned checkpoints): accepted-modified, items 6 and 7
   added; vendor surfaces listed in the seam as to-be-opened, not asserted.
8. Maturity verdicts and Contested: accepted, downgrades, split verdict, two real disputes.
9. Gulli sweep and aliases: accepted-modified, class names removed and aliases added; Gulli ch.
   12 title taken from the review and not re-verified.
10. Carrier alignment and open questions: accepted, both added.
11. Titles, URLs, slogan attribution: accepted-modified, title and attribution fixed; direct URLs
    only for pages opened.
12. Interrupts quote and 30-day retention: accepted, quote scoped; retention added from the
    review, not re-opened.
13. Duplicate anchor, "Journal before effect": accepted, anchor replaced; marked as existing idiom.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Thesis and verdict.** The thesis stands as folded. Verdict: Established, with the agent-safe replay and rollback part Emerging. Name the two Contested disputes in one paragraph.
2. **Grounding.** Change the stub's `Grounding: production` to companion repo plus research. A first-hand claim is not ours to make. (Author checklist.)
3. **Carrier.** Listing Studio is the primary carrier. The repricer is the side-effect example (a price write), as the map suggests.
4. **Code.** Use the new package `listing-studio/checkpointing/` exactly as the map specifies, with a scripted model and offline tests on stdlib and pydantic only.
   - Provider tabs: LangGraph only (checkpointer plus thread_id), as a compile-checked illustration.
   - No OpenAI or Anthropic tabs, because neither offers a checkpointer API to show. (Author checklist.)
5. **Unverified claims.** The LangGraph `@task` caching and `async` default claims ship only if the fact-checker opens the page. Otherwise, cut them. The same applies to the 30-day retention figure and to the vendor SDK resume surfaces.
6. **Seams and aliases.**
   - 5.1 owns state shape, and 8.7 owns long-running and background agents. Refer to both in plain text.
   - Use an `Also called:` line only for sourced terms. (Author checklist.)
7. **Off limits.** No From-production callout, no coinage, and no edits to shipped chapters.

## Reconcile log (Stage 5)

QA inputs: prose critic, fact-checker, cold reader, and an independent second-engine review of the draft (OpenAI Codex). Each finding was checked against the chapter, the companion code or the primary source before acting.

**Orchestrator and prose critic**

- Hook ratio ("about as readily as it prevents") had no source: fixed, reworded to "can cause that failure even as it prevents the one it was built for".
- "A model will not write the identical email" and "never answers the same way twice": fixed, now "may word the email differently" and "can answer differently each time you ask". The content-key sentence ("they may not be") and the quotable line ("can change its mind") were scoped the same way.
- `/rewind` closing aphorism: fixed, cut.
- Performed pair after the `run` listing: fixed, replaced with one sentence.
- Short-sentence closer after the step key: fixed, merged, and now explains why the step is stuck.
- "The fix has two parts." signposting: fixed, cut.
- Model-written subjects in the opening: fixed, italic plus quoted. Trace fixture strings left plain.
- Trace uses steps `a`/`b`: softened, the intro now says step `b` stands in for the announcement step; test names not changed.
- Neighbour paragraph duplicating See also, and ownership narration: fixed, cut to the 5.1 split; "owns" phrasing removed from the 8.4 and 8.5 mentions.
- Alt text narrating the shape convention: fixed, trimmed.
- Build housekeeping in the body ("compile-checked", "no OpenAI tab"): fixed, the compile-check claim is cut and the no-tab line now tells the reader what to do.
- Gotcha 4 generic (structured errors): fixed, replaced with the unknown-outcome rule (see second engine 2).
- Gotcha 1 flourish and universal: fixed.
- "Neither reports field data" duplicated the footnotes: fixed, cut; the no-postmortem sentence stays (author checklist).
- Anti-pattern narration in gotcha 7: fixed, the named anti-pattern is stated directly.
- Step 7 sending email, and `"sku": "LS-1001"` against the bible's `supplier_sku`: not changed. Moving the send to step 9 would redraw the diagram and fixtures, and the bible gives the desk no SKU value to copy. Carrier untouched; both go to the author checklist.

**Cold reader**

- Undefined terms: fixed by glossing at first use: idempotency key, write-ahead, fencing, reducers, thread scope, transactional outbox, heartbeat, injected text, `thread_id`.
- Bare chapter numbers 5.1, 8.4, 8.5, 8.7, 5.4: already titled in plain text; kept unlinked (unmerged chapters).
- Build listing lacked `Step`, `Receiver`, `ScriptedModel` and the imports: fixed, three new anchored blocks (`ckpt-step`, `ckpt-receiver`, `ckpt-model`) added to the companion code and registered in the doc-sync test.
- Why a step key "leaves the step stuck": fixed, explained.
- L104 multi-call paragraph too compressed, `/rewind` analogy loose, LangGraph tab names unshown: rejected, budget; the tab is an illustration and the plain listing is the primary.

**Fact-checker**

- [^7] "five distinct ways": softened to "cataloguing the ways a resume goes wrong"; the count is dropped because two reads of the abstract disagreed. Full title added.
- LangGraph "at every step": softened to "saves graph state as checkpoints grouped under a thread id".
- Restate "non-deterministic step": softened; engines "record each completed step ... with its result"; the page (re-opened) says Restate records the operation and its result and skips completed steps. Footnote retitled "Key Concepts", the page's current title.
- [^11] `/rewind`: fixed; the example now uses a file only the shell has touched, matching the docs.
- [^5] parameter comparison and 24-hour pruning: fixed, scoped to Stripe's v1 API.
- First-person "I could not find a public postmortem": kept, author checklist.
- IETF Idempotency-Key draft as a second source: rejected, not opened this stage.

**Second-engine review**

1. Durability modes missing: softened. "Not redone once its checkpoint has committed" and gotcha 7's commit clause; LangGraph durability-mode specifics not added because the map marks that page unopened.
2. No unknown-outcome path: fixed, gotcha 4 (query the receiver, stop for an operator, never mint a new key) and gotcha 5 (past the key window, treat the send as unknown).
3. Rollback contradicts effect safety: fixed, gotcha 2 now says rollback restores local state only and the journal must sit outside it.
4. Universal non-determinism: fixed (see orchestrator item above).
5. Cancel as unconditionally clean: fixed, clean only when honoured at a step boundary; a cancel mid-send is a crash. Heartbeat sentence already scoped to long-running activities.
6. Engines vs libraries conflated: softened, the dispute is now "a system that notices a dead worker and restarts it", and the engine sentence adds that a step still running when the worker died runs again.
7. Carrier step 7 and SKU: not changed, author checklist.
8. Evidence overstated: fixed, the trace is described as separate tests, and the compile-check claim is cut (no test imports the LangGraph file).
9. Snapshot invariants: fixed, one sentence on an atomic write of a deep copy.
10. Resume compatibility: fixed, one clause in gotcha 1 (reject or migrate a run whose step list changed).
11. Disputes invented: softened, "Two questions are open"; verdict unchanged (Established core, Emerging agent-safe replay).
12. Claude Code anchor: fixed (see [^11]); the retention figure is not in the chapter.
13. Aliases collapse related mechanisms: rejected, the line follows ruling 6; author checklist.
14. Citation metadata: fixed, full titles for both papers, ACRFence's CoDAIM workshop venue, "papers" not "preprints". "It is cheap" cut from In short.
15. Trim apparatus: fixed (neighbour paragraph).
