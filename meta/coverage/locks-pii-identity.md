# Coverage map: Locks, PII & Identity (chapter 8.5)

> Research-derived spec for what the chapter must cover. Angles run: vendor/primary docs
> (PostgreSQL, PgBouncer, MCP, OWASP), academic (one position paper), failure modes, incidents,
> alias sweep, daily-tool, everyday-engineer gotchas, skeptical read. Review and trim the
> **Must-cover** list; that sets scope. Bar: definitive but tight.

**Thesis.** Locking, PII handling and service-account auth each fail under agents in a
predictable way (a model pause turns a short lock into a stall or a stale write, context and
traces multiply the exits for personal data, ambient credentials turn injected instructions
into a confused deputy), and each is fixed by a check in your code at a boundary the model
cannot talk across.

**Who decides:** your code. **Grounding:** companion repo plus research; no "From production"
callout (the stub's `production + research` is overridden). **Budget:** standard pattern,
about 2,000 to 2,800 words; three pillars is dense, see Open questions.

## Must-cover

Ranked. All items are new (the chapter is a stub).

1. **Serialize writers, and never hold a transaction across a model call** - two repricer runs
   (or a retry) on one listing's price. Use commit-time serialization for the short write:
   `pg_advisory_xact_lock` (transaction scope; session locks outlive a rollback and stack, so
   avoid them behind a pooler), or optimistic concurrency (`UPDATE ... WHERE version = $v`).
   An open transaction across a multi-second LLM call starves the pool, so the model step runs
   outside any transaction and the write is checked at commit. The docs also warn the lock table
   is finite. On a failed check return a structured, non-leaking "conflict, re-read" result.
   *Skip it:* lost updates. **Standard.** PostgreSQL docs, Explicit Locking 13.3.5.
2. **Leases and fencing for long steps** - when a step must hold ownership across a model pause,
   use an application lease; it can expire while the slow step runs, so the store checks a
   monotonically increasing fencing token and rejects the stale write. Separate locks for
   efficiency from locks for correctness. *Skip it:* two runs both believe they own the record.
   **Established.** Kleppmann 2016. Seam: 7.3 owns resume; 7.1 and 7.3 split idempotency (keys
   at the retry layer, replay at checkpoints).
3. **Tenant isolation is enforced below the model** - code binds the tenant from the
   authenticated request; the data layer enforces it with row-level security (default-deny;
   superusers, `BYPASSRLS` roles and unforced table owners bypass it; unique and foreign-key
   checks can leak existence). Gotcha: under PgBouncer transaction pooling `SET` is never
   supported, so tenant context is set per transaction (`SET LOCAL` / `set_config(..., true)`),
   never per session. Retrieval needs the same filter before the vector search, not after.
   *Skip it:* one merchant's catalog data reaches another's run. **Standard** (principle),
   **Emerging** (agent-specific practice). PostgreSQL Row Security Policies; PgBouncer features
   page; OWASP LLM02:2025 (scenario 2 covers retrieval access-control bypass).
4. **PII has more doors than the prompt** - prompt, logs and traces, tool results, answer, and
   also the provider boundary and anything persisted from context (embeddings, checkpoints,
   memory). Minimise what enters context, pseudonymise with reversible placeholders where the
   task needs the entity, redact before persistence. Gotchas: SDK and middleware trace hooks
   log raw tool payloads and bearer tokens by default; models mangle or invent placeholders
   (`<EMAIL_1>`) on the way back, so the round trip needs a validate step. Reversible
   pseudonymisation is not anonymisation. Detectors are probabilistic (Presidio says it cannot
   guarantee finding all sensitive information): detection is a layer, not the control.
   Provider retention terms change; link the vendor page. *Skip it:* personal data in traces
   nobody scoped. **Established** (practice), **Emerging** (agent traces, memory). OWASP
   LLM02:2025; Presidio docs. Seams: 4.4 model-boundary filters, 8.1 trace pipelines, 5.3
   memory writes, 8.6 retention policy; 8.5 owns application-layer minimisation and the
   placeholder round trip. Link 1.5 for context minimisation.
5. **Delegation, not impersonation, with an audit chain** - the agent acts for a user or tenant
   and carries both identities, so audit answers "what did run X do, as whom, under which
   grant". RFC 8693 gives the vocabulary (`act`, `may_act`; nested `act` for multi-hop). One
   shared service account or long-lived key destroys attribution. *Skip it:* the log says
   "the agent did it". **Established** (OAuth), **Emerging** (applied to agents). RFC 8693;
   South et al., arXiv:2501.09674.
6. **Scoped, short-lived credentials and revocation** - scope a credential to tenant, task and
   short life; start minimal and escalate on challenge. MCP Security Best Practices (spec
   2025-11-25) name progressive scope elevation and warn against omnibus scopes (`files:*`,
   `db:*`, `admin:*`). Revocation must be tested. On an `insufficient_scope` or denial return a
   structured result that does not reveal what exists. *Skip it:* one stolen token reaches
   everything. **Emerging** for per-run agent scoping; least privilege itself is **Standard**.
7. **The confused deputy, and sessions are not identity** - an agent or MCP server holding
   authority can be induced to spend it for someone else. Name it correctly (Hardy 1988, the
   compiler that overwrote a billing file). MCP forbids token passthrough, requires accepting
   only tokens issued for the server, requires per-client consent on proxy servers, says
   servers must not use sessions for authentication and should bind session IDs to the user
   (`<user_id>:<session_id>`). Resumed runs (7.3) re-check identity. Protocol-agnostic; MCP is
   one instance, 2.4 owns server and transport duties. *Skip it:* the deputy is the agent.
   **Standard** (the problem), **Emerging** (agent-era fixes). Hardy 1988; MCP spec 2025-11-25.

Ceiling is seven. Workload identity (SPIFFE) would be a second chapter.

## Mention-and-link

- Prompt injection and the lethal trifecta: 4.6. Output PII filters: 4.4. Approval gates: 4.3.
- Harness permissions and execution boundary: 2.6. Retrieval and its ACLs: 5.2.
- Retry, idempotency, resume: 7.1, 7.3. Memory writes: 5.3. Sandbox and egress: 9.4.
- Retention, regulation (GDPR and the like): 8.6. Traces and redaction in observability: 8.1.
- MCP transport and consent mechanics: 2.4, 9.3. Deployment secrets: 8.7. Context: 1.5.

## Out of scope

Compliance programs and DPIAs (8.6); building an identity provider, SPIFFE (cite only);
differential privacy and training-data privacy; consensus systems (ZooKeeper, etcd, Raft: cite
Kleppmann, stop); frozen provider retention terms.

## Maturity summary

- **Standard:** database locking and isolation; tenant isolation as a principle; least
  privilege; the confused deputy as a named problem; token audience validation.
- **Established:** fencing tokens and the lease caveat; PII detection as a layer; token
  exchange and delegation vocabulary.
- **Emerging:** agent-specific tenant isolation; per-run agent credentials and delegation
  chains; PII in agent traces and memory; MCP authorization (optional, revised between dated
  specs).
- **Contested:** any claim that PII redaction "solves" privacy. (The claim about agent-identity
  products shipping a registry without enforcement is dropped: no primary source.)

Chapter verdict: **Emerging**, with a split proposed in Open questions. Mixed evidence takes
the lower tier.

## Aliases

- authenticated delegation, agent identity: South et al., arXiv:2501.09674.
- Identity & Privilege Abuse: OWASP Agentic Top 10 ASI03 (title read from OWASP's announcement).
- delegation vs impersonation, actor claim: RFC 8693. confused deputy: Hardy 1988.
- sensitive information disclosure: OWASP LLM02:2025.
- redaction, tokenization: OWASP LLM02; Presidio (irreversible redaction vs reversible
  operators; do not conflate with anonymisation).
- lease, fencing token: Kleppmann. Sub-mechanisms (advisory lock, token passthrough) are
  body terms, not aliases.
- "Non-Human Identity" and "Agent IAM": not verified from an opened primary source; left out.

## Reader-verifiable anchors

1. PostgreSQL docs: a session-level advisory lock "is held until explicitly released or the
   session ends" and survives a rollback; two `psql` sessions show it (13.3.5).
2. A remote MCP server consent flow in a public agent client (OAuth with an RFC 8707 `resource`
   parameter): the reader sees the scopes requested. Candidate client to confirm in Stage 2.
   Claude Code's `apiKeyHelper` is dropped: it rotates the CLI's own model key, not a delegated
   credential.

## Incidents

- **Asana MCP server, June 2025.** A bug let MCP users reach other organizations' data;
  reported at roughly 1,000 customers, limited to object types the MCP user could normally see;
  server offline and connections reset. Maps to item 3. Asana's own page was not opened (the
  URL tried returned 404); figures here come from secondary reports, so **verify before
  quoting**, or cite only that the exposure crossed tenants.
- **Salesloft Drift, August 2025.** GTIG (UNC6395): stolen OAuth tokens for the Drift
  integration; tokens revoked 20 August; the 28 August update confirms the "Drift Email"
  integration reached a very small number of Google Workspace accounts, so not only
  Salesforce. Initial access unexplained. Maps to 5 and 6. Opened.
- **GitHub MCP toxic agent flow, Invariant Labs, 26 May 2025.** Malicious issue hijacked an
  agent with access to non-public repositories. Vendor demonstration, not a postmortem. Maps to 6, 7, 4.6.
  Not re-opened this pass.

## Named-idea candidates

Strike "Two names on every call" (inaccurate for nested `act`; manufactured). Keep "bind it
below the model" as plain prose, not a named concept. Lean on confused deputy and
authenticated delegation.

## Carrier

- **Repricer:** two overlapping runs on one listing (items 1, 2). The primary code surface.
- **Listing Studio:** multi-tenant catalog for isolation (3); a source sheet carrying personal
  data reaching prompts and traces (4). "Supplier contact details" is not in the carrier
  bible; proposed amendment if kept, else use a generic "contact fields".
- Other surfaces: one-sentence contrasts at most.

## Sources

- PostgreSQL, "Explicit Locking" (13.3.5) and "Row Security Policies" (opened 2026-11-28).
- PgBouncer, Features (opened): SET/RESET not supported under transaction pooling.
- Kleppmann, "How to do distributed locking," 8 Feb 2016.
- Hardy, "The Confused Deputy," ACM SIGOPS OSR 22(4), Oct 1988, pp. 36-38,
  doi:10.1145/54289.871709 (record only; paper text not opened).
- RFC 8693 OAuth 2.0 Token Exchange, Jan 2020 (Jones, Nadalin, Campbell, Bradley, Mortimore).
- MCP Security Best Practices, spec 2025-11-25 (opened); sibling 2.4 cites the same revision.
- OWASP LLM02:2025; OWASP Top 10 for Agentic Applications for 2026, 9 Dec 2025 (list opened;
  ASI03 body text not opened).
- South, Marro, Hardjono, Mahari, Whitney, Greenwood, Chan, Pentland, "Authenticated
  Delegation and Authorized AI Agents," arXiv:2501.09674, v1 16 Jan 2025 (opened; the arXiv
  page names no venue, so no venue is claimed).
- Presidio docs (presidio.dataprivacystack.org). Invariant Labs, 26 May 2025.
- Google Cloud Threat Intelligence, Salesloft Drift report (opened, 28 Aug update).

## Open questions for the author

1. Chapter verdict: single **Emerging**, or split Standard (locks, tenant isolation) /
   Emerging (agent identity and delegation)? Recommend the split.
2. Three pillars in one chapter is dense; keep at about 2,500 words, or split identity out?
3. Keep "supplier contact details" (bible amendment) or use generic contact fields?
4. Cite Asana only as "crossed tenants" until its own disclosure is found?

## Map review (Stage 1.5)

Reviewed by a second engine. Dispositions:

1. Alias line cited a source that was not an opened primary source: accepted; line removed, NHI and Agent IAM dropped as unverified.
2. Locks across LLM pauses: accepted; items 1 and 2 rewritten (no transaction across a model call, OCC, leases with fencing).
3. Unopened sources: accepted-modified; South authors fixed and "ICML oral" removed (arXiv page names no venue, so the reviewer's "Position Paper Track" is also unclaimed); MCP moved to 2025-11-25 (opened); Drift 28 August scope added (opened); Asana contradiction fixed but its page still unopened; "ASI03 &" change rejected, OWASP's post uses "&"; Hardy still record-only.
4. Missing thesis, litmus, budget, grounding, open questions: accepted; all added.
5. Missing PII provider boundary, pre-retrieval ACLs, failure-return contract, IETF drafts: accepted-modified; first three added; RFC 9728 and ID-JAG drafts not opened, so not cited.
6. Bloat and seam collisions: accepted; identity merged to three items, seams clarified, 2.6, 5.2, 1.5 added (plain text, no links).
7. Overclaimed verdicts: accepted; agent-specific items downgraded, uncited Contested claim removed, split proposed.
8. Everyday-engineer sweep: accepted-modified; PgBouncer SET gap verified; SDK default trace logging and placeholder mangling kept as gotchas to confirm against SDK docs in Stage 2.
9. Carrier contradictions: accepted; helpdesk tickets removed, one primary surface, bible amendment flagged.
10. apiKeyHelper anchor: accepted-modified; dropped, MCP consent-flow anchor proposed, client unconfirmed.
11. Alias sweep: accepted-modified; sub-mechanisms separated, redaction vs anonymisation distinguished; extra aliases (OBO, least agency, NHI) lack opened sources, not added.
12. Weak named ideas: accepted; "Two names on every call" struck.
13. Citation precision: accepted-modified; OWASP scenario 2 added, 7.1/7.3 and 1.5 aligned; Presidio stewardship wording and exact PostgreSQL page URLs left for Stage 2.

## Stage 1.6 orchestrator rulings (conservative defaults; author confirms in the PR)

**Budget:** pattern chapter, up to 2,800 prose words.

1. **Scope:** one chapter with three pillars: locks, PII, identity. Identity is not split out.
2. **Verdict:** a single headline of Emerging, with the split argued in prose: Standard for locks and tenant isolation, Emerging for agent identity and delegation.
3. **Code:** a new `listing-studio/concurrency/` package, in memory and offline:
   - a lease with a fencing token, where a stale holder's write is rejected;
   - an optimistic-concurrency version check;
   - a small redaction helper that strips PII fields before a trace or prompt.

   The Postgres advisory lock appears as an SQL listing in prose only; it is not executed.
4. **Carrier:** generic contact fields only. Do not add "supplier contact details" to the carrier bible.
5. **Asana:** describe it only as an incident that "crossed tenants", from the secondary reports the map lists, hedged. No figures.
6. **ASI03 title:** use the "&" form.
7. **No From-production callout.** No new alias line.

## Reconcile log (Stage 5)

Findings from prose QA, the fact check and the cold read.

Prose critic:

1. Closing aphorism in In short: fixed; cut.
2. Four checks restated five times: fixed; the list in "Why" cut to its first sentence, alt text trimmed to describe the picture.
3. "I rate the chapter as a whole emerging": fixed; deleted with "So the maturity splits". The meta line carries the verdict.
4. Callout titled "In Listing Studio" but describing the repricer: fixed; retitled "In the repricer", named as the sibling agent, and "repricer" used from the opening on.
5. "Six stores" against a list of seven: fixed; "every one of those stores".
6. Uncited "models drop and invent placeholders": softened to a capability claim in the prose and the gotcha.
7. Alt text that argues: fixed; trimmed, closing sentence cut.
8. "Matters more than anything": fixed; replaced with the reason (only the store sees the stale token).
9. Two "X without Y is a hope/guess" lines: fixed; the gotcha lead made plain.
10. Repeated "what to do and nothing about" shape: fixed; the OCC paragraph says only that the result carries no value, the code comment deleted (source and chapter together).
11. Docstring in "X, not Y" form: fixed; it now describes behaviour (source and chapter together).
12. Self-contradicting PgBouncer `SET` sentence: fixed; says PgBouncer does not track or reset a plain `SET`, so it leaks.
13. Tracer gotcha with no instance: fixed; folded into the PII paragraph as one sentence, gotcha cut.
14. "Two limits keep this honest" signpost: fixed; cut.
15. Hardy detail beyond a read source: softened; body keeps only the paper's central example (a compiler holding write access its invoker lacked), billing-file detail cut, footnote reworded.
16. "Three neighbours" with four links: fixed; "Four neighbours".
17. "Oldest bug in the database book": fixed; replaced with a gloss of what a lost update is.

Fact checker:

18. OWASP LLM02 [^5] cited for the whole list of doors: fixed; the fact-checker's replacement wording and footnote string adopted.
19. Hardy [^9] unverified: softened (see 15).
20. Salesloft "revoke all at once": verified against the GTIG page ("Salesloft, in collaboration with Salesforce, revoked all active access and refresh tokens with the Drift application", 20 Aug 2025); wording kept close to that sentence. "Tokens carried whatever access the integration held" is not stated on the page: cut.
21. Unfootnoted "standard practice" line: rejected; the fact checker rates it defensible as written.
22. Code blocks match source; SQL is illustrative: no action.

Cold reader:

23. Lost update undefined: fixed; glossed at first use.
24. Advisory lock and `hashtext`: fixed; advisory lock glossed as a lock on an application-chosen number, `hashtext` glossed as the hash that yields that number, `$1`/`$2` named.
25. Fencing token used before definition: fixed; defined in the "What it actually is" paragraph.
26. RLS abbreviation: fixed; introduced at first use.
27. `BYPASSRLS` and `FORCE ROW LEVEL SECURITY`: fixed; glossed as a role attribute and a table setting that applies policies to the owner.
28. Covert channel: fixed; glossed.
29. Pseudonymisation: fixed; glossed (anyone holding the mapping can re-link the data).
30. `act` claim and "claim": fixed; claims glossed as the token's signed fields.
31. Token audience: fixed; glossed in the maturity paragraph and tied to the MCP "issued for" rule.
32. Token passthrough: fixed; glossed.
33. Transaction pooling: fixed; glossed.
34. Salesloft Drift used as if known: fixed; named where the incident is first told.
35. `max_locks_per_transaction`: fixed; named as Postgres settings.
36. `Row` described after the listing, `@dataclass` import missing: fixed; both listings now include the import and the OCC listing defines `Row`. Snippet anchors moved in `occ.py` and `lease.py`; tests pass.
37. Session-key fix for agents with no session: fixed; the resume rule restated for a run with no session.
38. No RLS listing, no token-exchange code, no model call in listings: rejected; out of scope for the companion code under the Stage 1.6 code ruling.
39. Listing Studio and carrier terms in the callout: fixed with 4.
40. Long alt text: fixed with 7.
41. OAuth "scope", the lease's `now` parameter, and no companion path or run command: rejected for budget (the chapter sits at the ceiling); scopes are covered by 2.4 MCP, and `now` is the caller's clock, readable from the timeline.
42. Missing-reasoning items (why the `_xact_` form avoids the pause, why surviving a rollback hurts, the conflict-to-leak step, how to tell efficiency from correctness locks, where `SET LOCAL` runs, why post-ranking filtering leaks): rejected for budget; each is either stated in the SQL comment, the `psql` reproduction, the SKU-1 example, Kleppmann's split, or the retrieval paragraph.

Cuts made for budget, so the author sees what was thinned:

- The session-lock-behind-a-pooler gotcha (it repeated the advisory-lock paragraph, which keeps the rule and the `psql` check).
- The "leases and token exchange are overhead you can skip" tail of the when-not-to clause.
- The sentence listing what changed under agents (pause, context fan-out, an actor that follows what it reads), folded into one clause naming the three properties.
- The "redaction step" restatement list in "Why you'd reach for it".
