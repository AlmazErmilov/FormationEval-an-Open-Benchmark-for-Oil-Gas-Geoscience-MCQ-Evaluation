# FormationEval, an open benchmark for petroleum geoscience evaluation

**FormationEval** is a public benchmark suite for evaluating language models on petroleum geoscience and adjacent subsurface disciplines.

It currently contains three public tracks:

| Track | Format | Status | Notes |
|------|--------|--------|------|
| `formationeval_v0.1.json` | MCQ | evaluated | Christmas 2025. 505 FormationEval-authored multiple-choice questions across 7 domains and 72 evaluated models |
| `formationeval_diskos_qa_v0.2.json` | QA | imported, not yet rerun | Imported 17 March 2026. 1027 public DISKOS-QA question-answer pairs normalized into the FormationEval suite |
| `formationeval_spe_mcq_v0.3.json` | MCQ | imported, not yet rerun | Imported 21 March 2026. 100 public SPE MCQ items from the `ynuwara/spe_mcq_dataset` Hugging Face dataset |

Paper: [arXiv:2601.02158](https://arxiv.org/abs/2601.02158) ([PDF](https://arxiv.org/pdf/2601.02158) | [local copy](paper/2601.02158v2.pdf))

Hugging Face: [Dataset](https://huggingface.co/datasets/AlmazErmilov/FormationEval) | [Leaderboard](https://huggingface.co/spaces/AlmazErmilov/FormationEval-Leaderboard)

**Website**: [formationeval.no](https://www.formationeval.no)

## Current status

- The original model-comparison goal of the project was already addressed by the evaluated 505-question MCQ `v0.1` benchmark (Christmas 2025).
- March 2026 update: the suite now also includes the public DISKOS-QA and SPE MCQ tracks.
- The public leaderboard and quiz still reflect only the evaluated MCQ `v0.1` track.
- A full rerun on the expanded suite is pending because this is a self funded one person project and expanded suite evaluation requires materially more token spend.

If you want to collaborate, support reruns or discuss related research and engineering work, contact `almaz.ermilov@gmail.com`.

Almaz Ermilov is a former petrophysicist and now a full time software engineer focused on LLM transparency, control and security in high hazard industries.

## Why this benchmark

FormationEval is meant to keep three things explicit:

- provenance for every released item
- a clean public-release policy for authored and imported tracks
- evaluation artifacts that are easy to inspect and reproduce

## Public suite structure

The benchmark now has a split release structure.

| File | Purpose |
|------|---------|
| `data/benchmark/formationeval_v0.1.json` | canonical evaluated MCQ track |
| `data/benchmark/formationeval_diskos_qa_v0.2.json` | canonical imported QA track |
| `data/benchmark/formationeval_spe_mcq_v0.3.json` | canonical imported MCQ track |
| `data/benchmark/formationeval_v0.3_manifest.json` | current machine-readable suite manifest |
| `data/benchmark/formationeval_v0.2_manifest.json` | historical manifest snapshot for the DISKOS-QA split release |
| `eval/results/leaderboard.md` | current leaderboard for MCQ `v0.1` only |
| `eval/results/analysis.md` | current analysis for MCQ `v0.1` only |

The paper, published leaderboard, quiz, and current evaluation pipeline cover the MCQ `v0.1` track only.

## Data format

### MCQ track

FormationEval-authored MCQ items use the established schema:

- `id`, `version`
- `domains`, `topics`
- `difficulty`, `language`
- `question`, `choices`, `answer_index`, `answer_key`
- `rationale`, `sources`, `derivation_mode`
- `metadata.calc_required`, `metadata.contamination_risk`

Imported MCQ tracks reuse the same general shape with a few extensions:

- `difficulty` may be `unknown`
- `topics` may be an empty array when the upstream source does not provide question-level topic tags
- `metadata` stays present as an object, but FormationEval-specific fields may be unset for imported tracks
- `figure` may be present as `{ filename, alt }` for imported MCQ items with local static figure assets

### QA track

The imported DISKOS-QA track uses a separate QA schema:

- `id`, `version`, `question_format`
- `language`, `topics`
- `question`, `answer_text`
- `context_snippets`
- `sources`
- `derivation_mode`
- `metadata.diskos`

`context_snippets` is stored as an array of objects with `chunk_index`, `chunk_id`, and `text`.

## Derivation modes

The suite currently uses three derivation modes:

- `concept_based`: FormationEval-authored questions written from scratch from source concepts
- `open_licensed`: FormationEval-authored questions derived from explicitly reusable materials
- `external_open_benchmark`: imported third-party benchmark content kept with its own provenance and licensing notes

## Licensing and provenance

This repository contains both FormationEval-authored material and imported third-party benchmark tracks.

- Project-authored materials remain under [CC BY 4.0](LICENSE).
- The imported DISKOS-QA track is redistributed with upstream attribution and a separate third-party notice.
- The imported SPE MCQ track is redistributed with explicit provenance and a separate third-party notice.
- The underlying DISKOS public corpus provenance points to Zenodo record `10775273` under CC BY 4.0.

Read [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before reusing the imported tracks. (As of March 17, 2026, the upstream DISKOS-QA README states `NLOD 2.0` for the benchmark data, while the upstream Python package metadata still mentions `MIT` for the code package. FormationEval follows the upstream README notice for the imported data track. As of March 21, 2026, the upstream SPE MCQ Hugging Face dataset is tagged `MIT`, while the dataset card also says the question bank is originally from the `Study Guide for the SPE Petroleum Engineering Certification Examination (4th ed., 2011)`. FormationEval keeps that upstream source context explicit in its item-level provenance and third-party notices.)

## Repository structure

```text
data/
├── benchmark/          # Public benchmark files and manifest
├── sources/
│   ├── open/           # Public source registry
│   └── private/        # Private source material (gitignored)
└── working/            # Intermediate outputs (gitignored)
src/                    # MCQ generation and benchmark utilities
eval/                   # MCQ evaluation pipeline and reports
assets/                 # Fonts and static assets
docs/                   # Progress and supporting documentation
paper/                  # Paper source and figures
```

See [data/benchmark/README.md](data/benchmark/README.md) for file-level details and [data/sources/open/README.md](data/sources/open/README.md) for the public source registry.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution rules. FormationEval-authored MCQ additions and fixes follow one workflow. The imported DISKOS-QA and SPE MCQ tracks are maintained as normalized mirrors of upstream benchmarks rather than community-authored extension workflows.

## Citation

If you use FormationEval in research, cite the current paper for the MCQ `v0.1` benchmark, cite DISKOS-QA separately when discussing the imported QA track, and cite the upstream SPE MCQ dataset separately when discussing the imported MCQ track.

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
