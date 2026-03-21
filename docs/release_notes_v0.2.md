# FormationEval v0.2

This release turned FormationEval into a split benchmark suite. The evaluated
505 question MCQ track stayed frozen and DISKOS-QA was added as a separate
imported QA track with 1027 items.

FormationEval `v0.1` was the first 505-question benchmark version and formed a small part
of the work presented at EAGE Digital 2026 in Stavanger in the session *New
Frontiers In Geomodelling: Recent Digital Advances* under the title
*Multi-Agent Framework for Subsurface Workflows: Petrophysicist, Geologist
and Reservoir Engineer GenAI Agents*. I built it to compare models for oil
and gas geoscience and subsurface tasks, including open weight models, and to
have a public leaderboard with enough size and structure to be useful in
practice. At that point I did not see public benchmarks or leaderboards in
that area that matched that need.

DISKOS-QA was added later as the next separate imported track when it became
available publicly and fit the same benchmark space.

The broader idea here was simple. I wanted to keep useful open domain datasets
in one place so they are easier to browse, compare and verify while keeping
the original attribution and provenance explicit. DISKOS-QA therefore stays a
clearly separate imported track with explicit attribution and provenance.

DISKOS-QA, developed by the FORCE consortium, points to a public oil and gas
text corpus released on Zenodo. FormationEval keeps those source links and
third party notes visible so the track can be traced back and checked
independently.

## What changed

- kept `formationeval_v0.1.json` unchanged as the evaluated MCQ benchmark
- added `formationeval_diskos_qa_v0.2.json` with 1027 imported QA rows
- added `formationeval_v0.2_manifest.json` as the first suite manifest
- updated the website, Hugging Face dataset repo and Hugging Face Space to
  reflect the split structure
- added third party notices and provenance links for DISKOS-QA and the
  underlying Zenodo corpus

## Scope

The published leaderboard, quiz, paper and evaluation pipeline still cover
only the 505 question MCQ `v0.1` track. DISKOS-QA was added for browsing,
provenance and future evaluation work.

## Why no rerun yet

The original model comparison goal was already addressed by the evaluated MCQ
benchmark. A full rerun on the expanded suite is a separate effort because
this is a self funded one person project and expanded evaluation requires
materially more token spend.

The main value of this release was to make FormationEval more useful as a
curated benchmark space for oil, gas and subsurface LLM evaluation, not to
promise an immediate leaderboard refresh.

If you want to collaborate, support reruns or discuss related work, reach out
at `almaz.ermilov@gmail.com`.
