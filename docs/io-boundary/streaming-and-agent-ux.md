# 6.3 Streaming & Agent UX

*Where the person meets the agent. The interface is a two-way control surface fed by a stream of events: your code translates those events once, at its edge, and every step, tick and approval card on screen comes from what the harness did, never from what the model says it did.*

*Also called: token streaming, agent UI, agentic UX, UI message stream (Vercel AI SDK).*

## Why you'd reach for it

The model writes *"Price updated, all done!"* into its transcript, and a moment earlier the pricing tool it called threw an exception. If your interface draws its green tick from the model's sentence, the person watching sees a success that never happened, and they move on to the next product.

Every agent interface answers two questions while the agent works: what is happening, and what can the person do about it. Piping the model's tokens to the screen answers the first for a chatbot and stops working when the agent calls a tool. The tokens carry the model's narration of its work, which can run ahead of the work, describe a plan the harness never executed, or report a result that came back as an error. The harness is the code around the model that runs the tools and enforces the rules (see [2.6 The Harness](../the-unit/the-harness.md)); it is the only part of the system that knows what actually ran.

The second question is where a typewriter UI, one that only prints text as it arrives, fails outright. A person watching an agent needs to stop it, approve the step that changes something, and see what a stop left behind. Rendering text gives them none of that; they need you to treat the stream as a sequence of typed events and the interface as a surface that sends decisions back.

Take the repricer, an agent on a commerce platform that adjusts catalog prices within the merchant's rules, with a merchandiser watching its run on a dashboard. The agent decides to call `update_price` on the Aldsworth standing desk (`supplier_sku` `NV-ALDSWORTH-DM`) with `price_cents` set to 41900, which is $419.00. That call changes what shoppers pay, so it should stop and ask. A dashboard of streamed text shows her the model announcing the change and no button to refuse it. A step row bound to the tool call shows her "awaiting approval", the exact SKU and price, and a decline that guarantees the tool never runs.

Reach for event streaming and a real agent UI when:

- **A person watches the run.** A silent screen gives them no way to tell work from a hang.
- **The agent calls tools.** Each call needs a row whose state the model cannot set.
- **Some actions change the world.** A price, an order, an email: each needs an approval card.
- **The person may need to stop or redirect it.** A stop button needs a stream it can cut.

Skip it when nobody is watching. A nightly batch that rewrites five thousand descriptions needs logs and a report at the end; streaming its tokens to an empty room buys complexity and nothing else.

## What it actually is

An agent UI is a renderer of harness events. The provider streams typed events over a transport (usually SSE, the browser standard for a server pushing a sequence of events down one HTTP response); your code translates them once, at its edge, into a small vocabulary of its own; and the interface derives every displayed state from that vocabulary through a reducer (a function that folds each event into the current UI state), sending stop and approval decisions back the other way.

![Two provider streams, Anthropic Messages events and OpenAI Responses events including an error inside an HTTP 200, cross a dashed line, your edge, into one translator, the only code that reads them. Of the seven kinds of UI event, the translator emits five: text, thinking, done, error and tool_call. The harness, which runs tools and makes writes wait for a person, is the only source of the other two, approval and tool_result. The interface reduces the events. The transcript reads "Price updated, all done!" and is display only; thinking is not displayed. The update_price step, setting the desk to 41900 cents, goes from running to awaiting approval and ends failed, because the tool raised. Approve, decline and stop send decisions back to the harness, bound to the call ID.](streaming-and-agent-ux-event-surface.svg)

Your code makes every structural decision here: how events are translated, what a step row shows, whether an action waits for a person, what gets sanitised for the browser. The model decides what to say and which tool to call. What is particular to agents is that the model's narration can report a success the harness never saw, so the UI must not consult it.

This reference rates each practice on a four-step trust scale: Standard, Established, Emerging, Contested. Streaming itself is Standard: both major model APIs document it as the way to receive a response incrementally.[^1][^2] Rendering tool calls from harness events, with running, done and failed states, is Established, and you can check it on your own screen in the collapsible tool-call rows of a coding agent or chat product you already use. The generative UI protocols under *Ecosystem & tooling* are Emerging; AG-UI is still deprecating event types ahead of its 1.0.[^11] Showing streamed reasoning as an explanation of what the model did is Contested, because research shows reasoning traces often omit the factors that drove the answer.[^3]

Three neighbours share this boundary. The server-side rule that a write waits is 4.3 Human-in-the-Loop; showing the pause is UI work. Emitting events from inside the system is 7.2 Observer. Making a complete response match a schema is [2.2 Structured Output](../the-unit/structured-output.md), and a half-streamed object has no such guarantee.

## How to do it

Start with the vocabulary. Every provider streams a different set of event types, and your front end should know none of them. It sees one shape:

```python
class UIEvent(BaseModel):
    kind: Literal["text", "thinking", "tool_call", "tool_result", "approval", "done", "error"]
    text: str = ""          # text / thinking delta, or an error message
    call_id: str = ""       # tool_call, tool_result, approval
    tool: str = ""
    args: dict = {}
    ok: bool = True         # tool_result only
```

Seven kinds cover a working agent UI: model text, model reasoning, a tool call with complete arguments, its result, an approval request, the end of one model response, and an error. The contract is that only the translator reads provider events, and only the harness emits `tool_result` and `approval`. The model cannot produce either. `done` closes a response, not the run: a response that asks for a tool ends before the tool runs, and the harness decides when the whole run is over.

The harness side turns each tool call into UI events. Tools that change the world wait for a person, and the rule lives in a set in your code (`NEEDS_APPROVAL = {"update_price"}`), never in a prompt:

```python
def run_tool_call(call: UIEvent, tools: dict, approve):
    """Yield the UI events for one tool call; write tools wait for a human."""
    if call.tool in NEEDS_APPROVAL:
        yield UIEvent(kind="approval", call_id=call.call_id, tool=call.tool, args=call.args)
        if not approve(call):  # the person said no: the tool never runs
            yield UIEvent(kind="tool_result", call_id=call.call_id, tool=call.tool,
                          ok=False, text="declined")
            return
    try:
        out = tools[call.tool](**call.args)
        yield UIEvent(kind="tool_result", call_id=call.call_id, tool=call.tool, text=str(out))
    except Exception as exc:  # a failed tool must still end the step visibly
        yield UIEvent(kind="tool_result", call_id=call.call_id, tool=call.tool,
                      ok=False, text=str(exc))
```

The approval event carries the call ID, the tool and the exact arguments, so the card names this call and no other. `approve` is a callable that returns the person's decision. A declined call yields a failed result and returns before the tool is touched. A tool that raises still yields a result, so no step is left spinning.

The UI state comes from the reducer. A step becomes "done" only from a `tool_result`, and an `error` fails every step still open:

```python
def reduce(state: dict, e: UIEvent) -> dict:
    """The UI shows a step as done only when the harness reports a tool result."""
    if e.kind == "text":
        state["transcript"] += e.text  # model prose: display only
    elif e.kind == "tool_call":
        state["steps"][e.call_id] = "running"
    elif e.kind == "approval":
        state["steps"][e.call_id] = "awaiting approval"
    elif e.kind == "tool_result":
        state["steps"][e.call_id] = "done" if e.ok else "failed"
    elif e.kind == "error":  # the stream or a call broke: no step may keep spinning
        state["error"] = e.text
        for call_id, step in state["steps"].items():
            if step in ("running", "awaiting approval"):
                state["steps"][call_id] = "failed"
        if e.call_id:
            state["steps"][e.call_id] = "failed"
    return state
```

A few lines wire the pieces together:

```python
def run_turn(provider_events, translate, tools, approve, state):
    """One model response: translate it, run each tool call, fold every event into state."""
    def emit(ui):
        reduce(state, ui)
        return ui  # in a web app, also send it to the browser as one SSE `data:` line
    for e in translate(provider_events):
        yield emit(e)
        if e.kind == "tool_call":
            for ui in run_tool_call(e, tools, approve):
                yield emit(ui)
```

The listing deliberately leaves out the web endpoint that sends each event to the browser and the step that returns tool results to the model; both are ordinary server code, and that loop is the harness's (2.6).

One run, from the companion repo's tests, using the repricing scenario above:

1. The translator emits `text`, `text`, then one `tool_call` for `update_price` with `{"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 41900}`, only once the arguments are complete. Both providers' scripted streams produce this identical sequence.
2. The step shows `running`, then `awaiting approval` with the SKU and price when the harness emits `approval`.
3. The merchandiser declines. The harness emits a failed `tool_result` with `"declined"`, the step shows `failed`, and the pricing tool is called zero times.
4. In a second run she approves, but the tool raises. The model's text says *"Price updated, all done!"*, and the step still ends `failed`, because the reducer never reads the transcript to decide a step's state.

When a provider adds an event or you switch providers, one translator changes and the dashboard does not.

> **In the companion repo.** `listing-studio/streaming/` holds every listing above, with offline tests on scripted provider streams. They prove that a declined call never runs, that a step is done only from a result, and that a failed, incomplete or broken stream fails every open step.

### What the provider actually sends

Anthropic's Messages API sends each content block as a `content_block_start`, any number of `content_block_delta` events and a `content_block_stop`, between `message_start` and `message_stop`.[^1] Text arrives as `text_delta`, reasoning as `thinking_delta`, and tool arguments as `input_json_delta` carrying a `partial_json` string. That string is not parseable until the block's `content_block_stop`.[^1] By default the API buffers each argument value until it is complete.[^1] Setting `eager_input_streaming` on a tool removes that buffering, and then the string may not be valid JSON at all,[^13] so the Anthropic translator guards the parse and turns a failure into an `error` for that call.

OpenAI's Responses API sends semantic events instead: `response.created`, `response.output_text.delta`, `response.function_call_arguments.delta` and `.done`, and a terminal `response.completed`, `response.failed` or `response.incomplete`.[^5] Only the first of those terminals is success, so the translator maps the other two to `error`. A function call's name and `call_id` arrive on `response.output_item.added`; its complete arguments arrive as one string on `response.function_call_arguments.done`. The translator matches the two by `output_index`, because the item's `id` is optional.[^5]

Two rules hold on both. Errors can arrive as an `error` event inside a stream that opened with HTTP 200, so a status-code check catches nothing;[^1][^5] on the Anthropic wire, an overload shows up this way.[^1] New event types appear over time, and Anthropic's docs say your code should handle unknown types gracefully;[^1] both translators ignore what they do not recognise.

Frameworks add a layer. LangGraph streams in modes such as `messages` for model tokens and `updates` for state after each step, and a subgraph stays silent unless you pass `subgraphs=True`.[^6] Map those into the same vocabulary too.

### Wiring it to a provider

The translators are the only provider-specific code. Each reads raw stream events as dictionaries (the SDK's `model_dump()` of each event) and yields the same `UIEvent` sequence.

=== "OpenAI Responses API"

    ```python
    def translate_openai(events):
        """OpenAI Responses stream: argument deltas end in one `.done` event."""
        names = {}  # output_index -> (call_id, tool name); item.id is optional, the index is not
        for e in events:
            t = e["type"]
            if t == "response.output_text.delta":
                yield UIEvent(kind="text", text=e["delta"])
            elif t == "response.reasoning_summary_text.delta":
                yield UIEvent(kind="thinking", text=e["delta"])
            elif t == "response.output_item.added" and e["item"]["type"] == "function_call":
                item = e["item"]
                names[e["output_index"]] = (item["call_id"], item["name"])
            elif t == "response.function_call_arguments.done":
                if e["output_index"] not in names:  # never die mid-stream: say so instead
                    yield UIEvent(kind="error", text="arguments for an unknown tool call")
                    continue
                call_id, name = names[e["output_index"]]
                yield UIEvent(kind="tool_call", call_id=call_id, tool=name,
                              args=json.loads(e["arguments"]))
            elif t == "response.completed":
                yield UIEvent(kind="done")
            elif t in ("response.failed", "response.incomplete"):  # terminal, and not success
                r = e.get("response") or {}
                why = r.get("error") or r.get("incomplete_details") or {}
                yield UIEvent(kind="error", text=why.get("message") or why.get("reason") or t)
            elif t == "error":
                yield UIEvent(kind="error", text=e["message"])
            # every other event type: ignored, never fatal
    ```

=== "Anthropic Messages API"

    ```python
    def translate_anthropic(events):
        """Anthropic Messages stream: content blocks arrive as start / delta / stop."""
        tool = None  # the open tool_use block: {"id", "name", "json"}
        for e in events:
            t = e["type"]
            if t == "content_block_start" and e["content_block"]["type"] == "tool_use":
                cb = e["content_block"]
                tool = {"id": cb["id"], "name": cb["name"], "json": ""}
            elif t == "content_block_delta":
                d = e["delta"]
                if d["type"] == "text_delta":
                    yield UIEvent(kind="text", text=d["text"])
                elif d["type"] == "thinking_delta":
                    yield UIEvent(kind="thinking", text=d["thinking"])
                elif d["type"] == "input_json_delta" and tool:
                    tool["json"] += d["partial_json"]  # partial JSON: not parseable yet
            elif t == "content_block_stop" and tool:
                try:
                    args = json.loads(tool["json"] or "{}")  # complete only now
                    yield UIEvent(kind="tool_call", call_id=tool["id"], tool=tool["name"], args=args)
                except json.JSONDecodeError:  # possible with eager_input_streaming: never run it
                    yield UIEvent(kind="error", call_id=tool["id"], tool=tool["name"],
                                  text="invalid tool input")
                tool = None
            elif t == "message_stop":
                yield UIEvent(kind="done")
            elif t == "error":  # arrives as an event after a 200, not an HTTP error
                yield UIEvent(kind="error", text=e["error"]["message"])
            # ping and event types we do not know yet: ignored, never fatal
    ```

### Showing the work honestly

A spinner that outlives the work tells the person something false. Keep "the model is writing" visibly distinct from "your code is running a tool", because they fail differently: one is slow, the other can be wrong.

Reasoning streams need a different default. Anthropic streams thinking deltas and OpenAI streams reasoning summaries (`response.reasoning_summary_text.delta`).[^1][^5] Collapse them, or show a short summary, and never present them as an audit log of why the agent acted: Chen et al. found reasoning models often fail to mention the hints that changed their answers.[^3] The companion reducer receives `thinking` events and deliberately does not display them. When thinking arrives redacted or omitted, show that it happened and nothing more.

### Stop, steer, resume

A stop button needs something to call. For OpenAI background runs there is an explicit `POST /v1/responses/{id}/cancel`.[^7] The Claude Agent SDK's `interrupt()` ends the current response while keeping the session open, so the person can redirect rather than restart.[^8] A message sent during tool calls reaches the model only after they finish,[^8] and the UI should say so. A stop cannot undo a committed write, so a step it cut off should say whether its tool ran, did not run, or is not yet known.

Recovery from a broken stream differs by provider. An OpenAI background response created with streaming on is rejoined by passing the last event's `sequence_number` as `starting_after`;[^7] keep event identity so a reconnect neither repeats text nor reruns a tool. Anthropic's guidance resumes from the most recent text block, because tool-use and thinking blocks "cannot be partially recovered." For Claude 4.5 models and earlier you resume by placing the partial response in an assistant message; for 4.6 and later you add a user message that asks the model to continue from where it left off.[^1] Durable, resumable background runs belong to [7.3 Checkpointing](../reliability/stopping-gracefully.md) and to [8.7 Deployment & Runtimes](../production/deployment-and-runtimes.md).

### Partial structured output

Display a half-streamed object, but let nothing act on it. The Vercel AI SDK says partial outputs streamed via `streamText` "cannot be validated against your provided schema"; its `elementStream` with `Output.array()` yields each array element only once it is complete and validated.[^9] A price parsed from `{"supplier_sku": "NV-ALDSWORTH-DM", "price_` must never reach `update_price`.

## Security & trust

Streaming trades moderation for latency. OpenAI's streaming guide warns that streaming "makes it more difficult to moderate the content of the completions,"[^2] and text a person has already read cannot be unsent. Decide per surface, by what the text could contain and what rendering it could set off, not by who reads it. A shopper-facing assistant may buffer each sentence through a check, or stream with a path to retract a message; a dashboard of your own catalogue data can usually stream, though it still renders text you did not write. Validation and retraction belong to 4.4 Guardrails & Safety.

The rendering boundary is its own risk. OWASP's LLM05:2025, Improper Output Handling, covers model output passed unchecked to a browser, where it can become cross-site scripting or Markdown injection.[^10] Streamed Markdown adds a quieter risk: an image link the model was induced to write makes the browser fetch that URL, and the URL's query string can carry data out. Strip raw HTML, allowlist the hosts images and links may load from, set a Content Security Policy (a response header that limits what a page may load), and never execute UI code the model authored. How the model gets induced in the first place is [4.6 Prompt Injection](../craft/prompt-injection.md).

## Ecosystem & tooling

Generative UI is an interface the agent assembles at run time rather than one you hard-coded, and its three protocols sit at different layers. AG-UI is an event protocol between an agent backend and a front end, independent of transport, with lifecycle events (`RunStarted`, `RunFinished`, `RunError`) plus text, tool-call, state and reasoning events.[^11] A2UI has the agent send declarative JSON that names components from a catalogue you, the developer, registered, and its own description says it is "never executable code."[^4] MCP Apps lets a tool name a `ui://` resource, an HTML application the server supplies, which the host renders in a sandboxed iframe and talks to with JSON-RPC over `postMessage`.[^12] They combine: AG-UI carries events, A2UI describes a component, MCP Apps hosts a server's app. A2UI's trust rests on the catalogue and MCP Apps' on the sandbox; neither puts model-authored HTML into your page. When the model picks a registered product card to show a shopper, that is tool use with a picture attached ([2.1 Tool Use](../the-unit/tool-use.md)). 9.3 The Protocol Landscape compares the protocols in depth.

## Gotchas

- **A buffering proxy defeats SSE.** A reverse proxy or CDN that buffers responses delivers the whole stream at the end; turn buffering off for the streaming route.
- **The SDK hides the error event.** Anthropic's docs say SDK users never receive the in-stream `error`; the SDK ends the stream and raises.[^1] Catch that exception and emit your own `error` event, as the companion wrappers do, so the reducer can fail the open steps.
- **UI state leaking into context.** The snapshots that drive your dashboard are not model context. Keep them out of the prompt, and bound tool-result history in long sessions with 5.4 Compaction.
- **An approval the client can forge.** The card is a rendering. The server must check that the approval matches the pending call ID and refuse an expired or already-resolved one; the gate is 4.3's.

## In short

Translate provider events once, at your edge, into a small fixed vocabulary, and let the interface derive every step from harness events, never from the model's prose. Parse tool arguments only when complete, fail every open step on an error, bind each approval card to one call ID, and give the stop button a real cancel to call. Decide what to buffer by what the text could contain and set off, not by who reads it. Pick a generative UI protocol for the layer it serves, and render nothing the model wrote as code.

<small class="chapter-meta">**Maturity: Standard (event streaming) / Established (rendering from harness events) / Emerging (generative UI protocols)** (both APIs document event streaming; the UI protocols are still renaming events) · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Anthropic, "Streaming messages." <https://platform.claude.com/docs/en/build-with-claude/streaming>
[^2]: OpenAI, "Streaming API responses." <https://developers.openai.com/api/docs/guides/streaming-responses>
[^3]: Chen, Y., et al., "Reasoning Models Don't Always Say What They Think" (2025), arXiv:2505.05410. <https://arxiv.org/abs/2505.05410>
[^4]: A2UI. <https://a2ui.org>
[^5]: OpenAI, "Responses streaming events" (API reference). <https://developers.openai.com/api/reference/resources/responses/streaming-events>
[^6]: LangChain, "Streaming" (LangGraph). <https://docs.langchain.com/oss/python/langgraph/streaming>
[^7]: OpenAI, "Background mode." <https://developers.openai.com/api/docs/guides/background>
[^8]: Anthropic, "Send messages to a running agent" (Claude Agent SDK). <https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode>
[^9]: Vercel, AI SDK, "Generating structured data." <https://ai-sdk.dev/docs/ai-sdk-core/generating-structured-data>
[^10]: OWASP, "LLM05:2025 Improper Output Handling." <https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/>
[^11]: AG-UI, "Events." <https://docs.ag-ui.com/concepts/events>
[^12]: Model Context Protocol, "MCP Apps." <https://modelcontextprotocol.io/extensions/apps/overview>
[^13]: Anthropic, "Fine-grained tool streaming." <https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming>

## See also

- [2.1 Tool Use](../the-unit/tool-use.md), because every tool-call row on screen renders one of its calls.
- [2.2 Structured Output](../the-unit/structured-output.md), for the complete-object guarantee that a partial stream does not have.
- 4.3 Human-in-the-Loop, for the server-side gate the approval card renders.
- 4.4 Guardrails & Safety, for checking and retracting what was streamed.
- 7.2 Observer, for emitting the events this chapter displays.
- 6.4 Voice & Realtime Agents, where interruption becomes barge-in.

## Further reading

- Anthropic, [Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming): the full event flow, delta types and recovery rules, with raw SSE examples.
- OpenAI, [Responses streaming events](https://developers.openai.com/api/reference/resources/responses/streaming-events): every event type with its schema, including the tool-specific ones this chapter skips.
- AG-UI, [Events](https://docs.ag-ui.com/concepts/events): the closest thing to a shared vocabulary for agent-to-front-end events.
- OWASP, [LLM05:2025 Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/): the rendering-boundary risks in one page.
- Chen et al., [Reasoning Models Don't Always Say What They Think](https://arxiv.org/abs/2505.05410): the evidence for not treating streamed reasoning as an explanation.
