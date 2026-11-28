"""Check the grader against people before you trust it; pick thresholds from data."""
from __future__ import annotations


# --8<-- [start:evals-calibrate]
def agreement(judge: list[bool], human: list[bool]) -> float:
    return sum(j == h for j, h in zip(judge, human)) / len(human)


def cohens_kappa(judge: list[bool], human: list[bool]) -> float:
    """Agreement beyond what chance alone would give (1 = perfect, 0 = chance)."""
    n = len(human)
    observed = agreement(judge, human)
    p_j, p_h = sum(judge) / n, sum(human) / n
    chance = p_j * p_h + (1 - p_j) * (1 - p_h)
    return 1.0 if chance == 1 else (observed - chance) / (1 - chance)


def trust_judge(judge: list[bool], human: list[bool], min_kappa: float = 0.6) -> bool:
    """Only a judge that clears the bar on a human-labelled slice may grade."""
    return cohens_kappa(judge, human) >= min_kappa
# --8<-- [end:evals-calibrate]


# --8<-- [start:evals-floor]
def choose_floor(slice_: list[tuple[float, bool]], target_precision: float):
    """Lowest confidence floor whose answered items hit the target precision.

    slice_ is (confidence, was_correct) from a labelled sample. Returns None
    if no floor reaches the target: then the classifier should not run alone.
    """
    for floor in sorted({conf for conf, _ in slice_}):
        kept = [ok for conf, ok in slice_ if conf >= floor]
        if sum(kept) / len(kept) >= target_precision:
            return floor
    return None
# --8<-- [end:evals-floor]
