# 9.2 Multi-Agent

*More than one agent: a specialist your agent calls like a tool, a peer that takes over the conversation, or a team that messages itself. Ask who holds control after the hop and what the hop costs. A second agent earns its keep when it isolates a context window, a permission boundary or a domain owner that one agent cannot hold.*

*Also called: multi-agent systems, MAS, agent teams, subagents, handoffs, manager pattern, group chat.*

## Why you'd reach for it

Split one task across several agents and the result can get much better or much worse. One study ran 260 agent configurations across six benchmarks, holding tools, prompts and token budgets equal. Against a single agent, a team with a central coordinator did 80.8% better on a financial-reasoning task that splits into independent parts, and independent agents with no coordinator did 70.0% worse on a sequential planning task, where each step depends on the one before.[^kim] The authors conclude that the fit between architecture and task decides the result, not the number of agents.

"Multi-agent" is usually sold as an upgrade. The word covers three designs: a specialist your agent calls like a tool, a handoff that gives the conversation to another agent, and a team that coordinates among itself. Only the last two change who owns the conversation, the part earlier chapters do not teach. All three make the same trade. A second agent cannot see the first one's context, so whatever it needs is sent and paid for again; it sees only what you pass it; and it adds a place for the run to go wrong.

Take a merchant helpdesk, a support agent for the businesses selling on a commerce platform. A merchant writes in: they were billed this month for a listing the platform suspended two weeks ago. The intake step files the message under `billing` (that classifier is built in [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md)), and a billing agent with access to invoices picks up the conversation. Three turns in, the merchant gets to the point. Why was the listing suspended, and can it be fixed? Answering needs tools held by a second agent built to diagnose listing problems.

The billing agent can call the listing specialist as a tool: ask a narrow question, get an answer back, keep talking to the merchant. Or it can hand off, and the listing agent becomes the one the merchant is talking to, carrying whatever history your code passes across. Pass all of it and the listing agent reads invoice lines it has no reason to see. Pass a summary and it can lose the suspension date the merchant mentioned in their first message. For this conversation a single agent holding both toolsets is probably the better build, and it is the one to beat: both questions turn on the same few messages, and neither toolset needs keeping from the other.

A second agent usually pays for itself in one of three situations:

- **A context window one agent cannot hold.** Answering one question means reading dozens of policy documents. A subagent reads them in its own window and only its summary comes back.
- **A permission boundary.** An agent that can issue refunds and an agent that reads free text from strangers are safer as two principals: identities with their own credentials and permissions. Two tool lists alone do not make that boundary. The harness has to enforce each agent's credentials at the tool layer ([2.6 The Harness](../the-unit/the-harness.md)), because hostile text can still travel between agents (see Gotchas).
- **A domain owner.** The billing team owns the billing agent's prompt, tools and evals (the test suites that score its answers), and ships changes on its own schedule.

When the work shares context or runs in sequence, keep one agent and give it more tools ([2.1 Tool Use](../the-unit/tool-use.md)) or split it into steps your code runs ([3.1 Prompt Chaining](../composition/prompt-chaining.md)). When the reason is speed on parallel jobs, that is concurrency, covered in [3.3 Orchestrator-Workers](../composition/fan-out.md).

## What it actually is

A multi-agent system is two or more model loops, each with its own instructions, tools and context window, working on one task, with something passing between them: a question and its answer, a whole conversation, or messages on a shared board. The question that sorts every design is who holds control after the hop.

![Three rows. Top: your code sends one job to three workers and merges the results, keeping control throughout. Middle: a main agent calls a specialist like a tool, and control comes back to the main agent. Bottom: an agent hands the conversation to a peer, control moves with it and nothing hands it back by default, and a bracket asks what history crossed. Only the bottom row changes who owns the conversation.](more-than-one-agent-three-shapes.svg)

The three shapes differ in who decides. In the first, your code fans work out to several model calls, or runs a fixed panel of personas, and collects the results. A manager agent your code makes call specialists in a set order belongs here too, because the order lives in your code. When a model plans the list of workers instead, that is orchestrator-workers; [3.3](../composition/fan-out.md) and [3.5 The Specialist Panel](../composition/specialist-panel.md) cover both. In the second shape, the model decides when to consult a specialist and reads the result it returns: tool use with a model behind the tool. In the third, a model gives the conversation to a peer, or a group of agents decides among itself who speaks next. Control moves, and nothing hands it back unless an agent transfers it again. Only this shape changes who owns the conversation, so only it needs design ideas you do not already have. Anthropic's guidance draws the same line between workflows, where code orchestrates model calls along set paths, and agents that direct their own process.[^bea]

This book grades techniques on four levels ([How We Label](../about/how-we-label.md)): Standard (the accepted default), Established (proven and common), Emerging (still settling) and Contested (overclaimed or disputed). The evidence for net benefit is thin and task-dependent, so the umbrella claim that more agents make a better system is Contested. A specialist called as a tool, which OpenAI's and LangChain's libraries both offer,[^openai-multi][^langchain] is Established because it is tool use: it inherits tool use's contract and failure modes and leaves the conversation where it was. A read-only subagent used to isolate context is the same shape and Established on the same grounds; once it writes, it is much less settled. Handoffs and peer teams are Emerging, because they change who owns the conversation and nobody has published a measurement of how well that holds up. Model-picked speakers are Contested.

Two neighbours get confused with this. Routing ([3.2](../composition/the-router-that-isnt.md)) classifies a request once, at the door; a handoff fires from inside an agent that is already running and moves the conversation mid-stream. Cross-vendor protocols ([9.3 The Protocol Landscape](protocol-landscape.md)) answer how agents connect, not whether they should.

## How to do it

Build the smallest shape that clears one of the three triggers, and move up only when a run shows you the smaller shape failing. Before you keep a second agent, compare it with a strong single agent on representative tasks for quality, tokens and latency ([4.2 Evaluation](../craft/proving-it-works.md)).

### Start with a specialist as a tool

In the OpenAI Agents SDK, `Agent.as_tool()` turns an agent into a tool, and "a manager agent keeps control of the conversation"; with `handoffs`, by contrast, "that specialist becomes the active agent".[^openai-multi] LangChain's docs draw the same line between subagents and handoffs.[^langchain]

Start with the tool. In the helpdesk, the billing agent gets a `check_listing_status` tool whose implementation is the listing agent, given a narrow question ("why was this listing suspended, and on what date?") and returning a short structured answer. The billing agent stays the merchant's single point of contact, and the listing agent never sees the invoice. The contract is the one any tool has: a typed input, a typed output, and your code validating what comes back before the caller acts on it.

The subagent you can watch on your own screen is this shape used for context isolation. Claude Code's docs describe it directly: "Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions."[^cc-subagents] Ask it to search a large codebase and only the summary lands in your window. Keep it to research and review, where the subagent reads and reports. Once subagents write in parallel, they make decisions their siblings cannot see, the case Cognition argues against and [3.3](../composition/fan-out.md) takes up.[^cognition]

### Hand off when a different agent should own the rest

Hand off when the rest of the conversation belongs to another agent: the issue is now a listing problem, it will take several more turns, and the listing agent's tools fit those turns better.

In the OpenAI Agents SDK a handoff is a tool the model sees, named `transfer_to_<agent_name>`; calling it makes the receiver the active agent for the rest of that turn.[^openai-multi] Which agent answers the merchant's next message is up to your application, which stores the active agent between turns. The receiver sees the full history by default. An `input_filter` is a function your code supplies that receives the history about to cross and returns what the receiver will see.[^handoffs] Filters do not work when OpenAI's server stores the conversation for you (through `conversation_id` or `previous_response_id`); if your code keeps the history, this does not affect you.

Three things can cross the hop: the full history (the default, invoice lines included), a filtered history, or a structured payload of fields your code defines, such as the listing ID and suspension date. A payload-only hop in the OpenAI SDK still needs a filter that removes the history, because a handoff's `input_type` only adds metadata the model supplies at handoff time.[^handoffs] Sensitive detail can also sit in the merchant's own messages or in a summary, so filter those too. Pick the narrowest option that carries what the receiver needs, and name those fields in code. A summary is a model's guess at what matters; a payload is your list of what must survive. Shrinking history here is compaction ([5.4 Compaction](../knowledge/compaction-and-the-window.md)), and a long history costs attention as well as tokens ([1.5 Context Engineering](../foundations/context-engineering.md)).

Bound the hops in your own code. Count transfers per conversation, treat a transfer straight back to the agent that just handed off as a bounce unless it carries a new finding, and send anything past the cap to a person ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md)). When your code refuses a transfer, return a structured result (status, reason, next owner) so the run carries on instead of crashing or going quiet. Place per-hop checks yourself: in the OpenAI SDK, input guardrails apply only to the first agent and output guardrails only to the agent that produces the final output, and tool input guardrails do not cover handoffs.[^handoffs]

Without a framework, the loop is short. The sketch below is illustrative and untested:

```python
def take_turn(agents, active, messages, hops, max_hops=3):
    """Run one merchant turn. Returns who owns the next turn, and the reply."""
    while True:
        reply = agents[active].step(messages)   # one model call with this agent's tools
        if reply.transfer_to is None:
            return active, reply.text           # store `active` for the next turn
        if hops.count >= max_hops or hops.is_bounce(active, reply):
            return "human_queue", {"status": "transfer_refused",
                                   "reason": "hop cap or bounce with no new finding",
                                   "next_owner": "human_queue"}
        hops.record(active, reply.transfer_to)
        messages = handoff_filter(messages, reply.payload)  # your code decides what crosses
        active = reply.transfer_to
```

The model chooses to call a transfer tool; the count, the filter and the next owner stay in your code.

One run of the helpdesk handoff, in order (illustrative):

1. On turn three the billing agent calls `transfer_to_listing_issue`, because the open question is now the suspension.
2. Your code checks the hop count and applies the filter: invoice lines are stripped, and the merchant's messages cross with a payload of `{"listing_id": "L-4821", "suspended_on": "2026-11-03"}`.
3. The listing agent becomes the active agent, looks up the suspension, and tells the merchant what to fix.
4. The merchant asks for a refund. The listing agent transfers back to billing with a new finding, that the listing was suspended for most of the billed period, so your code counts a second hop rather than a bounce, and billing, which can issue refunds, takes it from there. A third transfer would pass the cap and go to a person.

### Teams and group chat, used sparingly

Peer teams add shared state beside a lead. In Claude Code's agent teams, experimental and disabled by default, one session leads, and the teammates message each other and coordinate through a shared task list, where claiming a task takes a file lock so two teammates cannot take the same one.[^cc-teams] The docs say teams "add coordination overhead and use significantly more tokens than a single session", and for "sequential tasks, same-file edits, or work with many dependencies" a single session or subagents do better. They add: "Two teammates editing the same file leads to overwrites."

Conversation-driven control goes further. In AutoGen's group chat, the model reading the conversation picks which agent speaks next.[^autogen] You can cap the turns and keep the transcript, but you cannot know in advance which agent will speak, in what order, or for how many turns. Use it in research, where exploring is the job, and keep it out of anything that touches a customer.

> **In Listing Studio.** The product-listing pipeline, which turns a supplier's product feed into a storefront page, stays one state graph on purpose: one shared listing record that every step reads and writes, with your code choosing the next step. Its specialist panel ([3.5](../composition/specialist-panel.md)) is three fixed personas who draft page sections independently before a reconcile step merges them, the first shape, because your code fixes who runs. The launch-package step lets a model name extra deliverables, which is orchestrator-workers ([3.3](../composition/fan-out.md)), and every worker still returns to the graph. Splitting the pipeline into agents that hand off would buy hops and lose shared state with nothing isolated in return.

## Gotchas

**Every hop is paid for in tokens.** Anthropic measured its multi-agent research system, a fan-out design, at roughly 15 times the tokens of a chat, against roughly 4 times for a single agent.[^anthropic-multiagent] Cost scales with what each agent reads, so one long history can in principle cost more than several small payloads; measure rather than assume. Each hop also adds latency and another transcript to debug.

**Coordination fails in measured ways.** The MAST paper (a Multi-Agent System failure Taxonomy) sorts failures from annotated traces into 14 modes in three categories: system design issues, inter-agent misalignment and task verification.[^mast] Kim et al. found errors amplified about 17.2 times, relative to a single agent, when agents worked independently, against 4.4 times with a central coordinator.[^kim] It is a pattern in their traces and does not prove a cause.

**A filtered handoff drops context, and the dropped part is often a decision.** Cognition's argument against splitting work is that "actions carry implicit decisions, and conflicting decisions carry bad results".[^cognition] It was aimed at parallel workers; it applies as hard to handoffs, where the receiver sees only what crossed. If the billing agent had already told the merchant a refund was likely, and the filter dropped that turn, the listing agent will contradict it.

**What crosses a boundary is untrusted input.** A message from another agent is text another model wrote, possibly after reading something hostile, so validate it the way you validate a tool result ([4.4 Guardrails & Safety](../craft/guardrails-and-safety.md), [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md)). In Claude Code's agent teams, a teammate's message is marked as coming from another session, cannot approve a permission prompt for the user, and cannot relay a denied action to a teammate to get around the check.[^cc-teams] A handoff also opens the confused-deputy attack, where a low-privilege agent persuades a high-privilege one (the "deputy" holding the permissions) to act for it. Identity and execution isolation are in [8.5 Locks, PII & Identity](../production/locks-pii-identity.md) and [9.4 Sandboxing](sandboxing.md).

**Production evidence is first-party and thin.** The most detailed public account of a multi-agent system misbehaving is Anthropic's write-up of its research system, whose early versions spawned "50 subagents for simple queries";[^anthropic-multiagent] [3.3](../composition/fan-out.md) covers it. No third-party postmortem of a multi-agent production failure has turned up, and MAST's traces are research annotations. The [anti-patterns catalog](../catalogs/anti-patterns.md) lists the result as over-orchestration.

## In short

Default to one agent. Add a second only when you can name what it isolates: a context window the first cannot hold, a permission the first should not have, or a team that owns the second's behaviour. When you add one, call it as a tool and keep control where it was; that shape is proven and cheap to reason about. Hand off only when the rest of the conversation belongs to the other agent, and when you do, decide in code exactly what crosses and cap the hops. Leave peer teams for independent research and review, and keep model-chosen speakers away from customers until someone publishes evidence that they hold up.

<small class="chapter-meta">**Maturity: Contested** (the umbrella claim is hyped and the evidence is task-dependent; specialist-as-tool and read-only subagents are Established, handoffs and teams Emerging) · *Who decides:* your code (fan-out, fixed panels) / the model (specialist calls, handoffs, speaker selection) · *Grounding:* research · *Last reviewed:* 2026-11</small>

## Sources

[^kim]: Kim et al., "Towards a Science of Scaling Agent Systems," arXiv:2512.08296 (v1 2025-12-09, v3 2026-04-08). 260 configurations, six benchmarks, five architectures, with identical prompts, tools and compute budgets; +80.8% on structured financial reasoning under centralized coordination and a 70.0% drop on sequential planning under independent coordination, both relative to a single agent; cross-validated R² of 0.373 for the architecture-task fit model. Trace-level error amplification of 17.2x for independent systems and 4.4x for centralized coordination. The paper also reports figures for other architectures and a regression on this measure; read the full text before leaning on them. A preprint with no stated venue, and one study. <https://arxiv.org/abs/2512.08296>
[^bea]: Anthropic, "Building Effective Agents" (2024-12-19). The workflow-versus-agent distinction and the orchestrator-workers definition. <https://www.anthropic.com/research/building-effective-agents>
[^openai-multi]: OpenAI Agents SDK, "Agent orchestration" (multi-agent page). The contrast between agents as tools, where a manager keeps control, and handoffs, where the specialist becomes the active agent for the rest of the turn. <https://openai.github.io/openai-agents-python/multi_agent/>
[^langchain]: LangChain, "Multi-agent" (Python docs). The subagents-versus-handoffs split. <https://docs.langchain.com/oss/python/langchain/multi-agent>
[^cc-subagents]: Anthropic, Claude Code docs, "Subagents." <https://code.claude.com/docs/en/sub-agents>
[^cognition]: Cognition (Walden Yan), "Don't Build Multi-Agents" (2025-06-12). The shared-context argument for a single-threaded agent, aimed at parallel subagents. <https://cognition.com/blog/dont-build-multi-agents>
[^handoffs]: OpenAI Agents SDK, "Handoffs." Handoffs as `transfer_to_<agent_name>` tools; full history by default; `input_filter`; `input_type` as handoff metadata that does not replace the history; the server-managed-conversation constraint; nested history as an opt-in beta; which guardrails apply across a handoff. <https://openai.github.io/openai-agents-python/handoffs/>
[^cc-teams]: Anthropic, Claude Code docs, "Orchestrate teams of Claude Code sessions" (agent teams). Experimental and disabled by default; a team lead; shared task list with file-locked claiming; direct messages between teammates; the comparison with subagents; the coordination-overhead and same-file warnings; "Messages between agents" for the rule that a teammate's message is marked as coming from another session and cannot supply the user's consent. <https://code.claude.com/docs/en/agent-teams>
[^autogen]: Wu, Q. et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation," arXiv:2308.08155 (2023). Multi-agent conversation, including group chat with a model-selected next speaker (described in the paper body). <https://arxiv.org/abs/2308.08155>
[^anthropic-multiagent]: Anthropic, "How we built our multi-agent research system" (2025-06-13). Roughly 4x chat tokens for agents and roughly 15x for multi-agent systems, measured on internal evals at publication; the early failure of "spawning 50 subagents for simple queries". <https://www.anthropic.com/engineering/multi-agent-research-system>
[^mast]: Cemri, M. et al., "Why Do Multi-Agent LLM Systems Fail?" arXiv:2503.13657 (2025). 14 failure modes in 3 categories: system design issues, inter-agent misalignment, task verification. <https://arxiv.org/abs/2503.13657>

## See also

- [3.3 Orchestrator-Workers](../composition/fan-out.md): the fan-out mechanism under most multi-agent systems, with the token multiplier and MAST at length.
- [3.5 The Specialist Panel](../composition/specialist-panel.md): code-owned panels of personas, and the limits of debate.
- [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md): one-shot classification at the door, the thing a handoff is often mistaken for.
- [2.6 The Harness](../the-unit/the-harness.md): where a permission boundary between agents is actually enforced.
- [5.4 Compaction](../knowledge/compaction-and-the-window.md): what to keep when history has to shrink, at a handoff or anywhere.
- [9.3 The Protocol Landscape](protocol-landscape.md): how agents from different vendors connect, once you have decided they should.
- [9.6 Coding Agents](coding-agents.md): where subagents and agent teams are most visible in daily use.
- [1.6 Do You Even Need a Framework?](../foundations/do-you-need-a-framework.md): multi-agent coordination is a common reason teams adopt one.

## Further reading

- Kim et al., ["Towards a Science of Scaling Agent Systems"](https://arxiv.org/abs/2512.08296): a controlled comparison of single- and multi-agent architectures across task shapes.
- Cognition, ["Don't Build Multi-Agents"](https://cognition.com/blog/dont-build-multi-agents): the best skeptical take, from a team that builds a coding agent.
- OpenAI Agents SDK, ["Handoffs"](https://openai.github.io/openai-agents-python/handoffs/): the primary description of handoff mechanics and history filtering.
- Claude Code, ["Agent teams"](https://code.claude.com/docs/en/agent-teams): a shipping peer-team design with its costs and limits stated.
- Cemri et al., ["Why Do Multi-Agent LLM Systems Fail?"](https://arxiv.org/abs/2503.13657): the failure taxonomy to read before you design the hops.
