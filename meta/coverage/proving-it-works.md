# Coverage map: Evaluation (chapter 4.2)

> Spec for the chapter, not a draft. Stub at `docs/craft/proving-it-works.md` has no prose, so nothing is marked `[*]`/`[+]`. Sweep angles run: vendor docs, academic, practitioner, skeptical read, incidents (none found; stated below), daily-tool (partial). Alias sweep (angle 7) not run. Neighbours: 4.1 Prompt Architecture (unshipped; owns prompt versioning, golden cases, the release gate), 3.7 The Outer Loop (unshipped; owns code-owned verification and reward hacking), 3.4 Evaluator-Optimizer (shipped stub; the model grading its own draft at runtime). Last reviewed 2026-11.

## The mental model

An eval is a test suite for behavior that differs between runs. A unit test asserts one output; an eval samples many inputs, grades each output against a stated bar, and reports a rate, so a prompt, model, or tool change becomes a measured delta and not an impression. The chapter's spine is the boundary the reference already draws: where code decides, ordinary tests suffice; where the model decides, you need evals ([who-decides](../foundations/who-decides.md) points here for exactly this). The reader should leave able to build a small golden set from real failures, pick a grader per criterion (code first, model where necessary, human to calibrate), and know that the judge is itself a model that needs checking.

**Who decides:** your code. The eval harness owns the cases, the aggregation and the gate; a model judge contributes a per-case verdict and never controls flow (unlike [3.4](../composition/evaluator-optimizer.md), where the grader steers the runtime loop).

**Thesis candidate:** "An eval score is evidence only to the extent that its cases came from real failures, its graders were checked against people, and its rate is read with its noise."

## Must-cover (ranked)

1. **Why unit tests are not enough, and what an eval is.** Same input, different outputs; one green run is an anecdote. Skip it and teams ship on vibes. Verdict: Established. Lead: Anthropic, "Define success criteria and build evaluations"; Anthropic, "Demystifying evals".
2. **Build the golden set from real failures, small first, by error analysis.** Read traces, name failure modes, then write cases and graders for those; generic metrics (helpfulness) predict nothing. Start with tens; each case needs an unambiguous expected result. Skip it and the set measures what the author imagined. Verdict: Established (error analysis: practitioner consensus, not formally studied). Lead: Anthropic, "Demystifying evals" ("20-50 simple tasks drawn from real failures is a great start"); Husain; Anthropic multi-agent post ("about 20 queries"). Sequencing, not a dispute: develop-tests favours volume with automated grading, Demystifying favours a small unambiguous set first; read transcripts to check the graders.
3. **Grader taxonomy: code, then model, human to calibrate.** Anthropic develop-tests: choose "the fastest, most reliable, most scalable method"; code first, human grading "Avoid if possible," model grading tested for reliability first. Code graders are cheap but brittle. **Worked sub-case: a classifier step** (shipped [3.2](../composition/the-router-that-isnt.md) promises this): labelled inputs, a code grader against the label, per-category precision and recall, and a confidence threshold (3.2's `0.6` floor) chosen from the data, not guessed. Verdict: Established. Lead: Anthropic develop-tests; "Demystifying evals" (prefer deterministic graders). Offline graders get gamed too: "Make your graders resistant to bypasses or hacks" (one sentence, link 3.7).
4. **LLM-as-judge, and its measured biases.** Position, verbosity, and self-enhancement bias; judge agreement with humans can match human-human agreement on some tasks. Mitigate by swapping order, binary or anchored-scale criteria, and (Demystifying) "an isolated LLM-as-judge" per dimension; the multi-agent post found one call scoring 0.0-1.0 most consistent for its case, so the right setup is empirical, which is item 5's point. Skip it and the judge silently rewards length or its own style. Verdict: Established, with an argued caveat on judge reliability. Lead: Zheng et al. 2306.05685; Wang et al. 2305.17926; Panickssery et al. 2404.13076; survey Gu et al. 2411.15594.
5. **Validate the validator.** Measure judge vs human labels on a labeled slice (precision/recall for binary, Cohen's kappa for agreement) before trusting the score; re-check when the judge model or prompt changes. Criteria themselves drift as people grade. Verdict: Emerging (the need is clear, the practice is thin). Lead: Shankar et al. 2404.12272; Yan, "Evaluating the Effectiveness of LLM-Evaluators".
6. **Noise: report a rate with its uncertainty, and repeat trials.** A rate over 20 cases has a wide error bar, so a 5-point move between prompt versions can be noise; repeat trials per case (Demystifying: "we run multiple trials to produce more consistent results") and compare with error bars. Run-to-run: pass@k (at least one success) vs pass^k (all k succeed) coincide at k=1 and diverge; customer-facing work needs the second. Skip it and teams chase noise. Verdict: Established for the statistics, Emerging for practice in LLM evals. Lead: Miller 2411.00640; tau-bench 2406.12045; Demystifying.
7. **Agent evals: grade the outcome, read the transcript.** Final state beats exact step sequence; trajectories are inspected to separate agent error from grader error. Humans still catch what evals miss. Verdict: Emerging. Lead: Anthropic "Demystifying evals"; Anthropic multi-agent post ("People testing agents find edge cases that evals miss").
8. **Offline vs online, and the three-level cost ladder.** Unit-style assertions every change, human and model review of logged traces, then A/B tests for mature products. Production traces feed the golden set. Verdict: Established (offline vs online); the three-level ladder is Husain's framing, attribute it. Production failures feed the golden set (Demystifying, "drawn from real failures"). Lead: Husain.
9. **Capability vs regression evals, and overfitting.** Demystifying: capability evals ask "What can this agent do well?", regression evals ask "Does the agent still handle all the tasks it used to?"; saturation is when an agent passes all solvable tasks, so graduate saturated capability tasks into the regression set. A set you tune against stops measuring. Boundary: the release gate consumes the regression set and is 4.1's. Verdict: Established. Lead: Demystifying.

## Mention-and-link

- Prompt versioning, golden cases as a release gate: [4.1 Prompt Architecture](prompts-are-source-code.md) (planned). Say "the gate consumes this chapter's set" and stop.
- Code-owned verify-and-retry, reward hacking, the grader the agent can game: 3.7 The Outer Loop (planned).
- A model grading its own draft at runtime: [3.4 Evaluator-Optimizer](../composition/evaluator-optimizer.md). Contrast: that is a loop inside the product; this is measurement of the product. Same judge caveats apply.
- Classifier and routing steps: [3.2 The Router That Isn't](../composition/the-router-that-isnt.md) points here for its confidence floor; see item 3.
- Schema adherence as a metric: [2.2 Structured Output](../the-unit/structured-output.md) already points here; schema validity is a code grader.
- Decomposition varying run to run: [3.3 Orchestrator-Workers](../composition/fan-out.md) points here.
- Retrieval quality metrics (recall, groundedness): 5.2 RAG owns them; this chapter names them as graders only.
- Guardrails and human review at runtime: 4.4 and 4.3.

## Out of scope

Public leaderboards and model benchmarks (a different question: which model, not does my system work; one sentence on contamination at most). Training-time reward models. Red-teaming and prompt-injection testing (4.6). Observability tooling as a product survey. Pricing and platform comparisons.

## Maturity summary

- **Established:** golden sets from real failures; error analysis; code graders; regression runs; the cost ladder.
- **Established, with a caveat:** LLM-as-judge (works on bounded criteria; biases documented; calibration required). The stub's lens parenthetical should read "the method is settled; judge reliability is the moving part."
- **Emerging:** judge validation practice; pass^k reporting; agent trajectory grading; criteria drift handling.
- **Contested:** none. Volume vs reading data is sequencing (item 2), not two camps.

**Verdict candidate: Established**, with an argued sentence that the method is settled and judge reliability and agent evals are the moving parts. Last reviewed 2026-11. Downgrade to Emerging only if the author wants the agent-eval half to carry the verdict.

## Aliases (angle 6, partial)

evals, LLM-as-judge, golden set (stub); eval-driven development; model-graded evals; graders (Anthropic, OpenAI); test set. Gulli's books are not checked; alias sweep pending.

## Reader-verifiable anchors

Inspect (UK AI Security Institute and Meridian Labs, https://inspect.aisi.org.uk/): a dataset "provides labelled samples," a solver "produces an answer for each sample," a scorer "evaluates the output." Public and runnable. The OpenAI hosted Evals platform is deprecated (read-only 2026-10-31, shutdown 2026-11-30); do not anchor on it.

## Carrier section

Primary anchor Listing Studio, Stockwell. Golden set: cases across the Aldsworth desk, the bunk bed and the phone case (the bible's empty case: a grader must pass a correct do-nothing), plus listings a merchandiser corrected before publish; each a case (supplier feed in, expected required attributes out). Code grader first: schema validity, required fields, price within the supplier's minimum advertised price and margin rule. Model grader only for what code cannot see: whether the description invents a specification not in the feed (faithfulness, direct scoring), calibrated on a human-labeled slice. The step-2 clarify loop (evaluator-optimizer) shows the boundary: its runtime grader is a product feature; the eval measures whether that grader's questions are any good. Do not reach for the merchant helpdesk unless retrieval metrics are needed. Grounding: research; no "From production:" callout.

## Gotchas (feed Anti-Patterns)

- Judging with the same model that wrote the output (self-preference; develop-tests advises a different model).
- Unanchored 1-10 scales; anchor the endpoints or prefer binary per criterion.
- Generic metrics (helpfulness) in place of failure-specific ones.
- Eval set built from imagined inputs, never refreshed from production.
- Tuning the prompt to the golden set until it measures nothing.
- Treating one green run, a pass@k number, or a 5-point delta on 20 cases as reliability.
- Never reading transcripts, so grader bugs read as agent failures.
- Rigid step-sequence graders that fail valid alternative paths.
- Judge prompt or model changed silently; scores move for the wrong reason.

## Incidents

None found: no public agent postmortem attributing a production failure to missing evals was located. State this plainly; do not invent one.

## Named-idea candidates (offer, never force)

"Golden set from real failures"; "validate the validator"; "rate, not run". Plain descriptions, none a coinage claim.

## Sources

1. Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena," arXiv 2306.05685, submitted 2023-06-09; NeurIPS 2023 Datasets and Benchmarks; ">80% agreement"; position, verbosity, self-enhancement bias.
2. Wang et al., "Large Language Models are not Fair Evaluators," arXiv 2305.17926, 2023-05-29; order-swap manipulation; Vicuna-13B beat ChatGPT on 66 of 80 queries with ChatGPT as judge.
3. Panickssery, Bowman, Feng, "LLM Evaluators Recognize and Favor Their Own Generations," arXiv 2404.13076, 2024-04-15.
4. Shankar et al., "Who Validates the Validators?" arXiv 2404.12272, 2024-04-18; criteria drift.
5. Yao, Shinn, Razavi, Narasimhan, "tau-bench," arXiv 2406.12045, 2024-06-17; pass^k.
6. Gu et al., "A Survey on LLM-as-a-Judge," arXiv 2411.15594, 2024-11-23 (v6 2025-10-19).
7. Anthropic, "Demystifying evals for AI agents," 2026-01-09 (Grace, Hadfield, Olivares, De Jonghe), https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents.
8. Anthropic, "How we built our multi-agent research system," 2025-06-13.
9. Anthropic docs, "Define success criteria and build evaluations," https://platform.claude.com/docs/en/test-and-evaluate/develop-tests (ordering text read).
10. OpenAI, "Working with evals" (deprecated platform; historical only, not an anchor).
14. Miller, "Adding Error Bars to Evals," arXiv 2411.00640, 2024-11-01.
11. Husain, "Your AI Product Needs Evals," 2024-03-29, https://hamel.dev/blog/posts/evals/.
12. Yan, "Evaluating the Effectiveness of LLM-Evaluators," 2024-08-18, https://eugeneyan.com/writing/llm-evaluators/.
13. Inspect, https://inspect.aisi.org.uk/.

## Verify before quoting

- Anthropic docs pages move. Re-fetch.
- Judge agreement figures are model- and task-specific; cite the finding, never a number as current.
- Not opened, so not cited: G-Eval (2303.16634), Ragas (2309.15217), the Chatbot Arena paper, LangSmith/Braintrust docs. Add only after opening.

## Second-reviewer pass (Claude Opus; codex unavailable, usage limit)

Each finding checked against the opened primary source (Miller arXiv page, Demystifying, shipped 3.2, carrier bible); the rest taken from the reviewer's report, which opened them.

- M1 accepted: out-of-repo reference removed; alias line now says only that Gulli's books are unchecked.
- M2 accepted: item 6 now covers sample-size noise and repeated trials; Miller 2411.00640 verified (Evan Miller, 2024-11-01).
- M3 accepted: 3.2 verified to point here twice; added to Mention-and-link and a classifier sub-case in item 3; old item 3 merged into item 2.
- M4 accepted: "Who decides: your code" line added.
- M5 accepted: Contested bullet dropped; recast as sequencing in item 2.
- M6 accepted: OpenAI Evals no longer an anchor or lead; Inspect is the anchor.
- M7 accepted: item 9 re-led on the capability/regression quotes (verified in Demystifying).
- M8 accepted: per-criterion isolation cited to Demystifying, contrary multi-agent finding noted.
- m1 accepted: item 3 leads on develop-tests ordering.
- m2 accepted: gotcha now "unanchored scales".
- m3 accepted: "same model", develop-tests cited, "family" dropped.
- m4 accepted: ladder attributed to Husain; real-failures claim moved to Demystifying.
- m5 accepted-modified: one sentence in item 3 plus link to 3.7.
- m6 accepted: item 5 Established with caveat; stub parenthetical flagged.
- m7 accepted: grounding "research".
- m8 accepted: carrier cases use desk, bunk bed, phone case, corrected listings.
- m9 accepted: Gu et al. used as survey lead in item 4.
- m10 accepted: author-only questions section removed (belongs in the PR body).
- m11 accepted: sweep header states each angle once.
- m12 accepted-modified: reviewer's thesis adopted verbatim.

## Orchestrator rulings (Stage 1.6, 2026-11-27)

- **Thesis (binding):** "An eval score is evidence only to the extent that its cases came from real failures, its graders were checked against people, and its rate is read with its noise."
- **Spine:** must-cover 1 to 9 as ranked; 3.2's confidence-floor promise is honoured in item 3's classifier sub-case (where a threshold comes from: a labelled slice and a chosen operating point, not a guess). Budget ceiling ~2,800 prose words.
- **Who decides:** your code (harness owns cases, aggregation, gate); a model judge returns a per-case verdict and never controls flow. Contrast 3.4 in one sentence.
- **Maturity:** Established, argued as "the method is settled; judge reliability and agent evals are the moving parts." Last reviewed 2026-11.
- **Worked pattern (code):** an offline harness over a small Listing Studio golden set: a code grader for required attributes, a fake model judge calibrated against human labels (agreement and Cohen's kappa), repeated trials, a rate with an error bar, and a gate that refuses to call a small delta between two prompt versions a win. Provider tabs show the judge call only, compiled not run.
- **Carrier:** desk, bunk bed, phone case (the correct do-nothing case), listings a merchandiser corrected. No artifact outside the carrier bible.
- **Anchor:** Inspect is the reader-verifiable anchor; OpenAI hosted Evals is named only as deprecated, if at all.
- **Author-only defaults:** no coinage (named-idea candidates are plain descriptions, not claimed terms); no From-production callout; no edit to shipped chapters (3.2, 2.2, 3.3 already point here). The stub's "Grounding: production" becomes "research + companion repo" pending the author. Alias line needs author sign-off; ship the stub's aliases only.
