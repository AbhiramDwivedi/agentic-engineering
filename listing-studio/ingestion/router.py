"""Page router: send only the pages that need vision to the vision call.

The vision call is injected. Tests and the chapter use a scripted fake.
"""
from __future__ import annotations

from typing import Callable

from pydantic import BaseModel

from .document import Anchor, Element, IngestResult


# --8<-- [start:ingest-pages]
class Page(BaseModel):
    """One PDF page as a PDF library or layout parser hands it over."""
    number: int
    text: str = ""        # text layer (selectable text); empty on a scan
    tables: list[list[list[str]]] = []   # each table: rows of cells, header first
    has_diagram: bool = False   # set upstream, e.g. the parser found a figure


def needs_vision(page: Page) -> bool:
    """A scan (no text layer) or a dimension diagram needs the vision call."""
    return len(page.text.strip()) < 20 or page.has_diagram


def ingest_pages(
    name: str, pages: list[Page],
    vision: Callable[[Page], dict[str, str] | None],
) -> IngestResult:
    """Code reads text and tables; only flagged pages reach `vision`."""
    if not pages:
        return IngestResult(status="failed", reason="no pages")
    elements: list[Element] = []
    ok = unread = 0
    for page in pages:
        where = f"page {page.number}"
        if needs_vision(page):
            try:
                found = vision(page)
            except Exception:
                found = None
            if not found:            # failed or empty: flag the page, never a silent empty
                unread += 1
                continue
            elements += [
                Element(kind="field", name=label, value=value, read_by="vision",
                        anchor=Anchor(file=name, locator=where))
                for label, value in found.items()
            ]
        else:
            for t, (header, *rows) in enumerate(page.tables, start=1):
                for r, row in enumerate(rows, start=2):   # row 1 is the header
                    for col, value in zip(header, row):
                        elements.append(Element(
                            kind="field", name=col, value=value,
                            anchor=Anchor(file=name, locator=f"{where}, table {t}, row {r}, col {col}"),
                        ))
            if page.text:
                elements.append(Element(
                    kind="text", name="page_text", value=page.text,
                    anchor=Anchor(file=name, locator=where),
                ))
        ok += 1
    status = "ok" if not unread else "partial" if ok else "failed"
    reason = None if not unread else f"{unread} page(s) unread"
    return IngestResult(status=status, reason=reason, pages_ok=ok, elements=elements)
# --8<-- [end:ingest-pages]
