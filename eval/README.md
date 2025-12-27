# Evaluation pipeline

Evaluates LLMs on the FormationEval benchmark via Azure OpenAI.

## Quick start

```bash
# Single model (recommended for first test)
python eval/run_evaluation.py --models gpt-4o-mini

# All configured models
python eval/run_evaluation.py

# Rebuild reports from cached responses (no API calls)
python eval/run_evaluation.py --analyze-only

# Validate config without running
python eval/run_evaluation.py --dry-run
```

## Requirements

```bash
pip install pyyaml tqdm scipy
```

Environment variables in `.env`:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
```

## File structure

```
eval/
├── run_evaluation.py      # CLI entry point
├── config.yaml            # Model configuration
├── extraction.py          # Answer extraction (A/B/C/D)
├── metrics.py             # Accuracy, CI, bias analysis
├── reports.py             # Output generation
├── providers/
│   └── azure_openai.py    # Azure OpenAI client
├── cache/                 # API responses (gitignored)
└── results/               # Output reports
```

## Configuration

Edit `config.yaml` to add/remove models:

```yaml
models:
  - name: gpt-4o-mini
    deployment: gpt-4o-mini
  - name: o3-mini
    deployment: o3-mini
    reasoning_effort: medium  # for reasoning models
```

## Output files

| File | Description |
|------|-------------|
| `results/all_results.json` | All runs with per-question answers |
| `results/leaderboard.md` | Model rankings by accuracy |
| `results/analysis.md` | Hardest questions, bias analysis |
| `results/questions.csv` | Per-question breakdown |

## Metrics

- **Accuracy** with 95% Wilson confidence intervals
- **Difficulty breakdown** (easy/medium/hard)
- **Domain breakdown** (Petrophysics, Geology, etc.)
- **Position bias** (A/B/C/D distribution)
- **Length bias** (preference for longer answers)

## Caching

Responses are cached per model/question in `cache/{model}/{question_id}.json`. Re-running skips cached questions automatically.
