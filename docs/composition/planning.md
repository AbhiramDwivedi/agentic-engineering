# 3.6 Planning & Task Decomposition

*The model writes the sequence once, your code checks it before anything runs, and your code decides when, if ever, to ask the model again. Plan-and-execute trades the step-by-step loop's adaptivity for a plan you can validate and cap in advance, and the price is a bad plan that stays frozen until your trigger fires.*

*Also called: planning, plan-and-execute, planner-executor, task decomposition, static planning.*

## Why you'd reach for it

Ask a model to plan a task before doing it and you inherit a decision the word "planning" hides: after each step runs, do you go back and ask the model again? LangGraph's reference notebook for plan-and-execute (LangGraph is LangChain's graph-based agent framework) asks again after every single step, success or failure, so it behaves like the step-by-step agent loop it was presented as an alternative to.[^langgraph-replan] The label tells you nothing about which one you have.

The two answers fail in opposite directions. A model consulted after every step can change course the moment the world surprises it, but the whole sequence never exists as something your code can read, check, and cap before the first side effect. A plan written once and walked to the end gives you that checkpoint, one place to reject the sequence before it touches a price or a customer, and also a sequence that keeps executing after it has stopped making sense.

Take a launch agent from the companion code. Listing Studio turns a supplier feed into a storefront listing for Stockwell, a mid-market commerce platform, and this agent gets one goal, launch the Aldsworth desk (a sit-stand desk), and four tools it can call: `draft_copy`, `check_map_price`, `set_price`, and `write_email`. The model plans three steps: draft the copy, set the price to $349.00, write the merchant announcement email. The desk carries a minimum advertised price (MAP), the lowest price the supplier lets a retailer advertise, and $349.00 is under the $399.00 MAP. Walk that plan blindly and the email announces a price your own pricing tool refused. Ask the model again after every step and you pay a planning call for each step that went fine.

The model writes the whole plan once. Your code validates it before anything runs, executes it, and goes back to the model only when a step fails, carrying what already ran and what broke.

Reach for it when:

- the steps depend on the input, so you cannot write the sequence into code yourself;
- you can name, before step one, the events that should change the plan (a failed check, a refused price);
- you want to validate, cap, or approve the whole sequence before any step has a side effect.

Skip it when the sequence is the same on every run; that is a chain your code owns ([3.1 Prompt Chaining](prompt-chaining.md)). Skip it too when every observation could redirect the next action; that is [2.5 The Agent Loop](../the-unit/the-agent-loop.md).

## What it actually is

Planning is the model writing an ordered sequence of steps toward a goal, as a typed artifact (a structured object your code parses against a schema and can inspect), before your code commits to running any of it. Plan-and-execute splits the work into two roles: a planner call that writes the sequence, and an executor, which is your code, that walks it, checks each result, and decides when the planner is consulted again.

![Two lanes. The top lane is plan-and-execute with a code-owned replan trigger, drawn from one listing's run. A rounded planner, the model, writes plan 1: draft_copy, set_price 34900, write_email. A rectangle, your code, checks the plan's shape before any step runs, and it passes. Code runs draft_copy, which succeeds without calling the model. Code runs set_price 34900, which fails because 34900 is below the MAP of 39900, so write_email from plan 1 never runs. That failure is the only replan trigger, and the run allows one replan; a second failure would halt it. Code asks the planner again with what already ran and the failure text. The planner writes plan 2: set_price 39900, write_email. Code checks it again before any step, both steps succeed, and code ends the run with status done. The model was called twice. The bottom lane is the step-by-step loop for contrast: the model is consulted after every step, so model calls alternate with draft_copy, set_price and write_email, and the model decides when the run is done. A model call after every successful step in a trace means you built the step-by-step loop.](planning-replan.svg)

Two decisions live in that definition, and they belong to different owners. The model decides the decomposition and the order, a plan tailored to this goal and this input; that half is the new part. Your code decides how often to ask again, and that decision is a spectrum with three points worth naming:

- **Static plan-first.** The model writes the sequence once; code runs every step and never consults the planner again.
- **Trigger-based replanning.** Code runs the existing plan and asks the planner for a revision only when a defined event fires, such as a failed step. An ordinary success never triggers one.
- **Step-wise reconsult.** The planner sees the result of every step and revises. This is the step-by-step loop of [2.5](../the-unit/the-agent-loop.md), ReAct-style (reason, act, observe, then call the model again),[^react] even when the code keeps a `Plan` object. The difference from 2.5 is one of degree, with no bright line.

What changes along the line is how much the plan is worth as a checkpoint. The static end gives you one model call, a validated artifact, and a step count fixed before anything runs, with the highest risk of a frozen bad plan. The step-wise end gives you the most adaptivity and loses the up-front checkpoint. To place a real system, read its code. HumanLayer's 12-Factor Agents makes the same call: the loop, and when to break out of it, belong in your code.[^12factor]

The research family sorts onto the same line.[^plansolve][^hugginggpt] ReWOO (Xu et al., 2023) is static plan-first proper: it plans every tool call up front, with placeholder variables (named slots a later call fills with an earlier tool's output), so the model is not re-prompted after each observation.[^rewoo] ADaPT (Prasad et al., 2024) is trigger-based: it decomposes a subtask further only when the executor fails it, and reports success rates up to 28.3% higher on ALFWorld, 27% on WebShop, and 33% on TextCraft (simulated household, shopping, and crafting tasks used as benchmarks) than iterative-executor and plan-and-execute baselines.[^adapt]

If you can write down, before step one, the conditions under which the plan should change, build trigger-based replanning that checks for exactly those. If you cannot enumerate them, you have a step-by-step task, because any observation might be the one that should change the plan, and only a model consulted after every step will see it.[^adaplanner]

Gulli and Nawalgaria's public draft *Building AI Agents* argues that reasoning models have collapsed the ReAct loop into one large planning call followed by a deterministic executor.[^gulli2-ch22] That is static plan-first, ReWOO's 2023 shape, with a stronger model making the call; the frozen-plan trade is unchanged.

How proven is it? Standard: checking a model-written plan as untrusted input, capping its length, and gating irreversible steps behind a person are ordinary input discipline, and a visible plan a person reviews is shipping in daily tools; Anthropic's research system has its lead agent save its plan to memory so it survives context truncation.[^anthropic-multiagent] Emerging: static or trigger-based execution as a common, proven production architecture, because the evidence is 2023-2024 research and a reference tutorial that turns out to be step-wise. Contested: trusting the plan's correctness with nothing outside the model checking it, so the inner loop where the model decides is also the only judge of its own plan. Valmeekam et al. found that GPT-4, the best model they tested, produced a successful plan on its own in about 12% of cases on average, across classical-planning domains (planning problems written in a formal language such as PDDL); the figure describes that benchmark, not a general rate.[^critical-investigation] Results improved when an external verifier fed errors back, and Kambhampati et al.'s LLM-Modulo framework is the constructive answer: models cannot reliably plan or check their own plans alone, and are useful inside a loop where a sound external verifier (a checker whose acceptance can be trusted) critiques what they propose.[^llm-modulo]

## How to do it

A plan is a list of steps, each naming a tool, one string input, and the reason the model gave for it. `extra="forbid"` makes a step with an unexpected field fail to parse, which keeps the shape the executor reads identical to the shape the model was asked for.

```python
class Step(BaseModel):
    """One step the model proposes: which tool, with what input, and why."""
    model_config = ConfigDict(extra="forbid")

    tool: str
    arg: str
    why: str


class Plan(BaseModel):
    """The whole sequence, written once, before any step runs."""
    model_config = ConfigDict(extra="forbid")

    steps: list[Step]
```

Structural validation is your code's job. `validate_plan` checks three things (an empty plan, a plan over `MAX_STEPS`, a tool off the allowlist) and returns every reason it finds. It does not check tool arguments; each tool's body owns those. `MAX_STEPS` caps one plan's length and is not a budget for the run. A production contract adds a stable id per step, declared dependencies checked for cycles, a projected cost checked against a budget, completion evidence (what a step must return to count as done, such as the price the store confirmed), and a status field.

Semantic verification, whether the plan reaches the goal, is a question code alone cannot answer. LLM-Modulo's sound verifier needs a domain with a formal model (rules a program can check a plan against, as a PDDL domain provides),[^llm-modulo] and most commerce settings have none: nothing formal says a sequence of listing steps is the right one. The fallback is a human approval gate on the consequential or irreversible steps a plan names ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md)). A plan that passed `validate_plan` is well-formed, and nothing in this file knows whether it is right.

```python
# The allowlist and the cap are code, not prompt. A plan is text the model
# wrote after reading content you do not control (a supplier note, a
# competitor page), so it is checked as untrusted input before step one runs.
ALLOWED_TOOLS = {"draft_copy", "check_map_price", "set_price", "write_email"}
MAX_STEPS = 6


def validate_plan(plan: Plan) -> list[str]:
    """Return every reason to reject the plan; an empty list means run it."""
    problems = []
    if not plan.steps:
        problems.append("plan has no steps")
    if len(plan.steps) > MAX_STEPS:
        problems.append(f"plan has {len(plan.steps)} steps, cap is {MAX_STEPS}")
    for i, step in enumerate(plan.steps, start=1):
        if step.tool not in ALLOWED_TOOLS:
            problems.append(f"step {i}: tool {step.tool!r} is not on the allowlist")
    return problems
```

The executor asks the planner once, validates, and walks the steps. Only a `StepFailed` raised by a tool sends it back to the model, and every revised plan is validated again before any of its steps run. `planner_fn(goal, done, failure)` is the seam: the first call carries an empty `done` list and no failure; a replan call carries what already ran and the failure text, and asks for the remaining work only. Four names come from the rest of the file: `StepFailed` is the exception a tool raises when its own check refuses the input, `RunResult` records the status, replan count, and log, `tools` maps each allowlisted name to a function taking the step's `arg` string, and `planner_prompt` builds the planner's prompt text. The full file is in the companion repo.

```python
MAX_REPLANS = 1


def run(planner_fn: Callable[..., Plan], tools: dict[str, Any], goal: str) -> RunResult:
    result = RunResult(status="done")
    done: list[str] = []
    plan = planner_fn(goal, done, None)          # the model writes the plan once
    while True:
        problems = validate_plan(plan)           # code checks it before any step
        if problems:
            result.status = "halted" if result.replans else "rejected"
            result.log.append("rejected: " + "; ".join(problems))
            return result
        for step in plan.steps:
            try:
                out = tools[step.tool](step.arg)
            except StepFailed as exc:
                # The code-owned trigger: only a failed step asks the model
                # again, never an ordinary success.
                if result.replans >= MAX_REPLANS:
                    result.status = "halted"
                    result.log.append(f"halted: {step.tool} failed, no replans left")
                    return result
                result.replans += 1
                result.log.append(f"replan after {step.tool}: {exc}")
                plan = planner_fn(goal, done, f"{step.tool} failed: {exc}")
                break                            # discard the rest of the old plan
            done.append(f"{step.tool}: {out}")
            result.log.append(f"ran {step.tool}")
        else:
            return result                        # every step ran; plan complete
```

> **In the companion repo.** The run below uses a fake planner and fake tools. Prices are integer cents passed as strings, so `"34900"` is $349.00. The fake `set_price` raises `StepFailed` on any price below the desk's MAP of 39900 ($399.00), standing in for a real MAP check. It is a reasoned illustration, not production history.

One run, goal "launch the Aldsworth desk":

1. The planner is called once and returns `[draft_copy, set_price "34900", write_email]`. `validate_plan` returns an empty list. The plan skipped `check_map_price` and passed anyway, because validation checks shape and no rule makes the planner include that step. The MAP rule inside `set_price` catches it, and that rule is code.
2. `draft_copy` runs and returns "copy drafted".
3. `set_price "34900"` raises `StepFailed("34900 is below MAP 39900")`. That exception is the code-owned trigger. `write_email` never runs from this plan, so no email announces a price the tool refused.
4. `replans` goes from 0 to 1. The planner is called a second time with `done=["draft_copy: copy drafted"]` and the failure `"set_price failed: 34900 is below MAP 39900"`.
5. The new plan, `[set_price "39900", write_email]`, is validated again, both steps run, and the status is `done`.

Three tested variants pin down the edges. A plan containing `email_all_customers` is rejected with "not on the allowlist" and no step runs, including the harmless ones before it. A second failure after the replan halts the run, and the planner is never called a third time. A clean plan runs to `done` with the planner called exactly once. That count is the checkable signature of trigger-based replanning: if your trace shows a planner call after every successful step, you built the step-by-step loop.

**The failure report.** This listing passes the exception text; a production executor sends back which step, which check, and what it observed, so the replan has more to act on than "failed".

**The replan policy.** This executor knows one move, a full replan of the remaining work, which can recover from a structurally wrong plan; a local retry of the failed step is cheaper and cannot. Decide which failure gets which, and what happens when replanning does not converge (this code halts; the alternatives are escalating to a person or shipping the best partial result).

**The shape.** Once a plan has independent branches it is a graph. LLMCompiler (Kim et al.) plans tool calls that way, each naming the earlier calls it needs, and dispatches each as soon as those finish;[^llmcompiler] running parallel parts is [3.3 Orchestrator-Workers](fan-out.md)'s job.

Coding tools show the plan-as-artifact half: Claude Code's plan mode blocks edits until you approve its plan,[^cc-plan] Cursor's Plan Mode drafts an editable plan for you to review,[^cursor-plan] and once approved each resumes its ordinary step-by-step loop.

#### Wiring it to a provider

Each variant swaps only the planner call. The LangGraph tab makes one structured-output call and leaves out the tutorial's replan-after-every-step graph.

=== "LangGraph"

    ```python
    def planner_fn(goal: str, done: list[str], failure: str | None) -> Plan:
        return planner_chain.invoke(planner_prompt(goal, done, failure))
    ```

=== "OpenAI Responses API"

    ```python
    def planner_fn(goal: str, done: list[str], failure: str | None) -> Plan:
        response = client.responses.create(
            model="gpt-6.2-sol",
            input=[{"role": "user", "content": planner_prompt(goal, done, failure)}],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "Plan",
                    "schema": Plan.model_json_schema(),
                    "strict": True,
                }
            },
        )
        return Plan.model_validate_json(response.output_text)
    ```

=== "Anthropic Messages API"

    ```python
    def planner_fn(goal: str, done: list[str], failure: str | None) -> Plan:
        reply = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=1024,
            tools=[{
                "name": "write_plan",
                "description": "Write the ordered steps for this goal.",
                "input_schema": Plan.model_json_schema(),
            }],
            tool_choice={"type": "tool", "name": "write_plan"},
            messages=[{"role": "user", "content": planner_prompt(goal, done, failure)}],
        )
        block = next(b for b in reply.content if b.type == "tool_use")
        return Plan.model_validate(block.input)
    ```

## Security & trust

A planner reads things you did not write: a supplier's spec sheet, a competitor's product page, a tool's error text. The OWASP Top 10 for Agentic Applications lists Agent Goal Hijack (ASI01) first: an attacker redirecting an agent's objective through content it reads rather than code it runs.[^owasp-asi] An injected instruction (text planted in content the model reads) that reaches a single call corrupts one output; one that reaches the planner can rewrite every step after it.

The allowlist in `validate_plan` stops the bluntest version, a planner talked into adding `email_all_customers`, before step one. Replans go through the same check because the replan prompt carries failure text, which a tool may have copied from somewhere untrusted. The allowlist cannot catch a hijack that stays inside allowed tools, such as a `write_email` whose argument has been rewritten; that is why tool bodies validate their own arguments and irreversible steps get an approval gate.

OWASP's announcement names EchoLeak (CVE-2025-32711), a zero-click prompt-injection flaw in Microsoft 365 Copilot, as its illustration of ASI01.[^echoleak] The published exploit leaks data through one response's auto-fetched image URL, with no evidence a multi-step plan was rewritten, so it belongs to the general injection-to-exfiltration chain in [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md). This chapter claims only the narrower planner-hijack case. No named public incident of it had surfaced at this page's last review, and the controls above are reasoned from OWASP's categories, a taxonomy announced in December 2025.

## Gotchas

**A valid plan can still be wrong.** The trace's first plan passed every check and priced the desk below MAP; only the price tool's own rule caught it. Where no sound verifier exists, the backstop is a deterministic check that must-run steps appear in the plan, or a person reading it before the consequential steps execute.

**The frozen plan.** A static plan keeps executing after the world has moved, for as long as your trigger takes to fire. A trigger that fires only on exceptions misses a step that succeeds with the wrong result, so make the tools that matter fail loudly.

**The step-by-step loop under another name.** If the planner runs after every step, you are paying for reconsultation and keeping a `Plan` object as decoration. That can be the right design; call it [2.5](../the-unit/the-agent-loop.md) and budget it as one.

**Replanning that does not stop.** Failure write-ups of AutoGPT, the 2023 goal-driven agent, trace its runaway replanning to three causes: goals with no completion criterion, no comparison of a new plan against what already ran, and no iteration or cost cap.[^autogpt-failures] Hou et al.'s static analysis of 6,549 public agent repositories found 68 unbounded-loop failures across 47 projects, at 91.9% precision.[^ial] `MAX_REPLANS` is the cap here; set yours before a run discovers it for you.

**A planner with nothing to decide.** If the plan comes back the same for every input, it is a script with a model call in front, the over-planning entry in the [Anti-Patterns Catalog](../catalogs/anti-patterns.md). Measure plan quality apart from end-to-end success (executability, replan frequency), because a failed run cannot tell you whether the plan, a step, or the replan broke ([4.2 Evaluation](../craft/proving-it-works.md)). Benchmarks such as PlanBench test planning apart from recall of memorized plans.[^planbench]

## In short

Let the model write the plan and keep every other decision in code. Validate the plan as untrusted input before step one, go back to the model only on triggers you named in advance, and cap replans so the run halts or escalates. Put a person in front of irreversible steps, because for most commerce tasks no automated check knows whether the plan is right. Start trigger-based; if you cannot list the conditions that should change the plan, build the agent loop under its own name. To check what you built, count the planner calls on a clean run.

<small class="chapter-meta">**Maturity: Standard (structural validation, human approval gate) · Emerging (a model-written plan as a common, proven execution architecture) · Contested (autonomous planning correctness with no external check)** (validating and gating a plan is ordinary input discipline; plan-first execution rests on 2023-2024 research and a tutorial that turns out step-wise; GPT-4's unchecked plans succeeded in about 12% of one benchmark's cases) · *Who decides:* the model (the plan) / your code (when to ask again) · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^langgraph-replan]: LangChain/LangGraph, plan-and-execute tutorial notebook (`langchain-ai/langgraph`, `docs/docs/tutorials/plan-and-execute/plan-and-execute.ipynb`; the older `examples/plan-and-execute/` path is now a redirect stub). Defines `replan_step` and a `should_end` router; the edge from the agent node to the replan node is unconditional (`add_edge("agent", "replan")`), so `replan_step` runs after every executed step and returns either a final response or a revised plan. Cited at a pinned commit because the path has moved. <https://github.com/langchain-ai/langgraph/blob/23961cff61a42b52525f3b20b4094d8d2fba1744/docs/docs/tutorials/plan-and-execute/plan-and-execute.ipynb>
[^react]: Yao, S. et al., "ReAct: Synergizing Reasoning and Acting in Language Models," arXiv:2210.03629 (ICLR 2023). The interleaved reason-act-observe baseline that plan-and-execute is contrasted against. <https://arxiv.org/abs/2210.03629>
[^12factor]: HumanLayer, "12-Factor Agents," Factor 8, "Own your control flow." Argues for owning the agent loop in your own code, including when to break out of it (for example, to wait for a human), rather than leaving control flow to a framework or the model. <https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-08-own-your-control-flow.md>
[^plansolve]: Wang, L. et al., "Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models" (ACL 2023). The prompting-level root of the family: one call told to devise a plan that divides the task into subtasks, then carry them out, in a single generation. <https://arxiv.org/abs/2305.04091>
[^hugginggpt]: Shen, Y. et al., "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face" (2023). An LLM controller plans which specialized models to invoke and in what order, closer to the tool-selection problem of [2.1 Tool Use](../the-unit/tool-use.md) than to a new architecture. <https://arxiv.org/abs/2303.17580>
[^adaplanner]: Sun, H. et al., "AdaPlanner: Adaptive Planning from Feedback with Language Models" (NeurIPS 2023). The case for the adaptive end: agents that "rely on static plans that are not adaptable to environmental feedback" degrade as problem complexity and plan horizon grow; it proposes closed-loop in-plan and out-of-plan refinement. <https://arxiv.org/abs/2305.16653>
[^rewoo]: Xu, B. et al., "ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models" (2023). Plans all tool calls up front with placeholder variables rather than interleaving reasoning and observation, reducing token use relative to ReAct-style loops. <https://arxiv.org/abs/2305.18323>
[^llmcompiler]: Kim, S. et al., "An LLM Compiler for Parallel Function Calling" (ICML 2024). A planner emits a graph of tool calls; a task-fetching unit dispatches tasks as their dependencies are met; an executor runs them. Speed and cost figures are the paper's own benchmark results. <https://arxiv.org/abs/2312.04511>
[^adapt]: Prasad, A. et al., "ADaPT: As-Needed Decomposition and Planning with Language Models," *Findings of the Association for Computational Linguistics: NAACL 2024*, pp. 4226-4252. Decomposes a subtask into a sub-plan only when the executor fails it; success rates "up to 28.3% higher in ALFWorld, 27% in WebShop, and 33% in TextCraft" than iterative-executor and plan-and-execute baselines are the paper's reported benchmark results. <https://aclanthology.org/2024.findings-naacl.264/>
[^gulli2-ch22]: Gulli, A. & Nawalgaria, *Building AI Agents: From Design Patterns to Production* (2026 public draft), ch. 22, "What's Next." The source of the claim, paraphrased here, that reasoning models collapsed the ReAct loop into one planning call. A public draft; wording may change before print.
[^anthropic-multiagent]: Anthropic, "How we built our multi-agent research system" (2025-06-13). The lead agent begins by "thinking through the approach and saving its plan to Memory to persist the context," since exceeding the context window truncates the run. <https://www.anthropic.com/engineering/multi-agent-research-system>
[^critical-investigation]: Valmeekam, K., Marquez, M., Sreedharan, S., Kambhampati, S., "On the Planning Abilities of Large Language Models: A Critical Investigation" (2023). The best model tested, GPT-4, had "an average success rate of ~12% across the domains" when generating plans autonomously, a benchmark-specific figure; external verifiers that feed back on the plans and back-prompt the model improve results. <https://arxiv.org/abs/2305.15771>
[^llm-modulo]: Kambhampati, S. et al., "LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks" (ICML 2024, spotlight). Autoregressive LLMs cannot by themselves reliably plan or self-verify; a sound external verifier, distinct from syntactic checking, is what an LLM-Modulo framework adds. <https://arxiv.org/abs/2402.01817>
[^planbench]: Valmeekam, K. et al., "PlanBench: An Extensible Benchmark for Evaluating Large Language Models on Planning and Reasoning about Change" (NeurIPS 2023, Datasets and Benchmarks Track). Built from classical-planning domains to distinguish planning from retrieval of memorized planning-like text. <https://arxiv.org/abs/2206.10498>
[^cc-plan]: Claude Code docs, "Choose a permission mode." Plan mode blocks edits until you approve a drafted plan; approval resumes the ordinary tool-calling loop. Keybindings and tool lists change; check the live page. <https://code.claude.com/docs/en/permission-modes>
[^cursor-plan]: Cursor, "Introducing Plan Mode" and Plan Mode docs. Researches the codebase, asks clarifying questions, and drafts an editable Markdown plan for you to review; approval resumes normal agent execution. <https://cursor.com/blog/plan-mode>, <https://cursor.com/docs/agent/plan-mode>
[^owasp-asi]: OWASP GenAI Security Project, Agentic Security Initiative, "OWASP Top 10 for Agentic Applications" (announced 2025-12-09). ASI01, Agent Goal Hijack, listed first; the announcement names EchoLeak as its illustration. The controls in this chapter are reasoned from the category, not taken from an OWASP list. The taxonomy is new and under revision; wording and order should be re-checked against the canonical document. <https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/>
[^echoleak]: EchoLeak, CVE-2025-32711, disclosed by Aim Security (2025): an indirect prompt injection hidden in an email, chained with an auto-fetched image URL, exfiltrating internal data with no user interaction. Microsoft patched it server-side and reported no known exploitation in the wild. Named here via the OWASP announcement above; full treatment in 4.6.
[^autogpt-failures]: "AutoGPT Planning Failures: Infinite Loops & Resource Depletion (2023)," a case study in `vectara/awesome-agent-failures` drawn from community reports and GitHub issues. It names "Lack of Concrete Termination Criteria," "No comparison between new plans and previously executed plans," and "No built-in limits on execution time or iterations." Practitioner evidence, not a vendor postmortem; usage figures circulating in secondary compilations could not be traced to an original report and are not repeated. <https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/autogpt-planning-failures.md>
[^ial]: Hou, X., Wang, S., Zhao, Y., Wang, H., "When Agents Do Not Stop: Uncovering Infinite Agentic Loops in LLM Agents" (2026). Static analysis across 6,549 public LLM-agent repositories; manual review confirmed 68 unbounded-loop failures across 47 projects, at 91.9% precision. <https://arxiv.org/abs/2607.01641>

## See also

- [1.3 Workflow or Agent?](../foundations/workflow-or-agent.md): the agency spectrum this pattern sits in the middle of, with the model deciding the plan and code owning the walk.
- [2.2 Structured Output](../the-unit/structured-output.md): the typed contract a plan and each step's report rely on.
- [2.5 The Agent Loop](../the-unit/the-agent-loop.md): the step-by-step loop at the far end of this chapter's spectrum.
- [3.1 Prompt Chaining](prompt-chaining.md): the sequence your code writes, for when the steps never change.
- [3.3 Orchestrator-Workers](fan-out.md): the parallel sibling, where the model sizes independent work; LLMCompiler's graph-shaped plans are where the two meet.
- [3.7 The Outer Loop](the-outer-loop.md): the deterministic verify-and-retry loop a validated plan can run inside, with termination and futility detection in full.
- [4.1 Prompt Architecture & Management](../craft/prompts-are-source-code.md): hardening a vague goal with clarifying questions before anything is planned.
- [4.2 Evaluation](../craft/proving-it-works.md): measuring plan quality apart from end-to-end success.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md): the approval gate on an irreversible step a plan names.
- [4.5 Reasoning & Thinking Budgets](../craft/reasoning-and-thinking-budgets.md): chain-of-thought, Tree of Thoughts, and search-based planning, where the plan is a search over reasoning paths.
- [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md): the general injection-to-exfiltration chain, EchoLeak included.
- [5.1 State, Not Memory](../knowledge/state-not-memory.md): the plan as state the agent persists and re-reads, not a transcript.
- [5.4 Compaction](../knowledge/compaction-and-the-window.md): what crosses into each step's context as the plan is walked.
- [9.1 Long-Running Agents](../frontier/when-you-want-autonomy.md): the repricer, a long-running agent, at full scale.
- [9.6 Coding Agents](../frontier/coding-agents.md): plan modes and plan-file workflows in coding tools, in depth.
- [G. The Security Posture Map](../catalogs/security-posture.md): the catalog where an ASI01 row will point back here.

## Further reading

- Kambhampati et al., ["LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks"](https://arxiv.org/abs/2402.01817) (ICML 2024): the skeptical case and its constructive answer, an external verifier around the model.
- Xu et al., ["ReWOO"](https://arxiv.org/abs/2305.18323) (2023): the clearest statement of why you would plan everything up front.
- Prasad et al., ["ADaPT"](https://aclanthology.org/2024.findings-naacl.264/) (NAACL 2024 Findings): trigger-based decomposition with numbers against both static extremes.
- LangGraph, [plan-and-execute notebook](https://github.com/langchain-ai/langgraph/blob/23961cff61a42b52525f3b20b4094d8d2fba1744/docs/docs/tutorials/plan-and-execute/plan-and-execute.ipynb): read the replan edge before you copy it.
- OWASP, ["Top 10 for Agentic Applications"](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) (2025-12-09): Agent Goal Hijack and the rest of the agentic threat list.
