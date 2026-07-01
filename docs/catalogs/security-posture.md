# The Security Posture Map

> **The decision it resolves:** across all these patterns, what can an attacker actually do, and where is each defense taught?

> **Stub: planned for a later release.**

The security twin of the [Hardening Checklist](hardening-checklist.md): one scannable page framed
by the [OWASP Top 10 for GenAI](https://genai.owasp.org/llm-top-10/), mapping each threat class to
the chapter that argues its defense in full, so a pattern chapter can point here instead of
re-teaching the same threat. Security stays woven through the individual chapters; this hub sits
over that coverage rather than replacing it. Where a threat has no natural home chapter (data and
model poisoning, system-prompt leakage, misinformation), the map owns it outright.

Two boundaries keep it honest. It is not governance and compliance: that answers "am I covered?"
against the EU AI Act, NIST AI RMF, ISO 42001, SOC 2, and GDPR, and lives in
[Operating in Production](../production/index.md), whereas this answers "what are my attack
surfaces and defenses?" It is also separate from guardrails and safety. Guardrails is the
mechanism, the input, output, and action controls argued in
[The Craft of Control](../craft/index.md); this map is the threat model and defense-in-depth
posture those controls answer to.

Its per-threat homes draw from [Tool Use](../the-unit/tool-use.md) and
[MCP](../the-unit/mcp.md) (prompt injection, excessive agency), [Skills](../the-unit/skills.md)
(supply chain), [Structured Output](../the-unit/structured-output.md) (improper output handling),
and [Retrieval](../knowledge/index.md) (vector and embedding weaknesses), among others. The OWASP
taxonomy itself is close to Standard; the individual defenses range from Standard to Emerging.
