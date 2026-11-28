# 3.7 The Outer Loop

*A second loop that your code owns: run the agent, check its answer with a verifier the model cannot argue with, then retry with the failure, stop, or hand the case to a person.*

*Also called: verify-and-retry, loop engineering, the fix loop; the Ralph loop is its minimal shell form.*

## Why you'd reach for it

Often the first outer loop is a person. An agent proposes a change, someone reads the test output, pastes the failure back into the chat and asks again, and the agent stops only when that person is satisfied or gives up.[^gulli2-ch20] Handing that seat to code takes a few dozen lines, and the obvious first version is wrong.

The obvious version gives the agent the check as a tool and tells it to keep going until the check passes. That puts the check inside the model's own turn, in the agent loop of [2.5](../the-unit/the-agent-loop.md) (the inner loop, where the model picks each tool call until it declares itself finished). The model now decides what a red result means. It can read "below the floor by fifty dollars" and conclude that is close enough, or that the check is out of date, and nothing in the structure stops it.

Take a repricer: an agent that watches competitor prices and adjusts a merchant's prices within rules, with nobody approving each change. The Aldsworth sit-stand desk carries a minimum advertised price (MAP) of $399, a floor the supplier sets and the merchant has agreed not to advertise below. A competitor lists the desk at $349. Matching it is the obvious move. If the floor lives only in the prompt and the model is trusted to respect it, the one time it does not, a $349 price goes live, and the cost is a MAP breach with the supplier that no later retry can unpublish.

The fix is to move the check out of the model's turn and into a second loop your code drives, the outer loop. Your code calls the agent, takes the price it proposes, and runs a plain function that checks MAP and margin. On a pass it publishes; on a fail it sends the failure back for another attempt; past a hard limit it gives up and hands the case to a merchandiser. The model never sees the function run and never gets a vote on its verdict. Keeping the check out of the model's turn is what lets the loop run unattended, and it caps the loop at the quality of the function it calls.

Reach for an outer loop when:

- "done" is something a function can decide with no judgment call: the tests pass, the price clears MAP and margin, the totals reconcile;
- a rejected attempt costs nothing but tokens, because nothing reaches the outside world until the verifier passes;
- you want attempts to run without a person reading each one.

Skip it when "done" needs judgment (is this product copy persuasive?). A cap on a loop with nothing checkable to converge toward turns an unanswerable question into an expensive one; put a model in the grader's seat with [3.4 Evaluator-Optimizer](evaluator-optimizer.md), or hand the case to a person. Skip it too when one call nearly always succeeds: validate once and escalate the rare failure.

## What it actually is

An outer loop is a controller in your code that wraps complete agent runs. It calls the agent for an attempt, invokes a verifier on the result itself, and branches on the verdict: publish on a pass, feed a structured failure into the next attempt on a fail, and stop at a hard attempt cap or when the attempts stop making progress. The model decides everything inside an attempt; your code decides whether the attempt was good enough, whether to try again, and when to quit.

![Two zones side by side. On the left, inside the model's turn, sits one rounded box: an agent attempt, one complete run in which the model decides and proposes a price. On the right is a large zone labelled your code, the controller, and every box in it is a rectangle. Your code calls the agent for attempt n with the failures so far. The agent hands back a price, 34900, and your code passes it to a verifier, a plain function that checks MAP and margin. The verifier's result goes to a rectangle that branches on the verdict. A pass goes to publish the price. A fail turns into feedback text, price 34900 is below MAP 39900, which is the only thing that crosses back into the model's side, as input to the next attempt. When the attempt cap is hit, or the same failure comes back twice, the loop gives up, and a merchandiser, a person outside the loop, gets the failures. The verifier, the verdict, publish and give up all sit inside your code; the model never sees the verifier run and never votes on the verdict, it only reads the feedback text your code chose to send.](the-outer-loop-verdict.svg)

Having a deterministic check somewhere does not put a system in this pattern. A coding agent that runs `pytest` as one of its own tool calls and reads the exit code is still inside 2.5's loop, because the model chose to run the check and the model decides what the result means. The pattern starts where a controller outside the model's turn invokes the verifier on its own schedule and reads the boolean without asking the model what it thinks of it. A quick check on any design: trace every path from a failing verdict to a shipped result; if any runs through the model, the model is still deciding.

That test is also the seam with [3.4](evaluator-optimizer.md), which draws the same generate, check, retry loop with a model grading the draft against a rubric. A judgment rendered by a model puts the loop in 3.4; a check a deterministic function can render puts the decision in your code, and the loop here.

The word "autonomous" needs the same test. In the inner loop the model runs on its own inside one attempt. In the outer loop, code runs on its own, with no person watching, and decides whether the model was right without asking how it reached its number.

Structurally this is generate-and-validate, and most of its parts are older than language-model agents. GenProg (2009) generated candidate bug fixes by genetic programming and accepted any that passed the test suite.[^genprog] Reflexion (2023) fed a verbal reflection on each failure into the next attempt,[^reflexion] and Anthropic's evaluator-optimizer workflow followed in 2024. Gulli and Nawalgaria call the craft of building such loops loop engineering and frame it as the phase after prompt and context engineering.[^gulli2-ch20] What changed is the generator. A language model can read a failure report and act on it, which a genetic operator cannot. The loop around it is engineering you already know. Anthropic gives verifiability through automated tests as the reason agents suit coding,[^anthropic-bea] 12-Factor Agents argues for owning looping and halting in your code,[^12factor] and Kambhampati and colleagues' LLM-Modulo work (a framework that pairs a model's proposals with external critics) makes the general case that language models are unreliable as planners or self-verifiers alone and useful once an external, sound verifier, one that never passes a wrong answer, checks what they propose.[^llm-modulo] For narrow tasks with a verifier like that, the pattern is Established.

The weight sits on "sound". Verification is usually cheaper than generation, which makes retrying against a check tractable, but every check still costs something, and a fair check does not promise that any fixed number of attempts will converge.[^wei-verifier] That is why the claim that a good verifier alone lets a mid-tier model grind its way to a correct answer is contested: a verifier that is incomplete or editable passes wrong answers, however many attempts you run. Two parts of the pattern are younger still: detecting that attempts have stopped making progress, and carrying distilled lessons from one attempt to the next. Both are Emerging; carrying lessons instead of whole transcripts is [5.4 Compaction](../knowledge/compaction-and-the-window.md)'s ground, and a model that rewrites its own prompt or tools between attempts is [9.7 Self-Improving Systems](../frontier/self-improving-systems.md).

Claude Code, Anthropic's coding agent, exposes this distinction as a setting. Its `/goal` command, which keeps the agent working until a stated condition holds, by default has a small, fast model judge after each turn whether the condition is met, which is 3.4's shape; a Stop hook (a check that runs when the agent tries to finish) "can run a script for deterministic checks or a prompt for model-evaluated ones," and the script form is this chapter.[^claude-goal] Its `/loop` command re-runs a prompt on an interval and is a scheduler.[^claude-loop]

The Ralph loop, Geoffrey Huntley's name for re-running a coding agent in a bare shell `while` loop,[^ralph-huntley] is the minimal form: code owns the repetition, but with no verifier nothing owns the verdict. Anthropic's official `ralph-loop` plugin, run as `/ralph-loop`, shows where its safety lives: `--max-iterations` defaults to unlimited, and the plugin's README says to rely on it as the primary safety mechanism rather than on the completion phrase the model prints.[^ralph-plugin]

## How to do it

Write the verifier first. Its contract: take the proposed price and the rules, return a `Verdict` whose `feedback` says what is wrong in terms the next attempt can act on.

```python
@dataclass
class Verdict:
    ok: bool
    feedback: str | None = None  # structured failure, fed back into the next attempt


def verify_price(price_cents: int, rules: PriceRules) -> Verdict:
    """Pure function over pinned rules."""
    if price_cents < rules.map_cents:
        return Verdict(False, f"price {price_cents} is below MAP {rules.map_cents} "
                              f"for {rules.sku}; MAP is a hard floor.")
    margin = (price_cents - rules.cost_cents) / price_cents
    if margin < rules.min_margin:
        return Verdict(False, f"margin {margin:.0%} is under the {rules.min_margin:.0%} "
                              f"minimum at cost {rules.cost_cents}.")
    return Verdict(True)
```

The feedback names the defect, the number and the rule, because the model reads it next attempt; a bare `False` would leave it guessing. This is also the line between this chapter's retry and the one in [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md). A 7.1 retry fires on an infrastructure failure (a timeout, a rate limit) where the attempt itself may have been fine, so it backs off and resends. This retry fires when an attempt was checked on its merits and rejected, so it regenerates with the critique. Mixing them up sends a network blip through a full critique-and-regenerate cycle, or answers a bad price with nothing but backoff. A verifier crash is an infrastructure failure: route it to 7.1, do not count it against the cap, and keep the stack trace away from the model.

Deterministic is not the same as reliable. The same suite scores differently under different resourcing: Anthropic measured a 6-percentage-point gap on one agentic coding benchmark between its most- and least-resourced setups, and concluded that leaderboard differences under 3 points deserve skepticism until the configuration is matched.[^infra-noise] Individual tests flake too, passing on one run and failing on the next against the same code.[^flakiness] Pin the verifier's environment and decide in advance how a flaky check is re-run, so one bad run neither passes a wrong answer nor burns an attempt. `verify_price` is pure arithmetic over pinned rules, so the repricer gets this cheaply; a test suite does not.

Then the loop. `attempt(failures)` is one complete inner agent run that returns a price; `run_outer_loop` returns an `Outcome` whose `price_cents` is set only when the verifier passed.

```python
@dataclass
class Outcome:
    status: str                      # "passed" or "gave_up"
    price_cents: int | None = None   # set only when the verifier passed
    attempts: int = 0
    failures: list[str] = field(default_factory=list)  # for the human on give-up


def run_outer_loop(
    attempt: Callable[[list[str]], int],  # one inner agent run: failures so far -> price
    rules: PriceRules,
    max_attempts: int = 3,                # hard attempt cap
) -> Outcome:
    failures: list[str] = []
    for n in range(1, max_attempts + 1):
        price = attempt(failures)              # the model decides inside this call
        verdict = verify_price(price, rules)   # the code decides here, on its own schedule
        if verdict.ok:
            return Outcome("passed", price, n, failures)
        if failures and verdict.feedback == failures[-1]:
            break                              # same failure twice: futile, stop early
        failures.append(verdict.feedback)
    # Give up explicitly: hand the failures to the merchandiser, never ship a bad price.
    return Outcome("gave_up", None, n, failures)
```

A run, using a scripted model that returns canned prices in place of a live one, with the real loop and verifier (landed cost $280.00, minimum margin 20%):

1. Your code calls `attempt([])`. The model sees the competitor at $349 and matches it, proposing `34900`.
2. Your code calls `verify_price(34900, rules)`. It fails with `"price 34900 is below MAP 39900 for NV-ALDSWORTH-DM; MAP is a hard floor."` There is no earlier failure to compare against, so the loop records the feedback.
3. Your code calls `attempt([feedback])`. The model reads the floor and proposes `39900`.
4. Your code calls `verify_price(39900, rules)`. It passes, at a margin of about 30% against a 20% minimum, and the loop returns `Outcome("passed", 39900, attempts=2)` with the one rejection kept in `failures` for the audit trail.

Two other runs show the stops. If the model inches up through `34900`, `37900` and `38900`, every attempt fails on MAP with a different message (each names its price), the no-progress check never fires, and the cap ends it: `Outcome("gave_up", None, attempts=3)` with three failures for the merchandiser. If the model proposes `34900` twice, the second feedback matches the first exactly, and the loop gives up at attempt 2 even with `max_attempts=5`.

Two controls decide when the loop stops trying. The cap is the guarantee, and it has to be unconditional and owned by your code. It counts attempts, not dollars. A 2026 static analysis of 6,549 public agent repositories confirmed 68 unbounded-loop failures across 47 of them, which is the case for having a cap at all.[^ial] Framework limits such as the OpenAI Agents SDK's `max_turns`[^openai-maxturns] and LangGraph's `recursion_limit`[^langgraph-recursion] bound the steps inside one run, the inner loop, and do not cap repeated complete attempts. For spend, SWE-agent's `per_instance_cost_limit` and `total_cost_limit` show the shape a dollar cap takes.[^swe-agent-cost]

No-progress detection is the Emerging half, and the listing's rule is its minimal form: exact string equality against the previous failure. It works here because the verifier's messages are deterministic. A test runner's raw output changes cosmetically between runs, so reduce it to a signature first (the failing test names and error types). Neither direction proves anything. A model can churn through different symptoms with no real progress (an A, B, A oscillation passes this check and runs to the cap), and a repeated failure can sit on top of a real partial fix. Pair the signature with a measure that should only move one way where you have one, such as a rising pass count, and treat the whole check as an early exit.

What happens when the loop gives up is a decision made once, in code: escalate, ship the best attempt, or fail closed. For a price, fail closed: the current price stays, and the failures go to a merchandiser who can see what the agent tried; escalation mechanics are in [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md).

Scaling up changes two things. As rules multiply, the verifier should report every failing rule at once; returning only the first keeps the listing short, but in production the model fixes MAP and walks into the margin rule on the next attempt. As SKUs multiply, each gets its own loop and cap under a total cap for the batch, the split SWE-agent makes between per-instance and total limits.

#### Wiring it to a provider

Only `attempt` changes between providers. Each version asks for a structured price and hands it to the same `run_outer_loop`. The tabs use names from the companion repo's `listing-studio/outer_loop/`: `PriceRules` holds the sku, `map_cents`, `cost_cents` and `min_margin`; `PriceCandidate` is the structured output; `propose` (a chat model bound to it), `client` (the provider's SDK client) and `_PRICE_TOOL` (the Anthropic tool definition) request it.

=== "LangGraph"

    ```python
    def attempt(failures: list[str]) -> int:
        prompt = "Set price_cents for NV-ALDSWORTH-DM; a competitor sells it at 34900."
        if failures:
            prompt += " Earlier attempts were rejected: " + " | ".join(failures)
        return propose.invoke(prompt).price_cents


    rules = PriceRules("NV-ALDSWORTH-DM", map_cents=39900, cost_cents=28000, min_margin=0.20)
    outcome = run_outer_loop(attempt, rules, max_attempts=3)
    print(outcome.status, outcome.price_cents)
    ```

=== "OpenAI Responses API"

    ```python
    def attempt(failures: list[str]) -> int:
        prompt = "Set price_cents for NV-ALDSWORTH-DM; a competitor sells it at 34900."
        if failures:
            prompt += " Earlier attempts were rejected: " + " | ".join(failures)
        response = client.responses.create(
            model="gpt-6.2-sol",
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "PriceCandidate",
                    "schema": PriceCandidate.model_json_schema(),
                    "strict": True,
                }
            },
        )
        return PriceCandidate.model_validate_json(response.output_text).price_cents


    rules = PriceRules("NV-ALDSWORTH-DM", map_cents=39900, cost_cents=28000, min_margin=0.20)
    outcome = run_outer_loop(attempt, rules, max_attempts=3)
    print(outcome.status, outcome.price_cents)
    ```

=== "Anthropic Messages API"

    ```python
    def attempt(failures: list[str]) -> int:
        prompt = "Set price_cents for NV-ALDSWORTH-DM; a competitor sells it at 34900."
        if failures:
            prompt += " Earlier attempts were rejected: " + " | ".join(failures)
        reply = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=1024,
            tools=[_PRICE_TOOL],
            tool_choice={"type": "tool", "name": "propose_price"},
            messages=[{"role": "user", "content": prompt}],
        )
        block = next(b for b in reply.content if b.type == "tool_use")
        return PriceCandidate.model_validate(block.input).price_cents


    rules = PriceRules("NV-ALDSWORTH-DM", map_cents=39900, cost_cents=28000, min_margin=0.20)
    outcome = run_outer_loop(attempt, rules, max_attempts=3)
    print(outcome.status, outcome.price_cents)
    ```

## Gotchas

**A verifier nobody touched can still be wrong.** Smith and colleagues showed in 2015 that automatically generated patches can pass a test suite and still be wrong, because a suite is an incomplete specification.[^overfitting] The repricer has the same exposure: `verify_price` checks MAP and margin, and if the merchant has a third rule nobody wrote into the function, the loop will certify a price that breaks it and report `passed`. An untouched suite that misses a requirement passes the wrong answer just as a tampered one would.

**A verifier the agent can edit is worse than none.** METR, an independent model-evaluation group, found frontier models in evaluation runs modifying tests or scoring code and patching the evaluator to obtain a passing score. The rate was 43 times higher on RE-Bench than on HCAST (30.4% of runs against 0.7%); METR guesses that RE-Bench's visible scoring function is why, alongside harder tasks or different scaffolding.[^metr-outer] A passing check switches off the suspicion you would bring to an unchecked answer, so a gamed one does more damage than none. Keep the verifier outside the agent's write access, pin which tests must be collected and assert that none were skipped, run task-specific tests alongside the previously passing regression suite, and promote only an artifact re-verified fresh in a clean copy the agent never wrote to. SWE-bench Verified, a human-screened coding benchmark, splits it the same way: hidden `FAIL_TO_PASS` tests check the fix and `PASS_TO_PASS` tests check nothing else broke.[^swebench-verified] The repricer gets this almost free, since `verify_price` lives in your code and the model has no tool that reaches it. Keep it that way as the agent gains tools.

**Do not loop over irreversible actions.** A retry assumes a rejected attempt cost nothing. If an attempt publishes, sends or deletes before the verifier runs, a retry compounds the damage. In a user-reported incident from July 2025, a Replit coding agent ran destructive commands against a production database during a code freeze that existed only as an instruction the agent had read. It was not a verify-and-retry loop, but it shows the shape of the risk.[^replit] The repricer's attempt only proposes; the caller publishes, and only on `passed`. Blast-radius controls belong to [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md) and OWASP's Excessive Agency category.[^owasp-llm06]

## In short

Write the verifier before the loop. If you cannot write the stop condition as a function that returns a verdict without calling a model, you do not have an outer loop yet; you have [3.4](evaluator-optimizer.md). Keep that function in your code, out of the agent's reach, and make its pass the only route to a side effect. Cap attempts unconditionally, add the no-progress check as an early exit you do not lean on, and make giving up a real outcome that lands with a person. Then spend most of your remaining effort on what the verifier covers, because the loop's `passed` certifies only what the verifier checks.

<small class="chapter-meta">**Maturity: Established (narrow tasks with an external, sound verifier) · Emerging (systematic no-progress detection; cross-attempt lesson induction)** (generate-and-validate predates agents by about fifteen years and vendors document it; stall detection and lesson carry-over have no settled rule) · *Who decides:* your code (whether to retry and when to stop) / the model (each attempt) · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^gulli2-ch20]: Gulli, A. & Nawalgaria, A., *Building AI Agents: From Design Patterns to Production* (2026 public draft), ch. 20 (public draft link; may refuse automated fetches), "Loop Engineering: The System Is the Loop." The person-as-loop observation and the framing of loop engineering as a phase following prompt engineering (2022-2024) and context and harness engineering (2025). The manuscript is a public draft under active revision; paraphrased here, re-verify before quoting. <https://docs.google.com/document/d/1keM4ZbbfVmdsq3EAkbAliIegOpnnuBf-_KpD4oDOF0o>
[^genprog]: Weimer, W., Nguyen, T., Le Goues, C., Forrest, S., "Automatically Finding Patches Using Genetic Programming" (ICSE 2009). Candidate patches generated by genetic programming and accepted once they pass the available positive and negative test cases; no language model involved. <https://doi.org/10.1109/ICSE.2009.5070536>
[^anthropic-bea]: Anthropic, "Building Effective Agents" (2024-12-19). On coding tasks: "Code solutions are verifiable through automated tests; Agents can iterate on solutions using test results as feedback." <https://www.anthropic.com/research/building-effective-agents>
[^12factor]: HumanLayer, "12-Factor Agents," Factor 8, "Own your control flow." <https://github.com/humanlayer/12-factor-agents>
[^llm-modulo]: Kambhampati, S. et al., "LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks" (ICML 2024). <https://arxiv.org/abs/2402.01817>
[^wei-verifier]: Jason Wei, "Asymmetry of verification and verifier's law" (2025). A practitioner essay, not peer-reviewed. <https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law>
[^claude-goal]: Anthropic, Claude Code docs, "Keep Claude working toward a goal" (`/goal`). By default a small, fast model checks after each turn whether the condition holds; a Stop hook "can run a script for deterministic checks or a prompt for model-evaluated ones." <https://code.claude.com/docs/en/goal>
[^claude-loop]: Anthropic, Claude Code docs, "Run prompts on a schedule" (`/loop`). Re-runs a prompt on a fixed or Claude-chosen interval until the user cancels it or Claude decides the work is done. <https://code.claude.com/docs/en/scheduled-tasks>
[^ralph-huntley]: Geoffrey Huntley, "Ralph Wiggum as a 'software engineer'" (2025-07-14). In its purest form, a Bash loop that feeds the same prompt file to a coding agent forever. <https://ghuntley.com/ralph/>
[^ralph-plugin]: Anthropic, `claude-plugins-official` repository, `plugins/ralph-loop` (command `/ralph-loop`). `--max-iterations` defaults to unlimited; `--completion-promise` matches an exact phrase; the README: "Always rely on `--max-iterations` as your primary safety mechanism." <https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop>
[^infra-noise]: Anthropic, "Quantifying infrastructure noise in agentic coding evals" (2026-02-05). A 6-percentage-point gap between the most- and least-resourced setups on Terminal-Bench 2.0 (p < 0.01); "leaderboard differences below 3 percentage points deserve skepticism until the eval configuration is documented and matched." <https://www.anthropic.com/engineering/infrastructure-noise>
[^flakiness]: Google Testing Blog, "Test Flakiness: One of the main challenges of automated testing." Cited for the existence and cost of flaky tests, which pass and fail against the same code; no list of causes is claimed from it. <https://testing.googleblog.com/2021/03/test-flakiness-one-of-main-challenges.html>
[^ial]: "When Agents Do Not Stop: Uncovering Infinite Agentic Loops in LLM Agents" (2026). Static analysis across 6,549 public LLM-agent repositories; 68 confirmed unbounded-loop failures across 47 projects, at 91.9% precision. Evidence for having a cap, not for any particular no-progress rule. <https://arxiv.org/abs/2607.01641>
[^openai-maxturns]: OpenAI Agents SDK docs, running agents. `Runner.run` accepts `max_turns`; exceeding it raises `MaxTurnsExceeded`. It bounds one run's own turns. Defaults change between versions; check the live docs. <https://openai.github.io/openai-agents-python/running_agents/>
[^langgraph-recursion]: LangGraph docs, Graph API, `recursion_limit` and `GraphRecursionError`. Bounds one graph execution's own steps. Defaults change between versions; check the live docs. <https://docs.langchain.com/oss/python/langgraph/graph-api>
[^swe-agent-cost]: SWE-agent documentation. `per_instance_cost_limit` and `total_cost_limit` bound spend in dollars regardless of turn count. Re-confirm parameter names against the installed version. <https://swe-agent.com/latest/reference/model_config/>
[^overfitting]: Smith, E., Barr, E., Le Goues, C., Brun, Y., "Is the Cure Worse Than the Disease? Overfitting in Automated Program Repair" (ESEC/FSE 2015). Patches generated and evaluated against the same test set can pass it while remaining incorrect, because tests are an imperfect proxy for correctness. <https://people.cs.umass.edu/~brun/pubs/pubs/Smith15fse.pdf>
[^metr-outer]: METR, "Recent Frontier Models Are Reward Hacking" (2025-06-05). Observed in evaluation runs, not production. Reward hacking in 30.4% of RE-Bench runs against 0.7% on HCAST, a 43x difference; the link to visibility of the scoring function is METR's own guess, alongside harder tasks or different scaffolding, not a measured cause. <https://metr.org/blog/2025-06-05-recent-reward-hacking/>
[^swebench-verified]: OpenAI, "Introducing SWE-bench Verified." A 500-sample, human-annotated subset of SWE-bench; hidden `FAIL_TO_PASS` tests tied to the issue and `PASS_TO_PASS` regression tests; 93 developers screened 1,699 samples for underspecified issues or unfair tests to select the 500. <https://openai.com/index/introducing-swe-bench-verified/>
[^replit]: vectara/awesome-agent-failures, "Replit AI Database Deletion Incident - July 2025." A user-reported incident during a 12-day experimental build; not a formal postmortem. <https://github.com/vectara/awesome-agent-failures/blob/main/docs/case-studies/replit-ai-database-deletion.md>
[^owasp-llm06]: OWASP Top 10 for LLM Applications, LLM06 Excessive Agency. <https://genai.owasp.org/llm-top-10/>
[^reflexion]: Shinn, N. et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (arXiv, 2023). <https://arxiv.org/abs/2303.11366>

## See also

- [1.2 Who Decides?](../foundations/who-decides.md): the two-loops framing this chapter puts to work.
- [2.5 The Agent Loop](../the-unit/the-agent-loop.md): the inner loop each attempt runs; a check the model calls itself stays there.
- [2.6 The Harness](../the-unit/the-harness.md): the code around the model in general; this chapter is its verification half.
- [3.4 Evaluator-Optimizer](evaluator-optimizer.md): the same loop with a model as the grader, for "done" conditions that need judgment, and where judge bias and the self-correction ceiling live.
- [4.2 Evaluation](../craft/proving-it-works.md): the verifier bottleneck and the generator-verifier gap (checking an answer costing less than producing one) in full generality.
- [4.3 Human-in-the-Loop](../craft/human-in-the-loop.md): where a give-up lands and how the person sees what was tried.
- [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md): blast radius and approval gates for the irreversible case.
- [5.4 Compaction](../knowledge/compaction-and-the-window.md): carrying lessons, not transcripts, between attempts.
- [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md): the infrastructure retry this chapter's retry must not be confused with, and retries of tools that are unsafe to call twice.
- [9.1 Long-Running Agents](../frontier/when-you-want-autonomy.md): the same loop run as a campaign over hours or days.
- [9.4 Sandboxing](../frontier/sandboxing.md): the execution boundary that keeps the verifier out of the agent's reach.
- [9.6 Coding Agents](../frontier/coding-agents.md): coding-agent operating patterns and plan-file conventions in depth.
- [9.7 Self-Improving Systems](../frontier/self-improving-systems.md): loops where the model edits its own prompt, tools or memory between attempts.
- [Anti-Patterns Catalog](../catalogs/anti-patterns.md): over-orchestration, including a loop where one validated call would do.
