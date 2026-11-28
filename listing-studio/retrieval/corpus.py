"""A tiny helpdesk policy corpus and a labeled query fixture (all invented)."""
from __future__ import annotations

from pydantic import BaseModel


class Chunk(BaseModel):
    id: str
    text: str


CORPUS = [
    Chunk(id="refund-window", text="Merchants can request a refund of the monthly plan fee within 14 days of billing."),
    Chunk(id="invoice-download", text="Download invoices from Settings, Billing history. Each invoice lists the plan fee and tax."),
    Chunk(id="listing-rejected", text="A listing is rejected when the title breaks the marketplace style rules. Edit the title and resubmit."),
    Chunk(id="image-specs", text="Product photos must be at least 1000 pixels on the long edge with a plain background."),
    Chunk(id="reset-password", text="To reset your password, choose Forgot password on the sign-in page and follow the emailed link."),
    Chunk(id="add-teammate", text="Owners can invite a teammate from Settings, Team. Teammates cannot see billing."),
    Chunk(id="error-lst-4012", text="Error LST-4012 means the daily listing limit was reached. Try again after midnight UTC."),
]

# (query, id of the chunk that answers it). Paraphrases are deliberate: the
# lexical scorer misses some, the dense scorer misses others.
LABELED_QUERIES = [
    ("how do I get my money back for the subscription", "refund-window"),
    ("refund within 14 days", "refund-window"),
    ("where can I get a copy of my invoice", "invoice-download"),
    ("why was my product listing turned down", "listing-rejected"),
    ("minimum photo size", "image-specs"),
    ("I forgot my login credentials", "reset-password"),
    ("give a colleague access", "add-teammate"),
    ("LST-4012", "error-lst-4012"),
]
