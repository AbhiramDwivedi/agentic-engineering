# 8.1 Observability

*Seeing inside: trace and monitor non-deterministic runs so you can debug what the model actually did.*

*Also called: tracing, monitoring, telemetry.*

## Why you'd reach for it

An agent produces a wrong answer, you run it again on the same input, and it produces a right one. With an ordinary service that would be good news, because a bug you can reproduce is a bug you can fix. With an agent it means the evidence is gone.

Take Listing Studio, a pipeline that turns a supplier's spreadsheet into a finished product listing through a chain of model calls and tool calls. A merchandiser reports that the listing for a sit-stand desk reached review claiming a 300 lb weight capacity, where the spec sheet says 250. You rerun the job and the new draft says 250. The log for the bad run shows the job started, the job finished, and every HTTP call returned 200. Nothing in that record says whether the model misread the spec sheet, the parsing tool returned the wrong row, or an earlier step overwrote the field. You close the ticket as "could not reproduce", and next week the bug ships again on another product, where an overstated weight rating is a safety claim with liability attached.

A service's failure lives in its code, which stays put between runs. An agent's failure lives partly in decisions the model made at run time, which leave nothing behind unless you record them. MAST, a taxonomy of why multi-agent LLM systems fail, was built from 150 execution traces, the step-by-step records of real runs, and ships with a dataset of more than 1,600 annotated ones.[^1] A request log holds none of that.

The fix is to record each run as a trace: a tree of records called spans. One root span stands for the whole run, and under it sits a child span for each model call and each tool call, each holding the id of its parent. Ids and token counts go in every time; prompts and tool payloads go in only when you choose, scrubbed before they leave your process. That choice, made before the incident, decides what the desk ticket can tell you. With ids alone, the bad run shows which steps ran, in what order, and how each ended; to see which step wrote 300, the run also needs its content captured. Those capture decisions matter more than the tracing product you choose.

Reach for a trace when:

- **The model picks the path.** A loop or a tool set, where the steps differ from run to run.
- **Work fans out.** Steps run on several workers, and the record has to be joined back up.
- **Someone will ask why.** A merchant or an auditor wants the step that produced a claim.
- **Cost must be attributed.** Finance wants cost per run or per customer.

The counter-trigger is a single model call with a fixed prompt and no tools. Log its request id, model, token counts and finish reason like any API call, and add the span tree once the shape stops being fixed.

## What it actually is

Agent observability is distributed tracing applied to a run whose shape the model decides: one root span per run, a child span for every model call and tool call, each carrying its parent's id, exported out of your process under a capture policy you set before the run starts. The model decides what the run does; your code decides what gets recorded about it, what is kept, and who can read it.

![One agent run drawn as a trace inside your process. A root span, invoke_agent listing-studio, has no parent. Three child spans, chat claude-sonnet-5-5, execute_tool lookup_sku and a second chat, each carry the root's id, and the model's replies decide how many there are. Each span exports as it closes, children first and the root last. By default a span records its ids, plus the answering model, token counts and finish reason, or the tool name, and goes straight across the process boundary to a trace store that rebuilds the tree. Prompts, replies and tool arguments meet an opt-in capture_content gate, off by default. When it is on, a redaction step turns an email address into [contact], and if the redactor fails the content is dropped and the ids kept, all before export.](seeing-inside-trace.svg)

Structurally this is the distributed tracing teams have run for years. What changes with an agent is that you cannot know the tree's shape before the run, and the most useful payload, the text the model read and wrote, is also the riskiest to store.

Tracing practice is Established. Spans with parent ids, export over OTLP (OpenTelemetry's wire protocol), and head and tail sampling (deciding whether to keep a trace when it starts, or once it has finished) are old ideas with long production use. The vocabulary for agent spans is Emerging. The OpenTelemetry GenAI semantic conventions, the shared attribute names for model and agent spans, carry Development status, and their first standalone release, v0.1.0, shipped in November 2026 with breaking changes.[^2] Teach your code the shape and pin the version you emit.

A model-call span requires two attributes, `gen_ai.operation.name` and `gen_ai.provider.name`; a tool-call span requires the operation name and `gen_ai.tool.name`. The operation name says what kind of step the span records: `chat` for a model call, `execute_tool` for a tool call (with the span named `execute_tool {gen_ai.tool.name}`), and `invoke_agent` for an agent run. The spec marks token usage Recommended, including cache and reasoning tokens. Message content (`gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, `gen_ai.tool.definitions`) is Opt-In, which means off unless you turn it on.[^2] Traces debug one run. The spec's duration and token-usage metrics carry the alerts: they are recorded on every call, so they keep counting after you sample traces away.[^2]

Two neighbours get confused with this. [7.2 Observer](../reliability/a-silent-failure-is-worse.md) is the in-process pattern, where your code emits an event as a step completes and subscribers act on it. Observability starts where 7.2 stops, once an event leaves your process and has to be stored, joined and read. 4.2 Evaluation consumes traces: saved runs become regression sets (fixed inputs re-run after every change), and online scorers, graders that run automatically on live traffic, mark each live run.

## How to do it

The cheapest version that works is a context manager that opens a span, makes the currently open span its parent, and exports the span when the block ends. Export goes to a sink, anything with an `export(span)` method: a list in a test, the console, an OTLP exporter in production. Wrap the agent loop in a root span and each model call and tool call in a child, and the tree builds itself. An ordinary tool-calling loop, with the spans added:

```python
def run_listing(sink: Sink, client: Callable[[list], dict],
                tools: dict[str, Callable[..., Any]], request: str,
                capture_content: bool = False) -> str:
    with span(sink, "invoke_agent listing-studio", **{"gen_ai.operation.name": "invoke_agent"}):
        messages: list = [{"role": "user", "content": request}]
        for _ in range(MAX_STEPS):
            reply = traced_chat(sink, client, messages, capture_content)
            call = reply.get("tool_call")
            if call is None:
                return reply["text"]
            with span(sink, f"execute_tool {call['name']}", **{
                "gen_ai.operation.name": "execute_tool",
                "gen_ai.tool.name": call["name"],
            }) as s:
                result = tools[call["name"]](**call["args"])
                if capture_content:
                    s.attributes["tool.arguments"] = call["args"]
            messages.append({"role": "tool", "content": result})
        return "stopped: step cap reached"
```

`span(sink, name, **attributes)` yields a `Span` with a trace id, its own span id and its parent's id, and hands it to `sink.export` when the block exits, including when the block raised; an exporter's error is swallowed so the run carries on. The parent comes from a `ContextVar`, Python's context-local variable, which each thread and async task sees separately, so nesting `with` blocks is all it takes. `traced_chat` adds message content only when `capture_content` is true, copying the message list so later turns cannot rewrite it, and `MAX_STEPS` (4) stops a model that keeps asking for tools.

<details markdown>
<summary>The span primitive and the model-call span</summary>

```python
@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_id: str | None
    attributes: dict[str, Any] = field(default_factory=dict)


class Sink(Protocol):
    def export(self, span: Span) -> None: ...


_current: ContextVar[Span | None] = ContextVar("current_span", default=None)
_ids = itertools.count(1)


@contextmanager
def span(sink: Sink, name: str, **attributes: Any) -> Iterator[Span]:
    parent = _current.get()  # the open span, if any, becomes this span's parent
    s = Span(
        name=name,
        trace_id=parent.trace_id if parent else f"trace-{next(_ids)}",
        span_id=f"span-{next(_ids)}",
        parent_id=parent.span_id if parent else None,
        attributes=dict(attributes),
    )
    token = _current.set(s)
    try:
        yield s
    finally:
        _current.reset(token)
        try:
            sink.export(s)  # exported even when the body raised
        except Exception:
            pass  # a broken exporter costs the span, never the run
```

```python
def traced_chat(sink: Sink, client: Callable[[list], dict], messages: list,
                capture_content: bool = False) -> dict:
    with span(sink, f"chat {MODEL}", **{
        "gen_ai.operation.name": "chat",
        "gen_ai.provider.name": "anthropic",
        "gen_ai.request.model": MODEL,
    }) as s:
        reply = client(messages)
        s.attributes.update({
            "gen_ai.response.model": reply["model"],  # what actually answered
            "gen_ai.usage.input_tokens": reply["input_tokens"],
            "gen_ai.usage.output_tokens": reply["output_tokens"],
            "gen_ai.response.finish_reasons": [reply["finish_reason"]],
        })
        if capture_content:  # opt-in: content is off unless you ask for it
            s.attributes["gen_ai.input.messages"] = list(messages)  # a copy: the list grows later
            s.attributes["gen_ai.output.messages"] = reply["text"]
        return reply
```

</details>

One traced run, where the model asks for a tool and then answers, leaves four spans in the sink in the order chat, execute_tool, chat, invoke_agent, all under one trace id. A span exports when it closes, so the children go first and the root last, and the backend rebuilds the tree from parent ids.

> **In the companion repo.** `listing-studio/telemetry/` runs this loop against a scripted model. The tests check that one run yields four spans under one trace id; that a default model span carries tokens and no content; that a merchant's email becomes `[contact]` before export; that a raising redactor still exports all four spans without content; that a raising sink lets the run finish; that a looping model stops after four calls; and that captured input cannot change after export.

### When the run crosses a process

A `ContextVar` holds the parent inside one process. A real pipeline fans steps out to async workers and sends tool calls to MCP servers ([MCP](../the-unit/mcp.md), the Model Context Protocol, is the open standard for connecting tools to a model application), so the parent has to travel with the work. The standard carrier is the W3C `traceparent` value, which encodes the trace id and the calling span's id. You attach it to the job you enqueue, and the worker opens its spans under it. MCP has settled where it goes on a tool call. SEP-414, an MCP specification proposal now at Final status, puts `traceparent`, `tracestate` (vendor-specific trace state) and `baggage` (key-value pairs that ride along with the request) in the request's `_meta` metadata field, in their W3C formats, so the trace continues from the agent into the tool server.[^3] The companion code runs in one process and does not exercise this.

### The same shape on the OpenTelemetry SDK

In production the OpenTelemetry SDK supplies spans, propagation and exporters, and instrumentation libraries can emit the model-call spans; you add thin manual spans for your own decisions, such as a check's verdict. The listing below opens the root and the first model-call span on the SDK. The companion repo compile-checks it without running an exporter, and its token counts are placeholders.

```python
provider = TracerProvider()
# Batch export, so telemetry never blocks the agent loop.
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
tracer = provider.get_tracer("listing-studio")

with tracer.start_as_current_span("invoke_agent listing-studio") as root:
    root.set_attribute("gen_ai.operation.name", "invoke_agent")
    with tracer.start_as_current_span("chat claude-sonnet-5-5") as chat:
        chat.set_attribute("gen_ai.operation.name", "chat")
        chat.set_attribute("gen_ai.provider.name", "anthropic")
        chat.set_attribute("gen_ai.usage.input_tokens", 412)
        chat.set_attribute("gen_ai.usage.output_tokens", 96)
        # No gen_ai.input.messages here: content stays off unless you opt in.
```

## Security & trust

The default decides what reaches a third party, and two widely used tools ship opposite ones. In the OpenAI Agents SDK, "Tracing is enabled by default", and `trace_include_sensitive_data` defaults to `True`, so model spans carry the request input and response output unless you change it. Setting `OPENAI_AGENTS_DISABLE_TRACING=1` turns tracing off globally, and tracing is unavailable to organizations under Zero Data Retention, a contract under which OpenAI does not retain API request data.[^4] Claude Code goes the other way. Telemetry needs `CLAUDE_CODE_ENABLE_TELEMETRY=1`; trace export is a beta that is off by default and needs `CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1` plus an `OTEL_TRACES_EXPORTER`; and prompt content is redacted unless you set `OTEL_LOG_USER_PROMPTS=1`.[^5] To check it, set `CLAUDE_CODE_ENABLE_TELEMETRY=1` and `OTEL_LOGS_EXPORTER=console` and watch prompt events arrive with their content redacted.

Then set a capture policy. On every span: run, step and parent ids, the operation, model and provider, token counts, finish reason, latency, error class, tool name, and the step's verdict. They are small and carry no customer text. Only on purpose: message content, tool arguments and results, and the system prompt. For large or sensitive payloads the conventions also allow content by reference, `gen_ai.input.messages_ref`, a pointer to storage you control in place of the text.[^2] The spec says of `gen_ai.output.messages` that it is "likely to contain sensitive information including user/PII data", the risk OWASP lists as LLM02:2025 Sensitive Information Disclosure.[^2][^8]

Redact in your own process, before export. Once a prompt carrying a merchant's email reaches a third-party trace store, redaction has turned into a deletion request.

```python
CONTENT_KEYS = ("gen_ai.input.messages", "gen_ai.output.messages", "tool.arguments")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def scrub(text: str) -> str:
    return EMAIL.sub("[contact]", text)


class RedactingSink:
    """Wraps a real sink. Content is scrubbed here, in your process, before export."""

    def __init__(self, inner: Sink, redact: Callable[[str], str] = scrub) -> None:
        self.inner = inner
        self.redact = redact

    def export(self, span: Span) -> None:
        try:
            for key in CONTENT_KEYS:
                if key in span.attributes:
                    span.attributes[key] = self.redact(str(span.attributes[key]))
        except Exception:
            # Fail closed: a broken redactor must not crash the run, and must
            # not let unredacted content out. Drop the content, keep the ids.
            for key in CONTENT_KEYS:
                span.attributes.pop(key, None)
        self.inner.export(span)
```

`RedactingSink` wraps whatever sink you export to and scrubs the three content keys before passing the span on. When the redactor itself fails, the `except` branch still sends the span out with its ids and token counts, and drops the content keys. Langfuse's hook chooses differently. Its `mask_otel_spans` can change span attributes only, never names, ids, parents or resource attributes, and if the hook raises, "Langfuse drops the whole export batch."[^6] That keeps content in too, at the cost of every span in the batch. Who may read traces and how long you keep them is policy, covered in [8.5 Locks, PII & Identity](locks-pii-identity.md).

## Operating in production

**Sampling.** Agent runs are expensive to store whole. Head sampling is cheap, but OpenTelemetry's own documentation notes that "you cannot ensure that all traces with an error within them are sampled with head sampling alone." Tail sampling can keep the failures, but it is harder to implement and operate, and tail samplers "often end up as vendor-specific technology today."[^7] Langfuse samples client-side and per whole trace, with `sample_rate` defaulting to 1, which keeps everything.[^9] For agents I would start from a policy that keeps every failed run and every run an automated check scored low, and samples the healthy majority. That is my reasoning from cost, unmeasured, and the companion code does not sample.

**Where the data lives.** Three vocabularies coexist: the OTel GenAI conventions, OpenInference (Arize's Apache-2.0 instrumentation conventions), and each vendor's native attributes. Langfuse ingests OTLP and maps GenAI, OpenInference and its own attributes, and LangSmith receives spans at an OTLP endpoint.[^10][^11][^12] Choose the platform by where your data may live, and keep instrumentation on OTLP so the choice stays reversible; proprietary SDK calls in agent code are what lock you in. When traces hold personal data that cannot go to a SaaS, self-hosting settles it. Langfuse can be self-hosted,[^10] and Arize's Phoenix is source-available under the Elastic License 2.0, which the OSI does not recognise as open source.[^12]

**Cost per run.** Token counts on model spans, plus a customer or feature attribute on the root span, give you cost per run, per loop iteration and per customer. The provider's report cannot: Anthropic's usage API, which its docs now label legacy, groups by API key, workspace, model and similar dimensions, with no notion of your run.[^13] The conventions define no dollar-cost attribute, so you multiply tokens by your own price table and reconcile against billing. Watch the cache counter: `gen_ai.usage.cache_read.input_tokens` is a subset of `gen_ai.usage.input_tokens`, so adding the two double-counts.[^2]

**Reading a trace.** Take the desk again, with content captured for the flagged run, and find the first span where 300 appears, which is usually earlier than the last span that errored. If the parsing tool's `execute_tool` span returned 250 and the next `chat` span wrote 300, the model misread it. If the tool span itself returned 300, the tool took the wrong row. If a step upstream of the draft wrote 300 over a field that already held 250, the overwrite is the bug. With content off you can still check finish reasons and empty tool results, since a truncated reply upstream explains many strange answers downstream, and diff the trace against a passing run on similar input. This order is practitioner method and unmeasured. Online scorers write their verdicts back onto traces (Braintrust records each scorer run as a score span).[^14] Online evals are still Emerging, and 4.2 Evaluation covers them.

## Gotchas

1. **With content off you see the shape alone.** Under the defaults recommended here, the desk trace leaves out which call wrote 300 and what it read. Plan for it before the incident: run a flagged slice of jobs with `capture_content=True` behind `RedactingSink`, or store content by reference (`gen_ai.input.messages_ref`) in a store you control.

2. **Record the model that answered.** Put `gen_ai.response.model` beside the request model, and a prompt or code version on the root span. Otherwise a provider moving an alias to a new snapshot shows up as a random regression.

3. **Attribute names move.** The GenAI conventions are in Development and have shipped breaking changes,[^2] so a hard-coded name can quietly stop matching your dashboards. Pin the version and keep the names in one module. For the same reason, "OTel GenAI compliant" from a vendor means compliant with some version; ask which.

4. **Telemetry must never take the run down.** A failing exporter or redaction hook should cost you the span and leave the listing intact. Export in batches off the hot path, and test that a raising sink or hook lets the run finish, as the companion tests do.

## In short

Trace every agent run as a tree: a root span for the run and a child for each model call and tool call, with parent ids carried across every process boundary. Put ids, model names, token counts and finish reasons on every span, keep content off by default, and scrub it in your own process whenever you turn it on. Emit OTLP against a pinned version of the GenAI conventions, so the platform stays a choice you can reverse, and when you sample, keep every failure. The dashboard you buy matters less than those capture decisions, which every later run inherits.

<small class="chapter-meta">**Maturity: Established** (tracing practice is proven; the OTel GenAI conventions and online evals are Emerging) · *Who decides:* your code · *Grounding:* research + companion repo · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Cemri, M., et al., "Why Do Multi-Agent LLM Systems Fail?" (2025), arXiv:2503.13657. <https://arxiv.org/abs/2503.13657>
[^2]: OpenTelemetry, GenAI semantic conventions, `semantic-conventions-genai` v0.1.0 (November 2026), status Development; see the client inference span, `execute_tool` span and metrics pages. The conventions previously lived in the main semantic-conventions repository. <https://github.com/open-telemetry/semantic-conventions-genai>
[^3]: Model Context Protocol, "SEP-414: Document OpenTelemetry Trace Context Propagation Conventions" (Final). <https://modelcontextprotocol.io/seps/414-request-meta>
[^4]: OpenAI, Agents SDK, "Tracing." <https://openai.github.io/openai-agents-python/tracing/>
[^5]: Anthropic, Claude Code documentation, "Monitoring." <https://code.claude.com/docs/en/monitoring-usage>
[^6]: Langfuse, "Masking sensitive LLM data." <https://langfuse.com/docs/observability/features/masking>
[^7]: OpenTelemetry, "Sampling." <https://opentelemetry.io/docs/concepts/sampling/>
[^8]: OWASP, "LLM02:2025 Sensitive Information Disclosure." <https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/>
[^9]: Langfuse, "Sampling." <https://langfuse.com/docs/observability/features/sampling>
[^10]: Langfuse, "OpenTelemetry (OTEL) for LLM Observability." <https://langfuse.com/integrations/native/opentelemetry>
[^11]: LangSmith, "Trace with OpenTelemetry." <https://docs.langchain.com/langsmith/trace-with-opentelemetry>
[^12]: Arize, OpenInference repository (Apache-2.0) <https://github.com/Arize-ai/openinference> and Phoenix repository (Elastic License 2.0) <https://github.com/Arize-ai/phoenix>.
[^13]: Anthropic, "Usage and Cost API" (marked legacy; the Usage and Cost Analytics API is recommended for new integrations). <https://platform.claude.com/docs/en/manage-claude/usage-cost-api>
[^14]: Braintrust, "Score production traces." <https://docs.braintrust.dev/observe/score-online>

## See also

- [7.2 Observer](../reliability/a-silent-failure-is-worse.md), the in-process events that this chapter's spans carry out of the process.
- [2.5 The Agent Loop](../the-unit/the-agent-loop.md), the loop whose steps become child spans, and [3.7 The Outer Loop](../composition/the-outer-loop.md), whose stop conditions a trace should record.
- [2.6 The Harness](../the-unit/the-harness.md), whose hooks are where many tools attach telemetry.
- [2.4 MCP](../the-unit/mcp.md), the tool boundary that trace context now crosses.
- 4.2 Evaluation, which turns saved traces into regression sets and scores live ones.
- [8.4 Controlling Cost](controlling-cost.md), for the levers once per-run cost is visible.
- [8.5 Locks, PII & Identity](locks-pii-identity.md), for who may read traces and how long they are kept.
- [8.6 Governance & Compliance](governance-and-compliance.md), where a trace becomes an audit record.
- [6.3 Streaming & Agent UX](../io-boundary/streaming-and-agent-ux.md), for showing a run's progress while it is still running.
- [8.7 Deployment & Runtimes](deployment-and-runtimes.md), for liveness of the workers your spans run on.

## Further reading

- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai): the attribute names and span shapes, with each one's stability level.
- [OpenTelemetry, "Sampling"](https://opentelemetry.io/docs/concepts/sampling/): head against tail sampling, and what each can and cannot keep.
- [Cemri et al., "Why Do Multi-Agent LLM Systems Fail?"](https://arxiv.org/abs/2503.13657): a failure taxonomy built from annotated traces, useful as a checklist when reading one.
- [OpenAI Agents SDK, "Tracing"](https://openai.github.io/openai-agents-python/tracing/): a working default-on tracer, and the settings that change what it captures.
- [Langfuse, "Masking sensitive LLM data"](https://langfuse.com/docs/observability/features/masking): one platform's redaction hook, with its limits stated plainly.
