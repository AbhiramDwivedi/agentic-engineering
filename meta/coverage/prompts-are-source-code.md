# Coverage map: Prompt Architecture & Management (chapter 4.1)

> **Thesis** (the one sentence the chapter argues): *Compose a prompt deliberately — identity and
> scope, then operating rules, then a well-defined slot for injected context, then the output
> contract, ordered by what changes least so the stable part caches — and manage the result like
> code: versioned, reviewed, tested against representative cases (behavioral tests, not compiler
> checks), and revertible the day it regresses.*
>
> Alternatives, offered for sign-off:
> 1. *The wording rarely breaks production; the missing version history, the missing golden set,
>    and the missing rollback path do — so the lifecycle half is the harder argument, not the
>    composition half.* (Leads with the skeptical, "this is the boring half that actually bites
>    you" framing.)
> 2. *Cache stability and instruction-following recency pull a prompt's layers in opposite
>    directions, and reconciling that tension — not picking a favorite four-box diagram — is what
>    composition actually is.* (Leads with the caching/recency trade-off in item 2 below.)
> 3. *A production prompt is a versioned interface between code and a stochastic model: separate
>    stable instructions from variable data, and ship each change only with representative
>    evaluations, traceable configuration, and a rollbackable version.* (Second-reviewer
>    alternative; leads with the interface framing and states the lifecycle discipline in full
>    inside one sentence rather than gesturing at it.)
>
> **Budget:** standard pattern, ~2,000-2,800 prose words to the end of *In short* (code, sources,
> and cross-links excluded). Six must-cover items (trimmed from the first draft's seven-plus-a-
> catalog after the second-reviewer pass; see below) fits this row **only if**: automatic prompt
> optimization stays the one sentence it now is under Mention-and-link (not a must-cover item), the
> composition-discipline item folds persona and few-shot in as a single paragraph rather than two
> sections, and the ecosystem mention names one category plus at most two exemplars, never a
> vendor list. Recommend holding the standard-pattern row under those constraints rather than
> requesting the larger flagship row.
>
> Research-derived spec for what the chapter must cover to let a reader compose a prompt
> deliberately and manage it as a versioned artifact, and where to stop — handing depth to the
> chapters that own it. Built from a sweep across vendor/primary docs, academic literature,
> security, practitioner writeups, the skeptical read, the alias sweep, the everyday-engineer
> angle, the daily-tool angle, and incidents; see "Sweep angles run and skipped" below. The chapter
> path (`docs/craft/prompts-are-source-code.md`) is a stub whose gloss, alias line, and lens line
> were rescoped but never argued in prose, so nothing below is marked `[*]`/`[+]` against the
> chapter itself — this map evaluates the stub's three claims (the gloss, the alias line, and the
> bare `Standard`/`production` lens line) rather than assuming them. This is the second pass on
> this map: a first draft went through an independent second-reviewer pass, and every finding from
> that review was checked against primary sources before being folded in or declined; see "Second-
> reviewer pass" below for the disposition of each finding. Review and trim the **Must-cover**
> list; that sets the chapter's scope. Bar: definitive but tight (the Gang-of-Four / Wikipedia
> test), not exhaustive.

## The seam with 1.5 Context Engineering and 2.3 Skills

Both neighbors are shipped chapters this chapter must not re-teach, and both were read in full for
this map, along with their own coverage maps (`meta/coverage/context-engineering.md`,
`meta/coverage/skills.md`).

**The ownership line, drawn precisely.** 1.5 owns *which* runtime content enters the context
window, *how much* of it, and *how it is assembled or curated* at call time: the context window as
the shared budget, the two costs every token pays (money and attention), context rot, progressive
disclosure as the general principle, and the four named window-failure modes (poisoning,
distraction, confusion, clash). 1.5's own text is explicit that "everything that competes for that
span is 'context': the system prompt, the tool definitions, retrieved knowledge, reloaded memory,
few-shot examples, and the message history," and its curation moves — write less in, reveal on
demand, compress, isolate — are all about *selecting and shaping runtime content*, not about the
authored document's structure. **4.1 owns the authored template**: the fixed layers of the prompt
document itself (identity and scope, operating rules, a slot for injected context, an output
contract), the delimiters and insertion points that mark where runtime content lands inside that
template, the data contract each slot expects (for example: "the injected-context slot receives a
list of tagged document snippets with a source field," not the freeform prose 1.5 might otherwise
curate into it), and the template's lifecycle (versioned, reviewed, tested, rolled back). Put
plainly: 1.5 decides what goes in the box and how full the box gets; 4.1 builds the box, labels its
compartments, and keeps a paper trail of who moved the walls and when. **This chapter never
decides what content fills the injected-context slot, how much of it there is, or how it is
curated — that decision belongs to 1.5 (and, for retrieval and memory specifically, to Part V) in
every one of the items below.** This redraws the seam more narrowly than an earlier version of
this map, which let "injected context: the per-request variable material" read as though 4.1
governed selection and quantity; it does not, and every must-cover item below has been checked and
worded to keep that line.

**2.3 owns Skills**: a `SKILL.md` plus bundled files/scripts that the *runtime* reveals in stages,
where the model only decides which skill to pull in. 2.3 is explicit that a skill "packages
procedural knowledge the model needs only *sometimes*" and is a mechanism for *not* putting
content in the always-resident prompt at all. 4.1's composition layers describe what's *always* in
the window every call; a Skill is the escape hatch for content that would otherwise bloat that
always-resident prompt. State this contrast in one line in "Mention-and-link" — do not re-explain
the three load levels or the supply-chain security material, both fully 2.3's.

## The mental model (what the reader must leave with)

A prompt is not one clever paragraph; it is an authored template with named slots that change at
different rates, and 4.1's whole job is that template — how its slots are arranged, what each slot
promises to receive, and how the finished document is managed once it ships. The chapter does not
decide what fills the slots at runtime (1.5's job); it decides the shape of the container and its
lifecycle. So the chapter has two honest jobs: **compose the template deliberately** (state the
task and success criteria explicitly, separate instructions from data with consistent delimiters,
order rules where sequence matters, and order the stable layers first because a cache can only
reuse a contiguous, unchanging prefix) and **manage the template like the artifact it is**
(versioned with an identity that survives a rollback, reviewed, tested against representative
cases before it ships, and revertible with a paired record of the model and generation
configuration it ran with, since a prompt version reverted against a since-changed model is not
actually the old, working combination). Treat either job as optional and the other absorbs
failures it wasn't designed to catch: sloppy composition surfaces as a lifecycle incident nobody
can explain; a missing lifecycle turns a one-line composition tweak into an unreviewed, unversioned
production surprise.

## Must-cover (ranked)

Each: why it matters, the failure mode if skipped, maturity, lead citation.

1. **Composition discipline: the baseline, before cache ordering, persona, or few-shot** — state
   the task and success criteria explicitly rather than assuming the model will infer intent;
   separate instructions from data and examples using consistent delimiters (Anthropic's own
   current guidance: "XML tags help Claude parse complex prompts unambiguously, especially when
   your prompt mixes instructions, context, examples, and variable inputs. Wrapping each type of
   content in its own tag... reduces misinterpretation";[^anthropic-pe] "provide instructions as
   sequential steps using numbered lists or bullet points when the order or completeness of steps
   matters"[^anthropic-pe]); order rules sequentially where sequence genuinely matters. Fold in, as
   *optional, measured* techniques rather than default wins, the two choices readers reach for by
   habit: persona prompting (assigning the model a role) does not reliably improve performance on
   *factual* tasks — Zheng et al. (EMNLP Findings 2024), testing 162 personas across 4 model
   families and 2,410 factual questions, found personas in system prompts do not improve
   factual-task performance;[^zheng-persona] Kong et al. (NAACL 2024) is the honest counter-
   evidence on a *different task class*, zero-shot reasoning benchmarks specifically, where
   role-play prompting measurably helped (e.g. AQuA accuracy 53.5% → 63.8% on
   ChatGPT).[^kong-roleplay] Few-shot examples trace to Brown et al. (2020), which established
   in-context few-shot learning as a capability at all,[^brown-fewshot] but Min et al. (2022)'s
   often-cited "label correctness barely matters" finding is itself task-class limited: it was
   measured on classification and multiple-choice tasks specifically, across the 12 models tested,
   and shows demonstrations there teach the label space, input distribution, and output format
   rather than the "right answer" by example — do not generalize it into a universal claim about
   what examples teach across every prompt.[^min-demos] Format sensitivity compounds all of this:
   Sclar et al. (ICLR 2024) measured swings of up to 76 accuracy points from prompt-formatting
   choices a human would consider meaning-preserving.[^sclar-format] *Skip it:* a reader ships a
   prompt with an implicit, unstated success criterion, or assumes "adding a persona" or "adding
   examples" is a free quality lever untested for their own task class. **Standard** (the baseline
   discipline: explicit task, delimiters, ordered rules — vendor-documented, no controversy);
   **Established** (few-shot as a capability) inside a **Contested** corner (persona prompting as a
   reliable, task-general lever; the "more examples always helps" habit). (Anthropic, prompting
   best practices;[^anthropic-pe] Zheng et al., arXiv:2311.10054; Kong et al., arXiv:2308.07702;
   Brown et al., arXiv:2005.14165; Min et al., arXiv:2202.12837; Sclar et al., arXiv:2310.11324.)

2. **The four-layer template and cache-aware ordering — the artifact's structure, not its
   contents** — define four named layers: identity and scope (who the model is, what it's for,
   what's explicitly out of scope), operating rules (how to behave, including what to do on
   failure or genuine uncertainty — pointer to [4.3 Human-in-the-Loop](human-in-the-loop.md) for
   the escalation mechanics), a **slot** for injected context (a defined insertion point with a
   data contract — e.g. "receives tagged document snippets" — never the selection, quantity, or
   curation of what fills it, which is 1.5's decision entirely), and an output contract (format
   and schema constraints). Order the stable layers first: Anthropic's prompt-caching mechanism
   caches only a *contiguous prefix* from the start of the prompt, up to four breakpoints, with a
   per-model minimum cacheable length that varies (roughly 512 to 4,096 tokens across current model
   families as of this sweep) and a default 5-minute TTL, refreshed on reuse, with an optional
   1-hour TTL at added cost[^anthropic-cache] — so identity and operating rules, which repeat
   across calls, belong at the front where a cache hit can reuse them, and the injected-context
   slot, which changes every call, belongs after the cacheable prefix, never inside it. OpenAI's
   equivalent mechanics are model-specific and currently in flux, not a single stable rule: models
   from GPT-5.6 onward use a roughly 1,024-visible-token minimum and support explicit cache
   breakpoints, while GPT-5.5 and earlier models generally require roughly 2,048 tokens, place
   breakpoints implicitly at regular intervals, and do not support explicit breakpoints at
   all[^openai-cache] — cite the live docs, never freeze this table. A second, separate finding
   cuts against a naive reading of "stable content always goes first": Anthropic's own long-context
   guidance recommends placing instructions *after* a long (~20k+ token) document because it
   measurably improves compliance,[^anthropic-longctx] and OpenAI's GPT-4.1 guide finds repeating
   instructions at both the start and end of a long context beats stating them once above the
   content alone.[^openai-gpt41] Name the trade-off honestly rather than resolve it into one rule:
   a stable output-contract block placed last for compliance reasons is no longer a prefix and
   cannot itself be cached the way the identity/rules block can. This is each vendor's own
   documented guidance for its own model family under a specific condition (a long document in the
   window) — it is not established as a provider-independent "always put the output contract last"
   rule, and a reader should verify it against their own evals before treating it as universal.
   *Skip it:* a reader interleaves volatile content into what should be the stable prefix and pays
   for the whole prompt on every call, or assumes a caching or ordering rule verified for one
   vendor's long-document case transfers unchanged to every prompt. **Established** (prompt
   caching mechanics exist and are vendor-documented, though the specific thresholds are volatile
   and must be re-verified against live docs); the compliance-placement heuristic for the output
   contract is **model-specific / Emerging** pending a reader's own evals, not a settled,
   provider-independent rule. (Anthropic, prompt caching docs;[^anthropic-cache] Anthropic, "Long
   context prompting tips";[^anthropic-longctx] OpenAI, prompt caching docs;[^openai-cache] OpenAI,
   GPT-4.1 prompting guide;[^openai-gpt41] the four-layer decomposition itself — Identity /
   Instructions / Context Injection / Output Constraints — is Gulli & Nawalgaria's own organizing
   structure for this material, attributed and reordered here for cache stability rather than
   reproduced as given.[^gulli-ch2])

3. **The instruction hierarchy governs which layer wins when sources conflict — documented today
   on one platform, not yet confirmed as a cross-vendor guarantee** — the operating-rules layer
   does not exist in isolation; a production system layers a platform's own baked-in behavior, the
   developer's system prompt, and (often) live user text, and something decides which wins when
   they conflict. OpenAI's Model Spec names this explicitly as a chain of command — Root, then
   System, then Developer, then User, then Guideline, each level overriding the ones below it, with
   no negotiation and no "more polite request wins"[^openai-modelspec] — but the Spec is itself an
   *intended-behavior* document, and says so plainly: "Our production models do not yet fully
   reflect the Model Spec, but we are continually refining and updating our systems to bring them
   into closer alignment with these guidelines."[^openai-modelspec] Cite it as a stated design
   intent, not a verified behavioral guarantee. Anthropic and Google do not publish an equivalently
   explicit hierarchy document; this sweep found no primary source establishing that either
   platform's actual role semantics mirror OpenAI's five-level structure, so do not assert
   cross-vendor parity — name OpenAI's as the clearest primary source for the *concept*, and treat
   the concept's applicability elsewhere as unconfirmed. *Skip it:* a reader treats "the prompt" as
   one flat document and is surprised when a user's in-conversation instruction doesn't override
   what they wrote in the system prompt, or assumes a written, guaranteed hierarchy applies
   uniformly across every vendor. **Established** (that OpenAI documents an intended hierarchy);
   **Emerging / unconfirmed** (that production behavior fully matches it, or that other vendors
   have an equivalent explicit specification). (OpenAI, Model Spec, "Chain of
   Command."[^openai-modelspec])

4. **Templating mechanics for a template you control** — three concrete failure classes. First,
   silent missing variables: a template that references a field the upstream step never populated
   should fail loudly (a render error), not interpolate an empty string the model then reasons over
   as if it were real data. Second, cache-busting nondeterminism: anything nondeterministic placed
   before the cache breakpoint (a live timestamp, a request ID) silently defeats caching for the
   whole prefix, a mistake that is easy to make and invisible until someone checks the cache-hit
   rate. Third, and precisely: a real, patched vulnerability class shows what "escaping" actually
   means in practice. CVE-2025-65106 (published 2025-11-19) describes LangChain-core's f-string
   template implementation as *the* vulnerability — unrestricted attribute-access syntax such as
   `{obj.attr}` or `{obj[0]}` let an attacker who controlled template *structure* traverse Python
   object internals; the fix restricts f-string variables to valid Python identifiers only. The
   advisory describes the accompanying Mustache and Jinja2 changes as *defensive hardening*, not
   fixes for a confirmed exploit in those formats specifically — and notably, the Jinja2 hardening
   was later reverted in `langchain-core` 1.1.3 because the restriction "significantly limited
   legitimate Jinja2 usage and broke existing templates," with the advisory's own guidance that
   Jinja2 is intended for use only with *trusted* template sources.[^cve-template] The practical
   rule for the common case this chapter owns — a template you wrote and control, with only
   variable *values* coming from elsewhere — is simpler than the CVE: keep the template hardcoded
   in your own source and pass untrusted content only as data through the render context, never as
   template syntax. Untrusted-template-content exploitation (an attacker's text read as an
   instruction once it lands in the rendered prompt) is [4.6 Prompt Injection](prompt-injection.md)'s
   depth — this item owns hygiene mechanics for a template you control, not the adversarial-content
   attack surface. *Skip it:* a missing-variable bug ships silently, a cache silently stops
   working, or a team reads the CVE headline as "never use Jinja2" rather than the narrower,
   accurate lesson about accepting untrusted template structure. **Standard** (template hygiene as
   engineering discipline). (CVE-2025-65106 / GHSA-6qv9-48xg-fc7f.[^cve-template])

5. **The lifecycle: version identity, run-level traceability, promotion, and rollback** — treat a
   prompt template like the artifact it is, with more machinery than "save a copy and diff it."
   A version needs an **immutable identity** that is never silently overwritten. Every production
   run needs **traceability**: which prompt version ran, paired with the model and generation
   configuration it ran with — rollback is not actually operational without that pairing, because
   reverting a prompt version against a since-changed model or config is not the old, working
   combination, it's a new, untested one. Decide explicitly whether model, tool, and configuration
   changes travel *bundled with* a prompt version or are versioned independently; an unstated
   default here is a bug waiting to happen. Google's Vertex AI Prompt resource is the clearest
   primary example of a vendor doing this: creating a version via the SDK's prompt-versioning
   workflow bundles the model name, prompt contents, variables, generation configuration, system
   instruction, and safety settings as one unit, with named "list available prompt versions" and
   "restore a version of a prompt" operations.[^vertex-promptmgmt] **Promotion/deployment** (moving
   a version from staging to production) is the last mile of the lifecycle — name it as a required
   step, do not build a deployment pipeline in prose. Review and version control themselves are
   general software-engineering discipline applied to a new artifact type, not something specific
   to prompts; treat them as such. Grading methodology — how to build and trust a representative
   test set, pass^k, judge validity — is [4.2 Evaluation](proving-it-works.md)'s depth; this item
   names the *golden-set-before-ship* discipline and stops. *Skip it:* a team cannot say who
   changed a prompt, why, which model it was tested against, or how to get back to the version that
   worked, and finds out a change regressed production from a complaint rather than a test.
   **Standard** (version control, code review, and rollback as general engineering practice,
   applied here to a new artifact type — no controversy in the principle); prompt-specific
   golden-set regression testing as its *own* discipline is **Established or Emerging depending on
   the evidence available at draft time** — this split is not yet settled and depends on the
   author's ruling on production grounding (see Open Questions). (12-Factor Agents, Factor 2 "Own
   your prompts" and Factor 3 "Own your context window";[^12factor2] Google, Vertex AI prompt
   management / Prompt resource versioning.[^vertex-promptmgmt])

6. **Composition rule: prompts are not secret stores** — OWASP names this directly: LLM07:2025
   System Prompt Leakage, the risk that a "hidden" system prompt is treated as a secure container
   for credentials, business rules, or internal taxonomy, when nothing guarantees it stays
   hidden.[^owasp-llm07] The composition rule this chapter owns: never place a credential, an
   internal-only fact, or anything whose disclosure would be a real incident inside any layer of
   the template, and design the operating-rules layer so that a leaked prompt costs you nothing
   worse than revealing your own prompt style. The *attack* side of this — how a prompt actually
   gets extracted or leaked, direct or indirect injection — is [4.6 Prompt
   Injection](prompt-injection.md)'s full depth; this item states the design rule and cites the
   risk category, nothing more, and this map does not carry a leak-incident catalog because this
   sweep found no leak example meeting the bar of a primary, verifiable citation (see Incidents).
   *Skip it:* a leaked prompt exposes a credential, an internal pricing rule, or a competitive
   detail nobody meant to ship. **Standard** (the design rule itself; OWASP-named category).
   (OWASP, LLM07:2025 System Prompt Leakage.[^owasp-llm07])

## Mention-and-link (one line, a pointer, not a section)

- **The context window as the shared budget, and the two costs every token pays, and the selection
  or curation of runtime content that fills any slot this chapter defines** → [1.5 Context
  Engineering](../foundations/context-engineering.md); this chapter's job is the authored template
  and its lifecycle, never what fills a slot at runtime.
- **Progressive disclosure and Skills** — packaging content the model needs only sometimes so it
  never enters the always-resident prompt at all, the escape hatch from this chapter's
  always-in-context layers → [2.3 Skills](../the-unit/skills.md).
- **Structured output / the output contract's schema mechanics** — this chapter names the output
  contract as a layer; the schema and validation depth is [2.2 Structured
  Output](../the-unit/structured-output.md)'s.
- **Prompt injection and system-prompt extraction attacks** — the adversarial half of both the
  templating item and the "not a secret store" rule above (an attacker's text read as an
  instruction, or a technique used to extract a hidden prompt) → [4.6 Prompt
  Injection](prompt-injection.md); this chapter owns template hygiene and the composition rule, not
  the attack surface.
- **The escalation path when the operating-rules layer says "ask a human"** → [4.3
  Human-in-the-Loop](human-in-the-loop.md).
- **Reasoning effort, thinking budgets, and extended-thinking parameters** — a composition-adjacent
  knob, owned in full → [4.5 Reasoning & Thinking Budgets](reasoning-and-thinking-budgets.md).
- **Evaluation methodology for a golden set** (how you build and grade one, pass^k, judge
  validity) → [4.2 Evaluation](proving-it-works.md); this chapter names the golden-set discipline,
  4.2 owns how to build and trust one.
- **Model selection as a prompt-portability concern** (a prompt tuned for one model degrading on
  another) → [8.2 Which Model?](../production/which-model.md).
- **Prompt-caching cost mechanics in full** (pricing, cache-hit economics beyond the ordering
  rule) → [8.4 Controlling Cost](../production/controlling-cost.md).
- **Automatic prompt optimization** — the case where a *model*, not a person, edits the prompt
  (DSPy's `MIPRO`/`MIPROv2`, OPRO, GEPA); the litmus edge case for this chapter (composing and
  versioning a prompt is your code's decision; letting a model rewrite it is the model's), and its
  full depth, including any production-adoption or benchmark claims, belongs to → [9.7
  Self-Improving Systems](../frontier/self-improving-systems.md).[^dspy][^opro][^gepa]

## Out of scope (name it, point out)

- Prompt-management platforms as a product category (e.g. Langfuse as an open-source example, the
  Anthropic Console as the vendor-native example) — name the category and one or two exemplars in
  chapter prose; never a comparison matrix across vendors.
- The full instruction-hierarchy/chain-of-command *security* treatment (jailbreaks that exploit
  hierarchy confusion) → [4.6 Prompt Injection](prompt-injection.md).
- Automatic prompt optimization's mechanics and any production-adoption claim → [9.7
  Self-Improving Systems](../frontier/self-improving-systems.md); this chapter names it in one
  sentence and stops.
- The three-level Skills loading model → [2.3 Skills](../the-unit/skills.md).
- Reasoning/thinking-budget parameters → [4.5 Reasoning & Thinking
  Budgets](reasoning-and-thinking-budgets.md).
- Grading methodology for a golden set (how to build one, pass^k, judge validity) → [4.2
  Evaluation](proving-it-works.md).
- Live per-model cache-pricing numbers and minimum-cacheable-token tables — these differ by model
  and change with every release; cite the live doc, never reproduce a frozen table.

## Maturity summary

- **Standard:** the composition baseline (explicit task/success criteria, delimiters, ordered
  rules); template hygiene (fail loudly on a missing variable, keep templates hardcoded, pass
  untrusted content only as data); version control, code review, and rollback as engineering
  discipline applied to prompts; "prompts are not secret stores" as a design rule.
- **Established:** prompt caching mechanics as a vendor-documented capability (though specific
  thresholds are volatile); few-shot examples as a capability; that OpenAI documents an intended
  instruction hierarchy.
- **Emerging / model-specific:** the compliance-placement heuristic for where the output contract
  belongs in a long prompt (each vendor's own guidance for its own model family under specific
  conditions, not a settled provider-independent rule); cross-vendor parity for the instruction
  hierarchy (unconfirmed for Anthropic and Google); prompt-specific golden-set regression testing
  as its own discipline, pending the author's production-grounding ruling.
- **Contested:** persona prompting as a reliable, task-general quality lever (mixed evidence,
  task-dependent); "more few-shot examples always helps" as a default habit; any claim that a
  prompt-management platform makes prompt engineering itself a solved problem.

## Aliases

True synonyms — names other sources use for this chapter's subject, each with its source:

- **prompt architecture** — Gulli & Nawalgaria, *Building AI Agents* (public draft manuscript), ch.
  2 title.[^gulli-ch2]
- **prompt composition** — general practitioner usage; not attributable to one source.
- **prompt versioning** — vendor/practitioner term of art (Braintrust, LangWatch, PromptLayer
  product documentation all use it directly).
- **prompt management** — the umbrella term the vendor-tooling ecosystem uses for this chapter's
  lifecycle half (Vertex AI's own feature name is "Prompt management";[^vertex-promptmgmt]
  LangSmith, Langfuse, and PromptLayer all use the same term for their product category).
- **prompt lifecycle management** — practitioner/vendor phrasing for the same idea, used
  interchangeably with "prompt versioning" across the same tooling cluster.
- **PromptOps** — practitioner/vendor framing analogous to DevOps; no single canonical origin,
  used across multiple 2026 vendor and practitioner posts.
- **prompts-as-code / "prompts are code"** — widespread practitioner framing, not this reference's
  coinage; 12-Factor Agents' Factor 2 "Own your prompts" is the sharpest primary-source statement
  of the same idea.[^12factor2]

Related, not synonyms — components or neighboring techniques this chapter's items draw on, each
worth a mention but not a stand-in for the chapter's title:

- **persona design / persona prompting** — the term of art the Zheng et al. paper's own title
  uses ("Personas in System Prompts").[^zheng-persona] A technique this chapter's composition item
  discusses, not a synonym for prompt architecture as a whole.
- **few-shot prompting / in-context learning** — Brown et al.'s own framing.[^brown-fewshot] Same
  status as persona prompting: a component technique, not a synonym.
- **chain of command / instruction hierarchy** — OpenAI's own term, Model Spec.[^openai-modelspec]
  A mechanism this chapter's item 3 explains, not a synonym for the chapter's subject.
- **four-layer prompt / Identity-Instructions-Context Injection-Output Constraints** — Gulli &
  Nawalgaria's own organizing structure, attributed and reordered here by cache stability rather
  than reproduced as given;[^gulli-ch2] a structure the chapter adopts, not a synonym for its
  title.
- **automatic prompt optimization / prompt optimizer / reflective prompt evolution** — DSPy/GEPA
  papers' own terms; a related but distinct technique whose depth belongs to 9.7, one sentence here.
- **spec engineering / spec-driven development** — a related but explicitly *non*-synonymous
  practitioner term (GitHub Spec Kit, AWS Kiro, Addy Osmani's writing) for the human-authored
  specification a coding agent executes from. A spec governs a task; a prompt as composed here
  governs a model's standing behavior. Included as a named neighbor for the alias sweep's
  completeness, not as a candidate for the chapter's own `*Also called:*` line. Flag for author
  judgment: keep as a related-term footnote, or omit as scope creep toward 9.6 Coding Agents.

## Reader-verifiable anchors

- **Two coding agents, two different answers to "which file is the versioned prompt," both
  checkable today.** Anthropic's current documentation states plainly that "Claude Code reads
  `CLAUDE.md`, not `AGENTS.md`," with the supported bridge for a repository that already
  standardized on `AGENTS.md` being either a `@AGENTS.md` import line inside a `CLAUDE.md` file or
  a plain symlink (`ln -s AGENTS.md CLAUDE.md`).[^cc-memory] OpenAI's Codex takes the opposite
  design: it reads layered `AGENTS.md` files (and an `AGENTS.override.md` variant that takes
  precedence at each level), discovered from a global scope down through the project's directory
  tree and concatenated root-to-leaf, so files closer to the working directory override earlier
  guidance because they appear later in the combined prompt.[^codex-agentsmd] A reader can open
  either tool's own docs and their own project's instructions file today — two different, live,
  version-controlled answers to how a prompt-as-source-code artifact is composed from layered
  files, from two different vendors, checkable without this chapter's help.
- **The Anthropic Console's Evaluate feature visibly implements part of the lifecycle this chapter
  argues for.** A reader can generate or import test cases (including an auto-generate feature),
  compare the outputs of two or more prompt versions side by side, and have a person grade response
  quality on a 5-point scale to see whether a change improved it — version, test, and compare, as
  an actual product surface a reader can open today, not a diagram.[^anthropic-console] (Narrowed
  from an earlier draft of this map, which additionally claimed a one-click "Get Code" deployment
  gate; the cited article does not establish that claim, so it is dropped here rather than
  reproduced unverified.)

## Incidents

- **CVE-2025-65106 (2025-11-19)** — a real, patched vulnerability in `langchain-core`'s f-string
  template implementation specifically (unrestricted attribute-access syntax), with Mustache and
  Jinja2 receiving defensive hardening rather than fixes for a confirmed exploit in those formats;
  the Jinja2 hardening was itself later reverted in `langchain-core` 1.1.3 because it broke
  legitimate use, with the advisory's own guidance that Jinja2 should be used only with trusted
  template sources.[^cve-template] Directly maps to the templating item above (item 4); the
  realistic blast radius requires an application that accepts untrusted *template structure*, not
  just untrusted variable values, and this chapter should say so rather than let the CVSS score
  imply universal severity to every templated prompt.
- **Public system-prompt leaks (e.g. Bing/"Sydney," a purported GPT-5 system prompt) were removed
  from this section** after the second-reviewer pass. Neither example has a primary, verifiable
  citation this sweep could stand behind (the GPT-5 case in particular was never officially
  confirmed by OpenAI), and both are extraction *attacks* rather than a composition failure this
  chapter owns — they belong, if cited at all, to [4.6 Prompt Injection](prompt-injection.md) with
  a primary source found there. This chapter states the design rule (item 6) and stops.
- **A named, dated, public postmortem of a prompt change regressing a production system**: none
  found this sweep. The pattern (an undocumented, unversioned prompt edit breaking output,
  discovered late) is consistently described across practitioner blogs, but this sweep found no
  single company-attributed, dated incident write-up to cite by name. State "the pattern is
  well-attested anecdotally; no named postmortem found" rather than force a citation.

## Named-idea candidates

The chapter's framing ("prompts are source code") is already a widely used practitioner phrase,
not a coinage available to claim, and it does the naming job well enough on its own — recommend
**no forced coinage** for the chapter's central idea. One small, nameable technique is worth
offering, not forcing:

1. **"The static prefix"** — for the cache-ordering discipline in item 2 (put what changes least
   at the front, and know that a stable block placed at the end for compliance reasons stops being
   a prefix and stops being cacheable). Small, precise, plain enough for a design review. Offered,
   not forced; strike if the author judges "cache-aware ordering" reads better without a name.

## Sources

Vendor/primary: Anthropic, prompt engineering documentation, "Prompting best practices" (clear and
direct instructions, sequential steps, XML-tag structuring).[^anthropic-pe] Anthropic, "Prompt
caching" documentation (cache breakpoints, per-model minimum cacheable length, 5-minute default TTL
with an optional 1-hour TTL).[^anthropic-cache] Anthropic, "Long context prompting tips"
(instructions after long documents; query placement).[^anthropic-longctx] Anthropic, "Evaluate
prompts in the developer console" (test-case generation, side-by-side version comparison,
grading).[^anthropic-console] OpenAI, "Prompt caching" API guide (model-specific minimums and
breakpoint support, GPT-5.6+ vs. earlier).[^openai-cache] OpenAI, GPT-4.1 prompting guide
(instruction placement in long context).[^openai-gpt41] OpenAI, Model Spec, including its own
production-alignment caveat.[^openai-modelspec] Google, Vertex AI "Prompt management" documentation
and prompt-template SDK samples (versioned model/contents/variables/generation-config/system-
instruction/safety-settings, list/restore version operations).[^vertex-promptmgmt] HumanLayer,
12-Factor Agents, Factor 2 "Own your prompts" and Factor 3 "Own your context window"
(2025).[^12factor2] Anthropic, Claude Code memory documentation (`CLAUDE.md` vs.
`AGENTS.md`).[^cc-memory] OpenAI, Codex `AGENTS.md` / `AGENTS.override.md` documentation.[^codex-agentsmd]
Academic: Zheng et al., "When 'A Helpful Assistant' Is Not Really Helpful," EMNLP Findings 2024,
arXiv:2311.10054.[^zheng-persona] Kong et al., "Better Zero-Shot Reasoning with Role-Play
Prompting," NAACL 2024, arXiv:2308.07702.[^kong-roleplay] Brown et al., "Language Models are
Few-Shot Learners," NeurIPS 2020, arXiv:2005.14165.[^brown-fewshot] Min et al., "Rethinking the
Role of Demonstrations," EMNLP 2022, arXiv:2202.12837.[^min-demos] Sclar et al., "Quantifying
Language Models' Sensitivity to Spurious Features in Prompt Design, or: How I Learned to Start
Worrying About Prompt Formatting," ICLR 2024, arXiv:2310.11324.[^sclar-format] Khattab et al.,
"DSPy," arXiv:2310.03714.[^dspy] Opsahl-Ong et al., introducing "MIPRO," arXiv:2406.11695, shipped
in the DSPy library as the `MIPROv2` optimizer.[^miprov2] Yang et al., "Large Language Models as
Optimizers" (OPRO), arXiv:2309.03409.[^opro] Agrawal et al., "GEPA: Reflective Prompt Evolution Can
Outperform Reinforcement Learning," ICLR 2026 Oral, arXiv:2507.19457 (cite v2).[^gepa] Security:
OWASP, "LLM07:2025 System Prompt Leakage."[^owasp-llm07] GitHub Security Advisory
GHSA-6qv9-48xg-fc7f / CVE-2025-65106 (`langchain-core` template injection, including its later
Jinja2-hardening revert).[^cve-template] Gulli, A. and Nawalgaria, A., *Building AI Agents: From
Design Patterns to Production*, public draft manuscript (foreword dated August 2026), ch. 2
"Prompt Architecture," for the four-layer decomposition, attributed and reordered.[^gulli-ch2]

> **Verify before quoting:** Anthropic's and OpenAI's per-model minimum cacheable prompt length and
> breakpoint support change with every model release; cite the live docs page, never a frozen
> table (verified against both vendors' current docs as of this sweep, 2026-09). OpenAI's and
> Anthropic's specific prompt-caching discount percentages and TTL pricing move; cite the finding
> (automatic prefix caching exists, ordering and thresholds are model-specific), not a frozen
> number. The Gulli & Nawalgaria manuscript is a public draft with no confirmed final publisher or
> year found by this sweep; re-check the front matter and chapter numbering against the live draft
> immediately before the chapter ships, and do not assert a publication year this sweep could not
> verify. The Model Spec is an intended-behavior document, not a verified account of current model
> behavior; quote its own caveat rather than imply the hierarchy is guaranteed in production.

## Second-reviewer pass (Codex, 2026-09-05)

Every finding below was checked against a primary source before being accepted, partially
accepted, or declined; none was applied on the reviewer's word alone.

1. **ACCEPTED.** 1.5's own text already owns runtime content selection, quantity, and assembly;
   redrew the seam so 4.1 owns only the template's layers, insertion points, and each slot's data
   contract, and re-checked every must-cover item for the same leak.
2. **ACCEPTED.** Verified Anthropic's current prompting-best-practices doc verbatim (sequential
   steps "when the order or completeness of steps matters"; XML tags to separate "instructions,
   context, examples, and variable inputs"); added a composition-discipline item and folded persona
   and few-shot into it as one paragraph.
3. **ACCEPTED.** Verified Vertex AI's Prompt resource bundles model name, contents, variables,
   generation config, system instruction, and safety settings, with named list/restore-version
   operations; extended the lifecycle item with version identity, traceability, and promotion.
4. **ACCEPTED.** Refetched the cited article directly: it demonstrates test-case generation,
   side-by-side version comparison, and grading, but not a "Get Code" deployment gate or a
   standalone saved-prompt-library feature; narrowed the anchor to what is actually shown.
5. **ACCEPTED.** Fetched the manuscript's own front matter: the authors are Antonio Gulli and Anant
   Nawalgaria (not "K. Nawalgaria"); found no primary confirmation of a 2027 Springer date, so this
   map cites a dated public draft manuscript instead of asserting a publisher year; removed all
   editorial-process fingerprints from the map body.
6. **ACCEPTED.** Removed automatic prompt optimization from Must-cover; it is now one sentence
   under Mention-and-link pointing to 9.7, with the benchmark statistic dropped.
7. **ACCEPTED.** Reduced the item to the single composition rule "prompts are not secret stores"
   with the OWASP LLM07 citation and a link to 4.6; removed the leak catalog from both Must-cover
   and Incidents, since neither example met the primary-citation bar.
8. **ACCEPTED.** Refetched the advisory directly: f-string is the described vulnerability;
   Mustache and Jinja2 received hardening, not confirmed-exploit fixes; the Jinja2 hardening was
   reverted in 1.1.3. Rewrote the templating item and the Incidents entry to match exactly, and
   moved untrusted-template exploitation to the 4.6 pointer.
9. **ACCEPTED.** Refetched OpenAI's current prompt-caching docs: minimums and explicit-breakpoint
   support now differ by model generation (GPT-5.6+ vs. GPT-5.5 and earlier); rewrote the claim as
   model-specific and volatile.
10. **ACCEPTED.** Split the maturity call: caching mechanics Established (though the specific
    thresholds are volatile); the compliance-placement/output-contract-ordering heuristic
    downgraded to model-specific/Emerging, not asserted as a provider-independent rule.
11. **ACCEPTED.** Refetched the Model Spec directly and confirmed its own production-alignment
    caveat verbatim; reframed the chain of command as OpenAI-specific and downgraded cross-provider
    parity to Emerging/unconfirmed, since no equivalent explicit spec was found for Anthropic or
    Google.
12. **ACCEPTED.** Min et al.'s own result is scoped to classification and multiple-choice tasks
    across the 12 tested models; narrowed the claim in the map to that task class rather than
    generalizing it to what examples "teach" broadly.
13. **ACCEPTED.** Split the verdict: version control, review, and rollback are Standard general
    engineering practice; prompt-specific golden-set regression is Established or Emerging
    depending on evidence, explicitly deferred to the author's production-grounding ruling.
14. **PARTIAL.** Confirmed the paper's own abstract names the algorithm "MIPRO," not "MIPROv2,"
    and the citation now says so — but DSPy's shipped library genuinely ships the class as
    `MIPROv2`, so both names are accurate for their own referent (the paper vs. the library) rather
    than one being simply wrong; deleted the "nobody runs it inline in production" absolute either
    way, and the whole item is now one sentence in Mention-and-link, not a must-cover claim.
15. **ACCEPTED.** Kept the original thesis, replaced "exactly like the code it is" with a
    qualified "manage the result like code... tested against representative cases (behavioral
    tests, not compiler checks)," and added the reviewer's thesis as a third listed alternative.
16. **ACCEPTED.** Split Aliases into true synonyms (adding prompt management and prompt lifecycle
    management, both verified as the vendor-ecosystem's own terms) and a new "Related, not
    synonyms" list for persona prompting, few-shot, chain of command, four-layer prompt, automatic
    prompt optimization, and spec engineering, each with its source.
17. **PARTIAL.** Dropped the unverifiable "nearly every reader" claim and verified and added
    Codex's layered `AGENTS.md`/`AGENTS.override.md` convention as the contrasting public anchor;
    kept the underlying Claude Code `CLAUDE.md`-not-`AGENTS.md` claim, since it was already
    correctly cited and re-verified against the same primary source.
18. **ACCEPTED.** Verified the full title ("...or: How I Learned to Start Worrying About Prompt
    Formatting") and the ICLR 2024 venue directly on the paper's own arXiv page; fixed the
    bibliography entry.
19. **ACCEPTED.** Cut Must-cover to six items and reduced the ecosystem mention to one category
    plus at most two exemplars, dropping the seven-vendor list.
20. **ACCEPTED.** Confirmed step 8 ("brand-voice polish") is the carrier bible's correct step
    number with no error; relabeled the regression-and-rollback scene itself as a proposed,
    reasoned/companion-repo illustration pending the author's confirmation of any production scope,
    and kept the candidate From-production scope checklist as an open question below.

## Orchestrator rulings (Stage 1.6, 2026-09-07)

1. **Thesis: the second reviewer's framing, adopted with one softening.** *A production prompt is a
   versioned interface between code and a stochastic model: separate the stable instructions from
   the variable data, and ship each change only with representative evaluations, traceable
   configuration, and a version you can roll back to.* The original "exactly like code" is
   overclaimed — prompts are coupled to a stochastic model and are checked by behavioral tests, not
   by a compiler — and the chapter says so in as many words.
2. **Budget row: standard pattern (~2,000-2,800 prose words)** under the three constraints the map
   sets: automatic prompt optimization is one sentence pointing at 9.7; persona and few-shot are
   argued inside item 1 rather than as sections; the ecosystem mention names one category and at
   most two exemplars.
3. **Ecosystem scope: one vendor-native example and one open-source example.** The longer vendor
   list an earlier draft carried is cut.
4. **"Spec engineering" stays, in the "Related, not synonyms" list, as one clause.** It is a real,
   sourced practitioner term and readers will arrive carrying it; naming it and drawing the line
   (a spec governs one task, this chapter's template governs standing behavior) costs a sentence
   and prevents a category error. It does not open 9.6's territory at one clause.
5. **Google's Prompt resource is cited only for the fields this sweep directly verified** — model,
   contents, variables, generation config, system instruction, safety settings. Tool-definition
   bundling is not claimed, because it was not confirmed.

## Author-only questions (Stage 1.6 — shipped at the default, author rules at the PR)

1. **The lens line's grounding claim.** The stub asserts a blanket `Grounding: production`. That is
   too broad: items 1-4 and 6 are vendor-doc and research grounded. Only the lifecycle half has a
   plausible first-hand claim, and **only the author knows whether it holds.** Candidate clauses,
   none assumed true: prompts lived in the same repository as the code that called them; prompt
   changes went through the same PR review as any other change; a prompt changed in the same commit
   as the code consuming it; template variables were rendered by application code rather than
   hand-edited per environment.
   - *Default shipped:* **no production claim anywhere in the chapter.** The lens line reads
     `Grounding: vendor docs + research`, the lifecycle discipline is argued from 12-Factor Agents
     and Vertex AI's documented pattern, and item 5's maturity ships at the lower of its two
     candidate tiers. Confirm any clause above and both the callout and the tier can rise.
2. **The step-8 lifecycle scene** (a brand-voice prompt change that regressed output, caught by a
   golden set, rolled back). The step number checks out against the carrier bible; the event does
   not, because nothing says it happened.
   - *Default shipped:* **labelled a reasoned illustration**, not carrier fact and not production
     history.
3. **Named idea.**
   - *Default shipped:* **none.** "Prompts are source code" is an existing practitioner phrase, not
     this chapter's coinage, and the map recommends no forced replacement.

[^anthropic-pe]: Anthropic, "Prompting best practices" (prompt engineering documentation, verified
2026-09). "Claude responds well to clear, explicit instructions. Being specific about your desired
output can help enhance results." "Provide instructions as sequential steps using numbered lists or
bullet points when the order or completeness of steps matters." "XML tags help Claude parse complex
prompts unambiguously, especially when your prompt mixes instructions, context, examples, and
variable inputs. Wrapping each type of content in its own tag... reduces misinterpretation."
<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>
[^anthropic-cache]: Anthropic, "Prompt caching" documentation. Up to 4 cache breakpoints per
request; minimum cacheable length varies by model family (roughly 512-4,096 tokens as of this
sweep, 2026-09); default 5-minute TTL, refreshed on each cache hit, with an optional 1-hour TTL at
additional cost. <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>
[^anthropic-longctx]: Anthropic, "Long context prompting tips." For prompts with long (~20k+ token)
documents: place documents near the top of the prompt; place instructions and the query after the
document, which measurably improves compliance and response quality.
<https://docs.anthropic.com/en/docs/long-context-window-tips>
[^anthropic-console]: Anthropic, "Evaluate prompts in the developer console." Manually add or
import test cases from a CSV, or auto-generate them; compare the outputs of two or more prompts
side by side; have subject matter experts grade response quality on a 5-point scale. Does not, on
its own, establish a formal saved-version library or a one-click deployment gate; cited only for
the test-generation, comparison, and grading workflow it demonstrates.
<https://claude.com/blog/evaluate-prompts>
[^openai-cache]: OpenAI, "Prompt caching" API guide (verified 2026-09). Minimums and breakpoint
support differ by model generation: models from GPT-5.6 onward use a roughly 1,024-visible-token
minimum and support explicit cache breakpoints; GPT-5.5 and earlier models generally require
roughly 2,048 tokens, place breakpoints implicitly at regular intervals, and do not support
explicit breakpoints. Cite the live doc; these thresholds move with each model generation.
<https://developers.openai.com/api/docs/guides/prompt-caching>
[^openai-gpt41]: OpenAI, "GPT-4.1 Prompting Guide." Instructions placed at both the start and end
of a long context outperform placing them once; if placed once, above the content beats below.
<https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide>
[^openai-modelspec]: OpenAI, Model Spec, "Chain of Command" and Overview (2026-08-18 revision
verified). Authority levels Root > System > Developer > User > Guideline; higher-authority
instructions override lower ones, with no precedence given to recency or tone across levels. The
document's own caveat, from its Overview: "Our production models do not yet fully reflect the
Model Spec, but we are continually refining and updating our systems to bring them into closer
alignment with these guidelines." <https://model-spec.openai.com/2026-08-18.html>
[^vertex-promptmgmt]: Google, Vertex AI "Prompt management" documentation and the "Create and use a
Vertex AI Prompt" SDK sample (verified 2026-09). A saved prompt version bundles the model name,
prompt contents, variables, generation configuration, system instruction, and safety settings as
one unit via `create_version`/`get_version`; the documentation set separately names "List available
prompt versions" and "Restore a version of a prompt" as supported operations. Tool-definition
bundling was not independently confirmed by this sweep (see Open Questions).
<https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/prompt-classes>;
<https://docs.cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-prompt-template-create-generate-save>
[^12factor2]: HumanLayer, "12-Factor Agents" (2025). Factor 2, "Own your prompts": treat prompts
as first-class, explicitly defined, tested, and versioned code rather than a framework's hidden
default. Factor 3, "Own your context window": the context window (prompts, instructions,
history, tool calls, memory) is the primary interface to the model and worth controlling
directly. <https://github.com/humanlayer/12-factor-agents>
[^zheng-persona]: Zheng, M., Pei, J., Logeswaran, L., Lee, M., Jurgens, D., "When 'A Helpful
Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large
Language Models," Findings of EMNLP 2024, pp. 15126-15154. 162 personas, 4 model families, 2,410
factual questions; personas in system prompts do not improve factual-task performance.
<https://arxiv.org/abs/2311.10054>
[^kong-roleplay]: Kong, A. et al., "Better Zero-Shot Reasoning with Role-Play Prompting," NAACL
2024. Role-play prompting improves zero-shot reasoning-benchmark accuracy (e.g. AQuA 53.5% →
63.8% on ChatGPT); the honest counter-evidence to Zheng et al.'s factual-task finding, on a
different task class (reasoning, not factual recall). <https://arxiv.org/abs/2308.07702>
[^brown-fewshot]: Brown, T. et al., "Language Models are Few-Shot Learners," NeurIPS 2020. The
founding demonstration of in-context few-shot learning as a model capability.
<https://arxiv.org/abs/2005.14165>
[^min-demos]: Min, S. et al., "Rethinking the Role of Demonstrations: What Makes In-Context
Learning Work?" EMNLP 2022. On classification and multiple-choice tasks specifically, across the 12
models tested, randomly relabeled few-shot demonstrations barely hurt performance; what matters on
those tasks is the label space, input distribution, and format the examples establish, not label
correctness. Do not generalize beyond that task class. <https://arxiv.org/abs/2202.12837>
[^sclar-format]: Sclar, M., Choi, Y., Tsvetkov, Y., Suhr, A., "Quantifying Language Models'
Sensitivity to Spurious Features in Prompt Design, or: How I Learned to Start Worrying About
Prompt Formatting," ICLR 2024. Meaning-preserving formatting changes swing task accuracy by up to
76 points (LLaMA-2-13B); the FORMATSPREAD metric. <https://arxiv.org/abs/2310.11324>
[^dspy]: Khattab, O. et al., "DSPy: Compiling Declarative Language Model Calls into Self-Improving
Pipelines," 2023. A framework and compiler that optimizes prompts and few-shot demonstrations
against a metric rather than by hand. <https://arxiv.org/abs/2310.03714>
[^miprov2]: Opsahl-Ong, K. et al., "Optimizing Instructions and Demonstrations for Multi-Stage
Language Model Programs," 2024. The paper's own abstract introduces the algorithm as "MIPRO";
DSPy's shipped library implements it as the `MIPROv2` optimizer class. Cite the paper for "MIPRO,"
the library docs for "MIPROv2." <https://arxiv.org/abs/2406.11695>
[^opro]: Yang, C. et al., "Large Language Models as Optimizers" (OPRO), 2023. An LLM iteratively
proposes and scores candidate prompts against a task metric; reported gains up to 8% on GSM8K and
up to 50% on Big-Bench Hard over human-designed prompts. <https://arxiv.org/abs/2309.03409>
[^gepa]: Agrawal, L. et al., "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement
Learning," ICLR 2026 Oral. Natural-language reflection over sampled trajectories evolves prompts.
Cite v2 of the preprint; any specific benchmark percentage belongs to 9.7, not this chapter's
one-sentence pointer. <https://arxiv.org/abs/2507.19457>
[^cc-memory]: Anthropic, Claude Code documentation, "How Claude remembers your project" (memory
docs, verified 2026-09). States plainly that Claude Code reads `CLAUDE.md`, not `AGENTS.md`; the
supported bridge is a `@AGENTS.md` import inside `CLAUDE.md`, or a symlink.
<https://code.claude.com/docs/en/memory>
[^codex-agentsmd]: OpenAI, Codex `AGENTS.md` configuration documentation (verified 2026-09). Codex
discovers `AGENTS.override.md` (checked first) and `AGENTS.md` at a global scope and at each
directory level from the project root down to the working directory, then concatenates files
root-to-leaf, so files closer to the working directory override earlier guidance by appearing
later in the combined prompt. <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
[^owasp-llm07]: OWASP, "LLM07:2025 System Prompt Leakage," Top 10 for LLM Applications 2025.
Hidden system instructions are not a secure container for secrets or business logic; once leaked
they can be reverse-engineered or abused.
<https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/>
[^cve-template]: GitHub Security Advisory GHSA-6qv9-48xg-fc7f / CVE-2025-65106 (published
2025-11-19). Describes `langchain-core`'s f-string template implementation as the vulnerability
(unrestricted attribute-access syntax such as `{obj.attr}`, `{obj[0]}`; fixed by requiring valid
Python identifiers only); describes the accompanying Mustache and Jinja2 changes as defensive
hardening rather than fixes for a confirmed exploit in those formats. The Jinja2 hardening was
later reverted in `langchain-core` 1.1.3 because it "significantly limited legitimate Jinja2 usage
and broke existing templates," with the advisory noting Jinja2 is intended for trusted template
sources only. Patched versions for the original fix: `langchain-core` 1.0.7 (1.0.x line) and 0.3.80
(0.3.x line). CVSS 8.3; risk is highest for applications accepting untrusted template *structure*,
not merely untrusted variable values.
<https://github.com/langchain-ai/langchain/security/advisories/GHSA-6qv9-48xg-fc7f>
[^gulli-ch2]: Gulli, A. and Nawalgaria, A., *Building AI Agents: From Design Patterns to
Production*, public draft manuscript (foreword dated August 2026), ch. 2, "Prompt Architecture."
Author names verified directly against the manuscript's own front matter (Antonio Gulli and Anant
Nawalgaria); no confirmed final publisher or year was found by this sweep, so this map cites the
dated public draft rather than asserting a publication year. The four-layer decomposition
(Identity / Instructions / Context Injection / Output Constraints) is the manuscript's own
organizing structure for this material; attributed and reordered here by cache stability rather
than reproduced as given. Public manuscript export:
<https://docs.google.com/document/d/1keM4ZbbfVmdsq3EAkbAliIegOpnnuBf-_KpD4oDOF0o/export?format=txt>
