# 2.7 Decision Models

*A model call that writes no text: you hand it a question with fixed options, it hands back a probability for each option, and your code decides what that probability is allowed to do.*

*Also called: decision model, Decisions API (OpenAI, Perplexity, Google), System One model (TypeSafe), decision-scoring model (Microsoft), Decider, System 1 model, evaluation model (Vercel's earlier name).*

## Why you'd reach for it

Ask a decision model whether a product listing makes an unverified safety claim and you get back `{"true": 0.98, "false": 0.02}`. It is tempting to read that as 98% sure. The Vercel AI SDK documentation puts it flatly: for a boolean, 0.98 "means a strong yes", and "it is not confidence in either outcome."[^vercel-sdk] The number arrives in one fast pass with no prose to parse. Whether it means 98% is something only your labeled data can tell you.

The older way to get a yes or no from a model was generation. You asked a chat model, got back *"Yes, the listing calls the desk 'certified safe,' which..."*, and pulled a verdict out of the sentence, or you used [Structured Output](structured-output.md) to force a `bool` field. Either way you paid for a full generation to get one label. In one comparison of rubric judging, LLM judges cost 16 to 357 times as much as decision models and took 5 to 350 times as long, while the decision models trailed them significantly in at most 6 of the paper's 27 head-to-head comparisons.[^rao]

Take Listing Studio, a catalog tool that turns a supplier's spreadsheet into a published product page, and the compliance check it runs before anything goes live. For the Aldsworth sit-stand desk (`NV-ALDSWORTH-DM`) that check has teeth: a Prop 65 warning for the formaldehyde in its MDF top, a BIFMA safety claim, and a 250 lb `weight_capacity_lbs` rating that must never be overstated, because a wrong load rating is a liability and a returns wave. Ask one compound question, "is this listing compliant?", and three separate judgments come back tangled into one probability, where two clean factors can outweigh one bad one. Threshold it at 0.5, which is what taking the likelier answer amounts to, and a listing scored 0.55 compliant ships. Swap providers behind an adapter, the SDK layer that puts several vendors behind one interface, and the distribution you were thresholding may quietly become a bare label with no probability behind it; code that fills the gap with 1.0 treats a guess as certainty. Either way the overstated weight rating ends up on a live page.

The fix is mostly your code. Ask one question per factor, send the questions together over the same listing in one request, and own everything that happens after the distributions come back: the threshold, the path for a refusal, the escalation for an unsure answer, and the rule that combines three answers into one verdict. Then check, on labeled examples of your own, whether the probabilities mean what your threshold assumes they mean.

Reach for a decision model when:

- **The answers are fixed in advance.** Yes or no, one of a known list of categories, a rung on a rubric.
- **The volume is high and the input is shared.** Many judgments per item and many items per hour, where a judge's cost and latency add up.
- **Code acts on the answer.** A gate blocks, a branch fires, a person gets paged, and you want to choose how sure the model must be before that happens.

The counter-trigger: if the judgment needs its reasoning written down (why the copy breaks the rule, what it should say instead), or the answer is not one of a set you can list ahead of time, generate it with structured output. If the task is a trajectory, many steps where each action changes the next input, the evidence so far favors generation (see Gotchas).

## What it actually is

In one pass, a decision model returns a probability distribution over options your code fixed in advance. The model produces the distribution. The threshold that turns it into an action, and every rule after it, live in your code.

![Your code sends the Aldsworth desk listing and three true-or-false questions, one per compliance factor, to a decision model (the hexagon) in one request. It returns 0.02 true and 0.98 false for a missing Prop 65 warning, 0.98 true and 0.02 false for an unverified safety claim, and 0.02 true and 0.98 false for an overstated weight capacity. Against the dashed 0.90 threshold set in your code, that reads false, true, false, and any confident true blocks, so the listing is blocked. Had the safety answer been 0.55, no bar would cross and the listing would escalate. A second lane shows a bare label with no distribution, which your code escalates instead of trusting.](decision-models-distribution.svg)

Three question shapes cover the core of the category. A **predicate** asks whether a statement is true and returns P(true). A **choice** returns a distribution over options you list. It can only share probability among the options you supplied, so when none may fit, list a "none of these" option or ask a predicate first. A **score** returns a distribution over the ordered levels of a rubric, and you can act on the most likely level, as the companion code does, or on the distribution's weighted average. Names and limits are per vendor. OpenAI calls the first shape a predicate;[^openai] TypeSafe, Perplexity and Google name it `noul`, their API's word for a predicate;[^typesafe][^pplx-api][^google] the Vercel AI SDK calls it `boolean`.[^vercel-sdk] Several questions can share one input in a single request, 1 to 400 on OpenAI and up to 1,000 on Google,[^openai][^google] and each question still gets its own distribution. Whether that input is processed and billed once varies by provider.

A decision model chooses among options you wrote, and your code chooses what happens next, so it is a capability you call, a sibling of structured output. Whether its answer is a structural decision depends on what the option controls. A choice that picks the next route or tool hands the model that decision, as in [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md); a predicate that blocks an action leaves the decision with code, as part of [2.6 The Harness](the-harness.md). In shape it is a classifier with probability outputs, an old idea behind a new API. What is new is that you get the classifier without training one: you write the question in plain language and read a distribution on the first call. The other names listed at the top mean the same thing.

**Maturity: Emerging.** The product category is a few months old, and most speed and calibration figures are the vendors' own. The practices around it are older. Putting thresholds and an abstain rule in code is standard for any classifier, and Microsoft's model card says the integrating application must define options, thresholds, escalation paths and human oversight.[^mscard] Post-hoc calibration, fitting a small correction on held-out labeled data so that stated probabilities match observed frequencies, is established method.[^guo] Out-of-the-box calibration is contested: Microsoft claims calibrated probabilities while its card text publishes no calibration metrics,[^mscard] and an independent benchmark found error rates of 1.71% to 12.77% among answers given at 0.90 or higher, across 13 decision models on 1,273 MedQA medical multiple-choice questions.[^freyer] Two uses are contested as well, inside closed loops and as an outright replacement for LLM judges; Gotchas 2 and 3 give the evidence.

## How to do it

The contract is two small types. A `Question` carries its shape, its text and the options the model must distribute over. An `Answer` carries the distribution, or one of the two ways a provider can fail to give you one.

```python
@dataclass(frozen=True)
class Question:
    kind: str                      # "predicate" | "choice" | "score"
    text: str
    options: tuple[str, ...]       # predicate: ("true", "false"); score: ordered levels


def predicate(text: str) -> Question:
    return Question("predicate", text, ("true", "false"))


def choice(text: str, options: tuple[str, ...]) -> Question:
    return Question("choice", text, options)


def score(text: str, levels: int) -> Question:
    return Question("score", text, tuple(str(i) for i in range(1, levels + 1)))


@dataclass(frozen=True)
class Answer:
    probs: dict[str, float] | None   # None: the vendor gave a label, not a distribution
    label: str | None = None         # the adapter-fallback label, when probs is None
    refused: bool = False            # the provider declined to decide
```

The function below is the policy, and none of it is the model. Each answer resolves to one of three outcomes: the chosen option when the top probability clears the threshold, `escalate` when it does not or when no usable distribution came back, and `abstain` when the provider declined to decide. `THRESHOLD` is 0.90 in the companion module, the tested code kept in this site's repository under [`listing-studio/`](https://github.com/AbhiramDwivedi/agentic-engineering/tree/main/listing-studio). That value suits its test fixture and nothing else; you set yours from the calibration check in Evaluating it.

```python
def decide(answer: Answer, question: Question, threshold: float = THRESHOLD) -> str:
    """Return the chosen option, "abstain" (refused), or "escalate" (not sure enough)."""
    if answer.refused:
        return "abstain"
    if not answer.probs or not all(0.0 <= p <= 1.0 for p in answer.probs.values()):
        # No distribution, an empty one, or a malformed one carries no confidence.
        return "escalate"
    best = max(question.options, key=lambda o: answer.probs.get(o, 0.0))
    return best if answer.probs.get(best, 0.0) >= threshold else "escalate"
```

A real gate usually weighs several factors. TypeSafe's documentation advises that a question weighing several independent factors be decomposed into separate questions and recombined in code.[^typesafe] The model then judges each factor on its own, and the combination rule becomes a line of Python you can read, test and change.

```python
def compliance_gate(client, listing: str, questions: list[Question]) -> str:
    """One predicate per independent factor, one request, combined here in code."""
    answers = client.decide_many(listing, questions)
    if not questions or len(answers) != len(questions):
        return "escalate"           # a missing judgment is never a pass
    outcomes = [decide(a, q) for a, q in zip(answers, questions)]
    if "true" in outcomes:          # any confident violation blocks the listing
        return "block"
    if all(o == "false" for o in outcomes):
        return "pass"
    return "escalate"               # an unsure or refused answer goes to a human
```

One run of the gate on the Aldsworth desk:

1. Your code builds three predicates, one per compliance factor: a missing Prop 65 warning, an unverified safety claim, and an overstated `weight_capacity_lbs`. Each is phrased so that `true` means a problem, as in "Is a required Prop 65 warning missing from the listing?"
2. `decide_many` sends all three with the listing in one request; in the companion code a scripted fake, `FakeDecisionClient`, plays the vendor.
3. Two predicates come back at `{"true": 0.02, "false": 0.98}`. The safety-claim predicate comes back at `{"true": 0.98, "false": 0.02}`.
4. `decide` holds each against 0.90 and returns `false`, `true`, `false`.
5. `compliance_gate` sees a confident violation and returns `block`. A reply missing an answer returns `escalate` before any answer is read; otherwise, with no confident violation, an unsure or refused answer escalates for a reviewer ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md)).

You can see a real distribution this afternoon. Google AI Studio offers a no-cost API tier for prototyping with `gemini-decision-1`.[^google] Perplexity lists Apache-2.0 open weights for `pplx-decider-flash-v1.3`, built on a 4B base model.[^pplx-hf] The vendors' request shapes differ and are weeks old, so the companion code wires none of them.

> **In Listing Studio.** The pipeline's categorize step (step 3) already places each product in the catalog taxonomy through a schema-constrained `category_path` field ([2.2 Structured Output](structured-output.md)); a choice question over the same candidate paths would return a distribution instead, so a desk split almost evenly between two paths surfaces as a near tie to escalate rather than a confident-looking string. A score could grade the brand-voice polish step (step 8) against a written voice rubric. The compliance gate above would sit inside the publish step's validation (step 9), before the listing is written to the catalog.

## Evaluating it

A threshold is only as good as your knowledge of what the numbers mean, and the vendors do not agree on that. Perplexity defines choice confidence as `(p_top - 1/n) / (1 - 1/n)`, which measures how concentrated the distribution is and says nothing about whether the top option is right.[^pplx-api] Calibration is the property you want: among answers the model gives at 0.9, about 90% should turn out correct. Only then does 0.98 earn the reading "98% sure", and only your labeled data can show it. Generative models asked for P(true) in the right format can be well calibrated,[^kadavath] which gives you a reason to measure a decision model and promises nothing about it. When calibration is off, temperature scaling is the standard post-hoc fix: it divides the model's raw scores by one constant, fitted on held-out labeled data, which softens or sharpens every probability at once.[^guo]

The check is cheap. Label a sample of your own items, record the P(true) the model gave each, and bin them by that probability. In each bin, compare the average P(true) with the share of items that were actually true; expected calibration error (ECE) is that gap averaged across bins, each weighted by how many items it holds. Then look for a threshold on confidence, the larger of P(true) and P(false). The lowest confidence above which the model was right every time on your sample is only a starting floor, because zero errors on a few dozen rows bounds nothing. Pick it on one labeled set, confirm it on a second set, weigh a wrong pass against an escalation, and recheck as labels accumulate. On UNFAIR-ToS, a benchmark of unfair clauses in online terms of service, tuning a binary threshold took Jev, TypeSafe's System One decision model, from a micro-F1 (F1, the balance of precision and recall, pooled across all labels) of 0.50 to 0.75, as its authors report.[^jev]

<details markdown>
<summary>The calibration check (reliability bins, ECE, and the lowest all-correct threshold)</summary>

```python
def calibrate(rows: list[tuple[float, bool]], bins: int = 5) -> dict:
    """rows: (P(true) the model gave, whether it was actually true).

    Returns expected calibration error (ECE) and the lowest confidence threshold
    above which every prediction on this fixture was correct.
    """
    n = len(rows)
    ece = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        cell = [(p, y) for p, y in rows if lo <= p < hi or (b == bins - 1 and p == 1.0)]
        if cell:
            conf = sum(p for p, _ in cell) / len(cell)
            acc = sum(y for _, y in cell) / len(cell)
            ece += len(cell) / n * abs(conf - acc)
    best = None
    for t in sorted({max(p, 1 - p) for p, _ in rows}):
        sure = [(p, y) for p, y in rows if max(p, 1 - p) >= t]
        if all((p >= 0.5) == y for p, y in sure):
            best = t
            break
    return {"ece": ece, "threshold": best}
```

</details>

> **In the companion repo.** `calibrate` runs on a ten-row labeled fixture and returns an ECE of 0.158 and a threshold of 0.90, matching the policy's `THRESHOLD`. Ten rows prove the code runs; they say nothing about any vendor's model.

Run the check again whenever you change provider, model version or question wording, because each of those changes what the numbers mean.

## Gotchas

1. **A label where you expected a distribution.** Adapters hide this one. The Vercel AI SDK page marks Anthropic as a structured language-model adapter: its booleans are "prompted estimates of P(true)", its choice and score answers omit distributions, and "the SDK does not promise calibration across providers."[^vercel-sdk] The same page lists TypeSafe, OpenAI, Perplexity and Google as native. The Vercel AI Gateway's TypeSafe-compatible API returns `confidence: 0` and `probabilities: {}` when a language model produced a fallback answer, documented as unavailable sentinels;[^vercel-gw] code that reads `probabilities.get("true", 0)` turns "unavailable" into a confident false. Handle absence explicitly: `decide` escalates an empty or malformed distribution. A per-question refusal (OpenAI documents one)[^openai] differs from a request that times out: catch the timeout at the client boundary and turn it into answers the policy escalates, a wrapper the companion code leaves to you.

2. **Cascading to a bigger model mostly buys cost savings.** The Vercel AI Gateway can rerun a decision on another model when confidence or a probability band matches a rule; both stages bill, and a language-model fallback returns no confidence at all.[^vercel-gw] The cascade from a decision model to an LLM judge gained at most 2.7 points over the best single judge even with oracle thresholds, and over 85% of flash-tier LLM verdicts repeated the decision model's most confident errors.[^rao] Cascade for cost, if you cascade at all ([8.4 Controlling Cost](../production/controlling-cost.md)); do not expect the second model to rescue the cases the first got confidently wrong.

3. **Single decisions, not trajectories.** System1-Arena tests 30 models on single questions and in closed-loop environments, where each action changes what the model sees next. The largest System-1 models (the paper's term for decision models) matched fast closed LLMs on non-agentic tasks, with better calibration at about a quarter of the latency; in the closed-loop environments large open LLMs succeeded most often, at up to 32.9%, and small System-1 models rarely succeeded.[^arena] Jev chose the optimal Blackjack action 90% of the time and did poorly on FrozenLake, a grid-world navigation game.[^jev] The evidence on trajectories is thin and poor for small decision models, so keep the agent loop, where the model reads results and chooses the next step, with generation ([2.5 The Agent Loop](the-agent-loop.md)) unless your own trajectory evaluation says otherwise. Inside single decisions, expect lower peak accuracy than generation (67.71% to 89.08% on MedQA for decision models against 78.32% to 96.86% for generative configurations), and run-to-run agreement of 92.30% to 100% across three runs, so an answer is not guaranteed to repeat.[^freyer]

4. **Removing text generation does not remove prompt injection.** Wu and Lim rebuilt 510 cases from InjecAgent, a benchmark of prompt-injection attacks on tool-using agents, and ran them against Jev. Malicious content in the input shifted action probabilities, though it rarely made the model pick the attacker's target outright; adaptive attacks that used the returned scores as feedback doubled the mean highest attacker-target probability, and validated attack success rose from 1.8% to 3.5%.[^wu] Where untrusted text such as a supplier's product description drives a routing or compliance gate, the probability is attack surface ([4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md), [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md)).

5. **The whole input rides in every call.** A decision call has no memory between requests, so the listing and any state the judgment needs go in the tokens each time. Put the current evidence and the policy the judgment depends on in the input as well, and send only the fields the question needs. Microsoft's model accepts 32,768 tokens and Google's 256K.[^mscard][^google] Budgeting what goes in is [1.5 Context Engineering](../foundations/context-engineering.md).

## In short

Use a decision model for high-volume, fixed-option judgments over one shared input, where a generated answer would cost more and take longer; generate with structured output when the judgment needs reasoning or open-ended answers. Ask one question per factor, batch them, and combine the answers in code. Keep the threshold, the abstain path and the escalation path in your own code, and set the threshold from a calibration check on your own labeled data, rerun whenever the provider or model changes. Treat a missing distribution as missing, and never as certainty. A 0.98 means only what your labeled data says it means.

<small class="chapter-meta">**Maturity: Emerging** (a product category a few months old, with vendor-reported speed and calibration; code-side thresholds are standard, post-hoc calibration established) · *Who decides:* a capability, not a pattern · *Grounding:* research + companion repo · *Last reviewed:* 2026-11</small>

## Sources

[^vercel-sdk]: Vercel, AI SDK Core documentation on decisions. <https://ai-sdk.dev/docs/ai-sdk-core/decisions>
[^rao]: Rao and Callison-Burch, "Decision Models vs. LLMs as Rubric Judges: Cheaper, Faster, and Wrong in the Same Places." <https://arxiv.org/abs/2609.29769> Preprint.
[^openai]: OpenAI, Decisions create reference (`POST /v1/decisions`). <https://developers.openai.com/api/reference/resources/decisions/methods/create>
[^typesafe]: TypeSafe documentation. <https://docs.typesafe.ai>
[^pplx-api]: Perplexity, API reference for decisions. <https://docs.perplexity.ai/api-reference/decisions-post>
[^google]: Google, "Gemini Decisions API" (2026-11-11). <https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/>
[^guo]: Guo, C., et al., "On Calibration of Modern Neural Networks," ICML 2017. <https://arxiv.org/abs/1706.04599>
[^mscard]: Microsoft, "Microsoft-Decision-1" model card, Azure AI Foundry catalog. <https://ai.azure.com/catalog/models/Microsoft-Decision-1> Vendor-reported; the card text publishes no calibration metrics.
[^freyer]: Freyer et al., "Benchmarking decision models against generative large language models on medical multiple-choice questions" (2026-10-28). <https://arxiv.org/abs/2610.38448> Preprint; MedQA only.
[^pplx-hf]: Perplexity, `pplx-decider-flash-v1.3` model card, Hugging Face. <https://huggingface.co/perplexity-ai/pplx-decider-flash-v1.3> The repository requires an access token.
[^kadavath]: Kadavath, S., et al., "Language Models (Mostly) Know What They Know" (2022). <https://arxiv.org/abs/2207.05221>
[^jev]: Deußer et al., "Evaluating and Benchmarking the System One Model Jev" (2026-09-29). <https://arxiv.org/abs/2609.37647> Preprint.
[^vercel-gw]: Vercel, "Decision Fallbacks," AI Gateway documentation (last updated 2026-10-08). <https://vercel.com/docs/ai-gateway/models-and-providers/decision-fallbacks> Vercel is renaming parts of this product (previously "evaluation fallbacks"); check the live page.
[^arena]: Chen et al., "System1-Arena: Which Decisions Can Be Left to System 1?" (2026-10-15). <https://arxiv.org/abs/2610.21244> Preprint.
[^wu]: Wu and Lim, "Decision Hijacking: Prompt Injection Attacks on Jev's Typed Probabilistic Decisions" (2026-09-23). <https://arxiv.org/abs/2609.28613> Preprint.

## See also

- [2.2 Structured Output](structured-output.md), the generative sibling: reach for it when the answer needs reasoning or does not fit a fixed set of options.
- [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md), when a choice's distribution decides which path a request takes and the confidence floor becomes a routing decision.
- [2.6 The Harness](the-harness.md), when a predicate gates an action and becomes part of the permission policy around the model.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md), for what `escalate` should actually do once it fires.
- [4.2 Evaluation](../craft/proving-it-works.md), because a decision model can serve as a judge and the calibration check is an eval like any other.
- [3.7 The Outer Loop](../composition/the-outer-loop.md), the code-side verify-and-retry loop that can consume a decision model's verdict as its check.
- [8.4 Controlling Cost](../production/controlling-cost.md), for cascade mechanics and the cases where a cascade pays for itself.
- [8.2 Which Model?](../production/which-model.md), for choosing between a decision model, a small generative model and a frontier judge.
- [8.3 To Train or to Prompt](../production/train-or-prompt.md), for when a classifier you train yourself beats one you call.

## Further reading

- OpenAI, [Decisions API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create): the predicate, choice and score shapes and their limits, in one vendor's wire format.
- Vercel, [AI SDK Decisions](https://ai-sdk.dev/docs/ai-sdk-core/decisions): the clearest public statement of which providers return real distributions and which return prompted estimates.
- Rao and Callison-Burch, [Decision Models vs. LLMs as Rubric Judges](https://arxiv.org/abs/2609.29769): the cost and latency comparison, and the evidence that cascades share the first model's confident errors.
- Chen et al., [System1-Arena](https://arxiv.org/abs/2610.21244): where single-pass decision models hold up, and how small ones fare in closed-loop environments.
- Guo et al., [On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599): the paper behind temperature scaling and the reliability-bin method the calibration check uses.
