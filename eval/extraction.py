"""
Answer extraction utilities for FormationEval evaluation pipeline.

Extracts A/B/C/D answers from model responses with pattern tracking.
"""

import re


def strip_thinking(response: str) -> str:
    """
    Remove reasoning/thinking tags from response (for o1/o3/DeepSeek-R1 models).

    These models output their reasoning process in <thinking> or <think> tags
    before providing the final answer.
    """
    response = re.sub(r'<thinking>.*?</thinking>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return response.strip()


def clean_response(response: str) -> str:
    """
    Clean formatting before extraction.

    - Strips thinking tags
    - Converts to uppercase
    - Removes markdown bold/italic around letters
    - Normalizes whitespace
    """
    text = strip_thinking(response).upper()
    # Remove markdown bold/italic around single letters
    text = re.sub(r'\*+([ABCD])\*+', r'\1', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text


def extract_answer(response: str) -> tuple[str | None, str]:
    """
    Extract A/B/C/D from model response with pattern tracking.

    Returns:
        tuple: (answer, pattern_name) where answer is None if extraction fails.

    Examples:
        >>> extract_answer("B")
        ('B', 'first_char')
        >>> extract_answer("The answer is C")
        ('C', 'answer_is')
        >>> extract_answer("I would choose D because...")
        ('D', 'choose')
        >>> extract_answer("B. The porosity increases...")
        ('B', 'letter_period')
        >>> extract_answer("(A)")
        ('A', 'parentheses')
        >>> extract_answer("**B**")
        ('B', 'first_char')
        >>> extract_answer("I think it's probably B")
        ('B', 'end_of_string')
        >>> extract_answer("See explanation above")
        (None, 'failed')
    """
    text = clean_response(response)

    if not text:
        return None, "failed"

    # 1. Direct letter at start (most common for well-prompted models)
    if text[0] in 'ABCD':
        return text[0], "first_char"

    # 2. Pattern matching (order: most specific -> most general)
    patterns = [
        # Explicit answer statements
        (r'CORRECT\s+ANSWER[:\s]+([ABCD])', "correct_answer"),
        (r'ANSWER\s+IS[:\s]+([ABCD])', "answer_is"),
        (r'ANSWER[:\s]+([ABCD])', "answer_colon"),

        # Choice/option statements
        (r'CHOOSE\s+([ABCD])', "choose"),
        (r'CHOICE\s+IS[:\s]+([ABCD])', "choice_is"),
        (r'OPTION\s+([ABCD])', "option"),
        (r'SELECT\s+([ABCD])', "select"),
        (r'GO\s+WITH\s+([ABCD])', "go_with"),

        # Letter with punctuation
        (r'\(([ABCD])\)', "parentheses"),
        (r'\b([ABCD])\)', "letter_paren"),
        (r'\b([ABCD])\.', "letter_period"),
        (r'\b([ABCD]),', "letter_comma"),

        # Letter at boundaries
        (r'^([ABCD])\b', "start_of_string"),
        (r'\b([ABCD])\s*$', "end_of_string"),

        # "is X" pattern (catches "...is B")
        (r'\bIS\s+([ABCD])\b', "is_x"),

        # Last resort: any standalone letter (risky but catches edge cases)
        (r'\b([ABCD])\b(?!.*\b[ABCD]\b)', "standalone"),
    ]

    for regex, pattern_name in patterns:
        match = re.search(regex, text)
        if match:
            return match.group(1), pattern_name

    return None, "failed"


def check_answer(predicted: str | None, correct_index: int) -> bool:
    """
    Check if the predicted answer matches the correct answer.

    Args:
        predicted: Extracted answer letter (A/B/C/D) or None
        correct_index: Correct answer index (0-3)

    Returns:
        True if correct, False otherwise (including if predicted is None)
    """
    if predicted is None:
        return False

    expected = chr(ord('A') + correct_index)
    return predicted == expected


# For testing the module directly
if __name__ == "__main__":
    test_cases = [
        ("B", "B", "first_char"),
        ("The answer is C", "C", "answer_is"),
        ("I would choose D because...", "D", "choose"),
        ("B. The porosity increases...", "B", "letter_period"),
        ("(A)", "A", "parentheses"),
        ("**B**", "B", "first_char"),
        ("I think it's probably B", "B", "end_of_string"),
        ("See explanation above", None, "failed"),
        ("Answer: A", "A", "answer_colon"),
        ("The correct answer is D", "D", "correct_answer"),
        ("<thinking>Let me think about this...</thinking>The answer is B", "B", "answer_is"),
    ]

    print("Testing extraction patterns:\n")
    for response, expected_answer, expected_pattern in test_cases:
        answer, pattern = extract_answer(response)
        status = "PASS" if answer == expected_answer and pattern == expected_pattern else "FAIL"
        print(f"[{status}] Input: {response[:50]!r}")
        print(f"       Expected: ({expected_answer!r}, {expected_pattern!r})")
        print(f"       Got:      ({answer!r}, {pattern!r})\n")
