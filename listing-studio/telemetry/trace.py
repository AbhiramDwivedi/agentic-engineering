"""A minimal span tracer: parent-linked spans, a sink, and a redacting exporter.

Self-contained on purpose (stdlib only, no OpenTelemetry install, no dependency on
7.2's observer/). telemetry_otel.py shows the same shape on the real SDK.
"""
from __future__ import annotations

import itertools
import re
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Protocol


# --8<-- [start:telemetry-span]
@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_id: str | None
    attributes: dict[str, Any] = field(default_factory=dict)


class Sink(Protocol):
    def export(self, span: Span) -> None: ...


_current: ContextVar[Span | None] = ContextVar("current_span", default=None)
_ids = itertools.count(1)


@contextmanager
def span(sink: Sink, name: str, **attributes: Any) -> Iterator[Span]:
    parent = _current.get()  # the open span, if any, becomes this span's parent
    s = Span(
        name=name,
        trace_id=parent.trace_id if parent else f"trace-{next(_ids)}",
        span_id=f"span-{next(_ids)}",
        parent_id=parent.span_id if parent else None,
        attributes=dict(attributes),
    )
    token = _current.set(s)
    try:
        yield s
    finally:
        _current.reset(token)
        try:
            sink.export(s)  # exported even when the body raised
        except Exception:
            pass  # a broken exporter costs the span, never the run
# --8<-- [end:telemetry-span]


class InMemorySink:
    """Test sink: keeps every exported span in order."""

    def __init__(self) -> None:
        self.spans: list[Span] = []

    def export(self, span: Span) -> None:
        self.spans.append(span)


# --8<-- [start:telemetry-redact]
CONTENT_KEYS = ("gen_ai.input.messages", "gen_ai.output.messages", "tool.arguments")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def scrub(text: str) -> str:
    return EMAIL.sub("[contact]", text)


class RedactingSink:
    """Wraps a real sink. Content is scrubbed here, in your process, before export."""

    def __init__(self, inner: Sink, redact: Callable[[str], str] = scrub) -> None:
        self.inner = inner
        self.redact = redact

    def export(self, span: Span) -> None:
        try:
            for key in CONTENT_KEYS:
                if key in span.attributes:
                    span.attributes[key] = self.redact(str(span.attributes[key]))
        except Exception:
            # Fail closed: a broken redactor must not crash the run, and must
            # not let unredacted content out. Drop the content, keep the ids.
            for key in CONTENT_KEYS:
                span.attributes.pop(key, None)
        self.inner.export(span)
# --8<-- [end:telemetry-redact]
