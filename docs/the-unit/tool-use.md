# 2.1 Giving the Model Hands

<div class="chapter-meta" markdown>
**Maturity: Standard** (every major vendor ships it, and the base of the augmented LLM) · *Grounding:* production + research
</div>

> "Tool access is one of the highest-leverage primitives you can give an agent."[^2]
>
> Anthropic, *Tool use with Claude*

## 1. Why you'd reach for it

A language model can reason about almost anything you put in the prompt, but it cannot reach outside it. It has no way to look up a fact that postdates its training, read a row from your database, or change anything in the world. Whatever it produces is text. A tool lets it act on the real system instead.

Take pricing. You ask the model to set the price on a sit-stand desk in your catalog, and it gives you a confident $379. The supplier's contract sets a minimum advertised price of $399, but that floor lives in your pricing rules, and the model has never seen it. So the $379 goes live, the price is now below the contract floor, and a sub-MAP price can get your catalog dropped.

Give the model a tool and the problem goes away. You hand it a function that checks a proposed price against the rules. It proposes $379, the function reports a floor of $399, and the model revises. The model still writes the number, but the floor comes from your code.

So reach for a tool when the model needs something it cannot get on its own: a fact that has changed, a value from your data, a check it cannot run, an action in the world. When your own code already holds the answer, call the code and leave the model out of it.

## 2. What it actually is

A tool is a typed function the model can call. The contract is small:

```python
class PriceCheckRequest(BaseModel):
    """What the model fills in when it decides to call the tool."""

    supplier_sku: str
    proposed_price_cents: int = Field(gt=0)


class PriceVerdict(BaseModel):
    """The structured verdict your code hands back to the model."""

    ok: bool
    proposed_price_cents: int
    map_floor_cents: int  # minimum advertised price
    margin_floor_cents: int  # lowest price that clears the margin rule
    floor_cents: int  # max(map, margin): the binding floor
    reason: str
```

`PriceCheckRequest` is what the model fills in. `PriceVerdict` is what your code returns. Two things make a contract the model can actually use. The schema should be strict, so the model cannot invent fields or skip required ones, which on the major APIs means `additionalProperties: false` and every field marked required.[^3] The descriptions have to be good, because the model picks a tool by reading its description, never its code. And keep the set small. Vendors put the comfortable ceiling around twenty tools, past which the model starts choosing from a crowd.[^3]

**Maturity: Standard.** Every major vendor ships tool use, and Anthropic places it at the base of the augmented LLM, the unit it treats as the foundation of an agentic system.[^1] The benchmarks bear this out: on suites like SWE-bench, giving a model even basic tools produces large jumps in what it can do.[^2]

## 3. How to do it

Start with the tool your code owns. It is a plain function with a typed input and a typed output, and the answer it returns is arithmetic:

```python
def check_price(req: PriceCheckRequest) -> PriceVerdict:
    """A typed tool. A deterministic guardrail your code owns, not the model.

    The model decides whether to call this, and with what price. The verdict
    is something it cannot argue with: math, not opinion.
    """
    rule = RULES[req.supplier_sku]
    margin_floor = round(rule.cost_cents / (1 - rule.min_margin_pct))
    floor = max(rule.map_floor_cents, margin_floor)
    ok = req.proposed_price_cents >= floor
    reason = (
        "clears MAP and margin floor"
        if ok
        else (
            f"below binding floor of {floor} cents "
            f"(MAP {rule.map_floor_cents}, margin {margin_floor})"
        )
    )
    return PriceVerdict(
        ok=ok,
        proposed_price_cents=req.proposed_price_cents,
        map_floor_cents=rule.map_floor_cents,
        margin_floor_cents=margin_floor,
        floor_cents=floor,
        reason=reason,
    )
```

The floor is the larger of the MAP price and the margin floor. A proposed price either clears it or gets sent back. Because the rule lives in code, the model cannot talk its way past it.

Next, decide how much say the model gets. With the default `tool_choice` of `auto`, it chooses each turn whether to call a tool or just answer. You can demand a call with `required`, pin it to one specific tool, or shut tools off with `none`.[^3] Auto invites two opposite mistakes, and you will see both: the model skips a tool it needed, or it reaches for one it did not, spending latency and tokens to look up what it already knew.[^8]

The model itself is mocked behind a small `Protocol`, so the loop can be tested without a real model call:

```python
class ToolCall(BaseModel):
    """The model's decision: call this tool with these typed args."""

    name: str
    request: PriceCheckRequest


class ModelClient(Protocol):
    """The boundary. A real impl wraps an LLM; the fake returns a script.

    propose() returns a ToolCall when the model decides to use a tool, or a
    final price in cents (int) when it decides to answer directly.
    """

    def propose(
        self, prompt: str, last_verdict: Optional[dict]
    ) -> "ToolCall | int": ...
```

A real implementation wraps an LLM. A test passes in a fake that returns a scripted decision. The loop does not care which it gets.

Then the loop itself, where the model calls a tool and reacts to what comes back:

```python
def price_listing(model: ModelClient, prompt: str, max_steps: int = 4) -> dict:
    """The model decides each step: call the typed tool, or just answer.

    Returns {"price_cents", "checked", "verdict"}. `checked` is False when the
    model skipped the tool, which is the demonstrable failure mode.
    """
    last_verdict = None
    for _ in range(max_steps):
        decision = model.propose(prompt, last_verdict)
        if isinstance(decision, ToolCall):
            verdict: PriceVerdict = check_price(decision.request)
            last_verdict = verdict.model_dump()
            if verdict.ok:
                return {
                    "price_cents": verdict.proposed_price_cents,
                    "checked": True,
                    "verdict": verdict,
                }
            # not ok: loop, so the model sees the floor and adjusts
            continue
        # decision is an int: the model answered without checking
        return {"price_cents": decision, "checked": False, "verdict": None}
    raise RuntimeError("model did not converge on an in-policy price")
```

The `isinstance(decision, ToolCall)` branch is where the model's choice becomes code. Return a tool call and your code runs the guardrail and hands the result back. If the result rejects the price, the loop comes around again with the binding floor in hand, and the model tries a new number. That read-then-act rhythm is the idea behind ReAct, which threads reasoning through tool calls instead of forcing an answer in one shot.[^4] A model can also return several calls at once; the loop runs them and feeds the results back together.

!!! example "In Listing Studio"
    This is step 6 of the pipeline, **price**. The model proposes `price_cents` for the Aldsworth listing, and `check_price` enforces `compliance.map_enforced` and the margin floor before the listing's `status` can move from `draft` to `review`. Devon's code owns that gate. The model only proposes the number.

The companion code runs as plain Python, which keeps the loop testable on its own. In the real pipeline the same loop runs inside a LangGraph node. That changes two things. The `ModelClient` wraps a real LLM rather than the scripted fake, and the listing is read from and written to Postgres rather than held in memory. The tool, the contract, and the loop are the same code.

## 4. Gotchas

An agent with tools can do real damage, so most of the work is in the failure modes.

1. **The model fabricates arguments.** It calls the right tool with a wrong value: a made-up SKU, a price with an extra zero, a date that never existed. Inventing plausible arguments is among the most common tool failures in the research, and a stronger model shrinks it without closing it.[^5] So validate every argument before you act on it. `PriceCheckRequest` rejects a non-positive price at the type boundary, and a real tool checks that the SKU exists and the value is in range before it touches anything.

2. **Tool results are untrusted input.** A product description you fetch, a row you read, a web page a tool returns: any of it can carry text that reads to the model as an instruction. Treat tool output as data, never as a command, and never let raw output trigger another action unchecked. This is indirect prompt injection, the first entry on the OWASP Top 10 for LLM applications, and injected text can make the agent leak your data or take an action you did not intend.[^6]

3. **The model can skip the tool.** With `tool_choice: auto` it decides each turn, and sometimes it just answers. In the companion loop that is the bare-integer path, and the failure-mode test pins it down: the model returns $379 directly, never calls the guardrail, and a sub-MAP price ships with `checked` set to `False`. The fix is a gate your code enforces before `status` moves to `review`, not a sterner prompt. An unchecked price cannot reach the storefront when reaching it requires a passing check. This is the anti-pattern the chapter feeds the catalog: the model left to police a rule the code should own.

4. **Give each tool the least power that works.** A tool scoped to read one table cannot drop another. Keep the destructive, irreversible actions, the refunds and deletes and publishes, behind a person rather than behind a model's confidence. OWASP calls this excessive agency: the more an over-scoped tool can do, the more damage a single wrong call does.[^6] [Knowing When to Ask](../craft/human-in-the-loop.md) covers the human gate, and [Guardrails & Safety](../craft/guardrails-and-safety.md) covers enforcing it.

5. **Plan for the call to fail.** Tools time out and return half an answer. Make retries idempotent so a repeat does not double-charge. Cap the loop so a model stuck proposing rejected prices fails loudly instead of spinning. And remember that tools writing shared state race with people. When Maya edits the same desk the agent is pricing, two writers fight over one row, and the locking and isolation are your code's job.[^6]

6. **Know how often this works.** On realistic multi-step tasks, even frontier models finish fewer than half, and they hold up worse than that across repeated runs.[^7] That is the case for gating every consequential action and keeping each agent's scope narrow. These models are fluent enough that the unreliability is easy to miss. Design for it anyway.

7. **Tools cost tokens and time.** The schemas ride along in the input on every request, and each call is one more round trip.[^2] Trace every call, so a run that fails can be replayed and debugged.

## 5. In short

Give the model the price-check tool, but never let an unchecked price reach `review`. The model owns the proposal and the retry. Your code owns the schema, the validation, the permissions, and the final say on whether anything the tool returns is acted on.

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
