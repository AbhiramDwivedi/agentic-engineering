# Coverage map: Sandboxing (chapter 9.4)

> Research-derived spec for what the chapter must cover so a reader can decide where agent-run
> code and shell commands execute, and how much isolation that needs. Angles run: vendor docs,
> academic and benchmark, security and incidents, skeptical read, alias sweep, daily-tool, everyday
> engineer (thin; vendor comparison posts are leads, not citations). Skipped: practitioner
> production postmortems (almost none published). Bar: definitive but tight.

**Thesis.** A sandbox is an enforced boundary your code builds around what the model's code can
touch, and it only helps if you name the threat, cover every execution path, and refuse to give
the code both sensitive data and an outbound channel.

**Litmus.** Your code decides the boundary; the model's choices inside it belong to 2.5. This is
established engineering inside the harness, not agentic novelty.

## The mental model

The model writes code, the boundary decides what that code can reach, and that decision does not
depend on the model behaving. Three things organize the chapter. First, name the threat (a
confused model, an injected instruction, hostile code) before choosing a mechanism. Second,
isolation mechanisms (OS sandbox, container, gVisor, microVM) are composable and differ in shared
surface and cost; they are compared against a threat model, not ranked on one ladder, and
approvals are authorization, not isolation. Third, a microVM cannot prevent data theft when the
harness gives the code both sensitive files and an attacker-writable destination.

## Must-cover

Ranked. `[+]` = no existing chapter text (stub only).

1. **The boundary: filesystem, network, credentials, and every execution path** `[+]`. Anthropic
   states effective sandboxing needs both filesystem and network isolation (without network a
   compromised agent leaks files; without filesystem it escapes to the network). Add the third
   axis: the inherited environment, secrets included. Then the inventory: the Claude Code sandbox
   "covers shell commands only"; file tools, MCP servers and hooks run outside it, and the
   boundary's own config paths (`.claude` settings, `.mcp.json`, shell startup files) are
   write-protected because editing them arranges later execution outside. *Skip it:* the sandbox
   that isn't (subprocess plus timeout sold as safe). **Standard** (principle). (Anthropic
   2025-10-20; Claude Code docs.)
2. **Mechanisms, compared against a threat model** `[+]`. OS sandbox (Seatbelt, bubblewrap),
   container (shared host kernel), gVisor (user-space kernel; its docs reject assuming
   virtualization hardware is automatically safer), Firecracker microVM (own guest kernel).
   Composable, each trading startup and compatibility for shared surface. **Established**
   (implementation trade-offs); vendor selection is **Emerging**. (gVisor docs; Agache et al.,
   NSDI 2020.)
3. **Default containers fail in documented ways** `[+]`. Docker socket, privileged mode, writable
   host mounts, and disclosed runtime bugs (runc CVE-2024-21626) are escape routes.
   SandboxEscapeBench (arXiv:2603.02277) tests deliberately vulnerable configurations, not whether
   every patched container is escapable. **Established** (risk); benchmark **Emerging**.
4. **Two deployment shapes** `[+]`. Local-agent sandbox (Claude Code `/sandbox`, OpenAI's
   `sandbox_mode`) versus hosted execution (Anthropic code execution tool, microVM services).
   Different threat models and knobs. **Standard.**
5. **Network egress is the second wall; filesystem, credential and network policy as one
   section** `[+]`. Default-deny, hostname allowlist through a proxy; documented gaps: no TLS
   inspection, UDP/QUIC not carried, fully disabled network in the hosted code tool. Cite OWASP
   ASI02 ("Execution Sandboxes and Egress Controls") and ASI05 (strict network limits) each for
   what it says. **Standard.**
6. **Failure classes, kept separate** `[+]`. Dangerous configuration (`dangerouslyDisableSandbox`
   retries, `excludedCommands`, `allowUnixSockets`, native Windows running unsandboxed, fail-open
   via `failIfUnavailable`) versus implementation bugs (CVE-2025-54794, CVE-2025-54795: a string
   allowlist is not a sandbox). Documented weaknesses, no prevalence claim. **Established.**
7. **The result contract** `[+]`. What the model gets back after a denied operation, nonzero
   exit, timeout, expired environment or unavailable backend: a bounded structured result (status,
   exit info, truncated output, actionable diagnostic), as Anthropic's execution API separates
   execution results from tool errors. Failure never widens permissions on its own. Model recovery
   -> 2.5; deterministic retry -> 3.7. **Standard.**
8. **Tenant separation and resource limits as security obligations** `[+]`. Bind each environment
   to one tenant and session, restrict reuse, clean up explicitly (OWASP ASI05 per-session
   isolation; E2B paused sandboxes persist filesystem and memory until killed). Enforce CPU,
   memory, process-count, storage, output and wall-clock limits and kill descendant processes
   (Docker has no limits by default; gVisor leaves exhaustion to host cgroups). Identity -> 8.5;
   recovery -> 7.3. Warm-pool economics -> 8.4/8.7. **Emerging.**
9. **Sandbox versus approvals; the trifecta**, as brief distinctions. Approvals set when the agent
   asks; the sandbox sets technical limits. Sensitive data plus untrusted content plus an outbound
   channel (Willison 2025-06-16) survives a perfect sandbox; restrict before execution, and
   remember authority already in context. **Standard.** -> 4.3, 4.6.

## Mention-and-link

- Harness owns the boundary -> 2.6. Approvals and guardrails -> 4.3, 4.4.
- Trifecta and egress design -> 4.6. Local MCP servers and least privilege -> 2.4.
- Skills that run scripts, unsigned by default -> 2.3. Write, execute, observe, fix -> 2.5.
- Coding agents behind these sandboxes -> 9.6; browser and computer use -> 9.5.
- Context economy: return bounded summaries and artifact references, not raw output (Anthropic,
  code execution with MCP) -> 1.5, 2.4, 5.4. Budgets and kill switches -> 8.4.

## Out of scope

- Writing seccomp or Landlock profiles, Kubernetes runtime classes.
- Vendor price and cold-start tables (rot). Verifying agent-written code correctness -> 4.2, 3.4.
- Durable execution and recovery -> 7.x. Confidential computing and GPU isolation (one line).

## Maturity summary

- **Standard:** filesystem plus network isolation as a pair; covering every execution path;
  default-deny egress; sandbox and approvals as separate controls.
- **Established:** OS, gVisor and microVM isolation of untrusted generated code with known
  trade-offs; auditing sandbox settings; container-escape risk.
- **Emerging:** hosted agent-sandbox platforms as a category and vendor choice; escape
  benchmarks; stateful, pausable sandboxes.
- **Contested:** none by default; any vendor safety or prompt-reduction percentage (Anthropic's
  84% has no stated method) is cited only with that caveat.

Overall verdict **Established**, landscape paragraph Emerging.

## Aliases

Actual alternate names: code execution sandbox, sandbox agents, execution boundary (harness
vocabulary), sandbox mode (OpenAI's coding agent), `/sandbox` (Claude Code). Not synonyms: microVM is an
implementation mechanism; Code Interpreter is a tool that provides sandboxed execution. "Isolation
ladder" is invented and dropped. Gulli and Nawalgaria, *Building AI Agents* (2026), ch12 "Code
Execution and Sandbox Agents", ch15 for the boundary; TOC at
link.springer.com/book/10.1007/978-3-032-39096-7; the edition and definition need a pass before
attribution.

## Reader-verifiable anchors

1. In Claude Code on macOS, Linux or WSL2, with the sandbox on, ask Claude to run `touch
   ~/sandbox-probe` (expect "Operation not permitted" or "Read-only file system") and `curl
   --noproxy '*' https://example.com` (expect "Could not resolve host"). A command typed at the
   `!` prompt usually runs unsandboxed, so it proves nothing. Decline any retry outside the
   sandbox. This tests those two restrictions, not complete isolation. (Claude Code docs.)
2. OpenAI's coding-agent CLI: `sandbox_mode` accepts read-only, workspace-write, danger-full-access, separate from
   `approval_policy`. (learn.chatgpt.com/docs/sandboxing.)

## Incidents

- Auto-GPT (Euler, Positive Security, 2023-06-29): indirect injection led to model-written
  Python, then Docker escape by overwriting a mounted `docker-compose.yml` used at next start;
  fixed in v0.4.3. A security disclosure, not a production postmortem.
- CVE-2025-54794 and CVE-2025-54795 (fixed in 0.2.111 and 1.0.20); runc CVE-2024-21626.
- Replit database deletion (Jul 2025): only with a primary source, and only for its narrower
  lesson, environment separation.
- No public postmortem found of an agent escaping a real production sandbox.

## Named-idea candidates

- **Sandbox the effects, not the process** (filesystem, network, credentials).
- **Pick the mechanism by the neighbour** (what sits next to the code).

## Carrier and code seam

Listing Studio does not run model-written code. Proposed, pending an author decision and a
`meta/carrier-bible.md` update first (the bible requires new specifics added there): a
merchant-facing analyst that writes Python over a merchant's sales CSVs. The Repricer works
through typed tools, a contrast case rather than settled canon. Code: yes, small.
`listing_studio.sandbox`: an `ExecutionBackend` interface; one functioning OS-enforced isolation
backend (not a subprocess wrapper) with negative tests that forbidden file and network access
fail; the bounded result contract (item 7); a subprocess-plus-timeout runner kept only as the
labelled unsafe comparison that leaks an env var. The seam says plainly that a subprocess is not
isolation.

## Sources

Anthropic, "Making Claude Code more secure and autonomous with sandboxing", 2025-10-20; sandbox
runtime repo github.com/anthropic-experimental/sandbox-runtime. Claude Code sandboxing docs
(code.claude.com/docs/en/sandboxing). Anthropic code execution tool docs and "Code execution with
MCP". OpenAI coding-agent sandboxing docs. gVisor docs (security model). Agache et al., "Firecracker",
NSDI '20, pp. 419-434. Marchand et al., arXiv:2603.02277 (v1 2026-03-01). OWASP Top 10 for
Agentic Applications 2026 (2025-12-09; ASI02, ASI05). Willison, 2025-06-16. NVD CVE-2024-21626,
CVE-2025-54794, CVE-2025-54795. Euler, Positive Security, 2023-06-29. E2B docs. Docker resource
constraints docs.

> **Verify before quoting:** OpenAI page paths redirect; its protected-path and default-network
> details were not read. Hosted-sandbox limits and E2B's isolation tech need a primary-source
> pass. The Gulli ch12 row needs a definition check.

## Map review (Stage 1.5)

Second-engine review. Findings verified against the Claude Code docs, OWASP ASI02, Positive
Security, `meta/carrier-bible.md` and `mkdocs.yml`.

1. Accepted-modified: working isolation backend with negative tests required; subprocess kept as unsafe comparison.
2. Accepted: docs confirm shell-only scope and write-protected config paths; now item 1.
3. Accepted: result contract added as item 7; links 2.5 and 3.7.
4. Accepted: tenant and session binding added to item 8; links 8.5, 7.3.
5. Accepted: resource limits restated as security obligations; economics moved to 8.4/8.7.
6. Accepted: ladder dropped for composable mechanisms against a threat model; approvals separated.
7. Accepted: prevalence claim deleted; configuration and bug classes separated.
8. Accepted-modified: reviewer's data-theft sentence adopted as third organizing fact; slogan struck.
9. Accepted: items merged (1+5 policy, 7+8 as brief item 9); lifecycle trimmed to security duties.
10. Accepted: labels revised; blanket Contested removed.
11. Accepted: docs confirm `!` runs unsandboxed; anchor 1 respecified.
12. Accepted-modified: aliases split from implementation terms; Gulli TOC linked, definition check left open.
13. Accepted: analyst surface flagged as author decision needing a bible update first (bible line 218).
14. Accepted: context-economy line added to Mention-and-link.
15. Accepted: thesis and litmus verdict added; author questions below.
16. Accepted: Positive Security disclosure verified and added; Replit narrowed.
17. Accepted: ASI02 title verified ("Execution Sandboxes and Egress Controls"); citations split.

## Open questions for the author

1. Authorize the merchant-analyst surface in the carrier bible, or keep the Repricer contrast only?
2. Which OS-enforced backend should the code seam demonstrate (bubblewrap-based, or Docker with hardening)?
3. Keep Replit at all, given no primary source yet?
4. Confirm Established as the overall verdict.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Maturity: Established overall. The principles are Standard. The platform and vendor landscape paragraph is Emerging. Last reviewed 2026-11.
2. Carrier: use the Repricer contrast only. Do not add a merchant-analyst surface, because the carrier bible is not edited in this PR. That edit goes on the author checklist.
3. Code: package `sandbox/` (local to this chapter).
   - An `ExecutionBackend` protocol.
   - A bounded structured result contract: exit status, truncated stdout and stderr, and a timeout flag.
   - A policy-enforcing fake backend with negative tests. Forbidden file paths and network egress must be refused, and the sensitive-data-plus-outbound-channel combination must be rejected at configuration time.
   - The subprocess-plus-timeout runner, labelled as the unsafe comparison.
   - Tests must run offline on Windows and Linux. No OS-level isolation is exercised in the tests.
   - The prose must say plainly that the tests prove the contract and the policy, not kernel isolation. Real OS-enforced backends (container, gVisor-class, platform sandboxes) are described in prose with citations, and no specific backend is chosen.
4. Drop Replit; it has no primary source.
5. Findings folded on the reviewer's word must be verified by the writer against the primary source before they are cited. If a claim can't be verified, cut it.
6. No From-production callout, no coinage, and no aliases beyond those the map verified.

## Reconcile log (Stage 5)

Fact-check:

1. OWASP ASI05: fixed. Footnote now cites the ASI05 primary page; prose quotes "sandboxed containers with strict limits, including network access"; "egress" no longer attributed to OWASP.
2. Auto-GPT: fixed. Scoped to the self-built Docker setup; "a security team" became "a security researcher"; Gotcha 2 now says the escape rewrote a writable mount.
3. Code execution tool quote: fixed. "completely disabled" replaced with the documented "no internet access".
4. CVE-2025-54795 fix version: verified against GitHub advisory GHSA-x56v-x2h6-7j34 (approval-prompt bypass, patched in 1.0.20); kept, and both GHSAs added to the footnote.
5. `_OPEN`/`_NET` undefined: fixed. Moved inside the `sandbox-fake` snippet anchor and shown in the chapter; prose names the literal-call patterns they match.
6. `subprocess.run` process-tree behaviour: rejected for a citation; standard library behaviour, stated as engineering advice.
7. Glossing of OS terms: fixed (see cold read 2).
8. OpenAI docs host URL: rejected; the cited page resolved and both quotes verified.

Cold read:

1. Missing imports: fixed. Snippet anchors widened to include imports and `PolicyError`; mirrored blocks re-synced, tests pass.
2. Undefined terms: fixed by glossing Seatbelt, bubblewrap, Landlock, namespaces, cgroups, hypervisor, egress, the `!` prefix and TLS inspection at first use; Stockwell glossed in the callout.
3. l.34 Auto-GPT link: fixed. Stated as an analogy between `docker-compose.yml` and the agent's own configuration.
4. l.163 "why cross-platform": fixed. Says the tests depend on no kernel feature.
5. No real backend or model wiring shown: rejected. Ruling 3 keeps the backend choice open and out of the tests.
6. "Neither recovery path ever widens the policy": rejected; the policy is frozen and no code path widens it.

Prose critique:

1. Trifecta rule restated: fixed. Gotcha 6 cut to env-var and token scrubbing; the `Policy` comment dropped.
2. Subprocess-with-timeout restated: fixed. Docstrings cut to one line each; l.109 and Gotcha 1 point at the unsafe runner instead of restating it.
3. l.11 "usually": fixed. Now "the easiest boundary to build", a claim about effort, not prevalence.
4. Performed closers at l.9, l.36, l.47, l.179: fixed. l.179 now ends on the fact that both CVEs were in-app string checks, which fits the path-restriction bypass.
5. l.49 unnamed defaults: fixed. Names Claude Code's working-directory writes plus host allowlist and the hosted container's lack of internet access.
6. l.169 carrier label: fixed. "In Listing Studio" became "On Stockwell", since the Repricer is a sibling surface.
7. l.30 dead sentence: fixed (cut).
8. l.87 MCP tangent: rejected; it is the context-economy line the map review asked for.
9. Gotcha 3 semicolon chain: rejected; the five documented holes are the point and each is one clause.
10. Approval-prompt trigger bullet: rejected; it is a common reason teams adopt a sandbox, and Gotchas 3 to 5 qualify it.

Also cut: the uncited Docker-socket example in Gotcha 2. Never added: E2B, and the per-session OWASP attribution (per-session binding stays as uncited engineering advice).
