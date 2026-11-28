# 4.3 Human-in-the-Loop

*Your code decides which actions need a person, the person sees exactly what will run and can change it, and their yes is bound to that one action.*

*Also called: HITL, approval gate, human approval, human oversight, human-on-the-loop, escalation, tool confirmation (Google ADK), permission prompt (Claude Code), `needs_approval` (OpenAI Agents SDK), `interrupt` (LangGraph), "contact humans with tool calls" (12-Factor Agents).*

## Why you'd reach for it

Anthropic reports that people using Claude Code accept 93% of the permission prompts it shows them.[^automode] The post states no method or sample, and the figure measures acceptance only. If most of the actions that triggered a prompt were harmless, saying yes nine times in ten is the right behaviour. What the number cannot tell you is whether the rare bad action got the same quick yes.

Deciding where the person goes fails in two directions. Put a person in front of too many actions and, if browser-warning field studies carry over,[^warningland] they start clicking through and the gate turns into a log entry with an extra click. Put them in front of too few, or let the model decide when to ask, and an irreversible action runs with nobody in the path. Pausing a run is the easy part. The hard part is choosing the few actions that deserve a person, showing them what will happen, and making their answer apply to the action that runs and nothing else.

Take a pricing step in Listing Studio, the pipeline our examples use to turn a supplier's product feed into a live store listing. The step sets the price of the Aldsworth standing desk, whose MAP (minimum advertised price, the floor the brand lets a retailer advertise) is 39900 cents ($399.00; every price here is in cents). [4.6 Prompt Injection](prompt-injection.md) asks what an attacker can make this step do; this chapter asks who signs off on a legitimate change. A model proposes the price, and code sorts it into three bands. Below 39900 the change is refused outright, because nobody should be asked to approve a price the supplier agreement forbids. From 39900 up to 42899 the price sits close enough to the floor that a merchandiser, the person who owns the category's pricing, decides. At 42900 and above it applies without anyone. Get this wrong and a live listing carries a price nobody chose, and if a merchandiser approved 41000 while a different number was written, the log shows a signed decision nobody made.

You need this when:

- the action is irreversible or expensive to undo (a payment, a refund, a live price, a deletion, a message to a customer);
- the action leaves your system or acts for someone outside it;
- policy or a contract says a named person must decide;
- you are still building confidence in an agent that will later run with less supervision.

You do not need a person when a rule can decide the case on its own. A price below the floor needs a refusal, which [4.4 Guardrails & Safety](guardrails-and-safety.md) covers, and a reversible draft nobody sees until review needs nothing.

## What it actually is

A human-in-the-loop gate is a pause your code inserts in front of a consequential action. Code decides the action needs a person, saves the pending action with a digest (a hash of its exact name and arguments), and stops. The run resumes only when a person answers who is not the requester (the identity that asked for the action, here the repricing service); proving who they are is your identity layer's job. Before anything executes, code checks the answer against the digest and re-runs the policy on any edit. The person can approve, reject with a reason the model gets back, or edit the action.

![The Aldsworth desk pricing step, MAP floor 39900 cents. The model proposes set_price at 41000. Code sorts prices into three bands: below 39900 refused and 42900 and above applied, both with no person; 41000 lands in the middle band and is saved as a pending request with a digest of the exact action. A merchandiser, never the requester, approves, rejects with a reason, or edits. On resume code checks the digest and re-bands any edit, then writes 41000 once. Rounded shapes are the model, rectangles your code.](human-in-the-loop-gate.svg)

Your code decides whether a person is needed, by a rule on the tool, its arguments, and the amount. The model may ask for one. HumanLayer's 12-Factor Agents, a set of agent design principles, makes that its seventh factor, "contact humans with tool calls":[^12factor] the model emits a `request_human_input` intent like any other tool call. Treat that call as a signal your code weighs, never the control itself. Structurally this is the two-person rule a payments system has used for decades, with requester and approver kept apart. What is new is the requester, a model that can propose prices faster than anyone can read them and phrase each one persuasively.

The approval gate is one of three places a person can sit. Before the action, they approve it. During the run, they watch and interrupt, which is the steering interface in [6.3 Streaming & Agent UX](../io-boundary/streaming-and-agent-ux.md). After the fact, they audit a sample, which belongs to [4.2 Evaluation](proving-it-works.md) and [8.6 Governance & Compliance](../production/governance-and-compliance.md), the latter including the EU AI Act's human-oversight duties. In Anthropic's study of Claude Code sessions, people with fewer than 50 sessions ran with full auto-approve in roughly 20% of sessions, and by 750 sessions in over 40%, while their interrupt rate rose from about 5% to about 9% of turns. Experienced users traded approving each action for watching and stepping in; the authors write that effective oversight "doesn't require approving every action but being in a position to intervene when it matters."[^autonomy] A gate is for the small set of actions where stepping in afterwards is too late.

Gating consequential actions is standard practice. OWASP's entry on excessive agency lists "require user approval" for high-impact actions,[^owasp] OpenAI's agent guide says sensitive, irreversible, or high-stakes actions "should trigger human oversight until confidence in the agent's reliability grows,"[^openai-guide] and the major agent SDKs each ship a pause and resume. Keeping the gate meaningful is much less settled. The evidence that people keep reading prompts comes from browser warnings and decision-aid studies, plus vendor-reported numbers; editing an action before approving it has no common format across the SDKs; and the newest idea, a model classifier doing the approving, has a published stress test against it.

Three neighbours get confused with this. A guard that refuses a price below the floor is code acting alone and lives in [4.4](guardrails-and-safety.md). The outer loop in [3.7](../composition/the-outer-loop.md) decides when a run gives up; the give-up lands here, as an escalation a person receives. Routing on the model's confidence is [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md).

## How to do it

The gate is a pure function that returns `auto`, `ask`, or `deny`. The request is the record the person sees, carrying the digest and an ID that doubles as the idempotency key (the value that makes a second identical resume a no-op). `check_price`, the MAP check, comes from the companion repo's `pricing.tools` module.

```python
AUTO_FROM_CENTS = 42900  # at or above this the change applies without a person


def gate_policy(action: str, args: dict) -> str:
    """Return "auto", "ask" or "deny". Deny is checked first and nothing below
    can widen it: a person is never asked to approve a price the floor refuses."""
    if action != "set_price":
        return "ask"  # an action we have no rule for goes to a person
    price = args["proposed_price_cents"]
    if not check_price(args["supplier_sku"], price)["ok"]:
        return "deny"  # below the 39900 MAP floor: code refuses, no human in the path
    return "auto" if price >= AUTO_FROM_CENTS else "ask"
```

```python
def action_digest(action: str, args: dict) -> str:
    """Hash of the exact action. An approval carries this, so approving one
    price cannot be replayed against another."""
    canonical = json.dumps({"action": action, "args": args}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


class ApprovalRequest(BaseModel):
    request_id: str  # the idempotency key, and the thread the step resumes on
    requester: str
    action: str
    args: dict
    digest: str
    expires_at: float
    status: str = "pending"  # pending | approved | rejected | expired | applied
    decided_by: Optional[str] = None
    reason: Optional[str] = None
    edited_args: Optional[dict] = None
```

The step holds the pause and the resume. `fx` records the step's effects for the tests: `fx.before_pause` stands in for an audit write placed before the pause, and `fx.applied` holds the prices actually written. `Effects`, `Outcome`, and `TTL_SECONDS` (one hour) are short definitions in `human_in_the_loop/pause_resume.py`.

```python
def reprice_step(store, request_id, requester, args, fx: Effects) -> Outcome:
    """Runs from the top every time it is called, first run and every resume."""
    fx.before_pause += 1  # a write before the pause happens again on resume
    action = "set_price"
    band = gate_policy(action, args)
    if band == "deny":
        return Outcome("refused", "below the MAP floor")
    if band == "ask":
        req = store.load(request_id)
        if req is None:
            req = ApprovalRequest(
                request_id=request_id, requester=requester, action=action, args=args,
                digest=action_digest(action, args), expires_at=store.now() + TTL_SECONDS)
            store.save(req)
        if req.digest != action_digest(action, args):
            return Outcome("refused", "arguments changed since the request was made")
        if req.status == "pending":
            return Outcome("paused", req.digest)  # the person sees this
        if req.status in ("rejected", "expired"):
            return Outcome(req.status, req.reason or "no decision")
        if req.status == "applied":
            return Outcome("applied", "already applied")  # duplicate resume writes nothing
        args = req.edited_args or args
        req.status = "applied"
        store.save(req)
    fx.applied.append(args["proposed_price_cents"])  # the write that must happen once
    return Outcome("applied", str(args["proposed_price_cents"]))
```

The store keeps requests in a JSON file, so a different process can pick one up, and it is where a decision is checked: by someone other than the requester, against the digest, with any edit re-banded.

```python
class ApprovalStore:
    def __init__(self, path: str, now: Callable[[], float] = time.time):
        self.path, self.now = path, now

    def _all(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, encoding="utf-8") as f:
            return json.load(f)

    def save(self, req: ApprovalRequest) -> None:
        data = self._all()
        data[req.request_id] = req.model_dump()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, request_id: str) -> Optional[ApprovalRequest]:
        raw = self._all().get(request_id)
        if raw is None:
            return None
        req = ApprovalRequest(**raw)
        if req.status == "pending" and self.now() >= req.expires_at:
            req.status = "expired"  # silence resolves to reject, never to approve
            self.save(req)
        return req

    def decide(self, request_id, approver, digest, approve=True, reason=None, edited_args=None):
        req = self.load(request_id)
        if req.status != "pending":
            raise ApprovalError(f"request is {req.status}")
        if approver == req.requester:
            raise ApprovalError("the requester cannot approve their own request")
        if digest != req.digest:
            raise ApprovalError("stale approval: it was given for a different action")
        if approve and edited_args is not None:
            if gate_policy(req.action, edited_args) == "deny":
                raise ApprovalError("edit refused: below the floor")  # re-banded after the edit
            req.edited_args = edited_args
        req.status = "approved" if approve else "rejected"
        req.decided_by, req.reason = approver, reason
        self.save(req)
```

Two bands need no person: at 39899 the step returns `refused` and saves nothing, and at 42900 it writes the price. The middle band, traced through one companion test:

1. The model proposes 41000. The gate returns `ask`, the step saves a pending request with the digest of `set_price` at 41000, and returns `paused` with that digest, which is what the merchandiser's screen shows.
2. A fresh `ApprovalStore`, standing in for a different process, reads the request back from the file, and the merchandiser approves it with the digest they were shown.
3. The step runs again from the top. `fx.before_pause` now reads 2, because that line ran on the first call and again on resume, which is harmless for a counter and a duplicate for a real write. The request is approved, so the step marks it `applied` and writes 41000 once.
4. A duplicate resume finds the request already `applied`, returns "already applied", and writes nothing.

An approval that is not bound to the exact arguments approves whatever runs next, so the refusals get the most tests. An edit from 41000 to 42900 applies 42900; the edit is the person's answer to a request that needed one. An edit to 39899 is refused with "edit refused: below the floor" and the request stays `pending`, so the merchandiser can try again. When the person decides, an approval carrying the digest for 40100 on a request for 41000 is refused as stale. When the step resumes, arguments of 40100 after the person approved 41000 return `refused` with "arguments changed since the request was made", and nothing is written. The requester cannot approve its own request. A request left past its one-hour lifetime comes back `expired`, writes nothing, and a late approval is refused.

> **In the companion repo.** `listing-studio/tests/test_human_in_the_loop.py` runs every outcome above offline, with an injectable clock for the expiry.

**Reply shapes.** Approve and reject are the minimum. A rejection should come back to the model as a structured tool result, here `{"status": "rejected", "detail": "hold for the sale"}`, so the model can propose something else instead of retrying blind. Editing is the most useful shape and the least settled: LangGraph has no edit format of its own, so your node reads whatever the resume value carries, validated only if you give `interrupt()` a schema; the OpenAI Agents SDK offers approve and reject only and warns servers not to accept replacement arguments from the client;[^openai-sdk] Google's ADK passes a `payload` back to the tool.[^adk] Treat an edited value as fresh input: authenticate who sent it, validate it, and run the policy on it again, which is why the edit to 39899 is refused. Reasons and edits also go back into the prompt, so pass them as capped, structured fields rather than free text.

**What the person sees.** Show the exact action and its validated arguments, the before and after values, whether the action can be undone, and a flag on anything that came from an untrusted source, such as a supplier's spec sheet. Untrusted text shown to a person is still data: cap its length and keep it out of the prompt, as [4.6](prompt-injection.md) shows.

**From one gate to many.** In production, key each request by the tool call's ID, so a duplicate resume of that call finds the same request; a re-issued call gets a new ID. Give each queue an owner and a deadline, and decide in advance what the deadline does; here silence resolves to reject, so the current price stays. An escalation from [3.7](../composition/the-outer-loop.md) or a failed listing from [3.1 Prompt Chaining](../composition/prompt-chaining.md) lands in the same queue and carries what was tried, why it stopped, and the safe default if nobody answers.

#### Wiring it to a provider

The tabs below are compile-checked and reuse the tested functions. LangGraph's `interrupt()` pauses inside a node and saves state through the checkpointer under the `thread_id`; resuming with `Command(resume=...)` re-runs the node from its start, and `interrupt()` then returns the person's answer.[^langgraph] `PriceState` is a two-field `TypedDict` (`args`, `result`) in the illustration file. The Responses tab stops at the pause or hands back the immediate outcome.

The OpenAI Agents SDK has the same shape built in: mark a tool with `needs_approval`, read pending calls from `result.interruptions`, call `state.approve()` or `state.reject()`, and pass the state back to `Runner.run`.[^openai-sdk] Google's ADK uses `require_confirmation`, which its documentation marks unsupported on two of its session services and experimental outside Python.[^adk]

=== "LangGraph"

    ```python
    def approve_node(state: PriceState) -> dict:
        args = state["args"]
        band = gate_policy("set_price", args)
        if band == "deny":
            return {"result": {"status": "refused"}}
        if band == "ask":
            answer = interrupt({"digest": action_digest("set_price", args), "args": args})
            if answer["digest"] != action_digest("set_price", args):
                return {"result": {"status": "refused", "detail": "stale approval"}}
            if not answer["approve"]:
                return {"result": {"status": "rejected", "detail": answer.get("reason")}}
            args = answer.get("edited_args") or args
            if gate_policy("set_price", args) == "deny":
                return {"result": {"status": "refused", "detail": "edit below the floor"}}
        return {"result": {"status": "applied", "price": args["proposed_price_cents"]}}


    builder = StateGraph(PriceState)
    builder.add_node("approve", approve_node)
    builder.add_edge(START, "approve")
    builder.add_edge("approve", END)
    graph = builder.compile(checkpointer=InMemorySaver())  # use a durable saver in production

    config = {"configurable": {"thread_id": "reprice-aldsworth-1"}}  # same id on resume
    # graph.invoke({"args": {...}, "result": None}, config)   -> pauses, returns __interrupt__
    # graph.invoke(Command(resume={"digest": d, "approve": True}), config)
    ```

=== "OpenAI Responses API"

    ```python
    def run_until_pause(store: ApprovalStore, tools: list, user_text: str, requester: str):
        fx = Effects()
        response = client.responses.create(model=MODEL, input=user_text, tools=tools)
        for item in response.output:
            if item.type != "function_call" or item.name != "set_price":
                continue
            args = json.loads(item.arguments)
            outcome = reprice_step(store, item.call_id, requester, args, fx)
            if outcome.status == "paused":
                return {"paused": item.call_id, "response_id": response.id}  # return to the caller
            # Otherwise hand the outcome back; a rejection reason reaches the model here.
            return client.responses.create(
                model=MODEL, previous_response_id=response.id, tools=tools,
                input=[{"type": "function_call_output", "call_id": item.call_id,
                        "output": json.dumps(outcome.as_tool_result())}])
    ```

## Gotchas

**People stop reading.** I know of no public study that measures how often people wrongly approve agent prompts, so the evidence is borrowed. Akhawe and Felt observed more than 25 million browser security warnings and found click-through ranged from about a tenth of Firefox's malware and phishing warnings to 70.2% of Chrome's SSL warnings; the design of the warning moved behaviour.[^warningland] Invariant Labs notes that many agent users already choose "Always Allow" and stop watching individual actions.[^invariant] Ask less, and ask about consequences: a prompt that says "set the Aldsworth desk to $410.00, $11 above the floor, reversible" gets read where a stream of file-write confirmations does not. Allow-list the low-risk class outright, and make rejection as cheap as approval.

**A rationale can make it worse.** Bansal and colleagues found that AI explanations "increased the chance that humans will accept the AI's recommendation, regardless of its correctness."[^bansal] Leave the model's case for 41000 off the approval screen and show the diff and the consequence.

**Resume re-runs the step.** LangGraph's docs say the node restarts from the beginning on resume, so "any code before the interrupt runs again," and side effects before it should be idempotent.[^langgraph] Put writes after the pause, or make them safe to repeat. LangGraph also warns against wrapping `interrupt()` in a bare `try/except`, which swallows the pause.

**Saved state is not proof of anything.** The OpenAI Agents SDK warns that `RunState.from_json()` does "not authenticate the snapshot or the person submitting it," and tells servers not to accept replacement arguments, approval records, or serialized state from the client.[^openai-sdk] Keep the pending request on the server and take only the decision and the digest from the approver.

**An instruction is no gate.** SaaStr's founder says he told Replit's agent "eleven times in ALL CAPS" not to make changes, and that it then deleted his production database;[^register] as [2.6 The Harness](../the-unit/the-harness.md) argues, an instruction in a prompt is advice to the model, and only code in the execution path stops the call.

**The gate can sit where nothing reaches it.** In Claude Code, permission rules are evaluated deny, then ask, then allow, and a broad allow cannot carve an exception out of a deny.[^cc-permissions] In its Agent SDK, a call auto-approved by an allow rule or a permissive mode never reaches the `canUseTool` callback, so an approval check placed there is "silently bypassed."[^sdk-permissions] Put your gate in the execution path of the tool itself, as `reprice_step` does, and test it: give the tool a blanket allow and check that 39899 is still refused.

**A classifier as approver is a trade.** Anthropic's auto mode replaces the prompt with a model classifier. On 10,000 real internal actions its false positive rate (safe actions it blocked) was 0.4%. On 52 overeager actions, ones that went further than the user wanted, its false negative rate (risky actions it let through) was 17%, and Anthropic says it "is not a drop-in replacement for careful human review on high-stakes infrastructure."[^automode] An independent stress test by Ji and colleagues, a preprint, measured an 81.0% end-to-end false negative rate on 128 deliberately ambiguous DevOps prompts, and more than a third of the state-changing actions fell outside what the classifier checks.[^ji] The two workloads are different, so neither number is "the" rate. Use a classifier to thin out low-stakes prompts, and keep a person on the band where the cost of a miss is a live price.

**Use confidence to add review.** A model's confidence is calibrated when it matches how often the model is right, so that answers given at 80% are right about 80% of the time. Kadavath and colleagues found models can partly predict what they know but "struggle with calibration" on new tasks.[^kadavath] Use low confidence to add a person, and keep high confidence from removing one on a consequential band.

## In short

Write the rule that decides when to ask in code, on the tool, the arguments, and the amount, and keep it to the actions you cannot take back. Refuse what policy forbids before anyone is asked. Save the pending action with a digest of its exact arguments, resume from durable state, re-run the policy on the original and on any edit, and apply each approved request once. Show the approver the action, the diff, and whether it can be undone, without the model's argument for it. Let silence mean no. Then measure: if people approve nearly everything, ask less often before you conclude they are careless.

<small class="chapter-meta">**Maturity: Standard (approval gates and pause/resume) / Emerging (classifier-as-approver)** (gating is in OWASP, OpenAI's guide, and the major agent SDKs; a classifier doing the approving rests on vendor numbers, and the one independent stress test found it missed most risky actions) · *Who decides:* your code (whether to ask and what an answer may change); a person (yes, no, or an edit) · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^automode]: John Hughes, Anthropic, "Claude Code auto mode," 2026-03-25. The 93% figure ("in practice users accept 93% of them anyway") is stated without a method or sample. The 0.4% false positive rate is on real internal traffic (n = 10,000); the 17% false negative rate is on 52 overeager actions curated from sessions where an employee denied the action or it was flagged afterwards. <https://www.anthropic.com/engineering/claude-code-auto-mode>
[^autonomy]: Miles McCain et al., Anthropic, "Measuring AI agent autonomy in practice," 2026-02-18. Auto-approve use by session count, interrupt rates by experience, and the oversight quotation. <https://www.anthropic.com/research/measuring-agent-autonomy>
[^12factor]: HumanLayer, "12-Factor Agents," factor 7, "Contact humans with tool calls." <https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-07-contact-humans-with-tools.md>
[^owasp]: OWASP Gen AI Security Project, "LLM06:2025 Excessive Agency," mitigation 6, "Require user approval": "Utilise human-in-the-loop control to require a human to approve high-impact actions before they are taken." <https://genai.owasp.org/llmrisk/llm062025-excessive-agency/>
[^openai-guide]: OpenAI, "A practical guide to building agents," p. 31, on high-risk actions as a trigger for human intervention. <https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf>
[^openai-sdk]: OpenAI Agents SDK (Python), "Human-in-the-loop." `needs_approval`, `RunResult.interruptions`, `state.approve()` and `state.reject()`, resuming with `Runner.run(agent, state)`, and the warnings that `RunState.from_json()` does not authenticate the snapshot and that servers should not accept replacement tool calls, arguments, approval records, or serialized state from the client. The page documents no edit-on-approval. <https://openai.github.io/openai-agents-python/human_in_the_loop/>
[^adk]: Google Agent Development Kit, "Tool confirmation." `require_confirmation`, `request_confirmation` with `hint` and `payload`, the unsupported `DatabaseSessionService` and `VertexAiSessionService`, and experimental status in TypeScript, Go, and Kotlin. <https://adk.dev/tools-custom/confirmation/>
[^langgraph]: LangChain, LangGraph "Interrupts." `interrupt()`, `Command(resume=...)`, the checkpointer and thread ID requirement, the node restarting from its beginning on resume, idempotent side effects before an interrupt, and "Do not wrap interrupt calls in try/except." <https://docs.langchain.com/oss/python/langgraph/interrupts>
[^warningland]: Devdatta Akhawe and Adrienne Porter Felt, "Alice in Warningland: A Large-Scale Field Study of Browser Security Warning Effectiveness," USENIX Security 2013. Figures from the abstract. <https://www.usenix.org/conference/usenixsecurity13/technical-sessions/presentation/akhawe>
[^invariant]: Invariant Labs, blog post on the GitHub MCP vulnerability, 2025-05-26. The "Always Allow" sentence. <https://invariantlabs.ai/blog/mcp-github-vulnerability>
[^bansal]: Gagan Bansal et al., "Does the Whole Exceed its Parts? The Effect of AI Explanations on Complementary Team Performance," CHI 2021. Quotation from the abstract. arXiv:2006.14779. <https://arxiv.org/abs/2006.14779>
[^register]: Simon Sharwood, The Register, 2025-07-21, on the Replit and SaaStr incident. The founder's own account, from his posts and a LinkedIn video; no Replit postmortem is cited. <https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/>
[^cc-permissions]: Anthropic, Claude Code docs, "Configure permissions": "Rules are evaluated in order: deny, then ask, then allow." Version-dependent; checked 2026-11. <https://code.claude.com/docs/en/permissions>
[^sdk-permissions]: Anthropic, Claude Agent SDK docs, "Configure permissions," the warning "Auto-approved tools never reach `canUseTool`." <https://code.claude.com/docs/en/agent-sdk/permissions>
[^ji]: Zimo Ji et al., "Measuring the Permission Gate: A Stress-Test Evaluation of Claude Code's Auto Mode," arXiv:2604.04978v3, revised 2026-10-22. AmPermBench: 128 prompts across four DevOps task families, 253 state-changing actions; 81.0% end-to-end false negative rate (95% CI 73.8% to 87.4%); 70.3% on the 160 actions the classifier evaluates; 36.8% of state-changing actions out of its scope. A preprint. <https://arxiv.org/abs/2604.04978>
[^kadavath]: Saurav Kadavath et al., "Language Models (Mostly) Know What They Know," 2022. Wording from the abstract. arXiv:2207.05221. <https://arxiv.org/abs/2207.05221>

## See also

- [2.4 MCP](../the-unit/mcp.md): the consent seam a tool server exposes, which this chapter grows into a durable request.
- [2.6 The Harness](../the-unit/the-harness.md): permission modes, hooks, and why an instruction to the model never replaces code in the path.
- [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md): confidence routing, which can send work to a person.
- [3.3 Orchestrator-Workers](../composition/fan-out.md): where workers disagree beyond reconciling, the conflict comes to a person.
- [3.7 The Outer Loop](../composition/the-outer-loop.md): where a run gives up; the give-up lands in this chapter's queue.
- [4.4 Guardrails & Safety](guardrails-and-safety.md): the code-only refusal behind the `deny` band.
- [4.6 Prompt Injection & the Lethal Trifecta](prompt-injection.md): the same price step under attack, and why approval decays.
- [6.3 Streaming & Agent UX](../io-boundary/streaming-and-agent-ux.md): the interface for watching and interrupting a run.
- [7.3 Checkpointing](../reliability/stopping-gracefully.md): durable state, which the pause depends on.
- [8.6 Governance & Compliance](../production/governance-and-compliance.md): audit, override rates, and regulatory human-oversight duties.

## Further reading

- [LangGraph, Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts): the pause and resume primitive, with the re-run and side-effect rules.
- [OpenAI Agents SDK, Human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/): approvals in an SDK, and the clearest warning about trusting serialized state.
- [Anthropic, Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode): a vendor's honest numbers on replacing the prompt with a classifier.
- [Ji et al., Measuring the Permission Gate](https://arxiv.org/abs/2604.04978): the independent stress test of that classifier.
- [Akhawe and Felt, Alice in Warningland](https://www.usenix.org/conference/usenixsecurity13/technical-sessions/presentation/akhawe): the large-scale evidence that warning design moves click-through.
