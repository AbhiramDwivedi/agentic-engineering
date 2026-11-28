# State of Play, 2026

> **The decision it resolves:** what does the fast-moving landscape look like *right now*?

*Last reviewed: 2026-11.*

This page is a dated snapshot of the parts of agentic engineering that are still moving: models,
frameworks, harnesses and protocols. It compiles the **Emerging** and **Contested** verdicts from
the chapters into one place, with the fact that earns each verdict and the month that chapter was
last reviewed. It adds nothing the chapters do not argue. When a chapter is re-reviewed, its rows
here are regenerated from it, and a verdict that moves is logged in [Changes](changes.md).

Read the Reviewed column before the verdict. A row dated 2026-06 says what was true in June, and in
this part of the field five months is long enough for a spec revision or a model retirement.
Verdicts are copied from each chapter's trust line, scope included, so "Emerging (stall detection)"
covers that part of the chapter only. For the settled patterns, see the
[Pattern Quick-Reference](quick-reference.md).

## Models: what you are buying

The model is the part that changes under you without a code change. The chapters that deal with it
agree on the method (test on your own data, pin versions, record which model ran) and flag the
newer products around it as Emerging.

| Moving part | Verdict | Where it stands | Reviewed | Chapter |
|---|---|---|---|---|
| Tier routers and advisor pairings | Emerging | The method for choosing a model is vendor-documented and Established; routing between tiers is newer. Vendors retire models on their own schedule: on September 30, 2026 Anthropic gave notice that `claude-sonnet-4-5-20250929` would retire on November 30, after which a request to it fails with a 404. | 2026-11 | 8.2 Which Model? |
| RFT, RLVR and prompt optimizers | Emerging | The prompt-then-tune ladder is settled. A hosted tune is tied to a base model its vendor will retire: on Amazon Bedrock, for models launched on or after 7 September 2026, a base model in Legacy status accepts no new fine-tuning jobs. | 2026-11 | 8.3 To Train or to Prompt |
| LoRA parity and small-beats-frontier | Contested | The best-known report of tuned small models beating GPT-4 comes from authors at a fine-tuning vendor, against a 2024 GPT-4 baseline. | 2026-11 | 8.3 To Train or to Prompt |
| Decision models | Emerging | A product category a few months old, with speed and calibration figures that are mostly the vendors' own. One independent benchmark found error rates of 1.71% to 12.77% among answers given at 0.90 confidence or higher, across 13 decision models on 1,273 medical multiple-choice questions. | 2026-11 | 2.7 Decision Models |
| Reasoning as oversight | contested | The thinking-budget dial is Established and all three major vendors ship it. Thinking across tool calls is still changing, and reading reasoning as an account of what drove the answer is contested. | 2026-11 | 4.5 Reasoning & Thinking Budgets |
| Native speech-to-speech and full-duplex | Emerging | Cascaded streaming pipelines are Established. In speech-to-speech, audio reaches the tool-calling model with no transcript to inspect, and one 2026 study reports a 69.10% average attack success rate for hidden audio prompt injection against Gemini 3 Pro. | 2026-11 | 6.4 Voice & Realtime Agents |

## Patterns and frameworks: what the evidence supports

The composition patterns split cleanly. The fixed versions, where your code decides, are Standard
or Established. The verdicts drop where a model judges its own work, picks its own roster, or plans
with no external check.

| Moving part | Verdict | Where it stands | Reviewed | Chapter |
|---|---|---|---|---|
| Going autonomous for everything | Contested | The guidance to start simple and sit near the workflow end is Standard to Established; the hybrid is Established to Emerging. See [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md). | 2026-06 | 1.3 |
| Intrinsic self-correction, no external signal | Contested | The research finds a model checking only its own reasoning is not reliably better than its own first attempt, and can be worse. With an independent judge or an external signal, the loop is Established. | 2026-08 | 3.4 Evaluator-Optimizer |
| Same-model prompted-persona panels as a quality improvement | Contested | The evidence that personas prompted from one model improve output is thin and partly negative. | 2026-09 | 3.5 The Specialist Panel |
| Dynamic persona selection; heterogeneous-model synthesis | Emerging | Fixed parallel execution is Standard. Letting the model pick which seats run, or synthesizing across different models, is not yet settled. | 2026-09 | 3.5 The Specialist Panel |
| A model-written plan as a common, proven execution architecture | Emerging | Plan-first execution rests on 2023 to 2024 research. Validating a plan and gating it on human approval are Standard. | 2026-11 | 3.6 Planning & Task Decomposition |
| Autonomous planning correctness with no external check | Contested | GPT-4's unchecked plans succeeded in about 12% of one benchmark's cases. | 2026-11 | 3.6 Planning & Task Decomposition |
| Systematic no-progress detection; cross-attempt lesson induction | Emerging | Generate-and-validate with a sound verifier predates agents by about fifteen years and is Established. Stall detection and carrying lessons between attempts have no settled rule. | 2026-11 | 3.7 The Outer Loop |
| Multi-agent (the umbrella claim) | Contested | A study of 260 configurations across six benchmarks found a coordinated team 80.8% better than a single agent on a task that splits into independent parts, and independent agents 70.0% worse on a sequential planning task. Specialist-as-tool and read-only subagents are Established; handoffs and teams are Emerging. | 2026-11 | 9.2 Multi-Agent |
| Prompt optimizers; skill, context and harness editing | Emerging | Eval-driven prompt tuning is Established. The optimizers are open source and the artifact is a text file, but the headline figures for GEPA are its authors' own. | 2026-11 | 9.7 Self-Improving Systems |
| Self-modifying agents in production | Contested | The gains were measured under sandboxing and human oversight, their authors warn the edits can introduce vulnerabilities, and no independent production replication was found as of 2026-11. | 2026-11 | 9.7 Self-Improving Systems |

## Harnesses: agents that run on their own

The harness practices are mostly settled. What is still moving is how far a run can go without a
person, and what can safely stand in for that person.

| Moving part | Verdict | Where it stands | Reviewed | Chapter |
|---|---|---|---|---|
| Stall detection | Emerging | The loop shape and branching on stop reason are Standard; checking ground truth each step is Established. | 2026-11 | 2.5 The Agent Loop |
| A model as approver; pruning stale harness parts | Emerging | Mediated tool calls, sandboxes, hooks and caps are Standard. | 2026-11 | 2.6 The Harness |
| Classifier-as-approver | Emerging | Approval gates and pause/resume are Standard. A classifier doing the approving rests on vendor numbers, and the one independent stress test found it missed most risky actions. | 2026-11 | 4.3 Human-in-the-Loop |
| Long-running agents | Emerging | The core pattern, an initializer session followed by one-feature sessions that each leave a mergeable state, comes from one vendor and was tested on full-stack web apps. Nearly all the evidence comes from coding campaigns. | 2026-11 | 9.1 Long-Running Agents |
| Coding agents overall | Emerging | The harness practices (hooks, permissions, sandbox, diff review) are Established. In METR's randomized trial, 16 experienced developers took 19% longer with early-2025 AI tools while estimating the tools had made them 20% faster; the productivity effect is Contested. | 2026-11 | 9.6 Coding Agents |
| General desktop autonomy, injection defences, evaluation method | Emerging | Three labs ship the computer-use loop, and scoped structured browsing is Established. OSWorld launched with humans completing over 72% of tasks against 12.24% for the best model; vendor scores have since climbed and harder suites followed. | 2026-11 | 9.5 Computer Use & Browser Agents |
| Compaction strategy choice and testing | Emerging | Tool-result masking and server-side compaction ship from Anthropic, OpenAI and Claude Code. Which rung to use rests on one SWE-agent study, a vendor benchmark and a preprint. | 2026-11 | 5.4 Compaction |
| Long-term memory | Emerging | The vocabulary is settled and the mechanisms ship from Anthropic, LangChain and Letta. The benchmarks are recent, vendor results conflict, and no cited source tracks a write policy over months. | 2026-11 | 5.3 Memory |
| Progress files | Emerging | Typed state is Standard; the line between state and memory is not settled vocabulary. | 2026-11 | 5.1 State, Not Memory |
| Agent-safe replay and rollback | Emerging | Per-step checkpointing and durable-execution engines are Established. The agent-specific hazards rest on vendor docs and two 2026 papers. | 2026-11 | 7.3 Checkpointing |
| Managed platforms | Emerging | Sync, stream and async with leases and idempotency are settled, so the shapes are Established. The hosted agent platforms are young and partly in beta: Claude Managed Agents runs behind the `managed-agents-2026-04-01` beta header. | 2026-11 | 8.7 Deployment & Runtimes |
| Multi-step search planning | Emerging | Grounding over a corpus too large for the window is Standard; search as a tool is Established. | 2026-11 | 5.2 Retrieval (RAG) |
| Long context versus RAG | Contested | One study found long-context models ahead on average when given enough resources, RAG far cheaper, and routing each query between the two kept most of the accuracy at a fraction of the cost. | 2026-11 | 5.2 Retrieval (RAG) |

## Protocols: the wire between parties

Connectivity to tools is settled. Most other connections an agent makes, to a peer agent, a
person's screen, or a checkout, run on specs that are young and still revising. The protocol
chapter keeps one dated row per connection; this table copies it.

| Connection | Protocol | Verdict | Cost of adopting early | Reviewed |
|---|---|---|---|---|
| Agent to tools and data | MCP, revision 2026-07-28 | Standard (MCP); Emerging (this revision) | New clients fail against old-only servers; SDK and host support lag | 2026-11 |
| Agent to opaque peer agent | A2A 1.0.x | Emerging | Every task state needs handling; published protocol-level attacks | 2026-11 |
| Agent to person (embedded app) | MCP Apps | Emerging | Host support varies by client | 2026-11 |
| Agent to person (native UI) | A2UI | Emerging | A component catalog and a renderer per platform | 2026-11 |
| Agent backend to frontend | AG-UI | Emerging | Event plumbing to adopt | 2026-11 |
| Agent to merchant checkout | UCP or ACP (competing) | Emerging; adoption Contested | Two young specs that may both need supporting | 2026-11 |
| Payment authorisation | AP2 | Emerging | Mandate signing on both sides | 2026-11 |
| Pay per request | x402 or MPP | Emerging | Settlement setup on both sides | 2026-11 |

Every row above comes from 9.3 The Protocol Landscape (reviewed 2026-11), which also marks the need
for A2A as Contested. Four neighbouring chapters carry their own moving parts on the wire:

| Moving part | Verdict | Where it stands | Reviewed | Chapter |
|---|---|---|---|---|
| "MCP makes agents reliable" | contested | MCP is the settled cross-vendor connectivity standard, now under the Linux Foundation; the reliability claim is the overclaim. See [2.4 MCP](../the-unit/mcp.md). | 2026-06 | 2.4 |
| The "new paradigm" framing of skills | contested | The packaging mechanism is Established, shipping and stabilising. See [2.3 Skills](../the-unit/skills.md). | 2026-06 | 2.3 |
| Generative UI protocols | Emerging | Event streaming is Standard. AG-UI is still deprecating event types ahead of its 1.0. | 2026-11 | 6.3 Streaming & Agent UX |
| OTel GenAI conventions and online evals | Emerging | Tracing practice is Established. The OpenTelemetry GenAI semantic conventions carry Development status, and their first standalone release, v0.1.0, shipped in November 2026 with breaking changes. | 2026-11 | 8.1 Observability |

## Security and governance

The attacks are better understood than the defences, and the law is ahead of its enforcement.

| Moving part | Verdict | Where it stands | Reviewed | Chapter |
|---|---|---|---|---|
| Prompt-injection defences the model must honor | Contested | The threat is Established, settled and unsolved. Only checks your code enforces hold deterministically. | 2026-11 | 4.6 Prompt Injection & the Lethal Trifecta |
| Constraint by design | Emerging | The patterns for limiting what a session can read, send and change date from 2025. | 2026-11 | 4.6 Prompt Injection & the Lethal Trifecta |
| Delegation and per-run credentials for agents | Emerging | Locks and tenant isolation are standard. OAuth has the vocabulary, a 2025 position paper argues for extending it to agents, and the protocol guidance for agent tools is still being revised between dated spec releases. | 2026-11 | 8.5 Locks, PII & Identity |
| Enforcement and AI-specific standards | Emerging | The core runtime controls are Established. ISO/IEC 42001 was first published in December 2023, and the EU AI Act's obligations apply in phases, so its enforcement practice is still forming. | 2026-11 | 8.6 Governance & Compliance |

## Due for re-review

Rows dated before 2026-11 come from chapters that have not been re-read since. The oldest are
[1.3 Workflow or Agent?](../foundations/workflow-or-agent.md), [2.3 Skills](../the-unit/skills.md)
and [2.4 MCP](../the-unit/mcp.md) (2026-06), then 3.4 Evaluator-Optimizer (2026-08) and 3.5 The
Specialist Panel (2026-09). The MCP row matters most: 9.3 The Protocol Landscape, reviewed in
November, lists MCP revision 2026-07-28 as Emerging, and 2.4 predates that revision.
