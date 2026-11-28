# Coverage map: Governance & Compliance (chapter 8.6)

> Research-derived spec for what the chapter must cover, and where to stop. Angles run: vendor and
> primary docs, regulation and standards texts, the skeptical read, the alias sweep, incidents
> (three public cases, below). Nothing here is legal advice; the chapter says so once, plainly.
> Bar: definitive but tight.

## Thesis

Compliance regimes keep moving their dates and paperwork, but they ask engineering for the same
deterministic control plane: a classified system inventory, a durable decision record, an
enforceable human override, and user-facing disclosure. Budget: Standard pattern, 2,000 to 2,800
words. Who decides: your code. Controls are code and process, never delegated to the model.

## The mental model

Governance is the set of decisions an organisation can show it made about an AI system: what it is
for, who may change it, what it may do, what is logged, who can stop it. Compliance is the narrower
act of showing that evidence to an outside party under a rule. The first job is classification:
most commerce surfaces (listing copy) carry light duties, and only a few uses are heavily
regulated. Build the four controls once, then map them to whichever rule applies. Disclosure and
literacy duties are the part that differs by regime.

## Must-cover

Ranked. Dates are as the source states them and are volatile.

1. **Classify, and know your role** `[+]`. The EU AI Act sorts systems by use (Arts. 5, 6, Annex
   III). Art. 6(2): Annex III systems "shall be considered to be high-risk"; Art. 6(3) carves out
   systems posing no "significant risk of harm", but profiling of natural persons stays high-risk
   (not re-opened on a clean text; verify on EUR-Lex). Art. 25(1): a deployer becomes a provider by
   branding a high-risk system, substantially modifying it, or changing its intended purpose.
   *Skip it:* over-built conformity machinery for a copywriting tool, or a hiring use ignored.
   **Established** (classify-first); **Emerging** (how regulators apply it to LLM wrappers).
2. **The duties a commerce team meets, split by who they bind** `[+]`. Art. 50(1) and 50(2) bind
   providers (interaction disclosure; machine-readable marking of synthetic output, with an
   exemption for assistive standard editing). Deployer duties sit in Art. 50(4): disclose deep
   fakes and AI text published to inform the public on matters of public interest, exempt where a
   person holds editorial responsibility after human review. Ordinary product copy is not that.
   Art. 4 (AI literacy) binds providers and deployers but sits outside the Art. 99(3)-(5) fine
   caps; penalties are national under Art. 99(1). Art. 99(4): up to EUR 15 000 000 or 3% for
   listed operator obligations including Arts. 26 and 50. *Skip it:* the shopper assistant ships
   with no disclosure. **Standard** (disclosure UI); **Emerging** (text marking).
3. **High-risk runtime obligations** `[+]`. Art. 12(1) automatic event logs; Art. 14 oversight
   "commensurate with the risks, level of autonomy and context of use", with override or stop;
   Art. 26(6) deployers keep logs under their control "at least six months"; Art. 73 serious
   incident reporting, with shorter tiers than 15 days for some cases (2 and 10 days per the
   reviewer, unverified here). Key seam with 8.1: operational traces are sampled and disposable;
   the compliance record is unsampled, immutable and retention-bound. **Established** (as
   engineering); the statutory deadlines are Emerging.
4. **Existing law already bites, and buyers ask for assurance** `[+]`. Consumer-protection law has
   no AI exemption. *Moffatt v. Air Canada*, 2024 BCCRT 149 (14 Feb 2024): the tribunal held the
   airline liable for negligent misrepresentation by its website chatbot, award CAD 812.02; a
   tribunal, not a court. FTC Operation AI Comply (25 Sept 2024) included DoNotPay, an "AI lawyer"
   claim with no testing, proposed order of $193,000. SOC 2 (AICPA Trust Services Criteria) is the
   audit mid-market SaaS buyers ask for first; primary text not opened this session. **Established**.
5. **A management system, not a one-off audit: ISO/IEC 42001** `[+]`. First edition published
   2023-12-18 (IEC webstore); it "specifies the requirements and provides guidance for establishing,
   implementing, maintaining and continually improving" an AI management system. Certifiable,
   unlike NIST. Public certification counts are not centrally published; do not claim adoption
   either way. **Emerging.**
6. **NIST AI RMF 1.0 as the vocabulary** `[+]`. NIST AI 100-1, January 2023: GOVERN, MAP,
   MEASURE, MANAGE; GOVERN 1.1, MAP 3.5, MANAGE 4.1 as hooks. Generative AI Profile NIST AI 600-1,
   July 2024, which lists value chain and component integration among its risks. **Established**
   as reference; **Contested** whether the paperwork reduces harm (see Incidents).
7. **Governing agents in motion** `[+]`. Which human delegated authority for an action; model and
   prompt pinned with re-evaluation on change, since silent upstream drift voids a prior review;
   an approved tool and MCP registry. Seams: 2.6, 4.1, 8.5. NIST's 2026 agent initiative was
   suggested by the reviewer and not opened. **Emerging.**
8. **The governance record** `[+]`. Inventory with purpose and risk class; model and prompt version
   per decision; approval record; change log; incident log; vendor list. Self-changing harnesses
   need the diff and an approver (pointer to 9.7). **Standard** (inventory, change log);
   **Established** (immutable audit logging, human override).

## Mention-and-link

- Approval gates and escalation → 4.3; filters, red-teaming → 4.4, 4.6; prompt versioning → 4.1.
- Trace capture → 8.1; PII, identity, secrets → 8.5; cost caps → 8.4; model and vendor terms → 8.2.
- Self-improving harness governance → 9.7; security posture catalog (`docs/catalogs/security-posture.md`).

## Out of scope

- Legal interpretation, jurisdiction advice, GDPR depth (counsel; 8.5 for engineering).
- US state, sector and other national regimes: name that they exist, do not catalogue.
- Policy-document writing, model cards, GPAI provider duties (Chapter V): one sentence.

## Maturity summary

- **Standard:** owner, inventory entry, change record; user-facing AI disclosure.
- **Established:** risk-based classification; audit logging; human override; NIST AI RMF vocabulary.
- **Emerging:** ISO/IEC 42001 certification; machine-readable text marking; regulator treatment of
  LLM and agent wrappers; agent governance standards.
- **Contested:** whether compliance paperwork reduces harm (skeptical source: Raji et al., "Closing
  the AI Accountability Gap", arXiv:2001.00973, Jan 2020, argues for internal end-to-end audits).
- Chapter verdict: **Established (core runtime controls) · Emerging (enforcement and AI-specific
  standards)**. Rate practices, not calendar dates.

## Aliases

For the `*Also called:*` line, all needing author sign-off: AI governance, responsible AI, AI risk
management (NIST), AI management system, AIMS (ISO/IEC 42001), AI assurance, AI GRC, AI TRiSM
(Gartner), model risk management (bank supervisory guidance). Sources per alias to be cited at
drafting.

## Reader-verifiable anchors

- Content Credentials (C2PA) on generated images, checkable at contentcredentials.org/verify,
  against the unsettled marking of text.
- Vendor admin controls: Claude Code managed settings and the vendor compliance APIs, where admins
  restrict tools and pull audit logs (docs not opened here; open before citing).
- Statutes and NIST AI 100-1 (doi.org/10.6028/NIST.AI.100-1) are sources, not daily tools.

## Incidents

Public cases above (*Moffatt*, DoNotPay). No AI Act enforcement decision found. An Italian
Garante fine against OpenAI was suggested and not verified; excluded.

## Carrier

Listing Studio: the compliance reviewer persona is an advisory draft check (step 5, see 3.5). The
control is deterministic, at the publish gate: `compliance.safety_claims[]` forces a human
sign-off and writes a decision record. Contrast a kids' bunk bed with a phone case for
classification. Shopper assistant: disclosure. Merchant helpdesk: human-override path. Repricer:
change record and approver.

## Named-idea candidates

"The governance record" (item 8), offered for accept or strike. "Classify first" struck as a
slogan.

## Code seam

New `listing-studio/governance/` package: a decision-record writer (JSON line per consequential
action: model version, prompt version, approver, outcome) and an AI-disclosure label helper.
Imports the 4.3 gate and 8.1 trace id if shipped; otherwise stand-alone.

## Open questions for the author

1. Approve the alias list and "The governance record" as a named idea?
2. Chapter verdict split as above, or a single Emerging?
3. Name the vendor admin tools as the daily-tool anchor once the docs are opened?

## Sources (opened this session)

- Regulation (EU) 2024/1689 via artificialintelligenceact.eu (Arts. 26, 50, 99 opened again this
  pass; a reproduction with garbled marks; EUR-Lex returned no content). Re-open on EUR-Lex.
- NIST AI 100-1 and NIST AI 600-1 (opened). ISO/IEC 42001 via IEC webstore abstract only.
- *Moffatt* via ABA Business Law Today and law-firm summaries; FTC press release 25 Sept 2024
  via search results; arXiv:2001.00973 abstract page.

> **Verify before quoting:** every AI Act date; the amending act (reported as Regulation (EU)
> 2026/1744, in force 27 July 2026; unopened, including any 2 December 2026 Art. 50(2)
> grandfathering and any Art. 4 or Art. 99(6a) change); BS EN ISO/IEC 42001:2026 is likely a
> European adoption of the 2023 text (unverified).

## Map review (Stage 1.5)

1. Secondary read cited by name instead of the primary source: accepted; deleted.
2. Missing thesis, budget, litmus, open questions: accepted; added.
3. Art. 50 provider/deployer split: accepted; confirmed on the Art. 50 page.
3. Art. 4 outside Art. 99 caps: accepted; confirmed on the Art. 99 page.
3. Art. 26(6) six-month retention: accepted; confirmed.
3. Art. 6(3) profiling, Art. 73 tiers, Art. 99(6a), 2026/1744 details: accepted-modified; stated as unverified, EUR-Lex unreachable.
3. ISO 42001:2026 as a regional adoption: accepted-modified; flagged as likely, unverified.
4. SOC 2 and existing-law liability: accepted-modified; added, Moffatt and FTC verified, AICPA text unopened.
5. Agent governance: accepted-modified; added, NIST agent initiative unopened.
6. Compress EU items, demote 9.7, 8.1 contrast, add links: accepted.
7. Vendor, skeptical, incident sweeps: accepted-modified; Moffatt, FTC, Raji verified; Garante rejected as unverified.
8. Maturity verdicts reconciled: accepted.
9. Tool anchors instead of statutes: accepted-modified; vendor docs unopened.
10. Persona is not the control: accepted; moved to the publish gate.
11. Repricer naming, disclosure consistency: accepted.
12. Alias attribution and synonyms, strike slogan: accepted.
13. ISO 42001 abstract only: accepted-modified; adoption claim removed, text still paywalled.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Code:** a new `listing-studio/governance/` package:
   - a decision-record writer (append-only, with who/what/why/model/override fields);
   - an AI-disclosure label helper.

   Use local equivalents only; do not import 4.3's or 8.1's unmerged code.
2. **Verdict:** split, as the map has it. Established for the core runtime controls; Emerging for enforcement and AI-specific standards. Carry "Last reviewed: 2026-11".
3. **Unverified items:** drop Regulation 2026/1744, the Art. 73 tiers, the Art. 6(3) profiling rule and SOC 2 specifics unless a primary source is opened. No legal advice framing.
4. **Named idea:** "The governance record" is plain description, not a coinage. It goes on the checklist.
5. **Vendors:** no vendor admin tools are named.
6. **No From-production callout.** No new alias line.

## Reconcile log (Stage 5)

Fact-check:
1. Moffatt facts: softened; verified through secondary sources only (the tribunal site blocks automated reads); on the author checklist.
2. FTC "AI lawyer": fixed; now quotes "the world's first robot lawyer".
3. Art. 6(2) quote: verified; Annex III areas read on the Annex III page and the reasoning added for why product copy is outside it.
4. Art. 25(1): verified; no change.
5. Art. 50(1), (2), (4): verified; no change to the readings, now framed as readings for counsel.
6. Art. 4 wording: fixed; "sufficient" removed, now "take measures to support AI literacy"; not checked against the Official Journal, on the checklist.
7. Art. 99 caps and Art. 4 outside them: fixed; moved to note 6, which now points at EUR-Lex.
8. Art. 12(1): verified; no change.
9. Art. 14 pinpoint: fixed; cited as Art. 14(3)-(4).
10. Art. 26(6): verified; no change.
11. Art. 73: fixed; Art. 73(1) read and URL added to note 7.
12. NIST AI 100-1 date and four functions: verified from the NIST PDF; functions now glossed from its text.
13. NIST AI 600-1 date and value-chain risk: verified from the NIST PDF; kept.
14. ISO/IEC 42001 day of publication: softened; "December 2023".
15. Raji claim: softened; now states what the paper argues, and the "contested" claim and editorial closer are gone.
16. C2PA verify URL: fixed; moved URL in body and note 12, credited to the Content Authenticity Initiative.
17. "No enforcement decision found": fixed; replaced with phased application of the Act (note 6).
18. "Images are further along": softened; now "a working standard exists for images".
19. Annex III 2 Dec 2027 date sentence: rejected; secondary sources only.
20. Citation for the Established half of the verdict: rejected; the claim is softened to "long use in regulated software" instead.

Prose critique:
1. Length: fixed; 2,797 argued words, mostly cut from the legal survey (penalties, Art. 73 and the general-purpose model note moved to notes).
2. L34 Raji overclaim and closer: fixed (see fact-check 15).
3. L136 "three things" with four listed: fixed; the single-writer limit moved into Gotcha 2 and the signposting opener cut.
4. L44 legal call too confident, Art. 50(2) unaddressed: fixed; softened to readings handed to counsel, and the visible label is stated not to be machine marking.
5. Four controls restated at L3, L15, L28, L157: fixed; full list kept only in the definition, tagline and L15 cut, In short kept as an action list.
6. L9 colon-zinger: fixed.
7. L11 quantifier and closer: fixed.
8. L130 overclaim and aphorism: fixed.
9. Code comments re-teach prose: fixed; the L73 and L104 duplicates cut.
10. Counter-trigger restated in Gotcha 5: fixed; Gotcha 5 second half cut.
11. Warehouse screen not a carrier surface: fixed; marked hypothetical; on the checklist.
12. Callout list-itis: fixed; helpdesk and repricer tour cut.
13. L54 risk-class restatement: fixed.
14. L32 which loop: fixed; names the agent loop and per-step records.
15. Lens line parenthetical: fixed; removed.
16. Withheld airline name: fixed; Air Canada named.
17. Dated absence claim: fixed (see fact-check 17).

Cold read:
1. Undefined terms: fixed; glossed control plane, conformity machinery, publish gate, the rail-height claim, deep fakes, negligent misrepresentation, Operation AI Comply, proposed order, the four NIST functions, write-once retention lock, and the carrier terms in the callout (persona, `compliance.safety_claims[]`, shopper assistant, repricer).
2. Missing steps: fixed at L9 (both cases ran on existing law), L13 (why a sampled trace store fails), L40 (Annex III areas), L44 (commercial vs public-interest text), L46 (Art. 4 enforcement left to national rules, in note 6), L130 (where `surface` and `ai_generated` come from).
3. Snippet imports: fixed; an imports block, kept in sync by a new `governance-imports` anchor.
4. Gate, override and inventory not shown: fixed; gate and override described in prose, an example inventory table added, and both stated as outside the companion code.
5. Alt text too long: fixed; shortened.
6. "Chapter of duties" ambiguity: fixed; now "Chapter V of the Act", in note 7.

Second-engine review: the map findings are dispositioned under Map review above; no draft findings are on record.
