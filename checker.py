llm_output = """
Summary:
This tool checks whether an LLM answer follows rules.

Steps:
1. Read the answer.
2. Check the rules.

This always works.
"""

rules = {
    "must_include": ["Summary", "Steps"],
    "must_not_include": ["always works"],
    "max_words": 80
}

def check_output(text, rules):

    text_lower = text.lower()

    score = 100
    failures = []

    for item in rules["must_include"]:
        if item.lower() not in text_lower:
            score -= 20
            failures.append(f"Missing item: {item}")

    for item in rules["must_not_include"]:
        if item.lower() in text_lower:
            score -= 20
            failures.append(f"Forbidden phrase: {item}")

    word_count = len(text.split())

    if word_count > rules["max_words"]:
        score -= 10
        failures.append("Too many words")

    return {
        "score": score,
        "failures": failures
    }

result = check_output(llm_output, rules)

print(result)
