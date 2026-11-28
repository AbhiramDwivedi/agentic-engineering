# Coverage map: To Train or to Prompt (chapter 8.3)

> Research-derived spec for what the chapter must cover so a reader can decide, with evidence,
> whether a failing behavior is a prompt problem, a context problem, or a weights problem, and
> what the cheapest sufficient fix is. Sweep angles run: vendor docs, academic/benchmarks,
> security/failure modes, skeptical read, alias sweep, everyday-engineer, daily-tool, incidents
> (none found). Review and trim **Must-cover**; that sets the scope.

**Budget:** framing / concept chapter, about 1,200 to 2,000 prose words. **Litmus:** your code,
an offline engineering decision; tuning changes the worker's weights, not who owns runtime
control flow.

**Thesis (one sentence):** Fine-tune only after evals, prompting and retrieval have hit a ceiling
on consistency, latency or unit cost, and only if you can afford to redo the work whenever the
base model retires; do not fine-tune to teach a model facts.

## The mental model (what the reader must leave with)

Diagnose the failure first. Missing or stale knowledge is a context problem (retrieve it).
Inconsistent format, tone or task execution is a behavior problem (prompt first, then train).
Cost or latency at fixed quality is an efficiency problem (a smaller model, possibly a tuned
one). Training is the most expensive rung, needs an eval baseline to justify and measure it, and
ties you to a base model the vendor will retire. The ladder: eval, prompt, context and retrieval,
automated prompt optimization (one line, then 9.7), and only then weights. The behavior-versus-
knowledge split is OpenAI's framing ("Optimizing LLM accuracy"); credit it. It holds for
fine-tuning, not for continued pretraining (out of scope).

## Must-cover

Ranked. `[+]` = no existing text (stub only). Eight items.

1. **Diagnose the failure before choosing the lever** `[+]` - knowledge vs behavior vs efficiency
   gap, and which rung fixes which; the two levers are "additive, not exclusive" (OpenAI).
   *Skip it:* training to fix what context would have fixed, the catalog's "Fine-tuning as a
   flinch". **Established.** RAFT (Zhang et al., arXiv:2403.10131) belongs here as the
   combination case: tune the model to quote relevant passages and ignore distractors. **Emerging.**
2. **The baseline comes first: no eval, no tuning** `[+]` - a prompt-engineering eval set is the
   precondition and the only way to know it helped. **Standard.** (OpenAI model-optimization
   loop: evals, prompt, fine-tune, evals. Pointer to 4.2.)
3. **Fine-tuning does not reliably add knowledge** `[+]` - new facts are learned slowly and then
   raise hallucination; retrieval beat unsupervised fine-tuning for seen and new facts.
   **Established** (finding), one-study caveat each. (Gekhman et al., arXiv:2405.05904; Ovadia
   et al., arXiv:2312.05934.)
4. **What training is good for, and the methods** `[+]` - consistent format, tone and task
   execution; a smaller model at equal quality. One line each: SFT, DPO (Rafailov et al.,
   arXiv:2305.18290), RFT (a grader scores outputs), and RLVR, where a programmatic verifier
   supplies the reward (Lambert et al., Tulu 3, arXiv:2411.15124, which names RLVR; DeepSeek-R1,
   arXiv:2501.12948, applies RL to verifiable tasks). RLVR is the route for agentic skills such as
   tool calling where a checker exists; 2.1 and 2.3 delegate it here. PEFT in two sentences: LoRA
   (Hu et al., arXiv:2106.09685) and QLoRA (Dettmers et al., arXiv:2305.14314) cut cost and forget
   less, but whether they match full fine-tuning is **Contested** (Biderman et al.,
   arXiv:2405.09673; Schulman and Thinking Machines, "LoRA Without Regret", 2025-09-29). LIMA
   (arXiv:2305.11206) shows how little data style needs. **Established** (SFT); **Emerging**
   (RFT, RLVR, grader design).
5. **Prompting has more room than folklore says: context economy** `[+]` - baking long
   instructions and examples into weights frees the window and avoids paying for those tokens on
   every call, but prompt caching and many-shot in-context learning push break-even back toward
   prompting. Many-shot ICL (Agarwal et al., arXiv:2404.11018, NeurIPS 2024) performs comparably
   to fine-tuning on some tasks, at linear inference cost per example. Mosbach et al.
   (arXiv:2305.16938, Findings of ACL 2023) found fine-tuning generalizes about as well as
   few-shot ICL at matched scale, with large variance; use it for that, not for long context.
   Automated prompt optimization is one rung here (DSPy, arXiv:2310.03714); mechanics in 9.7.
   **Contested** (parity claims); the rung is **Standard** for manual eval-driven prompting,
   **Emerging** for optimizers (DSPy and GEPA, arXiv:2507.19457, come from one lab; no independent
   production evidence read).
6. **Small tuned model versus frontier model, and distillation** `[+]` - a tuned small model can
   match a frontier model on a narrow task; claims are task-, date- and vendor-dependent. LoRA Land
   (arXiv:2405.00732) compared 310 LoRA models to base models and GPT-4, by a vendor with a stake
   and a 2024 baseline; Li et al. (arXiv:2305.05862) is the skeptical counterweight (a general
   model against domain-tuned BloombergGPT). Distillation needs curated teacher data, and vendor
   terms may restrict using teacher outputs to train competing models. **Contested.**
7. **Training can break what you did not test** `[+]` - benign fine-tuning degrades safety
   alignment (Qi et al., arXiv:2310.03693; **Established**); narrow fine-tuning can produce broad
   misalignment (Betley et al., arXiv:2502.17424; **Emerging**, one recent paper). Pointer to 4.4.
8. **The total cost of owning a tuned model** `[+]` - data curation, eval upkeep, retraining on
   every base-model change, and retirement. Bedrock's lifecycle page: once a model enters Legacy,
   no new fine-tuning jobs, existing customizations continue until EOL, and migration is not
   automatic. OpenAI's model-optimization page says it is winding down its fine-tuning platform,
   closed to new users. The lifecycle principle is **Standard**; the vendor retreat is volatile.

## Mention-and-link

- Model selection and open-weight versus hosted choice → 8.2.
- Cost levers, caching, cascades (FrugalGPT, arXiv:2305.05176: cascades cut spend sharply at
  matched quality, per the authors; do not freeze the figure) → 8.4 and 3.2.
- Context engineering → 1.5; tool use → 2.1; skills → 2.3; retrieval → 5.2; memory → 5.1, 5.3.
- Prompt versioning → 4.1; evaluation design → 4.2; safety eval after tuning → 4.4;
  self-improving loops and DSPy/GEPA mechanics → 9.7; structured output for format → 2.2.

## Out of scope

- Training infrastructure, hyperparameters, LoRA layer and rank choices, RLHF pipelines (cite,
  do not teach). Pretraining and continued pretraining. GPU and multi-LoRA serving.
- Vendor API minutiae: job-creation calls, per-model availability. Link to the docs.

## Maturity summary

- **Standard:** eval before change; prompt first; lifecycle cost of a tuned model.
- **Established:** diagnose knowledge vs behavior; SFT for format, tone, efficiency; fine-tuning
  does not reliably add knowledge; safety regression after tuning.
- **Emerging:** RFT and RLVR; automated prompt optimizers; RAFT; emergent misalignment.
- **Contested:** LoRA parity with full fine-tuning; "tuned small model beats frontier"; tuning
  versus many-shot prompting parity.

Chapter verdict: **Established** for the decision ladder; the hosted-product facts, RFT and
optimizers are Emerging or volatile, so carry a Last reviewed line.

## Aliases (*Also called:*)

"Prompt, RAG, fine-tune" ladder (OpenAI); model optimization (OpenAI); RAG vs. fine-tuning;
post-training; model adaptation; customization (Bedrock); "Learning and Adaptation" is Gulli's
2025 chapter title, to be checked against that book before use. Alias wording needs author
sign-off.

## Reader-verifiable anchors

- OpenAI's model-optimization page shows the evals, prompt, fine-tune loop and the wind-down
  notice: https://developers.openai.com/api/docs/guides/model-optimization
- Bedrock model lifecycle page: https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html
- Daily-tool anchor: Claude Code's CLAUDE.md and skills, and Cursor rules, adapt a frozen model
  through context alone; a reader can see behavior changed with no weight update. (Confirm
  against current docs when drafting.)

## Incidents

None found as postmortems. Closest evidence is research on failure (arXiv:2310.03693, 2502.17424).

## Named-idea candidates

- **The ladder** (eval, prompt, context, optimize, train); standard idea, no coinage.
- **Behavior, not knowledge** as the one-line test, credited to OpenAI's framing.
- **Fine-tuning as a flinch**: the site's existing anti-pattern for this chapter; link, do not coin.

## Carrier

Listing Studio. Anchor: step 3 *categorize* (taxonomy placement) and step 8 *brand-voice polish*
(consistent labels and voice, high volume, cheap model wanted). Counter-case: stale compliance
rules and supplier facts are knowledge, so retrieval. The Merchant helpdesk or Category scout is
reached for only if a second case is needed. Numbers must come from measured runs, otherwise stay
qualitative.

## Code seam

NONE recommended: a framing chapter, so it ships without companion code. If the author wants one artifact: an
offline comparison harness (baseline prompt vs few-shot vs stub "tuned" model) over either the
`listing-studio/routing` Merchant helpdesk intake classifier or a new step 3 categorize fixture
(`structured_output` holds the pricing decision, not categorize); it needs 4.2's eval harness
first. Do not fabricate a training run.

## Sources

Vendor: OpenAI "Optimizing LLM accuracy", model-optimization and reinforcement fine-tuning guides;
AWS Bedrock model lifecycle page (opened). Research: Gekhman arXiv:2405.05904; Ovadia
arXiv:2312.05934; Biderman arXiv:2405.09673; Qi arXiv:2310.03693 (ICLR 2024); Betley
arXiv:2502.17424; Agrawal (GEPA) arXiv:2507.19457; Khattab (DSPy) arXiv:2310.03714; Zhou (LIMA)
arXiv:2305.11206; Mosbach arXiv:2305.16938; Agarwal arXiv:2404.11018; Zhao (LoRA Land)
arXiv:2405.00732; Zhang (RAFT) arXiv:2403.10131; Chen, Zaharia, Zou (FrugalGPT) arXiv:2305.05176;
Hu (LoRA) arXiv:2106.09685; Dettmers (QLoRA) arXiv:2305.14314; Rafailov (DPO) arXiv:2305.18290;
Lambert (Tulu 3) arXiv:2411.15124 (2024-11-22); DeepSeek-AI arXiv:2501.12948 (2025-01-22);
Li arXiv:2305.05862; Schulman and Thinking Machines, thinkingmachines.ai/blog/lora (2025-09-29).

> **Verify before quoting:** OpenAI cutoff dates (the page gives none; see its deprecations page).
> Anthropic's fine-tuning wording and any Claude 3 Haiku EOL date (open the Bedrock model card).
> Vendor terms on distillation and model collapse (Shumailov et al., Nature 2024) were not opened.
> Vertex AI Gemini tuning status unchecked. LoRA Land and GEPA margins are authors' reports.

## Open questions for the author

1. Ship a comparison harness, or keep the chapter code-free?
2. Resolved: evidence-only, no From-production callout (see Stage 1.6 ruling 6).
3. Aliases and the "Fine-tuning as a flinch" link: approve wording.
4. How hard to lean on the wind-down of hosted fine-tuning, given it is volatile?

## Map review (Stage 1.5)

1. Missing thesis, budget, litmus, Open questions - accepted-modified: added all four, thesis reworded; Who-decides stub line left (map-only edit).
2. Mosbach misused for long context - accepted: finding restated, Agarwal (verified) added.
3. OpenAI/Bedrock availability - accepted-modified: OpenAI page opened, no dates, so the reviewer's dates not adopted; Bedrock lifecycle page replaces the unopened notice; Vertex left as unverified.
4. Gaps: context economy, RLVR, distillation - accepted: added; Shumailov and vendor ToS unopened, so flagged, not cited.
5. 9.7 seam and bloat - accepted: ten items cut to eight, DSPy/GEPA one line, LoRA two sentences, RAFT merged.
6. LoRA Land misplaced - accepted: moved to item 6; LoRA, QLoRA, DPO papers opened and cited (venues not confirmed on arXiv pages, so omitted).
7. Maturity contradictions - accepted: Item 1 aligned, optimizers Emerging, item 7 split, retreat marked volatile; split chapter verdict taken.
8. Carrier misnaming and seam errors - accepted: Merchant helpdesk or Category scout; code seam corrected.
9. Anchors, aliases - accepted-modified: "Flavor 1", DSPy/GEPA aliases dropped, new aliases added; Gulli chapter title flagged unchecked.
10. FrugalGPT figure, links, 8.7 route - accepted: figure removed, links added, routed to 8.2.
11. Orphan source, truncated URLs - accepted-modified: Li wired into item 6, URLs completed; most venues omitted as unverified.
12. Attribution and flinch - accepted: OpenAI credited, flinch listed; "Flavor 1" struck.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Code:** none. A framing and decision chapter, so it ships without a companion package. It still carries the one explanatory diagram (the decision ladder).
2. **Verdict:** Established for the decision ladder, with Emerging (RFT, RLVR, prompt optimizers) and Contested (LoRA parity, "small tuned beats frontier") argued in the prose. Carry a "Last reviewed: 2026-11" line.
3. **Hosted fine-tuning wind-down:** mention it once, hedged, and only where a source opened in the map supports it. Drop any vendor cutoff date the map marks unverified.
4. **Named idea:** "Fine-tuning as a flinch" is not used as a coinage. Plain description only. It goes on the author checklist.
5. **Aliases:** keep any existing stub alias line unchanged. Add none.
6. **No From-production callout.**

## Reconcile log (Stage 5)

Prose critic:
1. Retirement assumes closed models (L32/77) - fixed: scoped to hosted tuning; open weights trade retirement for hosting and an ageing base.
2. Prompt portability understated - fixed: "a re-run of the eval and, often, some rework of the prompt."
3. "Three neighbours" lists four - fixed: "Four"; RAFT appositive split into two sentences.
4. Format contradiction (L19/36/58) - fixed: training is for "a format no schema can express"; structured output stays first.
5. Ladder restated five times - fixed: L15 parenthetical, "Climb in order" line and the When-the-weights opener cut; list kept once in the definition.
6. Label recital - fixed: Contested list cut from the maturity paragraph; in-section labels replaced with plain words; lens line kept (required).
7. Established rests on thin studies - fixed: verdict rests on documented practice; studies back the knowledge half only.
8. Body bookkeeping (L75) - fixed: Betley caveat cut; L69 vendor caveat kept as argument.
9. LIMA overclaim - fixed: "than teams expect" dropped, "shifted a large model's response style."
10. RLVR "the route" - fixed: "one option", with the weak-check failure named.
11. LoRA paragraph has no recommendation - fixed: start with LoRA, move to full fine-tuning on a plateau.
12. "Just as real" and BloombergGPT mislabel - fixed: "Domain training does not always win either"; BloombergGPT described as pretrained on finance.
13. "No eval, no tuning" fragment - fixed: cut.
14. "Climb in order" beat - fixed: cut.
15. Carrier muddle and weight rating - fixed: compliance review named as the third case; weight rating replaced with a BIFMA claim.
16. Alt-text shape narration - fixed in the alt text; the SVG's own caption line is unchanged (diagram not re-cut at this stage).
17. Weak way in - fixed: opens on a generic stale-rule failure (pricing rules); the carrier stays later.

Fact-checker:
18. LoRA Land "many" - fixed: "beat GPT-4 by about 10 points on average" across 31 tasks; Predibase affiliation confirmed from the paper's front matter, vendor caveat kept.
19. Li et al. mixed - fixed: "several" kept; footnote notes wins and losses (NER).
20. CLAUDE.md/Cursor uncited - fixed: footnotes to the Claude Code memory docs and Cursor Rules, both opened.
21. RFT URL is the API reference - fixed: both URL forms confirmed to resolve to the reference; footnote relabelled.
22. GEPA "one research group" - softened: "share many of their authors"; unverifiable production-evidence claim removed.
23. AWS scope - fixed: launched on or after 2026-09-07; "deployments created before then" replaces "customizations".
24. DSPy undefined - fixed: glossed. Distillation uncited - softened to "one common way". Qi venue - kept (ICLR 2024).

Cold reader:
25. Weights, context window, eval (now in the lede), prompt optimizer, prompt caching, grader, maturity labels (gloss plus link), Prop 65, frozen model, cascades - fixed: glossed at first use.
26. Low-rank adapters and verifier-based training used before definition - fixed: both mentions removed from the maturity paragraph; LoRA defined at first use.
27. Sibling-category choice as behavior unargued - fixed: one clause added.
28. "Smaller model untuned first" unargued - fixed: argued in the small-model section.
29. Optimizer vs retrieval cost unordered - softened: retrieval is its own branch; the order is "roughly by cost" and a default.
30. Build test (eval size, data format) - rejected: eval mechanics belong to 4.2, which is linked; budget.
31. Alt text carries the explanation - rejected: the alt text describes the picture for screen readers; shape-convention sentence cut.

Second engine (draft review):
32. Ladder contradicts the accuracy guide - fixed: guide opened and confirmed; the diagnosis picks the lever and the order is a default, cited to the guide.
33. Training-data contract - fixed: one sentence on keeping training and scoring examples separate.
34. Knowledge prohibition - softened: "as a default"; RAFT kept as the combined case.
35. Retirement intrinsic to tuning - fixed with 1; shared upkeep stated.
36. RLVR oversold - fixed with 10.
37. Litmus line assigns runtime control to code - fixed: the decision to tune does not change who makes runtime decisions.
38. No break-even test - rejected beyond the existing cost bullets and the 8.4 link: budget.
39. Attention cost omitted - fixed: one sentence, send only the relevant examples.
40. GEPA authorship, Betley count - fixed with 22 and 8; the clash with the 9.7 stub's verdict on optimizers goes to the author.
41. Generalizations exceed citations - fixed: LIMA, forgetting (scoped to the study), LoRA large-data boundary (post opened), BloombergGPT regime.
42. Daily-tool anchor uncited - fixed with 20.
43. Distillation uncited - softened with 24.
44. Aliases unresolved - left for the author; no alias line added.
45. Carrier conflates supplier facts with rules - fixed with 15.
