"""
Metrics calculation for FormationEval evaluation pipeline.

Includes accuracy, confidence intervals, breakdowns, and bias analysis.
"""

import math
from collections import defaultdict

from extraction import extract_answer, check_answer


def compute_wilson_ci(n_correct: int, n_total: int, alpha: float = 0.05) -> tuple[float, float]:
    """
    Compute Wilson score confidence interval.

    Args:
        n_correct: Number of correct answers
        n_total: Total number of questions
        alpha: Significance level (default 0.05 for 95% CI)

    Returns:
        Tuple of (lower_bound, upper_bound) as proportions
    """
    if n_total == 0:
        return 0.0, 0.0

    # Use scipy if available, otherwise fallback to approximation
    try:
        from scipy.stats import norm
        z = norm.ppf(1 - alpha / 2)
    except ImportError:
        # z for 95% CI
        z = 1.96

    p = n_correct / n_total
    n = n_total

    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator

    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)

    return lower, upper


def compute_accuracy(responses: list[dict], questions: list[dict]) -> dict:
    """
    Compute overall accuracy metrics.

    Args:
        responses: List of API response dicts with 'question_id', 'raw_response'
        questions: List of question dicts with 'id', 'answer_index'

    Returns:
        Dict with accuracy metrics
    """
    # Build question lookup by id
    q_by_id = {q["id"]: q for q in questions}

    correct = 0
    failed_extractions = 0
    pattern_counts = defaultdict(int)
    results_by_qid = {}

    for resp in responses:
        qid = resp["question_id"]
        q = q_by_id.get(qid)
        if q is None:
            continue

        raw = resp.get("raw_response", "")
        predicted, pattern = extract_answer(raw)
        pattern_counts[pattern] += 1

        is_correct = check_answer(predicted, q["answer_index"])
        if is_correct:
            correct += 1

        if predicted is None:
            failed_extractions += 1

        results_by_qid[qid] = {
            "predicted": predicted,
            "correct": is_correct,
            "raw_response": raw,
            "extraction_pattern": pattern,
        }

    total = len(responses)
    accuracy = correct / total if total > 0 else 0.0
    ci_lower, ci_upper = compute_wilson_ci(correct, total)

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "failed_extractions": failed_extractions,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "extraction_patterns": dict(pattern_counts),
        "results_by_qid": results_by_qid,
    }


def compute_difficulty_breakdown(
    results_by_qid: dict, questions: list[dict]
) -> dict[str, dict]:
    """
    Compute accuracy breakdown by difficulty level.

    Returns:
        Dict mapping difficulty -> {accuracy, correct, total}
    """
    q_by_id = {q["id"]: q for q in questions}
    breakdown = defaultdict(lambda: {"correct": 0, "total": 0})

    for qid, result in results_by_qid.items():
        q = q_by_id.get(qid)
        if q is None:
            continue

        difficulty = q.get("difficulty", "unknown")
        breakdown[difficulty]["total"] += 1
        if result["correct"]:
            breakdown[difficulty]["correct"] += 1

    # Calculate accuracies
    for level, data in breakdown.items():
        total = data["total"]
        correct = data["correct"]
        data["accuracy"] = correct / total if total > 0 else 0.0
        ci_lower, ci_upper = compute_wilson_ci(correct, total)
        data["ci_lower"] = ci_lower
        data["ci_upper"] = ci_upper

    return dict(breakdown)


def compute_domain_breakdown(
    results_by_qid: dict, questions: list[dict]
) -> dict[str, dict]:
    """
    Compute accuracy breakdown by domain.

    Note: Questions can belong to multiple domains.

    Returns:
        Dict mapping domain -> {accuracy, correct, total}
    """
    q_by_id = {q["id"]: q for q in questions}
    breakdown = defaultdict(lambda: {"correct": 0, "total": 0})

    for qid, result in results_by_qid.items():
        q = q_by_id.get(qid)
        if q is None:
            continue

        domains = q.get("domains", [])
        for domain in domains:
            breakdown[domain]["total"] += 1
            if result["correct"]:
                breakdown[domain]["correct"] += 1

    # Calculate accuracies
    for domain, data in breakdown.items():
        total = data["total"]
        correct = data["correct"]
        data["accuracy"] = correct / total if total > 0 else 0.0

    return dict(breakdown)


def compute_position_bias(results_by_qid: dict) -> dict:
    """
    Compute answer position distribution (A/B/C/D).

    Returns:
        Dict with counts and percentages for each position
    """
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    valid_total = 0

    for result in results_by_qid.values():
        predicted = result.get("predicted")
        if predicted in counts:
            counts[predicted] += 1
            valid_total += 1

    percentages = {}
    for letter, count in counts.items():
        percentages[letter] = count / valid_total if valid_total > 0 else 0.0

    # Compute bias level (deviation from uniform 25%)
    max_deviation = max(abs(p - 0.25) for p in percentages.values())
    if max_deviation <= 0.05:
        bias_level = "low"
    elif max_deviation <= 0.10:
        bias_level = "medium"
    else:
        bias_level = "high"

    return {
        "counts": counts,
        "percentages": percentages,
        "bias_level": bias_level,
    }


def compute_length_bias(
    results_by_qid: dict, questions: list[dict]
) -> dict:
    """
    Compute how often the model picks the longest answer choice.

    Returns:
        Dict with length bias metrics
    """
    q_by_id = {q["id"]: q for q in questions}
    longest_picked = 0
    valid_total = 0
    correct_is_longest = 0

    for qid, result in results_by_qid.items():
        q = q_by_id.get(qid)
        if q is None:
            continue

        predicted = result.get("predicted")
        if predicted is None:
            continue

        valid_total += 1
        choices = q["choices"]
        lengths = [len(c) for c in choices]
        longest_idx = lengths.index(max(lengths))

        predicted_idx = ord(predicted) - ord('A')
        if predicted_idx == longest_idx:
            longest_picked += 1

        # Also track benchmark baseline (how often correct IS longest)
        correct_idx = q["answer_index"]
        if correct_idx == longest_idx:
            correct_is_longest += 1

    rate = longest_picked / valid_total if valid_total > 0 else 0.0
    benchmark_rate = correct_is_longest / valid_total if valid_total > 0 else 0.0

    # Interpretation:
    # - vs_random: How much above random (25%) the model picks longest
    # - vs_benchmark: How much above/below the benchmark correct-is-longest rate
    return {
        "longest_picked_count": longest_picked,
        "total": valid_total,
        "longest_picked_rate": rate,
        "vs_random": rate - 0.25,
        "benchmark_correct_is_longest_rate": benchmark_rate,
        "vs_benchmark": rate - benchmark_rate,
        "bias_level": "low" if abs(rate - 0.25) <= 0.05 else ("medium" if abs(rate - 0.25) <= 0.10 else "high"),
    }


def compute_all_metrics(responses: list[dict], questions: list[dict]) -> dict:
    """
    Compute all metrics for a model evaluation run.

    Returns:
        Complete metrics dict for the run
    """
    accuracy_metrics = compute_accuracy(responses, questions)
    results_by_qid = accuracy_metrics.pop("results_by_qid")

    difficulty = compute_difficulty_breakdown(results_by_qid, questions)
    domain = compute_domain_breakdown(results_by_qid, questions)
    position = compute_position_bias(results_by_qid)
    length = compute_length_bias(results_by_qid, questions)

    return {
        **accuracy_metrics,
        "by_difficulty": difficulty,
        "by_domain": domain,
        "answer_distribution": position["percentages"],
        "bias_analysis": {
            "position_bias": position["bias_level"],
            "position_distribution": position["counts"],
            "length_bias_raw": length["longest_picked_rate"],
            "length_bias_vs_random": length["vs_random"],
            "length_bias_vs_benchmark": length["vs_benchmark"],
            "length_bias_level": length["bias_level"],
        },
        "answers": results_by_qid,
    }


def find_hardest_questions(
    all_runs: list[dict], questions: list[dict], top_n: int = 10
) -> list[dict]:
    """
    Find questions that were failed by the most models.

    Args:
        all_runs: List of run results with 'answers' dict
        questions: List of question dicts
        top_n: Number of hardest questions to return

    Returns:
        List of dicts with question info and failure counts
    """
    q_by_id = {q["id"]: q for q in questions}
    failure_counts = defaultdict(int)
    model_answers = defaultdict(dict)

    for run in all_runs:
        model = run.get("model", "unknown")
        answers = run.get("answers", {})
        for qid, result in answers.items():
            if not result.get("correct", False):
                failure_counts[qid] += 1
            model_answers[qid][model] = result.get("predicted")

    # Sort by failure count (most failed first)
    sorted_questions = sorted(failure_counts.items(), key=lambda x: -x[1])

    hardest = []
    for qid, fail_count in sorted_questions[:top_n]:
        q = q_by_id.get(qid, {})
        hardest.append({
            "question_id": qid,
            "question": q.get("question", ""),
            "choices": q.get("choices", []),
            "correct_answer": chr(ord('A') + q.get("answer_index", 0)),
            "difficulty": q.get("difficulty", "unknown"),
            "topics": q.get("topics", []),
            "models_failed": fail_count,
            "total_models": len(all_runs),
            "model_answers": model_answers.get(qid, {}),
        })

    return hardest
