# Coverage map: MCP (chapter 2.4)

> Research-derived spec for what the chapter must cover so a reader can connect an agent to tools and
> data over MCP in production *safely*, and where to stop. Built from a 5-angle sweep (vendor/primary
> docs, academic/benchmarks, OWASP security, practitioner writeups, the skeptical read). Review and
> trim the **Must-cover** list; that sets the chapter's scope. Bar: definitive but tight (the
> Gang-of-Four / Wikipedia test), not exhaustive.
>
> This chapter treats **MCP as the settled, cross-vendor connectivity standard** (now under the Linux
> Foundation). Packaging procedural knowledge (Skills) lives in 2.3; A2A and the broader protocol
> landscape stay in 9.3.
>
> **No production grounding.** The carrier is a batch pipeline with mostly in-process tools; there is
> no shipped MCP story. This is a **reasoned / companion-repo** chapter — demonstrations are
> `> In the companion repo.` (e.g. the merchant helpdesk reaching a docs MCP server), never
> `> From production.`

## The mental model (what the reader must leave with)

**MCP** is not "a new kind of agent." It is a wire protocol: a standard way for a host to connect to
servers that expose **tools, resources, and prompts**, so a tool written once works across vendors.
Run the litmus test honestly and it deflates: MCP is *connectivity plumbing* — your code decides what
to connect and what it's allowed to do; the model is just the worker that may call a connected tool.
The value is real but **operational, not architectural**. And the security frame is the other half of
the model: the moment MCP carries an untrusted tool description or connects an untrusted server, every
"tool-result-is-untrusted" lesson from 2.1 applies, plus a supply-chain trust boundary that is new —
you are granting ambient authority to software you may not control.

## Must-cover (for safe production use)

Ranked. Each: why it matters, the failure mode if skipped, maturity, lead citation. `[+]` = gap
(the chapter is currently a stub, so treat all as `[+]`).

1. **MCP: the settled connectivity standard** `[+]` — host / client / server over JSON-RPC 2.0;
   servers expose **tools, resources, prompts** (clients can offer sampling, roots, elicitation);
   transports are stdio and Streamable HTTP. Frame it as the cross-vendor default — donated to the
   Linux Foundation's Agentic AI Foundation, adopted by Anthropic, OpenAI, Google, Microsoft — so a
   tool is written once and reused. Litmus: connectivity plumbing, your code decides. *Skip it:*
   readers reinvent per-vendor glue or treat MCP as magic. **Standard.** (MCP spec rev 2025-11-25;
   LF/AAIF announcement 2025-12-09.)

2. **Tool descriptions and results are untrusted input — tool poisoning** `[+]` *(the security
   spine)* — the spec itself says tool descriptions/annotations "should be considered untrusted,
   unless obtained from a trusted server." A malicious description or a poisoned tool *result* is
   indirect prompt injection straight into context. Cross-link 2.1's "treat tool results as
   untrusted." *Skip it:* data exfiltration, hijacked actions via a third-party server. **Standard
   risk.** (MCP spec "Tool Safety"; OWASP MCP Tool Poisoning → LLM01/LLM06; arXiv:2503.23278.)

3. **The third-party-server trust boundary: supply chain, rug pulls, over-broad permission** `[+]`
   — installing an MCP server is installing software with ambient authority. Cover: vet the source
   and audit before use; the **rug pull** (a server silently mutates a tool definition *after*
   approval — clients verify at install, not on change); and least-privilege scoping so one
   compromised server can't reach everything. *Skip it:* a trusted integration turns malicious and
   the agent never notices. **Established risk; Emerging defences.** (OWASP MCP Security Cheat Sheet;
   ETDI arXiv:2506.01333; postmark-mcp incident, Sept 2025.)

4. **Authorization, consent, and the human gate** `[+]` — MCP's security model is consent-first:
   hosts MUST obtain explicit user consent before exposing data or invoking a tool, and remote
   servers add OAuth/authorization-server concerns. Pair this with the destructive-action gate from
   4.3. *Skip it:* silent privileged actions, broken audit trail. **Standard principle.** (MCP spec
   "User Consent and Control"; remote-transport authorization → mention-and-link 4.3.)

5. **The failure-return contract** `[+]` *(standing lens)* — when an MCP server is unreachable, times
   out, or returns malformed data, the failure must come back to the model as a structured,
   recoverable message, not a raw stack trace — and a **stale cached tool list** must not be assumed
   live. *Skip it:* the agent loops on a dead server or acts on tools that no longer exist. **Standard
   practice.** (Inherits 2.1's loop contract; OpenAI Agents SDK `cache_tools_list` caveat.)

6. **The skeptical read + the reliability check** `[+]` — name the overclaim plainly: MCP is
   connectivity, not reliability; standardising the wire does not make the agent good at using it. And
   calibrate: even with MCP, models complete only a minority of realistic multi-step MCP tasks.
   *Skip it:* you ship the hype that "MCP makes agents reliable." **Contested** (the reliability
   claim); **Established** (the reliability gap). (MCPMark arXiv:2509.24002; MCP-Universe,
   SalesforceAIResearch.)

7. **When an MCP server (vs a Skill)** `[+]` — the MCP side of the decision the reader will hit:
   reach for an MCP server when the need is *connectivity* — reach this system's tools, data, or
   resources over a standard wire so it works across vendors. A skill can teach the workflow that
   *drives* MCP tools; they compose, it is not a vs. framing. State the MCP side crisply and point to
   the Skills chapter for procedural-knowledge packaging. *Skip it:* the reader cargo-cults both.
   **Established.** (Anthropic: skills "complement MCP servers" → mention-and-link 2.3.)

## Mention-and-link (one line, a pointer, not a section)

- **Skills / procedural knowledge** — when the need is packaging how-to context and revealing it on
  demand, not connecting to a system over the wire → 2.3 Skills. The "MCP server vs Skill" decision
  states the MCP side here and links there.
- **Tool Use** — the contract, schema design, `tool_choice`, treating results as untrusted; MCP tools
  *are* tools, so don't re-teach the loop → 2.1 Tool Use.
- **Structured output** — validating tool outputs against a schema (a poisoning mitigation) →
  2.2 The Machine-Checkable Contract.
- **Guardrails & human-in-the-loop** — destructive-action approval, allowlisting, blast-radius, and
  the remote-server authorization gate → 4.4 Guardrails & Safety, 4.3 Knowing When to Ask.
- **A2A and the broader protocol landscape** — agent-to-agent and competing protocols → 9.3 The
  Protocol Landscape (mention-and-link only; out of scope here by author decision).
- **Live adoption/benchmark numbers** (SDK downloads, server counts, per-model MCP pass rates) →
  link to source, never hardcode; they rot.

## Out of scope (name it, point out)

- **Writing a production MCP server end-to-end** (transport internals, full auth server) → MCP spec;
  this chapter teaches the *consumer's* trust model, not a server tutorial.
- **Packaging procedural knowledge** (Skills, progressive disclosure) → 2.3.
- **A2A / multi-agent protocols and the protocol bake-off** → 9.3.
- **Vendor API minutiae** (exact beta headers, hosted-MCP plumbing, SDK calls) → vendor docs; cite,
  don't reproduce.
- **Deep RAG / retrieval** as a way to populate context → Part V.

## Maturity summary

- **Standard:** MCP as the cross-vendor connectivity standard; consent-first authorization; treating
  tool descriptions and results as untrusted.
- **Established:** the supply-chain / third-party-server risk; the reliability gap (models complete a
  minority of realistic multi-step MCP tasks); "skill for knowledge / MCP for connectivity"
  composition.
- **Emerging:** robust rug-pull / mutable-description defences (ETDI-style signed tool definitions);
  hardened remote-transport authorization patterns.
- **Contested:** "MCP makes agents reliable"; any framing that sells a connectivity protocol as a
  genuinely-new agentic capability.

## Sources

Vendor / primary: MCP specification rev 2025-11-25 (modelcontextprotocol.io/specification/2025-11-25,
incl. "Security and Trust & Safety", "Tool Safety", "User Consent and Control"); OpenAI Agents SDK MCP
docs (openai.github.io/openai-agents-python/mcp/, incl. the `cache_tools_list` caveat).
Standardization: Linux Foundation "Agentic AI Foundation" announcement, 2025-12-09
(linuxfoundation.org/press). Security: OWASP "MCP Tool Poisoning"
(owasp.org/www-community/attacks/MCP_Tool_Poisoning, → LLM01/LLM06); OWASP MCP Security Cheat Sheet
(cheatsheetseries.owasp.org); OWASP Top 10 for LLM Applications 2025 (genai.owasp.org). Research: MCP
landscape & threats arXiv:2503.23278 (Hou et al., 16 threats × 4 lifecycle phases); Systematic
Analysis of MCP Security arXiv:2508.12538; ETDI (signed tool definitions vs rug pull/squatting)
arXiv:2506.01333; MCPMark arXiv:2509.24002; MCP-Universe (SalesforceAIResearch, GitHub). Skeptical /
practitioner: The New Stack "The case for running AI agents on Markdown files instead of MCP servers."

> **Verify before quoting:** the MCP spec revision string (2025-11-25), MCP SDK-download and
> active-server counts, and any per-model MCP-task pass rate are all volatile or surface-specific —
> cite the finding and the live source, never a frozen value. CVE IDs (MCPoison CVE-2025-54136,
> CurXecute CVE-2025-54135) and the postmark-mcp incident are illustrative; re-verify before naming
> them in prose.

## Open questions for the author (rule on these before drafting)

1. **CVE specificity.** Name MCPoison / CurXecute / postmark-mcp as concrete anchors, or keep the
   security section at the category level (poisoning / rug pull / over-broad permission) to avoid
   rot? Recommendation: category-level in prose, CVEs in a footnote.
2. **Carrier grounding.** Confirmed companion-repo / reasoned (no production MCP story). Which surface
   demonstrates it in the companion repo — the merchant helpdesk reaching a docs MCP server is the
   leading candidate; confirm before drafting the `> In the companion repo.` example.
3. **Depth of the security section.** Full trust-boundary treatment here, or a tight version that
   defers blast-radius/least-privilege depth to 4.4 Guardrails? Recommendation: own the
   *poisoning / rug-pull / consent* triad here; mention-and-link the general guardrail machinery.
4. **OpenAI/Google parity.** How much cross-vendor coverage (OpenAI hosted MCP, approvals) versus
   keeping the spec + Anthropic as the worked example with others as asides?
