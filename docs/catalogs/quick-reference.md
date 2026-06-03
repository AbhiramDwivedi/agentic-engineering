# Pattern Quick-Reference

> **The decision it resolves:** at a glance, what is each pattern — and should you trust it?

One row per pattern: its litmus verdict (new, or engineering you already knew?) and its maturity
verdict (standard, or hype?). Click through for the full chapter.

!!! note "Stub — rows fill in and link up as chapters land."

| Pattern | Who decides | Maturity |
|---|---|---|
| [Tool use](../the-unit/tool-use.md) | the model | Standard |
| [Structured output](../the-unit/structured-output.md) | a feature | Standard |
| [Prompt chaining](../composition/prompt-chaining.md) | your code (a draw) | Standard |
| [Dispatch ("the router that isn't")](../composition/the-router-that-isnt.md) | your code | Standard |
| [Fan-out / orchestrator-workers](../composition/fan-out.md) | the model (sizes its work) | Established |
| [Evaluator-optimizer](../composition/evaluator-optimizer.md) | the model | Established |
| [Specialist panel](../composition/specialist-panel.md) | the model | Emerging |
| [Retry & graceful degradation](../reliability/which-failures-sink-the-ship.md) | your code | Standard |
| [The observer rule](../reliability/a-silent-failure-is-worse.md) | your code | Standard |
| [Multi-agent](../frontier/more-than-one-agent.md) | the model | Contested |

The pattern is only the vocabulary. The judgement of which one a given step actually needs — and
the honesty to admit when the real answer is "this is just a retry loop" — is the job.
