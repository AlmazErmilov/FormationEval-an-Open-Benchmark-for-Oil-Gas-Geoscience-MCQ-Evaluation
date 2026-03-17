# FormationEval benchmark data

This directory contains the public benchmark files for the FormationEval suite.

Paper: [arXiv:2601.02158](https://arxiv.org/abs/2601.02158) ([PDF](https://arxiv.org/pdf/2601.02158) | [local copy](../../paper/2601.02158v2.pdf))

The current paper covers the FormationEval-authored MCQ `v0.1` track. The imported DISKOS-QA track was added later as a separate track in the public suite.

## Files

| File | Format | Purpose |
|------|--------|---------|
| `formationeval_v0.1.json` | JSON array | evaluated MCQ track |
| `formationeval_v0.1.pdf` | PDF | readable MCQ export for review |
| `formationeval_diskos_qa_v0.2.json` | JSON array | imported DISKOS-QA track |
| `formationeval_v0.2_manifest.json` | JSON object | suite manifest with track metadata |

## Track summary

| Track | Items | Format | Evaluated | Notes |
|------|------:|--------|-----------|------|
| FormationEval MCQ `v0.1` | 505 | 4-choice MCQ | Yes | current leaderboard and paper track |
| DISKOS-QA `v0.2` | 1027 | open QA | No | imported external benchmark track |

## MCQ track schema

```text
id                            - unique identifier
version                       - formationeval_v0.1
domains                       - array of broad categories
topics                        - array of specific subjects
difficulty                    - easy | medium | hard
language                      - en | ru | no | mixed
question                      - question text
choices                       - array of 4 options
answer_index                  - correct answer index
answer_key                    - correct answer letter
rationale                     - explanation of the answer
sources                       - provenance metadata
derivation_mode               - concept_based | open_licensed
metadata.calc_required        - boolean
metadata.contamination_risk   - low | medium | high
```

## QA track schema

```text
id                                 - formationeval_v0.2_diskos_{topic_slug}_{question_id12}
version                            - formationeval_v0.2
question_format                    - qa
language                           - en
topics                             - DISKOS topic labels
question                           - question text
answer_text                        - reference answer
context_snippets[]                 - { chunk_index, chunk_id, text }
sources[]                          - direct benchmark provenance plus underlying corpus provenance
derivation_mode                    - external_open_benchmark
metadata.diskos.question_id        - upstream Question_ID
metadata.diskos.chunk_ids          - upstream chunk id list
metadata.diskos.well_names         - upstream well names field
metadata.diskos.wellbore_names     - upstream wellbore names field
metadata.diskos.field_names        - upstream field names field
metadata.diskos.formation_names    - upstream formation names field
metadata.diskos.filter_type        - well | field | formation
metadata.diskos.filter_name        - upstream filter name
metadata.diskos.topic              - upstream topic label
metadata.diskos.evolutions         - upstream evolutions field
metadata.diskos.document_id        - upstream document id
metadata.diskos.document_name      - upstream document name
metadata.diskos.entailed           - upstream entailed flag
```

`topic_slug` is lowercase, spaces and hyphens become underscores, and other non-alphanumeric characters are stripped. Example: `Well-Log -> well_log`.

## DISKOS-QA track breakdown

### Filter types

| Filter type | Count |
|-------------|------:|
| well | 428 |
| formation | 342 |
| field | 257 |

### Topics

| Topic | Count |
|-------|------:|
| Drilling | 190 |
| Rock and Core | 167 |
| Test fluid and pressure | 151 |
| VSP - Well seismic | 119 |
| Geology | 117 |
| Petrophysics | 109 |
| Well-Log | 90 |
| Wellbore / well path | 84 |

### Entailed flag

| Value | Count |
|-------|------:|
| true | 938 |
| false | 89 |

The `entailed` field is preserved as upstream metadata. It is not treated as a local quality gate.

Some `metadata.diskos.*` fields are intentionally kept as raw upstream string literals in the canonical QA JSON for fidelity to the public CSV export. Website-facing derived data may normalize those fields for display.

## Source examples

Each DISKOS-QA item carries two source entries:

```json
[
  {
    "source_id": "diskos_qa_benchmark_2026",
    "source_title": "DISKOS-QA benchmark",
    "source_url": "https://github.com/georgeghon/DISKOS-QA",
    "source_type": "open_data",
    "year": 2026,
    "license": "NLOD 2.0 (as stated in upstream README)",
    "attribution": "DISKOS-QA, FORCE industry collaboration",
    "retrieved_at": "2026-03-17",
    "notes": "Imported external QA benchmark track from the public DISKOS-QA repository. See THIRD_PARTY_NOTICES.md for licensing notes."
  },
  {
    "source_id": "diskos_underlying_corpus_zenodo_10775273",
    "source_title": "Large Oil and Gas industry text dataset from Norwegian, UK and Dutch public oil and gas documents",
    "source_url": "https://zenodo.org/records/10775273",
    "source_type": "open_data",
    "year": 2024,
    "license": "CC BY 4.0",
    "attribution": "FORCE and collaborators",
    "retrieved_at": "2026-03-17",
    "notes": "Underlying public corpus provenance referenced by DISKOS-QA."
  }
]
```

## Current public status

- The current leaderboard and quiz cover the 505-question MCQ `v0.1` track only.
- The imported DISKOS-QA track is published for browsing, provenance, and future evaluation work.
- The original model-comparison goal of the project was already addressed by MCQ `v0.1`.
- A full rerun on the expanded suite is pending because this is a self funded one person project and QA evaluation requires materially more token spend.

If you want to collaborate, support reruns or discuss related research and engineering work, contact `almaz.ermilov@gmail.com`.

## Usage

```python
import json
from pathlib import Path

benchmark_dir = Path("data/benchmark")

with open(benchmark_dir / "formationeval_v0.1.json") as handle:
    mcq_rows = json.load(handle)

with open(benchmark_dir / "formationeval_diskos_qa_v0.2.json") as handle:
    qa_rows = json.load(handle)

print(len(mcq_rows), len(qa_rows))
print(mcq_rows[0]["question"])
print(qa_rows[0]["question"])
```

## Scope and citation

The current paper and published leaderboard cover the FormationEval-authored MCQ `v0.1` track. Cite the current FormationEval paper for MCQ `v0.1` and cite DISKOS-QA separately when discussing the imported QA track.

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

## Known limitations

- The current paper, leaderboard, quiz, and evaluation pipeline cover only the MCQ `v0.1` track. The imported DISKOS-QA track is published for browsing and future reruns.
- The MCQ `v0.1` track remains uneven across domains and source collections, with the largest share of questions in petrophysics and petroleum geology.
- Residual MCQ surface-level biases still exist, especially around answer length and qualifier wording. See the paper and [`analysis.md`](../../eval/results/analysis.md) for the current discussion.
- The imported QA track preserves some upstream metadata fields as raw string literals for fidelity to the public CSV release.

## Licensing

- FormationEval-authored MCQ materials are released under the project licence.
- The imported DISKOS-QA track carries its own third-party notice and attribution requirements.

Read [../../THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md) before reusing the imported QA track.
