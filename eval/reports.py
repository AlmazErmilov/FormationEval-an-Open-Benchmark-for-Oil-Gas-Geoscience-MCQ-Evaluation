"""
Report generation for FormationEval evaluation pipeline.

Generates JSON, Markdown leaderboard, analysis, and CSV outputs.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from metrics import find_hardest_questions


# =============================================================================
# Model metadata: open-weight status and pricing
# Pricing is per million tokens (input/output) in USD
# Sources: OpenRouter, Azure OpenAI, OpenAI API (December 2025)
# =============================================================================

MODEL_METADATA = {
    # === OpenAI (Azure) - Proprietary ===
    "gpt-4o": {"open_weight": False, "price_input": 2.50, "price_output": 10.00},
    "gpt-4o-mini": {"open_weight": False, "price_input": 0.15, "price_output": 0.60},
    "gpt-4.1": {"open_weight": False, "price_input": 2.00, "price_output": 8.00},
    "gpt-4.1-mini": {"open_weight": False, "price_input": 0.40, "price_output": 1.60},
    "gpt-4.1-nano": {"open_weight": False, "price_input": 0.10, "price_output": 0.40},
    "gpt-5-chat": {"open_weight": False, "price_input": 1.25, "price_output": 10.00},
    "gpt-5-mini-low": {"open_weight": False, "price_input": 0.25, "price_output": 2.00},
    "gpt-5-mini-medium": {"open_weight": False, "price_input": 0.25, "price_output": 2.00},
    "gpt-5-mini-high": {"open_weight": False, "price_input": 0.25, "price_output": 2.00},
    "gpt-5-nano-low": {"open_weight": False, "price_input": 0.10, "price_output": 0.80},
    "gpt-5-nano-medium": {"open_weight": False, "price_input": 0.10, "price_output": 0.80},
    "gpt-5-nano-high": {"open_weight": False, "price_input": 0.10, "price_output": 0.80},
    "gpt-5.1-chat-low": {"open_weight": False, "price_input": 1.25, "price_output": 10.00},
    "gpt-5.1-chat-medium": {"open_weight": False, "price_input": 1.25, "price_output": 10.00},
    "gpt-5.1-chat-high": {"open_weight": False, "price_input": 1.25, "price_output": 10.00},
    "gpt-5.2-chat-low": {"open_weight": False, "price_input": 1.75, "price_output": 14.00},
    "gpt-5.2-chat-medium": {"open_weight": False, "price_input": 1.75, "price_output": 14.00},
    "gpt-5.2-chat-high": {"open_weight": False, "price_input": 1.75, "price_output": 14.00},
    "o3-mini-low": {"open_weight": False, "price_input": 1.10, "price_output": 4.40},
    "o3-mini-medium": {"open_weight": False, "price_input": 1.10, "price_output": 4.40},
    "o3-mini-high": {"open_weight": False, "price_input": 1.10, "price_output": 4.40},
    "o4-mini-low": {"open_weight": False, "price_input": 1.10, "price_output": 4.40},
    "o4-mini-medium": {"open_weight": False, "price_input": 1.10, "price_output": 4.40},
    "o4-mini-high": {"open_weight": False, "price_input": 1.10, "price_output": 4.40},
    # OpenAI open-source models (via OpenRouter)
    "gpt-oss-120b": {"open_weight": True, "price_input": 1.00, "price_output": 4.00},
    "gpt-oss-20b-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},

    # === Anthropic Claude - Proprietary ===
    "claude-opus-4.5": {"open_weight": False, "price_input": 15.00, "price_output": 75.00},
    "claude-sonnet-4.5": {"open_weight": False, "price_input": 3.00, "price_output": 15.00},
    "claude-3.7-sonnet": {"open_weight": False, "price_input": 3.00, "price_output": 15.00},
    "claude-haiku-4.5": {"open_weight": False, "price_input": 1.00, "price_output": 5.00},
    "claude-3.5-haiku": {"open_weight": False, "price_input": 0.80, "price_output": 4.00},

    # === Google Gemini - Proprietary ===
    "gemini-2.5-pro": {"open_weight": False, "price_input": 1.25, "price_output": 10.00},
    "gemini-2.5-flash": {"open_weight": False, "price_input": 0.075, "price_output": 0.30},
    "gemini-2.5-flash-lite": {"open_weight": False, "price_input": 0.02, "price_output": 0.10},
    "gemini-3-pro-preview": {"open_weight": False, "price_input": 1.25, "price_output": 10.00},
    "gemini-3-flash-preview": {"open_weight": False, "price_input": 0.15, "price_output": 0.60},
    "gemini-2.0-flash-001": {"open_weight": False, "price_input": 0.10, "price_output": 0.40},
    "google_gemini-2.0-flash-exp_free": {"open_weight": False, "price_input": 0.00, "price_output": 0.00},

    # === Google Gemma - Open weight ===
    "gemma-2-9b-it": {"open_weight": True, "price_input": 0.02, "price_output": 0.02},
    "gemma-3-27b-it-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},
    "gemma-3-12b-it-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},
    "gemma-3-4b-it-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},
    "gemma-3n-e4b-it-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},
    "gemma-3n-e2b-it-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},

    # === xAI Grok - Proprietary ===
    "grok-4.1-fast": {"open_weight": False, "price_input": 0.20, "price_output": 0.50},
    "grok-4-fast": {"open_weight": False, "price_input": 3.00, "price_output": 15.00},
    "grok-3-mini": {"open_weight": False, "price_input": 0.30, "price_output": 0.50},

    # === DeepSeek - Open weight ===
    "deepseek-r1": {"open_weight": True, "price_input": 0.55, "price_output": 2.19},
    "deepseek-v3.2": {"open_weight": True, "price_input": 0.27, "price_output": 1.10},
    "deepseek-r1-0528-qwen3-8b": {"open_weight": True, "price_input": 0.14, "price_output": 0.14},

    # === Qwen (Alibaba) - Open weight ===
    "qwen3-235b-a22b-2507": {"open_weight": True, "price_input": 0.30, "price_output": 0.60},
    "qwen3-32b": {"open_weight": True, "price_input": 0.10, "price_output": 0.20},
    "qwen3-14b": {"open_weight": True, "price_input": 0.07, "price_output": 0.14},
    "qwen3-8b": {"open_weight": True, "price_input": 0.04, "price_output": 0.08},
    "qwen3-vl-8b-instruct": {"open_weight": True, "price_input": 0.06, "price_output": 0.40},
    "qwen3-vl-8b-thinking": {"open_weight": True, "price_input": 0.06, "price_output": 0.40},
    "qwen3-30b-a3b-thinking-2507": {"open_weight": True, "price_input": 0.20, "price_output": 0.80},

    # === Meta Llama - Open weight ===
    "llama-4-scout": {"open_weight": True, "price_input": 0.15, "price_output": 0.60},
    "llama-3.1-8b-instruct": {"open_weight": True, "price_input": 0.05, "price_output": 0.08},
    "llama-3.2-3b-instruct": {"open_weight": True, "price_input": 0.02, "price_output": 0.04},

    # === Mistral - Open weight ===
    "mistral-medium-3.1": {"open_weight": True, "price_input": 0.40, "price_output": 2.00},
    "mistral-small-3.2-24b-instruct": {"open_weight": True, "price_input": 0.10, "price_output": 0.30},
    "mistral-small-24b-instruct-2501": {"open_weight": True, "price_input": 0.10, "price_output": 0.30},
    "mistral-nemo": {"open_weight": True, "price_input": 0.07, "price_output": 0.07},
    "ministral-3b-2512": {"open_weight": True, "price_input": 0.02, "price_output": 0.04},
    "ministral-8b-2512": {"open_weight": True, "price_input": 0.04, "price_output": 0.08},
    "ministral-14b-2512": {"open_weight": True, "price_input": 0.07, "price_output": 0.14},

    # === Microsoft Phi - Open weight ===
    "phi-4-reasoning-plus": {"open_weight": True, "price_input": 0.07, "price_output": 0.14},

    # === Nvidia Nemotron - Open weight ===
    "nemotron-3-nano-30b-a3b-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},
    "nemotron-nano-9b-v2-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},
    "nemotron-nano-12b-v2-vl-free": {"open_weight": True, "price_input": 0.00, "price_output": 0.00},

    # === Moonshot Kimi - Proprietary ===
    "kimi-k2-thinking": {"open_weight": False, "price_input": 0.40, "price_output": 1.75},

    # === MiniMax - Proprietary ===
    "minimax-m2": {"open_weight": False, "price_input": 0.20, "price_output": 1.00},

    # === Zhipu GLM - Open weight ===
    "glm-4.7": {"open_weight": True, "price_input": 0.40, "price_output": 1.50},
    "glm-4-32b": {"open_weight": True, "price_input": 0.20, "price_output": 0.60},
}


def get_model_metadata(model_name: str) -> dict:
    """Get metadata for a model, with fallback for unknown models."""
    if model_name in MODEL_METADATA:
        return MODEL_METADATA[model_name]

    # Try partial matching for models with suffixes
    for key in MODEL_METADATA:
        if model_name.startswith(key) or key.startswith(model_name):
            return MODEL_METADATA[key]

    # Unknown model - return defaults
    return {"open_weight": None, "price_input": None, "price_output": None}


def format_price(price_input: float | None, price_output: float | None) -> str:
    """Format pricing as a compact string."""
    if price_input is None or price_output is None:
        return "N/A"
    if price_input == 0 and price_output == 0:
        return "Free"
    # Show as $in/$out per 1M tokens
    return f"${price_input:.2f}/${price_output:.2f}"


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
        "**Legend:**",
        "- **Open**: Whether model weights are publicly available",
        "- **Price ($/M)**: Cost per million tokens (input/output) in USD",
        "- **Correct/Total**: Number of correct answers out of questions processed",
        "- **Failed**: Extraction failures (model response could not be parsed)",
        "",
        "*Pricing sources: OpenRouter, Azure OpenAI, OpenAI API (December 2025)*",
        "",
        "## Overall rankings",
        "",
        "| Rank | Model | Open | Price ($/M) | Accuracy | Correct/Total | Failed | 95% CI | Easy | Medium | Hard |",
        "|------|-------|------|-------------|----------|---------------|--------|--------|------|--------|------|",
    ]

    for i, run in enumerate(sorted_runs, 1):
        model = run.get("model", "unknown")
        acc = run.get("accuracy", 0) * 100
        ci_lower = run.get("ci_lower", 0) * 100
        ci_upper = run.get("ci_upper", 0) * 100
        ci_margin = (ci_upper - ci_lower) / 2

        # Get counts
        correct = run.get("correct", 0)
        total = run.get("total", 0)
        failed = run.get("failed_extractions", 0)

        by_diff = run.get("by_difficulty", {})
        easy = by_diff.get("easy", {}).get("accuracy", 0) * 100
        medium = by_diff.get("medium", {}).get("accuracy", 0) * 100
        hard = by_diff.get("hard", {}).get("accuracy", 0) * 100

        # Get model metadata
        meta = get_model_metadata(model)
        open_weight = meta.get("open_weight")
        if open_weight is True:
            open_str = "Yes"
        elif open_weight is False:
            open_str = "No"
        else:
            open_str = "?"
        price_str = format_price(meta.get("price_input"), meta.get("price_output"))

        lines.append(
            f"| {i} | {model} | {open_str} | {price_str} | {acc:.1f}% | {correct}/{total} | {failed} | ±{ci_margin:.1f}% | {easy:.1f}% | {medium:.1f}% | {hard:.1f}% |"
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
