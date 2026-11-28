# Decision Frameworks

> **The decision it resolves:** the recurring "which should I pick?" calls, in one place.

This page collects the site's decision guides for quick reference. The core four are workflow or agent,
framework or raw SDK, which model, and train or prompt. Six more sit beside them: whether to
send a judgment to a decision model, when to add a second agent, state or memory, how to
route, whether to build or rent the runtime, and whether to let a system improve itself. Each entry gives the default, what moves you off it, the verdict from the chapter's trust
line, and the chapter that argues it in full.

## At a glance

| The call | Start here | Maturity | Chapter |
|---|---|---|---|
| Workflow or agent? | a fixed path, with agency only in the step that needs judgment | split (see below) | [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md) |
| Framework or raw SDK? | a framework, unless the job is small or you must own every layer | Standard | [1.6 Do You Even Need a Framework?](../foundations/do-you-need-a-framework.md) |
| Which model? | a model per step, the cheapest that passes that step's cases | Established | 8.2 Which Model? |
| Train or prompt? | prompt and context first, with the eval written before either | Established | 8.3 To Train or to Prompt |
| Decision model or generation? | a decision model for high-volume, fixed-option judgments | Emerging | 2.7 Decision Models |
| One agent or several? | one agent | Contested | 9.2 Multi-Agent |
| State or memory? | typed state first | Established | 5.1 State, Not Memory |
| Dispatch or routing? | a dictionary when the input already carries a label | Standard (static dispatch) · Established (LLM routing) | [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md) |
| Build or rent the runtime? | build the queue, lease and supervisor once, then rent if the operating load is what you want rid of | Established (the shapes) / Emerging (managed platforms) | 8.7 Deployment & Runtimes |
| Let it improve itself? | offline prompt optimization against your existing eval | Emerging / Contested | 9.7 Self-Improving Systems |

## The core four

### Workflow or agent?

**The question to ask** is how much agency a given step needs, which gets further than asking
whether the system is an agent. Agency runs on a spectrum, from your code deciding the flow to
the model deciding it.

**Default:** sit as far toward the workflow end as the task allows. A fixed path is cheaper and
easier to test. For most production work the answer is a hybrid: a deterministic pipeline with a
small bounded-agency step, a sub-agent with two to four tools, dropped into the one place that
needs judgment. Listing Studio has this shape: the graph is fixed, and the clarify-attributes
step grades its own questions and loops.

**Turn the dial up when** the task is open-ended, the steps cannot be listed up front, the path
depends on inputs you cannot predict, or a predetermined workflow falls short too often.

**Turn it back down when** the agent's outputs are stable enough to write as rules, its cost
outruns the value of its autonomy, or you spend more time fixing it than it saves.

**Maturity: split.** Start simple and sit near the workflow end is Standard to Established; "go
autonomous for everything" is Contested; the hybrid is Established to Emerging. The far end of
the spectrum, a loop that plans and acts on its own, is 9.1 Long-Running Agents.

Chapter: [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md)

### Framework or raw SDK?

**Default:** assume you will want a framework and make it prove otherwise. The plumbing (state,
checkpointing, retries, streaming, observability) is real, and if you skip the framework you
will rebuild it under deadline.

**Weigh four axes, with judgment rather than a points total:**

- How much of the plumbing would you rebuild, and would you rebuild it well? This one carries
  the most weight.
- How far is your control flow from a single linear pass? Branches, loops, parallel fan-out and
  handoffs favor a framework.
- Is this your product or infrastructure? The prompts, tools and guardrails stay yours; the loop
  and the state store are infrastructure.
- What does your team already know, and how much lock-in can you tolerate? A portable library is
  a smaller bet than a managed runtime that owns your execution.

**Stay on the SDK when** the job is a single agent calling one or two tools, a throwaway, or a
hard requirement to own every layer.

**Which framework:** LangGraph is the chapter's default for graph-shaped, long-running,
control-heavy production work; CrewAI gets a fast multi-agent prototype running sooner. Let the
four axes make the pick; a demo that happened to use one settles nothing.

**Maturity: Standard** (the build-vs-buy discipline and the cargo-cult caution).

Chapter: [1.6 Do You Even Need a Framework?](../foundations/do-you-need-a-framework.md)

### Which model?

**Default:** choose per step, by your own cases. Put a model name on each step in one config
table, give each step its own cases (a prompt plus the answer you expect), and let a candidate
take a step only when it wins on those cases at a cost per passed case you are willing to pay.
In Listing Studio, the categorize step picks one label from a list the code already holds, and
the write-copy step drafts open prose; one product-wide model would price both at the harder
step's rate.

**Reach for per-step choice when** steps differ in difficulty, volume makes price matter, you
depend on a hosted model the vendor will retire, or a successor ships and someone asks whether
to move.

**Skip it for** a single-call prototype with no cases yet: pick the cheapest model that handles
the task and come back at the second step or the first user.

**Keep in place:** pinned, dated model IDs, every retirement date on the calendar from the day
you adopt a model, and the replacement run through the same comparison early in the notice
window. A public leaderboard measures someone else's cases.

**Maturity: Established** (vendor-documented method and retirement policies; tier routers and advisor pairings are
Emerging).

Chapter: 8.2 Which Model?

### Train or prompt?

**Default:** fix it with the prompt and the context, and write the eval before you touch either.
The decision runs as a diagnosis followed by a ladder.

**Diagnose the failure first:**

| The failure is | The lever |
|---|---|
| knowledge (the model lacks facts) | retrieval; training will not hold the facts reliably and goes stale when they change |
| behavior (tone, task execution, format) | climb the ladder: eval, prompt, context, prompt optimization, then training |
| cost (a large model is doing a narrow job) | a smaller model, run untuned against the eval before you tune it |
| format alone | structured output, which holds the reply to a schema, before any training ([2.2 Structured Output](../the-unit/structured-output.md)) |

**Climb only when the eval says so.** Re-run it at each rung; stop when it passes, and move up
only when the cheaper rung has plateaued. When you reach the weights, start with supervised
fine-tuning on a modest curated set.

**Budget it as recurring.** Whatever you train, put its retraining on the calendar next to the
base model's retirement date.

**Maturity: Established** (the prompt-then-tune ladder is a settled decision framework; RFT,
RLVR and prompt optimizers are Emerging, LoRA parity and small-beats-frontier Contested).

Chapter: 8.3 To Train or to Prompt. Choosing the model comes first (8.2 Which Model?); tuning
changes the model you already picked.

## Six more that recur

### Decision model or generation?

Use a decision model, which returns a probability for each of a fixed set of options and writes
no text, for high-volume, fixed-option judgments over one shared input, where code acts on the
answer. Generate with structured output when the judgment needs its reasoning written down, the
answer is not from a list you can write ahead of time, or the task is a trajectory of many steps.
Keep the threshold, the abstain path and the escalation path in your own code, and set the
threshold from a calibration check on your own labeled data.

**Maturity: Emerging** (a product category a few months old, with vendor-reported speed and
calibration; code-side thresholds are standard, post-hoc calibration established). Chapter: 2.7
Decision Models.

### One agent or several?

Default to one. Add a second only when you can name what it isolates: a context window the first
cannot hold, a permission the first should not have, or a team that owns the second's behaviour.
Call it as a tool and keep control where it was. Hand off only when the rest of the conversation
belongs to the other agent, and decide in code what crosses and how many hops are allowed.

**Maturity: Contested** (the umbrella claim is hyped and the evidence is task-dependent;
specialist-as-tool and read-only subagents are Established, handoffs and teams Emerging).
Chapter: 9.2 Multi-Agent.

### State or memory?

State first. Give every multi-step agent a typed record, a reducer on every field more than one
step writes, and a durable checkpointer. Before anyone adds a memory layer, delete the store,
start a fresh run tomorrow, and see whether anything behaves differently. If nothing does, the
store was holding state, and a field or a reducer would have served better than a vector
database. Build memory when the answer is yes; that is 5.3 Memory.

**Maturity: Established** (typed state is Standard; the line between state and memory is not
settled vocabulary, and progress files are Emerging). Chapter: 5.1 State, Not Memory.

### Dispatch or routing?

Read the input before you pick the mechanism. A reliable label already present means a
dictionary, with an explicit deny branch for unknown types. Unlabelled input with few, stable,
latency-sensitive categories means an embedding router. Fuzzy or shifting categories mean an LLM
call, with `unclear` kept in the taxonomy, low confidence escalated to a person, and a labelled
eval set in place before customers see it. The full table of what picks the path, and when, lives
in the [quick-reference](quick-reference.md).

**Maturity: Standard (static dispatch) · Established (LLM routing).** Chapter:
[3.2 Routing & Dispatch](../composition/the-router-that-isnt.md).

### Build or rent the runtime?

Whichever you choose, the shape is the same: return a job id for anything that might outlive a
request, put an idempotency key on every side effect, cap concurrency and restarts, and keep
progress outside the worker so a deploy or a crash costs a step and leaves the run intact. Write
the queue, the lease and the supervisor once yourself, so you know exactly what you would hand
over. Then rent if the operating load is what you want rid of. Renting trades that load against
control, access to raw state and traces, and portability, and data residency can force the
answer. A host takes the loop, the sandbox, the session store and the restarts; the budget, the
permissions, the retention and the trust boundary stay in your code.

**Maturity: Established (the shapes) / Emerging (managed platforms)** (sync, stream and async
with leases and idempotency are settled; the hosted agent platforms are young and partly in
beta). Chapter: 8.7 Deployment & Runtimes.

### Let it improve itself?

Start with offline prompt optimization against the eval you already have, with an explicit
selection set, a sealed test set, and the winning prompt reviewed as a diff. Move to skill or
playbook evolution only when you have an execution-based check and a pruning habit. Keep agents
that rewrite their own code and harness in the lab until someone publishes a production
replication. On every rung the evaluator and the promotion step stay outside the optimizer's
reach, and a gain counts only when it holds on data the optimizer never selected on.

**Maturity: Emerging / Contested** (eval-driven prompt tuning is Established; prompt optimizers
and skill, context and harness editing are Emerging; self-modifying agents in production are
Contested). Chapter: 9.7 Self-Improving Systems.

## How to use this page

Take the default unless you can name the trigger that moves you off it. If you cannot name one,
the default holds. If you can, open the chapter before you build: the entry here is the short
version, and the chapter covers how the non-default choice goes wrong.
