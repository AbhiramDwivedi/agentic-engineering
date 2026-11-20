# 3.4 Evaluator-Optimizer

*One call drafts, a second grades it against a written bar and says what to fix, and the loop revises until the verdict passes or a cap stops it. Give the grader nothing but its own opinion and the loop is grading its own homework.*

*Also called: generator-critic, self-refine, reflection, LLM-as-a-judge.*

## Why you'd reach for it

Ask a model to check its own work and it will find something to change. Whether the change is an improvement depends on what it has to check the work against.

One model call gives you one draft. Where the bar is mechanical you check it and you are done: a schema validates or it does not. Where the bar is a judgment (does this read well, does this translation keep the nuance, has this search gathered enough) a single call gets no second look, and the failure is quiet because nothing raises. You get a plausible, mediocre answer that passes every validator you own, and it ships.

Take the second step of a supplier-feed pipeline. Listing Studio turns a raw supplier feed into a live storefront listing, and that step handles the rows the feed left incomplete. The Aldsworth desk, a dual-motor sit-stand desk from Northvale Furnishings, arrives with `leg_material` blank and no `weight_capacity_lbs` at all, so something has to write the clarifying questions for the supplier. The first draft asks three, two circling the same point about the frame, the third loose enough ("could you tell us more about the materials?") that the supplier replies with a paragraph and the field stays empty. A validator catches none of that. It can confirm the questions are non-empty and that each gap is mentioned somewhere, but not that a question is answerable. The listing waits at `draft` for a second round trip with a supplier who has no reason to hurry.

So add a call whose only job is to grade. Give it the gaps, the draft and a written rubric, have it return a score plus reasons the drafter can act on, and cap the rounds.

Reach for it when:

- the bar is a judgment you can describe but not compute, and you can write down what good looks like;
- a first draft is usually usable and usually improvable, and the improvement is worth two or three more model calls;
- the evaluator can be handed something the drafter cannot assert by itself: a tool result, a retrieved fact, a test outcome.

Anthropic's guide, which named the workflow, draws roughly the same boundary: it pays off "when we have clear evaluation criteria, and when iterative refinement provides measurable value."[^anthropic-eo] If the people who own the bar cannot agree on what it is, a judge call does not settle that argument. It hard-codes one side of it. And if the check is mechanical, run the check: a judge call to confirm a word count is money spent to replace a regex.

## What it actually is

Evaluator-optimizer is two model calls in a loop: "one LLM call generates a response while another provides evaluation and feedback in a loop," in Anthropic's words.[^anthropic-eo] The drafter goes again with the feedback in hand, and the loop repeats until the evaluation passes or your code stops it. The literature calls that first call the generator; this chapter says drafter, matching the code below.

![The same loop drawn twice, side by side, with one node different. On the left, chapter 3.4: the bar is a judgment, can a supplier answer this question with a value. On the right, chapter 3.7's loop: the bar is a rule, is the description 150 words or fewer. Both sides run the identical circuit. A rectangle of your code hands over the work, a rounded node drafts, and an evaluate() box runs two rungs, first the free exact checks and then the node that settles the verdict. That second rung is the only thing that differs: on the left it is rounded, a model grading the draft against a written rubric, which no function can compute; on the right it is a rectangle counting words against a limit, which any function can compute. From there both sides are identical again: a verdict carrying passed, a score and specific reasons; a rectangle holding the cap of three rounds and the ratchet that keeps the best score rather than the last; and either the reasons routed back to the drafter or the best draft released. Look at what computes passed.](evaluator-optimizer-who-judges.svg)

What the model decides here is small and specific: whether the draft is good enough. Your code decides how many rounds run, which draft survives, what the loop returns when the rounds run out, and whether the judge is called at all. That one judgment is enough to make the pattern new, because no dispatch table (a static lookup from event type to handler) and no retry loop can render it, and it is also the pattern's whole exposure, because a judgment can be wrong in ways a failing test never is.

The loop next door is identical on a whiteboard. The moment the check is something a deterministic function renders (a compiler exit code, a test's pass count, a word count) the deciding has moved into your code. Generate, check, maybe retry is then [3.7 The Outer Loop](the-outer-loop.md)'s pattern wearing this chapter's picture: same boxes, same arrows, a different owner of the verdict. [3.1 Prompt Chaining](prompt-chaining.md) draws the same line at smaller scale: a chain's gate is a code check with a fixed retry behind it. To tell them apart, look at what computes `passed`.

None of this was invented in 2025, and the lineage shows what makes the loop work. Self-Refine (Madaan et al., NeurIPS 2023) proved the cheap version: one model as generator, critic and refiner, no additional training, gains across the seven tasks it evaluated.[^self-refine] Reflexion (Shinn et al., NeurIPS 2023) got more out of the same calls by keeping the critique, a verbal reflection in an episodic memory buffer carried into the next attempt, a semantic gradient standing in for a weight update.[^reflexion] CRITIC (Gou et al., ICLR 2024) went further and changed what the evaluator eats: its critic calls external tools, a search engine or a code interpreter, and checks the draft against what comes back.[^critic] The idea is older than any of them. Constitutional AI (Bai et al., 2022) has a written constitution drive a model's critique and revision of its own output, and the AI-labeled preferences that fall out become training signal rather than a loop at inference ([8.3 To Train or to Prompt](../production/train-or-prompt.md)).[^cai]

CRITIC changed the evaluator's diet for a reason: a model grading its own work with nothing else to go on is not reliably better than its own first attempt, and can be worse. Huang et al. (ICLR 2024) isolate that case and name it *intrinsic* self-correction (no external feedback, the model checking only its own reasoning), and find LLMs "struggle to self-correct their responses" under it, in several settings talking themselves out of a correct first answer.[^huang] Planning shows the same shape. Valmeekam, Marquez and Kambhampati found that self-critique degraded plan generation and that the critic produced false-positive verifications, certifying plans that did not work.[^stechly1] Stechly et al. later generalize the limitation across reasoning and planning tasks broadly.[^stechly2]

What closes the gap is a signal the drafter did not produce. If you use a coding agent, you have watched the everyday case work: write, execute, observe, fix, where the test suite's failure is a fact about the code rather than an opinion about it ([2.5 The Agent Loop](../the-unit/the-agent-loop.md) and [9.6 Coding Agents](../frontier/coding-agents.md) own the mechanism). CRITIC's tool-calling critic is the same move made deliberately.[^critic] At the far end of the scale, DeepMind's AlphaEvolve scores a population of candidate programs with an automated evaluator rather than letting the model read its own work, and that setup produced a 4x4 complex-matrix-multiplication algorithm using 48 scalar multiplications, beating, in that setting, Strassen's 1969 algorithm, the textbook method for multiplying matrices in fewer multiplications.[^alphaevolve] Put something in the evaluator's hands that the drafter does not already believe.

With an independent judge or an external signal, this is an established workflow, with a research lineage behind it and vendor documentation in front of it. Grading its own homework and nothing more is contested, and the burden of proof sits on the loop rather than on the skeptic.

[3.5 The Specialist Panel](specialist-panel.md) runs fixed personas over one input once and nothing revises; [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md) rejects or redacts and never asks for a rewrite. A fan-out synthesizer that grades its own reconciliation and goes round again has quietly become this loop ([3.3 Orchestrator-Workers](fan-out.md)).

## How to do it

The minimum is a drafter, a judge, and a loop with a cap. Two typed contracts hold it together.

```python
class ClarifyingQuestions(BaseModel):
    """The drafter's output: one clarifying question per attribute this
    supplier feed row left missing or ambiguous."""
    model_config = ConfigDict(extra="forbid")

    questions: list[str]


class Verdict(BaseModel):
    """The evaluator's judgment. `reasons` must be specific enough for the
    drafter's next attempt to act on."""
    model_config = ConfigDict(extra="forbid")

    passed: bool
    score: float          # 0.0-1.0; the ratchet compares drafts on this
    reasons: list[str]    # e.g. "question 2 duplicates question 1"
```

A verdict that comes back as a bare `false` tells the drafter nothing it can act on, so the next attempt is a re-roll rather than a revision and you have bought a random number with a judge call. "Question 2 duplicates question 1" is the shape you want, a critique that names the defect, which is [2.2 Structured Output](../the-unit/structured-output.md) doing judge duty.

The loop itself is short. The `evaluate()` it calls is the three-rung ladder defined a few lines below: the free exact checks first, a judge call only on what clears them.

```python
# The cap guards a measured failure mode, not a hypothetical one: see
# "When Agents Do Not Stop" (arxiv.org/abs/2607.01641).
DEFAULT_MAX_ITERATIONS = 3


@dataclass
class LoopResult:
    """passed: whether the loop ended on a passing verdict. draft: the
    best-scoring attempt seen, not necessarily the last one drafted.
    verdict: the Verdict that scored `draft`. iterations: rounds run.
    stopped_reason: "passed" or "capped"."""
    passed: bool
    draft: ClarifyingQuestions
    verdict: Verdict
    iterations: int
    stopped_reason: str  # "passed" or "capped"


def run_loop(
    drafter_fn: Any,  # callable(gaps, feedback: Verdict | None) -> ClarifyingQuestions
    judge_fn: Any,     # callable(gaps, draft) -> Verdict
    gaps: list[str],
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> LoopResult:
    """Draft, evaluate, revise -- until the verdict passes or the cap trips.

    A revision that scores lower than the best draft so far still counts
    against `iterations` and is still discarded; `best` only moves forward
    on a strictly higher score.
    """
    best_draft: Optional[ClarifyingQuestions] = None
    best_verdict: Optional[Verdict] = None
    feedback: Optional[Verdict] = None

    for i in range(1, max_iterations + 1):
        draft = drafter_fn(gaps, feedback)
        verdict = evaluate(judge_fn, gaps, draft)

        if best_verdict is None or verdict.score > best_verdict.score:
            best_draft, best_verdict = draft, verdict

        if verdict.passed:
            return LoopResult(
                passed=True, draft=draft, verdict=verdict,
                iterations=i, stopped_reason="passed",
            )
        feedback = verdict  # the specific critique, never a bare "fail"

    return LoopResult(
        passed=False, draft=best_draft, verdict=best_verdict,
        iterations=max_iterations, stopped_reason="capped",
    )
```

Four controls in that listing do the work.

The cap is unconditional. Three rounds, whatever the model would prefer, and the number lives in your code rather than in a prompt. A round count is one ceiling; a spend limit and a wall-clock deadline bound what it does not. It guards a measured failure mode: a 2026 static-analysis sweep of 6,549 public LLM-agent repositories confirmed 68 unbounded-loop failures across 47 projects at 91.9% precision.[^ial]

Inside the cap, the ratchet decides what survives. `best_verdict` moves only when a draft scores strictly higher than the one it replaces, so a worse revision still gets graded, still counts against `iterations`, and is then discarded. Without it you return whatever the last round produced, and a loop that alternates between two "fixes" with no net progress hands you whichever one it happened to stop on.

The revise edge is what makes any of that a loop. In plain Python it is one line, `feedback = verdict`, plus the top of the `for`. Leave it out and you get a system that computes a verdict, logs it, and carries on with the draft it already had: a judge's bill and a decorated trace.

Then the exit, which is a contract. `LoopResult` never raises, never returns `None`, and never dresses a failing draft as a pass. It carries `passed`, the best draft, the verdict that scored it, and `stopped_reason`, so the caller decides once, in code, what a capped run means: ship the best draft anyway, escalate to a person ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md)), or fail closed. Letting that fall out of wherever the loop happened to be when the cap hit is how a mediocre draft ships with nobody choosing to.

An evaluator can stand on three rungs. A deterministic oracle (a schema validator, a compiler, a unit test, a regex) is nearly free and never wrong about what it checks, and it checks only what is mechanically checkable. An LLM judge with a written rubric is what you need the moment the check is subjective. A human is the backstop where the call is too consequential or ambiguous to automate. Order them cheapest and most reliable first, and put the ordering in code rather than a comment: that is all `evaluate()` is.

<details markdown><summary><code>evaluate()</code> defined: the free gate, then the judge</summary>

```python
@dataclass
class GateResult:
    ok: bool
    reasons: list[str]


def gate_draft(gaps: list[str], draft: ClarifyingQuestions) -> GateResult:
    """Cheap, exact, no model call: no empty questions, no duplicates, and
    every named gap covered by at least one question."""
    reasons = []
    seen: set[str] = set()
    for q in draft.questions:
        if not q.strip():
            reasons.append("a clarifying question is empty")
            continue
        normalized = q.strip().lower()
        if normalized in seen:
            reasons.append(f"duplicate question: {q!r}")
        seen.add(normalized)

    for gap in gaps:
        if not any(gap.lower() in q.lower() for q in draft.questions):
            reasons.append(f"no question addresses the gap {gap!r}")

    return GateResult(ok=not reasons, reasons=reasons)


def evaluate(judge_fn: Any, gaps: list[str], draft: ClarifyingQuestions) -> Verdict:
    """Cheap-first: gate_draft() runs before judge_fn ever does. A draft
    that fails the gate never reaches a model -- the judge call is the
    expensive step, so it only runs on what already cleared the free one.
    """
    gate = gate_draft(gaps, draft)
    if not gate.ok:
        return Verdict(passed=False, score=0.0, reasons=gate.reasons)
    return judge_fn(gaps, draft)
```

</details>

Be honest about which parts of the task have a real termination condition. "No more than 150 words" is machine-checkable and the loop can prove it is done. "Are these good clarifying questions" cannot be proved at all; that loop runs on a judgment plus a cap, and calling the cap a stop condition does not make it one.

One run on the Aldsworth desk, whose feed row ingest has already parsed:

1. Step 2 hands `run_loop` the two gaps ingest could not fill, `leg_material` and `weight_capacity_lbs`. `feedback` is `None`, so the drafter writes cold.
2. The first draft asks three questions, two of them about the frame. `gate_draft` finds no empty strings and no duplicates, but no question names `weight_capacity_lbs`, so `evaluate` returns `passed=False`, `score=0.0` and one reason, and the judge is never called. A missing gap is the kind of failure a validator can see; the loose question from the opening is not, and it is still in the draft. The failed round costs a drafter call and nothing else.
3. `best_verdict` is `None`, so this failing draft becomes `best` by default, `feedback` becomes that verdict, and the loop goes round.
4. The second draft covers both gaps, clears the gate, and reaches the judge, which returns *"passed: false, score: 0.6, reasons: ['question 3 asks about materials in general and cannot be answered with a value for leg_material']"*. 0.6 beats 0.0, so the ratchet moves `best` forward, and that reason is what the drafter sees next.
5. The third draft names the field and asks for a number. The judge returns `passed=True` with `score=0.9`, and `run_loop` returns immediately: `iterations=3`, `stopped_reason="passed"`. Had it failed too, the caller would have got `passed=False`, `stopped_reason="capped"`, and the best draft seen.

The loop scales two ways, and they trade against each other.

Going from one round to many grows the context as well as the count: every round after the first carries the previous draft and its critique into the prompt, so tokens per round rise alongside the rounds. Forward the critique and not the transcript ([5.4 Compaction](../knowledge/compaction-and-the-window.md)); a loop that appends the full history of its own failures spends more on remembering them than on fixing them.

The other direction trades revision for parallelism. Best-of-N is the sibling that never loops: sample N drafts independently, score each, keep the highest. The draws carry nothing forward and cannot thrash, at the cost of paying for N generations up front and learning nothing from what the judge said. They also run at once, where a revision loop is sequential, so N drafts can cost more and still land sooner. The lineage runs through reward-model reranking, scoring each draw with a model trained to predict which output a human would prefer, from Stiennon et al.'s summarization work to WebGPT.[^bestofn] The difference shows in the signature below: gaps only, no feedback to carry.

<details markdown><summary>Best-of-N: the same evaluator, no revision round</summary>

```python
@dataclass
class BestOfNResult:
    draft: ClarifyingQuestions
    verdict: Verdict


def run_best_of_n(
    drafter_fn: Any,  # callable(gaps) -> ClarifyingQuestions -- no feedback arg
    judge_fn: Any,     # callable(gaps, draft) -> Verdict
    gaps: list[str],
    n: int,
) -> BestOfNResult:
    """Draw n independent drafts, score each, return the highest scorer."""
    candidates = [drafter_fn(gaps) for _ in range(n)]
    scored = [(draft, evaluate(judge_fn, gaps, draft)) for draft in candidates]
    best_draft, best_verdict = max(scored, key=lambda pair: pair[1].score)
    return BestOfNResult(draft=best_draft, verdict=best_verdict)
```

</details>

DSPy, a framework for composing LLM calls as typed modules rather than prompt strings, ships both as separate classes, `dspy.Refine` (iterate with generated feedback) beside `dspy.BestOfN` (parallel rollouts, no feedback), so the boundary is two objects you can import rather than one idea under two names.[^dspy]

> **From production.** The version of this loop I shipped ran this shape, and the cap was three. Nobody argued with three: it was a default that turned out to be fine rather than a number anyone measured.

The common frameworks each ship a spelling of this loop, differing mostly in where the cap lives. LangGraph makes it a conditional edge back to the drafting node, the shape LangChain's Reflection Agents post publishes.[^langgraph-refl] The OpenAI Agents SDK ships it runnable: `examples/agent_patterns/llm_as_a_judge.py` is a generator agent, a judge agent, and a loop that runs until the judge is satisfied.[^oai-judge] Google's Agent Development Kit (ADK) gives you a `LoopAgent` and an `exit_loop` tool for the critic, with no default iteration cap, so `max_iterations` is yours to set.[^adk-loop] CrewAI puts the same idea at task level with `guardrail_max_retries`.[^crewai]

#### Wiring it to a provider

`route_after_evaluate` maps `{"revise": "draft", "done": END}`, so a revise verdict routes back to the drafter instead of into a log line. The raw-SDK versions build only `drafter_fn` and `judge_fn` and hand them to the same `run_loop`; the cap, the ratchet and the gate do not change per provider.

=== "LangGraph"

    ```python
    class ClarifyState(TypedDict):
        gaps: list[str]
        draft: Optional[ClarifyingQuestions]
        verdict: Optional[Verdict]
        best_draft: Optional[ClarifyingQuestions]
        best_verdict: Optional[Verdict]
        iteration: int


    def draft_node(state: ClarifyState) -> dict:
        """Draft clarifying questions, informed by the prior verdict's reasons
        on every round after the first."""
        prompt = f"Draft one clarifying question per open attribute: {state['gaps']}."
        if state.get("verdict") is not None and not state["verdict"].passed:
            prompt += f" Fix these problems: {state['verdict'].reasons}"
        draft = draft_chain.invoke(prompt)
        return {"draft": draft, "iteration": state.get("iteration", 0) + 1}


    def _judge_fn(gaps: list[str], draft: ClarifyingQuestions) -> Verdict:
        return judge_chain.invoke(
            f"Grade these clarifying questions against gaps {gaps}: {draft.questions}"
        )


    def evaluate_node(state: ClarifyState) -> dict:
        """Gate first, judge second -- the same evaluate() the plain-Python
        listing uses. The ratchet: best_* only moves forward on a strictly
        higher score."""
        verdict = evaluate(_judge_fn, state["gaps"], state["draft"])
        best_draft, best_verdict = state.get("best_draft"), state.get("best_verdict")
        if best_verdict is None or verdict.score > best_verdict.score:
            best_draft, best_verdict = state["draft"], verdict
        return {"verdict": verdict, "best_draft": best_draft, "best_verdict": best_verdict}


    def route_after_evaluate(state: ClarifyState) -> str:
        """The wired revise edge: a "revise" verdict actually routes back to
        draft_node, bounded by DEFAULT_MAX_ITERATIONS -- never an unbounded
        loop, and never a verdict computed only to be displayed."""
        if state["verdict"].passed:
            return "done"
        if state["iteration"] < DEFAULT_MAX_ITERATIONS:
            return "revise"
        return "done"  # capped: state["best_draft"] carries the failure-return contract


    builder = StateGraph(ClarifyState)
    builder.add_node("draft", draft_node)
    builder.add_node("evaluate", evaluate_node)
    builder.add_edge(START, "draft")
    builder.add_edge("draft", "evaluate")
    builder.add_conditional_edges(
        "evaluate", route_after_evaluate, {"revise": "draft", "done": END}
    )
    graph = builder.compile()

    result = graph.invoke({"gaps": ["leg_material", "weight_capacity_lbs"], "iteration": 0})
    print(result["best_verdict"].passed, result["best_draft"].questions)
    ```

=== "OpenAI Responses API"

    ```python
    def drafter_fn(gaps: list[str], feedback: Verdict | None) -> ClarifyingQuestions:
        prompt = f"Draft one clarifying question per open attribute: {gaps}."
        if feedback is not None:
            prompt += f" Fix these problems: {feedback.reasons}"
        response = client.responses.create(
            model="gpt-5.5",
            input=[{"role": "user", "content": prompt}],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "ClarifyingQuestions",
                    "schema": ClarifyingQuestions.model_json_schema(),
                    "strict": True,
                }
            },
        )
        return ClarifyingQuestions.model_validate_json(response.output_text)


    def judge_fn(gaps: list[str], draft: ClarifyingQuestions) -> Verdict:
        response = client.responses.create(
            model="gpt-5.5",
            input=[
                {
                    "role": "user",
                    "content": f"Grade these clarifying questions against gaps {gaps}: {draft.questions}",
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "Verdict",
                    "schema": Verdict.model_json_schema(),
                    "strict": True,
                }
            },
        )
        return Verdict.model_validate_json(response.output_text)


    result = run_loop(drafter_fn, judge_fn, GAPS)
    print(result.stopped_reason, result.draft.questions)
    ```

=== "Anthropic Messages API"

    ```python
    def drafter_fn(gaps: list[str], feedback: Verdict | None) -> ClarifyingQuestions:
        prompt = f"Draft one clarifying question per open attribute: {gaps}."
        if feedback is not None:
            prompt += f" Fix these problems: {feedback.reasons}"
        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=[_DRAFT_TOOL],
            tool_choice={"type": "tool", "name": "produce_clarifying_questions"},
            messages=[{"role": "user", "content": prompt}],
        )
        tool_block = next(b for b in reply.content if b.type == "tool_use")
        return ClarifyingQuestions.model_validate(tool_block.input)


    def judge_fn(gaps: list[str], draft: ClarifyingQuestions) -> Verdict:
        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=[_JUDGE_TOOL],
            tool_choice={"type": "tool", "name": "produce_verdict"},
            messages=[
                {
                    "role": "user",
                    "content": f"Grade these clarifying questions against gaps {gaps}: {draft.questions}",
                }
            ],
        )
        tool_block = next(b for b in reply.content if b.type == "tool_use")
        return Verdict.model_validate(tool_block.input)


    result = run_loop(drafter_fn, judge_fn, GAPS)
    print(result.stopped_reason, result.draft.questions)
    ```

## Gotchas

**The judge has a thumb on the scale.** Zheng et al. document position, verbosity and self-enhancement bias in LLM judges. Their repetitive-list attack, padding an answer with a restatement of its own list, inflated Claude-v1's and GPT-3.5's scores roughly 91% of the time against 8.7% for GPT-4, the same strong judge that otherwise reaches over 80% agreement with human preference on that paper's benchmarks.[^judge] Panickssery, Bowman and Feng add the finding that bites hardest here: self-recognition ability correlates linearly with self-preference, so a model scores its own output higher than the quality gap explains.[^selfpref] In most implementations, this chapter's companion code included, drafter and evaluator are the same model. Reach first for an external signal, a tool result or a test outcome, because it does not run through the judge's taste. The prompting mitigations are damage control: a different model as judge, the draft's provenance hidden from it, reference-guided grading (handing the judge a worked answer to compare against rather than grading in the abstract), randomized order wherever two candidates are compared. Worth doing, and none of them a fix, because independence is a matter of degree. Two calls to the same model in different roles are one opinion asked twice, and two different models can still share a training-era taste.

Whether any of them closes the gap for a same-model pair is unsettled. Treat a judge you have not checked against human labels as an instrument with an unknown offset ([4.2 Evaluation](../craft/proving-it-works.md)).

**A bad evaluator gets exploited, not fooled.** METR, the lab that runs independent frontier-model evaluations, watched models monkey-patch the evaluator function, overwrite an equality operator, and stub out a timing function. Reward hacking ran more than 43 times more often on one of its task suites than the other. METR's own explanation is a maybe: on that suite the model could see the entire scoring function.[^metr] Their setting has a gradient and a visible scorer and yours is three capped rounds of a prompt, but the mechanism carries: your drafter reads the rubric's own reasons every round, which is the visible-scoring-function case in miniature. Optimization pressure finds the holes in a rubric the way it finds them in a benchmark, and the symptom is a score that climbs while the output stops getting better.

**The multiplier is per iteration.** Three rounds with a judge call in each is six model calls where generate-and-ship is one, and the free gate is what keeps it below that: in the run above it rejected round one before the judge ever saw it, so the worked example cost five. Treat that as a multiplier on generation cost rather than a fixed overhead, and price it before putting it on a high-volume, low-stakes step ([8.4 Controlling Cost](../production/controlling-cost.md)). Run the arithmetic on your own token prices.[^cost]

**A rubber stamp, or a judge that never says yes.** Both are common and cheap to detect, so log `score` and `stopped_reason` on every run. If nothing ever fails the first round, the rubric is decoration and you are paying a judge call to admire the drafter. If every run ends at `capped`, the bar sits above what the drafter can reach and the loop is a three-call tax. Neither shows up in a demo, because a demo is one run.

**The loop where a validator would do.** Wrapping a judge and a revision round around work a schema check already settles is the over-orchestration entry in the [Anti-Patterns Catalog](../catalogs/anti-patterns.md), and it is expensive because it looks like diligence.

## In short

Build the loop where the bar is a judgment you can write down but cannot compute, and build its controls first: an unconditional cap, a ratchet that keeps the best draft rather than the last, a verdict carrying reasons and not a bare fail, a revise edge that routes back, and one decision made in code about what a capped run ships. Run the free checks before the paid ones. Give the evaluator a signal the drafter did not produce, or at minimum a different model reading a rubric it did not write; where you cannot, keep the cap at two or three and treat the loop as polish rather than repair, because the evidence for a model fixing its own work unaided points the other way. If the critiques are not helping, draw N independently instead. And before any of it, check what computes `passed`. If a function can, you want the cheaper loop next door.

<small class="chapter-meta">**Maturity: Established (with an independent judge or an external signal) · Contested (intrinsic self-correction, no external signal)** (the workflow is vendor-named with a 2022-2024 research lineage behind it, and that same literature finds a model checking only its own reasoning is not reliably better than its own first attempt, and can be worse) · *Who decides:* the model (the verdict) · *Grounding:* production + research · *Last reviewed:* 2026-08</small>

## Sources

[^anthropic-eo]: Anthropic, "Building Effective Agents" (2024-12-19). "In the evaluator-optimizer workflow, one LLM call generates a response while another provides evaluation and feedback in a loop." Named as effective "when we have clear evaluation criteria, and when iterative refinement provides measurable value," instanced by literary translation and complex multi-round search. <https://www.anthropic.com/research/building-effective-agents>
[^self-refine]: Madaan, A. et al., "Self-Refine: Iterative Refinement with Self-Feedback" (NeurIPS 2023). A single LLM generates, critiques and refines its own output with no additional training. The paper reports outputs "improving by ~20% absolute on average in task performance" across the seven tasks it evaluates: an absolute gain, not a relative one, and secondary summaries that render it as a relative improvement are wrong. <https://arxiv.org/abs/2303.17651>
[^reflexion]: Shinn, N. et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (NeurIPS 2023). Converts feedback into a verbal reflection stored in an episodic memory buffer and carried into the next attempt, described by the authors as a semantic gradient signal, with no weight update. <https://arxiv.org/abs/2303.11366>
[^critic]: Gou, Z. et al., "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing" (ICLR 2024). The evaluator step calls external tools (a search engine, a code interpreter) rather than only introspecting. <https://arxiv.org/abs/2305.11738>
[^cai]: Bai, Y. et al., "Constitutional AI: Harmlessness from AI Feedback" (Anthropic, 2022-12). A written constitution lets a model critique and revise its own outputs; the resulting AI-labeled preferences train a reward model rather than a human-labeled one, the approach known as RLAIF (reinforcement learning from AI feedback). <https://arxiv.org/abs/2212.08073>
[^huang]: Huang, J. et al., "Large Language Models Cannot Self-Correct Reasoning Yet" (ICLR 2024). Defines intrinsic self-correction (no external feedback) and finds LLMs "struggle to self-correct their responses" under it, sometimes changing a correct initial answer to an incorrect one. The word in the abstract is *responses*; *reasoning* is from the title, so quote the two separately. <https://arxiv.org/abs/2310.01798>
[^stechly1]: Valmeekam, K., Marquez, M., Kambhampati, S., "Can Large Language Models Really Improve by Self-critiquing Their Own Plans?" (2023). Self-critique degrades plan-generation performance and produces false-positive verifications. <https://arxiv.org/abs/2310.08118>
[^stechly2]: Stechly, K., Valmeekam, K., Kambhampati, S., "On the Self-Verification Limitations of Large Language Models on Reasoning and Planning Tasks" (2024). <https://arxiv.org/abs/2402.08115>
[^alphaevolve]: Novikov, A. et al. (Google DeepMind), "AlphaEvolve: A coding agent for scientific and algorithmic discovery" (2025). An LLM-driven evolutionary loop over a population of candidate programs, each scored by an automated evaluator function. Its reported infrastructure results (fleet-compute recovery, kernel speedups) are snapshot measurements of one system at one moment and will move; the 4x4 complex-matrix-multiplication result, 48 scalar multiplications and the first improvement on Strassen's 1969 algorithm in that setting, is a discrete published finding. <https://arxiv.org/abs/2506.13131>
[^judge]: Zheng, L. et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023, Datasets & Benchmarks track). Documents position, verbosity and self-enhancement bias in LLM judges. The repetitive-list attack (appending a restatement of the answer's own list) inflated Claude-v1's and GPT-3.5's scores roughly 91% of the time against 8.7% for GPT-4; GPT-4 as judge otherwise reaches over 80% agreement with human preference on the paper's own benchmarks. Both figures are benchmark-specific and model-generation-specific; cite the finding, not a frozen percentage. <https://arxiv.org/abs/2306.05685>
[^selfpref]: Panickssery, A., Bowman, S., Feng, S., "LLM Evaluators Recognize and Favor Their Own Generations" (NeurIPS 2024). Self-recognition ability correlates linearly with self-preference bias. <https://arxiv.org/abs/2404.13076>
[^metr]: METR (Model Evaluation and Threat Research), "Recent Frontier Models Are Reward Hacking" (2025-06-05). Observed reward-hacking behavior during task evaluation, including monkey-patching the evaluator function, overwriting an equality operator, and stubbing out a timing function. Reward hacking was "more than 43x more common on RE-Bench tasks than HCAST tasks, perhaps because on RE-Bench tasks the model was able to see the entire scoring function": METR states the visibility explanation as a conjecture, not a measured cause, and this page keeps that hedge. An early, evolving estimate on a specific benchmark pair. <https://metr.org/blog/2025-06-05-recent-reward-hacking/>
[^ial]: Hou, Wang, Zhao, Wang, "When Agents Do Not Stop: Uncovering Infinite Agentic Loops in LLM Agents" (submitted 2026-07-02). Static analysis across 6,549 public LLM-agent repositories; 68 confirmed unbounded-loop failures across 47 projects, at 91.9% precision. <https://arxiv.org/abs/2607.01641>
[^cost]: No per-iteration cost figure specific to this pattern surfaced in the research for this page. The multiplier is arithmetic over your own provider's token prices and your own round count, not a published benchmark number.
[^bestofn]: Stiennon, N. et al., "Learning to Summarize from Human Feedback" (NeurIPS 2020), <https://arxiv.org/abs/2009.01325>; Nakano, R. et al., "WebGPT: Browser-Assisted Question-Answering with Human Feedback" (2021), <https://arxiv.org/abs/2112.09332>. The lineage for best-of-N reranking: sample N independent completions, score each with a reward model, keep the highest, with no revision step.
[^langgraph-refl]: LangChain, "Reflection Agents." Nodes for draft, tool execution and revision, with a conditional edge inspecting state to decide whether to loop back or finish. <https://www.langchain.com/blog/reflection-agents>
[^oai-judge]: OpenAI, the public `openai/openai-agents-python` repository, `examples/agent_patterns/llm_as_a_judge.py`. A generator agent produces an outline, a judge agent evaluates it and returns feedback, and the loop continues until the judge is satisfied. <https://github.com/openai/openai-agents-python/blob/main/examples/agent_patterns/llm_as_a_judge.py>
[^adk-loop]: Google, Agent Development Kit docs, "Loop agents." `LoopAgent` runs its sub-agents repeatedly; an `exit_loop` tool, typically given to a critic or refiner sub-agent, sets an escalate flag the runtime reads to stop the loop. There is no default iteration cap: without an explicit `max_iterations`, the loop runs until a sub-agent escalates, so the ceiling is something you supply. <https://adk.dev/agents/workflow-agents/loop-agents/>
[^crewai]: CrewAI, "Tasks" docs. Task-level guardrails validate output before it passes to the next task; `guardrail_max_retries` controls retry attempts on failure, and the older `max_retries` attribute is deprecated in its favour. Re-confirm against the version you install. <https://docs.crewai.com/en/concepts/tasks>
[^dspy]: DSPy, `Refine` and `BestOfN` module docs. `Refine` runs a module up to N times with generated feedback between attempts, stopping on a reward threshold or N attempts; `BestOfN` runs the same module N times with no feedback and keeps the highest-reward or first-passing result. <https://dspy.ai/api/modules/Refine/>, <https://dspy.ai/tutorials/output_refinement/best-of-n-and-refine/>

## See also

- [1.2 Who Decides?](../foundations/who-decides.md): the tell in one line ("it judges its own draft and loops"); this chapter is the full treatment.
- [2.2 Structured Output](../the-unit/structured-output.md): the typed verdict the loop routes on, and why `reasons` is part of the contract.
- [2.5 The Agent Loop](../the-unit/the-agent-loop.md): the write, execute, observe, fix cycle this chapter names as self-correction with an external signal.
- [3.1 Prompt Chaining](prompt-chaining.md): a chain's gate is a code check with a fixed retry behind it, which is the smaller version of the same seam.
- [3.3 Orchestrator-Workers](fan-out.md): a synthesizer that grades its own reconciliation and goes round again has become this loop.
- [3.5 The Specialist Panel](specialist-panel.md): fixed personas judging one input once, with no revision round.
- [3.7 The Outer Loop](the-outer-loop.md): the same shape with a deterministic verifier behind it, where your code owns the stop condition. The heaviest link on this page.
- [4.2 Evaluation](../craft/proving-it-works.md): judge validity, judge-human agreement, and how to tell whether your evaluator is measuring anything.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md): where a capped, still-failing run should land.
- [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md): reject or redact with no revision round, the lighter cousin of this pattern.
- [5.4 Compaction](../knowledge/compaction-and-the-window.md): what crosses forward each round, so cost does not compound with iteration count.
- [8.3 To Train or to Prompt](../production/train-or-prompt.md): Constitutional AI and RLAIF, the same critique-and-revise idea moved to training time.
- [8.4 Controlling Cost](../production/controlling-cost.md): the per-iteration multiplier in the wider economics.
- [9.2 Multi-Agent](../frontier/more-than-one-agent.md): debate, correlated judgment, and multi-agent review, which this chapter deliberately stays out of.
- [9.7 Self-Improving Systems](../frontier/self-improving-systems.md): loops that rewrite the prompt or the tool rather than the artifact, a riskier animal.

## Further reading

- Anthropic, ["Building Effective Agents"](https://www.anthropic.com/research/building-effective-agents) (2024-12-19): the primary definition of the workflow and the criteria under which it pays off.
- Huang et al., ["Large Language Models Cannot Self-Correct Reasoning Yet"](https://arxiv.org/abs/2310.01798) (ICLR 2024): the best skeptical read, and the paper that sets the ceiling this chapter argues around.
- Madaan et al., ["Self-Refine"](https://arxiv.org/abs/2303.17651) (NeurIPS 2023): the founding inference-time result, with the prompts and the task-by-task breakdown.
- Gou et al., ["CRITIC"](https://arxiv.org/abs/2305.11738) (ICLR 2024): the constructive answer, an evaluator that calls tools instead of introspecting.
- Zheng et al., ["Judging LLM-as-a-Judge"](https://arxiv.org/abs/2306.05685) (NeurIPS 2023): read this before trusting any judge you did not validate.
- OpenAI, [`llm_as_a_judge.py`](https://github.com/openai/openai-agents-python/blob/main/examples/agent_patterns/llm_as_a_judge.py): this chapter's shape as runnable code you can clone and step through.
