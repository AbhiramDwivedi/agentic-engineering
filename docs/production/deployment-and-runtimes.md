# 8.7 Deployment & Runtimes

*An agent run can outlive the request that started it and can hang while looking healthy. Deploying one means deciding where the run's state lives, who notices when it stops making progress, and what you still own when a vendor hosts the loop.*

*Also called: agent deployment, agent runtimes, managed agents, always-on agents, async agents.*

## Why you'd reach for it

Put an agent behind an ordinary API endpoint and the first run that takes ten minutes finds your load balancer's idle timeout for you. The connection drops, the client shows an error, the user clicks again, and because the first run never knew its caller had gone, two runs are now spending tokens on the same job.

The second failure is quieter. The worker is up, it answers its health check, the dashboard is green, and the agent loop inside it is waiting on a tool call that will never return. Nothing restarts it, because nothing is wrong with the process. The run is stuck, and you learn about it from the customer.

Both failures come from treating an agent like a web handler. A handler finishes in milliseconds and holds nothing worth keeping. An agent run lasts minutes, makes paid calls, writes to real systems, and is safe to kill only between steps, which nothing in a web stack can see. So the deployment question is who holds the run's progress while it lasts, and what happens to that progress when the process holding it dies.

In Listing Studio, the pipeline that turns a supplier's feed into storefront pages, a merchandiser uploads a refreshed feed for a whole category. As one synchronous request the batch dies at the first gateway timeout; as a background thread in the web process it dies on the next deploy. Either way the merchandiser re-uploads and pays again for the products that had finished.

The fix is old and boring: accept the job, hand back an id at once, put the work on a queue, and let a worker hold it under a lease, a claim on the job that expires unless the worker keeps renewing it. Give every side effect an idempotency key, a unique id the receiving system uses to refuse a repeat, so a retried job cannot do its damage twice.

You need this when:

- a run can take longer than your gateway or serverless timeout;
- nobody is watching, because a schedule, a webhook or a CI job started the run;
- the run has side effects you cannot safely repeat, such as a publish, a price change or an email;
- you are weighing a hosted agent platform.

You do not need it for a chat turn that answers in a few seconds. Serve that synchronously, and stream it if a person is watching.

## What it actually is

Agent deployment is the code around the model's loop that decides how a run is started, where its progress is recorded, and what replaces it when it dies. There are three serving shapes: the caller waits for the answer, the caller watches a stream, or the caller gets a ticket and collects the result later. The ticket shape is a queue and a pool of workers, each holding a job under an expiring lease. Beside them sit a durable record of progress outside any one worker, and a supervisor, a loop on a timer that hands a job to a new worker when its lease lapses.

![Three serving shapes: wait, watch and ticket. A ticket job on worker A heartbeats once, then hangs; the supervisor requeues it when the lease lapses, and worker B finishes it with the side effect recorded once. A strip shows a job abandoned after three lapsed attempts. Only the model's loop is not your code.](deployment-and-runtimes-ticket.svg)

Your code makes every decision on that picture. The model decides what happens inside a run, and that loop is the payload a worker carries. The serving shape, the lease, the retry and the restart are familiar backend engineering. What is new is the payload: long, unpredictable in duration, and side-effecting partway through. That makes at-least-once delivery, where a queue may hand the same job out twice but never zero times, dangerous in a way it is not for a thumbnail resize.

The shapes are established practice. Queues with leases and dead-letter queues (a side queue where jobs that keep failing are parked) are standard infrastructure,[^2] and vendors now document the agent versions: OpenAI's background mode returns a response id you poll or cancel instead of holding a socket open.[^1] The hosted agent platforms are emerging; Claude Managed Agents, for one, is in beta.[^9]

Three neighbours get confused with this one. [7.3 Checkpointing](../reliability/stopping-gracefully.md) saves progress between steps inside one run's graph; this chapter covers the worker around it. [9.1 Long-Running Agents](../frontier/when-you-want-autonomy.md) covers campaigns that span many sessions; here the unit is one unattended run. [6.3 Streaming & Agent UX](../io-boundary/streaming-and-agent-ux.md) owns the streaming shape.

## How to do it

Pick the shape from the run's length and its audience: answer a short run in the request, stream one a person watches, and for anything else return a job id and delivers by polling or a webhook, with cancellation in the contract, because a caller who can start a ten-minute run needs a way to stop one. To try the provider version, create an OpenAI response with `background: true`, drop the connection, and fetch the result by its id; cancelling is a `POST` to its `/cancel` path, and cancelling twice is harmless.[^1]

The store holds the jobs, an index from idempotency key to job, and the side effects already done.

```python
LEASE_SECONDS = 30.0


@dataclass
class Job:
    job_id: str
    idempotency_key: str
    payload: dict
    status: str = "queued"  # queued | running | done | abandoned
    worker: str | None = None
    lease_expires: float = 0.0
    attempts: int = 0
    result: str | None = None


@dataclass
class JobStore:
    jobs: dict[str, Job] = field(default_factory=dict)
    by_key: dict[str, str] = field(default_factory=dict)
    effects: dict[str, str] = field(default_factory=dict)  # idempotency key -> recorded side effect
```

The endpoint records the job and returns its id. It never runs the work, and a client that retries with the same idempotency key gets the same job back.

```python
def submit(store: JobStore, payload: dict, idempotency_key: str) -> str:
    """The endpoint: enqueue and return a job id."""
    if idempotency_key in store.by_key:
        return store.by_key[idempotency_key]
    job = Job(job_id=uuid.uuid4().hex[:8], idempotency_key=idempotency_key, payload=payload)
    store.jobs[job.job_id] = job
    store.by_key[idempotency_key] = job.job_id
    return job.job_id
```

The worker takes a job under a 30-second lease and must renew it before it runs out, or the supervisor gives the job to someone else.

```python
def claim(store: JobStore, worker: str, now: float) -> Job | None:
    """The worker takes the oldest queued job under a lease that expires unless renewed."""
    for job in store.jobs.values():
        if job.status == "queued":
            job.status, job.worker = "running", worker
            job.lease_expires = now + LEASE_SECONDS
            job.attempts += 1
            return job
    return None


def heartbeat(store: JobStore, job_id: str, worker: str, now: float) -> bool:
    """Renew the lease. False means the job was reclaimed and this worker must stop."""
    job = store.jobs[job_id]
    if job.status != "running" or job.worker != worker:
        return False
    job.lease_expires = now + LEASE_SECONDS
    return True
```

Where you call `heartbeat` decides what it proves. From a timer thread it proves the process is alive. From the agent loop, after each model or tool call returns, it proves the run is moving: a loop stuck on a hung tool call stops renewing, its lease lapses, and the job goes to a worker that is not stuck. The loop stops the run as soon as `heartbeat` returns `False`. Supervise progress, not liveness. Size the lease to the longest single step plus headroom; a step that can run longer, such as a slow model call, needs a longer lease or a renewal from inside it. AWS Bedrock AgentCore draws the same line: its `/ping` separates `Healthy` from `HealthyBusy`, a session reporting `Healthy` for 15 minutes is terminated as idle, and a blocking entrypoint call can stall the ping and get a busy agent killed.[^4]

<details markdown>
<summary>The other half: completing once, and reclaiming stalled jobs</summary>

```python
def complete(store: JobStore, job: Job, worker: str, side_effect: str) -> bool:
    """Finish a job. The side effect is recorded once per idempotency key, however often it runs."""
    if job.worker != worker:  # lost the lease; a newer worker owns this job
        return False
    if job.idempotency_key not in store.effects:
        store.effects[job.idempotency_key] = side_effect
    job.status, job.result = "done", store.effects[job.idempotency_key]
    return True
```

```python
def reclaim_stalled(store: JobStore, now: float, max_attempts: int = 3) -> list[str]:
    """The supervisor: requeue running jobs whose lease lapsed. Past max_attempts, stop retrying."""
    reclaimed = []
    for job in store.jobs.values():
        if job.status == "running" and job.lease_expires < now:
            job.worker = None
            job.status = "queued" if job.attempts < max_attempts else "abandoned"
            reclaimed.append(job.job_id)
    return reclaimed
```

</details>

One run, pieced together from the companion tests:

1. The endpoint returns a job id. The client times out, retries with the same key, and gets the same id back.
2. Worker A claims the job at t=0, so its lease runs to t=30. At t=25 it finishes a step and heartbeats, and a supervisor pass at t=31 finds nothing to reclaim.
3. Worker A's loop hangs on a tool call and stops heartbeating. Once the lease lapses, the supervisor requeues the job.
4. Worker B claims it as attempt 2, finishes, and `complete` records the side effect against the idempotency key.
5. Worker A wakes. Its `heartbeat` returns `False` and its late `complete` is rejected, so the side effect is recorded once. A job whose third attempt lapses gets status `abandoned` and is not retried.

In production the idempotency key travels with the side effect itself, as a header on the publish call or a unique constraint on the row, so the downstream system can refuse the duplicate. [7.3 Checkpointing](../reliability/stopping-gracefully.md) owns that technique; deployment makes it mandatory, because a lease-based queue delivers at least once by design.

### From one worker to a pool

With a pool of workers, three settings matter. Size the queue's lease (SQS calls it the visibility timeout) to the longest step if workers renew it, or to the whole run if they cannot: AWS advises at least six times the function timeout when Lambda consumes the queue.[^2] Add a dead-letter queue so a person can inspect a job that keeps failing; AWS recommends a `maxReceiveCount` of at least 5 before a message moves there.[^2] And cap worker concurrency, because fifty workers started at once are fifty agents hitting one provider rate limit, a retry storm that [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md) then has to clean up.

On SIGTERM, the signal a platform sends to ask a process to stop, a worker should stop claiming, finish or checkpoint the current step, and release its lease within the grace period. Skip it and the step is lost: on SIGTERM a headless Claude Code run exits with code 143 (the conventional code for that signal) and leaves the turn in progress unfinished, with no result recorded.[^3] Let the platform's supervisor (systemd, Kubernetes, the queue lease) restart it, cap the restarts, and page when the cap is hit.

### Durable execution and deploys

A ten-minute run will eventually be running when you deploy. Either the old worker dies with the run's progress, or new code changes the prompt or tools under a run that started on the old one. The first is answered by keeping progress outside the worker. In Anthropic's managed agent service the session log sits outside the harness, so nothing in the harness needs to survive a crash, and a replacement resumes from the last recorded event.[^6] A framework checkpointer, which saves a graph's state after each step, gives you that half.

The second is answered by versioning. Temporal, a durable workflow engine, calls a run a Workflow and lets you pin it: a pinned Workflow is guaranteed to complete on a single Worker Deployment Version, and an old version counts as drained once its pinned runs close.[^5] A long log replayed raw into the model can overflow its window; [1.5 Context Engineering](../foundations/context-engineering.md) and [5.4 Compaction](../knowledge/compaction-and-the-window.md) cover what goes back in.

### Who starts the run

Prefer push events over polling; poll only with a cursor and a cap per pass. A schedule needs two explicit policies. Skip a run missed while you were down, and backfill (run missed fires late) only when every fire matters, as with a ledger. Skip or queue a fire that arrives while the last run is still going, and never run two at once. Anthropic's scheduled deployments take a cron expression and an IANA timezone, add jitter, and do not backfill triggers missed while paused.[^8] Check the signature on every inbound webhook, and allow-list any callback URL a client gives you, because that callback is a server-side request forgery door.[^7] The mechanics belong to [8.5 Locks, PII & Identity](locks-pii-identity.md) and [9.4 Sandboxing](../frontier/sandboxing.md).

### Nobody at the terminal

A run started by a schedule or a CI job has nobody to answer a permission prompt, so the deployment answers four questions up front: who approves a risky action (the safe default is deny), what the run may leave behind (a pull request rather than a push to main), how much a stuck run can spend, and how you learn it finished. Claude Code's headless mode covers three. `claude -p "..." --output-format json` reports `total_cost_usd` and exits non-zero on failure; `--permission-prompts none` denies anything that would prompt and carries on; `--max-budget-usd` stops the run once its estimated spend reaches a cap, in print mode only.[^3][^14] Run it with `--output-format stream-json` and a forbidden tool, then read `permission_denials` in the final result.

> **In Listing Studio.** The repricer, which adjusts prices against competitors within rules, runs as a supervised worker with a per-run spend ceiling, a restart cap that ends in a page, and an idempotency key on every price change. Its heartbeat fires only when a pricing step completes, because a wedged repricer renewing a liveness heartbeat would leave stale prices on the storefront.

## Ecosystem & tooling

You can rent most of the above from four classes of host. Provider agent services run the loop, the sandbox and the session store: Claude Managed Agents is the full form, in beta behind the `managed-agents-2026-04-01` header,[^9] and OpenAI's background mode the thin one.[^1] Cloud agent platforms such as Bedrock AgentCore host an agent you wrote, in any framework and against any model.[^13] Framework agent servers such as LangSmith Agent Server deploy a graph built in that framework.[^11] Cloudflare Agents makes each agent a Durable Object, one addressable instance with its own durable storage.[^12]

The vendor takes the loop, the sandbox, the session store and the restarts. You keep the system prompt, the tools and their permissions, the session lifecycle, the per-run budget, the output and the trust boundary. That is the familiar cloud shared-responsibility boundary, and retention is the sharpest case of what stays with you. Managed Agents transcripts persist until you delete them, and the service is not eligible for zero data retention (self-hosted excepted) or HIPAA.[^9] OpenAI's background mode stores response data for roughly ten minutes so it can be retrieved, even when `store` is false.[^10] [8.6 Governance & Compliance](governance-and-compliance.md) has the mechanics.

Define the agent once and version it, then start one session per run, so runs stay comparable. Keep the spend ceiling ([8.4 Controlling Cost](controlling-cost.md)) and the identity each run acts as in your own code.

Build or rent trades operational load against control, access to raw state and traces, and portability, since session formats and supported models vary by host. Data residency can force the answer. Write the queue, the lease and the supervisor once yourself, about the size of the listings above, before you rent them, so you know exactly what you hand over. The sources here are vendor documentation and none compares the two independently, so treat a vendor's claim that one is better as marketing until your own load has tested it.

## Gotchas

1. **A heartbeat that proves the wrong thing.** A liveness probe passes while the loop waits forever on a tool, and an unrenewed lease shorter than the run hands every long job to a second worker. Renew it per step. The symptoms are a trace whose last span is a tool call minutes old, and duplicate publishes spaced one visibility timeout apart.

2. **A keep-alive that defeats the idle timeout.** On AgentCore, a ping handler that sets `time_of_last_update` to now on every ping resets the idle clock, so sessions run to their maximum lifetime.[^4] A heartbeat that always says "busy" does the same to your own supervisor.

3. **A deploy changes the code under a running job.** A run that started on yesterday's prompt can finish on today's, and its output may match neither. Pin in-flight runs to the version that started them, or drain the old workers before you cut over.[^5]

4. **Unbounded restarts.** A poison message, a job that crashes every worker that takes it, restarts forever and burns money. Cap restarts, route the job to the dead-letter queue, and alarm on its depth.

5. **The schedule outlives its model.** When a scheduled deployment names a retired model, Anthropic's service records a failed run and pauses the schedule.[^8] Watch the schedule's state as well as its output.

## In short

Return a job id for anything that might outlive a request, and make each worker earn its lease by finishing steps. Put an idempotency key on every side effect, cap concurrency and restarts, and keep progress outside the worker so a deploy or a crash costs a step, not the run. Build that once, then rent if the operating load is what you want rid of, and keep the budget, the permissions, the retention and the trust boundary in your own code, because a host can enforce limits you set but cannot choose them for you.

<small class="chapter-meta">**Maturity: Established (the shapes) / Emerging (managed platforms)** (sync, stream and async with leases and idempotency are settled; the hosted agent platforms are young and partly in beta) · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: OpenAI, "Background mode." <https://developers.openai.com/api/docs/guides/background>
[^2]: AWS, "Configuring an Amazon SQS queue to use with Lambda." <https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-configure.html>
[^3]: Anthropic, "Run Claude Code programmatically." <https://code.claude.com/docs/en/headless>. `permission_denials` is documented for `stream-json` output.
[^4]: AWS, "Handle asynchronous and long running agents with Amazon Bedrock AgentCore Runtime." <https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-long-run.html>
[^5]: Temporal, "Worker Versioning." <https://docs.temporal.io/worker-versioning>. See also "Worker deployments," <https://docs.temporal.io/production-deployment/worker-deployments>.
[^6]: Martin, L., Cemaj, G., and Cohen, M., "Scaling Managed Agents: Decoupling the brain from the hands," Anthropic Engineering (8 April 2026). <https://www.anthropic.com/engineering/managed-agents>
[^7]: OWASP, "Server-Side Request Forgery Prevention Cheat Sheet." <https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html>
[^8]: Anthropic, "Scheduled deployments," Claude Managed Agents documentation. <https://platform.claude.com/docs/en/managed-agents/scheduled-deployments>. On Claude Platform on AWS the deployment stays active and records rejected runs instead of pausing.
[^9]: Anthropic, "Claude Managed Agents overview." <https://platform.claude.com/docs/en/managed-agents/overview>
[^10]: OpenAI, "Data controls in the OpenAI platform." <https://developers.openai.com/api/docs/guides/your-data>
[^11]: LangChain, "LangSmith deployments." <https://docs.langchain.com/langsmith/deployments>
[^12]: Cloudflare, "Agents." <https://developers.cloudflare.com/agents/>
[^13]: AWS, "Host agent or tools with Amazon Bedrock AgentCore Runtime." <https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html>
[^14]: Anthropic, "CLI reference," Claude Code documentation. <https://code.claude.com/docs/en/cli-reference>. Defines `--max-budget-usd` and `--permission-prompts`.

## See also

- [7.3 Checkpointing](../reliability/stopping-gracefully.md), for step-level progress and the idempotency-key technique.
- [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md), for retries under rate limits.
- [6.3 Streaming & Agent UX](../io-boundary/streaming-and-agent-ux.md), for streaming and reconnects.
- [8.1 Observability](seeing-inside.md), for the progress signals a supervisor reads.
- [8.4 Controlling Cost](controlling-cost.md), for per-run budgets and spend ceilings.
- [8.6 Governance & Compliance](governance-and-compliance.md), for retention and data handling on hosted runtimes.
- [9.1 Long-Running Agents](../frontier/when-you-want-autonomy.md), for multi-session campaigns.
- [9.4 Sandboxing](../frontier/sandboxing.md), for the execution boundary a hosted runtime provides.

## Further reading

- [OpenAI, "Background mode"](https://developers.openai.com/api/docs/guides/background), the ticket shape as a provider API.
- [AWS, "Handle asynchronous and long running agents with Amazon Bedrock AgentCore Runtime"](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-long-run.html), a busy-versus-idle health contract.
- [Temporal, "Worker deployments"](https://docs.temporal.io/production-deployment/worker-deployments), on deploys under running work.
- [Anthropic, "Scaling Managed Agents"](https://www.anthropic.com/engineering/managed-agents), on separating the loop, the sandbox and the session log.
- [Anthropic, "Run Claude Code programmatically"](https://code.claude.com/docs/en/headless), the flags for an unattended run.
