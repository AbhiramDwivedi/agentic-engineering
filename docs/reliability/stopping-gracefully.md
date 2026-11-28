# 7.3 Checkpointing

*Stopping gracefully: save the run's state after every step so a cancelled or crashed run resumes where it stopped, and journal each side effect before it leaves the process, because the step that was in flight will run again.*

*Also called: checkpoint and resume, durable execution (Temporal, Restate, DBOS), time travel (LangGraph, for replaying from a saved checkpoint), file checkpointing (Claude Code).*

## Why you'd reach for it

A long agent run dies at the worst moment: it has just sent an email and has not yet written down that it did. You restart it from its last checkpoint, the email step runs again, and the model, asked the same question a second time, words the email differently. The merchant gets *"Your listing is live"* and, a minute later, *"Your listing has launched"*.

Checkpointing alone can cause that failure even as it prevents the one it was built for. Take a product-listing pipeline that turns a supplier's spreadsheet row into a storefront page in nine steps: ingest the feed, fill in missing attributes, categorize, write the copy, build the page sections, set the price, assemble a launch package, polish the voice, publish. Without checkpoints, a crash at step 8 throws away seven steps of paid model work on the Aldsworth sit-stand desk, and the merchandiser who clicked *Generate listing* waits for all of it again. With a checkpoint saved after each step, the run resumes at step 8. Frameworks give you that half.

The hard half is the step that was running when the process died. A checkpoint is written between steps, so what the running step had already done to the outside world is not in it. Step 7 assembles the launch package, and one of its deliverables is the merchant announcement email. If the process dies after the email provider accepts the send and before the checkpoint lands, the resume runs step 7 again from its first line. A deterministic program would send the identical email, and an idempotency key (a value sent with the request so the provider can recognise a repeat and act once) computed from its contents would catch it. A model asked a second time may word the email differently. If it does, the key changes with the wording, the provider sees a new request, and the merchant gets two.

Save the state after every step, so finished work is not redone once its checkpoint has committed. And before any side effect leaves the process, write down what the step is about to send and under which key, so the replay reuses that record instead of asking the model again. The second part is the old write-ahead idea from databases (log what you are about to do before you do it), applied to the one participant in your system that can answer differently each time you ask.

Reach for checkpointing when:

- **The run is long enough to lose.** Minutes of model calls, or a run that waits on a person or a slow tool.
- **Someone will want to stop it.** A merchandiser's cancel button, a spending limit, a deploy that restarts the worker.
- **A step touches the world.** An email, a price write, a publish: anything you cannot take back by deleting a row.

The counter-trigger: a run that finishes in one or two model calls and writes nothing outside your process. Rerun it from the top. A checkpoint store you do not need is one more place holding customer data.

## What it actually is

Checkpointing saves a run's state under a run id each time a step finishes, so a resume skips the finished steps and starts at the first unfinished one. The step that was in flight when the process stopped has no checkpoint and runs again from its start, so every step that causes a side effect needs a journal entry written before the effect, holding the exact call and its idempotency key, and on replay the step reuses that entry instead of asking the model again.

![A run drawn twice, before and after a crash. First pass: step 6 finishes and is checkpointed. Step 7 asks the model, the one rounded node, for the announcement email; your code journals the call and its key, sends the email, and the process dies before step 7's checkpoint. On the resume, step 6 is skipped and step 7 runs again, finds the journal entry, never reaches the model, and resends the recorded email under the same key; the provider answers deduped and the merchant receives one email.](stopping-gracefully-replay.svg)

Your code decides all of it. Checkpoint, replay, cancel and the fencing of effects (making a repeated effect harmless) are deterministic infrastructure; the model is the non-deterministic worker inside a step, and the design exists to keep its non-determinism from leaking through a restart. None of the machinery is new. Databases have logged intent ahead of effects for decades, and payment APIs have offered idempotency keys for years. What is new is a worker that, replayed, can change its mind.

The core is Established. LangGraph's persistence layer saves graph state as checkpoints grouped under a thread id.[^1] Durable-execution engines such as Temporal, Restate and DBOS go further: they record each completed step, such as a model call or a tool call, with its result in a log, and on replay reuse the recorded result instead of running the step again.[^2][^3][^4] A step that was still running when the worker died runs again. Idempotency keys themselves are Standard, and Stripe's documentation is the usual reference.[^5]

Replay that is safe for agents is Emerging. The evidence is two 2026 papers that build attack testbeds around resumed and rolled-back agents, one of them cataloguing the ways a resume goes wrong.[^6][^7] I could not find a public postmortem of a duplicate effect caused by an agent resume. The hazard is shown in the lab and follows from how replay works, and that is as strong as the claim gets.

Two questions are open. The first is whether a library checkpointer, such as LangGraph's Postgres saver, is enough in production, or whether you need a system that notices a dead worker and restarts it, which a saver inside the dead process cannot do. The second is whether replaying from an old checkpoint, which LangGraph calls time travel, is safe recovery once the run has touched the world. LangGraph's own documentation says replay re-executes the steps after the checkpoint, model and tool calls included, and that editing an old checkpoint's state creates a fork rather than rolling anything back.[^8] My position on both: a library saver is fine for runs whose effects you fence yourself; move to an engine when a dead worker that nobody restarts is unacceptable; and use time travel to debug, never to undo.

What goes in the record, its typed fields, its reducers (the functions that merge each step's update into the state) and its thread scope (which run the record belongs to), is the subject of 5.1 State, Not Memory. This chapter is about saving snapshots of that record and resuming from them.

## How to do it

The minimum is two pieces: a saver that records which steps finished and the state they left, and a loop that consults it. The journal field is for the fix further down. A step is a function from state to new state.

```python
import hashlib
import json
from typing import Callable

from .receiver import Receiver
from .scripted import ScriptedModel

Step = Callable[[dict], dict]  # a step maps state to new state
```

```python
class Saver:
    """In-memory stand-in for a durable store (a database row in production)."""

    def __init__(self):
        self.done: list[str] = []   # names of steps that finished
        self.state: dict = {}       # state as of the last finished step
        self.journal: dict[str, dict] = {}  # step -> the effect it first issued
```

```python
def run(steps: list[tuple[str, Step]], saver: Saver, state: dict) -> dict:
    """Run steps in order; checkpoint after each. Resume skips finished steps."""
    state = {**state, **saver.state}
    for name, step in steps:
        if name in saver.done:
            continue                       # finished before the crash
        state = step(state)                # if this raises, nothing is saved
        saver.done.append(name)            # checkpoint: between steps only
        saver.state = dict(state)
    return state
```

The contract is where the checkpoint line sits: after `step(state)` returns, never inside it. If the step raises, nothing is saved and the resume runs it again from its first line. For a step that sends something, that rerun is how the opening's email went out twice. In a real store the two checkpoint lines must be one atomic write of a deep copy of the state, or a crash between them marks a step done whose state was never saved.

The tempting fix is an idempotency key, and what matters is what you derive it from.

```python
def content_key(params: dict) -> str:
    """Fragile: a replayed step with new wording gets a new key."""
    return hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:12]


def step_key(run_id: str, step: str) -> str:
    """Stable across replays, but the receiver must compare parameters."""
    return f"{run_id}:{step}"
```

A content key hashes the parameters, so it is stable only when the parameters are, and on a model-written email they may not be. A step key names the step, so it survives the replay. Against a receiver that compares parameters, it turns a silent duplicate into a loud failure: Stripe's v1 API compares a reused key's parameters with the original request's and returns an error if they differ.[^5] A loud failure beats a duplicate email, but the step is stuck: each retry asks the model again and is rejected again, so something has to hold the first attempt's parameters.

```python
def journaled_send(saver: Saver, receiver: Receiver, run_id: str,
                   step: str, model: ScriptedModel) -> str:
    """Replay returns the first attempt's recorded effect, not the model's new one."""
    if step not in saver.journal:
        saver.journal[step] = model.decide(step)   # record before sending
    return receiver.send(step_key(run_id, step), saver.journal[step])
```

The journal entry is written before the send. On replay the step finds it and sends the recorded parameters under the same key, so the receiver sees an exact repeat and dedupes it, and the model is never asked again. In the companion repo the journal is an in-memory dict; in production it has to reach durable storage before the request leaves the process, or a crash between the two loses it. Engineers who have built a transactional outbox, which writes the outgoing message in the same database transaction as the state change and sends it afterwards, will recognise the shape.

The receiver and the model are the companion repo's offline stand-ins: a provider that dedupes by key, and a model that rewords on replay.

```python
class ParamMismatch(Exception):
    """Same idempotency key, different parameters."""


class Receiver:
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.seen: dict[str, dict] = {}  # key -> params
        self.effects: list[dict] = []    # what really happened

    def send(self, key: str, params: dict) -> str:
        if key in self.seen:
            if self.strict and self.seen[key] != params:
                raise ParamMismatch(f"key {key!r} reused with different params")
            return "deduped"
        self.seen[key] = params
        self.effects.append(params)
        return "done"
```

```python
class ScriptedModel:
    def __init__(self, replies: list[dict]):
        self.replies = list(replies)
        self.calls = 0

    def decide(self, step: str) -> dict:
        reply = self.replies[min(self.calls, len(self.replies) - 1)]
        self.calls += 1
        return reply
```

What the companion repo's tests show, one test per claim, with step `b` standing in for the announcement step:

1. Steps run in order. Step `a` finishes and the saver records it. Step `b` raises partway, so `saver.done` is still `["a"]`.
2. The resume skips `a` and runs `b` again from its start. The call log reads `["a", "b", "b"]`: the finished step ran once, the step in flight twice.
3. Without a journal, the scripted model writes the announcement twice, first with the subject "Your listing is live", then "Your listing has launched". Keyed on content, the receiver records two effects: a duplicate email.
4. Keyed on the step, against a strict receiver, the second send raises `ParamMismatch` instead.
5. With the journal, the first send returns `"done"` and the replay returns `"deduped"`: one effect and one model call.

The step key assumes one effect per step. Step 7 sends an email and also pushes ad copy to a channel, so the key needs a third part, the call's position within the step, and the journal holds a list. Where the model decides how many calls a step makes, as in the half of step 7 where it names extra deliverables (see [Orchestrator-Workers](../composition/fan-out.md)), the position is only stable if the journal records the whole plan from the first attempt and the replay works through that recorded list.

### Cancel, budget stop, crash

Cancel is the polite version of a crash: a stop your code chooses, at a seam it picked, with a save. Temporal separates cancellation, a request the workflow receives and can clean up after, from termination, which stops it with no cleanup, and a long-running activity learns it was cancelled only when it sends a heartbeat, a periodic still-alive report, to the server.[^9] An agent needs the same two things: a cancel flag checked between steps and inside any long tool call, and a path that finishes or abandons the current step, saves, and stops. 12-Factor Agents asks for this in its sixth factor, that you can launch, pause and resume an agent through simple APIs.[^10]

The three ways a run stops leave three different states:

- **User cancel.** Honoured at a step boundary, the run stops with a checkpoint written and nothing in flight, so the resume is clean. A cancel that interrupts a send leaves the same state as a crash.
- **Budget stop.** Your code stops the run when spend reaches the limit set in 8.4 Controlling Cost. Checked between steps, it is as clean as a cancel. A hard cap that kills the process mid-step leaves the same state as a crash.
- **Crash.** The step in flight runs again on resume, and only the journal keeps its effects single.

You can see this boundary on your own screen. In Claude Code, let it edit one file, have a shell command create a second file, then run `/rewind`: the documentation says file checkpoints track Claude's edits, and that a file only the shell has touched is not tracked, so the first file goes back and the second stays as it is.[^11]

#### Wiring it to a provider

LangGraph handles the saver and the resume: compile the graph with a checkpointer and give every run a `thread_id`, the key its checkpoints are stored under. The checkpointer does not journal side effects, so the `announce` node still needs the key and the journal from above.

=== "LangGraph"

    ```python
    builder = StateGraph(ListingState)
    builder.add_node("announce", announce)
    builder.add_node("publish", publish)
    builder.add_edge(START, "announce")
    builder.add_edge("announce", "publish")
    builder.add_edge("publish", END)

    # Use a durable saver (Postgres, SQLite) in production, not InMemorySaver.
    graph = builder.compile(checkpointer=InMemorySaver())

    config = {"configurable": {"thread_id": "listing-aldsworth-42"}}
    graph.invoke({"sku": "LS-1001", "announced": False, "published": False}, config)
    # After a crash, graph.invoke(None, config) resumes from the last checkpoint.
    ```

With a direct OpenAI or Anthropic API call, wrap it in the plain saver above.

## Gotchas

1. **The world moved while the run was stopped.** A checkpoint holds the state as it was. An access token may have expired, or a person's approval aged out. On resume, re-check whatever the next step depends on: a repricer that resumes and writes a `price_cents` computed against yesterday's competitor price undercuts a price that has since moved. Do not resume a run whose single-use credentials are spent, or one whose step list a deploy has since changed, unless you migrate it deliberately.

2. **A poisoned checkpoint replays the poison.** State is input to the next step. If injected text (instructions an attacker smuggled in through a document or tool result) reached the state before the checkpoint, every resume feeds it back to the model, and the fix is to roll back to a clean checkpoint, not resume. A rollback restores local state only: effects already sent stay sent, so keep the journal outside what the rollback rewinds. One of the 2026 papers shows a rollback restoring authority the agent had already used or lost, so a spent permission works twice.[^6]

3. **Fat checkpoints.** Keep raw blobs such as the supplier's spec-sheet PDF out of the checkpoint and store a reference. A blob slows every write and, on resume, reloads stale payload into the model's context (see 5.4 Compaction).

4. **The outcome is unknown.** If the process died after the send and the receiver does not dedupe, or its reply never arrived, you cannot tell whether the effect happened. Ask the receiver for the request's status before resending, and stop for an operator when it cannot say. Never mint a new key to get past the doubt, because if the first send landed, a new key guarantees the duplicate.

5. **The fence expires.** Stripe's v1 API may prune keys after 24 hours.[^5] A run paused for two days and then resumed sends its journaled call to a receiver that has forgotten the key, and the effect happens again. Know your receiver's window before you promise that a long pause resumes safely; past it, treat the send as unknown.

6. **Checkpoints pile up.** A listing run's snapshots hold supplier and merchant data. Prune them on a schedule tied to the run's lifecycle; 8.5 Locks, PII & Identity covers what may be stored at all.

7. **An in-memory saver survives nothing.** `InMemorySaver` is for tests, and a durable saver protects a step only once its write has committed. Even then, **resume without a journal**, a durable saver and a working resume with no record of in-flight effects, sends every side effect in the interrupted step twice.

## In short

Save after every step with a durable saver; LangGraph and the engines hand it to you. Then find each step that touches the world, journal its call and key before the effect, and send it to a receiver that dedupes and, better, compares parameters. Re-check prices, tokens and approvals on resume. Move to a durable-execution engine when you need something outside your process to notice a dead worker and restart it (8.7 Deployment & Runtimes).

<small class="chapter-meta">**Maturity: Established (per-step checkpointing, durable-execution engines) · Emerging (agent-safe replay and rollback)** (savers and engines ship and are documented; the agent-specific hazards rest on vendor docs and two 2026 papers) · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: LangChain, "Persistence," LangGraph documentation. <https://docs.langchain.com/oss/python/langgraph/persistence>
[^2]: Temporal, "Workflows," Temporal documentation. <https://docs.temporal.io/workflows>
[^3]: Restate, "Key Concepts," Restate documentation. <https://docs.restate.dev/concepts/durable_execution>
[^4]: DBOS, "Architecture," DBOS documentation. <https://docs.dbos.dev/architecture>
[^5]: Stripe, "Idempotent requests," Stripe API reference. <https://docs.stripe.com/api/idempotent_requests>
[^6]: Zheng, Yang, Zhang, Quinn, "ACRFence: Preventing Semantic Rollback Attacks in Agent Checkpoint-Restore," arXiv:2603.20625 (CoDAIM workshop, 2026). Results come from attack testbeds, not field data. <https://arxiv.org/abs/2603.20625>
[^7]: Wu, Li, Jiang, Niu, Wang, Zhang, "Safe to Resume? Breaking Execution Continuity of Agent Execution via Rollback," arXiv:2608.29381 (2026). Preprint; the failures are demonstrated on testbeds. <https://arxiv.org/abs/2608.29381>
[^8]: LangChain, "Use time travel," LangGraph documentation. <https://docs.langchain.com/oss/python/langgraph/use-time-travel>
[^9]: Temporal, "Cancellation," Python SDK documentation. <https://docs.temporal.io/develop/python/workflows/cancellation>
[^10]: HumanLayer, "12-Factor Agents," factor 6. <https://github.com/humanlayer/12-factor-agents>
[^11]: Anthropic, "Checkpointing," Claude Code documentation. <https://code.claude.com/docs/en/checkpointing>

## See also

- [7.1 Retry & Graceful Degradation](which-failures-sink-the-ship.md), which needs the same effect fencing, because a retry also sends one call twice.
- [7.2 Observer](a-silent-failure-is-worse.md), for spotting the run that stalled and needs a resume.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md), where a run pauses on a checkpoint for a person, and where approval expiry lives.
- [3.3 Orchestrator-Workers](../composition/fan-out.md), whose model-sized fan-out is the hard case for keying effects per call.
- [2.1 Tool Use](../the-unit/tool-use.md), whose gotcha on idempotent retries is the same discipline at the scale of one call.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for "resume without a journal".

## Further reading

- LangChain, [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence): the library checkpointer, threads and checkpoints in one page.
- Temporal, [Workflows](https://docs.temporal.io/workflows): the journal-and-replay model as an engine runs it.
- Stripe, [Idempotent requests](https://docs.stripe.com/api/idempotent_requests): the reference contract for keys, parameter comparison and pruning.
- Wu et al., [Safe to Resume?](https://arxiv.org/abs/2608.29381): the failure modes of resuming an agent, tested.
