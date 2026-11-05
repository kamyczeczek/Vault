from scripts.plain_language_meter import generate_items, score_fixture, score_rubric


def test_items_are_generated_from_source_with_known_answers():
    items = generate_items("Alpha matters. Beta follows!")
    assert [item.answer for item in items] == ["Alpha matters", "Beta follows"]
    assert all(item.answer in item.prompt for item in items)


def test_fixture_returns_comprehension_and_fixed_rubric():
    result = score_fixture("Alpha matters.", ["Alpha matters!"])
    assert result["comprehension"] == 1.0
    assert len(result["source_fingerprint"]) == 64
    assert set(result["rubric"]) == {"simplicity", "informativeness", "coherence", "faithfulness"}


def test_empty_rubric_input_is_rejected():
    try:
        score_rubric(" ")
    except ValueError:
        pass
    else:
        raise AssertionError("empty text must be rejected")


def test_empty_source_and_mismatched_responses_fail_closed():
    assert generate_items("") == []
    try:
        score_fixture("Alpha matters.", [])
    except ValueError:
        pass
    else:
        raise AssertionError("mismatched responses must be rejected")
