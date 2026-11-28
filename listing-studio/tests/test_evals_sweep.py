"""The seed sweep is deterministic, so its numbers are asserted exactly."""
import pytest
from evals.sweep import expected_rate, sweep


def test_expected_rates():
    assert round(expected_rate("v1"), 3) == 0.694
    assert round(expected_rate("v2"), 3) == 0.731


def test_sweep_values():
    r = sweep()
    assert r["seeds"] == 200
    assert r["winners"] == 2
    assert r["min_gap"] == pytest.approx(-30.0)
    assert r["max_gap"] == pytest.approx(32.5)
    assert r["no_better"] == 0.385
