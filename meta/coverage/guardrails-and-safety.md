# Coverage map: Guardrails & Safety (chapter 4.4)

> Spec for the chapter, not a draft. Stub at `docs/craft/guardrails-and-safety.md` has no prose, so nothing is marked `[*]`/`[+]`. Sweep angles run: vendor docs, academic, security, skeptical read, incidents (one, partly verified), daily-tool (partial). Alias sweep and SDK issue trackers not run. Last reviewed 2026-11. Neighbours, all unmerged: 2.6 The Harness (tool-call permissions, hooks, where a check runs and how it fails), 4.3 Human-in-the-Loop, 4.6 Prompt Injection, 3.4 and 4.2.

## The mental model

A guardrail is a check on content that crosses the model boundary: input (user text, retrieved text) or output (the answer, before a person or downstream system receives it). The check is a rule your code owns (schema, allowlist, arithmetic against a record) or a classifier that returns a verdict (moderation endpoint, safeguard model, small judge call). The reader leaves able to say which kind each check is, what it costs in false positives and latency, what it does when it errors, and why one filter is never the plan. A model with no tools that reads only your own text and the user's input is ordinary output validation, which is this chapter (4.6 hands it here); anything that gates a tool call is 2.6.

**Who decides (the litmus):** schema, allowlist and record checks: your code decides, engineering the reader knows (OWASP: treat model output as untrusted input). Classifier checks: a model returns a verdict, but your code owns what happens next. A guardrail outputs block, redact, flag or route to `review` (4.3) and never steers or rewrites the run. A retry with the violation fed back is the evaluator-optimizer loop (3.4) or the outer verify-and-retry loop (3.7), owned there.

**Thesis candidate:** "Put a code check on every claim your records can settle, and spend a classifier only on what they cannot, at a false-positive rate you have measured." Fail direction goes in the body, not the thesis.

## Must-cover (ranked)

1. **Deterministic guardrails first: schema, allowlist, claim-vs-record.** Validate shape (pydantic, 2.2), then check values against ground truth your code holds (a numeric claim in copy against `attributes`, a category against an allowlist, a URL against a domain list). Fast and cheap, but "may miss nuanced violations" (LangChain's wording). OWASP LLM05: validate and encode output before downstream components. Skip it and a classifier is asked to do arithmetic. Standard. Lead: OWASP LLM05:2025; LangChain guardrails; 2.2 points here.
2. **Classifier guardrails, and which kind to reach for.** Fixed-taxonomy endpoints cover harm categories: OpenAI `omni-moderation-latest` (free, per-category scores 0 to 1; "signals", not an automatic blocking decision; recalibrate after model upgrades). Policy-as-input classifiers take your own policy: Llama Guard supports "zero-shot or few-shot prompting with diverse taxonomies at the input" (Inan et al.); gpt-oss-safeguard (OpenAI, 2025-10-29, 120b and 20b, Apache 2.0) takes the policy "during inference, rather than being trained into the model"; a structured-output judge call (Anthropic's harmlessness-screen pattern) is the lightweight form. These can catch a restricted claim worded loosely, which a regex cannot. OpenAI's own caveat: a dedicated trained classifier can beat policy-reasoning on complex risks, and the models are slow and compute-intensive. Code-first ordering stands: the record check beats any classifier on arithmetic. Established for harm categories; Emerging for business-policy classification. Lead: arXiv 2312.06674; gpt-oss-safeguard announcement; OpenAI moderation guide; Anthropic "Mitigate jailbreaks."
3. **When the check itself fails: fail-open vs fail-closed.** The classifier times out, the moderation API is down, or the screen declines to classify (Anthropic: Haiku's classifiers "can decline the screening request itself, so treat a response with `stop_reason: "refusal"` as a harmful verdict"). Choose per check, keyed to reversibility: block or route to `review` when the output ships to a storefront, pass and log when it is cheap to undo. Skip it and a guardrail errors open by accident. Reasoned argument; one vendor source. Link 2.6 for hook fail-closed behaviour; do not duplicate.
4. **False-positive cost, thresholds, and shadow mode.** Two error bills: a missed violation, and a blocked legitimate case. Few public measurements exist, mostly vendor-run: Constitutional Classifiers reports a 0.38% absolute rise in production refusals and 23.7% inference overhead (a jailbreak-defense setting; existence proof, not benchmark); Llama Guard reports precision and recall; 4.3 already cites Anthropic's auto-mode figure, so link it rather than retell. The practitioner answer is shadow mode: run a new check log-only on real traffic, label the flagged slice (4.2's job), then turn on blocking, and log every block. No source opened for shadow mode (Azure's page, opened, does not document a detect-only mode); present as practice, not citation. 3.2's confidence floors are honoured here. Emerging. Lead: arXiv 2501.18837; arXiv 2312.06674.
5. **PII and sensitive-data filters, both sides.** Redact, mask, hash or block (LangChain's four strategies), on input, output and tool results. Presidio's own docs: "there is no guarantee that Presidio will find all sensitive information." OWASP LLM02: prefer withholding the data (least privilege) over scrubbing what the model emitted. Established; recall is the open edge. Lead: LangChain; Presidio; OWASP LLM02:2025.
6. **What the caller returns, and the two gaps in placement.** When a check trips, the user gets a structured refusal and the log gets a reason; a raw exception reaching the shopper is the unguarded path (OpenAI tripwires; Guardrails AI `on_fail`). Two placement facts change what a check decides: OpenAI Agents SDK guardrails run on the first agent's input and last agent's output only, so mid-pipeline output goes unchecked; and parallel input checks let side effects happen before the tripwire. One paragraph, then link 2.6 for placement and hooks. Established.
7. **Layering, and what a classifier does not stop.** Hackett et al. report evasion of six deployed detectors, up to 100% in some cases, with character injection. One sentence, then link 4.6 for the adaptive-attack evidence. Anything that must hold goes to enforcement (2.6) or a human gate (4.3).
8. **Frameworks, one line each plus what each leaves unchecked.** OpenAI Agents SDK; LangChain middleware; NeMo Guardrails (Rebedea et al.; also the topical-rail use, one clause); Guardrails AI (hosted inference cutoff 2026-08-25, now past); managed services, Azure AI Content Safety (Prompt Shields, groundedness detection; groundedness is a preview feature that retires 2027-04-30) and Bedrock/Model Armor (unopened, name only after opening). Emerging; APIs move. Framework-positive stance.

## Mention-and-link

- Tool-call permissions, hooks, enforcement vs steering, where a check runs: 2.6 ("what a check decides; 2.6 owns where it runs"). Inbound promises from 2.1 and MCP (2.4), blast radius and allowlisting, route to 2.6 and 2.1 in one paragraph; injection to 4.6.
- Approval gates, `deny` band, below-floor price refusal: 4.3 (link, do not retell).
- Prompt injection, trifecta, adaptive attacks: 4.6.
- Schema validity: 2.2. Measuring a guardrail: 4.2. Rewrite loops: 3.4, 3.7. Confidence floors and default-deny: 3.2.

## Out of scope

Injection defenses (4.6), approval UX (4.3), tool-call enforcement and sandboxing (2.6), alignment and RLHF, red-team method, jurisdictional compliance (name nothing legal beyond the incident).

## Maturity summary

- **Standard:** schema and allowlist validation; output as untrusted.
- **Established:** moderation classifiers for harm categories; PII redaction; block-and-refuse; cheap-first layering.
- **Emerging:** policy-as-input classifiers for business policy; false-positive measurement and shadow mode; fail-direction practice; framework APIs.
- **Contested:** classifier detection of injection as a security control (4.6 owns).

**Verdict candidate: Established**, with an argued sentence: the deterministic layers and harm classifiers are settled; the moving parts are policy classifiers, framework APIs and measured false-positive cost. Last reviewed 2026-11 (the stub says 2026-06; fix). Drop "action" from the stub's input/output/action triple.

## Aliases

guardrails, safeguards, content filters, moderation, rails (NeMo), validators (Guardrails AI), tripwires (OpenAI). Ship the stub's terms only; alias line needs author sign-off.

## Reader-verifiable anchor

The moderation endpoint is free and returns per-category scores: a reader sees a score and a threshold in minutes.

## Carrier section

Primary anchor Listing Studio, step 4 (write copy) and step 8 (brand-voice polish). Scenario: **output guardrails on generated listing copy.** Way-in candidate: step 8's polish rewrites copy that passed every check and reintroduces "holds 300 lb" against a rated 250. Cases: the Aldsworth desk (capacity overclaim vs `attributes.weight_capacity_lbs`, a liability per the bible; the inverse case, copy dropping a required Prop 65 warning, is optional), the bunk bed (a safety claim not in `compliance.safety_claims`; restricted-term list), the phone case (every guard correctly passes), a supplier sheet whose contact, email or cost bleeds into `copy.description` (PII regex). Layers in cost order: schema, claim-vs-record, PII regex, one scripted classifier call. Guard after the polish, not before. A violation blocks the listing into `review` (link 4.3); no rewrite here. Shopper assistant only if an input example is needed. Moffatt is the stakes paragraph, not the opening. No "From production:" callout (author's call).

## Code/demo plan for coder-tester

Offline; stdlib, pydantic and anyio only; no langgraph, no provider SDKs. A `Guardrail` result type (`passed`, `reason`, `severity`, `mode` of `enforce` or `shadow`), a `GuardrailSuite` running checks cheap-first, a tripwire exception carrying the violation. Deterministic checks: capacity claim vs `attributes`; unsupported claim vs `compliance`; restricted terms; email/phone/cost regex. A `FakeClassifier` with scripted verdicts that can also raise or time out. The demo records call order and counts (for example, the classifier was never called on the listings the record check blocked); it quotes no latency, since a fake has none. Tests: desk overclaim blocked; bunk bed blocked; phone case passes all layers; PII stripped; threshold flip changes outcome on a labelled mini-set (false-positive and miss counts); classifier raises and the listing lands in `review`; a `shadow` check records the finding but passes; polish reintroduces a claim and the post-polish guard catches it; optionally one anyio test asserting a side effect already happened when a parallel check trips late, no narrative. Provider tab: Anthropic harmlessness screen only, compiled not run (2.6 already carries the OpenAI one).

## Gotchas (feed Anti-Patterns)

- A single classifier as the whole plan.
- A guardrail that errors open by accident.
- Checking before a rewrite step, not after.
- Moderation categories mistaken for business policy.
- Thresholds copied from a model version since upgraded.
- No measured false-positive rate, so the filter is quietly disabled.

## Incidents

One, partly verified: Moffatt v Air Canada, BC Civil Resolution Tribunal, decided 2024-02-14 (secondary reports): the airline was held answerable for a bereavement-fare statement its chatbot made. The primary returned HTTP 403 and was not opened; it is unclear whether the bot used generative AI. The stakes argument does not depend on that, only on the business being liable for what its bot said, so it can be used once verified without claiming an "AI failure". Mapped guard: claim-vs-record. Do not publish until the primary is read. Other public agent-guardrail postmortems: none found; do not invent.

## Named-idea candidates (offer, never force)

"Cheap checks first"; "price the guardrail"; "guard after the rewrite." Plain descriptions, none a coinage.

## Sources

Opened 2026-11-28 unless noted; web docs cited as accessed.

1. OpenAI Agents SDK, Guardrails, https://openai.github.io/openai-agents-python/guardrails/.
2. Inan et al., "Llama Guard," arXiv 2312.06674, 2023-12-07.
3. OpenAI, Moderation guide, https://developers.openai.com/api/docs/guides/moderation.
4. Rebedea et al., "NeMo Guardrails," arXiv 2310.10501, EMNLP 2023 demo.
5. LangChain, Guardrails, https://docs.langchain.com/oss/python/langchain/guardrails.
6. Guardrails AI README, https://github.com/guardrails-ai/guardrails.
7. Sharma et al., "Constitutional Classifiers," arXiv 2501.18837.
8. Hackett et al., "Bypassing LLM Guardrails," arXiv 2504.11168 (v3 2025-07-14).
9. OWASP LLM05:2025 and LLM02:2025, https://genai.owasp.org/llmrisk/.
10. Anthropic, "Mitigate jailbreaks and prompt injections," https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks.
11. Microsoft Presidio, https://presidio.dataprivacystack.org/.
12. OpenAI, "Introducing gpt-oss-safeguard," https://openai.com/index/introducing-gpt-oss-safeguard/ (2025-10-29).
13. Azure AI Content Safety overview, https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview (updated 2026-11-06).
14. Moffatt v Air Canada, 2024 BCCRT 149 (citation from search results; primary not opened).

## Verify before quoting

- gpt-oss-safeguard: sizes and licence taken from the announcement; model card not opened.
- Llama Guard 4: not opened; open Meta's model card before naming a version or taxonomy, else cite the paper only.
- Not opened: AWS Bedrock Guardrails (page fetch returned nothing usable), Google Model Armor, Prompt Guard, ShieldGemma.
- OpenAI moderation model names and categories, Guardrails AI sunset, LangChain middleware names, Agents SDK parameters: volatile.
- Constitutional Classifiers figures are one system's; do not generalise.

## Map review (Stage 1.5)

An independent review (Claude Opus standing in for codex, unavailable) wrote 18 findings. Each was checked against the primary source where one exists; Llama Guard, gpt-oss-safeguard, Anthropic's page, Azure's overview and the neighbour chapters' text were reopened.

- F1 accepted: 2.6 verified to print tool-guardrail code and to say "what a check decides; this chapter covers where it runs"; placement items merged into item 6, OpenAI tab and anyio narrative dropped.
- F2 accepted: 3.4 verified ("rejects or redacts and never asks for a rewrite"); retry-with-feedback removed from item 2 and tests.
- F3 accepted: Llama Guard abstract and gpt-oss-safeguard announcement verified (date, sizes, licence, quote, limitations); item 2 rewritten; model card still unopened.
- F4 accepted: Anthropic refusal quote verified; item 3, gotcha and test added.
- F5 accepted: "one public measurement" claim replaced; 4.3 cross-linked.
- F6 accepted: way-in candidate added to the carrier section.
- F7 accepted-modified: shadow mode added with a test, but no source supports it (Azure's page does not document detect-only; Bedrock unopened), so it is practice, not citation.
- F8 accepted-modified: Azure opened (groundedness retires 2027-04-30); Bedrock fetch failed, left unopened; Llama Guard 4 named only as unverified.
- F9 accepted: demo records call order and counts; no latency quoted.
- F10 accepted: desk keeps the capacity overclaim; unsupported compliance claim moved to the bunk bed.
- F11 accepted: routing line added; re-pointing the 2.1 and 2.4 links is an edit to shipped chapters, left to the author.
- F12 accepted: body cut to the budget; Moffatt item removed from must-cover, framework item trimmed, gotchas pruned, author questions moved to the PR body.
- F13 accepted: thesis narrowed to one decision.
- F14 accepted-modified: Hackett kept as a single sentence, 4.6 linked for the rest.
- F15 accepted: 4.6's handoff added to the mental model.
- F16 accepted: topical rails as one clause in item 8.
- F17 accepted: incident note now says the stakes argument does not depend on a generative bot.
- F18 accepted: lens-line date and "action" go on the author's PR checklist.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. Thesis and way in as proposed (the polish step reintroducing a capacity overclaim). The Aldsworth desk appears for its weight capacity only, not its price.
2. Maturity: Established, with one argued sentence; injection and jailbreak detection is Contested and is pointed to 4.6, not argued here.
3. Scope: 4.4 decides what a content check concludes. Where a check runs and how tool calls are permitted belongs to 2.6; approval to 4.3; rewriting to 3.4. A violation blocks the listing into review. There is no rewrite loop.
4. The Moffatt case goes in only if its primary decision is opened and read before ship. Otherwise it is cut, not hedged.
5. Code goes under `listing-studio/guardrails/`. Tests are offline and import only stdlib, pydantic and anyio. The classifier is scripted. Any provider or framework example is an illustration file and is compile-checked only.
6. No From-production callout, and no coinage.
7. Shipped chapters (2.1, 2.4) are not edited. Re-pointing their links goes in the PR checklist. The stub's "input/output/action" triple becomes input and output; "action" points to 2.6.
