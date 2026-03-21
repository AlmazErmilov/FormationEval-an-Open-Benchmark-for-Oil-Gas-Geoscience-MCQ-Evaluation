# FormationEval v0.2

FormationEval v0.2 was the split release that kept the evaluated MCQ benchmark frozen and added DISKOS-QA as a separate imported QA track in the public suite.

## Highlights

- kept `formationeval_v0.1.json` unchanged as the evaluated MCQ benchmark
- added `formationeval_diskos_qa_v0.2.json` with 1027 imported QA rows
- added `formationeval_v0.2_manifest.json` as the suite manifest for the split release
- updated the website, Hugging Face dataset repo, and Hugging Face Space text to clarify that the public leaderboard and quiz still cover MCQ `v0.1` only
- added explicit third-party notices and provenance links for DISKOS-QA and the underlying Zenodo corpus

## Scope note

The published leaderboard, quiz, paper scope, and evaluation pipeline remained tied to the 505-question MCQ `v0.1` track. The DISKOS-QA track was added for browsing, provenance, and future evaluation work.

## Public note

The original model-comparison goal of the project was already addressed by the evaluated 505-question MCQ benchmark. A full rerun on the expanded suite is pending because this is a self funded one person project and expanded suite evaluation requires materially more token spend.

If you want to collaborate, support reruns or discuss related research and engineering work, contact `almaz.ermilov@gmail.com`.
