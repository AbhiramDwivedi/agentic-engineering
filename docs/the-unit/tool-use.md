# 2.1 Giving the Model Hands

<div class="chapter-meta" markdown>
**Maturity: Standard** (every major vendor documents it, and the base of the augmented LLM) · *Who decides:* the model · *Grounding:* production + research
</div>

*Tool use is when the model decides to call a typed function you expose. Your code decides what that function does.*

## Why you'd reach for it

Ask a model to set the price on the Aldsworth sit-stand desk and it gives you a number that looks reasonable. Sometimes that number is $379. The supplier sets a minimum advertised price of $399, and the model cannot know that, because the floor lives in your pricing rules and never appeared in its training. So the $379 ships to the storefront, and now you have a MAP violation. A supplier can pull your catalog over one of those.

The fix is to stop asking the model to recall the floor and let it look the floor up instead. You give it a function that checks a proposed price against the rules. The model calls the function, reads the result, and revises its number.

Reach for a tool when the model needs something it cannot reliably produce on its own: a current fact, a ruling from your pricing rules, a read from the catalog, an action on a record. If your code already knows what to call and when, that part does not need a tool. What makes it tool use, rather than an ordinary function call, is that the model makes the call.

## What it actually is

A tool is a typed function the model may choose to invoke. Tool use is the model making that choice. The contract is small:

```python
--8<-- "listing-studio/pricing/models.py:contract"
```

`PriceCheckRequest` is what the model fills in when it calls the tool. `PriceVerdict` is what your code hands back. The model proposes; the verdict is yours.

**The litmus verdict: the model decides.** With the default `tool_choice` of `auto`, the model chooses on each turn whether to call a tool or answer directly.[^2] That choice is what separates tool use from an ordinary function call. If your code runs `check_price` on a fixed step, you have been writing that kind of call for decades. If the model reads the draft listing, judges that the price needs checking, and issues the call itself, the decision has moved out of your control flow and into the model.

**The maturity verdict: Standard.** Every major model vendor documents tool use, and Anthropic puts it at the base of the augmented LLM, the unit it treats as the foundation of an agentic system.[^1] Anthropic calls tool access "one of the highest-leverage primitives you can give an agent," and reports that on benchmarks like SWE-bench, adding even basic tools produces large capability gains.[^2]

In Listing Studio the pricing step runs on every listing because the pipeline schedules it, and that scheduling is plain code. What the model decides is narrower: inside the step, it proposes a price and chooses whether to check that price before moving on.

## How to do it

Start with the tool your code owns. It is a plain function with a typed input and a typed output, and the verdict it returns is arithmetic:

```python
--8<-- "listing-studio/pricing/tools.py:tool"
```

The floor is the larger of the MAP price and the margin floor. The proposed price either clears it or it does not, and the `reason` explains the result. Because the rule lives in code, the model cannot talk its way past it.

The seam that keeps this testable is a small `Protocol` in front of the model:

```python
--8<-- "listing-studio/pricing/model_client.py:protocol"
```

A real implementation wraps an LLM. A test passes in a fake that returns a scripted decision. The loop does not care which it gets, so you can test the decision logic without a model call.

Then the loop, where the model decides:

```python
--8<-- "listing-studio/pricing/agent.py:loop"
```

The `isinstance(decision, ToolCall)` branch is where that decision shows up in code. If the model returns a tool call, you run the guardrail and pass the verdict back. If the verdict rejects the price, the loop goes around again with the binding floor in hand, and the model proposes a new number. This read-then-act cycle is the idea behind ReAct, which interleaves reasoning with tool calls instead of making the model commit to an answer in one shot.[^4]

!!! example "In Listing Studio"
    This is step 6 of the pipeline, **price**. The model proposes `price_cents` for the Aldsworth listing, and `check_price` enforces `compliance.map_enforced` and the margin floor before the listing's `status` can move from `draft` to `review`. Devon's code owns that gate. The model only proposes the number.

The companion code runs as plain Python so it stays testable in isolation. In the real pipeline the same loop runs inside a LangGraph node, which changes two things: the `ModelClient` wraps a real LLM rather than the scripted fake, and the listing is read from and written to Postgres rather than held in memory. The tool, the contract, and the loop are the same code.

## Gotchas

The model can skip the tool. With `tool_choice: auto` it decides each turn, and sometimes it just answers.[^2] In the companion loop that is the bare-integer path, and the failure-mode test makes it concrete: the model returns $379 directly, never calls the guardrail, and a sub-MAP price ships with `checked` set to `False`. The guardrail would have caught it.

A better prompt will not fix this; the fix is structural. You can nudge the model toward tools in the system prompt, and you can force a call with `tool_choice`,[^2] but a nudge is not a guarantee, and a forced call still trusts the model to act on the result. The durable answer is to stop treating the verdict as advice. Make the in-policy check a gate your code enforces before `status` moves to `review`, so an unchecked price cannot reach the storefront whatever the model does. This is the anti-pattern the chapter feeds the catalog: letting the model self-police a rule the code should own.

Tools that touch shared state bring a second problem the model cannot help with. The pricing tool reads and writes the catalog, and so does Maya when she edits the same desk in the dashboard. Two writers, one row. Transactional safety, locking, and isolation levels are your code's job, because the model proposed a price and was never going to manage a database transaction. The OpenAI agent guide draws the same line: validation belongs to the application, not the model.[^3]

Tools cost time and money. Every round trip is another model call, and the tool schemas ride along in the input tokens on every request.[^2] Bound the loop, as `max_steps` does here, so a model that keeps proposing rejected prices fails loudly rather than spinning.

## In short

Give the model the price-check tool, but never let an unchecked price reach `review`. The model owns the proposal and the retry; your code owns the verdict.

## Sources

[^1]: Anthropic, "Building effective agents" (2024). <https://www.anthropic.com/research/building-effective-agents>
[^2]: Anthropic, "Tool use with Claude." <https://platform.claude.com/docs/en/docs/build-with-claude/tool-use/overview>
[^3]: OpenAI, "A Practical Guide to Building Agents" (2025). <https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf>
[^4]: Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., and Cao, Y., "ReAct: Synergizing Reasoning and Acting in Language Models" (2022). <https://arxiv.org/abs/2210.03629>

## See also

- [2.2 The Machine-Checkable Contract](structured-output.md), the typed-output side of the same boundary.
- [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md), on enforcing a verdict as a gate.
- [1.2 Who Decides?](../foundations/who-decides.md), the litmus this chapter applies.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for "the model self-polices a rule the code should own."
