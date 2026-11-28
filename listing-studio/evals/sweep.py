"""Seed sweep: how often does the gate call a winner when v2 really is better?

Offline and deterministic. Same seeding as example.main: v1 uses `seed`,
v2 uses `seed + 1`.
"""
from __future__ import annotations

from .cases import GOLDEN
from .example import P_PASS, fake_system
from .harness import compare, run_eval


def expected_rate(version: str) -> float:
    """True pass rate implied by the case odds."""
    return sum(P_PASS[version][c.id] for c in GOLDEN) / len(GOLDEN)


def sweep(seeds: range = range(200)) -> dict:
    winners, gaps = 0, []
    for s in seeds:
        v1 = run_eval(fake_system("v1", s), GOLDEN)
        v2 = run_eval(fake_system("v2", s + 1), GOLDEN)
        winners += compare(v1, v2) == "b is better"
        gaps.append((v2.mean - v1.mean) * 100)
    return {
        "seeds": len(gaps),
        "winners": winners,
        "min_gap": min(gaps),
        "max_gap": max(gaps),
        "no_better": sum(g <= 0 for g in gaps) / len(gaps),
    }


def main() -> None:
    r = sweep()
    print(f"expected v1 {expected_rate('v1'):.3f}, v2 {expected_rate('v2'):.3f}")
    print(f"gate called v2 the winner on {r['winners']}/{r['seeds']} seeds")
    print(f"measured gap range {r['min_gap']:+.1f} to {r['max_gap']:+.1f} points")
    print(f"v2 measured no better than v1 on {r['no_better']:.1%} of seeds")


if __name__ == "__main__":
    main()
