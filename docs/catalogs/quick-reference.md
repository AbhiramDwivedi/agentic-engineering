# Pattern Quick-Reference

> **The decision it resolves:** at a glance, what is each pattern, and should you trust it?

One row per pattern: its litmus test (new, or engineering you already knew?) and its maturity
lens (standard, or hype?). Click through for the full chapter.

> **Stub: rows fill in and link up as chapters land.**

| Pattern | Who decides | Maturity |
|---|---|---|
| [Tool use](../the-unit/tool-use.md) | the model | Standard |
| [Structured output](../the-unit/structured-output.md) | a feature | Standard |
| [Prompt chaining](../composition/prompt-chaining.md) | your code (a draw) | Standard |
| [Dispatch table (front controller)](../composition/the-router-that-isnt.md) | your code | Standard |
| [LLM routing](../composition/the-router-that-isnt.md) | the model | Established |
| [Orchestrator-workers](../composition/fan-out.md) | the model (sizes its work) | Established |
| [Evaluator-optimizer](../composition/evaluator-optimizer.md) | the model | Established |
| [Specialist panel](../composition/specialist-panel.md) | the model | Emerging |
| [Retry & graceful degradation](../reliability/which-failures-sink-the-ship.md) | your code | Standard |
| [The observer rule](../reliability/a-silent-failure-is-worse.md) | your code | Standard |
| [Multi-agent](../frontier/more-than-one-agent.md) | the model | Contested |

## Which thing is picking the path?

Several patterns let something choose what runs next, and they get conflated in design reviews.
The useful question is not *who* decides but *when*, so this table sorts them by that.

| Pattern | Who decides | When the decision happens | Reach for it when |
|---|---|---|---|
| [Dispatch table](../composition/the-router-that-isnt.md) | your code | at table-authoring time; nothing decides at runtime | the input already carries a reliable label |
| [Semantic / embedding routing](../composition/the-router-that-isnt.md) | your code, via a trained artifact | per request, by similarity search, no model call | categories are stable and routing must be near-free |
| [LLM routing](../composition/the-router-that-isnt.md) | the model | once, up front, before any handler runs | categories are fuzzy, evolving, or need language judgment |
| [Tool use](../the-unit/tool-use.md) | the model | repeatedly, a fresh choice every turn | actions must be chosen step by step |
| [Skill selection](../the-unit/skills.md) | the model | inline, mid-response, with no classifier step | capabilities are documents the model reads and picks from |
| [Agent handoffs](../frontier/more-than-one-agent.md) | the model | mid-run, via a tool call that transfers control and history | a different agent should own the rest of the conversation |
| [Orchestrator-workers](../composition/fan-out.md) | the model | at planning time: how to split, how many workers | the work must be sized and split dynamically |
| [Model cascading](../production/controlling-cost.md) | your code or a small learned router | per request, by predicted difficulty or cost | the same task could run cheaper most of the time |

The pattern is only the vocabulary. The judgement of which one a given step actually needs, and
the honesty to admit when the real answer is "this is just a retry loop", is the job.
