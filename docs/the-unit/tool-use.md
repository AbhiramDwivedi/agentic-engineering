# 2.1 Giving the Model Hands

<div class="chapter-meta" markdown>
**Maturity: Standard** (every major vendor documents it, and the base of the augmented LLM) · *Who decides:* the model · *Grounding:* production + research
</div>

*Tool use is when the model decides to call a typed function you expose, and your code decides what that function actually does. The model gets hands; you keep the rules.*

## Why you'd reach for it

Ask a model to price the Aldsworth sit-stand desk and it will give you a number. It will sound certain. Sometimes that number is $379, which is below the $399 minimum advertised price the supplier contract sets, and nothing in the model's weights knows that floor exists. The price reads fine, ships to the storefront, and turns into a MAP violation: a breach that can get the whole catalog delisted by the supplier.

The model is not stupid here. It is blind. The MAP floor lives in your pricing rules, not in its training data, so asking it to respect a number it cannot see is asking it to guess. Tool use removes the guess. You hand the model a function it can call to check a proposed price against the rules, it calls it, and it adjusts.

Reach for a tool whenever the model needs something it cannot reliably produce on its own: a current fact, a ruling from your business logic, a read from your database, or an action in the world. Skip it when your own code already knows what to do. A tool is worth its complexity only when the decision to use it belongs to the model.

## What it actually is

A tool is a typed function the model may choose to invoke. Tool use is the model making that choice. The contract is small and worth seeing in full, because everything else follows from it:

```python
--8<-- "listing-studio/pricing/models.py:contract"
```

`PriceCheckRequest` is what the model fills in when it decides to call the tool. `PriceVerdict` is what your code hands back. The boundary is the whole point. The model owns the proposal; your code owns the ruling.

**The litmus verdict: the model decides.** With the default `tool_choice` of `auto`, the model decides on each turn whether to call a tool or answer directly.[^2] That is a structural decision moving out of your control flow and into the model, which is exactly what separates a genuinely new capability from a function call on a fixed line. When your code calls `check_price`, that is a method invocation you have written since forever. When the model reads the desk's draft listing and decides on its own that this needs a price check, then issues the call, the judgment is the model's.

**The maturity verdict: Standard.** Tool use is documented by every major model vendor and sits at the base of the "augmented LLM," the unit Anthropic puts at the foundation of every agentic system.[^1] It is not emerging and it is not contested. Anthropic calls tool access "one of the highest-leverage primitives you can give an agent," and reports that on benchmarks like SWE-bench, adding even basic tools produces outsized capability gains.[^2] Reach for it without debate.

One distinction keeps people honest. In Listing Studio the pricing step runs on every listing, because the pipeline is code and the pipeline decided that. The agentic part is not that the step runs. It is that inside the step, the model proposes the price and chooses to verify it against the tool rather than emitting a number and moving on. The loop, not the schedule, is where the model decides.

## How to do it

Start with the tool your code owns. It is a plain function with a typed input and a typed output, and its verdict is arithmetic, not opinion:

```python
--8<-- "listing-studio/pricing/tools.py:tool"
```

There is nothing for the model to argue with here. The floor is the larger of the MAP price and the margin floor, the proposed price either clears it or does not, and the reason string says which. The rule lives in code, where the model cannot negotiate with it.

Next, the seam that keeps this testable. You do not want a real model call in a unit test, so the model sits behind a small `Protocol`:

```python
--8<-- "listing-studio/pricing/model_client.py:protocol"
```

A real implementation wraps an LLM. A fake one returns a script. The loop that drives them does not care which, so you can test the decision logic deterministically, with no model call at all.

Then the loop itself, where the model decides:

```python
--8<-- "listing-studio/pricing/agent.py:loop"
```

The `isinstance(decision, ToolCall)` branch is the moment of decision rendered in code. If the model returns a tool call, you run the guardrail and hand back the verdict. If the verdict rejects the price, the loop continues, handing the model the binding floor so it can propose again. The intellectual root of this read-act-observe cycle is the ReAct framing, which interleaves reasoning with tool actions rather than forcing the model to answer in one shot.[^4]

!!! example "In Listing Studio"
    This is step 6 of the pipeline, **price**. The model proposes `price_cents` for the Aldsworth listing, and `check_price` enforces `compliance.map_enforced` and the margin floor before the listing's `status` can move from `draft` to `review`. The proposal is the model's. The gate is Devon's code.

The companion code runs as plain Python so it stays testable in isolation. In the real pipeline the same loop runs inside a LangGraph node, which changes exactly two things: the `ModelClient` wraps a real LLM instead of the scripted fake, and the listing is read from and written to Postgres instead of held in memory. The tool, the contract, and the loop are the same code.

## Gotchas

The model can skip the tool. With `tool_choice: auto` it decides each turn, and sometimes it just answers.[^2] In the companion loop that is the bare-integer path, and the failure-mode test makes it concrete: the model returns $379 directly, never calls the guardrail, and a sub-MAP price ships with `checked` set to `False`. The guardrail would have caught it. The model just never asked.

The fix is structural, not a better prompt. You can nudge the model toward tools in the system prompt, and you can force a call outright with `tool_choice`,[^2] but a nudge is not a guarantee and a forced call still trusts the model to act on the result. The durable answer is to stop treating the verdict as advice. Make the in-policy check a gate your code enforces before `status` moves to `review`, so an unchecked price cannot reach the storefront no matter what the model does. This is the anti-pattern the chapter feeds the catalog: letting the model self-police a rule the code should own.

Tools that touch shared state bring a second problem the model cannot help with. The pricing tool reads and writes the catalog, and so does Maya when she edits the same desk in the dashboard. Two writers, one row. Transactional safety, locking, and isolation are your code's job, because the model decided a price but was never going to manage a database transaction. Guardrails and tool-call validation belong to the application, not the model, a point the OpenAI agent guide makes the same way.[^3]

Tools are not free. Every round trip is another model call, and the tool schemas ride along in the input tokens on every request.[^2] Bound the loop, as `max_steps` does here, so a model that keeps proposing rejected prices fails loudly instead of spinning.

## In short

Give the model the price-check tool, but never let an unchecked price reach `review`. Own the verdict in code, and let the model own only the proposal and the retry. The model may propose. Your typed tool disposes.

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
