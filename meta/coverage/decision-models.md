# Coverage map: Decision Models (chapter 2.7, NEW, no stub)

> Research-derived spec. Review and trim **Must-cover**; that sets scope. Budget: standard pattern,
> about 2,000 to 2,800 words of prose. Every cited page was opened unless marked UNVERIFIED.
> Nothing here is a first-hand claim.

**Thesis.** A decision model swaps text generation for one pass that returns a probability
distribution over options your code defined, and that pays off only when your code owns the
thresholds, checks calibration on your own labeled data, and refuses a fallback that returns a
number with no distribution behind it.

## The mental model

A decision model is a model call that generates no text. It returns P(true) for a statement, a
distribution over fixed options, or a distribution over rungs of an ordered rubric. The model
produces the distribution per request; thresholds, abstain, escalate and combination rules live in
code. Litmus: **a capability, not a pattern** (hexagon, Part II sibling of 2.2). Which control-flow
class a use falls in depends on the caller: a threshold inside a router is 3.2's call, a gate in the
harness is 2.6's. Do not sell it as new: it is a classifier with probability outputs behind a new
API. Constructive answer on the same page: use the distribution, own the threshold.

## Must-cover (ranked, 8)

1. **The three question shapes and shared-prefill batching**: predicate (P(true)), choice
   (distribution over options), score (distribution over ordered levels). Option bounds are per
   vendor: OpenAI score takes 2 to 10 levels, Google choice takes 2 to 255 options (its post states
   no score maximum). Spellings differ: predicate (OpenAI) / `noul` (TypeSafe, Perplexity, Google) /
   `boolean` (Vercel AI SDK). Several questions share one input in one request (OpenAI 1 to 400,
   Google up to 1,000). Vendors add further shapes; out of scope. Skip it: readers hear "classify
   with an LLM" and miss that the output is a distribution. **n/a** (definition).
2. **One judgment per question, batched in one call, combined in code**: TypeSafe's docs say a
   question weighing several independent factors should be decomposed and recombined in code.
   Skip it: compound questions bring back the entangled judgment. **Emerging.** (TypeSafe docs;
   OpenAI reference.)
3. **Thresholds, abstain and escalate live in code**: Microsoft's card says the integrating
   application must define options, thresholds, escalation paths and human oversight. Tuning a
   binary threshold took micro-F1 on UNFAIR-ToS from 0.50 to 0.75 (arXiv:2609.37647). Cost
   cascade: Vercel Gateway reruns a decision on another model when confidence or a probability band
   matches; both stages bill and a language-model fallback returns no confidence. A decision-model-
   to-LLM cascade gained at most 2.7 points over the best single judge even with oracle thresholds,
   so the win is cost (arXiv:2609.29769). Skip it: the 0.5 default ships, or escalation is assumed
   to buy accuracy. **Standard** (thresholds and abstain), **Emerging** (cost cascades),
   **Contested** (cascades for accuracy). Cascade mechanics belong to 8.4.
4. **Probabilities, confidence and calibration**: Perplexity defines choice confidence as
   `(p_top - 1/n) / (1 - 1/n)`, concentration and not correctness; Vercel says a boolean 0.98 "is
   not confidence in either outcome." Microsoft claims calibrated probability with no metrics.
   Independent: among answers at 0.90 or higher, error ran 1.71% to 12.77% across 13 decision models
   on 1,273 MedQA questions (arXiv:2610.38448); over 85% of flash-tier LLM verdicts repeat a decision
   model's most confident errors (arXiv:2609.29769). Method: post-hoc temperature scaling (Guo et
   al., arXiv:1706.04599); P(True) can be well calibrated in the right format (Kadavath et al.,
   arXiv:2207.05221). Skip it: "0.9" is read as 90%. **Established** (the method), **Contested**
   (vendor out-of-the-box calibration).
5. **The adapter trap**: the Vercel AI SDK page labels Anthropic the structured language-model
   adapter: booleans are "prompted estimates of P(true)", choice and score omit distributions, and
   "the SDK does not promise calibration across providers." Native: TypeSafe, OpenAI, Perplexity,
   Google (per that page). The TypeSafe gateway fallback sentinel is `confidence: 0` and
   `probabilities: {}`, documented as "unavailable". Code that thresholds on `confidence` must
   handle absence, and a per-question refusal (OpenAI) or timeout needs a typed return, not an
   exception. Skip it: a swapped provider silently changes what the number means. **Emerging.**
6. **Reliability limits, single decisions and closed loops**: System1-Arena (arXiv:2610.21244;
   92k questions, 105 tasks, 138 closed-loop environments, 30 models): largest System-1 models match
   fast closed LLMs on non-agentic tasks with better calibration at about a quarter of the latency;
   in closed loops large open LLMs succeed most (up to 32.9%) and small System-1 models rarely
   succeed. The abstract does not report large System-1 closed-loop scores; check the table before
   drafting. Jev (arXiv:2609.37647): 90% optimal Blackjack action, weak on FrozenLake. Say "single
   decisions, not trajectories". Inside single decisions: low-resource languages, noisy labels and
   rubric judgments degrade; three-run agreement ran 92.30% to 100% (arXiv:2610.38448); no knowledge
   absent from the input. **Contested** (closed loops), **Emerging** (the rest).
7. **Prompt injection and decision hijacking**: removing text generation does not remove injection.
   Wu and Lim (arXiv:2609.28613, 2026-09-23), 510 reconstructed InjecAgent cases against Jev:
   malicious content shifts action probabilities but rarely makes it pick the attacker's target;
   adaptive score-feedback attacks doubled the mean highest attacker-target probability, and
   validated success rose from 1.8% to 3.5%. Where untrusted input drives a routing or compliance
   gate, a probability is attack surface. Depth to 4.6 and 4.4. **Emerging.**
8. **Decision models versus the alternatives**: Rao and Callison-Burch (arXiv:2609.29769): LLM
   judges cost 16 to 357 times as much and take 5 to 350 times as long, and decision models trail
   them significantly in at most 6 of 27 comparisons. Freyer et al. (arXiv:2610.38448): decision
   models 67.71% to 89.08% on MedQA, generative configurations 78.32% to 96.86%, so lower peak
   accuracy. Use decision models for high-volume, fixed-option judgments over one shared input;
   use generation (2.2) for reasoning-heavy ones. Comparison to fine-tuned encoders and first-token
   `logprobs` has no primary source yet: UNVERIFIED, researcher to find one or leave it out.
   **Emerging.**

## Mention-and-link

- Schema-constrained generation → 2.2 Structured Output. Dispatch that consumes a choice, and LLM
  routing proper → 3.2. Harness gates and permission policy → 2.6; escalation to humans → 4.3.
- Judge methodology → 4.2 (a decision model can act as a judge, a Microsoft preview feature).
  Safety classifiers → 4.4; injection depth → 4.6. Outer-loop verifier → 3.7. Model choice → 8.2;
  cost cascades → 8.4. The agent loop this does not suit → 2.5.
- Context economy: a decision call carries the whole state in tokens every call. Microsoft's
  context limit is 32,768 tokens and Google's 256K; OpenAI documents a string `maxLength` of
  10,485,760 with no unit, so do not compare them. Depth → 1.5 Context Engineering.

## Out of scope

Training a classifier (8.3); a calibration library; vendor pricing and leaderboards (rot); medical
or legal deployment guidance beyond the vendor's own caution.

## Maturity summary

- **Standard:** code-side thresholds and abstain rules. **Established:** post-hoc calibration.
- **Emerging (chapter verdict):** the product category, about two months old at review; speed and
  calibration claims mostly vendor-reported. Carry "Last reviewed: 2026-11".
- **Contested:** vendor calibration out of the box; "System 1 replaces LLM judges"; closed loops.

## Aliases (source for each)

Decision models (Perplexity blog; Vercel AI Gateway docs, previously "evaluation models"); decision
models and "Decider" (arXiv:2609.29769); Decisions API (OpenAI, Perplexity, Google); System One model
(TypeSafe; Microsoft's route is `.../systemone`); decision-scoring model (Microsoft card); "System 1
models" (arXiv:2610.21244). No catalog home found in either Gulli book or the pre-2026 agentic guides
checked.

## Reader-verifiable anchors

- Google AI Studio offers a no-cost API tier for `gemini-decision-1`; a reader can send a predicate
  and a choice and read the distribution.
- Perplexity ships Apache-2.0 open weights (`pplx-decider-flash-v1.3`, 4B), but the card says the
  repository needs a Hugging Face token: a weaker anchor, say so.

## Incidents

None found for decision models. Injection research is item 7.

## Named-idea candidate (author accepts or strikes)

**Number without a distribution** (the adapter trap).

## Carrier mapping (Listing Studio)

Atomic predicates over canonical `compliance` fields: `prop65`, a `safety_claims` entry, and
`weight_capacity_lbs` overstated, on the Aldsworth desk (`NV-ALDSWORTH-DM`) and the phone case
(`NV-PHONECASE-01`), combined in code (item 2). `choice` over `category_path` as an explicit
contrast with 2.2 at step 3. `score` anchored to step 8, a brand-voice rubric.

## Code seam

New offline package `listing-studio/decision_models/`, tests in
`listing-studio/tests/test_decision_models.py`. A `FakeDecisionClient` returns distributions for the
three shapes, a refusal and a no-distribution (adapter) answer. Thresholds, abstain and escalate are
plain functions, and a calibration check (reliability bins, ECE, best threshold) runs on a small
labeled fixture. No SDK, no network; it builds and runs offline.

## Open questions for the author

1. Add 2.7 to `mkdocs.yml` and `docs/the-unit/index.md` (with `(planned)` until merge)?
2. Litmus placement as "a capability, not a pattern": confirm.
3. No Anthropic-native endpoint exists, so the three-provider tab rule cannot hold: omit provider
   tabs, or show one native vendor plus the adapter?
4. Carrier overlap with 2.2 at step 3: keep the contrast framing?
5. Encoder and `logprobs` comparison: keep without a primary source, or cut item 8's last clause?

## Sources (opened)

OpenAI Decisions create reference (`POST /v1/decisions`) developers.openai.com/api/reference/
resources/decisions/methods/create · Google blog "Gemini Decisions API" (2026-11-11) blog.google/
innovation-and-ai/technology/developers-tools/gemini-decisions-api/ · Microsoft Foundry card
ai.azure.com/catalog/models/Microsoft-Decision-1 · Microsoft Tech Community "Introducing
Microsoft-Decision-1" (2026-10-09) · TypeSafe docs docs.typesafe.ai · Perplexity API reference
docs.perplexity.ai/api-reference/decisions-post · Perplexity blog perplexity.ai/hub/blog/
perplexity-decider (2026-11-12) · Hugging Face perplexity-ai/pplx-decider-flash-v1.3 · Vercel AI SDK
ai-sdk.dev/docs/ai-sdk-core/decisions · Vercel AI Gateway Decision Fallbacks docs. arXiv:2610.21244
"System1-Arena: Which Decisions Can Be Left to System 1?" (Chen et al., 2026-10-15) · arXiv:2609.37647
"Evaluating and Benchmarking the System One Model Jev" (Deußer et al., 2026-09-29) · arXiv:2609.29769
"Decision Models vs. LLMs as Rubric Judges: Cheaper, Faster, and Wrong in the Same Places" (Rao,
Callison-Burch) · arXiv:2610.38448 "Benchmarking decision models against generative large language
models on medical multiple-choice questions" (Freyer et al., 2026-10-28) · arXiv:2609.28613 "Decision
Hijacking: Prompt Injection Attacks on Jev's Typed Probabilistic Decisions" (Wu, Lim, 2026-09-23) ·
arXiv:1706.04599 (Guo et al., ICML 2017) · arXiv:2207.05221 (Kadavath et al., 2022).

> **Verify before quoting:** model names, versions and prices rot; Vercel renames are in progress;
> cite the finding and the live page, not a snapshot number.

## Map review (Stage 1.5)

1. Missing thesis, budget, open questions: accepted-modified, added; thesis reworded.
2. Prompt injection omitted: accepted, arXiv:2609.28613 opened and matches; OWASP IDs not re-opened, so not cited.
3. Working notes in a public map: accepted, verification notes deleted, Gulli line made neutral.
4. Fifth litmus label: accepted-modified, now "a capability, not a pattern" matching 2.2; caller decides class.
5. Missing comparison to alternatives: accepted-modified, LLM comparison cited (2609.29769, 2610.38448); encoder and logprobs parts have no opened source.
6. Google omitted, vendor limits universal: accepted-modified, Google blog opened; limits labeled per vendor; Google states no score maximum so none claimed; `locate`/`box` not verified, left unnamed.
7. Must-cover bloat and seams: accepted, consolidated to 8; 2.6 and 8.2 added; `5.1/2.2` fixed to 1.5.
8. Maturity verdicts: accepted-modified, cost cascades Emerging, accuracy cascades and vendor calibration Contested, thresholds Standard, definitions n/a.
9. Anchors: accepted-modified, Google free tier added (verified); Flash v1.3 exists but its card is token-gated, noted as weak.
10. Carrier mapping: accepted, canonical compliance fields and steps 3 and 8 confirmed in carrier-bible.
11. Context limits, REST path: accepted-modified, path is `/v1/decisions`, OpenAI's limit unit is unstated on the page; `gpt-6-luna` window and `experimental_decide` not verified, omitted.
12. Item 2 heading: accepted, retitled.
13. Paper titles, closed-loop baseline: accepted-modified, exact titles used; abstract confirms only small System-1 "rarely succeed", large System-1 scores flagged for a table check.
14. Aliases and named idea: accepted-modified, Decider and Google added; `Narrow Decision Models` (2610.25553) unopened so skipped; "The judgment line" struck.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **New chapter.** 2.7 is new. The writer creates `docs/the-unit/decision-models.md`. At Stage 5, reconcile adds the nav entry after 2.6 in the-unit section and adds the section index line. The title "Decision Models" goes on the author checklist.
2. **Litmus.** "A capability, not a pattern," placed as in 2.2. Maturity is Emerging with a Last reviewed line of 2026-11, and the sub-verdicts are argued in prose. (Author checklist.)
3. **Provider tabs.** Omit them. The vendor surfaces are new and uneven, and no tab may depend on an identifier the fact-checker cannot open. Name the vendors in prose with cited links only.
4. **Contrast with 2.2.** Keep it at step 3, in plain text or as a link, since 2.2 is on main.
5. **Encoder and logprobs comparison.** Cut it, because it has no primary source.
6. **Code.** Approve `listing-studio/decision_models/`. It contains a FakeDecisionClient, the three question shapes, refusal, the no-distribution adapter fallback, threshold, abstain and escalate functions, and a calibration check on a small fixture. Tests use stdlib and pydantic only.
7. **Unverified items.** The items the fold left out stay out.
8. **Excluded.** No From-production callout and no coinage. Do not edit shipped chapters; in particular, no back-links are added to 2.2. (Author checklist.)

## Reconcile log (Stage 5)

Prose review:

1. Hook vs calibration (0.98 as "98% sure"): fixed. The hook says only labeled data can tell; Evaluating it says when 0.98 earns that reading.
2. Rubric results contradict: fixed. The "low-resource languages, noisy labels, rubric judgments" list was cut (its cited source is MedQA-only); the Rao count is glossed as head-to-head comparisons.
3. "Primary listing": fixed, now "The function below is the policy".
4. "Escalating" vs `escalate`: fixed, Gotcha 2 says "Cascading".
5. Restatement in the definition and classifier paragraphs: fixed, both trimmed.
6. Walkthrough repeats the diagram: fixed. The 0.55 case stays only in the diagram; step 2's test detail is cut.
7. Alt text narrates the hexagon: fixed; alt text and SVG description shortened to the picture.
8. Maturity paragraph bookkeeping: fixed. The source-date sentence is gone; the last sentence points to Gotchas 2 and 3.
9. Vendor-limit list and the "further shapes" sentence: fixed; option counts dropped, sentence cut.
10. Colon-zinger before the Jev figure: fixed.
11. Zero-error threshold with no caveat: fixed. It is now a starting floor, picked on one labeled set and confirmed on another.
12. Performed opener: fixed, cut; the compound-question sentence says two clean factors can outweigh one bad one.
13. "The 0.5 default": fixed, glossed as what taking the likelier answer amounts to.
14. "Rarely ask one question": fixed, "A real gate usually weighs several factors".
15. Token note duplicated in the body: fixed, left to the footnote.
16. Paragraph restating the code comments: fixed; its tail cut and the THRESHOLD sentence moved above the code.
17. Gotcha 3 sprawl and the orphaned "knows nothing" sentence: fixed. The universal claim was cut; Gotcha 5 now advises putting the evidence and policy in the input (the Microsoft-card attribution was not re-opened, so not cited). System1-Arena's scale figures (92,000 questions, 105 tasks) were cut for budget, as was Gotcha 5's OpenAI unit-less length-limit sentence.
18. Compliance gate not placed in the pipeline: fixed. It sits in the publish step's validation (step 9); step 8 reads "a score could grade". The carrier bible is unchanged.
19. Alias line: not changed; on the author checklist.

Fact check:

1. Vercel 0.98 gloss: fixed with the suggested wording.
2. Gateway footnote URL missing: fixed.
3. Sentinel attribution: fixed; now the Vercel AI Gateway's TypeSafe-compatible API, cited to Decision Fallbacks.
4. Prop 65 predicate polarity: fixed in test, prose and SVG label ("Is a required Prop 65 warning missing from the listing?"); pytest passes.
5. 0.98 vs 0.97: fixed by moving the trace, test and diagram to 0.98/0.02, which keeps the hook and closing line on the Vercel figure.
6. "4B model": fixed, "built on a 4B base model".
7. "Publishes" open weights: softened to "lists".
8. Microsoft card: softened to "its card text publishes no calibration metrics".
9. Jev undefined: fixed, glossed as TypeSafe's System One decision model; the result is marked author-reported.

Cold read:

1. Glosses added: adapter, `noul`, the companion code (linked), UNFAIR-ToS, micro-F1, InjecAgent, MedQA, closed-loop environments, System-1 models, temperature scaling.
2. The 0.5 default and the all-correct threshold carry their missing steps; Kadavath is scoped to generative models.
3. THRESHOLD used before defined: fixed, defined above the decide block.
4. Terminology drift: the chapter now says the listed names mean the same thing. No real-client request added (Stage 1.6 ruling 3).
5. Rejected: the dual-process gloss for "System One" (TypeSafe's naming rationale not sourced); import lines and `dataclass` in the listings (the snippets mirror the companion regions byte for byte); un-hiding `calibrate` from its details block (it is supporting code, and the prose now states what it computes); a separate "reliability bins" gloss (the binning is described in the prose); the lethal-trifecta gloss (it is the linked chapter's title, explained there).
6. The 27-comparison count is glossed only as head-to-head comparisons; what the 27 pair was not re-opened.

Second-engine draft review:

1. Gate passes with missing answers: fixed in code. An empty question set or an answer-count mismatch escalates; new test.
2. Zero-error threshold fits noise: fixed in prose (prose item 11); calibration and threshold selection kept separate.
3. ECE described as confidence vs accuracy while the code bins P(true) against true-frequency: fixed; the prose describes what the code computes (0.158 unchanged).
4. No "none of these" outcome for choice: fixed with one sentence, no new citation.
5. "Decides nothing structural" overreach: fixed. Whether the answer is structural depends on what the option controls; "capability" stays.
6. Trajectory claim too categorical: softened; generation stays the default unless your own trajectory evaluation says otherwise. Table figures not re-opened, so not added.
7. Score drops rubric ordering: softened. The prose says the companion acts on the most likely level and a weighted average is the alternative; code not redesigned.
8. "Input is read once": softened; processing and billing vary by provider.
9. "Knows nothing not in the input": fixed, the universal claim cut (prose item 17).
10. No timeout or invalid-response state: partly fixed. `decide` escalates an empty or malformed distribution, with tests; the timeout wrapper is named as left to the reader; no timeout type added.
11. Predicate polarity and refusal precedence: fixed; a confident violation blocks before a refusal escalates. The 0.48/0.46 split removed (no fixture).
12. Citation trail: Vercel URL and sentinel fixed. Google title change rejected: the short title is not wrong and the longer one was not re-opened.
13. Nav and section index: fixed.
14. Opening thesis and context cost: fixed. The hook states the labeled-data condition; Gotcha 5 adds "send only the fields the question needs".
15. Review residue and access prerequisites: fixed. Stage 1.5 wording made neutral; the Google tier marked "for prototyping". The SDK early-access note was not re-opened, so not added.
