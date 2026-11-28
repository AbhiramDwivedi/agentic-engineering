"""Check that the model's confidence means something before you pick a threshold."""
from __future__ import annotations


# --8<-- [start:dm-calibrate]
def calibrate(rows: list[tuple[float, bool]], bins: int = 5) -> dict:
    """rows: (P(true) the model gave, whether it was actually true).

    Returns expected calibration error (ECE) and the lowest confidence threshold
    above which every prediction on this fixture was correct.
    """
    n = len(rows)
    ece = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        cell = [(p, y) for p, y in rows if lo <= p < hi or (b == bins - 1 and p == 1.0)]
        if cell:
            conf = sum(p for p, _ in cell) / len(cell)
            acc = sum(y for _, y in cell) / len(cell)
            ece += len(cell) / n * abs(conf - acc)
    best = None
    for t in sorted({max(p, 1 - p) for p, _ in rows}):
        sure = [(p, y) for p, y in rows if max(p, 1 - p) >= t]
        if all((p >= 0.5) == y for p, y in sure):
            best = t
            break
    return {"ece": ece, "threshold": best}
# --8<-- [end:dm-calibrate]
