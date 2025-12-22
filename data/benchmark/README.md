# FormationEval Benchmark v0.1

Multiple-choice questions for evaluating LLMs on Oil & Gas geoscience knowledge.

## Overview

| Metric | Value |
|--------|-------|
| Questions | 481 |
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
id              - Unique identifier
question        - Question text
choices         - Array of 4 options (A-D)
answer_index    - Correct answer index (0-3)
answer_key      - Correct answer letter (A-D)
rationale       - Explanation of correct answer
difficulty      - easy | medium | hard
domains         - Array of broad categories
topics          - Array of specific subjects
sources         - Provenance metadata
metadata        - calc_required, contamination_risk
```

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

## License

Questions are concept-based derivations from source materials. See `sources` field for attribution.
