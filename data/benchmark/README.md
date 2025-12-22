# FormationEval Benchmark v0.1

Multiple-choice questions for evaluating LLMs on Oil & Gas geoscience knowledge.

## Overview

| Metric | Value |
|--------|-------|
| Questions | 481 |
| Unique topics | 775 |
| Format | 4-choice MCQ |
| Language | English |

## Difficulty

| Level | Count | % |
|-------|------:|--:|
| Easy | 120 | 25% |
| Medium | 264 | 55% |
| Hard | 97 | 20% |

## Domains

Questions may belong to multiple domains.

| Domain | Count |
|--------|------:|
| Petrophysics | 271 |
| Petroleum Geology | 129 |
| Sedimentology | 94 |
| Geophysics | 80 |
| Reservoir Engineering | 40 |
| Drilling Engineering | 24 |
| Production Engineering | 13 |

## Answer Distribution

| A | B | C | D |
|:-:|:-:|:-:|:-:|
| 132 (27%) | 123 (26%) | 116 (24%) | 110 (23%) |

## Sources

| Source | Questions |
|--------|----------:|
| Ellis & Singer - Well Logging for Earth Scientists (2007) | 219 |
| Bjørlykke - Petroleum Geoscience (2010) | 262 |

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
