# Coverage map: Tool Use (chapter 2.1)

> Research-derived spec for what the chapter must cover to let a reader build with tool use in
> production *safely*, and where to stop. Built from a 3-angle sweep (vendor docs, OWASP security,
> academic/benchmark). Review and trim the **Must-cover** list; that sets the chapter's scope.
> Bar: definitive but tight (the Gang-of-Four / Wikipedia test), not exhaustive.

## The mental model (what the reader must leave with)

A tool is a typed function the model may choose to call; tool use is the model making that choice,
while your code owns what the tool does and whether its result is allowed to matter. Everything
hard about tool use follows from one fact: the model's decision to call, its choice of arguments,
and its handling of the result are all unreliable, so the safety has to live in your code, not in
the prompt.

## Must-cover (for safe production use)

Ranked. Each: why it matters, the failure mode if skipped, maturity, lead citation. `[*]` = the
chapter already covers it; `[+]` = gap in the current 2.1.

1. **The contract: schema design** `[*partial]` — typed JSON-Schema params, `strict` mode
   (`additionalProperties:false`, all required), clear descriptions, keep tool count small
   (vendor guidance: under ~20). *Skip it:* the model fabricates or mis-types arguments and picks
   the wrong tool. **Standard.** (OpenAI function-calling; Anthropic tool use.)
2. **The decision + `tool_choice` modes** `[+]` — `auto` / `required` / forced-function / `none`
   / allowed-subset. Over-calling and under-calling are both failure modes. *Skip it:* the model
   skips a needed check, or calls tools it shouldn't, burning latency and money. **Standard**
   (the modes); **Emerging** (when-to-call/abstention). (Vendor docs; When2Call, arXiv:2504.18851.)
3. **The loop** `[*]` — model calls, your code executes, you return the result by id, the model
   continues; parallel and multiple calls in one turn. *Skip it:* broken multi-turn behavior.
   **Standard.** (ReAct, arXiv:2210.03629; vendor docs.)
4. **Validate the model's arguments; never trust them** `[+]` — tool-usage hallucination: right
   tool, fabricated parameter values. *Skip it:* bad or destructive arguments get executed.
   **Established.** (Gorilla, arXiv:2305.15334; hallucination taxonomy, arXiv:2412.04141.)
5. **Treat tool *results* as untrusted input** `[+]` — indirect/second-order prompt injection: a
   poisoned tool output hijacks the agent. *Skip it:* data exfiltration, hijacked actions.
   **Standard risk.** (OWASP LLM01 Prompt Injection; LLM05 Improper Output Handling.)
6. **Least privilege and blast radius** `[*partial]` — scope each tool to the minimum permission;
   gate destructive or irreversible actions behind human approval. *Skip it:* the agent takes an
   irreversible harmful action. **Standard principle.** (OWASP LLM06 Excessive Agency; links to
   4.3 Human-in-the-loop, 4.4 Guardrails.)
7. **Failure and limits** `[*partial]` — timeouts, idempotent retries, partial-failure handling,
   bounded loops (step caps), and concurrency/transactional safety when tools write shared state.
   *Skip it:* hangs, double-writes, runaway cost. **Established.** (OWASP LLM10 Unbounded
   Consumption.)
8. **The reliability reality (why you gate)** `[+]` — the calibration that justifies all of the
   above: even frontier models complete fewer than half of realistic multi-step tool tasks, and
   consistency across repeats (pass^k) is worse. *Skip it:* you ship an over-trusted agent.
   **Established** (the finding); **Contested** ("autonomous agents" marketing). (tau-bench,
   arXiv:2406.12045; MCPMark, arXiv:2509.24002.)
9. **Cost and observability** `[*partial]` — tool schemas ride in the input tokens on every
   request, each call is a round trip, and every tool call must be traceable. *Skip it:* cost
   blowup and undebuggable runs. **Standard.** (Vendor pricing docs.)

## Mention-and-link (one line, a pointer, not a section)

- **MCP** as the cross-vendor tool-connectivity standard (now under the Linux Foundation) → 2.4 MCP.
- **Structured output / constrained decoding** internals (function calling *is* structured output) → 2.2.
- **Fine-tuning / RLVR for tool use** → 8.3 To Train or to Prompt.
- **RAG-based tool retrieval** for very large tool catalogs → one line + link.
- **Live benchmark numbers** (BFCL leaderboard) → link, do not hardcode; they rot.

## Out of scope (name it, point out)

- Building MCP servers (→ MCP spec / 2.3).
- Constrained-decoding library internals (XGrammar/Outlines/Guidance) — cite, do not teach.
- Provider-specific API minutiae (exact headers, SDK calls) → vendor docs.
- Multi-agent tool orchestration → Part IX.

## Maturity summary

- **Standard:** tool calling as a capability, JSON-Schema contracts, the ReAct loop, `tool_choice`
  modes, MCP for connectivity, treating tool results as untrusted, least privilege.
- **Established:** multi-step tool use for narrow tasks, argument validation as practice, fine-tuning.
- **Emerging:** long-horizon agentic tool use, when-to-call/abstention, dual-control settings.
- **Contested:** "fully autonomous" tool-using agents; any single quoted hallucination rate.

## Sources

Vendor: Anthropic "Tool use with Claude" (platform.claude.com/.../tool-use/overview); OpenAI
"Function calling" (developers.openai.com/.../function-calling). Security: OWASP Top 10 for LLM
Applications 2025 (genai.owasp.org/llm-top-10). Research: ReAct arXiv:2210.03629; Toolformer
arXiv:2302.04761; Gorilla arXiv:2305.15334; tau-bench arXiv:2406.12045; MCPMark arXiv:2509.24002;
When2Call arXiv:2504.18851; tool-hallucination taxonomy arXiv:2412.04141; BFCL (ICML 2025,
gorilla.cs.berkeley.edu/leaderboard.html). MCP: anthropic.com/news/model-context-protocol; Linux
Foundation AAIF.

> **Verify before quoting:** live BFCL scores and any specific per-model hallucination percentage
> are directional and source-dependent; cite the finding, not a frozen number.
