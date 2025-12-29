# Progress log

## 2025-12-29: Paper additional fixes

### What changed

- Fixed ISBNs in refs.bib to match chapter README files:
  - Ellis & Singer: 978-1-4020-3738-2 → 978-1-4020-4602-5
  - Bjørlykke: 978-3-642-02331-6 → 978-3-642-02332-3
- Added \label to all 4 tables (tab:summary, tab:distribution, tab:sources, tab:leaderboard)
- Updated all table references to use \ref{} instead of hard-coded numbers
- Added note to Table 2 caption: "Domain counts are non-exclusive: questions may belong to multiple domains"

## 2025-12-29: Paper draft corrections

### What changed

- Fixed open-weight model count: 29 → 32 (verified against leaderboard.md)
- Fixed Appendix B reference: now accurately describes it as a summary with full prompt in repository
- Fixed length bias range: 43-47% → 38-47% (verified against analysis.md)
- Replaced all TODO URLs with actual repository URL
- Updated refs.bib with actual GitHub URLs

### Notes

- Repository is private but will be opened before publication
- All factual claims now verified against source data files

## 2025-12-29: Paper draft figure notes

### What changed

- Added figure and table planning notes to the LaTeX skeleton
- Added a placeholder table for domain and difficulty distribution

## 2025-12-29: Paper draft skeleton

### What changed

- Added a LaTeX skeleton under `paper/` with `main.tex`, `refs.bib`, and `README.md`
- Outlined sections for dataset design, evaluation, results, and discussion
- Added placeholder references for related work and sources

## 2025-12-29: Data availability section

### What changed

- Added a data and code availability section to the paper draft with placeholders for commit-tagged links
- Added repository and dataset placeholder references in `paper/refs.bib`

## 2025-12-29: PDF export font update

### What changed

- Switched the PDF export to Noto Sans with Noto Sans Math fallback so symbols render correctly
- Removed ASCII normalization for PDF text output
- Added Noto Sans font files and license under `assets/fonts/`

## 2025-12-29: PDF export adjustments

### What changed

- Switched the PDF export to built-in fonts and added text normalization for symbols
- Added PDF bookmarks for question navigation and a `--group-by` option for domain/topic sections
- Moved the answer highlight to the "Correct answer:" label only
- Removed font assets from the repo

### Notes

- Use `python src/export_benchmark_pdf.py --group-by domain` for a grouped version
- Standard fonts replace symbols like <= and rho with ASCII forms

## 2025-12-29: Benchmark PDF export script

### What changed

- Added `src/export_benchmark_pdf.py` to generate a readable PDF from `data/benchmark/formationeval_v0.1.json`
- Added DejaVu Sans fonts under `assets/fonts/` to support Unicode characters
- Added `reportlab` to `requirements.txt`

### Notes

- Default output is `data/benchmark/formationeval_v0.1.pdf`; override with `--output` if needed
- The PDF layout includes metadata, choices with the correct answer highlight, rationale, and source details

## 2025-12-28: Leaderboard improvements and cleanup

### Leaderboard format changes

Reorganized leaderboard.md for better readability:

1. **Overall rankings** - Simple table with: Rank, Model, Open, Price, Accuracy, Correct/Total
2. **By difficulty** - Detailed table with: Rank, Model, Company, Accuracy, Parse err, Easy, Medium, Hard
3. **By domain** - Domain breakdown (unchanged)
4. **Bias analysis** - Position and length bias (unchanged)

New columns added:
- **Company**: Organization that developed the model (OpenAI, Anthropic, Google, etc.)
- Renamed "Failed" to "Parse err" for clarity

### Model fixes

**qwen3-8b rerun:**
- Previous: 100% empty responses (provider issue)
- After rerun: 88.7% accuracy with 10 parse errors
- Status: Fixed and included in leaderboard

**gemma-2-9b-it removed:**
- Issue: 63% empty responses from provider (320/505)
- Investigation: Model returns empty strings, not extraction bug
- Action: Removed from config and cache deleted
- Note: Added to config as "DISABLED: 63% empty responses from provider"

### Final model count

72 models evaluated on 505 questions.

---

## 2025-12-28: Model reruns and leaderboard analysis

### Completed reruns

Converted free tier models to paid versions for reliable evaluation:

| Model | Status | Accuracy |
|-------|--------|----------|
| gpt-4o | Completed (was 489/505) | 92.9% |
| gemma-3-27b-it | Completed (paid) | 85.3% |
| gemma-3-12b-it | Completed (paid) | 82.2% |
| gemma-3-4b-it | Completed (paid) | 71.3% |
| gemma-3n-e4b-it | Completed (paid) | 75.2% |
| nemotron-3-nano-30b-a3b | Completed (paid) | 77.4% |
| nemotron-nano-9b-v2 | Completed (paid) | 79.6% |
| nemotron-nano-12b-v2-vl | Completed (paid) | 77.4% |
| gpt-oss-20b | Completed (paid) | 89.3% |

Skipped: gemma-3n-e2b-it (only available as free tier, too slow)

### Removed from leaderboard

- gemini-2.0-flash-exp_free: Incomplete run (75/505), deleted cache
- gemma-2-9b-it: 63% empty responses from provider (unreliable)
- Old free tier caches: Deleted to avoid confusion

### Analysis findings

**claude-sonnet-4.5 anomaly investigated:**
- Accuracy: 89.1% (lower than claude-3.7-sonnet at 94.7% and claude-haiku-4.5 at 91.5%)
- Extraction verified: 0 failures, 505/505 answers extracted correctly
- Pattern distribution: 374 first_char, 35 letter_paren, 35 answer_colon, etc.
- Conclusion: This is the model's actual performance, not an extraction issue

**Benchmark observations:**
- All 72 models show "High" length bias (correct answers systematically longer)
- Petrophysics is consistently the hardest domain across all models
- Production Engineering has high variance (small sample size, ~14 questions)

---

## 2025-12-28: Pricing audit and corrections

### Sources verified

- OpenRouter API (model pages fetched December 2025)
- Azure OpenAI pricing (us-east-2 region)

### Corrections applied to `eval/reports.py`

Updated 23 model prices to match current OpenRouter rates:

| Model | Old ($/M in/out) | New ($/M in/out) |
|-------|------------------|------------------|
| gpt-oss-120b | 1.00/4.00 | 0.04/0.19 |
| claude-opus-4.5 | 15.00/75.00 | 5.00/25.00 |
| gemini-2.5-flash | 0.075/0.30 | 0.30/2.50 |
| gemini-2.5-flash-lite | 0.02/0.10 | 0.10/0.40 |
| gemini-3-pro-preview | 1.25/10.00 | 2.00/12.00 |
| gemini-3-flash-preview | 0.15/0.60 | 0.50/3.00 |
| gemma-2-9b-it | 0.02/0.02 | 0.03/0.09 |
| grok-4-fast | 3.00/15.00 | 0.20/0.50 |
| deepseek-r1 | 0.55/2.19 | 0.30/1.20 |
| deepseek-v3.2 | 0.27/1.10 | 0.22/0.32 |
| deepseek-r1-0528-qwen3-8b | 0.14/0.14 | 0.02/0.10 |
| qwen3-235b-a22b-2507 | 0.30/0.60 | 0.07/0.46 |
| qwen3-32b | 0.10/0.20 | 0.08/0.24 |
| qwen3-14b | 0.07/0.14 | 0.05/0.22 |
| qwen3-8b | 0.04/0.08 | 0.03/0.11 |
| qwen3-vl-8b-thinking | 0.06/0.40 | 0.18/2.10 |
| qwen3-30b-a3b-thinking-2507 | 0.20/0.80 | 0.05/0.34 |
| llama-4-scout | 0.15/0.60 | 0.08/0.30 |
| llama-3.1-8b-instruct | 0.05/0.08 | 0.02/0.03 |
| llama-3.2-3b-instruct | 0.02/0.04 | 0.02/0.02 |
| mistral-small-3.2-24b-instruct | 0.10/0.30 | 0.06/0.18 |
| mistral-small-24b-instruct-2501 | 0.10/0.30 | 0.03/0.11 |
| mistral-nemo | 0.07/0.07 | 0.02/0.04 |
| phi-4-reasoning-plus | 0.07/0.14 | 0.07/0.35 |

### Additional corrections (second pass)

| Model | Old ($/M in/out) | New ($/M in/out) | Source |
|-------|------------------|------------------|--------|
| gpt-5-nano-{low,medium,high} | 0.10/0.80 | 0.05/0.40 | Azure |
| ministral-3b-2512 | 0.02/0.04 | 0.10/0.10 | OpenRouter |
| ministral-8b-2512 | 0.04/0.08 | 0.15/0.15 | OpenRouter |
| ministral-14b-2512 | 0.07/0.14 | 0.20/0.20 | OpenRouter |
| glm-4-32b | 0.20/0.60 | 0.10/0.10 | OpenRouter |

### Notes

- OpenRouter prices vary by provider; listed are typical/lowest rates
- gemma-3n-e2b-it: only free version exists on OpenRouter (marked as Free)
- Run `python eval/run_openrouter.py --analyze-only` to regenerate leaderboard with updated prices

---

## 2025-12-28: Leaderboard enhancements and OpenRouter integration

### OpenRouter provider added

Created `eval/providers/openrouter.py` and `eval/config_openrouter.yaml` to evaluate models via OpenRouter API. This enables testing open-source models (Llama, Qwen, Mistral, DeepSeek, Gemma) alongside proprietary ones.

**Key features:**
- Per-model concurrency override for rate-limited free tier models
- Combined cache analysis (both Azure and OpenRouter results)
- 50 OpenRouter models configured (41 paid, 9 free tier)

### Combined benchmark results

| Provider | Models | Complete runs |
|----------|--------|---------------|
| Azure OpenAI | 24 | 24 |
| OpenRouter | 50 | ~46 (some rate-limited) |
| **Total** | **70** | **~70** |

### Leaderboard columns added

Added model metadata to `eval/reports.py`:

| Column | Description |
|--------|-------------|
| Open | Whether model weights are publicly available (Yes/No) |
| Price ($/M) | Cost per million tokens (input/output) in USD |
| Correct/Total | Number of correct answers out of questions processed |
| Failed | Extraction failures (response could not be parsed) |

**Pricing sources:** OpenRouter, Azure OpenAI, OpenAI API (December 2025)

### Top performers (70 models)

| Rank | Model | Open | Price | Accuracy |
|------|-------|------|-------|----------|
| 1 | gemini-3-pro-preview | No | $1.25/$10.00 | 99.8% |
| 2 | glm-4.7 | Yes | $0.40/$1.50 | 98.6% |
| 3 | gemini-3-flash-preview | No | $0.15/$0.60 | 98.2% |
| 4 | gemini-2.5-pro | No | $1.25/$10.00 | 97.8% |
| 5 | grok-4.1-fast | No | $0.20/$0.50 | 97.6% |

*Note: gpt-oss-20b-free excluded (only 1/505 questions processed)*

### Best value models (>90% accuracy, low cost)

| Model | Accuracy | Price ($/M) |
|-------|----------|-------------|
| gemini-2.5-flash-lite | 91.3% | $0.02/$0.10 |
| qwen3-14b | 92.9% | $0.07/$0.14 |
| gemini-2.5-flash | 95.0% | $0.07/$0.30 |
| gemini-2.0-flash-001 | 93.3% | $0.10/$0.40 |
| grok-4.1-fast | 97.6% | $0.20/$0.50 |

### Best open-weight models

| Model | Accuracy | Price ($/M) |
|-------|----------|-------------|
| glm-4.7 | 98.6% | $0.40/$1.50 |
| deepseek-r1 | 96.2% | $0.55/$2.19 |
| deepseek-v3.2 | 94.9% | $0.27/$1.10 |
| llama-4-scout | 93.1% | $0.15/$0.60 |
| qwen3-235b-a22b-2507 | 93.1% | $0.30/$0.60 |

### Files modified

- `eval/reports.py` — added MODEL_METADATA dict, leaderboard columns
- `eval/run_openrouter.py` — per-model concurrency support
- `eval/config_openrouter.yaml` — 50 models, free tier at end with concurrency: 3

### Known issues

- Free tier models rate-limited (20 RPM, 1000/day)
- Some models return empty responses (gemma-2-9b-it: 320 empty)
- Running Azure and OpenRouter scripts separately overwrites reports; use `--analyze-only` to regenerate combined reports

---

## 2025-12-27: Evaluation pipeline implemented and tested

### Implementation

Created a modular evaluation pipeline in `eval/` with the following structure:

```
eval/
├── run_evaluation.py      # Main CLI entry point
├── config.yaml            # Model configuration (12 Azure OpenAI models)
├── extraction.py          # Answer extraction with regex patterns
├── metrics.py             # Accuracy, Wilson CI, bias analysis
├── reports.py             # JSON/Markdown/CSV output generation
├── providers/
│   ├── __init__.py
│   └── azure_openai.py    # AsyncAzureOpenAI client with caching
├── cache/                 # Per-question response cache (gitignored)
└── results/               # Output reports
```

### First benchmark run: gpt-4o-mini

| Metric | Value |
|--------|-------|
| **Overall accuracy** | 84.8% (428/505) |
| **95% CI** | [81.4%, 87.6%] |
| **Failed extractions** | 0 (100% success) |
| **Time** | ~8 minutes (20 concurrent) |

**By difficulty:**
- Easy: 90.9% (120/132)
- Medium: 80.7% (221/274)
- Hard: 87.9% (87/99)

**By domain:**
- Geophysics: 92.5%
- Drilling Engineering: 91.7%
- Petroleum Geology: 90.7%
- Sedimentology: 89.8%
- Reservoir Engineering: 88.4%
- Petrophysics: 80.5%
- Production Engineering: 71.4%

**Extraction pattern:** 100% first_char (model responds with single letter due to strict prompt)

### Files modified

- `requirements.txt` — added pyyaml, tqdm, scipy
- `.gitignore` — added eval/cache/*
- `.env.example` — added Azure OpenAI variables
- `.env` — added Azure OpenAI credentials

### Usage

```bash
python eval/run_evaluation.py --models gpt-4o-mini   # Single model
python eval/run_evaluation.py                        # All 12 models
python eval/run_evaluation.py --analyze-only         # Rebuild reports from cache
```

---

## 2025-12-27: Azure infrastructure setup for benchmark evaluation

### Context

Set up Azure infrastructure to run the FormationEval benchmark evaluation pipeline. The goal is to evaluate multiple LLMs (OpenAI, DeepSeek, Grok, Llama, etc.) on the 505 MCQ benchmark.

### Resources created

All resources in **East US 2** region (best model coverage):

| Resource | Name | Purpose |
|----------|------|---------|
| Resource Group | `formationeval-rg` | Container |
| AI Foundry Hub | `formationeval-hub` | Parent for projects |
| AI Foundry Project | `formationeval-project` | Serverless model deployments |
| Azure OpenAI | `formationeval-openai` | OpenAI model deployments |

### Azure OpenAI models deployed (12 models, ready)

| Model | Version | Purpose |
|-------|---------|---------|
| gpt-5.2-chat | 2025-12-11 | Latest frontier |
| gpt-5.1-chat | 2025-11-13 | Frontier |
| gpt-5-chat | 2025-10-03 | Frontier |
| gpt-5-mini | 2025-08-07 | Frontier with reasoning_effort |
| gpt-5-nano | 2025-08-07 | Fast baseline |
| o3-mini | 2025-01-31 | Reasoning |
| o4-mini | 2025-04-16 | Balanced reasoning |
| gpt-4.1 | 2025-04-14 | 1M context |
| gpt-4.1-mini | 2025-04-14 | Cost-effective |
| gpt-4.1-nano | 2025-04-14 | Fastest |
| gpt-4o | 2024-11-20 | Multimodal |
| gpt-4o-mini | 2024-07-18 | Fast, cheap |

### Models available via AI Foundry portal (serverless)

No registration required:
- DeepSeek-R1, DeepSeek-V3.2
- Kimi-K2-Thinking
- Grok-3, Grok-3-mini
- Llama-4-Maverick, Llama-3.3-70B
- Mistral-Large-3

### Models requiring registration or quota

Apply at https://aka.ms/oai/access for registration:
- gpt-5, gpt-5.1, gpt-5.2 (non-chat variants with reasoning_effort)
- o3, o3-pro (full reasoning)
- gpt-oss-120b (OpenAI open-weight)
- Grok-4

Request quota at https://aka.ms/oai/stuquotarequest:
- o1 (quota = 0)
- codex-mini (quota = 0)
- gpt-5.1-codex-mini (quota = 0)

### Files created

- `docs/azure_setup.md` — Full setup documentation with credentials, CLI commands, cost estimates (gitignored)

### Next steps

1. Deploy third-party models via AI Foundry portal
2. Apply for registration for gated models
3. Update `.env` with credentials
4. Implement evaluation script

---

## 2025-12-27: Evaluation pipeline refinements

### Changes to `docs/evaluation_pipeline_concept.md`

**1. System prompt strengthened**

| Before | After |
|--------|-------|
| "Respond with the letter of your answer (A, B, C, or D)." | "State your final answer as a single letter: A, B, C, or D." |

Rationale: "State your final answer" implies definitiveness (no hedging), "single letter" is unambiguous. No "only" needed — "single" already conveys the constraint.

**2. max_tokens: 10 → null**

Reasoning models like DeepSeek-R1 output `<think>...</think>` tags in the visible response. With max_tokens: 10, the response gets truncated before the answer appears, causing extraction failures.

- OpenAI o1/o3: reasoning tokens are internal (hidden), so low limits work
- DeepSeek-R1: reasoning is visible, needs thousands of tokens
- Setting null lets models decide completion length

**3. Extraction pattern tracking added**

The `extract_answer()` function now returns `tuple[str | None, str]` instead of `str | None`:

```python
# Before
def extract_answer(response: str) -> str | None:
    ...
    return text[0]

# After
def extract_answer(response: str) -> tuple[str | None, str]:
    ...
    return text[0], "first_char"
```

Pattern names: `first_char`, `answer_is`, `answer_colon`, `choose`, `parentheses`, `letter_period`, `end_of_string`, `standalone`, `failed`

**4. Results schema updated**

```json
{
  "predicted": "B",
  "correct": true,
  "raw_response": "The answer is B",
  "extraction_pattern": "answer_is"
}
```

**5. Analysis output enhanced**

Added extraction pattern distribution table to `analysis.md`:

| Model | first_char | answer_is | end_of_string | failed |
|-------|-----------|-----------|---------------|--------|
| GPT-4o | 89% | 8% | 2% | 0% |
| DeepSeek-R1 | 12% | 65% | 18% | 1% |

This helps debug instruction-following differences across models.

**6. CSV columns extended**

Added `{model}_pattern` column for per-question extraction method.

### Files modified

- `docs/evaluation_pipeline_concept.md` — all changes above

---

## 2025-12-26: Evaluation pipeline concept finalized

### Context

Researched LLM evaluation frameworks (lm-evaluation-harness, LightEval, Inspect AI) and decided on a custom Python script approach for the FormationEval benchmark. Primary reasons:
- Azure AI Foundry (Llama, Mistral, DeepSeek) not natively supported by existing harnesses
- MCQ evaluation is straightforward (no log-prob scoring needed)
- Full control over Azure SDK integrations
- Faster time to results

### Design decisions

| Decision | Choice |
|----------|--------|
| Prompt format | Zero-shot with instruction |
| Answer parsing | Flexible regex (scan for A/B/C/D) |
| Output formats | JSON + Markdown + CSV (full content) |
| Caching | Yes, cache API responses |
| Error handling | Retry 3x, then abort |
| Providers | Azure-only (OpenAI + AI Foundry) |
| Failed extraction | Count as wrong |
| Reasoning models | Strip thinking tags first |
| Versioning | Full (model version, API version, timestamp) |
| Statistics | 95% Wilson CI only |
| Rate limiting | Batched parallel (20 concurrent, ~30-45s/model) |
| Bias analysis | Yes (length, position, qualifier words) |

### Outputs planned

- `leaderboard.md` — Model rankings with accuracy by difficulty/domain
- `analysis.md` — Hardest questions, error patterns, model agreement
- `questions.csv` — Per-question breakdown for spreadsheet analysis
- `results.json` — Full structured data

### Files created

- `docs/evaluation_pipeline_concept.md` — Full concept and implementation plan

### Next steps

1. Implement core evaluation script
2. Set up Azure endpoints
3. Run initial evaluation on 2-3 models
4. Generate first leaderboard

---

## 2025-12-24: System prompt updates to prevent bias at generation time

### Problem

Analysis of the few-shot examples in `src/prompts/mcq_generator_system_prompt.txt` revealed they contradicted the text guidance:
- 2 of 3 examples had correct answer as the longest option
- No examples demonstrated qualifier word balance
- Text said "avoid patterns where correct answer is always longest" but examples showed the opposite

LLMs learn more from examples than from text instructions, so the examples were teaching the wrong behavior.

### Changes made

**1. Added qualifier word guidance section** (after Balance section)

New guidance about using absolute words ("always", "never") and hedged words ("may", "can") in both correct answers and distractors to prevent exploitable patterns.

**2. Updated note before examples**

Added reminder that examples demonstrate length balance.

**3. Added 2 items to `<what_not_to_do>` section**

Explicit prohibitions against:
- Making correct answer consistently longest/shortest
- Creating exploitable word patterns (absolute words only in distractors, hedged words only in correct answers)

**4. Fixed all three few-shot examples for length balance**

| Example | Correct | Before (chars) | After (chars) | Result |
|---------|---------|----------------|---------------|--------|
| 1 | B | A:66, B:48, C:66, D:48 | A:66, B:61, C:66, D:63 | B no longer shortest |
| 2 | D | A:62, B:56, C:42, D:72 | A:71, B:68, C:66, D:72 | D no longer clearly longest |
| 3 | C | A:57, B:55, C:66, D:58 | A:69, B:64, C:66, D:67 | C no longer longest (A is) |

### Rationale

Fixing bias at generation time is more efficient than post-generation cleanup. The dataset required 136 edits to fix length and qualifier biases. Updated examples should reduce this burden for future question generation.

---

## 2025-12-23: Bias analysis and fix planning

### Completed
1. **LaTeX → UTF-8 conversion**: All 45 LaTeX patterns across 21 questions converted to Unicode
2. **Known limitations documented** in `data/benchmark/README.md`
3. **Deep bias analysis** - full report below

---

## Detailed bias analysis report

### Issue #1: Answer length bias

**Criticality: HIGH (8/10)**

| Position | Count | Actual | Expected | Deviation |
|----------|-------|--------|----------|-----------|
| Longest (correct) | 326 | 64.6% | 25% | +39.6% |
| 2nd longest | 81 | 16.0% | 25% | -9.0% |
| 3rd longest | 55 | 10.9% | 25% | -14.1% |
| Shortest | 43 | 8.5% | 25% | -16.5% |

**By difficulty (critical finding)**:
| Difficulty | Longest=correct | Assessment |
|------------|-----------------|------------|
| Easy | 50.8% | Acceptable |
| Medium | 63.9% | Concerning |
| Hard | **84.8%** | Severe |

**Character counts**:
- Correct answer avg: 86.6 chars
- Distractor avg: 69.8 chars
- Difference: +16.7 chars

### Issue #2: Qualifier word bias

**Criticality: CRITICAL (9/10)**

**Absolute words (almost never correct)**:
| Word | In correct | In distractor | Correct rate |
|------|------------|---------------|--------------|
| always | 0 | 49 | 0.0% |
| never | 0 | 3 | 0.0% |
| only | 3 | 108 | 2.7% |
| all | 3 | 33 | 8.3% |
| completely | 0 | 7 | 0.0% |
| entirely | 0 | 5 | 0.0% |
| impossible | 0 | 5 | 0.0% |

**Hedged words (almost always correct)**:
| Word | In correct | In distractor | Correct rate |
|------|------------|---------------|--------------|
| may | 13 | 0 | 100.0% |
| can | 50 | 16 | 75.8% |
| often | 10 | 2 | 83.3% |
| tends to | 15 | 6 | 71.4% |

**162 questions (32%) contain exploitable patterns.**

### Issue #3: Structural patterns

**Criticality: MODERATE (4/10)**

| Pattern | In correct | In distractor | Diff |
|---------|------------|---------------|------|
| Contains comma | 38.6% | 27.8% | +10.8% |
| Contains parentheses | 10.7% | 3.4% | +7.3% |
| Contains "while" | 6.3% | 3.4% | +3.0% |

### Issue #4: Position distribution

**Criticality: LOW (2/10)**

| Position | Count | Percentage |
|----------|-------|------------|
| A | 138 | 27.3% |
| B | 130 | 25.7% |
| C | 124 | 24.6% |
| D | 113 | 22.4% |

Well balanced - not a concern.

---

## Combined impact

**A model could achieve ~70% accuracy using ONLY surface heuristics:**
- Random baseline: 25%
- Pick longest: 64.6%
- Exploit qualifiers: +5-10%
- Combined: ~68-72%

**Comparison to standards**:
| Benchmark | Length bias | Qualifier bias |
|-----------|-------------|----------------|
| MMLU | ~35-40% | Mild |
| ARC | ~30-35% | Moderate |
| FormationEval v0.1 | **64.6%** | **Severe** |

---

## Fix strategies

### Phase 1: Low risk (immediate)
- Remove "always" from 13 safe instances
- Expand 17 very short distractors
- Expected: 64.6% → ~58-60%

### Phase 2: Expert review
- Review 36 "always" cases
- Review 108 "only" cases
- Add hedged words to distractors
- Expected: ~58% → ~48-52%

### Phase 3: Deep fixes
- Regenerate 84 hard questions
- Expand remaining short distractors
- Expected: ~50% → ~35-40%

---

## 2025-12-23: Length bias fixes applied

### Strategy: EXPAND, don't delete

Added technical context to distractors to match/exceed correct answer length while preserving factual incorrectness.

### Fixes applied

| Category | Fixed | Total |
|----------|-------|-------|
| "always" distractor expansions | 49 | 49 |
| "only" distractor expansions | 87 | 89 |

### Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Longest=correct | 64.6% | 51.5% | **-13.1pp** |
| Distractor avg length | 69.8 chars | 74.0 chars | +4.2 chars |
| Length gap | +16.7 chars | +12.6 chars | **-4.1 chars** |

### Position distribution after fixes

| Position | Before | After |
|----------|--------|-------|
| Longest (correct) | 64.6% | 45.7% |
| 2nd longest | 16.0% | 29.7% |
| 3rd longest | 10.9% | 13.9% |
| Shortest | 8.5% | 10.7% |

### Remaining work

Qualifier word bias still present (not addressed in this round):
- "always" → 0% correct rate (exploitable)
- "may" → 100% correct rate (exploitable)

See `docs/bias_fix_tracking.md` for full details.

---

## 2025-12-23: "Always" vocabulary diversification

### Strategy: Substitute with varied synonyms

Replaced all 49 instances of "always" in distractors with context-appropriate synonyms to break the single-word exploit pattern.

### Substitution rules

1. **Context-aware selection**: Match word to semantic context
   - Comparatives (greater/higher) → invariably, necessarily
   - Change verbs (increases/decreases) → consistently, necessarily
   - Causation (causes/prevents) → inherently, intrinsically
   - Properties (contains/has) → universally, invariably

2. **Avoid redundancy**: Skip words already in the sentence
   - "always fundamentally" → "invariably fundamentally" (not "inherently fundamentally")

3. **Natural flow**: Ensure grammatical naturalness
   - "must always be" → "must necessarily be"

### Distribution of replacements

| Word | Count | % |
|------|-------|---|
| invariably | 12 | 24% |
| necessarily | 12 | 24% |
| inherently | 11 | 22% |
| consistently | 8 | 16% |
| intrinsically | 5 | 10% |
| universally | 1 | 2% |

### Results

| Metric | Before | After |
|--------|--------|-------|
| "always" in distractors | 49 | 0 |
| Simple heuristic "always=wrong" | Works (100%) | Broken |
| Vocabulary diversity | 1 word | 6 words |

### Partial success

- ✓ Broke single-word "always" exploit pattern
- ✓ Diversified absolute vocabulary across 6 words
- ✓ Each new word appears in only 8-12 distractors (vs 49)
- ✗ Combined "any-absolute-word=wrong" pattern still exploitable
- ✗ All 6 new words have 0% in correct answers

### Next steps for full fix

To fully address qualifier bias:
1. Add "invariably/necessarily/inherently" to ~10-15 correct answers where scientifically accurate
2. Add "may/can" to ~10-15 distractors where claim remains wrong
3. This requires domain expertise to verify scientific accuracy

---

## 2025-12-23: "May" distractor additions

### Strategy: Add "may" to distractors with "no-effect" claims

Added "may" to 13 distractors that claim something "has no effect" or "is independent of" when that's factually wrong. These remain wrong because they still assert no relationship exists.

### Selection criteria

Safe patterns for "may" addition:
- "X has no effect on Y" → "X may have no effect on Y" (still claims no effect)
- "X is independent of Y" → "X may be independent of Y" (still claims no relationship)
- "X cannot affect Y" → "X may not affect Y" (still denies effect)

### Modifications applied

| ID | Position | Pattern modified |
|----|----------|------------------|
| petrophysics_clay_conductivity_004 | D | "is independent of" |
| petrophysics_dielectric_salinity_003 | B | "has no effect" |
| petrophysics_gamma_interactions_003 | B | "is independent of" |
| petrophysics_salinity_effect_006 | D | "has no effect" |
| petrophysics_pulsed_neutron_physics_002 | D | "are independent of" |
| petrophysics_nmr_diffusion_003 | B | "has no effect" |
| petrophysics_fluid_properties_006 | B | "is independent of" |
| petrophysics_wave_propagation_004 | D | "is independent of" |
| petrophysics_porosity_evaluation_008 | A | "is independent of" |
| petrophysics_permeability_stoneley_008 | B | "has no effect" |
| petrophysics_volumetric_pe_012 | B | "is independent of" |
| reservoirengineering_overpressure_compaction_011 | D | "has no influence" |
| geophysics_rock_physics_link_001 | D | "cannot affect" |

### Results

| Metric | Before | After |
|--------|--------|-------|
| "may" in correct answers | 13 | 13 |
| "may" in distractors | 0 | 13 |
| "may" correct rate | 100% | **50%** |

### Success

- ✓ Broke "may = correct" exploit pattern completely
- ✓ All modified distractors remain factually wrong
- ✓ No domain expertise required (used "no-effect" patterns only)

### Remaining qualifier bias issues

| Word | In correct | In distractor | Correct rate | Status |
|------|------------|---------------|--------------|--------|
| may | 13 | 13 | 50% | ✓ Fixed |
| never | 0 | 3 | 0% | Not addressed |
| only | 3 | 108 | 2.7% | Not addressed |
| invariably | 0 | 12 | 0% | Still exploitable |
| necessarily | 0 | 12 | 0% | Still exploitable |
| inherently | 0 | 11 | 0% | Still exploitable |
