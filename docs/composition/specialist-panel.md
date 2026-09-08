# 3.5 The Specialist Panel

*Several expert viewpoints over one input, each in its own model call with its own narrow brief, merged by a step that keeps the disagreement visible instead of averaging it away. Whether your code fixes that roster or something picks it per input separates two patterns that share the name.*

## Why you'd reach for it

Ask a single model call to write a product page that is discoverable, priced within the rules, and legally safe, and you get back something that reads like all three. It fails by omission. The required warning is not wrong, it is absent, and nothing in the output marks the gap: no error, no lowered confidence, just a fluent page with a hole in it.

That happens whenever one call has to satisfy several concerns that pull against each other. Nothing in the prompt says which one gives way, so the model settles it inside a single pass of generation, silently, and your only detector is a person who remembers what should have been there.

Take Listing Studio, a pipeline that turns a raw supplier feed into a live storefront listing for Stockwell, a mid-market commerce platform. Its fifth step writes the page's content blocks: hero, specs, FAQ. On the Aldsworth desk, an MDF-topped sit-stand model, the FAQ block is contested ground. Discoverability wants the phrasing shoppers search for. Compliance requires the Prop 65 warning (California's chemical-exposure notice, triggered here by the formaldehyde in that top) and forbids overstating the 250 lb weight capacity. Pricing needs wording that does not undercut the supplier's minimum advertised price (MAP). One call weighing all three writes a good-looking FAQ that drops the warning, and the desk either gets caught by a merchandiser or publishes without a required disclosure.

The fix is to stop asking one call to hold three jobs. Run each concern as its own call with a brief scoped tightly enough to resist drift, have each return typed claims rather than a paragraph, and merge the claims in a step you wrote. Who names the seats is the question underneath: your code, the same roster every time, or a step that reads the input and picks the lenses it calls for. The harder half arrives immediately: the published evidence on persona prompts is thin and partly negative, and the extra calls are real money.

Reach for a panel when:

- several concerns pull against each other over one output, and you want the trade-off auditable;
- the concerns are separable, each judgeable without a sibling's output in hand (concerns that feed each other belong to [3.1 Prompt Chaining](prompt-chaining.md));
- the failure you fear is omission, so you want a viewpoint whose only job is noticing what is missing;
- you can name the viewpoints at author time and say in advance which one outranks which.

The counter-trigger is the baseline you have to beat: one well-scoped prompt naming every concern and returning a typed answer. Until you run it, you do not know the panel earned anything.

## What it actually is

A specialist panel hands the same input to several model calls at once, each carrying a different professional viewpoint and a brief scoped to it, then merges their outputs into one decision through a reconcile step. The personas are prompts, the parallelism is ordinary concurrency, and the merge is where you decide what a disagreement means.

![The same panel step drawn twice, with a count of the seats that actually ran. In the first lane your code decided: an Aldsworth desk and a phone case both feed one rectangle holding the literal roster of seo, pricing and compliance, and three seats run for either product, an SEO specialist on search terms, a pricing analyst on MAP and margin, and a compliance reviewer on warnings. The count reads three. In the second lane the model decides which lenses this product calls for before any seat runs. The desk, carrying a Prop 65 warning and a MAP price floor, gets all three seats and a count of three. The phone case, with no compliance regime and no price floor, gets the SEO seat only, and the pricing and compliance seats are drawn as empty dashed outlines marked not selected, for a count of one. Either way the seats that ran feed one rectangle marked reconcile, in your code, which ranks compliance over pricing over seo and emits three named outputs: accepted, rejected, and conflict.](specialist-panel-seats.svg)

Two different mechanisms answer to that description, and only one changes what the program does. In the first, the roster is a list in your code, and the branch count was fixed the day someone typed it. Anthropic's guide already names that shape: voting, one of its two Parallelization variants (the other, sectioning, splits a task into different pieces), "running the same task multiple times to get diverse outputs," instanced by several different prompts reviewing one piece of code from different angles.[^anthropic-bea] In the second, something reads the input first and decides which of a small named set of viewpoints this input calls for, before any of them runs. The branch count becomes a property of the input, and a phone case with no compliance regime and no price floor runs a shorter panel. It also fails in a new way, because skipping the compliance seat on a product that needed one puts the omission back, a step earlier.

The line between them is checkable in a minute. Run two different products through the step and count the specialists. If the count never changes, the roster is your code's, and the word "specialist" is doing no work that "three prompts" would not do just as honestly.

Only the second mechanism has direct published evidence, and less of it than you would want. Solo Performance Prompting is the closest: given a task it "first generates a list of participants with different personas," letting "the language model identify the personas dynamically instead of manually defining them."[^spp] That is input-conditioned selection, demonstrated. It is also sequential turns inside one context rather than parallel calls, over an open vocabulary the model invents rather than a fixed named set, and the paper reports that the benefit "only emerges in GPT-4."[^spp] Reading it as support for a parallel, fixed-vocabulary panel is an extrapolation, and no vendor names that workflow.

Concurrent model calls with a merge step are Standard: scatter-gather across a worker pool is decades old. Two narrower things are Emerging. Deciding per input which viewpoints apply rests on that one paper alone.[^spp] Heterogeneous-model synthesis is the other: Mixture-of-Agents runs different models as proposers and has an LLM aggregator synthesize them, reporting that it "significantly outperforms LLM rankers."[^moa] Its own ablation points away from personas: sampling one model repeatedly loses to using several different ones.[^moa]

Contested is the claim the pattern is usually sold on. Zheng and colleagues tested 162 roles across 2,410 factual questions and four model families and found that adding a persona to the system prompt yields no accuracy gain on fact-based question answering, and that most personas have no effect or a negative one.[^persona-null] The debate literature agrees from another direction: debating does not reliably beat self-consistency once baselines are tuned fairly,[^mad-limits] and a 2025 study across nine benchmarks found debate often losing to single-agent chain-of-thought at far higher cost, naming model heterogeneity rather than more personas as the fix.[^mad-heterogeneity] A panel can still be worth building, just not on the strength of the job titles.

Five independently varying axes separate this pattern from its neighbours: **membership** (a roster fixed at author time, or selected per input), **model diversity** (one model in several roles, or different models), **context** (isolated calls, or one shared context everyone reads and writes), **interaction** (a single pass each, or rounds of back-and-forth), and **aggregation** (a deterministic vote or rule, or generative synthesis by a model).

Self-consistency samples one prompt many times and takes the most common answer, varying none of them.[^selfconsistency] Mixture-of-Agents moves one axis, model diversity.[^moa] Debate, where agents read each other's answers and revise over rounds, moves two: context and interaction.[^debate][^divergent] Solo Performance Prompting moves membership, per task.[^spp] A panel-of-judges, several small models scoring one output between them, moves diversity and aggregation.[^poll] The panel in the code below moves nothing: fixed, homogeneous, isolated, single-pass, merged by a rule.

Three siblings get mistaken for a panel. [3.2 Routing & Dispatch](the-router-that-isnt.md) picks one mutually exclusive category and sends the input down a single path; a panel admits several viewpoints at once and chooses between no paths at all. [3.3 Orchestrator-Workers](fan-out.md) has a model decide how many pieces an open-ended task breaks into; a panel's viewpoints are named in advance, so even under per-input selection the question is which of N known lenses to turn on. [3.4 Evaluator-Optimizer](evaluator-optimizer.md) loops one draft against a verdict; a panel judges once and never revises. Both Gulli books and Ng's four-pattern list file this under multi-agent collaboration, far broader than this single-pass shape.[^gulli-adp][^ng]

## How to do it

Each persona call is one instance of [1.4 The Augmented LLM](../foundations/the-augmented-llm.md), one model call against a typed state contract, wearing a different hat each time. A persona that returns a paragraph gives the merge nothing to work with, so each returns typed claims: a field, a value, a rationale. The `field` is a dotted path into the listing record, so the merge matches personas by field rather than by prose ([2.2 Structured Output](../the-unit/structured-output.md)).

<details markdown><summary>The typed contract: what each persona returns, and what the reconciler emits (<code>specialist_panel/schemas.py</code>)</summary>

```python
class PersonaClaim(BaseModel):
    """One specialist's proposed value for one field, and why. `field` is
    a dotted path into the Listing (e.g. "content_blocks.faq"), never free
    text -- the reconciler matches claims by field, not by prose."""
    model_config = ConfigDict(extra="forbid")

    field: str
    value: str
    rationale: str


class PersonaVerdict(BaseModel):
    """One persona's full opinion on this listing: a name from the fixed
    roster, and zero or more typed claims -- never a paragraph."""
    model_config = ConfigDict(extra="forbid")

    persona: str
    claims: list[PersonaClaim]


class AcceptedClaim(BaseModel):
    """A claim the reconciler kept, and which persona it came from."""
    model_config = ConfigDict(extra="forbid")

    field: str
    value: str
    source_persona: str


class RejectedClaim(BaseModel):
    """A claim the reconciler dropped, and the reason it lost -- never a
    silent omission."""
    model_config = ConfigDict(extra="forbid")

    field: str
    value: str
    source_persona: str
    reason: str


class Conflict(BaseModel):
    """Two or more personas claimed the same field with different values.
    `winner` names the persona whose claim survived and `rule` names what
    decided it -- the reconciler never blends the values into one averaged
    answer."""
    model_config = ConfigDict(extra="forbid")

    field: str
    dissenting_personas: list[str]
    winner: str
    rule: str


class MissingSpecialist(BaseModel):
    """A persona call that errored, timed out, or returned nothing --
    reported as a structured absence, never a silent gap in the panel."""
    model_config = ConfigDict(extra="forbid")

    persona: str
    reason: str


class PanelDecision(BaseModel):
    """The reconciler's typed output: what survived, what didn't and why,
    every conflict with its resolution, every specialist that didn't
    answer, and whether a human needs to see this before it ships."""
    model_config = ConfigDict(extra="forbid")

    accepted: list[AcceptedClaim]
    rejected: list[RejectedClaim]
    conflicts: list[Conflict]
    missing: list[MissingSpecialist]
    escalate: bool
```

</details>

`PanelDecision` is the discipline in one object: what lost, what was contested, what never answered, each with its reason attached, and `escalate` as a boolean a caller can act on.

The fan-out itself is unremarkable. `ROSTER` is a plain Python list, three names long, and the model is never asked who belongs on it. Each persona runs in its own task, an exception becomes a `MissingSpecialist` rather than taking the other two down, and every attempt is charged to a per-persona `CallStats` on the result object.

<details markdown><summary>The fixed roster, run concurrently, with per-persona cost on the result (<code>specialist_panel/roster.py</code>)</summary>

```python
ROSTER: list[str] = ["seo", "pricing", "compliance"]


def _approx_tokens(text: str) -> int:
    """A rough proxy (~4 chars/token, the common estimate), not a
    provider's real usage report -- swap in the provider's own usage field
    once a variant is wired to a live API."""
    return max(1, len(text) // 4)


@dataclass
class CallStats:
    """What the panel actually cost, per persona -- visible on the
    returned object, never hidden in a log line only ops can see."""
    calls: dict[str, int] = field(default_factory=dict)
    tokens: dict[str, int] = field(default_factory=dict)

    @property
    def total_calls(self) -> int:
        return sum(self.calls.values())

    @property
    def total_tokens(self) -> int:
        return sum(self.tokens.values())


@dataclass
class PanelRun:
    verdicts: dict[str, PersonaVerdict]
    missing: list[MissingSpecialist]
    cost: CallStats


def _call_persona_safe(
    persona_fn: Any, persona: str, listing: dict, cost: CallStats
) -> PersonaVerdict | None:
    """Run one persona and turn any exception into `None`. The attempt is
    charged to `cost` either way -- a call that fails still cost
    something -- and run_panel() reports the absence as a
    MissingSpecialist, never as a raised exception that takes the other
    two personas down."""
    prompt = f"{persona} review of {listing.get('supplier_sku', 'this listing')}"
    cost.calls[persona] = cost.calls.get(persona, 0) + 1
    cost.tokens[persona] = cost.tokens.get(persona, 0) + _approx_tokens(prompt)
    try:
        verdict = persona_fn(persona, listing)
    except Exception:
        return None
    output = " ".join(f"{c.field} {c.value} {c.rationale}" for c in verdict.claims)
    cost.tokens[persona] += _approx_tokens(output)
    return verdict


async def _run_all(
    persona_fn: Any, listing: dict, cost: CallStats
) -> dict[str, PersonaVerdict | None]:
    results: dict[str, PersonaVerdict | None] = {}

    async def _one(persona: str) -> None:
        results[persona] = await anyio.to_thread.run_sync(
            _call_persona_safe, persona_fn, persona, listing, cost
        )

    async with anyio.create_task_group() as tg:
        for persona in ROSTER:
            tg.start_soon(_one, persona)
    return results


def run_panel(persona_fn: Any, listing: dict) -> PanelRun:
    """Run every persona in ROSTER concurrently over the same listing.

    persona_fn(persona, listing) -> PersonaVerdict is the seam the
    provider variants inject. A persona that raises or returns nothing
    usable is recorded in `missing`, never silently dropped from the
    panel -- reconcile() decides what a missing specialist means for the
    decision.
    """
    cost = CallStats()
    raw = anyio.run(_run_all, persona_fn, listing, cost)

    verdicts: dict[str, PersonaVerdict] = {}
    missing: list[MissingSpecialist] = []
    for persona, verdict in raw.items():
        if verdict is None:
            missing.append(MissingSpecialist(persona=persona, reason="call failed or timed out"))
        else:
            verdicts[persona] = verdict
    return PanelRun(verdicts=verdicts, missing=missing, cost=cost)
```

</details>

No framework hands you a typed merge with your precedence in it. Google's Agent Development Kit gives sub-agents isolated branches and no aggregator at all;[^adk-parallel] LangGraph's reducer and the OpenAI Agents SDK's manager agent give you a seam to write one into.[^oai-orchestration] Here it is pure code, with no model call. `PRECEDENCE` ranks compliance over pricing over discoverability, a ranking a person made once, in the open, for a stated reason. A conflict is settled by that ranking, never by blending two values into a third neither persona proposed, and both the losing claim and the conflict survive into the output. A missing compliance reviewer sets `escalate`: the panel does not rule in the absence of the specialist whose claim would have settled it. Precedence only decides which claim wins. A compliance seat that misread the material still takes the field.

```python
# Your code decided this order once, when it was written. On a field two
# personas both claimed, the earlier persona's value wins: compliance over
# pricing over discoverability, because a dropped disclosure costs more
# than a duller headline. PRECEDENCE must name every persona in ROSTER.
PRECEDENCE = ["compliance", "pricing", "seo"]

# A conflict escalates to a person when the persona whose claim would have
# settled it never answered -- the panel does not rule in a missing
# specialist's absence.
ESCALATE_ON_MISSING = {"compliance"}


def reconcile(
    verdicts: dict[str, PersonaVerdict], missing: list[MissingSpecialist]
) -> PanelDecision:
    """Merge typed verdicts into one typed decision, conflict intact.

    Two or more personas claiming the same field with different values is
    resolved by PRECEDENCE, never averaged: the losing claim lands in
    `rejected` with the rule that beat it, and the conflict itself lands in
    `conflicts` so a caller can see that it happened, not just its
    outcome.
    """
    by_field: dict[str, list[tuple[str, str]]] = {}
    for persona, verdict in verdicts.items():
        for claim in verdict.claims:
            by_field.setdefault(claim.field, []).append((persona, claim.value))

    accepted: list[AcceptedClaim] = []
    rejected: list[RejectedClaim] = []
    conflicts: list[Conflict] = []

    for field_name, claims in by_field.items():
        if len({value for _, value in claims}) == 1:
            # Every persona that touched this field agrees; nothing to
            # arbitrate.
            persona, value = claims[0]
            accepted.append(AcceptedClaim(field=field_name, value=value, source_persona=persona))
            continue

        ranked = sorted(claims, key=lambda c: PRECEDENCE.index(c[0]))
        winner_persona, winner_value = ranked[0]
        accepted.append(
            AcceptedClaim(field=field_name, value=winner_value, source_persona=winner_persona)
        )
        for persona, value in ranked[1:]:
            rejected.append(
                RejectedClaim(
                    field=field_name,
                    value=value,
                    source_persona=persona,
                    reason=f"overruled by {winner_persona} (precedence: {PRECEDENCE})",
                )
            )
        conflicts.append(
            Conflict(
                field=field_name,
                dissenting_personas=[p for p, _ in ranked[1:]],
                winner=winner_persona,
                rule="field-level precedence",
            )
        )

    missing_personas = {m.persona for m in missing}
    escalate = bool(missing_personas & ESCALATE_ON_MISSING)

    return PanelDecision(
        accepted=accepted, rejected=rejected, conflicts=conflicts,
        missing=missing, escalate=escalate,
    )
```

One run over the Aldsworth desk:

1. `run_panel` reads `ROSTER` and starts three calls at once, each getting the same listing and a brief naming only the fields its role covers.
2. The SEO call returns claims on `content_blocks.faq` and `title`. The compliance call returns one on `content_blocks.faq` carrying the Prop 65 line, and one capping the stated weight capacity.
3. The pricing call raises. `_call_persona_safe` turns it into `None`, the attempt is still charged, and `run_panel` records a `MissingSpecialist`. The other two results are untouched.
4. `reconcile` groups claims by field. `content_blocks.faq` holds two different values, so `PRECEDENCE` ranks compliance first: its value is accepted, the SEO value lands in `rejected` reading *overruled by compliance*, and a `Conflict` records the field, the dissenter, the winner, and the rule.
5. `ESCALATE_ON_MISSING` is `{"compliance"}`. Compliance answered, so `escalate` stays false and the block ships with its conflict on the record. If compliance had failed instead, the listing would go to a person ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md)) rather than publish on two thirds of a panel.
6. `cost.total_calls` reads 3 where a single prompt reads 1, and every seat read the listing in full to get there ([8.4 Controlling Cost](../production/controlling-cost.md)).

Did the extra calls buy anything? The companion code scores the panel and one well-scoped multi-criteria call by which fields each named.

<details markdown><summary>The ablation harness: the panel against a single well-scoped call (<code>specialist_panel/ablation.py</code>)</summary>

```python
@dataclass
class AblationResult:
    """What the panel found and what it cost, next to the single-call
    baseline. `omissions_caught_by_panel` compares which fields got a
    claim at all, not whether two free-text values agree -- field coverage
    is the honest floor a mechanical comparison can answer."""
    panel_fields: set[str]
    single_fields: set[str]
    omissions_caught_by_panel: set[str]
    panel_calls: int
    single_calls: int


def run_ablation(
    persona_fn: Any,      # callable(persona, listing) -> PersonaVerdict
    single_call_fn: Any,  # callable(listing) -> PersonaVerdict, one call, every concern
    listing: dict,
) -> AblationResult:
    """Baseline: single_call_fn is one well-scoped prompt asked to cover
    every specialist's concern in a single pass, scored the same way the
    panel is -- by which fields it named. A panel that never runs this
    comparison cannot tell a real gain from a longer answer that says the
    same thing three ways.
    """
    panel = run_panel(persona_fn, listing)
    decision = reconcile(panel.verdicts, panel.missing)
    panel_fields = {c.field for c in decision.accepted} | {c.field for c in decision.rejected}

    single: PersonaVerdict = single_call_fn(listing)
    single_fields = {c.field for c in single.claims}

    return AblationResult(
        panel_fields=panel_fields,
        single_fields=single_fields,
        omissions_caught_by_panel=panel_fields - single_fields,
        panel_calls=panel.cost.total_calls,
        single_calls=1,
    )
```

</details>

Field coverage is only a floor. Add the best single specialist alone, same-model self-consistency,[^selfconsistency] and a heterogeneous ensemble where you can afford one, and score on quality, omission recall, whether a genuine disagreement survived where a person can see it, latency, and cost ([4.2 Evaluation](../craft/proving-it-works.md)).

> **In the companion repo.** [`listing-studio/specialist_panel/`](https://github.com/AbhiramDwivedi/agentic-engineering/tree/main/listing-studio/specialist_panel) runs the whole shape offline against an injected `persona_fn`, ablation and compliance timeout included.

**Adding a persona is two decisions**: what it outranks, and what it yields to. A panel that outgrows your ability to state those rankings can no longer say why one seat won. Give each seat only the fields its viewpoint needs, too, since a context stuffed with everything spends tokens and degrades attention at once ([1.5 Context Engineering](../foundations/context-engineering.md)).

**Swapping the rule for a model** is what Mixture-of-Agents demonstrates when the proposers are different models,[^moa] and it inherits the judge pathologies [3.4 Evaluator-Optimizer](evaluator-optimizer.md) catalogues, so three controls stop being optional: mask each specialist's provenance where the model is shared, since self-recognition tracks self-preference;[^selfpref] randomize the order verdicts arrive in, since position bias is documented;[^judge-bias] and require an abstain-or-escalate path instead of a forced pick. None of it is in the code above.

#### Wiring it to a provider

The graph pane wires three persona nodes from `START` to one reconcile node, every edge written at build time. The OpenAI Agents SDK's manager agent is that seam higher up the stack: specialist agents called through `Agent.as_tool()` when you want "one agent to own the final answer, combine outputs from multiple specialists."[^oai-orchestration] Read its parallel-agents cookbook example with the notebook's own disclaimer in view: it calls itself "a toy example that you likely wouldn't parallelize in the real world."[^oai-parallel] CrewAI's `role` / `goal` / `backstory` triad names the same seats, and its default process runs them in sequence, so check the process before calling a crew a panel.[^crewai]

=== "LangGraph"

    ```python
    llm = init_chat_model("openai:gpt-5.5")
    persona_chain = llm.with_structured_output(PersonaVerdict)


    class PanelState(TypedDict):
        listing: dict
        # Keyed by persona and merged with dict union -- three nodes write to
        # this key at once, and none of them needs to know the other two ran.
        verdicts: Annotated[dict[str, PersonaVerdict], operator.or_]
        decision: Optional[PanelDecision]


    def make_persona_node(persona: str):
        """One node per roster entry, built at graph-definition time -- the
        roster decides the node count, never a model."""
        def _node(state: PanelState) -> dict:
            verdict = persona_chain.invoke(
                f"You are the {persona} specialist. Review this Listing Studio "
                f"product and return typed claims only for fields your role "
                f"covers: {state['listing']}"
            )
            return {"verdicts": {persona: verdict}}
        return _node


    def reconcile_node(state: PanelState) -> dict:
        """The typed merge: a persona that never wrote to `verdicts` is
        reported, not silently absent."""
        missing = [
            MissingSpecialist(persona=p, reason="node did not report a verdict")
            for p in ROSTER if p not in state["verdicts"]
        ]
        return {"decision": reconcile(state["verdicts"], missing)}


    builder = StateGraph(PanelState)
    for _persona in ROSTER:
        builder.add_node(_persona, make_persona_node(_persona))
        builder.add_edge(START, _persona)
    builder.add_node("reconcile", reconcile_node)
    for _persona in ROSTER:
        builder.add_edge(_persona, "reconcile")
    builder.add_edge("reconcile", END)
    graph = builder.compile()

    result = graph.invoke(
        {"listing": {"supplier_sku": "NV-ALDSWORTH-DM", "title": "Aldsworth Dual-Motor Sit-Stand Desk"}}
    )
    print(result["decision"].accepted, result["decision"].conflicts)
    ```

=== "OpenAI Responses API"

    ```python
    def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
        response = client.responses.create(
            model="gpt-5.5",
            input=[
                {
                    "role": "user",
                    "content": (
                        f"You are the {persona} specialist. Review this Listing "
                        f"Studio product and return typed claims only for fields "
                        f"your role covers: {listing}"
                    ),
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "PersonaVerdict",
                    "schema": PersonaVerdict.model_json_schema(),
                    "strict": True,
                }
            },
        )
        return PersonaVerdict.model_validate_json(response.output_text)


    panel = run_panel(persona_fn, ALDSWORTH_LISTING)
    decision = reconcile(panel.verdicts, panel.missing)
    print(decision.accepted, decision.conflicts)
    ```

=== "Anthropic Messages API"

    ```python
    _VERDICT_TOOL = {
        "name": "produce_persona_verdict",
        "description": "Return this specialist's typed claims about the listing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "persona": {"type": "string"},
                "claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "value": {"type": "string"},
                            "rationale": {"type": "string"},
                        },
                        "required": ["field", "value", "rationale"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["persona", "claims"],
            "additionalProperties": False,
        },
    }


    def persona_fn(persona: str, listing: dict) -> PersonaVerdict:
        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=[_VERDICT_TOOL],
            tool_choice={"type": "tool", "name": "produce_persona_verdict"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are the {persona} specialist. Review this Listing "
                        f"Studio product and return typed claims only for fields "
                        f"your role covers: {listing}"
                    ),
                }
            ],
        )
        tool_block = next(b for b in reply.content if b.type == "tool_use")
        return PersonaVerdict.model_validate(tool_block.input)


    panel = run_panel(persona_fn, ALDSWORTH_LISTING)
    decision = reconcile(panel.verdicts, panel.missing)
    print(decision.accepted, decision.conflicts)
    ```

## Gotchas

**The personas may not be buying you diversity.** A panel's output reads more thorough than one call's whether or not it is. Three personas on one model share one model's blind spots, and a job title in a system prompt is a weak lever on what the model knows.[^persona-null][^mad-limits] Where a panel does help, my read is that the help comes from splitting one overloaded instruction into narrow briefs, or from different models, which is the fix the debate study names.[^mad-heterogeneity] Neither is the persona.

**A model merge smooths away what you built the panel to see.** If the reconcile step is itself a prompt, the quiet failure is a lone compliance objection rounded off into a fluent summary, with no record anywhere that a conflict happened. A minority objection has to survive into the output as data, which is what `rejected` and `conflicts` are for. Coordination is where multi-call systems break in the measured record, too: MAST, the Multi-Agent System Failure Taxonomy, sorts real traces into 14 modes across three categories, and only one of the three is bad model output on a single step.[^mast] Test the merge separately, on conflicting claims, malformed fields, and a missing specialist.

**The cost is a multiple, and running the seats at once does not reduce it.** Every seat reads the input in full, so three personas cost roughly three times the input tokens of one call, on every product, including the ones that needed a single viewpoint. Swapping the code merge for a model adds a fourth call. Concurrency shortens the wait and leaves the bill alone. A fixed roster is also the expensive end of the pattern: per-input selection that drops the pricing and compliance seats on a phone case pays for one seat where yours pays for three, every time. Put cheap models in the seats ([8.2 Which Model?](../production/which-model.md)).

**A fixed panel dressed as a decision.** Billing a roster your code wrote as the model choosing its own experts is the over-orchestration entry in the [Anti-Patterns Catalog](../catalogs/anti-patterns.md), and the deflated version, three narrow prompts and a precedence rule, is a good design on its own.

**Security is inherited until the seats get their own tools.** A fixed panel with no inter-agent messaging adds no distinguishing attack surface: every seat reads the same input, and treating model output as untrusted ([2.1 Tool Use](../the-unit/tool-use.md)) covers it. Give the personas distinct tools, memory, or privileges and the risk model moves to [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md) and OWASP's agentic categories.[^owasp-agentic]

## In short

Start with the one call. Write it well, name every concern in it, make it return a typed answer, and measure it. When it keeps dropping a concern under load, split it into seats and put the merge in code, where a reader can see what was rejected and why. A missing specialist stops the listing; the per-seat cost goes on the record. Then run the ablation and be willing to lose: if the panel does not catch what the single call misses, delete it. Where you can afford it, different models in the seats have better evidence behind them than different personalities on one.

<small class="chapter-meta">**Maturity: Standard (fixed parallel execution) · Emerging (dynamic persona selection; heterogeneous-model synthesis) · Contested (same-model prompted-persona panels as a quality improvement)** (the evidence that prompted personas from one model improve output is thin and partly negative) · *Who decides:* your code (the fixed roster) / the model (the personas, where selection is dynamic) · *Grounding:* companion repo + research · *Last reviewed:* 2026-09</small>

## Sources

[^anthropic-bea]: Anthropic, "Building Effective Agents" (2024-12-19). Parallelization and its two variants; voting defined as "running the same task multiple times to get diverse outputs," instanced by "several different prompts review and flag the code if they find a problem" and by multiple prompts evaluating different aspects of one piece of content. <https://www.anthropic.com/research/building-effective-agents>
[^spp]: Wang, Z., Mao, S., Wu, W., Ge, T., Wei, F., Ji, H., "Unleashing the Emergent Cognitive Synergy in Large Language Models: A Task-Solving Agent through Multi-Persona Self-Collaboration" (NAACL 2024). Names its method Solo Performance Prompting: "given an input task, SPP first generates a list of participants with different personas," and "we let the language model identify the personas dynamically instead of manually defining them." States that "cognitive synergy only emerges in GPT-4 and does not appear in less capable models, such as GPT-3.5-turbo and Llama2-13b-chat." One model, several personas simulated in sequence within a single multi-turn context, not parallel independent calls. <https://arxiv.org/abs/2307.05300>
[^moa]: Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., Zou, J., "Mixture-of-Agents Enhances Large Language Model Capabilities" (2024). A layered architecture whose default proposers are heterogeneous open models; the aggregator "significantly outperforms LLM rankers" and "does not simply select one of the generated answers... but potentially performs sophisticated aggregation." Its ablation comparing repeated sampling from one model against several different models finds "using multiple different LLMs consistently yielded better results." Leaderboard scores are mid-2024 snapshots and are deliberately not repeated here; check the live source. <https://arxiv.org/abs/2406.04692>
[^persona-null]: Zheng, M. et al., "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models" (EMNLP Findings 2024). 162 roles across 6 relationship types and 8 expertise domains, tested against 2,410 factual questions across 4 model families: adding any persona to a system prompt yields no accuracy gain on fact-based QA; the paper's own wording is that most personas have no or negative impact, and that a persona might hurt in some situations. A different Zheng, and a different paper, from the judge-bias citation below. <https://arxiv.org/abs/2311.10054>
[^mad-limits]: Smit, A.P., Grinsztajn, N., Duckworth, P., Barrett, T.D., Pretorius, A., "Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs" (ICML 2024). Multi-agent debating systems do not reliably outperform self-consistency or ensembling baselines; some perform better only after hyperparameter tuning, which suggests sensitivity rather than inherent superiority. <https://arxiv.org/abs/2311.17371>
[^mad-heterogeneity]: "Stop Overvaluing Multi-Agent Debate -- We Must Rethink Evaluation and Embrace Model Heterogeneity" (submitted 2025-02-12, rev. 2025-06-21). Five debate methods across nine benchmarks and four foundation models: debate often fails to outperform single-agent chain-of-thought and self-consistency despite far higher inference cost, and the paper proposes heterogeneous foundation models as the consistent fix. Preprint; treat as directional. <https://arxiv.org/abs/2502.08788>
[^selfconsistency]: Wang, X. et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (ICLR 2023). Samples multiple reasoning paths from one prompt, with no persona variation, and selects the most consistent answer by marginalizing over samples: a deterministic vote rather than a model-rendered aggregation. <https://arxiv.org/abs/2203.11171>
[^debate]: Du, Y., Li, S., Torralba, A., Tenenbaum, J.B., Mordatch, I., "Improving Factuality and Reasoning in Language Models through Multiagent Debate" (2023). N agents answer independently, then read each other's responses and revise over multiple rounds. <https://arxiv.org/abs/2305.14325>
[^divergent]: Liang, T. et al., "Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate" (EMNLP 2024). Names the Degeneration-of-Thought problem, where a model that has committed to a stance cannot be dislodged by reflection alone, and proposes a debate with a managing judge. <https://arxiv.org/abs/2305.19118>
[^poll]: Verga, P. et al., "Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models" (2024). A panel of smaller models from different providers beats a single large judge across six datasets, with reduced bias and cost. Evaluation-specific rather than drafting. <https://arxiv.org/abs/2404.18796>
[^selfpref]: Panickssery, A., Bowman, S., Feng, S., "LLM Evaluators Recognize and Favor Their Own Generations" (NeurIPS 2024). Self-recognition ability correlates with self-preference bias. A related but distinct finding from the judge-bias paper below, not a replication of it. <https://arxiv.org/abs/2404.13076>
[^judge-bias]: Zheng, L. et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023, Datasets and Benchmarks track). Documents position, verbosity, and self-enhancement bias in LLM judges. <https://arxiv.org/abs/2306.05685>
[^mast]: Cemri, M. et al., "Why Do Multi-Agent LLM Systems Fail?" (NeurIPS 2025, Datasets and Benchmarks Track). MAST, the Multi-Agent System Failure Taxonomy: 14 failure modes clustered into 3 categories (specification and system design issues, inter-agent misalignment, task verification and termination), from 1,600+ annotated traces across 7 multi-agent frameworks. The abstract states the trace and framework counts; it does not state a task count. <https://arxiv.org/abs/2503.13657>
[^adk-parallel]: Google, Agent Development Kit docs, "Parallel agents" (workflow agents). `ParallelAgent` runs sub-agents concurrently, each in its own execution branch, with no automatic sharing of state between branches and no built-in aggregator; execution is deterministic and not model-controlled. Current ADK docs also note that, starting in ADK 2.0 for Python and Go, templated workflow agents "have been superseded by more flexible workflow structures, including graph-based workflows and dynamic workflows," so verify which style the version you install ships. <https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/>
[^oai-orchestration]: OpenAI, Agents SDK docs, "Agent orchestration." Agents as tools: "a manager agent keeps control of the conversation and calls specialist agents through `Agent.as_tool()`," used "when you want one agent to own the final answer, combine outputs from multiple specialists, or enforce shared SDK guardrails in one place." <https://openai.github.io/openai-agents-python/multi_agent/>
[^oai-parallel]: OpenAI, developers.openai.com cookbook, "Parallel Agents with the OpenAI Agents SDK." Four specialized agents run concurrently via `asyncio.gather` over one product review, and a meta-agent combines their labelled outputs. The notebook states plainly that it presents "a toy example that you likely wouldn't parallelize in the real world." <https://developers.openai.com/cookbook/examples/agents_sdk/parallel_agents>
[^crewai]: CrewAI, "Agents" and "Crafting Effective Agents" docs. The `role` / `goal` / `backstory` triad as a persona vocabulary; the default sequential process runs the roles in order rather than at once. Verify the current process types (`Process.sequential` and hierarchical) against the version you install. <https://docs.crewai.com>
[^owasp-agentic]: OWASP GenAI Security Project, "OWASP Top 10 for Agentic Applications" (2026 edition, announced 2025-12-09). ASI07 Insecure Inter-Agent Communication and ASI08 Cascading Failures are the categories a privilege-separated panel falls under. Newly published at the time of writing; re-confirm category names and numbering against the live document. <https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/>
[^gulli-adp]: Gulli, A., *Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems* (2025), chapter 7, "Multi-Agent Collaboration," per the publisher's public table of contents. Cited for the chapter title only; the chapter text was not independently read. The same umbrella title appears as chapter 6 of Gulli and Nawalgaria, *Building AI Agents* (2026 public draft).
[^ng]: Ng, A., public posts (2024) naming four agentic design patterns: Reflection, Tool Use, Planning, and Multi-Agent Collaboration.

## See also

- [1.2 Who Decides?](../foundations/who-decides.md): the test this chapter's split verdict is argued against.
- [1.4 The Augmented LLM](../foundations/the-augmented-llm.md): the unit each persona call is one instance of, one model call against a typed state contract.
- [1.5 Context Engineering](../foundations/context-engineering.md): why each seat should read only the fields its viewpoint needs.
- [2.2 Structured Output](../the-unit/structured-output.md): the typed contract the claims and the merged decision both depend on.
- [3.2 Routing & Dispatch](the-router-that-isnt.md): the sibling that picks one mutually exclusive path, where a panel admits several viewpoints at once.
- [3.3 Orchestrator-Workers](fan-out.md): the sibling where a model sizes its own fan-out, against a panel's viewpoints named in advance.
- [3.4 Evaluator-Optimizer](evaluator-optimizer.md): the sibling that loops one draft against a verdict; a panel judges once and never revises.
- [4.2 Evaluation](../craft/proving-it-works.md): the measurement depth behind the ablation this chapter insists on.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md): where an escalated, unreconcilable panel decision should land.
- [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md): the risk model once personas get distinct tools or privileges.
- [8.2 Which Model?](../production/which-model.md): cheap models in the seats, the strong one in the merge.
- [8.3 To Train or to Prompt](../production/train-or-prompt.md): fine-tuning distinct persona models instead of prompting one model into several roles.
- [8.4 Controlling Cost](../production/controlling-cost.md): the token multiple a panel commits you to, in depth.
- [9.2 Multi-Agent](../frontier/more-than-one-agent.md): iterative debate, layered Mixture-of-Agents aggregation, and the software-team role-play architectures (ChatDev, MetaGPT, CAMEL) this chapter names only.
- [9.6 Coding Agents](../frontier/coding-agents.md): the software-team role-play variant, where the panel is the product.

## Further reading

- Zheng, M. et al., ["When 'A Helpful Assistant' Is Not Really Helpful"](https://arxiv.org/abs/2311.10054) (EMNLP Findings 2024): the null result on persona prompts; read it before you budget for a panel.
- Wang, J. et al., ["Mixture-of-Agents Enhances Large Language Model Capabilities"](https://arxiv.org/abs/2406.04692) (2024): the strongest positive result in this space, and its ablation arguing for different models rather than different personas.
- Wang, Z. et al., ["Multi-Persona Self-Collaboration"](https://arxiv.org/abs/2307.05300) (NAACL 2024): the one published mechanism where a model selects its own participants per task, with its own stated model-capability limit.
- Smit, A. et al., ["Should we be going MAD?"](https://arxiv.org/abs/2311.17371) (ICML 2024): the best skeptical read on multi-call ensembles against fairly tuned single-agent baselines.
- Verga, P. et al., ["Replacing Judges with Juries"](https://arxiv.org/abs/2404.18796) (2024): the evaluation-side panel, and the clearest case for heterogeneity over persona variation.
- OpenAI, ["Agent orchestration"](https://openai.github.io/openai-agents-python/multi_agent/): the shape as a maintained vendor pattern, with `Agent.as_tool()` as the mechanism.
