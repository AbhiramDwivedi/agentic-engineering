# 8.3 To Train or to Prompt

*Fine-tuning changes how a model behaves far more reliably than what it knows. Diagnose the failure first, fix missing knowledge with context, and reach for the weights only after an eval (a fixed set of real inputs with a scorer) shows the prompt and the context have run out on consistency, latency or unit cost.*

## Why you'd reach for it

A team fine-tunes its pricing rules into a model so there is no prompt to maintain. The next quarter the rules change, and the model keeps applying the old ones with the confidence it had when they were true. Fine-tuning feels like the serious fix when a model keeps getting your business wrong: you continue its training on your own examples, and the change lands in its weights, the learned parameters that hold what it knows and how it behaves. For facts, the evidence says it is a poor lever. In one controlled study, models picked up new facts from fine-tuning slowly, and as they did, they became more prone to hallucinate.[^3] In another, retrieval beat unsupervised fine-tuning (training on raw text, with no question-and-answer pairs) at getting knowledge into the answers, both for facts the model had seen in pretraining and for facts it had not.[^4]

Training is still the right tool for a different class of failure, and the expensive part of the decision is telling the classes apart. A model that misses a fact needs the fact in its context window, the text sent with each call. A model that knows what to do and does it inconsistently (the wrong format on the occasional call, a tone that drifts across a batch, a label that wobbles between two near-identical categories) has a behavior problem, and behavior is what training changes well. The third failure has nothing wrong with the output: quality is fine and the bill or the latency is not. OpenAI's accuracy guide frames the first split as knowledge against behavior, and treats retrieval and fine-tuning as additive levers you can combine.[^1]

Getting the diagnosis wrong costs more than wasted compute. Tune a fact into the weights and it goes stale on the day the fact changes, and the tuned model answers with the same confidence it had when the fact was true. Tune a hosted model and you have also tied the fix to a base model that its vendor will eventually retire. The [Anti-Patterns Catalog](../catalogs/anti-patterns.md) records the general habit: training a model to fix what a better prompt or some context would have fixed.

Take Listing Studio, a pipeline that turns a supplier's spreadsheet into a published product listing in nine steps. Two of those steps look like tuning candidates, and they come out differently; a third shows what never belongs in the weights. The *brand-voice polish* step rewrites every listing into one house voice at high volume, where a cheaper model would pay for itself. That is pure behavior. The model already knows what a walnut sit-stand desk is; it needs to describe every desk the same way. The *categorize* step places each product in the catalog's taxonomy, and it is mixed. The taxonomy is knowledge that changes whenever merchandising adds a category, so it belongs in the prompt. Only the consistency of choosing between two sibling categories is a behavior a model could be trained toward: the model has both categories in front of it and still files near-identical products differently. The *compliance review* step enforces rules such as a Prop 65 warning (California's required notice for listed chemicals) or the wording a BIFMA stability claim may use (the furniture industry's test standard), and those change on a regulator's or a standards body's schedule. Train them in and the pipeline ships last year's rules with full confidence.

The fix is to name which of the three failures you have, write an eval that measures it, pick the lever that addresses that failure, then climb from the cheapest version upward, stopping at the first rung that clears the bar.

Reach for training when:

- an eval shows that prompting and context have plateaued on a behavior: a format no schema can express, tone, or task execution;
- the task is narrow and high-volume, and a smaller model at the same quality would cut latency or unit cost;
- the instructions and examples you resend on every call have grown expensive, and prompt caching (the provider storing a repeated prefix and billing it at a discount) does not recover the cost;
- a program can score the output, which opens the reinforcement methods below, where training rewards high-scoring outputs.

As a default, do not train to supply facts that are missing or that change (retrieve them instead, see [5.2 Retrieval (RAG)](../knowledge/retrieval-rag.md)), when you have no eval, or when you cannot afford to redo the work on the next base model.

## What it actually is

Train-or-prompt is the decision of which lever fixes a failing model: the prompt, the context, or the weights. It runs as a diagnosis followed by a ladder. The diagnosis sorts the failure into knowledge, behavior or efficiency. Each class has its own lever, and the levers combine. For a behavior failure the default order runs roughly by cost (eval, prompt, context, prompt optimization, training), and you climb only as far as the eval says you must.

![A decision ladder. A failing behavior enters a diagnosis box that sorts it into a knowledge gap, a behavior gap or a cost gap. Knowledge gaps go sideways to retrieval, where the facts stay in documents, and a barred line shows they never reach training. Behavior gaps climb a ladder of rectangles, cheapest first: write the eval, then prompt, then context, then prompt optimization, and reach training only at the top. Between rungs the eval is re-run, and you climb only when it has plateaued; at every rung, an eval that passes means stop. Cost gaps go to a smaller model, which may be a tuned one, drawn as a dashed link to the training rung.](train-or-prompt-ladder.svg)

Nothing in this decision hands control to the model. The choice to tune is an offline engineering call, made by your team and justified by a measurement, much like the decision to add a cache, and it does not change who makes the runtime decisions in the system the tuned model runs in. What is new is the shape of the cost. Tune a hosted model and the thing you tuned belongs to a vendor and has an end date; tune open weights and you own them, along with the serving, while the base still ages.

Prompt-first, eval-driven tuning is Established, which on this site means proven and common, with known trade-offs ([labels](../about/how-we-label.md)). OpenAI documents the loop (evals, then prompting, then fine-tuning, then evals again),[^2] and its accuracy guide adds that the levers fix different problems and stack, so the diagnosis picks the lever and the order is only a default.[^1] Two studies of knowledge injection back the knowledge half of the split.[^3][^4] The upper rungs are younger, and the sections below say where the evidence is still settling or disputed.

Four neighbours are easy to mistake for this decision. Choosing which model to run ([8.2 Which Model?](which-model.md)) comes first; tuning changes the model you already picked. Retrieval is the knowledge lever, and the two combine: RAFT (retrieval-augmented fine-tuning) trains a model to quote the relevant passages from retrieved documents and ignore the distractors. It trains the behavior of reading well; the knowledge itself stays in the documents.[^5] Format failures have a cheaper fix than either lever: structured output, where the API holds the reply to a schema ([2.2 Structured Output](../the-unit/structured-output.md)), so try it before you train for format. And [9.7 Self-Improving Systems](../frontier/self-improving-systems.md) automates some rungs of this ladder in a loop; this chapter is about the call a team makes once, on evidence.

## How to do it

### Write the eval first

A fine-tuning run without a baseline gives you a different model and no way to say whether it is better. The eval set you need is the one you would build to engineer the prompt anyway: real inputs, the outputs you want, and a scorer for the failure you diagnosed. OpenAI's model-optimization loop starts and ends with evals for that reason.[^2] Designing the set is the job of [4.2 Evaluation](../craft/proving-it-works.md); the rule here is that it exists before anyone schedules a training job. If you do train, keep the examples you train on separate from the ones you score on, or the score will flatter the model.

### Spend the prompt before the weights

The case for baking long instructions and examples into the weights is real: every call stops paying for those tokens, and the window is freed for the input. Two things push the break-even back toward the prompt. Prompt caching makes a fixed prefix cheap to resend (see [8.4 Controlling Cost](controlling-cost.md)). And examples in the prompt go further than folklore allows: with hundreds or thousands of examples in context, many-shot prompting performed comparably to fine-tuning on some tasks, at an inference cost that grows with every example you add.[^6] Tokens are not the only cost: a crowded window spreads the model's attention thin, so send only the examples relevant to the input. In one careful comparison at matched model scale, fine-tuning and few-shot prompting generalized about equally well, with large variance on both sides.[^7]

The next rung is context, which means putting the facts the model is missing into the window: by hand for a small fixed set like the taxonomy, by retrieval for a large or changing one like the compliance library ([1.5 Context Engineering](../foundations/context-engineering.md)). You can watch this rung work in your own tools. The instruction file a coding agent reads, such as Claude Code's `CLAUDE.md` or Cursor's rules, changes how a frozen model (one whose weights you cannot change) behaves on your repository with no weight update at all.[^24][^25]

If the prompt has many knobs (instructions, example choice, step wording), a prompt optimizer can search them for you: a program that rewrites the prompt, scores each version on your eval, and keeps the best. DSPy, a framework that compiles prompts against a metric, is the widely cited example, and 9.7 covers the mechanics.[^8] Optimizers are still settling. DSPy and GEPA, a later optimizer, share many of their authors, and most of the published evidence for both comes from those authors.[^9]

### When the weights earn it

Once the eval shows the cheaper rungs have plateaued, the method follows from what you can supply:

- **Supervised fine-tuning (SFT):** pairs of an input and the exact output you want. The default for tone, task execution and any format a schema cannot hold. LIMA shifted a large model's response style with about a thousand curated examples.[^10]
- **Preference tuning (DPO, direct preference optimization):** pairs of a better and a worse output, for when you can rank answers more easily than you can write the ideal one.[^11]
- **Reinforcement fine-tuning (RFT):** a grader, a function or a second model that gives each output a score, rates the model's attempts, and training pushes toward higher scores.[^12]
- **Reinforcement learning with verifiable rewards (RLVR):** the grader is a program, a check with a right answer.[^13][^14] For agentic skills like tool calling ([2.1 Tool Use](../the-unit/tool-use.md)) it is one option, and the check has to test success: a tool call that parses and names the right function can still pass the wrong arguments, and a model trained on a weak check learns to satisfy the check.

SFT is the proven rung. RFT, RLVR and the craft of writing graders are still settling, and the grader is a second program you now have to get right.

Parameter-efficient fine-tuning (PEFT) trains a small set of added weights instead of the whole model. LoRA (low-rank adaptation) adds small update matrices beside the frozen weights,[^15] and QLoRA does the same over a quantized base (its weights stored at lower precision) so it fits on smaller hardware.[^16] Both cost less, and LoRA forgot less of what the base model knew in the study below. Whether adapters learn as much as full fine-tuning is disputed: one study found LoRA learned less on code and math,[^17] and a later analysis from Thinking Machines found it matched full fine-tuning across many post-training settings when configured well, though not on the largest datasets.[^18] Start with LoRA, because it is cheaper, and move to full fine-tuning only if the eval plateaus below the bar.

### The small-model case

The efficiency case for training is a small model doing one narrow job as well as a large one, and it does happen. One study of 310 LoRA-tuned models reported that, across 31 narrow tasks, they beat GPT-4 by about 10 points on average.[^19] The authors sell fine-tuning, and the baseline is a 2024 frontier model. Domain training does not always win either: on several financial text tasks, general-purpose GPT models held their own against BloombergGPT, a large model pretrained on finance.[^20] Read any "tuned small beats frontier" result as true for that task, that date and that pair of models, and measure it on yours.

Before you tune a small model, run it untuned against the eval. If it clears the bar, you get the latency and cost win with no training run, no data to curate and no retraining when the base changes. If it falls short, one common way to get training data is distillation: generate outputs with a large model, curate them, and train the small one on the result. The curation is the work; uncurated teacher outputs teach the small model the teacher's mistakes. Read your provider's terms before you train on its outputs.

## Gotchas

**Training breaks what you did not test.** In Qi et al.'s experiments, fine-tuning aligned models on a small set of benign examples degraded their safety behavior,[^21] which is reason enough to rerun your safety evals after every tuning job ([4.4 Guardrails & Safety](../craft/guardrails-and-safety.md)). A newer result goes further: Betley et al. trained a model to write insecure code and found it behaving badly on unrelated prompts.[^22] The practical rule holds either way: the eval for a tuned model covers more than the behavior you tuned.

**A hosted tune is a fork of a model someone else will retire.** Prompts and tuned models share some upkeep: both need a current eval, and a few-shot prompt has examples to curate. A tuned model adds a training set to refresh and a retraining whenever the base model changes. On Amazon Bedrock, for models launched on or after 7 September 2026, once a base model enters Legacy status you cannot start new fine-tuning jobs on it, deployments created before then keep running until end of life, and nothing migrates them for you.[^23] A prompt moves to a new model with a re-run of the eval and, often, some rework of the prompt. A tuned model moves with a new training run, new data checks and the same eval. Open weights avoid the retirement but not the aging: you host the model, and newer bases keep arriving. The hosted products themselves are volatile: as of this review, OpenAI's model-optimization guide says the company is winding down its fine-tuning platform and has closed it to new users.[^2]

**Training to feel decisive.** A tuning job looks like engineering in a way that editing a prompt does not, and that is how teams end up training before they have an eval or a diagnosis. If you cannot name the failure class and show the plateau on a chart, you are not ready to train.

**Baking a long prompt into weights to save tokens.** It works, and it freezes those instructions until the next training run. Price caching first, and keep anything that changes (policy, prices, the taxonomy) out of the weights.

## In short

Default to the prompt and the context, and write the eval before you touch either. If the failure is knowledge, retrieve it; training will not hold it reliably and will go stale when it changes. If the failure is behavior, push prompting, examples and context against the eval until the curve flattens, and train only then, starting with supervised fine-tuning on a modest curated set. If the failure is cost, try a smaller model untuned before you tune one. Whatever you train, put its retraining on the calendar next to the base model's retirement date, and budget it as a recurring cost.

<small class="chapter-meta">**Maturity: Established** (the prompt-then-tune ladder is a settled decision framework; RFT, RLVR and prompt optimizers are Emerging, LoRA parity and small-beats-frontier Contested) · *Who decides:* your code (an offline engineering call) · *Grounding:* research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: OpenAI, "Optimizing LLM accuracy." <https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy>
[^2]: OpenAI, "Model optimization." Shows the evals, prompt, fine-tune loop and, at the time of review (2026-11), the notice that the fine-tuning platform is winding down and closed to new users; no cutoff dates are given on the page. <https://developers.openai.com/api/docs/guides/model-optimization>
[^3]: Gekhman, Z., et al., "Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?" (2024). One study; the effect is measured on closed-book question answering. <https://arxiv.org/abs/2405.05904>
[^4]: Ovadia, O., et al., "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs" (2023). One study, on knowledge-intensive question answering. <https://arxiv.org/abs/2312.05934>
[^5]: Zhang, T., et al., "RAFT: Adapting Language Model to Domain Specific RAG" (2024). <https://arxiv.org/abs/2403.10131>
[^6]: Agarwal, R., et al., "Many-Shot In-Context Learning" (NeurIPS 2024). Parity is task-dependent. <https://arxiv.org/abs/2404.11018>
[^7]: Mosbach, M., et al., "Few-shot Fine-tuning vs. In-context Learning: A Fair Comparison and Evaluation" (Findings of ACL 2023). <https://arxiv.org/abs/2305.16938>
[^8]: Khattab, O., et al., "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines" (2023). <https://arxiv.org/abs/2310.03714>
[^9]: Agrawal, L. A., et al., "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning" (2025). Margins are the authors' reports. <https://arxiv.org/abs/2507.19457>
[^10]: Zhou, C., et al., "LIMA: Less Is More for Alignment" (2023). <https://arxiv.org/abs/2305.11206>
[^11]: Rafailov, R., et al., "Direct Preference Optimization: Your Language Model is Secretly a Reward Model" (2023). <https://arxiv.org/abs/2305.18290>
[^12]: OpenAI, Fine-tuning API reference: the reinforcement method and its graders, marked alpha. The guide URL resolved to this reference at review. <https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning>
[^13]: Lambert, N., et al., "Tulu 3: Pushing Frontiers in Open Language Model Post-Training" (2024), which names RLVR. <https://arxiv.org/abs/2411.15124>
[^14]: DeepSeek-AI, "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning" (2025), applying RL to verifiable tasks. <https://arxiv.org/abs/2501.12948>
[^15]: Hu, E. J., et al., "LoRA: Low-Rank Adaptation of Large Language Models" (2021). <https://arxiv.org/abs/2106.09685>
[^16]: Dettmers, T., et al., "QLoRA: Efficient Finetuning of Quantized LLMs" (2023). <https://arxiv.org/abs/2305.14314>
[^17]: Biderman, D., et al., "LoRA Learns Less and Forgets Less" (2024). <https://arxiv.org/abs/2405.09673>
[^18]: Schulman, J., and Thinking Machines Lab, "LoRA Without Regret" (2025-09-29). A lab blog post, not peer-reviewed. <https://thinkingmachines.ai/blog/lora/>
[^19]: Zhao, J., et al., "LoRA Land: 310 Fine-tuned LLMs that Rival GPT-4, A Technical Report" (2024). Reports 4-bit LoRA models beating GPT-4 by 10 points on average across 31 tasks; the authors are at Predibase, a fine-tuning vendor, and the baseline is 2024 GPT-4. <https://arxiv.org/abs/2405.00732>
[^20]: Li, X., et al., "Are ChatGPT and GPT-4 General-Purpose Solvers for Financial Text Analytics? A Study on Several Typical Tasks" (2023). GPT-4 beat BloombergGPT on some tasks and lost on others, such as named-entity recognition. <https://arxiv.org/abs/2305.05862>
[^21]: Qi, X., et al., "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!" (ICLR 2024). <https://arxiv.org/abs/2310.03693>
[^22]: Betley, J., et al., "Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs" (2025). <https://arxiv.org/abs/2502.17424>
[^23]: Amazon Web Services, "Model lifecycle," Amazon Bedrock User Guide. Applies to models launched on or after 2026-09-07; earlier models follow the separate Legacy lifecycle page. <https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html>
[^24]: Anthropic, "How Claude remembers your project," Claude Code docs: CLAUDE.md files give Claude persistent instructions loaded into each session. <https://code.claude.com/docs/en/memory>
[^25]: Cursor, "Rules": persistent, reusable context at the prompt level. <https://cursor.com/docs/context/rules>

## See also

- [8.2 Which Model?](which-model.md), the decision that comes before this one: pick the model, then decide whether to change it.
- [5.2 Retrieval (RAG)](../knowledge/retrieval-rag.md), the lever for knowledge failures, and the one this chapter sends you to most often.
- [1.5 Context Engineering](../foundations/context-engineering.md), on curating the window, the rung below training.
- [4.2 Evaluation](../craft/proving-it-works.md), on building the eval set every rung of the ladder depends on.
- [4.4 Guardrails & Safety](../craft/guardrails-and-safety.md), for the safety evals to rerun after a tuning job.
- [2.2 Structured Output](../the-unit/structured-output.md), the cheaper fix when the failure is format.
- [4.1 Prompt Architecture & Management](../craft/prompts-are-source-code.md), on versioning the prompts each rung changes.
- [5.1 State, Not Memory](../knowledge/state-not-memory.md) and [5.3 Memory](../knowledge/real-memory.md), for knowledge that belongs in a store rather than the weights.
- [3.2 Routing & Dispatch](../composition/the-router-that-isnt.md), for sending easy requests to a cheaper model before you train one.
- [8.4 Controlling Cost](controlling-cost.md), on caching and cascades (a cheap model first, escalating to a stronger one when it fails), which move the break-even between a long prompt and a tuned model.
- [9.7 Self-Improving Systems](../frontier/self-improving-systems.md), where prompt optimizers like DSPy and GEPA are covered in depth.
- [The Anti-Patterns Catalog](../catalogs/anti-patterns.md), for training a model to fix what a prompt or some context would have fixed.

## Further reading

- OpenAI, ["Optimizing LLM accuracy"](https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy): the knowledge-versus-behavior framing, with the prompt, retrieval and fine-tuning levers laid out side by side.
- Gekhman et al., ["Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?"](https://arxiv.org/abs/2405.05904): the clearest experiment on why training is a poor way to add facts.
- Biderman et al., ["LoRA Learns Less and Forgets Less"](https://arxiv.org/abs/2405.09673), read with Thinking Machines' ["LoRA Without Regret"](https://thinkingmachines.ai/blog/lora/): both sides of the adapter-parity argument.
- Qi et al., ["Fine-tuning Aligned Language Models Compromises Safety"](https://arxiv.org/abs/2310.03693): the case for rerunning safety evals after every tuning job.
- AWS, ["Model lifecycle"](https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle.html): what retirement does to a customized model, in one vendor's terms.
