# 4.5 Reasoning & Thinking Budgets

*Reasoning models absorbed chain-of-thought prompting into a dial you pay for in output tokens. Start each step as low as its kind of work allows, sweep the levels on your own cases, and raise effort only where the extra thinking pays.*

*Also called: reasoning techniques, hidden chain-of-thought, extended thinking, adaptive thinking, thinking budget, reasoning effort, thinking level.*

## Why you'd reach for it

For a couple of years one of the best-known prompts in the field was five words long. Adding "Let's think step by step" to a question made 2022's models write out their working, and on one arithmetic benchmark accuracy jumped from 17.7% to 78.7%.[^kojima] Send those words to a current reasoning model, one trained to work through a problem in hidden text before it answers, and they buy you little. It does that already, and you pay for every token of it as output whether or not you ever read it.[^openai][^meincke]

So the decision moved. You no longer write the reasoning into the prompt; you buy it through a dial each major vendor now exposes: OpenAI's reasoning effort, Anthropic's effort setting, Google's thinking level.[^openai][^anthropic-effort][^google] The thinking that dial controls is billed as output tokens, counts against the same output cap as the answer, and adds to the wait before the first visible word, because it is generated first. Every effort level is an invoice line before it is a quality setting.

Teams get the dial wrong in two directions. One is to turn effort up to be safe, on the theory that more thinking cannot hurt. It can hurt, in cost and in accuracy: on trivial inputs reasoning models spend hundreds of tokens re-checking an answer they had at the start,[^chen-over] and on some task families accuracy falls as the thinking gets longer.[^gema] The other is to leave effort at the SDK default and never look at it again, so a model upgrade that changes the default, or rejects the old parameter, changes your spend or breaks the request with no code change on your side.

Take a catalog pipeline that turns a supplier's spreadsheet into product listings. One step places each product in the store's taxonomy; another decides which compliance insert a product needs. For a phone case the category, phone accessories, is in the title. For a sit-stand desk the model has to read a materials list, notice formaldehyde in the MDF (medium-density fiberboard) top, and connect it to California's Prop 65, the rule that requires a warning on products containing listed chemicals. The compliance step can earn a few thousand thinking tokens. The taxonomy step is close to a lookup, and at high effort it pays for a page of deliberation on every product.

The fix is a measurement. Run the same cases through the same grader at each effort level, starting from the lowest level the model accepts, record quality, tokens, latency and cost, and ship the cheapest level whose quality holds.

Raise the effort when:

- **The task is multi-step and checkable.** Math, code, multi-hop rules, a plan with dependencies: the families where chain-of-thought helped most in the first place.[^sprague]
- **A wrong answer is expensive.** An agent that changes live prices, or a compliance warning printed on a product page.
- **Nobody is waiting.** Batch jobs can absorb the latency.

Keep it low or off when the step is high-volume and the answer is close to a lookup: classifying an incoming support message, extracting a field, choosing a category.

## What it actually is

A reasoning model is trained to generate intermediate tokens, its thinking, before it writes the answer, and the thinking budget is the control your code has over how much of that it does. The control comes in two shapes, a token ceiling or a named effort level such as `low`, `medium` or `high`, and the vendors have moved toward the named level. Anthropic's manual `budget_tokens` is a legacy mode that its newer models reject; its replacement is adaptive thinking, where the model decides on each request whether to think and for how long, steered by the effort level.[^anthropic-ext] Google's current models take a thinking level.[^google]

![Your code sets an effort level and an output cap; inside that budget the model decides how much to think, producing hidden thinking tokens and then the visible answer; both add up to one billed output-token count. Below, the chapter's scripted sweep: none and low score 0.50, medium scores 1.00 for 6,420 tokens and is shipped, high falls back to 0.50 at 15,120 tokens.](reasoning-and-thinking-budgets-the-dial.svg)

Who decides is split. How to think, and under adaptive thinking whether to think at all, is the model's call, trained in. Your code decides the envelope: the effort level, the output cap, which steps get thinking, and whether you sample several answers and take a vote. The capability is new, but the decision you make about it is an ordinary cost-and-quality trade-off, the same kind you make when you pick a model size.

The research name for why it works is test-time compute: spending more computation at inference instead of on a bigger model. Snell and colleagues found that, matched for compute, extra inference let a smaller model beat one 14 times larger on problems it could already partly solve, with the best allocation depending on difficulty.[^snell] DeepSeek-R1 showed that reinforcement learning on answers a program can check teaches a model to reason at length by itself,[^r1] and s1 controlled thinking length at inference by cutting it off or forcing it to continue, which it called budget forcing.[^s1]

The old prompting techniques each went somewhere different. Chain-of-thought prompting, asking the model to show its working,[^wei] was absorbed. Meincke and colleagues found that on reasoning models it buys marginal accuracy for far more time and tokens, and on non-reasoning models a small average gain with less consistent answers;[^meincke] a meta-analysis by Sprague and colleagues found its benefit concentrated in math and symbolic tasks.[^sprague] Self-consistency, sampling several reasoning paths and taking the majority answer,[^wang] survived as harness code: N calls and a vote, the voting variant covered in [Orchestrator-Workers](../composition/fan-out.md). In Tree of Thoughts the model proposes and scores partial solutions and a search procedure picks which to extend;[^yao] that search is code you build around the model, and it belongs to [Planning](../composition/planning.md).

**Maturity: Established.** All three major vendors ship the dial and document it as a cost decision, and the test-time compute results point the same way on hard, checkable problems, by an amount that depends on difficulty.[^snell][^r1] The surface around the dial is less settled: thinking across tool calls changed on all three vendors within a year, so treat any wire detail here as dated, and reasoning as an oversight signal is contested (Gotcha 4).

## How to do it

The mechanics are shared across vendors; the field names are not, and they live in the provider tabs. Thinking tokens are billed at the output rate and count against the output cap, so a cap sized for the answer can be spent entirely on thinking, leaving no visible text; OpenAI marks that response `status: "incomplete"` with the reason `max_output_tokens`.[^openai] You may be shown a summary of the thinking and billed for all of it.[^anthropic-ext] In Anthropic's words, "Effort is a behavioral signal, not a strict token budget," and it also shapes how many tool calls the model makes and how long the answer runs.[^anthropic-effort]

You can watch the bill on your own screen. Send one prompt to an OpenAI reasoning model at low effort and again at high, and compare `usage.output_tokens_details.reasoning_tokens` on the two responses. Then set `max_output_tokens` to a few hundred on a hard prompt; the status can come back incomplete.[^openai] On Anthropic the same split is `usage.output_tokens_details.thinking_tokens`.[^anthropic-ext]

The decision procedure is an effort sweep. Fix a set of cases that look like your traffic, fix a grader (code that marks each answer pass or fail), and run every case at every level. Supported levels vary by model: `gpt-6.2-sol` rejects `none`, and on `claude-sonnet-5-5` leaving out the thinking settings leaves thinking on, so its no-thinking baseline is a setting of its own.[^openai][^anthropic-effort] The contract is three small types:

```python
from collections.abc import Callable

from pydantic import BaseModel

# Supported levels are model-dependent; trim this list to what your model accepts.
LEVELS = ["none", "low", "medium", "high"]


class Case(BaseModel):
    id: str
    prompt: str
    expected: str


class ModelReply(BaseModel):
    text: str  # empty when the output cap was spent on thinking
    visible_tokens: int
    thinking_tokens: int


class LevelReport(BaseModel):
    level: str
    quality: float  # fraction of runs that passed
    output_tokens: int  # visible + thinking, summed over all runs
    cost: float
```

The sweep holds the cases, the grader and the cap fixed and varies only the level. Each adapter returns empty text when the response was cut off, so a truncated reply counts as a failure and is still billed:

```python
def run_sweep(
    model_fn: Callable[[Case, str, int], ModelReply],
    cases: list[Case],
    grade: Callable[[Case, str], bool],
    cap: int = 5000,  # max output tokens per call
    repeats: int = 3,
    units_per_1k: float = 1.0,
    levels: list[str] = LEVELS,
) -> list[LevelReport]:
    reports = []
    for level in levels:
        passed = tokens = runs = 0
        for case in cases:
            for _ in range(repeats):
                reply = model_fn(case, level, cap)
                runs += 1
                tokens += reply.visible_tokens + reply.thinking_tokens
                passed += bool(reply.text) and grade(case, reply.text)
        reports.append(
            LevelReport(
                level=level,
                quality=passed / runs,
                output_tokens=tokens,
                cost=tokens / 1000 * units_per_1k,
            )
        )
    return reports
```

Then pick the cheapest level within a tolerance of the best, refuse to pick at all if nothing reaches an absolute quality floor, and print the bill:

```python
def cheapest_passing(
    reports: list[LevelReport], floor: float = 0.9, tolerance: float = 0.05
) -> LevelReport | None:
    """The cheapest level within `tolerance` of the best, or None if nothing reaches `floor`."""
    best = max(r.quality for r in reports)
    if best < floor:
        return None
    ok = [r for r in reports if r.quality >= max(floor, best - tolerance)]
    return min(ok, key=lambda r: r.cost)


def bill(reports: list[LevelReport]) -> str:
    return "\n".join(
        f"{r.level:<7} quality={r.quality:.2f} output_tokens={r.output_tokens} cost={r.cost:.2f}"
        for r in reports
    )
```

Repeats matter because a case can pass on one run and fail on the next at the same level; [Evaluation](proving-it-works.md) owns how many you need and how to read the spread. The listing omits latency for brevity. Add median and 95th-percentile latency (p50 and p95) per level before you trust the pick for anything a person waits on.

> **In the companion repo.** `reasoning_budget/` runs this sweep offline against a scripted model whose numbers are invented to show the shape of a result; nothing was measured on any real model. Two cases (the phone case's category and the desk's Prop 65 warning), three repeats each, the default 5,000-token cap, and cost in abstract units per thousand output tokens.

The cases carry their own inputs, and the grader is an exact match:

```python
CASES = [
    # Trivial: the category is in the title.
    Case(
        id="NV-PHONECASE-01",
        prompt="Store category for: 'Clear slim phone case, shock-absorbing corners'.",
        expected="phone-accessories",
    ),
    # Multi-step: the warning has to be worked out from the materials list.
    Case(
        id="NV-ALDSWORTH-DM",
        prompt=(
            "Which compliance notice does this need? Sit-stand desk; materials: "
            "steel frame, MDF top bonded with formaldehyde-based resin."
        ),
        expected="prop-65",
    ),
]


def exact_match(case: Case, text: str) -> bool:
    return text.strip() == case.expected
```

`python -m reasoning_budget` runs the sweep and prints the bill and the pick:

```python
from .scripted import CASES, exact_match, scripted_model
from .sweep import bill, cheapest_passing, run_sweep


def main() -> None:
    reports = run_sweep(scripted_model, CASES, exact_match, cap=5000)
    print(bill(reports))
    pick = cheapest_passing(reports)
    print("ship:", pick.level if pick else "nothing reaches the floor")


if __name__ == "__main__":
    main()
```

One run of that illustration:

1. At `none`, the phone case is categorized correctly and the desk's warning is missed. Quality 0.50, 120 output tokens, cost 0.12.
2. At `low`, the same split, now for 1,920 tokens.
3. At `medium`, both cases pass. Quality 1.00, 6,420 tokens, cost 6.42.
4. At `high`, the desk still passes, but the phone case comes back as "cases", a worse category reached after 2,400 tokens of deliberation, the overthinking Gotcha 2 describes. Quality drops to 0.50 at the highest cost, 15.12.
5. The pick is `medium`. Drop the cap to 2,000 and `high` returns no text on either case, scores 0.00, and still bills 12,000 tokens.

In this run the effort the desk needs is effort the phone case pays for, and at `high` the phone case gets worse for it.

### Where to start

A starting point per kind of step, for your sweep to overwrite:

| The step looks like | Start at | Then |
|---|---|---|
| Classifying, extracting, routing an incoming message | no thinking, or the lowest level | raise it only if the sweep shows misses on the hard cases |
| Writing or summarizing in one pass | low | drop lower if quality holds; chain-of-thought's gains sat mostly in math and symbolic work[^sprague] |
| Multi-step, checkable reasoning: rules, math, code, plans | medium | sweep up to high, and check the easy cases for overthinking |
| Structured output | lower than you would guess | sweep down; Anthropic's guidance for one model warns that `max` effort can overthink it[^anthropic-effort] |

When one step sees both kinds of input, as the taxonomy step does with phone cases and desks, a fixed level can overpay on one or underthink on the other. Adaptive thinking narrows that gap by thinking less on easy inputs, so measure before you split. The next move is to choose the effort per request, from a cheap difficulty signal or from the step's identity. That is still emerging practice; [Routing & Dispatch](../composition/the-router-that-isnt.md) covers the routing machinery and [Controlling Cost](../production/controlling-cost.md) the money.

### Thinking across tool calls

Inside an agent loop the model calls a tool, reads the result, and decides what to do next; [The Agent Loop](../the-unit/the-agent-loop.md) covers the loop itself. Interleaved thinking lets the model reason between those calls within one turn, so it can work out what a tool result means before it picks the next call. Anthropic's adaptive thinking does this without a flag. OpenAI returns reasoning items and Gemini returns thought signatures, opaque records of the model's reasoning state, which you pass back on the next request so the model keeps its chain, unless the provider holds the conversation state for you.[^anthropic-thinking][^openai][^google]

One rule is general: return that reasoning state complete and unmodified. On Anthropic that means thinking blocks, including `redacted_thinking` blocks, which carry reasoning the safety systems encrypted instead of showing you. The API rejects modified blocks with a 400, and a filter that keeps only `type == "thinking"` throws the redacted ones away.[^anthropic-thinking] Two more specifics are Anthropic's. On newer Claude models prior thinking stays in the context and is billed as input on every later turn; [Compaction](../knowledge/compaction-and-the-window.md) covers what to do when the window fills. And a forced `tool_choice` is rejected under manual thinking, and on `claude-sonnet-5-5` on every request.[^anthropic-thinking]

#### Wiring it to a provider

Each tab is one `model_fn` for the sweep. For `none`, the Anthropic tab asks for an answer without up-front thinking. The OpenAI model rejects `none`, so run its sweep with `levels=LEVELS[1:]`.

=== "LangGraph"

    ```python
    from langchain.chat_models import init_chat_model


    def model_fn(case: Case, level: str, cap: int) -> ModelReply:
        llm = init_chat_model(
            "openai:gpt-6.2-sol",
            reasoning_effort=level,  # gpt-6.2-sol rejects "none"
            max_tokens=cap,
        )
        msg = llm.invoke(case.prompt)
        usage = msg.usage_metadata or {}
        thinking = usage.get("output_token_details", {}).get("reasoning", 0)
        return ModelReply(
            text=msg.text,
            visible_tokens=usage.get("output_tokens", 0) - thinking,
            thinking_tokens=thinking,
        )
    ```

=== "OpenAI Responses API"

    ```python
    from openai import OpenAI

    client = OpenAI()


    def model_fn(case: Case, level: str, cap: int) -> ModelReply:
        resp = client.responses.create(
            model="gpt-6.2-sol",
            input=case.prompt,
            reasoning={"effort": level},  # gpt-6.2-sol rejects "none"
            max_output_tokens=cap,
        )
        thinking = resp.usage.output_tokens_details.reasoning_tokens
        # status "incomplete" means the cap ran out, often mid-thinking
        text = resp.output_text if resp.status == "completed" else ""
        return ModelReply(
            text=text,
            visible_tokens=resp.usage.output_tokens - thinking,
            thinking_tokens=thinking,
        )
    ```

=== "Anthropic Messages API"

    ```python
    import anthropic

    client = anthropic.Anthropic()


    def model_fn(case: Case, level: str, cap: int) -> ModelReply:
        if level == "none":  # answer without thinking first
            kwargs = {"thinking": {"type": "between_tools"}}
        else:
            kwargs = {"thinking": {"type": "adaptive"}, "output_config": {"effort": level}}
        reply = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=cap,
            messages=[{"role": "user", "content": case.prompt}],
            **kwargs,
        )
        text = "".join(b.text for b in reply.content if b.type == "text")
        if reply.stop_reason == "max_tokens":
            text = ""  # truncated: grade as a failure
        total = reply.usage.output_tokens
        thinking = reply.usage.output_tokens_details.thinking_tokens
        return ModelReply(text=text, visible_tokens=total - thinking, thinking_tokens=thinking)
    ```

## Gotchas

1. **A cap sized for the answer.** You cap output at 500 tokens because the answer is a category name, turn effort up, and get an empty response, because the thinking spent the cap. Size the cap for thinking plus answer, check the status or stop reason on every response, and treat an incomplete response as a failure.[^openai] The adapters' empty-text rule is this check.

2. **More thinking can make the answer worse.** Which of your tasks will overthink is hard to predict, so the sweep runs every level instead of assuming the top one is safe. Chen and colleagues document o1-style models spending large token counts on problems as small as 2+3.[^chen-over] Gema and colleagues find task families where accuracy falls as reasoning length grows,[^gema] and Liu and colleagues find chain-of-thought hurts on tasks where deliberation also makes people worse.[^liu]

3. **An attacker can spend your thinking for you.** The OverThink attack plants decoy problems in retrieved context; the model reasons through them before answering, and reasoning-token use rose 12x to 46x on the paper's text datasets.[^overthink] OWASP lists this class of harm as unbounded consumption.[^owasp] Cap effort and output tokens on any step that reads untrusted input, and alert on reasoning-token spend per request, which [Observability](../production/seeing-inside.md) covers.

4. **The visible reasoning can leave out why the model answered.** Turpin and colleagues biased models toward an answer with a feature of the prompt, and the explanations did not mention it.[^turpin] Lanham and colleagues found that how much a model's answer depends on its stated reasoning varies widely by task,[^lanham] and Chen and colleagues at Anthropic found reasoning models often did not mention hints they had used.[^chen-faith] Use the thinking to debug. Do not show it to a user as the justification, audit on it alone, or build a guardrail that trusts it; [Guardrails & Safety](guardrails-and-safety.md) and [Human-in-the-Loop](human-in-the-loop.md) cover what to check instead. Whether monitoring reasoning can become a dependable safety signal is contested: Korbak and colleagues call it "a new and fragile opportunity."[^korbak]

5. **Changing the dial can cost you the cache.** Changing the thinking configuration or a top-level effort value between requests can invalidate all or part of the prompt cache, so code that flips effort per request can lose the cache hits it expected. Where a model supports a per-message effort change, that route keeps the cache.[^anthropic-effort][^anthropic-ext]

6. **The dial moves under you.** The API surface changed on all three vendors inside a year, and settings copied from an older config break: on current Claude models a non-default `temperature`, `top_p` or `top_k` returns a 400 on every request.[^anthropic-thinking] Pin the effort level and the cap next to the prompt in versioned config ([Prompt Architecture & Management](prompts-are-source-code.md)), and rerun the sweep on every model upgrade.

## In short

Take "think step by step" out of prompts sent to reasoning models; the training already does that work, and the prompt adds tokens and time for marginal accuracy. Treat effort as a per-step cost setting: start each step as low as its kind of work allows, run the same cases at every level the model accepts, and raise effort only where the sweep shows quality that justifies the bill. Size the output cap for thinking plus answer, cap effort on any step that reads untrusted input, pass reasoning state back untouched across tool calls, and read the visible reasoning as a debugging aid, never as the reason the model answered.

<small class="chapter-meta">**Maturity: Established** (the dial; thinking across tool calls is still changing, and reasoning as oversight is contested) · *Who decides:* the model (how much to think) / your code (effort, cap, vote) · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^kojima]: Kojima, T., et al., "Large Language Models are Zero-Shot Reasoners" (2022). The 17.7% to 78.7% figure is MultiArith with a 2022 model. <https://arxiv.org/abs/2205.11916>
[^wei]: Wei, J., et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (2022). <https://arxiv.org/abs/2201.11903>
[^wang]: Wang, X., et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (2022). <https://arxiv.org/abs/2203.11171>
[^yao]: Yao, S., et al., "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (2023). <https://arxiv.org/abs/2305.10601>
[^meincke]: Meincke, L., Mollick, E., Mollick, L., and Shapiro, D., "Prompting Science Report 2: The Decreasing Value of Chain of Thought in Prompting" (2025). Not peer-reviewed. <https://arxiv.org/abs/2506.07142>
[^sprague]: Sprague, Z., et al., "To CoT or not to CoT? Chain-of-thought helps mainly on math and symbolic reasoning" (2024). <https://arxiv.org/abs/2409.12183>
[^snell]: Snell, C., et al., "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters" (2024). The 14x comparison is FLOPs-matched. <https://arxiv.org/abs/2408.03314>
[^r1]: DeepSeek-AI, "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning" (2025). <https://arxiv.org/abs/2501.12948>
[^s1]: Muennighoff, N., et al., "s1: Simple test-time scaling" (2025). <https://arxiv.org/abs/2501.19393>
[^chen-over]: Chen, X., et al., "Do NOT Think That Much for 2+3=? On the Overthinking of o1-Like LLMs" (2024). <https://arxiv.org/abs/2412.21187>
[^gema]: Gema, A. P., et al., "Inverse Scaling in Test-Time Compute" (2025). <https://arxiv.org/abs/2507.14417>
[^liu]: Liu, R., et al., "Mind Your Step (by Step): Chain-of-Thought can Reduce Performance on Tasks where Thinking Makes Humans Worse" (2024). <https://arxiv.org/abs/2410.21333>
[^overthink]: Kumar, A., et al., "OverThink: Slowdown Attacks on Reasoning LLMs" (2025). The multipliers are the paper's, per dataset. <https://arxiv.org/abs/2502.02542>
[^owasp]: OWASP, "LLM10:2025 Unbounded Consumption," Top 10 for LLM Applications (2025). <https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/>
[^turpin]: Turpin, M., et al., "Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting" (2023). <https://arxiv.org/abs/2305.04388>
[^lanham]: Lanham, T., et al., "Measuring Faithfulness in Chain-of-Thought Reasoning" (2023). <https://arxiv.org/abs/2307.13702>
[^chen-faith]: Chen, Y., et al., "Reasoning Models Don't Always Say What They Think" (2025). <https://arxiv.org/abs/2505.05410>
[^korbak]: Korbak, T., et al., "Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety" (2025). <https://arxiv.org/abs/2507.11473>
[^openai]: OpenAI, "Reasoning models" (accessed 2026-11-28). Billing as output, `output_tokens_details.reasoning_tokens`, the `incomplete` status, reasoning items, model-dependent effort values including models that reject `none`. <https://developers.openai.com/api/docs/guides/reasoning>
[^anthropic-thinking]: Anthropic, "Thinking" (accessed 2026-11-28). Thinking on by default, unmodified thinking blocks including `redacted_thinking`, per-model retention of prior thinking, forced `tool_choice` limits, sampling parameters on current models. <https://platform.claude.com/docs/en/build-with-claude/thinking>
[^anthropic-ext]: Anthropic, "Extended thinking" (accessed 2026-11-28). Manual `budget_tokens` as a legacy mode, adaptive thinking as its replacement, `usage.output_tokens_details.thinking_tokens`, summarized thinking, caching. <https://platform.claude.com/docs/en/build-with-claude/extended-thinking>
[^anthropic-effort]: Anthropic, "Effort" (accessed 2026-11-28). The "behavioral signal" wording, per-model defaults, running Claude Sonnet 5.5 without up-front thinking, the Opus 4.7 note that `max` effort can overthink structured output, cache behaviour on effort changes and per-message effort. <https://platform.claude.com/docs/en/build-with-claude/effort>
[^google]: Google, "Gemini thinking" (accessed 2026-11-28). Thinking levels and thought signatures; what each Gemini generation accepts changes, so recheck. <https://aistudio.google.com/docs/thinking>

## See also

- [2.5 The Agent Loop](../the-unit/the-agent-loop.md), the inner loop that thinking across tool calls runs inside.
- [3.3 Orchestrator-Workers](../composition/fan-out.md), for the voting variant of parallelization that self-consistency became.
- [3.6 Planning & Task Decomposition](../composition/planning.md), where Tree-of-Thoughts-style search lives when you build it.
- [4.2 Evaluation](proving-it-works.md), for the repeat count and grading discipline the sweep depends on.
- [4.4 Guardrails & Safety](guardrails-and-safety.md), on why a guardrail should not trust the model's stated reasoning.
- [5.4 Compaction](../knowledge/compaction-and-the-window.md), for the context that retained thinking fills.
- [8.4 Controlling Cost](../production/controlling-cost.md), for the spend side of the effort dial.

## Further reading

- Anthropic, [Effort](https://platform.claude.com/docs/en/build-with-claude/effort): the clearest vendor account of what an effort level does and does not control.
- OpenAI, [Reasoning models](https://developers.openai.com/api/docs/guides/reasoning): billing, the output cap and incomplete responses, with the usage fields.
- Snell et al., [Scaling LLM Test-Time Compute Optimally](https://arxiv.org/abs/2408.03314): the research case for spending at inference, and why it depends on difficulty.
- Meincke et al., [The Decreasing Value of Chain of Thought in Prompting](https://arxiv.org/abs/2506.07142): the short empirical case that the old prompt trick has stopped paying.
- Korbak et al., [Chain of Thought Monitorability](https://arxiv.org/abs/2507.11473): the best argument for and against treating visible reasoning as oversight.
