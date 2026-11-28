"""Tests for chapter 7.1 companion code. Offline: fake providers, injected clock and RNG."""
import random

import pytest

from resilience.classify import TERMINAL, TRANSIENT, ProviderError, classify
from resilience.fallback import answer_with_fallback
from resilience.idempotent import IdempotentTool, PriceStore
from resilience.retry import RetryBudget, call_with_retry


class Flaky:
    def __init__(self, errors, result="ok"):
        self.errors, self.result, self.calls = list(errors), result, 0

    def __call__(self, *_):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return self.result


def kw(sleeps):
    return dict(sleep=sleeps.append, rng=random.Random(0), now=lambda: 0.0)


def test_classify_codes():
    assert classify(ProviderError(503)) == TRANSIENT
    assert classify(ProviderError(529)) == TRANSIENT
    assert classify(ProviderError(401)) == TERMINAL
    assert classify(ProviderError("max_tokens")) == TERMINAL
    assert classify(ProviderError("refusal")) == TERMINAL
    assert classify(ProviderError("context_overflow")) == TERMINAL  # compact first


def test_two_meanings_of_429():
    assert classify(ProviderError(429, "rate_limit_error")) == TRANSIENT
    assert classify(ProviderError(429, "rate_limit_error", "enforced_spend_limit_reached")) == TERMINAL
    assert classify(ProviderError(429, "insufficient_quota", "credit_balance_exhausted")) == TERMINAL
    assert classify(ProviderError(429, detail="project_spend_limit_exceeded")) == TERMINAL


def test_timeout_retried_only_when_safe_to_replay():
    timeout = ProviderError(0, "timeout")
    assert classify(timeout) == TRANSIENT
    assert classify(timeout, idempotent=False) == TERMINAL
    f = Flaky([ProviderError(0, "timeout")])
    with pytest.raises(ProviderError):
        call_with_retry(f, RetryBudget(), idempotent=False, **kw([]))
    assert f.calls == 1  # an unkeyed write that timed out is not replayed


def test_retries_transient_then_succeeds():
    f, sleeps = Flaky([ProviderError(503)]), []
    assert call_with_retry(f, RetryBudget(), **kw(sleeps)) == "ok"
    assert f.calls == 2 and len(sleeps) == 1 and 0 <= sleeps[0] <= 1.0


def test_three_attempts_then_raises():
    f = Flaky([ProviderError(503)] * 5)
    with pytest.raises(ProviderError):
        call_with_retry(f, RetryBudget(), **kw([]))
    assert f.calls == 3


def test_terminal_not_retried():
    f = Flaky([ProviderError(401)])
    with pytest.raises(ProviderError):
        call_with_retry(f, RetryBudget(), **kw([]))
    assert f.calls == 1


def test_retry_after_honoured():
    f, sleeps = Flaky([ProviderError(429, "rate_limit_error", retry_after=7.0)]), []
    call_with_retry(f, RetryBudget(), **kw(sleeps))
    assert sleeps == [7.0]


def test_deadline_stops_retry():
    f = Flaky([ProviderError(503, retry_after=40.0)])
    with pytest.raises(ProviderError):
        call_with_retry(f, RetryBudget(), deadline=30.0, **kw([]))
    assert f.calls == 1


def test_budget_sheds_retries():
    budget = RetryBudget(ratio=0.1, floor=3)
    for _ in range(10):
        with pytest.raises(ProviderError):
            call_with_retry(Flaky([ProviderError(503)] * 3), budget, max_attempts=2, **kw([]))
    assert budget.retries == 3  # the floor; 10 calls * 0.1 never exceeds it


def test_fallback_to_smaller_model_is_labelled():
    big = Flaky([ProviderError(503)] * 9)
    small = Flaky([], "short copy")
    a = answer_with_fallback("p", [("big", big), ("small", small)], RetryBudget(), **kw([]))
    assert (a.model, a.degraded, big.calls) == ("small", True, 3)


def test_fallback_not_taken_on_terminal():
    big = Flaky([ProviderError(429, "insufficient_quota", "credit_balance_exhausted")])
    small = Flaky([], "x")
    with pytest.raises(ProviderError):
        answer_with_fallback("p", [("big", big), ("small", small)], RetryBudget(), **kw([]))
    assert small.calls == 0


def test_all_rungs_fail_raises():
    chain = [("a", Flaky([ProviderError(503)] * 9)), ("b", Flaky([ProviderError(503)] * 9))]
    with pytest.raises(ProviderError):
        answer_with_fallback("p", chain, RetryBudget(), **kw([]))


def test_replayed_write_does_not_duplicate():
    store = PriceStore()
    tool = IdempotentTool(store)
    first = tool.set_price("run-1", 6, "SKU-1", 1999)
    replay = tool.set_price("run-1", 6, "SKU-1", 1999)  # timed out, so the run replays it
    assert first == replay and store.writes == 1
    tool.set_price("run-1", 7, "SKU-1", 2099)
    assert store.writes == 2
