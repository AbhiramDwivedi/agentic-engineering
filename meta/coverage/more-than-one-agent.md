# Coverage map: 9.2 Multi-Agent

> Research-derived spec for what the chapter must cover so a reader can decide, with evidence,
> whether a second agent earns its cost, and where to stop. Angles run: vendor docs, academic and
> benchmarks, skeptical read, practitioner writeups, alias sweep, daily-tool, failure modes,
> incidents (no third-party multi-agent postmortem found; see Incidents). Review and trim
> **Must-cover**. Bar: definitive but tight, not exhaustive. Budget: Standard pattern, about
> 2,000 to 2,800 prose words.

## Thesis

A second agent earns its token and coordination overhead only when it isolates a context window,
a permission boundary or a domain owner that one agent cannot hold; on shared-context or
sequential tasks, splitting agents degrades accuracy while multiplying spend.

## Litmus

Your code decides: fixed fan-out, pipelines and panels (3.3, 3.5), and a manager that you wrote
to call specialists in a set order. The model decides: a handoff mid-run, a dynamically spawned
subagent, a group chat where the model picks the next speaker. Passing the litmus says it is
new, not that it is proven; the Trust verdict below is separate.

## The mental model (what the reader must leave with)

"Multi-agent" names three different things. Code that fans work out to model calls is
concurrency (3.3, 3.5). A specialist called as a tool returns a result and the caller keeps
control. A peer that takes over the conversation, or a team that messages each other, is the
only form that is a distinct architecture. Each extra agent pays in tokens, in lost shared
context and in new failure modes, and the evidence for net benefit is task-dependent. Ask who
holds control after the hop, and what the hop costs.

## Must-cover

Ranked. `[+]` = new for this stub.

1. **Sort the word first** `[+]`: (a) code-owned fan-out and panels, (b) manager with
   specialists called as tools, (c) peers that transfer control or converse. Only (c) differs
   from 3.3 and 3.5. *Skip it:* the chapter sells ordinary concurrency as an architecture.
   (Anthropic, "Building Effective Agents", 2024-12-19.)
2. **Agents as tools versus handoffs** `[+]`: three vendors expose the same two-way split.
   OpenAI Agents SDK: `Agent.as_tool()` ("a manager agent keeps control of the conversation")
   versus `handoffs` ("that specialist becomes the active agent"). LangChain multi-agent docs:
   subagents (all routing through the main agent) versus handoffs ("behavior changes
   dynamically based on state"). Google ADK names the same split (`AgentTool` versus
   `sub_agents`); that page was not opened, verify before quoting. *Skip it:* readers confuse
   a subagent call with a handoff. **Established** for the manager shape; **Emerging** for
   handoffs (below).
3. **Handoff mechanics** `[+]`: in the OpenAI Agents SDK a handoff is a tool (`transfer_to_<agent>`);
   the receiver sees full history by default; `input_filter` edits it. Constraints: server-managed
   conversations (`conversation_id`, `previous_response_id`) do not support handoff input
   filters; nested history is an opt-in beta. Origin: Swarm, now "experimental, educational"
   and "replaced by the OpenAI Agents SDK". Bound the hops: cap turns and detect A-to-B-to-A
   loops; the Handoffs page does not document `max_turns`, so cite the SDK run docs when
   claiming a cap. *Skip it:* handoff confused with routing (3.2). **Emerging**: a retired
   educational origin and a beta history API, no production benchmark.
4. **Subagents as context isolation** `[+]`: own context window, own tools, independent
   permissions; only the result returns. Claude Code docs: "Each subagent runs in its own
   context window with a custom system prompt, specific tool access, and independent
   permissions." Defensible reason for a second agent, narrowed to read-only research and
   review style work; Cognition's critique applies to writes. Link 2.6 for the permission
   boundary and 9.6 for coding-agent playbooks. **Established** at that narrow scope.
5. **Peer teams and shared state** `[+]`: Claude Code agent teams (experimental, off by
   default): independent sessions with a shared task list (file locking on claims) and a
   direct mailbox, versus subagents that only report back. The docs say teams "add
   coordination overhead and use significantly more tokens", suit independent work, and that
   "two teammates editing the same file leads to overwrites"; for sequential or same-file work
   use one session or subagents. Choices: full history, filtered history, structured payload,
   or a task board. **Emerging.**
6. **When it helps and when it hurts, measured** `[+]`: Kim et al., "Towards a Science of
   Scaling Agent Systems" (arXiv:2512.08296; v1 2025-12-09, v3 2026-04-08): 260 configurations,
   six benchmarks, five architectures; relative to a single agent, +80.8% on decomposable
   financial reasoning and a 70.0% drop on sequential planning; cross-validated R squared 0.373.
   Takeaway: architecture-task fit, not agent count. A preprint with no stated venue; one study.
7. **Cost and failure anatomy, one item** `[+]`: coordination tax (duplicated tokens,
   summarised-away context per hop, latency per hop, harder debugging) plus how it fails. MAST,
   Cemri et al., "Why Do Multi-Agent LLM Systems Fail?" (arXiv:2503.13657, NeurIPS 2025
   Datasets and Benchmarks): 14 failure modes in 3 categories. Kim et al. Table 5: error
   amplification of 17.2x for independent agents versus 4.4x with centralized coordination
   (decentralized 7.8x, hybrid 5.1x); their regression finds the main effect not significant, so
   say "trace-level amplification factor", not "proven cause". 3.3 owns the token multiplier
   and MAST at length; give one paragraph here and link.
8. **Skepticism, aimed at peers** `[+]`: Cognition (Yan, 2025-06-12): share full traces,
   actions carry implicit decisions. That argument targets parallel workers (3.3 holds the
   exchange); here apply it to handoffs and teams, where each hop drops context.
9. **Conversation-driven control** `[+]`: AutoGen group chat, the model picks the next speaker
   (Wu et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation",
   arXiv:2308.08155, COLM 2024). AutoGen is now folded into Microsoft Agent Framework (as 1.6
   records). Least predictable control shape, thinnest evidence. **Contested.**
10. **Security and failure across the boundary** `[+]`: a peer's failure returns as a
    structured, recoverable message; treat what crosses each boundary as untrusted input.
    Threat names (OWASP Top 10 for Agentic Applications, 2025-12-09): ASI03 identity and
    privilege abuse (the confused deputy across a handoff), ASI07 insecure inter-agent
    communication, ASI08 cascading failures. The OWASP page itself did not list the IDs when
    opened; confirm them in the downloadable framework before citing. Claude Code's own rule is
    a worked example: a teammate's message is treated as coming from another session, not from
    the user, and cannot carry approval. Link 4.4, 4.6, 8.5, 9.4.

## Mention-and-link

- Fan-out count, orchestrator-workers, token multiplier (about 4x agents, 15x multi-agent in
  Anthropic's 2025-06-13 report), the 90.2% result, the runaway-spawning failure, MAST at
  length: 3.3. Do not repeat.
- Specialist panel, personas, debate and its limits, reconcile step: 3.5. Debate (Du et al.,
  "Improving Factuality and Reasoning in Language Models through Multiagent Debate",
  arXiv:2305.14325, ICML 2024). Huang et al., "Large Language Models Cannot Self-Correct
  Reasoning Yet" (arXiv:2310.01798, ICLR 2024) concerns intrinsic single-model
  self-correction, not debate; do not apply its quote to debate.
- Routing versus handoff: 3.2. Compaction at handoff: 5.4. Human escalation: 4.3.
- Harness and permission boundaries: 2.6. Coding agents: 9.6. Protocols (A2A, under the Linux
  Foundation): 9.3. MCP: 2.4. Isolation: 9.4. Framework choice: 1.6.

## Out of scope

- Framework tutorials (CrewAI, ADK, AutoGen APIs): cite, point to vendor docs.
- Software-team role-play systems (ChatDev, MetaGPT, CAMEL): name once; unverified here.
- Agent identity at enterprise scale: 8.5. Cross-vendor federation and agent cards: 9.3.

## Maturity summary

- **Standard:** none.
- **Established:** manager shape (specialist as tool); subagent context isolation for read-only
  research work.
- **Emerging:** handoffs; peer teams with shared task lists; the measured architecture-task fit
  (a study, not a technique).
- **Contested:** conversation-driven speaker selection; the umbrella claim that more agents is
  better. Chapter verdict: **Contested** (the stub's projection stands). Last reviewed applies.
- MAST and Kim et al. are evidence, not techniques, and carry no verdict of their own.

## Aliases

multi-agent systems, MAS, agent teams (Claude Code, Anthropic); subagents (Claude Code,
LangChain); handoffs (OpenAI Swarm, Agents SDK, LangChain); manager pattern (OpenAI Agents
SDK multi-agent page); sub_agents, transfer_to_agent, AgentTool (ADK; not opened); group chat,
conversation-driven (AutoGen); crew (CrewAI; not opened); small, focused agents (12-Factor
Agents, not opened). Not aliases: "routines" (the Swarm README does not define the term; it
defines agents and handoffs), "coordination tax", "agent-to-agent" (9.3's protocol subject).
Author sign-off needed before any alias ships.

## Reader-verifiable anchors

- Claude Code subagents: run one and watch only the summary return (code.claude.com/docs/en/sub-agents).
- Claude Code agent teams: code.claude.com/docs/en/agent-teams.
- OpenAI Agents SDK: handoffs appear to the model as `transfer_to_<agent_name>`
  (openai.github.io/openai-agents-python/handoffs/); the contrast with `as_tool()` is on
  /multi_agent/.

## Incidents

No third-party public postmortem of a multi-agent production failure was found; MAST traces are
research annotations. Anthropic's own runaway-spawning failure is cited in 3.3. State this
plainly.

## Named-idea candidates

- "Coordination tax" is not ours; the researcher brief attributes it to Gulli and Nawalgaria,
  *Building AI Agents* (2026). Attribute if used, or avoid.
- None forced; the author may strike all.

## Carrier

Merchant helpdesk handing a conversation across billing, listing-issue and account
specialists, set against Listing Studio deliberately staying one state graph. Open question.

## Sources

Anthropic, "Building Effective Agents" (2024-12-19); Anthropic, "How we built our multi-agent
research system" (2025-06-13); Yan, Cognition, "Don't Build Multi-Agents" (2025-06-12; add
canonical URL); Cemri et al., arXiv:2503.13657 (submitted 2025-03-17, v3 2025-10-26); Kim et
al., arXiv:2512.08296; Wu et al., arXiv:2308.08155 (2023-08-16); Du et al., arXiv:2305.14325;
Huang et al., arXiv:2310.01798; OpenAI Agents SDK Handoffs and Multi-agent pages; openai/swarm
README; Claude Code subagents and agent teams docs; LangChain multi-agent docs
(docs.langchain.com/oss/python/langchain/multi-agent); OWASP Top 10 for Agentic Applications
(2025-12-09); A2A (a2a-protocol.org).

## Seams

3.3 owns dynamic fan-out and the token multiplier; 3.5 owns personas, debate limits and the
reconcile step; 3.2 owns one-shot routing and links here for mid-run handoff; 9.3 owns
protocols. 9.2 owns the umbrella decision, the manager-versus-handoff split, handoff
semantics, and the cost and failure evidence. Corrections: handoffs do not lack shared state
(default is full history, `input_filter` edits it); cost scales with tokens (about 15x in
Anthropic's report), not with agent count.

## Code seam

Likely NONE. Optional: a small offline `listing-studio` example contrasting an agent called as
a tool with a handoff, only if the author wants runnable code; otherwise the chapter is prose
plus one diagram.

## Open questions for the author

1. Carrier: merchant helpdesk handoff versus Listing Studio staying single-graph. Approve?
2. Code: none, or one tool-versus-handoff example?
3. Title: nav says "9.2 Multi-Agent", the file is `more-than-one-agent`; rename or keep?
4. Any first-hand multi-agent production claim for the "From production:" callout (none supplied)?
5. Use or strike "coordination tax" as a named idea, with the Gulli attribution?

## Map review (Stage 1.5)

Findings from the second-engine review of the map, one line each.

1. Unverified secondary source cited twice: accepted; both mentions removed, facts restated against primary sources.
2. Missing thesis, budget, open questions: accepted; added, with the proposed thesis.
3. Litmus misclassification: accepted-modified; litmus section added, "the one place" deleted; speaker selection and handoffs both sit in model-decides.
4. Manager versus handoff gap: accepted-modified; verified on OpenAI multi-agent and LangChain pages, ADK left flagged as unopened (301 redirect), OpenAI's practical guide not opened.
5. Inter-agent security and amplification: accepted-modified; 17.2x versus 4.4x confirmed in the paper's text, wording hedged as a pattern, not a cause; OWASP IDs match secondary sources only, flagged.
6. Cycles, shared state, teams: accepted-modified; agent-teams docs verified; `max_turns` is not on the Handoffs page, so cited as unverified there.
7. Seam violation with 3.3: accepted; item 4 moved to Mention-and-link, items 7 and 8 merged or reframed.
8. Maturity verdicts: accepted-modified; handoffs Emerging, conversation-driven Contested, isolation narrowed, MAST dropped from summary; coordination tax folded into item 7 and left unrated.
9. Citation omissions: accepted-modified; titles added; venues for Cemri and AutoGen not confirmed from primary pages and dropped, Kim v3 numbers verified, `input_filter` constraint confirmed; 90.2% baseline detail and A2A verbatim quote not verified, A2A quote dropped.
10. Aliases and named idea: accepted-modified; non-synonyms removed, "who holds the pen" cut, attribution kept as the brief states; Swarm "routines" is not in the README, so excluded either way.
11. No carrier: accepted; carrier and open question added.
12. Seams to 2.6, 9.6, agent teams anchor: accepted; added.
13. "Skipped" incidents label: accepted; moved into angles run.
14. Title mismatch: accepted; header aligned, rename listed as open question.
15. Missing URLs and dates: accepted-modified; dates and URLs added where opened, Cognition URL still to add.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Maturity: Contested overall. In prose, the manager shape and subagent context isolation are Established, narrowed to read-only research work. Handoffs and peer teams are Emerging. Conversation-driven speaker selection is Contested.
2. Code: none. Short illustrative fragments in prose are fine. There is no listing-studio package.
3. Carrier: the merchant helpdesk handoff is allowed as a sibling surface, because Listing Studio stays one state graph and cannot show a handoff. Listing Studio is the counter-example.
4. Title and file: keep the filename `more-than-one-agent` and the current nav label. The rename goes on the author checklist.
5. No From-production callout.
6. "Coordination tax": use it only as an attributed phrase in quotation marks with the source cited. It is not this book's coinage. No new aliases beyond those the map verified.
7. Drop the OWASP ASI IDs, which were confirmed only in secondary sources, unless the writer verifies them against the primary OWASP page. Drop `max_turns` from the handoff claims.
8. Kim et al. figures: quote them only as the map words them, with the regression hedged.

## Reconcile log (Stage 5)

One line per finding. Sources re-checked on 2026-11-28 against the Kim et al. v3 full text, the OpenAI Agents SDK Handoffs and Agent orchestration pages, and the Claude Code agent-teams page.

**Cold reader**

1. "principals" undefined: fixed; glossed as identities with their own credentials and permissions.
2. "state graph", "supplier feed", "storefront page" undefined: fixed; callout glosses the state graph as one shared listing record every step reads and writes.
3. `input_filter` inputs and outputs unclear: fixed; defined as a function that receives the history about to cross and returns what the receiver sees.
4. `conversation_id` / `previous_response_id` unexplained: fixed; glossed as server-stored history, with "if your code keeps the history, this does not affect you".
5. "compaction" only linked: fixed; glossed as shrinking history at the hop, linked to 5.4.
6. "evals" undefined: fixed; glossed inline.
7. MAST acronym never expanded: fixed; expanded as Multi-Agent System failure Taxonomy.
8. Maturity labels used before definition: fixed; four levels defined in prose with a link to How We Label.
9. "deputy" jargon: fixed; glossed as the agent holding the permissions.
10. "intake step ... classifier" thin: fixed; intake described as sorting the message into a category.
11. Missing step on why a second agent re-reads context: fixed; it cannot see the first agent's window, so context is sent and paid for again.
12. Single-agent verdict for the helpdesk unargued: fixed; both questions turn on the same messages and neither toolset needs isolating.
13. Manager-in-shape-one confusing: fixed; "the order lives in your code" stated up front.
14. "Established because two libraries ship it": fixed; the rationale is now that the shape is tool use and leaves conversation ownership unchanged (see prose critic 2).
15. "amplified relative to what": fixed; "relative to a single agent" added.
16. Refund routed to a human looked like a design flaw: fixed; step now transfers back to billing as a counted hop carrying a new finding, with the cap sending a third transfer to a person.
17. Build test, no framework-free sketch and no payload shape: fixed; illustrative loop added (transfer, hop cap, bounce check, filter, next owner, structured refusal) and a concrete payload in the trace. Labeled illustrative and untested; no companion code, per ruling 2.
18. "1.6", "3.3" bare numbers: rejected for in-text cross-references that are links with titles on first use; bare numbers after first use follow the book's convention.
19. Agent-teams enable step not given: rejected; out of scope, the footnote links the page.

**Fact-checker**

1. AutoGen COLM 2024 venue: softened; venue dropped, cited as arXiv 2023, group chat attributed to the paper body.
2. MAST NeurIPS 2025 venue: softened; venue dropped, cited as arXiv 2025 with the three categories.
3. -70.0% benchmark: verified (paper intro: "sequential planning under independent coordination"); prose and footnote now name the architecture for both +80.8% (centralized) and -70.0% (independent), and the matched budgets.
4. 7.8x decentralized and "Table 5": softened; only seen in a model-extracted summary, not verbatim, so both cut. Footnote now says the paper reports other architectures' figures.
5. "Regression not significant": softened; not confirmed verbatim, so the specific claim is cut and the body says the amplification is a pattern that does not prove a cause.
6. "Number of agents did not predict": softened; replaced with the authors' verbatim conclusion (architecture-task alignment, not number of agents, determines success).
7. Line 33 libraries claim unfootnoted: fixed; markers added.
8. Established verdicts rest on vendor docs: fixed in rationale (tool use, not availability); verdicts kept per ruling 1, flagged for the author.
9. Line 77 cost reasoning reads as fact: softened; "in principle", "measure rather than assume".
10. MAST expansion: fixed.

**Prose critic**

1. L85 "No one has published a postmortem" overclaim: fixed; header now "Production evidence is first-party and thin", names Anthropic's write-up (the one 3.3 cites, including "spawning 50 subagents for simple queries"), self-reference cut.
2. L33 Established/Emerging inconsistency: fixed; shipping is no longer the reason for either verdict. Tool-shaped designs are Established because they are tool use; handoffs and teams Emerging because they change conversation ownership with no published measurement. "The parts separate cleanly" cut.
3. L69 garbled sentence and narrated quotes: fixed; split, "plainly" and "concrete" lead-ins cut.
4. L55 narrated significance and chiasmus: fixed; opens on the three options directly.
5. L79 citation bookkeeping: fixed; regression detail cut, one plain hedge kept.
6. L9 hook precision: fixed; architectures named.
7. L83 four jobs in one paragraph: fixed; failure-message sentence moved to hop bounding.
8. Carrier panel "reviewers in order": fixed; three personas drafting sections independently, then a reconcile step, per the bible; step 7's model-decided extras acknowledged and pointed to 3.3.
9. "the listing-issue agent" presupposed: fixed; introduced as a second agent built to diagnose listing problems.
10. Weak LangChain quote: fixed; quote dropped, paraphrased as the same subagents-versus-handoffs line.
11. "worth knowing" and Swarm trivia: fixed; constraint stated directly, Swarm sentence and footnote cut.
12. "only one of them is new" before the three are named: fixed; the three named in the same paragraph.
13. L77 15x attached to hops generally: fixed; labeled a fan-out design, cost reasoning hedged.
14. "this chapter is about whether they should": fixed.

**Second-engine review of the draft**

1. Classification contradicts the litmus: fixed-modified; "new architecture" replaced in prose and diagram by "changes who owns the conversation", and model-planned workers named as orchestrator-workers (3.3). Model-decided specialist calls stay classed as tool use, which is agentic but already taught.
2. Permission boundary implies automatic isolation: fixed; the boundary requires harness-enforced credentials at the tool layer, pointer to 2.6.
3. Thesis asserts necessity: softened; "usually pays for itself", parallel speed routed to 3.3. The suggested replacement thesis was rejected; the three triggers stay as the chapter's argument.
4. Kim comparison lacks conditions: fixed; architectures and matched budgets named, and a single-agent baseline comparison added with a link to 4.2.
5. Handoffs described as irreversible: fixed; "nothing hands it back unless an agent transfers it again", the SDK's "rest of the turn" scope, and app-managed active agent across turns. Bounce detection replaces the ban on immediate returns.
6. Payload choices mix topology and payload: fixed; three payload choices, task board moved to teams; `input_type` adds metadata and does not replace history (verified); summaries and messages need filtering too.
7. Failure return and guardrail coverage: fixed; structured refusal (status, reason, next owner) in prose and sketch; guardrail scope verified verbatim and added.
8. Maturity verdicts exceed evidence: fixed-modified; rationale corrected, verdicts kept per ruling 1 for the author to confirm.
9. "Subagents only report back" outdated: fixed; teams described with a lead; the subagent-messaging nuance was verified but cut for length, so no claim about subagents' messaging remains.
10. Group-chat criticism overstated: fixed; turn caps and transcripts acknowledged, unpredictability narrowed to speaker order and length, restriction kept as a recommendation.
11. Carrier contradicts the bible: fixed (as prose critic 8).
12. Map references an unverified secondary source: fixed; Stage 1.5 entry reworded.
13. Attention cost missing: fixed; one clause with a link to 1.5.
14. Absolutes: fixed; "A filtered handoff drops context", postmortem header narrowed.
15. Source apparatus unfinished: fixed-modified; trace labeled illustrative, Cognition URL in the chapter; unopened alias sources stay flagged rather than resolved.
