# 3.1 Prompt Chaining

*Why not one big prompt: split the task into a fixed sequence of model calls, because a single call cannot reliably hold the whole thing, and let your code own the order and gate what crosses between steps.*

*Also called: prompt pipelines, sequential workflows.*

## Why you'd reach for it

The failure that costs you most in a multi-step pipeline is the one that never fails.

Ask a single model call to do five jobs at once (categorize a product, describe it, list its
features, set a price, polish the voice) and every answer comes back a little worse than it would
have from a prompt doing one job. That is the cheap problem, and you can see it. The expensive one
is invisible. The model gets something wrong early, treats its own wrong answer as settled, and
builds everything downstream on top of it. Nothing raises. No request fails. The output just
drifts further from the truth as the window fills, and no code is positioned to notice.
[1.5 Context Engineering](../foundations/context-engineering.md) covers that degradation in depth.

Take a product-listing pipeline, the kind that turns a supplier's raw spreadsheet into a finished
storefront page: it categorizes each product, writes the copy, builds the page sections, runs
compliance checks, and publishes. Suppose the categorize job, buried inside the one big prompt,
files a sit-stand desk somewhere outside `office/desks/standing-desks`. Nothing errors. The copy
gets written for the wrong shelf, the page sections answer the questions a different shopper would
ask, the compliance checks run against another category's rules, and the listing goes live where
nobody shopping for a standing desk will ever see it. Caught between steps, that mistake costs one
extra model call. Caught after publish, it costs a mislisted product, the sales it does not make
while it sits there, and a piece of the team's willingness to trust the pipeline at all.

Prompt chaining splits the work at the seams where your code can check it. Categorize becomes its
own call, and its one-field output gets validated against the real taxonomy before the copy call
runs at all. A failed check re-asks that step once with the validation error folded in; a second
failure stops the run loudly, at the step that broke.

![A conveyor-belt illustration of the gated chain: a categorize station reads the supplier spreadsheet, a gate checks that the category exists, a failed check loops back for one re-ask or drops to a loud abort, and only a small card carrying sku, title, and category rides forward to the write-copy station.](prompt-chaining-flow.jpg)

Reach for a chain when:

- the task decomposes into fixed subtasks you can name before the run;
- the intermediate outputs are checkable by code: a path that must exist in a taxonomy, a price
  against a floor, an object against a schema;
- the pipeline runs unattended, so it has to fail predictably rather than creatively.

If the model has to decide what happens next at runtime, you want the agent loop instead. And when
the subtasks are so entangled that no intermediate output means anything on its own, a chain adds
round trips without adding a usable checkpoint; the Gotchas cover that case.

## What it actually is

Prompt chaining is a task decomposed into an ordered sequence of model calls, where each call
processes the previous call's output, your code fixes the order before the run, and a programmatic
check between steps decides what is allowed to cross. Anthropic's guide, which named the pattern,
describes it as decomposing "a task into a sequence of steps, where each LLM call processes the
output of the previous one", and calls it "ideal for situations where the task can be easily and
cleanly decomposed into fixed subtasks".[^anthropic] OpenAI's guide does not name the pattern but
defines the same category: "A workflow is a sequence of steps that must be executed to meet the
user's goal."[^openai-guide] Each step is the augmented LLM of
[1.4 The Augmented LLM](../foundations/the-augmented-llm.md), one model call with its contract,
doing one job.

That definition can be repeated fluently without being understood, which is what I discovered the
first time I tried to explain the pattern out loud and heard myself waving at a row of boxes. So
look at the join itself. Call 1 asks for a category and answers `"office/desks/standing-desks"`.
Your code checks that string against the taxonomy, then pastes it into the text of prompt 2. Prompt
2 now contains a substring that call 1 produced. That splice is the link the name refers to, and a
chain of them is a chain of prompts, each one built partly out of the previous answer.

Two things follow. Prompt 2 cannot be written until call 1 has answered, because it has a hole in
it shaped like call 1's output. And nothing fills that hole except an answer, so an early wrong
turn does not stop the run. It gets pasted in, and every step after it works from a premise nobody
checked.

Structurally there is nothing new here. A pipeline of steps with validation between them is how
batch systems have been built for decades, and your code decides the sequence, which is what keeps
chaining off the list of genuinely new patterns. What is new is the *reason* you split. You are
not splitting for modularity, or reuse, or team boundaries. You are splitting
because a single model call cannot reliably hold the whole task: attention thins as the window
fills, an early wrong turn compounds silently, and only a boundary between calls gives your code
somewhere to stand. Put no check on that boundary and you have paid for an extra round trip and
bought nothing.

Reach for the gated sequence without much debate. It is the default workflow shape in both
vendors' guides, along with the explicit trade they describe, "to trade off latency for higher
accuracy, by making each LLM call an easier task",[^anthropic][^openai-guide] and the idea
predates the agentic vocabulary. AI Chains, a CHI 2022 paper, showed that chaining prompts into
inspectable, editable intermediate steps improved task outcomes and users' sense of transparency
and control in a 20-person study,[^aichains] and least-to-most prompting, which solves decomposed
subproblems in sequence and feeds each one the previous answer, beat chain-of-thought on
compositional generalization.[^l2m] What is not settled is everything built above a simple gate.
Consensus and resampling schemes across steps are still emerging, and the reflex to decompose
maximally is disputed outright; the Gotchas cover both.

Two neighbours get confused with this one, and both confusions import assumptions that do not
hold. **Chain-of-thought** is one model call reasoning stepwise inside a single response;[^cot] a
chain is multiple discrete calls, each a full round trip, with your code inspecting what crosses
each boundary. Inside one response there is no gate, no external state, and no added per-step
latency or cost. A chain has all three. **Evaluator-optimizer** differs on who decides whether to
run another round. In a chain your code decides: it advances when a deterministic check passes,
and on failure it re-runs a fixed number of times, then stops. In
[3.4 Evaluator-Optimizer](evaluator-optimizer.md) the model decides, grading its own output
against a quality bar and revising until the grade clears or a cap intervenes, so the iteration
count is not fixed in the code. The gate makes the same distinction at smaller scale. A plain code
check keeps you in chaining; a model grading the output crosses over only when its verdict drives
an open-ended revise-until-good loop rather than a single pass or fail. Two-pass generation, draft
then rewrite once in a fixed second call, stays on the chaining side, because that second pass is
unconditional.

A chain sits at the far end of a control spectrum from the agent loop. The chain fixes its
sequence in code before the run; a loop hands that decision to the model, which chooses its next
action each turn and runs until an exit condition stops it.[^openai-guide] For an unattended
production pipeline the chain wins, and the reasons are unglamorous: predictable cost and latency,
a gate at every boundary, per-step debuggability, and clean resumability. Because each gate hands
the next step a small validated state, a run that dies at step six restarts from step six on that
state; a loop keeps its state as one evolving transcript, with no equally clean place to resume
from. The loop wins when the shape of the task is unknown before the run starts.
[1.3 Workflow or Agent?](../foundations/workflow-or-agent.md) owns the full spectrum;
[9.1 Autonomous Agents](../frontier/when-you-want-autonomy.md) owns the loop.

## How to do it

The example is the seam from the story above, categorize feeding write-copy, and here is one run of
it in the reference's visual language. Rectangles are your code deciding, rounded boxes are the
model deciding, dashed boxes are data in flight. The string leaving the gate and landing in the
empty slot in prompt 2 is the splice.

![An animated schematic of two model calls side by side. Call 1 holds prompt 1, a model, and response 1. Its response names a category that does not exist, so your code's gate rejects it against the three-item catalog taxonomy shown underneath and sends it back to be re-asked with the rejection appended to the same prompt. The second answer passes the gate, and the validated category value then flies into an empty slot in prompt 2, which stays dimmed and unbuildable until it arrives.](prompt-chaining-flow.svg)

Each step's output is a typed contract, the capability from
[2.2 Structured Output](../the-unit/structured-output.md) doing inter-step duty:

```python
class CategoryDecision(BaseModel):
    """Step 3 (categorize) output: where the product belongs in the taxonomy."""
    model_config = ConfigDict(extra="forbid")

    category_path: str  # e.g. "office/desks/standing-desks"
    confidence: float    # 0.0-1.0; the model's stated confidence


class CopyDraft(BaseModel):
    """Step 4 (write copy) output: the drafted listing copy for one product."""
    model_config = ConfigDict(extra="forbid")

    description: str
    bullets: list[str]
```

Between the two calls sits what Anthropic's diagram calls a gate: a programmatic check on an
intermediate step, confirming the process is on track before the next call runs.[^anthropic] This
one checks what the schema cannot. A schema validates that `category_path` is a string; the gate
validates that the string names a category that exists.

```python
@dataclass
class GateResult:
    ok: bool
    error: str | None = None  # structured message for the re-ask prompt if not ok


def validate_category(decision: CategoryDecision) -> GateResult:
    """category_path must be a real node in the catalog taxonomy."""
    if decision.category_path not in TAXONOMY:
        return GateResult(
            ok=False,
            error=(
                f"category_path {decision.category_path!r} is not in the "
                f"catalog taxonomy. Choose one of: {sorted(TAXONOMY)}."
            ),
        )
    return GateResult(ok=True)
```

The chain itself is plain sequential code. Read it for two decisions: what happens when the gate
fails, and how little crosses when it passes.

```python
def run_chain(
    categorize_fn: Any,  # callable(messages) -> CategoryDecision
    write_copy_fn: Any,  # callable(messages) -> CopyDraft
    supplier_sku: str,
    title: str,
) -> CopyDraft:
    """Categorize, gate, then write copy -- in that fixed order."""
    messages = [
        {"role": "user", "content": f"Categorize {title} (SKU {supplier_sku})."}
    ]
    decision = categorize_fn(messages)
    gate = validate_category(decision)

    if not gate.ok:
        messages.append({"role": "user", "content": f"Invalid category: {gate.error}"})
        decision = categorize_fn(messages)
        gate = validate_category(decision)

    if not gate.ok:
        raise RuntimeError(f"categorize step failed its gate twice: {gate.error}")

    # Only the validated category_path crosses the gate -- not the transcript.
    copy_messages = [
        {
            "role": "user",
            "content": (
                f"Write listing copy for {title} (SKU {supplier_sku}) "
                f"in category {decision.category_path}."
            ),
        }
    ]
    return write_copy_fn(copy_messages)
```

One run on the desk, end to end:

1. Your code sends the categorize prompt: "Categorize Aldsworth Dual-Motor Sit-Stand Desk (SKU
   NV-ALDSWORTH-DM)."
2. The model returns a schema-valid `CategoryDecision` whose `category_path` is
   `"furniture/desks/sit-stand"`. The shape is right. The path does not exist.
3. The gate rejects it and `run_chain` re-asks the same step, folding the structured error into
   the message along with the valid paths. That is the same splice pointed backwards: the answer
   becoming text in its own prompt.
4. The model returns `"office/desks/standing-desks"`, and the gate passes.
5. Your code forwards `supplier_sku`, `title`, and the validated `category_path` into the copy
   prompt. The categorize transcript and the rejected first attempt stay behind.
6. The copy call drafts `description` and `bullets` for a standing desk, and the chain returns a
   typed `CopyDraft`.

Step 2 is the one to sit with. `"furniture/desks/sit-stand"` is well-formed, sensible English, and
a perfectly good string for that field. It is wrong only because the catalog has no such shelf, and
no schema will ever tell you that. Neither would you, reading it, without the taxonomy open beside
it, which is the position your code is in at every step boundary.

Two things change at production scale. **The model choice decouples per step.** Categorize is an
easy classification and runs fine on a small, cheap model; a brand-voice polish near the end of a
pipeline is where a strong model earns its price ([8.2 Which Model?](../production/which-model.md)).
**The retry budget multiplies.** `run_chain` re-asks a failed step exactly once, then aborts, which
is deliberately tighter than the bounded re-ask loop in
[2.2 Structured Output](../the-unit/structured-output.md). Every retry here is a full model call
with its own latency and cost, and whatever budget you allow gets multiplied by the number of
steps. One re-ask catches the transient miss. A second failure on the same gate is evidence of
something retries will not fix: a bad prompt, a gap in the taxonomy, a step that needs a person.
In a batch run, scope the abort. Set the failed SKU aside for a human and keep the rest of the feed
moving, since the products in a feed are independent and a worker pool can run their chains
concurrently even though each product's chain is serial.

> **In Listing Studio.** The nine-step pipeline, ingest through publish, is this pattern at the top
> level: your code fixes the order, and each step hands a more complete listing to the next. The
> categorize-to-copy seam shown above repeats at every step boundary, and every added step is
> another chance for a quiet wrong turn to become a premise for everything after it.

#### Wiring it to a provider

The LangGraph tab shows the whole graph, since the sequential graph is the reference shape for a
chain.[^langgraph] The two raw-SDK tabs define only the step functions and hand them to the shared,
tested `run_chain` above. How you word each step's prompt belongs to
[4.1 Prompt Management](../craft/prompts-are-source-code.md).

=== "LangGraph"

    ```python
    class ChainState(TypedDict):
        supplier_sku: str
        title: str
        category: Optional[CategoryDecision]
        category_error: Optional[str]  # the gate's structured error, fed back on retry
        attempt: int                   # how many times categorize has run
        copy: Optional[CopyDraft]


    def categorize_node(state: ChainState) -> dict:
        """Step 3 (categorize), gated immediately after the call."""
        prompt = f"Categorize {state['title']} (SKU {state['supplier_sku']})."
        if state.get("category_error"):
            prompt += f" Previous attempt was rejected: {state['category_error']}"
        decision = categorize_chain.invoke(prompt)
        gate = validate_category(decision)
        return {
            "category": decision,
            "category_error": gate.error,
            "attempt": state.get("attempt", 0) + 1,
        }


    def route_after_gate(state: ChainState) -> str:
        """continue, retry once, or abort."""
        if state["category_error"] is None:
            return "continue"
        if state["attempt"] < 2:
            return "retry"
        return "abort"


    def abort_node(state: ChainState) -> dict:
        """The retry also failed: abort loudly."""
        raise RuntimeError(
            f"categorize step failed its gate twice: {state['category_error']}"
        )


    def write_copy_node(state: ChainState) -> dict:
        """Step 4 (write copy): only the validated category_path crosses the gate."""
        decision = state["category"]
        draft = write_copy_chain.invoke(
            f"Write listing copy for {state['title']} (SKU {state['supplier_sku']}) "
            f"in category {decision.category_path}."
        )
        return {"copy": draft}


    builder = StateGraph(ChainState)
    builder.add_node("categorize", categorize_node)
    builder.add_node("write_copy", write_copy_node)
    builder.add_node("abort", abort_node)
    builder.add_edge(START, "categorize")
    builder.add_conditional_edges(
        "categorize",
        route_after_gate,
        {"continue": "write_copy", "retry": "categorize", "abort": "abort"},
    )
    builder.add_edge("write_copy", END)
    builder.add_edge("abort", END)
    chain = builder.compile()

    result = chain.invoke(
        {"supplier_sku": "NV-ALDSWORTH-DM", "title": "Aldsworth Dual-Motor Sit-Stand Desk"}
    )
    print(result["copy"].description)
    ```

=== "OpenAI Responses API"

    ```python
    def categorize_fn(messages: list[dict]) -> CategoryDecision:
        response = client.responses.create(
            model="gpt-5.5",
            input=messages,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "CategoryDecision",
                    "schema": CategoryDecision.model_json_schema(),
                    "strict": True,
                }
            },
        )
        return CategoryDecision.model_validate_json(response.output_text)


    def write_copy_fn(messages: list[dict]) -> CopyDraft:
        response = client.responses.create(
            model="gpt-5.5",
            input=messages,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "CopyDraft",
                    "schema": CopyDraft.model_json_schema(),
                    "strict": True,
                }
            },
        )
        return CopyDraft.model_validate_json(response.output_text)


    copy = run_chain(
        categorize_fn,
        write_copy_fn,
        supplier_sku="NV-ALDSWORTH-DM",
        title="Aldsworth Dual-Motor Sit-Stand Desk",
    )
    print(copy.description)
    ```

=== "Anthropic Messages API"

    ```python
    def categorize_fn(messages: list[dict]) -> CategoryDecision:
        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=[_CATEGORY_TOOL],
            tool_choice={"type": "tool", "name": "produce_category_decision"},
            messages=messages,
        )
        tool_block = next(b for b in reply.content if b.type == "tool_use")
        return CategoryDecision.model_validate(tool_block.input)


    def write_copy_fn(messages: list[dict]) -> CopyDraft:
        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=[_COPY_TOOL],
            tool_choice={"type": "tool", "name": "produce_copy_draft"},
            messages=messages,
        )
        tool_block = next(b for b in reply.content if b.type == "tool_use")
        return CopyDraft.model_validate(tool_block.input)


    copy = run_chain(
        categorize_fn,
        write_copy_fn,
        supplier_sku="NV-ALDSWORTH-DM",
        title="Aldsworth Dual-Motor Sit-Stand Desk",
    )
    print(copy.description)
    ```

## Gotchas

**Errors compound multiplicatively.** With independent per-step failure, end-to-end reliability is
the product of the steps, and that product decays fast. As arithmetic rather than measurement: a
step that is right 99 percent of the time gives you roughly 90 percent end to end across ten steps,
and roughly 37 percent across a hundred. An industry preprint derives the same shape and argues
that per-step reliability has to be engineered well past "usually right" before long chains are
viable.[^sixsigma] The gate is what stops that decay from being silent. Without one, step nine
operates at whatever error the first eight accumulated.

**A silent gate is worse than no gate.** A failed check has to come back as a structured,
recoverable signal: re-ask the step with the validation error, route to a person where a retry is
the wrong tool ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md)), or abort the run loudly. A
gate that logs the failure and passes the object through anyway, or dies in a raw exception nothing
catches, has spent a round trip to change nothing.

**Do not forward the transcript.** What crosses a gate is a context-budget decision. Each step
should get a window curated for its job, and the lazy alternative, appending every prior step's
output and shipping the pile forward, quietly rebuilds the mega-prompt you split to escape, now
spread across more calls. The pile costs tokens and drains attention from the input the step
actually needs. [1.5 Context Engineering](../foundations/context-engineering.md) owns the depth
here, along with [5.4 Compaction](../knowledge/compaction-and-the-window.md).

**Every step is a full round trip.** More calls means more latency and more spend. The vendor
framing trades latency for accuracy,[^anthropic] and that trade is wrong in two common places:
user-facing surfaces with an interactive latency budget, where three serial calls blow a budget one
call fits inside, and steps a model already does reliably in one shot, where the extra hop buys
nothing.

**Over-decomposition is its own anti-pattern.** Ten tiny steps are not safer than four substantial
ones. Each split adds a round trip, a gate that can misfire, and a boundary needing curated
context, so past the point where each step is already easy for the model, splitting further adds
cost and failure surface with no reliability gain. Splitting hurts outright when subtasks are
entangled: a 2025 preprint models the trade as competing noise sources and finds that chunking
long-context work helps when per-call degradation dominates and hurts when cross-chunk dependency
dominates.[^noise] Growing context windows move this boundary too, weakening the case for splitting
short tasks without erasing it for long ones. "Decompose maximally, always" is a habit worth
distrusting, and the [Anti-Patterns Catalog](../catalogs/anti-patterns.md) files it.

> **From production.** The pipeline I shipped this on reports every step's success or failure to an
> orchestrating service, so a failure arrives already labelled with the step that produced it, and a person can
> fix the input and re-trigger from there instead of replaying the whole run. What it does not have
> is a content gate between steps. Each step judges whether it finished, not whether what it
> produced is true, and that gap is exactly where a wrong category rides through unchallenged. The
> taxonomy check above is the gate I would add to that baseline, and the one I would argue for
> first.

## In short

Chain when the task decomposes into fixed, code-checkable subtasks and the pipeline has to run
unattended and fail predictably. Gate every boundary, and make a gate failure structured and loud:
re-ask once with the error, then abort or escalate, and never pass an unvalidated object forward.
Forward the minimum the next step needs, because the transcript is dead weight. Expect to pay a
round trip per step, and prune steps that stop earning their gate. If the model has to decide what
happens next, you have left this pattern and want an agent loop. The gated sequence is safe to
reach for; treat everything above it, consensus schemes, resampling across steps, frameworks that
predict when to decompose, as still settling.

<small class="chapter-meta">**Maturity: Standard** (the gated sequence is vendor guidance's default workflow shape; the fixes beyond a simple gate are still settling) · *Who decides:* your code · *Grounding:* production + research · *Last reviewed:* 2026-07</small>

## Sources

[^anthropic]: Anthropic, "Building Effective Agents" (2024-12-19). The pattern definition ("decomposes a task into a sequence of steps, where each LLM call processes the output of the previous one"), the programmatic "gate" on intermediate steps, and the stated trade ("trade off latency for higher accuracy, by making each LLM call an easier task"). <https://www.anthropic.com/research/building-effective-agents>
[^openai-guide]: OpenAI, "A Practical Guide to Building Agents" (April 2025), pp. 4 and 14, for the workflow definition and the run-loop framing. The guide describes the loop as "a 'run', typically implemented as a loop that lets agents operate until an exit condition is reached", with exit conditions including tool calls, a structured output, errors, or a maximum number of turns. It also holds that applications integrating LLMs without letting them control workflow execution are not agents. <https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/>
[^aichains]: Wu, T., Terry, M., and Cai, C. J., "AI Chains: Transparent and Controllable Human-AI Interaction by Chaining Large Language Model Prompts," CHI 2022. <https://doi.org/10.1145/3491102.3517582>
[^l2m]: Zhou, D., et al., "Least-to-Most Prompting Enables Complex Reasoning in Large Language Models" (2022). <https://arxiv.org/abs/2205.10625>
[^cot]: Wei, J., et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (2022). <https://arxiv.org/abs/2201.11903>
[^sixsigma]: Patel et al. (Lyzr Research), "The Six Sigma Agent" (2026). Non-peer-reviewed preprint; cited for the compounding-error shape, not as settled authority. <https://arxiv.org/abs/2601.22290>
[^noise]: Xu et al., "When Does Divide and Conquer Work for Long Context LLM? A Noise Decomposition Framework" (2025). Preprint; the chunking-helps-versus-hurts framework is a lens rather than settled guidance. <https://arxiv.org/abs/2506.16411>
[^langgraph]: LangChain, "Workflows and agents" (LangGraph docs). The reference sequential-graph shape: nodes, edges, `StateGraph`. <https://docs.langchain.com/oss/python/langgraph/workflows-agents>

## See also

- [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md): the spectrum this pattern sits at the workflow end of, and the longer answer to "chain or loop?"
- [1.5 Context Engineering](../foundations/context-engineering.md): what to carry across the gate and what to leave behind, the depth behind "do not forward the transcript."
- [2.2 Structured Output](../the-unit/structured-output.md): the typed contract each gate validates, and the re-ask-with-structured-error shape this chapter's gate reuses at the step boundary.
- [3.2 Routing & Dispatch](the-router-that-isnt.md): conditional branching between steps is routing, not chaining; a chain that picks its next step from a classifier is that chapter's pattern in a chain's clothes.
- [3.3 Orchestrator-Workers](fan-out.md): where steps have no ordering dependency, fan them out in parallel instead of chaining them.
- [3.4 Evaluator-Optimizer](evaluator-optimizer.md): the model judging its own output and deciding whether to loop, the genuinely new sibling this pattern gets mistaken for.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md): the gate failure that needs a person rather than a retry.
- [9.1 Autonomous Agents](../frontier/when-you-want-autonomy.md): the agent loop in depth, the other end of the comparison above.
