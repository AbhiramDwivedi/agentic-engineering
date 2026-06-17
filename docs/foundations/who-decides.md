# 1.2 Who Decides?

<small class="chapter-meta">**Maturity: n/a** (this *is* the test other chapters are scored against) · *Who decides:* the lens itself · *Grounding:* the reference's classification lens</small>

*The one question that sorts any "agentic" pattern: who makes the structural decision, the model or your code? The model deciding is the only thing that is genuinely new. Everything else is engineering you already know with a model dropped into one slot.*

## Why you'd reach for it

The field has a labelling problem, and it costs money. There is no agreed-upon definition of "agentic," so vendors attach the word to almost anything: a chatbot, a rules engine, a scheduled script. Gartner gave the habit a name, "agent washing," and projects that the vague label sets up enough failed expectations that a large share of agentic-AI initiatives will be cancelled by the end of 2027.[^washing] When you cannot tell a genuine model-driven capability from a dictionary lookup wearing a costume, you cannot budget for it, staff it, or test it.

Here is the concrete version. Listing Studio, the pipeline this reference teaches through, turns a raw supplier feed into a published storefront listing across nine steps. Two of those steps look similar on a slide. Step 9, **publish**, maps the *Generate listing* event to the right graph: a fixed lookup, one event to one handler. Step 2, **clarify attributes**, drafts questions about the Aldsworth desk's missing specs, grades its own questions, and loops until they are good enough. Call both "intelligent routing" in a design review and you have hidden the only fact that matters for the budget: step 9 is deterministic and you unit-test it in milliseconds, while step 2 is non-deterministic, costs model calls on every loop, and can only be trusted after an eval suite. Same word, opposite cost and opposite risk.

There is one question that separates them, and it is the spine of this whole reference: **who makes the structural decision, the model or your code?** If the model makes the call, the pattern is genuinely new, because nothing in the pre-LLM toolbox could make a judgement call inside a control flow. If your code makes the call and the model is just the worker inside a fixed structure, it is a pattern you already know, and the "agentic" label is marketing.

Reach for this test:

- When you are about to call something a "pattern" and want to know if it is actually new.
- When a vendor, a colleague, or your own slide deck attaches "agentic" or "routing" or "orchestration" to a component.
- When you are estimating the cost, the failure mode, or the test strategy for a step, because the answer to "who decides" sets all three.
- When you are writing or reviewing a contribution to this reference, where the test is the gate.

The counter-trigger: this test tells you whether a pattern is *new*, not whether it is *good*. If your question is "should I trust this in production," that is the maturity lens, a different axis covered in [How We Label](../about/how-we-label.md). Do not reach for the litmus to settle a quality argument.

## What it actually is

The litmus test is that one question applied to a single pattern at a time. A structural decision is one that changes the control flow: which step runs next, whether to loop again, how many parallel branches to spawn, which path to take. Ask who owns that decision, the model or your code, and the pattern sorts itself.

When the model owns it, the pattern is genuinely new. There are four tells, and each is a real model-made decision you can point to in running code:

- **It calls a tool.** The model, not a branch in your code, decides that this turn needs a function call and which one. ([2.1 Tool Use](../the-unit/tool-use.md).)
- **It judges its own draft and loops.** The model grades its own output against a bar and decides whether to revise or stop. ([3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md).)
- **It sizes its own work.** The model reads a task, decides how many subtasks it splits into, and how many workers to spawn. ([3.3 Orchestrator-Workers](../composition/fan-out.md).)
- **It picks a persona.** The model chooses which kind of expert to reason as before it answers. ([3.5 The Specialist Panel](../composition/specialist-panel.md).)

When your code owns the decision and the model only fills a slot inside the structure, the pattern is one you already know. A lookup table that maps an event to a handler. A loop that retries on failure. A callback that fires when a step finishes. These are useful and often necessary. They are not new, and a model sitting somewhere inside them does not make them new.

**This is a classification lens, not a quality judgement.** That is the discipline it asks for. "Genuinely new" is not a compliment and "you already knew it" is not a demotion. The point is honesty about what changed, so a reader can budget and test for the real thing.

### A pattern is not a system

One sharp boundary keeps this chapter from overreaching. Passing the litmus means *a model made a structural decision somewhere in your code*. It does not mean your system is "an agent." Those are different questions at different scales, and conflating them is how the word "agentic" loses meaning.

There is no settled definition of "agentic," and a reference that pretends otherwise reads as naive: Simon Willison crowdsourced 211 definitions and sorted them into 13 categories before settling on one he could live with.[^willison] The author's working line, offered as opinion: **using an agent to do a piece of work is a workflow; an agent deciding what to do next is agentic.** It is a decision-based distinction, and it has a like-minded published authority in LangChain's Harrison Chase, who defines an agent as "a system that uses an LLM to decide the control flow of an application."[^langchain] Others set a higher bar at the level of the whole system, reserving "agent" for autonomous, multi-step work, or treating agency as a spectrum of degrees rather than a yes-or-no.[^anthropic][^openai][^gulli][^smolagents]

That debate does not need resolving here, because the patterns in this reference are useful either way. Workflow or agent, you reach for the same tools, the same contracts, the same loops, and the same guardrails. The deep autonomy-and-spectrum argument is [1.3 Workflow or Agent?](workflow-or-agent.md)'s job. What 1.2 keeps is only the boundary: a pattern can pass the litmus (a model made a structural call) while the system around it is still, by anyone's higher bar, a workflow.

## How to apply it

Apply the test the way you would profile a system: take it one component at a time, ask the one question, and write down the answer with the reasoning, not the label. Worked across a realistic pattern set, the test produces a humbling result.

Start with the easy passes. **Tool use:** the model decides this turn needs a function and which one, so the model decides. New. **Evaluator-optimizer:** the model grades its own draft and decides whether to loop, so the model decides. New. **Orchestrator-workers:** the model reads the task and sizes its own fan-out, so the model decides. New. **Specialist panel:** the model picks which expert lens to reason through, so the model decides. New. Four patterns where a model makes a judgement call inside the control flow, which nothing in the old toolbox could do.

Now the clear failures. **Retry with backoff:** your code decides to try again after a failure; the model is the operation being retried, not the decider. Old. **Graceful degradation:** your code decides to fall back to a cheaper path when the first fails. Old. **Observer and callbacks:** your code decides to fire a notification when a step finishes, so the dashboard never lies. Old. Each is resilience engineering that predates LLMs by decades, doing the same job with a model now sitting in one of the slots. ([Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md), [Observer](../reliability/a-silent-failure-is-worse.md).)

The sharpest case is the one most often mislabelled, and it is worth slowing down on.

### The dispatcher is not routing

The front door of Listing Studio maps the *Generate listing* event to the pipeline graph. It is tempting to file this under Anthropic's named **Routing** workflow and call it agentic. It is not routing, and the reason is precise.

Routing always contains a *classification decision*: an input arrives without a known label, and something has to decide which category it belongs to before it can be sent on. Anthropic defines routing as classifying an input and directing it to a specialized follow-up, with the classification "handled either by an LLM or a more traditional classification model/algorithm."[^anthropic] Gulli, writing independently, defines his Routing pattern the same way, as "dynamically directing user requests" based on classification, where the classifier may be LLM-based, embedding-based, rule-based, or ML-model-based.[^gulli] Both authorities agree the classifier need not be a model. So "routing needs an LLM" is the wrong correction.

The right correction is sharper: a static dispatch table has *no classifier at all*. The caller already knows the label. The *Generate listing* event arrives stamped with its type, and the dispatcher does one thing, a dictionary lookup from a key it was handed. There is no decision to make, by a model or by anything else, because the answer came in with the question. Anthropic's routing and Gulli's routing both contain a decision; a dispatch table contains none. That is the deflation in one line, and it is the thesis of this reference in miniature: the most "agentic"-sounding component in the pipeline turns out to be a `dict`. ([3.2 Front Controller](../composition/the-router-that-isnt.md) carries the full treatment.)

### The honest draw

One pattern refuses to sort cleanly, and saying so is part of the credibility. **Prompt chaining** splits a task into an ordered sequence of model calls. By the test, your code controls the order, so it is a pipeline, an old idea. But you split the task *because one model call could not hold the whole thing reliably*. The structure is old; the reason for it is new. Call it a draw and move on. ([3.1 Prompt Chaining](../composition/prompt-chaining.md).)

### Two that are not patterns

Two more in the catalog are not patterns at all. **Structured output**, constraining the model to return a typed shape, is a capability the model has, the junior partner to tool use, not a structure you arrange. ([2.2 Structured Output](../the-unit/structured-output.md).) **Two-pass generation** and **the humanizer** (the brand-voice polish in step 8) are local coinages, instances of broader ideas, useful labels for a team but not entries in any canon. ([6.2 Output Assembly](../io-boundary/producing-the-deliverable.md).) Naming them honestly as coinages, rather than selling them as discovered patterns, is the same discipline the litmus enforces everywhere.

Sort the whole set and it lands like this:

| The model decides (genuinely new) | Your code decides (engineering you knew) | A feature, or a coined name |
|---|---|---|
| Tool use | Front controller / dispatch | Structured output |
| Evaluator-optimizer | Retry with backoff | Two-pass generation |
| Orchestrator-workers | Graceful degradation | The humanizer pass |
| The specialist panel | Observer / callbacks | |

And one honest draw: **prompt chaining**, an old structure used for a new reason.

> **In Listing Studio.** Every cell of that table maps to a step in the nine-step pipeline. The genuinely-new four run inside steps 2, 5, 6, and 7; the engineering-you-knew four wrap the whole graph in resilience and reporting; the coinages live in steps 3 and 8. One pipeline, all three columns.

Four genuinely new, four old, three that are not patterns, one draw. The interesting question was never "which patterns did I use," it was "which ones did the model actually change."

## Gotchas

The litmus is a sorting tool, and like any sorting tool it can be misread. Three cautions.

**New is not good.** The most common misread is to treat "the model decides" as praise and "your code decides" as a demerit. It is neither. The litmus answers *is this new*; it says nothing about *is this proven*. These are orthogonal axes, and they co-exist on every technique chapter. A "your code decides" pattern can be **Standard** and battle-tested: retry with backoff is about as proven as software gets, and it is firmly in the old column. A "the model decides" pattern can be **Contested**: fully autonomous agents pass the litmus easily and are still overclaimed today. The two labels do different jobs. [How We Label](../about/how-we-label.md) carries the maturity axis; read the two together, never one as the other.

**Classifying a pattern is not classifying a system.** The other misread runs the boundary from the What section the wrong way. A pipeline can contain four model-made decisions and still be, by the higher autonomy bar, a workflow rather than an agent. Do not let a passing litmus on one component tempt you into calling the whole system "an agent." That argument lives in [1.3 Workflow or Agent?](workflow-or-agent.md), and it has a different answer.

**The cost of getting it wrong is concrete, which is why it is worth the care.** Mislabel a deterministic dispatch table as "intelligent routing" and you set three wrong expectations at once. You budget for model calls a `dict` will never make. You plan for a non-deterministic failure mode that cannot occur, and miss the one that can. Worst, you reach for the wrong test entirely: the deterministic branch needs only a unit test, while the model-made call needs **evals** to know it works at all.[^anthropic] [4.2 Evaluation](../craft/proving-it-works.md) covers that distinction. The label is not a word game; it is the thing that tells a technical leader where the real risk sits.

The discipline that falls out of all three: **when in doubt, downgrade the claim.** If you cannot point to the specific model-made decision, the honest default is to classify the pattern as "your code decides," and a coinage as a coinage, not as canon. This is also the contribution rule. A pull request that sells a "code decides" pattern as agentic, or a local coinage as a discovered pattern, gets sent back, however good the writing. ([Contributing](../contributing.md).)

## In short

For any pattern you meet, ask the one question and write down the reasoning: *who makes the structural decision, the model or your code?* If you can point to a real model-made decision, the pattern is genuinely new, and you should budget and test for non-determinism. If your code owns the decision and the model only fills a slot, you have a pattern you already know, and the "agentic" label is doing marketing's work, not engineering's. Hold the result against the second axis: new is not the same as good, and a passing pattern does not make the system an agent. When you cannot tell, downgrade the claim. It is the honest move, and the one that protects the credibility this reference is built to sell.

## Sources

[^anthropic]: Anthropic, "Building Effective Agents" (19 Dec 2024). The five named workflow patterns include **Routing**, defined as "Routing classifies an input and directs it to a specialized followup task," with classification "handled … either by an LLM or a more traditional classification model/algorithm." The workflow-vs-agent distinction: workflows are "systems where LLMs and tools are orchestrated through predefined code paths" versus agents, "systems where LLMs dynamically direct their own processes and tool usage." <https://www.anthropic.com/research/building-effective-agents>
[^langchain]: Harrison Chase / LangChain, "What is an agent?": "an agent is a system that uses an LLM to decide the control flow of an application." <https://www.langchain.com/blog/what-is-an-agent>
[^gulli]: Antonio Gulli, *Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems* (Springer Nature, 2025; ISBN 9783032014016). Defines an agent as "a system designed to perceive its environment and take actions to achieve a specific goal." Routing is Chapter 2: "dynamically directing user requests to specialized handlers, agents, or processing paths based on classification," where the classifier may be LLM-based, embedding-based, rule-based, or ML-model-based. Free draft circulated by the author; verify exact wording against the print edition before quoting. <https://link.springer.com/book/10.1007/978-3-032-01402-3>
[^openai]: OpenAI, "A Practical Guide to Building Agents" (April 2025): "Agents are systems that independently accomplish tasks on your behalf." Explicitly excludes apps that integrate LLMs but do not use them to control workflow execution (single-turn chatbots, sentiment classifiers). <https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/>
[^smolagents]: Hugging Face, *smolagents* documentation, "Introduction to Agents": agency framed as a spectrum of degrees, where an LLM that merely controls an if/else branch ("Router") is rated low agency. <https://huggingface.co/docs/smolagents/conceptual_guides/intro_agents>
[^willison]: Simon Willison, "I think 'agent' may finally have a widely enough agreed upon definition to be useful" (18 Sept 2025): settles on "An LLM agent runs tools in a loop to achieve a goal," after grouping 211 crowdsourced definitions into 13 categories. <https://simonwillison.net/2025/Sep/18/agents/>
[^washing]: Gartner, "agent washing" (2025): vendors rebrand existing RPA and chatbots as "agents" because no universal definition exists; Gartner projects over 40% of agentic-AI projects will be cancelled by end of 2027. Treat as industry-analyst signal, not a technical authority. <https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027>

## See also

- [1.3 Workflow or Agent?](workflow-or-agent.md), which owns the autonomy-and-spectrum half of the definitional debate this chapter deliberately leaves open.
- [How We Label](../about/how-we-label.md), the maturity axis the litmus is orthogonal to: this lens asks *is it new*, that one asks *is it proven*.
- [2.1 Tool Use](../the-unit/tool-use.md), [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md), [3.3 Orchestrator-Workers](../composition/fan-out.md), [3.5 The Specialist Panel](../composition/specialist-panel.md), the four "model decides" patterns this chapter only names.
- [3.2 Front Controller](../composition/the-router-that-isnt.md), the dispatcher deflation in full: why a dispatch table is not Anthropic's Routing.
- [3.1 Prompt Chaining](../composition/prompt-chaining.md), the honest draw: an old structure used for a new reason.
- [4.2 Evaluation](../craft/proving-it-works.md), why the non-deterministic "model decides" branch needs evals where the deterministic branch needs only unit tests.
- [Contributing](../contributing.md), where "when in doubt, downgrade the claim" becomes the review gate.
