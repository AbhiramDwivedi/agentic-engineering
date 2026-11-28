# Reading Paths

> **The decision it resolves:** which chapters, in which order, for the problem you actually have?

The nav is organised by concept, from foundations out to the frontier. Most readers arrive with a
system to build or a decision to make, and for them the conceptual order buries the chapter they
need under five they can skim. Each path below picks the chapters for one job, puts them in an
order, and says in a sentence why each chapter sits where it does. The paths overlap on purpose:
the loop, the harness and evaluation turn up in most of them, because most systems need them.

Every path assumes the habit from [1.2 Who Decides?](../foundations/who-decides.md): for each
step, ask whether the model or your code makes the structural decision. If you read nothing else
first, read that chapter.

Chapters still in review are named here by number in plain text, and gain links as they land.

## By what you are building

### A chatbot or conversational assistant

1. [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md): Decide how much agency each
   turn needs before you pick a framework; the default is to sit near the workflow end.
2. [1.4 The Augmented LLM](../foundations/the-augmented-llm.md): The unit every turn runs on, a
   model call, a small tool set, and typed state.
3. [1.5 Context Engineering](../foundations/context-engineering.md): A multi-turn conversation is
   a window you curate turn by turn, so learn what belongs in it before you tune wording.
4. [2.1 Tool Use](../the-unit/tool-use.md): The model proposes actions; your code validates them
   and keeps the final say.
5. 5.1 State, Not Memory: A typed record and a checkpointer come before anything called memory.
6. 5.3 Memory: Only when the facts worth keeping cannot be listed in advance, and then through a
   tool you own.
7. 5.4 Compaction: Long conversations outgrow the window; mask old tool results before you
   summarise anything.
8. 6.3 Streaming & Agent UX: Render the interface from harness events, never from the model's
   prose.
9. 4.3 Human-in-the-Loop: Gate the actions you cannot take back, in code.
10. 4.6 Prompt Injection & the Lethal Trifecta: A chat surface takes untrusted input by
    definition; check which of the three properties each session holds.

### A RAG application

1. [1.5 Context Engineering](../foundations/context-engineering.md): Retrieval is one input to
   the window among several; this chapter sets the budget it competes for.
2. 5.2 Retrieval (RAG): Start with the cheapest thing that answers, and when the corpus does not
   fit, build the search as a system you own.
3. 6.1 Ingestion: What you retrieve is only as good as what you parsed, so put a code-owned
   boundary between the supplier's file and the model.
4. [2.2 Structured Output](../the-unit/structured-output.md): Answers that carry source ids need
   a schema, and their meaning still needs checking in your code.
5. 6.2 Synthesis: Assemble the deliverable from typed sections that keep their source ids.
6. 4.2 Evaluation: Build the case set from failures you have read before you tune chunking or
   ranking.
7. 4.6 Prompt Injection & the Lethal Trifecta: Retrieved text is untrusted input; read it as data.
8. 8.3 To Train or to Prompt: When someone proposes fine-tuning to fix a knowledge gap, this
   chapter says to retrieve it instead.

### A batch or document pipeline

1. [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md): Most pipelines belong at the
   workflow end; confirm yours does.
2. [3.1 Prompt Chaining](../composition/prompt-chaining.md): The gated sequence for fixed,
   code-checkable subtasks that must run unattended and fail predictably.
3. [2.2 Structured Output](../the-unit/structured-output.md): Every gate in the chain checks a
   typed object.
4. [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md): If the input carries a
   label, a dictionary routes it for zero tokens.
5. [3.3 Orchestrator-Workers](../composition/fan-out.md): Fixed parallel work goes in a literal
   and runs concurrently; reach for a planner only when the split varies.
6. 2.7 Decision Models: For high-volume, fixed-option judgments over one shared input, where a
   generated answer would cost more and take longer.
7. 6.1 Ingestion, then 6.2 Synthesis: The two ends of a document pipeline, typed elements in and a
   code-owned template out.
8. 7.1 Retry & Graceful Degradation: Retry only what could succeed, and give every write a key.
9. 7.3 Checkpointing: Save after every step and journal each effect before it happens, so an
   interrupted batch resumes without repeating work.
10. 8.4 Controlling Cost: Batch anything that can wait and cap every run in code.

### A coding-agent integration

1. 2.5 The Agent Loop: A coding agent runs this loop; know its named exits before you trust its
   "done".
2. 2.6 The Harness: The rules a coding agent must never break live here, enforced by code.
3. 9.6 Coding Agents: Bounded tasks with a check, a short instructions file, and the diff to the
   tests read first.
4. 9.4 Sandboxing: An agent that runs code it wrote needs a real OS or hypervisor backend and
   egress off by default.
5. 3.7 The Outer Loop: Write the verifier before the loop.
6. [2.3 Skills](../the-unit/skills.md) and [2.4 MCP](../the-unit/mcp.md): Knowledge and
   connectivity for the agent, and the trust boundary you cross with every server you did not
   write.
7. 4.6 Prompt Injection & the Lethal Trifecta: Issues, pages and files from outside are untrusted
   input to an agent that can write.

### An autonomous agent

1. [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md): Confirm the task needs this
   much agency; the chapter's default is to start simple.
2. 2.5 The Agent Loop: Every run ends with a named exit, and the step cap sits where the model's
   text cannot reach it.
3. 2.6 The Harness: Default to deny, and name the code behind each rule.
4. 3.6 Planning & Task Decomposition: Let the model write the plan and keep every other decision
   in code.
5. 3.7 The Outer Loop: A verifier in your code, out of the agent's reach, decides when a run is
   done.
6. 5.1 State, Not Memory, then 7.3 Checkpointing: A run that lasts hours needs state that
   survives a restart.
7. 4.3 Human-in-the-Loop: Irreversible actions still wait for a person.
8. 9.1 Long-Running Agents: Short sessions over a file your code owns, with acceptance checked in
   code.
9. 9.2 Multi-Agent: Last, and only when you can name what a second agent isolates.

## By role

### Securing an agent system

1. 4.6 Prompt Injection & the Lethal Trifecta: The threat model first. It covers untrusted input,
   sensitive data or systems, and the power to change state, and what to do where all three meet.
2. 2.6 The Harness: Where enforcement lives; a rule with only a prompt sentence behind it is a
   request.
3. 4.4 Guardrails & Safety: A code check on every claim your records can settle, a classifier
   only for the rest.
4. 9.4 Sandboxing: The execution boundary for anything that runs code.
5. 8.5 Locks, PII & Identity: Tenant binding from the authenticated request, and writes
   conditional on the version they were decided against.
6. [2.4 MCP](../the-unit/mcp.md): Treat tool descriptions and results from someone else's server
   as untrusted.
7. 4.3 Human-in-the-Loop: Save each pending action with a digest of its exact arguments.
8. 8.6 Governance & Compliance: An inventory row per system and a decision record per
   consequential action.

### A lead deciding whether to build

1. [1.1 It's Still Engineering](../foundations/its-still-engineering.md): When your code
   decides, the pattern is engineering your team already knows.
2. [1.2 Who Decides?](../foundations/who-decides.md): The test for telling a new pattern from a
   relabelled one, which is most of what a vendor pitch needs.
3. [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md): How much agency the problem
   needs, and why the default sits at the cheap, testable end.
4. [1.6 Do You Even Need a Framework?](../foundations/do-you-need-a-framework.md): The
   build-versus-buy call.
5. 4.2 Evaluation: Without a case set, nobody can say whether the system works.
6. 8.2 Which Model? and 8.4 Controlling Cost: Cost per passed case, and caps in code.
7. 9.2 Multi-Agent: The claim you are most likely to be sold, and its Contested verdict.
8. 9.7 Self-Improving Systems: Start with offline prompt optimization against your existing eval;
   self-modifying agents in production are Contested.
9. [The Anti-Patterns Catalog](anti-patterns.md) and the
   [Pattern Quick-Reference](quick-reference.md). Each is one page, for the review meeting.

## For the reader who already runs agents all day

### What do I still review?

You have stopped reading most of what the agent writes. These chapters cover the parts you should
keep reading.

1. 2.5 The Agent Loop: When the model says it is done, look at what it queued.
2. 9.6 Coding Agents: Read the diff to the tests before you read anything else.
3. 3.7 The Outer Loop: If your stop condition needs a model call to return a verdict, the chapter
   says you have an evaluator-optimizer loop, and its judge is what you are trusting.
4. 3.4 Evaluator-Optimizer: Self-correction with no external signal is Contested; know when your
   review loop is one.
5. 4.3 Human-in-the-Loop: Keep your attention for the actions you cannot take back.
6. 4.2 Evaluation: The failures you read are where the case set starts.
7. 9.7 Self-Improving Systems: When the system starts tuning its own prompts or skills, check that
   the evaluator and the promotion step stay outside the optimizer's reach.

### I'm running one unattended tonight

Work down the list before you leave. Each item is a question you can answer against your own
setup.

1. 2.5 The Agent Loop: Is there a step cap the model's text cannot reach, and does every exit get
   logged?
2. 2.6 The Harness: Which tools are left out of the session, and what do the deny rules say?
3. 9.4 Sandboxing: Is egress off by default, and is the filesystem isolated?
4. 8.4 Controlling Cost: Is there a per-run token and step cap in code?
5. 9.1 Long-Running Agents: Do budget and failure counts live in the file, so a relaunch cannot
   reset them?
6. 7.3 Checkpointing: If it dies overnight, can it resume without repeating an effect?
7. 7.2 Observer: Will a refusal or a truncated answer show up in the morning as an event?
8. 4.6 Prompt Injection & the Lethal Trifecta: Does any session tonight hold all three
   properties?

## The build path

The paths above are sorted by problem. This one sorts the chapters as a build: start from a bare
loop and add one capability per chapter until the result is a production system. The companion
code in `listing-studio/` grows along the same order, for the chapters whose grounding line names
the companion repo. It is a sequence to read and build against, not a book-length tutorial.

1. 2.5 The Agent Loop: The loop itself, branching on stop reason, with named exits and a step
   cap.
2. [2.1 Tool Use](../the-unit/tool-use.md): The model proposes a call; code validates it and
   decides whether to act.
3. [2.2 Structured Output](../the-unit/structured-output.md): Typed results for anything code
   consumes, validated for meaning after shape.
4. 2.6 The Harness: Deny rules, hooks and caps, each rule backed by code.
5. 4.4 Guardrails & Safety: Layered checks on output, ordered by cost.
6. 9.4 Sandboxing: An execution boundary once the agent runs code.
7. 3.7 The Outer Loop: A code-side verifier that decides when a run is done, with retries around
   it.
8. 4.2 Evaluation: A case set, graded by code first, so every later change can be measured.
9. 5.4 Compaction: Keeping long runs inside the window.
10. 5.1 State, Not Memory, then 7.3 Checkpointing: Typed state, saved after every step, with
    effects journalled before they happen.
11. 7.1 Retry & Graceful Degradation and 7.2 Observer: Retry what could succeed, and emit an event
    at every step boundary.
12. 8.1 Observability: The run as a trace tree, content off by default.
13. 8.7 Deployment & Runtimes: A job id for anything that might outlive a request, workers that
    earn their lease, and progress kept outside the worker so a crash costs a step.
14. 9.1 Long-Running Agents: Short sessions over a file your code owns, for jobs that outlast one
    window.

### Feature-to-chapter traceability

| What the build gains | Chapter |
|---|---|
| The loop, stop-reason branching, named exits, step cap | 2.5 The Agent Loop |
| Model-proposed tool calls, code-side validation | [2.1 Tool Use](../the-unit/tool-use.md) |
| Strict schemas, meaning checks after shape | [2.2 Structured Output](../the-unit/structured-output.md) |
| Deny rules, pre-tool hooks, caps | 2.6 The Harness |
| Cost-ordered output checks | 4.4 Guardrails & Safety |
| OS or hypervisor sandbox, default-deny egress | 9.4 Sandboxing |
| Verifier written before the loop | 3.7 The Outer Loop |
| Case set, code graders, a model judge only where code cannot see | 4.2 Evaluation |
| Tool-result masking, schema-bound summaries | 5.4 Compaction |
| Typed state, reducers, durable checkpointer | 5.1 State, Not Memory |
| Per-step saves, effect journal, dedupe at the receiver | 7.3 Checkpointing |
| Failure classifier, one retry owner, idempotency keys | 7.1 Retry & Graceful Degradation |
| Start, end and error events per step, fail-open sinks | 7.2 Observer |
| Trace tree with parent ids across processes | 8.1 Observability |
| Job ids, worker leases, capped concurrency and restarts | 8.7 Deployment & Runtimes |
| Progress file, acceptance checked in code, budget a relaunch cannot reset | 9.1 Long-Running Agents |

## How these paths relate to the nav

The conceptual nav stays the primary map. Each chapter carries its own maturity verdict and "who
decides" line, and these paths repeat neither. Terms that recur across paths are defined in the
[Glossary](glossary.md).
