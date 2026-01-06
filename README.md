# 🪨 FormationEval, an Open Benchmark for Oil & Gas Geoscience MCQ Evaluation
(attempts on creating something like MMLU, but for subsurface and petroleum sciences)

**FormationEval** is an open, research-oriented benchmark to evaluate language models on **Oil & Gas geoscience** and adjacent subsurface disciplines (petrophysics, petroleum geology, geophysics, reservoir engineering) inspired by **MMLU-style multiple-choice questions (MCQ)**.

The project focuses on **reproducibility, provenance, and licensing safety**: public releases contain **only benchmark items + source references**, not copyrighted textbooks or exam PDFs.

📄 **Paper**: [arXiv:2601.02158](https://arxiv.org/abs/2601.02158) ([PDF](https://arxiv.org/pdf/2601.02158) | [local copy](paper/2601.02158v1.pdf))

🤗 **HuggingFace**: [Dataset](https://huggingface.co/datasets/AlmazErmilov/FormationEval) | [Leaderboard](https://huggingface.co/spaces/AlmazErmilov/FormationEval-Leaderboard)

---

## Why this benchmark

Subsurface/O&G benchmarks for LLMs are rare or limited (or probably hidden with many resources remaining proprietary or access restricted). FormationEval aims to provide:

- a **well-defined schema** and validation rules,
- **transparent origin** for every item,
- a **clear public-release licensing policy**,
- an evaluation workflow that integrates with standard tooling.

---

## Scope

FormationEval currently targets a single, stable task format:

- **MCQ (4 options, single correct answer)**  
  Designed for straightforward scoring (accuracy) and leaderboard comparability.

Planned but optional "future-proof" fields exist (e.g., `image`, `evidence`, `tooling`) while keeping the dataset MCQ first.

---

## Current release (v0.1)

- **505 questions** across 7 domains (petrophysics, petroleum geology, geophysics, reservoir engineering, sedimentology, drilling, production)
- **3 sources**: Ellis & Singer (2007), Bjørlykke (2010), TU Delft OCW
- **72 models evaluated** via Azure OpenAI and OpenRouter

**Top performers:** Gemini 3 Pro Preview (99.8%), GLM-4.7 (98.6%), Gemini 3 Flash Preview (98.2%)

**Open-weight leaders:** GLM-4.7 (98.6%), DeepSeek-R1 (96.2%), DeepSeek-V3.2 (94.9%)

See the [leaderboard](eval/results/leaderboard.md) and [analysis](eval/results/analysis.md) for full results.

---

## Dataset format

Recommended storage: **JSONL** (one item per line) or **JSON**.

### Required fields (MCQ core)
Each item MUST include:

- `id`, `version`
- `domains` (array, 1-3 broad domains), `topics` (array, 1-3 specific topics)
- `difficulty` (`easy|medium|hard|unknown`)
- `language` (`en|ru|no|mixed`)
- `question`
- `choices` (exactly 4 strings)
- `answer_index` (0–3) and `answer_key` (`A–D`)
- `sources` (at least one entry)
- `derivation_mode` (`open_licensed|concept_based`)
- `rationale` (explanation of the answer, written from scratch)

### Optional fields (future-proof, keep minimal)
- `image` (URL or `assets/...` path, **only if redistributable**)
- `evidence` (short snippet for future grounded workflows)
- `metadata` (e.g., `time_limit_sec`, `calc_required`, `contamination_risk`)
- `authors` (for attribution)

> **Note on `contamination_risk`:** This field indicates the likelihood that similar questions appear in LLM training data. Values: `low`, `medium`, `high`. Questions derived from widely-used textbooks or common exam formats carry higher risk, potentially inflating model scores. Original, concept-based questions from niche sources are lower risk.

### Example item
```json
{
  "id": "formationeval_v0.1_petrophysics_porosity_0007",
  "version": "formationeval_v0.1",
  "domains": ["Petrophysics"],
  "topics": ["Porosity", "Neutron-Density Logging"],
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
```

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
Users may generate private question sets from textbooks/exams they are legally entitled to use ("Bring Your Own Sources"). Outputs remain private; this repo provides only schema + tooling.

---

## Repository Structure

```
├── data/
│   ├── benchmark/          # Final verified MCQ datasets (the deliverable)
│   ├── sources/
│   │   ├── open/           # Open-licensed materials (committed)
│   │   └── private/        # BYO/copyrighted materials owned legally (gitignored)
│   └── working/            # Intermediate outputs: chunks, candidates (gitignored)
├── src/                    # Pipeline scripts
├── eval/                   # Evaluation harness
│   └── results/            # Leaderboard and analysis (reports tracked, raw data gitignored)
├── assets/                 # Fonts and static resources
└── docs/                   # Documentation & source registry
```

See [`data/sources/open/README.md`](data/sources/open/README.md) for the registry of open-licensed materials.

A PDF version of the benchmark is available at `data/benchmark/formationeval_v0.1.pdf` (generated via `src/export_benchmark_pdf.py`).

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Verifying existing questions
- Adding new questions from allowed sources
- Schema compliance

---

## License

This project is licensed under [CC BY 4.0](LICENSE). You are free to share and adapt the material with appropriate attribution.

---

## Citation

If you use FormationEval in your research, please cite:

```bibtex
@misc{ermilov2026formationeval,
      title={FormationEval, an open multiple-choice benchmark for petroleum geoscience},
      author={Almaz Ermilov},
      year={2026},
      eprint={2601.02158},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2601.02158},
}
```
