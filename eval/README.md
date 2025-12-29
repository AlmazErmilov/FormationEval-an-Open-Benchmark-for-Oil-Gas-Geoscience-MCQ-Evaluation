# Evaluation pipeline

Evaluates LLMs on the FormationEval benchmark via Azure OpenAI and OpenRouter.

## Quick start

**Azure OpenAI:**
```bash
python eval/run_evaluation.py --models gpt-4o-mini   # Single model
python eval/run_evaluation.py                        # All configured models
python eval/run_evaluation.py --analyze-only         # Rebuild reports from cache
python eval/run_evaluation.py --dry-run              # Validate config
```

**OpenRouter** (Gemini, Claude, Llama, Qwen, DeepSeek, Mistral, etc.):
```bash
python eval/run_openrouter.py --models deepseek-r1   # Single model
python eval/run_openrouter.py                        # All configured models
python eval/run_openrouter.py --analyze-only         # Rebuild combined reports
```

## Requirements

```bash
pip install pyyaml tqdm scipy
```

Environment variables in `.env`:
```
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key

# OpenRouter
OPENROUTER_API_KEY=sk-or-your-key
```

## File structure

```
eval/
├── run_evaluation.py      # Azure OpenAI entry point
├── run_openrouter.py      # OpenRouter entry point
├── config.yaml            # Azure model configuration
├── config_openrouter.yaml # OpenRouter model configuration
├── extraction.py          # Answer extraction (A/B/C/D)
├── metrics.py             # Accuracy, CI, bias analysis
├── reports.py             # Output generation
├── providers/
│   ├── azure_openai.py    # Azure OpenAI client
│   └── openrouter.py      # OpenRouter client
├── cache/                 # API responses (gitignored)
└── results/               # Output reports (see below)
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

| File | Description | Tracked |
|------|-------------|---------|
| `results/leaderboard.md` | Model rankings by accuracy | Yes |
| `results/leaderboard.pdf` | PDF version of leaderboard | Yes |
| `results/analysis.md` | Hardest questions, bias analysis | Yes |
| `results/questions.csv` | Per-question breakdown | Yes |
| `results/all_results.json` | All runs with per-question answers | No (gitignored) |

## Metrics

- **Accuracy** with 95% Wilson confidence intervals
- **Difficulty breakdown** (easy/medium/hard)
- **Domain breakdown** (Petrophysics, Geology, etc.)
- **Position bias** (A/B/C/D distribution)
- **Length bias** (preference for longer answers)

## Caching

Responses are cached per model/question in `cache/{model}/{question_id}.json`. Re-running skips cached questions automatically.

## Design notes

See [`docs/evaluation_pipeline_concept.md`](../docs/evaluation_pipeline_concept.md) for design details and rationale.
