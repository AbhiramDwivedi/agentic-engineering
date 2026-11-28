# The Security Posture Map

> **The decision it resolves:** across all these patterns, what can an attacker do, and where is each defense taught?

<small class="chapter-meta">*Last reviewed:* 2026-11</small>

This is the security twin of the [Hardening Checklist](hardening-checklist.md): one page, framed
by the [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/), that maps each
threat class to the chapter that argues its defense in full, so a pattern chapter can point here
instead of re-teaching the same threat. Security stays woven through the individual chapters; this
page sits over that coverage and adds nothing the chapters do not argue.

Two neighbours share the territory. Governance and compliance answers "can I show I am covered?"
against the EU AI Act, the NIST AI Risk Management Framework and its Generative AI Profile, and
ISO/IEC 42001; that is 8.6 Governance & Compliance, in
[Operating in Production](../production/index.md). Guardrails are the mechanism: the input,
output, and action checks argued in 4.4 Guardrails & Safety, in
[The Craft of Control](../craft/index.md). This page holds the threat model those checks and
records answer to: the attack surfaces, and where each defense is taught.

## The map

One row per OWASP entry. The verdict is copied from the home chapter, from its trust line or, where
the chapter splits its verdict, from the tier that covers this defense. Read it as the maturity of
the defense; the threat itself is rarely in doubt.

| OWASP entry | What the attacker does | Home chapter | Also argued in | Verdict |
|---|---|---|---|---|
| **LLM01 Prompt Injection** | Plants instructions in text the model reads (a tool result, a retrieved page, an uploaded file, an image), which the model cannot tell apart from yours. | 4.6 Prompt Injection & the Lethal Trifecta | [2.1 Tool Use](../the-unit/tool-use.md), [2.4 MCP](../the-unit/mcp.md), [2.3 Skills](../the-unit/skills.md), [3.3 Orchestrator-Workers](../composition/fan-out.md), 6.1 Ingestion (multimodal injection), 9.5 Computer Use & Browser Agents | Established (threat) / Contested (defenses the model must honor) / Emerging (constraint by design) |
| **LLM02 Sensitive Information Disclosure** | Gets personal or confidential data out through model output, or finds it copied into stores nobody scoped. | 8.5 Locks, PII & Identity | 4.4 Guardrails & Safety (output checks), 8.1 Observability (traces that carry user data) | Emerging (locks and tenant isolation are standard; delegation and per-run credentials for agents are not settled) |
| **LLM03 Supply Chain** | Ships a malicious or compromised component you load: an MCP server whose tool list changes after you approved it (the rug pull), a third-party skill, a gateway or an extension. | [2.4 MCP](../the-unit/mcp.md) | [2.3 Skills](../the-unit/skills.md), 8.2 Which Model? (the provider gateway as a dependency), 9.6 Coding Agents | The supply-chain risk of consuming a third-party server is Established; signed tool definitions are Emerging |
| **LLM04 Data and Model Poisoning** | Writes to what the model will later trust: a retrieval corpus, a long-term memory store, a saved checkpoint. | 5.2 Retrieval (RAG) for the corpus; 5.3 Memory for the store | 9.1 Long-Running Agents (poisoning that persists across sessions), 7.3 Checkpointing (a poisoned checkpoint replays the poison) | 5.2: defenses against poisoning and injection are Contested. 5.3: Emerging |
| **LLM05 Improper Output Handling** | Rides model output into a downstream system unchecked: a schema-valid object with a wrong value or an injected string, or text a browser renders as script or Markdown. | 4.4 Guardrails & Safety | [2.2 Structured Output](../the-unit/structured-output.md), 6.3 Streaming & Agent UX (the rendering boundary) | Established (rule checks standard; policy classifiers and false-positive cost still moving) |
| **LLM06 Excessive Agency** | Turns one bad or hijacked call into real damage because a tool, script, or credential could reach more than the task needed. | [2.1 Tool Use](../the-unit/tool-use.md) for scope; 4.3 Human-in-the-Loop for the approval gate | 2.6 The Harness, 3.7 The Outer Loop, 9.4 Sandboxing, 8.5 Locks, PII & Identity, [2.3 Skills](../the-unit/skills.md) (scripts) | 4.3: Standard (approval gates and pause/resume) / Emerging (classifier-as-approver) |
| **LLM07 System Prompt Leakage** | Extracts the hidden system prompt and whatever was stored in it, from credentials to business rules. | 4.1 Prompt Architecture & Management | 4.6 Prompt Injection & the Lethal Trifecta (how prompts get extracted) | Established |
| **LLM08 Vector and Embedding Weaknesses** | Asks a shared index a question and gets another tenant's documents back. | 5.2 Retrieval (RAG) | 5.3 Memory (namespaces scoped per user) | The access pre-filter is Standard practice against the multi-tenant leak |
| **LLM09 Misinformation** | Benefits when a confident, well-formed answer is wrong and nobody checks it. | No chapter argues it under this entry | [2.2 Structured Output](../the-unit/structured-output.md) (a valid schema does not vouch for meaning), 6.2 Synthesis (a valid citation id is not a supported claim) | n/a |
| **LLM10 Unbounded Consumption** | Drives volume or recursion until the bill or the fan-out has no ceiling. | 8.4 Controlling Cost | [3.3 Orchestrator-Workers](../composition/fan-out.md) (the spawn cap), 4.5 Reasoning & Thinking Budgets, 2.6 The Harness (caps) | Established (for the mechanisms: caching, batch and code-enforced budgets are vendor-documented; savings figures are vendor-reported; learned cascades Emerging, semantic caching and advisor pairings Contested) |

## The agentic entries

OWASP's separate Top 10 for Agentic Applications names threats specific to agents. Two of them
have chapter homes. **Agent Goal Hijack (ASI01)** is an attacker redirecting the agent's objective
through content it reads; 4.6 treats it as the agentic counterpart of LLM01, and 3.6 Planning &
Task Decomposition covers it for a plan the model writes. **Memory & Context Poisoning (ASI06)**
is a planted entry that carries into every later session; 9.1 Long-Running Agents argues it, and
5.3 Memory builds the poisoning gate on the write path.

## Two surfaces outside both lists

- **The evaluator in a self-improving loop.** Once a system is rewarded for raising a score, the
  cheapest path to a higher score may run through the scorer. 9.7 Self-Improving Systems argues
  the defense: an authority boundary your code enforces, where the optimizer edits only a declared
  surface and the evaluator, test data, permissions, hooks and promotion step sit outside it,
  with a sealed test set the optimizer cannot read. Poisoned feedback becoming a poisoned update
  is the injection risk again. Verdict: Emerging / Contested (eval-driven prompt tuning is
  Established; prompt optimizers and skill, context and harness editing are Emerging;
  self-modifying agents in production are Contested).
- **The deployment's inbound edges.** 8.7 Deployment & Runtimes checks the signature on every
  inbound webhook and allow-lists any callback URL a client supplies, since that callback is a
  server-side request forgery door. Verdict: Established (the shapes) / Emerging (managed
  platforms).

## Where the defenses land

Read down the "Home chapter" column and one placement repeats. 4.6 puts it plainly: the defenses
that hold are the ones your code enforces, on what a session can read, what it can send, and what
it can change once untrusted text is in its context. 4.4, 8.5, and 9.4 each name your code as the
thing that decides. Where a model is asked to hold the line, by obeying only your instructions or
by approving an action as a classifier, the chapters grade the defense Contested or Emerging.

For the execution boundary, 9.4 Sandboxing carries the rule that pairs with every row above: cover
every path that executes something, and never hand the same code both sensitive data and a way out.

## Gaps

Two OWASP entries have no full home yet, and this page does not fill them.

- **Training-data and fine-tune poisoning.** LLM04 also covers poisoning a model's training or
  fine-tuning data. The chapters argue poisoning of what the model reads at run time (corpus,
  memory, checkpoint), and none argues the training side.
- **Misinformation as a security entry.** The defenses against confident wrong output are argued
  as correctness in 2.2 and 6.2. No chapter frames them under LLM09 or gives that framing a
  verdict.

## How to use this page

In a design review, take the row for every surface your system has: each tool, each server, each
corpus, each store, each place output is rendered or executed. For each, ask whether the home
chapter's defense is in place and whether your code, rather than the model, enforces it. A row you
cannot answer points to the next chapter to read.
