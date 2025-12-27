"""
Report generation for FormationEval evaluation pipeline.

Generates JSON, Markdown leaderboard, analysis, and CSV outputs.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from metrics import find_hardest_questions


def save_all_results_json(
    all_runs: list[dict],
    output_path: Path,
    benchmark_version: str = "formationeval_v0.1",
    total_questions: int = 505,
) -> None:
    """
    Save all evaluation runs to a single JSON file.

    The file is append-only: new runs are added to the 'runs' array.
    """
    # Load existing file if present
    existing = {"benchmark": benchmark_version, "total_questions": total_questions, "runs": []}
    if output_path.exists():
        try:
            with open(output_path, "r") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Add new runs (avoid duplicates by run_id)
    existing_ids = {r.get("run_id") for r in existing.get("runs", [])}
    for run in all_runs:
        if run.get("run_id") not in existing_ids:
            existing["runs"].append(run)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(existing, f, indent=2)


def generate_leaderboard_md(
    all_runs: list[dict],
    output_path: Path,
    benchmark_version: str = "formationeval_v0.1",
) -> None:
    """
    Generate Markdown leaderboard with model rankings.
    """
    if not all_runs:
        return

    # Sort by accuracy (descending)
    sorted_runs = sorted(all_runs, key=lambda x: -x.get("accuracy", 0))

    # Get latest run timestamp
    latest_ts = max(r.get("run_timestamp", "") for r in all_runs)

    lines = [
        f"# FormationEval {benchmark_version} leaderboard",
        "",
        f"Last updated: {latest_ts}",
        "",
        "## Overall rankings",
        "",
        "| Rank | Model | Accuracy | 95% CI | Easy | Medium | Hard |",
        "|------|-------|----------|--------|------|--------|------|",
    ]

    for i, run in enumerate(sorted_runs, 1):
        model = run.get("model", "unknown")
        acc = run.get("accuracy", 0) * 100
        ci_lower = run.get("ci_lower", 0) * 100
        ci_upper = run.get("ci_upper", 0) * 100
        ci_margin = (ci_upper - ci_lower) / 2

        by_diff = run.get("by_difficulty", {})
        easy = by_diff.get("easy", {}).get("accuracy", 0) * 100
        medium = by_diff.get("medium", {}).get("accuracy", 0) * 100
        hard = by_diff.get("hard", {}).get("accuracy", 0) * 100

        lines.append(
            f"| {i} | {model} | {acc:.1f}% | ±{ci_margin:.1f}% | {easy:.1f}% | {medium:.1f}% | {hard:.1f}% |"
        )

    # Add domain breakdown table
    lines.extend([
        "",
        "## By domain",
        "",
    ])

    # Collect all domains
    all_domains = set()
    for run in all_runs:
        all_domains.update(run.get("by_domain", {}).keys())
    domains_sorted = sorted(all_domains)

    if domains_sorted:
        header = "| Model | " + " | ".join(domains_sorted) + " |"
        separator = "|-------" + "|------" * len(domains_sorted) + "|"
        lines.extend([header, separator])

        for run in sorted_runs:
            model = run.get("model", "unknown")
            by_domain = run.get("by_domain", {})
            cells = [model]
            for domain in domains_sorted:
                acc = by_domain.get(domain, {}).get("accuracy", 0) * 100
                cells.append(f"{acc:.1f}%")
            lines.append("| " + " | ".join(cells) + " |")

    # Add bias summary
    lines.extend([
        "",
        "## Bias analysis summary",
        "",
        "| Model | Position bias | Length bias |",
        "|-------|---------------|-------------|",
    ])

    for run in sorted_runs:
        model = run.get("model", "unknown")
        bias = run.get("bias_analysis", {})
        pos_bias = bias.get("position_bias", "unknown")
        len_bias = bias.get("length_bias_level", "unknown")
        lines.append(f"| {model} | {pos_bias.title()} | {len_bias.title()} |")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def generate_analysis_md(
    all_runs: list[dict],
    questions: list[dict],
    output_path: Path,
    benchmark_version: str = "formationeval_v0.1",
) -> None:
    """
    Generate detailed analysis Markdown with hardest questions and patterns.
    """
    if not all_runs:
        return

    latest_ts = max(r.get("run_timestamp", "") for r in all_runs)

    lines = [
        f"# FormationEval {benchmark_version} analysis",
        "",
        f"Last updated: {latest_ts}",
        "",
    ]

    # Hardest questions
    hardest = find_hardest_questions(all_runs, questions, top_n=10)
    if hardest:
        lines.extend([
            "## Hardest questions",
            "",
            "Questions failed by the most models:",
            "",
            "| Rank | Question ID | Difficulty | Models failed | Correct |",
            "|------|-------------|------------|---------------|---------|",
        ])

        for i, q in enumerate(hardest, 1):
            qid_short = q["question_id"].split("_")[-1] if "_" in q["question_id"] else q["question_id"]
            lines.append(
                f"| {i} | ...{qid_short} | {q['difficulty']} | {q['models_failed']}/{q['total_models']} | {q['correct_answer']} |"
            )

        # Show top 3 with full text
        lines.extend(["", "### Example: Hardest questions", ""])
        for i, q in enumerate(hardest[:3], 1):
            lines.extend([
                f"**#{i}: {q['question_id']}**",
                "",
                f"> {q['question']}",
                "",
            ])
            for j, choice in enumerate(q["choices"]):
                letter = chr(ord('A') + j)
                marker = " **(correct)**" if letter == q["correct_answer"] else ""
                lines.append(f"- {letter}) {choice}{marker}")

            lines.extend([
                "",
                "**Model responses:**",
            ])
            for model, answer in q.get("model_answers", {}).items():
                status = "correct" if answer == q["correct_answer"] else "wrong"
                lines.append(f"- {model}: {answer or 'failed'} ({status})")
            lines.append("")

    # Model agreement analysis
    lines.extend([
        "---",
        "",
        "## Model agreement",
        "",
    ])

    q_by_id = {q["id"]: q for q in questions}
    all_correct = 0
    all_wrong = 0
    mixed = 0

    for qid in q_by_id:
        results = []
        for run in all_runs:
            answers = run.get("answers", {})
            if qid in answers:
                results.append(answers[qid].get("correct", False))

        if not results:
            continue
        if all(results):
            all_correct += 1
        elif not any(results):
            all_wrong += 1
        else:
            mixed += 1

    total = all_correct + all_wrong + mixed
    if total > 0:
        lines.extend([
            f"- All models correct: {all_correct}/{total} ({100*all_correct/total:.1f}%)",
            f"- All models wrong: {all_wrong}/{total} ({100*all_wrong/total:.1f}%)",
            f"- Mixed results: {mixed}/{total} ({100*mixed/total:.1f}%)",
            "",
        ])

    # Position bias details
    lines.extend([
        "## Bias exploitation analysis",
        "",
        "### Position bias (A/B/C/D distribution)",
        "",
        "| Model | A | B | C | D | Bias level |",
        "|-------|---|---|---|---|------------|",
    ])

    for run in all_runs:
        model = run.get("model", "unknown")
        dist = run.get("answer_distribution", {})
        bias = run.get("bias_analysis", {})
        lines.append(
            f"| {model} | {dist.get('A', 0)*100:.0f}% | {dist.get('B', 0)*100:.0f}% | "
            f"{dist.get('C', 0)*100:.0f}% | {dist.get('D', 0)*100:.0f}% | {bias.get('position_bias', 'unknown').title()} |"
        )

    lines.extend([
        "",
        "Expected from uniform distribution: 25% each",
        "",
    ])

    # Length bias details
    lines.extend([
        "### Length bias (picking longest answer)",
        "",
        "| Model | % picked longest | vs random (25%) | vs benchmark |",
        "|-------|------------------|-----------------|--------------|",
    ])

    for run in all_runs:
        model = run.get("model", "unknown")
        bias = run.get("bias_analysis", {})
        raw = bias.get("length_bias_raw", 0) * 100
        vs_random = bias.get("length_bias_vs_random", 0) * 100
        vs_bench = bias.get("length_bias_vs_benchmark", 0) * 100
        lines.append(f"| {model} | {raw:.0f}% | {vs_random:+.0f}% | {vs_bench:+.0f}% |")

    lines.extend([
        "",
        "**Interpretation:**",
        "- **vs random (25%)**: Positive = model prefers longer answers",
        "- **vs benchmark**: Negative = picking longest less often than correct-is-longest rate",
        "",
    ])

    # Extraction pattern distribution
    lines.extend([
        "## Extraction pattern distribution",
        "",
        "How models format their answers:",
        "",
    ])

    # Collect all patterns
    all_patterns = set()
    for run in all_runs:
        all_patterns.update(run.get("extraction_patterns", {}).keys())

    if all_patterns:
        patterns_sorted = sorted(all_patterns)
        header = "| Model | " + " | ".join(patterns_sorted) + " |"
        separator = "|-------" + "|------" * len(patterns_sorted) + "|"
        lines.extend([header, separator])

        for run in all_runs:
            model = run.get("model", "unknown")
            patterns = run.get("extraction_patterns", {})
            total_pats = sum(patterns.values())
            cells = [model]
            for pat in patterns_sorted:
                count = patterns.get(pat, 0)
                pct = 100 * count / total_pats if total_pats > 0 else 0
                cells.append(f"{pct:.0f}%")
            lines.append("| " + " | ".join(cells) + " |")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def generate_questions_csv(
    all_runs: list[dict],
    questions: list[dict],
    output_path: Path,
) -> None:
    """
    Generate CSV with per-question breakdown and raw responses.
    """
    if not all_runs or not questions:
        return

    q_by_id = {q["id"]: q for q in questions}
    models = [run.get("model", f"model_{i}") for i, run in enumerate(all_runs)]

    # Build header
    base_columns = [
        "question_id",
        "question_text",
        "choice_a",
        "choice_b",
        "choice_c",
        "choice_d",
        "correct_answer",
        "difficulty",
        "domains",
        "topics",
        "calc_required",
    ]

    model_columns = []
    for model in models:
        model_columns.extend([
            f"{model}_answer",
            f"{model}_correct",
            f"{model}_pattern",
            f"{model}_raw",
        ])

    header = base_columns + model_columns

    rows = []
    for q in questions:
        qid = q["id"]
        choices = q.get("choices", ["", "", "", ""])

        row = {
            "question_id": qid,
            "question_text": q.get("question", ""),
            "choice_a": choices[0] if len(choices) > 0 else "",
            "choice_b": choices[1] if len(choices) > 1 else "",
            "choice_c": choices[2] if len(choices) > 2 else "",
            "choice_d": choices[3] if len(choices) > 3 else "",
            "correct_answer": chr(ord('A') + q.get("answer_index", 0)),
            "difficulty": q.get("difficulty", "unknown"),
            "domains": ";".join(q.get("domains", [])),
            "topics": ";".join(q.get("topics", [])),
            "calc_required": str(q.get("metadata", {}).get("calc_required", False)),
        }

        for run in all_runs:
            model = run.get("model", "unknown")
            answers = run.get("answers", {})
            result = answers.get(qid, {})

            # Truncate raw response for CSV
            raw = result.get("raw_response", "")
            if len(raw) > 500:
                raw = raw[:497] + "..."

            row[f"{model}_answer"] = result.get("predicted", "")
            row[f"{model}_correct"] = str(result.get("correct", False))
            row[f"{model}_pattern"] = result.get("extraction_pattern", "")
            row[f"{model}_raw"] = raw

        rows.append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def generate_all_reports(
    all_runs: list[dict],
    questions: list[dict],
    output_dir: Path,
    benchmark_version: str = "formationeval_v0.1",
) -> dict[str, Path]:
    """
    Generate all output reports.

    Returns:
        Dict mapping report type to output path
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "json": output_dir / "all_results.json",
        "leaderboard": output_dir / "leaderboard.md",
        "analysis": output_dir / "analysis.md",
        "csv": output_dir / "questions.csv",
    }

    save_all_results_json(
        all_runs, paths["json"],
        benchmark_version=benchmark_version,
        total_questions=len(questions),
    )

    generate_leaderboard_md(all_runs, paths["leaderboard"], benchmark_version)
    generate_analysis_md(all_runs, questions, paths["analysis"], benchmark_version)
    generate_questions_csv(all_runs, questions, paths["csv"])

    return paths
