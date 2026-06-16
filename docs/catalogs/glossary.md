# Glossary

> **The decision it resolves:** what do we actually mean by that word?

Plain definitions of the terms this reference leans on, each linking to the chapter that develops
it. Named research techniques carry their citation. These are seed entries, expanded as chapters land.

## The two signals

**Litmus test.** The question that classifies every pattern: does the *model* make the structural
decision (call a tool, judge its own draft and loop, size its own work), or does *your code* (a
dispatch table, a retry loop)? Model-decides is genuinely new; code-decides is engineering you
already know. See [1.2 Who Decides?](../foundations/who-decides.md).

**Maturity lens.** The trust signal on every chapter, one of four levels. **Standard**: the
accepted default. **Established**: proven, with known trade-offs. **Emerging**: gaining traction,
still settling. **Contested**: overclaimed or disputed. See [How We Label](../about/how-we-label.md).

**Grounding.** Where a claim's evidence comes from: *production* (shipped first-hand), *companion
repo* (demonstrated in code), *research* (cited), or *reasoned*.

## Core concepts

**Augmented LLM.** The base unit of every agentic system: a model given tools, a typed output
contract, and sometimes memory. See [1.4 The Augmented LLM](../foundations/the-augmented-llm.md).

**Context engineering.** Treating the context window as the program, deciding what to put in it and
what to leave out, because both tokens and the model's attention are finite. See [1.5 Context
Engineering](../foundations/context-engineering.md).

**Progressive disclosure.** Revealing capability to the model in stages (a name and description
first, fuller instructions and files only when a task needs them) so the window holds only what is
relevant. The mechanism behind Agent Skills. See [2.3 Skills](../the-unit/skills.md).

**Workflow vs. agent.** A *workflow* runs a path your code lays out, with the model filling slots;
an *agent* decides its own path at runtime. Most production value sits on the workflow end. See
[1.3 Workflow or Agent?](../foundations/workflow-or-agent.md).

## Capabilities and patterns

**Tool use (function calling).** Giving the model a typed function it can choose to call: the model
picks the call and the arguments, your code runs it and owns the result. See
[2.1 Tool Use](../the-unit/tool-use.md).

**Structured output.** Constraining the model's output to a schema (JSON mode, constrained
decoding). The same machinery as a tool's input, used to shape an answer rather than run a function.
See [2.2 Structured Output](../the-unit/structured-output.md).

**MCP (Model Context Protocol).** The settled cross-vendor standard, now under the Linux Foundation,
for connecting a host to servers that expose tools, resources, and prompts, so a tool written once
works across vendors. See [2.4 MCP](../the-unit/mcp.md).

**RAG (retrieval-augmented generation).** Retrieving relevant documents and placing them in the
context before the model answers: semantic memory for the system. See
[5.2 Retrieval (RAG)](../knowledge/retrieval-rag.md).

The composition patterns (prompt chaining, front controller, orchestrator-workers,
evaluator-optimizer, specialist panel) are each defined in their own chapter under
[Composition](../composition/index.md).

## Named research

**ReAct.** Interleaving reasoning and acting: the model alternates a thought with a tool call rather
than committing to an answer in one shot. (Yao et al., 2022,
[arXiv:2210.03629](https://arxiv.org/abs/2210.03629))

**Gorilla.** An LLM connected to a large API set, and the source of the much-cited finding that a
model calls the right tool with fabricated arguments. (Patil et al., 2023,
[arXiv:2305.15334](https://arxiv.org/abs/2305.15334))

**tau-bench.** A tool-agent-user benchmark, behind the calibration that frontier models complete
fewer than half of realistic multi-step tool tasks. (Yao et al., 2024,
[arXiv:2406.12045](https://arxiv.org/abs/2406.12045))

**When2Call.** A benchmark for *when not* to call a tool, treating abstention as an open problem.
(Ross et al., 2025, [arXiv:2504.18851](https://arxiv.org/abs/2504.18851))
