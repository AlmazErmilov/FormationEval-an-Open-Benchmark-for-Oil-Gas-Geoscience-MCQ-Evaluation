# FormationEval-an-Open-Benchmark-for-Oil-Gas-Geoscience-MCQ-Evaluation
attempts on creating something like MMLU, but for subsurface and petroleum sciences

**FormationEval** is an open, research-oriented benchmark to evaluate language models on **Oil & Gas geoscience** and adjacent subsurface disciplines (petrophysics, petroleum geology, geophysics, reservoir engineering) inspired by **MMLU-style multiple-choice questions (MCQ)**.

The project focuses on **reproducibility, provenance, and licensing safety**: public releases contain **only benchmark items + source references**, not copyrighted textbooks or exam PDFs.

---

## Scope

FormationEval currently targets a single, stable task format:

- **MCQ (4 options, single correct answer)**  
  Designed for straightforward scoring (accuracy) and leaderboard comparability.

Planned but optional “future-proof” fields exist (e.g., `image`, `rationale`, `evidence`, `tooling`) while keeping the dataset MCQ first.

---

## Why this benchmark

Subsurface/O&G benchmarks for LLMs are rare or limited. FormationEval aims to provide:

- a **well-defined schema** and validation rules,
- **transparent origin** for every item,
- a **clear public-release licensing policy**,
- an evaluation workflow that integrates with standard tooling.

---

## Dataset format

Recommended storage: **JSONL** (one item per line) or **JSON**.

### Required fields (MCQ core)
Each item MUST include:

- `id`, `version`
- `domain`, `topic`
- `difficulty` (`easy|medium|hard|unknown`)
- `language` (`en|ru|no|mixed`)
- `question`
- `choices` (exactly 4 strings)
- `answer_index` (0–3) and `answer_key` (`A–D`)
- `sources` (at least one entry)
- `derivation_mode` (`open_licensed|concept_based`)

### Optional fields (future-proof, keep minimal)
- `rationale` (short explanation, can be written from scratch)
- `image` (URL or `assets/...` path, **only if redistributable**)
- `evidence` (short snippet for future grounded workflows)
- `metadata` (e.g., `time_limit_sec`, `calc_required`, `contamination_risk`)
- `authors` (for attribution)

### Example item
```json
{
  "id": "formationeval_v0_1_petrophysics_porosity_0007",
  "version": "formationeval_v0.1",
  "domain": "Petrophysics",
  "topic": "Porosity",
  "difficulty": "medium",
  "language": "en",
"question": "In a clean sandstone with highly saline formation water, what is the most typical neutron–density response in a water-filled interval (assuming logs are plotted on a compatible sandstone porosity scale)?",
  "choices": [
    "Large crossover consistent with gas effect",
    "Little to no separation; curves track closely",
    "Reverse crossover where density indicates much higher porosity than neutron",
    "Both curves read extremely low porosity regardless of lithology"
  ],
  "answer_index": 1,
  "answer_key": "B",
  "rationale": "In water-filled, clean clastics, neutron and density porosity estimates generally agree (track closely) when plotted on the appropriate matrix scale; large crossover is more typical of gas.",
  "sources": [
    {
      "source_id": "example_source_pack",
      "source_url": "https://example.org/resource",
      "source_title": "Example Open Resource",
      "source_type": "course",
      "year": 0,
      "license": "CC BY",
      "attribution": "Example University",
      "retrieved_at": "2025-12-14",
      "notes": "Concept-based item written from scratch (no verbatim/close paraphrase)."
    }
  ],
  "derivation_mode": "concept_based",
  "metadata": { "time_limit_sec": 90, "calc_required": false, "contamination_risk": "medium" }
}

---

## Public Release Policy: Licensing & Compliance

FormationEval is designed to avoid redistributing copyrighted content.

### Allowed for public release
Only the following item derivation modes are accepted in any dataset published in this repo:

1) **open_licensed**  
   Items derived from sources with explicit reuse terms (e.g., permissive government open data, CC licenses that allow derivatives), with required attribution.

2) **concept_based**  
   Items written **from scratch** based on concepts/facts learned from sources.  
   This explicitly **avoids** reproducing the source’s unique phrasing, structure or distinctive problem statements.

### Prohibited for public release
- **Verbatim copying** of questions/answers/explanations from copyrighted sources.
- **Close paraphrases** (same question with minor wording changes).
- Reproducing copyrighted tables/figures/diagrams or large excerpts.

### BYO Sources (private mode)
Users may generate private question sets from textbooks/exams they are legally entitled to use (“Bring Your Own Sources”). Outputs remain private; this repo provides only schema + tooling.
