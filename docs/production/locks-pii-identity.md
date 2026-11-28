# 8.5 Locks, PII & Identity

*Three old problems an agent makes worse: a model pause turns a short lock into a stall or a stale write, context copies personal data into stores nobody scoped, and a broad credential lets injected text spend your authority. Each is fixed by a check in your code at a boundary the model cannot argue with.*

## Why you'd reach for it

Two copies of a repricer, an agent that adjusts prices against the competition, wake up for the same standing desk: the scheduled run, and a retry of an earlier run that timed out. Both read the price, $399, and both spend a few seconds asking a model what the competition charges. One writes $389, the other writes $379, and because the second write lands last, the desk now sells at $379 though no rule, no person and no single run chose that number.

That is a lost update: two writers read the same value and the later write silently erases the earlier one. Agents take three problems you already know, concurrent writes, personal data and service credentials, and make each one worse through a property of how they run.

**The pause.** A model call holds the run for seconds in the middle of what used to be a millisecond read-and-write. Hold a database transaction open across that call and every waiting run keeps a pooled connection while it waits, so a slow model starves the pool. Release it, and the run writes back a decision made against data that has since changed.

**The copying.** Whatever you put in a prompt goes to the model provider, and usually also into a trace, a tool result, the answer, and anything persisted from the run: a checkpoint, a memory entry, an embedding. A supplier sheet with a contact's name and email in it lands in every one of those stores instead of one, and the trace store was never scoped for personal data.

**The authority.** An agent acts on instructions that arrive as text, and some of that text you did not write. Give it a credential that can reach every tenant, and anything that reaches its context can ask it to spend that credential on someone else's behalf. Security people call this the confused deputy, after Norm Hardy's 1988 paper about a compiler that held write access the user who invoked it lacked.[^9] In August 2025, attackers used compromised OAuth tokens belonging to one sales-chat integration, Salesloft Drift, to export data from many companies' Salesforce instances, and Salesloft and Salesforce responded by revoking every active token for that application.[^11]

The fix in each case is a check that lives in your code, at a boundary the model's output has to cross.

You need this when:

- **More than one run, retry or person can write the same record.** Retries and resumed runs (see 7.1 and 7.3) produce duplicates even when you schedule only one.
- **More than one tenant's data sits behind the agent's tools.**
- **Records carry personal fields the task does not need.** Contact names, emails, phone numbers.
- **The agent calls an API with a credential**, especially one shared across users or tenants.

When none of those hold (one writer, one tenant, no personal data, read-only access), an ordinary transaction and a read-only key are enough.

## What it actually is

These are boundary checks, in your code, between the model's decisions and the systems they touch. Every write is checked against the state it was decided on, using a version number or a fencing token (a number that grows with every new lease, so the store can spot a writer whose lease has lapsed). Every query is filtered by a tenant your code bound from the authenticated request. Personal data is removed or swapped for placeholders before it enters a prompt, a trace or storage. Every outbound call carries a credential scoped to one tenant, one task and a short life, and the audit log can say which run acted, for whom, under which grant.

![On the left, a rounded box is the model, which decides: it picks a price, asks for rows, reads a record and makes a call. Each action crosses a check in your code before reaching the store on the right. The version check refuses a $379 write decided at version 1 because the row is now at version 2, so the run re-reads and the store keeps $389. Queries are filtered by a tenant bound from the signed-in session, so the shared database returns one merchant's rows. A redaction step turns a supplier contact's email into EMAIL_1 before the prompt, the trace and storage. The credential is scoped to one merchant, one task and 15 minutes, naming the merchant as subject and run 4812 as actor, and the pricing API accepts only tokens issued for it.](locks-pii-identity-boundaries.svg)

Your code decides every one of these, and none of it is new engineering. Optimistic concurrency, row-level security, least privilege and token audience checks (an API accepting only tokens issued for it) are standard practice with long documentation behind them. What changed is the load that the pause, the copying and the authority put on them. Locks and tenant isolation are standard. Delegation and per-run credentials for agents are emerging: the vocabulary exists in OAuth, a 2025 position paper argues for extending it to agents,[^8] and the protocol guidance for agent tools is still being revised between dated spec releases.[^10]

Four neighbours get confused with this. [Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md) covers how hostile text gets into context; this chapter caps what that text can spend. [The Harness](../the-unit/the-harness.md) owns what the agent's tools may do on their own machine; this chapter owns the database and credential behind them. [Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md) and [Checkpointing](../reliability/stopping-gracefully.md) create the duplicate and resumed runs and own idempotency keys and replay; this chapter makes the write safe when a duplicate gets through anyway.

## How to do it

### Serialize the write and leave the thinking outside it

Split each step into three parts: read, call the model with no transaction open, then write with a check. The check comes in two forms. For a short read-compare-write, take a transaction-scoped advisory lock in Postgres. An advisory lock sits on a number your application picks, not on a row, and the `_xact_` form ends at commit or rollback.[^1] `hashtext` hashes the key string to that number; `$1` is the SKU and `$2` the new price:

```sql
BEGIN;
SELECT pg_advisory_xact_lock(hashtext('listing:' || $1));
SELECT price_cents, version FROM listings WHERE sku = $1;
-- compare against what the model decided on; milliseconds, no model call in here
UPDATE listings SET price_cents = $2, version = version + 1 WHERE sku = $1;
COMMIT;
```

Use the `_xact_` form. A session-level advisory lock "is held until explicitly released or the session ends," and it survives a rollback.[^1] You can watch this with two `psql` sessions: take `pg_advisory_lock(42)` in one, `ROLLBACK`, and the second still blocks on the same key. Behind a pooler such as PgBouncer in transaction mode (transaction pooling, where the pooler hands the server connection to another client after every transaction), the session a lock belongs to is whichever connection the pool handed you, and PgBouncer lists session-level advisory locks as never supported in that mode.[^4]

The cheaper form needs no lock at all. Optimistic concurrency stores a version with the row, has each run remember the version it read, and makes the write conditional on that version still being current. This is the listing I would start from:

```python
from dataclasses import dataclass


@dataclass
class Row:
    cents: int
    version: int


class VersionedStore:
    def __init__(self):
        self.rows: dict[str, Row] = {}

    def read(self, sku: str) -> Row:
        row = self.rows[sku]
        return Row(row.cents, row.version)

    def write_if_version(self, sku: str, cents: int, expected: int) -> dict:
        """SQL equivalent: UPDATE ... SET version = version + 1 WHERE version = $expected."""
        row = self.rows[sku]
        if row.version != expected:
            return {"ok": False, "error": "conflict", "action": "re-read"}
        self.rows[sku] = Row(cents, row.version + 1)
        return {"ok": True, "version": row.version + 1}
```

In the companion test both runs read version 1. The first write succeeds and moves the row to version 2, and the second gets `{"ok": False, "error": "conflict", "action": "re-read"}`. The conflict result carries no value from the other run, so a model reading it cannot leak a value it was never shown. The run then re-reads and asks the model again.

### Leases and fencing, when a step must own the record

Sometimes the step itself needs ownership across the pause: the run drafts a whole price schedule over several model calls and must be the only one doing so. That calls for a lease, a lock with an expiry. The trap Martin Kleppmann describes is that a lease can expire while its holder is paused (by a garbage collector in his example, by a slow model call in yours), and the holder wakes up still believing it owns the record.[^2] His fix is the fencing token: the store rejects any write carrying a number lower than one it has already seen.

```python
from dataclasses import dataclass


@dataclass
class Lease:
    holder: str
    token: int  # monotonically increasing; larger means newer
    expires_at: float


class LeaseManager:
    def __init__(self, ttl: float = 30.0):
        self.ttl = ttl
        self._last_token = 0
        self._current: Lease | None = None

    def acquire(self, holder: str, now: float) -> Lease | None:
        if self._current and self._current.expires_at > now:
            return None  # someone else still holds it
        self._last_token += 1
        self._current = Lease(holder, self._last_token, now + self.ttl)
        return self._current


class PriceStore:
    """Rejects any write whose token is below the highest token seen."""

    def __init__(self):
        self.prices: dict[str, int] = {}
        self.highest_token = 0

    def write(self, sku: str, cents: int, token: int) -> bool:
        if token < self.highest_token:
            return False  # a newer holder has already written
        self.highest_token = token
        self.prices[sku] = cents
        return True
```

One run, from the companion test, with a 30-second lease:

1. At t=0, `run-a` acquires the lease and gets token 1, then starts a slow model call.
2. At t=10, `run-b` asks for the lease and is refused, because `run-a` still holds it.
3. At t=31, `run-a`'s lease has expired mid-call. `run-b` acquires it and gets token 2.
4. `run-b` writes 1999 cents with token 2. The store records 2 as the highest token and accepts.
5. `run-a` wakes and writes 1500 cents with token 1. The store sees 1 is below 2 and rejects it. The price stays 1999.

The check runs in the store because the paused holder never consults the lease manager again; only the store sees its stale token. The fence guarantees the older holder never overwrites the newer one's write. It does not stop `run-a` writing at t=35 if `run-b` has not written yet; that write lands, and `run-b`'s later write replaces it. Kleppmann separates locks taken for efficiency (avoid duplicate work; an occasional double is tolerable) from locks taken for correctness, and only the second kind needs the fence.[^2] Most agent steps need the first kind plus optimistic concurrency at the write.

### Bind the tenant below the model

The tenant comes from the authenticated request, and your code binds it before the model runs. It never comes from a tool argument the model filled in, because a model can be talked into a different merchant ID as easily as a different price.

Postgres row-level security (RLS) enforces this where the data lives. With RLS enabled and no policy, the table is default-deny: "no rows are visible or can be modified."[^3] A policy such as `USING (tenant_id = current_setting('app.tenant_id')::uuid)` then limits every query, including the ones a tool builds from model output. Set the tenant per transaction, with `SET LOCAL app.tenant_id = ...` or `set_config('app.tenant_id', $1, true)`, inside the same transaction as the query. PgBouncer does not track or reset a plain `SET` under transaction pooling,[^4] so a session-level tenant setting stays on the server connection and leaks to the next client that connection serves.

Retrieval needs the same filter, inside the query, before the vector search ranks anything. Filtering the top results afterwards means another tenant's chunks were already fetched and ranked, and one bug in the filter puts them in context.

### Keep personal data out of what outlives the run

A prompt is one door for personal data. Others include the provider boundary, your traces, tool results and anything you persist from context. The model's answer is one too, and OWASP names output disclosure and retention policy as risks.[^5] Tracing hooks can record full tool inputs and outputs, so redact in your code before a span is written. Minimise first: if the pricing task does not need the supplier contact's name, drop the field before the record enters context. Where the task must refer to a person (a draft email to a supplier, say), swap the value for a placeholder, keep the mapping outside the model's reach, and restore afterwards. The restore needs a check, because a model can drop a placeholder or invent a new one.

<details markdown><summary>The redaction helper and the placeholder round trip (<code>concurrency/redact.py</code>)</summary>

```python
def redact_record(record: dict) -> dict:
    """Drop known personal fields from a structured record before it enters context."""
    return {k: v for k, v in record.items() if k not in PII_FIELDS}


def pseudonymise(text: str) -> tuple[str, dict[str, str]]:
    """Swap emails for placeholders; keep the map outside the model's reach."""
    mapping: dict[str, str] = {}

    def swap(m: re.Match) -> str:
        key = f"<EMAIL_{len(mapping) + 1}>"
        mapping[key] = m.group(0)
        return key

    return _EMAIL.sub(swap, text), mapping


def restore(text: str, mapping: dict[str, str]) -> str:
    """Put real values back, but only if every placeholder survived the model."""
    missing = [k for k in mapping if k not in text]
    if missing:
        raise ValueError(f"model dropped placeholders: {missing}")
    unknown = set(re.findall(r"<EMAIL_\d+>", text)) - set(mapping)
    if unknown:
        raise ValueError(f"model invented placeholders: {sorted(unknown)}")
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text
```

</details>

`PII_FIELDS` is the set `contact_name`, `contact_email`, `contact_phone`, and `_EMAIL` is a plain email regex, so the helper covers those fields and emails only. In the companion test, two emails become `<EMAIL_1>` and `<EMAIL_2>`, the round trip restores them exactly, and a reply that drops one or adds an `<EMAIL_9>` raises an error instead of sending a half-restored message.

A reversible placeholder is pseudonymisation: anyone holding the mapping can link the data back to the person, so treat the mapping table as the most sensitive thing the run holds and never write it to a trace. Detecting personal data in free text is also probabilistic. Presidio, the open-source detector, says that "there is no guarantee that Presidio will find all sensitive information."[^6] Put a detector behind field-level minimisation as a second layer, and keep the minimisation as the control.

### Give the agent a delegated, narrow identity

When the repricer changes a merchant's listing, two parties act, the agent and the merchant it acts for. OAuth token exchange (RFC 8693) has a word for each arrangement. Under impersonation the agent presents the merchant's identity and the logs cannot tell them apart. Under delegation the token's claims, the signed fields that say who it is about and who presents it, name the merchant as subject and the agent in an `act` (actor) claim, and nested `act` claims record a chain of hops.[^7] Delegation is the one you want, because it lets the audit log answer "what did run 4812 do, as whom, under which grant." One shared service account or long-lived key across every tenant reduces that answer to "the agent did it."

Scope each credential to one tenant, one task and a short life. The MCP security guidance (MCP is the protocol many agent clients use to call tools) describes the same shape: start with a minimal scope set, elevate on a specific challenge when a privileged operation is first attempted, and avoid omnibus scopes such as `files:*`, `db:*` and `admin:*`.[^10] It also says servers "MUST NOT accept any tokens that were not explicitly issued for the MCP server," which means checking the token's audience and forbids token passthrough (forwarding a client's token unchanged to another API), and "MUST NOT use sessions for authentication."[^10] Its session fix is to key state by `<user_id>:<session_id>`, with the user ID from the verified token, so a guessed session ID impersonates no one. An agent run with no session applies the same rule on resume: re-check the token before acting, since a grant valid when the run paused may have been revoked since. [MCP](../the-unit/mcp.md) covers the server and transport duties.

When a scope check fails, return a structured denial that says what to do (`{"error": "insufficient_scope", "action": "ask_user"}`) and nothing about what exists. A denial that says "SKU-1 belongs to another merchant" has told the model, and anyone reading its context, that SKU-1 exists. Then test revocation. The Salesloft Drift response was to revoke every active token for one application at once,[^11] and a revocation path you have never run is a guess.

> **In the repricer.** Stockwell's repricer, the sibling agent to Listing Studio, runs every price change through `write_if_version`, and the one job that drafts a full seasonal schedule holds a fenced lease. Tenant context is set per transaction from the merchant's authenticated session, and supplier records pass through `redact_record` before any prompt or trace sees them. Each run gets a token naming the merchant as subject and the repricer as actor, scoped to that merchant's pricing table for fifteen minutes.

## Gotchas

1. **The lock table is finite.** Advisory and regular locks share one memory pool sized by the `max_locks_per_transaction` and `max_connections` settings, and if it runs out the server "will be unable to grant any locks at all."[^1] A lock per listing per run, never released, gets you there on a large catalog.
2. **A lease without a fence stops only honest runs.** If the store does not check the token, nothing stops a paused holder from finishing its write.[^2]
3. **RLS has bypass doors.** Superusers and roles with the `BYPASSRLS` attribute always bypass it, and so do table owners unless the table is set to `FORCE ROW LEVEL SECURITY`, which applies its policies to the owner too.[^3] Have the application connect as a role that is neither. Unique and foreign-key checks bypass RLS too, so a duplicate-key error can reveal that another tenant's row exists; the Postgres docs call this a covert channel, a leak through a side effect instead of through the rows returned.[^3]
4. **Placeholders break on the way back.** A model can rename, merge or invent them. Validate the round trip, as `restore` does, and fail closed.

## In short

Take the model call out of every transaction and make each write conditional on the version it was decided against; reach for a fenced lease only when a step must own a record across several calls. Bind the tenant from the authenticated request and let the database enforce it. Drop personal fields before they enter context, and treat any detector as a second layer. Give each run a delegated credential for one tenant and one task, with a short life and a tested revocation path.

<small class="chapter-meta">**Maturity: Emerging** (locks and tenant isolation are standard; delegation and per-run credentials for agents are not settled) · *Who decides:* your code · *Grounding:* companion repo + research · *Last reviewed:* 2026-11</small>

## Sources

[^1]: PostgreSQL documentation, "Explicit Locking," section 13.3.5 Advisory Locks. <https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS>
[^2]: Kleppmann, M., "How to do distributed locking" (8 February 2016). <https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html>
[^3]: PostgreSQL documentation, "Row Security Policies," section 5.10. <https://www.postgresql.org/docs/current/ddl-rowsecurity.html>
[^4]: PgBouncer, "Features": the SQL feature table lists `SET`/`RESET` and session-level advisory locks as never supported under transaction pooling. <https://www.pgbouncer.org/features.html>
[^5]: OWASP GenAI Security Project, "LLM02:2025 Sensitive Information Disclosure" (covers disclosure through model output, runtime data orchestration and data-retention policy). <https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/>
[^6]: Presidio documentation, home page. <https://presidio.dataprivacystack.org/>
[^7]: Jones, M., Nadalin, A., Campbell, B., Bradley, J., Mortimore, C., "RFC 8693: OAuth 2.0 Token Exchange" (January 2020). <https://www.rfc-editor.org/rfc/rfc8693>
[^8]: South, T., Marro, S., Hardjono, T., Mahari, R., Whitney, C. D., Greenwood, D., Chan, A., Pentland, A., "Authenticated Delegation and Authorized AI Agents," arXiv:2501.09674 (v1, 16 January 2025). <https://arxiv.org/abs/2501.09674>
[^9]: Hardy, N., "The Confused Deputy (or why capabilities might have been invented)," *ACM SIGOPS Operating Systems Review* 22(4), October 1988, pp. 36-38. <https://doi.org/10.1145/54289.871709>. The paper text was not re-read for this chapter; the compiler example is summarised from its common retelling.
[^10]: Model Context Protocol, "Security Best Practices," specification revision 2025-11-25: sections on the confused deputy problem, token passthrough, session hijacking and scope minimization. <https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices>
[^11]: Google Threat Intelligence Group, "Widespread Data Theft Targets Salesforce Instances via Salesloft Drift" (26 August 2025, updated 28 August 2025). The update reports that the "Drift Email" integration's tokens were also used against a very small number of Google Workspace accounts. <https://cloud.google.com/blog/topics/threat-intelligence/data-theft-salesforce-instances-via-salesloft-drift>

## See also

- [4.6 Prompt Injection & the Lethal Trifecta](../craft/prompt-injection.md), for how hostile text reaches the context whose authority this chapter limits.
- [2.6 The Harness](../the-unit/the-harness.md), for permissions and the execution boundary on the agent's own machine.
- [2.4 MCP](../the-unit/mcp.md), for the server and transport side of tool authorization.
- [7.1 Retry & Graceful Degradation](../reliability/which-failures-sink-the-ship.md) and [7.3 Checkpointing](../reliability/stopping-gracefully.md), which create the duplicate and resumed runs these writes must survive.
- [5.2 Retrieval (RAG)](../knowledge/retrieval-rag.md), where the tenant filter has to run before ranking.
- [8.1 Observability](seeing-inside.md), for where traces go and how to redact them.
- [8.6 Governance & Compliance](governance-and-compliance.md), for retention and regulation of the personal data this chapter keeps out of context.
- [1.5 Context Engineering](../foundations/context-engineering.md), for deciding what enters context in the first place.

## Further reading

- Martin Kleppmann, ["How to do distributed locking"](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html): the fencing-token argument in full, with the efficiency-versus-correctness split.
- PostgreSQL, ["Row Security Policies"](https://www.postgresql.org/docs/current/ddl-rowsecurity.html): the reference for policies, bypass roles and the covert-channel warning.
- [RFC 8693, OAuth 2.0 Token Exchange](https://www.rfc-editor.org/rfc/rfc8693): delegation, impersonation and the `act` claim, from the source.
- MCP, ["Security Best Practices"](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices): the current guidance on token passthrough, sessions and scope minimization for agent tools.
- South et al., ["Authenticated Delegation and Authorized AI Agents"](https://arxiv.org/abs/2501.09674): the case for extending OAuth-style delegation to agents.
