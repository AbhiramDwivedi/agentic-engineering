"""Chapter 3.6 -- planning. Offline: a fake planner_fn stands in for the model;
the provider files are py_compile-checked only (they need API keys)."""
import os
import py_compile

from planning.execute import MAX_REPLANS, StepFailed, run
from planning.plan import ALLOWED_TOOLS, MAX_STEPS, Plan, Step, validate_plan

PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "planning")


def S(tool, arg="x"):
    return Step(tool=tool, arg=arg, why="because")


GOAL = "Launch the Aldsworth Dual-Motor Sit-Stand Desk"


MAP_CENTS = 39900  # $399.00 MAP for the Aldsworth desk


def make_tools():
    def set_price(arg):
        if int(arg) < MAP_CENTS:
            raise StepFailed(f"{arg} is below MAP {MAP_CENTS}")
        return f"price {arg}"

    return {
        "draft_copy": lambda a: "copy drafted",
        "check_map_price": lambda a: "map ok",
        "set_price": set_price,
        "write_email": lambda a: "email drafted",
    }


class FakePlanner:
    """Returns queued plans in order and records every call it receives."""

    def __init__(self, *plans):
        self.plans = list(plans)
        self.calls = []

    def __call__(self, goal, done, failure):
        self.calls.append((list(done), failure))
        return self.plans.pop(0)


def test_valid_plan_passes():
    assert validate_plan(Plan(steps=[S("draft_copy"), S("set_price")])) == []


def test_unknown_tool_rejected_and_nothing_runs():
    ran = []
    tools = {t: (lambda a, t=t: ran.append(t)) for t in ALLOWED_TOOLS}
    hijacked = Plan(steps=[S("draft_copy"), S("email_all_customers")])
    result = run(FakePlanner(hijacked), tools, GOAL)
    assert result.status == "rejected"
    assert ran == []  # validation happens before step one, not per step
    assert "allowlist" in result.log[0]


def test_step_cap_rejected():
    plan = Plan(steps=[S("draft_copy")] * (MAX_STEPS + 1))
    assert any("cap" in p for p in validate_plan(plan))
    assert validate_plan(Plan(steps=[])) == ["plan has no steps"]


def test_success_never_consults_model_again():
    planner = FakePlanner(Plan(steps=[S("draft_copy"), S("check_map_price"), S("set_price", "39900")]))
    result = run(planner, make_tools(), GOAL)
    assert result.status == "done" and result.replans == 0
    assert len(planner.calls) == 1  # one call: the plan, written once


def test_failure_triggers_one_replan_with_context():
    first = Plan(steps=[S("draft_copy"), S("set_price", "34900"), S("write_email")])
    second = Plan(steps=[S("set_price", "39900"), S("write_email")])
    planner = FakePlanner(first, second)
    result = run(planner, make_tools(), GOAL)
    assert result.status == "done" and result.replans == 1
    done, failure = planner.calls[1]
    assert done == ["draft_copy: copy drafted"]
    assert "set_price failed" in failure
    # the old plan's trailing write_email did not run before the new plan
    assert result.log.count("ran write_email") == 1


def test_replan_cap_halts():
    bad = Plan(steps=[S("set_price", "34900")])
    planner = FakePlanner(bad, bad)
    result = run(planner, make_tools(), GOAL)
    assert MAX_REPLANS == 1
    assert result.status == "halted" and result.replans == 1
    assert len(planner.calls) == 2  # never a third


def test_replan_is_validated_too():
    first = Plan(steps=[S("set_price", "34900")])
    bad_second = Plan(steps=[S("delete_listing")])
    result = run(FakePlanner(first, bad_second), make_tools(), GOAL)
    assert result.status == "halted"
    assert "allowlist" in result.log[-1]


def test_provider_files_compile():
    for f in ("planning_langgraph.py", "planning_responses.py", "planning_example.py"):
        py_compile.compile(os.path.join(PKG, f), doraise=True)
