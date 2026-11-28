"""Offline tests for the outer loop: a scripted fake model, no network."""
from outer_loop.loop import run_outer_loop
from outer_loop.verifier import PriceRules, verify_price

RULES = PriceRules("NV-ALDSWORTH-DM", map_cents=39900, cost_cents=28000, min_margin=0.20)


def scripted(prices):
    seen = []

    def attempt(failures):
        seen.append(list(failures))
        return prices[len(seen) - 1]

    attempt.seen = seen
    return attempt


def test_verifier_map_and_margin():
    assert not verify_price(34900, RULES).ok
    assert verify_price(39900, RULES).ok
    tight = PriceRules("X", map_cents=1000, cost_cents=9000, min_margin=0.20)
    assert "margin" in verify_price(10000, tight).feedback


def test_retry_feeds_failure_back_and_passes():
    fn = scripted([34900, 39900])
    out = run_outer_loop(fn, RULES)
    assert (out.status, out.price_cents, out.attempts) == ("passed", 39900, 2)
    assert fn.seen[0] == [] and "below MAP" in fn.seen[1][0]


def test_attempt_cap_gives_up():
    # different failures each time, so only the cap stops it
    tight = PriceRules("X", map_cents=1000, cost_cents=9000, min_margin=0.20)
    out = run_outer_loop(scripted([500, 9500, 9600, 9700]), tight, max_attempts=3)
    assert out.status == "gave_up" and out.price_cents is None and out.attempts == 3


def test_no_progress_stops_before_cap():
    fn = scripted([34900, 34900, 39900])
    out = run_outer_loop(fn, RULES, max_attempts=5)
    assert out.status == "gave_up" and out.attempts == 2 and len(fn.seen) == 2


def test_model_cannot_overrule_verifier():
    out = run_outer_loop(lambda f: 1, RULES, max_attempts=2)
    assert out.status == "gave_up" and out.price_cents is None
