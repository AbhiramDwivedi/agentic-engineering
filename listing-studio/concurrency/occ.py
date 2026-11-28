"""Optimistic concurrency: write only if the version you read is still current."""
from __future__ import annotations

# --8<-- [start:occ-version-check]
from dataclasses import dataclass


@dataclass
class Row:
    cents: int
    version: int


class VersionedStore:
    def __init__(self):
        self.rows: dict[str, Row] = {}

    def read(self, sku: str) -> Row:
        row = self.rows[sku]
        return Row(row.cents, row.version)

    def write_if_version(self, sku: str, cents: int, expected: int) -> dict:
        """SQL equivalent: UPDATE ... SET version = version + 1 WHERE version = $expected."""
        row = self.rows[sku]
        if row.version != expected:
            return {"ok": False, "error": "conflict", "action": "re-read"}
        self.rows[sku] = Row(cents, row.version + 1)
        return {"ok": True, "version": row.version + 1}
# --8<-- [end:occ-version-check]
