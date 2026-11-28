"""Carrier scenario: a bulk supplier ingest run, scripted and offline.

Maya's team ingests a supplier spreadsheet (a few hundred rows; two shown).
The agent reads rows and writes drafts. `publish` touches the live catalog,
so it is not in this session at all. The "draft only" rule is pinned so it
survives compaction, and a spend cap ends the run.
"""
from __future__ import annotations

from .limits import Limits
from .loop import Call, Result, Turn, run
from .policy import Rule, session_tools

ROWS = {
    1: {"supplier_sku": "NV-ALDSWORTH-DM", "title": "Aldsworth Dual-Motor Sit-Stand Desk"},
    2: {"supplier_sku": "NV-PHONECASE-01", "title": "Slim Phone Case"},
}
DRAFTS: dict[str, dict] = {}


def read_supplier_row(row: int) -> dict:
    return ROWS[row]                      # untrusted file content, parsed in a sandbox


def write_draft(supplier_sku: str, title: str, price_cents: int, target: str = "draft") -> dict:
    # A post hook cannot undo a write; that is why the deny rules come first.
    record = {"supplier_sku": supplier_sku, "title": title,
              "price_cents": price_cents, "status": target}
    DRAFTS[supplier_sku] = record
    return record


def publish(supplier_sku: str) -> dict:   # exists in the product, never in this session
    return {"supplier_sku": supplier_sku, "status": "published"}


ALL_TOOLS = {"read_supplier_row": read_supplier_row, "write_draft": write_draft,
             "publish": publish}
RULES = [
    Rule("deny", "write_draft", lambda a: a.get("target", "draft") != "draft"),
    Rule("ask", "write_draft", lambda a: a["price_cents"] > 500_000),
    Rule("allow", "write_draft"),
    Rule("allow", "read_supplier_row"),
]
DRAFT_ONLY = "Write to draft only. Never publish."


def draft_fields_ok(tool: str, result) -> str | None:
    """post_tool hook: the model never sees a draft that fails the field check."""
    if tool == "write_draft" and (result["price_cents"] <= 0 or result["status"] != "draft"):
        return f"bad draft fields for {result['supplier_sku']}"
    return None


class ScriptedModel:
    """Stands in for the model: replays fixed turns, then stops calling tools."""

    def __init__(self, turns: list[Turn]) -> None:
        self.turns = list(turns)

    def __call__(self, messages, tool_names) -> Turn:
        return self.turns.pop(0) if self.turns else Turn("All rows ingested.")


def _turn(name: str, **args) -> Turn:
    return Turn(calls=[Call(name, args)], cost_cents=50)


SCRIPT = [
    _turn("read_supplier_row", row=1),
    _turn("write_draft", supplier_sku="NV-ALDSWORTH-DM",
          title="Aldsworth Dual-Motor Sit-Stand Desk", price_cents=129_900),
    _turn("read_supplier_row", row=2),
    _turn("write_draft", supplier_sku="NV-PHONECASE-01", title="Slim Phone Case",
          price_cents=1_999),
    _turn("publish", supplier_sku="NV-PHONECASE-01"),                    # absent
    _turn("write_draft", supplier_sku="NV-PHONECASE-01", title="Slim Phone Case",
          price_cents=1_999, target="live"),                             # denied
    _turn("write_draft", supplier_sku="NV-ALDSWORTH-DM", title="Desk",
          price_cents=999_900),                                          # ask, declined
    _turn("write_draft", supplier_sku="NV-PHONECASE-01", title="Slim Phone Case",
          price_cents=-1),                                               # post hook
    _turn("read_supplier_row", row=1),                                   # never reached
]


def run_ingest(archive=lambda msgs: None) -> Result:
    messages = [{"role": "system", "content": DRAFT_ONLY, "pinned": True},
                {"role": "user", "content": "Ingest the supplier sheet as drafts."}]
    tools = session_tools(ALL_TOOLS, {"read_supplier_row", "write_draft"})
    return run(ScriptedModel(SCRIPT), tools, RULES, messages,
               Limits(max_steps=20, max_spend_cents=400),
               post=[draft_fields_ok], archive=archive)
