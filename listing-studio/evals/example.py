"""Offline demo: two prompt versions, a noisy gate, and a judge with a known bias.

No network. The "system" is a seeded fake whose pass probability differs by
prompt version, so the numbers are reproducible but behave like a model:
the same input does not always give the same answer.
"""
from __future__ import annotations

import random

from .calibrate import agreement, choose_floor, cohens_kappa, trust_judge
from .cases import GOLDEN, EvalCase
from .graders import judge_listing
from .harness import compare, run_eval

# --8<-- [start:evals-fake-system]
# Chance each prompt version gets a case right, by case id.
P_PASS = {
    "v1": dict(zip([c.id for c in GOLDEN], [.95, .6, .7, .5, .8, .6, .5, .9])),
    "v2": dict(zip([c.id for c in GOLDEN], [.95, .7, .8, .5, .8, .6, .6, .9])),
}


def fake_system(version: str, seed: int):
    """A system under test: right with the table's probability, else it
    drops a required attribute (or invents a forbidden one)."""
    rng = random.Random(seed)

    def system(case: EvalCase) -> dict:
        listing = dict(case.required)
        if rng.random() > P_PASS[version][case.id]:
            if case.forbidden:
                listing[case.forbidden[0]] = True
            else:
                listing.pop(next(iter(listing)))
        return listing

    return system
# --8<-- [end:evals-fake-system]

# --8<-- [start:evals-fake-judge]
def lenient_judge(prompt: str) -> str:
    """Known bias: a long listing sounds authoritative, so it passes."""
    listing = prompt.split("Listing:\n", 1)[1]
    return "yes" if len(listing) > 100 or "300" not in listing else "no"


def careful_judge(prompt: str) -> str:
    """Judges the claim, not the length (but only knows to flag 300)."""
    return "no" if "300 lb" in prompt.split("Listing:\n", 1)[1] else "yes"


CRITERION = "States no weight capacity above the supplier's 250 lb."
LONG = "The Aldsworth glides from 25 to 50 inches, remembers four presets, and carries "
# (listing text, human verdict on CRITERION)
LABELLED = [
    ("Dual-motor desk, holds 250 lb.", True),
    ("Dual-motor desk, holds up to 300 lb.", False),
    ("Sit-stand desk, 25-50 in height range.", True),
    ("Desk rated for 300 lb.", False),
    (LONG + "250 lb of gear.", True),
    (LONG + "an impressive 300 lb of gear.", False),
    (LONG + "a heavy 350 lb of gear.", False),
    ("Walnut top, four presets, 250 lb.", True),
]


def judge_verdicts(judge) -> list[bool]:
    return [judge_listing(judge, [CRITERION], text)[CRITERION] for text, _ in LABELLED]
# --8<-- [end:evals-fake-judge]

# 3.2's classifier, as (confidence, was_correct) on a labelled sample.
CLASSIFIER_SLICE = [
    (0.95, True), (0.9, True), (0.9, True), (0.85, True), (0.8, True),
    (0.7, True), (0.65, True), (0.6, True), (0.6, True),
    (0.55, False), (0.5, True), (0.4, False), (0.3, False),
]


# --8<-- [start:evals-example-run]
def main(seed: int = 0) -> None:
    v1 = run_eval(fake_system("v1", seed), GOLDEN)
    v2 = run_eval(fake_system("v2", seed + 1), GOLDEN)
    print(f"v1 {v1.mean:.2f} [{v1.low:.2f}, {v1.high:.2f}]")
    print(f"v2 {v2.mean:.2f} [{v2.low:.2f}, {v2.high:.2f}]")
    print("gate:", compare(v1, v2))

    human = [h for _, h in LABELLED]
    for name, judge in [("lenient", lenient_judge), ("careful", careful_judge)]:
        got = judge_verdicts(judge)
        print(f"{name} judge: agreement {agreement(got, human):.2f}, "
              f"kappa {cohens_kappa(got, human):.2f}, "
              f"trusted {trust_judge(got, human)}")

    print("floor at 95% precision:", choose_floor(CLASSIFIER_SLICE, 0.95))
# --8<-- [end:evals-example-run]


if __name__ == "__main__":
    main()
