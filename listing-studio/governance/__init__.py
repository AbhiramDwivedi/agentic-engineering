"""Governance record and AI-disclosure label (chapter 8.6)."""
from .disclosure import disclosure_label
from .record import DecisionRecord, RecordWriter

__all__ = ["DecisionRecord", "RecordWriter", "disclosure_label"]
