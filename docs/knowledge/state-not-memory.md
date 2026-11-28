# 5.1 State, Not Memory

*State first, memory later: most of what gets called agent memory is the run's own typed record with a durable backend. Memory is the smaller thing a future run reads so it can behave differently.*

## Why you'd reach for it

Send the Aldsworth sit-stand desk through Listing Studio, the product-onboarding pipeline that is this reference's running example, in which each step reads a shared record of the listing and writes back the fields it owns. Two checks run, one for the minimum advertised price (MAP, the floor a supplier contractually sets) and one for title length, and the record that comes out says only `["title too long"]`. The price was below the floor, the price check said so, and a later step wrote its own list over the first one without raising anything. A record that no longer mentions the violation will publish.

The tempting diagnosis is that the agent forgot, and the tempting fix is a memory layer: a vector store the steps write findings into and search later. That treats a merge bug as a recall problem. The record had a type and no rule for what happens when two steps write the same field, so the last writer won. The fix is a reducer, a function that decides how a new write combines with the value already there; here one annotation tells `flags` to append. Its companion is a checkpointer, which saves the record after each step so it survives a restart. Both belong to the run. A run, in this chapter, is one piece of work carried to its end on one thread (one shopper conversation, one listing job, named by a `thread_id`), however many graph invocations it takes; LangGraph's docs treat each invocation as a single graph run,[^lg-persistence] and this chapter means the larger unit.

Most of what teams call agent memory is state with a durable backend. Build it as typed, reduced, checkpointed state your code owns, and add memory only when a future run must behave differently because of this one.

Reach for a typed, reduced record when:

- more than one step writes the same record, and especially when two run at once;
- a run has to survive a process restart or a pause while a person reviews it;
- someone proposes a "memory layer" and nobody can name the future run that will read it;
- the prompt grows every call because the whole history rides along.

If your agent is one model call with no steps, a local variable is all the state it needs. And if a later run must act differently, as when a shopper's garage size should still be known on their next visit, that is memory, and [5.3 Memory](real-memory.md) (planned) owns it.

## What it actually is

State is what this run needs to finish. Memory is what a future run needs to behave differently. State is a typed record with a schema, one writer per field where the design allows, a reducer for every field that has more than one writer, and a lifetime bounded by its run. Your code owns all of it, and the model sees only the slice of it a step chooses to render into the prompt.

![A two by two grid. The rows ask who reads a stored thing: this run, to finish (state), or a future run, to behave differently (memory). The columns ask who writes it: your code, by schema; or the model, choosing what to keep. Top left, state your code writes: a typed record, reducers on shared fields, a checkpointer keyed by thread_id, and ADK temp: keys. Top right is empty, because state is code deciding throughout. Bottom left, memory your code writes: ADK user: and app: keys, a LangGraph Store write coded into a node, and a fixed rule such as saving the shopper's garage size. Bottom right, memory the model writes: the new half, taught in 5.3. A dashed progress file straddles the rows: state while its task still reads it, memory once a later task does.](state-not-memory-boundary.svg)

Two questions sort anything an agent stores. The reader question (does this run need it to finish, or does a future run need it to behave differently?) decides state or memory. The writer question (does your code write it by schema, or does the model choose what to keep?) decides whether anything agentic is happening. State is code deciding throughout; schemas, merge rules and save points are as old as databases. Memory the model writes is the new half, taught in [5.3](real-memory.md) (planned). Memory your code writes on a fixed rule is memory by scope but ordinary engineering by mechanism.

The shopper assistant on the same storefront shows both. A shopper says their garage is 200 square feet, and three turns later asks whether a heater will cope. Those turns are one conversation on one thread, so one run, and holding the number for it is state. Knowing it when the same shopper comes back next month, on a new thread, is memory.

**The vocabulary disagrees, so use the test.** Vendors routinely call state "memory". LangGraph documents a thread's state as "short-term memory" and its Store, a key-value store outside any one thread built to "retain information across different conversations or sessions", as long-term memory.[^lg-memory] The OpenAI Agents SDK calls its Sessions, a conversation's stored items reloaded before each turn, "built-in session memory".[^openai-sessions] CoALA, a research framework for language-agent design, defines working memory as what the agent holds for the current decision cycle: state under another name.[^coala] [1.4 The Augmented LLM](../foundations/the-augmented-llm.md) used "memory" loosely for anything retained across turns; this chapter splits that into state (this run) and memory (a future run). None of these is wrong; they use one word for two jobs, and the reader question tells you which job a store is doing.

Google's Agent Development Kit (ADK) prefixes its state keys by scope: `temp:` keys are "discarded after the invocation", `user:` keys are "shared across all sessions for that user", and `app:` keys are shared "across all users and sessions".[^adk-state] A `user:` or `app:` key is read by future runs so they behave differently, which makes it memory wearing state's name; `temp:` is state under any reading. The LangGraph Store is memory too, because it is read from other threads, and a different thread is a different run.

**Progress files sit on the line.** When a single task outlasts one context window, the long-running coding harnesses Anthropic has described (a harness is the code around the model that runs its loop, tools and checks) move the task's state into files and version control: a progress log, a feature list with pass flags, an init script, and descriptive commits.[^harness] By the reader question that is state: the task is one run stretched across sessions, with the files standing in for the thread. Anthropic's memory-tool documentation files the same pattern under memory, where a `/memories` directory "turns memory into a recovery mechanism".[^memory-tool] I would call it state while the task that wrote it is still reading it, and memory once a later task reads it to behave differently.

**State reaches the model only when you render it.** [1.5 Context Engineering](../foundations/context-engineering.md) says state and memory both reload into the window, and they do, by the same route: a step picks the fields it needs and writes them into the prompt. A field no step renders costs no tokens, so the record can hold more than the window should. The OpenAI Agents SDK is the exception: by default a session loads its whole stored history ahead of each new input (`SessionSettings(limit=None)`), so state and window are one object until you set `limit=N` or use a compacting session, one that summarises older items to free window space.[^openai-sessions]

**Where control flow lives is a trade-off.** 12-Factor Agents argues in its fifth factor that "you can engineer your application so that you can infer all execution state from the context window", execution state meaning the current step, waiting status and retry counts.[^twelve-factor] Keeping it separate, the factor grants, "may be worthwhile, but may be overkill for your use case". Unifying buys one source of truth with nothing to keep in sync. The cost shows up at compaction: whatever the summary drops was your control flow, and a pending approval inferred from message text disappears with the text. I mildly prefer the step, the retry count and any pending approval as typed fields, and the transcript left as the transcript.

**How proven is it.** On this reference's scale ([How We Label](../about/how-we-label.md)), typed state is Standard: it is a struct with a name, and LangGraph builds every graph on a declared state schema.[^lg-graph] Reducers, per-thread checkpointing and rendering a slice of state are Established, documented in the frameworks, and the first two are reproduced in the companion tests. Progress-file harnesses are Emerging, a published practice from one vendor's team. The distinction itself is Established rather than Standard, because the primary sources file state under "memory" and the vocabulary is unsettled.

Memory proper is state plus three things state does not need: a write policy (what is worth keeping), retrieval (finding it again among everything else) and forgetting (what to drop, and when). Those are [5.3](real-memory.md)'s (planned).

## How to do it

The record comes first. It is plain Python typing: `TypedDict` declares the fields, and `Annotated[list, operator.add]` attaches a reducer (here, list concatenation) to one of them, which LangGraph reads. A node, in the sense [1.4 The Augmented LLM](../foundations/the-augmented-llm.md) uses, is a function that reads the record and returns a partial dict of the fields it changed. The listings leave out imports and the two check nodes; the companion module `listing-studio/state/` has both.

```python
def merge_status(old: dict, new: dict) -> dict:
    """Reducer: step status accumulates; a later write updates only its own step."""
    return {**old, **new}


class RunState(TypedDict):
    supplier_sku: str                              # overwrite: one writer
    price_cents: int | None                        # overwrite: last write wins
    step_status: Annotated[dict, merge_status]     # merged by step name
    flags: Annotated[list, operator.add]           # appended by parallel nodes
```

Two fields overwrite on purpose, because each has one writer and the latest value is the right one. `step_status` merges by step name, so the price step recording `"done"` cannot erase the title step's `"failed"`. An unannotated field defaults to replace, and LangGraph also it ships `add_messages`, a reducer that appends messages and updates any whose ID already exists, for the transcript case.[^lg-graph]

Now take the reducer away and run the two checks in parallel. `StateGraph` is LangGraph's graph builder: you add nodes and edges, then compile it. Both checks run in the same super-step, LangGraph's name for one round of nodes whose writes are applied together at the end.

```python
class UnreducedState(TypedDict):
    price_cents: int
    flags: list          # no reducer: two writers in one step cannot both win


def build(schema):
    g = StateGraph(schema)
    g.add_node("check_map", check_map)
    g.add_node("check_title", check_title)
    g.add_edge(START, "check_map")      # both start in the same step
    g.add_edge(START, "check_title")
    g.add_edge("check_map", END)
    g.add_edge("check_title", END)
    return g.compile()


# build(UnreducedState).invoke({"price_cents": 39000, "flags": []})
# raises InvalidUpdateError (INVALID_CONCURRENT_GRAPH_UPDATE)
```

The graph refuses:

```text
langgraph.errors.InvalidUpdateError: At key 'flags': Can receive only one value per step. Use an Annotated key to handle multiple values.
For troubleshooting, visit: https://docs.langchain.com/oss/python/langgraph/errors/INVALID_CONCURRENT_GRAPH_UPDATE
```

LangGraph raises this because, in its own words, "there is uncertainty around how to update the internal state", and its documented fix is to declare a reducer.[^lg-error] With the reducer back, the same graph keeps both findings:

```python
def run_reduced() -> list:
    # Same graph, but RunState declares flags as Annotated[list, operator.add].
    out = build(RunState).invoke(
        {"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 39000,
         "step_status": {}, "flags": []}
    )
    return out["flags"]     # both writes survive (order is not guaranteed)
```

The quiet failure is the opening's: run the checks one after the other, in separate super-steps, against an unannotated `flags`, and nothing raises; the record ends as `["title too long"]`. The companion tests assert both behaviours.

**Persistence is still state.** The checkpointer saves a snapshot of the record after each super-step, keyed by `thread_id`, so a run can be inspected or continued later. LangGraph's in-memory saver, `InMemorySaver`, keeps them in the process and loses them all on restart.[^lg-persistence]

> **In the companion repo.** The durable saver in the test is `FileSaver`, a deliberately tiny stand-in: LangGraph's in-memory saver plus a pickle file. It is not production storage. The real choices are LangGraph's `SqliteSaver`, which its docs label for local development, and `PostgresSaver`, which they label for production.[^lg-persistence]

```python
class Run(TypedDict):
    supplier_sku: str
    price_cents: int


def price_node(state: Run) -> dict:
    return {"price_cents": 39900}       # MAP for NV-ALDSWORTH-DM


def build(checkpointer):
    g = StateGraph(Run)
    g.add_node("price", price_node)
    g.add_edge(START, "price")
    g.add_edge("price", END)
    return g.compile(checkpointer=checkpointer)


config = {"configurable": {"thread_id": "listing-NV-ALDSWORTH-DM"}}
# Process 1: build(saver).invoke({"supplier_sku": "NV-ALDSWORTH-DM",
#                                 "price_cents": 0}, config)
# Process 2 (after restart), a new saver over the same storage:
#   build(new_saver).get_state(config).values
#   InMemorySaver(): {}      the thread is gone
#   durable saver:   {"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 39900}
```

One run across a restart:

1. Process 1 builds the graph with a saver and invokes it on thread `listing-NV-ALDSWORTH-DM` with `price_cents` at 0.
2. The price node returns 39900, the desk's MAP in cents, and the checkpointer stores a snapshot of the record under that thread.
3. The process exits.
4. Process 2 builds a new saver over the same storage and asks the graph for the thread's state.
5. With `InMemorySaver` the answer is `{}`. With a durable saver it is `{"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 39900}`.

You can check the first half yourself: run any LangGraph graph with `InMemorySaver`, restart the process, and the thread is gone. An OpenAI `SQLiteSession` without a file path is the same, an "In-memory database (lost when process ends)".[^openai-sessions]

A durable checkpoint is what lets a run pause for a reviewer and pick up later. It does not turn the record into memory: the thread it belongs to is the only reader. Resuming and cancelling a half-finished run belong to [7.3 Checkpointing](../reliability/stopping-gracefully.md) (planned).

## Gotchas

**Cargo-cult memory.** A vector store carrying one run's state is an [anti-pattern](../catalogs/anti-patterns.md): retrieval is fuzzy where a field lookup is exact, and no amount of search fixes a missing field or reducer.

**The silent overwrite.** Only the parallel case raises. Give each field one writer or a reducer, and test that both findings survive.

**An in-memory checkpointer in production.** Single-process tests pass, and a restart or deploy drops every thread it held.

**State and window conflated.** Re-sending the full history every call is a choice, sometimes a framework default, that [1.5](../foundations/context-engineering.md) warns about. Render the slice the step needs.

**Control flow kept only in message text.** A pending approval that lives in a sentence vanishes when [5.4 Compaction](compaction-and-the-window.md) (planned) summarises that sentence away.

**Schema changes break persisted threads.** Rename `price_cents` and every paused run's snapshot still carries the old key. Checkpoints need data migration like any stored table.

**Checkpoints keep everything.** A snapshot holds every field, including any personal data a step wrote, for as long as you retain the thread; and a `thread_id` that is not namespaced by tenant (the merchant whose data it is) lets one merchant's run load another's record.

**A progress file nobody prunes.** Left in place after its task ends, it becomes memory with no write policy, and the next task inherits a stale plan. End it with its task unless a later task should read it.

## In short

State first, memory later. Give every multi-step agent a typed record, a reducer on every field more than one step writes, control flow in fields instead of prose, and a durable checkpointer (`SqliteSaver` on a laptop, `PostgresSaver` in production). Render only the slice each step needs. Before anyone adds a memory layer, run a test: delete the store, start a fresh run tomorrow, and see whether anything behaves differently. If nothing does, the store held state, and a missing field or reducer would have served you better than a vector database. Build memory when the answer is yes; that is [5.3](real-memory.md) (planned).

<small class="chapter-meta">**Maturity: Established** (typed state is Standard; the line between state and memory is not settled vocabulary, and progress files are Emerging) · *Who decides:* your code (schema, reducers, checkpointer) · *Grounding:* research + companion repo · *Last reviewed:* 2026-11</small>

## Sources

[^lg-memory]: LangChain, LangGraph "Memory overview". Thread-scoped state as short-term memory; the Store as long-term memory that can "retain information across different conversations or sessions". <https://docs.langchain.com/oss/python/langgraph/memory>
[^openai-sessions]: OpenAI Agents SDK, "Sessions". "Built-in session memory"; the full item history loaded ahead of new input by default (`SessionSettings(limit=None)`), `limit=N` and compaction sessions; `SQLiteSession` without a path as an "In-memory database (lost when process ends)". Class and parameter names move between SDK releases. <https://openai.github.io/openai-agents-python/sessions/>
[^coala]: Theodore R. Sumers, Shunyu Yao, Karthik Narasimhan, Thomas L. Griffiths, "Cognitive Architectures for Language Agents", arXiv:2309.02427 (2023, v3 2024; TMLR). Section 4.1: working memory "maintains active and readily available information as symbolic variables for the current decision cycle". <https://arxiv.org/abs/2309.02427>
[^adk-state]: Google Agent Development Kit, "State" (session state prefixes `temp:`, `user:`, `app:`). <https://adk.dev/sessions/state/>; sessions overview: <https://adk.dev/sessions/>
[^harness]: Justin Young, Anthropic, "Effective harnesses for long-running agents" (2025-11-26). Progress log, feature list with pass flags, init script and descriptive commits as the carry-over between sessions of one long task. <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
[^memory-tool]: Anthropic, "Memory tool" documentation, section "Multisession software development pattern". Marked stable at the time of review. <https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool>
[^twelve-factor]: HumanLayer, 12-Factor Agents, "Factor 5: Unify execution state and business state". Defines execution state as "current step, next step, waiting status, retry counts, etc." and business state as the workflow's message and tool-call history; "This separation creates complexity that may be worthwhile, but may be overkill for your use case." One practitioner's argued opinion, not a measured result. <https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-05-unify-execution-state.md>
[^lg-graph]: LangChain, LangGraph "Graph API overview". State schemas, per-key reducers, the default replace behaviour, `add_messages`, and super-steps. <https://docs.langchain.com/oss/python/langgraph/graph-api>
[^lg-error]: LangChain, LangGraph error reference, `INVALID_CONCURRENT_GRAPH_UPDATE`. The quoted cause and the reducer fix; the error text in the listing above is printed by the companion test run. <https://docs.langchain.com/oss/python/langgraph/errors/INVALID_CONCURRENT_GRAPH_UPDATE>
[^lg-persistence]: LangChain, LangGraph "Persistence". Information kept "beyond a single graph run"; checkpointers and threads; the in-memory saver losing all checkpoints on restart; `SqliteSaver` labelled for local development and `PostgresSaver` for production. <https://docs.langchain.com/oss/python/langgraph/persistence>

## See also

- [1.4 The Augmented LLM](../foundations/the-augmented-llm.md) introduced the node, the state object and `ListingState`; this chapter adds the merge rules and persistence that page deferred.
- [1.5 Context Engineering](../foundations/context-engineering.md) owns the window budget that decides how much of the record a step should render.
- [2.5 The Agent Loop](../the-unit/the-agent-loop.md) (planned) owns how the transcript accrues inside one model's loop; this chapter owns the typed record outside it.
- [3.7 The Outer Loop](../composition/the-outer-loop.md) (planned) decides when to retry; the step status and retry count it reads are fields in this record.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md) (planned) pauses a run on a checkpoint while a person decides.
- [5.2 Retrieval (RAG)](retrieval-rag.md) (planned) is about knowledge the run looks up, which is neither this run's state nor a past run's memory.
- [5.3 Memory](real-memory.md) (planned) takes over where this chapter stops: write policies, retrieval, forgetting and the model-managed memory tool.
- [5.4 Compaction](compaction-and-the-window.md) (planned) for what to do when the transcript outgrows the window, and why control flow should not live only there.
- [7.3 Checkpointing](../reliability/stopping-gracefully.md) (planned) owns save points, cancellation, resumption and durable execution.
- [Anti-Patterns Catalog](../catalogs/anti-patterns.md), where cargo-cult memory is listed.
