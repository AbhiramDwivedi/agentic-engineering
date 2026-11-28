# Coverage map: Prompt Injection & the Lethal Trifecta (chapter 4.6)

> Research-derived spec for what the chapter must cover, and where to stop. Angles run: vendor
> docs, academic and benchmarks, security and incidents, practitioner writeups, skeptical read,
> alias sweep (public catalogs only). Review and trim **Must-cover**; that sets scope.

## The mental model (what the reader must leave with)

A language model has one input channel. Instructions and data arrive as the same kind of text, so
anything the model reads can act as an instruction, and no one has found a reliable way to stop
that. There are two failure modes. **Leaks**: one session combines private data, untrusted content,
and a way to send data out (the lethal trifecta). **Unwanted actions**: untrusted content steers a
state change with no egress at all, such as a planted line in a supplier spec sheet that pushes a
price below the minimum advertised price. Meta's Rule of Two covers both, because its third leg is
"change state or communicate externally." Thesis: *prompt injection cannot be filtered out, so the
only defenses that hold are the ones your code enforces: what the session can read, what it can
send, and what it can change after it has read untrusted text.* A filter that survives an adaptive
attacker would refute this; the current evidence is that none has. Litmus: the model decides
whether to obey the injected text (agentic risk); your code decides which tools, data, and egress
exist (the harness, where every working defense lives).

## Relationship to shipped chapters

2.4 MCP already names the trifecta, says the durable defense is to remove one leg and keep a human
gate on the rest because there is no reliable filter, and ships a description scanner described as
a tripwire. 2.1 treats tool output as data. 3.3 tags worker output `trust="untrusted"` in
`render_for_synthesis()`. 4.6 is the deepening, not the first statement: it credits and links 2.4,
then adds the integrity case, the evidence that filters fail, the design patterns, and what tagging
does and does not buy. Items marked `[ext]` extend a shipped paragraph; `[+]` is new.

## Must-cover (ranked)

1. **Root cause and the two forms** `[+]` - no instruction/data boundary in the input; direct vs
   indirect (planted in a web page, email, spec sheet, tool result). Willison named the attack in
   Sept 2022 by analogy to SQL injection, crediting Riley Goodside's demonstration; the
   parameterized-query fix has not transferred. Whether jailbreaking is a kind of injection is
   contested: OWASP says it is a form of it, Willison argues they are different problems; state both
   in one sentence. **Established** (threat). (Willison 2022; Greshake et al. arXiv:2302.12173;
   OWASP LLM01:2025.)
2. **The trifecta and the Rule of Two, as co-equal frames** `[ext]` - trifecta (Willison, 16 June
   2025, his coinage, widely adopted) models leaks. Rule of Two (Meta, 31 Oct 2025): A untrusted
   input, B sensitive access, C change state or communicate externally; at most two per session,
   else supervision or a fresh session with a new context window (the carrier-relevant escape:
   split ingest from publish). Meta says it applies until robustness research can reliably detect
   and refuse injection, and is a supplement to least privilege, not a substitute. Credit 2.4's
   "remove a leg"; do not offer it as a new label.
3. **Why filters and prompts do not hold** `[ext]` - OWASP says it is unclear whether fool-proof
   prevention exists. "The Attacker Moves Second" (Nasr, Carlini et al., arXiv:2510.09023, 10 Oct
   2025) bypassed 12 recent defenses, most above 90% attack success where most had reported near
   zero. Willison: a 95% catch rate is a failing grade in web security. **Contested**.
4. **Model-side defenses: spotlighting and the instruction hierarchy** `[+]` - Spotlighting (Hines
   et al., arXiv:2403.14720, Microsoft, 2024): delimit, datamark, or encode untrusted input; the
   paper reports large drops in attack success on GPT-family models. Instruction Hierarchy
   (Wallace et al., arXiv:2404.13208, OpenAI, 2024): train the model to rank privileged over
   lower-privileged instructions. Both work only if the model chooses to honor them, so both are
   **Contested**: hygiene and mitigation, not a boundary. Seam note: 3.3's `untrusted` tag is this
   class of defense; say so plainly and link back.
5. **Break the legs by architecture** `[ext]` - least privilege per session, scope the data (one
   merchant), cut egress (no outbound fetch, no rendered remote images or links, allowlisted
   domains), separate sessions that read untrusted content from those holding private data.
   **Standard** (least privilege, per OWASP LLM01 and LLM06); tooling **Emerging**.
6. **The design patterns** `[+]` - Beurer-Kellner et al. arXiv:2506.08837: Action-Selector,
   Plan-Then-Execute, LLM Map-Reduce, Dual LLM, Code-Then-Execute, Context-Minimization. Quote the
   principle exactly: once an agent has ingested untrusted input, "it must be constrained so that it
   is impossible for that input to trigger any consequential actions." Scope conclusion (section 5):
   application-specific agents can be secured by principled design, general-purpose agents are not
   yet secure, and no single pattern suffices across all threat models. Plan-Then-Execute caveat:
   untrusted data can still influence action parameters. **Worked pattern: Dual LLM** (Willison, 25
   Apr 2023) or LLM Map-Reduce against the supplier spec sheet: an isolated reader emits constrained
   fields, the privileged side never sees raw text. The paper's furniture-retailer chatbot and
   review-summarizing recommender case studies are the public counterpart. Plan-Then-Execute gets one
   table row and a link to 3.6 (which owns planner hijack). **Emerging**.
7. **CaMeL and the frontier** `[+]` - Debenedetti et al. arXiv:2503.18813: control and data flow
   from the trusted query, capabilities block unauthorized flows; 77% of AgentDojo tasks with
   provable security vs 84% undefended. One paragraph; cost is utility. **Emerging** (research).
8. **Vendor posture** `[+]` - Anthropic (24 Nov 2025): RL, classifiers, red teaming; 1% attack
   success "still represents meaningful risk." OpenAI (7 Nov 2025, "Understanding prompt
   injections: a frontier security challenge"): "a hard, open problem." Cite the posture, never
   freeze the rates. **Established** that vendors call it open.
9. **Human confirmation and its limits** `[ext]` - gates are a real defense; in the Invariant demo
   the authors note many users already choose "Always Allow" and stop monitoring individual actions.
   Report Invariant's own framing ("not a flaw in the GitHub MCP server code itself," "a
   fundamental architectural issue"). Link 4.3.
10. **Testing** `[+]` - AgentDojo (arXiv:2406.13352: 97 tasks, 629 security cases) for adaptive
    evaluation; treat the model as an untrusted user (OWASP). Link 4.2. **Emerging**.

## Mention-and-link

- Tool results as untrusted, per-tool scoping, error-observation contract → 2.1. Tool poisoning,
  accidental MCP trifectas, consent gates → 2.4. Widened surface across workers → 3.3. Planner
  hijack and plan integrity → 3.6. Minimal context → 1.5. Approval design → 4.3. Guardrails → 4.4.
  Eval method → 4.2. Sandboxing, computer use → their chapters.
- Failed-guard returns: one sentence linking 3.3 ("a failed worker's error text never crosses");
  no separate section.

## Out of scope

Jailbreak research and safety training internals; gradient-based attack construction and working
payloads; memory poisoning beyond one line; multimodal and hidden-text catalogs beyond naming the
class; general AppSec.

## Maturity summary

- **Standard:** the threat exists; treat retrieved content as untrusted; least privilege.
- **Established:** indirect injection as an attack class (2023 onward, real CVE, real MCP incident);
  the trifecta as an analytic model; human gates.
- **Emerging:** architectural patterns, the Rule of Two, adaptive-attack evaluation, CaMeL.
- **Contested:** any claim that a filter, classifier, system prompt, tagging, spotlighting, or
  instruction-hierarchy training "solves" injection; any quoted catch rate.

**Proposed verdict: split.** Threat **Established**; model-dependent defenses **Contested**;
design-constraint defenses **Emerging**. It holds because removing a leg is deterministic; only
detection is probabilistic. *Last reviewed:* 2026-11.

## Aliases

prompt injection (Willison 2022; OWASP LLM01:2025), indirect prompt injection (Greshake 2023),
lethal trifecta (Willison 2025), Agents Rule of Two (Meta 2025), toxic agent flow (Invariant Labs
2025), LLM scope violation (Aim Labs, via press), agent goal hijack (OWASP Top 10 for Agentic
Applications 2026, ASI01; the agentic list's counterpart to LLM01, not a synonym). Gulli books: no
alias claim made until their security chapters are checked.

## Reader-verifiable anchors

- OWASP LLM01:2025 states the definition and says prevention is unclear.
- GitHub MCP case: a public issue steered an agent holding a private-repo token into leaking private
  data in a public pull request (Invariant Labs, 26 May 2025). Reader can verify from the published
  write-up. Heise disputes the "vulnerability" label; open it and report both views, or drop it.

## Incidents

1. **EchoLeak, CVE-2025-32711**, Microsoft 365 Copilot: zero-click, one crafted email. CVE record
   (MITRE, CNA Microsoft): CVSS 3.1 base 9.3, published 2025-06-11, "AI command injection in M365
   Copilot allows an unauthorized attacker to disclose information over a network." Chain per Reddy
   and Gujral, arXiv:2509.10540: classifier (XPIA) bypass, reference-style Markdown, auto-fetched
   images, a Teams proxy allowed by the content security policy. Report/fix dates (Jan/May 2025) are
   "per Aim Security, via press" or dropped. Maps to egress control; the filter existed and was
   bypassed.
2. **GitHub MCP toxic flow.** Maps to one repo per session, no auto-approve.

## Carrier

**Listing Studio**. Untrusted content: a supplier's spec sheet and feed text (3.3 plants a line in
one). Private data: the merchant's cost and margin rules the pipeline reads. Leak channel: the
launch step that publishes a page and sends the announcement email. Integrity case (no egress): the
price step (set `price_cents` within MAP and margin rules) steered below MAP, or a false compliance
claim on a published listing. The merchant helpdesk reading customer email is the EchoLeak mirror;
optional second example.

## Named-idea candidates (author accepts or strikes)

- **The three-leg test**, credited to Willison, not a coinage. "Remove a leg" is already in 2.4.
- No new coinage recommended.

## Sources

Willison: "The lethal trifecta for AI agents" (2025-06-16); "Prompt injection attacks against
GPT-3" (2022-09-12); "The Dual LLM pattern" (2023-04-25). arXiv: 2302.12173, 2403.14720,
2404.13208, 2506.08837, 2503.18813, 2406.13352, 2510.09023, 2509.10540. OWASP LLM01:2025 and Top 10
for Agentic Applications 2026 (ASI01). Meta, "Agents Rule of Two" (2025-10-31). Anthropic (2025-11-24)
and OpenAI (2025-11-07) prompt-injection posts. Invariant Labs, "GitHub MCP exploited"
(2025-05-26). MITRE CVE record CVE-2025-32711. Not opened as primary: Aim Labs post (403), MSRC.

> **Verify before quoting:** vendor attack-success rates (rotate per model); CaMeL 77% vs 84%
> (abstract only); OWASP wording and numbering; EchoLeak dates beyond the CVE record.

## Author-only questions (defaults in brackets, non-blocking)

1. Named idea: "the three-leg test"? [Default: use the trifecta under Willison's name.]
2. "From production:" callout? [Default: none.]
3. Edits to shipped chapters: 2.1 (See also points injection to 4.4, not 4.6) and 3.3 (its honesty
   note says no fan-out injection literature surfaced; LLM Map-Reduce in arXiv:2506.08837 is close).
   [Default: none; list as PR-body suggestions.]
4. Verdict wording: three-part split? [Default: yes.]
5. Merchant-helpdesk second case? [Default: no.]
6. Patterns: table plus one worked (Dual LLM)? [Default: yes.]

## Second-reviewer pass (Claude Opus; codex unavailable, usage limit)

Verified against: shipped `docs/the-unit/mcp.md` (trifecta paragraph, tripwire caveat),
`docs/composition/fan-out.md` (`render_for_synthesis`, `trust="untrusted"`, honesty note), arXiv
abstract pages for 2403.14720 and 2404.13208, and the MITRE CVE record.

- **M1 (2.4 already teaches trifecta/remove-a-leg): accepted.** mcp.md confirms it; added the
  relationship section, `[ext]` marks, struck "Remove a leg" as a new label.
- **M2 (thesis covers leaks only): accepted.** Two failure modes, Rule of Two co-equal, new thesis.
- **M3 (spotlighting, instruction hierarchy): accepted.** Both papers confirmed; Contested; 3.3 seam note.
- **M4 (paper scope conclusion, exact quote, Plan-Then-Execute caveat): accepted** from the reviewer's
  reading of the paper's tail; not independently re-read, so verify the section 5 wording at drafting.
- **M5 (worked pattern collides with 3.6): accepted.** Dual LLM / Map-Reduce worked; P-T-E one row.
- **m1 (EchoLeak primary facts): accepted.** CVE record confirms 9.3 and 2025-06-11; dates demoted.
- **m2 (ASI01 "Agent Goal Hijack"): accepted** on reviewer's check of OWASP; stub *Also called* line
  needs the same fix (not edited here).
- **m3 (jailbreak vs injection contested): accepted.**
- **m4 (Rule of Two detail, fresh session): accepted.**
- **m5 (verdict on a name): accepted;** dropped, coinage credited.
- **m6 (least-privilege tier clash): accepted;** Standard, dropped the "consensus" verdict.
- **m7 (failure-return contract): accepted;** converted to a link.
- **m8 (contradicts 3.3 honesty note): accepted;** PR-checklist item 3.
- **m9 (human-gate wording): accepted;** reworded, Heise opened or dropped.
- **m10 (workspace language, reproduce-exploit): accepted;** removed; carrier hedge closed.
- **m11 (citation fixes): accepted;** Goodside credit, "12 recent defenses," OpenAI title.

## Orchestrator rulings (Stage 1.6, 2026-11-27)

- **Thesis:** Prompt injection cannot be filtered out, so the only defenses that hold are the ones your code enforces: what the session can read, what it can send, and what it can change after it has read untrusted text.
- **Framing:** two failure modes, leaks (the lethal trifecta) and unwanted actions (state changes with no egress, the Rule of Two's third leg). 4.6 deepens what 2.4 already states (trifecta, remove a leg, no reliable filter) and links back to it rather than re-teaching it.
- **Budget:** standard (about 2,000 to 2,800 prose words, a ceiling).
- **Maturity:** split, three parts: the threat is Established; defenses that rely on the model resisting (filters, spotlighting, instruction hierarchy) are Contested; defenses that constrain by design (removing a leg, Dual LLM, CaMeL-style capability control) are Emerging. Last reviewed 2026-11. One quiet line, argued in prose.
- **Carrier:** Listing Studio. Leak case: supplier spec sheet plus merchant cost and margin data plus the publish and email step. Integrity case: an injected spec sheet steering `price_cents` below the MAP of 39900. No merchant-helpdesk second case.
- **Worked pattern:** Dual LLM (quarantined reader returns typed fields; the privileged side never sees raw untrusted text). Plan-Then-Execute is one table row linking to 3.6.
- **Author-only defaults (conservative, in the PR checklist):** no coinage (the trifecta stays credited to Willison; "three-leg test" not used); no From-production callout; no edits to shipped chapters (2.1 and 3.3 link suggestions go in the PR body); patterns as a table plus the one worked example.
- **Disclosure:** the Stage 1.5 review was a fresh Claude Opus reviewer, not codex (usage limit). Before drafting, verify the design-patterns paper's section 5 scope conclusion and the OWASP ASI01 name; fix the stub's *Also called* line to "Agent Goal Hijack" only if verified.
