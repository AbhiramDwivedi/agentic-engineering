# 2.5 The Agent Loop

*The model picks each next step and decides when it has finished. Your code runs the steps, shows the model what happened, and checks whether "finished" is true.*

*Also called: the agentic loop, the ReAct loop, the tool-use loop. One pass is a turn (Anthropic Agent SDK, OpenAI Agents SDK) or, in LangGraph, a super-step (one round of graph nodes; see Gotcha 3); the ceiling is a max-turns, iteration or recursion limit.*

## Why you'd reach for it

Ask a pricing agent for a price, let its reply run out of output tokens halfway through, and the simplest tool loop hands you *"The price should be"* as a finished answer. That loop, the one [Tool Use](tool-use.md) builds, keeps running tools while the model asks for them and treats whatever it said last as the result.

That loop reads "no tool call" as "done", and the two are different things. A model reply can stop without a tool call because the model finished, or because the provider cut it off at the token limit, refused it, or paused a long server-side tool run. Each reply carries a stop reason that says which. Two more endings never show up as a stop reason at all: the model keeps retrying a call that keeps failing, or it says it is done when it is not. And a model that never says done runs until something outside it stops the run.

Take the price step in Listing Studio, the pipeline at the fictional commerce platform Stockwell that turns a supplier's product feed into a store listing. The step sets `price_cents` for the Aldsworth dual-motor sit-stand desk, and the supplier's contract sets a minimum advertised price (MAP) of $399; a listed price under it can get the catalog dropped. The step takes several turns: look up competitor prices, check a candidate against the floor, then submit it for human review, which moves the listing from `draft` to `review`. Each bad ending has its own cost. A truncated reply gets recorded as a priced listing. A dead market feed gets retried until the step budget is gone. The model reports *"submitted"* with nothing queued, and the listing sits in `draft` while the team believes it moved. Or it queues $389, and a busy reviewer is the only thing between that price and the store.

The fix is to make the loop say why it ended: branch on the provider's stop reason instead of the absence of tool calls, count repeated failures, check "done" in code, and cap the steps. Every run then returns one of five named exits, and only one of them is an answer you can ship.

You need this when:

- the model chooses the next tool, and you cannot say in advance how many steps a run takes;
- a run can end in something other than an answer: truncated, refused, stuck;
- "done" means something your code can check, such as a row written, a price queued, a test passing.

When the steps are fixed and known in advance (look up, then check, then submit), write them as code and call the model once per step. A [prompt chain](../composition/prompt-chaining.md) has no stop reason to misread, because your code decides when it ends. [Workflow or Agent?](../foundations/workflow-or-agent.md) argues where that line falls.

## What it actually is

An agent loop calls the model, runs whatever tools it asks for, appends the results to what the model reads next, and calls it again. The model decides the next step and when to stop. Your code decides what the stop means: it reads which exit ended the run, checks any claim of "done" against the real system, and enforces a ceiling the model cannot talk its way past.

![A rounded box at the top is the model: it reads everything so far and picks the next step, a tool call or a stop. Below it a rectangle is your code, which branches on how the turn ended. On tool_use, your code runs each call and sends any failure back as an error result the model can read, then asks two questions. If the same call has failed three times, the run exits stalled. If the step cap is reached, it exits ceiling. Otherwise the results are appended and the model is called again. On end_turn, the model's claim of done goes to a code check: was a price queued, at or above the 39900 floor? Yes gives clean, the only exit that is an answer. No gives false_done. Any other stop reason, such as max_tokens or refusal, exits abnormal_stop with no answer. A strip along the bottom traces one real run for the Aldsworth desk: lookup_market times out and comes back as an error, the model retries and gets 41900, 44500 and 39900, check_price passes 41900, submit_for_review queues 41900, and at step 5 the model ends its turn, the check confirms 41900 is queued above the floor, and the run exits clean. Steps 1 to 4 went around the tool_use loop; step 5 went through the check.](the-agent-loop-exits.svg)

The model holding the next decision makes this an agent; Anthropic calls agents "typically just LLMs using tools based on environmental feedback in a loop".[^1] Your code does the executing: it runs each call, appends each result, and bounds the run. [Who Decides?](../foundations/who-decides.md) draws that line in general.

Anthropic says agents must "gain 'ground truth' from the environment at each step", meaning a real tool result in place of the model's guess at one.[^1] ReAct, the 2022 paper that named the pattern of interleaving reasoning steps with tool calls, supports this with a trade-off attached. Against chain-of-thought (the model reasoning step by step in text, with no tools), acting on real observations cut hallucination but brought more reasoning errors; it won on fact checking (Fever), lost on questions that need several lookups (HotpotQA), and the best results combined the two.[^2] Read for a price step, that favours grounding, because an invented competitor price is a hallucination.

Whatever the provider, a run ends in one of five ways:

- **Clean end.** The model stopped on its own (Anthropic's `end_turn`; in the OpenAI Agents SDK, a final output of the type you declared and no tool calls[^5]) and your code's check passed.
- **Abnormal stop.** The provider ended the reply first. Anthropic's names are `max_tokens` (out of output tokens), `model_context_window_exceeded`, `refusal`, and `pause_turn` (a server-side tool such as web search hit its own iteration limit). None is a finished answer, and none hands your code a complete call: a reply cut off mid-call leaves only part of one.[^3] `stop_sequence` (the reply hit a string you chose) is normal when you set it to mean done; the companion code sets none and treats it as abnormal.
- **Stall.** The model repeats a call that keeps failing. ReAct documents models "repetitively generat[ing] the previous thoughts and actions", which your code can count across turns and the model, reading its own history, often does not notice.[^2]
- **False done.** The model says it finished, and your check says it did not.
- **Ceiling.** Your step cap ran out first. The Anthropic Agent SDK, Anthropic's packaged agent loop, reports this as `error_max_turns` with no `result` field, the OpenAI Agents SDK raises `MaxTurnsExceeded`, and LangGraph raises `GraphRecursionError`.[^4][^5][^6]

Of the seven stop reasons Anthropic's Messages API documents, one means "run the tool", one means the model finished, `stop_sequence` means finished if you set it to, and the other four end a reply with neither a finished answer nor a call your code can run.[^3] A loop that checks only for tool calls treats all six non-tool endings as success, including the four that carry no answer.

The loop's shape is [Standard](../about/how-we-label.md), the accepted default. Anthropic, OpenAI and LangGraph each ship it and document how it ends.[^3][^4][^5][^6] Reading ground truth at each step and detecting stalls are Established, proven and common: they rest on vendor guidance and one peer-reviewed paper, and the paper's evidence for grounding is a trade-off. Tuning when to stop is less settled: none of these sources gives a cap or repeat count that transfers across tasks, since the right cap depends on how many steps the task needs and what a wasted step costs. Treat this chapter's numbers as starting points for your own traces.

Three neighbours get confused with this. [Tool Use](tool-use.md) is one call's contract and the basic loop; this chapter assumes it. [The Outer Loop](../composition/the-outer-loop.md) wraps this one: there, code or a person decides whether to run again, and a verifier checks the work this loop can only report on. When someone calls a system autonomous, ask which loop they mean: in this inner one the model decides, and in the outer one code does. Google ADK's `LoopAgent` is a different thing; ADK describes it as deterministic and not controlled by a model.[^7]

## How to do it

The contract first: one shape for a model reply, whatever provider produced it, and five names for how a run ends.

```python
CONTINUE, END = "tool_use", "end"  # the two stops that are not trouble

# The five ways a run ends. Only CLEAN is an answer.
CLEAN, ABNORMAL, STALLED, FALSE_DONE, CEILING = (
    "clean", "abnormal_stop", "stalled", "false_done", "ceiling",
)


@dataclass
class Call:
    id: str
    name: str
    args: dict


@dataclass
class Turn:  # one model reply, whichever provider produced it
    text: str
    calls: list
    stop: str  # CONTINUE, END, or the provider's own reason (max_tokens, refusal...)


@dataclass
class Result:
    exit: str  # one of the five above
    answer: str | None
    steps: int
    detail: str = ""  # the provider's stop reason, when the exit is ABNORMAL
```

`Turn.stop` carries `CONTINUE`, `END`, or the provider's own reason passed through unchanged, so an abnormal stop keeps its name in your logs.

The loop itself:

```python
def run_tool(tools: dict, call: Call) -> tuple[str, bool]:
    """Return (content, is_error). A failure goes back to the model as a result."""
    try:
        return json.dumps(tools[call.name](**call.args)), False
    except Exception as exc:  # timeout, bad arguments, unknown tool
        return f"{type(exc).__name__}: {exc}", True


def run_loop(model, tools, history, verify, max_steps=8, max_repeats=3) -> Result:
    failures = Counter()  # how often each exact call has failed
    for step in range(1, max_steps + 1):
        turn = model(history)
        history.append({"role": "assistant", "text": turn.text, "calls": turn.calls})
        if turn.stop == END:
            # The model says it is done. Your code checks the claim.
            exit_ = CLEAN if verify() else FALSE_DONE
            return Result(exit_, turn.text, step)
        if turn.stop != CONTINUE:
            # Truncated, refused, paused: no tool call, and no answer.
            return Result(ABNORMAL, None, step, detail=turn.stop)
        for call in turn.calls:
            content, is_error = run_tool(tools, call)
            history.append(
                {"role": "tool", "id": call.id, "content": content, "is_error": is_error}
            )
            if is_error:
                failures[(call.name, json.dumps(call.args, sort_keys=True))] += 1
        if max(failures.values(), default=0) >= max_repeats:
            return Result(STALLED, None, step)  # same call, same failure, again
    return Result(CEILING, None, max_steps)  # a cap hit is not "done"
```

Three things here go past the loop in [Tool Use](tool-use.md). `run_tool` turns any exception into a result with `is_error` set, so a timeout reaches the model as something to act on. The branch reads `turn.stop`, never "were there calls?", so a truncated reply returns `ABNORMAL` with no answer. And two guards live in code: `failures` counts each exact failed call (name plus sorted arguments) across the whole run, and the `for` bound is the ceiling. Each pass of that `for` is one turn, a model call plus the tools it asked for, and `step` counts turns. When the model says it is done, `verify`, a check that takes no arguments (the tests pass `lambda: price_is_valid(submitted, SKU)`), picks between `CLEAN` and `FALSE_DONE`, and in both cases the model's text comes back as `answer` so you can log what it claimed.

The price step's tools, and the check behind "done":

<details markdown>
<summary>make_tools and price_is_valid</summary>

```python
def make_tools(submitted: list) -> dict:
    def lookup_market(supplier_sku: str) -> dict:
        """Competitor prices for a product, in cents."""
        # Raises TimeoutError when the feed is slow; the loop turns that into
        # an is_error result the model can read and retry.
        return {"prices_cents": market_feed(supplier_sku)}

    def submit_for_review(supplier_sku: str, price_cents: int) -> dict:
        """Queue a price for human review. It does not check the price."""
        submitted.append(price_cents)
        return {"queued": True, "price_cents": price_cents}

    return {
        "lookup_market": lookup_market,
        "check_price": check_price,
        "submit_for_review": submit_for_review,
    }


def price_is_valid(submitted: list, sku: str) -> bool:
    """The code check behind "done": something was submitted, and it clears the floor."""
    return bool(submitted) and check_price(sku, submitted[-1])["ok"]
```

</details>

`submit_for_review` queues whatever price it is handed. That is deliberate, so the loop's own check has a bad price to catch; in production, validate in the tool too. `price_is_valid` reuses `check_price` from [Tool Use](tool-use.md), so "done" means a price was queued and it clears the floor, whatever the model says about it.

> **In the companion repo.** `listing-studio/agent_loop/` holds the full runnable code: the loop, the price-step tools, `make_model` (which turns the history into each API's message format) and all three provider variants. The runs below use a scripted fake model, so they run offline; `listing-studio/tests/test_agent_loop.py` asserts each one.[^10]

One run for SKU `NV-ALDSWORTH-DM`, MAP floor 39900 cents:

1. The model calls `lookup_market`. The market feed, a stub that this run's test makes time out, raises `TimeoutError`, and `run_tool` returns `TimeoutError: market feed timed out after 5s; retry` with `is_error` true.
2. The model reads the error and makes the same call again. The feed answers `[41900, 44500, 39900]`. One failure is not a stall: that call's count is 1 of 3.
3. The model calls `check_price` with 41900, which passes.
4. The model calls `submit_for_review` with 41900, which queues it.
5. The model ends its turn. `price_is_valid` finds 41900 queued and above the floor, and the run exits `clean` at step 5.

Change one thing and the run ends another way:

- **Abnormal.** The model's reply stops on `max_tokens` (or `refusal`) with no tool call. The run exits `abnormal_stop`, `answer` is `None`, and the reason sits in `detail`. The loop in [Tool Use](tool-use.md) would have printed the half-reply.
- **Stall.** The feed times out three times and the model retries with identical arguments each time: `stalled` at step 3. Three failed lookups for three different SKUs are three different calls, and the detector stays quiet.
- **False done.** The model announces it is done without calling `submit_for_review`, or after submitting 38900, under the floor: `false_done`. Sending the model back to fix it is the [outer loop's](../composition/the-outer-loop.md) job.
- **Ceiling.** The model checks a new price every turn and never ends. With `max_steps=4` the run exits `ceiling` at step 4, `answer` `None`.

A turn can carry several tool calls; `run_loop` already walks `turn.calls`. The provider is strict about the reply: one result for every call, even a failed one, with the results first in the message and any text after them; break that and Anthropic's API rejects the request with "tool_use ids were found without tool_result blocks immediately after".[^8] The Agent SDK runs read-only tools concurrently and state-changing ones in order.[^4] The companion code runs them in order.

#### Wiring it to a provider

The loop is plain Python. Each raw API needs a `to_turn` that maps its reply onto a `Turn`; LangGraph owns the loop itself, so its tab maps the end state instead (see [Do You Even Need a Framework?](../foundations/do-you-need-a-framework.md) for that trade). The LangGraph tab does not count steps, so it reports `steps` as 0, and it has no stall guard; one would go in middleware, LangChain's hooks that run your code around each model or tool call. `gpt-6.2-sol` is a current OpenAI model id.

=== "LangGraph"

    ```python
    def run_agent(task: str, sku: str, limit: int = 12) -> Result:
        from langchain.agents import create_agent
        from langchain.tools import tool
        from langgraph.errors import GraphRecursionError

        submitted: list = []
        tools = [tool(fn) for fn in make_tools(submitted).values()]
        agent = create_agent("openai:gpt-6.2-sol", tools=tools)
        try:
            # LangGraph owns the loop; recursion_limit is your ceiling. Set it.
            result = agent.invoke(
                {"messages": [{"role": "user", "content": task}]},
                config={"recursion_limit": limit},
            )
        except GraphRecursionError:
            return Result(CEILING, None, limit)
        last = result["messages"][-1]
        reason = last.response_metadata.get("finish_reason")
        if reason != "stop":  # "length", "content_filter": not an answer
            return Result(ABNORMAL, None, 0, detail=str(reason))
        # Stall detection is not built in: add it as middleware, or own the loop.
        return Result(CLEAN if price_is_valid(submitted, sku) else FALSE_DONE, last.content, 0)
    ```

=== "OpenAI Responses API"

    ```python
    def to_turn(response) -> Turn:
        """Map a Responses result onto a Turn. Look at status and refusals, not just calls."""
        calls = [
            Call(i.call_id, i.name, json.loads(i.arguments))
            for i in response.output
            if i.type == "function_call"
        ]
        if calls:
            return Turn(response.output_text, calls, CONTINUE)
        if response.status == "incomplete":  # max_output_tokens, content_filter
            return Turn(response.output_text, [], response.incomplete_details.reason)
        parts = [p for i in response.output if i.type == "message" for p in i.content]
        if any(p.type == "refusal" for p in parts):
            return Turn(response.output_text, [], "refusal")
        return Turn(response.output_text, [], END)
    ```

=== "Anthropic Messages API"

    ```python
    def to_turn(reply) -> Turn:
        """Map a Messages reply onto a Turn. Branch on stop_reason, not on 'no tool_use'."""
        calls = [Call(b.id, b.name, b.input) for b in reply.content if b.type == "tool_use"]
        text = "".join(b.text for b in reply.content if b.type == "text")
        if reply.stop_reason == "tool_use":
            return Turn(text, calls, CONTINUE)
        if reply.stop_reason == "end_turn":
            return Turn(text, calls, END)
        # max_tokens, refusal, pause_turn, model_context_window_exceeded, stop_sequence
        return Turn(text, calls, reply.stop_reason)
    ```

## Gotchas

1. **A forced tool call can loop forever.** Setting `tool_choice` to `required`, or to one named tool, applies to a single request. A loop that resends it every turn leaves the model no way to end a turn without calling a tool, so only the cap stops the run. The OpenAI Agents SDK merged a change in March 2025 that resets `tool_choice` to `auto` after a tool call, but only in two cases: it names one specific tool, or it is `required` and the agent has a single tool.[^9] If you own the loop, reset it yourself after the first call.

2. **Context grows every turn, wherever it is stored.** The model rereads the whole history on every call, and each tool result in it can steer the next step, which is how injected text chains actions through a loop ([Prompt Injection](../craft/prompt-injection.md)). Storing the history server-side with OpenAI's `previous_response_id` or `conversation_id`, which point the API at turns it already holds, saves you resending it,[^5] but the stored turns are still part of what the model reads. When the window fills, compaction summarizes older turns, and the Agent SDK warns that instructions from early in the run may not survive;[^4] [Compaction](../knowledge/compaction-and-the-window.md) covers it.

3. **Set a cap, and count the last turn.** The Agent SDK's `max_turns` defaults to no limit, and its count includes the final text-only reply: set it to exactly the number of tool rounds you expect, and a run that uses them all hits the cap before the model's final reply, ending `error_max_turns` with no result.[^4] Try that on your own SDK install to see a ceiling exit. LangGraph's recursion limit counts super-steps, and the model node and the tool node after it each take one, so the tab's `limit=12` allows roughly six model calls. Its default of 10,007 is no ceiling for a price step, so pass your own.[^6] A step cap is not a spend cap either, and this loop has none; the Agent SDK's `max_budget_usd`, a dollar limit per run, can overshoot by the cost of one response.[^4] [Controlling Cost](../production/controlling-cost.md) owns that. An inner loop with no ceiling is listed in the [Anti-Patterns Catalog](../catalogs/anti-patterns.md).

4. **The stall detector is narrow on purpose.** It counts failed calls with identical arguments across the whole run, so three failures of one call trip it whether or not they are consecutive. A model that varies its arguments, or repeats a call that succeeds, slips past it, and only the cap ends that run. Keep both guards.

5. **The model owns the retry; your code caps it.** After an `is_error` result the model may call the tool again, which is why Anthropic tells you to limit the retries your loop allows.[^8] The Agent SDK returns a permission denial the same way, as a tool result, and the model typically tries another approach or gives up.[^4] Retries your code makes on its own, with backoff, belong to [Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md).

6. **Some abnormal stops want a follow-up.** `pause_turn` arrives only when server-side tools such as web search hit their iteration limit, and the fix is to send the assistant content back unchanged so the model continues. A `max_tokens` stop in the middle of a tool call needs a retry with a higher limit, and Anthropic suggests retrying a `refusal` on another model.[^3] The companion loop reports all three as `abnormal_stop`; a production loop should resend on `pause_turn` and decide per reason whether to retry.

7. **An empty "done" is still a claim.** Anthropic documents replies that end `end_turn` with no content at all.[^3] Here `price_is_valid` catches one, because nothing was queued; a loop that trusts `end_turn` ships the empty string.

## In short

Treat anything but a verified clean end as a failure. Write the loop so every run ends with a named exit, log the exit with the run, and put the step cap where the model's text cannot reach it. When the model says it is done, look at what it queued.

<small class="chapter-meta">**Maturity: Standard** (the loop shape and branching on stop reason) · **Established** (ground truth each step; stall detection) · *Who decides:* the model picks each step and claims done; your code checks the claim and holds the ceiling · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Anthropic, "Building effective agents" (2024-12-19). <https://www.anthropic.com/engineering/building-effective-agents>
[^2]: Yao, S., et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (arXiv 2022; ICLR 2023). <https://arxiv.org/abs/2210.03629> The HotpotQA and Fever comparison is Table 1; the hallucination and reasoning-error finding is the paper's error analysis. Stated here in words, without the scores.
[^3]: Anthropic, "Handling stop reasons" (Claude API docs). <https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons>
[^4]: Anthropic, "How the agent loop works" (Agent SDK docs). <https://code.claude.com/docs/en/agent-sdk/agent-loop> Option names, defaults and result subtypes are version-dependent; checked 2026-11.
[^5]: OpenAI Agents SDK, "Running agents." <https://openai.github.io/openai-agents-python/running_agents/>
[^6]: LangGraph, "Graph API" (recursion limit). <https://docs.langchain.com/oss/python/langgraph/graph-api>
[^7]: Google Agent Development Kit, "Loop agents." <https://adk.dev/agents/workflow-agents/loop-agents/> Wording paraphrased. The page marks template workflow agents such as `LoopAgent` deprecated in favour of graph-based workflows; checked 2026-11.
[^8]: Anthropic, "Handle tool calls" (Claude API docs). <https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls>
[^9]: OpenAI Agents SDK, pull request #263, "Fix potential infinite tool call loop by resetting tool_choice after tool execution" (merged 2025-03-25); the failure was reported earlier in issue #191. <https://github.com/openai/openai-agents-python/pull/263> ; <https://github.com/openai/openai-agents-python/issues/191>
[^10]: Test coverage: the `to_turn` functions are tested against fake response objects; the live provider calls and the LangGraph tab are compile-checked only.

## See also

- [2.1 Tool Use](tool-use.md), the basic loop this chapter extends.
- [2.6 The Harness](the-harness.md), for the hooks and ceilings around the loop.
- [3.7 The Outer Loop](../composition/the-outer-loop.md), where code decides whether to run again.
- [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md), a different loop: a model judging a model's draft.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md), on the review gate `submit_for_review` feeds.
- [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md), for retries your code owns.
- [8.1 Observability](../production/seeing-inside.md), for tracing each turn and logging the exit.
- [9.1 Long-Running Agents](../frontier/when-you-want-autonomy.md), for running a loop with nobody watching.
