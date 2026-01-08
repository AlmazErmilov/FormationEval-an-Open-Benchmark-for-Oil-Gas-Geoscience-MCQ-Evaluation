# FormationEval Benchmark v0.1

Multiple-choice questions for evaluating LLMs on Oil & Gas geoscience knowledge.

📄 **Paper**: [arXiv:2601.02158](https://arxiv.org/abs/2601.02158) ([PDF](https://arxiv.org/pdf/2601.02158) | [local copy](../../paper/2601.02158v1.pdf))

## Citation

If you use this benchmark, please cite:

```bibtex
@misc{ermilov2026formationeval,
      title={FormationEval, an open multiple-choice benchmark for petroleum geoscience},
      author={Almaz Ermilov},
      year={2026},
      eprint={2601.02158},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2601.02158},
      doi={10.48550/arXiv.2601.02158}
}
```

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
| Correct answer is uniquely longest | >55% | 43.2% |
| Correct answer avg length | 86.6 chars | 86.6 chars |
| Distractor avg length | 69.8 chars | 74.0 chars |

**Impact**: Test-takers (human or LLM) may exploit this pattern by selecting the longest answer, artificially inflating scores.

**Status**: Distractor expansions applied to 136 questions containing "always" or "only" qualifiers. Length bias reduced by approximately 12 percentage points but still above the expected 25%.

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
| `only` | 3 | 108 | 2.7% | Not addressed (too common to exploit, context-dependent) |
| `may` | 13 | 13 | 50% | Fixed |

**Pattern**: Absolute words are almost never correct.

**Mitigation applied**:
1. All 49 "always" instances replaced with context-appropriate synonyms (invariably, necessarily, inherently, consistently, intrinsically, universally) to break single-word exploit.
2. Added "may" to 13 distractors with "no-effect" claims to break the 100% correct rate pattern.

**Remaining issue**: Absolute word replacements still have 0% correct rate. Combined "any-absolute=wrong" heuristic remains exploitable.

**Note on practical impact**: These limitations are documented for transparency. For benchmarking purposes, the remaining biases are unlikely to significantly skew results:

- Biases are expected to affect all models equally, so relative comparisons should remain meaningful
- In practice, modern LLMs tend to reason about question content rather than exploiting surface-level word patterns
- The major exploits (length bias, "always"=wrong, "may"=correct) have been addressed
- Remaining issues with "always" synonyms (invariably, necessarily, inherently, etc.) affect <10% of questions. The "only" pattern is not practically exploitable since the word is too common and context-dependent

Further refinements may be addressed in future versions.

## Files

| File | Description |
|------|-------------|
| `formationeval_v0.1.json` | JSON array of question objects |
| `formationeval_v0.1.pdf` | Readable PDF version of the benchmark |

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
