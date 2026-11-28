"""Sniff, route and parse a supplier file into the typed intermediate document.

Code decides the path (a front controller, not LLM routing). No model touches
the raw bytes. Stdlib readers only: CSV feeds and simple HTML spec sheets.
"""
from __future__ import annotations

import csv
import io
from html.parser import HTMLParser
from typing import Callable

from .document import Anchor, Element, IngestResult

MAX_BYTES = 1_000_000   # size cap: refuse before parsing (guardrail)


# --8<-- [start:ingest-sniff]
def sniff(data: bytes) -> str:
    """Classify by content, not by file extension."""
    head = data[:512].lstrip().lower()
    if data.startswith(b"%PDF"):
        return "pdf"
    if data.startswith(b"PK\x03\x04"):
        return "office"          # zip container: convert, don't trust
    if head.startswith((b"<!doctype html", b"<html")):
        return "html"
    try:
        lines = data[:2048].decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return "unknown"
    return "csv" if lines and "," in lines[0] else "unknown"
# --8<-- [end:ingest-sniff]


# --8<-- [start:ingest-csv]
def parse_csv(name: str, data: bytes) -> list[Element]:
    """Read cells with code. Every value keeps its row and column."""
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    if len(set(reader.fieldnames or [])) != len(reader.fieldnames or []):
        raise csv.Error("duplicate column name")
    out: list[Element] = []
    for row_no, row in enumerate(reader, start=2):   # row 1 is the header
        if None in row or None in row.values():   # overflow or missing cells
            raise csv.Error(f"row {row_no} has the wrong number of cells")
        for col, value in row.items():
            out.append(Element(
                kind="field", name=col, value=value,
                anchor=Anchor(file=name, locator=f"row {row_no}, col {col}"),
            ))
    return out
# --8<-- [end:ingest-csv]


class _SpecSheet(HTMLParser):
    """Collect <td> text. Scripts and styles are dropped."""

    def __init__(self) -> None:
        super().__init__()
        self.cells: list[str] = []
        self._skip = 0
        self._buf: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "td":
            self._buf = []

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
        if tag == "td" and self._buf is not None:
            cell = "".join(self._buf).strip()
            if cell:
                self.cells.append(cell)
            self._buf = None

    def handle_data(self, data):
        if self._buf is not None and not self._skip:
            self._buf.append(data)


def parse_html(name: str, data: bytes) -> list[Element]:
    """A two-column spec table becomes label/value elements."""
    p = _SpecSheet()
    p.feed(data.decode("utf-8", errors="replace"))
    out = []
    for i in range(0, len(p.cells) - 1, 2):
        out.append(Element(
            kind="field", name=p.cells[i], value=p.cells[i + 1],
            anchor=Anchor(file=name, locator=f"table cell {i // 2 + 1}"),
        ))
    return out


# --8<-- [start:ingest-route]
def ingest(
    name: str, data: bytes,
    pdf: Callable[[str, bytes], IngestResult] | None = None,
) -> IngestResult:
    """Route by sniffed type. Unparseable input returns a result, not a raise."""
    if len(data) > MAX_BYTES:
        return IngestResult(status="failed", reason="file too large")
    kind = sniff(data)
    try:
        if kind == "csv":
            elements = parse_csv(name, data)
        elif kind == "html":
            elements = parse_html(name, data)
        elif kind == "pdf" and pdf is not None:
            return pdf(name, data)   # split into Pages, then ingest_pages
        elif kind in ("pdf", "office"):
            return IngestResult(status="failed", reason=f"no {kind} reader configured")
        else:
            return IngestResult(status="failed", reason="unrecognised file type")
    except (UnicodeDecodeError, csv.Error) as exc:
        return IngestResult(status="failed", reason=f"unreadable: {exc}")
    if not elements:
        return IngestResult(status="failed", reason="no rows found")
    return IngestResult(status="ok", pages_ok=1, elements=elements)
# --8<-- [end:ingest-route]
