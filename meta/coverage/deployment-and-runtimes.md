# Coverage map: Deployment & Runtimes (chapter 8.7)

> Research-derived spec for what the chapter must cover so a reader can put an agent behind an
> endpoint, a queue or a schedule and keep it running, and choose between running the loop
> themselves and renting it. Angles run: vendor primary docs, practitioner posts, incidents
> (searched, none found), daily-tool, skeptical read, alias sweep. Skipped: academic (no founding
> papers exist for this topic). Review and trim **Must-cover**; that sets the chapter's scope.

## Thesis

An agent run outlives an HTTP request and can wedge while looking healthy, so deployment is
durable-state and progress-supervision engineering; renting a managed runtime moves the loop and
the sandbox to a vendor, never the state contract, the trust boundary or the spend ceiling.

**Litmus: your code decides.** Serving shape, leases, supervision, replay, triggers and the
hosting boundary are all decided by code; the model's loop is the long, non-deterministic,
side-effecting payload inside the worker. The stub's lens line needs this backfilled.
**Prose budget:** Standard pattern row, ~2,000-2,800 words.

## The mental model

The question is never "how do I host a function" but "who holds the state while the run lasts, and
what happens when the process holding it dies." Three serving shapes (wait, stream, hand back a
ticket), one topology for the ticket (queue, worker, durable record of progress), one decision on
top: run that loop yourself or rent it.

## Must-cover

Ranked. `[+]` = gap in the stub. Maturity per item.

1. **Serving shape and compute ceilings: sync, stream, async** `[+]` - a ten-minute run does not
   fit a request/response socket. Sync only for short bounded runs; stream when a human watches
   (6.3); async (accept, return an id, deliver by poll or webhook) otherwise, with caller-initiated
   cancel as part of the contract. Serverless fits only if the run fits: Lambda has a hard
   timeout ceiling (check the live page; earlier notes recorded 30 minutes); raise the queue's visibility
   timeout before the function timeout. *Skip it:* gateway timeouts kill healthy runs, users
   re-submit, you pay twice. **Established.** (OpenAI background mode: `background: true`, poll by
   id, `POST /v1/responses/{id}/cancel`, idempotent; AgentCore async model; Lambda timeout docs.)
2. **Queue, worker, delivery contract and backpressure** `[+]` - the queue is at-least-once, so a
   worker that outlives its lease gets the job again. Size the visibility timeout to the run (AWS
   advises at least six times the function timeout for Lambda consumers), heartbeat to extend it,
   add a dead-letter queue (AWS suggests `maxReceiveCount` of at least 5), and cap worker
   concurrency so a bulk job does not trip provider rate limits (retries -> 7.1). Agent runs are
   not idempotent by default, so side-effecting tools need idempotency keys (7.3 owns the
   technique; here: why deployment makes it mandatory). *Skip it:* double publishes, poison
   messages, a 429 storm. **Standard** (queues, leases, DLQ); **Established** (agent-specific
   sizing). (SQS visibility timeout docs; Lambda SQS event-source docs.)
3. **Supervision: liveness is not progress** `[+]` - restart policy, probes, graceful shutdown on
   SIGTERM inside the platform's grace period, capped restarts that end in a page. A healthy
   process can be stuck, so supervise task completion, not only a heartbeat. Use the platform
   supervisor (systemd, Kubernetes, the queue lease) before writing one. *Skip it:* a wedged agent
   that looks alive, or a restart storm. **Standard** (supervision); **Emerging** (progress-based
   checks for agents; one vendor contract so far). (Claude Code docs: SIGTERM exits 143 and leaves
   the turn unfinished; AgentCore `/ping` `Healthy` vs `HealthyBusy`, 15 minute idle
   termination, a blocked ping thread kills a busy agent.) Links 7.1, 7.3, 8.1.
4. **Durable execution and rollout versioning** `[+]` - the session log lives outside the worker so
   a replacement resumes. Seam with 7.3: 7.3 owns step-level checkpoints inside the graph; this
   chapter owns worker-level durability and what happens to in-flight runs when you deploy new
   code. Three public forms: workflow engines (Temporal: loop as Workflow, model and tool calls as
   Activities, Worker Versioning pins running Workflows to the code version that started them),
   framework checkpointers (7.3), provider-held sessions (item 7). A durable event log cannot be
   replayed raw into a bounded window (1.5, 5.4). *Skip it:* a crash loses an hour of paid work, or
   a deploy changes the prompt under a run mid-flight. **Established** (idea); **Emerging**
   (agent-specific engines). (Temporal worker-deployment docs; Anthropic, "Scaling Managed Agents",
   Lance Martin, Gabe Cemaj, Michael Cohen, 8 Apr 2026.)
5. **Triggers: poll, push, schedule, webhook** `[+]` - who starts a run. Prefer push; poll with a
   cursor and a cap; schedule with explicit missed-run and overlap policy. Inbound webhooks need
   signature checks. One line on the outbound-callback SSRF door, mechanics -> 8.5/9.4. *Skip it:*
   duplicate or missed fires. **Standard** (cron, webhooks); **Established** (agent specifics).
   (OWASP SSRF Prevention Cheat Sheet; Anthropic scheduled deployments: cron plus IANA timezone,
   jitter, no backfill on unpause.) Links 4.6.
6. **Background agents** `[+]` - agents without a person at the terminal: a non-interactive CLI run
   in CI, a scheduled run, a cloud session steered later. Deployment must answer: who answers
   permission prompts (default is deny), what the run may leave behind (a PR, not a push), how far a
   stuck run can spend, how you learn it finished. Anchor: `claude -p` exits non-zero on failure,
   `--permission-prompts none` denies instead of waiting (v2.1.259 or later; `--permission-mode
   dontAsk` is the settings route), `--max-budget-usd` stops the run, background work gets a
   10 minute idle wait by default. **Seam with 9.1: single-run unattended hosting is here;
   multi-session campaigns, progress files and how much autonomy to grant are 9.1.** **Established**
   (mechanics); **Emerging** (cloud-hosted sessions).
7. **Managed runtimes and the shared-responsibility boundary** `[+]` - the platform runs the loop,
   sandbox, session store and restarts; you own the system prompt, tools and permissions, session
   start and stop, budget, output handling and the trust boundary. Four runtime classes: provider
   agent services (Claude Managed Agents, beta header `managed-agents-2026-04-01`; OpenAI
   background mode as the thin form), cloud agent platforms (Bedrock AgentCore), framework agent
   servers (LangSmith Agent Server, the carrier's own stack), stateful actor runtimes (Cloudflare
   Agents, each a Durable Object). Define the agent once and version it; a session per run, never an
   agent per request. What stays yours: retention (Managed Agents sessions persist until deleted and
   are not eligible for ZDR except self-hosted, nor for HIPAA at all; OpenAI background mode stores
   about 10 minutes to disk even with `store: false`), per-run budgets, identity, and a schedule that
   pauses itself on a retired model. Mechanics -> 8.4, 8.5, 8.6. *Skip it:* rebuild a platform, or
   adopt one blind. **Standard** (the responsibility split); **Emerging** (the platforms; stamp
   "Last reviewed"); **Contested** (any claim that hosting removes the need for your own guardrails).
8. **Build versus rent, and lock-in** `[+]` - axes: control depth vs operational load, state and
   observability access, data residency (self-hosted sandboxes exist), model portability (AgentCore
   is framework- and model-agnostic; Anthropic's service is Claude-only and beta; the carrier is
   multi-provider LangGraph on Postgres), exit cost (session formats are provider-specific). Write
   the loop once yourself before renting it; rent where the ops burden is the cost. **Contested**
   (situational; no neutral evidence base).

## Mention-and-link

6.3 streaming and SSE reconnect; 7.1 retry; 7.3 checkpoints and idempotency keys; 8.1 tracing and
heartbeats; 8.4 cost; 8.5 secrets and IAM; 8.6 retention; 9.4 sandboxing; 9.1 autonomy; 9.2
fleets; 9.6 coding agents; 8.2 model choice and self-hosted inference; 2.5 and 3.7 loops; 2.6
harness; 1.5 and 5.4 context and compaction.

## Out of scope

Kubernetes, Terraform and CI for the service itself (cite one doc); provider API minutiae beyond
the one beta header; model choice and evals; sandbox isolation internals.

## Maturity summary

- **Standard:** supervision and graceful shutdown, queues with leases and DLQs, cron and webhook
  triggers, the responsibility split.
- **Established:** sync/stream/async rule, at-least-once plus idempotency, durable execution as an
  idea, non-interactive agent CLI runs.
- **Emerging:** managed agent platforms, agent-specific durable engines, cloud-hosted background
  sessions, progress-based supervision.
- **Contested:** build vs rent; "hosting removes the need for guardrails."

The stub projection (Established shapes, Emerging platforms) holds for the chapter headline; the
per-item tiers above refine it. Add background agents to the stub's scope line.

## Aliases

agent deployment, agent runtime, hosted agent runtime; managed agents (Claude Managed Agents);
Bedrock AgentCore Runtime; LangSmith Agent Server (formerly LangSmith Deployment); Cloudflare
Agents; background mode (OpenAI); headless / non-interactive mode, `claude -p`; scheduled
deployments; durable execution, workflow, activity (Temporal). Google's hosted runtime was
"Vertex AI Agent Engine", now "Agent Platform Runtime"; confirm before quoting. Dropped
"always-on agent" (9.1 owns it). "Daemon agent" is informal, no primary source. 12-Factor Agents
factors on launch/pause/resume and trigger-from-anywhere are candidate aliases, not yet opened.

## Reader-verifiable anchors

1. `claude -p "..." --output-format json`: read `total_cost_usd` and the exit code; add
   `--permission-prompts none` and watch denials in `permission_denials`.
2. Create an OpenAI response with `background: true`, drop the connection, retrieve by id (within
   the roughly 10 minute window when `store` is false).

## Incidents

None found for agents specifically (redelivery duplicates, hung workers, restart storms,
unattended runaway loops). Documented failure modes with vendor-stated causes (AgentCore blocked
ping thread, a `time_of_last_update` that defeats idle timeout, schedules pausing on retired
models) are Gotchas, not incidents. Unattended credential and spend failures route to 8.4, 8.5, 9.4.

## Named-idea candidates (author accepts or strikes)

- **Progress, not liveness.** A plain description, not a coinage.
- The responsibility split uses the standard cloud term, shared-responsibility boundary; no
  new name proposed.

## Carrier

Primary: the Listing Studio pipeline run as a queue worker (a bulk supplier-feed refresh through
the dispatcher: accept, return an id, deliver by webhook; batch size stated qualitatively). The
**repricer** is the always-on surface (per-run budget, capped restarts). The **category scout** is
the background-agent example. No first-hand production claim made.

## Code seam

A new listing-studio package is needed (none fits today; existing packages are `augmented_llm`,
`fan_out`, `routing`, `prompt_chaining`, `pricing`, `helpdesk_mcp`, `skills`). Candidate: a small
async-job package covering items 1 and 2: an endpoint that returns a job id, and a worker with a
lease heartbeat and an idempotency key, offline-testable with an in-memory queue. Managed-platform
sections stay prose with no code (beta, volatile, needs credentials).

## Sources

Anthropic: Claude Managed Agents overview and scheduled deployments
(platform.claude.com/docs/en/managed-agents/overview, .../scheduled-deployments); "Scaling Managed
Agents: Decoupling the brain from the hands" (anthropic.com/engineering/managed-agents); Claude
Code "Run Claude Code programmatically" (code.claude.com/docs/en/headless). OpenAI: background
guide (developers.openai.com/api/docs/guides/background) and data controls
(developers.openai.com/api/docs/guides/your-data). AWS: Lambda SQS configuration
(docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html), Lambda timeout, SQS
visibility timeout, AgentCore async docs. Temporal: worker deployments
(docs.temporal.io/production-deployment/worker-deployments). LangChain: docs.langchain.com/langsmith/deployments.
Cloudflare: developers.cloudflare.com/agents/. OWASP SSRF Prevention Cheat Sheet.

> **Verify before quoting:** Managed Agents details, budgets, Lambda and SQS ceilings, the 15
> minute AgentCore idle limit and the 10 minute Claude Code wait cap are quotable only against the
> live page with a "Last reviewed" date. Re-open the Anthropic engineering post and the Kubernetes
> pod-termination page before quoting identifiers or the default grace period. Pricing not
> collected; link live.

## Open questions for the author

1. Prose budget: Standard row (~2,000-2,800 words) with eight items, or split build-vs-rent out?
2. Where does the 9.1 line sit: is "single-run unattended hosting here, campaigns there" right?
3. Runtime taxonomy: name all four classes, or keep to provider and cloud platforms?
4. Approve a new listing-studio async-job package, or keep the chapter code-free?
5. Is a first-hand production callout available (queue worker, LangGraph server)? None claimed.

## Map review (Stage 1.5)

1. Thesis and budget missing: accepted; thesis and budget row added.
2. Litmus line missing: accepted; "your code decides" added.
3. Must-cover bloat: accepted; items 7 and 8 merged, Lambda ceiling folded into 1, now eight items.
4. Seam violations: accepted-modified; seams stated for 7.3, 8.4-8.6, 9.1; SSRF cut to one line; Young post dropped from Sources (belongs to 9.1).
5. Missing rollout versioning, backpressure, runtime classes: accepted; Temporal Worker Versioning, LangSmith Agent Server and Cloudflare Agents opened and cited; Kubernetes grace period not verified, so no figure given.
6. Progress supervision verdict mismatch: accepted; item 3 now Emerging.
7a. OpenAI retention: accepted; the guide gives no duration but the data controls page states roughly 10 minutes.
7b. HIPAA wording: accepted-modified; overview says Managed Agents is not HIPAA eligible at all, and ZDR is the only self-hosted exception.
7c. AWS six times visibility timeout: accepted; confirmed on the Lambda SQS page.
7d. Exit 143 not Claude-specific: rejected; the Claude Code headless page documents it for SIGTERM.
7e. 10 minute cap conflated with Bash ceiling: rejected; it is a separate background-wait default (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`). `--permission-prompts none` verified, `dontAsk` added.
7f. Lambda 1,800 s figure: accepted-modified; not re-verified, so the map says check the live page.
8. Alias sweep gaps: accepted-modified; LangSmith and Cloudflare added, "always-on" dropped, 12-Factor unopened so flagged.
9. Carrier drift and invented numbers: accepted; "Listing Studio pipeline", qualitative batch, new package stated.
10. Open questions missing: accepted.
11. Maturity misalignments: accepted; items split by Standard, Established, Emerging.
12. Cancellation and context-economy links: accepted; cancel added to item 1, 1.5 and 5.4 linked in item 4.
13. Named idea and Anchor 2: accepted; shared-responsibility term used, window note added.
14. URLs, author names, incident scope: accepted; full URLs and names added, incident note broadened; the engineering post is still to be re-opened.
15. Scaffolding phrases: accepted; removed.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Scope:** one chapter. Build vs rent stays inside it, as a section. The 9.1 seam is as the map states: hosting a single unattended run belongs here, campaigns belong to 9.1.
2. **Runtime classes:** describe all of them generically. Name a vendor only where a cited doc is opened.
3. **Code:** a new `listing-studio/jobs/` package, offline, with an in-memory queue:
   - an endpoint function that returns a job id;
   - a worker that takes a lease with a heartbeat;
   - an idempotency key so a redelivered job does not repeat its side effect;
   - a supervisor that reclaims a job whose heartbeat stalls.
4. **Verdict:** a headline of Established for the shapes and Emerging for the managed platforms, with the per-item split in prose.
5. **Figures:** drop the Lambda 1,800 s figure, the Kubernetes grace period and the 12-Factor aliases unless they are verified.
6. **No From-production callout.** No new alias line.

## Reconcile log (Stage 5)

**Prose critic**
1. Uncited "the half you keep causes incidents": fixed; clause cut, retention kept as the sharpest case.
2. "Bill with no ceiling" closer: fixed; cut.
3. "No platform takes those off your hands": fixed; scoped to "a host can enforce limits you set but cannot choose them for you".
4. Hook outruns the chapter: fixed; "can outlive".
5. "No natural point to kill": fixed; now "no safe point except between steps".
6. Grab-bag triggers paragraph: fixed; schedule defaults committed (skip missed runs unless every fire matters, skip or queue overlaps, never run two), webhook and SSRF folded into one sentence.
7. Overloaded durable-execution paragraph: fixed; split in two, Anthropic sentence made a full sentence, context aside scoped to "a long log ... can".
8. "Try all four": fixed; "covers three".
9. Gotchas restate the body: fixed; gotchas 1 and 2 merged with their observable symptoms, the restart gotcha now ends on a dead-letter alarm.
10. Straw-man "distrust the claim" sentence: fixed; cut.
11. Definition-paragraph list density: fixed; split, the "renews its claim" clause dropped.
12. Docstring re-teaches the prose: fixed in code and chapter; `submit` docstring trimmed, comment dropped, blocks re-synced.
13. Walkthrough lacks t=55/56/60: rejected; no single test drives that timeline (the tests cover the steps separately), so the walkthrough now says it is pieced together from the tests, and the diagram description no longer claims the tests drive it.
14. Alt text too long: fixed; cut to four sentences.

**Fact-checker**
1. [^5] does not support "loop = Workflow, call = Activity": fixed; Temporal's "Durable AI" page was opened and does not state the mapping either, so the clause was dropped. The pinned-Workflow and drained claims stay on [^5].
2. Deploy gotcha uncited: fixed; [^5] added, and the prompt failure mode is worded as inference ("can", "may").
3. "Own models only" and "session formats are provider-specific": softened to "session formats and supported models vary by host".
4. "Standard infrastructure": fixed; [^2] added.
5. "Contracts still moving": fixed; cut, beta status kept on [^9].
6. `--max-budget-usd` not defined on the headless page: fixed; the CLI reference was opened and added as [^14] (estimated spend, print mode only).
7. Durable Object and SIGTERM unglossed: fixed; both glossed.

**Cold reader**
1. Lease and idempotency key used before defined: fixed; glossed at first use.
2. At-least-once, dead-letter queue, poison message, backfill, Durable Object, pinned Workflow, checkpointer, exit 143: fixed; each glossed in place.
3. Lease sizing against the longest step: fixed; the heartbeat and pool paragraphs size the lease to the longest step when workers renew it, to the run when they cannot; the first gotcha says to renew per step.
4. Abandoned jobs reuse status "done": fixed in code; `reclaim_stalled` now sets status `abandoned`; test, chapter block and diagram label updated; pytest passes.
5. "Thin evidence" claims: fixed; the responsibility claim was cut, and the build-or-rent sentence is scoped to the sources cited (vendor documentation, none an independent comparison).
6. `Job`, `JobStore`, `LEASE_SECONDS` not shown: fixed; new `jobs-record` anchor shown in the chapter and wired into the doc-sync test.
7. Per-step heartbeat in the worker loop not shown: fixed by description (the loop heartbeats after each model or tool call and stops on `False`); no untested loop code added.
8. `HealthyBusy` semantics unclear: rejected; the agent's own `/ping` reports it, as the sentence says.
9. Same-name workers in `complete`: rejected; worker ids are unique by contract in the companion code.
10. Supervisor a process or a loop: fixed; "a loop on a timer".
11. `--permission-prompts none` unconfirmed: rejected; verified on the CLI reference, now cited as [^14].
12. Ecosystem paragraph dense: fixed; tightened.
13. "Idle timeout" and "jitter" unexplained: rejected; both are standard load-balancer and scheduler terms for this audience.
14. Missing reasoning steps (at-least-once to idempotency, "three times", "deployment makes it mandatory"): fixed; at-least-once is defined next to the risk it creates, and the walkthrough now says the third lapsed attempt sets status `abandoned`. The 7.3 pointer stays a pointer.
15. Alt text lacks a takeaway: fixed; the shortened alt text ends on who decides.
16. No supervisor-on-a-timer code, in-memory store only: rejected; the supervisor is described as a loop on a timer and durability is covered in prose; the companion code stays offline by design.
17. Companion repo and tests not linked: rejected; repo links are a site-wide convention outside this chapter.
18. Evidence sentence in "What it actually is": cut for budget; the build-or-rent paragraph keeps the scoped version.

**Alias line:** the chapter carries an `Also called:` line that includes "always-on agents", which 9.1 already uses and which the map review dropped. Left at its drafted value and put on the author's checklist rather than decided here.
