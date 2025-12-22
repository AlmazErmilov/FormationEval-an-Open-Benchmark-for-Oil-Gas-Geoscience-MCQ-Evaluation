# FormationEval Benchmark v0.1

MMLU-style multiple-choice questions for Oil & Gas geoscience evaluation.

## Statistics

| Metric | Value |
|--------|-------|
| Total questions | 481 |
| Unique topics | 175+ |
| Language | English |
| Format | 4-choice MCQ |

### Difficulty Distribution

| Level | Count | % |
|-------|-------|---|
| Easy | 120 | 25% |
| Medium | 264 | 55% |
| Hard | 97 | 20% |

### Domain Coverage

| Domain | Count |
|--------|-------|
| Petrophysics | 271 |
| Petroleum Geology | 129 |
| Sedimentology | 94 |
| Geophysics | 80 |
| Reservoir Engineering | 40 |
| Drilling Engineering | 24 |
| Production Engineering | 13 |

### Answer Key Distribution

| Key | Count | % |
|-----|-------|---|
| A | 132 | 27% |
| B | 123 | 26% |
| C | 116 | 24% |
| D | 110 | 23% |

## Sources

| Source ID | Title | Questions |
|-----------|-------|-----------|
| `ellis_singer_well_logging_2007` | Well Logging for Earth Scientists, 2nd Edition | 219 |
| `bjorlykke_petroleum_geoscience_2010` | Petroleum Geoscience: From Sedimentary Environments to Rock Physics | 262 |

## Schema

Each question contains:

- `id` - Unique identifier
- `question` - Question text
- `choices` - Array of 4 options
- `answer_index` - Correct answer (0-3)
- `answer_key` - Correct answer (A-D)
- `rationale` - Explanation
- `difficulty` - easy/medium/hard
- `domains` - Broad categories
- `topics` - Specific subjects
- `sources` - Provenance metadata
- `derivation_mode` - `concept_based`
- `metadata.calc_required` - Boolean
- `metadata.contamination_risk` - low/medium/high

## File Format

- `formationeval_v0.1.json` - JSON array of question objects

## Usage

```python
import json

with open('formationeval_v0.1.json', 'r') as f:
    questions = json.load(f)

for q in questions:
    print(q['question'])
    for i, choice in enumerate(q['choices']):
        print(f"  {chr(65+i)}) {choice}")
    print(f"Answer: {q['answer_key']}")
```

## License

Questions are concept-based derivations. See individual `sources` entries for attribution requirements.
