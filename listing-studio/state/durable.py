"""Demo 2: in-memory vs durable checkpointer across a simulated restart.

langgraph-checkpoint-sqlite is the real durable saver, but it is not a
dependency of this repo. FileSaver below is a deliberately tiny stand-in: it is
InMemorySaver plus a pickle file, enough to show the property that matters
(the thread survives a new saver instance). It is not production storage.
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class FileSaver(InMemorySaver):
    """InMemorySaver that writes itself to disk after every checkpoint write."""

    def __init__(self, path: str | Path):
        super().__init__()
        self.path = Path(path)
        if self.path.exists():
            data = pickle.loads(self.path.read_bytes())
            for thread, nss in data["storage"].items():
                for ns, cps in nss.items():
                    self.storage[thread][ns].update(cps)
            for key, w in data["writes"].items():
                self.writes[key].update(w)
            self.blobs.update(data["blobs"])

    def _flush(self) -> None:
        data = {
            "storage": {t: {ns: dict(c) for ns, c in nss.items()}
                        for t, nss in self.storage.items()},
            "writes": {k: dict(w) for k, w in self.writes.items()},
            "blobs": dict(self.blobs),
        }
        self.path.write_bytes(pickle.dumps(data))

    def put(self, *args, **kwargs):
        out = super().put(*args, **kwargs)
        self._flush()
        return out

    def put_writes(self, *args, **kwargs):
        super().put_writes(*args, **kwargs)
        self._flush()


# --8<-- [start:state-durable]
class Run(TypedDict):
    supplier_sku: str
    price_cents: int


def price_node(state: Run) -> dict:
    return {"price_cents": 39900}       # MAP for NV-ALDSWORTH-DM


def build(checkpointer):
    g = StateGraph(Run)
    g.add_node("price", price_node)
    g.add_edge(START, "price")
    g.add_edge("price", END)
    return g.compile(checkpointer=checkpointer)


config = {"configurable": {"thread_id": "listing-NV-ALDSWORTH-DM"}}
# Process 1: build(saver).invoke({"supplier_sku": "NV-ALDSWORTH-DM",
#                                 "price_cents": 0}, config)
# Process 2 (after restart), a new saver over the same storage:
#   build(new_saver).get_state(config).values
#   InMemorySaver(): {}      the thread is gone
#   durable saver:   {"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 39900}
# --8<-- [end:state-durable]


CONFIG = config


def run_once(saver) -> None:
    build(saver).invoke({"supplier_sku": "NV-ALDSWORTH-DM", "price_cents": 0}, CONFIG)


def recover(saver) -> dict:
    return build(saver).get_state(CONFIG).values
