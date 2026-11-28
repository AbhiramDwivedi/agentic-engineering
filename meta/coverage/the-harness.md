# Coverage map: The Harness (chapter 2.6)

> Research-derived spec, not a draft. Sweep run: vendor/primary docs, security (OWASP), practitioner
> writeups, skeptical read, alias sweep, daily-tool, incidents. Skipped: academic benchmarks (no
> harness-specific one that is not vendor-reported). Alias sweep: *Building AI Agents* checked;
> *Agentic Design Patterns* pending. Neighbours read: 2.1-2.5, 3.7, 4.6 (2.5 and 3.7 unmerged, may move).
> Review and trim **Must-cover**; that sets scope. Budget row: hub with code, standard pattern (~2,000-2,800 words).

## The mental model

An agent is the model plus everything that is not the model; that remainder is the harness (LangChain:
"every piece of code, configuration, and execution logic that isn't the model itself"). It has two
halves. **Steering** is text the model reads and can ignore: system prompt, tool descriptions, skills,
re-injected rules. **Enforcement** is code the model cannot argue with: permission verdicts, sandbox,
hooks, caps, the compaction trigger. The reader should leave able to say, for any rule, which half it
lives in, and to move every must-hold rule into enforcement. The loop (2.5) is one component. "Harness"
also means an eval or test harness; that sense belongs to 4.2.

## Must-cover

Ranked. Each: why, failure if skipped, maturity, lead citation. All `[+]`.

1. **Definition, the two halves, boundary** - Agent = Model + Harness. A *framework* is the kit; a
   harness is what you assemble from it or a product ships pre-assembled (Claude Code, Agent SDK); the
   blur is real (LangChain calls deepagents a "harness building library"), so state it as the chapter's
   own distinction and link 1.6. Guides (feedforward) and sensors (feedback) map onto steering and
   enforcement. *Skip:* "harness" stays a synonym for wrapper. **Standard** for the idea. LangChain
   "Anatomy"; Boeckeler; OpenAI "Harness engineering".
2. **Permissions: mediate every call, and the mode dial** - deny, then ask, then allow, first match
   wins; a denial returns to the model as a tool result. Modes (`default`, `acceptEdits`, `plan`, `auto`,
   `dontAsk`, `bypassPermissions`) change the default verdict for unmatched calls; `bypassPermissions`
   removes the seat. Absent beats denied: a tool never offered cannot be called. **Standard.** OWASP
   LLM06 (complete mediation); Claude Code permissions. Re-verify mode names at draft time.
3. **Execution boundary (sandbox) vs approvals** - the sandbox limits what a command *can* do
   (filesystem and network, both); approvals decide when to *ask*. Pattern rules on command text are
   fragile ("Bash permission patterns that try to constrain command arguments are fragile";
   `sh -c` slips past `Bash(rm *)`), so an allowlist on `argv[0]` is not a boundary: "the allowlist that
   isn't". Credentials stay outside. **Standard.** Anthropic sandboxing post (84% fewer prompts,
   vendor-internal); Codex: default `workspace-write` "keeps network access turned off"; Managed Agents.
   Depth in 9.4.
4. **Hooks: deterministic code at fixed points, and their failure mode** - before/after tool, model,
   stop, compaction. Short-circuit semantics (ADK `before_tool_callback` returning a dict skips the
   tool; Claude Code exit 2 blocks, and a hook's `allow` cannot override a deny or ask rule). A blocking
   hook's reason must reach the model as a readable result (also `PermissionDenied`). **Know the failure
   mode:** Claude Code treats exit 1 "as a non-blocking error" and the action goes ahead (a hook can opt
   into blocking on failure); Codex auto-review "fail[s] closed". A policy hook with a bug is a hook that
   is not there. **Standard.** Hooks docs; ADK callbacks; LangChain middleware. Seam to 4.4: 2.6 owns the
   interception point and its failure mode, 4.4 owns what the check decides.
5. **Ceilings and the veto live outside the loop body** *(extends 2.5 and 3.7; pointer only)* - 2.5
   owns the step cap, exits, `FALSE_DONE`, the `max_turns`/`max_budget_usd` defaults and one-response
   overshoot; 3.7 owns the Stop hook and `/goal`. New here: these are seats configured in settings,
   hooks and SDK options, not the `for` bound, and the companion test only asserts the harness passes
   its limits through to 2.5's loop. OWASP LLM10 is adjacent, not an authority on agent caps. **Standard.**
6. **In-run verification** - sensors that return output written for the model (OpenAI: lint messages
   "inject remediation instructions into agent context"); computational vs inferential checks; run the
   check in the harness, not as a tool the model chooses to call, or it can skip it (*Building AI Agents*
   ch.15). Premature victory is the documented failure. 3.7 owns cross-run verify-and-retry.
   **Established** (computational); **Contested** (behaviour verification; Boeckeler: AI-written tests
   "not good enough yet"). Anthropic "Effective harnesses".
7. **Model-as-approver** - a model in a code seat: Claude Code auto mode ("a background classifier checks
   that they align with your request"), Codex `approvals_reviewer = "auto_review"` (default `"user"`),
   `prompt`/`agent` hooks, `/goal`. Model-decides, carries an error rate. **Emerging.**
8. **The context pipeline: compaction trigger and re-injection** - the harness decides when to compact,
   what survives (pinned items, `PreCompact`), and re-injects persistent rules. The Agent SDK warns early
   instructions "may not be preserved". Depth in 5.4, 1.5. **Established.** Context economy: steering
   pays tokens and attention on every request (prompt, tool schemas, skills, re-injected rules), so
   inject the minimal relevant subset (1.5, 2.3).
9. **Harness assumptions go stale** - each component encodes a belief about what the model cannot do;
   Managed Agents says resets built for Sonnet 4.5's "context anxiety" became "dead weight" on Opus 4.5.
   Re-test on model change. **Emerging** (one vendor's account).

## Mention-and-link

Durable state 5.1/7.3; tracing 8.1; loop and exits 2.5; verify-and-retry 3.7; tools 2.1; MCP 2.4; skills
2.3; human approval 4.3; guardrails 4.4; injection 4.6; sandboxing 9.4; compaction 5.4; cost 8.4;
credentials 8.5; long-running agents 9.1. Out of scope: building a sandbox runtime, per-product settings
reference, multi-agent coordination, evaluating harness changes (4.2).

## Who decides (litmus)

Enforcement is the **code-decides** half by construction. Steering is text the model reads and can
ignore: it makes a bad call less likely and guarantees nothing. Seat 7 is the exception: a model
sitting in a code seat is model-decides and gets the usual error rate. Rule: put every rule that must
hold in enforcement. Deflation, followed by the constructive answer: harness engineering is mostly
engineering you know (policy enforcement point, interceptor chain, resource limits); what is new is
that the caller is a non-deterministic model that reads the refusals.

## Maturity verdict

Split meta line, in 2.5's form: **Standard** (mediated tool calls, sandbox, hooks, caps) ·
**Established** (in-run computational checks, compaction trigger, durable state) · **Emerging**
(model-as-approver, pruning stale components) · Contested noted in prose (behaviour verification; "the
harness matters more than the model"). The verdict grades techniques, not the age of the name: the
mechanisms are shipped by Anthropic, OpenAI, Google and LangChain and backed by OWASP, while efficacy
claims are vendor-reported (84% internal; Terminal Bench "Top 30 to Top 5", LangChain self-reported;
OpenAI "0 lines of manually-written code"). Carries "Last reviewed". The stub says Standard.

## Carrier placement (Listing Studio)

Do **not** retell the below-floor price story (2.5, 3.7, 4.6 own it). Use a bulk supplier ingest: one
spreadsheet, a few hundred SKUs, carrier steps 1 and 9, a long run that writes drafts and has a
`publish` tool that touches the live catalog. Seats exercised: `publish` absent from the session (not
merely denied); a PostToolUse check on draft fields; the sandbox parsing untrusted supplier files with
network off; a spend cap ending the run; and the "write to `draft` only" rule lost after compaction
unless pinned. Sibling surfaces only if needed. "From production": none unless the author supplies one.

## Code / demo plan (coder-tester; offline, scripted model, no network)

Package `listing-studio/harness/`, provider-neutral; import 2.5's loop if merged, else a flagged copy.
Anchors: `policy` (deny, ask, allow, first match; default deny; denial fed back as `is_error`; absent
tools); `hook` (`pre_tool`/`post_tool`/`on_stop`; fail-closed on exception as an argued choice; `allow`
never beats deny or ask); `limits` (passes caps to 2.5's loop; timeout via an injected clock); `compact`
(trigger, pinned items, `pre_compact` archive); `trace` (one event per decision).
Tests: `publish` absent and draft-only rule survives compaction; deny returns as a result; a raising
hook blocks; the hook's reason is readable by the model; `allow` does not beat deny/ask; limits pass
through. Tabs depart from the LangGraph default on purpose: raw APIs have no hook or permission layer.
LangGraph via `create_agent` middleware (`wrap_tool_call`), OpenAI Agents SDK tool guardrails, Anthropic
Agent SDK `PreToolUse` (verify names against live docs). One SVG within ~800px: steering and enforcement zones.

## Proposed thesis

Every rule that must hold belongs in the enforcement half of the harness, where the model cannot
argue with it; the steering half (prompt, tool descriptions, skills) only makes the model likelier to
propose something enforcement will accept.

## Candidate way in

A coding agent was told repeatedly not to change anything during a code freeze, and reportedly deleted
a live production database anyway: the freeze existed only in the prompt (public case, AIID 1152; hedge
"reportedly"). Open on that, then the distinction. Listing Studio comes second, glossed on first use.

## Named-idea candidates (author accepts or strikes)

- "Model proposes, code disposes": near-quote of *Building AI Agents* ch.15 ("The model proposes. The harness decides whether to execute."); credit it, not a coinage.
- "The seat test": who sits in each deciding seat, and can they be talked out of it? Default: unnamed.

## Aliases

Harness engineering, agent harness (OpenAI, LangChain, Fowler, Anthropic); scaffolding (unverified);
middleware (LangChain); callbacks (ADK); hooks (Claude Code); agent-computer interface (SWE-agent,
narrower); guides and sensors (Fowler); execution boundary, verification loop, context pipeline
(*Building AI Agents* ch.15); harness engineer (its Appendix B); harness-to-loop progression (to 3.7).

## Reader-verifiable anchors

1. Claude Code: a matching deny rule beats a `PreToolUse` hook's `allow`, and a matching ask rule still prompts.
2. Codex: "the default `workspace-write` sandbox mode keeps network access turned off".

## Incidents

- **Replit agent database deletion, 2025-07-18.** Agent "reportedly deleted a live production database
  during an active code freeze, despite receiving repeated instructions not to make changes" (AIID 1152).
  Environment-separation details were not verified at a primary source; omit or hedge.

## Open questions (author-only, conservative defaults)

1. Maturity: split line (default) vs single Established.
2. Hooks as spine vs a seat table. Default: table first, hooks as main mechanism.
3. Dependency on unmerged 2.5 code. Default: import if merged, else flagged copy.
4. Model-as-approver: must-cover seat 7 (default) vs Gotcha.
5. Any first-hand "From production" story. Default: none.
6. Edit 2.5's meta wording ("the harness around it") to "the loop is one component"; PR checklist item, not a shipped-chapter edit.

## Sources (all opened 2026-11-28 unless noted)

- OpenAI, "Harness engineering" (Feb 11 2026): https://openai.com/index/harness-engineering/
- Anthropic, "Effective harnesses for long-running agents" (Nov 26 2025): https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- Anthropic, "Managed Agents" (Apr 8 2026): https://www.anthropic.com/engineering/managed-agents
- Anthropic, "Making Claude Code more secure and autonomous with sandboxing" (Oct 20 2025): https://www.anthropic.com/engineering/claude-code-sandboxing
- LangChain, Trivedy, "The Anatomy of an Agent Harness" (Mar 10 2026): https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
- Boeckeler, "Harness engineering for coding agent users" (Apr 2 2026): https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html
- Claude Code hooks: https://code.claude.com/docs/en/hooks ; permissions: https://code.claude.com/docs/en/permissions
- Claude Agent SDK, "How the agent loop works": https://code.claude.com/docs/en/agent-sdk/agent-loop
- Codex approvals and security: https://learn.chatgpt.com/docs/agent-approvals-security (redirected from developers.openai.com/codex/agent-approvals-security)
- Google ADK callbacks: https://adk.dev/callbacks/ ; LangChain middleware: https://docs.langchain.com/oss/python/langchain/middleware/overview
- OWASP LLM06 Excessive Agency: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ ; LLM01: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- Yang et al., SWE-agent, arXiv:2405.15793
- Gulli and Nawalgaria, *Building AI Agents* (2026 public draft), ch.15 and Appendix B; Anthropic permission-modes and Codex auto-review pages as above.
- Replit incident: https://incidentdatabase.ai/cite/1152/ ; Fortune 2025-07-23 (search result only, not opened)

> **Verify before quoting:** hook event lists and permission-mode names change often (re-open docs);
> the 84%, Terminal Bench rank and million-line figures are vendor-reported, cite as such; Replit
> counts conflict by outlet; Codex docs moved domains; Fortune and Salesforce/Google "agent harness"
> pages were seen only in search results. 2.5 and 3.7 text may change before merge.

## Second-reviewer pass (Claude Opus; codex unavailable, usage limit)

Verified against the live hooks, Codex approvals and permissions pages and the 2.5 text, 2026-11-28.

1. M1 accepted: carrier and way in replaced (bulk ingest; public code-freeze case); price floor left to 2.5/3.7/4.6.
2. M2 accepted: broad definition, steering vs enforcement halves, thesis broadened, eval-harness sense pointed to 4.2.
3. M3 accepted: item 5 cut to a pointer at 2.5/3.7; companion test only passes limits through.
4. M4 accepted: permission modes added to item 2 (names verified, churn flagged); model-as-approver promoted to item 7, both products cited.
5. M5 accepted-modified: fail-open vs fail-closed in item 4; verified, but a Claude Code hook can opt into blocking on failure, so the contrast is the default only.
6. M6 accepted: split maturity line; verdict grades techniques not the name's age.
7. M7 accepted: aliases added, proposes/decides near-quote credited, `argv[0]` allowlist and run-check-in-harness points added; Agentic Design Patterns sweep marked pending.
8. M8 accepted: out-of-repo wording removed.
9. m1 accepted: framework/harness line framed as the chapter's own distinction, link 1.6.
10. m2 accepted: "loop is one component" chosen; 2.5 meta rewording parked as author checklist item 6.
11. m3 accepted: "dead weight" quoted, both models named.
12. m4 accepted: durable state and tracing demoted to mention-and-link.
13. m5 accepted: 4.4 seam line added to item 4.
14. m6 accepted: context-economy line added to item 8.
15. m7 accepted: blocking-hook reason reaching the model, `PermissionDenied`, plus a test.
16. m8 accepted-modified: tab departure justified; `tool_choice` dropped; Agents SDK guardrail and middleware names to be re-verified at draft time.
17. m9 accepted: injected clock, compaction/absent-publish test, allow-vs-deny/ask test; SVG grouped into two zones.
18. m10 accepted: figures hedged as vendor-reported; Replit details hedged; Codex anchor restricted to the verified sentence.
19. m11 accepted: budget row stated (hub with code, ~2,000-2,800).

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis and way in as proposed. The AIID 1152 case is hedged with "reportedly"; no environment details beyond the incident record.
2. Maturity: split line, as proposed, with "Last reviewed".
3. Scope: 2.6 is the in-run harness (what code enforces around one run). Cross-run verify-and-retry belongs to 3.7; stopping and "done" get one pointer each to 2.5 and 3.7.
4. Code is self-contained under `listing-studio/harness/`: 2.5 is not merged, so the loop is a small local copy, flagged in a comment. Tests are offline and import only declared dependencies; any LangGraph, OpenAI or Anthropic tab is an illustration file, compile-checked only.
5. No From-production callout. No coinage: "model proposes, code disposes" is credited to *Building AI Agents* ch.15; "the seat test" stays unnamed.
6. Model-as-approver is covered as a seat, marked Emerging.
7. Shipped chapter 2.5 is not edited; the wording note goes in the PR checklist.
