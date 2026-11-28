# The Hardening Checklist

> **The decision it resolves:** what turns a working demo into a system that survives production?

A demo runs once, on a good day, with someone watching. Production runs the same pipeline
over and over, against providers that time out, workers that crash mid-step, and tenants who
share a database. In nearly every fix below, your code decides. The exceptions are where 8.4
lets the model escalate through a tool, and where in 9.7 the model proposes and your code
promotes. They are the rails every pattern leans on and no pattern owns, so pattern chapters point here instead
of re-teaching them.

Each entry gives the concern, the maturity verdict copied from the chapter that argues it, and
the checks that chapter ends on. Read each check as a question for a design review: *does our
system do this yet?* The chapters sit under [Reliability](../reliability/index.md) and
[Operating in Production](../production/index.md), with the last entry from
[The Frontier](../frontier/index.md).

*Last reviewed: 2026-11*

## At a glance

| Concern | Chapter | Maturity |
|---|---|---|
| Retry and graceful degradation | [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md) | Standard |
| The observer rule | [7.2 Observer](../reliability/a-silent-failure-is-worse.md) | Standard |
| Checkpointing and resumption | [7.3 Checkpointing](../reliability/stopping-gracefully.md) | Established (per-step checkpointing, durable-execution engines) · Emerging (agent-safe replay and rollback) |
| Observability and tracing | [8.1 Observability](../production/seeing-inside.md) | Established |
| Token and cost economics | [8.4 Controlling Cost](../production/controlling-cost.md) | Established |
| Locks, tenancy and identity | [8.5 Locks, PII & Identity](../production/locks-pii-identity.md) | Emerging |
| Deployment and runtimes | 8.7 Deployment & Runtimes | Established (the shapes) / Emerging (managed platforms) |
| Held-out gates for self-improvement | 9.7 Self-Improving Systems | Emerging / Contested |

The verdicts carry their chapters' qualifiers. In 7.1, idempotency keys on agent tools and
cross-provider failover are Emerging. In 7.2, the event schema and hook-failure handling are
Established and OpenTelemetry alignment is Emerging. In 8.1, the OpenTelemetry GenAI conventions
and online evals are Emerging. In 8.4, the mechanisms are vendor-documented and the savings
figures vendor-reported; learned cascades are Emerging, and semantic caching and advisor
pairings are Contested. In 8.5, locks and tenant isolation are standard, while delegation and
per-run credentials for agents are not settled. In 8.7, sync, stream and async with leases and
idempotency are settled, and the hosted agent platforms are young and partly in beta. In 9.7,
eval-driven prompt tuning is Established, prompt optimizers and skill, context and harness
editing are Emerging, and self-modifying agents in production are Contested.

## Retry and graceful degradation

**Chapter:** [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md) · **Maturity: Standard**

Sort every failed call before acting on it. Retry what could succeed on a second try, fall back
to another model when the retries run out, and stop with a clear error when nothing you resend
will change the outcome.

1. A classifier sits in front of every model and tool call. A transient failure is retried with
   backoff inside a budget, a timeout only when the call is safe to replay, and a terminal
   failure stops the run and says why.
2. One layer owns retry, and the others are turned off.
3. Every write carries an idempotency key derived from the run and the step, so a replayed call
   returns the first result instead of writing a price twice.
4. A timeout is treated as an unknown outcome. Partial output from a streamed call that writes is
   discarded.
5. Every degraded answer is labelled and logged, and the fallback rungs run on purpose in tests.
6. Failover to another provider happens only if your application owns the message history, and
   the first calls after it are expected to pay for uncached input.
7. A circuit breaker per provider or per model stops retrying into an outage.
8. Errors fed back to the model are capped, and the classifier passes on only errors the model
   could act on. A spend cap or a missing permission stops the run.

## The observer rule

**Chapter:** [7.2 Observer](../reliability/a-silent-failure-is-worse.md) · **Maturity: Standard**

Every step reports when it starts and how it ended, to listeners that can see the run but never
change it, so a step that ends badly says so even when it did not raise.

1. Every step emits `start`, then `end` or `error`.
2. The outcome on `end` comes from the stop reason and whether any text came back. A refusal, a
   truncation or an empty turn is a finished step with a bad result, never a success.
3. Every sink fails open, and slow sinks sit behind a bounded queue that counts its drops.
4. Retries and gates read the step's result, not the events.
5. You have checked what your framework does when a hook throws, and whether its hooks cover the
   failure branch at all. Where they do not, you wrap the run yourself.
6. Events stay small: ids, kind, outcome, timestamp, error class.
7. Sinks are treated as data stores. Raw exceptions and prompts stay out of the user's view, and
   anything an operator needs beyond the event's fields goes through redaction first.
8. Each sink has a heartbeat or a counter that something else watches.

## Checkpointing and resumption

**Chapter:** [7.3 Checkpointing](../reliability/stopping-gracefully.md) · **Maturity: Established (per-step checkpointing,
durable-execution engines) · Emerging (agent-safe replay and rollback)**

Save the run's state after every step so a cancelled or crashed run resumes where it stopped,
and journal each side effect before it leaves the process, because the step that was in flight
will run again.

1. A durable saver writes after every step. The in-memory saver is for tests only.
2. Each step that touches the world journals its call and key before the effect, and sends it to
   a receiver that dedupes and, better, compares parameters.
3. On resume, prices, tokens and approvals are re-checked against the world as it is now.
4. When the outcome of a send is unknown, the run asks the receiver for the request's status and
   stops for an operator if it cannot say. It never mints a new key to get past the doubt.
5. You know how long your receiver keeps idempotency keys, and a pause longer than that is
   treated as an unknown send.
6. A checkpoint that may hold injected text is rolled back to a clean one, not resumed. The
   journal sits outside what a rollback restores.
7. Checkpoints hold references to large blobs, not the blobs, and are pruned on a schedule tied
   to the run's lifecycle.
8. A durable-execution engine comes in when something outside your process has to notice a dead
   worker and restart it.

## Observability and tracing

**Chapter:** [8.1 Observability](../production/seeing-inside.md) · **Maturity: Established**

Trace and monitor non-deterministic runs so you can debug what the model did.

1. Every run is a trace tree: a root span for the run, a child for each model call and tool
   call, with parent ids carried across every process boundary.
2. Every span carries ids, model names, token counts and finish reasons.
3. The model that answered is recorded beside the model requested, and the root span carries a
   prompt or code version.
4. Content is off by default and scrubbed in your own process whenever it is turned on. A flagged
   slice of runs with content captured, or content stored by reference, is set up before the
   first incident.
5. Spans are emitted as OTLP against a pinned version of the GenAI conventions, with the
   attribute names kept in one module.
6. Sampling keeps every failure.
7. A failing exporter or redaction hook costs the span and lets the run finish, and a test proves
   it.

## Token and cost economics

**Chapter:** [8.4 Controlling Cost](../production/controlling-cost.md) · **Maturity: Established**

An agent's bill is set by how many calls its loop makes and how much context each one re-sends.
Make the repeated prefix cheap, the waiting work cheap, the easy calls cheap, and the total
bounded.

1. Static content comes first in the prompt, and the cache fields in your usage logs show hits.
   Nothing unstable, such as a timestamp, JSON with unstable key order or a reordered tool list,
   sits in the cached prefix.
2. Anything that can wait is batched.
3. `max_tokens` is set generously. A response cut off by the cap is a failed attempt you paid
   for.
4. Every run's tokens and steps are capped in code.
5. Per-user and per-tenant budgets live in a shared store keyed by identity, backed by the
   provider's workspace spend cap and a tested kill switch.
6. A cascade is tried only on a step where a cheap check can tell good answers from bad, and is
   kept only if cost per passed case drops on an eval.
7. Semantic answer caching and advisor pairings stay off until your own numbers argue for them.

## Locks, tenancy and identity

**Chapter:** [8.5 Locks, PII & Identity](../production/locks-pii-identity.md) · **Maturity: Emerging**

A model pause turns a short lock into a stall or a stale write, context copies personal data
into stores nobody scoped, and a broad credential lets injected text spend your authority. Each
is fixed by a check in your code at a boundary the model cannot argue with.

1. No model call runs inside a transaction. Each write is conditional on the version it was
   decided against.
2. A step that must own a record across several calls takes a fenced lease, and the store checks
   the fence token.
3. Locks are released, so a large catalog cannot exhaust the server's lock table.
4. The tenant is bound from the authenticated request and enforced by the database. The
   application connects as a role that cannot bypass row-level security.
5. Personal fields are dropped before they enter context, and any detector is a second layer.
   Placeholder round trips are validated and fail closed.
6. Each run gets a delegated credential for one tenant and one task, with a short life and a
   tested revocation path.

## Deployment and runtimes

**Chapter:** 8.7 Deployment & Runtimes · **Maturity: Established (the shapes) / Emerging
(managed platforms)**

An agent run can outlive the request that started it and can hang while looking healthy.
Deploying one means deciding where the run's state lives, who notices when it stops making
progress, and what you still own when a vendor hosts the loop.

1. Anything that might outlive a request returns a job id.
2. Each worker earns its lease by finishing steps, and renews it per step. A liveness probe that
   passes while the loop waits on a tool proves nothing.
3. Every side effect carries an idempotency key.
4. Concurrency and restarts are capped. A job that crashes every worker that takes it goes to the
   dead-letter queue, and an alarm watches that queue's depth.
5. Progress lives outside the worker, so a deploy or a crash costs a step, not the run.
6. In-flight runs stay pinned to the version that started them, or the old workers drain before
   the cutover.
7. A heartbeat or keep-alive cannot report "busy" forever and defeat the idle timeout.
8. Scheduled runs are watched for their state as well as their output, since a schedule that
   names a retired model can pause.
9. When a vendor hosts the loop, the budget, the permissions, the retention and the trust
   boundary stay in your own code. A host can enforce limits you set but cannot choose them.

## Held-out gates for self-improvement

**Chapter:** 9.7 Self-Improving Systems · **Maturity: Emerging / Contested**

Systems that improve their own prompts, skills, memory, code or harness are graded by what is
being improved and by whether the gains survive a held-out check. The model proposes; your code
promotes.

1. Optimization runs against your existing eval, with an explicit selection set and a sealed
   test set. A gain counts only when it holds on data the optimizer never selected on.
2. The evaluator and the promotion step stay outside the optimizer's reach.
3. The winning prompt is reviewed as a diff before it ships.
4. The cost of population times iterations is budgeted before the run starts.
5. The selection set is refreshed on a schedule as live inputs drift.
6. The rollback plan covers what the change touched while live, since reverting a prompt does
   not unpublish the listing copy it wrote.
7. Agents that rewrite their own code and harness stay out of production until someone publishes
   a production replication.

## Where the concerns meet

The entries share failure paths, and their chapters cross-reference each other at these seams:

- **The idempotency key.** 7.1 and 7.3 both key each write by the run and the step, because a
  retry and a resume both send one call twice and need the same effect fencing.
- **Owning the message history** is what lets 7.1 fail over to another provider; see
  [5.1 State, Not Memory](../knowledge/state-not-memory.md).
- **Events and spans** cover the same steps. 7.2 says a step ended badly, 8.1 traces what it
  did, and 7.2's events are sampled and expired downstream as 8.1 describes.
- **Stored data** collects in observer sinks (7.2), trace content (8.1) and checkpoints (7.3).
  The first and last defer to 8.5 for what may be stored at all; 8.1 scrubs content in your own
  process.
- **The same key, a third time.** 8.7 puts an idempotency key on every side effect too,
  because a lease that expires mid-run hands the job to a second worker.
- **Budgets need identity.** The per-user budget in 8.4 is keyed by the identity 8.5 binds.

The [Anti-Patterns Catalog](anti-patterns.md) lists the failures these checks prevent, among
them the silent failure.
