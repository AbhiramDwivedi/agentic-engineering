# Coverage map: Computer Use & Browser Agents (chapter 9.5)

> Research-derived spec for what the chapter must cover. Angles run: vendor docs (Anthropic, OpenAI,
> Google), academic and benchmarks, security and incidents, daily-tool (Playwright MCP, Claude for
> Chrome), skeptical read, alias sweep. Skipped: StackOverflow and SDK-issue mining (no primary
> source opened; the Gotchas below come from vendor docs). Review and trim **Must-cover**.
> Bar: definitive but tight. Budget: standard-pattern chapter.

## Thesis

In a computer-use agent the model chooses each next UI action from what it observes, and your code owns everything else: what it observes, how an action is executed, and what proves the end state. Prefer structured controls where the page has them; pixels buy reach on software with no other door, at the price of targeting failures and an untrusted screen. (Hypothesis to support or narrow in drafting.)

## The mental model (what the reader must leave with)

Litmus line: it is agentic when the model chooses the next UI action from observations; a scripted browser sequence is automation you already know. Mechanically this is the ordinary tool-request, execute, tool-result loop (2.1, inner loop 2.5), not a new control structure. What is new is the observation (a screenshot, an accessibility snapshot, or both) and the grounding step from "what I see" to "what I act on." The model never touches the machine; the harness (2.6) executes, observes again, and owns step caps, logging and the verify-and-retry outer loop (3.7). Open the chapter on one concrete failed interaction, not on the definition.

## Must-cover

1. **The observation-to-action contract.** Three vendors ship the same shape (Anthropic computer and browser tools, OpenAI computer tool, Gemini `computer_use`). Teach: observation freshness (re-observe after navigation or a material DOM change), coordinate transforms when the screenshot is scaled, and re-observation after a targeting failure. **Established.**
2. **Perception and addressing are not exclusive: hybrid.** Pixels reach anything with a screen (desktop apps, canvases, remote desktops). Structured access (accessibility tree, element references) is cheaper and more deterministic but needs a DOM. Anthropic's browser tool combines both: references are scoped to the tab that produced them, stay valid only until that tab navigates or its DOM changes materially, and the API cannot detect a stale one, so the executor must return an error. Playwright MCP defaults to snapshots and offers coordinate tools opt-in via `--caps=vision`; that enables tools, it is not an automatic fallback. SeeAct finds grounding the main obstacle (arXiv:2401.01614). **Established** (both exist); the choice is engineering.
3. **Transport is not access.** MCP can carry an API, DOM operations or pixel actions, so "API, then MCP, then DOM, then pixels" is not a ladder of transports. Separate the interaction surface (API, structured page, pixels) from the transport (direct tool, MCP). "Prefer the API when one exists" is an editorial recommendation, labeled as such, not a measured law of reliability, latency and cost. Links to 2.1, 2.4. **Standard** as engineering judgment.
4. **Ordered action batches.** Some interfaces return several actions per turn. Anthropic's contract: run blocks in order, stop at the first failure, answer every `tool_use` (skipped ones with an `is_error` "Not executed" result, or the request is rejected), and if you gate on human confirmation, check before each block. OpenAI also returns ordered arrays. Replace "screenshot after every step" with observation after a bounded batch where the interface allows. **Established.**
5. **Benchmark calibration.** OSWorld launched with humans above 72% and the best model at 12.24% (arXiv:2404.07972); WebArena best GPT-4 agent 14.41% against 78.24% (arXiv:2307.13854); vendors report large gains. Current lead evidence: OSWorld 2.0 (arXiv:2606.29537, 2026), long-horizon tasks where agents fail on hidden state, lost constraints, guessing instead of clarifying, and skipping verification, alongside wrong clicks and pop-ups (links 9.1). Keep three things apart: protocol sensitivity (Emergence WebVoyager re-evaluates Operator at 68.6% against 87% reported, but changes evaluation rules, arXiv:2603.29020), evaluator error (an audit finds 15.3% of FAIL verdicts wrong, so reported scores can be too low, arXiv:2607.28367; WebArena Verified), and demonstrated task failure. Teach the questions: who ran it, which version, step budget, how success is judged. Never freeze a score; link live. Own-flow evaluation (end state, repeat runs, trajectories) is a pointer to 4.2. **Contested** (reliability claims only).
6. **Prompt injection, here only the browser surface.** Threat is **Established**. Brave's Comet disclosure (2025-08-20) is the public incident: hidden text in a Reddit comment led toward reading a one-time password from a logged-in mailbox. Anthropic reports browser attack success of 23.6% without mitigations and 11.2% with, with measured improvements and stated residual risk (2025-08-25; 2025-11-24); OpenAI says it is "unlikely to ever be fully solved" (2025-12-22). Treat all page-supplied text (hidden fields, URLs, tab titles, download URLs) as untrusted: a conservative trust rule, not a literal claim. Mitigations are **Emerging**; claims of solved injection are **Contested**. Full treatment in 4.6.
7. **Three boundaries, kept distinct: host isolation, session authority, network enforcement.** A VM or container isolates the host; a fresh profile does not by itself establish that. Session authority is what the logged-in browser can do if hijacked. Allowlists are not enforcement: Playwright MCP says its origin filters are "not a security boundary" and do not affect redirects. The chapter must decide whether the example runs credential-free or with a deliberately scoped authenticated session. Isolation depth to 9.4, identity depth to 8.5. **Standard** (isolation, least privilege).
8. **Confirmation and its failure path.** Vendors bake in prompts (Gemini `require_confirmation`, which the client must satisfy and acknowledge; OpenAI pending safety checks; Claude for Chrome confirmations), but a classifier is not a guarantee it catches every consequential action. The application owns authorization, must handle denied or unavailable confirmation, and must support human takeover. Provider handshakes here; the general approval pattern in 4.3. **Established.**
9. **Completion contracts: a click is not proof.** A download is asynchronous (started, completed, failed, correlated by an id); a successful click does not mean the price sheet landed. Verify the completed artifact before ingestion, report failures back, and sanitize reported URLs, which can carry credentials. Parsing in 6.1. "Task complete" from the model is not proof of the end state. **Established.**
10. **Failure modes and harness fixes.** Timing and pop-ups, scroll/drag/zoom fragility (Anthropic's own 2024 caveat), small text (zoom), wrong-element clicks, loops. Keyboard shortcuts over dropdowns, consistent environment, step/time/cost limits, failures returned as structured errors, not crashes. **Established.**
11. **Cost and context, two kinds.** Screenshots cost on the order of a thousand tokens or more and vendors cap images per request; accessibility trees and tool schemas are verbose too (the Playwright README says CLI invocations avoid "large tool schemas and verbose accessibility trees"). Teach minimal relevant observations and count both token and attention cost. General compaction to 5.4, cost to 8.4. Pruning screenshots does not establish reliable long-horizon operation. **Established** (the cost); long-horizon desktop operation **Emerging**.

## Mention-and-link

- Tool calling, results as untrusted, inner loop → 2.1, 2.5. MCP and Playwright-as-server → 2.4.
- Execution limits and permissions → 2.6. Outcome verification and retry → 3.7.
- Sandboxing depth → 9.4. Injection and the trifecta → 4.6. Human gates → 4.3. Guardrails → 4.4. Eval method → 4.2.
- Reading screenshots and documents as input → 6.1. Coding agents that use a browser → 9.6.
- Long runs → 9.1. Compaction → 5.4. Cost → 8.4. Identity → 8.5.

## Out of scope

- General browser-automation test suites (Playwright/Selenium docs); GUI-grounding model training; RPA vendor comparisons.
- Consumer agentic-browser product reviews beyond public security findings; mobile agents beyond one line.

## Maturity summary

- **Standard:** isolation and least privilege for any screen-driving agent; treat screen content as untrusted; confirm consequential actions.
- **Established:** the observation/action loop as a shipped capability from every major lab; scoped structured browsing via accessibility snapshots; step-level verification and logging.
- **Emerging:** general autonomous desktop operation and long-horizon reliability; injection defenses; independent evaluation method.
- **Contested:** vendor-reported versus independent reliability on real tasks; any claim that injection is solved or that unrestricted autonomy is safe.

Verdict: **Established** (the capability and scoped structured browsing) with **Emerging** for general desktop autonomy; **Contested** is reserved for unsupported reliability and safety guarantees. Last reviewed applies.

## Aliases

Computer use (Anthropic); Computer-Using Agent / CUA (OpenAI); browser agents; web agents; GUI agents (research term; OSWorld, SeeAct); screen-driving (descriptive). Product examples, not aliases: Operator, Atlas, Comet, Claude for Chrome. No public attribution of a grouping in the Gulli books was verified at section level (the public chapter 12 record confirms only its title), so none is claimed; the alias sweep against both books is not complete.

## Reader-verifiable anchors

- Playwright MCP README: accessibility-snapshot default, opt-in coordinate tools via `--caps=vision`.
- Anthropic computer-use docs: action set, batch-action rules, isolation and confirmation warnings; browser-use docs: references, downloads.

## Incidents

- Brave, Perplexity Comet indirect injection (2025-08-20): hidden spoiler-tag text in a Reddit comment, triggered by "summarize this page." Maps to: separating user instructions from page content, action-alignment check, confirmation, isolated profile.
- No public production postmortem of an agent mis-acting on a customer's behalf found.

## Carrier

The bible has no browser scenario yet; this grows it first. Proposed: the **Repricer** (the bible's sibling surface) reaches a supplier's merchant portal that exists only as a web admin, to download the nightly price sheet. Prefer the supplier feed; screen-drive only as fallback, in isolation, with a confirm gate on any write, and verify the downloaded file before ingestion. No firsthand-deployment claim.

## Named-idea candidates

- **The access ladder** (API, structured page, pixels): editorial, descriptive, for the author to accept; three rungs on the surface axis, with transport separate.

## Open questions for the author

1. Credential-free example or a deliberately scoped authenticated session for the portal?
2. Accept the thesis as stated, or narrow it (it is a hypothesis)?
3. Settle the Repricer browser scenario in the carrier bible before drafting?
4. Accept "access ladder" as a named idea, or leave as prose?
5. Scope: keep OSWorld 2.0 failure classes here, or defer to 9.1?

> **Verify before quoting:** every benchmark number, attack rate and model or tool name rots; cite the finding and the live source. The WebArena Verified claims are from an abstract only. The OSWorld 2.0 page gives no explicit date; confirm against arXiv:2606.29537. Re-check all three 2026 arXiv IDs before shipping.

## Map review (Stage 1.5)

Second-engine review. Verified against Anthropic computer-use and browser-use docs, arXiv abstracts, OSWorld 2.0 and the Playwright README.

1. Litmus/organizing distinction missing: accepted; thesis and mental model rewritten, loop reframed as ordinary tool loop.
2. Process-only section: accepted; removed.
3. Grounding contract: accepted; item 1 and 2 (reference scope and staleness verified in browser-use docs).
4. Ordered batches: accepted; item 4 (verified: in order, stop at first failure, every block answered, confirm before each block is conditional).
5. Authentication and boundaries: accepted; item 7 (README "not a security boundary", ignores redirects, verified).
6. Confirmation failure path: accepted-modified; item 8 (Gemini handshake not re-opened this pass, kept as written).
7. Download completion contract: accepted; item 9 (download events and URL sanitizing verified).
8. Transport versus access mechanism: accepted; item 3.
9. Skeptical evidence over-read: accepted; item 5 (Emergence changes protocol; audit covers false failures only, both verified).
10. Stale benchmark baseline: accepted-modified; OSWorld 2.0 added (arXiv:2606.29537; page date unconfirmed, flagged).
11. Threat/mitigation/guarantee conflated: accepted; item 6 and maturity summary.
12. Seam duplication: accepted; evaluation merged into item 5, pointers to 2.6, 3.7, 4.2 added.
13. Thesis and budget: accepted-modified; thesis framed as hypothesis, standard-pattern budget noted, opening scene specified.
14. Context costs and maturity: accepted; item 11 and verdict (README CLI-versus-schema claim verified).
15. Aliases and anchors: accepted; products split from aliases, unsupported term dropped, `--caps=vision` described as opt-in.
16. Gulli attribution: accepted; attribution dropped, sweep marked incomplete.
17. Carrier and sign-off: accepted; Repricer named, open questions listed.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Code seam:** none, so no listing-studio package. Short illustrative fragments in the prose are fine.
2. **Maturity:** follows the map's split.
   - The capability and scoped structured browsing are Established.
   - General desktop autonomy, injection defenses and evaluation method are Emerging.
   - Unsupported reliability or safety guarantees are Contested.
   - Last reviewed 2026-11.
3. **Examples are credential-free.** No authenticated session is shown.
4. **Carrier:** the Repricer fetches a supplier price sheet through a browser, described generically. The carrier bible is not edited, and adding the scenario there goes on the checklist.
5. **"Access ladder":** not a coinage. Describe the ordering in plain words (API, then structured browser, then pixels) without naming it.
6. **OSWorld 2.0:** keep its failure classes brief here. Do not state a release date.
7. **Gemini confirmation handshake:** the writer verifies it against the primary page or cuts it.
8. **Excluded:** no From-production callout and no aliases.


## Reconcile log (Stage 5)

Prose review (PC), fact check (FC), cold read (CR) and the second-engine map review (SE). Every finding was checked against the chapter and, for facts, the cited source.

- PC1 length: fixed. The 87% now appears once, in the protocol paragraph. The one-site-to-several paragraph is cut and the allowlist moved into Network enforcement. The Loops gotcha is cut because it duplicated the fail-into-the-loop contract. 2,793 argued words against the 2,800 ceiling.
- PC2 maturity disagreement: fixed. The body verdict and the meta line now list the same Emerging items: general desktop autonomy, injection defences, evaluation method.
- PC3 apparatus narration: fixed. The anti-pattern gotcha states the problem and its reason, and the "mitigations are Emerging" label sentence is deleted, since the paragraph already says neither vendor claims a complete defence.
- PC4 "three questions": fixed. They are now listed as first, second, third: protocol, evaluator, agent.
- PC5 carrier (supplier price sheets): kept as written. The author decides, and it is on the PR checklist.
- PC6 imagined model speech: fixed. *"done."* and *"click the export button"* are in italics, and the quotes around "what I see / what I act on" are dropped.
- PC7 rhetorical Q&A and the double "So": fixed. L11 is a plain claim.
- PC8 performed short pair: fixed. Joined into one sentence, with Playwright MCP split into its own paragraph.
- PC9 "common shape" in the hook: fixed. It now says agents fail this way because..., and the quote carries the rest.
- PC10 "removes that class": softened to "removes most of".
- PC11 the 87% seems attached to [^9]: fixed by wording. The sentence attributes the figure as reported in the re-evaluation, which states it.
- PC12 run-on list: fixed. Split before "They fail most".
- PC13 soft linter flags: rejected, as the critic advised. They introduce content.
- FC [^13]/[^14] titles: fixed. "Piloting Claude in Chrome" and "Mitigating prompt injections in browser use".
- FC `pending_safety_checks` literal: fixed. Now plain "pending safety checks" in the prose and in [^4], because the source does not use the field name.
- FC Gemini `blocked` decision: rejected. It is optional, and there is no budget for it.
- FC OSWorld 2.0 leaderboard numbers: rejected. They are optional, and live numbers would date the page; the chapter points to the live leaderboard instead.
- CR accessibility snapshot undefined at L27: fixed. Glossed at first use.
- CR Playwright never introduced: fixed. Playwright and Playwright MCP are each glossed at first use.
- CR MCP as transport: fixed. One clause says what a transport carries.
- CR benchmark names: fixed. OSWorld, WebArena and WebVoyager are each glossed from their sources.
- CR step budget and trajectory: fixed. Both glossed inline.
- CR allowlist and the redirect re-check: fixed. Both defined in Network enforcement.
- CR `is_error`: fixed. Named as a flag on a tool result.
- CR signed query-string credentials: fixed. Glossed as a temporary access token in the URL.
- CR outer loop and harness, linked only: fixed. Each has a one-clause gloss. The agent loop is left to its link because the sentence already says it is the tool cycle.
- CR why the benchmarks support Established: fixed. The verdict sentence now says Established covers shipped engineering and not reliability, and that the scores are the evidence for the Emerging tier.
- CR 12% to 87% jump: fixed. The two figures come from different benchmarks, and the second used the vendor's own protocol. No causal story is added beyond what the sources state.
- CR batch-confirmation risk: fixed. A per-turn gate can see a form only after the batch has filled and submitted it.
- CR fresh profile, reason missing: fixed. A profile is not a process or filesystem boundary.
- CR "easier to attack" bare in the gotcha: fixed. The reason is given (every page read can carry injected instructions).
- CR the flag-versus-fallback sentence: fixed with PC8.
- CR no code listing, so not buildable alone: rejected. The no-code-seam ruling 1 stands, and the vendor docs are linked.
- CR lethal trifecta undefined: rejected. It is a link title to the chapter that defines it.
- CR SVG picture-alone test: rejected for this stage. The diagram passed the diagram gate at Stage 3.5, and the alt text matches the paragraph.
- CR vendor field names without context: rejected. Each is tied to its vendor and footnoted. Glossing every field would thin nothing but cost words the budget does not have.
- SE 1 to 17 (map stage): checked against the draft. All dispositions still hold. The litmus line, grounding contract, ordered batches, three boundaries, confirmation failure path, download events, transport-versus-surface split, the protocol-versus-evaluator split, OSWorld 2.0 failure classes, context costs, product names kept separate from aliases, and the dropped attribution are all present in the chapter. No new finding.
