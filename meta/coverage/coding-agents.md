# Coverage map: Coding Agents (chapter 9.6)

> Research-derived spec for what the chapter must cover so a reader can run a coding agent on a
> real repository safely and know which claims about it are proven. Sweep angles run: vendor docs,
> academic and benchmarks, security and incidents, skeptical read, alias sweep, daily-tool angle,
> everyday-engineer gotchas. Skipped: a dedicated practitioner-blog pass; the Gulli alias sweep
> is unverified (no public chapter locators confirmed). Review and trim **Must-cover**.

## Thesis

A coding agent is only as reliable as the acceptance checks it cannot silently weaken, so a
green run has to be read together with any change the agent made to the checks, and the rules
that must hold belong in enforcement, not in instructions.

## The mental model

Code can be compiled, linted and tested, so a coding agent's loop gets partial feedback from the
environment (2.5). Partial: tests miss requirements, can be wrong, and the agent can edit them.
Anthropic's own appendix keeps human review for the broader requirements. The model chooses
searches, edits and next actions, which is what makes it agentic; the harness (2.6) permits
execution; a deterministic verify-and-retry wrapper is code deciding and belongs to 3.7.
Classify by who decides, not by packaging (CLI, IDE, chat); a fixed workflow may contain agentic
workers. Instructions are context the model may ignore; permissions, hooks and an execution
boundary are what hold.

## Must-cover

Ranked; maturity per item. Ten entries, merged where they overlapped; generic mechanisms are
pointers to siblings.

1. **A verifier in the loop, and its limits** - code is "verifiable through automated tests";
   agents iterate on test results. Cover verifier validity, the agent editing tests, independent
   acceptance checks, requirements tests miss. *Skip it:* credit the model for the suite.
   **Established** for bounded tasks; **Emerging** where transfer is unmeasured. (Anthropic,
   Building Effective Agents, appendix 1; SWE-agent arXiv:2405.15793.)
2. **The interface is part of the agent** - SWE-agent: an agent-computer interface (edit,
   navigate, run) with concise feedback and error recovery lifts results over a plain shell.
   Include one failure-return example separating test failure, unavailable environment,
   timeout and permission denial, with bounded diagnostics and whether state changed; retry
   mechanics link to 2.5/3.7. **Established.** (SWE-agent sections 2-3; Yang et al., 2024-05-06.)
3. **The instructions file, and what it is not** - CLAUDE.md / AGENTS.md carry build and test
   commands. Docs call it "context, not enforced configuration"; target under 200 lines. Cover
   which file applies in a monorepo, nested precedence, and how to check it loaded or conflicts
   (vendor-specific). Evidence it can hurt: context files "do not generally improve task
   success", over 20% more inference cost, human-written beat generated. **Established**
   (practice); **Emerging** (what makes one help). (Claude Code memory docs; agents.md;
   arXiv:2602.11988, Gloaguen et al.) Seam: 5.1, 1.5 context; 2.3 skills.
4. **Hooks and permissions: enforce, do not ask** - a `PreToolUse` hook exiting 2 blocks that
   call and stderr goes back to the model. Scope it: the guarantee covers the matched tool
   only; a path check on edit tools does not stop a subprocess write; any exit other than 0 or 2
   does not block unless `onFailure: "block"` is set; timeouts do not block by default.
   Permission rules: deny, ask, allow, first match wins. **Established.** (Claude Code hooks,
   permissions pages.) Seam: 2.6, 4.3, 4.4.
5. **Plan, then act** - read-only first, approve the plan, then edit; 3.6 with a human at the
   gate. *Skip it:* confident wrong solution. **Established** as a practice; general effect
   **Emerging.** (Claude Code best-practices.) Seam: 3.6.
6. **Give it a check, read the diff** - tests, linters, type checks as done-condition, plus
   review of any change to them; "said it was done and it wasn't" is the vendor's own failure.
   `claude -p` is a non-interactive entry; the outer loop is code (3.7), only if you build it.
   **Established.** Seam: 3.7, 9.1.
7. **Injection with repo access, and the execution boundary** - agents read issues, READMEs,
   dependencies and tool output. State the trifecta conditionally: if the agent also reaches
   sensitive data and an exfiltration channel, injection becomes data theft. Distinguish
   exfiltration prevention (egress limits, no secrets in workspace) from merge protection
   (scratch branches, required review), which limits repository damage but does not break the
   trifecta. Run tests inside an enforced, disposable boundary with scoped credentials; treat
   config, build scripts and hooks as executable, not ordinary edits. GitHub's cloud agent
   pushes to one branch (the PR branch if invoked by `@copilot` on a PR, else `copilot/`) with
   a default firewall. **Established** risk. (Willison 2025-06-16; OWASP LLM01/LLM06; GitHub
   docs, responsible use of agents.) Seam: 4.6 theory, 9.4 sandbox.
8. **Gate the irreversible action** - ask on push, deploy, destructive git, database and cloud
   calls; separate dev and prod credentials. Edits and test runs are free only inside item 7's
   boundary. **Established.**
9. **Measured value, honestly** - randomized trial, 16 experienced developers, 246 tasks:
   tasks took 19% longer while they believed 20% faster (early-2025 tools). METR's 2026-02-24
   update calls its new data an unreliable signal. OpenAI stopped reporting SWE-bench Verified
   (2026-02-23): of 138 problems o3 did not consistently solve over 64 runs, 59.4% had
   material test or description flaws, and contamination appeared in every frontier model
   tested. The audit is of that hard subset, not Verified overall. **Contested** (productivity
   effect size). (arXiv:2507.09089, Becker et al.; SWE-bench arXiv:2310.06770.) Seam: 4.2.
10. **Cost and attention** - long sessions cost tokens and degrade attention before the window
    fills; the coding mitigation is targeted search and selective file and output loading;
    compaction links to 5.4, its trigger to 2.6. **Established.** (Anthropic, effective context
    engineering; Claude Code docs.)

## Mention-and-link

Agent loop 2.5, harness 2.6; skills and MCP 2.3, 2.4 (supply-chain risk one line plus 4.6);
worktrees and subagent review 3.3, 3.4, 9.2; sandboxes 9.4; computer use 9.5; long runs 9.1;
self-modifying harnesses 9.7; human review as bottleneck 4.2, 4.3. Prose-budget row for 9.6 to
be declared before drafting.

## Out of scope

Tool-by-tool comparison or leaderboard; IDE autocomplete and chat-assist; writing an agent from
scratch (2.5); prompting craft for code (4.1).

## Maturity summary

- **Established:** feedback-driven coding in bounded settings; ACI design; instruction files
  (practice); hooks and permissions; gating irreversible actions; injection as a risk.
- **Emerging:** what makes an instructions file help; general effect of plan mode; transfer of
  verifier gains beyond bounded tasks.
- **Contested:** productivity effect size; benchmark scores as capability; "autonomous software
  engineer."

Verdict: **Established for the bounded practices, Emerging where transfer is unmeasured,
Contested for the productivity claim.** Badge **Established** with a Last-reviewed date and the
split argued in prose. (Superseded at Stage 5: see the reconcile log, item F5.) Not "Standard": that tier means an accepted default, not that a category
exists. Fleets, spec-first workflows and repo memory carry no verdict until individually sourced.

## Aliases

Synonyms: coding agents, CLI agents, agentic coding (stub), autonomous software engineer
(vendor marketing; contest by the litmus). Related terms, not synonyms: AI pair programmer
(broader), vibe coding (a mode of use, coined by Karpathy; Willison distinguishes it from
reviewed AI-assisted coding), spec-first, AGENTS.md, rules files, headless mode and `claude -p`,
`/loop`, harness engineer (operator role, 2.6).

## Reader-verifiable anchors

1. A `.claude/settings.json` `PreToolUse` hook on the edit tool that exits 2 for a protected
   path blocks that tool's edit and returns stderr to the model. It does not cover writes by a
   shell subprocess; check that separately. The same rule in CLAUDE.md is not enforced.
2. Copilot cloud agent push scope depends on invocation path (item 7; GitHub docs).

## Incidents

Each labeled by evidence status.
- **Replit / SaaStr, July 2025.** Press report of user claims (The Register 2025-07-21): an
  agent deleted a production database during a stated freeze. Counts disputed; CEO promised
  separate dev and prod databases. Maps to: freeze in prose is not enforcement.
- **Amazon Q Developer extension, July 2025 (CVE-2025-8217).** Vendor bulletin AWS-2025-015: a
  broadly scoped token let an attacker merge malicious code into 1.84.0; AWS says it did not
  execute. A supply-chain case; the CLI `--trust-all-tools` lesson is separate.
- **Cursor CurXecute, CVE-2025-54135 (Aim Labs, 2025-08).** Researcher disclosure: a crafted
  Slack message retrieved through MCP led to an MCP config write and execution before approval;
  fixed in 1.3.9. A demonstrated exploit, not observed customer harm. Repository-file entry
  vectors are a separate hypothesis. Maps to: config files are code.
- **Nx "s1ngularity", 2025-08-26.** Nx postmortem (2025-09-05): malicious npm versions, live
  about 4 hours, ran a post-install script that scanned for secrets and tried local AI CLIs;
  root cause was an injectable `pull_request_target` workflow and a leaked publish token. The
  postmortem does not say which flags were used; do not claim permission-skipping from it.

All four feed the Incident File catalog.

## Named-idea candidates

None offered. Name ideas only once the corrected argument earns them. Credit ACI to SWE-agent
and the lethal trifecta to Willison.

## Carrier

An external coding agent maintaining the Listing Studio repository (fix a failing test in the
pricing module), or the Repricer's codebase as the repo-write example. Coding agents stay
external to the product surfaces; the carrier is the repo, not the pipeline.

## Sources

Vendor: Claude Code docs (memory, hooks, permissions, best-practices); agents.md; Anthropic
Building Effective Agents (2024-12-19) and effective context engineering; GitHub Copilot
responsible use of agents. Research: arXiv:2310.06770, 2405.15793, 2507.09089, 2602.11988; METR
2026-02-24; OpenAI 2026-02-23. Security: Willison 2025-06-16; OWASP LLM Top 10 2025;
AWS-2025-015; Aim Labs / Tenable CVE-2025-54135; The Register 2025-07-21; Nx postmortem.

> **Verify before quoting:** hook and permission names and the 200-line guidance change with
> releases. The CurXecute chain and fix version were not re-opened at fold time (disclosure page
> returned empty); re-open before quoting.

## Open questions for the author

1. Badge: Established with the split argued in prose (recommended), or another tier?
2. Do the four incidents go in one Gotchas paragraph or only the Incident File?
3. Code: none (default), or a small tested hook config as a listing?
4. Aliases and any named idea need your sign-off.

## Map review (Stage 1.5)

Second-engine review, 17 findings, checked against primary sources where reachable.

1. Accepted: verifier overclaim; thesis rewritten as falsifiable, item 1 covers verifier validity.
2. Accepted: item 8 and 7 now require an enforced disposable boundary; config and hooks treated as executable.
3. Accepted-modified: failure-return example added to item 2; kept to one example.
4. Accepted: instruction discovery and scope added to item 3; vendor-specific.
5. Accepted: item 10 covers attention cost and targeted retrieval.
6. Accepted: litmus allocation added to the mental model.
7. Accepted-modified: items merged and trimmed, prose-budget row flagged; ten entries kept.
8. Accepted: "Standard as a category" removed; fleets, spec-first, repo memory unrated.
9. Accepted: trifecta stated conditionally; scratch branch limits damage only.
10. Accepted: verified against the hooks page (exit 2 blocks, other codes do not, `onFailure`).
11. Accepted: verified against GitHub docs (PR branch via `@copilot`, else `copilot/`).
12. Accepted: verified against OpenAI post (138 hard-subset problems, 59.4%); percentage kept with its selection criterion, scoped to the audited subset.
13. Accepted-modified: Slack-via-MCP chain matches the reviewer's account; the disclosure page could not be opened, so it is flagged unverified.
14. Accepted: evidence status labelled; Nx postmortem opened and the unsupported flags claim dropped.
15. Accepted-modified: synonyms split from related terms, Karpathy credited; Gulli locators unavailable, marked unverified.
16. Accepted: both named ideas removed.
17. Accepted-modified: Repricer name used, production-callout invitation removed.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Maturity.** The badge is Established (revised at Stage 5 to a two-tier verdict; see the reconcile log, item F5). The prose argues the split: the bounded practices are Established, transfer where it is unmeasured is Emerging, and the productivity claim is Contested. Last reviewed 2026-11.
2. **Code.** None. A hook config may appear as an illustrative fragment in the prose, labelled as untested, with no listing-studio package. A tested hook config goes on the author checklist.
3. **Incidents.** One Gotchas paragraph. The CurXecute chain is quoted only if the writer verifies it on a primary page; otherwise cut it. Drop the Nx permission-skipping claim.
4. **Excluded.** No aliases, since the Gulli locators are unverified. No coinage, no named idea, no From-production callout.

## Reconcile log (Stage 5)

Fact-check (F), prose critique (P), cold read (C), second-engine review (S). Each finding was
checked against the chapter text or the primary source before acting.

- F1 Plan mode exception: fixed; the interactive-terminal bypass-permissions exception added.
- F2 Cursor footnote credit: fixed; advisory re-opened, reporters credited as hxofir-a and MaccariTA.
- F3 agents.md nearest-file quote: fixed; not verbatim, paraphrased without quote marks.
- F4 "strongest evidence" superlative: softened to "easiest to check automatically", which the citation supports and the maturity paragraph no longer contradicts.
- F5 Maturity: changed. Headline is now **Emerging (coding agents overall) / Established (the harness practices)**, argued in one sentence in the prose; productivity stays Contested. Supersedes ruling 1; on the author checklist.
- F6 Plan mode "unmeasured": softened to "We found no measurement".
- F7 context-eng truncated quote: rejected; the quoted words are a verbatim run of the source sentence.
- F8 `Edit|Write` omits other edit tools: rejected; tool names vary by version and the shell-bypass sentence already covers the class.
- P1 Hook overclaim: fixed (same as F4).
- P2 Header "enforce, do not ask" vs the ask-rule advice: fixed; retitled "rules that hold".
- P3 Apparatus narration in gotchas 1 and 2: fixed; both catalog-filing clauses cut.
- P4 Gotcha 2 header vs examples: fixed; retitled "A boundary nobody enforces is a wish", and a closing sentence names the unenforced boundary in each case.
- P5 Worked-run closing overclaim: fixed; it now names both code decisions (plan gate, hook) and says the sandbox and review cover the shell path the hook misses.
- P6 Gotcha 3 restates the hook paragraph: fixed; cut.
- P7 METR restated; "your code deciding" tic: fixed; the `claude -p` repeat cut, METR numbers kept in the maturity paragraph only.
- P8 "untested" body sentence: fixed; cut, the footnote carries it.
- P9 Overloaded maturity paragraph: fixed; split into a verdict paragraph and a doubts paragraph.
- P10 Tricolon density: fixed in part; three lists cut to two items.
- P11 Narrating the source's tone: fixed; both lead-ins replaced by the quotes.
- P12 "genuinely agentic": fixed.
- P13 $20 rounding gap implausible: fixed; the bug is now a discount applied after the floor check.
- P14 CLAUDE.md "enforced by nothing" restatement: fixed; cut.
- C1 Undefined terms: fixed by glossing MAP, the Aldsworth desk (one product), cents, `PreToolUse` (before the diagram), harness, agent-computer interface, deny rule, managed setting, snapshots, exfiltration and MCP.
- C2 SWE-bench subset-to-whole leap: fixed; the prose says why a hard-subset flaw and reproducible fixes undercut leaderboard reading.
- C3 METR opt-out caveat: fixed; the self-selected sample is named.
- C4 Three incidents as one mistake: fixed (same as P4).
- C5 "Only step 3 was your code" vs the litmus paragraph: fixed (same as P5).
- C6 `protect-tests.sh` not shown; settings location missing: fixed; script shown (adapted from the vendor's protected-files example), file location `.claude/settings.json` stated.
- C7 `onFailure` version not in body: fixed; version added inline.
- C8 Short commands-only file vs the cost finding: fixed; one clause says why.
- C9 Scratch branch and the trifecta: fixed; the reason is stated.
- C10 Long alt text: fixed; shortened.
- C11 Rating labels used before the scale is introduced: fixed; "On this book's maturity scale" added.
- C12 Opening scar told twice: rejected; the carrier retelling adds the diff as the only witness, which the prose critique asked to protect.
- C13 No example output for the failure types: rejected; the budget is at its ceiling and each bullet states what to return.
- S1 The second-engine pass covered the map; its findings are dispositioned in the Stage 1.5 section above, and none reopened at drafting.

