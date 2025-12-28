#!/usr/bin/env python3
"""
FormationEval benchmark evaluation pipeline - OpenRouter models.

Evaluates open-source and commercial LLMs via OpenRouter API.

Usage:
    python eval/run_openrouter.py                           # Run all models
    python eval/run_openrouter.py --models deepseek-r1      # Run specific model(s)
    python eval/run_openrouter.py --analyze-only            # Regenerate reports from cache
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

from providers.openrouter import OpenRouterProvider
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

    expanded = expand_env_vars(raw)
    config = yaml.safe_load(expanded)
    return config


def load_benchmark(benchmark_path: Path) -> list[dict]:
    """Load benchmark questions from JSON file."""
    with open(benchmark_path, "r") as f:
        questions = json.load(f)
    return questions


async def run_model_evaluation(
    provider: OpenRouterProvider,
    model_config: dict,
    questions: list[dict],
    default_concurrency: int = 15,
) -> dict:
    """
    Run evaluation for a single model.

    Returns:
        Run result dict with metrics
    """
    model_name = model_config["name"]
    model_id = model_config["model"]
    # Per-model concurrency override (for rate-limited free tier models)
    concurrency = model_config.get("concurrency", default_concurrency)

    print(f"\n{'='*60}")
    print(f"Evaluating: {model_name}")
    print(f"  Model ID: {model_id}")
    print(f"  Concurrency: {concurrency}")
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

    # Run evaluation
    responses = await provider.evaluate_batch(
        model=model_id,
        questions=questions,
        concurrency=concurrency,
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
            "model_id": model_id,
            "provider": "openrouter",
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

    # Get OpenRouter API key
    openrouter_config = config.get("openrouter", {})
    api_key = openrouter_config.get("api_key", "")

    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set in .env")
        return []

    # Create provider
    provider = OpenRouterProvider(
        api_key=api_key,
        cache_dir=cache_dir,
        max_retries=config.get("inference", {}).get("max_retries", 3),
        timeout=config.get("inference", {}).get("timeout_seconds", 60),
    )

    concurrency = config.get("inference", {}).get("concurrency", 15)
    models = config.get("models", [])

    # Filter models if specified
    if selected_models:
        models = [m for m in models if m["name"] in selected_models]
        if not models:
            print(f"Error: No matching models found for: {selected_models}")
            return []

    print(f"\nRunning evaluation on {len(models)} model(s):")
    for m in models:
        print(f"  - {m['name']} ({m['model']})")

    # Run evaluations
    all_runs = []
    for model_config in models:
        try:
            run_result = await run_model_evaluation(
                provider=provider,
                model_config=model_config,
                questions=questions,
                default_concurrency=concurrency,
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

    Includes both OpenRouter and Azure cached results for combined reporting.
    """
    cache_dir = PROJECT_ROOT / config.get("cache", {}).get("directory", "eval/cache")

    if not cache_dir.exists():
        print(f"Cache directory not found: {cache_dir}")
        return []

    # Get configured models to know their friendly names
    model_name_map = {}
    for m in config.get("models", []):
        # Cache key uses sanitized model ID
        sanitized = m["model"].replace("/", "_").replace(":", "_")
        model_name_map[sanitized] = m["name"]

    all_runs = []

    # Scan all cached model directories
    for model_cache in sorted(cache_dir.iterdir()):
        if not model_cache.is_dir() or model_cache.name.startswith('.'):
            continue

        cache_name = model_cache.name

        # Determine friendly name
        if cache_name in model_name_map:
            model_name = model_name_map[cache_name]
        else:
            model_name = cache_name  # Use cache dir name as-is (e.g., gpt-4o-mini)

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

        # Get provider from first response
        first_resp = responses[0]
        provider = first_resp.get("provider", "azure" if "deployment" in first_resp else "openrouter")
        model_id = first_resp.get("model", cache_name)

        # Get timestamp from most recent response
        timestamps = [r.get("timestamp", "") for r in responses if r.get("timestamp")]
        latest_ts = max(timestamps) if timestamps else datetime.now(timezone.utc).isoformat()

        run_result = {
            "run_id": f"cache_{model_name}",
            "run_timestamp": latest_ts,
            "model": model_name,
            "model_info": {
                "model_id": model_id,
                "provider": provider,
                "source": "cache",
            },
            **metrics,
        }

        all_runs.append(run_result)
        print(f"    Accuracy: {metrics['accuracy']*100:.1f}%")

    return all_runs


def main():
    parser = argparse.ArgumentParser(
        description="FormationEval benchmark evaluation - OpenRouter models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python eval/run_openrouter.py                         # Run all models
  python eval/run_openrouter.py --models deepseek-r1    # Run one model
  python eval/run_openrouter.py --models gemini-2.5-pro llama-4-scout  # Multiple
  python eval/run_openrouter.py --analyze-only          # Rebuild reports from cache
        """,
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=SCRIPT_DIR / "config_openrouter.yaml",
        help="Path to config file (default: eval/config_openrouter.yaml)",
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
        api_key = config.get("openrouter", {}).get("api_key", "") or ""
        print(f"\nOpenRouter API key: {'SET' if api_key else 'NOT SET'}")
        print(f"\nModels to evaluate ({len(config.get('models', []))} total):")
        for m in config.get("models", []):
            if not args.models or m["name"] in args.models:
                print(f"  - {m['name']} ({m['model']})")
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
    for i, run in enumerate(sorted_runs[:5], 1):
        provider = run.get("model_info", {}).get("provider", "unknown")
        print(f"  {i}. {run['model']}: {run['accuracy']*100:.1f}% ({provider})")


if __name__ == "__main__":
    main()
