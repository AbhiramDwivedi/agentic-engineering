# 8.4 Controlling Cost

*Make the repeated prefix cheap, the waiting work cheap, the easy calls cheap, and the total bounded. An agent's bill is set by how many calls its loop makes and how much context each one re-sends, so the first savings come from changing those, and any lever that trades quality for money is judged on cost per passed case.*

## Why you'd reach for it

Move an agent to a model with half the price per token and the monthly bill can still go up. The bill also counts how many calls the loop makes, how much context each call re-sends, and how many tokens come back, and a cheaper model that needs more turns, or fails and gets retried, can lose on all three.

The re-sending is the part teams underestimate. A model API keeps no memory between requests, so an agent loop sends the whole conversation every turn: system prompt, tool schemas, every earlier tool call and result. Without caching, input cost grows with the square of the turn count. Take a run that opens with 2,000 tokens of instructions and tool definitions and adds about 2,000 tokens a turn. Turn *n* sends 2,000 × *n* tokens, so turn twenty sends 40,000, and the whole run sends 2,000 × (1 + 2 + ... + 20) = 420,000. Output costs five times input on Anthropic's price table,[^anthropic-batch] and hidden reasoning tokens bill as output (4.5 Reasoning & Thinking Budgets), so a step that reasons at length can outspend the context it re-sends.

Anthropic's account of its multi-agent research system puts numbers on the multiplier: agents use about four times the tokens of a chat, multi-agent systems about fifteen times. On the BrowseComp browsing benchmark, token usage alone explained 80 percent of the variance in scores in Anthropic's own evaluation.[^multiagent] That is a correlation on one benchmark and proves no cause, but the budget question follows: a multi-agent design pays only on a task where the better answer is worth fifteen times a chat's spend.

Listing Studio, a pipeline on a commerce platform, turns a supplier's spreadsheet and photos into a storefront listing through dozens of model calls across nine steps. Every call opens with the same long system prompt and product-schema tools, so a merchant onboarding a whole catalog pays full input price for that identical opening on every call, and interactive prices for work nobody is waiting on.

Reach for this chapter when:

- **The same long prefix rides on every call.** A big system prompt, a tool catalog, a reference document.
- **Work can wait.** Overnight catalog onboarding, eval runs, backfills.
- **Most calls are easy and a few are hard,** and a check after the call can tell which.
- **A loop can run away.** An agent that chooses its own next step can choose a hundred of them.

The counter-trigger is a short call made a few hundred times a day, where the bill is noise. Measure first: per-step token and cost fields in your traces (8.1 Observability) show which line of the bill to cut. The cheapest cut is often token hygiene: trimming verbose tool output and schemas, such as a supplier lookup that returns the whole row when the step needs three fields.

## What it actually is

Controlling cost is four moves, all made in your code. Keep the repeated prefix of every request (its opening tokens: system prompt, tool schemas, fixed context) byte-identical so the provider can serve it from cache. Route work that can wait through a discounted batch tier. Send each call to the cheapest model that passes a check and escalate on failure, a chain called a cascade. Cap what one run, and one user, can spend. Caching and batch change the price of the same work and lose nothing. Cascades and budgets change the work itself, so they can cost quality, and they are judged on cost per passed case: an eval run's total spend divided by the cases that passed its checks.

![One agent request: a wide static block (rules, tool schemas, catalog context) and a narrow dynamic one (timestamp, listing). Four code-owned levers act on it. A cache bills the static block cheaply and a batch lane halves the price of waiting work: same quality, lower price. A cascade escalates to a larger model on a failed check, and a budget stops the loop before a step would cross the limit: both judged on cost per passed case.](controlling-cost-levers.svg)

Nearly all of this is your code deciding, with engineering you already know: a cache key, a job queue, an if-statement, a counter. A learned router or semantic cache adds a trained model or an embedding lookup, and your code still makes the call. The model decides only when you hand it escalation as a tool, as in Anthropic's advisor tool: the model doing the work (the executor) can ask a stronger model (the advisor) for guidance mid-task, and chooses when.[^cost]

How proven is it? The mechanisms are established; the savings figures are a weaker claim. Anthropic, OpenAI and Google all document prompt caching, Anthropic and OpenAI both document a half-price batch tier, and the static-first rule is in the vendors' own guidance.[^anthropic-caching][^openai-caching][^google-caching] Learned and confidence-gated cascades are emerging, tested on fixed benchmarks rather than multi-step agent pipelines. Advisor pairings as a money saver, and semantic answer caching, are contested, the first on its vendor's own numbers. Nearly every savings number here comes from a vendor's own benchmark, so read those numbers as directional.

Picking the model for each step belongs to 8.2 Which Model?; gating a cheap model and escalating when it fails is covered here. Trimming the window belongs to [Context Engineering](../foundations/context-engineering.md) and 5.4 Compaction.

## How to do it

Start with the move that costs nothing. A provider's prompt cache matches on the exact prefix of a request: opening tokens identical to a recent request's are billed at a fraction of the input price. So static content goes first and dynamic content last. The builder below does that, and hashes everything before the divider so a test can prove the prefix never drifts.

```python
import hashlib

STATIC_RULES = (
    "You write product listings for Listing Studio.\n"
    "Follow the brand style guide. Never invent specifications.\n"
)


def build_prompt(catalog_context: str, listing: str, now: str) -> str:
    """Static parts first, per-call parts last, so the prefix stays identical."""
    static = STATIC_RULES + catalog_context
    dynamic = f"Current time: {now}\nListing to improve:\n{listing}"
    return static + "\n---\n" + dynamic


def prefix_hash(prompt: str) -> str:
    """Hash of everything before the dynamic section: the cacheable prefix."""
    prefix = prompt.split("\n---\n", 1)[0]
    return hashlib.sha256(prefix.encode()).hexdigest()[:12]
```

Its contract: `catalog_context` is identical across calls, and anything that varies goes after the divider.

One run of the companion tests (`listing-studio/tests/test_cost.py`):

1. Build the prompt for the Aldsworth sit-stand desk, then for a phone case, with the same catalog context.
2. The prompts differ, and `prefix_hash` returns the same value for both.
3. Move the timestamp to the top and build both again.
4. The hashes differ. A real cache would miss on every call, because the first line changes every minute.
5. Nothing raised an error in either case. In production the only signs of the miss are the bill and the usage fields.

Send the same long request to Anthropic's API twice, and the second response's `usage` block reports the prefix under `cache_read_input_tokens` instead of `cache_creation_input_tokens`; on OpenAI the read shows as `usage.input_tokens_details.cached_tokens`.[^anthropic-caching][^openai-caching] Log both and alert when the hit rate, the share of input served from cache, drops.

The concept is portable and the wire details are not. Anthropic's caching is explicit: a `cache_control` marker on a block caches everything up to it, in the order tools, then system prompt, then messages. The first request writes the prefix to the cache at a premium; later ones read it at a tenth of the input price on most models, a twentieth on Opus 5.5 and Sonnet 5.5.[^anthropic-caching] On OpenAI's GPT-5.6 and later, caching starts at 1,024 tokens, with `prompt_cache_key` separating cache accounting per customer.[^openai-caching] Google caches implicitly on Gemini 2.5 and newer.[^google-caching] Appendix D has the write premiums and lifetimes.

### Work that can wait

Anything nobody is waiting on, such as overnight onboarding but never a live helpdesk reply, can go through a batch API, which Anthropic and OpenAI both discount by 50 percent for up to a 24-hour wait.[^anthropic-batch][^openai-batch] On Anthropic the discount stacks with caching, but batched requests run concurrently and in any order, so cache hits are best-effort; Anthropic recommends the one-hour cache lifetime for batches that share context.[^anthropic-batch]

### Cheap first, strong when the check fails

A cascade sends the call to a cheap model, checks the answer, and pays for the strong model only when the check fails. In the companion's illustrative units, a cheap call costs 1 and a strong call 5, so a passing case costs 1 and a failing case 6. If a share *p* of cheap answers pass, the average case costs 1 + 5(1 − *p*), against 5 for always calling the strong model. That is lower whenever *p* is above 0.2: the cascade wins once more than one cheap answer in five passes the check.

<details markdown>
<summary>The cascade gate (<code>cost/cascade.py</code>)</summary>

```python
CHEAP_COST, STRONG_COST = 1, 5


def cascade(
    task: str,
    cheap: Callable[[str], str],
    strong: Callable[[str], str],
    passes: Callable[[str], bool],
) -> CascadeResult:
    """Return the cheap answer if it passes the check, else pay for the strong one."""
    draft = cheap(task)
    if passes(draft):
        return CascadeResult(draft, "cheap", escalated=False, cost=CHEAP_COST)
    return CascadeResult(
        strong(task), "strong", escalated=True, cost=CHEAP_COST + STRONG_COST
    )
```

`CascadeResult` is a dataclass of the answer, the tier, whether it escalated, and the cost.

</details>

The design rests on `passes`, which has to be cheap and trustworthy: a schema validation, a lookup against the catalog taxonomy, a rule your code already enforces. The cheapest rung sits before any model: a regex that rejects a malformed SKU, or a dedupe against listings already written, settles cases for nothing.

Anthropic's cost guide gives the same shape with effort, an API setting for how thoroughly the model works and so how many tokens it spends, in place of model size: run every task at low effort and re-run only the failures at high. On the SWE-bench Pro coding benchmark, that cut Claude Opus 5.5's cost by about 40 percent against running everything at high, at the same pass rate. The failure signal there was the benchmark's tests; your pipeline needs a cheap one of its own. Each first-pass failure also takes two runs of wall-clock time, as in every cascade.[^cost]

Learned routers replace the fixed check with a model that predicts which tier a query needs. FrugalGPT reports matching GPT-4 at up to 98 percent lower cost, and Hybrid LLM up to 40 percent fewer large-model calls with no drop in quality; RouteLLM trains its routers on preference data.[^frugalgpt][^hybrid][^routellm] All three measured single queries on fixed benchmarks, never a multi-step agent pipeline, and crafted text can push a router's queries to the expensive tier.[^rerouting]

Advisor pairings are the same economics with the model deciding when to escalate, and the vendor's own numbers are the reason to wait. On a coding benchmark, a pairing whose executor consulted the advisor often scored 1.7 points above the executor alone, "at the edge of run-to-run noise", for about 2.1 times the cost. On a chart-reading task, a pairing scored 7 points below its executor alone. The tool's definition also adds about 1,000 prompt tokens to every request, consulted or not.[^cost]

### A budget the loop cannot argue with

`max_tokens` caps one response, and the model has no idea what the run has spent. The guard below bounds the run: before each step it projects the spend, taking the next step to cost as much as the largest so far, and stops with `"budget_exceeded"` if that would cross the limit or the step count runs out.

<details markdown>
<summary>The budget guard (<code>cost/budget.py</code>)</summary>

```python
def run_with_budget(
    step: Callable[[int], tuple[str, int, bool]],
    max_tokens: int,
    max_steps: int = 20,
) -> RunResult:
    """Call step(i) -> (output, tokens_spent, finished) while the next step fits."""
    used, biggest, latest = 0, 0, ""
    for i in range(1, max_steps + 1):
        if used + biggest > max_tokens:  # next step projected at the largest yet
            return RunResult("budget_exceeded", i - 1, used, latest)
        output, spent, finished = step(i)
        used += spent
        biggest = max(biggest, spent)
        latest = output  # keep the work done so far
        if finished:
            return RunResult("done", i, used, output)
    return RunResult("budget_exceeded", max_steps, used, latest)
```

`RunResult` is a dataclass with `status`, `steps`, `tokens_used` and `answer`.

</details>

With a 1,000-token budget and 400 tokens a step, steps one and two bring the total to 800. Step three would reach 1,200, so the guard stops before it, after two steps, with step two's output as the answer. A step bigger than any before it can still cross the limit, so leave headroom. With a large budget and `max_steps=5`, the loop stops at step five.

A tripped budget has to return a structured result your caller can tell apart from a crash. It has to be final, so the retry layer does not spend the budget again (7.1 Retry & Graceful Degradation), and it keeps the work done so far for a person or a resumed run (7.3 Checkpointing): the companion's `RunResult` puts the last completed step's output in `answer`.

> **In Listing Studio.** Bulk catalog onboarding is the batch case: a merchant's catalog goes through overnight on the batch tier with the one-hour cache. The cascade wraps the categorize step, which assigns each product a catalog category, with a taxonomy lookup as the failure signal. The step cap belongs to the Repricer, the sibling agent that watches competitor prices and plans its own steps.

## Gotchas

1. **Cache misses are silent.** A timestamp near the top, JSON serialized with unstable key order, or a tool list rebuilt in a different order each call will miss on every request. On Anthropic, changing a tool definition invalidates the whole cache, and a prompt under the minimum cacheable length is processed uncached with no error.[^anthropic-caching] The cache expires while a run waits on a human, and failover to another provider starts cold. Compaction and context editing (clearing stale tool results from the history) rewrite history, so everything after the edit point misses; 5.4 Compaction weighs that trade.

2. **A tight `max_tokens` can cost more.** A response cut off by the cap is a failed attempt you paid for. On an internal Anthropic benchmark, Claude Fable 5.2 capped at 16,384 tokens had 85 percent of attempts cut off and cost $27.96 per solved task, against $24.42 at 64,000; Claude Opus 5.5, which neither cap cut off, cost the same at both in single runs.[^cost] Judge a cap on cost per passed case, never cost per call.

3. **One counter is not a per-user budget.** A counter inside one process bounds one run on one replica. A tenant who opens fifty sessions, or an attacker running up your per-use bill (OWASP's Denial of Wallet), walks straight past it.[^owasp] Per-user and per-tenant budgets live in a shared store keyed by identity (8.5 Locks, PII & Identity), backed by the provider's workspace spend cap and a tested kill switch.

4. **Semantic caching is the risky tier.** An exact-match cache of a deterministic tool result is safe when its key carries the tenant and every input that changes the answer. Plan caching, which reuses plan templates from earlier runs, reports about half the cost and a quarter less latency, and is still emerging.[^plancache] A semantic cache that serves a stored answer for a "similar" query is a different bet: fixed similarity thresholds give no correctness guarantee,[^vcache] and the CacheAttack study hijacked responses through deliberate key collisions at an 86 percent hit rate.[^cacheattack] Never share one across tenants or use one for an answer that depends on current state, such as a price.

5. **A lever that saves on paper can cost more in practice.** Anthropic's own measurements found context editing cost more than it saved on a short run and changed nothing on a long one.[^cost] Run each lever against your eval set (4.2 Evaluation) and keep it only if cost per passed case falls.

## In short

Do the free work first. Put static content first and watch the cache fields in your usage logs, batch anything that can wait, set `max_tokens` generously, and cap every run's tokens and steps in code, with a shared per-user budget above that. Then, with an eval, try a cascade on a step where a cheap check can tell good answers from bad, and keep it only if cost per passed case drops. Leave semantic answer caching and advisor pairings off until your own numbers argue for them.

<small class="chapter-meta">**Maturity: Established** (for the mechanisms: caching, batch and code-enforced budgets are vendor-documented; savings figures are vendor-reported; learned cascades Emerging, semantic caching and advisor pairings Contested) · *Who decides:* your code (the model only when escalation is a tool) · *Grounding:* research + companion repo · *Last reviewed:* 2026-11</small>

## Sources

[^multiagent]: Anthropic, "How we built our multi-agent research system" (2025-06-13). The token multipliers (about 4x a chat for agents, about 15x for multi-agent systems) and the BrowseComp finding that token usage alone explains 80 percent of performance variance, all measured on Anthropic's internal evaluations. <https://www.anthropic.com/engineering/multi-agent-research-system>
[^cost]: Anthropic, "Optimizing for cost and intelligence" (Claude Platform docs, read 2026-11-28). The free-wins versus trade-offs split, the `max_tokens` benchmark, the low-effort re-run recipe on SWE-bench Pro, the advisor pairing results, and the context-editing measurement. All figures are Anthropic-internal and, in the page's words, "directional, not guarantees." <https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence>
[^anthropic-caching]: Anthropic, "Prompt caching" (Claude Platform docs, read 2026-11-28). Prefix order, multipliers (with per-model exceptions to the 0.1x read rate), invalidation rules, the silent minimum, and the usage fields. <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>
[^openai-caching]: OpenAI, "Prompt caching" (API docs, read 2026-11-28). Minimum length, write rates and lifetimes for GPT-5.6 and later, `prompt_cache_key`, and the static-first advice. <https://developers.openai.com/api/docs/guides/prompt-caching>
[^google-caching]: Google, "Context caching" (Gemini API docs, read 2026-11-28). Implicit caching on by default for Gemini 2.5 and newer; explicit caching on supported models. The page as read gave no discount rate. <https://aistudio.google.com/docs/caching>
[^anthropic-batch]: Anthropic, "Batch processing" (Claude Platform docs, read 2026-11-28). The 50 percent discount, batch limits, the 24-hour expiry, best-effort cache hits within batches, and a price table listing output at five times input for each model. <https://platform.claude.com/docs/en/build-with-claude/batch-processing>
[^openai-batch]: OpenAI, "Batch API" (API docs, read 2026-11-28). The 50 percent discount, the 24-hour completion window, and the request and file-size limits. <https://developers.openai.com/api/docs/guides/batch>
[^owasp]: OWASP, "LLM10:2025 Unbounded Consumption," Top 10 for LLM Applications 2025. Covers denial of wallet: attackers exploiting the cost-per-use model with a high volume of operations. <https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/>
[^frugalgpt]: Chen, L., Zaharia, M., Zou, J., "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance" (2023). Author-reported, on fixed benchmarks. <https://arxiv.org/abs/2305.05176>
[^hybrid]: Ding, D., et al., "Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing" (2024). Author-reported, on fixed benchmarks. <https://arxiv.org/abs/2404.14618>
[^routellm]: Ong, I., et al., "RouteLLM: Learning to Route LLMs with Preference Data" (2024). <https://arxiv.org/abs/2406.18665>
[^rerouting]: Shafran, A., Schuster, R., Ristenpart, T., Shmatikov, V., "Rerouting LLM Routers" (2025). <https://arxiv.org/abs/2501.01818>
[^plancache]: Zhang, Q., Wornow, M., Wan, G., Olukotun, K., "Agentic Plan Caching: Test-Time Memory for Fast and Cost-Efficient LLM Agents" (2025). Figures from the abstract, author-reported. <https://arxiv.org/abs/2506.14852>
[^vcache]: Schroeder, L. G., et al., "vCache: Verified Semantic Prompt Caching" (2025). <https://arxiv.org/abs/2502.03771>
[^cacheattack]: Zhang, Z., et al., "From Similarity to Vulnerability: Key Collision Attack on LLM Semantic Caching" (2026). The 86 percent figure is the hit rate for response hijacking reported in the abstract. <https://arxiv.org/abs/2601.23088>

## See also

- [1.5 Context Engineering](../foundations/context-engineering.md): what goes in the window, and so what every call re-sends.
- [2.1 Tool Use](../the-unit/tool-use.md): tool schemas ride on every request.
- [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md): routing by task path, the other meaning of "routing."
- 8.2 Which Model?: choosing the tier each step runs on.
- 8.1 Observability: the per-step cost fields to measure first.
- 7.1 Retry & Graceful Degradation: why a tripped budget is final.
- 2.5 The Agent Loop and 2.6 The Harness: the loop's own stop conditions.
- 4.5 Reasoning & Thinking Budgets: capping hidden reasoning tokens.
- 8.3 To Train or to Prompt: a fine-tuned small model as a cascade's cheap rung.
- 8.7 Deployment & Runtimes: self-hosting, where the bill becomes hardware.
- 9.2 Multi-Agent: where the token multipliers bite hardest.
- Appendix D: dated price tables, kept out of this chapter because they rot.

## Further reading

- Anthropic, ["Optimizing for cost and intelligence"](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence): which levers are free and which trade quality, with measured results.
- Anthropic, ["Prompt caching"](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) and OpenAI, ["Prompt caching"](https://developers.openai.com/api/docs/guides/prompt-caching): the two vendors' mechanics, including what invalidates a cache.
- Chen, Zaharia, Zou, ["FrugalGPT"](https://arxiv.org/abs/2305.05176) (2023): the paper that framed model cascades for LLM cost.
- Schroeder et al., ["vCache"](https://arxiv.org/abs/2502.03771) (2025), on the limits of fixed similarity thresholds.
