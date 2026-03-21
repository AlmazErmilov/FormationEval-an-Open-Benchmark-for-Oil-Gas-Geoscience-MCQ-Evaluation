# FormationEval v0.3

FormationEval v0.3 adds a third public track to the suite: 100 petroleum
engineering MCQs from the SPE MCQ Dataset published by Yohanes Nuwara on
Hugging Face.

FormationEval `v0.1` was the first 505-question benchmark version and formed a small part
of the work presented at EAGE Digital 2026 in Stavanger in the session *New
Frontiers In Geomodelling: Recent Digital Advances* under the title
*Multi-Agent Framework for Subsurface Workflows: Petrophysicist, Geologist
and Reservoir Engineer GenAI Agents*. I built it to compare models of
different sizes for oil and gas geoscience and subsurface tasks, including
open weight models, and to have a public leaderboard that was useful in
practice. At that point I did not see public benchmarks or leaderboards in
that area that matched that need.

This release continues that same line of work. After the original benchmark,
DISKOS-QA was added as a separate imported QA track and this release adds the
smaller 100-question SPE MCQ Dataset from Yohanes Nuwara as another separate
imported track.

The broader idea behind that structure is simple. I want to keep useful open
domain specific datasets in one place so they are easier to browse, compare
and verify, without losing the original attribution. Each imported track stays
clearly separate, with explicit source links and provenance, so anyone can
trace the data back and check it independently.

## What changed

- kept `formationeval_v0.1.json` unchanged as the evaluated MCQ benchmark
- kept `formationeval_diskos_qa_v0.2.json` unchanged as the imported QA track
- added `formationeval_spe_mcq_v0.3.json` with 100 imported MCQs from
  `ynuwara/spe_mcq_dataset`
- added 10 vendored figure assets for SPE questions that include diagrams
- added `formationeval_v0.3_manifest.json` as the new current suite manifest
- updated the website question browser with a track selector so users can
  switch between `FormationEval OG (v0.1)`, `DISKOS-QA` and `SPE MCQ Dataset`
  in one place
- kept the dedicated `/diskos-qa` route, the quiz and the leaderboard unchanged
- updated the Hugging Face dataset repo and Space to match the three track
  structure

## Attribution and provenance

FormationEval treats imported tracks as imported tracks. DISKOS-QA, developed
by the FORCE consortium, and the SPE MCQ Dataset from Yohanes Nuwara
are kept as separate imported tracks with explicit source attribution,
provenance and third party notices.

For the SPE MCQ track specifically, the suite keeps both:

- the direct Hugging Face dataset provenance for `ynuwara/spe_mcq_dataset`
- the upstream source context note from the dataset card, which says the MCQ
  bank is originally from the *Study Guide for the SPE Petroleum Engineering
  Certification Examination (4th ed., 2011)*

## Scope

The published leaderboard, quiz, paper and evaluation pipeline still cover
only the evaluated MCQ `v0.1` track.

## Why no rerun yet

The original model comparison goal was already addressed by the evaluated 505
question MCQ benchmark. A full rerun on the expanded suite is a separate
effort because this is a self funded one person project and expanded
evaluation requires materially more token spend.

The main value of this update is growing FormationEval as a curated benchmark
space for oil, gas and subsurface LLM evaluation, not promising an immediate
leaderboard refresh.

If you want to collaborate, support reruns or discuss related work, reach out
at `almaz.ermilov@gmail.com`.
