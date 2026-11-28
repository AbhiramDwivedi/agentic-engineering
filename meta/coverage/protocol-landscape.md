# Coverage map: The Protocol Landscape (chapter 9.3)

> Research-derived spec for what the chapter must cover so a reader can choose a protocol for
> each connection in an agent system and know how settled it is. Sweep: vendor and primary
> specs, governance announcements, the skeptical read, the alias sweep, the daily-tool angle,
> and one academic security finding. Landscape chapter: prose budget set by the Stage 1.6 ruling below.
> Bar: definitive but tight.

## Thesis

Protocol compatibility cannot establish permission to act: every remote delegation, tool call
or purchase still needs an authority check in your harness, whatever the protocol says.
Litmus: protocols carry interactions; your code owns permissions and the execution boundary;
model-chosen delegation stays agentic and is taught in 2.5 and 9.2.

## The mental model

Several protocols standardise different connections. MCP connects a host to tools and data.
A2A connects one agent to another opaque agent. MCP Apps, A2UI and AG-UI sit between agent
and person. Commerce and payment protocols sit between agent and merchant or payer. Some are
complementary layers; some compete inside a layer (UCP and ACP both cover checkout). The
reader asks "which connection am I on, which protocols compete there, and how settled are
they?" Trust boundaries cut across all of them: publisher identity, untrusted descriptions
and artifacts, and scoped authority. The chapter treats that in one short section and links
2.6, 4.6 and 8.5 for depth. Protocol-level attacks on A2A are published (A2ABreak, below),
distinct from disclosed operational incidents.

## Must-cover

Ranked. Seam notes mark where neighbours stop.

1. **The connection map.** Resource (MCP), peer agent (A2A), person (MCP Apps, A2UI, AG-UI),
   payment (UCP, ACP, AP2, x402, MPP). Instruction files (AGENTS.md, Agent Skills) belong to
   2.3. Say which are layers and which compete. *Skip it:* readers treat every protocol as an
   MCP rival. Framing verdict: **n/a** (concept); each protocol carries its own.
2. **MCP revision 2026-07-28, in one caveat.** Versions are date strings ("2.0" is informal
   community usage, uncited). It dropped the `initialize` handshake and `Mcp-Session-Id`;
   requests carry version and capabilities in `_meta`; `server/discover` is mandatory. The
   versioning page also supports interoperating with initialization-based revisions, so the
   selection criterion is version and capability compatibility. Detailed migration belongs to
   2.4. **Standard** (MCP as connectivity); the new revision **Emerging**.
3. **Deprecation is not an operational guarantee.** Roots, Sampling, Logging and Dynamic
   Client Registration become eligible for removal in the first revision released on or after
   2027-07-28; HTTP+SSE follows a separate rule (three months after SEP-2596 reaches Final).
   Eligible is not removed, and staying in the spec says nothing about SDK or host support.
   Distinguish specification lifecycle from implementation availability.
4. **A2A: the task lifecycle.** Agent Card at `/.well-known/agent-card.json` (optional JWS
   signature); three bindings; Messages versus Tasks; artifacts versus conversational
   messages; progress delivery; interruptions for input or authentication; rejection, failure
   and cancellation. Requirement: show how your code turns a remote failure into structured
   feedback for the calling model; retry and checkpoint mechanics link to Part VII. Version
   provenance: release v1.0.1 (published 2026-05-28; fixes to media type, errors, TaskStatus)
   supersedes the 1.0.0 header; cite a pinned release for normative claims, not `/latest/`.
   Verdict **Emerging** (joined AAIF 2026-08-17; independent evidence of production
   cross-vendor use is thin). Single-vendor patterns: 9.2.
5. **When A2A is overkill.** Default to a direct call or a tool wrapper. The stronger
   discriminator is stateful, multi-turn collaboration with a peer you cannot inspect, not an
   organisational boundary alone. Present this as editorial judgment unless comparative
   evidence turns up. Constructive answer: wrap the peer as a tool until the lifecycle
   features are needed. Verdict **Contested** (the need, not the spec).
6. **The person-facing edge.** MCP Apps (a tool declares `_meta.ui.resourceUri`; host renders
   a sandboxed `ui://` resource); A2UI (agent picks from registered components; describes
   what UI to deliver); AG-UI (an event protocol connecting agent to frontend; a different
   job from A2UI, per its docs). One paragraph each at most; streaming and UX stay in 6.3.
   **Emerging.**
7. **Commerce and payment.** UCP, ACP, AP2, x402 and MPP (Stripe and Tempo, announced
   2026-03-18; programmatic agent payments, fiat and stablecoin). UCP and ACP overlap on
   checkout; AP2 (mandates) and x402/MPP (pay per request) do different jobs. Not every
   protocol proves user authorisation. UCP's relation to AP2 is conditional on the AP2
   Mandates extension (reported by review; confirm on a dated UCP spec before quoting).
   ACP: beta, date-versioned. Verdict **Emerging**; adoption claims **Contested**.
   Carrier: shopper assistant, as a proposed extension needing carrier approval (the bible
   gives it no checkout powers).
8. **Authorisation on the payment edge.** Mandates and signed intent are evidence; the
   decision to spend is shared between the user, validating merchant and payment parties, and
   your harness policy. Distinguish harness policy from counterparty enforcement. Links 4.3,
   8.5. **Established** (principle).
9. **Discovery, trust and cost.** Registries, Agent Cards and `server/discover` are claims by
   the publisher, not endorsements; a well-known URI is a familiar convention, but Agent Card
   practice is **Emerging**. Exposed schemas, cards and returned content cost tokens and
   attention; connecting does not force every schema into the window (Anthropic describes
   on-demand loading and filtering). Minimal disclosure and filtered results. Depth in 1.5,
   2.4, 4.6.
10. **The decision table, with a compatibility check.** Per connection: protocol, maturity,
    cost of adopting early, the do-nothing option (a direct API call). Add a dated, cited
    check that both endpoints support the same binding, revision and extensions, and a "no
    compatible interface" outcome. Exhaustive SDK matrices stay external. Last-reviewed month
    on every row.

## Mention-and-link

MCP fundamentals, tool poisoning, OAuth: 2.4. Tool calling: 2.1. Instruction formats: 2.3.
Multi-agent, handoffs: 9.2; orchestrator-workers: 3.3. Approval UI: 6.3, 4.3. Injection
across boundaries: 4.6. Identity, tokens: 8.5. Registry governance: 8.6. Token cost: 1.5.

## Out of scope

Writing an MCP or A2A server end to end; payment-network, KYC and stablecoin mechanics;
per-vendor SDK matrices; AG-UI streaming mechanics (6.3).

## Maturity summary

- **Standard:** MCP as connectivity (AAIF, Linux Foundation); protocol-delivered text is
  untrusted.
- **Established:** authorisation stays in your harness.
- **Emerging:** MCP 2026-07-28; A2A in practice; Agent Cards and registries; MCP Apps, A2UI,
  AG-UI; UCP, ACP, AP2, x402, MPP.
- **Contested:** the need for A2A (editorial); commerce adoption and "winner" claims.
- **n/a:** the edge-map framing.

## Search terms and aliases (author sign-off needed)

- Aliases: "open protocols", "interoperability protocols" (Gulli draft; alias sweep only).
  "agent-to-agent" for A2A.
- Search terms, not aliases: Agent Card, discovery, federation (mechanisms or wider concepts).
- Disambiguate IBM's Agent Communication Protocol (merged into A2A, August 2025) from the
  Agentic Commerce Protocol.
- "MCP 2.0": informal; official pages use dates. USB-C analogy: attribute to Anthropic's
  MCP explainer.

## Contests

- Guides using `agent.json`, `/tasks/send` or `message/send` for A2A mismatch the 1.0.x spec
  (`agent-card.json`; PascalCase methods such as `SendMessage`). Target: catalog B rows
  homed at 9.3.
- AP2 described as Intent, Cart, Payment mandates; the current site says Checkout and
  Payment mandates. Check the v0.1 wording first.
- AP2 was announced 2025-09-16. "MCP is stateful with a handshake" is out of date.

## Reader-verifiable anchors

- The MCP Excalidraw app in Claude (documented on the MCP Apps overview page): reproduces
  the person-facing edge.
- A named public A2A sample or the project's documented local quickstart, not "any server".

## Incidents and evidence

- A2ABreak (Lotfi, Rahman, Karim, Bertino, arXiv:2609.10871, 2026-09-09): 11 protocol-level
  vulnerabilities found from the A2A specification; experimental.
- A2ASecBench (Li et al., ICLR 2026): protocol-aware attacks across A2A stages.
- MCP incidents (MCPoison CVE-2025-54136, CurXecute CVE-2025-54135, postmark-mcp): reuse
  from 2.4 by link.

## Code seam

NONE. A framing chapter; no listing-studio package. The decision table is the artefact.

## Named-idea candidates

None earns promotion beyond a descriptive heading ("Which connection are you on?").

## Sources

Opened: MCP deprecated registry (2026-07-28); A2A v1.0.1 release page; Stripe MPP post;
A2ABreak abstract; A2ASecBench page; AG-UI introduction. Opened in the first pass: MCP
versioning and changelog, MCP Apps overview, A2A spec 1.0.0, AAIF posts (2026-08-17,
2026-10-06), AP2, ACP repo, x402, A2UI. Not read: A2A v1.0 announcement post (2026-03-12),
UCP dated spec, Anthropic code-execution-with-MCP post. Opened at Stage 4/5: UCP
specification overview and checkout at version 2026-08-25; AAIF "Where A2A fits in the open
agent ecosystem" (2026-08-20); SEP-2596 (merged Final 2026-05-18); A2ABreak abstract re-read. Secondary, do not cite: ACP Instant
Checkout scale-back reports.

> **Verify before quoting:** every version and date; UCP spec version and AP2 extension
> condition; x402 foundation host; ACP stable date; MCP SDK support; MCP Apps clients.

## Open questions for the author

1. Does 2.4 get a migration note for 2026-07-28, or does 9.3 carry the one caveat only?
2. Include MPP beside x402, or narrow the selection criteria and say why?
3. May the shopper assistant gain checkout powers as a carrier extension?
4. Sign off the alias line and the "Contested" verdict on A2A need.

## Map review (Stage 1.5)

Second-engine review. Verification: primary pages opened for 1, 3, 5, 6, 12, 13;
others checked against cited sources or hedged.

1. Accepted: A2ABreak verified (arXiv:2609.10871); cross-protocol trust section added.
2. Accepted-modified: layers versus competitors added; UCP/ACP overlap not independently opened.
3. Accepted: A2ASecBench exists (ICLR 2026); "none measure protocols" removed.
4. Accepted: lifecycle and failure-return requirement replaces method inventory.
5. Accepted: MPP verified (Stripe, 2026-03-18); folded into item 7.
6. Accepted: AG-UI verified as agent-frontend event protocol; one sentence in item 6.
7. Accepted: 2.4 owns migration; 9.3 keeps one caveat and the compatibility criterion.
8. Accepted: dated compatibility check and no-interface outcome added to item 10.
9. Accepted-modified: thesis adopted; reworded from the review's sentence.
10. Accepted: direct call as default; counterparty enforcement distinguished.
11. Accepted: framing verdict n/a; direct-call advice labelled editorial.
12. Accepted: registry verified; twelve-month promise removed.
13. Accepted: v1.0.1 verified (2026-05-28); pinned-release rule added.
14. Accepted-modified: extension condition kept but marked unconfirmed (UCP page not readable).
15. Accepted-modified: cost framing added; Anthropic post unread, so attributed as described.
16. Accepted-modified: aliases split from search terms; "MCP 2.0" marked informal.
17. Accepted: anchors replaced with documented, reproducible ones.
18. Accepted: sources labelled honestly; questions section added.
19. Accepted: shopper checkout flagged as a proposed extension.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** landscape chapter, up to 2,800 prose words.

1. **Maturity.** The framing is `n/a`, with a verdict per protocol as the map gives. The claim that A2A is needed is Contested, and is labelled as the book's editorial judgement. Last reviewed 2026-11.
2. **Code.** None. The decision table is the artefact.
3. **The 2026-07-28 MCP revision.** 9.3 carries a single caveat that points to 2.4 in plain text. The shipped chapter 2.4 is not edited. Its migration note goes on the author checklist (the MCP 2.0 migration debt is already known).
4. **MPP.** Include MPP beside x402, as one line each, cited.
5. **Carrier.** The shopper assistant does not gain checkout powers. Commerce payment protocols are described generically, with no carrier extension, and this goes on the checklist.
6. **Unconfirmed items.** Keep the UCP AP2-extension condition only if the writer confirms it on the primary page; otherwise cut it. Item 15 is attributed as described.
7. **Not included.** No aliases (sign-off pending), no coinage, no From-production callout.

## Reconcile log (Stage 5)

Fact-checker:
1. SEP-2596 gotcha: fixed. Confirmed merged with the `final` label on 2026-05-18; HTTP+SSE removable since about August 2026; SEP-2596 glossed and cited.
2. UCP overview `/latest/` URL: fixed. Pinned to version 2026-08-25.
3. "Where A2A fits" (2026-08-20): fixed. Cited for UCP as an A2A extension, dated in Further reading, "stack" changed to "fit together", added to map sources.
4. A2ABreak "confirmed experimentally": fixed. Now "validated against expert review" (abstract re-read; it names the three attack classes).
5. Tencent "production use": fixed. Now "integrating"; Huawei kept as a user.
6. "Cross-vendor default" uncited: softened. Now "hosts from several vendors support it", cited to the MCP Apps client list.
7. "SDK and host support lag" uncited in the table: kept as a labelled cost-of-adoption judgement, shortened.

Prose-critic:
1. Opening scenario dropped: fixed. A supposed restock job for the repricer sibling is carried through the A2A edge, the payment edge, the authority check, the overkill call and credential scoping.
2. Payment paragraph with no instance or recommendation: fixed. Recast as five protocols doing three jobs, with the restock order and a recommendation.
3. Thesis restated: fixed. "The fix, in miniature" cut, and the first sentence of the agentic paragraph cut.
4. Contested label narrated: fixed. Label kept (Stage 1.6); the call is now made plainly: wrap first, move to A2A when you hand-build a task lifecycle.
5. Maturity roll-call opener: fixed. Cut; MCP's Standard now carries a reason, and the two MCP verdicts are distinguished.
6. "X is not Y" gotchas: fixed. Three bullets rewritten as plain statements; the support point is now explained (SDKs and hosts can drop a feature sooner).
7. Token-cost paragraph in Security: fixed. Cut; See also keeps the 1.5 pointer.
8. "usually": fixed. "A common failure".
9. "anyone": fixed. Names the merchant and payment processor.
10. Signposting topic sentences: fixed. Both removed.
11. Person-facing edge with no recommendation: fixed. Choose by who owns the screen.
12. "genuinely": fixed. Cut.
13. "The artefact is a decision": fixed. Folded; "catalogue" made "catalog".
14. "It carried the conversation": fixed. Merged.
15. Bare cross-references: rejected. Unmerged chapters are named in plain text by house rule. Trailing whitespace fixed.

Cold-reader:
1. harness, binding, extension, MCP Tasks, SEP-2596, mandate, era matrix: fixed. Each glossed where first met.
2. Why a new client fails against an old server: fixed. Old servers expect the handshake first.
3. Authority check never shown: fixed. New subsection with a worked check for the restock order (a policy sketch, not companion code).
4. Payment paragraph density: fixed. Three jobs; IBM disambiguation moved to a footnote.
5. "bounded": fixed. A limit, a counterparty and an expiry.
6. "Scope authority": fixed. Shown on the restock credential.
7. A2A version note aimed at authors: fixed. Now tells the reader what to record.
8. Alt text about 150 words: fixed. 73 words; SVG description trimmed to match.
9. Stablecoin, FIDO, maturity vocabulary: stablecoin glossed; FIDO clause cut from the body (kept in the footnote); the vocabulary is defined on the labelling page. Softened.

Second-engine review: its findings address the map and were dispositioned in the Map review (Stage 1.5) above; no further findings at this stage.
