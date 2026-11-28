from injection.run import SPEC_SHEET, fake_reader, run_listing


def obeying_planner(prompt):
    return [
        {"tool": "set_price", "price_cents": 19900},
        {"tool": "send_email", "payload": {"title": "x", "cost_cents": 31000}},
    ]


def honest_planner(prompt):
    return [
        {"tool": "set_price", "price_cents": 44900},
        {"tool": "publish", "payload": {"title": "Aldsworth desk", "price_cents": 44900}},
    ]


def test_injected_line_never_reaches_privileged_prompt():
    out = run_listing(SPEC_SHEET, fake_reader, honest_planner)
    assert out["ok"]
    assert "ignore" not in out["prompt"].lower()
    assert "attacker" not in out["prompt"]
    assert out["prompt"].endswith("Certifications: bifma, prop65.")


def test_obeying_model_is_refused_by_code():
    out = run_listing(SPEC_SHEET, fake_reader, obeying_planner)["outcomes"]
    assert out[0] == {"ok": False, "error": "refused: price below MAP", "floor_cents": 39900}


def test_cost_egress_refused():
    out = run_listing(SPEC_SHEET, fake_reader, obeying_planner)["outcomes"]
    assert out[1] == {"ok": False, "error": "refused: fields not allowed to leave",
                      "fields": ["cost_cents"]}


def test_clean_path():
    out = run_listing(SPEC_SHEET, fake_reader, honest_planner)["outcomes"]
    assert all(o["ok"] for o in out)


def test_hijacked_reader_output_is_rejected():
    def bad(raw):
        return {**fake_reader(raw), "set_price": 19900}

    def long_note(raw):
        return {**fake_reader(raw), "note": "x" * 121}

    assert run_listing(SPEC_SHEET, bad, honest_planner) == {
        "ok": False, "error": "reader output rejected: ValidationError"}
    assert not run_listing(SPEC_SHEET, long_note, honest_planner)["ok"]
