# 1.6 Do You Even Need a Framework?

<small class="chapter-meta">**Maturity: Standard** (the build-vs-buy discipline and the cargo-cult caution) · *Who decides:* your code · *Grounding:* production + research · *Last reviewed:* 2026-06</small>

*Build-vs-buy for agent plumbing. A framework is an abstraction over the tool loop, state, checkpointing, retries, and orchestration you would otherwise write yourself. For most teams shipping a real production system, it earns its place; the cases where the raw SDK wins are narrower than the "you don't need a framework" advice suggests.*

## Why you'd reach for it

You can build an agent with nothing but the model provider's SDK and a `while` loop. The provider gives you the augmented LLM for free: a model that takes tools and returns either a final answer or a request to call one. Wrap that in a loop, dispatch the tool calls, feed the results back, and you have a working agent in a page of code. For a single agent calling one or two tools, that is the whole job, and reaching for a framework would be over-engineering.

The trouble starts when the system grows past the toy. The first time a run dies on step seven of nine, you discover the plumbing the loop was missing. Where is the state? If it lived in local variables, it is gone, and the merchandiser who clicked *Generate listing* twenty minutes ago gets an error instead of a listing. So you add a state object, then persistence so a crash does not lose it, then a way to resume from the failed step instead of re-running the six that succeeded and re-paying for their model calls. Then you want to see what the model actually did when a listing comes out wrong, so you add tracing on every step. Then two steps could run in parallel, so you add concurrency. Each addition is reasonable. Together they are a framework, and you are now maintaining it by hand, badly, instead of shipping listings.

That is the cost of the naive build: not that it cannot be done, but that you rebuild known infrastructure under deadline, hit the edge cases in production that the mature frameworks already hit and fixed, and own the result forever. The plumbing is real work, and most of it is not your product. A merchant does not pay Stockwell for a hand-rolled checkpointer.

Reach for a framework when:

- your control flow is graph-shaped or multi-step: branches, loops, parallel fan-out, or steps that hand off to each other;
- a run can fail partway and you need to resume it, not restart it (durable execution and checkpointing, covered in [7.3 Checkpointing](../reliability/stopping-gracefully.md));
- you want state, streaming, retries, and observability hooks as solved problems rather than a backlog;
- more than one agent has to coordinate ([9.2 Multi-Agent](../frontier/more-than-one-agent.md)).

You do not need one when the system is a single agent calling one or two tools, when it is a throwaway or a prototype, or when owning every layer is itself a hard requirement (you are building the framework, or you are in an environment where you cannot take the dependency). For those, the raw SDK plus a loop is the right amount of machinery, and the section below gives that camp its fair hearing.

## What it actually is

An agent framework is an abstraction over the plumbing you would otherwise write yourself. Name the plumbing concretely, because that is what makes the value legible: state management; **durable execution and checkpointing**, which is the answer to "what happens when step seven dies" (save state after each step, resume from the last good one); streaming; retries; the tool-call loop glue; observability hooks; and graph or handoff orchestration for control flow more complex than a straight line. LangGraph's checkpointers, for instance, persist the whole graph state after every node so a crashed run resumes from the last checkpoint rather than from scratch.[^langgraph] None of that is your product. All of it is necessary the moment the system is real.

By the litmus test of this reference, a framework is firmly **your code decides**: it is scaffolding around the model, not a decision the model makes. ([1.2 Who Decides?](who-decides.md).) It does not pass any test for "genuinely new." It is ordinary infrastructure, which is exactly why the build-vs-buy question is ordinary engineering, the same call you make on a queue, a cache, or an ORM.

The discipline is **Standard**: build-vs-buy is as old as software, and the answer is usually buy when the thing you would build is generic infrastructure that someone else has already hardened. What is volatile is the catalog of tools and which features each one has this quarter; that part is fast-moving and **Emerging**, which is why this chapter sends the live feature matrix to the appendices rather than freezing one here, and carries a Last-reviewed stamp.

This is not the same question as [1.3 Workflow or Agent?](workflow-or-agent.md), and it is worth keeping them apart. That chapter asks whether you need agentic control flow at all. This one assumes you have decided you do, and asks how to build it. Decide *that* before you decide *how*.

### The framework-positive default, and the SDK-first counter-camp

Here is the chapter's position, stated as a position and not as a neutral fact: **for most teams shipping a real agentic system, a framework earns its place, and the cases where you should skip it come down to the three narrow ones named below.** The plumbing above is real, you will rebuild it under deadline, and you will rebuild it worse than a framework that has already absorbed years of production edge cases. This is the author's argued call, grounded in having shipped one (see the production callout below), not a survey result.

The honest counter-camp deserves a real hearing, because it comes from a credible source and it is right within its bounds. Anthropic's *Building Effective Agents* recommends the opposite default: "We suggest that developers start by using LLM APIs directly: many patterns can be implemented in a few lines of code."[^anthropic] Its caution about frameworks is the sharpest version of the argument, and it is true: frameworks "often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug," and "they can also make it tempting to add complexity when a simpler setup would suffice."[^anthropic] When you cannot see the prompt your framework actually sent the model, you cannot debug why the model misbehaved, and that opacity is a genuine tax. The provider SDK keeps the prompt and response in your hands.

So when does SDK-direct actually win? Three cases, and they are narrow. A single agent calling one or two tools, where the loop is a page of code and a framework would only add indirection. A throwaway or a prototype, where you will delete it before the plumbing matters. And a team that must own every layer, by requirement rather than preference. Outside those, the system grows into the plumbing, and the framework that already solved it pays for itself. Start direct to learn the mechanics, reach for the framework when the system outgrows the loop, which for production work it usually does.

Use a framework for the same reason you use any infrastructure: the alternative is rebuilding it yourself, and you would rebuild it worse. The rule that ties it together: **adopt a framework when the plumbing is its whole value to you.** Graph-shaped control flow, durable execution, multi-agent coordination: that is where it pays. A single agent and one tool is not, and wrapping it in a framework is its own mistake.

## The decision criteria

There is no scorecard here on purpose. The call is a few axes weighed with judgment, not a points total, and a reference that hands you a spreadsheet is pretending the decision is more mechanical than it is. Here are the axes.

**How much of the plumbing would you rebuild, and would you rebuild it well?** This is the heaviest axis. If you need state, checkpointing, retries, streaming, and observability, you are looking at months of infrastructure that is not your product, and a mature framework has already hit the edge cases you have not imagined yet. If you need a loop and one tool, you would rebuild almost nothing, and the framework is dead weight.

**How non-standard is your control flow?** Straight-line and simple favors the SDK. Graph-shaped, with branches, loops, parallel fan-out, and handoffs between steps, favors a framework, because that orchestration is precisely what they are built to express. The further your control flow is from a single linear pass, the more a framework saves you.

**Is this core to your product, or is it infrastructure?** You build what differentiates you and buy what does not. The agent's behavior, its prompts, its tools, its guardrails are yours and stay yours. The loop that calls the model and the store that persists state are infrastructure, and infrastructure is what frameworks are for.

**What is your team's familiarity, and your lock-in tolerance?** A team fluent in a framework ships faster on it; a team that would spend a month learning one to build a two-tool agent should not. And weigh how coupled the framework is to a runtime you would struggle to leave, especially the cloud-coupled stacks. A portable library you can walk away from is a smaller bet than a managed runtime that owns your execution.

Weigh those four and the recommendation falls out. Heavy plumbing, graph-shaped flow, infrastructure-not-product: buy the framework. A single agent, one or two tools, a throwaway, or a hard requirement to own every layer: stay on the SDK. Most production agentic systems land in the first bucket, which is why the default leans framework-positive.

> **In Listing Studio.** The nine-step pipeline is exactly the heavy-plumbing, graph-shaped case: branches, a self-grading loop in *clarify attributes*, parallel fan-out in *assemble launch package*, and a hard rule that nothing publishes until every step reports back. Rebuilding the state, checkpointing, and orchestration for that by hand would be most of the engineering and none of the product.

## The comparison: LangGraph vs CrewAI

> **This comparison is a snapshot, and it will change.** Frameworks ship monthly; capabilities move, gaps close, new entrants arrive. Treat the verdict below as a reasoned position as of mid-2026, not a durable fact, and re-decide on current evidence before you commit. The live, dated matrix lives in the appendices, not here.

First, the wider field in one line each, so the two are placed in context. **Vendor Agents SDKs** (OpenAI's Agents SDK, the Anthropic Agent SDK) are thin, provider-aligned starting points, increasingly capable as the SDKs absorb framework features.[^landscape] **Cloud-coupled stacks** (Google ADK, AWS Bedrock AgentCore, Microsoft Agent Framework) trade portability for managed runtime, durability, and tight integration with their cloud.[^landscape] **Durable-execution engines** (Temporal, Inngest) are not agent frameworks at all but workflow runtimes you can put underneath one when crash-safety is the hard requirement.[^landscape] **AutoGen** pioneered the conversational multi-agent style and has been folded into Microsoft's Agent Framework.[^landscape] Pick from these categories on the same criteria above. The rest of the budget goes to the two most representative open-source choices.

**LangGraph is graph-first.** You model the system as an explicit state machine: nodes, edges, and a shared state schema, with control flow you draw rather than infer. Its strengths are exactly the heavy-plumbing axes: explicit state, built-in checkpointing and durable execution (state persisted after each node, resumable after a crash), and low-level control over what runs when.[^langgraph][^comparison] The price is a steeper ramp; you are writing a graph, and that is more upfront structure than wiring up a few roles.[^comparison]

**CrewAI is role-first.** You describe agents as roles with goals and tools, group them into a crew that collaborates on tasks, and let the higher-level abstraction handle the orchestration. It has two modes, autonomous *Crews* and more deterministic, event-driven *Flows*, and the design lets you stand up a working multi-agent prototype quickly.[^crewai] The trade is the same one Anthropic warns about generally: the higher-level abstraction gives you less direct control and more between you and the prompts than a graph you wrote yourself.[^comparison]

The call. **Pick LangGraph when control and durability are the point:** complex or graph-shaped control flow, long-running jobs that must checkpoint and resume, and a system you expect to operate in production for a long time where you will want to see and shape exactly what happens at each step. **Pick CrewAI when speed to a working multi-agent setup matters more than fine control:** a prototype, a straightforward crew-of-roles task, a team that wants the orchestration handled and is willing to trade some control for it. This is a real call and not a both-are-great wash. For the production case this reference is built around, the heavy-plumbing, graph-shaped, durable one, LangGraph is the closer fit, which is why it is the carrier's stack and the author's production choice. For a faster, more autonomous multi-agent build with less plumbing to express, CrewAI gets you there sooner.

A small honest summary, kept to a few rows, not a scorecard:

| | LangGraph | CrewAI |
|---|---|---|
| Mental model | explicit state graph (nodes, edges, shared state) | roles in a crew, plus event-driven flows |
| Control | low-level, you draw the flow | higher-level, the abstraction drives |
| Durable execution | built-in checkpointing, resumable | session memory; less of the workflow-state story |
| Best fit | complex flow, long-running, production control | fast multi-agent prototype, less plumbing |

The exhaustive, dated, feature-by-feature matrix across every framework lives in Appendix D, [State of Play, 2026](../catalogs/state-of-play.md), and the framework-choice guide in Appendix C, [Decision Frameworks](../catalogs/decision-frameworks.md). This chapter argues the decision; those hold the perishable specifics.

> **From production.** I shipped a real agentic system on LangGraph, a multi-step pipeline of the same shape as Listing Studio, and it earned the choice on the criteria above, not because a demo used it. The pipeline was graph-shaped with branches, loops, and parallel steps, runs were long enough that losing one to a crash was expensive, and we needed explicit state and checkpointing so a failed run resumed instead of starting over and re-paying for the work that had succeeded. The orchestration and durable execution were most of what we would otherwise have rebuilt by hand, and rebuilt worse.

## Gotchas

The framework-positive default has a real downside, and selling it without the tax would be the kind of overclaim this reference exists to avoid. You pay an abstraction to learn and debug. You pay indirection: a stack trace through a framework is longer and less obvious than one through your own loop. And you pay **hidden control flow**: the framework assembles the prompt and you may not see what it actually sent the model, which is the exact opacity Anthropic flags.[^anthropic] That hidden scaffolding is not free at runtime either. The framework's prompt templates and injected context ride in the context window and can bloat it invisibly, a cost covered in [1.5 Context Engineering](context-engineering.md). Mitigate the opacity by logging the raw prompts and responses your framework sends, so the abstraction never hides the one thing you most need when the model misbehaves.

Lock-in is real but its severity is **Contested**, so weigh it honestly rather than treating it as a dealbreaker or a non-issue. A portable open-source library you can fork and walk away from is a light commitment. A cloud-coupled managed runtime that owns your execution is a heavy one, and the bet should be sized accordingly. There is no single answer; the answer is "how hard would it be to leave, and can you live with that."

The sharpest failure mode is the one with its own entry in the [Anti-Patterns Catalog](../catalogs/anti-patterns.md): **cargo-culting the framework.** Adopting LangGraph, or CrewAI, or anything else, because a blog post or a conference demo used it, rather than because the decision criteria pointed there, is how teams end up fighting an abstraction they never needed for a problem a page of SDK code would have solved. The framework is not the skill. Choosing the right one on evidence, for your control flow and your plumbing and your team, is the skill. When the criteria do not clearly call for a framework, the honest default is to stay on the SDK and revisit when the system outgrows it.

## In short

If you are shipping a real agentic system, assume you will want a framework and make it prove otherwise, because the plumbing is real, you will rebuild it under deadline, and you will rebuild it worse. The cases where the raw SDK wins are narrow and worth naming: a single agent calling one or two tools, a throwaway, or a hard requirement to own every layer. Decide on the criteria, not the hype: how much plumbing you would rebuild and whether you would rebuild it well, how graph-shaped your control flow is, whether this is your product or infrastructure, and your team's familiarity and lock-in tolerance. For graph-shaped, long-running, control-heavy production work, LangGraph is the strong default and the one this reference builds on; for a fast multi-agent prototype with less plumbing to express, CrewAI gets you there sooner. Whatever you pick, pick it because the criteria pointed there, never because a demo used it.

## Sources

[^anthropic]: Anthropic, "Building Effective Agents" (2024-12-19). Recommends starting with the raw API: "We suggest that developers start by using LLM APIs directly: many patterns can be implemented in a few lines of code." The framework caution: frameworks "often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug," and "they can also make it tempting to add complexity when a simpler setup would suffice." Quotes verified 2026-06. <https://www.anthropic.com/research/building-effective-agents>
[^langgraph]: LangGraph documentation on persistence and checkpointers: graph state is saved after each node (via savers such as a Postgres-backed checkpointer), so a crashed or paused run resumes from the last checkpoint rather than restarting, and supports time-travel debugging over saved checkpoints. Capability claim is volatile; verify against live LangGraph docs before publish. <https://docs.langchain.com/oss/python/langgraph/persistence>
[^crewai]: CrewAI documentation and 2026 framework overviews: role-and-crew primitives (agents as role + goal + tools, grouped into a crew executing tasks under a process), with two operational modes, autonomous *Crews* and deterministic, event-driven *Flows*. Capability claim is volatile; verify against live CrewAI docs before publish. <https://docs.crewai.com/>
[^comparison]: Cross-framework comparison pieces (2026), used for the LangGraph-vs-CrewAI contrast: LangGraph as an explicit state machine with built-in checkpointing and lower-level control versus a steeper ramp; CrewAI as a higher-level role/crew abstraction that is faster to prototype with less direct control. Perishable landscape content; cite the finding, re-verify the verdict at write time, and re-stamp "Last reviewed." Representative: Redwerk, "LangGraph vs. CrewAI in 2026" <https://redwerk.com/blog/langgraph-vs-crewai/>; and the framework comparisons collected in the appendices.
[^landscape]: 2026 agent-framework landscape surveys, used only for the category names (vendor Agents SDKs; cloud-coupled stacks Google ADK, AWS Bedrock AgentCore, Microsoft Agent Framework; durable-execution engines Temporal and Inngest; AutoGen folded into Microsoft Agent Framework). Categories are stable; specific tools and capabilities are dated, so this is mention-and-link only. See Appendix D, [State of Play, 2026](../catalogs/state-of-play.md). Representative: Firecrawl, "The best open source frameworks for building AI agents in 2026" <https://www.firecrawl.dev/blog/best-open-source-agent-frameworks>.

## See also

- **[1.3 Workflow or Agent?](workflow-or-agent.md)** decides whether you need agentic control flow at all; settle that before this chapter's "how to build it."
- **[1.4 The Augmented LLM](the-augmented-llm.md)** is the base unit the provider SDK gives you for free, the thing a framework wraps and orchestrates.
- **[1.5 Context Engineering](context-engineering.md)** for the hidden cost of framework scaffolding: injected templates and prompts ride in the context window.
- **[2.1 Tool Use](../the-unit/tool-use.md)** is the tool-call loop a framework's plumbing wraps; build it once by hand to understand what you are buying.
- **[2.4 MCP](../the-unit/mcp.md)** is the connectivity layer that is increasingly the thin-wrapper alternative to a heavy framework.
- **[7.3 Checkpointing](../reliability/stopping-gracefully.md)** is what durable execution actually is as a reliability technique, the headline reason graph-shaped systems reach for a framework.
- **[8.1 Observability](../production/seeing-inside.md)** is the tracing you either get as hooks from a framework or roll yourself, and the antidote to hidden control flow.
- **[9.2 Multi-Agent](../frontier/more-than-one-agent.md)** is a major reason teams adopt a framework, and where CrewAI's role-and-crew model is most at home.
- **Appendix C, [Decision Frameworks](../catalogs/decision-frameworks.md)** and **Appendix D, [State of Play, 2026](../catalogs/state-of-play.md)** hold the live, dated framework-choice guide and feature matrix this chapter deliberately does not freeze.
- **[Anti-Patterns Catalog](../catalogs/anti-patterns.md)** carries the cargo-cult entry this chapter feeds: adopting a framework because a demo used it, not because the criteria pointed there.
