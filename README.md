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
