# 6.2 Synthesis

*Assembling one deliverable from many model outputs, and checking the joins between them before anything ships.*

*Also called: fan-in, aggregation, synthesizer, output assembly, deliverable assembly.*

## Why you'd reach for it

Ask five model calls for five sections of a product page and each one comes back looking fine. Put them on one page and the description says the desktop is 60 by 28 inches while the spec table below it says 60 by 30, the FAQ repeats the description's opening line almost word for word, and the safety warning the page is legally required to carry is gone, because the call that wrote it hit its token limit and returned half a sentence.

Each section would pass a review on its own, and even the cut-off warning is a failure only because the page required it. The failures live at the seams, where outputs written blind to one another meet, and the seams belong to whoever does the assembling. So make the assembler your code.

The tempting fix is one bigger call that writes the whole page. It hits the output ceiling first: a model's output window is far smaller than its input window, and the LongWriter authors report that models they tested struggled to produce much past 2,000 words in one response.[^6] A single generation also cannot be partly re-run, and when a required block goes missing nothing notices, because nothing knew the block was required. The other tempting fix, a final call told to "merge and polish", reintroduces the problem in a new place. A rewrite is a fresh generation, and it can change any number it touches.

Listing Studio, the merchant tool this reference uses as its running example, drafts a storefront listing for a sit-stand desk, the Aldsworth, rated at 250 pounds. A brand-voice rewrite that turns "supports up to 250 lbs" into "built for 300 lbs" reads better, and an overstated load rating is a liability claim and a returns wave. A rewrite that quietly drops the Prop 65 warning (California's chemical-exposure notice, here for formaldehyde in the desktop) ships a compliance failure. A person skimming the final page for tone approves both.

You need this when:

- the output has parts generated separately: parallel workers, pipeline steps, a research fan-out;
- someone will act on the whole, such as a listing page, a category report or a merchant email;
- some facts must not move: dimensions, ratings, prices, compliance text, citations;
- the whole is longer than one call reliably writes.

You don't need it when one call produces one short answer with no required blocks; send the reply. Nor when the "parts" are separate artifacts that ship separately, like three independent emails: nothing sits next to anything, so there are no seams to check.

## What it actually is

Synthesis is the fan-in, the join after a fan-out, that turns many model outputs into one deliverable. Your code holds a template of slots (one fixed place per section, in a fixed order), fills each slot from a typed section result, checks the seams between sections, allows at most one model editing pass whose output is diffed against its input, and gates publication on what the checks found. The model writes the prose inside each slot. It never decides which slots exist, what order they go in, or which source a sentence came from.

![Five section results for the Aldsworth desk listing arrive in any order, each from its own model call: FAQ, which repeats the description's opening line; Specifications, stating 60 by 30 inches and 250 lbs; the Prop 65 notice, truncated at max_tokens with half a sentence; Description, stating 60 by 28 inches; and Highlights. Wires cross as code places each result into a code-owned template with fixed slots in a fixed order (Description, Specifications, Highlights, Prop 65 notice, FAQ), source ids attached; the required Prop 65 slot is empty. Code seam checks then find that the two sections disagree on the desktop size, and the spec table wins, and that the FAQ repeats the description, so only that pair is reworded. The one rounded shape is the model's editing pass, run once to even out voice; it turns "supports up to 250 lbs" into "built for 300 lbs". A code fidelity diff reports dropped 250 and added 300, so the unpolished page is kept. A code publish gate then blocks the page because the required Prop 65 notice is truncated; the other exit, ready for a person to approve, is not taken on this run.](producing-the-deliverable-assembly.svg)

Your code decides almost everything in that picture, and almost all of it is engineering you already know. A template with slots is mail merge. Comparing one fact across sections is a join on a key. Refusing to publish with a required section missing is form validation. The one model step after the parts are written, the editing pass, is a single call over assembled text. The model chooses words in it, never what runs next, so by the who-decides test of [1.2](../foundations/who-decides.md) it adds no new pattern. In Listing Studio it is step 8, the brand-voice polish (the humanizer pass). What is new is the material you are merging: free text from a writer that can change any fact it touches, which is why the checks run in code.

The maturity is Established. Assembling in code is settled practice: Anthropic's guide describes sectioning, splitting a task into independent subtasks whose outputs are "aggregated programmatically",[^1] and LongWriter's AgentWrite gets past the output ceiling by planning an outline and writing it one section at a time.[^6] Carrying source ids from worker to final page has vendor support: Anthropic's Citations feature returns the cited text with location pointers into the source document,[^3] and Anthropic's research system runs citation as its own stage over the finished report.[^2] Two parts are younger: pulling comparable facts out of free text, and the editing pass. I know of no benchmark that measures how often a voice rewrite changes a fact, so diff it every time.

Four neighbours get confused with this. [3.3 Orchestrator-Workers](../composition/fan-out.md) splits the work and ends where its `gather()` returns; synthesis starts there. [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md) has a model grade a draft and send the writer back to try again; 3.7 The Outer Loop does the same with a code verifier. Here each check runs once and code decides what to keep. [2.2 Structured Output](../the-unit/structured-output.md) supplies the slot schemas, the typed shape each section returns.

## How to do it

The page layout is a list in code. Each slot names a section, its heading, and whether the page can ship without it.

```python
@dataclass(frozen=True)
class Slot:
    section_id: str
    heading: str
    required: bool = True


# Code owns the layout. The model never decides what sections exist or in
# what order; it only fills the slots.
LAUNCH_TEMPLATE = [
    Slot("description", "Description"),
    Slot("specs", "Specifications"),
    Slot("bullets", "Highlights"),
    Slot("prop65", "California Prop 65 notice"),
    Slot("faq", "FAQ", required=False),
]


@dataclass
class Assembled:
    text: str
    blocked: list[str] = field(default_factory=list)  # required, not ok
    omitted: list[str] = field(default_factory=list)  # optional, not ok


def assemble(template: list[Slot], results: dict[str, SectionResult]) -> Assembled:
    parts, blocked, omitted = [], [], []
    for slot in template:
        r = results.get(slot.section_id)
        if r is None or r.status != "ok":
            (blocked if slot.required else omitted).append(slot.section_id)
            continue
        ids = ",".join(r.source_ids)
        parts.append(f"## {slot.heading}\n\n{r.body} [src:{ids}]")
    return Assembled("\n\n".join(parts), blocked, omitted)
```

`assemble` consumes one `SectionResult` per slot, the contract every section returns (listings omit imports; the companion files have them). A failed or cut-off section is a value with a status and a reason. It is never an exception and never an empty string spliced into the page, and its source ids travel with its text as a field, so a reorder cannot separate them.

<details markdown>
<summary>The contract: <code>SectionResult</code>, and how a worker result (3.3's <code>WorkerResult</code>: an id, an ok flag, the content or an error) or a raw reply becomes one</summary>

```python
class SectionResult(BaseModel):
    """One section's outcome: its status, its text and the sources it used."""
    model_config = ConfigDict(extra="forbid")

    section_id: str
    status: Literal["ok", "failed", "truncated"]
    body: str = ""
    source_ids: list[str] = []
    reason: str | None = None


def from_worker(worker: WorkerResult, source_ids: list[str]) -> SectionResult:
    """Wrap 3.3's WorkerResult and attach the ids its schema does not carry."""
    if not worker.ok:
        return SectionResult(
            section_id=worker.deliverable_id, status="failed", reason=worker.error
        )
    return SectionResult(
        section_id=worker.deliverable_id,
        status="ok",
        body=worker.content or "",
        source_ids=source_ids,
    )


# Anthropic: stop_reason "max_tokens" or "model_context_window_exceeded".
# OpenAI Responses: status "incomplete" (reason "max_output_tokens").
CUT_OFF = {"max_tokens", "model_context_window_exceeded", "incomplete"}


def from_reply(
    section_id: str, text: str, stop: str, source_ids: list[str]
) -> SectionResult:
    if stop in CUT_OFF:
        return SectionResult(
            section_id=section_id,
            status="truncated",
            body=text,
            source_ids=source_ids,
            reason=f"output cut off ({stop})",
        )
    return SectionResult(
        section_id=section_id, status="ok", body=text, source_ids=source_ids
    )
```

</details>

A second run on the Aldsworth desk, different from the one drawn above:

1. Five section calls finish in whatever order they finish. The FAQ call fails on a provider error and comes back as a `failed` result.
2. The Prop 65 reply stopped at the token limit, so `from_reply` marks it `truncated` with the reason "output cut off (max_tokens)".
3. `assemble` walks `LAUNCH_TEMPLATE` in order. Description, specifications and highlights render under their headings, each ending in its `[src:...]` marker.
4. The Prop 65 slot is required and not `ok`, so it lands in `blocked`. The FAQ is optional, so it lands in `omitted` and the page is still shippable without it.
5. Re-running the Prop 65 slot alone repairs the page and keeps the other four results, which a single whole-page generation cannot offer.

### Checking the seams

Sections written by separate calls disagree, because no call saw the others. The check pulls a small fact table out of each section (`desktop_size_in`, `weight_capacity_lbs`) and compares it in code. Extraction from free text is lossy and still Emerging. A better arrangement has each section return its key facts as structured fields beside its prose; that means adding a field to `SectionResult`, and the companion code takes the tables as given. Having a model read pairs of sections and flag disagreements also works, and it is Emerging too. Mündler and colleagues found that 17.7 percent of ChatGPT's sentences contradicted another sentence in the same output.[^8] That model had its whole output in view, and sections written blind never see each other at all.

On a hit, your code decides, and it never averages. The canonical section wins (on a listing, the spec table, which came from supplier data), or the conflict surfaces unresolved and goes to a person through [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md). Averaging 28 and 30 gives 29, a size neither the supplier nor any section stated.

Parallel sections also repeat the same selling point. Detect it in code with word-run overlap, then ask a model to reword only the flagged pair. Detection is Standard; the model rewrite is Emerging and goes through the same diff as everything else.

<details markdown>
<summary>Fact-table comparison and repeat detection</summary>

```python
@dataclass
class Conflict:
    key: str
    values: dict[str, str]    # section_id -> the value that section states
    winner: str | None        # canonical section's value, or None: escalate


def find_conflicts(
    tables: dict[str, dict[str, str]], canonical: str = "specs"
) -> list[Conflict]:
    """Compare per-section fact tables. Never average a disagreement away:
    the canonical section wins, or the conflict is surfaced unresolved."""
    by_key: dict[str, dict[str, str]] = {}
    for section, facts in tables.items():
        for key, value in facts.items():
            by_key.setdefault(key, {})[section] = value
    return [
        Conflict(key, values, values.get(canonical))
        for key, values in by_key.items()
        if len(set(values.values())) > 1
    ]


def _grams(body: str, n: int) -> set[tuple[str, ...]]:
    words = re.findall(r"[a-z0-9']+", body.lower())
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def find_repeats(sections: dict[str, str], n: int = 5) -> list[tuple[str, str]]:
    """Pairs of sections sharing a run of n words: the same selling point twice."""
    grams = {sid: _grams(body, n) for sid, body in sections.items()}
    ids = sorted(grams)
    return [
        (a, b) for i, a in enumerate(ids) for b in ids[i + 1 :] if grams[a] & grams[b]
    ]
```

</details>

### The editing pass

After assembly, one call over the whole page evens out voice, units and name spellings. It may reword. It may not add, drop or change a fact, and code holds it to that by diffing its output against its input. One pass, no retry loop: if the diff finds anything, the page ships unpolished.

```python
def _facts(text: str) -> Counter:
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    ids = re.findall(r"\[src:[^\]]*\]", text)
    names = re.findall(r"\b[A-Z][A-Za-z0-9-]{2,}\b", text)
    return Counter(numbers + ids + names)


def fidelity_diff(before: str, after: str) -> list[str]:
    """What the pass added or dropped: numbers, source ids, capitalized names."""
    a, b = _facts(before), _facts(after)
    return [f"dropped {k!r}" for k in a - b] + [f"added {k!r}" for k in b - a]


def polish_checked(edit_fn: Callable[[str], str], text: str) -> tuple[str, list[str]]:
    """One editing pass, no retry loop (retrying until the diff is clean
    would be 3.7's outer loop). On a failed call or a changed fact, keep
    the unpolished text."""
    try:
        edited = edit_fn(text)
    except Exception as e:  # cut off, refused, provider error
        return text, [f"editing pass failed: {e}"]
    problems = fidelity_diff(text, edited)
    return (text if problems else edited), problems
```

`fidelity_diff` is deliberately crude. It counts numbers, `[src:...]` markers and capitalized words before and after, and reports what moved. It catches 250 becoming 300, and it catches a dropped Prop 65 section because the counts of "Prop" and "65" fall. It understands nothing about meaning or about which number belongs to which claim: "supports 250 lbs" rewritten as "supports well under 250 lbs" passes, and so does a pass that swaps two numbers, because every counted token survived. It also over-fires, rejecting a pass that merely capitalized a word differently. Over-firing costs you only the polish; a miss ships the changed text. Treat it as a tripwire for the facts you can count, and read the page yourself for anything subtler.

Safer still, keep text that must not change, such as the Prop 65 notice, out of the pass and splice it back in code. Whatever stays in the prompt, put the parts that matter at the start or end: models use information in the middle of a long context less reliably,[^9] a finding from retrieval tasks, so treat it as a heuristic here. Give the seam check the spec fact table and one-line section summaries rather than five full drafts. [1.5 Context Engineering](../foundations/context-engineering.md) and [5.4 Compaction](../knowledge/compaction-and-the-window.md) carry the depth.

### Truncation and the publish gate

A cut-off reply is a stump that looks like a result. Anthropic's API reports it as `stop_reason: "max_tokens"` (or `model_context_window_exceeded` when the context window fills), and its guidance is to raise the limit or continue, and to tell the reader when a response is incomplete.[^4] OpenAI's Responses API returns `status: "incomplete"` with `incomplete_details.reason: "max_output_tokens"`, and on reasoning models the reasoning tokens count against that cap, so the visible answer can come back empty.[^5] `from_reply` turns both into a `truncated` result before assembly sees them. The structural fix is the template itself: short slots are less likely to hit the cap, and the one that does can be re-run alone.

The last check before a person sees the page is the publish gate. It returns reasons, and an empty list means ready for approval: every required slot filled, no leaked placeholders or tool-call text, every cited id resolving to a known source, length in bounds. The approval itself belongs to a person, because publishing is the irreversible step.

<details markdown>
<summary>The publish gate</summary>

```python
LEAK_MARKERS = ("{{", "TODO", "<tool_call", "[PLACEHOLDER")


def cited_ids(text: str) -> set[str]:
    groups = re.findall(r"\[src:([^\]]*)\]", text)
    return {i for g in groups for i in g.split(",") if i}


def publish_gate(
    assembled: Assembled, final: str, known_ids: set[str], max_chars: int = 6000
) -> list[str]:
    """Return the reasons not to publish; empty means ready for a person to
    approve. The approval itself is 4.3's human gate, not this function."""
    reasons = [f"required section missing: {s}" for s in assembled.blocked]
    reasons += [f"leaked text: {m}" for m in LEAK_MARKERS if m in final]
    reasons += [f"unknown source id: {i}" for i in sorted(cited_ids(final) - known_ids)]
    if not 200 <= len(final) <= max_chars:
        reasons.append(f"length out of bounds: {len(final)}")
    return reasons
```

</details>

### When the parts will not fit

Sometimes the parts are too large to pass through one window, or each hop through a coordinator can lose detail. Anthropic's research system has subagents write their output to external storage and "pass lightweight references back" to the coordinator, to avoid a "game of telephone".[^2] Category scout, the research agent that studies a product category before a merchant stocks it, has this shape: each worker's notes on a dozen competing desks go to storage, the synthesizer receives ids and one-paragraph summaries, and it opens the full note behind any id it cites. Whether to stuff everything into one window or collapse in stages is ordinary engineering, decided by size.

> **In the companion repo.** `listing-studio/assembly/` runs the Aldsworth beats offline against a fake model. Run `python -m pytest tests/test_assembly.py` from `listing-studio/`. Given the two sections' fact tables, the 60x28 versus 60x30 conflict picks the spec table's 60x30; a polish that turns 250 into 300 is rejected and the unpolished text kept; a failed editing call keeps it too; and a truncated Prop 65 section blocks publishing while a failed FAQ section is only omitted.

> **In Listing Studio.** Step 7 assembles the `launch_package`: the listing, an announcement email and ad copy. Step 8, the brand-voice polish, rewrites it to one voice, and step 9 validates before writing to the catalog. The template here is the listing page inside that package, step 8 is the editing pass, and the publish gate is step 9's validation.

#### Wiring it to a provider

The editing pass is the one call worth showing per provider. The Responses and Messages versions refuse a cut-off reply, and `polish_checked` then keeps the original.

=== "LangGraph"

    ```python
    EDIT_PROMPT = (
        "Edit for one consistent voice. Reword only. Do not add, remove or change "
        "any number, name or [src:...] marker. Return the full text.\n\n"
    )


    def edit_fn(text: str) -> str:
        return llm.invoke(EDIT_PROMPT + text).content


    # polished, problems = polish_checked(edit_fn, assembled.text)
    ```

=== "OpenAI Responses API"

    ```python
    EDIT_PROMPT = (
        "Edit for one consistent voice. Reword only. Do not add, remove or change "
        "any number, name or [src:...] marker. Return the full text."
    )


    def edit_fn(text: str) -> str:
        reply = client.responses.create(
            model="gpt-6.2-sol", instructions=EDIT_PROMPT, input=text
        )
        # status "incomplete" means cut off (reasoning tokens count against the
        # cap too): refuse it, and polish_checked keeps the original.
        if reply.status == "incomplete":
            raise RuntimeError("editing pass cut off; keep the unpolished text")
        return reply.output_text


    # polished, problems = polish_checked(edit_fn, assembled.text)
    ```

=== "Anthropic Messages API"

    ```python
    EDIT_PROMPT = (
        "Edit for one consistent voice. Reword only. Do not add, remove or change "
        "any number, name or [src:...] marker. Return the full text."
    )


    def edit_fn(text: str) -> str:
        reply = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=4096,
            system=EDIT_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        # Cut off mid-page: refuse it, and polish_checked keeps the original.
        if reply.stop_reason in ("max_tokens", "model_context_window_exceeded"):
            raise RuntimeError("editing pass cut off; keep the unpolished text")
        return next(b.text for b in reply.content if b.type == "text")


    # polished, problems = polish_checked(edit_fn, assembled.text)
    ```

## Gotchas

**A valid citation id is not a supported claim.** Carry-through guarantees the id survives; it says nothing about whether the sentence still says what the source says. Liu, Zhang and Liang audited generative search engines in 2023 and found about half of their sentences fully supported by their citations, and about three quarters of citations supporting the sentence they were attached to.[^7] An editing pass can break a claim and keep its id. A trailing marker per section also records only which sources the section used, and loses which source backs which sentence. Checking entailment, whether the source actually supports the sentence, after a rewrite is Emerging. A gate that resolves every cited id against a known source list costs a set difference; a person checks that the sources support the sentences.

**Citations and structured output do not combine.** Anthropic's documentation states that its Citations feature cannot be used together with structured outputs (checked November 2026).[^3] Keep source ids in your own schema and verify them in your code, which is what the code above does.

**The editing pass costs a whole page of output.** It reads the assembled page and writes all of it back, so its output tokens scale with the page. On long deliverables, polish only the slots whose voice drifted, or skip the pass. [8.4 Controlling Cost](../production/controlling-cost.md) has the arithmetic.

**Worker text is untrusted input.** Section bodies drawn from supplier feeds or the web land in your page and in the editing prompt. Escape them for the destination (Markdown, HTML, email) and keep them in the data part of the prompt; [4.6](../craft/prompt-injection.md) has the depth.

**Do not loop the pass until the diff is clean.** Retrying a rewrite until no fact moves is a code-owned verify-and-retry loop (3.7's outer loop) with a stopping condition you cannot guarantee, and every retry is another chance to move a fact the diff cannot count.

## In short

Write the page layout down as a template in code, and have every section return a typed result that carries its status and its source ids. Compare the few facts that must agree across sections, and resolve conflicts by a stated precedence or by a person, never by averaging. If you want one voice, run one editing pass and diff it for numbers, names and ids; on any change, ship the unpolished page. Treat a `max_tokens` or `incomplete` reply as a failure, block publishing on a missing required slot, and leave the final approval to a person. Code-owned assembly is settled practice. The editing pass is the part to distrust, so give it the least room.

<small class="chapter-meta">**Maturity: Established** (code-owned assembly is Standard; carrying source ids is Established; fact extraction from prose and the fact-preserving editing pass are Emerging) · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Anthropic, "Building effective agents" (2024). <https://www.anthropic.com/research/building-effective-agents>
[^2]: Anthropic, "How we built our multi-agent research system" (2025). <https://www.anthropic.com/engineering/multi-agent-research-system>
[^3]: Anthropic, "Citations." <https://platform.claude.com/docs/en/build-with-claude/citations>. The incompatibility with structured outputs is a product limitation and may change; re-check before relying on it.
[^4]: Anthropic, "Stop reasons and fallback." <https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons>
[^5]: OpenAI, "Reasoning models." <https://developers.openai.com/api/docs/guides/reasoning>
[^6]: Bai, Y., et al., "LongWriter: Unleashing 10,000+ Word Generation from Long Context LLMs" (2024). <https://arxiv.org/abs/2408.07055>. The roughly 2,000-word figure describes the models the authors tested in 2024; treat it as directional.
[^7]: Liu, N. F., Zhang, T., Liang, P., "Evaluating Verifiability in Generative Search Engines" (2023). <https://arxiv.org/abs/2304.09848>. The paper reports 51.5 percent of sentences fully supported and 74.5 percent citation precision across the engines it audited in 2023.
[^8]: Mündler, N., et al., "Self-contradictory Hallucinations of Large Language Models: Evaluation, Detection and Mitigation" (2023). <https://arxiv.org/abs/2305.15852>. The 17.7 percent figure is for ChatGPT in 2023 and measures contradiction within one model's output, not across separately written sections.
[^9]: Liu, N. F., et al., "Lost in the Middle: How Language Models Use Long Contexts" (2023). <https://arxiv.org/abs/2307.03172>

## See also

- [1.2 Who Decides?](../foundations/who-decides.md): why a single editing call over assembled text adds no new pattern.
- [1.5 Context Engineering](../foundations/context-engineering.md): what to pass the editing pass and the checks, and where in the prompt.
- [2.2 Structured Output](../the-unit/structured-output.md): the typed slot schemas and fact fields every section returns.
- [3.3 Orchestrator-Workers](../composition/fan-out.md): the fan-out whose `gather()` this chapter picks up from.
- [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md): what the checks become if a model grades the page and sends the writer back.
- [3.5 The Specialist Panel](../composition/specialist-panel.md): where the page's content blocks are built before they reach the template.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md): where unresolved conflicts and the final approval land.
- [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md): why worker output pulled from the web is untrusted text inside your deliverable.
- [5.4 Compaction](../knowledge/compaction-and-the-window.md): condensing parts before they cross into the synthesizer's window.
- [6.1 Ingestion](getting-the-mess-in.md): the other end of the I/O boundary.
- [6.3 Streaming & Agent UX](streaming-and-agent-ux.md): showing the assembled page as it fills in.
- [8.4 Controlling Cost](../production/controlling-cost.md): what a whole-page editing pass costs.

## Further reading

- Anthropic, ["Building effective agents"](https://www.anthropic.com/research/building-effective-agents) (2024): sectioning and programmatic aggregation in the vendor's own taxonomy.
- Anthropic, ["How we built our multi-agent research system"](https://www.anthropic.com/engineering/multi-agent-research-system) (2025): a production synthesizer, its separate citation stage, and the references-not-copies advice.
- Bai et al., ["LongWriter"](https://arxiv.org/abs/2408.07055) (2024): the output ceiling measured, and outline-then-sections as the way past it.
- Shao et al., ["Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models"](https://arxiv.org/abs/2402.14207) (2024): STORM, a research system that plans an outline from gathered sources before writing.
- Adams et al., ["From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting"](https://arxiv.org/abs/2309.04269) (2023): a neighbour technique for packing more facts into fixed-length text.
- Liu, Zhang, Liang, ["Evaluating Verifiability in Generative Search Engines"](https://arxiv.org/abs/2304.09848) (2023): the best measurement of how often a cited sentence is actually supported.
