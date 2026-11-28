# 5.4 Compaction

*Compaction and the window: summarize and prune the context so it stays useful. Mask before you summarize, and keep what must survive where no summary can reach it.*

*Also called: context compression, summarization, context-window management.*

## Why you'd reach for it

Halfway through a long agent run, a supplier confirms that one standing desk adjusts from 27 to 48 inches, and the agent replies that it will use that range instead of the 25 to 50 printed on the spec sheet. Many turns later the context window (everything the model reads on a call) is nearly full, the harness replaces the older turns with a summary, and the summary says *"supplier rows were ingested and checked."* The confirmation is gone, nothing raised an error, and the next listing the agent drafts for that desk carries the spec sheet's range.

Any agent that runs long enough faces this trade. You have to shrink the window, because the evidence so far says models get less reliable as their input grows, well before the advertised limit. RULER tested 17 models that claimed 32,000-token windows and found about half held up at that length,[^ruler] and NoLiMa found 11 of 13 models fell below half their short-input score at 32,000 tokens once the answer could not be found by matching words.[^nolima] [1.5 Context Engineering](../foundations/context-engineering.md) carries the rest of that evidence. The cost of shrinking is that every way of doing it removes something. Masking a tool result leaves a key that fetches the original back. A summary leaves nothing, and the model reading it cannot tell what went.

Listing Studio, the commerce platform our examples use, runs a bulk ingest: one agent session reads a few hundred rows of a supplier's product feed and drafts a store listing for each. The session has one pinned rule, "drafts only", so nothing is published without a person; a pinned message is one no rewrite may touch. The desk's height range lived in one ordinary message. Lose it and a merchandiser reviews every later draft for that desk against a spec sheet the supplier has already corrected, and the wrong range ships if they miss it. A pin would have kept it, and so would a state record: a small structure your code writes each decision into and renders back into the window on every call. A probe would have caught the loss. It asks the compacted window questions whose answers must still be there and reports the ones it can no longer answer.

Use the lightest rewrite that fits, masking old tool results before you summarize anything, and keep whatever must survive in a pin or a state record your code owns, because a summary drops specifics without telling you and only a probe will catch it.

You need compaction when:

- a run outgrows the window, or grows long enough that you have measured quality dropping;
- most of the window is tool output (file contents, search results, feed rows) that the model has already used;
- the run must keep going in one session, because restarting loses work.

You do not need it for short runs that finish well inside the window; compacting them buys a lossy rewrite for nothing. If a single tool output is what fills the window, return less from the tool, and if a sub-task produces most of the noise, give it its own window.

## What it actually is

Compaction is any rewrite your code makes to the history it holds so the next model call reads a smaller window. The rewrites form a ladder, lightest first: mask old tool results, replacing each with a placeholder that keeps its archive key (Anthropic calls this clearing); trim long messages; summarize older turns into a single message; offload content to files the agent can read back; or isolate a sub-task in a sub-agent whose window is thrown away. Each rung trades tokens for information. Your code decides when to rewrite and what is protected; the model decides only one thing, what a summary says.

![The compaction ladder, lightest first: code masks old tool results, keeping keys, and trims long messages; the model summarizes older turns, which can drop the desk's 27-48 range; code offloads content to files, keeping paths, and isolates a sub-task, keeping only its result. The pinned "drafts only" rule and a state record holding 27-48 sit outside every rung, and code renders both into the next call.](compaction-and-the-window-ladder.svg)

Masking, trimming and offloading are pure code, the same move as replacing a blob with a storage key. Anthropic calls clearing tool results "one of the safest lightest touch forms of compaction",[^anthropic-ce] because it loses nothing you cannot get back: Manus describes the same idea as compression that stays restorable, dropping a page's content while keeping its URL.[^manus] A summary keeps no such pointer. Once it replaces the original turns, the original is gone unless your code archived it first.

The mechanisms are established. Anthropic and OpenAI both ship server-side compaction, Anthropic ships rule-based tool-result clearing, and LangChain ships summarization and context-editing middleware.[^langchain] The degradation research is still emerging, and the evidence for which rung to use is thin. The one controlled study, Lindenbauer and colleagues on SWE-agent with SWE-bench Verified, found that masking old observations matched LLM summarization at lower cost, and a hybrid of the two was cheaper again; the authors call the result initial.[^lindenbauer] In their preliminary runs on SWE-bench Lite, tool observations made up about 84% of an average turn, so masking them removes most of what each turn adds.[^lindenbauer]

Three neighbours get confused with this. [1.5 Context Engineering](../foundations/context-engineering.md) is the discipline of choosing what goes in the window; compaction is its move for a window that has already grown. [2.6 The Harness](../the-unit/the-harness.md) owns the compaction seat: when the trigger fires and which rules are pinned. [5.1 State, Not Memory](state-not-memory.md) is where facts go that must survive any rewrite.

## How to do it

The companion code is a standalone package, `listing-studio/compaction/`. A message carries a `pinned` flag and, for tool results, a `result_id` the archive uses as a key. The token count is an estimate: one word, one token.

<details markdown>
<summary>The message and the token estimate</summary>

```python
class Message(BaseModel):
    role: str                     # "user", "assistant" or "tool"
    content: str
    pinned: bool = False          # a pinned message is never masked, trimmed or summarized
    result_id: str | None = None  # set on tool results; the archive key


def estimate_tokens(history: list[Message]) -> int:
    """An estimate: one word counts as one token. Trigger on this, not on message count."""
    return sum(len(m.content.split()) for m in history)
```

</details>

The first rung replaces every tool result except the last few with a placeholder that names its archive key. Here `keep_last` counts tool results.

```python
def mask_observations(history: list[Message], keep_last: int, archive: dict) -> list[Message]:
    """Rung 1: replace old tool results with a placeholder that carries an archive key."""
    tool_idx = [i for i, m in enumerate(history) if m.role == "tool" and not m.pinned]
    old = set(tool_idx[: max(len(tool_idx) - keep_last, 0)])
    out = []
    for i, m in enumerate(history):
        if i in old:
            archive[m.result_id] = m.content  # the full text stays recoverable by key
            m = m.model_copy(update={"content": f"[result masked; archive key {m.result_id}]"})
        out.append(m)
    return out
```

The summarizing rung is where the model writes. The docstring lists what your code does around that call; note that `keep_last` counts messages here, where masking counted tool results. `summarize` is any function from the older messages to summary text: a model call in production, a scripted stand-in in the tests. `_usable` rejects an empty summary or one that opens like a refusal.

```python
def compact(history: list[Message], summarize: Callable[[list[Message]], str],
            budget_tokens: int, keep_last: int, archive: dict) -> list[Message]:
    """Rung 3: summarize the middle. Triggers on the token estimate, archives the
    full history first, keeps pins and the last keep_last messages, and returns the
    history unchanged if the summarizer raises, returns nothing or refuses."""
    if estimate_tokens(history) <= budget_tokens:
        return history
    archive["history"] = [m.model_dump() for m in history]
    recent = history[-keep_last:]
    older = history[:-keep_last]
    try:
        summary = summarize([m for m in older if not m.pinned])
    except Exception:
        return history  # a failed summary must not cost the window
    if not _usable(summary):
        return history  # empty or refused: keep what we have
    pins = [m for m in older if m.pinned]
    return pins + [Message(role="assistant", content=summary)] + recent
```

A decision that must survive should not wait for a summarizer to notice it; code writes it into the state record the moment it is made. The probe then takes a list of `Question`s, each with an `ask` (what a later turn would need to know) and an `expect` (the fact that answers it), and checks whether each `expect` is still readable in the window.

<details markdown>
<summary>The state record and the probe</summary>

```python
class RunState(BaseModel):
    decisions: dict[str, str] = {}  # written by code the moment a decision is made


def render(state: RunState) -> Message:
    """Put the state record back into the window. Call it every turn, after any compaction."""
    lines = [f"- {k}: {v}" for k, v in state.decisions.items()]
    return Message(role="user", content="Run state (kept by code):\n" + "\n".join(lines), pinned=True)
```

```python
def probe(history: list[Message], state: RunState, questions: list[Question]) -> list[str]:
    """A presence probe: is the expected fact anywhere in render(state) + history?
    It tests that the fact is still there, not that a model would recall it.
    Returns the questions the window can no longer answer."""
    window = " ".join(m.content for m in [render(state), *history]).lower()
    return [q.ask for q in questions if q.expect.lower() not in window]
```

</details>

One ingest session, run on the companion test fixture:

1. The session holds 26 messages at 243 estimated tokens: the pinned "drafts only" rule, twelve supplier rows (each a request and a tool result), and, after row 3, the message recording the supplier's 27-48 range for the desk, SKU `NV-ALDSWORTH-DM`.
2. The budget is 120 estimated tokens. Masking every tool result except the last three brings the window to 162, still over.
3. Summarizing instead, starting again from the original 243-token session and keeping its last four messages, brings it to 60. The pin survives. The summary is the scripted stand-in's *"Summary of 21 earlier messages: supplier rows were ingested and checked."*, and 27-48 is nowhere in the window.
4. The probe asks two questions, whether publishing is allowed and which height range the desk uses. With an empty state record it reports the height question as unanswerable.
5. Code writes the decision into the state record. The probe runs against the same compacted history and passes both questions, because `render` puts 27-48 back in the window.
6. At a budget of 200, the companion's `shrink` (it tries the rungs in order and stops at the first that fits) never summarizes: masking the original session down to its last four tool results fits at 171, and the original message, decision included, is still there.

> **In the companion repo.** `listing-studio/tests/test_compaction.py` runs the trace offline with a scripted summarizer, and also checks that an empty, raising or refusing summarizer leaves the history unchanged and that the archive restores a masked result by key.

**What to pin, and what to move out.** Pin the standing rules, the task statement, the plan and its open decisions, and the identifiers later turns need. Pins cost tokens on every call, which [2.6](../the-unit/the-harness.md) weighs. A rule that must hold, such as "drafts only", should also be enforced in code, because a pinned sentence is still advice to the model. Durable facts and control flow go in state, as in step 5. Placement matters too: "Lost in the Middle" suggests keeping pins and the summary at the start or the end of the window.[^liu]

**Writing the summary.** This is the one step the model decides, so give it a schema in place of a request for prose: the task, decisions with their reasons, artifacts touched, open items, and the next step. Factory describes summarizing only the newly dropped span and merging it into the existing summary,[^factory] which avoids summarizing a summary, where a detail the first pass kept can drop out of the second.

**Offload.** Offloading writes the bulky thing to a file and keeps a path in the window; Manus treats the file system as context that is "unlimited in size, persistent by nature".[^manus] It is the right rung for exact values you will need verbatim, and [5.1](state-not-memory.md) covers the record that holds the path.

**Isolate.** Isolation gives a sub-task its own window and takes back only its result, which is [9.2 Multi-Agent](../frontier/more-than-one-agent.md). Cognition warns that compressing context is "hard to get right" and that "You will still eventually hit a limit";[^cognition] a sub-task's fresh window postpones it, and just the result comes back to yours.

**Testing what it lost.** The probe above is a presence probe: it checks that the fact is still in the window, which a model needs before it can recall anything. Write probe questions whose answers sit only in the span you expect to drop: a specific value, the artifacts changed, the next step, the reason for a decision. Factory groups probes into those four kinds.[^factory] Add two regressions to every compaction change, one that a pinned item survives and one that an unpinned specific is lost unless it is in state. A model-judged probe tests recall, and it needs its own calibration, which [4.2 Evaluation](../craft/proving-it-works.md) covers.

#### Wiring it to a provider

Both major APIs now compact on the server, and they differ in what you can read back. Anthropic's on-demand compaction, in beta behind the `compact-2026-09-04` header, takes a top-level `compaction` parameter and returns a `compaction` block whose summary is text you can read and probe.[^anthropic-compaction] Anthropic's docs recommend this mode over automatic compaction at a token threshold wherever it is available. For the masking rung, Anthropic's context editing (header `context-management-2025-06-27`, strategy `clear_tool_uses_20250919`) clears old tool results on the server while "Your client application maintains the full, unmodified conversation history", and an `exclude_tools` list protects the results you treat as pins.[^anthropic-edit] OpenAI's Responses API compacts through `context_management` with a `compact_threshold`, or on request through `/responses/compact`, and the compacted item "is opaque and not intended to be human-interpretable".[^openai] You cannot read that item, so the only check left is a probe on the model's answers. Every name here is beta or recent; check the live docs before you copy one.

Claude Code is the instance on your own screen. Run `/context` to see what fills the window, then `/compact focus on <topic>` to steer the summary, or put a "Compact Instructions" section in CLAUDE.md. Its docs warn that "detailed instructions from early in the conversation may be lost" and tell you to put persistent rules in CLAUDE.md, which is pinning by another name.[^claude-code]

## Gotchas

**Summarizing when masking would do.** The masking study's cost result is the reason to try the cheap rung first.[^lindenbauer] Factory's vendor-run benchmark compares summarizers only, with no masking arm.[^factory] A preprint by Satish and colleagues found that on Terminal-Bench with Qwen, runs using roughly a third of the tokens could take 20 to 80% longer,[^satish] so a token saving is not automatically a time saving. Measure on your own runs before you add a summarizer.

**Any fact your run cannot afford to lose has to live somewhere a summarizer cannot reach.** That means a pin, a state record, or a file with a path in the window. A decision that exists only in a message survives exactly as long as the next summary happens to mention it.

**Trusting a summary nobody probed.** Losses are silent and land on specifics, such as the files an agent touched and instructions given once.[^factory][^claude-code] Probe before you trust a new summarization prompt, and again when you change models.

**Triggering at the hard limit.** Set the trigger from the point where your own measurements show quality dropping, and leave room for the summarization call itself; Anthropic's docs say to compact "before you outgrow it, not after".[^anthropic-compaction] When one tool output refills the window right after each summary, the harness loops. Claude Code stops auto-compacting after a few attempts and shows an error,[^claude-code] and your harness needs the same stop.

**Checking for an empty summary and missing the refusal.** The failure contract is that a summarizer that raises, returns nothing, or refuses leaves the history unchanged. On Anthropic's on-demand path a failed summary still returns HTTP 200 with empty `content`, and `stop_reason` tells you why, including `"refusal"`.[^anthropic-compaction] Check `stop_reason` before you look for the block.

**Breaking the cache.** Masking old content on the server "invalidates cached prompt prefixes",[^anthropic-edit] and a new summary changes everything after it. Mask in large steps (Anthropic's `clear_at_least` exists for this), and place a cache breakpoint after the system prompt so it survives each rewrite.

**Carrying an injection forward.** A summary of turns that contained a malicious instruction can restate it in your own assistant's voice. Untrusted content belongs in tool results you can mask or archive; [4.6 Prompt Injection](../craft/prompt-injection.md) covers the rest.

## In short

Mask old tool results first, each with a key that gets it back, and stop there if the window fits. Summarize only when it does not, with a schema, an archive of the original, and a failure path that keeps the history. Before any of that, move what must survive out of the transcript: rules into pins and code, decisions into a state record, bulky exact values into files. Then probe the compacted window, because a summary will not tell you what it dropped. Trigger below the point where you measured quality falling.

<small class="chapter-meta">**Maturity: Established (mechanisms) / Emerging (strategy choice and testing)** (tool-result masking and server-side compaction ship from Anthropic, OpenAI and Claude Code; the degradation research is still settling, and which rung to use rests on one SWE-agent study, a vendor benchmark and a preprint) · *Who decides:* your code (when, what is pinned, whether to keep the result); the model (what a summary says) · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^liu]: Nelson F. Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," TACL 2024. arXiv:2307.03172. <https://arxiv.org/abs/2307.03172>
[^ruler]: Cheng-Ping Hsieh et al., "RULER: What's the Real Context Size of Your Long-Context Language Models?" 2024. arXiv:2404.06654. Figures from the abstract. <https://arxiv.org/abs/2404.06654>
[^nolima]: Ali Modarressi et al., "NoLiMa: Long-Context Evaluation Beyond Literal Matching," ICML 2025. arXiv:2502.05167. Figures from the abstract. <https://arxiv.org/abs/2502.05167>
[^anthropic-ce]: Anthropic, "Effective context engineering for AI agents," 2025-09-29. <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
[^manus]: Yichao "Peak" Ji, Manus, "Context Engineering for AI Agents: Lessons from Building Manus," 2025-07-18. Restorable compression, and the file system as context. <https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus>
[^lindenbauer]: Tobias Lindenbauer et al., JetBrains Research and TU Munich, "The Complexity Trap: Simple Observation Masking Is as Efficient as LLM Summarization for Agent Context Management," NeurIPS 2025 DL4C workshop. arXiv:2508.21433. Five configurations of SWE-agent on SWE-bench Verified; the hybrid was 7% cheaper than masking and 11% cheaper than summarization; the 84% observation share comes from preliminary runs on SWE-bench Lite-50. The authors describe generality as initial. <https://arxiv.org/abs/2508.21433>
[^factory]: Factory Research, "Evaluating context compression," 2025-12-16. Scores on six dimensions by a GPT-5.2 judge; Factory sells one of the compared methods; no masking arm; Factory's own method scored 0.26 to 0.35 points ahead of Anthropic's and OpenAI's on a five-point scale. The post also describes anchored iterative summarization and four probe types, and calls artifact tracking unsolved. <https://factory.com/news/evaluating-compression>
[^satish]: Ritul Satish, Prasoon Sinha, Akiho Kawada, Neeraja J. Yadwadkar, "Beyond Token Savings: A Systematic Study of Context Compression in LLM Agents," arXiv:2609.32961, 2026. A preprint, not peer reviewed; about 35,000 runs on three open-weight models. Figures from the abstract. <https://arxiv.org/abs/2609.32961>
[^cognition]: Walden Yan, Cognition, "Don't Build Multi-Agents," 2025-06-12. <https://cognition.com/blog/dont-build-multi-agents>
[^anthropic-compaction]: Anthropic, "Compaction overview" and "Compaction on demand," Claude API docs, beta; checked 2026-11-28. Header `compact-2026-09-04`, the `compaction` parameter and block, `instructions`, `usage.iterations`, the empty-content and `stop_reason` failure table, "Use on-demand compaction wherever it is available," and "compact before you outgrow it, not after." <https://platform.claude.com/docs/en/build-with-claude/compaction> and <https://platform.claude.com/docs/en/build-with-claude/compaction-on-demand>
[^anthropic-edit]: Anthropic, "Context editing," Claude API docs, beta; checked 2026-11-28. Header `context-management-2025-06-27`, `clear_tool_uses_20250919` (defaults: trigger at 100,000 input tokens, keep 3 tool uses), `clear_at_least`, `exclude_tools`, the full-history quotation and the cache-invalidation note. <https://platform.claude.com/docs/en/build-with-claude/context-editing>
[^openai]: OpenAI, "Compaction," API guide, undated; checked 2026-11-28. `context_management`, `compact_threshold`, `/responses/compact`, the opaque-item quotation, and "If you use `previous_response_id` chaining, do not manually prune." <https://developers.openai.com/api/docs/guides/compaction>
[^langchain]: LangChain, "Built-in middleware," checked 2026-11-28: Summarization ("Automatically summarize conversation history when approaching token limits") and Context editing ("trimming or clearing tool uses"). <https://docs.langchain.com/oss/python/langchain/middleware/built-in>
[^claude-code]: Anthropic, Claude Code docs, "How Claude Code works," checked 2026-11-28. Auto-compaction, `/context`, `/compact` with a focus, Compact Instructions, the lost-instructions warning and the thrashing stop. <https://code.claude.com/docs/en/how-claude-code-works>

## See also

- [1.5 Context Engineering](../foundations/context-engineering.md): the evidence that windows degrade, and the curation moves compaction belongs to.
- [2.6 The Harness](../the-unit/the-harness.md): the compaction seat, the trigger, pinned rules and what pins cost.
- [5.1 State, Not Memory](state-not-memory.md): the record that holds what no summary may drop.
- [5.2 Retrieval (RAG)](retrieval-rag.md): fetching content back into the window on demand, the read side of offloading.
- [5.3 Memory](real-memory.md): what persists across sessions, past any one window.
- [3.3 Orchestrator-Workers](../composition/fan-out.md) and [9.2 Multi-Agent](../frontier/more-than-one-agent.md): isolation, a sub-task in a window of its own.
- [4.2 Evaluation](../craft/proving-it-works.md): calibrating a model-judged probe.
- [4.6 Prompt Injection](../craft/prompt-injection.md): untrusted content that a summary can carry forward.
- [Anti-Patterns Catalog](../catalogs/anti-patterns.md): where these gotchas are collected.

## Further reading

- [Lindenbauer et al., The Complexity Trap](https://arxiv.org/abs/2508.21433): the one controlled comparison of masking against summarization.
- [Anthropic, Compaction overview](https://platform.claude.com/docs/en/build-with-claude/compaction): the three ways to compact on one API, side by side.
- [OpenAI, Compaction guide](https://developers.openai.com/api/docs/guides/compaction): server-side compaction with an opaque result.
- [Manus, Context Engineering for AI Agents](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus): restorable compression and the file system as context, from a team running agents in production.
- [Factory, Evaluating context compression](https://factory.com/news/evaluating-compression): probe-based evaluation of summaries, read with its caveats.
