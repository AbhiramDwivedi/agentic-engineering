# Coverage map: Long-Running Agents (chapter 9.1)

> Research-derived spec for what the chapter must cover, and where to stop. Angles: vendor and
> primary docs, academic and benchmarks, security and failure modes, practitioner writeups,
> skeptical read, alias sweep, daily-tool, incidents. Skipped: the everyday-engineer angle (SDK
> issue trackers). Bar: definitive but tight. Title note: the stub's H1 is "Long-Running Agents"
> while the slug is `when-you-want-autonomy`; open question 1.

**Thesis.** Across fresh sessions a progress log cannot establish completion: each resumed session
must revalidate the work against acceptance criteria the agent cannot change. (A reasoned
recommendation built on documented premature-completion and regression failures, not an
established law.)

## The mental model

Litmus line: the model chooses the next subgoal and action; code owns authorization, acceptance,
restart and termination. A scheduled batch with fixed work is ordinary engineering, not this
chapter. Three jobs are separate and must not be conflated: model-selected work (inner loop, 2.5),
code-owned verification and retry (outer loop, 3.7), and session relaunch (a wrapper that starts a
fresh session when one ends; it verifies nothing by itself). A long run is the same loops past one
context window, so the harness must carry state, verify, cap spend, and reach a person. Autonomy is
a dial code sets; default to the lowest that meets the need. This chapter keeps to the
cross-session progress contract; the surrounding mechanics are linked, not retaught.

## Must-cover

Ranked. All `[+]` (stub has nothing yet). Evidence is mostly coding campaigns; transfer to the
commerce carrier is reasoned, say so.

1. **Name the dial and the loop** `[+]` - five user roles (operator, collaborator, consultant,
   approver, observer) separate how much the agent does from how capable it is. One short
   paragraph; the spectrum lives in 1.3, modes in 2.6. *Skip it:* "autonomous" is read as "smart".
   **Emerging** (framework). The inner/outer distinction is this reference's framing, offered as
   such. (Feng, McDonald, Zhang, arXiv:2506.12469.)
2. **Why long runs fail** `[+]` - per-step error compounds, and models condition on their own earlier
   mistakes, within the tested execution tasks; thinking mitigates self-conditioning. *Skip it:*
   "just run it longer." **Established** (finding, scoped to the experiments), **Contested** (how
   far it extrapolates). (Sinha et al., arXiv:2509.09677.)
3. **The capability trend, defined first** `[+]` - METR's metric is the human-expert time for tasks a
   model completes at 50% success, not agent runtime. The seven-month doubling is the paper's
   historical fit since 2019 and may have accelerated. A 50% horizon is not a reliable-unattended
   horizon. **Emerging**; extrapolation **Contested**. Cite the live source, freeze no numbers.
   (Kwa et al., arXiv:2503.14499.)
4. **The cross-session progress contract** `[+]` (the core) - fresh context per session; an
   initializer sets up `init.sh`, a progress log, a JSON feature list (all failing), and a commit;
   each later session does one feature and leaves a mergeable state. The startup ritual revalidates;
   shutdown writes a bounded handoff. Failures: building too much at once, a later session declaring
   the job done. **Emerging** (one vendor pattern, widely copied; tested on full-stack web apps only,
   generalization left as future work by its author). (Young, Anthropic, 2025-11-26.) Memory
   mechanics: 5.1, 5.4.
5. **Completion is code-authorized, not self-reported** `[+]` - Young restricts edits to `passes` by
   prompting and asks the agent to self-verify; that is not tamper-proof acceptance. The chapter's
   recommendation (label it as such): agent-written notes are separate from completion records,
   acceptance criteria are protected from the agent, and a completion transition needs independent
   evidence. A relaunch wrapper (Carlini's `while true`) verifies nothing; his checks live in tests
   and CI. Oracles and held-out tests, terse output, fast sampled mode. **Established** (a verifier
   is needed), **Emerging** (what makes one sufficient). (Carlini, 2026-02-05; Young.) Controller
   design: 3.7, gates: 4.3.
6. **Failure returns as a structured handoff** `[+]` - failed work returns to the next session as
   recoverable feedback: failed operation, observed evidence, retryability, remaining budget,
   escalation reason. Recovery mechanics: 7.1. **Emerging** (this reference's contract).
7. **Campaign-wide caps and crash recovery** `[+]` - durable campaign identity; cumulative budget,
   wall-clock and failure accounting that survive relaunch (per-session caps reset and defeat the
   campaign budget); a futility rule (same failure N times); persisted cancellation; reconcile
   uncertain external writes before resuming, since side effects sit outside checkpoint boundaries
   and must be idempotent (LangGraph fault-tolerance docs). One reported run: nearly 2,000 sessions,
   about two weeks, just under $20,000 (vendor-reported). **Standard** (hard stopping conditions);
   contract here, depth in 7.3, 8.7, cost 8.4. (Anthropic "Building effective agents"; Carlini.)
8. **Escalation and the kill switch** `[+]` - blockers, checkpoints, a person who can stop it;
   experienced users shift from approving each action to monitoring and interrupting. Auto mode
   pauses to prompting after 3 consecutive or 20 total classifier blocks. **Established** (practice),
   **Emerging** (classifier-approved autonomy). (Anthropic, "Measuring AI agent autonomy in
   practice," 2026-02-18; permission-modes docs.) Gate design 4.3.
9. **Context across sessions is an attack surface** `[+]` - mistaken agent notes or poisoned tool
   output promoted into trusted instructions persist across sessions; isolation does not stop it.
   Keep provenance and trust separation between instructions, observations and agent summaries;
   hand off only relevant state (token cost and degraded attention). OWASP Agentic Top 10 item
   ASI06, "Memory & Context Poisoning" (page is public). **Emerging.** Depth 5.1, 5.4, 4.6.
10. **Parallel agents, briefly** `[+]` - separate the two arrangements. Cursor reports lock
    contention (20 agents performing like 2 to 3) and benefits from planner/worker hierarchy;
    Carlini uses task-lock files and states he uses no orchestration agent. Together they do not
    establish one winning topology; keep the disagreement as a limit on generalization. **Emerging.**
    (Lin, Cursor, 2026-01-14; Carlini.) Topology: 9.2.
11. **Isolation precedes lower oversight** `[+]` - `bypassPermissions` is documented for containers
    and VMs and offers no injection protection; stated boundaries can be lost to compaction, so use
    deny rules. **Standard.** Sandbox 9.4.

## Mention-and-link

Deployment, supervision, scheduling, always-on: 8.7. Inner loop 2.5; controller 3.7; harness and
modes 2.6; gates 4.3; guardrails 4.4; injection 4.6. Memory and compaction 5.4, 5.1;
observability 8.1; cost 8.4; topologies 9.2; sandbox 9.4; coding agents 9.6; self-modifying
harnesses 9.7; checkpoint and resume 7.3, 7.1.

## Out of scope

Daemon and queue engineering (8.7, 7.1, 7.3); governance (8.6); identity (8.5); benchmark
leaderboards; "zero-human company" claims.

## Maturity summary

- **Standard:** hard stopping conditions; least privilege and isolation before reduced oversight.
- **Established:** compounding error (as scoped); human checkpoints; a verifier is needed.
- **Emerging:** the progress contract, completion records, failure handoff; autonomy frameworks;
  the inner/outer split as framing; classifier-gated approval; planner/worker/judge; horizon trends.
- **Contested:** multi-day unattended agents as production practice; productivity multipliers
  (METR's 19% slowdown, early-2025 tools, not a verdict on later ones); extrapolating 50% horizons.

Chapter verdict: **Emerging** (Last reviewed 2026-11). "Verifier is the bottleneck" is reasoned, not
a settled law.

## Aliases and related

Aliases (each needs a source and author sign-off; the Gulli-book alias sweep is still owed):
long-running agents, long-horizon agents (Anthropic engineering post), unattended or overnight runs.
Related, not synonyms: levels of autonomy (a framework, Feng et al.); the Ralph loop (3.7's
mechanism); always-on (8.7).

## Reader-verifiable anchors

- Permission modes: Shift+Tab cycles `default`, `acceptEdits`, `plan`, with `bypassPermissions` and
  `auto` appearing only when enabled; `dontAsk` is never in the cycle (set with
  `--permission-mode dontAsk`). The sentence "Auto mode reduces permission prompts but does not
  guarantee safety" is on the permission-modes page.
- Young's post shows `claude-progress.txt` and the `passes` field; Carlini's post shows the
  relaunch loop and `current_tasks/` lock files. Reproduce with a bounded loop (step and time cap),
  not the raw `while true`.

## Incidents

- Replit coding agent, July 2025: an assistant reportedly deleted a live production database during
  a declared code freeze (AI Incident Database #1152, an index, not the original). Original
  accounts: The Register 2025-07-21, Tom's Hardware, the user's posts; single-source, not an
  independent investigation. Lesson: a freeze stated in prose is not a control; deny rules and
  dev/prod separation are mitigations, not proof either would have prevented it.
- Carlini: an agent ran `pkill -9 bash` and killed its own loop.

## Carrier

Listing Studio is primary. The Repricer is a sibling surface (carrier-bible), not Listing Studio
running overnight: keep it distinct and state the model-selected decision it shows. A catalog-wide
recategorization campaign is a new scenario and needs carrier-bible approval before it is the
example.

## Code seam

New small module, suggested `campaign` under `listing-studio/`, on top of `outer_loop` (3.7 branch)
and `agent_loop` (2.5). It demonstrates: a progress file read at startup, completion records the
agent cannot write (acceptance checked by code), cumulative budget across relaunches, and an
escalation record. Offline, scripted fake model, as a contract demonstration, never capability
evidence. Depends on 3.7 merging or stacking on it.

## Sources

Young, Anthropic, 2025-11-26, anthropic.com/engineering/effective-harnesses-for-long-running-agents.
McCain et al., 2026-02-18, anthropic.com/research/measuring-agent-autonomy. Carlini, 2026-02-05,
anthropic.com/engineering/building-c-compiler. "Building effective agents," 2024-12-19. Lin, Cursor,
2026-01-14, cursor.com/blog/scaling-agents. Claude Code permission modes,
code.claude.com/docs/en/permission-modes. Kwa et al., arXiv:2503.14499. Feng et al.,
arXiv:2506.12469. Sinha et al., arXiv:2509.09677. Becker et al., arXiv:2507.09089. OWASP Top 10 for
Agentic Applications (2026), ASI06. LangGraph fault tolerance docs. AIID #1152.

> **Verify before quoting:** METR horizon figures move per revision; auto-mode defaults change;
> Carlini cost and Cursor scale figures are vendor-reported; Replit is single-source.

## Open questions for the author

1. Title: keep "Long-Running Agents" or rename to match the slug? (default: keep H1.)
2. Thesis and ceiling: accept the cross-session progress-contract thesis, Emerging? (default: yes.)
3. Carrier: approve the recategorization campaign, or stay on the Repricer? (default: Repricer.)
4. Code dependency: stack on the 3.7 branch? (default: yes.)
5. Aliases: sign off after the alias sweep. (default: none added.)

## Map review (Stage 1.5)

Second-engine review. Verified against Carlini, Young, METR abstract, OWASP ASI06,
permission-modes docs, LangGraph docs, AIID page.

1. Accepted-modified: wrapper verifies nothing (confirmed); litmus line added, 3.7 not conflated.
2. Accepted: Young prompts and self-verifies (confirmed); completion records split, labeled recommendation.
3. Accepted: failure-return handoff added as item 6 (reasoned contract, no new source).
4. Accepted: campaign-wide invariants added; LangGraph idempotency quote confirmed.
5. Accepted: ASI06 page exists and covers it (confirmed); item 9 added.
6. Accepted: scope compressed to prerequisites and links; autonomy and mode items shortened.
7. Accepted: METR defined as human-time horizon (confirmed in abstract).
8. Accepted: inner/outer marked as framing; bottleneck downgraded to reasoned.
9. Accepted-modified: claims scoped to coding campaigns, transfer marked reasoned; no extra SDK check added.
10. Accepted: arrangements separated (Carlini states no orchestration agent, confirmed).
11. Accepted: single thesis stated; budget set at Stage 1.6 (up to 2,800 prose words).
12. Accepted: Repricer kept distinct; recategorization needs bible approval.
13. Accepted: Shift+Tab claim corrected (dontAsk never in cycle, confirmed); bounded reproduction.
14. Accepted: aliases separated from related concepts; sweep noted as owed.
15. Accepted-modified: "reportedly" kept (confirmed); The Register and Tom's Hardware linked via AIID, Fortune not on the AIID page so dropped.
16. Accepted: open questions added; no unpublished references.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **H1.** Keep "Long-Running Agents" and the slug. A rename goes on the checklist.
2. **Thesis and maturity.** Accept the thesis, labelled in the prose as reasoned rather than established. The chapter is Emerging. Stopping conditions and isolation are Standard. Last reviewed 2026-11.
3. **Carrier.** Stay on the Repricer, the existing sibling surface. The recategorization carrier is not added; it goes on the checklist.
4. **Code.** Package `campaign/`, written as a LOCAL equivalent. It must not import `outer_loop` or `agent_loop`, which are unmerged in other PRs, so do not stack. It demonstrates four things:
   - a progress file read at startup;
   - completion records written only by code after an acceptance check, which the agent cannot write;
   - a cumulative budget across relaunches;
   - an escalation record.
5. **Excluded.** No aliases (sign-off is pending), no coinage, no From-production callout. Fortune is dropped as a source.

## Reconcile log (Stage 5)

Prose critic:

1. Fixed: definition, trigger, In short and meta line narrowed to "the model works the task it is handed"; the `todo[0]` reconciliation moved up beside the definition. Code unchanged (option c rejected: the fixed order keeps the tests deterministic).
2. Fixed: the "say it finished" aphorism closer cut.
3. Fixed: framing narration and the chiasmus closer cut; the paragraph ends on the Carlini fact.
4. Fixed: gotcha 5 split in two; auto-mode thresholds cut (release-volatile); the Replit caveat moved into footnote 11.
5. Fixed: thesis-paragraph fragments rewritten as one sentence with clauses.
6. Fixed: "The decisions split cleanly" cut to its two new sentences, placed under the diagram.
7. Fixed: "widely copied" cut (no source); last maturity sentence recast as a plain verdict.
8. Fixed: colon before the five roles; restating clause cut.
9. Fixed: gotcha 7 (developer-productivity RCT) cut as off-thesis; its footnote removed.
10. Fixed: "tokens stand in for dollars here" added at the budget walkthrough.
11. Fixed: "Notice who can change" and "The recommendation here" recast.
12. Fixed: step 5 now says "with the default step limit".
13. Fixed: "The scale is real:" cut; the Carlini numbers stand alone.

Fact checker:

1. Softened: [^6] now supports "common" stopping conditions and "recommended" sandbox testing; meta line matches.
2. Softened: the Replit freeze is one "its user says he had given it in chat".
3. Fixed: "widely copied" cut.
4. Fixed: a sentence after `accept_reprice` says the tests bind it to the two-argument `Check` with a wrapper.
5. Rejected: the zero-price division is not mentioned; the chapter claims no robustness.

Cold reader:

1. Fixed (glossed): compaction, SKU, mergeable state, deny rule, lethal trifecta, autonomy dial, "the books".
2. Fixed: where `current` and `floor` come from, and why never from the candidate.
3. Rejected: cross-references to unmerged chapters stay plain text by convention.
4. Rejected: no relaunch-wrapper code; the budget is at its ceiling and the wrapper is a loop over `run_session`.

Second-engine review: its map findings are dispositioned in the Stage 1.5 section above.
