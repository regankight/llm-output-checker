import json

# --- Rule checking -----------------------------------------------------

def check_output(text, rules):
    """Evaluate a single LLM output against a rules dict.

    Supported rule keys:
      must_include:     list[str] - phrases that must appear
      must_not_include: list[str] - phrases that must not appear
      max_words:        int       - maximum allowed word count
      require_json:     bool      - if True, text must be valid JSON
      required_keys:    list[str] - keys required when require_json is True
    """
    text_lower = text.lower()

    score = 100
    failures = []

    for item in rules.get("must_include", []):
        if item.lower() not in text_lower:
            score -= 20
            failures.append({
                "category": "structure",
                "message": f"Missing item: {item}"
            })

    for item in rules.get("must_not_include", []):
        if item.lower() in text_lower:
            score -= 20
            failures.append({
                "category": "content",
                "message": f"Forbidden phrase: {item}"
            })

    if "max_words" in rules:
        word_count = len(text.split())
        if word_count > rules["max_words"]:
            score -= 10
            failures.append({
                "category": "length",
                "message": "Too many words"
            })

    if rules.get("require_json"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            score -= 20
            failures.append({
                "category": "schema",
                "message": "invalid JSON"
            })
        else:
            for key in rules.get("required_keys", []):
                if key not in parsed:
                    score -= 20
                    failures.append({
                        "category": "schema",
                        "message": f"Missing required key: {key}"
                    })

    return {
        "score": score,
        "passed": len(failures) == 0,
        "failures": failures
    }


# --- Batch evaluation ----------------------------------------------------

def evaluate_batch(outputs, rules):
    """Run check_output on a list of outputs, tagging each with an id."""
    results = []
    for output_id, text in enumerate(outputs, start=1):
        result = check_output(text, rules)
        results.append({"output_id": output_id, **result})
    return results


# --- Demo / test cases -----------------------------------------------------

if __name__ == "__main__":
    text_rules = {
        "must_include": ["Summary", "Steps"],
        "must_not_include": ["always works"],
        "max_words": 80
    }

    # Test case 1: a valid, passing output
    passing_output = """
Summary:
This tool checks whether an LLM answer follows rules.

Steps:
1. Read the answer.
2. Check the rules.
"""

    # Test case 2: fails a normal rule (forbidden phrase)
    failing_rule_output = """
Summary:
This tool checks whether an LLM answer follows rules.

Steps:
1. Read the answer.
2. Check the rules.

This always works.
"""

    # Test case 3: fails JSON/schema validation (missing required key)
    json_rules = {
        "require_json": True,
        "required_keys": ["summary", "steps"]
    }
    failing_schema_output = '{"summary": "Checks rules."}'

    print("1) Passing output:")
    print(check_output(passing_output, text_rules))
    print()

    print("2) Output that fails a normal rule:")
    print(check_output(failing_rule_output, text_rules))
    print()

    print("3) Output that fails JSON/schema validation:")
    print(check_output(failing_schema_output, json_rules))
    print()

    print("Batch evaluation over multiple outputs:")
    outputs = [passing_output, failing_rule_output]
    for result in evaluate_batch(outputs, text_rules):
        print(result)
