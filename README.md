# llm-output-checker
Small QA tool for checking structured LLM output reliability.

Small prototype for validating whether LLM outputs follow required structure and avoid common failure patterns.

## What It Checks

- Required sections or phrases
- Forbidden phrases
- Word-count limits

## Why

LLM outputs can appear fluent while still failing operational requirements.

This project explores lightweight QA checks for structured AI workflows.

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
    "failures": [
        "Forbidden phrase: always works"
    ]
}
```

## Status

Prototype / learning project.

## Future Ideas

- JSON schema validation
- Batch output testing
- Structured scoring
- Multi-output comparison
- Workflow QA pipelines
