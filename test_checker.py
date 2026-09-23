import pytest

from checker import check_output, evaluate_batch


RULES = {
    "must_include": ["Summary", "Steps"],
    "must_not_include": ["always works"],
    "max_words": 80
}

JSON_RULES = {
    "require_json": True,
    "required_keys": ["summary", "steps"]
}


@pytest.mark.parametrize("text, rules, expected_failures", [
    (
        "Steps:\n1. Read it.",
        RULES,
        [{"category": "structure", "message": "Missing item: Summary"}],
    ),
    (
        "Summary:\nDone.\n\nSteps:\n1. This always works.",
        RULES,
        [{"category": "content", "message": "Forbidden phrase: always works"}],
    ),
    (
        "not json",
        JSON_RULES,
        [{"category": "schema", "message": "invalid JSON"}],
    ),
    (
        '{"summary": "ok"}',
        JSON_RULES,
        [{"category": "schema", "message": "Missing required key: steps"}],
    ),
    (
        "one two three four five six",
        {"max_words": 5},
        [{"category": "length", "message": "Too many words"}],
    ),
], ids=[
    "missing_required_phrase",
    "forbidden_phrase",
    "invalid_json",
    "missing_required_key",
    "word_count_exceeded",
])
def test_single_rule_violation_reported_with_correct_category(text, rules, expected_failures):
    result = check_output(text, rules)
    assert result["passed"] is False
    assert result["failures"] == expected_failures


@pytest.mark.parametrize("text, rules", [
    ("Summary:\nDone.\n\nSteps:\n1. Read it.", RULES),
    ('{"summary": "ok", "steps": []}', JSON_RULES),
], ids=["plain_text_rules", "json_schema_rules"])
def test_passing_output_has_no_failures(text, rules):
    result = check_output(text, rules)
    assert result["score"] == 100
    assert result["passed"] is True
    assert result["failures"] == []


def test_multiple_failures_stack_and_fail_overall():
    text = "This always works. " * 30  # missing both phrases, forbidden phrase present, too long
    result = check_output(text, RULES)

    assert result["passed"] is False
    categories = {f["category"] for f in result["failures"]}
    assert categories == {"structure", "content", "length"}
    assert result["score"] == 100 - 20 - 20 - 20 - 10  # 2 missing + 1 forbidden + length


def test_rules_without_must_include_or_must_not_include_does_not_crash():
    # a rules dict carrying only max_words must not assume the other keys exist
    result = check_output("one two three four five six", {"max_words": 5})
    assert result["failures"] == [{"category": "length", "message": "Too many words"}]


class TestEvaluateBatch:

    def test_tags_each_result_with_output_id_in_order(self):
        outputs = [
            "Summary:\nSteps:\n1. Done.",       # passes
            "Steps:\n1. This always works.",    # missing Summary + forbidden phrase
        ]
        results = evaluate_batch(outputs, RULES)

        assert [r["output_id"] for r in results] == [1, 2]
        assert results[0]["passed"] is True
        assert results[1]["passed"] is False

    def test_on_empty_list_returns_empty_list(self):
        assert evaluate_batch([], RULES) == []
