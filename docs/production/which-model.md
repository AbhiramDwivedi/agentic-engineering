# 8.2 Which Model?

*Model per step, chosen by your own cases. Give each step of a pipeline the cheapest model that passes that step's cases, keep the choice in configuration, and treat every swap and every retirement as an eval run.*

*Also called: model selection, model tiering, model portability, model-agnostic design.*

## Why you'd reach for it

On September 30, 2026, Anthropic notified developers that `claude-sonnet-4-5-20250929` would be retired on November 30, and that after retirement a request to it fails with a 404.[^dep] If one model ID sits under every call your product makes, that notice sets a deadline for the whole product, and the model someone picked off a leaderboard last year becomes a migration nobody scheduled.

The easy first move is to choose a model once, for the product, the way you'd choose a database. The choice then has to serve every step at once: the call that picks a category from a fixed list and the call that writes three paragraphs of persuasive copy get the same model, priced and paced for the harder of the two. When the vendor ships a successor or retires the old one, all of those calls move together, and nothing tells you which of them got worse.

They do get worse, sometimes. When researchers compared the March and June 2023 versions of GPT-4, accuracy on one task, identifying prime numbers, fell from 84 percent to 51 percent, under the same model name.[^drift] A model is a dependency that changes behavior when it changes version, and its vendor sets the version calendar.

Take Listing Studio, a product-listing pipeline that turns a supplier's spreadsheet into a storefront page. One click runs nine steps; this chapter's table shows four of them. Step 3, **categorize**, places the Aldsworth sit-stand desk in the catalog taxonomy: one label from a list your code already holds, checked against a schema. Step 4, **write copy**, drafts the description and bullets, where the answer is open and quality is a judgment. Run both on the flagship, the vendor's largest and priciest model, and you pay flagship rates on every product for a categorization the step's cases might show a cheaper model gets right. Run both on the cheap model and the copy suffers. A single product-wide choice forces a compromise on one of the two steps.

The fix is small. Name a model for each step in configuration, keep a set of cases for each step (a case is a prompt plus the answer you expect), and let a model take a step only when it passes that step's cases. Running candidates through those cases is the eval run, and a swap is the config change at the end of it.

Reach for this when:

- **Steps differ in difficulty.** Schema-bound extraction and classification sit next to open drafting or multi-step reasoning in the same pipeline.
- **Volume makes price matter.** A step that runs on every product, every request, is where a cheaper model pays back.
- **You depend on a hosted model.** Vendors retire older models on their own schedule; Anthropic says it does so regularly.[^dep]
- **A successor ships.** "Should we move to the new model?" is a question your cases can answer and a launch post cannot.

When you don't: a single-call prototype with no cases yet. Pick one model, start on the cheapest one that handles the task, and come back when you have a second step or a first user.

## What it actually is

Model selection, done as engineering, is a per-step configuration value that only an eval may change. Each step names its model in one place your code reads; each step owns a set of cases with known answers; a candidate replaces the current model for a step only when it does better on that step's cases; and a retirement notice starts the same comparison against the replacement before the date arrives.

![Four steps of the pipeline, categorize, write copy, price and polish, each look up their own row in one configuration table, the only place a model ID lives: categorize and price read openai:gpt-6.2-sol, write copy and polish read anthropic:claude-sonnet-5-5. Below, an eval for the categorize step, started when a successor ships or a retirement notice arrives. Three cases with known answers, a sit-stand desk, a bunk bed and a phone case, run through the current model A and a candidate C. If they tie at three of three, the table keeps A, because a tie is not a win. If A scores two of three and C scores three of three, C wins strictly and is written into the categorize row. Every shape is a rectangle, because the table, the cases, the comparison and the swap are all your code. The scores are the chapter's toy cases and say nothing about any real model.](which-model-per-step.svg)

Your code makes every decision here. The configuration table, the cases, the comparison and the swap rule are ordinary software, a lookup plus a regression test. Nothing in it is agentic, so you version the table and gate a change on a test the way you already do for any other config.

**Maturity: Established.** Anthropic's own guidance for choosing a model is this method applied to a single choice: build tests specific to your use case, run your actual prompts and data, compare models on accuracy and edge cases, then weigh performance against cost, and it calls the evaluation set "the most important step in the process."[^choose] Running that method once per step is this chapter's extension of it. Both large vendors publish retirement policies with minimum notice periods, so a pinned ID has a known expiry.[^dep][^oai-dep] The newer ideas at the edge of this chapter are less proven. Learned routers that pick a tier per request have been measured by their authors on fixed benchmarks; the studies cited here do not test agent pipelines,[^frugalgpt][^hybridllm][^routellm] and pairing a cheap executor with an expensive advisor has vendor measurements that cut both ways (see Gotchas).

Three neighbours get confused with this. [Routing & Dispatch](../composition/the-router-that-isnt.md) decides *which task* a request is; this chapter decides *which model* runs a task you already identified. Model cascades and cost routers, where a cheap model answers first and a learned rule escalates the hard cases, are a cost technique, covered in depth in 8.4 Controlling Cost. And a [fallback chain](../reliability/which-failures-sink-the-ship.md) picks a second model when the first one errors, which is an availability decision made at runtime; per-step selection is a quality decision made ahead of time. Before you swap models at all, check whether a different effort or thinking budget on the current one closes the gap; Anthropic suggests that lever is often better than switching models, and [Reasoning & Thinking Budgets](../craft/reasoning-and-thinking-budgets.md) covers it.[^choose]

## How to do it

Start with the configuration. One table maps each step to a model, and one function is the only way any step gets its model:

```python
STEP_MODELS: dict[str, str] = {
    "categorize": "openai:gpt-6.2-sol",
    "write_copy": "anthropic:claude-sonnet-5-5",
    "price": "openai:gpt-6.2-sol",
    "polish": "anthropic:claude-sonnet-5-5",
}


def model_for(step: str) -> str:
    """One lookup per step. A step with no entry fails loudly, never falls back."""
    if step not in STEP_MODELS:
        raise KeyError(f"no model configured for step {step!r}")
    return STEP_MODELS[step]
```

The contract is that model IDs live here and nowhere else. A step that calls a provider with a hard-coded string is a step a migration will miss. The `provider:model` format is the one LangGraph's `init_chat_model` accepts, and the raw-SDK tabs split it on the colon. A missing step raises instead of falling back to a default, because a silent default is how a new step ends up on whatever model was cheapest the day someone wrote the fallback.

Then the comparison. Each case is a prompt and its expected answer; a client is any callable from prompt to text, so a real client wraps a provider call and a test passes a fake. A `score` helper in the same file returns the share of cases where the client's answer matches the expected one exactly:

```python
def compare(clients: dict[str, Client], cases: list[Case]) -> dict[str, float]:
    """Run the same cases through every candidate model and score each."""
    return {model: score(client, cases) for model, client in clients.items()}


def choose(scores: dict[str, float], current: str) -> str:
    """Swap only when a candidate beats the current model on the eval."""
    best = max(scores, key=scores.get)
    return best if scores[best] > scores[current] else current
```

The swap rule is strict on purpose: a tie keeps the current model, so churn needs evidence. `choose` also ignores cost; it answers only whether a candidate is better on the cases. Exact match is the cheapest scorer that works for a step like categorize, where the answer is one label; a drafting step needs a rubric or a judge, and [Evaluation](../craft/proving-it-works.md) covers building those and reading their error bars.

One run, with two fake candidates and three toy cases for the categorize step (a sit-stand desk, a bunk bed and a phone case, each with its correct category):

1. `compare` sends all three prompts to candidate A, the current model, and to candidate B.
2. A answers all three correctly and scores 1.0. B labels the bunk bed and the phone case `Misc` and scores 1/3.
3. `choose` sees A on top and returns A. Nothing changes.
4. A new candidate C arrives and scores 1.0, tying A. `choose` keeps A, because a tie is not a win.

A separate run shows the other branch. Suppose A had scored 2/3 on the same cases. C's 1.0 is then a strict win, and `choose` returns C, the value you write into `STEP_MODELS`. These scores are toys from the companion tests and say nothing about any real model.

The cost half of the rule is yours to apply. Record each candidate's spend on the run beside its score, and check the winner's cost per passed case before you write it into the table; price per token hides the retries. A model at half the price that fails a third of a step's cases can cost more once you count the retries and the human review, and a pricier model that never needs a retry can be the cheap one. Because the rule is strict, a cheaper model that only ties the current one does not take the step through `choose`. If that saving is worth having, you make the call by hand with the cost figures in front of you. A retirement forces the same call: the current model is going away, so its named replacement only has to match the current score.

Going from one step to the pipeline adds no new mechanism. Each step gets its own cases and its own `compare` run, and each writes its own row. Before any score counts, apply the capability gates that rule candidates out: does the step need image input, strict schema adherence (see [Structured Output](../the-unit/structured-output.md)), or a long effective context, and does the candidate meet the step's latency budget and your rate limits? Then compare the survivors on cases. Expect the prompt to move with the model. Expect to retune a prompt when it moves to another model family, so a fair comparison gives each candidate a prompt you have actually tried on it.

#### Wiring it to a provider

The config lookup is the same in every tab; only the call changes. In the raw-SDK tabs, `client` is that provider's SDK client, built once at startup; a table that mixes providers uses the `provider` half of the ID to pick which client to call.

=== "LangGraph"

    ```python
    llm = init_chat_model(model_for("categorize"))  # "openai:gpt-6.2-sol"
    answer = llm.invoke("Categorize: Aldsworth dual-motor sit-stand desk")
    ```

=== "OpenAI Responses API"

    ```python
    provider, model = model_for("categorize").split(":", 1)  # "openai", "gpt-6.2-sol"
    response = client.responses.create(
        model=model,
        input="Categorize: Aldsworth dual-motor sit-stand desk",
    )
    ```

=== "Anthropic Messages API"

    ```python
    provider, model = model_for("write_copy").split(":", 1)  # "anthropic", "claude-sonnet-5-5"
    message = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": "Write copy: Aldsworth dual-motor sit-stand desk"}],
    )
    ```

## Gotchas

1. **A leaderboard is someone else's cases.** A public benchmark measures a task its authors chose, and your categorize step is not on it. A flagship picked from a ranking can lose to a cheaper model on the twenty cases that describe your catalog.

2. **A swap moves more than the weights.** Request parameters change across model generations too. Anthropic's API version `2026-10-21` removed `temperature`, `top_p` and `top_k`, and a request that still sends them gets a 400 error.[^dep] A migration that only edits the model string can fail on the first call, or pass every call and drift on quality. Run the replacement against your real prompts and tool schemas, the same `compare` you used to choose, before the config changes.

3. **Retirement runs on the vendor's calendar.** Anthropic gives at least 60 days' notice before retiring a publicly released model and moves models through four states, Active, Legacy, Deprecated and Retired.[^dep] OpenAI promises at least six months for generally available models, three for specialised variants, and much shorter notice, such as two weeks, for anything named "preview".[^oai-dep] So pin dated model IDs, keep previews off business-critical steps, and put each pinned model's retirement date on a calendar the day you adopt it. Anthropic's console exports usage broken down by API key and model, which is how you find the step nobody remembered was still on the old ID.[^dep] Run your cases against the named replacement early in the notice window, while a failure is still a ticket and not an outage.

4. **An unpinned name can change under you.** On April 24 and 25, 2025, OpenAI rolled out a GPT-4o update to ChatGPT that made it noticeably more sycophantic, and began rolling it back on April 28.[^syco] That was a consumer product, but the lesson carries to the API: a moving alias hands the version calendar to the vendor, so pin the ID and gate each change on your cases.

5. **Pairing a cheap model with an expensive checker is a bet.** Anthropic measured its own advisor pattern, a cheaper executor that escalates hard decisions to a stronger advisor. On an internal coding benchmark the pairing gained 1.7 points, "at the edge of run-to-run noise", for about 2.1 times the cost of the executor alone. On a chart benchmark another pairing scored 7 points below the executor alone, "beyond run-to-run noise".[^cost] Learned routers between tiers can also be steered by crafted inputs.[^rerouting][^rerouteguard] Measure any pairing on your cases before you trust it; cascades and cost routing get their full treatment in 8.4 Controlling Cost.

6. **A provider gateway has a price.** One config value behind one call site, where the model ID enters, is enough for most teams, and an OpenAI-compatible endpoint, which several providers and self-hosted servers expose, often covers the rest. A gateway that speaks every provider's API is one more choice, with three costs. It offers the features all providers share, so a provider-specific parameter waits for the gateway to support it. Your prompt cache may not travel: Anthropic's cache matches only a 100 percent identical prompt prefix and is isolated per organization.[^cache] Its documentation does not say whether a cached prefix survives a change of model, so don't count on one. And a gateway concentrates your provider keys in one dependency. In March 2026, two LiteLLM releases reached PyPI with malicious code in them.[^litellm] Pin the gateway's version and give it keys scoped to what it routes. Framework lock-in more broadly is [Do You Even Need a Framework?](../foundations/do-you-need-a-framework.md).

7. **Local is one answer to residency, and not the only one.** Open weights trade a capability gap and an operations burden for control over where data goes and what each call costs at high volume, within whatever the model's license permits. Hosted vendors now sell geographic controls too, at a premium listed on their pricing pages.[^pricing] Any break-even between self-hosting and an API depends on how busy you keep the hardware, so treat a published break-even figure as someone else's utilization. If you do self-host, vLLM serves an OpenAI-compatible HTTP API, so the same per-step config and the same `compare` run point at it unchanged.[^vllm]

## In short

Put a model name on each step in one config table, give each step its own cases, and let a candidate take a step only when it wins on those cases at a cost per passed case you are happy to pay. Pin dated IDs, calendar every retirement the day you adopt a model, and run the replacement through the same comparison early in the notice window. The model names in your config will be wrong within a year or two; the cases, the table and the swap rule are what you keep.

<small class="chapter-meta">**Maturity: Established** (vendor-documented method and retirement policies; tier routers and advisor pairings are Emerging) · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^choose]: Anthropic, "Choosing the right model." Read 2026-11-28. <https://platform.claude.com/docs/en/about-claude/models/choosing-a-model>
[^dep]: Anthropic, "Model deprecations." Notice period, lifecycle states, the 404 on retired models, the usage audit, the Sonnet 4.5 retirement and the sampling-parameter removal; read 2026-11-28. Dates on this page change; re-read it before relying on any of them. <https://platform.claude.com/docs/en/about-claude/model-deprecations>
[^oai-dep]: OpenAI, "Deprecations." Read 2026-11-28. <https://developers.openai.com/api/docs/deprecations>
[^drift]: Chen, Zaharia, Zou, "How is ChatGPT's behavior changing over time?" (2023). One study of two model versions; cited for the existence of drift, not its typical size. <https://arxiv.org/abs/2307.09009>
[^syco]: OpenAI, "Expanding on what we missed with sycophancy" (2025-05-02). The update rolled out April 24 to 25 and the rollback began April 28. <https://openai.com/index/expanding-on-sycophancy/>
[^cost]: Anthropic, "Optimizing for cost and intelligence." Anthropic-internal results that the page itself calls directional; the coding pairing is Opus 5.5 at high effort with a Fable 5.1 advisor, the chart pairing Opus 5.5 at low effort with the same advisor on Anthropic's Chartography benchmark. Read in part, 2026-11-28. <https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence>
[^frugalgpt]: Chen, Zaharia, Zou, "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance" (2023). The LLM cascade idea, measured on fixed benchmarks. <https://arxiv.org/abs/2305.05176>
[^hybridllm]: Ding et al., "Hybrid LLM: Cost-Efficient and Quality-Aware Query Routing" (ICLR 2024). Difficulty-aware routing between model tiers. <https://arxiv.org/abs/2404.14618>
[^routellm]: Ong et al., "RouteLLM: Learning to Route LLMs with Preference Data" (2024). Learned routing between a strong and a weak model; cited without its benchmark-specific percentages. <https://arxiv.org/abs/2406.18665>
[^rerouting]: Shafran, Schuster, Ristenpart, Shmatikov, "Rerouting LLM Routers" (2025). <https://arxiv.org/abs/2501.01818>
[^rerouteguard]: Zhang et al., "RerouteGuard: Understanding and Mitigating Adversarial Risks for LLM Routing" (2026). <https://arxiv.org/abs/2601.21380>
[^cache]: Anthropic, "Prompt caching." Read in part, 2026-11-28. Isolation is per workspace on some platforms; no statement found either way on reuse across models. <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>
[^litellm]: LiteLLM, "Security Update: Suspected Supply Chain Incident" (2026-03-24). The project's own advisory; the cause was still under investigation when it was written. <https://docs.litellm.ai/blog/security-update-march-2026>
[^pricing]: Anthropic, "Pricing," sections on data residency and cloud platform pricing. Read 2026-11-28; check the page for current multipliers. <https://platform.claude.com/docs/en/about-claude/pricing>
[^vllm]: vLLM, "Online Serving" (OpenAI-compatible server). <https://docs.vllm.ai/en/latest/serving/online_serving/>

## See also

- [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md), which decides the task; this chapter picks the model for it.
- [4.2 Evaluation](../craft/proving-it-works.md), for building the cases and scorers every swap here depends on.
- [4.5 Reasoning & Thinking Budgets](../craft/reasoning-and-thinking-budgets.md), the lever to try before switching models.
- [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md), for the runtime fallback when a model errors.
- [8.1 Observability](seeing-inside.md), for seeing per-step cost and drift in traces.
- [8.3 To Train or to Prompt](train-or-prompt.md), for when no hosted model passes your cases.
- [8.4 Controlling Cost](controlling-cost.md), for cascades, caching and batching.
- [1.6 Do You Even Need a Framework?](../foundations/do-you-need-a-framework.md), on lock-in beyond the model.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for one model chosen once for every step.

## Further reading

- Anthropic, ["Choosing the right model"](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model): the efficiency-first and capability-first starting strategies.
- Anthropic, ["Model deprecations"](https://platform.claude.com/docs/en/about-claude/model-deprecations): the live retirement table and migration practice.
- OpenAI, ["Deprecations"](https://developers.openai.com/api/docs/deprecations): notice periods and the retirement history.
- Chen, Zaharia, Zou, ["How is ChatGPT's behavior changing over time?"](https://arxiv.org/abs/2307.09009): the drift study.
- Chen, Zaharia, Zou, ["FrugalGPT"](https://arxiv.org/abs/2305.05176): the cascade paper, for the reader heading to 8.4.
