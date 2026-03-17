# Contributing

Contributions to FormationEval are welcome. The repository now contains two different public track types, and they do not follow the same contribution workflow.

## FormationEval-authored MCQ track

The MCQ track is the community-editable part of the benchmark.

You can help by:

- reviewing existing MCQ items for correctness
- proposing fixes to rationales, provenance, or metadata
- proposing new FormationEval-authored questions in English, Norwegian, or Russian

### Allowed sources for authored MCQs

- open-licensed materials
- government or institutional open data
- your own original questions based on domain knowledge

### Rules for authored MCQs

- write questions from scratch
- do not copy or closely paraphrase copyrighted material
- include proper attribution in `sources`
- follow the MCQ schema in the root README

### Not allowed

- verbatim questions from copyrighted textbooks or exams
- close paraphrases of copyrighted material
- questions without clear source attribution

## Imported DISKOS-QA track

The DISKOS-QA track is an imported external benchmark track. It is maintained as a normalized mirror of an upstream benchmark with separate provenance and licensing context. It is not a community-authored extension workflow in this repository.

You can help by:

- reporting data normalization bugs
- reporting provenance or licensing-note mistakes
- reporting broken links or schema inconsistencies

Do not open contribution proposals that add new third-party QA rows in an ad hoc format. External benchmark additions should be discussed first as a benchmark integration proposal, not as routine question authoring.

## Schema compliance

### MCQ requirements

- 4 choices with exactly one correct answer
- required fields: `id`, `question`, `choices`, `answer_index`, `rationale`, `sources`, and related metadata
- difficulty label and domain/topic tags

### QA requirements

- imported rows must preserve upstream identifiers and provenance
- `question_format` must be `qa`
- `context_snippets` must preserve `chunk_index`, `chunk_id`, and `text`
- `derivation_mode` for imported DISKOS-QA rows must be `external_open_benchmark`

## How to contribute

1. Open an issue to discuss the change.
2. Fork the repository.
3. Make changes following the rules above.
4. Submit a pull request with a clear description.

## Questions

If you are unsure whether something belongs in the authored MCQ workflow or in the external benchmark integration workflow, open an issue first.
