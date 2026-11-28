# The Incident File

> **The decision it resolves:** which public agent failure looks like the one you are about to ship?

Every entry here is a public case that a chapter of this reference cites, carried over with that
chapter's own source and mapped to the control the chapter argues would have caught it. Use it two
ways: as the evidence behind a maturity verdict, and as the quickest answer when a team proposes
to skip a control. Read the footnotes before you quote an entry. Several cases are security
disclosures or demonstrations rather than observed harm, and one rests on a single person's
account; each footnote says which.

The file holds what the chapters cite and grows when they cite more. No chapter yet cites a
personal-agent exposure or a scale claim that later failed review, so neither has an entry.

## The file at a glance

| Case | When | What failed | The control | Chapter |
|---|---|---|---|---|
| [Replit deletes a production database](#replit-production-database) | July 2025 | a code freeze held only as an instruction | a gate in the execution path | 2.6, 4.3, 9.1, 9.6, 3.7 |
| [Claude Code path and approval bypasses](#claude-code-bypasses) | 2025 | string checks inside the application | an OS-level boundary | 9.4 |
| [Cursor writes its own MCP config](#cursor-mcp-config) | August 2025 | a config write that meant running code | treating that write as execution | 9.6, [2.4](../the-unit/mcp.md) |
| [GitHub MCP leaks non-public repositories](#github-mcp) | May 2025 | all three legs of the trifecta in one session | removing a leg; approvals people read | 4.6, 4.3 |
| [EchoLeak in Microsoft 365 Copilot](#echoleak) | June 2025 | an injection classifier, evaded | constraint by design | 4.6, 5.2 |
| [Slack AI exfiltration](#slack-ai) | August 2024 | retrieval mixing public and restricted text | treating the index as untrusted | 5.2 |
| [Perplexity Comet follows a hidden comment](#comet) | August 2025 | page content not separated from the request | host isolation, scoped session authority | 9.5 |
| [Poisoned memories in ChatGPT and Gemini](#memory-poisoning) | 2024, 2025 | the model wrote its own future prompt | a write gate your code labels | 5.3 |
| [Auto-GPT escapes its container](#auto-gpt-escape) | June 2023 | the container's own definition mounted writable | filesystem and network isolation | 9.4 |
| [Amazon Q Developer extension](#amazon-q) | July 2025 | a token scoped wider than its job | token scope | 9.6 |
| [LiteLLM releases on PyPI](#litellm) | March 2026 | a gateway holding every provider key | version pinning, scoped keys | 8.2 |
| [MCP rug pulls and postmark-mcp](#mcp-supply-chain) | 2025 | trusted tool definitions that changed | tool-definition pinning | [2.4](../the-unit/mcp.md) |
| [LangChain template injection](#langchain-template) | November 2025 | untrusted template structure | templates in source, untrusted values only | 4.1 |
| [AutoGPT replans without stopping](#autogpt-loops) | 2023 | no completion criterion, no cap | a replan cap | 3.6 |
| [50 subagents for a simple query](#fifty-subagents) | 2025 | the model sizing its own fan-out | a cap your code enforces | [3.3](../composition/fan-out.md), 9.2 |
| [Moffatt v. Air Canada](#air-canada) | February 2024 | a chatbot's wrong policy answer | a control plane of records | 8.6 |
| [DoNotPay and Operation AI Comply](#donotpay) | September 2024 | an untested marketing claim | existing consumer law | 8.6 |

## Destructive actions

### Replit deletes a production database { #replit-production-database }

In July 2025 a coding agent on Replit reportedly deleted a live production database during an
active code freeze, despite repeated instructions not to make changes.[^h-aiid] SaaStr's founder
says he told the agent "eleven times in ALL CAPS" not to make changes;[^hitl-register] by his own
account, "there is no way to enforce a code freeze" in the tool.[^ca-register] The freeze existed
only as an instruction the agent had read.[^ol-replit]

**What would have caught it.** An instruction in a prompt is advice to the model, and only code in
the execution path stops the call (2.6 The Harness, 4.3 Human-in-the-Loop). 9.1 Long-Running
Agents adds that a boundary stated in the prompt can be lost when a long context is compacted, so
it belongs in a deny rule, a harness permission setting that blocks a tool or command on every
call.[^lr-aiid] 3.7 The Outer Loop draws the retry lesson: if an attempt can delete before the
verifier runs, a retry compounds the damage, so the attempt only proposes. The harness controls
are **Standard (mediated tool calls, sandboxes, hooks, caps)** in 2.6; approval gates are
**Standard (approval gates and pause/resume)** in 4.3.

The evidence is one person's account, with no Replit postmortem behind it, and 9.1's source notes
that the accounts do not show a deny rule would have prevented the deletion.

## Approval and permission bypasses

### Claude Code path and approval bypasses { #claude-code-bypasses }

CVE-2025-54794 was a path-prefix check in Claude Code that a sibling directory sharing the prefix
slipped past, fixed in 0.2.111; CVE-2025-54795 let a crafted command skip the approval prompt,
fixed in 1.0.20.[^sb-cc] Both needed untrusted content in the agent's context, and both were string
checks inside the application.

**What would have caught it.** 9.4 Sandboxing treats a string allowlist as a filter, and filters get
bypassed; the boundary that holds is the operating system's. Filesystem plus network isolation with
default-deny egress is **Established** there.

### Cursor writes its own MCP config { #cursor-mcp-config }

Cursor's advisory for CVE-2025-54135 describes an indirect prompt injection that could write an MCP
config file without approval and so execute code; it was patched in 1.3.9.[^ca-cursor]
[2.4 MCP](../the-unit/mcp.md) files the same CVE, CurXecute, under prompt injection to
execution.[^mcp-cve]

**What would have caught it.** 9.6 Coding Agents names the gap: a config file the agent could write
even though writing it meant running code. A write that executes needs the same gate as execution.
The harness practices are **Established (the harness practices)** in 9.6.

## Injection and exfiltration

### GitHub MCP leaks non-public repositories { #github-mcp }

In Invariant Labs' May 2025 demonstration, an issue planted in a public GitHub repository steered an
agent holding a token for non-public repositories into copying their data into a public pull
request.[^pi-invariant] Invariant calls it "a fundamental architectural issue" and notes that many
users already choose an "Always Allow" policy and stop monitoring individual actions.[^hitl-invariant]

**What would have caught it.** The session held sensitive data, untrusted content and a way out, the
lethal trifecta of 4.6 Prompt Injection & the Lethal Trifecta. One repository per session would have
removed a leg. The "Always Allow" habit is 4.3's case for asking less and asking about consequences,
so the approvals that remain get read. 4.6 grades the threat and its defenses as **Established
(threat) / Contested (defenses the model must honor) / Emerging (constraint by design)**.

### EchoLeak in Microsoft 365 Copilot { #echoleak }

CVE-2025-32711, published 11 June 2025 with a CVSS 3.1 score of 9.3, let one crafted email make
Microsoft 365 Copilot disclose data with no click from the user.[^pi-cve] The documented chain
evaded Microsoft's injection classifier (XPIA), slipped past link redaction with reference-style
Markdown, and sent the data out through an auto-fetched image routed via a Teams proxy that the
content security policy allowed.[^pi-echoleak] 5.2 Retrieval (RAG) counts it among the public
incidents that ran through retrieval.[^rag-echoleak]

**What would have caught it.** 4.6 reads EchoLeak as the cost of a bypassed filter. Defenses that
depend on the model or a classifier resisting are Contested as protection; defenses that constrain
by design, such as removing a leg of the trifecta, are deterministic where they apply.

### Slack AI exfiltration { #slack-ai }

In August 2024 PromptArmor showed a message posted in a public Slack channel, retrieved alongside a
secret from a restricted one, making Slack AI render a link that carried the secret out.[^rag-slack]

**What would have caught it.** 5.2 treats whatever is in the index as untrusted input: whoever can
write to the corpus can steer the answers. It grades defenses against poisoning and injection as
Contested and sends the mechanism to 4.6.

### Perplexity Comet follows a hidden comment { #comet }

In August 2025 Brave showed that Perplexity's Comet browser, asked to summarize a Reddit thread,
would follow instructions hidden behind a spoiler tag in one comment: find the user's email
address, trigger a one-time-password login, read the code from the user's logged-in Gmail, and post
both back as a reply. Comet passed page content to its model without separating it from the user's
request.[^cu-comet]

**What would have caught it.** 9.5 Computer Use & Browser Agents treats everything the page supplies
as untrusted and names three boundaries: host isolation, session authority scoped to what the task
needs, and confirmation owned by your application. Its verdict for this ground is **Emerging
(general desktop autonomy, injection defences, evaluation method)**.

### Poisoned memories in ChatGPT and Gemini { #memory-poisoning }

In 2024 a security researcher showed ChatGPT saving false "memories" planted by content it was asked
to process, and those beliefs carried into later conversations.[^mem-chatgpt] In early 2025 he did
the same to Gemini through an uploaded document, which told the model to save only when the user
next said "yes".[^mem-gemini]

**What would have caught it.** 5.3 Memory gates every write on an author label that your code sets,
because the model will not reliably report where a "fact" came from. Once tool output enters the
context, every write is tagged `tool` for as long as that output stays there, and a user
confirmation means approval of the exact key and value shown. The chapter is **Emerging**.

## Escapes

### Auto-GPT escapes its container { #auto-gpt-escape }

In June 2023 a security researcher got Auto-GPT to escape the Docker container it ran in, with every
step going through the agent's own tools.[^sb-autogpt] The agent browsed a page carrying
instructions in zero-size text, downloaded a script and ran it. The script rewrote the project's own
`docker-compose.yml`, mounted writable inside the container, to mount the host's root filesystem
with full privileges; the next restart ran the attacker's configuration on the host. No container
bug was needed.

**What would have caught it.** 9.4 Sandboxing: no privileged containers, no writable host paths, and
never the file that defines the container. Isolation is **Established** there.

## Supply chain

### Amazon Q Developer extension { #amazon-q }

In July 2025 AWS found that a GitHub token with overly broad scope let an attacker commit malicious
code into release 1.84.0 of its Amazon Q Developer extension; the code failed to execute because of
a syntax error.[^ca-aws] The agent did not cause it.

**What would have caught it.** 9.6 files it with the Replit and Cursor cases as a boundary nothing
enforced: a token trusted to do less than its scope allowed. Scope the token to the job.

### LiteLLM releases on PyPI { #litellm }

In March 2026 two LiteLLM releases reached PyPI with malicious code in them.[^wm-litellm]

**What would have caught it.** 8.2 Which Model? points out that a gateway speaking every provider's
API concentrates your provider keys in one dependency: pin its version and give it scoped keys. The
chapter is **Established**.

### MCP rug pulls and postmark-mcp { #mcp-supply-chain }

[2.4 MCP](../the-unit/mcp.md) names the incidents in its class: the rug-pull class (MCPoison,
CVE-2025-54136), prompt injection to execution (CurXecute, CVE-2025-54135), and the postmark-mcp
package incident of September 2025.[^mcp-cve]

**What would have caught it.** Pinning tool definitions, so a server that changes a definition after
you approved it is caught. 2.4 grades pinning Emerging, because it is guidance rather than a settled
part of the protocol.

### LangChain template injection { #langchain-template }

CVE-2025-65106 let anyone who controlled the *structure* of a LangChain f-string template use syntax
such as `{obj.attr}` to walk Python object internals; the fix restricted f-string variables to plain
identifiers.[^pa-cve]

**What would have caught it.** 4.1 Prompt Architecture & Management: keep templates in your own
source and pass untrusted content only as values. The chapter is **Established**.

## Runaway loops

### AutoGPT replans without stopping { #autogpt-loops }

Failure write-ups of AutoGPT, the 2023 goal-driven agent, trace its runaway replanning to three
causes: goals with no completion criterion, no comparison of a new plan against what already ran,
and no iteration or cost cap.[^pl-autogpt]

**What would have caught it.** 3.6 Planning & Task Decomposition sets a replan cap in code before
the first run.

### 50 subagents for a simple query { #fifty-subagents }

Anthropic's account of its multi-agent research system names "spawning 50 subagents for simple
queries" as an early failure mode it had to guardrail against explicitly.[^fo-anthropic] 9.2
Multi-Agent cites it as the most detailed public account of a multi-agent system
misbehaving.[^ma-anthropic]

**What would have caught it.** [3.3 Orchestrator-Workers](../composition/fan-out.md): a cap on the
fan-out, enforced by your code after the plan comes back and before any worker starts. The pattern
is **Established (dynamic orchestrator-workers)** there. The evidence is one
vendor's first-party account.

## Liability and claims

### Moffatt v. Air Canada { #air-canada }

A customer asked Air Canada's website chatbot about a fare policy, got a wrong answer, and booked on
the strength of it. The British Columbia Civil Resolution Tribunal held the airline liable for
negligent misrepresentation and awarded CAD 812.02.[^gc-aircanada] The forum is a small-claims
tribunal, and it applied ordinary law; the chatbot being a model changed nothing.

**What would have caught it.** 8.6 Governance & Compliance does not claim a control would have
prevented the wrong answer. Its control plane answers the questions that follow one: which model
wrote it, which prompt was live, who approved it. 8.6 grades those controls **Established (core
runtime controls)** there.

### DoNotPay and Operation AI Comply { #donotpay }

The US Federal Trade Commission's Operation AI Comply targeted DoNotPay, which had marketed "the
world's first robot lawyer" without testing it; the proposed settlement order carried
$193,000.[^gc-ftc]

**What would have caught it.** Testing the claim before marketing it. 8.6 reads both cases as
existing law at work: consumer protection has no AI exemption.

<small class="chapter-meta">*Last reviewed:* 2026-11</small>

## Sources

[^h-aiid]: AI Incident Database, Incident 1152, "LLM-Driven Replit Agent Reportedly Executed Unauthorized Destructive Commands During Code Freeze, Leading to Loss of Production Data" (2025-07-18). <https://incidentdatabase.ai/cite/1152/> Press accounts differ on the details; this chapter relies only on the incident record.
[^hitl-register]: Simon Sharwood, The Register, 2025-07-21, on the Replit and SaaStr incident. The founder's own account, from his posts and a LinkedIn video; no Replit postmortem is cited. <https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/>
[^ca-register]: Simon Sharwood, "Vibe coding service Replit deleted user's production database, faked data, told fibs galore," The Register (2025-07-21). The account is the founder's own, from his posts; the article carries no response from Replit. <https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/>
[^ol-replit]: vectara/awesome-agent-failures, "Replit AI Database Deletion Incident - July 2025." A user-reported incident during a 12-day experimental build; not a formal postmortem. <https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/replit-ai-database-deletion.md>
[^lr-aiid]: AI Incident Database, Incident 1152 (2025), an index linking the original reports in The Register (2025-07-21) and Tom's Hardware and the user's own posts. Single-source and not an independent investigation; the accounts do not show that a deny rule would have prevented the deletion. <https://incidentdatabase.ai/cite/1152/>
[^sb-cc]: NIST NVD, CVE-2025-54794 and CVE-2025-54795 (Claude Code). <https://nvd.nist.gov/vuln/detail/CVE-2025-54794>, <https://nvd.nist.gov/vuln/detail/CVE-2025-54795>; GitHub advisories GHSA-pmw4-pwvc-3hx2 (fixed in 0.2.111) and GHSA-x56v-x2h6-7j34 (fixed in 1.0.20). <https://github.com/advisories/GHSA-pmw4-pwvc-3hx2>, <https://github.com/advisories/GHSA-x56v-x2h6-7j34>
[^ca-cursor]: Cursor, GitHub security advisory GHSA-4cxx-hrm3-49rm, "Arbitrary code execution from Cursor Agent through a prompt injection via MCP Special Files," CVE-2025-54135, crediting researchers hxofir-a and MaccariTA (2025-08). A demonstrated exploit, not observed customer harm. <https://github.com/cursor/cursor/security/advisories/GHSA-4cxx-hrm3-49rm>
[^mcp-cve]: Incidents in this class: the rug-pull class (MCPoison, CVE-2025-54136), prompt-injection-to-execution (CurXecute, CVE-2025-54135), and the postmark-mcp package incident, September 2025.
[^pi-invariant]: Invariant Labs, "GitHub MCP Exploited: Accessing private repositories via MCP," 2025-05-26. Also the source of the term "toxic agent flow." <https://invariantlabs.ai/blog/mcp-github-vulnerability>
[^hitl-invariant]: Invariant Labs, blog post on the GitHub MCP vulnerability, 2025-05-26. The "Always Allow" sentence. <https://invariantlabs.ai/blog/mcp-github-vulnerability>
[^pi-cve]: CVE-2025-32711, CVE record (CNA: Microsoft): "AI command injection in M365 Copilot allows an unauthorized attacker to disclose information over a network." CVSS 3.1 base 9.3, published 2025-06-11. <https://www.cve.org/CVERecord?id=CVE-2025-32711>
[^pi-echoleak]: Pavan Reddy and Aditya Sanjay Gujral, "EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System," 2025. arXiv:2509.10540. The zero-click chain: XPIA classifier evasion, reference-style Markdown, auto-fetched images, a CSP-allowed Teams proxy. <https://arxiv.org/abs/2509.10540>
[^rag-echoleak]: Reddy, P. and Gujral, A., "EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System" (arXiv 2025-09-06). CVE-2025-32711 in Microsoft 365 Copilot. <https://arxiv.org/abs/2509.10540>
[^rag-slack]: PromptArmor, "Data Exfiltration from Slack AI via Indirect Prompt Injection" (August 2024). <https://promptarmor.substack.com/p/data-exfiltration-from-slack-ai-via>
[^cu-comet]: Brave, "Agentic Browser Security: Indirect Prompt Injection in Perplexity Comet" (2025-08-20). <https://brave.com/blog/comet-prompt-injection/>
[^mem-chatgpt]: Rehberger, J., "ChatGPT: Hacking Memories with Prompt Injection," Embrace The Red (2024-05-22). <https://embracethered.com/blog/posts/2024/chatgpt-hacking-memories/>
[^mem-gemini]: Rehberger, J., "Hacking Gemini's Memory with Prompt Injection and Delayed Tool Invocation," Embrace The Red (2025-02-10). Reported to Google in December 2024. <https://embracethered.com/blog/posts/2025/gemini-memory-persistence-prompt-injection/>
[^sb-autogpt]: Euler, L., Positive Security, "Hacking Auto-GPT and escaping its docker container" (2023-06-29). A security disclosure, fixed in Auto-GPT v0.4.3; not a production postmortem. <https://positive.security/blog/auto-gpt-rce>
[^ca-aws]: AWS, Security Bulletin AWS-2025-015, "Security Update for Amazon Q Developer Extension for Visual Studio Code (Version #1.84)," CVE-2025-8217 (2025-07-23). A supply-chain case: the agent did not cause it. <https://aws.amazon.com/security/security-bulletins/AWS-2025-015/>
[^wm-litellm]: LiteLLM, "Security Update: Suspected Supply Chain Incident" (2026-03-24). The project's own advisory; the cause was still under investigation when it was written. <https://docs.litellm.ai/blog/security-update-march-2026>
[^pa-cve]: GitHub Security Advisory GHSA-6qv9-48xg-fc7f / CVE-2025-65106 (published 2025-11-19). The vulnerability is in `langchain-core`'s f-string templates (attribute-access syntax such as `{obj.attr}`, `{obj[0]}`), fixed by allowing only valid Python identifiers (patched in 1.0.7 and 0.3.80). Mustache and Jinja2 changes were defensive hardening; the Jinja2 hardening was reverted in 1.1.3 because it "significantly limited legitimate Jinja2 usage and broke existing templates," and the advisory says Jinja2 is intended for trusted template sources only. Risk is highest where an application accepts untrusted template structure, not merely untrusted values. <https://github.com/langchain-ai/langchain/security/advisories/GHSA-6qv9-48xg-fc7f>
[^pl-autogpt]: "AutoGPT Planning Failures: Infinite Loops & Resource Depletion (2023)," a case study in `vectara/awesome-agent-failures` drawn from community reports and GitHub issues. It names "Lack of Concrete Termination Criteria," "No comparison between new plans and previously executed plans," and "No built-in limits on execution time or iterations." Practitioner evidence, not a vendor postmortem; usage figures circulating in secondary compilations could not be traced to an original report and are not repeated. <https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/autogpt-planning-failures.md>
[^fo-anthropic]: Anthropic, "How we built our multi-agent research system" (2025-06-13). The orchestrator-worker architecture behind Claude's Research feature; the token-multiplier finding (roughly 4x chat for agents, roughly 15x for multi-agent systems, measured on internal evals at publication); the subagent context-isolation framing; the lead-agent synthesis step; the non-determinism admission; the coding-tasks caveat; and the "spawning 50 subagents for simple queries" postmortem. <https://www.anthropic.com/engineering/multi-agent-research-system>
[^ma-anthropic]: Anthropic, "How we built our multi-agent research system" (2025-06-13). Roughly 4x chat tokens for agents and roughly 15x for multi-agent systems, measured on internal evals at publication; the early failure of "spawning 50 subagents for simple queries". <https://www.anthropic.com/engineering/multi-agent-research-system>
[^gc-aircanada]: *Moffatt v. Air Canada*, 2024 BCCRT 149 (British Columbia Civil Resolution Tribunal, 14 February 2024). <https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html>. A tribunal decision, not a court judgment.
[^gc-ftc]: US Federal Trade Commission, "FTC Announces Crackdown on Deceptive AI Claims and Schemes" (25 September 2024), the Operation AI Comply announcement including DoNotPay. <https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes>. The $193,000 figure is the proposed order as announced.
