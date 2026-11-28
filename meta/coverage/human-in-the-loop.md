# Coverage map: Human-in-the-Loop (chapter 4.3)

> Research-derived spec, not a first draft. Sweep: vendor/primary docs, academic, security (OWASP),
> practitioner, skeptical read, alias sweep. Skipped: dedicated GitHub-issue sweep (flagged in
> Incidents). Current as of 2026-11. Gulli books checked via the alias crosswalk, see Aliases.

## The mental model

A human gate is code that decides when to ask; the model never decides whether it needs permission.
The model may *request* a person. Your code owns the trigger, the pause, the saved state, the
resume, and what the reply may change. Pausing is solved: every framework ships it. The hard part
is keeping the gate worth something, so the design questions are which few actions deserve a person,
what that person sees, and what the approval is bound to.

## Who decides (litmus)

| Question | Decider |
|---|---|
| Does this action need a human? | **Your code** (rule on tool, arguments, amount). Model-judged "should I ask?" is a signal, not a control |
| May the model request a human? | Model, via a tool call (12-Factor Agents factor 7). Agentic, advisory |
| Approve, reject, edit | **Human** |
| What happens after the reply | **Your code** (re-validate, re-check, audit) |

Verdict: the gate is a two-person rule, engineering you already know. The agentic part is only the
model-initiated request and the over- and under-asking it brings.

## Must-cover (ranked)

`[+]` new here. Stub has no body.

1. **Gate by consequence, in code** `[+]` Deterministic rule on irreversible, high-value or external
   actions (OpenAI "high-risk actions" trigger, p. 31; OWASP LLM06 "Require user approval"). OpenAI frames
   it as lasting "until confidence in the agent's reliability grows", so gates are graduated.
   Foil: *Building AI Agents* "gate every mutation on a human, no exceptions". *Skip it:* everything or
   nothing is gated. **Standard.**
2. **Where the human sits** `[+]` Approve-before (gate), monitor-and-interrupt (steer; 6.3), review-after
   (sampled audit; 4.2, 8.6). Lead evidence: Anthropic's autonomy post: experienced users auto-approve more
   (about 20% of sessions, over 40% by 750 sessions) and interrupt more (5% to 9% of turns); oversight is "being
   in a position to intervene when it matters". Alias: human-on-the-loop. **Established.**
3. **Pause, persist, resume** `[+]` Durable state plus a reply keyed to the paused call. LangGraph
   `interrupt()` + `Command(resume=...)`: checkpointer and `thread_id`; the node re-runs from its top, so
   side effects before the interrupt repeat; no bare `try/except`; deterministic interrupt order. OpenAI
   Agents SDK: `needs_approval`, `result.interruptions`, `state.approve()/reject()`, `Runner.run(agent, state)`;
   `RunState.from_json()` does not authenticate the snapshot or submitter. ADK: `require_confirmation`,
   `tool_context.request_confirmation`; unsupported with `DatabaseSessionService` and `VertexAiSessionService`
   (verified verbatim); experimental in TypeScript, Go and Kotlin. Native provider forms for the tabs
   (OpenAI remote-MCP `require_approval`; Anthropic: withhold execution, return an error `tool_result`) are
   unverified: coder checks. **Standard** (primitive), uneven across SDKs.
4. **Bind the approval to the action** `[+]` An approval covers a digest of the validated action and
   inputs. Execution re-checks the digest and re-runs policy (the price may have moved in hours). The
   approver is authorized and logged; the requester cannot approve their own request; a duplicate approval
   applies once (idempotency key). Never accept replacement args or state from the client (OpenAI SDK
   page). Expiry resolves to reject. **Established** as practice, thin public evidence.
5. **Reply shapes** `[+]` approve, reject-with-reason (structured result to the model), answer-a-question, and
   **edit-and-resume**, which is **Emerging**: LangGraph has no edit schema (your tool reads the resume
   value), the OpenAI SDK offers none and warns against client args, ADK passes a `payload`. An edited value
   comes from outside the model, so re-validate and authenticate it. Context economy: reason and edit
   re-enter the prompt, so pass them as capped structured fields.
6. **Approval fatigue, with evidence** `[+]` No public figure measures how often people wrongly approve
   agent prompts. Adjacent evidence: Parasuraman & Manzey (complacency in experts), Bansal et al. (explanations
   raised acceptance regardless of correctness, so a rationale string can hurt), and security-warning
   habituation: Akhawe & Felt (USENIX 2013, 25M+ impressions; click-through varied widely by warning type,
   from about a tenth to 70.2% for Chrome SSL, so design moves behavior). Vendor datum: Anthropic reports users
   accept 93% of manual prompts (no method or sample). That is an acceptance rate, not a miss rate: if prompted
   actions are mostly benign, 93% is a working gate. The cost is attention. Invariant Labs notes many users pick
   "Always Allow". Mitigations: fewer, consequence-first prompts; show diff and consequence, not rationale;
   allow-list the low-risk class; cheap rejection. **Established** (failure mode, by analogy), **Emerging** (fixes).
7. **Tiers of autonomy** `[+]` Two sentences only; mode table and evaluation order belong to 2.6. Kept lesson:
   auto-approved calls never reach `canUseTool`, so a gate placed there is silently skipped; a broader allow
   entry must not override a deny band.
8. **Classifier-as-approver is a trade** `[+]` Anthropic auto mode: 0.4% FPR (n=10,000 real traffic) but 17%
   FNR on 52 curated "overeager" actions, drawn from sessions an employee denied or flagged; "not a drop-in
   replacement for careful human review on high-stakes infrastructure". arXiv:2604.04978 (Ji et al., v3): 81.0%
   end-to-end FNR on AmPermBench (128 synthetic DevOps prompts, Sonnet 4.6, CI 73.8-87.4%), 70.3% on 160 in-scope
   actions; 36.8% of state changes out of scope; authors say not directly comparable. Cite neither as "the rate".
   **Emerging** (vendor itself concedes; Contested label dropped, author's call).
9. **Receiving end of escalation** `[+]` What an escalation carries and where it lands (queue, owner, SLA, safe
   default). Failure-threshold triggers belong to 3.7; confidence routing to 3.2. One sentence of calibration
   evidence: verbalized confidence beats token probabilities in RLHF models (Tian et al.); models partly
   generalize P(IK) across tasks but struggle with calibration on new ones (Kadavath et al., abstract). Confidence
   may route to review, never around it. **Emerging.**
10. **What the human sees** `[+]` Exact action, validated args, before/after diff, reversibility, untrusted-source
    flag (4.6: length-capped, treated as data). Model-initiated `request_human_input` is just a tool (12-Factor
    factor 7). **Established.**

## Mention-and-link

4.6 (approval decays; Invariant in one clause, do not retell); 4.4 and 4.6 `guard_action` (code refusal,
`deny`); 2.4 `require_consent` seam; 2.6 (modes, hooks); 3.1 (failed SKU for a person); 3.2 (confidence
routing); 3.3 (irreconcilable conflicts); 3.7 (give-up lands here); 6.3 (UI, steering); 7.3 (checkpoints);
4.2 and 8.6 (override rate, audit). Out of scope: EU AI Act Art. 14 (8.6), RLHF feedback (8.3), computer-use UX (9.5).

## Maturity summary

Split verdict, as 4.6 did: **Standard** for gating consequential actions and pause/resume; **Emerging** for
keeping the gate meaningful (fatigue fixes, classifier approval, confidence routing, edit-and-resume). Argued
sentence: the practice is in OWASP, OpenAI, Anthropic and every SDK, but the evidence that gates stay read is
adjacent-domain and vendor-reported. Author confirms (stub says Standard).

## Carrier placement (Listing Studio)

Same price step, three bands, continuing 4.6's Aldsworth desk (MAP floor 39900). Below the floor: code refusal
(`pricing.check_price`; 4.6 and 4.4 own it). Floor up to 42899: the model proposes, code bands it, a person decides.
42900 and above: auto-applies. A merchandiser (a role, not a persona; "compliance reviewer" is a model persona in the
bible) approves, rejects with a reason returned to the model, or **edits** 40500 to 42900 and resumes. Fixtures avoid
19900 and 44900. The edit is re-banded after the edit. Second beat only if needed: the Repricer, a model-driven
cut, as the genuinely autonomous blast-radius case. "From production:" none assumed; the meta grounding line must read
"companion repo + research" unless the author supplies one.

## Code/demo plan for coder-tester (offline, importable in CI)

CI installs only pydantic, mcp, anyio. **No tested file may import langgraph/openai/anthropic.** Dir
`listing-studio/human_in_the_loop/`; layout like `fan_out/`.
- `gate_policy(action, args) -> auto | ask | deny`; `deny` delegates to `pricing.check_price`. Table tests at
  39899, 39900, 39901, 42899, 42900, and the edit path (an edit to 39899 refused). A broader allow cannot override deny.
- `approval_request`: pydantic model of what the human sees plus action digest and idempotency key.
- `pause_resume` (plain Python): pending request persisted as JSON; resume in a *fresh* object from the serialized
  form; resume re-invokes the step from the top; assert a side-effect counter is 2 when the write precedes the
  pause and 1 after. Tests: stale approval (digest mismatch) refused, duplicate resume applies once,
  requester-cannot-approve.
- `edit_and_resume`, `reject_as_result`, `timeout_default(now=...)` with injectable clock; expiry resolves to reject.
- Illustration files, py_compile-checked only, never imported: `pause_resume_langgraph.py` (`interrupt()` +
  `Command(resume=...)`, in-memory saver, fixed `thread_id`; default tab per house rule) and
  `pause_resume_responses.py` (plain loop with approver callback, the 2.4 seam grown into a durable request).
  Adding langgraph to runtime deps is an author decision. Claim no version pin.

## Proposed thesis and way in

Thesis: **A human gate is worth the interruption only when your code triggers it on consequence, the person
sees what will happen and can edit it, and the approval is bound to the action that actually runs.**

Way in: a gate is only a control if someone reads it. Anthropic reports users accept 93% of manual prompts
(a vendor figure, no method given). Read carefully, that is an acceptance rate: if the prompts are mostly benign,
yes is the right answer. The danger is the rare bad prompt that gets the same reflexive yes, and no public figure
measures that. Quotable line candidate (hedged): "A gate nobody reads is a log entry with extra clicks."

## Aliases

HITL (*Agentic Design Patterns* ch. 13 "Human-in-the-Loop"), approval gate, human approval, tool confirmation (ADK),
permission prompt/mode (Claude Code), human oversight, human-on-the-loop, "contact humans with tool calls",
escalation, human checkpoint, approval gateway, interrupt node/point, `interrupt_before` (static, older LangGraph)
and dynamic `interrupt()`, `permission_policy: always_ask`, retry-escalate-human ladder, `needs_approval`,
`require_confirmation`. Reconcile with the stub's *Also called* line; needs author sign-off.

## Reader-verifiable anchors

1. Claude Code permission modes and deny, ask, allow order. 2. OpenAI Agents SDK `needs_approval` + `result.interruptions`.

## Incidents

Invariant Labs GitHub MCP exploit (2025-05-26): "Always Allow" weakness (shared with 4.6). Candidate for "an
instruction is not a gate": Replit/SaaStr database deletion (July 2025), founder-reported via The Register: he says
he told the agent eleven times not to change code; secondary reporting, attribute as his account. No public
postmortem of a rubber-stamped approval found. GitHub-issue sweep (resume re-execution, `Send`+interrupt, `RunState`
serialization) not run.

## Author-only questions (conservative defaults)

1. Maturity: split verdict (Standard/Emerging) vs stub's Standard. Default: split.
2. Include the 81% FNR stress test? Default: one sentence, third-party, workload-dependent, with denominators.
3. First-hand "From production:"? Default: none.
4. Coinage "consequence gate"? Default: not used as a name.
5. Carrier: same price step with three bands (continuity with 4.6) and a merchandiser approver? Default: yes.
6. Classifier-as-approver labelled Emerging rather than Contested? Default: Emerging.
7. Regulatory oversight: out, pointer to 8.6. Add langgraph as a runtime dep? Default: no.

## Sources (all opened 2026-11-28 unless noted)

- LangGraph Interrupts: <https://docs.langchain.com/oss/python/langgraph/interrupts>
- OpenAI Agents SDK, Human-in-the-loop: <https://openai.github.io/openai-agents-python/human_in_the_loop/>
- ADK Tool Confirmation: <https://adk.dev/tools-custom/confirmation/> (old google.github.io URL 301s here)
- Claude Code permissions: <https://code.claude.com/docs/en/permissions>; Agent SDK permissions: <https://code.claude.com/docs/en/agent-sdk/permissions>
- Anthropic, Claude Code auto mode: <https://www.anthropic.com/engineering/claude-code-auto-mode>
- Anthropic, Measuring AI agent autonomy in practice (2026-02): <https://www.anthropic.com/research/measuring-agent-autonomy> (new users ~20% full auto-approve, over 40% by 750 sessions; interrupts 5% to 9% of turns)
- Ji et al., Measuring the Permission Gate, arXiv:2604.04978 (v3, 2026-10-22)
- Anthropic, Building Effective Agents: <https://www.anthropic.com/engineering/building-effective-agents>
- OpenAI, A Practical Guide to Building Agents (PDF text read, p. 31): <https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf>
- OWASP LLM06:2025 Excessive Agency: <https://genai.owasp.org/llmrisk/llm062025-excessive-agency/>
- 12-Factor Agents, factor 7: <https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md>
- Invariant Labs (2025-05-26): <https://invariantlabs.ai/blog/mcp-github-vulnerability>
- Akhawe & Felt, "Alice in Warningland", USENIX Security 2013 (abstract opened 2026-11-28)
- Replit/SaaStr database deletion, July 2025: <https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/>
- Parasuraman & Manzey 2010, Human Factors 52(3):381-410, doi:10.1177/0018720810376055 (abstract only read)
- Bansal et al., CHI 2021, arXiv:2006.14779; Tian et al., EMNLP 2023, arXiv:2305.14975; Kadavath et al., arXiv:2207.05221; Madras et al., NeurIPS 2018, arXiv:1711.06664

> **Verify before quoting:** the 93% figure (no method stated), all auto-mode error rates, the 81% FNR
> (revised v3), SDK parameter names and Claude Code version-gated behaviors (fast-moving; add "Last reviewed").
> Bansal's "overreliance" is my reading of the abstract. The 4.6 branch is unmerged; recheck the link.

## Second-reviewer pass (Claude Opus; codex unavailable, usage limit)

1. Accept-modified: way in rewritten; 93% verified verbatim, stated as an acceptance rate; no miss-rate figure exists; line hedged.
2. Accept: carrier is the same price step in three bands with new fixtures; Q5 default corrected; 4.6 verified (19900, 44900, 39900, "4.3 covers designing approvals people keep reading").
3. Accept: tests are plain Python and never import langgraph; LangGraph and Responses files are compile-only illustrations.
4. Accept: approver is a merchandiser; "compliance reviewer" is a model persona.
5. Accept: model proposes, code bands, person decides; Repricer demoted to optional second beat.
6. Accept: new item 2 (before/during/after, human-on-the-loop alias, "no exceptions" foil).
7. Accept: new item 4 (digest binding, authorized approver, no self-approval, idempotency, stale-approval tests).
8. Accept-modified: split verdict; author confirms.
9. Accept: item 7 cut to two sentences, 2.6 linked.
10. Accept: escalation item narrowed to the receiving end; 3.7 and 3.2 linked; second carrier beat dropped.
11. Accept: `ask` is the new code, `deny` delegates to `pricing.check_price` (present in the tree); 2.4 seam referenced.
12. Accept: counts replace the unshippable test, hook test recast, concrete numbers, injectable clock, floor edge table.
13. Accept: edit-and-resume rated Emerging.
14. Accept-modified: Replit lead checked against The Register (founder's account only, attributed); issue sweep still not run, stated.
15. Accept-modified: Akhawe & Felt abstract opened and cited; Anderson et al. CHI 2015 not verified, dropped; clinical alarm fatigue left unsourced.
16. Accept: denominators added; Contested dropped for Emerging, put to the author.
17. Accept: ADK page re-opened; `DatabaseSessionService` and `VertexAiSessionService` verbatim; experimental in TypeScript, Go, Kotlin.
18. Accept: Kadavath wording follows the abstract ("partially generalize", "struggle with calibration on new tasks").
19. Accept-modified: aliases extended from the reviewer's book crosswalks, not re-opened here; author sign-off.
20. Accept: grounding line flagged in the carrier section.
21. Accept-modified: provider-native forms noted as unverified; coder verifies before use.
22. Accept: context-economy line added to item 5.
23. Accept: body cut to budget via items 7, 9, 10.
24. Accept: 3.1 added to the link list.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis and way in as proposed. The 93% figure is quoted as an acceptance rate with "no method stated"; the chapter does not imply a miss rate.
2. Maturity: split line (approval gates Standard; classifier-as-approver Emerging), with "Last reviewed". The stub's single Standard goes in the PR checklist.
3. Carrier: the same Aldsworth price step 4.6 uses, now in three bands. The prose acknowledges 4.6 in one sentence: 4.6 asks what an attacker can make the step do; 4.3 asks who signs off on a legitimate change. Fixtures avoid 4.6's 19900 and 44900.
4. The Replit/SaaStr case is 2.6's way in. Here it gets at most one attributed sentence, pointing to 2.6 for the harness lesson.
5. No From-production callout and no coinage. The 81% FNR stress test is included only if the fact-checker can trace it to a primary source; otherwise it is cut.
6. Code: tested pause/resume is plain Python, importing only declared dependencies; LangGraph `interrupt()` and Responses approval are compile-checked illustration files. LangGraph is not added as a dependency for 4.3.
7. EU AI Act human-oversight obligations: one pointer to 8.6, not covered here.
8. Shipped chapters are not edited.
