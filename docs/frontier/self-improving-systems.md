# 9.7 Self-Improving Systems

*Systems that improve their own prompts, skills, memory, code or harness, graded by what is being improved and by whether the gains survive a held-out check.*

*Also called: self-improving agents, prompt optimization (DSPy, GEPA), skill and memory evolution, autoresearch, evolutionary code search.*

## Why you'd reach for it

Call GEPA, a prompt optimizer in DSPy (a library that tunes the prompts of a model pipeline against your metric),[^dspy-paper] without a selection set, the examples that decide which rewritten prompt wins, and it does something reasonable-sounding: it logs a warning and scores its candidate prompts on the training examples instead.[^dspy] The run finishes, the best prompt comes back with a score, and that score was measured on the same data the optimizer learned from. Nothing failed, and you now hold a number that cannot tell you whether the new prompt is better on the next input.

Every self-improving system has a part that changes and a part that decides whether the change was good. GEPA's default lets the first part grade its own homework. The field's results hold up where the grader is honest and out of the optimizer's reach, and they evaporate where it is not.

An agent that makes the same mistake on Tuesday that it made on Monday is wasting your money, and the fixes you get inside a single run (a critic catches the error, the model revises, see [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md)) vanish when the run ends.

Take a product-listing pipeline that drafts the description for each product in a supplier's feed. A reviewer edits those drafts before they publish, and every edit is a small complaint about the prompt. You collect a few hundred of them and point an optimizer at the description prompt. If the same examples drive the rewrites, pick the winner and report the final score, the prompt learns the quirks of those products: the sit-stand desks, their height ranges, the phrasing that particular reviewer likes. Then it ships to every listing in the catalog on the strength of a number it was tuned to produce.

The fix takes two disciplines. Keep the data the optimizer learns from apart from the data that accepts or rejects its edits, and keep both apart from a final test you touch once. Then put the scorer, the test set and the promotion step (the code that writes an accepted change into the live system) outside what the optimizer is allowed to edit.

Reach for self-improvement when:

- **A failure recurs across runs** and you can describe it with examples.
- **A cheap, honest score exists**: an execution result, a passing test, a measured edit distance, something the candidate cannot argue with.
- **The artifact is diffable and revertible**: a prompt file, a skill document, a function.
- **You have enough examples to hold some back** without starving the optimizer.

When you cannot score the outcome or cannot undo the change, do not build the loop. Fix the prompt by hand, add the failing cases to your evaluation suite ([4.2 Evaluation](../craft/proving-it-works.md)), and let a person promote the change.

## What it actually is

A self-improving system is a loop that proposes changes to an artifact the system will reuse in future runs (a prompt, a skill, a memory, a program, the harness itself), scores each candidate against data, and keeps only the candidates that pass. Persistence is the defining property. A change that disappears when the task ends is revision inside a run, and it belongs to 3.4.

![The proposer (the model) reads failures in the feedback set and writes one edit to a candidate artifact inside a dashed editable surface: a prompt file, a skill document or code. Your code scores the candidate on a selection set the proposer never sees, and a gate checks whether it beats the current version by a margin. A failure returns a rejection message to the proposer and leaves the live system untouched. A pass becomes a versioned diff that only the promotion step writes to the live system. The evaluator, the held-out test set and the promotion step are locked outside the editable surface](self-improving-systems-gate.svg)

The model decides what to try. It reads failures, reflects on them in language, and writes a new candidate, and that part is agentic. Whether that candidate goes live should be your code's decision. Andrej Karpathy's `autoresearch` repository is the counter-case. It gives a coding agent a training script and a fixed five-minute budget per experiment, and its `program.md` tells the agent to keep a commit if `val_bpb` (a validation loss where lower is better) improved and run `git reset` otherwise.[^autoresearch] The keep-or-discard decision there is the agent following an instruction, and no controller checks that it did. That is a fine trade for a research toy; in production the check belongs in code the agent cannot skip.

The survey by Ren and colleagues organizes the field by the target being updated and by the signal driving the update.[^survey] The targets differ in blast radius and in how you roll them back:

- **A prompt**: one text file, reviewed as a diff, reverted with version control.
- **A skill document or memory playbook**: text the agent loads on demand, which grows and can rot.
- **Program or harness code**: the tools, the loop, the scaffolding. A bad edit here can break every run.
- **Weights**: a fine-tune, covered in [8.3 To Train or to Prompt](../production/train-or-prompt.md) and out of scope here.

The evidence sorts along the same list. Tuning a prompt against a held-out eval is Established, because it is the eval discipline teams already run. The optimizers that automate the tuning are Emerging: they are open source and the artifact is a text file, but the headline figures for GEPA are its authors' own.[^gepa] Skill, memory and harness editing with an execution-based check is Emerging too, supported by preprints and a few peer-reviewed results. Agents that rewrite their own code are Contested as a production practice: the gains were measured under sandboxing and human oversight, their authors warn the edits can introduce vulnerabilities, and no independent production replication was found as of 2026-11. Reading them as proof of production readiness overclaims them.

Three neighbours get confused with this. [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md) critiques and revises within one task and forgets afterwards. [3.7 The Outer Loop](../composition/the-outer-loop.md) is your code retrying a task until a check passes; nothing it learns carries to the next task. [5.3 Memory](../knowledge/real-memory.md) owns how an agent writes and reads what it remembers; this chapter owns the gate a learned write must pass before it is trusted.

## How to do it

### Keep three sets of data apart

Loops scored on sampled data keep three data roles apart. The **feedback set** is what the optimizer reads: the failures and scores it reflects on to write candidates (DSPy's `trainset`). The **selection set** decides whether a candidate replaces the current version, and it is queried every round (DSPy's `valset`). The **test set** is touched once, at the end, to report the number you will believe.

The selection set needs its own wall because it is queried repeatedly. Each accept-or-reject decision leaks a little information about it, and after enough rounds the winner has fitted the selection set much as it would have fitted the training data. Blum and Hardt describe this adaptive overfitting for competition leaderboards, where repeated submissions let entrants climb a public score without improving on fresh data.[^ladder] A rule that accepts any strict improvement makes it worse. On a few dozen examples a one-point gain is often noise, and every noisy win is kept, so the search accumulates whatever happened to fit those examples. Compare candidates with an uncertainty-aware test (a confidence interval, say), require a margin, and re-run the cases the current version already gets right as a regression check. The statistics of that comparison belong to [4.2 Evaluation](../craft/proving-it-works.md).

The strongest support for an honest grader comes from VERSE, a preprint on evolving agent scaffolds: in a controlled study, self-evolution failed without verification by executing the candidates.[^verse] SkillOpt, a preprint on optimizing agent skill documents, shows the three-way split in practice. It accepts edits on a selection split, reports on a separate test split, and feeds the score drops of rejected edits back into later reflection.[^skillopt] Its acceptance rule is any strict improvement, so on a small selection set add the margin it lacks.

Two details the figure cannot show: bound the size of each edit, so a rejection points at one change, and log every rejected candidate as well as returning it to the proposer. The test set runs once, after the last round.

### Start with the prompt

The targets form a ladder of rungs ordered by blast radius: prompt, then skills and memory, then code and harness. The prompt is the rung to try first because the artifact is a text file and the scorer is usually your existing eval. OPRO, an earlier line, showed a model could propose better prompts given a history of prompts and their scores.[^opro] GEPA adds reflection: the model reads execution traces in natural language and writes rules into the prompt. On their six tasks, its authors report beating GRPO (a reinforcement-learning method that updates model weights) by 6% on average and by up to 20%, while using up to 35 times fewer rollouts (a rollout is one full run of the system on a task). They also report beating MIPROv2, DSPy's earlier prompt optimizer, by over 10%.[^gepa]

You can run this today. `pip install gepa` gets the standalone optimizer, and DSPy exposes it as `dspy.GEPA`.[^gepa-repo] Pass `valset` every time. The `dspy.GEPA(...)` constructor requires exactly one budget setting, `auto`, `max_full_evals` or `max_metric_calls`, and a `reflection_lm` to write the rewrites.[^dspy] A minimal sketch:

```python
# Untested sketch.
import dspy

def metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
    score = similarity(pred.description, gold.description)  # your scorer, 0 to 1
    return dspy.Prediction(score=score, feedback=f"reviewer wrote: {gold.description}")

optimizer = dspy.GEPA(
    metric=metric,
    auto="light",  # exactly one budget option
    reflection_lm=dspy.LM("anthropic/claude-sonnet-5-5"),
)
optimized = optimizer.compile(
    program,
    trainset=feedback_set,   # what the optimizer reflects on
    valset=selection_set,    # what picks the winner; never omit it
)
# The metric must take five arguments; its feedback text is what reflection reads.
# Score `optimized` once on the sealed test set.
```

Review the winning prompt as a diff before it ships, as you would any change to source ([4.1 Prompt Architecture & Management](../craft/prompts-are-source-code.md)).

### Skills, memory and playbooks

The next rung keeps learned material outside the prompt and loads it when relevant. Voyager, a Minecraft agent, wrote code skills into a library and kept only those that passed a self-verification check before reuse.[^voyager] ACE (Agentic Context Engineering) treats the agent's context as a playbook it curates incrementally, offline and online, and reports gains of about 10.6% on agent benchmarks.[^ace] Its authors name two failure modes: *context collapse*, where repeated whole-playbook rewrites erode detail, and *brevity bias*, where the optimizer drifts toward short generic advice. Their remedy is structure (itemized entries, incremental edits) beside the acceptance check.

Each lesson costs tokens and attention on every run that loads it. Retrieve lessons on demand instead of loading the library, prune entries that never fire, consolidate duplicates, and regression-check the library after each change. Loading mechanics live in [2.3 Skills](../the-unit/skills.md) and [5.3 Memory](../knowledge/real-memory.md).

### Code and harness, where the verifier does the work

AlphaEvolve shows what the loop can do when the score is cheap and exact. A model mutates programs, automated evaluators score them, and a population of the best is kept; among its reported results is a procedure for multiplying 4x4 complex matrices with 48 scalar multiplications.[^alphaevolve] The evaluator carries the result, because a matrix product is either correct or wrong and the model never grades itself. That limits it to problems with a cheap, honest score.

The Darwin Gödel Machine pushes further: an archive of coding agents that edit their own code, with each variant scored on coding benchmarks. Its authors report SWE-bench (real GitHub issues the agent must fix) rising from 20.0% to 50.0% and Polyglot (coding tasks across several languages) from 14.2% to 30.7%, with gains transferring across benchmarks and models, all under sandboxing and human oversight.[^dgm] In their safety discussion they warn that changes optimized only for a benchmark "might inadvertently introduce vulnerabilities." Hyperagents also makes the improvement procedure itself editable,[^hyperagents] which widens the editable surface from the candidate to the procedure that improves it.

### The promotion contract

Treat a self-proposed change as a change request from a colleague you have not met: a versioned diff, a hard gate or a human reviewer ([4.3 Human-in-the-Loop](../craft/human-in-the-loop.md)), a rollback path and a log entry. The candidate never writes to the live system directly. Artifact versioning belongs to 4.1 and the audit trail to [8.6 Governance & Compliance](../production/governance-and-compliance.md).

## Security & trust

Once a system is rewarded for raising a score, the cheapest path to a higher score may run through the scorer, which makes the evaluator the thing to defend. Research has measured the first step: STOP, a self-improving code optimizer, reported generated code that tried to bypass its sandbox.[^stop] The following are reasoned scenarios rather than production incidents: a candidate that deletes a failing test, loosens a threshold in the config the evaluator reads, games a metric that rewards length or keyword overlap, or wins because the judge is the same model family as the proposer and shares its blind spots. Huang and colleagues found that models correcting their own reasoning without external feedback were unreliable.[^huang] Their tasks were reasoning problems, not prompt edits, but the step carries: a model judging whether its own edit helped is self-correction without external feedback, so its sense that it improved cannot stand in for the check.

The defence is an authority boundary your code enforces. The optimizer may change only a declared editable surface: this prompt file, this skill directory. The evaluator, the test data, the permissions policy, the hooks and the promotion step live outside it, where the candidate cannot read or write them. Reviewing an evaluator diff after a run does not help, because a candidate that weakened the evaluator mid-trial has already been scored by the weakened version. Keep a sealed test set the proposer cannot read, and run deterministic checks beside any model-judged ones. The harness controls are in [2.6 The Harness](../the-unit/the-harness.md), isolation in [9.4 Sandboxing](sandboxing.md), and poisoned feedback turning into a poisoned update is the injection risk in [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md).

The cautionary case is an autonomous repricing agent, one that watches competitor prices and adjusts its own prices within rules. Let it propose edits to its pricing-strategy prompt and score them on margin, and it is doing self-improvement. Let it edit the rules that bound it, the price floors and the margin limits, and the margin score can rise on the selection set while the live catalog sells below cost.

## Gotchas

- **The bill scales with population times iterations.** Each round costs the candidate rollouts plus a full evaluation on the selection set, and model-judged scores multiply that. Budget it before you start ([8.4 Controlling Cost](../production/controlling-cost.md)).
- **The selection set goes stale.** It wears out from repeated queries and drifts away from live traffic as your inputs change. Refresh it on a schedule and keep the test set sealed.
- **Retrying with feedback looks like learning.** Reflexion reports 91% pass@1 (solved on the first scored attempt) on HumanEval, a Python coding benchmark, and that figure comes from retrying the same task with feedback from its tests.[^reflexion] Its memory carries across attempts at one task, not to new tasks, so it sits on the 3.4 side of the boundary, and it says nothing about durable gains on unseen tasks.
- **Online learning from live traffic has no efficacy evidence yet.** Yan and colleagues argue that self-evolving agents trained on production traffic are held back by gaps in agentic reinforcement-learning systems, and introduce AReaL2.0 as one implementation; the abstract reports no experimental results.[^areal] Treat it as a direction.
- **A revertible file can have irreversible effects.** Reverting the prompt does not unpublish the listing copy it wrote while live, so the rollback plan has to cover what the change touched.

## In short

Start with offline prompt optimization against your existing eval, with an explicit selection set, a sealed test set, and the winning prompt reviewed as a diff. Move to skill or playbook evolution only when you have an execution-based check and a pruning habit. Leave agents that rewrite their own code and harness in the lab until someone publishes a production replication. On every rung, the evaluator and the promotion step stay outside the optimizer's reach, and a gain counts only when it holds on data the optimizer never selected on.

<small class="chapter-meta">**Maturity: Emerging / Contested** (eval-driven prompt tuning is Established; prompt optimizers and skill, context and harness editing are Emerging; self-modifying agents in production are Contested) · *Who decides:* the model proposes, your code promotes · *Grounding:* research · *Last reviewed:* 2026-11</small>

## Sources

[^dspy]: Stanford NLP, DSPy, `dspy.GEPA` (`dspy/teleprompt/gepa/gepa.py`). When `valset` is omitted, `compile` warns and uses the trainset; the constructor requires exactly one of `auto`, `max_full_evals`, `max_metric_calls`, and a `reflection_lm` or custom instruction proposer. Library API, volatile; checked 2026-11. <https://github.com/stanfordnlp/dspy>
[^autoresearch]: Karpathy, A., `autoresearch`, `program.md` (MIT licence). <https://github.com/karpathy/autoresearch>
[^survey]: Ren et al., "Self-Improvements in Modern Agentic Systems: A Survey" (2026). Preprint; the target-and-signal organization is taken from the abstract. <https://arxiv.org/abs/2607.13104>
[^ladder]: Blum, A. and Hardt, M., "The Ladder: A Reliable Leaderboard for Machine Learning Competitions" (2015). <https://arxiv.org/abs/1502.04585>
[^skillopt]: Yang et al., SkillOpt (2026). Preprint, not peer-reviewed as of review. <https://arxiv.org/abs/2605.23904>
[^verse]: Wang et al., VERSE (2026). Preprint, not peer-reviewed as of review. <https://arxiv.org/abs/2610.02616>
[^dspy-paper]: Khattab, O., et al., "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines" (2023). <https://arxiv.org/abs/2310.03714>
[^opro]: Yang, C., et al., "Large Language Models as Optimizers" (2023). <https://arxiv.org/abs/2309.03409>
[^gepa]: Agrawal, L. A., et al., "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning" (v2, 2026-02-14). Figures are the authors' own, across six tasks. <https://arxiv.org/abs/2507.19457>
[^gepa-repo]: gepa-ai, `gepa` README. <https://github.com/gepa-ai/gepa>
[^voyager]: Wang, G., et al., "Voyager: An Open-Ended Embodied Agent with Large Language Models" (2023). <https://arxiv.org/abs/2305.16291>
[^ace]: Zhang, Q., et al., "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models" (2025; ICLR 2026). <https://arxiv.org/abs/2510.04618>
[^alphaevolve]: Novikov, A., et al., "AlphaEvolve: A coding agent for scientific and algorithmic discovery" (2025). <https://arxiv.org/abs/2506.13131>
[^dgm]: Zhang, J., Hu, S., Lu, C., Lange, R., Clune, J., "Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents" (2025). Held-out transfer in Section 4.4; the vulnerabilities quote is from the safety discussion in Section 5. Authors' results. <https://arxiv.org/abs/2505.22954>
[^hyperagents]: Zhang et al., Hyperagents (2026). Preprint. <https://arxiv.org/abs/2603.19461>
[^stop]: Zelikman, E., et al., "Self-Taught Optimizer (STOP): Recursively Self-Improving Code Generation" (2023). <https://arxiv.org/abs/2310.02304>
[^huang]: Huang, J., et al., "Large Language Models Cannot Self-Correct Reasoning Yet" (2023). Supports only that intrinsic self-correction without external feedback is unreliable. <https://arxiv.org/abs/2310.01798>
[^reflexion]: Shinn, N., et al., "Reflexion: Language Agents with Verbal Reinforcement Learning" (2023). The 91% figure is from the abstract. <https://arxiv.org/abs/2303.11366>
[^areal]: Yan, R., et al., "Next-Generation Agentic Reinforcement Learning Systems Enable Self-Evolving Agents" (2026). The abstract argues a thesis and introduces AReaL2.0 as one implementation; it reports no experimental results. <https://arxiv.org/abs/2607.01120>

## See also

- [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md): the critique-and-revise loop inside one run, which this chapter extends across runs.
- [4.2 Evaluation](../craft/proving-it-works.md): how to build the scorer and the held-out comparison the gate depends on.
- [5.3 Memory](../knowledge/real-memory.md): how learned lessons are written and read, and how they get poisoned.
- [2.6 The Harness](../the-unit/the-harness.md) and [9.4 Sandboxing](sandboxing.md): the boundary that keeps the evaluator out of the optimizer's reach.
- [8.3 To Train or to Prompt](../production/train-or-prompt.md): when the artifact to improve is the weights.
- [1.5 Context Engineering](../foundations/context-engineering.md) and [5.4 Compaction](../knowledge/compaction-and-the-window.md): what accumulated lessons cost the context window.
