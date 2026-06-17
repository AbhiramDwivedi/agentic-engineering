# Coverage map: Workflow or Agent? (chapter 1.3)

> Research-derived spec for the reference's **autonomy / spectrum chapter** — *where a system
> sits between predefined code paths and model-directed control, and the honest truth that most
> production value today is on the workflow end.* This is a **framing chapter, not a technique
> chapter**: it inherits the autonomy/spectrum half of the "what is agentic" debate that
> [1.2 Who Decides?](../../docs/foundations/who-decides.md) deliberately handed off (see 1.2's
> "A pattern is not a system"). Built from a 4-angle sweep (primary framing docs; framework
> levels-of-agency taxonomies; practitioner "when to use which" writeups + cost/latency data;
> the skeptical / anti-hype read). Bar: definitive but tight (~5–8 items). **Maturity is
> *split*** — the *guidance* is Standard/Established, the "agents for everything" overclaim is
> Contested — argued in the summary. Review and trim the **Must-cover** list; that sets scope.

## The mental model (what the reader must leave with)

Workflow and agent are not two boxes; they are the two ends of one **spectrum of agency** — how
much control over the program's flow you hand to the model. At one end your code owns every step
(a predefined path the model only fills in); at the other the model decides what to do next, in a
loop, until it judges the goal met. Almost every real system lives somewhere between. The
load-bearing, slightly unfashionable truth: **most production value today sits near the workflow
end**, because predefined paths are cheaper, faster, testable, and reliable, and you should reach
for model-directed control only when the task is open-ended enough that no fixed path can express
it — and only when agency *demonstrably* earns its cost. The author's own working line settles the
definitional noise without joining the fight: *using an agent to do a piece of work is a workflow;
an agent deciding what to do next is agentic.* The chapter's job is to make the spectrum legible
and the "start simplest, add agency deliberately" discipline operational — **not** to relitigate
the definition (1.2 already planted that) and **not** to teach the five workflow patterns
(Part III owns those).

## Must-cover (for a complete, honest framing)

Ranked. Each: why it matters, the failure mode if skipped, the (framing-chapter) maturity stance,
and a lead citation. `[+]` = a gap the stub must fill (the chapter is a stub, so all are `[+]`).

1. **The spectrum itself — predefined paths ↔ model-directed control** `[+]` — the chapter's
   spine. Define the two ends crisply (workflow = "LLMs and tools orchestrated through predefined
   code paths"; agent = "LLMs dynamically direct their own processes and tool usage") and then
   *immediately* dissolve the binary: it is a continuum, not a switch, and "is this an agent?" is
   usually the wrong question — "how much agency does this step need?" is the right one.
   *Skip it:* readers keep arguing a false binary and mis-size systems. **n/a** (framing); the
   *distinction* is **Standard**. (Anthropic, *Building Effective Agents*; deepset, "a spectrum,
   not a binary.")
2. **Agency as degrees — the levels taxonomy** `[+]` — make the spectrum concrete with a named
   ladder so "more/less agency" isn't hand-waving. smolagents' four rungs are the cleanest:
   ☆ none (output doesn't touch flow) · ★ low (LLM picks an if/else branch — a "router") · ★★
   moderate (LLM picks which tool/function runs) · ★★★ high (LLM controls an iterative loop and can
   spawn further agentic work). Note pointedly that "LLM picks a branch" rates only *low* agency —
   this is the bridge back to 1.2's litmus (passing the litmus ≠ a high-agency system).
   *Skip it:* the spectrum stays abstract; the reader can't place their own system on it.
   **n/a** (framing); the levels framing is **Established**. (HF smolagents, *Introduction to
   Agents*; corroborate with Gulli's L0→L3 complexity levels.)
3. **The honest truth: most production value is on the workflow end — and *why*** `[+]` — the
   chapter's thesis and its most useful, least fashionable claim. The four reasons predefined paths
   win for most work: **reliability/reproducibility** (same input → same output; an audit/compliance
   requirement), **cost** (every agent decision is an inference call; ~$0.01–0.50+ each, multiplying
   at volume), **latency** (milliseconds for a fixed path vs. seconds per reasoning hop), and
   **testability/debuggability** (a fixed path takes unit tests; a model-driven loop needs evals —
   forward-link 4.2). *Skip it:* the reference reads as agent-hype like everything else it's meant
   to cure. **Established** (the guidance is well-supported across vendors + practitioners);
   carries a **"Last reviewed"** stamp (cost/latency are moving). (Practitioner: Tensoria/MindStudio
   "when to use which"; deepset; cost/latency figures cited as *finding*, not frozen.)
4. **"Start with the simplest thing; add agency only when it demonstrably helps"** `[+]` — the
   operational discipline that falls out of #3, and the single most-cited piece of vendor guidance
   on this topic. Anthropic states it directly: find the simplest solution, increase complexity
   only when it measurably improves outcomes — *"which might mean not building agentic systems at
   all."* Frame agency as a cost you justify, not a default you assume. *Skip it:* teams reach for
   an autonomous agent where a prompt or a pipeline would do, and pay for it. **Standard**
   (the most broadly-endorsed advice in the space). (Anthropic, *Building Effective Agents*; echoed
   by OpenAI's guide and the 2026 practitioner playbooks.)
5. **When you actually *need* an agent** `[+]` — the other side of #4, stated generously so the
   chapter isn't anti-agent. Reach for model-directed control when the task is **open-ended**
   (the steps can't be enumerated up front), the path is **unpredictable / input-dependent**, the
   work needs **judgment over unstructured input**, or the horizon is long and branchy. Give the
   crisp positive trigger, not just the caution. *Skip it:* the chapter reads as "never use agents,"
   which is dishonest and unhelpful. **Established.** (Anthropic; OpenAI "A Practical Guide to
   Building Agents"; Tensoria/MindStudio decision criteria.)
6. **The author's definition, stated as the resolution — not the fight** `[+]` — carry forward
   1.2's load-bearing move so 1.3 doesn't re-open the war: *agent does the work = workflow; agent
   decides the next step = agentic* (decision/control-based), with **LangChain / Harrison Chase**
   as the like-minded authority ("a system that uses an LLM to decide the control flow"). Name the
   higher-bar camp fairly in one breath (Anthropic/OpenAI autonomy framing; Gulli goal-directed;
   smolagents degrees; Willison's "runs tools in a loop"), then resolve: *the spectrum is real, the
   definition is low-value to litigate, and **the patterns in this reference apply either way.***
   *Skip it:* the chapter either re-fights 1.2's battle or looks naive about the disagreement.
   **n/a** (framing). (LangChain — author's camp; Anthropic/OpenAI/Gulli/smolagents/Willison — the
   spectrum camp; all already sourced in the 1.2 map — **reuse**.)
7. **The hybrid is the real answer (and the refactor-back signal)** `[+]` — the 2026 practitioner
   consensus that closes the chapter honestly: the best production systems are **not** pure-workflow
   or pure-agent but **deterministic boundaries around a bounded-agency step** — keep the fixed
   pipeline, drop a small sub-agent (2–4 tools) into only the step that needs judgment. Pair it with
   the *reverse* signal: refactor an agent **back** to a workflow when its outputs are stable enough
   to write as rules, its cost outruns the value of its autonomy, or you spend more time fixing it
   than it saves. *Skip it:* the chapter leaves a false either/or and misses the most actionable
   guidance. **Established / Emerging** (the hybrid pattern is consolidating fast — **"Last
   reviewed"** stamp). (MindStudio; Tensoria; deepset; the 2026 playbooks.)

> **Anti-sprawl discipline (author directive, honor it):** the definitional fight is *low-value* —
> item 6 is one tight passage, not a section, and the spectrum (1–5) plus the hybrid (7) are the
> chapter's weight. 1.3 carries **more spectrum depth** than 1.2 did, but the same refusal to let
> the *definition* debate sprawl. If trimming to bar, the safe merges: fold #6 into #1's opening,
> or fold #7's refactor-back signal into #3.

## Mention-and-link (one line, a pointer, not a section)

- **The litmus test** (the *classification* lens — model vs. your code decides) → [1.2 Who
  Decides?](../../docs/foundations/who-decides.md). 1.3 is the *spectrum/maturity-of-autonomy* half;
  1.2 is the per-pattern test. Name the seam, don't re-teach it.
- **The five named workflow patterns** — prompt chaining, routing, parallelization,
  orchestrator-workers, evaluator-optimizer — **named at a high level only**; depth is Part III.
  → 3.1 Prompt Chaining, 3.2 Front Controller, 3.3 Orchestrator-Workers, 3.4 Evaluator-Optimizer
  (and 3.5 Specialist Panel). **Do NOT teach them here** (1.1 already promised 1.3 would *name* them).
- **The augmented LLM** — the base unit at the workflow end (model + tools + contract) → 1.4.
- **Build-vs-buy / frameworks** (LangGraph et al. for orchestrating either end) → 1.6 Do You Even
  Need a Framework?
- **Eval vs. unit test** (why the model-driven end needs evals where the fixed path needs unit
  tests) → 4.2 Evaluation.
- **Autonomous agents in depth** (the far ★★★ end, the one real agent loop) → 9.1 Autonomous Agents.
- **The maturity lens** (the orthogonal trust axis) → about/how-we-label.

## Out of scope (name it, point out)

- **Teaching any of the five workflow patterns** — Part III owns each; here they are one line + a
  link.
- **Re-running the litmus or the three-way split table** — that is 1.2's job; cross-link.
- **What an "agent" *is* as a base unit** (LLM + tools + contract) → 1.4 The Augmented LLM.
- **Multi-agent topologies and protocols** → 9.2 Multi-Agent / 9.3 Protocol Landscape.
- **Frozen cost/latency numbers** — cite the *finding* (agent steps cost inference $ and seconds;
  fixed paths cost ms) and a live source; never hardcode a per-call price or a latency figure.
- **The deep how-to of building an autonomous loop** → 9.1.

## Maturity summary (a *split* verdict — argue it, don't assert it)

This chapter carries **two stances, deliberately**, because the topic divides cleanly:

- **The guidance is Standard → Established.** "Workflow and agent are a spectrum," "start with the
  simplest thing and add agency only when it demonstrably helps," and "most production value sits on
  the workflow end" are about as well-supported as advice gets in this field — endorsed across
  Anthropic, OpenAI, framework docs, and 2026 practitioner writeups, and backed by the hard
  economics of cost/latency/testability. Lead with it confidently.
- **"Autonomous agents for everything" is Contested.** The same sources that endorse agents
  *warn against defaulting to them*; the market habit of labelling any LLM app "agentic" is the
  overclaim 1.1/1.2 already flag (Gartner agent-washing). Lead the autonomous-everything read with
  skepticism.
- **The hybrid (bounded agency inside a deterministic shell) is Established/Emerging** — clearly the
  direction of travel, consolidating through 2026, so it carries a **"Last reviewed"** date.

Because cost, latency, and the hybrid consensus all move, the chapter should stamp **"Last reviewed
<date>"** even though its core guidance is durable.

## CODE verdict

**CODE: NO** (framing/spectrum chapter — no companion code required, and the stub's current
"Maturity: Standard" + "research + production" line should be **revised** to reflect the split
above and an optional last-reviewed stamp). Rationale: there is no single runtime shape to diagram
or snippet here — the chapter's payload is the spectrum, the discipline, and the decision criteria,
all of which the *pattern* chapters (Part III) and 9.1 demonstrate in real code. A **shape diagram**
still earns its place: a single Mermaid figure showing the agency spectrum (rectangles at the
workflow end → rounded nodes at the agent end, in the shared visual language), which is prose +
diagram, not companion code. **Optional, only if the author wants it:** a *tiny* illustrative
contrast — the same Listing Studio step done two ways, a fixed `price = lookup(rules)` line vs. a
model-decides-then-code-gates sketch — but 1.1 *already* uses exactly that price-step contrast, so
reusing/cross-linking it is better than re-coding it. Recommend NO new companion code; reuse 1.1's
contrast by reference if an illustration is wanted.

## Open questions for the author

1. **The five workflows — name-only, confirmed?** 1.1's "See also" promises 1.3 covers "the
   spectrum *and* the five named workflow patterns." This map treats the five as **mention-and-link
   (named at a high level, taught in Part III)** to avoid duplicating Part III. Confirm that
   "named, not taught" satisfies the 1.1 promise — or do you want a one-paragraph *map* of the five
   (one line each) as an on-ramp to Part III, which would add one must-cover item?
2. **Where does the ★★★ autonomous end stop in 1.3 vs. 9.1?** 1.3 should *place* high autonomy on
   the spectrum and say "most value isn't here (yet)"; 9.1 Autonomous Agents owns the how-to and the
   one real agent loop. Confirm the seam: 1.3 = "where it sits and when it's worth it," 9.1 = "how
   to build it." Anything more than placement risks duplicating 9.1.
3. **Last-reviewed stamp — yes?** The core guidance is durable but the cost/latency anchors and the
   hybrid consensus are moving. Recommend stamping "Last reviewed <date>." Agree?
4. **Item count.** The must-cover list is **7** (within the ~5–8 bar). If you want it tighter, the
   pre-cleared merges are #6→#1 and #7's refactor-back signal→#3. Your call on scope.

## Sources

Most are already sourced in the 1.2 coverage map — **reuse those citations** (the author's
directive to cite across authorities, not Anthropic alone, applies here too). Verified live June
2026; re-verify URLs/quotes at publish.

*Primary framing docs (reuse from 1.2):*

- **Anthropic, *Building Effective Agents*** (anthropic.com/research/building-effective-agents;
  19 Dec 2024) — the workflow/agent distinction ("predefined code paths" vs. "dynamically direct
  their own processes"); the **"start with the simplest solution… increase complexity only when it
  demonstrably improves outcomes, which might mean not building agentic systems at all"** guidance;
  the cost/latency tradeoff caution; the five named workflow patterns (named here, taught in Part
  III). **The load-bearing citation for items 1, 3, 4, 5.**
- **OpenAI, *A Practical Guide to Building Agents*** (April 2025) — "agents independently accomplish
  tasks"; explicitly *excludes* single-turn LLM apps; corroborates "use an agent only when the task
  needs model-driven control." (Item 5.)
- **LangChain / Harrison Chase, "What is an agent?"** (blog.langchain.com) — "a system that uses an
  LLM to decide the control flow of an application," plus the chains→autonomous-agents spectrum.
  **The author's-camp anchor for item 6.**
- **Hugging Face *smolagents*, *Introduction to Agents*** (huggingface.co/docs/smolagents/
  conceptual_guides/intro_agents; source at github.com/huggingface/smolagents
  …/conceptual_guides/intro_agents.mdx) — **agency as a continuous spectrum**, four levels
  (☆ none · ★ low/router · ★★ moderate/tool-choice · ★★★ high/loop+spawn). **The levels anchor for
  item 2.**
- **Antonio Gulli, *Agentic Design Patterns*** (Springer 2025, ISBN 9783032014016) — goal-directed
  agent definition and **L0 (reasoning engine) → L3 (multi-agent)** complexity levels; corroborates
  the degrees framing independently of HF. (Items 2, 6; verify intro wording against print.)
- **Simon Willison, "…a widely enough agreed upon definition…"** (simonwillison.net/2025/Sep/18/
  agents/) — "an LLM agent runs tools in a loop to achieve a goal" (the *loop* is itself a
  spectrum nuance); 211 definitions / 13 categories. (Item 6, the skeptical-but-settled read.)

*Practitioner "when to use which" + cost/latency (new for 1.3):*

- **deepset, "AI Agents and Deterministic Workflows: A Spectrum, Not a Binary Choice"**
  (deepset.ai/blog/ai-agents-and-deterministic-workflows-a-spectrum) — the explicit
  spectrum-not-binary framing. (Items 1, 7.)
- **Tensoria, "Workflow vs AI Agent: When to Use Which (and When Not To)"** and **MindStudio,
  "Agentic Workflows vs Traditional Automation"** — the five decision criteria (predictability,
  decision complexity, token cost/latency, reliability/debuggability, maintenance); the
  cost/latency figures (~$0.01–0.50+ per agent decision; ms vs. seconds); the **hybrid pattern**
  (bounded sub-agent inside a deterministic shell) and the **refactor-agent-back-to-workflow**
  signals. **Cite as finding, not frozen numbers.** (Items 3, 5, 7.)
- **2026 practitioner playbooks** (e.g. promptengineering.org "Agents at Work: The 2026 Playbook")
  — corroborate "start simplest / reliability-first" as the current consensus. (Items 3, 4.)

*Skeptical / Contested read (reuse from 1.1/1.2):*

- **Gartner, "agent washing" / "over 40% of agentic-AI projects cancelled by 2027"**
  (gartner.com newsroom, 2025-06-25) — the market overclaim that makes "agents for everything"
  Contested. Industry-analyst signal, not a technical authority.

*Internal:* `docs/foundations/who-decides.md` (1.2 — the litmus half; read its "A pattern is not a
system" for the seam), `docs/foundations/its-still-engineering.md` (1.1 — already promises 1.3
covers the spectrum + names the five workflows; reuse its price-step contrast rather than re-coding),
`meta/design-system.md` (maturity tiers; the shared diagram visual language), `SPINE.md` (ch3:
"the spectrum; the honest truth that most production value is on the workflow end").

> **Verify before quoting:** (a) **Anthropic's "simplest solution… which might mean not building
> agentic systems at all"** — the chapter's most-quoted line; confirm exact wording at the live URL
> (Anthropic occasionally re-hosts this essay between /research/ and /engineering/). (b)
> **smolagents' star/levels table** — wording shifts across doc revisions; cite the live
> conceptual-guide URL (and the .mdx source) with an access date. (c) **All cost/latency figures**
> ($/decision, ms vs. seconds) are directional and source-dependent — cite the finding and the live
> source, never a frozen value. (d) **LangChain "decide the control flow"** — attribute to the
> canonical blog post, not a paraphrase. (e) **Gulli's L0→L3 and intro definition** — confirm
> against the print/PDF before quoting.
