#!/usr/bin/env python3
"""
FormationEval benchmark evaluation pipeline.

Evaluates LLMs on the FormationEval MCQ dataset via Azure OpenAI.

Usage:
    python eval/run_evaluation.py                      # Run all models
    python eval/run_evaluation.py --models gpt-4o-mini # Run specific model(s)
    python eval/run_evaluation.py --analyze-only       # Regenerate reports from cache
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Add eval directory to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from dotenv import load_dotenv

from providers.azure_openai import AzureOpenAIProvider
from metrics import compute_all_metrics
from reports import generate_all_reports

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")


def expand_env_vars(text: str) -> str:
    """Expand ${VAR} patterns in text with environment variables."""
    pattern = r'\$\{([^}]+)\}'

    def replace(match):
        var_name = match.group(1)
        value = os.environ.get(var_name, "")
        if not value:
            print(f"  Warning: Environment variable {var_name} not set")
        return value

    return re.sub(pattern, replace, text)


def load_config(config_path: Path) -> dict:
    """Load and parse YAML config with environment variable expansion."""
    with open(config_path, "r") as f:
        raw = f.read()

    # Expand environment variables
    expanded = expand_env_vars(raw)
    config = yaml.safe_load(expanded)
    return config


def load_benchmark(benchmark_path: Path) -> list[dict]:
    """Load benchmark questions from JSON file."""
    with open(benchmark_path, "r") as f:
        questions = json.load(f)
    return questions


async def run_model_evaluation(
    provider: AzureOpenAIProvider,
    model_config: dict,
    questions: list[dict],
    concurrency: int = 20,
) -> dict:
    """
    Run evaluation for a single model.

    Returns:
        Run result dict with metrics
    """
    model_name = model_config["name"]
    deployment = model_config.get("deployment", model_name)
    reasoning_effort = model_config.get("reasoning_effort")

    print(f"\n{'='*60}")
    print(f"Evaluating: {model_name}")
    print(f"  Deployment: {deployment}")
    if reasoning_effort:
        print(f"  Reasoning effort: {reasoning_effort}")
    print(f"  Questions: {len(questions)}")
    print(f"{'='*60}")

    # Progress callback
    try:
        from tqdm import tqdm
        pbar = tqdm(total=len(questions), desc=model_name, unit="q")

        def progress(completed, total):
            pbar.n = completed
            pbar.refresh()
    except ImportError:
        pbar = None

        def progress(completed, total):
            if completed % 50 == 0 or completed == total:
                print(f"  Progress: {completed}/{total}")

    # Run evaluation (use model_name as cache_key to separate reasoning_effort variations)
    responses = await provider.evaluate_batch(
        deployment=deployment,
        questions=questions,
        concurrency=concurrency,
        reasoning_effort=reasoning_effort,
        cache_key=model_name,
        progress_callback=progress,
    )

    if pbar:
        pbar.close()

    # Compute metrics
    metrics = compute_all_metrics(responses, questions)

    # Build run result
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    run_result = {
        "run_id": f"{run_id}_{model_name}",
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model_name,
        "model_info": {
            "deployment": deployment,
            "reasoning_effort": reasoning_effort,
        },
        **metrics,
    }

    # Print summary
    print(f"\n  Results for {model_name}:")
    print(f"    Accuracy: {metrics['accuracy']*100:.1f}% ({metrics['correct']}/{metrics['total']})")
    print(f"    95% CI: [{metrics['ci_lower']*100:.1f}%, {metrics['ci_upper']*100:.1f}%]")
    print(f"    Failed extractions: {metrics['failed_extractions']}")

    return run_result


async def run_all_evaluations(
    config: dict,
    questions: list[dict],
    selected_models: list[str] | None = None,
) -> list[dict]:
    """
    Run evaluations for all configured models.

    Args:
        config: Loaded config dict
        questions: List of questions
        selected_models: Optional list of model names to run (None = all)

    Returns:
        List of run result dicts
    """
    # Setup paths
    cache_dir = None
    if config.get("cache", {}).get("enabled", True):
        cache_dir = PROJECT_ROOT / config.get("cache", {}).get("directory", "eval/cache")

    # Get Azure OpenAI credentials
    azure_config = config.get("azure_openai", {})

    # Create provider
    provider = AzureOpenAIProvider(
        endpoint=azure_config.get("endpoint", ""),
        api_key=azure_config.get("api_key", ""),
        api_version=azure_config.get("api_version", "2024-02-01"),
        cache_dir=cache_dir,
        max_retries=config.get("inference", {}).get("max_retries", 3),
        timeout=config.get("inference", {}).get("timeout_seconds", 30),
    )

    concurrency = config.get("inference", {}).get("concurrency", 20)
    models = config.get("models", [])

    # Filter models if specified
    if selected_models:
        models = [m for m in models if m["name"] in selected_models]
        if not models:
            print(f"Error: No matching models found for: {selected_models}")
            return []

    print(f"\nRunning evaluation on {len(models)} model(s):")
    for m in models:
        print(f"  - {m['name']}")

    # Run evaluations
    all_runs = []
    for model_config in models:
        try:
            run_result = await run_model_evaluation(
                provider=provider,
                model_config=model_config,
                questions=questions,
                concurrency=concurrency,
            )
            all_runs.append(run_result)
        except Exception as e:
            print(f"\n  ERROR evaluating {model_config['name']}: {e}")
            print("  Skipping this model and continuing...")

    await provider.close()
    return all_runs


def analyze_from_cache(config: dict, questions: list[dict]) -> list[dict]:
    """
    Rebuild metrics from cached responses (no API calls).

    Useful for re-analyzing results after code changes.
    """
    cache_dir = PROJECT_ROOT / config.get("cache", {}).get("directory", "eval/cache")

    if not cache_dir.exists():
        print(f"Cache directory not found: {cache_dir}")
        return []

    models = config.get("models", [])
    all_runs = []

    for model_config in models:
        model_name = model_config["name"]
        deployment = model_config.get("deployment", model_name)
        model_cache = cache_dir / deployment

        if not model_cache.exists():
            print(f"  No cache for {model_name}, skipping")
            continue

        print(f"  Loading cache for {model_name}...")

        # Load all cached responses
        responses = []
        for cache_file in model_cache.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    responses.append(json.load(f))
            except (json.JSONDecodeError, OSError):
                continue

        if not responses:
            print(f"    No cached responses found")
            continue

        print(f"    Loaded {len(responses)} cached responses")

        # Compute metrics
        metrics = compute_all_metrics(responses, questions)

        # Get timestamp from most recent response
        timestamps = [r.get("timestamp", "") for r in responses if r.get("timestamp")]
        latest_ts = max(timestamps) if timestamps else datetime.now(timezone.utc).isoformat()

        run_result = {
            "run_id": f"cache_{model_name}",
            "run_timestamp": latest_ts,
            "model": model_name,
            "model_info": {
                "deployment": deployment,
                "reasoning_effort": model_config.get("reasoning_effort"),
                "source": "cache",
            },
            **metrics,
        }

        all_runs.append(run_result)
        print(f"    Accuracy: {metrics['accuracy']*100:.1f}%")

    return all_runs


def main():
    parser = argparse.ArgumentParser(
        description="FormationEval benchmark evaluation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python eval/run_evaluation.py                       # Run all models
  python eval/run_evaluation.py --models gpt-4o-mini  # Run one model
  python eval/run_evaluation.py --models gpt-4o gpt-5-mini  # Run multiple
  python eval/run_evaluation.py --analyze-only        # Rebuild reports from cache
        """,
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=SCRIPT_DIR / "config.yaml",
        help="Path to config file (default: eval/config.yaml)",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        help="Specific model name(s) to evaluate",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Regenerate reports from cached responses (no API calls)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and show what would be evaluated",
    )

    args = parser.parse_args()

    # Load config
    print(f"Loading config from: {args.config}")
    config = load_config(args.config)

    # Load benchmark
    benchmark_path = PROJECT_ROOT / config.get("benchmark", {}).get("path", "data/benchmark/formationeval_v0.1.json")
    print(f"Loading benchmark from: {benchmark_path}")
    questions = load_benchmark(benchmark_path)
    print(f"  Loaded {len(questions)} questions")

    # Dry run - just show config
    if args.dry_run:
        print("\n=== DRY RUN ===")
        endpoint = config.get("azure_openai", {}).get("endpoint", "") or "NOT SET"
        api_key = config.get("azure_openai", {}).get("api_key", "") or ""
        print(f"\nAzure endpoint: {endpoint[:50]}{'...' if len(endpoint) > 50 else ''}")
        print(f"API key: {'SET' if api_key else 'NOT SET'}")
        print(f"\nModels to evaluate:")
        for m in config.get("models", []):
            if not args.models or m["name"] in args.models:
                print(f"  - {m['name']} (deployment: {m.get('deployment', m['name'])})")
        return

    # Run evaluation or analyze from cache
    if args.analyze_only:
        print("\n=== ANALYZE ONLY MODE ===")
        print("Rebuilding metrics from cache (no API calls)")
        all_runs = analyze_from_cache(config, questions)
    else:
        print("\n=== RUNNING EVALUATION ===")
        all_runs = asyncio.run(run_all_evaluations(
            config=config,
            questions=questions,
            selected_models=args.models,
        ))

    if not all_runs:
        print("\nNo evaluation results to report.")
        return

    # Generate reports
    output_dir = PROJECT_ROOT / config.get("output", {}).get("directory", "eval/results")
    benchmark_version = config.get("benchmark", {}).get("version", "formationeval_v0.1")

    print(f"\n=== GENERATING REPORTS ===")
    print(f"Output directory: {output_dir}")

    paths = generate_all_reports(
        all_runs=all_runs,
        questions=questions,
        output_dir=output_dir,
        benchmark_version=benchmark_version,
    )

    print(f"\nReports generated:")
    for name, path in paths.items():
        print(f"  - {name}: {path}")

    # Print final summary
    print(f"\n{'='*60}")
    print("EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Models evaluated: {len(all_runs)}")
    print(f"Questions per model: {len(questions)}")
    print(f"\nTop performers:")
    sorted_runs = sorted(all_runs, key=lambda x: -x.get("accuracy", 0))
    for i, run in enumerate(sorted_runs[:3], 1):
        print(f"  {i}. {run['model']}: {run['accuracy']*100:.1f}%")


if __name__ == "__main__":
    main()
