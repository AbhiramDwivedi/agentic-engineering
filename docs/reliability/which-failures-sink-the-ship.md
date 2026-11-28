# 7.1 Retry & Graceful Degradation

*Which failures sink the ship. Sort every failed call before you act on it: retry what could succeed on a second try, fall back to another model when the retries run out, and stop with a clear error when nothing you resend will change the outcome.*

*Also called: retry with backoff, fallback chain.*

## Why you'd reach for it

A timeout tells you when you stopped waiting. It tells you nothing about whether the other side finished the work, and in an agent the other side is often a tool that writes something.

Take a repricing agent, an autonomous loop that watches competitor prices and adjusts a catalog within the merchant's rules. It decides to set the Aldsworth sit-stand desk to $399 and calls its `set_price` tool. The tool writes the new `price_cents` and then its reply arrives late, so the agent's call to it times out. Two things now want to send that call again. Your retry wrapper sees a timeout, which both vendor SDKs retry by default,[^1][^7] and replays it. And if the error reaches the model, the model reads that `set_price` failed and, reasonably, calls it again. Each replay is a second write to a price that was already set, and if a merchandiser, the person who manages the catalog, corrected the price by hand in the meantime, her edit is overwritten by a decision the agent made a minute ago.

Retry logic is old engineering, but three things make it easier to get wrong in an agent. The vendor SDK already retries a failed call before your code sees the error, so a loop you add on top multiplies attempts instead of adding to them: three attempts in each of two layers is nine calls. One status code can mean opposite things: Anthropic's API returns a 429 for a rate limit, which a short wait fixes, and also for a monthly spend cap, which no wait inside a run will fix.[^1] And some of the calls that time out are tool calls with side effects, which the model itself may decide to replay.

The fix has two parts. Every write carries an idempotency key, a unique ID for one intended action that lets the receiver recognise a repeat and return the first result. And every failure is classified first. A transient failure is retried with backoff inside a budget, a timeout only when the call is safe to replay. When the retries run out, the call moves to the next rung of a fallback chain, an ordered list of models, and the answer is labelled degraded. A terminal failure stops the run and says why.

You need this deliberately, beyond the SDK's defaults, when:

- **Your agent calls tools that write.** Prices, tickets, emails, anything a replay would repeat.
- **You run on more than one model** and want to keep answering when one is down or out of quota.
- **A run is long.** A blip at step six of nine should not cost you the first five.
- **You layer retries**, a framework's policy over an SDK's.

The counter-trigger: a single read-only call, behind a user who can press the button again, needs only the SDK's defaults.

## What it actually is

Retry and graceful degradation is the code wrapped around every call that can fail, deciding per failure among three answers. **Retry**: the failure is transient, and the same call may succeed after a wait. **Fall back**: the retries ran out, and another model might still answer. **Stop**: the failure is terminal, because resending the same call will not change the outcome.

![A failed call enters a classifier in your code. Transient failures (408, a 429 rate limit, 5xx, 529, or a timeout on a call that is safe to replay) wait with jittered backoff and loop back to the same call, inside a budget. When those retries are spent, the call falls back one rung to the next model, and the answer is marked degraded. Terminal failures (400, 401, 403, 404, 413, any spend cap, a refusal, max_tokens, context overflow) go straight to a clear error. Every box is your code; the model decides nothing here.](which-failures-sink-the-ship-classify.svg)

The transient set is the familiar one, plus connection failures; Anthropic's 529 `overloaded_error` has an OpenAI counterpart in a 503 "Model temporarily overloaded".[^1][^2] A spend cap is terminal whatever its status code. Some failures arrive with a 200. A refusal, or a response cut off at `max_tokens`, comes back the same way if you resend the identical request, so both are terminal for a plain retry. The remedies Anthropic documents are different requests: a higher `max_tokens` or a continuation for the cut-off, and for most refusals a retry on another Claude model.[^14] Whether your application takes that refusal fallback is a policy decision for 4.4 Guardrails & Safety; shopping a refusal around until some model complies defeats the check that refused. Context overflow, a request longer than the model's context window, stops here too, because the rungs below are smaller models whose windows are no larger. Shrink the context and resubmit (see 5.4 Compaction).

The engineering is the kind Google's *Site Reliability Engineering* book (the SRE book) wrote down in 2016.[^3][^4] What changed is what sits in the slot: a slow dependency billed per token, part of whose traffic is tool calls with side effects.

**Maturity: Standard.** Backoff with jitter, retry budgets, deadlines and idempotency keys are long-standing distributed-systems practice, documented by Google SRE, by AWS and by Stripe.[^3][^5][^6] Two pieces are younger, and both are Emerging. Idempotency keys on agent tools apply Stripe's mechanism to a caller that can decide on its own to replay, which is reasoned practice more than measured practice. Automatic failover across providers is Emerging, because conversation state and caches stay with the provider.

3.7 The Outer Loop also retries, but for quality: the answer came back and failed a check. Here the call never returned a usable answer, so a verifier that crashes is a failure for this chapter, and a verifier that rejects is an attempt for that one. 7.3 Checkpointing resumes a run after the process dies, and owns graceful shutdown; this chapter keeps the run answering while its dependencies fail.

## How to do it

Start with the classifier and the error it reads. `ProviderError` is what your adapter raises: a thin layer per provider that turns that SDK's exceptions, and any 200 you cannot use, into one shape.

```python
@dataclass
class ProviderError(Exception):
    """What a provider adapter raises, on an error status or on a 200 it cannot use."""
    code: int | str  # HTTP status, or the stop reason on a 200 ("max_tokens")
    kind: str = ""  # provider error type, e.g. "rate_limit_error", "timeout"
    detail: str = ""  # provider error code, e.g. "credit_balance_exhausted"
    retry_after: float | None = None  # seconds, from the retry-after header


TRANSIENT = "transient"  # the same call may succeed after a wait
TERMINAL = "terminal"    # resending the same call will not help

SPEND_CAPS = {
    "enforced_spend_limit_reached",  # Anthropic
    "credit_balance_exhausted", "organization_spend_limit_exceeded",  # OpenAI
    "project_spend_limit_exceeded", "organization_usage_limit_exceeded",
}


def classify(err: ProviderError, idempotent: bool = True) -> str:
    # A 429 has two meanings: a rate limit passes, a spend cap does not.
    if err.kind == "insufficient_quota" or err.detail in SPEND_CAPS:
        return TERMINAL
    if err.kind == "timeout":
        # Unknown outcome: replay only a call that is safe to repeat.
        return TRANSIENT if idempotent else TERMINAL
    if err.code in (408, 429, 500, 502, 503, 504, 529):
        return TRANSIENT
    # 400, 401, 403, 404, 413, a refusal, max_tokens, context overflow
    return TERMINAL
```

The spend-cap check runs first because it shares a status code with the rate limit. OpenAI returns its billing errors as 429s, with `insufficient_quota` as the error type and the specific cause, such as `credit_balance_exhausted`, as the error code, and says retrying them won't restore access.[^2] A timeout is retried only when `idempotent` is true: a model call, or a write that carries a key. A write without a key passes `idempotent=False`, and its timeout stops the run as an unknown outcome for a person to check. Anything unrecognised falls through to terminal, the safe direction: an unknown error that stops the run gets a person's attention. A 409 is left out on purpose. Anthropic's SDK retries it,[^1] but a conflict is transient only when it is a lock that will release, which only the adapter knows.

The retry wrapper calls the classifier on every failure and retries only the transient ones:

```python
class RetryBudget:
    """Per-client cap: retries may use at most `ratio` of recent calls (SRE ch. 21)."""

    def __init__(self, ratio: float = 0.1, floor: int = 3):
        self.ratio, self.floor = ratio, floor
        self.calls = 0
        self.retries = 0

    def allow(self) -> bool:
        return self.retries < max(self.floor, self.ratio * self.calls)


def call_with_retry(
    fn: Callable[[], T],
    budget: RetryBudget,
    *,
    idempotent: bool = True,  # False for a write that carries no key
    max_attempts: int = 3,
    base: float = 0.5,
    cap: float = 8.0,
    deadline: float = 30.0,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.monotonic,
    rng: random.Random = random.Random(),
) -> T:
    start = now()
    for attempt in range(1, max_attempts + 1):
        budget.calls += 1
        try:
            return fn()
        except ProviderError as err:
            if classify(err, idempotent) != TRANSIENT or attempt == max_attempts:
                raise  # terminal, or out of attempts: the caller decides
            if not budget.allow():
                raise  # shed load instead of piling on
            wait = err.retry_after
            if wait is None:
                wait = rng.uniform(0, min(cap, base * 2 ** attempt))  # full jitter
            if now() - start + wait > deadline:
                raise  # one deadline for all the waits, not one per attempt
            budget.retries += 1
            sleep(wait)
    raise AssertionError("unreachable")
```

Four rules live in that loop. The wait uses full jitter, a random time between zero and the capped exponential, so that a thousand clients that failed together do not retry together.[^13] A `retry-after` header from the server wins over the computed wait, used exactly as given. The budget counts retries against every call that passes through it. The 10% is Cuervo's per-client rule from the SRE book: retry only while retries stay below 10% of requests.[^3] The floor of three is the listing's own choice, so that a quiet client can still retry. When the budget is spent the error goes straight up, so in an outage the client sheds load instead of multiplying it. The listing's counter never resets; a production budget counts over time, like the SRE book's example of 60 retries per minute per process.[^4] Last, one deadline covers all the attempts and waits on a rung, in place of a fresh timeout per attempt, after the SRE book's deadline propagation.[^4] It bounds the waiting only. Each attempt's own timeout stays with the HTTP client, and the fallback chain starts a fresh deadline on each rung, so a deadline for the whole run has to be passed down by the caller.

In the tests, a `retry_after` of 7.0 produces a sleep of exactly 7.0 seconds; one that would overshoot the 30-second deadline raises after a single call. A spend-cap 429 is one call, with no retry and no fallback. A timed-out write with no key is one call. Ten failing calls through one budget get exactly three retries.

When retries are spent, the fallback chain takes over. Each rung is a model and the function that calls it, tried in order. The chain is for model answers, which write nothing and so are safe to replay:

```python
def answer_with_fallback(
    prompt: str,
    chain: list[tuple[str, Callable[[str], str]]],
    budget: RetryBudget,
    **retry_kwargs,
) -> Answer:
    last: ProviderError | None = None
    for i, (model, call) in enumerate(chain):
        try:
            text = call_with_retry(lambda: call(prompt), budget, **retry_kwargs)
            return Answer(text, model, degraded=i > 0)
        except ProviderError as err:
            if classify(err) == TERMINAL:
                raise  # terminal: stop, do not shop the call around
            last = err  # retries spent: try the next rung
    raise last  # every rung failed: stop and say so
```

One answer through a two-rung chain, with the primary model overloaded:

1. The primary returns a 529. The classifier calls it transient; the wrapper waits a random time under a second and calls again.
2. A second 529, a jittered wait of up to two seconds, a third call.
3. A third 529. Three attempts are spent, so the wrapper raises.
4. The error is not terminal, so the chain moves to the second rung, a smaller model from the same provider.
5. The smaller model answers. The result comes back as `Answer(text, model, degraded=True)`.

A spend cap at step 1 would have ended the run there, because another rung bills the same account. The ladder can extend past models: a cached or templated answer, then queueing the request and telling the user when to expect it, then a clear failure. Every rung below the first sets `degraded`, and the interface shows it: when the shopper assistant, the storefront's chat agent, answers from a smaller model, the shopper should be able to tell.

For the duplicate write, the repricer's `set_price` tool takes a key built from the run and the step, so every replay of the same step carries the same key:

```python
class IdempotentTool:
    def __init__(self, store: PriceStore):
        self.store = store
        self.seen: dict[str, str] = {}  # key -> first result, replayed after

    def set_price(self, run_id: str, step: int, sku: str, price_cents: int) -> str:
        key = f"{run_id}:{step}"  # same run and step, same key, on every replay
        if key in self.seen:
            return self.seen[key]  # the write already ran; return its result
        self.store.set_price(sku, price_cents)
        self.seen[key] = f"{sku} set to {price_cents}"
        return self.seen[key]
```

In the test, a call and its replay return the same string and the store records one write; a new step makes a second write. The tool records the key after the store returns, so it covers a write that landed while its reply was lost. It is a sketch. The check and the write are separate steps, so two concurrent calls with one key can both write; a key reused with a different price returns the old result; and an in-memory dict is lost on restart. A real key travels down to whatever commits the write and is kept there durably. Stripe's API is the shape: the server saves the first response to an `Idempotency-Key`, including a 500, replays it to any retry with that key, returns an error if a retry's parameters differ, and may prune keys once they are 24 hours old.[^6]

That leaves the second replay, the model's. A tool failure that code can fix, a timeout or a dropped connection, should be retried in code with the same key, so the model never sees it. If the timeout does reach the model, its re-call is a new step with a new key, because the agent loop counts the steps, and the test shows that makes a second write. So the error has to say the write may already have landed and the model should check before trying again. A failure only the model can fix, such as a SKU that does not exist, goes to the model as a short error it can act on. Anthropic marks a failed tool call with `is_error: true` on the tool result, and the Model Context Protocol (MCP) uses `isError`.[^8][^9] Each error costs context, so cap the model's attempts. The 12-Factor Agents guide suggests escalating to a person after a run of consecutive errors on one tool, about three in its example, and Anthropic's tool docs advise limiting how many retries the loop allows.[^10][^8]

#### Wiring it to a provider

The OpenAI Python SDK retries connection errors, 408, 409, 429 and 5xx twice by default with a short exponential backoff, and times out after ten minutes; `max_retries` changes the count and 0 turns retries off.[^7] Anthropic's SDK retries the same statuses and follows the server's `x-should-retry` header when it sends one.[^1] LangGraph's `RetryPolicy`, which you attach to a node, defaults to three attempts with jitter on.[^11] Give a node that policy on top of the OpenAI defaults and it makes up to 3 x 3 = 9 calls, and the SRE book shows three layers of four attempts each reaching 64 calls at the bottom for one request.[^4]

One layer owns retry. If you use `call_with_retry`, construct the client with `max_retries=0` and give the framework no retry policy. The adapter then carries the server's retry headers through, as Anthropic asks of any client that retries without its SDK: `retry-after` into `retry_after`, and an `x-should-retry: false` into an error the classifier stops on, such as `code="no_retry"`.[^1] If you would rather keep the SDK's retries, delete the wrapper and keep the rest: the classifier, the fallback chain, the budget and the keys.

## Gotchas

1. **A timeout is an unknown outcome.** The call may still be billed and the write may still commit. Streams make this sharper: an error can arrive after the API has returned a 200 and sent part of the answer, and Anthropic's SDK does not retry an error in a stream.[^1] The adapter has to classify that error from the stream's error event, since the status is still 200. Discard partial output from a call that writes; for a prose answer, show it only if it is labelled as degraded.

2. **Silent substitution.** A degraded answer passed off as the full one is a bug no happy-path test will catch. Label it, log it, and run the fallback rungs on purpose in tests, because a rung that only runs during an outage is first exercised when you can least afford it to break.

3. **Cross-provider failover leaves its state behind.** Conversation state the provider holds for you, such as OpenAI's `previous_response_id`, means nothing to another vendor, so failover only works if your application owns the message history (see 5.1 State, Not Memory). The prompt cache does not travel either, so expect the first calls after a failover to pay for uncached input. And the other model behaves differently on your task, so evaluate a fallback model on your own cases before it takes traffic (choosing models is the subject of 8.2 Which Model?).

4. **Retrying into an outage.** When a provider is down, clients retrying in lockstep keep it down. A circuit breaker stops calling after repeated failures, then lets a trial call through after a pause: closed, open, half-open.[^12] Keep one per provider or per model. A breaker held in one process does not share state with other workers, and at low volume a handful of failures can trip it on noise.

5. **"Self-healing" with no bound.** Feeding every error back to the model and letting it try again looks like self-healing. Without a cap it spends tokens on a failure no reasoning will fix, such as a spend cap or a missing permission. The classifier is the cheap way to make sure the model only sees errors it could act on. Retrying a failure without asking whether it could succeed is listed in the [Anti-Patterns Catalog](../catalogs/anti-patterns.md).

## In short

Retry only what could succeed. Put the classifier in front of every model and tool call, let one layer own retry and turn the others off, give every write a key derived from the run and the step, and label every degraded answer. When the classifier says terminal, stop and say why: a clear failure at step one is cheaper than nine steps of tokens billed against a spend cap, or a price written twice.

<small class="chapter-meta">**Maturity: Standard** (backoff, budgets, deadlines and idempotency keys are long-standing distributed-systems practice; keys on agent tools and cross-provider failover are Emerging) · *Who decides:* your code · *Grounding:* research + companion repo · *Last reviewed:* 2026-11</small>

## Sources

[^1]: Anthropic, "Claude API errors." <https://platform.claude.com/docs/en/api/errors>
[^2]: OpenAI, "Error codes." <https://developers.openai.com/api/docs/guides/error-codes>
[^3]: Cuervo, A. F., "Handling Overload," ch. 21 of Beyer, B., et al. (eds.), *Site Reliability Engineering* (O'Reilly, 2016). <https://sre.google/sre-book/handling-overload/>
[^4]: Ulrich, M., "Addressing Cascading Failures," ch. 22 of Beyer, B., et al. (eds.), *Site Reliability Engineering* (O'Reilly, 2016). <https://sre.google/sre-book/addressing-cascading-failures/>
[^5]: Brooker, M., "Timeouts, retries, and backoff with jitter," Amazon Builders' Library (2019). <https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/> The URL now redirects to builder.aws.com.
[^6]: Stripe, "Idempotent requests," API v1 reference. <https://docs.stripe.com/api/idempotent_requests>
[^7]: OpenAI, openai-python README, "Retries" and "Timeouts." <https://github.com/openai/openai-python>
[^8]: Anthropic, "Handle tool calls." <https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls>
[^9]: Model Context Protocol, "Tools," specification 2025-06-18. <https://modelcontextprotocol.io/specification/2025-06-18/server/tools>
[^10]: HumanLayer, "Factor 9: Compact errors into context window," *12-Factor Agents*. <https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md>
[^11]: LangGraph, `RetryPolicy` in `langgraph/types.py` (source). <https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/types.py>
[^12]: Fowler, M., "Circuit Breaker" (6 March 2014). <https://martinfowler.com/bliki/CircuitBreaker.html>
[^13]: Brooker, M., "Exponential Backoff And Jitter," AWS Architecture Blog (2015). <https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>
[^14]: Anthropic, "Stop reasons and fallback." <https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons>

## See also

- [2.1 Tool Use](../the-unit/tool-use.md), where a failing tool hands the model an error it can act on.
- [2.2 Structured Output](../the-unit/structured-output.md), for re-asking when the output fails its schema.
- 4.3 Human-in-the-Loop, for where an escalated error goes when the model's attempts run out.
- 8.7 Deployment & Runtimes, for supervisors that restart what this chapter could not save.
- 2.5 The Agent Loop and 2.6 The Harness, for what the model does with an error.
- 7.2 Observer, for seeing degraded answers and tripped breakers in production.
- 8.4 Controlling Cost, for pricing the fallback rungs.
