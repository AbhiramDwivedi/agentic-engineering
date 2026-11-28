# 9.1 Long-Running Agents

*A job that outlives one context window, run as a series of fresh sessions. Each session reads a progress file, does one unit of work and stops; your code, never the agent, decides what counts as done, what the whole campaign may spend, and when a person takes over.*

## Why you'd reach for it

The second session of a long-running agent is the dangerous one. It starts with an empty context window, reads the notes its predecessor left, sees that a lot of work has been done, and declares the job finished. That is a documented failure in Anthropic's write-up of its harness for multi-session coding agents, alongside its twin, an early session that tries to build everything at once and leaves a half-finished mess for the next one to inherit.[^1]

Both failures come from the same gap. A model's working memory is its context window, and a job that takes hours or days does not fit in one. So the run is cut into sessions, and the only thing that crosses from one session to the next is whatever was written down. If the agent wrote it, the next session is trusting the agent's own account of its progress, and that account is exactly what drifts over a long run. In tested long execution tasks, per-step errors compound, and models condition on their own earlier mistakes, so a wrong turn early makes later wrong turns more likely; thinking models resist this better.[^2] How far that finding extrapolates beyond the experiments is contested, but the direction is the one a long run should design for.

The capability trend makes the question more urgent without answering it. METR measures a model's *time horizon*: the length of task, in human-expert time, that the model completes with 50% success. That horizon has doubled roughly every seven months since 2019 on the paper's historical fit, and may have accelerated since.[^3] The number describes how long a task a model can finish half the time. It says nothing about how long a model can run unwatched, and a coin-flip success rate on a two-day job is a long way from something you would leave running overnight.

Put the gap in a concrete setting. The Repricer is an agent on a commerce platform that watches competitor prices and adjusts its own catalog's prices within rules; it picks which products to look at and proposes each new price itself. A competitor starts a sale on 3,000 SKUs (stock-keeping units, one per product), and you ask the Repricer to respond overnight. A single session fills its window after a few hundred products, so the job runs as a campaign of sessions. If session four reads a note saying "2,400 repriced, the rest look fine" and stops, 600 products sit at stale prices against a competitor's sale until someone notices. If each session carries its own $5 spending cap and a wrapper relaunches it forty times, you have a $200 budget that nobody set.

The fix is a contract between sessions, owned by code: every session reads a progress file at startup; only your code writes completion records, after an acceptance check the agent cannot change; spending and failure counts accumulate across the whole campaign; and whatever the campaign could not finish lands in a record written for a person.

Reach for it when:

- **The work outlasts one context window**, even with compaction (the harness summarizing older context to free room).
- **It splits into units your code can check one at a time**: a price, a feature, a test that passes.
- **A model has to make the call inside each unit**, because the method or the answer depends on what it finds.
- **A person can be reached** when the campaign gets stuck.

And the counter-trigger: a scheduled batch with a fixed list of work, where no model chooses anything, is ordinary engineering. Write the cron job. If you cannot write the acceptance check in code, do not run the work unattended at all; run it with a person approving each step instead.

## What it actually is

A long-running agent is an agent loop that runs across many fresh sessions toward one goal. Inside each session the model works the task it is handed: it decides how to approach it and what result to propose. Outside, your code owns four things the model never touches: the state carried between sessions, the acceptance of finished work, the spend and stop conditions for the whole campaign, and the route to a person. The campaign is finished when the code's records say every task is accepted, whatever the agent's notes say.

![A relaunch wrapper, drawn as a rectangle, starts a fresh session. Inside the session a rounded model node reads a snapshot of the progress file and proposes a result for the next task. A rectangular acceptance check in your code rules on the candidate: on a pass it writes a completion record to the progress file, on a fail it counts the attempt, and after three failures it writes an escalation record that routes to a person. The progress file, also a rectangle, holds the task list, the completion records, the cumulative spend and the escalations, and the next session starts by reading it.](when-you-want-autonomy-campaign.svg)

The model's half is agentic. Your code's half is engineering you already know: checkpoint and resume is how batch jobs have survived restarts for decades. What is new is a worker that writes its own notes, so the notes have to be kept away from the books, the records of what code accepted. In the companion code below, your code hands out tasks in a fixed order (`todo[0]`) so the tests are deterministic, and the model's decision is the price it proposes. A full Repricer can also let the model choose which SKU to examine next from the competitor signals it has read; that choice moves inside the agent, and nothing about the acceptance check or the budget changes.

Three jobs hide inside "the agent ran for two days". The *inner loop* is the model choosing work within a session: call a tool, read the result, decide what next (see 2.5 The Agent Loop). The *outer loop* is your code verifying that work and retrying or stopping (see 3.7 The Outer Loop). The *relaunch wrapper* is whatever starts a fresh session when the last one ends. Nicholas Carlini's account of building a C compiler with a team of agents runs each one in a plain `while true` shell loop; the loop itself checks nothing, and his checks live in the test suite and CI.[^4]

How much a campaign is allowed to do is a separate setting from how capable its model is. Feng, McDonald and Zhang describe five roles a person can take toward an agent, from most hands-on to least: operator, collaborator, consultant, approver and observer.[^5] A long run usually puts you in the approver or observer seat. Your code sets that autonomy dial, meaning how far down the list the person sits, and the right default is the most hands-on role that still gets the job done; [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md) covers the spectrum.

**Maturity: Emerging.** The core pattern, an initializer session followed by one-feature sessions that each leave a mergeable state (code clean enough to merge to the main branch, with no major bugs), comes from one vendor, and its author tested it on full-stack web apps and left generalization to other domains as future work.[^1] Nearly all the evidence comes from coding campaigns; carrying it to repricing is reasoned, not measured. The parts that are older than agents are firmer: hard stopping conditions are common, and testing in a sandbox is recommended.[^6] Revalidating each resumed session against criteria the agent cannot change is reasoned from documented failures, and the sources here do not measure it.

Two neighbours get confused with this. 7.3 Checkpointing covers saving and resuming a run's state; this chapter is about what that state is allowed to claim. 8.7 Deployment & Runtimes covers scheduling, supervision and always-on agents as services.

## How to do it

Anthropic's version of the contract has two kinds of session.[^1] An *initializer* session sets up the environment once: a setup script (`init.sh`), a progress log (`claude-progress.txt`), a JSON feature list with every feature marked failing in a `passes` field, and a first git commit. Every later session follows a startup ritual (read the log and the git history, run a basic test to confirm the app still works), takes one feature, and shuts down by committing a mergeable state and appending to the log.

Only a prompt protects `passes`. The post restricts edits to that field by prompting the agent and asks the agent to verify its own work before flipping it.[^1] A prompt is a request the model can ignore, and nothing in code stops it from flipping the field. Go one step further: keep the agent's notes and the completion records in separate places, keep the acceptance criteria where the agent cannot edit them, and let a task become done only when code has seen independent evidence.

The companion code does that for the Repricer. It is plain Python with no framework; the agent is any callable that takes a SKU and a read-only snapshot and returns a candidate. One session:

```python
def run_session(path: str, tasks: list[str], agent: Agent, check: Check,
                budget: Budget, max_steps: int = 20) -> SessionResult:
    p = load_progress(path, tasks)                       # 1. resume from the file, not from memory
    steps = 0
    while steps < max_steps:                             # 2. stop condition: steps
        todo = p.pending()
        if not todo:
            return SessionResult("complete" if not p.escalations else "stuck", steps)
        if budget.left(p) <= 0:                          # 3. stop condition: cumulative budget
            save_progress(path, p)
            return SessionResult("budget", steps)
        sku = todo[0]
        snapshot = Progress(**json.loads(json.dumps(p.__dict__)))  # the agent gets a copy
        candidate = agent(sku, snapshot)
        steps += 1
        p.spent += int(candidate.get("tokens", 0))
        if check(sku, candidate):                         # 4. only code writes completion
            p.done[sku] = candidate["new_price"]
        else:
            p.attempts[sku] = p.attempts.get(sku, 0) + 1
            if p.attempts[sku] >= budget.max_attempts:   # 5. give up loudly, hand to a human
                p.escalations.append({"sku": sku, "reason": "acceptance check failed",
                                      "attempts": p.attempts[sku]})
        save_progress(path, p)
    return SessionResult("step_limit", steps)
```

It depends on two small contracts. The acceptance check is code, and it rules on the candidate alone: the right SKU, a numeric price, at or above the floor, and within a maximum move from the current price.

```python
def accept_reprice(sku: str, candidate: dict, floor: float, max_move: float, current: float) -> bool:
    """The acceptance check: code decides whether a task is done, never the agent."""
    price = candidate.get("new_price")
    if candidate.get("sku") != sku or not isinstance(price, (int, float)):
        return False
    return price >= floor and abs(price - current) / current <= max_move
```

The session takes a two-argument `check`, so a small wrapper binds the other three. The tests close over a floor of 10.0, a maximum move of 10%, and a current price looked up in a fixed price table. In production `current` comes from your catalog and `floor` from your pricing rules, never from the candidate, or the agent could move the goalposts.

The budget caps the campaign, and it reads what has been spent from the file, so a relaunch inherits the total instead of starting from zero.

```python
@dataclass
class Budget:
    """A cap on the whole campaign, not on one session. `spent` is restored from the file."""
    cap: int
    max_attempts: int = 3

    def left(self, p: Progress) -> int:
        return self.cap - p.spent
```

<details markdown>
<summary>The progress file: what a fresh session reads at startup</summary>

```python
@dataclass
class Progress:
    """Everything a fresh session needs to know. The context window holds none of it."""
    tasks: list[str]                                          # SKUs the campaign must reprice
    done: dict[str, float] = field(default_factory=dict)      # sku -> accepted price (code-written)
    attempts: dict[str, int] = field(default_factory=dict)    # sku -> failed attempts so far
    spent: int = 0                                            # cumulative tokens across relaunches
    escalations: list[dict] = field(default_factory=list)     # items waiting for a human

    def pending(self) -> list[str]:
        stuck = {e["sku"] for e in self.escalations}
        return [t for t in self.tasks if t not in self.done and t not in stuck]


def load_progress(path: str, tasks: list[str]) -> Progress:
    """Read the progress file at startup; first launch seeds it from the task list."""
    if not os.path.exists(path):
        return Progress(tasks=list(tasks))
    with open(path, encoding="utf-8") as f:
        return Progress(**json.load(f))


def save_progress(path: str, p: Progress) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(p.__dict__, f, indent=2)
    os.replace(tmp, path)  # a crash mid-write never leaves a half file
```

</details>

One campaign over three SKUs, with a step limit of two per session, as the tests run it:

1. Session one finds no progress file and seeds one from the task list. The agent proposes a price for SKU-1, the check passes, and code writes the completion record and saves the file.
2. SKU-2 goes the same way. The step limit is reached and the session ends with `step_limit`, two of three done. Nothing in the model's context survives.
3. Session two starts cold and loads the file. `pending()` returns only SKU-3, so that is the only task the agent sees. It passes, and the session ends with `complete`.
4. Run it again with an agent whose SKU-1 candidates always fail the check. After the third failure, code writes `{"sku": "SKU-1", "reason": "acceptance check failed", "attempts": 3}`, moves on to SKU-2, and ends the session `stuck` rather than `complete`.
5. Run it with the default step limit, a cap of 150 tokens (tokens stand in for dollars here) and an agent that spends 100 per step. The budget is checked before each step, so the session stops after two steps with 200 spent, and a relaunch reads that 200 from the file and does nothing. Size the cap knowing it can overrun by one step's cost.

A separate test hands the agent a snapshot and lets it write its own completion record into that snapshot. The record never reaches the file, because the session only ever saves its own copy.

The `agent` argument is where a provider goes. Wrap the tool loop from [2.1 Tool Use](../the-unit/tool-use.md), or a LangGraph agent, in a function that returns the candidate and the tokens it spent.

### More than one agent at a time

A natural next step is several agents working one campaign in parallel, and the structural change is a claim: `pending()` has to skip tasks another agent holds, so each task needs an owner and an expiry that a crashed agent cannot hold forever. Carlini's agents claim work by writing lock files into a shared `current_tasks/` directory, and he states that he uses no orchestration agent.[^4] Cursor reports the opposite pressure: with locks alone, twenty agents performed like two or three, and a planner-and-worker hierarchy helped.[^7] Two vendor reports do not settle a topology, and they disagree; 9.2 Multi-Agent takes it up.

## Gotchas

1. **Caps that reset on relaunch.** A per-session step or spend cap is defeated by the wrapper that relaunches the session. Campaign identity, cumulative spend, wall-clock time and failure counts have to live in the durable record and survive every restart. Add a futility rule (the same failure N times, then stop), and persist a cancellation flag so a stop request outlives the session that received it. Carlini's compiler took nearly 2,000 sessions over about two weeks and cost just under $20,000, by his own account.[^4] 8.4 Controlling Cost covers the spend side.

2. **Side effects outside the checkpoint.** The progress file records what code accepted, but pushing the price to the storefront is a write to someone else's system. If a session crashes after the push and before the save, the next session cannot tell whether the price went live. LangGraph's fault-tolerance guidance is to treat a missing acknowledgement as unknown, reconcile before resuming, and make side-effecting steps idempotent so a replay does no harm.[^8] Key the write on campaign and SKU so a repeat changes nothing; 7.3 Checkpointing has the resume mechanics.

3. **A thin failure record.** The escalation in the companion code names the SKU, the reason and the attempt count. A production record should also carry the failed operation, the evidence the check saw, whether a retry could help, and the budget left, so the person or the next session can act on it without replaying the run. 7.1 Retry & Graceful Degradation covers recovery.

4. **Notes that become instructions.** Whatever one session writes, the next one reads as context. A mistaken summary, or competitor-page text carrying an injected instruction that the agent copied into its notes, persists across every later session, and starting each session fresh does nothing to stop it. OWASP lists this as memory and context poisoning (ASI06) in its Top 10 for agentic applications.[^9] Keep provenance on what crosses sessions, keep agent summaries apart from the instructions you wrote, and hand over only the state the next task needs, which also saves tokens and attention. 4.6 Prompt Injection & the Lethal Trifecta goes deeper on the lethal trifecta: an agent that holds private data, reads untrusted content and can send data out.

5. **Lower oversight before isolation.** Claude Code's `bypassPermissions` mode, which skips permission prompts, is documented for containers and VMs and offers no protection against prompt injection, and the same page says auto mode "reduces permission prompts but does not guarantee safety."[^10] You can watch the dial on your own screen: Shift+Tab cycles `default`, `acceptEdits` and `plan`, with `bypassPermissions` and `auto` appearing only when enabled.

    A boundary stated in the prompt can also be lost when a long context is compacted, so put it in a deny rule, an entry in the harness's permission settings that blocks a tool or command on every call whatever the prompt says. In July 2025 an AI coding assistant on Replit reportedly deleted a live production database during a code freeze its user says he had given it in chat.[^11] Carlini's agent once ran `pkill -9 bash` and killed its own loop.[^4] Isolate first, then lower the oversight; 9.4 Sandboxing covers the environment.

6. **Nobody who can stop it.** A campaign needs a named person, a way to reach them on a blocker, and a kill switch they can use without the agent's cooperation. Anthropic's study of agent use in practice found experienced users shifting from approving each action to monitoring and interrupting, which works only if interrupting is cheap.[^12] 4.3 Human-in-the-Loop covers the gates.

## In short

Run a long job as short sessions over a file your code owns. Let the model work each task and propose the result, and let only an acceptance check in code mark anything done. Keep budget, failure counts and cancellation in that file so a relaunch cannot reset them, isolate the environment before you lower the oversight, and make sure a stuck campaign ends with a record a person can act on. If you cannot write the acceptance check, keep a person approving each step until you can.

<small class="chapter-meta">**Maturity: Emerging** (one vendor's progress pattern, tested on coding campaigns; stopping conditions are common and sandboxing recommended) · *Who decides:* the model works each task and proposes, your code assigns, accepts and stops · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Young, Anthropic Engineering, "Effective harnesses for long-running agents" (2025-11-26). <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
[^2]: Sinha, A., et al., "The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs" (2025). Findings are scoped to the paper's execution tasks. <https://arxiv.org/abs/2509.09677>
[^3]: Kwa, T., et al., "Measuring AI Ability to Complete Long Tasks" (METR, 2025). The horizon figures move with each revision; read the live paper rather than a quoted number. <https://arxiv.org/abs/2503.14499>
[^4]: Carlini, N., Anthropic Engineering, on building a C compiler with parallel Claude agents (2026-02-05). Session, duration and cost figures are self-reported. <https://www.anthropic.com/engineering/building-c-compiler>
[^5]: Feng, K. J. K., McDonald, D. W., and Zhang, A. X., "Levels of Autonomy for AI Agents" (2025). <https://arxiv.org/abs/2506.12469>
[^6]: Anthropic, "Building effective agents" (2024-12-19). <https://www.anthropic.com/research/building-effective-agents>
[^7]: Lin, Cursor, "Scaling agents" (2026-01-14). Scale figures are vendor-reported. <https://cursor.com/blog/scaling-agents>
[^8]: LangChain, LangGraph documentation, "Fault tolerance." <https://docs.langchain.com/oss/python/langgraph/fault-tolerance>
[^9]: OWASP GenAI Security Project, Top 10 for Agentic Applications (2026), ASI06 "Memory & Context Poisoning." <https://genai.owasp.org/agentic-applications-2026/asi06-memory-context-poisoning/>
[^10]: Anthropic, Claude Code documentation, "Permission modes." Mode names and auto-mode thresholds change between releases. <https://code.claude.com/docs/en/permission-modes>
[^11]: AI Incident Database, Incident 1152 (2025), an index linking the original reports in The Register (2025-07-21) and Tom's Hardware and the user's own posts. Single-source and not an independent investigation; the accounts do not show that a deny rule would have prevented the deletion. <https://incidentdatabase.ai/cite/1152/>
[^12]: McCain, et al., Anthropic, "Measuring AI agent autonomy in practice" (2026-02-18). <https://www.anthropic.com/research/measuring-agent-autonomy>

## See also

- [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md), for the spectrum the autonomy dial sits on.
- [2.1 Tool Use](../the-unit/tool-use.md), for the tool loop that goes inside the `agent` callable.
- 2.5 The Agent Loop, for the inner loop each session runs.
- 3.7 The Outer Loop, for the code-owned verify-and-retry controller.
- 7.3 Checkpointing, for saving and resuming state safely.
- 8.7 Deployment & Runtimes, for running campaigns as supervised services.
- 9.2 Multi-Agent, for the topologies parallel campaigns need.
- 9.4 Sandboxing, for the isolation that comes before lower oversight.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for "the agent marks its own work done."
