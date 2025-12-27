# FormationEval evaluation pipeline concept

Custom evaluation script for running the FormationEval benchmark on LLMs via Azure APIs.

## Design decisions

### Core decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Prompt format | Zero-shot with instruction | Balance between simplicity and accuracy |
| Answer parsing | Flexible (scan for letter) | Handles verbose model responses |
| Output formats | JSON + Markdown + CSV | Machine-readable + human-readable + spreadsheet |
| Caching | Yes, cache responses | Resume interrupted runs, re-analyze without API calls |
| Error handling | Retry 3x, then abort | Fail fast on persistent issues |
| Cost tracking | No | Check Azure portal directly |
| Question analysis | Full | Per-question results, error patterns, model agreement |
| Providers | Azure only (initially) | Focused scope, add others later if needed |

### Additional decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Failed extraction | Count as wrong | Simplest, most conservative approach |
| Baselines | No baselines | Focus on model-to-model comparison |
| Bias exploitation | Yes, analyze all biases | Length, position, qualifier word patterns |
| Question filtering | No, always run all 505 | Consistent evaluation, simpler logic |
| Reasoning models | Strip thinking first | Remove `<thinking>` tags before extraction for o1/o3 |
| Versioning | Full versioning | Record model version, API version, timestamps |
| Statistics | Confidence intervals only | 95% Wilson CI, no significance tests |
| Rate limiting | Sequential with delays | Safest approach, configurable delay |
| CSV content | Full (everything) | Question text + metadata + raw responses |
| Sample questions | Yes, include examples | Show 3-5 examples for hardest/easiest questions |
| Run naming | Timestamp only | Auto-generated, sortable, unique |
| Contamination analysis | Skip | Focus on difficulty and domain breakdowns |

---

## Pipeline architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EVALUATION PIPELINE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   CONFIG                INFERENCE              ANALYSIS         OUTPUT   │
│  ┌──────┐              ┌──────────┐           ┌────────┐      ┌───────┐ │
│  │models│              │          │           │        │      │.json  │ │
│  │.yaml │─────────────▶│ Azure    │──────────▶│ Score  │─────▶│.md    │ │
│  └──────┘              │ APIs     │           │ Analyze│      │.csv   │ │
│  ┌──────┐              │          │           │        │      └───────┘ │
│  │bench │─────────────▶│ (cached) │           └────────┘                │
│  │.json │              └──────────┘                                      │
│  └──────┘                   │                                            │
│                             ▼                                            │
│                        cache/{model}/{qid}.json                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## File structure

```
eval/
├── run_evaluation.py          # Main entry point
├── config.yaml                # Model endpoints & settings
├── providers/
│   ├── __init__.py
│   ├── base.py                # Abstract provider interface
│   ├── azure_openai.py        # GPT-4o, GPT-4o-mini, o1-mini
│   └── azure_foundry.py       # Llama, Mistral, DeepSeek via Azure AI
├── analysis/
│   ├── __init__.py
│   ├── metrics.py             # Accuracy, CI, per-domain stats
│   ├── question_analysis.py   # Hardest questions, error patterns
│   └── reports.py             # Generate Markdown, CSV
├── cache/                     # Raw API responses (gitignored)
│   └── {model_name}/
│       └── {question_id}.json
└── results/                   # Evaluation outputs
    ├── all_results.json       # All runs accumulated (append-only)
    ├── leaderboard.md         # Current leaderboard (regenerated)
    ├── analysis.md            # Current analysis (regenerated)
    └── questions.csv          # Per-question breakdown (regenerated)
```

---

## Prompt template

### System prompt

```
You are taking a multiple-choice exam on Oil & Gas geoscience.
For each question, select the single best answer from the options provided.
State your final answer as a single letter: A, B, C, or D.
```

### User prompt

```
{question}

A) {choice_a}
B) {choice_b}
C) {choice_c}
D) {choice_d}

Answer:
```

---

## Answer extraction

Flexible regex-based extraction to handle various response formats.

### Preprocessing

```python
def strip_thinking(response: str) -> str:
    """Remove reasoning/thinking tags from response (for o1/o3 models)."""
    response = re.sub(r'<thinking>.*?</thinking>', '', response, flags=re.DOTALL)
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    return response.strip()

def clean_response(response: str) -> str:
    """Clean formatting before extraction."""
    text = strip_thinking(response).upper()
    # Remove markdown bold/italic
    text = re.sub(r'\*+([ABCD])\*+', r'\1', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text
```

### Extraction logic

```python
def extract_answer(response: str) -> tuple[str | None, str]:
    """
    Extract A/B/C/D from model response with pattern tracking.
    Returns (answer, pattern_name) where answer is None if extraction fails.

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
        >>> extract_answer("**B**")  # markdown
        ('B', 'first_char')
        >>> extract_answer("I think it's probably B")
        ('B', 'end_of_string')
        >>> extract_answer("See explanation above")  # no letter
        (None, 'failed')
    """
    text = clean_response(response)

    if not text:
        return None, "failed"

    # 1. Direct letter at start (most common for well-prompted models)
    if text[0] in 'ABCD':
        return text[0], "first_char"

    # 2. Pattern matching (order: most specific → most general)
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
```

### Examples: What the regex handles

| Model response | Extracted | Pattern name |
|----------------|-----------|--------------|
| `B` | B ✅ | `first_char` |
| `B)` | B ✅ | `first_char` |
| `The answer is B` | B ✅ | `answer_is` |
| `Answer: C` | C ✅ | `answer_colon` |
| `The correct answer is D` | D ✅ | `correct_answer` |
| `(A)` | A ✅ | `parentheses` |
| `Option B` | B ✅ | `option` |
| `I would choose C` | C ✅ | `choose` |
| `I'll go with D` | D ✅ | `go_with` |
| `B. Because the porosity...` | B ✅ | `letter_period` |
| `B, since the formation...` | B ✅ | `letter_comma` |
| `I think it's B` | B ✅ | `end_of_string` |
| `...therefore the answer is C` | C ✅ | `answer_is` |
| `The choice is D` | D ✅ | `choice_is` |
| `**B**` | B ✅ | `first_char` (after markdown strip) |
| `I believe B is correct` | B ✅ | `standalone` |

### Edge cases that still fail

| Model response | Why it fails |
|----------------|--------------|
| `Both A and C could be correct` | Multiple letters, ambiguous |
| `I'm not sure, maybe B or D` | Multiple letters, ambiguous |
| `The porosity indicates option two` | No letter, just "two" |
| `See explanation above` | No letter at all |

These are rare and correctly counted as wrong (model didn't follow instructions).

---

## Metrics

### Leaderboard metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| Overall accuracy | Correct / Total | `correct / 505` |
| By difficulty | Accuracy per difficulty level | `correct_easy / total_easy`, etc. |
| By domain | Accuracy per domain | `correct_domain / total_domain` |
| 95% confidence interval | Wilson score interval | Standard formula |
| Calc-required accuracy | Questions needing calculation | Subset analysis |

### Question analysis metrics

| Metric | Description |
|--------|-------------|
| Hardest questions | Questions failed by most models (with full text examples) |
| Easiest questions | Questions passed by all models |
| Model agreement | Simple % agreement across models |
| Answer distribution | Model's A/B/C/D selection rates |
| Error patterns | Common wrong answer selections |

### Bias exploitation analysis

Check if models exploit known benchmark biases:

| Bias type | How we detect it | Expected if no bias |
|-----------|------------------|---------------------|
| **Length bias** | Correlation between model's answers and longest choice | ~25% pick longest |
| **Position bias** | Deviation from uniform A/B/C/D selection | ~25% each |
| **Qualifier word bias** | Does model avoid answers with "always", "never"? | No pattern |

```python
def compute_length_bias(results, questions):
    """
    Compute how often model picks the longest answer choice.
    Expected: ~25% if no bias.
    """
    longest_picked = 0
    for qid, result in results.items():
        q = questions[qid]
        lengths = [len(c) for c in q['choices']]
        longest_idx = lengths.index(max(lengths))
        predicted_idx = ord(result['predicted']) - ord('A')
        if predicted_idx == longest_idx:
            longest_picked += 1
    return longest_picked / len(results)


def compute_position_bias(results):
    """
    Compute answer position distribution.
    Expected: ~25% each if no bias.
    """
    counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for result in results.values():
        if result['predicted'] in counts:
            counts[result['predicted']] += 1
    total = sum(counts.values())
    return {k: v/total for k, v in counts.items()}
```

Bias score interpretation:
- **Low bias**: Distribution within ±5% of expected
- **Medium bias**: Distribution within ±10% of expected
- **High bias**: Distribution >10% off expected

---

## Output formats

### all_results.json

Single file that accumulates all evaluation runs. Each run adds a new entry to the `runs` array.

```json
{
  "benchmark": "formationeval_v0.1",
  "total_questions": 505,
  "runs": [
    {
      "run_id": "2024-12-26_143022",
      "run_timestamp": "2024-12-26T14:30:22Z",
      "model": "gpt-4o",
      "model_info": {
        "provider": "azure_openai",
        "deployment": "gpt-4o",
        "model_version": "2024-08-06",
        "api_version": "2024-02-01"
      },
      "accuracy": 0.782,
      "correct": 395,
      "total": 505,
      "failed_extractions": 2,
      "ci_lower": 0.745,
      "ci_upper": 0.818,
      "by_difficulty": {
        "easy": {"accuracy": 0.894, "correct": 118, "total": 132},
        "medium": {"accuracy": 0.763, "correct": 209, "total": 274},
        "hard": {"accuracy": 0.646, "correct": 64, "total": 99}
      },
      "by_domain": {
        "Petrophysics": {"accuracy": 0.813, "correct": 221, "total": 272},
        "Petroleum Geology": {"accuracy": 0.755, "correct": 114, "total": 151}
      },
      "answer_distribution": {"A": 0.26, "B": 0.25, "C": 0.26, "D": 0.23},
      "bias_analysis": {
        "position_bias": "low",
        "length_bias": 0.28,
        "length_bias_level": "low"
      },
      "answers": {
        "formationeval_v0.1_petrophysics_001": {
          "predicted": "D",
          "correct": true,
          "raw_response": "D",
          "extraction_pattern": "first_char"
        },
        "formationeval_v0.1_petrophysics_002": {
          "predicted": "C",
          "correct": false,
          "raw_response": "I think C because...",
          "extraction_pattern": "standalone"
        }
      }
    },
    {
      "run_id": "2024-12-26_152045",
      "model": "gpt-4o-mini",
      "...": "..."
    }
  ]
}
```

**How it works:**
- Run script for `gpt-4o` → adds one entry to `runs[]`
- Run script for `gpt-4o-mini` → adds another entry to `runs[]`
- Run script for `llama-3.1-70b` → adds another entry
- All results in one file, easy to compare

### leaderboard.md

```markdown
# FormationEval v0.1 leaderboard

Run: 2024-12-26 14:30:22 UTC

## Overall rankings

| Rank | Model | Accuracy | 95% CI | Easy | Medium | Hard |
|------|-------|----------|--------|------|--------|------|
| 1 | GPT-4o | 78.2% | ±3.6% | 89.4% | 76.3% | 64.6% |
| 2 | Claude 3.5 Sonnet | 76.8% | ±3.7% | 87.1% | 75.2% | 63.6% |
| 3 | Llama 3.1 70B | 71.3% | ±4.0% | 84.8% | 69.0% | 56.6% |

## By domain

| Model | Petrophysics | Petroleum Geology | Geophysics | Sedimentology |
|-------|--------------|-------------------|------------|---------------|
| GPT-4o | 81.3% | 75.5% | 73.8% | 72.4% |
| ... | ... | ... | ... | ... |

## Bias analysis summary

| Model | Position bias | Length bias |
|-------|---------------|-------------|
| GPT-4o | Low | Low |
| Llama 3.1 70B | Medium | High |
| ... | ... | ... |
```

### analysis.md

```markdown
# FormationEval v0.1 analysis

Run: 2024-12-26 14:30:22 UTC

## Hardest questions

Questions failed by the most models:

| Rank | Question ID | Topic | Models failed | Correct |
|------|-------------|-------|---------------|---------|
| 1 | ...petrophysics_042 | Archie equation | 8/10 | C |
| 2 | ...geology_089 | Migration pathways | 7/10 | B |
| ... | ... | ... | ... | ... |

### Example: Hardest question (#1)

**Question:** In the Archie equation, what is the physical meaning of the
cementation exponent 'm'?

- A) The ratio of pore volume to grain volume
- B) The tortuosity of the current path through the rock
- C) The surface area available for ionic conduction
- D) The resistivity of the formation water

**Correct answer:** C

**Model responses:**
- GPT-4o: B (wrong)
- Claude 3.5: B (wrong)
- Llama 70B: A (wrong)

---

## Model agreement

- All models correct: 245/505 (48.5%)
- All models wrong: 28/505 (5.5%)
- Mixed results: 232/505 (45.9%)

## Bias exploitation analysis

### Position bias (A/B/C/D distribution)

| Model | A | B | C | D | Bias level |
|-------|---|---|---|---|------------|
| GPT-4o | 26% | 25% | 26% | 23% | Low |
| Llama 3.1 70B | 31% | 22% | 28% | 19% | Medium |

Expected from benchmark: A=27%, B=26%, C=25%, D=22%

### Length bias (picking longest answer)

| Model | % picked longest | Expected | Bias level |
|-------|------------------|----------|------------|
| GPT-4o | 28% | 25% | Low |
| Llama 3.1 70B | 38% | 25% | High |

Note: Benchmark has length bias (correct answer is longest in 51.5% of questions).
Models with high length bias may be exploiting this pattern.

## Error patterns

### Most common wrong answers

| Question ID | Correct | Most common wrong | Count |
|-------------|---------|-------------------|-------|
| ...petrophysics_042 | C | A | 6/10 |
| ... | ... | ... | ... |

## Extraction pattern distribution

How models format their answers:

| Model | first_char | answer_is | end_of_string | standalone | failed |
|-------|-----------|-----------|---------------|------------|--------|
| GPT-4o | 89% | 8% | 2% | 1% | 0% |
| GPT-4o-mini | 72% | 18% | 6% | 3% | 1% |
| Llama 3.1 70B | 45% | 32% | 12% | 8% | 3% |
| DeepSeek-R1 | 12% | 65% | 18% | 4% | 1% |

**Observations:**
- GPT-4o follows instructions well (89% direct letter)
- Llama tends to elaborate more (only 45% direct)
- DeepSeek-R1 prefers "The answer is X" format after reasoning
```

### questions.csv

Full export with question text, metadata, and raw responses:

```csv
question_id,question_text,choice_a,choice_b,choice_c,choice_d,correct_answer,difficulty,domains,topics,calc_required,gpt-4o_answer,gpt-4o_correct,gpt-4o_raw,gpt-4o-mini_answer,gpt-4o-mini_correct,gpt-4o-mini_raw,...
formationeval_v0.1_petrophysics_001,"The historical French term...",It was primarily...,It replaced...,It physically...,It provided...,D,easy,"Petrophysics,Petroleum Geology","Well Logging History,Measurement Principles",false,D,true,"D",C,false,"I think C because...",...
...
```

Columns per model:
- `{model}_answer` — Extracted answer (A/B/C/D or empty if failed)
- `{model}_correct` — Boolean
- `{model}_raw` — Raw model response (truncated to 500 chars)
- `{model}_pattern` — Extraction pattern used (first_char, answer_is, etc.)

---

## Configuration (config.yaml)

```yaml
benchmark:
  path: data/benchmark/formationeval_v0.1.json
  version: "0.1"

cache:
  enabled: true
  directory: eval/cache

output:
  directory: eval/results
  formats:
    - json
    - markdown
    - csv

inference:
  max_retries: 3
  retry_delay_seconds: 2
  timeout_seconds: 30
  temperature: 0
  max_tokens: null             # No limit - reasoning models (DeepSeek-R1) need room for <think> tags
  concurrency: 20              # Parallel requests (Azure default: 1000 RPM)
  delay_between_batches: 1.0   # Seconds between batches

# Rate limit reference (Azure defaults):
# - Azure OpenAI: ~1000+ RPM (depends on quota)
# - Azure AI Foundry (Llama/Mistral): 1000 RPM, 200K TPM
# - Safe: 20 concurrent = ~20 req/sec = ~1200 RPM (with delays, stays under limit)
# - 505 questions at 20 concurrent ≈ 30-45 seconds per model

models:
  # Azure OpenAI models
  - name: gpt-4o
    provider: azure_openai
    deployment: gpt-4o  # Your deployment name
    endpoint: ${AZURE_OPENAI_ENDPOINT}
    api_key: ${AZURE_OPENAI_API_KEY}
    api_version: "2024-02-01"

  - name: gpt-4o-mini
    provider: azure_openai
    deployment: gpt-4o-mini
    endpoint: ${AZURE_OPENAI_ENDPOINT}
    api_key: ${AZURE_OPENAI_API_KEY}
    api_version: "2024-02-01"

  # Azure AI Foundry models (Llama, Mistral, etc.)
  - name: llama-3.1-70b
    provider: azure_foundry
    model: meta-llama-3.1-70b-instruct
    endpoint: ${AZURE_AI_FOUNDRY_ENDPOINT}
    api_key: ${AZURE_AI_FOUNDRY_API_KEY}

  - name: mistral-large
    provider: azure_foundry
    model: mistral-large
    endpoint: ${AZURE_AI_FOUNDRY_ENDPOINT}
    api_key: ${AZURE_AI_FOUNDRY_API_KEY}
```

---

## Usage

```bash
# Run evaluation on all configured models
python eval/run_evaluation.py

# Run on specific models only
python eval/run_evaluation.py --models gpt-4o gpt-4o-mini

# Resume from cache (skip already-evaluated questions)
python eval/run_evaluation.py --resume

# Regenerate reports from cached results (no API calls)
python eval/run_evaluation.py --analyze-only
```

---

## Implementation plan

### Phase 1: Core infrastructure
1. Create file structure
2. Implement base provider interface
3. Implement Azure OpenAI provider
4. Implement caching layer
5. Basic evaluation loop

### Phase 2: Azure AI Foundry
1. Implement Azure AI Foundry provider (Llama, Mistral, DeepSeek)
2. Test with one model

### Phase 3: Metrics and analysis
1. Implement accuracy calculations
2. Implement confidence intervals
3. Per-domain, per-difficulty breakdowns
4. Question-level analysis

### Phase 4: Reports
1. JSON output
2. Markdown leaderboard
3. Markdown analysis
4. CSV export

### Phase 5: Polish
1. Error handling improvements
2. Progress bars
3. Documentation
4. Testing with real Azure endpoints

---

## Dependencies

```txt
openai>=1.0.0           # Azure OpenAI SDK
azure-ai-inference      # Azure AI Foundry SDK
pyyaml                  # Config parsing
tqdm                    # Progress bars
scipy                   # Confidence intervals (Wilson score)
```

---

## Environment variables

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key

# Azure AI Foundry
AZURE_AI_FOUNDRY_ENDPOINT=https://your-endpoint.inference.ai.azure.com/
AZURE_AI_FOUNDRY_API_KEY=your-key
```

---

## Notes

- All API responses are cached to `eval/cache/` to enable:
  - Resuming interrupted evaluation runs
  - Re-analyzing results without additional API costs
  - Debugging answer extraction issues
- The cache directory should be gitignored
- Results directory can be committed for reproducibility

---

## Quick reference: All decisions

| Category | Decision | Choice |
|----------|----------|--------|
| **Prompt** | Format | Zero-shot with instruction |
| **Prompt** | System message | "...State your final answer as a single letter: A, B, C, or D." |
| **Parsing** | Method | Flexible regex with pattern tracking |
| **Parsing** | Reasoning models | Strip `<thinking>` tags first |
| **Parsing** | Failed extraction | Count as wrong answer |
| **Output** | Formats | JSON + Markdown + CSV |
| **Output** | Results storage | Single `all_results.json` (append new runs) |
| **Output** | CSV content | Full (question text + metadata + raw responses) |
| **Output** | Run naming | Timestamp only (auto-generated) |
| **Output** | Sample questions | Include 3-5 examples with full text |
| **Output** | Raw responses | Yes, saved for debugging/analysis |
| **Caching** | Enabled | Yes, cache all API responses |
| **Errors** | Retry policy | 3 retries, then abort entire run |
| **Rate limits** | Execution | Batched parallel (20 concurrent, ~30-45 sec/model) |
| **Versioning** | Level | Full (model version, API version, timestamps) |
| **Statistics** | Method | 95% Wilson confidence intervals |
| **Statistics** | Significance tests | No (CI only) |
| **Baselines** | Include | No |
| **Filtering** | Subsets | No, always run all 505 questions |
| **Bias** | Analysis | Yes (length, position, qualifier words) |
| **Contamination** | Analysis | Skip |
| **Providers** | Supported | Azure only (initially) |

---

## Terms cheat sheet

| Term | Simple explanation |
|------|-------------------|
| **Zero-shot** | No examples given — just ask the question directly |
| **Few-shot** | Give 3-5 example Q&As before the test question |
| **Answer extraction** | Finding A/B/C/D in model's response text |
| **Failed extraction** | Model responded but we couldn't find A/B/C/D |
| **Caching** | Saving API responses to disk to avoid re-calling |
| **Wilson CI** | Formula for "how confident are we in this percentage?" |
| **95% CI** | "We're 95% sure the true value is in this range" |
| **Position bias** | Model prefers certain letters (e.g., always picks A) |
| **Length bias** | Model prefers longer answer choices |
| **Thinking tags** | `<thinking>...</thinking>` from reasoning models (o1, o3) |
| **Rate limit** | API restriction: "max N requests per minute" |
| **Batched parallel** | Send 10 requests at once, wait, send next 10 |
| **Baseline** | Simple reference point (random=25%, always-A=27%) |
| **Concurrency** | How many requests run at the same time |

### Wilson CI: How the ±3.6% is calculated

**The problem:**
You got 395/505 = 78.2% accuracy. But how confident are we?

**Simple approximation formula:**
```
CI = ±1.96 × √(p × (1-p) / n)

Where:
  p = proportion correct (0.782)
  n = sample size (505)
  1.96 = z-score for 95% confidence
```

### CI size depends on sample size and accuracy

| Questions | Accuracy | CI width |
|-----------|----------|----------|
| 100 | 80% | ±7.8% |
| 505 | 80% | ±3.5% |
| 1000 | 80% | ±2.5% |
| 505 | 50% | ±4.4% |
| 505 | 90% | ±2.6% |

More questions → narrower CI → more confident.
Accuracy near 50% → wider CI (more uncertainty).

---

## Document history

| Date | Change |
|------|--------|
| 2024-12-26 | Initial concept document created |
| 2024-12-26 | Updated: batched parallel requests, terms cheat sheet |
| 2024-12-26 | Updated: improved regex with examples, Wilson CI examples |
| 2024-12-26 | Updated: concurrency 10→20 based on Azure rate limits (1000 RPM) |
| 2024-12-27 | Updated: max_tokens→null (support reasoning models), strengthened prompt, added extraction pattern tracking |
