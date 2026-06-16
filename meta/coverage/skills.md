# Coverage map: Skills (chapter 2.3)

> Research-derived spec for what the chapter must cover so a reader can package agent capabilities
> (Skills) and use them in production *safely*, and where to stop. Built from a 5-angle sweep
> (vendor/primary docs, academic/benchmarks, OWASP security, practitioner writeups, the skeptical
> read). Review and trim the **Must-cover** list; that sets the chapter's scope. Bar: definitive but
> tight (the Gang-of-Four / Wikipedia test), not exhaustive.
>
> This chapter is **security-first**: a Skill is untrusted *code + instructions* from a source you
> may not control, so installing one is a supply-chain decision — that frame leads the chapter, not a
> footnote. It is also the **home for progressive disclosure** (the load-on-demand mechanism).
> Connectivity (MCP) lives in 2.4; the general context-economy principle lives in 1.5.
>
> **`VERIFY — production grounding unconfirmed; confirm a real shipped skill in the carrier before
> any From-production claim ships.`** This chapter assumes a production Skill *may* exist in the
> carrier (e.g. a `pricing`/MAP-compliance skill packaging the rules), but that is unconfirmed. Until
> a real shipped skill is verified, demonstrations are `> In the companion repo.` / `> In Listing
> Studio.`, never `> From production.`

## The mental model (what the reader must leave with)

A **Skill** is not "a new kind of agent." It is a folder of procedural knowledge — a `SKILL.md`
(YAML `name` + `description`, then a fuller instruction body), plus optional bundled files and
executable scripts — that the runtime reveals to the model in stages so the context window only ever
holds what the current task needs. Run the litmus test honestly and it deflates: Skills are *context
engineering as packaging*. Your runtime decides what to reveal; the model only decides which skill to
pull in. The value is real but **operational, not architectural**. And the security frame is the
other half of the model: a `SKILL.md` body is *injected instructions* and bundled scripts *execute*,
so installing a third-party skill is installing third-party code with whatever authority you grant
it. Every "tool-result-is-untrusted" lesson from 2.1 applies the moment a skill comes from a source
you don't control, plus a supply-chain trust boundary that is the chapter's spine.

## Must-cover (for safe production use)

Ranked. Each: why it matters, the failure mode if skipped, maturity, lead citation. `[+]` = gap
(the chapter is currently a stub, so treat all as `[+]`).

1. **A Skill is untrusted code + instructions — the supply-chain decision** `[+]` *(the chapter's
   spine)* — a `SKILL.md` body is injected instructions and bundled scripts execute, so installing or
   using a third-party skill is a supply-chain decision, not a convenience. Cover: audit before use
   (Anthropic's own guidance is to vet a skill before installing it); treat a third-party skill like
   third-party code (read the body *and* the scripts); scope what those scripts can touch
   (least-privilege, blast radius). This leads the chapter. *Skip it:* a "helpful" markdown folder
   ships injected instructions or runs a script that exfiltrates data or takes a privileged action,
   and nobody audited it. **Established risk; Emerging defences.** (Anthropic Agent Skills guidance
   on auditing; OWASP MCP Security Cheat Sheet — supply-chain class; OWASP LLM01/LLM06.)

2. **Progressive disclosure — the three load levels** `[+]` *(this chapter owns it)* — Level 1
   metadata always in the system prompt (~name + description), Level 2 the `SKILL.md` body loaded
   only when triggered, Level 3 referenced files/scripts read or executed only as needed (script
   *output* enters context, not the code). This is the chapter's centrepiece and the named
   cross-reference target from 2.1 (schema-bloat mitigation) and 1.5 (the general principle).
   *Skip it:* you lose the one idea that makes Skills worth a chapter, and the cost story collapses.
   **Established.** (Anthropic Agent Skills overview, the three-level table; engineering post,
   2025-10-16.)

3. **Skills: what they are, and the litmus deflation** `[+]` — a Skill is a `SKILL.md` (YAML
   `name`/`description` + body) plus optional bundled files/scripts; "an onboarding guide for a new
   hire." Classify it honestly: packaging + context engineering, *not* a genuinely-new pattern. The
   model decides *to pull a skill in*; the runtime decides *what gets revealed*. *Skip it:* readers
   treat folders-of-markdown as a breakthrough and over-architect. **Established** (the mechanism is
   shipping and stabilising). (Anthropic Agent Skills overview; engineering post, 2025-10-16.)

4. **Context economy: why progressive disclosure pays twice** `[+]` *(standing lens)* — every
   instruction block, bundled file, and script output in the window costs both tokens *and* degraded
   attention; the mitigation is to inject the minimal relevant subset, which is exactly what staged
   loading does. State both costs, name the win (effectively unbounded bundled content at near-zero
   idle cost), and the trade (a description that fails to trigger silently strands the whole skill).
   *Skip it:* the chapter sells the feature without the discipline that justifies it. **Standard
   principle.** (1.5 Context Engineering for depth — mention-and-link; Anthropic token-cost table.)

5. **The skeptical read: "skills are a new paradigm" is overclaimed** `[+]` — name the overclaim
   plainly: "skills" today lumps together markdown instructions, packaged code, and workflow
   orchestration that have little in common; the win is routing + context management, not smarter
   prompts. Resist the "new paradigm / the endgame" framing. *Skip it:* you ship the hype and erode
   the trust the reference is selling. **Contested** (the paradigm claim). (Steve Kinney "Agent
   Skills, Stripped of Hype"; OSS Insight "Agent Skills … Transitional Layer.")

6. **The failure-return contract for skill scripts** `[+]` *(standing lens)* — when a skill's bundled
   script errors, times out, or returns malformed data, the failure must come back to the model as a
   structured, recoverable message, not a raw stack trace — and never as silent success. *Skip it:*
   the agent loops on a dead script or hides the error and proceeds on bad state. **Standard
   practice.** (Inherits 2.1's loop contract.)

7. **When a Skill (vs an MCP server)** `[+]` — the Skills side of the decision the reader will hit:
   reach for a Skill when you need to give the model *procedural knowledge and context* — how to do a
   workflow, which rules to apply, what good output looks like — packaged once and revealed on
   demand. A skill can teach the workflow that *drives* MCP tools; they compose, it is not a vs.
   framing. State the Skills side crisply and point to the MCP chapter for connectivity. *Skip it:*
   the reader cargo-cults both. **Established.** (Anthropic: skills "complement MCP servers"; The New
   Stack "Skills vs MCP" → mention-and-link 2.4.)

## Mention-and-link (one line, a pointer, not a section)

- **MCP / connectivity** — when the need is reaching a system's tools/data over the wire, not
  packaging procedural knowledge → 2.4 MCP. The "Skill vs MCP server" decision states the Skills side
  here and links there.
- **Context Engineering** — progressive disclosure as the general context-economy principle; this
  chapter owns the *Skills mechanism*, 1.5 owns the *principle* → 1.5 Context Engineering.
- **Tool Use** — the contract, schema design, `tool_choice`, treating results as untrusted; a skill
  often packages the workflow that calls tools, so don't re-teach the loop → 2.1 Tool Use.
- **Structured output** — validating a skill script's output against a schema (a poisoning
  mitigation) → 2.2 Structured Output.
- **Guardrails & human-in-the-loop** — destructive-action approval, allowlisting, blast-radius for
  what a skill's scripts may touch → 4.4 Guardrails & Safety, 4.3 Human-in-the-Loop.
- **Live adoption/benchmark numbers** (skill counts, marketplace stats) → link to source, never
  hardcode; they rot.

## Out of scope (name it, point out)

- **Connectivity protocols** (MCP wire format, transports, servers) → 2.4 MCP.
- **A2A / multi-agent protocols and the protocol bake-off** → 9.3.
- **Vendor API minutiae** (exact beta headers, `skill_id` plumbing, SDK calls) → vendor docs; cite,
  don't reproduce.
- **Deep RAG / retrieval** as a way to populate context → Part V.
- **Fine-tuning a model for better skill selection** → 8.3.

## Maturity summary

- **Standard:** progressive disclosure as a context principle.
- **Established:** Skills (the packaging mechanism, shipping and stabilising); the three-level loading
  model; "skill for knowledge / MCP for connectivity" composition; the supply-chain risk of
  installing third-party skills.
- **Emerging:** robust audit / signing tooling for third-party skills; cross-surface skill
  portability; standardised skill discovery beyond a single vendor.
- **Contested:** "Skills are a new paradigm / the endgame"; any framing that sells
  folders-of-markdown as a genuinely-new agentic capability.

## Sources

Vendor / primary: Anthropic "Agent Skills" overview (platform.claude.com/docs/en/agents-and-tools/
agent-skills/overview, incl. the three-level loading table and the audit-before-use guidance) and
engineering post "Equipping agents for the real world with Agent Skills" (anthropic.com/engineering,
2025-10-16). Security: OWASP MCP Security Cheat Sheet (cheatsheetseries.owasp.org) for the
supply-chain class as it applies to installable capabilities; OWASP Top 10 for LLM Applications 2025
(genai.owasp.org), LLM01 Prompt Injection (the `SKILL.md` body as injected instructions) and LLM06
Excessive Agency (what a skill's scripts are allowed to touch). Skeptical / practitioner: Steve
Kinney "Agent Skills, Stripped of Hype" (stevekinney.com/writing/agent-skills); The New Stack "The
case for running AI agents on Markdown files instead of MCP servers"; OSS Insight "Agent Skills …
Transitional Layer."

> **Verify before quoting:** the `SKILL.md` token-cost numbers (~100 tokens metadata / <5k body) and
> any skill-count or marketplace adoption figures are volatile or surface-specific — cite the finding
> and the live source, never a frozen value.

## Open questions for the author (rule on these before drafting)

1. **Carrier grounding — `VERIFY`.** Listing Studio is a batch pipeline with mostly in-process tools.
   Is there a *real shipped* Skill to tell a "From production:" story about (e.g. a `pricing`/MAP
   skill packaging the compliance rules), or is this a companion-repo / reasoned chapter? Confirm a
   real shipped skill before any From-production claim ships; until then, demonstrations stay
   `> In the companion repo.` / `> In Listing Studio.`
2. **Depth of the security section.** Full trust-boundary treatment here (audit, third-party-code
   discipline, script scoping), or a tight version that defers blast-radius/least-privilege depth to
   4.4 Guardrails? Recommendation: own the *injected-instructions + executable-script + audit-before-
   use* triad here as the chapter's spine; mention-and-link the general guardrail machinery.
3. **Cross-vendor parity.** How much non-Anthropic coverage of the skill/packaging mechanism, versus
   keeping Anthropic Agent Skills as the worked example with others as asides? (The mechanism is least
   standardised across vendors of anything in this chapter.)
