# Third-party notices

FormationEval includes both project-authored material and imported third-party benchmark content.

## FormationEval-authored materials

Project-authored materials in this repository are released under the project licence, [CC BY 4.0](LICENSE), unless stated otherwise.

## DISKOS-QA imported track

The public QA track in `data/benchmark/formationeval_diskos_qa_v0.2.json` is imported from the public DISKOS-QA benchmark repository:

- upstream benchmark: <https://github.com/georgeghon/DISKOS-QA>
- raw public CSV used for normalization: `benchmark/dataset/FORCE_QA_public_final.csv`

Notice:

> Contains data under the Norwegian Licence for Open Government Data (NLOD) distributed by the DISKOS-QA benchmark project.

This repository preserves attribution and adds schema normalization. It does not relicense the imported QA data as project-authored CC BY 4.0 material.

Upstream licence note context:

- the DISKOS-QA upstream README states `NLOD 2.0` for the benchmark data
- the upstream Python package metadata also mentions `MIT` for the code package
- GitHub did not detect a standalone upstream `LICENSE` file as of March 17, 2026

FormationEval treats the benchmark-data notice in the upstream README as the governing notice for the imported QA track and keeps that distinction explicit.

## SPE MCQ imported track

The public MCQ track in `data/benchmark/formationeval_spe_mcq_v0.3.json` is imported from the public Hugging Face dataset:

- upstream dataset: <https://huggingface.co/datasets/ynuwara/spe_mcq_dataset>
- upstream author attribution: Yohanes Nuwara

Upstream source context:

- the upstream Hugging Face metadata tags the dataset as `MIT`
- the upstream dataset card also says the MCQ bank is originally from the *Study Guide for the SPE Petroleum Engineering Certification Examination (4th ed., 2011)*
- the upstream dataset exposes 10 question figures, which FormationEval vendors as local static assets for stable public browsing

FormationEval redistributes this imported MCQ track with explicit provenance and a stronger third-party notice. It does not present the imported question bank or figures as FormationEval-authored CC BY material and does not treat the upstream `MIT` tag as the only relevant reuse context.

Reusers should review the upstream Hugging Face dataset card and the original source context before downstream reuse of the imported SPE MCQ content or figures.

## Underlying DISKOS corpus provenance

The imported QA track also carries provenance for the public underlying corpus referenced by DISKOS-QA:

- Zenodo record: <https://zenodo.org/records/10775273>
- title: *Large Oil and Gas industry text dataset from Norwegian, UK and Dutch public oil and gas documents*
- licence: `CC BY 4.0`

This provenance is retained in item-level source metadata for transparency and reproducibility.
