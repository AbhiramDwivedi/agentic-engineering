# 4.2 Evaluation

*Proving it works: run the system over a small set of cases taken from real failures, grade each output with code where code can see the problem and with a checked model judge where it cannot, and read the pass rate together with its error bar.*

*Also called: evals, LLM-as-judge, golden sets.*

## Why you'd reach for it

A prompt change lifts a listing generator from 65 percent to 85 percent on its test set, and a team would reasonably ship that as a 20-point win. Those numbers come from a fake: a stand-in system in this reference's companion repo that gets each case right with a fixed chance written into a table. By that table the new prompt is better by less than 4 points. One test case has the same odds in both versions, and it went from 2 passes in 5 to 5 in 5.

A unit test can trust one green run because the code under test gives the same answer every time. A step where a model decides can give a different answer to the same input on the next run, so one green run is an anecdote. You need many inputs, several runs of each, a grader that turns each output into pass or fail, and a rate at the end. A rate looks like evidence whether or not it is. An eval score is evidence only to the extent that its cases came from real failures, its graders were checked against people, and its rate is read with its noise.

Take Listing Studio, a pipeline on the Stockwell commerce platform that turns a supplier's raw product feed into a published product listing. One product it lists, the Aldsworth sit-stand desk, is rated for 250 lb, and a listing that claims more is a liability and a returns wave. A test set someone imagined will not contain the feed row where the supplier wrote `"250 (static 300)"`; that case exists because a merchandiser caught it before publish. A model judge (a second model asked to grade the output) that likes long, confident copy will pass a long listing claiming 300 lb, and the companion repo has one that does. A 20-point jump on eight cases ships a prompt on luck. I found no public postmortem that blames a production failure on a missing eval, so the case here rests on mechanism and published research.

Reach for it wherever the model makes a decision your code then trusts ([Who Decides?](../foundations/who-decides.md) sends you here for exactly that):

- a prompt, model, or tool change you want to ship on evidence;
- an output code can only partly check, such as a product description or a clarifying question;
- a classifier whose confidence threshold you are about to set;
- an agent whose path varies between runs, as [Orchestrator-Workers](../composition/fan-out.md) decompositions do.

Where your code decides, ordinary tests are enough. The dispatch table in [Routing & Dispatch](../composition/the-router-that-isnt.md) needs a unit test, and a pass rate would add nothing.

## What it actually is

An eval is a test suite for behavior that differs between runs. It has a set of cases (the **golden set**), each an input with an unambiguous expected result, sometimes that the system should add nothing; a **grader** per criterion that turns one output into pass or fail; and a **harness** that runs every case several times, turns the verdicts into a pass rate with its uncertainty, and passes that rate to a **gate**, code that calls a change better than the previous version only when their error bars do not overlap. Each part has one condition to meet before the score counts as evidence: the cases came from real failures, the graders were checked against people (for a model judge, by **kappa**, a score of how far its agreement with human labels beats chance), and the rate is read with its noise.

![An eval pipeline in three columns, each headed by the condition that makes its score evidence. First, cases came from real failures. A feed row reading 250 (static 300), caught by a merchandiser before publish, becomes one of eight golden cases, each naming the failure it came from, one of them a do-nothing case, while cases someone imagined would not contain that row. Second, graders were checked against people. A code grader checks the claimed weight is 250 lb, and a rounded model judge grades only what code cannot see; against hand labels on a kappa scale with a bar at 0.6, the lenient judge scores 0.50 and is not trusted, the careful judge 0.75 and is trusted. Third, the rate is read with its noise. The harness runs each case several times, and v1 passes 0.65 with a 95 percent interval of 0.44 to 0.86 while v2 passes 0.85 with 0.71 to 0.99, so the bars overlap. Below, the same eight cases read two ways. The dashboard shows 0.65 to 0.85, a 20-point win, and the gate, your code, calls it not distinguishable because v2's low end sits below v1's high end.](proving-it-works-evidence.svg)

Your code decides here. The harness owns the cases, the arithmetic, and the call on whether a change is better. A model judge, where there is one, returns a verdict per case and per criterion and has no say in what runs next. In [Evaluator-Optimizer](../composition/evaluator-optimizer.md), by contrast, a model grades a draft inside the product and its verdict steers the loop. The two meet in Listing Studio's clarify step, which drafts questions about specs the feed left out and grades them before sending: that grader is a product feature, and an eval is how you learn whether its verdicts are any good. The judge biases below apply to both.

The method is settled. Anthropic's guidance on success criteria,[^develop] its write-up on agent evals,[^demystify] and Husain's practitioner essay[^husain] describe the same loop of cases, graders, and a rate, and where they differ it is over the order of work. Judge reliability and agent evals are the moving parts: model judges carry measured biases, the practice of checking them is thin, and grading a multi-step agent is still being worked out. You can see the settled half on your own screen in Inspect, the public eval framework from the UK AI Security Institute and Meridian Labs, which splits an eval into a dataset that "provides labelled samples," a solver that "produces an answer for each sample," and a scorer that "evaluates the output."[^inspect] That is the shape of the code below.

A public leaderboard asks which model is best at someone else's fixed task; an eval asks whether your system does your task. The release check that blocks a prompt change belongs to [Prompt Architecture](prompts-are-source-code.md), which consumes this chapter's set.

## How to do it

### Start from failures you have read

Before writing a case, read outputs. Run the step over real inputs and name the ways it went wrong. Each named failure becomes a case and usually a grader. Generic criteria such as "helpfulness" score everything and predict nothing; a case built from a named failure tells you whether that failure is back.[^husain] Anthropic's agent-eval guidance says "20-50 simple tasks drawn from real failures is a great start,"[^demystify] and its multi-agent research team began with "about 20 queries."[^multiagent] Its success-criteria page leans toward volume with automated grading.[^develop] The two fit in sequence: start small and unambiguous, and grow the set once you trust its graders.

In the cases below, MAP is minimum advertised price (the floor a supplier lets retailers advertise), Prop 65 is California's chemical-exposure warning label, and a bunk bed's entrapment warning covers gaps where a child can get stuck.

```python
@dataclass(frozen=True)
class EvalCase:
    id: str
    failure_mode: str          # the failure this case came from
    feed: dict                 # the raw supplier feed row
    required: dict             # attributes the listing must carry, and their values
    forbidden: tuple = ()      # attributes the listing must NOT invent


DESK = {
    "supplier_sku": "NV-ALDSWORTH-DM",
    "height_range_in": "25-50",
    "weight_capacity_lbs": 250,
    "color": "walnut",
    "price_cents": 39900,
    "map_enforced": True,
}

GOLDEN = [
    EvalCase("desk-baseline", "none (control)", DESK,
             {"height_range_in": "25-50", "weight_capacity_lbs": 250}),
    EvalCase("desk-weight-overstated", "overstated weight capacity",
             {**DESK, "weight_capacity_lbs": "250 (static 300)"},
             {"weight_capacity_lbs": 250}),
    EvalCase("desk-below-map", "price below MAP",
             {**DESK, "note": "launch discount 15%"},
             {"price_cents": 39900, "map_enforced": True}),
    EvalCase("desk-prop65-missing", "missing compliance warning",
             DESK, {"prop65_warning": True}),
    EvalCase("desk-color-typo", "unnormalised attribute",
             {**DESK, "color": "Wlnut"}, {"color": "walnut"}),
    EvalCase("bunk-guardrail", "missing entrapment warning",
             {"supplier_sku": "NV-BUNKBED-01", "guardrail_height_in": 5},
             {"entrapment_warning": True}),
    EvalCase("bunk-weight-in-title", "attribute buried in free text",
             {"supplier_sku": "NV-BUNKBED-01", "title": "Bunk bed, 200 lb per bunk"},
             {"weight_capacity_lbs": 200}),
    EvalCase("phonecase-do-nothing", "invented compliance on a plain product",
             {"supplier_sku": "NV-PHONECASE-01", "color": "black"},
             {}, forbidden=("prop65_warning", "map_enforced", "assembly_required")),
]
```

Each case records the failure it came from. `desk-weight-overstated` is the `"250 (static 300)"` feed. `phonecase-do-nothing` is the case where the right answer is to add nothing: a phone case carries no compliance regime and no MAP flag, so a listing that gives it a Prop 65 warning has invented something. A set without a do-nothing case rewards a system that stamps every warning on everything. Eight cases is a teaching set; it is too small to decide anything, as the trace shows.

### Grade with code first

Anthropic's guidance is to choose "the fastest, most reliable, most scalable method." Its page lists code-based grading first, then human grading, marked "Avoid if possible," then model grading once it has been tested for reliability.[^develop] People stay in the loop as the calibration, in [Check the judge against people](#check-the-judge-against-people).

```python
def grade_attributes(case: EvalCase, listing: dict) -> Grade:
    """Pass only if every required attribute is present and right, and
    nothing forbidden was invented. A correct do-nothing passes."""
    problems = [
        f"{key}: want {want!r}, got {listing.get(key)!r}"
        for key, want in case.required.items()
        if listing.get(key) != want
    ]
    problems += [f"invented {key}" for key in case.forbidden if key in listing]
    return Grade(not problems, tuple(problems))
```

The grader passes only if every required attribute is present and correct and nothing forbidden appears, so an empty listing passes the phone case. Schema validity is the cheapest code grader of all, and [Structured Output](../the-unit/structured-output.md) gets you most of the way to it. Code graders are brittle in a predictable direction: an exact match on `"walnut"` fails `"Walnut"`, so decide whether the grader or the system normalises. They can also be gamed. "Make your graders resistant to bypasses or hacks,"[^demystify] because a grader that only checks a field exists is passed by any value; [The Outer Loop](../composition/the-outer-loop.md) covers the agent that learns to game its verifier.

A classifier step is the cleanest case for a code grader, because each labelled input has one right answer. Report **precision** (of the items it put in a category, the fraction that belonged there) and **recall** (of the items that belonged, the fraction it caught) per category, since an average hides the category it gets wrong. The same labelled set picks the confidence threshold. The classifier in Routing & Dispatch hands any message it is less than `0.6` confident about to a person; that **confidence floor** is a code default awaiting evaluation. Keep the lowest floor at which the messages still answered hit your target precision, since a lower floor sends fewer to a person.

```python
def choose_floor(slice_: list[tuple[float, bool]], target_precision: float):
    """Lowest confidence floor whose answered items hit the target precision.

    slice_ is (confidence, was_correct) from a labelled sample. Returns None
    if no floor reaches the target: then the classifier should not run alone.
    """
    for floor in sorted({conf for conf, _ in slice_}):
        kept = [ok for conf, ok in slice_ if conf >= floor]
        if sum(kept) / len(kept) >= target_precision:
            return floor
    return None
```

### Use a model judge where code cannot see

Code cannot reliably tell whether a description claims a specification the feed lacks. A model judge can, with checking.

```python
JUDGE_PROMPT = (
    "You are grading one product listing against ONE criterion.\n"
    "Criterion: {criterion}\n\nListing:\n{listing}\n\n"
    "Answer with exactly one word: yes or no."
)


def parse_verdict(reply: str) -> bool:
    """Anything that is not a clear 'yes' counts as a fail: fail closed."""
    return reply.strip().lower().startswith("yes")


def judge_listing(
    judge: Callable[[str], str], criteria: list[str], listing_text: str
) -> dict[str, bool]:
    """One isolated call per criterion, one binary verdict each. The judge
    returns verdicts; it never decides what happens next."""
    return {
        c: parse_verdict(judge(JUDGE_PROMPT.format(criterion=c, listing=listing_text)))
        for c in criteria
    }
```

One criterion per call, a yes-or-no verdict, and anything unclear counts as a fail. Anthropic's agent-eval guidance recommends "an isolated LLM-as-judge" per dimension;[^demystify] its multi-agent team found a single call scoring 0.0 to 1.0 most consistent for its case,[^multiagent] so the right setup is something you measure on your own data.

Judges carry documented biases. They are swayed by where an answer sits in the prompt (position bias), by length (verbosity bias), and by their own writing (self-enhancement bias).[^zheng][^panickssery][^gu] Wang and colleagues changed which model won a comparison just by swapping the order of the answers.[^wang] The mitigations: when the judge compares two answers side by side (a pairwise comparison), run it in both orders and keep only verdicts that survive the swap, prefer binary criteria or scales with every point described (anchored), and judge with a different model from the one that wrote the output.[^develop] Judge agreement with humans can match human-to-human agreement on some tasks,[^zheng] which is why a judge is worth the trouble, and "some tasks" is why you check yours.

### Check the judge against people

Label a slice by hand, run the judge on the same slice, and compare. Raw agreement flatters: a judge that says yes to everything agrees with your labellers as often as they say yes. **Cohen's kappa** corrects for that by measuring agreement beyond what chance alone would give, 1 for perfect and 0 for chance.[^yan]

```python
def agreement(judge: list[bool], human: list[bool]) -> float:
    return sum(j == h for j, h in zip(judge, human)) / len(human)


def cohens_kappa(judge: list[bool], human: list[bool]) -> float:
    """Agreement beyond what chance alone would give (1 = perfect, 0 = chance)."""
    n = len(human)
    observed = agreement(judge, human)
    p_j, p_h = sum(judge) / n, sum(human) / n
    chance = p_j * p_h + (1 - p_j) * (1 - p_h)
    return 1.0 if chance == 1 else (observed - chance) / (1 - chance)


def trust_judge(judge: list[bool], human: list[bool], min_kappa: float = 0.6) -> bool:
    """Only a judge that clears the bar on a human-labelled slice may grade."""
    return cohens_kappa(judge, human) >= min_kappa
```

The `min_kappa=0.6` bar is a default for this example, not a standard, and it has nothing to do with the 0.6 confidence floor above. Re-run the check whenever the judge's model or prompt changes. Expect the rubric itself to move: Shankar and colleagues found that people refine what they mean by "good" while grading, so the labels and the criteria drift together.[^shankar]

### Read the rate with its noise

```python
@dataclass(frozen=True)
class Rate:
    mean: float
    low: float
    high: float


def run_eval(system: Callable[[EvalCase], dict], cases: list[EvalCase],
             trials: int = 5) -> Rate:
    """Pass rate with a 95% interval from the standard error across cases.

    Each case's score is its pass fraction over `trials` runs. The cases are
    the sample, so the error bar is the CLT standard error of the per-case
    scores (Miller, arXiv 2411.00640), not a binomial over all trials as if
    they were independent questions.
    """
    scores = [
        sum(grade_attributes(c, system(c)).passed for _ in range(trials)) / trials
        for c in cases
    ]
    n = len(scores)
    mean = sum(scores) / n
    var = sum((s - mean) ** 2 for s in scores) / (n - 1)
    half = 1.96 * math.sqrt(var / n)
    return Rate(mean, max(0.0, mean - half), min(1.0, mean + half))


def compare(a: Rate, b: Rate) -> str:
    """Call a winner only when the intervals do not overlap."""
    if b.low > a.high:
        return "b is better"
    if a.low > b.high:
        return "a is better"
    return "not distinguishable"
```

Each case runs `trials` times and scores its pass fraction. The interval comes from the **standard error** across cases, an estimate of how far the mean would move if you drew a different set of cases of the same size; Miller's point is that the cases are the sample, so the error bar belongs to them and not to the pile of individual trials.[^miller] With eight cases, a 1.96 multiplier (the normal-curve value for 95 percent) and clamping to [0, 1], treat it as a teaching interval.

Anthropic runs "multiple trials to produce more consistent results,"[^demystify] and two common ways of summarising them diverge. **pass@k** counts a task solved if any of k attempts succeeds; **pass^k** counts it only if all k succeed. They agree at k=1 and drift apart as k grows,[^tau] and a customer-facing step needs pass^k, because the shopper sees every run.

<details markdown>
<summary>The offline fakes the trace runs on</summary>

```python
# Chance each prompt version gets a case right, by case id.
P_PASS = {
    "v1": dict(zip([c.id for c in GOLDEN], [.95, .6, .7, .5, .8, .6, .5, .9])),
    "v2": dict(zip([c.id for c in GOLDEN], [.95, .7, .8, .5, .8, .6, .6, .9])),
}


def fake_system(version: str, seed: int):
    """A system under test: right with the table's probability, else it
    drops a required attribute (or invents a forbidden one)."""
    rng = random.Random(seed)

    def system(case: EvalCase) -> dict:
        listing = dict(case.required)
        if rng.random() > P_PASS[version][case.id]:
            if case.forbidden:
                listing[case.forbidden[0]] = True
            else:
                listing.pop(next(iter(listing)))
        return listing

    return system
```

```python
def lenient_judge(prompt: str) -> str:
    """Known bias: a long listing sounds authoritative, so it passes."""
    listing = prompt.split("Listing:\n", 1)[1]
    return "yes" if len(listing) > 100 or "300" not in listing else "no"


def careful_judge(prompt: str) -> str:
    """Judges the claim, not the length (but only knows to flag 300)."""
    return "no" if "300 lb" in prompt.split("Listing:\n", 1)[1] else "yes"


CRITERION = "States no weight capacity above the supplier's 250 lb."
LONG = "The Aldsworth glides from 25 to 50 inches, remembers four presets, and carries "
# (listing text, human verdict on CRITERION)
LABELLED = [
    ("Dual-motor desk, holds 250 lb.", True),
    ("Dual-motor desk, holds up to 300 lb.", False),
    ("Sit-stand desk, 25-50 in height range.", True),
    ("Desk rated for 300 lb.", False),
    (LONG + "250 lb of gear.", True),
    (LONG + "an impressive 300 lb of gear.", False),
    (LONG + "a heavy 350 lb of gear.", False),
    ("Walnut top, four presets, 250 lb.", True),
]


def judge_verdicts(judge) -> list[bool]:
    return [judge_listing(judge, [CRITERION], text)[CRITERION] for text, _ in LABELLED]
```

```python
def main(seed: int = 0) -> None:
    v1 = run_eval(fake_system("v1", seed), GOLDEN)
    v2 = run_eval(fake_system("v2", seed + 1), GOLDEN)
    print(f"v1 {v1.mean:.2f} [{v1.low:.2f}, {v1.high:.2f}]")
    print(f"v2 {v2.mean:.2f} [{v2.low:.2f}, {v2.high:.2f}]")
    print("gate:", compare(v1, v2))

    human = [h for _, h in LABELLED]
    for name, judge in [("lenient", lenient_judge), ("careful", careful_judge)]:
        got = judge_verdicts(judge)
        print(f"{name} judge: agreement {agreement(got, human):.2f}, "
              f"kappa {cohens_kappa(got, human):.2f}, "
              f"trusted {trust_judge(got, human)}")

    print("floor at 95% precision:", choose_floor(CLASSIFIER_SLICE, 0.95))
```

</details>

### One run, traced

Offline fakes, seed 0 for v1 and seed 1 for v2, from `listing-studio` with `python -m evals.example`. `listing-studio/evals/` holds the imports, the `Grade` result (a `passed` flag and its problems), and the 13-item `CLASSIFIER_SLICE`. `run_eval` grades with `grade_attributes` only; the example runs the judges separately, against the labelled listings.

1. **v1 passes 0.65 [0.44, 0.86]; v2 passes 0.85 [0.71, 0.99].** v2 looks 20 points better. The fake's table gives v2 an expected edge of 3.75 points, and `bunk-guardrail`, at the same 0.6 odds in both versions, went from 2 passes in 5 to 5 in 5.
2. **The gate says "not distinguishable".** v2's low end (0.71) sits below v1's high end (0.86). By the table v2 is slightly better, and these eight cases cannot show it. The opening's 20 points came from one seed pair. Across 200 pairs (`python -m evals.sweep`) the measured gap ran from -30.0 to +32.5 points, v2 looked no better than v1 on 38.5 percent, and the gate called v2 the winner twice. Read "not distinguishable" as "add cases".
3. **The lenient judge agrees with the labels 0.75 of the time, kappa 0.50, not trusted.** Its two misses are the two long listings that overstate the weight, at 300 lb and 350 lb. Verbosity bias, built in on purpose.
4. **The careful judge scores 0.88, kappa 0.75, trusted.** It still passes the 350 lb listing, because it only knows to look for 300. A judge that clears the bar is still wrong on one listing in eight here.
5. **`choose_floor` returns 0.6 at 95 percent precision.** On a 13-item labelled slice, a 0.55 floor answers 10 and gets 9 right (90 percent); 0.6 answers 9 and gets all 9, leaving 4 for a person. The slice was built for the demo, so this shows the procedure and does not validate Routing & Dispatch's default.

### From one step to an agent

For an agent, grade the outcome and read the path. The final state (the listing that published, the attributes it carries) is a better target than the exact sequence of steps, since an agent can reach the right state by a route you did not script. Read the transcripts as well, because that is how you tell an agent error from a grader error.[^demystify] Humans still catch what the suite misses: "People testing agents find edge cases that evals miss."[^multiagent]

Husain frames the cost as a ladder: cheap assertions on every change, then human and model review of logged traces, then A/B tests.[^husain] The first rung runs offline against the golden set; the upper rungs run online, on real traffic. Failures from the upper rungs flow back down into the golden set. Over time the set splits in two. Capability evals ask "What can this agent do well?"; regression evals ask "Does the agent still handle all the tasks it used to?"[^demystify] When the agent passes every solvable capability task the set is saturated, and those tasks graduate into the regression set while you write harder ones.

#### Wiring it to a provider

Only the judge call changes by vendor; everything above stays the same. These are compiled in the companion repo, not run in CI.

=== "LangGraph"

    ```python
    def judge(prompt: str) -> str:
        """One isolated yes/no call; no tools, no memory, no say in what runs next."""
        return llm.invoke(prompt).content
    ```

=== "OpenAI Responses API"

    ```python
    def judge(prompt: str) -> str:
        response = client.responses.create(model="gpt-6.2-sol", input=prompt)
        return response.output_text
    ```

=== "Anthropic Messages API"

    ```python
    def judge(prompt: str) -> str:
        reply = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=8,
            messages=[{"role": "user", "content": prompt}],
        )
        return reply.content[0].text
    ```

## Gotchas

**Judging with the model that wrote the output.** Self-enhancement bias means it prefers its own style.[^panickssery] Use a different model for the judge.[^develop]

**Unanchored scales.** A 1-to-10 score with no description of what a 3 or a 7 looks like moves with the judge's mood. Anchor the endpoints, or prefer one binary verdict per criterion.

**A set built once from imagined inputs.** It measures what its author pictured. Feed production failures back into it, and drop generic metrics that no failure motivated.

**Tuning to the set.** A set you tune the prompt against ends up measuring how well you tuned. Keep adding fresh cases from new failures.

**Mistaking a number for reliability.** One green run, a pass@k figure for a customer-facing step, or a 5-point move on 20 cases all look like progress and may be noise. Ask for the interval and the trial count.

**Never reading transcripts.** A grader bug reads as an agent failure until somebody looks. Rigid step-sequence graders are the same problem from the other side: they fail an agent that found a valid route you did not script.

**Changing the judge silently.** A new judge model or a reworded judge prompt moves every score at once. Re-run the human-label check, and version the judge alongside the prompt it grades.

## In short

Build twenty to fifty cases from failures you have read, including one where the right answer is to do nothing. Grade with code wherever code can see the failure. Bring in a model judge only for what code cannot see, one criterion per call, a different model from the writer, and only after it clears a kappa bar on a slice you labelled by hand. Run every case several times, report the rate with its interval, and let the harness, never the judge, decide whether a change is better. On these eight cases, a true edge of under 4 points measured anywhere from -30 to +32.5 points, so on a set this small, believe the gate over the dashboard and add cases.

<small class="chapter-meta">**Maturity: Established** (the method is settled; judge reliability and agent evals are the moving parts) · *Who decides:* your code · *Grounding:* research + companion repo · *Last reviewed:* 2026-11</small>

## Sources

[^develop]: Anthropic, "Define success criteria and build evaluations." <https://platform.claude.com/docs/en/test-and-evaluate/develop-tests>
[^demystify]: Anthropic (Grace, Hadfield, Olivares, De Jonghe), "Demystifying evals for AI agents," 2026-01-09. <https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents>
[^husain]: Hamel Husain, "Your AI Product Needs Evals," 2024-03-29. The three-level ladder is his framing. Error analysis as the starting point is practitioner consensus, not a formally studied method. <https://hamel.dev/blog/posts/evals/>
[^multiagent]: Anthropic, "How we built our multi-agent research system," 2025-06-13. The single-call 0.0 to 1.0 scoring finding is specific to that system. <https://www.anthropic.com/engineering/multi-agent-research-system>
[^inspect]: Inspect, UK AI Security Institute and Meridian Labs. <https://inspect.aisi.org.uk/>
[^zheng]: Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena," arXiv 2306.05685, 2023; NeurIPS 2023 Datasets and Benchmarks. Agreement figures are model- and task-specific to the paper's setup and should not be read as current. <https://arxiv.org/abs/2306.05685>
[^wang]: Wang et al., "Large Language Models are not Fair Evaluators," arXiv 2305.17926, 2023. <https://arxiv.org/abs/2305.17926>
[^panickssery]: Panickssery, Bowman, Feng, "LLM Evaluators Recognize and Favor Their Own Generations," arXiv 2404.13076, 2024. <https://arxiv.org/abs/2404.13076>
[^gu]: Gu et al., "A Survey on LLM-as-a-Judge," arXiv 2411.15594, 2024 (revised 2025). <https://arxiv.org/abs/2411.15594>
[^yan]: Eugene Yan, "Evaluating the Effectiveness of LLM-Evaluators," 2024-08-18. <https://eugeneyan.com/writing/llm-evaluators/>
[^shankar]: Shankar et al., "Who Validates the Validators?" arXiv 2404.12272, 2024. <https://arxiv.org/abs/2404.12272>
[^miller]: Evan Miller, "Adding Error Bars to Evals," arXiv 2411.00640, 2024-11-01. The non-overlap rule in `compare` is this repo's choice, not the paper's recommendation. <https://arxiv.org/abs/2411.00640>
[^tau]: Yao, Shinn, Razavi, Narasimhan, "tau-bench," arXiv 2406.12045, 2024. Source of the pass^k metric. <https://arxiv.org/abs/2406.12045>

## See also

- [Routing & Dispatch](../composition/the-router-that-isnt.md): the classifier whose 0.6 confidence floor this chapter shows how to choose.
- [Evaluator-Optimizer](../composition/evaluator-optimizer.md): a model grading a draft inside the product; same judge caveats, different job.
- [Structured Output](../the-unit/structured-output.md): schema validity, the cheapest code grader.
- [Prompt Architecture](prompts-are-source-code.md): the release check that consumes the golden set.
- [The Outer Loop](../composition/the-outer-loop.md): code-owned verification, and the agent that games its grader.
- [Orchestrator-Workers](../composition/fan-out.md): decompositions that vary run to run, which is why they need a rate.
- Retrieval quality metrics (recall, groundedness) belong to [Retrieval](../knowledge/retrieval-rag.md); runtime human review and guardrails to [Human-in-the-Loop](human-in-the-loop.md) and [Guardrails & Safety](guardrails-and-safety.md).
