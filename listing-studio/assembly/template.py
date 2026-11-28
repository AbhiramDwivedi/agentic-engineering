"""Template-owned assembly: code fixes the layout and the order."""
from __future__ import annotations

from dataclasses import dataclass, field

from .schemas import SectionResult


# --8<-- [start:assembly-template]
@dataclass(frozen=True)
class Slot:
    section_id: str
    heading: str
    required: bool = True


# Code owns the layout. The model never decides what sections exist or in
# what order; it only fills the slots.
LAUNCH_TEMPLATE = [
    Slot("description", "Description"),
    Slot("specs", "Specifications"),
    Slot("bullets", "Highlights"),
    Slot("prop65", "California Prop 65 notice"),
    Slot("faq", "FAQ", required=False),
]


@dataclass
class Assembled:
    text: str
    blocked: list[str] = field(default_factory=list)  # required, not ok
    omitted: list[str] = field(default_factory=list)  # optional, not ok


def assemble(template: list[Slot], results: dict[str, SectionResult]) -> Assembled:
    parts, blocked, omitted = [], [], []
    for slot in template:
        r = results.get(slot.section_id)
        if r is None or r.status != "ok":
            (blocked if slot.required else omitted).append(slot.section_id)
            continue
        ids = ",".join(r.source_ids)
        parts.append(f"## {slot.heading}\n\n{r.body} [src:{ids}]")
    return Assembled("\n\n".join(parts), blocked, omitted)
# --8<-- [end:assembly-template]
