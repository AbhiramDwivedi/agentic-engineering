# Coverage map: Structured Output (chapter 2.2)

> Research-derived spec for what the chapter must cover to let a reader make a model emit output
> their code can act on — what the schema guarantees, what it does not, and how to handle the
> cases where it breaks — and where to stop. Built from a 5-angle sweep (vendor docs, academic
> +benchmark, OWASP security, practitioner writeups, the skeptical read). Review and trim the
> **Must-cover** list; that sets the chapter's scope. Bar: definitive but tight (the Gang-of-Four
> / Wikipedia test), not exhaustive. Structured output is a **capability, not a pattern** — a
> hexagon in the diagram language, the junior partner to Tool Use (2.1), never sold as a distinct
> agentic pattern.

> **Author sign-off (2026-06-17) — scope locked.** All 8 must-cover items approved as written.
> Decisions: (a) **carrier anchor = the pricing decision** (Listing Studio `price` step — a typed
> pricing decision with a `reasoning` field first), not attribute extraction; (b) **reason-then-format
> is shown in the companion code** (the `reasoning` field precedes the typed payload), not merely
> described — item 7's mitigation gets a worked demo; (c) **item 7 kept as a full must-cover section**
> (both sides argued, reason-then-format as the takeaway); (d) **streaming partial objects = one-line
> mention only** inside item 5, not taught. *Grounding caveat:* the pricing step is real, but the
> chosen example is less first-hand than attribute extraction — prefer "In Listing Studio." /
> "In the companion repo." framing over first-hand "From production." claims unless verified.

## The mental model (what the reader must leave with)

A schema is a typed contract you hand the model, and structured output is the same
constrained-decoding machinery as tool/function calling pointed at one job: making the model fill
that contract so your code gets a typed object instead of prose it has to parse. The one fact
everything else follows from: the constraint guarantees the *shape* (valid JSON, the right fields,
the right types), never the *content* — a schema-valid object can still be wrong, hallucinated, or
carry an injection inside a string field, so validation of meaning stays in your code, and the
cases where even the shape breaks (refusals, truncation) are a contract you have to handle, not a
guarantee you can lean on.

## Must-cover (for trustworthy production use)

Ranked. Each: why it matters, the failure mode if skipped, maturity, lead citation. This is a
fresh write — every item is a gap `[+]`, none `[*]`.

1. **The contract: a schema is a typed contract** `[+]` — a JSON Schema (or Pydantic model /
   TypedDict) is the typed shape the model must fill; mark all fields, forbid extras
   (`additionalProperties: false`), keep descriptions sharp. *Skip it:* you parse free-text prose
   by regex and it drifts the first time the model phrases the answer differently. **Standard.**
   (OpenAI Structured Outputs; Anthropic Structured outputs.)
2. **Structured output IS the same machinery as tool/function calling** `[+]` — the junior-partner
   relationship and the spine of the chapter: function calling is constrained decoding aimed at a
   tool's input schema; "structured output mode" is the same decoder aimed at your response
   schema. One reaches outside the model (a tool runs); the other only shapes what the model
   already produced. *Skip it:* the reader treats it as a separate agentic pattern and over-sells
   it. **Standard.** (Anthropic ships both `strict: true` tool use and JSON outputs as one
   "Structured outputs" feature; link 2.1 Tool Use.)
3. **How it actually works: prompt-and-pray vs JSON mode vs strict schema** `[+]` — three
   reliability tiers: ask in the prompt and hope; JSON mode (valid JSON, *no* schema adherence);
   strict `json_schema` / grammar-constrained decoding (the decoder cannot emit a token that
   violates the schema). The trade-off is reliability vs the supported-schema subset. *Skip it:*
   the reader picks JSON mode, gets syntactically valid JSON with the wrong field names, and
   trusts it. **Standard** (strict mode); **Established** (the tiered distinction). (OpenAI:
   "While both ensure valid JSON is produced, only Structured Outputs ensure schema adherence";
   Outlines, arXiv:2307.09702; XGrammar, arXiv:2411.15100.)
4. **Valid shape is not valid content** `[+]` — the central failure mode: constrained decoding
   guarantees syntax and shape, never semantic correctness; a schema-valid object can be
   hallucinated, out of range, or carry injected instructions inside a string field. You must
   still validate meaning in your code. *Skip it:* the team ships "the schema makes it correct,"
   passes the typed object straight downstream, and a clean-shaped wrong value (or an injection)
   goes live. **Standard risk.** (Gemini docs, verbatim: "structured output guarantees
   syntactically correct JSON... does not guarantee the values are semantically correct"; OWASP
   LLM05 Improper Output Handling; OWASP LLM01 for the in-field-injection point.)
5. **Failure modes that break even the shape** `[+]` — refusals (the safety message takes
   precedence over the schema), `max_tokens` / length truncation (incomplete, unparseable JSON),
   plus the practitioner cliffs: deeply-nested / union / recursive schemas and enums where
   adherence degrades, and streaming partial objects. *Skip it:* `JSON.parse()` throws in
   production on a truncated or refused response that the happy path never anticipated. **Standard**
   (refusals/truncation are documented and detectable); **Emerging** (the nesting/complexity
   reliability cliff — benchmarked, not settled). (Anthropic + OpenAI both document `refusal` and
   max-tokens cases; JSONSchemaBench, arXiv:2501.10868.)
6. **The failure-return contract: re-ask, don't throw** `[+]` — when parse/validation fails, hand
   the model back a structured, recoverable error (the validation message) so it can self-correct
   on retry, instead of raising a raw exception that ends the run. This is the loop's failure path,
   and it is old validation discipline, not a new idea. *Skip it:* a single malformed object
   crashes the pipeline run instead of being repaired in one cheap retry. **Established.**
   (Instructor's reask-on-validation-error; "good LLM validation is just good validation," Liu &
   Leo 2023.)
7. **The reasoning-quality cost of over-constraining, and the mitigation** `[+]` — forcing a tight
   format can degrade reasoning; the mitigation is reason-then-format — let the model think in free
   text first, then emit the typed object (a thinking field, or a two-step call). This is a live
   debate, so present both sides. *Skip it:* the reader wraps a hard schema around a reasoning task
   and quietly loses accuracy. **Contested** (the magnitude and even the direction are disputed).
   (Tam et al. "Let Me Speak Freely?", arXiv:2408.02442; the dottxt rebuttal "Say What You Mean.")
8. **Cost and context economy** `[+]` — the schema rides in the input tokens on every call, so a
   large or deeply-nested schema taxes every request in tokens and attention; strict-mode schema
   compilation can also add first-call latency. The mitigation: keep schemas tight, factor out what
   the step doesn't need. *Skip it:* a sprawling schema silently inflates per-call cost and crowds
   the window. **Standard.** (Vendor pricing/docs; links 1.5 Context Engineering.)

## Mention-and-link (one line, a pointer, not a section)

- **Tool Use** — the loop, the call/decision, treating tool *results* as untrusted, least
  privilege. Function calling is structured output that also runs a function → 2.1 Tool Use.
- **Building tool/function schemas** for the agentic loop (vs response schemas) → 2.1 Tool Use.
- **Context Engineering** — the schema-in-window token/attention cost as a standing budget item →
  1.5 Context Engineering.
- **Evaluation** — measuring schema-adherence and content correctness as a metric → 4.2 Evaluation.
- **Guardrails & Safety** — validating/encoding output before it acts downstream (the LLM05 depth)
  → 4.4 Guardrails & Safety (planned).
- **Output Assembly** — turning the typed object into the shipped deliverable → 6.2 Output Assembly
  (planned).
- **Live schema-adherence numbers** (JSONSchemaBench, per-model JSON-validity rates) → link, do not
  hardcode; they rot.

## Out of scope (name it, point out)

- Constrained-decoding library internals (XGrammar / Outlines / Guidance / llama.cpp GBNF) — cite
  the references, do not teach the FSM/grammar machinery.
- Building tool/function schemas for the agentic loop, the tool-call loop, and tool-result trust →
  2.1 Tool Use.
- Provider API minutiae (exact field spellings, SDK signatures, per-provider JSON-Schema subsets) →
  vendor docs. (Flag for the writer: Gemini's `responseSchema`/`responseJsonSchema` spelling shifts
  across SDKs — quote from the live doc.)
- Output validation/guardrail depth and downstream encoding → 4.4 Guardrails & Safety.
- RAG / retrieval that *feeds* a schema → Part V.

## Maturity summary

- **Standard:** structured output as a capability; JSON-Schema (and Pydantic/TypedDict) contracts;
  strict `json_schema` / grammar-constrained decoding as the reliable mode; the function-calling =
  structured-output equivalence; "valid shape, not valid content" as the operating assumption;
  handling documented refusals and truncation; schema-in-window cost.
- **Established:** the three-tier reliability distinction (prompt-and-pray vs JSON mode vs strict);
  the re-ask-on-validation-error failure-return contract; validation-of-meaning as practice.
- **Emerging:** reliability cliffs on deeply-nested / union / recursive / large schemas (benchmarked
  but unsettled); robust streaming of partial structured objects.
- **Contested:** "the schema guarantees correct content" / "structured output solves hallucination"
  (marketing beyond the evidence); whether format restriction hurts reasoning, and by how much; any
  single quoted JSON-validity or schema-adherence percentage.

## Sources

Vendor: Anthropic "Structured outputs" (platform.claude.com/docs/en/build-with-claude/
structured-outputs) and "Tool use" (platform.claude.com/.../tool-use/overview); OpenAI "Structured
Outputs" (developers.openai.com/api/docs/guides/structured-outputs); Google Gemini "Structured
output" (ai.google.dev/gemini-api/docs/structured-output). Frameworks: Instructor
(python.useinstructor.com — reask/validation + retrying concepts); LangChain `with_structured_output`
(reference.langchain.com). Security: OWASP Top 10 for LLM Applications 2025 — LLM05 Improper Output
Handling (genai.owasp.org/llmrisk/llm052025-improper-output-handling/), LLM01 Prompt Injection.
Academic: Tam et al. "Let Me Speak Freely?" arXiv:2408.02442; dottxt rebuttal "Say What You Mean"
(blog.dottxt.ai/say-what-you-mean.html); Willard & Louf "Efficient Guided Generation" (Outlines)
arXiv:2307.09702; "XGrammar" arXiv:2411.15100; Geng et al. "Grammar-Constrained Decoding..."
arXiv:2305.13971 (EMNLP 2023); "JSONSchemaBench" arXiv:2501.10868. Guidance
(github.com/guidance-ai/guidance) and llama.cpp GBNF (github.com/ggml-org/llama.cpp grammars
README) — cite as references, internals out of scope. Practitioner: Instructor "good LLM validation
is just good validation" (Liu & Leo, 2023).

> **Verify before quoting:** the OpenAI announcement's "~40%→100% schema reliability" figure traces
> to introducing-structured-outputs-in-the-api (returns 403 to automated fetch) — do not hardcode
> it; the developers.openai.com guide carries the qualitative claim safely. Per-model JSON-validity
> rates and JSONSchemaBench per-framework adherence numbers are volatile — cite the finding and the
> live source, never a snapshot. Gemini parameter spelling (`responseSchema` vs `responseJsonSchema`)
> shifts across SDKs — quote the live doc. The "Let Me Speak Freely?" finding is contested (dottxt
> rebuttal); present the debate, not a verdict.
