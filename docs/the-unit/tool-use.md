# 2.1 Giving the Model Hands

<div class="chapter-meta" markdown>
**Maturity: Standard** (every major vendor ships it, and the base of the augmented LLM) · *Grounding:* production + research
</div>

> "Tool access is one of the highest-leverage primitives you can give an agent."[^2]
>
> Anthropic, *Tool use with Claude*

## 1. Why you'd reach for it

A language model is a brilliant talker with no hands and a frozen memory. It can reason about almost anything you put in front of it, yet it cannot look up a fact that appeared after training, read a row from your database, or change anything in the world. Left alone, it can only produce text. Tool use is how it stops talking and starts doing.

Pricing shows the gap. Ask a model to set the price on a sit-stand desk in your catalog and it hands you a confident number, say $379. The desk's supplier enforces a minimum advertised price of $399, and that floor lives in your pricing rules, not in anything the model ever read. The number looks fine, ships to the storefront, and becomes a contract violation that can get your catalog pulled.

The model never had a chance, because the floor was never in front of it. Give it a tool and the blindness lifts: a function that checks a price against the rules. It proposes $379, the tool answers that the floor is $399, and it tries again. The model still does the talking. Your code keeps the facts.

So reach for a tool whenever the model needs something it cannot produce on its own. A fact that changes. A ruling from your rules. A read from your data, or an action on a record. When your code already holds the answer, skip the model and run the code.

## 2. What it actually is

A tool is a typed function the model can call. The contract is small:

```python
--8<-- "listing-studio/pricing/models.py:contract"
```

`PriceCheckRequest` is what the model fills in. `PriceVerdict` is what your code returns. Two things make a contract the model can actually use. The schema should be strict, so the model cannot invent fields or skip required ones, which on the major APIs means `additionalProperties: false` and every field marked required.[^3] The descriptions have to be good, because the model picks a tool by reading its description, never its code. And keep the set small. Vendors put the comfortable ceiling around twenty tools, past which the model starts choosing from a crowd.[^3]

**Maturity: Standard.** Every major vendor ships tool use, and Anthropic places it at the base of the augmented LLM, the unit it treats as the foundation of an agentic system.[^1] The benchmarks back the enthusiasm: on suites like SWE-bench, giving a model even basic tools produces large jumps in what it can do.[^2]

## 3. How to do it

Start with the tool your code owns. It is a plain function with a typed input and a typed output, and the answer it returns is arithmetic:

```python
--8<-- "listing-studio/pricing/tools.py:tool"
```

The floor is the larger of the MAP price and the margin floor. A proposed price either clears it or gets sent back. Because the rule lives in code, the model cannot talk its way past it.

Next, decide how much say the model gets. With the default `tool_choice` of `auto`, it chooses each turn whether to call a tool or just answer. You can demand a call with `required`, pin it to one specific tool, or shut tools off with `none`.[^3] Auto invites two opposite mistakes, and you will see both: the model skips a tool it needed, or it reaches for one it did not, spending latency and tokens to look up what it already knew.[^8]

The seam that keeps this testable is a small `Protocol` standing in front of the model:

```python
--8<-- "listing-studio/pricing/model_client.py:protocol"
```

A real one wraps an LLM. A test passes in a fake that returns a scripted decision. The loop does not care which it gets, so you can exercise the decision logic with no model call at all.

Then the loop itself, where the model calls a tool and reacts to what comes back:

```python
--8<-- "listing-studio/pricing/agent.py:loop"
```

The `isinstance(decision, ToolCall)` branch is where the model's choice becomes code. Return a tool call and your code runs the guardrail and hands the result back. If the result rejects the price, the loop comes around again with the binding floor in hand, and the model tries a new number. That read-then-act rhythm is the idea behind ReAct, which threads reasoning through tool calls instead of forcing an answer in one shot.[^4] A model can also fire several calls at once; the loop runs them and feeds the results back together.

!!! example "In Listing Studio"
    This is step 6 of the pipeline, **price**. The model proposes `price_cents` for the Aldsworth listing, and `check_price` enforces `compliance.map_enforced` and the margin floor before the listing's `status` can move from `draft` to `review`. Devon's code owns that gate. The model only proposes the number.

The companion code runs as plain Python, which keeps the loop testable on its own. In the real pipeline the same loop runs inside a LangGraph node. That changes two things. The `ModelClient` wraps a real LLM rather than the scripted fake, and the listing is read from and written to Postgres rather than held in memory. The tool, the contract, and the loop are the same code.

## 4. Gotchas

Tool use is the moment an agent stops being a chatbot and gets the power to do real harm, so most of the craft is in the failure modes.

1. **The model fabricates arguments.** It calls the right tool with a wrong value: a made-up SKU, a price with an extra zero, a date that never existed. Inventing plausible arguments is among the most common tool failures in the research, and a stronger model shrinks it without closing it.[^5] So validate every argument before you act on it. `PriceCheckRequest` rejects a non-positive price at the type boundary, and a real tool checks that the SKU exists and the value is in range before it touches anything.

2. **Tool results are untrusted input.** A product description you fetch, a row you read, a web page a tool returns: any of it can carry text that reads to the model as an instruction. Treat tool output as data, never as a command, and never let raw output trigger another action unchecked. This is indirect prompt injection, the first entry on the OWASP Top 10 for LLM applications, and it is what turns a helpful agent into a way out for your data.[^6]

3. **The model can skip the tool.** With `tool_choice: auto` it decides each turn, and sometimes it just answers. In the companion loop that is the bare-integer path, and the failure-mode test pins it down: the model returns $379 directly, never calls the guardrail, and a sub-MAP price ships with `checked` set to `False`. The fix is a gate your code enforces before `status` moves to `review`, not a sterner prompt. An unchecked price cannot reach the storefront when reaching it requires a passing check. This is the anti-pattern the chapter feeds the catalog: the model left to police a rule the code should own.

4. **Give each tool the least power that works.** A tool scoped to read one table cannot drop another. Keep the destructive, irreversible actions, the refunds and deletes and publishes, behind a person rather than behind a model's confidence. OWASP calls this excessive agency, and it is the line between a bug and an incident.[^6] [Knowing When to Ask](../craft/human-in-the-loop.md) covers the human gate, and [Guardrails & Safety](../craft/guardrails-and-safety.md) covers enforcing it.

5. **Plan for the call to fail.** Tools time out and return half an answer. Make retries idempotent so a repeat does not double-charge. Cap the loop so a model stuck proposing rejected prices fails loudly instead of spinning. And remember that tools writing shared state race with people. When Maya edits the same desk the agent is pricing, two writers fight over one row, and the locking and isolation are your code's job.[^6]

6. **Know how often this works.** The honest number matters more than the demo. On realistic multi-step tasks, even frontier models finish fewer than half, and they hold up worse than that across repeated runs.[^7] That is the case for gating every consequential action and keeping each agent's scope narrow. A fluent tool-using agent is useful and unreliable at the same time, and the design has to answer for the second half.

7. **Tools cost tokens and time.** The schemas ride along in the input on every request, and each call is one more round trip.[^2] Trace every call, because a run you cannot replay is a run you cannot debug.

## 5. In short

Give the model the price-check tool, but never let an unchecked price reach `review`. The model owns the proposal and the retry. Your code owns the schema, the validation, the permissions, and the last word on whether anything the tool returns is allowed to matter.

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
