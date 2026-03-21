# FormationEval v0.3

FormationEval v0.3 extends the public suite with a third track while keeping the evaluated MCQ benchmark frozen.

## Highlights

- kept `formationeval_v0.1.json` unchanged as the evaluated MCQ benchmark
- kept `formationeval_diskos_qa_v0.2.json` unchanged as the imported QA track
- added `formationeval_spe_mcq_v0.3.json` with 100 imported MCQ rows from `ynuwara/spe_mcq_dataset`
- added 10 vendored local figure assets for the imported SPE MCQ questions that require figures
- added `formationeval_v0.3_manifest.json` as the new current suite manifest
- updated the website question browser so users can switch between `FormationEval OG (v0.1)`, `DISKOS-QA`, and `SPE MCQ Dataset` in one place
- kept the dedicated `/diskos-qa` route and the current quiz and leaderboard behavior unchanged
- updated the Hugging Face dataset repo and Space text so the public suite description matches the new three-track structure

## Attribution and provenance

FormationEval continues to treat imported tracks as imported tracks. DISKOS-QA and SPE MCQ are kept with explicit source attribution, provenance links, and separate third-party notices rather than being reframed as FormationEval-authored content.

For the imported SPE MCQ track, the suite keeps both:

- the direct Hugging Face dataset provenance for `ynuwara/spe_mcq_dataset`
- the upstream source-context note from the dataset card, which says the MCQ bank is originally from the *Study Guide for the SPE Petroleum Engineering Certification Examination (4th ed., 2011)*

## Scope note

The published leaderboard, quiz, paper scope, and current evaluation pipeline still cover only the evaluated MCQ `v0.1` track.

## Public note

The original model-comparison goal of the project was already addressed by the evaluated 505-question MCQ benchmark. A full rerun on the expanded suite is pending because this is a self funded one person project and expanded suite evaluation requires materially more token spend.

If you want to collaborate, support reruns or discuss related research and engineering work, contact `almaz.ermilov@gmail.com`.
