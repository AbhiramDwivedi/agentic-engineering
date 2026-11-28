"""Strip personal fields before text reaches a prompt or a trace; round-trip placeholders."""
from __future__ import annotations

import re

PII_FIELDS = {"contact_name", "contact_email", "contact_phone"}
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


# --8<-- [start:pii-redact]
def redact_record(record: dict) -> dict:
    """Drop known personal fields from a structured record before it enters context."""
    return {k: v for k, v in record.items() if k not in PII_FIELDS}


def pseudonymise(text: str) -> tuple[str, dict[str, str]]:
    """Swap emails for placeholders; keep the map outside the model's reach."""
    mapping: dict[str, str] = {}

    def swap(m: re.Match) -> str:
        key = f"<EMAIL_{len(mapping) + 1}>"
        mapping[key] = m.group(0)
        return key

    return _EMAIL.sub(swap, text), mapping


def restore(text: str, mapping: dict[str, str]) -> str:
    """Put real values back, but only if every placeholder survived the model."""
    missing = [k for k in mapping if k not in text]
    if missing:
        raise ValueError(f"model dropped placeholders: {missing}")
    unknown = set(re.findall(r"<EMAIL_\d+>", text)) - set(mapping)
    if unknown:
        raise ValueError(f"model invented placeholders: {sorted(unknown)}")
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text
# --8<-- [end:pii-redact]
