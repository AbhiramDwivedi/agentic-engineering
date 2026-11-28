"""Chapter 5.4 tests: offline, stdlib + declared deps only. Scripted summarizer."""
from compaction.ladder import compact, fake_summarizer, mask_observations, shrink
from compaction.probe import probe
from compaction.scenario import DECISION, PIN, QUESTIONS, build_session
from compaction.state import RunState, render
from compaction.window import Message, estimate_tokens

BUDGET = 120
KEEP = 4


def texts(h):
    return " ".join(m.content for m in h)


def test_session_fixture_size():
    h = build_session()
    assert len(h) == 26
    assert estimate_tokens(h) == 243


def test_pinned_survives_unpinned_decision_lost():
    h = compact(build_session(), fake_summarizer, BUDGET, KEEP, {})
    assert PIN in texts(h)
    assert "27-48" not in texts(h)
    assert estimate_tokens(h) < BUDGET


def test_archive_holds_full_history():
    original, archive = build_session(), {}
    compact(original, fake_summarizer, BUDGET, KEEP, archive)
    assert archive["history"] == [m.model_dump() for m in original]


def test_failed_summarizers_leave_history_unchanged():
    original = build_session()

    def empty(_): return ""
    def boom(_): raise RuntimeError("provider down")
    def refuse(_): return "I'm sorry, I can't summarize this."

    for s in (empty, boom, refuse):
        assert compact(original, s, BUDGET, KEEP, {}) == original


def test_masking_keeps_last_n_and_archive_restores():
    archive = {}
    h = mask_observations(build_session(), 3, archive)
    tools = [m for m in h if m.role == "tool"]
    assert [m.content.startswith("[result masked") for m in tools] == [True] * 9 + [False] * 3
    assert archive["r1"].startswith("row 1:")
    assert "archive key r1" in tools[0].content


def test_probe_fails_without_state_passes_with_state():
    h = compact(build_session(), fake_summarizer, BUDGET, KEEP, {})
    assert probe(h, RunState(), QUESTIONS) == ["What height range do we use for the Aldsworth desk?"]
    state = RunState(decisions={"NV-ALDSWORTH-DM height_range_in": "27-48 (supplier confirmed)"})
    assert probe(h, state, QUESTIONS) == []
    assert "27-48" in render(state).content


def test_masking_alone_keeps_the_decision_when_it_fits():
    h = shrink(build_session(), fake_summarizer, 200, KEEP, {})
    assert estimate_tokens(h) <= 200
    assert DECISION in texts(h)
    assert probe(h, RunState(), QUESTIONS) == []


def test_chapter_scenario_numbers():
    h = build_session()
    assert len(h) == 26 and estimate_tokens(h) == 243
    assert len([m for m in h if m.role == "tool"]) == 12
    assert estimate_tokens(mask_observations(h, 3, {})) == 162
    c = compact(h, fake_summarizer, 120, 4, {})
    assert estimate_tokens(c) == 60
    assert "Summary of 21 earlier messages: supplier rows were ingested and checked." in texts(c)
    assert estimate_tokens(mask_observations(h, 4, {})) == 171
    assert estimate_tokens(shrink(h, fake_summarizer, 200, 4, {})) == 171


def test_trigger_is_the_token_estimate_not_message_count():
    many_short = [Message(role="user", content="ok") for _ in range(50)]
    assert compact(many_short, fake_summarizer, BUDGET, KEEP, {}) == many_short
    one_long = [Message(role="user", content=" ".join(["w"] * 500)), Message(role="user", content="end")]
    assert compact(one_long, fake_summarizer, BUDGET, 1, {}) != one_long
