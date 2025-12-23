# FormationEval Benchmark v0.1

Multiple-choice questions for evaluating LLMs on Oil & Gas geoscience knowledge.

## Overview

| Metric | Value |
|--------|-------|
| Questions | 505 |
| Unique topics | 811 |
| Format | 4-choice MCQ |
| Language | English |

## Difficulty

| Level | Count | % |
|-------|------:|--:|
| Easy | 132 | 26% |
| Medium | 274 | 54% |
| Hard | 99 | 20% |

## Domains

Questions may belong to multiple domains.

| Domain | Count |
|--------|------:|
| Petrophysics | 272 |
| Petroleum Geology | 151 |
| Sedimentology | 98 |
| Geophysics | 80 |
| Reservoir Engineering | 43 |
| Drilling Engineering | 24 |
| Production Engineering | 14 |

## Answer Distribution

| A | B | C | D |
|:-:|:-:|:-:|:-:|
| 138 (27%) | 130 (26%) | 124 (25%) | 113 (22%) |

## Sources

| Source | Questions |
|--------|----------:|
| Ellis & Singer - Well Logging for Earth Scientists (2007) | 219 |
| Bjørlykke - Petroleum Geoscience (2010) | 262 |
| TU Delft OCW - Petroleum Geology (2008) | 24 |

## Schema

```
id                            - Unique identifier
question                      - Question text
choices                       - Array of 4 options (A-D)
answer_index                  - Correct answer index (0-3)
answer_key                    - Correct answer letter (A-D)
rationale                     - Explanation of correct answer
difficulty                    - easy | medium | hard
domains                       - Array of broad categories
topics                        - Array of specific subjects
sources                       - Provenance metadata
derivation_mode               - concept_based
metadata.calc_required        - Boolean (calculation needed)
metadata.contamination_risk   - low | medium | high
```

### Contamination Risk

Indicates likelihood that similar questions exist in LLM training data:

| Risk | Meaning |
|------|---------|
| low | Unique to this source, unlikely in training data |
| medium | Common concept, similar questions may exist |
| high | Standard textbook topic, likely seen during training |

## Known limitations

### Answer length bias

Correct answers tend to be longer than distractors (partially addressed in v0.1):

| Metric | Original | After fixes |
|--------|----------|-------------|
| Correct answer is longest choice | 64.6% | 51.5% |
| Correct answer avg length | 86.6 chars | 86.6 chars |
| Distractor avg length | 69.8 chars | 74.0 chars |

**Impact**: Test-takers (human or LLM) may exploit this pattern by selecting the longest answer, artificially inflating scores.

**Status**: Distractor expansions applied to 136 questions containing "always" or "only" qualifiers. Length bias reduced by 13 percentage points but still above the expected 25%.

### Qualifier word bias

Certain qualifier words correlate strongly with answer correctness:

| Word | In correct | In distractor | Correct rate | Status |
|------|-----------|---------------|--------------|--------|
| `always` | 0 | 0 | N/A | Replaced with synonyms |
| `invariably` | 0 | 12 | 0% | New (from always) |
| `necessarily` | 0 | 12 | 0% | New (from always) |
| `inherently` | 0 | 11 | 0% | New (from always) |
| `consistently` | 0 | 8 | 0% | New (from always) |
| `never` | 0 | 3 | 0% | Not addressed |
| `only` | 3 | 108 | 2.7% | Not addressed |
| `may` | 13 | 0 | 100% | Not addressed |

**Pattern**: Absolute words are almost never correct. Hedged words (`may`) are almost always correct.

**Mitigation applied**: All 49 "always" instances replaced with context-appropriate synonyms (invariably, necessarily, inherently, consistently, intrinsically, universally) to break single-word exploit.

**Remaining issue**: Replacement words still have 0% correct rate. Combined "any-absolute=wrong" heuristic remains exploitable.

## File

`formationeval_v0.1.json` - JSON array of question objects

## Usage

```python
import json

with open('formationeval_v0.1.json') as f:
    questions = json.load(f)

for q in questions:
    print(q['question'])
    for i, c in enumerate(q['choices']):
        print(f"  {chr(65+i)}) {c}")
    print(f"Answer: {q['answer_key']}\n")
```

## Methodology

All questions are **concept-based**: written from scratch based on concepts from source materials. This approach:

- Tests understanding of concepts, not recognition of phrases
- Avoids reproducing copyrighted expression
- Uses standard technical terms (porosity, Archie equation, etc.) as-is

Each question includes a `rationale` explaining the correct answer and `sources` for provenance.

See [src/README.md](../../src/README.md) for generation details.

## License

Questions are original derivations. See `sources` field for attribution requirements.
