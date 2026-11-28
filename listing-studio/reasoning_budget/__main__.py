"""Run the scripted sweep: python -m reasoning_budget (offline, invented numbers)."""
from __future__ import annotations

# --8<-- [start:sweep-main]
from .scripted import CASES, exact_match, scripted_model
from .sweep import bill, cheapest_passing, run_sweep


def main() -> None:
    reports = run_sweep(scripted_model, CASES, exact_match, cap=5000)
    print(bill(reports))
    pick = cheapest_passing(reports)
    print("ship:", pick.level if pick else "nothing reaches the floor")


if __name__ == "__main__":
    main()
# --8<-- [end:sweep-main]
