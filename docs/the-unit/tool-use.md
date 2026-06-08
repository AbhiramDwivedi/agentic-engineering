# 2.1 Giving the Model Hands

<div class="chapter-meta" markdown>
**Maturity: Standard** (every major vendor ships it, and the base of the augmented LLM) · *Grounding:* production + research
</div>

*A tool is a typed function the model can choose to call. Tool use is the model making that choice. Your code owns what the tool does, and whether its result is allowed to matter.*

## Why you'd reach for it

Ask a model to set the price on the Aldsworth sit-stand desk and it gives you a number that looks reasonable. Sometimes that number is $379. The supplier sets a minimum advertised price of $399, and the model cannot know that. The floor lives in your pricing rules and never appeared in its training. So the $379 ships to the storefront, and now you have a MAP violation. A supplier can pull your catalog over one of those.

The fix is to stop asking the model to recall the floor and let it look the floor up instead. You give it a function that checks a proposed price against the rules. The model calls the function, reads the result, and revises its number.

Reach for a tool when the model needs something it cannot reliably produce on its own. A current fact. A ruling from your pricing rules. A read from the catalog, or an action on a record. If your code already knows what to call and when, that part does not need a tool.

## What it actually is

A tool is a typed function the model can call. The contract is small:

```python
--8<-- "listing-studio/pricing/models.py:contract"
```

`PriceCheckRequest` is what the model fills in. `PriceVerdict` is what your code returns. Two things make a contract the model can use well. The schema should be strict, so the model cannot invent fields or omit required ones. On the major APIs that means setting `additionalProperties: false` and marking every field required.[^3] The descriptions also have to be good. The model chooses a tool from its description, not from its code. Vendors suggest keeping the number of tools small, under about twenty, so the model is not picking from a crowd.[^3]

**Maturity: Standard.** Every major model vendor ships tool use. Anthropic places it at the base of the augmented LLM, the unit it treats as the foundation of an agentic system.[^1] Anthropic calls tool access "one of the highest-leverage primitives you can give an agent," and reports that on benchmarks like SWE-bench, adding even basic tools produces large jumps in capability.[^2]

## How to do it

Start with the tool your code owns. It is a plain function with a typed input and a typed output, and the result it returns is arithmetic:

```python
--8<-- "listing-studio/pricing/tools.py:tool"
```

The floor is the larger of the MAP price and the margin floor. The proposed price either clears it or it does not. Because the rule lives in code, the model cannot talk its way past it.

You also decide how much say the model gets. With the default `tool_choice` of `auto`, the model chooses on each turn whether to call a tool or answer directly. You can require a call with `required`, force one specific tool, or forbid tools with `none`.[^3] The default invites two opposite failures, and you will meet both. The model skips a tool it needed. Or it calls tools it did not need, paying latency and tokens to look up something it already knew.[^8]

The seam that keeps this testable is a small `Protocol` in front of the model:

```python
--8<-- "listing-studio/pricing/model_client.py:protocol"
```

A real implementation wraps an LLM. A test passes in a fake that returns a scripted decision. The loop does not care which it gets, so you can test the decision logic without a model call.

Then the loop, where the model calls the tool and reacts to the result:

```python
--8<-- "listing-studio/pricing/agent.py:loop"
```

The `isinstance(decision, ToolCall)` branch is where the model's choice shows up in code. If the model returns a tool call, you run the guardrail and pass the result back. If the result rejects the price, the loop goes around again with the binding floor in hand, and the model proposes a new number. This read-then-act cycle is the idea behind ReAct, which interleaves reasoning with tool calls instead of making the model answer in one shot.[^4] A model can also return several calls at once; the loop runs them and feeds the results back together.

!!! example "In Listing Studio"
    This is step 6 of the pipeline, **price**. The model proposes `price_cents` for the Aldsworth listing, and `check_price` enforces `compliance.map_enforced` and the margin floor before the listing's `status` can move from `draft` to `review`. Devon's code owns that gate. The model only proposes the number.

The companion code runs as plain Python so it stays testable in isolation. In the real pipeline the same loop runs inside a LangGraph node. That changes two things. The `ModelClient` wraps a real LLM rather than the scripted fake, and the listing is read from and written to Postgres rather than held in memory. The tool, the contract, and the loop are the same code.

## Gotchas

Tool use is where an agent stops being a chatbot and can do real damage, so most of the work is in the failure modes.

**The model fabricates arguments.** It will call the right tool with a wrong value: a made-up SKU, a price with an extra zero, a date that does not exist. Inventing plausible arguments is one of the most common tool failures measured in the research, and a better model reduces it without removing it.[^5] Validate every argument before you act on it. `PriceCheckRequest` rejects a non-positive price at the type boundary, and a real tool checks that the SKU exists and the value is in range before it touches anything.

**Tool results are untrusted input.** A product description you fetch, a row you read, a web page a tool returns: any of it can carry text that reads as an instruction to the model. Treat tool output as data, never as a command, and do not let raw output trigger another action without a check. This is indirect prompt injection, the first item on the OWASP Top 10 for LLM applications. It is the failure that turns a helpful agent into a way to exfiltrate data.[^6]

**The model can skip the tool.** With `tool_choice: auto` it decides each turn, and sometimes it just answers. In the companion loop that is the bare-integer path. The failure-mode test makes it concrete: the model returns $379 directly, never calls the guardrail, and a sub-MAP price ships with `checked` set to `False`. The fix is a gate your code enforces before `status` moves to `review`, not a sterner prompt. An unchecked price cannot reach the storefront if reaching it requires a passing check. This is the anti-pattern the chapter feeds the catalog: letting the model self-police a rule the code should own.

**Give each tool the least power that works.** A tool scoped to read one table cannot drop another. Keep destructive or irreversible actions, the refunds and deletes and publishes, behind a human approval rather than behind a model's confidence. OWASP files this under excessive agency, and it is the line between a bug and an incident.[^6] [Knowing When to Ask](../craft/human-in-the-loop.md) covers the human gate, and [Guardrails & Safety](../craft/guardrails-and-safety.md) covers enforcing it.

**Plan for the call to fail.** Tools time out and return partial results. Make retries idempotent so a repeat does not double-charge. Bound the loop with a step cap, so a model that keeps proposing rejected prices fails loudly rather than spinning. And remember that tools writing shared state race with people. When Maya edits the same desk the agent is pricing, two writers contend for one row, and the locking and isolation are your code's job.[^6]

**Know how often this works.** The honest number matters more than the demo. On realistic multi-step tasks, even frontier models finish fewer than half, and they are less consistent than that across repeated attempts.[^7] That is the argument for gating every consequential action and keeping each agent's scope narrow. A fluent tool-using agent is useful and unreliable at once, and the design has to answer for the second half.

**Tools cost tokens and time.** The schemas ride in the input on every request, and each call is another round trip.[^2] Trace every tool call, because a run you cannot replay is a run you cannot debug.

## In short

Give the model the price-check tool, but never let an unchecked price reach `review`. The model owns the proposal and the retry. Your code owns the schema, the validation, the permissions, and the final say on whether anything the tool returns is allowed to matter.

## Sources

[^1]: Anthropic, "Building effective agents" (2024). <https://www.anthropic.com/research/building-effective-agents>
[^2]: Anthropic, "Tool use with Claude." <https://platform.claude.com/docs/en/docs/build-with-claude/tool-use/overview>
[^3]: OpenAI, "Function calling." <https://developers.openai.com/api/docs/guides/function-calling>
[^4]: Yao, S., et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022). <https://arxiv.org/abs/2210.03629>
[^5]: Patil, S., et al., "Gorilla: Large Language Model Connected with Massive APIs" (2023). <https://arxiv.org/abs/2305.15334>
[^6]: OWASP, "Top 10 for LLM Applications" (2025). <https://genai.owasp.org/llm-top-10/>
[^7]: Yao, S., et al., "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains" (2024). <https://arxiv.org/abs/2406.12045>
[^8]: Ross, H., et al., "When2Call: When (not) to Call Tools" (2025). <https://arxiv.org/abs/2504.18851>

## See also

- [2.2 The Machine-Checkable Contract](structured-output.md), the typed-output side of the same boundary.
- [2.3 Skills & MCP](skills-and-mcp.md), for connecting tools at scale.
- [4.3 Knowing When to Ask](../craft/human-in-the-loop.md), on gating destructive actions behind a human.
- [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md), on enforcing the check as a gate and defending against injection.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for "the model self-polices a rule the code should own."
