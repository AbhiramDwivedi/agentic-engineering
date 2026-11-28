"""Tests for the retrieval chapter (5.2) code. Offline; stdlib + pydantic only.

The three provider files are compile-checked, not executed.
"""
import os
import py_compile

import pytest

from retrieval.corpus import CORPUS
from retrieval.evaluate import recall_at_k
from retrieval.scoring import dense_scores, lexical_scores, rank, rrf
from retrieval.tool import search_docs

PKG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "retrieval")


def _lex(q):
    return rank(lexical_scores(q, CORPUS))


def _dense(q):
    return rank(dense_scores(q, CORPUS))


def _hybrid(q):
    return rrf([_lex(q), _dense(q)])


def test_lexical_finds_literal_terms_but_misses_paraphrase():
    assert _lex("LST-4012")[0] == "error-lst-4012"
    assert _lex("give a colleague access") == []


def test_dense_finds_paraphrase_but_misses_exact_code():
    assert _dense("give a colleague access")[0] == "add-teammate"
    assert _dense("LST-4012") == []


def test_rrf_rewards_agreement():
    fused = rrf([["a", "b", "c"], ["c", "b", "x"]])
    assert set(fused[:2]) == {"b", "c"} and fused.index("a") > 1


def test_hybrid_recall_beats_either_scorer_alone():
    lex, dense, hybrid = (recall_at_k(f) for f in (_lex, _dense, _hybrid))
    assert (lex, dense, hybrid) == (5 / 8, 7 / 8, 1.0)


def test_tool_returns_structured_empty_result():
    r = search_docs("quarterly earnings of the moon")
    assert r.found is False and r.chunks == [] and "do not answer" in r.note


def test_tool_returns_chunks_on_a_hit():
    r = search_docs("refund within 14 days")
    assert r.found and r.chunks[0].id == "refund-window"
    assert len(r.chunks) <= 3


@pytest.mark.parametrize("name", ["retrieval_langgraph", "retrieval_responses", "retrieval_anthropic"])
def test_illustrations_compile(name):
    py_compile.compile(os.path.join(PKG, f"{name}.py"), doraise=True)


def test_found_means_candidates_not_evidence():
    # A query with one familiar word still returns a chunk that cannot answer it.
    r = search_docs("what is the password policy for Canada?")
    assert r.found and [c.id for c in r.chunks] == ["reset-password"]
