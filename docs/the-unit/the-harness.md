# 2.6 The Harness

*Everything in an agent that is not the model. One half is text the model reads and may ignore: the prompt, tool descriptions, instructions loaded for a task. The other half is code it cannot argue with: rules on which calls may run, your functions that run around each call, a walled-off place for tools to run, spending caps. A rule that must hold belongs in the second half.*

*Also called: harness engineering, the agent harness (OpenAI, Anthropic, LangChain, Böckeler); middleware (LangChain); hooks and permissions (Claude Code); guides and sensors (Böckeler); execution boundary, verification loop and context pipeline (Gulli and Nawalgaria, Building AI Agents).*

## Why you'd reach for it

In July 2025 a coding agent on Replit reportedly deleted a live production database during an active code freeze, despite repeated instructions not to make changes.[^aiid] The record does not say how the freeze was enforced. It does describe instructions that reached the model more than once, and a destructive command that ran anyway.

A model treats an instruction as one more thing in its context to weigh, and it only has to weigh it wrong once. Where a rule lives sets the price of that one mistake. Put a must-hold rule in the prompt and your worst case is the worst action the session can take. Put it in code that rules on each call before the tool runs, and for every call that code covers, your worst case is a refused call.

Take a bulk ingest at Stockwell, a fictional commerce platform whose Listing Studio pipeline turns supplier files into store listings. A merchandiser uploads a supplier's spreadsheet of a few hundred products, and an agent reads each row and writes a draft listing for a person to review. A `publish` tool writes to the live catalog that shoppers see. Every rule the team cares about fits in a system prompt (drafts only, never publish, flag odd prices, stop before the run gets expensive), and each is a sentence the model can lose.

A long run compacts its history (summarizes older turns so the conversation fits the context window), and the Claude Agent SDK warns that after compaction "specific instructions from early in the conversation may not be preserved".[^sdk-loop] A supplier's row is text the team did not write, and text in the context can read like an instruction ([Prompt Injection](../craft/prompt-injection.md) covers that attack). Lose the "drafts only" rule on row 300 and you have unreviewed listings live in the catalog, and a clean-up that starts with working out which ones.

The fix is to move each must-hold rule into a place your code owns. `publish` is left out of the session's tool list, so the model is never offered it. A rule check runs before every tool call and sends back a refusal the model can read. A hook, your own function the harness calls at a fixed point, checks each draft just after it is saved; it can report a bad draft but cannot take the write back. A spend cap ends the run from outside the loop. The "drafts only" line is pinned, marked so compaction always keeps it. The prompt still says all of it, so the model proposes fewer calls that get refused.

You need this when:

- the agent can call a tool whose effect you cannot cheaply undo: a write, a send, a publish, a delete;
- the run is long enough to compact, or it reads text you did not write;
- someone other than the model answers for what the run costs.

When the agent only reads and answers, and a person sees every answer before it goes anywhere, a system prompt and a step cap are enough.

## What it actually is

The harness is every part of an agent that is not the model: in LangChain's words, "every piece of code, configuration, and execution logic that isn't the model itself".[^anatomy] It has two halves. The **steering** half is text the model reads on each request: the system prompt, tool descriptions, [skills](skills.md) (instruction bundles loaded when a task needs them), rules re-injected after compaction. All it can do is make a good proposal likelier. The **enforcement** half is code that runs on each proposal: permission rules, hooks, the sandbox (a restricted environment the tool runs in), step and spend caps, and the compaction trigger, which decides when history is summarized and what survives it.

![A harness in two zones around one model. Steering, on top, is text the model reads and may ignore: the system prompt, tool descriptions, skills, and a pinned drafts-only rule. The model, drawn rounded, proposes a call such as write_draft with target live. Enforcement passes it through five checks in order: the session tool list, which does not offer publish; permission rules, where the first match in the list wins and no match means deny; pre-tool hooks, where the strictest verdict wins; the sandbox, where the tool runs; and a post-tool hook that checks the draft after it is already written. Each outcome returns to the model as a tool result. Before each model call a limits check ends the run at the 400-cent spend cap, so turn 9 never runs.](the-harness-seats.svg)

In *Building AI Agents*, Gulli and Nawalgaria frame the harness this way: the model proposes a call, and the harness decides whether to execute it.[^gulli] Structurally, almost all of this is engineering you already know: a policy enforcement point (a gate every call must pass), an interceptor chain (functions that each see the call), resource limits, an audit log. OWASP's advice on excessive agency (an agent allowed to do more than its job needs) could come from any access-control guide: "Implement authorization in downstream systems rather than relying on an LLM to decide if an action is allowed or not."[^owasp-mediation] What is new is the caller. It is non-deterministic, it reads your refusals, and it tries something else, so a refusal has to come back as a tool result the model can understand. In the Claude Agent SDK, a denied tool's rejection message arrives as the tool result, and Claude "typically attempts a different approach or reports that it couldn't proceed".[^sdk-loop]

Each check on a proposed call is a seat: a point in the run where code, and not the model, makes the decision. One kind of seat breaks the pattern, with a model sitting where code usually decides. Claude Code's auto mode has a background classifier review actions such as shell commands and network requests before they run, in place of asking you,[^cc-perms] and Codex can route approval requests to a reviewer agent with `approvals_reviewer = "auto_review"`.[^codex] That seat is the model deciding, with a model's error rate, and it is still Emerging. It cuts prompts on routine calls; keep the calls you cannot undo behind a rule or a [person](../craft/human-in-the-loop.md).

A framework is the kit you build a harness from, and Claude Code and the Claude Agent SDK come with one assembled ([Do You Even Need a Framework?](../foundations/do-you-need-a-framework.md) argues when the kit earns its keep). [The Agent Loop](the-agent-loop.md) is one part of the harness and owns stopping; [The Outer Loop](../composition/the-outer-loop.md) owns checking a finished run and retrying it. "Harness" also names the test harness that scores an agent; that sense belongs to [Evaluation](../craft/proving-it-works.md).

The mechanisms are Standard: between them, the Claude Code, Codex and LangChain docs cover mediated tool calls, hooks or middleware, sandboxes and caps as shipped features, and OWASP recommends mediation. In-run checks such as a linter and the compaction trigger are Established, though where to set the trigger and what a check should flag are still judgment calls. Claims about how much a harness is worth come from the teams selling the idea. LangChain says it moved its coding agent "Top 30 to Top 5 on Terminal Bench 2.0 by only changing the harness" (a public agent benchmark),[^anatomy] and OpenAI describes an internal product built with "0 lines of manually-written code".[^openai] Read both as existence proofs.

## How to do it

The companion code in `listing-studio/harness/` builds every seat around a small plain-Python agent loop. The model is any function that takes the messages and returns a `Turn` (its text, its tool calls, its cost), so the tests drive it with the scripted model in `scenario.py` and no network. `run` returns a `Result` (stop reason, messages, trace, spend).

Permissions come first. A rule has a verdict (deny, ask or allow), a tool name, and an optional test on the arguments. `decide` returns the first rule in the list that matches, and a call no rule matches is denied. `session_tools` builds the set of tools the model is offered at all.

```python
@dataclass(frozen=True)
class Rule:
    verdict: str                         # "deny" | "ask" | "allow"
    tool: str                            # tool name, or "*"
    when: Callable[[dict], bool] = lambda args: True


def decide(rules: list[Rule], tool: str, args: dict) -> tuple[str, str]:
    """First matching rule wins. No match means deny, never allow."""
    for rule in rules:
        if rule.tool in (tool, "*") and rule.when(args):
            return rule.verdict, f"rule: {rule.verdict} {rule.tool}"
    return "deny", f"no rule allows {tool}; default is deny"


def session_tools(all_tools: dict, wanted: set[str]) -> dict:
    """Absent beats denied: a tool left out of the session is never offered
    to the model, so there is nothing to ask for or argue about."""
    return {name: fn for name, fn in all_tools.items() if name in wanted}
```

The ingest's rules deny any `write_draft` whose `target` is anything but `draft`, ask a person about any price over 500,000 cents ($5,000), and allow the remaining draft writes and row reads. `publish` gets no rule, because it is not in the session. A tool left out is safer than a tool denied: a denial is a rule that has to stay correct as the rule list changes, and an absent tool has no rule to get wrong. OWASP's first mitigation says the same: "Limit the extensions that LLM agents are allowed to call to only the minimum necessary."[^owasp-limit]

Hooks are your functions at fixed points in the run: before a tool runs, after it returns, when the model says it is finished, before compaction. `combine` merges the rule's verdict with each pre-tool hook and keeps the strictest, so a hook can tighten a verdict and never loosen it (`SEVERITY` in `hook.py` ranks allow below ask below deny). `post_tool` checks a result before the model sees it.

```python
def combine(policy: tuple[str, str], hooks: list[PreHook], tool: str, args: dict):
    """Strictest verdict wins, so a hook's allow never beats a deny or an ask.
    A hook that raises counts as a deny: the run fails closed."""
    verdict, reason = policy
    for hook in hooks:
        try:
            out = hook(tool, args)
        except Exception as exc:                    # fail closed, on purpose
            out = ("deny", f"hook {hook.__name__} failed: {exc!r}")
        if out and SEVERITY[out[0]] > SEVERITY[verdict]:
            verdict, reason = out
    return verdict, reason


def post_tool(hooks: list[Callable[[str, dict], "str | None"]], tool, result):
    """Check a tool's output before the model sees it; a string is an error."""
    for hook in hooks:
        try:
            problem = hook(tool, result)
        except Exception as exc:
            problem = f"post hook {hook.__name__} failed: {exc!r}"
        if problem:
            return problem
    return None
```

Claude Code keeps the same guarantee, that a hook cannot loosen a rule, by a different route you can test yourself: a matching deny rule blocks a call even when a `PreToolUse` hook (its pre-tool hook) returned `"allow"`, and a matching ask rule still prompts.[^cc-perms] How rules rank against each other is Gotcha 2.

The companion's hooks fail closed: a hook that raises counts as a deny. Claude Code defaults the other way. A hook that exits with code 1 is a "non-blocking error", and "the action goes ahead, except for hooks whose failure blocks the action", such as one with `"onFailure": "block"`, and the docs' advice for a policy hook is "use `exit 2`".[^cc-hooks] Codex's reviewer sides with the companion: "Prompt-build, review-session, and parse failures fail closed."[^codex] In Claude Code, a policy hook that crashes with exit code 1 has stopped enforcing your policy for that call. Choose the failure mode on purpose, and test the crash path.

The sandbox is a separate seat with a different job. Rules and hooks decide whether a call runs and when to ask; the sandbox limits what a command can touch once it does. Rules written against command text cannot stand in for it; Claude Code's own docs warn that "Bash permission patterns that try to constrain command arguments are fragile".[^cc-perms] Anthropic adds that "effective sandboxing requires both filesystem and network isolation".[^sandbox] Supplier files belong in such a sandbox, so a row that talks the model into fetching a URL has nowhere to send it ([Sandboxing](../frontier/sandboxing.md) builds one).

Caps live in a `Limits` object the loop checks before every model call, so no text the model writes can raise them. Compaction archives the full history through a `pre_compact` callback, keeps pinned messages plus the most recent ones, and replaces the middle with one line. The Claude Agent SDK keeps rules another way: put them in CLAUDE.md, "because CLAUDE.md content is re-injected on every request".[^sdk-loop] Pinned or re-injected, every kept rule costs tokens on every call, so pin only the few that must survive ([Context Engineering](../foundations/context-engineering.md) covers the budget).

<details markdown><summary>The other seats: limits, compaction and the trace</summary>

```python
@dataclass
class Limits:
    max_steps: int = 20
    max_spend_cents: int = 500
    timeout_s: float = 60.0
    clock: Callable[[], float] = field(default=lambda: 0.0)   # inject in tests
    started: float = 0.0

    def stop_reason(self, steps: int, spent_cents: int) -> str | None:
        """Checked before every model call; the model cannot raise a cap."""
        if steps >= self.max_steps:
            return "step_cap"
        if spent_cents >= self.max_spend_cents:
            return "spend_cap"
        if self.clock() - self.started >= self.timeout_s:
            return "timeout"
        return None
```

```python
def compact(messages: list[dict], max_messages: int, keep_last: int,
            pre_compact: Callable[[list[dict]], None]) -> list[dict]:
    """Over the trigger, archive everything, then keep pinned messages
    plus the recent tail. The middle becomes one summary line."""
    if len(messages) <= max_messages:
        return messages
    pre_compact(list(messages))                  # archive before anything is lost
    pinned = [m for m in messages if m.get("pinned")]
    tail = [m for m in messages[-keep_last:] if not m.get("pinned")]
    dropped = len(messages) - len(pinned) - len(tail)
    summary = {"role": "user", "content": f"[{dropped} earlier messages compacted]"}
    return pinned + [summary] + tail
```

```python
class Trace:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def record(self, step: int, kind: str, name: str, outcome: str, reason: str = ""):
        self.events.append(
            {"step": step, "kind": kind, "name": name, "outcome": outcome, "reason": reason}
        )
```

</details>

Böckeler calls checks that run after a step sensors, which "observe after the agent acts"; her guides, which "anticipate the agent's behaviour and aim to steer it before it acts", are the steering half.[^boeckeler] `post_tool` is a sensor. Run such checks in the harness rather than as a tool, because a model can skip a tool it is offered.[^gulli] Write their output for the model to act on; OpenAI writes its lint messages "to inject remediation instructions into agent context".[^openai] Mechanical checks like these are settled; checks on behaviour are contested. Böckeler says leaning on AI-generated tests "puts a lot of faith" in them and "that's not good enough yet",[^boeckeler] and Anthropic records "Claude's tendency to mark a feature as complete without proper testing".[^effective]

<details markdown><summary>The loop with every seat wired in, showing where each check sits relative to the tool call</summary>

```python
def run(model, tools, rules, messages, limits, *, pre=(), post=(), on_stop=None,
        approve=lambda tool, args: False, archive=lambda msgs: None,
        max_messages=12, keep_last=4) -> Result:
    trace, steps, spent = Trace(), 0, 0
    while True:
        if (why := limits.stop_reason(steps, spent)) is not None:
            trace.record(steps, "limit", why, "stop")
            return Result(why, messages, trace, spent)
        turn = model(messages, list(tools))
        steps, spent = steps + 1, spent + turn.cost_cents
        messages.append({"role": "assistant", "content": turn.text})
        for call in turn.calls:
            if call.name not in tools:                    # absent, not denied
                out, outcome = f"error: no such tool {call.name!r}", "absent"
            else:
                verdict, reason = combine(decide(rules, call.name, call.args),
                                          list(pre), call.name, call.args)
                if verdict == "ask" and approve(call.name, call.args):
                    verdict = "allow"
                if verdict == "allow":
                    out, outcome = tools[call.name](**call.args), "allow"
                    if (bad := post_tool(list(post), call.name, out)):
                        out, outcome = f"error: {bad}", "post_blocked"
                else:
                    out, outcome = f"error: {reason}", verdict   # denial is a result
            trace.record(steps, "tool", call.name, outcome)
            messages.append({"role": "tool", "content": str(out),
                             "is_error": str(out).startswith("error:")})
        if not turn.calls:                                # model says it is done
            note = on_stop(messages) if on_stop else None
            if not note:
                return Result("done", messages, trace, spent)
            messages.append({"role": "user", "content": note})
        messages[:] = compact(messages, max_messages, keep_last, archive)
```

</details>

One scripted ingest run, two spreadsheet rows, 50 cents a turn against a 400-cent cap. Turn 8 is built to slip past the rules:

1. **Turns 1 to 4.** The model reads row 1, the Aldsworth sit-stand desk, and writes its draft at 129,900 cents; then reads row 2, a phone case, and writes its draft at 1,999 cents. Every call matches an allow rule.
2. **Turn 5.** The model calls `publish`. It is not in the session, so the model reads `error: no such tool 'publish'` and nothing runs.
3. **Turn 6.** The model calls `write_draft` with `target="live"`. The deny rule matches and the model reads `error: rule: deny write_draft`. The history is now 14 messages, past the trigger of 12, so the harness archives all 14 and compacts to the pinned "drafts only" rule, one line standing in for 9 dropped messages, and the last 4.
4. **Turn 7.** The model rewrites the desk at 999,900 cents ($9,999). The ask rule matches, the companion's default approver declines, and the model reads `error: rule: ask write_draft`.
5. **Turn 8.** The planted gap: no rule checks for a price below zero. The model writes the phone case at -1 cent. Neither the deny rule nor the ask rule matches, so the allow rule lets the tool run, and the post hook flags `bad draft fields for NV-PHONECASE-01`, which is what the model reads. The write has already landed: the stored phone case draft now says -1, replacing the valid 1,999-cent draft from turn 4.
6. **Before turn 9.** Spend has reached 400 cents. The run ends `spend_cap`, with the "drafts only" rule still the first message, and the ninth scripted turn never runs.

#### Wiring it to a provider

The raw Responses and Messages APIs (the plain model-call endpoints) have no permission or hook layer, so these examples use agent frameworks that do. Each refuses the live write; the first two leave `publish` out of the tool list, and the third blocks it with `disallowed_tools`, which the Agent SDK docs say "blocks listed tools, regardless of other settings".[^sdk-loop]

<details markdown><summary>The same deny rule in LangGraph, the OpenAI Agents SDK and the Claude Agent SDK</summary>

LangGraph's `wrap_tool_call` middleware sees every tool call before it runs:

```python
@wrap_tool_call
def enforce_policy(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    verdict, reason = decide(RULES, request.tool_call["name"], request.tool_call["args"])
    if verdict != "allow":                # an ask needs an approver; here: refuse
        return ToolMessage(content=f"error: {reason}",
                           tool_call_id=request.tool_call["id"], status="error")
    return handler(request)


agent = create_agent(
    "openai:gpt-6.2-sol",
    tools=[read_supplier_row, write_draft],     # publish is not in the list
    middleware=[enforce_policy],
)
```

The OpenAI Agents SDK attaches a tool input guardrail to one tool:

```python
@tool_input_guardrail
def enforce_policy(data):
    args = json.loads(data.context.tool_arguments or "{}")
    verdict, reason = decide(RULES, "write_draft", args)
    if verdict != "allow":
        return ToolGuardrailFunctionOutput.reject_content(f"error: {reason}")
    return ToolGuardrailFunctionOutput.allow()


@tool(tool_input_guardrails=[enforce_policy])
def write_draft(supplier_sku: str, title: str, price_cents: int, target: str = "draft") -> str:
    """Write a listing draft."""
    return f"draft saved for {supplier_sku}"


agent = Agent(name="Ingest", model="gpt-6.2-sol", tools=[write_draft])  # no publish
```

The Claude Agent SDK takes a `PreToolUse` hook and a list of disallowed tools:

```python
async def no_live_writes(input_data, tool_use_id, context):
    args = input_data["tool_input"]
    if args.get("target", "draft") != "draft":
        return {"hookSpecificOutput": {
            "hookEventName": input_data["hook_event_name"],
            "permissionDecision": "deny",
            "permissionDecisionReason": "Draft only: this session may not write live.",
        }}
    return {}                      # no opinion: normal permissions still apply


options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="mcp__studio__write_draft",
                                      hooks=[no_live_writes])]},
    disallowed_tools=["mcp__studio__publish"],
)
```

</details>

## Gotchas

1. **A post hook cannot undo a write.** Turn 8 shows it: the model was told the draft was bad, and the bad draft was saved anyway. Only a check that runs before the tool can turn a call into a refusal. A check that must hold before the side effect goes in a rule or a pre-tool hook (here, a deny on `price_cents <= 0`). Keep post hooks for what you can only see in the output.

2. **Rule order is your code's job.** Claude Code evaluates "deny, then ask, then allow", whatever order you wrote the rules in.[^cc-perms] The companion's `decide` walks the list in order, so a list with the allow rule for `write_draft` first would let the live write through. If you build your own, sort by verdict before matching or test the order.

3. **A mode changes what your rules do.** In Claude Code, `bypassPermissions` skips permission prompts except for a short list of actions, and `dontAsk` denies every call that would otherwise prompt.[^cc-perms] If bypass must never happen, set `permissions.disableBypassPermissionsMode` in managed settings, the admin-controlled layer users cannot override.

4. **Harness parts go stale.** Anthropic added context resets to its harness because Sonnet 4.5 wrapped up tasks early as its context filled; on Opus 4.5 the behaviour was gone, and "the resets had become dead weight".[^managed] Re-test those parts when you change models.


## In short

List the rules your agent must never break, and for each one name the code that enforces it: a tool left out of the session, a deny rule, a pre-tool hook, a sandbox, a cap. A rule with only a prompt sentence behind it is a request. Default to deny, make hooks fail closed, check before the write, and pin the few rules that must survive compaction.

<small class="chapter-meta">**Maturity: Standard** (mediated tool calls, sandboxes, hooks, caps) · **Established** (in-run computational checks, the compaction trigger) · **Emerging** (a model as approver; pruning stale harness parts) · *Who decides:* your code, on every call the model proposes · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^aiid]: AI Incident Database, Incident 1152, "LLM-Driven Replit Agent Reportedly Executed Unauthorized Destructive Commands During Code Freeze, Leading to Loss of Production Data" (2025-07-18). <https://incidentdatabase.ai/cite/1152/> Press accounts differ on the details; this chapter relies only on the incident record.
[^sdk-loop]: Anthropic, "How the agent loop works" (Claude Agent SDK docs), sections on tool permissions and automatic compaction. <https://code.claude.com/docs/en/agent-sdk/agent-loop> Checked 2026-11.
[^anatomy]: Trivedy, V., "The Anatomy of an Agent Harness," LangChain blog (2026-03-10). <https://www.langchain.com/blog/the-anatomy-of-an-agent-harness> The Terminal Bench result is LangChain's own, reported in an earlier post.
[^gulli]: Gulli, A. & Nawalgaria, A., *Building AI Agents: From Design Patterns to Production* (2026 public draft), ch. 15, "Agent Harness Engineering": the model proposes and the harness decides whether to execute; run checks in the harness rather than as tools. Paraphrased; the manuscript is a public draft under revision. <https://docs.google.com/document/d/1keM4ZbbfVmdsq3EAkbAliIegOpnnuBf-_KpD4oDOF0o>
[^owasp-mediation]: OWASP GenAI Security Project, "LLM06:2025 Excessive Agency," mitigation 7, complete mediation. <https://genai.owasp.org/llmrisk/llm062025-excessive-agency/>
[^owasp-limit]: OWASP GenAI Security Project, "LLM06:2025 Excessive Agency," mitigation 1, minimize extensions. <https://genai.owasp.org/llmrisk/llm062025-excessive-agency/>
[^cc-perms]: Anthropic, "Configure permissions" (Claude Code docs): rule evaluation order, permission modes, the warning on Bash argument patterns, and the precedence of rules over `PreToolUse` hook decisions. <https://code.claude.com/docs/en/permissions> Mode names and precedence details change between releases; checked 2026-11.
[^cc-hooks]: Anthropic, "Hooks reference" (Claude Code docs), exit-code behaviour, the exit-2 advice for policy hooks, and `onFailure`. <https://code.claude.com/docs/en/hooks> `onFailure` requires Claude Code v2.1.295 or later; checked 2026-11.
[^codex]: OpenAI, Codex docs, "Agent approvals and security." <https://learn.chatgpt.com/docs/agent-approvals-security> Formerly at developers.openai.com; checked 2026-11.
[^boeckeler]: Böckeler, B., "Harness engineering for coding agent users," martinfowler.com (2026-04-02). <https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html>
[^openai]: Lopopolo, R., "Harness engineering," OpenAI (2026-02-11). <https://openai.com/index/harness-engineering/> The code-volume figures are OpenAI's own account of an internal project.
[^sandbox]: Anthropic, "Making Claude Code more secure and autonomous with sandboxing" (2025-10-20). <https://www.anthropic.com/engineering/claude-code-sandboxing> The post also reports an 84% cut in permission prompts from Anthropic's internal usage, without saying how it was measured.
[^effective]: Anthropic, "Effective harnesses for long-running agents" (2025-11-26). <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>
[^managed]: Anthropic, "Managed Agents" (2026-04-08). <https://www.anthropic.com/engineering/managed-agents> One vendor's account of its own harness.

## See also

- [2.5 The Agent Loop](the-agent-loop.md): the loop is one component of the harness, and it owns stopping and the check on "done".
- [3.7 The Outer Loop](../composition/the-outer-loop.md): verify-and-retry across runs, the other loop your code owns.
- [4.6 Prompt Injection](../craft/prompt-injection.md): why text the agent reads cannot be trusted to steer it, and which harness limits hold.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md): what happens behind an ask verdict.
- [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md): what a check decides; this chapter covers where it runs and how it fails.
- [9.4 Sandboxing](../frontier/sandboxing.md): building the execution boundary.
- [2.1 Tool Use](tool-use.md) and [2.4 MCP](mcp.md): the tools every seat here sits in front of.
- [5.4 Compaction](../knowledge/compaction-and-the-window.md): what to keep when the trigger fires.
- [5.1 State, Not Memory](../knowledge/state-not-memory.md): durable state that outlives a run.
- [8.1 Observability](../production/seeing-inside.md): the companion's `Trace` records one event per decision (step, seat, tool, outcome); this is where those events go.
- [8.4 Controlling Cost](../production/controlling-cost.md): setting the spend cap.
- [8.5 Locks, PII & Identity](../production/locks-pii-identity.md): keeping credentials outside the session, where neither the model nor its tools' output can reach them.
- [9.1 Long-Running Agents](../frontier/when-you-want-autonomy.md): harnesses for runs that span many context windows.

## Further reading

- Böckeler, ["Harness engineering for coding agent users"](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html): the guides-and-sensors vocabulary, with a skeptic's eye on behaviour checks.
- Trivedy, ["The Anatomy of an Agent Harness"](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness): a component-by-component tour from a framework vendor.
- Anthropic, ["Configure permissions"](https://code.claude.com/docs/en/permissions) and ["Hooks reference"](https://code.claude.com/docs/en/hooks): a shipped harness's precedence rules, in full.
- OpenAI, ["Harness engineering"](https://openai.com/index/harness-engineering/): one team's account of building with an agent harness at scale.
- OWASP, ["LLM06:2025 Excessive Agency"](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/): the security case for mediating every call.
