# llm-output-checker

A small, dependency-free evaluation harness for checking LLM outputs against explicit rules — required content, forbidden content, length limits, and JSON schema — with a numeric score, a pass/fail verdict, and categorized failures.

## What It Checks

- **Structure** — required phrases are present (`must_include`)
- **Content** — forbidden phrases are absent (`must_not_include`)
- **Length** — output stays within a word limit (`max_words`)
- **Schema** — output is valid JSON and contains required keys (`require_json`, `required_keys`)

Every check can run on a single output or across a batch of many, using the same rules.

## Why

LLM outputs can appear fluent while still failing operational requirements — missing a required section, leaking a forbidden phrase, running long, or breaking a structured-output contract a downstream system depends on. This project is a lightweight way to catch that class of failure automatically, without a framework or an external API.

## Usage

```python
from checker import check_output, evaluate_batch

rules = {
    "must_include": ["Summary", "Steps"],
    "must_not_include": ["always works"],
    "max_words": 80
}

check_output(llm_output, rules)
# {"score": 80, "passed": False, "failures": [...]}

evaluate_batch([output_1, output_2, output_3], rules)
# [{"output_id": 1, "score": 100, "passed": True, "failures": []}, ...]
```

## Example

### Input

```text
Summary:
This tool checks whether an LLM answer follows rules.

Steps:
1. Read the answer.
2. Check the rules.

This always works.
```

### Rules

```python
rules = {
    "must_include": ["Summary", "Steps"],
    "must_not_include": ["always works"],
    "max_words": 80
}
```

### Output

```python
{
    "score": 80,
    "passed": False,
    "failures": [
        {
            "category": "content",
            "message": "Forbidden phrase: always works"
        }
    ]
}
```

### Schema validation example

```python
rules = {
    "require_json": True,
    "required_keys": ["summary", "steps"]
}

check_output('{"summary": "Checks rules."}', rules)
# {
#     "score": 80,
#     "passed": False,
#     "failures": [
#         {"category": "schema", "message": "Missing required key: steps"}
#     ]
# }
```

## Design decisions

- **Rule-based, not LLM-as-judge.** Checks are deterministic string/JSON operations, not a model grading another model. That trades semantic nuance (it can't tell if an answer is *good*, only whether it follows the stated rules) for something cheap, fast, and 100% reproducible — the same output always gets the same score. It's meant as a first-pass gate, not a replacement for human or model-graded review.
- **Four failure categories, not a flat list.** `structure` / `content` / `length` / `schema` map to distinct failure modes with different fixes (a prompt problem vs. a hard content violation vs. an output-format break). Categorizing failures makes them filterable and aggregable across a batch, which a flat list of strings isn't.
- **Batch evaluation reuses the single-output path.** `evaluate_batch()` is a thin loop over `check_output()`, not a separate code path — there's exactly one place scoring logic can diverge from itself.
- **No external dependencies at runtime.** `checker.py` itself only uses the standard library (`json`). Keeps the harness runnable anywhere without an install step, and keeps the diff for any future rule type small and auditable.
- **Explicitly out of scope (for now):** a full JSON Schema implementation (only required-key presence, not types/nesting/formats), an LLM-graded judge, a UI, a database, and any external API calls. The goal is a correct, minimal core that's easy to reason about, not a framework.

## Development

Tests use [pytest](https://docs.pytest.org/) (the one non-stdlib dependency in this project, used only for testing — `checker.py` itself stays dependency-free).

```bash
pip install -r requirements-dev.txt
pytest -v
```
