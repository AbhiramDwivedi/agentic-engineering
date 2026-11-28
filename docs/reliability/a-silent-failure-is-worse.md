# 7.2 Observer

*A silent failure is worse: every step reports when it starts and how it ended, to listeners that can see the run but never change it, so a step that ends badly says so even when it did not raise.*

*Also called: callbacks, hooks, lifecycle events, event listeners, stream events.*

## Why you'd reach for it

A model call can fail and still come back as HTTP 200. Anthropic's API reports a refusal as "a normal HTTP 200 response, not an error", and an answer cut off at the token limit arrives the same way, so the exception handler you wrapped around the call never runs.[^1] An agent that reports only its exceptions will show a green tick for a step that produced nothing usable.

An agent run is a chain of steps your code owns: model calls, tool calls, a fan-out (one step handing pieces of work to several parallel workers), a validation gate. Any of them can end without raising. The model refuses, or stops mid-sentence at `max_tokens`, or returns an empty turn; a fan-out worker can hand back nothing; a callback crashes inside a framework whose callback manager swallows handler errors by default.[^2] An asyncio task that dies with nobody awaiting it leaves only a logged diagnostic, "Task exception was never retrieved" with its traceback, and only when the task object is finally collected.[^3] In each case the run carries on, and the screens downstream of it can show progress that did not happen.

Listing Studio, a fictional catalog pipeline, turns a supplier's spreadsheet into a published product listing in nine steps, with a dashboard showing the merchandiser live progress. Suppose step 4, write copy, hits its token limit halfway through the description of a sit-stand desk. The response is well formed, the step returns, the dashboard ticks it off, the brand-voice polish in step 8 smooths the prose around the cut, and step 9 publishes a description that stops mid-thought into the live catalog. The run never failed as far as the code could tell, so nobody was told.

The fix is a rule your code enforces: every step emits an event when it starts and another when it ends or raises, the end event records how it ended (`ok`, `empty`, `truncated`, `refused`), and the listeners receiving those events can read them but never alter the run. The truncated description then shows up as truncated, on the dashboard and in the operator's log, and the decision about what to do with it goes to the code that owns retries and gates (7.1 and 3.1). This chapter covers the emitting side; that code reads the same outcome from the step's result.

You need this when:

- **A run has more than one step** and someone watches it: a user waiting on progress, an operator on call.
- **A step calls a model**, whose bad results arrive as normal responses.
- **Work runs in the background**: worker pools, async tasks, fan-outs whose results you gather later.
- **A framework calls your code through callbacks** and decides what happens when they raise.

A single synchronous model call whose caller checks the stop reason inline needs none of it; check the field and return. And once the events leave the process for a tracing backend, with dashboards and alerts on top, you are in 8.1 Observability, which covers the events once they leave the process.

## What it actually is

An observer is a listener your code notifies at every step boundary of a run. Each step emits a `start` event, then either an `end` event carrying the step's outcome or an `error` event if the step raised. The events go to a list of sinks (a dashboard feed, a log, a metrics counter), and the sinks have no path back into the run: they cannot change a result, retry a step or stop the run, and when one crashes the run carries on without it. The name is the Gang of Four's: a subject notifies its dependents of a change without knowing what they do with it.[^4]

![Three steps of a run drawn as rectangles in a row. Each step sends events down a one-way arrow: start, then end with an outcome (ok, empty, truncated, refused), or error. The arrows meet an emit box that fans each event out to three sinks: a user status line, an operator log, and a bounded queue. One sink is drawn crashed, and the run continues past it. No arrow leads from any sink back to a step.](a-silent-failure-is-worse-events.svg)

Your code decides all of it. The model produces a response; your code reads the stop reason, picks the outcome and emits the event, which makes this engineering you already know, applied to a loop whose failures are unusually quiet. That also separates these events from the status text some agents narrate about themselves (*"Checking the price floor now..."*). Narration is the model choosing what to say about its own progress, and it can report a step as done that never ran. An event emitted at a real step boundary reports what your code saw.

**Maturity: Standard.** Notifying listeners that cannot affect the notifier is decades-old practice, and the major agent SDKs ship a surface for it: OpenAI's Agents SDK has `RunHooks` and `AgentHooks`,[^5] LangChain has callback handlers,[^2] LangGraph has stream modes,[^6] and Claude Code and the Claude Agent SDK have hooks.[^7][^8] Anthropic's guidance asks agents to "gain ground truth from the environment at each step",[^9] and step-boundary events apply the same idea to the people operating the agent. Checking stop reasons is what the providers' own docs tell you to do.[^1] Two parts are less settled. There is no standard event schema, so the one below is this example's design, and tools disagree on what happens when a hook itself crashes. OpenTelemetry, the open-source tracing standard, has semantic conventions for generative AI (shared names for fields such as model and token counts), but they are still marked Development, so aligning your fields with them means tracking a spec that can still change.[^10]

Three neighbours get mistaken for it. A hook that can block an action or rewrite its input belongs to the harness, the code wrapped around the model that decides what it may do: permissions, hooks that gate, stop conditions (2.6 The Harness). Claude Code makes the line visible: `Stop` and `SubagentStop` hooks can block with exit code 2 and `PostToolUse` can inject context, so those gate, while `Notification` and `StopFailure` only observe.[^7] The line runs through what a callback does, not which surface it hangs on: a `SessionStart` hook can add context,[^7] and OpenAI's lifecycle hooks are handed the live agent and run context.[^5] Middleware, code a framework runs around every model or tool call with the power to change the call or its result, sits on the harness side too. Retry and fallback decide what happens after a failure (7.1 Retry & Graceful Degradation); the observer reports the failure and leaves the decision there. And feeding an error back to the model so it can recover is a context move, covered in [Context Engineering](../foundations/context-engineering.md) and in the ninth factor of 12-Factor Agents, a public set of design principles for LLM applications: "compact errors into the context window".[^11] Observer events go to your sinks, never into the model's window, so they cost no tokens.

## How to do it

Three pieces carry the pattern: an event type with an outcome, an `emit` that keeps a broken sink from breaking the run, and a wrapper that puts the events around a step. The contract comes first. A step returns its text and a stop reason normalised across providers (each provider's own values mapped onto one shared vocabulary), and `outcome_of` reads only those two fields:

```python
from __future__ import annotations

import logging
import queue
import time
from dataclasses import dataclass
from typing import Callable, Literal

logger = logging.getLogger(__name__)


Outcome = Literal["ok", "empty", "truncated", "refused", "error"]


@dataclass(frozen=True)
class Event:
    run_id: str
    step_id: str
    parent_id: str | None
    kind: Literal["start", "end", "error"]
    outcome: Outcome | None  # set on "end" and "error" only
    at: float  # monotonic seconds
    error_class: str | None = None


@dataclass(frozen=True)
class StepResult:
    text: str
    stop_reason: str  # normalised: "end_turn", "max_tokens" or "refusal"


def outcome_of(result: StepResult) -> Outcome:
    """Structural check only: presence and stop reason, never meaning."""
    if result.stop_reason == "refusal":
        return "refused"
    if result.stop_reason == "max_tokens":
        return "truncated"
    if not result.text.strip():
        return "empty"
    return "ok"
```

`outcome_of` asks whether text came back and why the model stopped, never whether the text is any good, so a fluent description with the wrong weight capacity reads `ok`. Checking meaning is the job of the code that validates the result ([Structured Output](../the-unit/structured-output.md), the gate in [Prompt Chaining](../composition/prompt-chaining.md), the verify-and-retry loop in 3.7 The Outer Loop), and a gate wrapped as a step of its own reports its verdict the same way. A refusal lands as `end` with outcome `refused` rather than as an `error` event, because the step completed and returned a bad result; `error` means the step itself raised, or handed back something `outcome_of` could not read. The event carries the exception's class name only (Gotcha 5 says why).

Publishing is the second piece. A sink is any callable that takes an event, and `emit` contains each one:

```python
Sink = Callable[[Event], None]


def emit(sinks: list[Sink], event: Event) -> None:
    """Fail open: a broken subscriber is logged, never allowed to break the run."""
    for sink in sinks:
        try:
            sink(event)
        except Exception as exc:
            # Class name only: a sink's error message can carry customer data.
            logger.warning("observer sink failed (%s); run continues",
                           type(exc).__name__)
```

Failing open means the work goes ahead when a listener or check fails; failing closed means it stops. Failing open makes the observer safe to add to a running system: a dashboard feed that throws on an unexpected field is logged, and the event still reaches the next sink and the run the next step. The isolation covers exceptions only. Every sink runs on the step's own thread, so one that blocks stalls the step, which is the next section's problem.

The wrapper is the third:

```python
def observed_step(
    sinks: list[Sink],
    run_id: str,
    name: str,
    step: Callable[[], StepResult],
    parent_id: str | None = None,
) -> StepResult:
    """Run one step, reporting start and end (or error) around it."""
    step_id = f"{run_id}:{name}"

    def event(kind, outcome=None, error_class=None) -> Event:
        return Event(run_id, step_id, parent_id, kind, outcome,
                     time.monotonic(), error_class)

    emit(sinks, event("start"))
    try:
        result = step()
        outcome = outcome_of(result)  # a malformed result is an error too
    except Exception as exc:
        emit(sinks, event("error", "error", type(exc).__name__))
        raise  # the observer reports; deciding what happens next is not its job
    emit(sinks, event("end", outcome))
    return result
```

`outcome_of` runs inside the `try`, so a worker that hands back `None` produces an `error` event instead of a lonely `start`. `step_id` and `parent_id` ride on every event, so when a step fans out to workers, each worker's events point back at the step that launched them and the run can be rebuilt as a tree afterwards. Here `step_id` is the step's name within the run; if a step retries, or two workers share a name, add a per-invocation counter so their histories stay apart. The timestamp is monotonic, which keeps durations honest when the wall clock jumps.

The companion tests (`listing-studio/tests/test_observer.py`) run a truncated step past two sinks, the first raising on every event: the healthy sink ends with `start` and `end · truncated`, and the caller gets the result unchanged.

### Many steps, slow sinks

An in-memory list is fine for one step. A real run has many steps and sinks that do I/O: a websocket to the dashboard, a log shipper, a metrics client. A sink that blocks on the network stalls the step that called it, so slow sinks go behind a bounded queue that a separate reader drains:

```python
class BoundedSink:
    """A queue-backed sink that drops when full, and counts what it dropped."""

    def __init__(self, maxsize: int = 100) -> None:
        self.queue: queue.Queue[Event] = queue.Queue(maxsize=maxsize)
        self.dropped = 0

    def __call__(self, event: Event) -> None:
        try:
            self.queue.put_nowait(event)
        except queue.Full:
            self.dropped += 1  # a slow reader never stalls the run
```

When the reader falls behind, the queue fills and new events are dropped and counted, so a slow dashboard degrades into a lossy one and the run never waits on it. The companion test pushes four events into a two-slot queue and finds two queued and two dropped. Export `dropped` as a metric, because a sink that loses events is a quiet failure of its own.

The reader that drains the queue is yours to start, a thread or an asyncio task, and it brings two traps. A task you start and keep no reference to "may get garbage collected at any time",[^12] so hold a reference to it. And a buffered sink loses what it holds when the process exits, so flush it on shutdown, with a time limit. OpenTelemetry's batch span processor (the component that collects finished trace records and exports them in batches) is the same design: a bounded queue that drops when full and flushes on shutdown.[^13] Flushing when a run is cancelled partway through belongs to 7.3 Checkpointing.

The same stream feeds two readers. The user's view is short and ordered (*writing description, truncated, retrying*); the operator's carries the ids, durations and error classes. Build both as projections of one stream, so the user's status line reports the same facts as the operator's log rather than a story of its own. Rendering that view in a browser is 6.3 Streaming & Agent UX.

> **In Listing Studio.** The live dashboard is the observer's sink on every step, and nothing publishes until every earlier step has reported back. The publish gate reads each step's outcome from its returned `StepResult`, through `outcome_of`, and never from the event stream: the queue can drop an event, and a gate that decides whether to publish cannot be lossy. The dashboard only displays that value.

#### Wiring it to a provider

The step callable is where each provider's stop signal becomes a `StepResult`, and the fields differ. (`llm` and `client` are the provider clients, created at module level in the companion files.) LangChain passes the provider's own reason through in `response_metadata`, with each provider's vocabulary, so the map names OpenAI's and Anthropic's values; extend it before you switch providers. OpenAI's Responses API reports an incomplete response in `incomplete_details.reason` (for example `max_output_tokens` or `content_filter`) and a refusal as a content item of type `refusal`;[^14] the tab treats a filtered response as refused and any other early stop as truncated. Anthropic's Messages API puts it all in `stop_reason`, including `model_context_window_exceeded`, which its docs say to treat as truncated.[^1] Gemini, not shown, signals trouble with a `finishReason` other than `STOP`, such as `MAX_TOKENS`, `SAFETY`, `RECITATION` or `MALFORMED_FUNCTION_CALL`.[^15]

=== "LangGraph"

    ```python
    # Stop reasons as OpenAI and Anthropic name them; extend for other providers.
    NORMALISED = {
        "length": "max_tokens",
        "max_tokens": "max_tokens",
        "model_context_window_exceeded": "max_tokens",
        "content_filter": "refusal",
        "refusal": "refusal",
    }


    def write_description(sinks: list[Sink], run_id: str, sku: str) -> StepResult:
        def step() -> StepResult:
            message = llm.invoke(f"Write a listing description for {sku}.")
            # LangChain surfaces the provider's stop reason in response_metadata.
            meta = message.response_metadata
            reason = meta.get("finish_reason") or meta.get("stop_reason", "")
            return StepResult(
                text=message.text,
                stop_reason=NORMALISED.get(reason, "end_turn"),
            )

        return observed_step(sinks, run_id, "describe", step)
    ```

=== "OpenAI Responses API"

    ```python
    def write_description(sinks: list[Sink], run_id: str, sku: str) -> StepResult:
        def step() -> StepResult:
            response = client.responses.create(
                model="gpt-6.2-sol",
                input=f"Write a listing description for {sku}.",
            )
            # An incomplete or refused response is still a normal return.
            details = response.incomplete_details
            refused = any(
                part.type == "refusal"
                for item in response.output
                if item.type == "message"
                for part in item.content
            )
            if refused or (details and details.reason == "content_filter"):
                reason = "refusal"
            elif details:  # max_output_tokens, or any other early stop
                reason = "max_tokens"
            else:
                reason = "end_turn"
            return StepResult(text=response.output_text, stop_reason=reason)

        return observed_step(sinks, run_id, "describe", step)
    ```

=== "Anthropic Messages API"

    ```python
    def write_description(sinks: list[Sink], run_id: str, sku: str) -> StepResult:
        def step() -> StepResult:
            reply = client.messages.create(
                model="claude-sonnet-5-5",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": f"Write a listing description for {sku}."}
                ],
            )
            # A refusal or truncation is an HTTP 200; stop_reason is the only tell.
            text = "".join(b.text for b in reply.content if b.type == "text")
            reason = reply.stop_reason or "end_turn"
            if reason == "model_context_window_exceeded":
                reason = "max_tokens"  # Anthropic's docs: treat it as truncated
            return StepResult(text=text, stop_reason=reason)

        return observed_step(sinks, run_id, "describe", step)
    ```

## Gotchas

1. **The observer that only hears exceptions.** Wiring events to `except` blocks alone reports every refusal, truncation and empty turn as a success, which is worse than reporting nothing, because the dashboard now vouches for the run. An outcome on every `end` event fixes this, within a limit. `ok` means only that text came back and the model stopped normally. Cemri et al.'s study of multi-agent failures, built from more than 1,600 annotated traces, gives a whole category to runs that end without anyone verifying the result.[^16] A structural outcome does not close that gap; it stops the observer from papering over it.

2. **Hooks fail quietly too.** In Claude Code, a hook that exits 1 is a "non-blocking error" and the action goes ahead;[^7] the Claude Agent SDK surfaces a throwing callback as `hook_callback_failed`;[^8] LangChain's handlers default to `raise_error=False`.[^2] You can watch the first on your own machine: a `PreToolUse` hook that exits 1 lets the tool call proceed, while exit 2 blocks it. Failing open is the right default for an observer, but it means a dead sink looks exactly like a quiet run, so give each sink a heartbeat or a received-events counter that something else watches. A hook that enforces a rule is the opposite case and must fail closed. Claude Code's `onFailure: "block"` turns a hook's crash, timeout or invalid output into a block, though it has no effect on `Stop`, `SubagentStop` or background hooks.[^7]

3. **The framework's hooks may skip the failure branch.** OpenAI's `RunHooks` has agent start and end hooks plus tool, LLM and handoff hooks, and no error hook,[^5] so an exception still reaches the caller but never reaches your sinks unless you wrap the run yourself. Google ADK's plugin error callbacks go the other way: when `on_model_error_callback` or `on_tool_error_callback` returns a value, the error is treated as recovered, which makes them recovery hooks that belong with 7.1.[^17] Before you hand-roll events, check what the framework already emits (LangGraph's `updates`, `custom`, `tasks` and `debug` stream modes, plus `get_stream_writer()` for your own[^6]), and before you trust it, check which branch it leaves out. These names move between releases.

4. **Events pile up.** Each step emits two events, and a run of nine steps that fans out to workers multiplies them. Keep each one small (ids, kind, outcome, timestamp, error class), and when the volume hurts, sample and expire them downstream as 8.1 describes, rather than emitting fewer and losing the failure branch first.

5. **A sink is a data store.** A sink that logs prompts or model output becomes a store of customer data nobody reviewed as one, and an exception message can carry a supplier's pricing or a customer's address. Keep raw exceptions and prompts out of the user's view, and send anything an operator needs beyond the event's fields through redaction first (8.5 Locks, PII & Identity).

## In short

Wrap every step so it emits `start` and then `end` or `error`, set the outcome on `end` from the stop reason and whether any text came back, and make every sink fail open, with the slow ones behind a bounded queue that counts its drops. Treat a refusal or a truncation as a finished step with a bad result, and let the code that owns retries and gates decide what to do about it, reading the result rather than the events. Then give each sink a heartbeat or a counter that something else watches.

<small class="chapter-meta">**Maturity: Standard** (step-boundary events and stop-reason checks are standard practice; the schema and hook-failure handling are Established; OTel alignment is Emerging) · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Anthropic, "Handling stop reasons." <https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons>
[^2]: LangChain, `langchain_core/callbacks/base.py` (`BaseCallbackHandler`, `raise_error`, `on_llm_error`, `on_tool_error`, `on_chain_error`). <https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/callbacks/base.py>
[^3]: Python documentation, "Developing with asyncio," detection of never-retrieved exceptions. <https://docs.python.org/3/library/asyncio-dev.html>
[^4]: Gamma, E., Helm, R., Johnson, R., and Vlissides, J., *Design Patterns: Elements of Reusable Object-Oriented Software* (Addison-Wesley, 1994), "Observer." Cited for the subject/observer split only.
[^5]: OpenAI Agents SDK, "Lifecycle" reference (`RunHooks`, `AgentHooks`). <https://openai.github.io/openai-agents-python/ref/lifecycle/>
[^6]: LangChain, "LangGraph: Streaming." <https://docs.langchain.com/oss/python/langgraph/streaming>
[^7]: Anthropic, "Claude Code hooks reference." <https://code.claude.com/docs/en/hooks>
[^8]: Anthropic, "Intercept and control agent behavior with hooks," Claude Agent SDK. <https://code.claude.com/docs/en/agent-sdk/hooks>
[^9]: Anthropic, "Building effective agents" (2024). <https://www.anthropic.com/research/building-effective-agents>
[^10]: OpenTelemetry, "Semantic conventions for generative AI systems" (status: Development). <https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/README.md>
[^11]: HumanLayer, "12-Factor Agents," Factor 9: Compact errors into the context window. <https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md>
[^12]: Python documentation, "Coroutines and Tasks," `asyncio.create_task`. <https://docs.python.org/3/library/asyncio-task.html>
[^13]: OpenTelemetry, "Tracing SDK" specification, Batching processor. <https://opentelemetry.io/docs/specs/otel/trace/sdk/>
[^14]: OpenAI, "Responses API reference." <https://developers.openai.com/api/reference/resources/responses>
[^15]: Google, "Gemini API: Generating content," `FinishReason`. <https://ai.google.dev/api/generate-content#FinishReason>
[^16]: Cemri, M., Pan, M. Z., Yang, S., et al., "Why Do Multi-Agent LLM Systems Fail?" (2025), arXiv:2503.13657. <https://arxiv.org/abs/2503.13657>
[^17]: Google, "Agent Development Kit: Plugins." <https://adk.dev/plugins/>

## See also

- [3.1 Prompt Chaining](../composition/prompt-chaining.md), whose gate between steps reads the same outcome directly from the step's result.
- [3.3 Orchestrator-Workers](../composition/fan-out.md), where `parent_id` keeps a fan-out's workers attached to the step that launched them.
- [2.2 Structured Output](../the-unit/structured-output.md), one of the semantic checks the structural outcome deliberately leaves out.
- [1.5 Context Engineering](../foundations/context-engineering.md), for the different move of feeding an error back to the model.
- 7.1 Retry & Graceful Degradation, which decides what happens after the failure this chapter reports.
- 8.1 Observability, for the events once they leave the process: tracing, export, dashboards, alerting.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for the failure modes this chapter feeds it.

## Further reading

- Anthropic, [Handling stop reasons](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons): the cleanest statement of which normal-looking responses are failures.
- Claude Code, [Hooks reference](https://code.claude.com/docs/en/hooks): exit codes, `onFailure`, and which events can block, all testable on your own machine.
- LangGraph, [Streaming](https://docs.langchain.com/oss/python/langgraph/streaming): the stream modes a graph already emits before you write any events of your own.
- Cemri et al., [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657): the failure taxonomy, including its category for runs that end unverified.
